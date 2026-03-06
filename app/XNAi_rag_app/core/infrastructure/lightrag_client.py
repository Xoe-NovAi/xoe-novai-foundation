"""
XNAi LightRAG Client - Relational & Structural Retrieval
=========================================================

Provides high-efficiency, local knowledge graph retrieval using LightRAG.
Supports PostgreSQL backend for persistent, on-disk graph storage.

Features:
- Dual-level retrieval (Low-level entities + High-level themes)
- Incremental indexing of new documents
- Optimized for local LLMs (Qwen, Krikri)
- 99% token reduction compared to standard GraphRAG
"""

import anyio
import logging
import os
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import LightRAG (optional)
try:
    from lightrag import LightRAG, QueryParam
    LIGHTRAG_AVAILABLE = True
except ImportError:
    LIGHTRAG_AVAILABLE = False
    LightRAG = None
    QueryParam = None
    logger.warning("LightRAG not available - relational search disabled")


@dataclass
class LightRAGConfig:
    working_dir: str = "./storage/data/lightrag"
    postgres_uri: Optional[str] = None
    llm_model: str = "ilsp/llama-krikri-8b-instruct"
    embedding_model: str = "all-MiniLM-L6-v2"
    mode: str = "hybrid"  # naive, local, global, hybrid


class LightRAGClient:
    """
    Client for LightRAG-based knowledge graph retrieval.
    """

    def __init__(self, config: Optional[LightRAGConfig] = None):
        self.config = config or LightRAGConfig()
        self.rag = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize LightRAG with Postgres storage"""
        if not LIGHTRAG_AVAILABLE:
            return False

        if self._initialized:
            return True

        try:
            # Set environment variables for LightRAG Postgres backend
            if self.config.postgres_uri:
                os.environ["POSTGRES_URI"] = self.config.postgres_uri

            # Initialize LightRAG
            # In a real implementation, we'd wrap the local LLM/embedding functions
            from app.XNAi_rag_app.core.dependencies import get_llm_complete, get_embeddings_func
            
            self.rag = LightRAG(
                working_dir=self.config.working_dir,
                kv_storage="PGKVStorage",
                doc_status_storage="PGDocStatusStorage",
                graph_storage="PGGraphStorage",
                vector_storage="PGVectorStorage",
                llm_model_func=get_llm_complete,
                embedding_func=get_embeddings_func
            )
            
            self._initialized = True
            logger.info("LightRAG client initialized with PostgreSQL backend")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize LightRAG: {e}")
            return False

    async def query(self, text: str, mode: Optional[str] = None) -> str:
        """Perform a graph-based query"""
        if not self._initialized or not self.rag:
            return ""
        
        mode = mode or self.config.mode
        try:
            param = QueryParam(mode=mode)
            return await self.rag.aquery(text, param=param)
        except Exception as e:
            logger.error(f"LightRAG query failed: {e}")
            return ""

    async def insert(self, content: str):
        """Incrementally index a document"""
        if not self._initialized or not self.rag:
            return False
        
        try:
            await self.rag.ainsert(content)
            return True
        except Exception as e:
            logger.error(f"LightRAG insertion failed: {e}")
            return False
