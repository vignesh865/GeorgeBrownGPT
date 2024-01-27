import streamlit as st
from langchain_community.llms import Ollama
from langchain.memory import ConversationBufferWindowMemory

# Initialize the LangChain model with memory
base_url1 = "https://db08-34-80-135-129.ngrok-free.app"

# Initialize the LangChain model with memory
llm1 = Ollama(model="mistral", base_url=base_url1)
# Initialize chat history

st.title("GreogeBrownGPT")

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
            full_response = llm1.invoke(prompt)
            message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})