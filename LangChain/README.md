# 🦜🔗 LangChain Learning Repository

A comprehensive collection of **LangChain tutorials, scripts, and AI-powered applications** for learning and building with Large Language Models.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-Framework-green.svg)](https://langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

## 📁 Repository Structure

```
LangChain/
├── Projects/          # 6 production-ready AI applications
├── Script/            # Learning notebooks for LangChain concepts
├── Input Files/       # Sample input data for tutorials
└── output files/      # Generated outputs and screenshots
```

## 🚀 Projects

Production-ready AI applications built with LangChain and Streamlit:

| Project | Description |
|---------|-------------|
| [Code Assistant](./Projects/Code_Assistant/) | AI coding helper for writing, debugging, and explaining code |
| [Cover Letter Generator](./Projects/Cover_Letter_Generator/) | AI cover letter writer with company research |
| [Mock Interview App](./Projects/Mock_Interview_%20App/) | Interactive mock interview practice chatbot |
| [Simple Gen App](./Projects/Simple_Gen_App/) | Basic GenAI chatbot demonstrating LangChain fundamentals |
| [Smart Email Writer](./Projects/Smart_Email_Writer/) | Professional email generator with export options |
| [YouTube Video Summarizer](./Projects/Youtube_Video_Summarizer/) | YouTube video summarizer using transcripts |

## 📚 Learning Scripts

Jupyter notebooks covering core LangChain concepts:

| Script | Topic |
|--------|-------|
| `Data_Ingestion_using_LangChain.ipynb` | Document loading and data ingestion |
| `Data_Transformation_using_LangChain.ipynb` | Text splitting and transformation |
| `Embedding_LangChain.ipynb` | Text embeddings with OpenAI & HuggingFace |
| `Embedding_using_Grok.ipynb` | Embeddings using Groq API |
| `Vector_Store.ipynb` | Vector databases with FAISS and ChromaDB |

## 🛠️ Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Optional: Tavily, Groq API keys for specific projects

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sathiya-Moorthi/LangChain.git
   cd LangChain
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

3. **Navigate to a project and install dependencies**
   ```bash
   cd Projects/Code_Assistant
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

## 🎯 Learning Path

Recommended order for newcomers to LangChain:

1. 📖 Start with `Script/Data_Ingestion_using_LangChain.ipynb`
2. 🔄 Learn transformations with `Script/Data_Transformation_using_LangChain.ipynb`
3. 🧮 Understand embeddings with `Script/Embedding_LangChain.ipynb`
4. 🗃️ Explore vector stores with `Script/Vector_Store.ipynb`
5. 💬 Build your first chatbot with `Projects/Simple_Gen_App/`
6. 🚀 Graduate to advanced projects!

## 📦 Tech Stack

- **LLM Framework**: [LangChain](https://langchain.com/)
- **Frontend**: [Streamlit](https://streamlit.io/)
- **AI Providers**: [OpenAI](https://openai.com/), [Groq](https://groq.com/)
- **Vector Stores**: FAISS, ChromaDB
- **Embeddings**: OpenAI, HuggingFace

## 🤝 Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) for the amazing framework
- [Streamlit](https://streamlit.io/) for rapid UI development
- [OpenAI](https://openai.com/) for GPT models

---

**Happy Learning! 🎓** If you find this helpful, please ⭐ the repository!
