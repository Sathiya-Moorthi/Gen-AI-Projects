# ==================== DEPLOYMENT INSTRUCTIONS ====================
"""
DEPLOYMENT GUIDE
================

1. PROJECT STRUCTURE
   Create the following folder structure:
   
   fallback-rag-chatbot/
   ├── app.py
   ├── rag_engine.py
   ├── pdf_processor.py
   ├── web_search.py
   ├── evaluator.py
   ├── config.py
   ├── utils.py
   ├── requirements.txt
   └── vectorstore/  (will be created automatically)

2. INSTALLATION
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   
   # Install dependencies
   pip install -r requirements.txt

3. CONFIGURATION
   
   - Get HuggingFace API token from: https://huggingface.co/settings/tokens
   - (Optional) Get Tavily API key from: https://tavily.com
   
   Edit config.py to customize:
   - LLM model (default: Mistral-7B-Instruct)
   - Similarity threshold
   - Chunk sizes
   - Web search provider

4. RUNNING THE APP
   
   streamlit run app.py
   
   The app will open in your browser at http://localhost:8501

5. USAGE
   
   a. Enter your HuggingFace API token in the sidebar
   b. Upload PDF documents (multiple files supported)
   c. Wait for processing to complete
   d. Start asking questions!
   
   The system will automatically:
   - Search your PDFs first
   - Evaluate confidence scores
   - Fallback to web search if confidence is low
   - Provide detailed reasoning for each answer

6. CUSTOMIZATION
   
   All backend parameters are in config.py:
   - SIMILARITY_THRESHOLD: Controls when to use web fallback (default: 0.40)
   - CHUNK_SIZE: Document chunking size (default: 1500)
   - TOP_K_RETRIEVAL: Number of chunks to retrieve (default: 4)
   - LLM_MODEL: HuggingFace model to use
   
7. TROUBLESHOOTING
   
   - If LLM is slow: Use HuggingFace Inference API (requires token)
   - If embeddings fail: Check internet connection for model download
   - If PDFs won't process: Ensure they're not password-protected
   - If web search fails: Check DuckDuckGo availability or use Tavily

8. PRODUCTION DEPLOYMENT
   
   For Streamlit Cloud:
   - Push code to GitHub
   - Connect repository in Streamlit Cloud
   - Add HF_TOKEN to secrets.toml
   
   For Docker:
   - Create Dockerfile with Python 3.10+
   - Install dependencies
   - Expose port 8501
   - Run: docker run -p 8501:8501 fallback-rag

9. FEATURES
   
   ✅ Modular architecture (easy to maintain)
   ✅ Custom CSS styling (React-like UI)
   ✅ Persistent vector storage
   ✅ Automatic fallback logic
   ✅ Confidence scoring
   ✅ Source attribution
   ✅ Web search integration
   ✅ Multi-document support
   ✅ Open-source models (no OpenAI required)
   ✅ Session state management

10. NOTES
   
   - First run will download models (~400MB for embeddings)
   - Vector store persists in ./vectorstore/ directory
   - Chat history is session-based (not persisted)
   - Backend parameters are hardcoded (no UI controls)
   - Supports CPU inference (GPU optional for faster processing)

For issues or questions, check the logs or refer to:
- LangChain docs: https://python.langchain.com
- HuggingFace docs: https://huggingface.co/docs
- Streamlit docs: https://docs.streamlit.io
"""