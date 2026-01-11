# GraphRAG

Experiments with Graph-based Retrieval-Augmented Generation.

## 📂 Projects

### [RAG_Battle](./RAG_Battle/)

A comprehensive RAG comparison system featuring:
- **Vector RAG**: Embeddings stored in PostgreSQL (pgvector)
- **Knowledge Graph**: Structured relationships in Neo4j
- **Smart Synthesis**: GPT-4o comparison and synthesis
- **Web Fallback**: DuckDuckGo search when local knowledge is insufficient

## 🚀 Overview

GraphRAG combines knowledge graphs with LLMs to improve:
- **Retrieval Accuracy**: Structured relationships provide better context
- **Multi-hop Reasoning**: Follow connections between entities
- **Hallucination Reduction**: Grounded answers from verified knowledge

## 🛠️ Tech Stack

- **LlamaIndex** - Orchestration framework
- **Neo4j** - Graph database
- **PostgreSQL + pgvector** - Vector storage
- **OpenAI GPT-4o** - Language model
- **Streamlit** - Web interface

## 📚 Getting Started

See [RAG_Battle/README.md](./RAG_Battle/README.md) for detailed setup instructions.
