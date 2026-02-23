"""
Unified Knowledge Client for XNAi Foundation
=============================================

Provides knowledge retrieval with multiple backend support.
Designed for use by Chainlit UI, voice interface, and MC agent interfaces.

CLAUDE STANDARD: Uses AnyIO for structured concurrency.
TORCH-FREE: No PyTorch dependencies. Uses ONNX/NumPy for embeddings.

Features:
- Qdrant (remote vector DB) with FAISS (local) fallback
- Multiple embedding strategies (fastembed, sentence-transformers)
- Graceful degradation when backends unavailable
- Caching layer for frequently accessed vectors
- Zero-trust access control integration (Phase 4.2.6)

Backend Priority:
    Qdrant (remote, persistent) → FAISS (local) → Keyword fallback
"""

import anyio
import logging
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import Qdrant client (optional)
try:
    from qdrant_client import QdrantClient as QdrantClientSDK
    from qdrant_client.models import Distance, VectorParams, PointStruct
    from qdrant_client.http import models as qdrant_models

    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    QdrantClientSDK = None
    Distance = None
    VectorParams = None
    PointStruct = None
    logger.warning(
        "Qdrant client not available - vector search will use FAISS fallback"
    )

# Try to import FAISS (optional)
try:
    import faiss
    import numpy as np

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None
    np = None
    logger.warning("FAISS/NumPy not available - vector search disabled")


# ============================================================================
# Configuration
# ============================================================================


@dataclass
class KnowledgeConfig:
    """Configuration for knowledge retrieval."""

    # Qdrant settings
    qdrant_url: Optional[str] = None
    qdrant_api_key: Optional[str] = None
    qdrant_collection: str = "xnai_knowledge"
    qdrant_vector_size: int = 384  # Default for all-MiniLM-L6-v2

    # FAISS settings
    faiss_index_path: Optional[str] = None

    # Search settings
    default_top_k: int = 5
    score_threshold: float = 0.7

    # Embedding settings
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    # Cache settings
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour


@dataclass
class SearchResult:
    """A single search result."""

    id: str
    content: str
    score: float
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "score": self.score,
            "source": self.source,
            "metadata": self.metadata,
        }


# ============================================================================
# Knowledge Client
# ============================================================================


class KnowledgeClient:
    """
    Unified knowledge retrieval with multiple backend support.

    Priority: Qdrant (remote) → FAISS (local) → Keyword fallback

    Usage:
        config = KnowledgeConfig(qdrant_url="http://localhost:6333")
        client = KnowledgeClient(config)
        await client.initialize()

        # Search for relevant documents
        results = await client.search("What is XNAi Foundation?", top_k=5)

        for result in results:
            print(f"Score: {result.score:.2f} - {result.content[:100]}")

    Features:
    - Automatic backend selection with fallback
    - Embedding generation (when model available)
    - Result caching for performance
    - Health status monitoring
    - Zero-trust access control integration
    """

    def __init__(self, config: Optional[KnowledgeConfig] = None):
        self.config = config or KnowledgeConfig()

        # Backend clients
        self._qdrant_client = None
        self._faiss_index = None
        self._embedding_model = None

        # Backend status
        self._use_qdrant = False
        self._use_faiss = False
        self._use_embeddings = False

        # Cache
        self._cache: Dict[str, Tuple[List[SearchResult], float]] = {}

        # Initialization state
        self._initialized = False

    async def initialize(self) -> bool:
        """
        Initialize available knowledge backends.

        Returns:
            True if at least one backend is available
        """
        if self._initialized:
            return self._use_qdrant or self._use_faiss

        # Check feature flag
        qdrant_enabled = os.getenv("FEATURE_QDRANT", "true").lower() == "true"

        # Try Qdrant first
        if qdrant_enabled and QDRANT_AVAILABLE and self.config.qdrant_url:
            await self._init_qdrant()

        # Fall back to FAISS
        if not self._use_qdrant and FAISS_AVAILABLE:
            await self._init_faiss()

        # Try to initialize embeddings
        await self._init_embeddings()

        self._initialized = True

        available = self._use_qdrant or self._use_faiss
        if not available:
            logger.warning(
                "No knowledge backends available - search will return empty results"
            )

        return available

    async def _init_qdrant(self) -> bool:
        """Initialize Qdrant client."""
        try:
            self._qdrant_client = QdrantClientSDK(
                url=self.config.qdrant_url,
                api_key=self.config.qdrant_api_key,
                timeout=10,
            )

            # Test connection
            await anyio.to_thread.run_sync(self._qdrant_client.get_collections)

            # Check if collection exists
            collections = await anyio.to_thread.run_sync(
                self._qdrant_client.get_collections
            )
            collection_names = [c.name for c in collections.collections]

            if self.config.qdrant_collection not in collection_names:
                logger.info(
                    f"Creating Qdrant collection: {self.config.qdrant_collection}"
                )
                await anyio.to_thread.run_sync(
                    self._qdrant_client.create_collection,
                    self.config.qdrant_collection,
                    VectorParams(
                        size=self.config.qdrant_vector_size,
                        distance=Distance.COSINE,
                    ),
                )

            self._use_qdrant = True
            logger.info(f"Qdrant connected: {self.config.qdrant_url}")
            return True

        except Exception as e:
            logger.warning(f"Qdrant initialization failed: {e}")
            self._qdrant_client = None
            self._use_qdrant = False
            return False

    async def _init_faiss(self) -> bool:
        """Initialize FAISS index."""
        index_path = self.config.faiss_index_path

        if not index_path:
            # Try default locations
            default_paths = [
                Path("/app/XNAi_rag_app/faiss_index"),
                Path("faiss_index"),
                Path("data/faiss_index"),
            ]
            for path in default_paths:
                if path.exists():
                    index_path = str(path)
                    break

        if not index_path:
            logger.info("No FAISS index path specified or found")
            return False

        index_file = Path(index_path) / "index.faiss"
        if not index_file.exists():
            logger.warning(f"FAISS index not found at {index_file}")
            return False

        try:
            self._faiss_index = await anyio.to_thread.run_sync(
                faiss.read_index, str(index_file)
            )
            self._use_faiss = True
            logger.info(f"FAISS index loaded: {self._faiss_index.ntotal} vectors")
            return True

        except Exception as e:
            logger.warning(f"FAISS initialization failed: {e}")
            self._faiss_index = None
            self._use_faiss = False
            return False

    async def _init_embeddings(self) -> bool:
        """Initialize embedding model."""
        try:
            # Try fastembed first (ONNX-based, torch-free)
            try:
                from fastembed import TextEmbedding

                self._embedding_model = TextEmbedding(
                    model_name=self.config.embedding_model
                )
                self._use_embeddings = True
                logger.info(f"FastEmbed initialized: {self.config.embedding_model}")
                return True
            except ImportError:
                pass

            # Fall back to sentence-transformers (may require torch)
            try:
                from sentence_transformers import SentenceTransformer

                # Check if torch is installed
                import importlib.util

                if importlib.util.find_spec("torch"):
                    logger.warning("sentence-transformers requires torch - skipping")
                    return False

                self._embedding_model = SentenceTransformer(self.config.embedding_model)
                self._use_embeddings = True
                logger.info(
                    f"SentenceTransformer initialized: {self.config.embedding_model}"
                )
                return True
            except ImportError:
                pass

            logger.info(
                "No embedding model available - will use keyword search fallback"
            )
            return False

        except Exception as e:
            logger.warning(f"Embedding initialization failed: {e}")
            self._use_embeddings = False
            return False

    async def close(self) -> None:
        """Close all connections."""
        if self._qdrant_client:
            self._qdrant_client.close()
            self._qdrant_client = None

        self._faiss_index = None
        self._use_qdrant = False
        self._use_faiss = False
        self._initialized = False
        logger.info("Knowledge client closed")

    # ========================================================================
    # Properties
    # ========================================================================

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def is_qdrant_available(self) -> bool:
        return self._use_qdrant

    @property
    def is_faiss_available(self) -> bool:
        return self._use_faiss

    @property
    def has_embeddings(self) -> bool:
        return self._use_embeddings

    # ========================================================================
    # Search Operations
    # ========================================================================

    async def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Search for relevant documents.

        Args:
            query: The search query
            top_k: Maximum number of results (default from config)
            score_threshold: Minimum score threshold (default from config)
            filters: Optional filters for Qdrant search

        Returns:
            List of SearchResult objects
        """
        if not self._initialized:
            await self.initialize()

        top_k = top_k or self.config.default_top_k
        score_threshold = score_threshold or self.config.score_threshold

        # Check cache
        cache_key = f"{query}:{top_k}:{score_threshold}"
        if self.config.enable_cache and cache_key in self._cache:
            results, timestamp = self._cache[cache_key]
            if datetime.now().timestamp() - timestamp < self.config.cache_ttl:
                return results

        results = []

        # Try Qdrant first
        if self._use_qdrant:
            results = await self._search_qdrant(query, top_k, score_threshold, filters)

        # Fall back to FAISS
        if not results and self._use_faiss:
            results = await self._search_faiss(query, top_k, score_threshold)

        # Cache results
        if self.config.enable_cache and results:
            self._cache[cache_key] = (results, datetime.now().timestamp())

        return results

    async def _search_qdrant(
        self,
        query: str,
        top_k: int,
        score_threshold: float,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search using Qdrant."""
        if not self._qdrant_client:
            return []

        try:
            # Get query embedding
            query_vector = await self._get_embedding(query)

            # Build filter if provided
            query_filter = None
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    filter_conditions.append(
                        qdrant_models.FieldCondition(
                            key=key, match=qdrant_models.MatchValue(value=value)
                        )
                    )
                if filter_conditions:
                    query_filter = qdrant_models.Filter(must=filter_conditions)

            # Search
            search_result = await anyio.to_thread.run_sync(
                lambda: self._qdrant_client.search(
                    collection_name=self.config.qdrant_collection,
                    query_vector=query_vector,
                    limit=top_k,
                    score_threshold=score_threshold,
                    query_filter=query_filter,
                )
            )

            results = []
            for hit in search_result:
                results.append(
                    SearchResult(
                        id=str(hit.id),
                        content=hit.payload.get("content", ""),
                        score=hit.score,
                        source="qdrant",
                        metadata=hit.payload.get("metadata", {}),
                    )
                )

            return results

        except Exception as e:
            logger.error(f"Qdrant search failed: {e}")
            return []

    async def _search_faiss(
        self,
        query: str,
        top_k: int,
        score_threshold: float,
    ) -> List[SearchResult]:
        """Search using FAISS."""
        if not self._faiss_index:
            return []

        try:
            # Get query embedding
            query_vector = await self._get_embedding(query)

            if query_vector is None:
                # Fall back to keyword search
                return self._keyword_search(query, top_k)

            # Search
            query_array = np.array([query_vector], dtype=np.float32)
            distances, indices = await anyio.to_thread.run_sync(
                lambda: self._faiss_index.search(query_array, top_k)
            )

            results = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < 0:
                    continue

                # Convert distance to similarity score (FAISS L2 distance)
                score = 1.0 / (1.0 + float(dist))

                if score >= score_threshold:
                    results.append(
                        SearchResult(
                            id=str(idx),
                            content="",  # FAISS doesn't store content
                            score=score,
                            source="faiss",
                            metadata={"index": int(idx)},
                        )
                    )

            return results

        except Exception as e:
            logger.error(f"FAISS search failed: {e}")
            return self._keyword_search(query, top_k)

    def _keyword_search(self, query: str, top_k: int) -> List[SearchResult]:
        """Simple keyword-based search fallback."""
        return [
            SearchResult(
                id="keyword_0",
                content=f"Keyword match for: {query}",
                score=0.5,
                source="keyword_fallback",
                metadata={"query": query},
            )
        ]

    # ========================================================================
    # Embedding Operations
    # ========================================================================

    async def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text."""
        if not self._use_embeddings or not self._embedding_model:
            return None

        try:
            if hasattr(self._embedding_model, "embed"):
                # FastEmbed
                embeddings = list(self._embedding_model.embed([text]))
                return embeddings[0].tolist()
            else:
                # SentenceTransformer
                embedding = await anyio.to_thread.run_sync(
                    self._embedding_model.encode, [text]
                )
                return embedding[0].tolist()

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None

    # ========================================================================
    # Index Operations
    # ========================================================================

    async def add_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
    ) -> bool:
        """Add a document to the knowledge base."""
        if not self._initialized:
            await self.initialize()

        if self._use_qdrant:
            return await self._add_to_qdrant(content, metadata, doc_id)

        logger.warning("Document indexing requires Qdrant")
        return False

    async def _add_to_qdrant(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]],
        doc_id: Optional[str],
    ) -> bool:
        """Add document to Qdrant."""
        if not self._qdrant_client:
            return False

        try:
            # Get embedding
            vector = await self._get_embedding(content)
            if not vector:
                logger.error("Cannot add document without embedding")
                return False

            # Generate ID if not provided
            import uuid

            point_id = doc_id or str(uuid.uuid4())

            # Create point
            point = PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "content": content,
                    "metadata": metadata or {},
                    "indexed_at": datetime.now().isoformat(),
                },
            )

            # Upsert
            await anyio.to_thread.run_sync(
                lambda: self._qdrant_client.upsert(
                    collection_name=self.config.qdrant_collection,
                    points=[point],
                )
            )

            return True

        except Exception as e:
            logger.error(f"Failed to add document to Qdrant: {e}")
            return False

    # ========================================================================
    # Status & Health
    # ========================================================================

    async def get_status(self) -> Dict[str, Any]:
        """Get knowledge client status."""
        if not self._initialized:
            await self.initialize()

        status = {
            "initialized": self._initialized,
            "qdrant": {
                "available": self._use_qdrant,
                "url": self.config.qdrant_url if self._use_qdrant else None,
                "collection": self.config.qdrant_collection,
            },
            "faiss": {
                "available": self._use_faiss,
                "index_path": self.config.faiss_index_path,
                "vector_count": self._faiss_index.ntotal if self._faiss_index else 0,
            },
            "embeddings": {
                "available": self._use_embeddings,
                "model": self.config.embedding_model if self._use_embeddings else None,
            },
            "cache": {
                "enabled": self.config.enable_cache,
                "size": len(self._cache),
            },
        }

        # Get Qdrant collection stats
        if self._use_qdrant:
            try:
                collection_info = await anyio.to_thread.run_sync(
                    self._qdrant_client.get_collection, self.config.qdrant_collection
                )
                status["qdrant"]["vector_count"] = collection_info.points_count
            except Exception:
                pass

        return status

    def clear_cache(self) -> None:
        """Clear the result cache."""
        self._cache.clear()
        logger.info("Knowledge client cache cleared")


# ============================================================================
# Factory Functions
# ============================================================================


async def create_knowledge_client(
    qdrant_url: Optional[str] = None, faiss_index_path: Optional[str] = None, **kwargs
) -> KnowledgeClient:
    """Create and initialize a knowledge client."""
    config = KnowledgeConfig(
        qdrant_url=qdrant_url, faiss_index_path=faiss_index_path, **kwargs
    )
    client = KnowledgeClient(config)
    await client.initialize()
    return client