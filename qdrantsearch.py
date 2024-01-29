from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import SentenceTransformerEmbeddings
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import ast

COLLECTION_NAME = "georgebrown-v2"

embeddings = SentenceTransformerEmbeddings(model_name='sentence-transformer-finetuned/georgebrown-v6-embeddings')

qdrant_client = QdrantClient(path="vector_db_v10")
qdrant = Qdrant(qdrant_client, COLLECTION_NAME, embeddings)

embeddings_version = 'v2' #For metadata searching

#This function takes query and the vectorized metadata keywords. Calculates the similarities and return the most similiar program codes.
def metadata_searcher(query, vectorized_df, program_codes, threshold = 0.50, top_n = 10):
    embeddings = SentenceTransformerEmbeddings(model_name=f'sentence-transformer-finetuned/georgebrown-{embeddings_version}-embeddings')
    #Creating an array to store maximum similarities of keywords for every row
    cosine_array = np.zeros(len(vectorized_df))
    vectorized_query = np.array(embeddings.embed_documents([query]))
    for rows in range(len(vectorized_df)):
        #This array will store the similarity scores for each key value in metada
        column_array = np.zeros(len(vectorized_df.columns))
        for index,column in enumerate(vectorized_df.columns):
            if vectorized_df[column].iloc[rows] == 'nan':
                pass
            else:
                column_array[index] = cosine_similarity(vectorized_query, np.array(vectorized_df[column].iloc[rows]))[0][0]             
        cosine_array[rows] = column_array.max()
    
    #Adding a scores column to program codes dataframe
    program_codes['Scores'] = cosine_array
    return_df = program_codes[program_codes['Scores'] > threshold].sort_values(by= 'Scores', ascending = False)
    return_df = return_df.drop_duplicates(subset = 'Program Information_Code', keep='first').head(top_n)
    return return_df['Program Information_Code'].tolist()

def metadata_vector_loader():
    vectorized_df = pd.read_csv(f'metadata_searcher/{embeddings_version}_vectorized_df.csv',index_col= 0,)
    program_codes = pd.read_csv(f'metadata_searcher/{embeddings_version}_program_codes.csv',index_col= 0)
    vectorized_df = vectorized_df.map(ast.literal_eval, na_action= 'ignore')
    vectorized_df = vectorized_df.fillna('nan')
    return vectorized_df,program_codes

def filter_year(query, filter):
    if '2024' in query:
        filter['year'] = 2024
        return filter
    if '2023' in query:
        filter['year'] = 2023
        return filter
    return filter


#return contexts with metadata aswell
def qdrant_search(query, vectorized_df, program_codes, threshold, top_n):
    contexts = []
    program_list = []
    program_list = metadata_searcher(query, vectorized_df, program_codes, threshold, top_n)
    if len(program_list) > 0:
        for program_code in program_list:
            for i in range(int(top_n/len(program_list))):
                filter = {'is_program_page': True, 'Program Information': {'Code': program_code}}
                filter = filter_year(query,filter)
                if i < len(qdrant.similarity_search(query, k= top_n, filter = filter)): #In case it returns less results
                    contexts.append(str(qdrant.similarity_search(query, k= top_n, filter = filter)[i].dict()))
        while i < (top_n - 1):
            i+=1
            filter = {'is_program_page': True, 'Program Information': {'Code': program_list[0]}} 
            filter = filter_year(query,filter)
            if i < len(qdrant.similarity_search(query, k= top_n, filter = filter)):
                contexts.append(str(qdrant.similarity_search(query, k= top_n, filter = filter)[i].dict()))
    else:
        for i in range(top_n):
            if i < len(qdrant.similarity_search(query, k= top_n)):
                contexts.append(str(qdrant.similarity_search(query, k= top_n)[i].dict()))
    return contexts

