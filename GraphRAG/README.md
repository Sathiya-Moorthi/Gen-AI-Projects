# GraphRAG

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.0+-green.svg)](https://neo4j.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-purple.svg)](https://openai.com/)

Experiments with Graph-based Retrieval-Augmented Generation, combining knowledge graphs with LLMs for enhanced context retrieval.

## Project Structure

```
GraphRAG/
├── RAG_Battle/         # Comprehensive RAG comparison system
│   ├── Vector RAG (PostgreSQL + pgvector)
│   ├── Knowledge Graph (Neo4j)
│   └── Smart Synthesis (GPT-4o)
├── .env.example        # Environment template
└── README.md
```

## Projects

### [RAG_Battle](./RAG_Battle/)

A comprehensive RAG comparison system featuring:
- **Vector RAG**: Embeddings stored in PostgreSQL (pgvector)
- **Knowledge Graph**: Structured relationships in Neo4j
- **Smart Synthesis**: GPT-4o comparison and synthesis
- **Web Fallback**: DuckDuckGo search when local knowledge is insufficient

## Why GraphRAG?

| Traditional RAG | GraphRAG |
|----------------|----------|
| Flat vector search | Structured relationships |
| Single-hop retrieval | Multi-hop reasoning |
| Context windows | Connected knowledge |
| May hallucinate | Grounded in verified data |

## Tech Stack

- **LlamaIndex** - Orchestration framework
- **Neo4j** - Graph database
- **PostgreSQL + pgvector** - Vector storage
- **OpenAI GPT-4o** - Language model
- **Streamlit** - Web interface

## Prerequisites

- Python 3.8+
- Neo4j Database (local or cloud)
- PostgreSQL with pgvector extension
- OpenAI API key

## Installation

1. Navigate to this directory:
   ```bash
   cd GraphRAG
   ```

2. Copy environment template:
   ```bash
   cp .env.example .env
   ```

3. Configure your credentials in `.env`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

See `.env.example` for required environment variables:
- `NEO4J_URI` - Neo4j connection string
- `NEO4J_USER` - Database username
- `NEO4J_PASSWORD` - Database password
- `OPENAI_API_KEY` - OpenAI API key

## Getting Started

See [RAG_Battle/README.md](./RAG_Battle/README.md) for detailed setup instructions.

## License

This project is part of [Gen-AI-Projects](../README.md) and is licensed under the MIT License.
