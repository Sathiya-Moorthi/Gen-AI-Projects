# 🦜🔗 LangChain Projects Collection

A curated collection of **AI-powered applications** built with [LangChain](https://langchain.com/) and [Streamlit](https://streamlit.io/), demonstrating modern LLM integration patterns.

## 📁 Projects

| Project | Description | Key Features |
|---------|-------------|--------------|
| [Code_Assistant](./Code_Assistant/) | AI coding helper for writing, debugging, and explaining code | Streaming responses, conversation memory |
| [Cover_Letter_Generator](./Cover_Letter_Generator/) | AI cover letter writer with company research | Tavily integration, tone customization |
| [Mock_Interview_App](./Mock_Interview_%20App/) | Interactive mock interview practice chatbot | Role-based questions, instant feedback |
| [Simple_Gen_App](./Simple_Gen_App/) | Basic GenAI chatbot demonstrating LangChain fundamentals | Conversation history, clean architecture |
| [Smart_Email_Writer](./Smart_Email_Writer/) | Professional email generator with export options | Multiple tones, .eml export, clipboard copy |
| [Youtube_Video_Summarizer](./Youtube_Video_Summarizer/) | YouTube video summarizer using transcripts | Auto transcript extraction, downloadable summaries |

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Optional: Tavily API key for Cover Letter Generator ([Get one here](https://app.tavily.com))

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LangChain/Projects
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

3. **Navigate to a project and install dependencies**
   ```bash
   cd Code_Assistant
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   copy .env.example .env
   # Edit .env and add your API keys
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 🛠️ Tech Stack

- **LLM Framework**: [LangChain](https://langchain.com/)
- **Frontend**: [Streamlit](https://streamlit.io/)
- **AI Provider**: [OpenAI](https://openai.com/) (GPT-4o-mini)
- **Research API**: [Tavily](https://tavily.com/) (optional)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

**Built with ❤️ using LangChain & Streamlit**
