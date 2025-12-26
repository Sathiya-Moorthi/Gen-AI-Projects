# ==================== FILE: config.py ====================
"""
Configuration settings for Fallback RAG Chatbot
All parameters are hardcoded here - no user adjustments in frontend
"""

import os

# RAG Settings
SIMILARITY_THRESHOLD = 0.40
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 300
TOP_K_RETRIEVAL = 4

# Model Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"  # or "meta-llama/Llama-2-7b-chat-hf"
LLM_TEMPERATURE = 0.7
MAX_NEW_TOKENS = 512

# Vector Database
VECTOR_DB_PATH = "./vectorstore"
COLLECTION_NAME = "pdf_documents"

# Web Search
WEB_SEARCH_PROVIDER = "duckduckgo"  # or "tavily"
WEB_SEARCH_RESULTS_COUNT = 5

# UI Settings
APP_TITLE = "🤖 Fallback RAG Chatbot"
APP_DESCRIPTION = "Intelligent document Q&A with automatic web search fallback"

# Confidence Levels
CONFIDENCE_HIGH = 0.6
CONFIDENCE_MEDIUM = 0.4
CONFIDENCE_LOW = 0.0