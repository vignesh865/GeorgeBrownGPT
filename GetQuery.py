from colorama import Fore, Back, Style
import qdrantsearch #it is a local file (qdrantsearch.py)

from hugchat import hugchat
from hugchat.login import Login

# Log in to huggingface and grant authorization to huggingchat
file = open("/Users/aliguneysel/Desktop/password.txt", "r").readlines()
email = file[0].replace('\n','')
password = file[1].replace('\n','')
sign = Login(email, password)
cookies = sign.login()


vectorized_df, program_codes = qdrantsearch.metadata_vector_loader()

#Input sentence
def get_query_return_context(query, vectorized_df,program_codes,threshold, top_n):
	top_n_contexts = qdrantsearch.qdrant_search(query, vectorized_df, program_codes, threshold, top_n)
	top_n_contexts_string = '\n'.join(top_n_contexts)
	return top_n_contexts_string


def print_output(query, top_n_context):
	chatbot = hugchat.ChatBot(cookies=cookies.get_dict()) 
	#					Just give the exact answer, 
	#				without adding any comment or mentioning about the contexts you recieved. 
	instruction = '''Provide a concise and accurate answer to the given input text, 
					considering the most relevant context among those presented. 
					If there is no related context, you must answer it by your knowledge.
					Do not mention about contexts, just give the answer.'''
	output = chatbot.query(f'{instruction}\nInput:{query}\nContext:{top_n_context}.')
	print(Fore.MAGENTA + Back.LIGHTWHITE_EX + 'GeorgeBrownGPT: ' + output + Style.RESET_ALL)
	print('\n')
	return output #Currently it is not a text



print(Fore.MAGENTA + Back.LIGHTWHITE_EX + 'Welcome to the GeorgeBrownGPT, how may I assist you today?' + Style.RESET_ALL + '\n')
while True:
	query = input(Fore.BLACK + Back.LIGHTWHITE_EX + 'You: ')
	print(Style.RESET_ALL)
	if query.lower() == 'exit':
		print(Fore.MAGENTA + Back.LIGHTWHITE_EX + 'Sure, exiting now. Have a great one.' + Style.RESET_ALL)
		break
	elif query == '' or query == None:
		print(Fore.MAGENTA + Back.LIGHTWHITE_EX + 'Please provide an input' + Style.RESET_ALL)
	else:	
		top_n_contexts = get_query_return_context(query, vectorized_df,program_codes,threshold = 0.5, top_n = 5)
		answer = print_output(query, top_n_contexts)

