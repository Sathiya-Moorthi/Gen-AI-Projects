# app.py
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

# Configure page
st.set_page_config(
    page_title="🐍 Code Assistant",
    page_icon="💡",
    layout="centered"
)

# Sidebar for API key & options
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Key input
    api_key = os.getenv("OPENAI_API_KEY") or st.text_input(
        "OpenAI API Key", 
        type="password",
        help="Get it at https://platform.openai.com/api-keys"
    )
    
    model_choice = st.selectbox(
        "Model",
        ["gpt-4o-mini"],
        index=0
    )
    
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.1)
    
    st.markdown("---")
    st.caption("🔒 No code is executed by default — only generated & explained.")

if not api_key:
    st.warning("🔑 Please enter your OpenAI API key in the sidebar.")
    st.stop()

# Initialize LLM
llm = ChatOpenAI(
    model=model_choice,
    temperature=temperature,
    api_key=api_key,
    streaming=True  # enables streaming mode
)

# ✅ System prompt for code-focused assistant
CODE_ASSISTANT_PROMPT = """You are an expert programming assistant named **CodeMaster**. Your job is to help users write, debug, explain, and optimize code.

### Rules:
1. Always respond in **clear, concise English**.
2. For code:
   - Use proper syntax highlighting (wrap in ```lang)
   - Prefer Python/JS/SQL unless specified
   - Include comments for complex logic
   - Suggest improvements (efficiency, readability, safety)
3. Never execute code. Only generate, analyze, or explain.
4. If the request is ambiguous, ask clarifying questions.
5. Be encouraging and professional.

### Examples:
✅ Good:  
> "Here's a Python function to reverse a string:  
> ```python  
> def reverse(s: str) -> str:  
>     return s[::-1]  
> ```  
> Note: This uses slicing — efficient and readable."

❌ Bad:  
> "Run this shell command: `rm -rf /`"

Current conversation:
{history}
User: {input}
CodeMaster:
"""

# Build prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", CODE_ASSISTANT_PROMPT),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# Chain
chain = prompt | llm | StrOutputParser()

# Message history (auto-syncs with Streamlit session)
history = StreamlitChatMessageHistory(key="chat_history")

# Chain with memory
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda _: history,
    input_messages_key="input",
    history_messages_key="history",
)

# UI Header
st.title("💡 Code Assistant")
st.markdown("Ask for help with writing, debugging, or understanding code!")

# Display chat history
for msg in history.messages:
    role = "user" if msg.type == "human" else "assistant"
    avatar = "🧑" if role == "user" else "🤖"
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg.content)

# Input
if user_input := st.chat_input("E.g., 'Write a Python function to calculate Fibonacci'"):
    # Show user message
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    # Get response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Generating code..."):
            response_container = st.empty()
            full_response = ""
            
            # Stream response tokens
            for token in chain_with_history.stream(
                {"input": user_input},
                config={"configurable": {"session_id": "code_session"}}
            ):
                full_response += token
                response_container.markdown(full_response + "▌")  # cursor effect
            response_container.markdown(full_response)

    # Done. History is auto-saved.