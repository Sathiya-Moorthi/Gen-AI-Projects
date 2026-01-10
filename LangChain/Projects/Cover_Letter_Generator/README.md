# 📄 Cover Letter Generator

An AI-powered **cover letter generator** with integrated company research, built with LangChain, Tavily, and Streamlit.

## ✨ Features

- 📝 **Two Input Modes**: Guided quick builder or freeform description
- 🌐 **Company Research**: Optional Tavily integration for real-time company insights
- 🎨 **Tone Customization**: Professional, Enthusiastic, Confident, or Humble
- ⚡ **Streaming Output**: Watch your cover letter generate in real-time
- 📥 **Easy Export**: Download as .txt or copy to clipboard
- 🔒 **Privacy First**: All data stays local

## 🏗️ Architecture

```
Cover_Letter_Generator/
├── app.py              # Main application with LangChain + Tavily
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md           # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- OpenAI API key
- Tavily API key (optional, for company research)

### Setup

1. **Navigate to the project directory**
   ```bash
   cd Cover_Letter_Generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   copy .env.example .env
   # Edit .env and add your API keys
   ```

## 🎮 Usage

Start the application:
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

### Quick Builder Mode
1. Fill in Job Title, Company Name, and Tone
2. Paste the job description
3. Add your background/resume highlights
4. Click "Generate Cover Letter"

### Freeform Mode
Describe your situation naturally, e.g.:
> "Applying to Stripe for Growth PM role. I have 4 years in fintech, grew MRR by 200%. Love their mission. Want confident tone."

## ⚙️ Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | ✅ Yes |
| `TAVILY_API_KEY` | Tavily API key for research | ❌ Optional |

## 📦 Dependencies

- `streamlit` - Web application framework
- `langchain` - LLM orchestration
- `langchain-openai` - OpenAI integration
- `langchain-tavily` - Tavily search integration
- `python-dotenv` - Environment variable management

## 📄 License

MIT License - See [LICENSE](../LICENSE) for details.

---

**Built with 🦜🔗 LangChain, 🔍 Tavily & Streamlit**
