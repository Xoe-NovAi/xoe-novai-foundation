"""
XNAi Query Rewriter - Intelligent Retrieval Expansion
======================================================

Provides autonomous query rewriting for improved RAG performance.
Uses local SLMs to transform vague queries into search-optimized terms.

Features:
- Semantic expansion
- Keyword decomposition
- Multi-perspective rewriting
"""

import logging
from typing import List

logger = logging.getLogger(__name__)

class QueryRewriter:
    """
    Transforms user queries for better vector/graph retrieval.
    """

    def __init__(self, model_func=None):
        self.model_func = model_func

    async def rewrite(self, query: str) -> List[str]:
        """
        Generate multiple search-optimized versions of a query.
        """
        prompt = f"""
        TASK: Rewrite the following user QUERY to improve search retrieval in a technical knowledge base.
        Generate 3 variations:
        1. KEYWORDS: Extract key technical terms.
        2. EXPANDED: A more detailed version including synonyms.
        3. QUESTION: A clearly phrased technical question.
        
        QUERY: {query}
        
        Format your response as a simple list.
        """

        if not self.model_func:
            # Fallback/Mock
            return [query, f"technical details of {query}", f"how does {query} work"]

        try:
            response = await self.model_func(prompt)
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"Rewriter model failed: {e}")
            return [query]

    def _parse_response(self, response: str) -> List[str]:
        """Simple line-based parser for the rewritten queries"""
        lines = response.strip().split("
")
        queries = []
        for line in lines:
            # Remove numbering or bullet points
            cleaned = line.strip().lstrip("1234567890. -*")
            if cleaned and len(cleaned) > 3:
                queries.append(cleaned)
        return queries[:3]
