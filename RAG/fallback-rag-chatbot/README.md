# Fallback RAG Chatbot

A production-ready RAG (Retrieval-Augmented Generation) chatbot with intelligent fallback mechanisms.

## ✨ Features

- **PDF Processing**: Upload and process multiple PDF documents
- **Vector Search**: FAISS-based similarity search
- **Confidence Scoring**: Evaluates retrieval quality
- **Web Fallback**: Automatically searches the web when local retrieval is insufficient
- **Open-Source Models**: Uses HuggingFace models (no OpenAI required)
- **Streamlit UI**: Clean, interactive chat interface

## 🏗️ Architecture

```
fallback-rag-chatbot/
├── app.py              # Main Streamlit application
├── rag_engine.py       # RAG pipeline and retrieval logic
├── pdf_processor.py    # PDF processing and chunking
├── web_search.py       # Web search fallback (DuckDuckGo/Tavily)
├── evaluator.py        # Confidence scoring and evaluation
├── config.py           # Configuration settings
├── utils.py            # Utility functions
├── styles.css          # Custom UI styling
└── vectorstore/        # Persistent vector database
```

## 🚀 Quick Start

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

### Brief Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app**:
   ```bash
   streamlit run app.py
   ```

3. **Configure**: Enter your HuggingFace token in the sidebar, upload PDFs, and start chatting!

## ⚙️ Configuration

Edit `config.py` to customize:
- `SIMILARITY_THRESHOLD`: When to trigger web fallback (default: 0.40)
- `CHUNK_SIZE`: Document chunk size (default: 1500)
- `TOP_K_RETRIEVAL`: Number of chunks to retrieve (default: 4)
- `LLM_MODEL`: HuggingFace model to use

## 📦 Dependencies

- `langchain` - RAG framework
- `streamlit` - Web UI
- `faiss-cpu` - Vector similarity search
- `sentence-transformers` - Embeddings
- `duckduckgo-search` - Web search fallback
