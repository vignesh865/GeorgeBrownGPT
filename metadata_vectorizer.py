import pandas as pd
from langchain_community.embeddings import SentenceTransformerEmbeddings
import os
from tqdm import tqdm

#This script needs to be run to create vectorized metadata table. 
#It saves the necessary csv files into metadata_searcer folder
#Takes around 6 minutes.

embeddings_version = 'v2'

folder_path = 'output_csv_files_all_keys'
embeddings = SentenceTransformerEmbeddings(model_name=f'sentence-transformer-finetuned/georgebrown-{embeddings_version}-embeddings')

# Get a list of all CSV files in the folder
csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

concatenated_df = pd.DataFrame()

for file in csv_files:
    file_path = os.path.join(folder_path, file)
    df = pd.read_csv(file_path)
    concatenated_df = pd.concat([concatenated_df, df], ignore_index=True)

def remove_special_chars(text):
    # Using regex to remove special characters
    return ''.join(e for e in text if e.isalnum() or e == ' ')

vectorized_df = concatenated_df.copy()
vectorized_df = vectorized_df.astype(str)
vectorized_df = vectorized_df.map(remove_special_chars)

def create_embeddings(question):
    return embeddings.embed_documents([question])

for column in tqdm(vectorized_df.columns):
    for index in range(len(vectorized_df)):
        if vectorized_df[column].iloc[index].lower() == 'nan':
            pass
        else:
            vectorized_df[column].iloc[index] = create_embeddings(vectorized_df[column].iloc[index])


vectorized_df.to_csv(f'metadata_searcher/{embeddings_version}_vectorized_df.csv')
concatenated_df['Program Information_Code'].to_csv(f'metadata_searcher/{embeddings_version}_program_codes.csv')