# ==================== FILE: utils.py ====================
"""
Utility functions for the RAG chatbot
"""

import time
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def format_confidence_badge(confidence: float) -> tuple:
    """
    Return badge text and color based on confidence score
    Returns: (badge_text, color_class)
    """
    if confidence >= 0.6:
        return ("HIGH", "success")
    elif confidence >= 0.4:
        return ("MEDIUM", "warning")
    else:
        return ("LOW", "error")


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to max_length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def format_sources(documents: List, scores: List[float]) -> str:
    """Format retrieved documents as HTML"""
    html = ""
    for idx, (doc, score) in enumerate(zip(documents, scores)):
        source = doc.metadata.get('source', 'Unknown')
        page = doc.metadata.get('page', 'N/A')
        
        html += f"""
        <div class="source-chunk">
            <div class="chunk-header">
                <span class="chunk-number">Chunk {idx + 1}</span>
                <span class="chunk-score">Score: {score:.3f}</span>
            </div>
            <div class="chunk-meta">📄 {source} - Page {page}</div>
            <div class="chunk-content">{doc.page_content[:300]}...</div>
        </div>
        """
    return html


def estimate_tokens(text: str) -> int:
    """Rough token estimation (1 token ≈ 4 chars)"""
    return len(text) // 4


def validate_pdf_file(file) -> bool:
    """Validate uploaded file is a PDF"""
    return file.name.lower().endswith('.pdf')