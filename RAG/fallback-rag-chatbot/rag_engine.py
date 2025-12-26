# ==================== FILE: rag_engine.py ====================
"""
RAG Engine Module
Core retrieval and generation logic with fallback mechanism
"""

from typing import Dict, List, Optional
import streamlit as st
from langchain_community.llms import HuggingFaceHub
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from evaluator import RetrievalEvaluator
from web_search import WebSearchFallback
import config
from utils import logger


class RAGEngine:
    """Main RAG engine with automatic fallback logic"""
    
    def __init__(self, vectorstore: Optional[Chroma] = None, hf_token: Optional[str] = None):
        self.vectorstore = vectorstore
        self.evaluator = RetrievalEvaluator()
        
        # Initialize LLM
        if hf_token:
            self.llm = HuggingFaceHub(
                repo_id=config.LLM_MODEL,
                model_kwargs={
                    "temperature": config.LLM_TEMPERATURE,
                    "max_new_tokens": config.MAX_NEW_TOKENS
                },
                huggingfacehub_api_token=hf_token
            )
        else:
            self.llm = None
            logger.warning("No HuggingFace token provided - LLM features limited")
        
        # Initialize web search
        self.web_search = WebSearchFallback(self.llm)
    
    def update_vectorstore(self, vectorstore: Chroma):
        """Update the vector store reference"""
        self.vectorstore = vectorstore
    
    def retrieve_documents(self, query: str) -> tuple:
        """
        Retrieve relevant documents from vector store
        
        Returns: (documents, scores)
        """
        if not self.vectorstore:
            return [], []
        
        try:
            # Retrieve with scores
            docs_and_scores = self.vectorstore.similarity_search_with_score(
                query,
                k=config.TOP_K_RETRIEVAL
            )
            
            if not docs_and_scores:
                return [], []
            
            # Separate documents and scores
            documents = [doc for doc, score in docs_and_scores]
            # Convert L2 distance to similarity (inverse)
            scores = [1 / (1 + score) for doc, score in docs_and_scores]
            
            logger.info(f"Retrieved {len(documents)} documents with scores: {[f'{s:.3f}' for s in scores]}")
            
            return documents, scores
            
        except Exception as e:
            logger.error(f"Retrieval failed: {str(e)}")
            return [], []
    
    def generate_from_pdf(self, query: str, documents: List[Document]) -> str:
        """Generate answer from PDF documents"""
        if not self.llm:
            # Fallback to simple context extraction
            context = "\n\n".join([doc.page_content[:500] for doc in documents[:2]])
            return f"Based on the uploaded documents:\n\n{context}\n\n[Note: Full generation requires HuggingFace API token]"
        
        context = "\n\n".join([doc.page_content for doc in documents])
        
        prompt = f"""Based on the following context from uploaded PDF documents, provide a clear and comprehensive answer to the question.

Context:
{context[:2000]}

Question: {query}

Answer (be specific and detailed):"""
        
        try:
            answer = self.llm.predict(prompt)
            return answer.strip()
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            return f"Error generating answer from PDF: {str(e)}"
    
    def generate_from_web(self, query: str, web_results: str) -> str:
        """Generate answer from web search results"""
        if not self.llm:
            return f"Based on web search:\n\n{web_results[:800]}\n\n[Note: Full generation requires HuggingFace API token]"
        
        prompt = f"""Based on the following web search results, provide a clear and comprehensive answer to the question.

Web Search Results:
{web_results[:2000]}

Question: {query}

Answer (be specific and cite sources where possible):"""
        
        try:
            answer = self.llm.predict(prompt)
            return answer.strip()
        except Exception as e:
            logger.error(f"Web generation failed: {str(e)}")
            return f"Error generating answer from web: {str(e)}"
    
    def query(self, user_query: str) -> Dict:
        """
        Main query method with automatic fallback
        
        Returns: {
            'answer': str,
            'source': 'pdf' | 'web' | 'both',
            'confidence': float,
            'reasoning': str,
            'grade': str,
            'retrieved_docs': List[Document],
            'scores': List[float],
            'web_results': Optional[Dict]
        }
        """
        # Step 1: Retrieve from PDF
        documents, scores = self.retrieve_documents(user_query)
        
        # Step 2: Evaluate confidence
        decision, reasoning, grade = self.evaluator.evaluate_retrieval(
            user_query, documents, scores
        )
        
        max_score = max(scores) if scores else 0.0
        
        # Step 3: Generate answer based on decision
        if decision == 'pdf':
            # High/medium confidence - use PDF
            answer = self.generate_from_pdf(user_query, documents)
            
            return {
                'answer': answer,
                'source': 'pdf',
                'confidence': max_score,
                'reasoning': reasoning,
                'grade': grade,
                'retrieved_docs': documents,
                'scores': scores,
                'web_results': None
            }
        
        else:
            # Low confidence - fallback to web
            web_data = self.web_search.search(user_query)
            answer = self.generate_from_web(user_query, web_data['results'])
            
            return {
                'answer': answer,
                'source': 'web',
                'confidence': max_score,
                'reasoning': reasoning,
                'grade': grade,
                'retrieved_docs': documents,
                'scores': scores,
                'web_results': web_data
            }
