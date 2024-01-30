import streamlit as st
import pyperclip
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
	return output #Currently it is not a text

# Function to handle predefined commands
def handle_predefined_commands(prompt):
    if prompt.lower() == 'exit':
        return 'Sure, exiting now. Have a great one.'
    elif prompt == '' or prompt is None:
        return 'Please provide an input'
    else:
        return None  # No predefined command matched


st.sidebar.image("logo.svg",use_column_width="always")
# st.sidebar.markdown("[Visit GBC Website](https://www.georgebrown.ca)")

# Add introduction text box in the sidebar
st.sidebar.title("GeorgeBrownGPT")
st.sidebar.title("Introduction")
st.sidebar.write("Welcome to the George Brown GPT QA Chatbot!")
st.sidebar.write("This chatbot is built for the George Brown College website.You can inquire about anything related to GBC.")

st.title("GeorgeBrownGPT")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    predefined_response = handle_predefined_commands(prompt)
    if predefined_response:
        # Display predefined response in chat message container
        with st.chat_message("assistant"):
            st.markdown(predefined_response)
        # Add predefined response to chat history
        st.session_state.messages.append({"role": "assistant", "content": predefined_response})
    else:
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner('Thinking..'):
                top_n_contexts = get_query_return_context(prompt, vectorized_df,program_codes,threshold = 0.5, top_n = 5)
                full_response = print_output(prompt, top_n_contexts)
                message_placeholder.markdown(full_response)

                # Add like/unlike buttons
                col1, col2, col3 = st.columns(3, gap='small')
                if col1.button("Copy "):
                    pyperclip.copy(full_response)
                    st.write("Assistant reply copied to clipboard!")
                if col2.button("👍"):
                    st.write("User liked the response!")
                if col3.button("👎"):
                    st.write("User unliked the response!")

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})