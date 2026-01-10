# 💬 Simple Gen App

A **basic GenAI chatbot** demonstrating LangChain fundamentals with conversation memory and Streamlit UI.

## ✨ Features

- 🤖 **AI Chat**: Conversational AI powered by GPT-4o-mini
- 💬 **Conversation Memory**: Context-aware responses across messages
- 🎨 **Clean UI**: Simple, intuitive Streamlit interface
- 🔐 **Flexible API Key**: Load from `.env` or enter in sidebar
- ⚡ **Fast Responses**: Efficient LangChain chain execution

## 🏗️ Architecture

```
Simple_Gen_App/
├── app.py              # Main chatbot application
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md           # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- OpenAI API key

### Setup

1. **Navigate to the project directory**
   ```bash
   cd Simple_Gen_App
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   copy .env.example .env
   # Edit .env and add your OpenAI API key
   ```

## 🎮 Usage

Start the application:
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

### How to Use

1. Enter your message in the chat input
2. Receive AI responses in real-time
3. Continue the conversation with follow-up questions
4. Previous messages are remembered for context

## 📦 Dependencies

- `streamlit` - Web application framework
- `langchain` - LLM orchestration
- `langchain-openai` - OpenAI integration
- `langchain-community` - Community integrations
- `python-dotenv` - Environment variable management

## 🎓 Learning Points

This project demonstrates:
- LangChain prompt templates with `ChatPromptTemplate`
- Conversation memory using `StreamlitChatMessageHistory`
- Chain composition with `RunnableWithMessageHistory`
- Output parsing with `StrOutputParser`

## 📄 License

MIT License - See [LICENSE](../LICENSE) for details.

---

**Built with 🦜🔗 LangChain & Streamlit**
