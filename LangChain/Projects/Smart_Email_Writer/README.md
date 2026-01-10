# ✉️ Smart Email Writer

A professional **AI email generator** with tone customization and multiple export options, built with LangChain and Streamlit.

## ✨ Features

- 📝 **Two Input Modes**: Quick builder with guided fields or freeform description
- 🎭 **Tone Options**: Formal, Friendly, Urgent, Empathetic, or Persuasive
- 📋 **9 Email Purposes**: Follow-ups, applications, sales, support, and more
- ⚡ **Streaming Output**: Watch your email generate in real-time
- 📥 **Multiple Export Options**:
  - Download as `.txt`
  - Download as `.eml` (open in email client)
  - Copy to clipboard
- ✏️ **Live Editing**: Edit the draft before exporting
- 🔒 **Privacy First**: 100% client-side, no data stored

## 🏗️ Architecture

```
Smart_Email_Writer/
├── app.py              # Main application with LangChain
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
   cd Smart_Email_Writer
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

### Quick Builder Mode
1. Select email purpose (e.g., "Follow-up after meeting")
2. Choose tone (e.g., "Friendly")
3. Add key details (Who? What? Why? Deadline?)
4. Click "Generate Email"

### Freeform Mode
Describe your email need naturally, e.g.:
> "Write a polite but urgent email to the client PM about delayed deliverables. We're 2 days late due to a third-party API issue. Offer a revised deadline and a discount."

## ⚙️ Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| Model | GPT model to use | gpt-4o-mini |
| Temperature | Creativity (0.0-1.0) | 0.3 |

## 📦 Dependencies

- `streamlit` - Web application framework
- `langchain` - LLM orchestration
- `langchain-openai` - OpenAI integration
- `python-dotenv` - Environment variable management

## 📄 License

MIT License - See [LICENSE](../LICENSE) for details.

---

**Built with 🦜🔗 LangChain & Streamlit**
