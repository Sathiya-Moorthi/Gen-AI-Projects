import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Sidebar for API Key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("Enter your OpenAI API Key:", type="password")
    if not api_key:
        st.warning("Please enter your OpenAI API Key in the sidebar or add it to a `.env` file.")
        st.stop()  # Stop execution until key is provided
    else:
        os.environ["OPENAI_API_KEY"] = api_key
        st.sidebar.success("✅ API Key set from input")
else:
    st.sidebar.success("✅ API Key loaded from `.env`")

# ✅ Define prompt with conversation history
prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a helpful AI assistant. Your responses should be:\n"
     "- Clear and concise\n"
     "- Helpful and informative\n"
     "- Professional yet friendly\n"
     "- Factually accurate\n"
     "- Focused on the user's needs"
    ),
    MessagesPlaceholder(variable_name="history"),  # ← for chat history
    ("human", "{input}")  # ← user input
])

# ✅ Initialize LLM (modern ChatOpenAI, not legacy OpenAI)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# ✅ Build chain
chain = prompt | llm | StrOutputParser()

# ✅ Use StreamlitChatMessageHistory (auto-syncs with st.session_state)
history = StreamlitChatMessageHistory(key="chat_history")

# ✅ Wrap chain with message history
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: history,  # Always return the same history
    input_messages_key="input",
    history_messages_key="history",
)

# 🎯 Streamlit UI
st.title("💬 GenAI Chatbot")
st.caption("Powered by LangChain + OpenAI 🚀")

# Display chat messages
for msg in history.messages:
    role = "user" if msg.type == "human" else "assistant"
    with st.chat_message(role):
        st.write(msg.content)

# Input & response
if prompt_input := st.chat_input("Ask me anything..."):
    # Display user message
    with st.chat_message("user"):
        st.write(prompt_input)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chain_with_history.invoke(
                {"input": prompt_input},
                config={"configurable": {"session_id": "any"}}  # required for RunnableWithMessageHistory
            )
        st.write(response)