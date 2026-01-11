# 📚 LangChain Learning Scripts

A collection of Jupyter notebooks covering core LangChain concepts from data ingestion to vector stores.

## 📁 Contents

| Notebook | Topic | Description |
|----------|-------|-------------|
| `Data_Ingestion_using_LangChain.ipynb` | Data Loading | Document loaders for PDF, text, and other formats |
| `Data_Transformation_using_LangChain.ipynb` | Text Processing | Text splitting, chunking, and transformation |
| `Embedding_LangChain.ipynb` | Embeddings | Text embeddings with OpenAI and HuggingFace |
| `Embedding_using_Grok.ipynb` | Embeddings | Alternative embeddings using Groq API |
| `Vector_Store.ipynb` | Vector Databases | Creating and querying FAISS and ChromaDB stores |

### Python Scripts

| File | Description |
|------|-------------|
| `Embedding_LangChain.py` | Standalone embedding example script |

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Jupyter Notebook or JupyterLab
- API keys for:
  - OpenAI (for most notebooks)
  - Groq (for Grok embedding notebook)

### Installation

1. **Install Jupyter**
   ```bash
   pip install jupyter
   ```

2. **Install dependencies** (run in each notebook as needed)
   ```bash
   pip install langchain langchain-openai langchain-community
   pip install langchain-huggingface sentence-transformers
   pip install faiss-cpu chromadb
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file with your API keys
   OPENAI_API_KEY=your_key_here
   GROQ_API_KEY=your_key_here
   ```

## 📖 Learning Path

Recommended order for beginners:

```mermaid
graph LR
    A[1. Data Ingestion] --> B[2. Data Transformation]
    B --> C[3. Embeddings]
    C --> D[4. Vector Stores]
```

1. **Data Ingestion** - Learn to load various document types
2. **Data Transformation** - Understand text chunking strategies
3. **Embeddings** - Convert text to numerical vectors
4. **Vector Stores** - Store and query embeddings efficiently

## ⚠️ Notes

- The `My_First_Vector_DB/` and `my_local_chroma_db/` folders contain generated vector database files and are excluded from version control
- Some notebooks may generate output files during execution
- Always restart the kernel and run all cells when testing

## 📦 Dependencies

- `langchain` - LLM orchestration framework
- `langchain-openai` - OpenAI integration
- `langchain-huggingface` - HuggingFace embeddings
- `faiss-cpu` - Facebook AI Similarity Search
- `chromadb` - ChromaDB vector database
- `sentence-transformers` - Sentence embeddings

---

**Part of the [LangChain Learning Repository](../README.md)**
