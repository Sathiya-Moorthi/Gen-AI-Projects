# ==================== FILE: web_search.py ====================
"""
Web Search Fallback Module
Handles web search when PDF confidence is low
"""

from typing import List, Dict, Optional
from langchain_community.tools import DuckDuckGoSearchRun
import config
from utils import logger


class WebSearchFallback:
    """Handles web search fallback functionality"""
    
    def __init__(self, llm=None):
        self.llm = llm
        self.search_tool = DuckDuckGoSearchRun()
        # For Tavily: from langchain_community.tools.tavily_search import TavilySearchResults
        # self.search_tool = TavilySearchResults(max_results=config.WEB_SEARCH_RESULTS_COUNT)
    
    def refine_query(self, original_query: str) -> str:
        """
        Transform query for better web search results
        Uses LLM to refine the query if available
        """
        if self.llm is None:
            return original_query
        
        prompt = f"""Rewrite the following question to be more specific and search-engine friendly.
Keep it concise (1-2 sentences). Focus on key concepts.

Original question: {original_query}

Refined search query:"""
        
        try:
            refined = self.llm.predict(prompt)
            logger.info(f"Refined query: {original_query} -> {refined}")
            return refined.strip()
        except Exception as e:
            logger.warning(f"Query refinement failed: {str(e)}")
            return original_query
    
    def search(self, query: str, refine: bool = True) -> Dict:
        """
        Perform web search
        
        Returns:
            {
                'results': str (formatted results),
                'refined_query': str,
                'sources': List[Dict] (if available)
            }
        """
        # Refine query if requested
        search_query = self.refine_query(query) if refine and self.llm else query
        
        try:
            # Perform search
            results = self.search_tool.run(search_query)
            
            logger.info(f"Web search completed for: {search_query}")
            
            return {
                'results': results,
                'refined_query': search_query,
                'sources': []  # DuckDuckGo doesn't provide structured sources
            }
            
        except Exception as e:
            logger.error(f"Web search failed: {str(e)}")
            return {
                'results': f"Web search encountered an error: {str(e)}",
                'refined_query': search_query,
                'sources': []
            }