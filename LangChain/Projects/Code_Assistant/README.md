# 💡 Code Assistant

An AI-powered **coding assistant** built with LangChain and Streamlit that helps you write, debug, explain, and optimize code.

## ✨ Features

- 🤖 **Smart Code Generation**: Write code in multiple languages with proper syntax highlighting
- 🐛 **Debugging Help**: Get assistance identifying and fixing bugs
- 📝 **Code Explanation**: Understand complex code with clear explanations
- 💬 **Conversation Memory**: Context-aware follow-up questions
- ⚡ **Streaming Responses**: Real-time token-by-token output
- 🎛️ **Configurable**: Adjustable temperature and model selection

## 🏗️ Architecture

```
Code_Assistant/
├── app.py              # Main application with LangChain integration
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
   cd Code_Assistant
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

### Example Prompts

- "Write a Python function to calculate Fibonacci numbers"
- "Debug this code: [paste your code]"
- "Explain how async/await works in JavaScript"
- "Optimize this SQL query for better performance"

## ⚙️ Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| Model | GPT model to use | gpt-4o-mini |
| Temperature | Response creativity (0.0-1.0) | 0.2 |

## 📦 Dependencies

- `streamlit` - Web application framework
- `langchain` - LLM orchestration
- `langchain-openai` - OpenAI integration
- `langchain-community` - Community integrations
- `python-dotenv` - Environment variable management

## 📄 License

MIT License - See [LICENSE](../LICENSE) for details.

---

**Built with 🦜🔗 LangChain & Streamlit**
