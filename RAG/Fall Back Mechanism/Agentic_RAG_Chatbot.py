"""
Fallback RAG Chatbot with PDF & Web Search
Full LangChain + Streamlit Implementation

Installation:
pip install streamlit langchain langchain-community langchain-openai
pip install pypdf sentence-transformers chromadb
pip install tavily-python duckduckgo-search
pip install faiss-cpu tiktoken

Usage:
streamlit run app.py
"""

import streamlit as st
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import tempfile
import time

# LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_classic.chains import RetrievalQA
from langchain_classic.prompts import PromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.documents import Document

# Optional: Use Tavily for better web search
# from langchain_community.tools.tavily_search import TavilySearchResults


@dataclass
class RetrievalResult:
    """Container for retrieval results"""
    documents: List[Document]
    scores: List[float]
    max_score: float
    source_type: str  # 'pdf' or 'web'
    reasoning: str


class RetrievalEvaluator:
    """Evaluates retrieved documents and assigns confidence scores"""
    
    def __init__(self, similarity_threshold: float = 0.4):
        self.threshold = similarity_threshold
    
    def evaluate_relevance(
        self, 
        query: str, 
        documents: List[Document], 
        scores: List[float]
    ) -> Tuple[str, str]:
        """
        Determine if retrieval should use local docs or web search
        Returns: (decision: 'local' | 'web', reasoning: str)
        """
        if not documents or not scores:
            return 'web', "No documents found in vector store"
        
        max_score = max(scores)
        
        if max_score >= self.threshold:
            reasoning = (
                f"High semantic similarity ({max_score:.3f}) found in uploaded PDFs. "
                f"Score exceeds threshold ({self.threshold:.2f}), indicating strong relevance."
            )
            return 'local', reasoning
        else:
            reasoning = (
                f"Low PDF relevance (score: {max_score:.3f} < threshold: {self.threshold:.2f}). "
                f"Performing web search to obtain current and comprehensive information."
            )
            return 'web', reasoning


class QueryTransformer:
    """Refines queries for better retrieval results"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def transform_query(self, original_query: str, context: str = "") -> str:
        """
        Rewrite ambiguous queries for improved search results
        """
        prompt = f"""Given the user query: "{original_query}"
        
Rewrite this query to be more specific and search-friendly.
Keep it concise (1-2 sentences).
Focus on key concepts and important terms.

Refined query:"""
        
        try:
            response = self.llm.predict(prompt)
            return response.strip()
        except:
            # Fallback to original query
            return original_query


class FallbackRAG:
    """Main RAG system with automatic fallback to web search"""
    
    def __init__(
        self,
        llm,
        vectorstore: Optional[Chroma] = None,
        similarity_threshold: float = 0.4,
        top_k: int = 3
    ):
        self.llm = llm
        self.vectorstore = vectorstore
        self.evaluator = RetrievalEvaluator(similarity_threshold)
        self.transformer = QueryTransformer(llm)
        self.top_k = top_k
        
        # Initialize web search tool
        self.web_search = DuckDuckGoSearchRun()
        
        # For Tavily (better quality, requires API key):
        # self.web_search = TavilySearchResults(max_results=3)
    
    def update_vectorstore(self, vectorstore: Chroma):
        """Update the vector store with new documents"""
        self.vectorstore = vectorstore
    
    def _retrieve_from_pdf(self, query: str) -> RetrievalResult:
        """Retrieve documents from PDF vector store"""
        if not self.vectorstore:
            return RetrievalResult(
                documents=[],
                scores=[],
                max_score=0.0,
                source_type='web',
                reasoning="No PDF documents uploaded"
            )
        
        # Retrieve with scores
        retriever = self.vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": self.top_k,
                "score_threshold": 0.0  # Get all results to evaluate
            }
        )
        
        # Get documents with scores
        docs_and_scores = self.vectorstore.similarity_search_with_score(
            query, 
            k=self.top_k
        )
        
        if not docs_and_scores:
            return RetrievalResult(
                documents=[],
                scores=[],
                max_score=0.0,
                source_type='web',
                reasoning="No relevant documents found"
            )
        
        documents = [doc for doc, score in docs_and_scores]
        # Chromadb returns L2 distance, convert to similarity (inverse)
        # Lower distance = higher similarity
        scores = [1 / (1 + score) for doc, score in docs_and_scores]
        max_score = max(scores)
        
        # Evaluate if we should use these docs or fallback to web
        decision, reasoning = self.evaluator.evaluate_relevance(
            query, documents, scores
        )
        
        return RetrievalResult(
            documents=documents,
            scores=scores,
            max_score=max_score,
            source_type=decision,
            reasoning=reasoning
        )
    
    def _search_web(self, query: str) -> str:
        """Perform web search and return results"""
        try:
            # Transform query for better web search
            refined_query = self.transformer.transform_query(query)
            
            # Perform search
            results = self.web_search.run(refined_query)
            return results
        except Exception as e:
            return f"Web search failed: {str(e)}"
    
    def generate_answer(self, query: str) -> Dict:
        """
        Main method: Generate answer with automatic fallback
        Returns: {
            'answer': str,
            'source': 'pdf' | 'web',
            'confidence': float,
            'reasoning': str,
            'retrieved_docs': List[Document],
            'scores': List[float]
        }
        """
        # Step 1: Try PDF retrieval
        retrieval_result = self._retrieve_from_pdf(query)
        
        # Step 2: Decide and generate answer
        if retrieval_result.source_type == 'local':
            # Use PDF documents
            answer = self._generate_from_pdf(query, retrieval_result.documents)
            
            return {
                'answer': answer,
                'source': 'pdf',
                'confidence': retrieval_result.max_score,
                'reasoning': retrieval_result.reasoning,
                'retrieved_docs': retrieval_result.documents,
                'scores': retrieval_result.scores,
                'web_results': None
            }
        else:
            # Fallback to web search
            web_results = self._search_web(query)
            answer = self._generate_from_web(query, web_results)
            
            return {
                'answer': answer,
                'source': 'web',
                'confidence': retrieval_result.max_score,
                'reasoning': retrieval_result.reasoning,
                'retrieved_docs': retrieval_result.documents,
                'scores': retrieval_result.scores,
                'web_results': web_results
            }
    
    def _generate_from_pdf(self, query: str, documents: List[Document]) -> str:
        """Generate answer from PDF documents"""
        context = "\n\n".join([doc.page_content for doc in documents])
        
        prompt = f"""Based on the following context from uploaded PDF documents, answer the question.
If the context doesn't contain enough information, say so clearly.

Context:
{context}

Question: {query}

Answer:"""
        
        try:
            response = self.llm.predict(prompt)
            return response.strip()
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def _generate_from_web(self, query: str, web_results: str) -> str:
        """Generate answer from web search results"""
        prompt = f"""Based on the following web search results, answer the question.
Provide a clear and concise answer.

Web Search Results:
{web_results}

Question: {query}

Answer:"""
        
        try:
            response = self.llm.predict(prompt)
            return response.strip()
        except Exception as e:
            return f"Error generating answer: {str(e)}"


# ==================== Streamlit UI ====================

def init_session_state():
    """Initialize Streamlit session state"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'vectorstore' not in st.session_state:
        st.session_state.vectorstore = None
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'embeddings' not in st.session_state:
        st.session_state.embeddings = None


def load_embeddings():
    """Load HuggingFace embeddings model"""
    with st.spinner("Loading embedding model..."):
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    return embeddings


def process_pdfs(uploaded_files, embeddings, chunk_size: int, chunk_overlap: int):
    """Process uploaded PDFs and create vector store"""
    all_documents = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {uploaded_file.name}...")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name
        
        try:
            # Load PDF
            loader = PyPDFLoader(tmp_path)
            documents = loader.load()
            
            # Add metadata
            for doc in documents:
                doc.metadata['source'] = uploaded_file.name
            
            all_documents.extend(documents)
            
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
        
        progress_bar.progress((idx + 1) / len(uploaded_files))
    
    status_text.text("Splitting documents into chunks...")
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents(all_documents)
    
    status_text.text(f"Creating vector store with {len(chunks)} chunks...")
    
    # Create vector store
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="pdf_collection"
    )
    
    progress_bar.empty()
    status_text.empty()
    
    return vectorstore, len(chunks)


def display_message(message: Dict):
    """Display a chat message with metadata"""
    role = message['role']
    content = message['content']
    
    if role == 'user':
        with st.chat_message('user'):
            st.write(content)
    
    elif role == 'assistant':
        with st.chat_message('assistant'):
            st.write(content)
            
            metadata = message.get('metadata', {})
            
            if metadata:
                # Source badge
                source = metadata.get('source')
                if source == 'pdf':
                    st.success("📄 **Source:** PDF Documents")
                elif source == 'web':
                    st.warning("🌐 **Source:** Web Search")
                
                # Confidence score
                confidence = metadata.get('confidence', 0)
                if source == 'pdf':
                    st.info(f"🎯 **Confidence Score:** {confidence:.3f}")
                    st.progress(confidence)
                elif source == 'web' and confidence > 0:
                    threshold = metadata.get('threshold', 0.4)
                    st.info(f"📊 **PDF Confidence:** {confidence:.3f} (Below threshold: {threshold:.2f})")
                
                # Reasoning
                reasoning = metadata.get('reasoning')
                if reasoning:
                    with st.expander("💡 View Reasoning"):
                        st.write(reasoning)
                
                # Retrieved context
                retrieved_docs = metadata.get('retrieved_docs', [])
                scores = metadata.get('scores', [])
                
                if retrieved_docs and source == 'pdf':
                    with st.expander("📚 View Retrieved PDF Chunks"):
                        for idx, (doc, score) in enumerate(zip(retrieved_docs, scores)):
                            st.markdown(f"**Chunk {idx+1}** (Score: {score:.3f})")
                            st.markdown(f"*Source: {doc.metadata.get('source', 'Unknown')} - Page {doc.metadata.get('page', 'N/A')}*")
                            st.text_area(
                                f"Content {idx+1}", 
                                doc.page_content, 
                                height=100, 
                                key=f"chunk_{message.get('id', idx)}_{idx}",
                                disabled=True
                            )
                            st.divider()
                
                # Web results
                web_results = metadata.get('web_results')
                if web_results and source == 'web':
                    with st.expander("🌐 View Web Search Results"):
                        st.text_area("Results", web_results, height=200, disabled=True)


def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Fallback RAG Chatbot",
        page_icon="🤖",
        layout="wide"
    )
    
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Configuration")
        
        # API Key input
        st.subheader("API Keys")
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Required for LLM operations"
        )
        
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
        
        st.divider()
        
        # Model settings
        st.subheader("Model Settings")
        model_name = st.selectbox(
            "LLM Model",
            ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
            index=0
        )
        
        temperature = st.slider("Temperature", 0.0, 1.0, 0.1, 0.1)
        
        st.divider()
        
        # RAG settings
        st.subheader("RAG Settings")
        similarity_threshold = st.slider(
            "Confidence Threshold",
            0.0, 1.0, 0.4, 0.05,
            help="Higher = more web searches, Lower = more PDF answers"
        )
        
        top_k = st.slider("Top K Documents", 1, 10, 3)
        
        chunk_size = st.number_input("Chunk Size", 500, 3000, 1000, 100)
        chunk_overlap = st.number_input("Chunk Overlap", 0, 500, 200, 50)
        
        st.divider()
        
        # PDF Upload
        st.subheader("📄 Upload PDFs")
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=['pdf'],
            accept_multiple_files=True
        )
        
        if uploaded_files and uploaded_files != st.session_state.uploaded_files:
            if not api_key:
                st.error("Please enter your OpenAI API key first!")
            else:
                # Load embeddings if not already loaded
                if st.session_state.embeddings is None:
                    st.session_state.embeddings = load_embeddings()
                
                # Process PDFs
                vectorstore, num_chunks = process_pdfs(
                    uploaded_files,
                    st.session_state.embeddings,
                    chunk_size,
                    chunk_overlap
                )
                
                st.session_state.vectorstore = vectorstore
                st.session_state.uploaded_files = uploaded_files
                
                st.success(f"✅ Processed {len(uploaded_files)} PDF(s) into {num_chunks} chunks!")
                
                # Initialize RAG system
                llm = ChatOpenAI(
                    model_name=model_name,
                    temperature=temperature
                )
                
                st.session_state.rag_system = FallbackRAG(
                    llm=llm,
                    vectorstore=vectorstore,
                    similarity_threshold=similarity_threshold,
                    top_k=top_k
                )
        
        # Display uploaded files
        if st.session_state.uploaded_files:
            st.write("**Uploaded Files:**")
            for file in st.session_state.uploaded_files:
                st.write(f"- {file.name}")
        
        st.divider()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    
    # Main content
    st.title("🤖 Fallback RAG Chatbot")
    st.markdown("""
    Ask questions about your uploaded PDFs. The system automatically decides whether to answer 
    from your documents or search the web based on confidence scores.
    """)
    
    # Display chat messages
    for message in st.session_state.messages:
        display_message(message)
    
    # Chat input
    if prompt := st.chat_input("Ask a question..."):
        if not api_key:
            st.error("⚠️ Please enter your OpenAI API key in the sidebar!")
            st.stop()
        
        # Add user message
        st.session_state.messages.append({
            'role': 'user',
            'content': prompt,
            'id': len(st.session_state.messages)
        })
        
        with st.chat_message('user'):
            st.write(prompt)
        
        # Initialize RAG system if needed
        if st.session_state.rag_system is None:
            llm = ChatOpenAI(
                model_name=model_name,
                temperature=temperature
            )
            st.session_state.rag_system = FallbackRAG(
                llm=llm,
                vectorstore=st.session_state.vectorstore,
                similarity_threshold=similarity_threshold,
                top_k=top_k
            )
        else:
            # Update threshold if changed
            st.session_state.rag_system.evaluator.threshold = similarity_threshold
            st.session_state.rag_system.top_k = top_k
        
        # Generate response
        with st.chat_message('assistant'):
            with st.spinner("Thinking..."):
                result = st.session_state.rag_system.generate_answer(prompt)
                
                st.write(result['answer'])
                
                # Display metadata
                if result['source'] == 'pdf':
                    st.success("📄 **Source:** PDF Documents")
                elif result['source'] == 'web':
                    st.warning("🌐 **Source:** Web Search")
                
                # Confidence score
                if result['source'] == 'pdf':
                    st.info(f"🎯 **Confidence Score:** {result['confidence']:.3f}")
                    st.progress(result['confidence'])
                elif result['source'] == 'web' and result['confidence'] > 0:
                    st.info(f"📊 **PDF Confidence:** {result['confidence']:.3f} (Below threshold: {similarity_threshold:.2f})")
                
                # Reasoning
                if result['reasoning']:
                    with st.expander("💡 View Reasoning"):
                        st.write(result['reasoning'])
                
                # Retrieved context
                if result['retrieved_docs'] and result['source'] == 'pdf':
                    with st.expander("📚 View Retrieved PDF Chunks"):
                        for idx, (doc, score) in enumerate(zip(result['retrieved_docs'], result['scores'])):
                            st.markdown(f"**Chunk {idx+1}** (Score: {score:.3f})")
                            st.markdown(f"*Source: {doc.metadata.get('source', 'Unknown')} - Page {doc.metadata.get('page', 'N/A')}*")
                            st.text_area(
                                f"Content {idx+1}", 
                                doc.page_content, 
                                height=100,
                                key=f"chunk_response_{idx}",
                                disabled=True
                            )
                            st.divider()
                
                # Web results
                if result['web_results'] and result['source'] == 'web':
                    with st.expander("🌐 View Web Search Results"):
                        st.text_area("Results", result['web_results'], height=200, disabled=True)
        
        # Add assistant message
        st.session_state.messages.append({
            'role': 'assistant',
            'content': result['answer'],
            'metadata': {
                'source': result['source'],
                'confidence': result['confidence'],
                'reasoning': result['reasoning'],
                'retrieved_docs': result['retrieved_docs'],
                'scores': result['scores'],
                'web_results': result['web_results'],
                'threshold': similarity_threshold
            },
            'id': len(st.session_state.messages)
        })


if __name__ == "__main__":
    main()