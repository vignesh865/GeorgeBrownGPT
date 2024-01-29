import streamlit as st
from langchain_community.llms import Ollama
from langchain.memory import ConversationBufferWindowMemory

import random
import pyperclip

# Initialize the LangChain model with memory
base_url1 = "https://db08-34-80-135-129.ngrok-free.app"

# Initialize the LangChain model with memory
llm1 = Ollama(model="mistral", base_url=base_url1)
# Initialize chat history



# Dummy replies
dummy_responses = [
    "I'm sorry, I don't have that information.",
    "Sure, let me find that for you!",
    "Interesting question! Here's what I know...",
    "I'm still learning, but I'll do my best to help.",
    "I'm not sure about that. Would you like assistance with something else?",
]

# Function to get a random dummy response
def get_random_response():
    return random.choice(dummy_responses)

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

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner('Thinking..'):
            # full_response = llm1.invoke(prompt)
            full_response = get_random_response()
            message_placeholder.markdown(full_response)

            # Add like/unlike buttons
            col1, col2 ,col3 = st.columns(3,gap='small')
            if col1.button("Copy "):
                pyperclip.copy(str(full_response))
                st.write("Assistant reply copied to clipboard!")
            if col2.button("👍"):
                st.write("User liked the response!")
            if col3.button("👎"):
                st.write("User unliked the response!")

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})