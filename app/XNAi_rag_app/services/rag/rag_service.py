#!/usr/bin/env python3
# ============================================================================
# Xoe-NovAi Phase 1 v0.1.0-alpha - RAG Orchestration Service
# ============================================================================

import time
import logging
from typing import List, Tuple, Dict, Any, Optional
from ...core.config_loader import get_config_value, load_config
from ...core.logging_config import get_logger, PerformanceLogger
from ...core.metrics import record_rag_retrieval, record_error

logger = get_logger(__name__)
CONFIG = load_config()

class RAGService:
    """
    Sovereign RAG Orchestration Service.
    Handles document retrieval, context truncation, and prompt construction.
    """
    
    def __init__(self, vectorstore: Any):
        self.vectorstore = vectorstore
        self.perf_logger = PerformanceLogger(logger)
        
    async def retrieve_context(
        self,
        query: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        max_context_chars: Optional[int] = None,
        per_doc_chars: Optional[int] = None
    ) -> Tuple[str, List[str]]:
        """
        Retrieve relevant documents from vectorstore with performance tracking.
        """
        if not self.vectorstore:
            logger.warning("Vectorstore not initialized, skipping RAG")
            return "", []
        
        top_k = top_k or get_config_value('rag.top_k', 5)
        
        try:
            start_time = time.time()
            # Async FAISS similarity search
            docs = await self.vectorstore.asimilarity_search(query, k=top_k)
            retrieval_ms = (time.time() - start_time) * 1000
            
            record_rag_retrieval(retrieval_ms)
            
            if not docs:
                logger.warning(f"No documents retrieved for query: {query[:50]}...")
                return "", []
            
            context, sources = self._build_truncated_context(docs, max_context_chars, per_doc_chars)
            
            logger.info(f"Retrieved {len(sources)} documents in {retrieval_ms:.2f}ms")
            return context, sources
            
        except Exception as e:
            logger.error(f"RAG retrieval failed: {e}", exc_info=True)
            record_error("rag_retrieval", "vectorstore")
            return "", []

    def _build_truncated_context(
        self, 
        docs: List[Any], 
        max_context_chars: Optional[int] = None,
        per_doc_chars: Optional[int] = None
    ) -> Tuple[str, List[str]]:
        """
        Enforce strict character limits to maintain CPU/RAM targets.
        """
        per_doc_limit = per_doc_chars or get_config_value('performance.per_doc_chars', 500)
        total_limit = max_context_chars or get_config_value('performance.total_chars', 2048)
        
        context_parts = []
        sources = []
        current_length = 0
        
        for doc in docs:
            content = doc.page_content[:per_doc_limit]
            source = doc.metadata.get("source", "unknown")
            
            entry = f"\n[Source: {source}]\n{content}\n"
            if current_length + len(entry) > total_limit:
                break
                
            context_parts.append(entry)
            current_length += len(entry)
            if source not in sources:
                sources.append(source)
                
        return "".join(context_parts), sources

    @staticmethod
    def generate_prompt(query: str, context: str = "") -> str:
        """
        Construct Ma'at Aligned prompt.
        """
        if context:
            return f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer (based only on context):"
        return f"Question: {query}\n\nAnswer:"
