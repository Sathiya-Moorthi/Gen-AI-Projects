# ==================== FILE: evaluator.py ====================
"""
Retrieval Evaluator Module
Evaluates document relevance and generates confidence scores
"""

from typing import List, Tuple
from langchain_core.documents import Document
import config
from utils import logger


class RetrievalEvaluator:
    """Evaluates retrieved documents and assigns confidence scores"""
    
    def __init__(self):
        self.threshold = config.SIMILARITY_THRESHOLD
    
    def calculate_relevance_grade(self, score: float) -> str:
        """Assign relevance grade based on score"""
        if score >= config.CONFIDENCE_HIGH:
            return "HIGH"
        elif score >= config.CONFIDENCE_MEDIUM:
            return "MEDIUM"
        else:
            return "LOW"
    
    def evaluate_retrieval(
        self, 
        query: str,
        documents: List[Document],
        scores: List[float]
    ) -> Tuple[str, str, str]:
        """
        Evaluate if retrieval should use PDF or trigger web search
        
        Returns: 
            - decision: 'pdf' | 'web' | 'both'
            - reasoning: str (explanation)
            - grade: 'HIGH' | 'MEDIUM' | 'LOW'
        """
        if not documents or not scores:
            return (
                'web',
                "No documents found in vector store. Performing web search for external information.",
                'LOW'
            )
        
        max_score = max(scores)
        grade = self.calculate_relevance_grade(max_score)
        
        # Get source information
        top_doc = documents[0]
        source_file = top_doc.metadata.get('source', 'Unknown')
        source_page = top_doc.metadata.get('page', 'N/A')
        
        if max_score >= config.CONFIDENCE_HIGH:
            reasoning = (
                f"High semantic similarity ({max_score:.3f}) detected in uploaded document. "
                f"Strong match found in '{source_file}' (Page {source_page}). "
                f"Answer extracted from local knowledge base with high confidence."
            )
            decision = 'pdf'
        
        elif max_score >= config.CONFIDENCE_MEDIUM:
            reasoning = (
                f"Medium relevance ({max_score:.3f}) found in '{source_file}'. "
                f"Score meets threshold ({self.threshold:.2f}) but indicates moderate confidence. "
                f"Answer provided from PDF with caveat that information may be partial."
            )
            decision = 'pdf'
        
        else:
            reasoning = (
                f"Low PDF relevance (score: {max_score:.3f} < threshold: {self.threshold:.2f}). "
                f"Insufficient confidence in uploaded documents. "
                f"Performing web search to obtain current, comprehensive information not available in local PDFs."
            )
            decision = 'web'
        
        logger.info(f"Evaluation: {decision.upper()} | Score: {max_score:.3f} | Grade: {grade}")
        
        return decision, reasoning, grade