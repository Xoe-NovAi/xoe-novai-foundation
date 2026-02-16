#!/usr/bin/env python3
# ============================================================================
# Xoe-NovAi Shadow Cache Manager (v1.0.0)
# ============================================================================
# Purpose: Multi-tiered hybrid vector architecture (FAISS + Qdrant)
# Performance: Tier 1 hot cache (<5k vectors) using IndexIVFPQ
# Concurrency: AnyIO TaskGroups with 0.95 similarity threshold early-exit
# Sovereignty: Redis-backed invalidation bus (xnai:vector_updates)
# ============================================================================

import anyio
import faiss
import numpy as np
import logging
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from qdrant_client.async_client import AsyncQdrantClient
from qdrant_client.http import models as rest
from .circuit_breakers.redis_state import RedisConnectionManager

logger = logging.getLogger(__name__)

class ShadowCacheManager:
    """
    Orchestrates hybrid vector search between Tier 1 (FAISS Hot) 
    and Tier 2 (Qdrant Cold).
    """
    
    def __init__(
        self, 
        qdrant_url: str,
        dimension: int = 1536, # Default for OpenAI / BGE-Large
        hot_limit: int = 5000,
        similarity_threshold: float = 0.95,
        redis_uri: Optional[str] = None
    ):
        self.qdrant_url = qdrant_url
        self.dimension = dimension
        self.hot_limit = hot_limit
        self.similarity_threshold = similarity_threshold
        
        # FAISS IndexIVFPQ: M=48 sub-quantizers, 100 centroids
        self.quantizer = faiss.IndexFlatL2(dimension)
        self.faiss_index = faiss.IndexIVFPQ(self.quantizer, dimension, 100, 48, 8)
        self.faiss_index.nprobe = 10
        
        # Local metadata storage for FAISS
        self.faiss_metadata = {}
        self.faiss_ids = []
        
        # Clients
        self.qdrant = AsyncQdrantClient(url=qdrant_url)
        self.redis = RedisConnectionManager(redis_url=redis_uri) if redis_uri else None
        
        self._is_trained = False
        logger.info(f"ShadowCacheManager initialized (Dim: {dimension}, Threshold: {similarity_threshold})")

    async def add_to_hot_cache(self, vectors: np.ndarray, ids: List[str], metadata: List[Dict]):
        """Adds vectors to the Tier 1 FAISS cache."""
        if not self._is_trained:
            logger.info("Training FAISS IVFPQ index...")
            # We need at least some data to train. In production, 
            # we'd use a representative sample.
            self.faiss_index.train(vectors.astype('float32'))
            self._is_trained = True
            
        self.faiss_index.add_with_ids(
            vectors.astype('float32'), 
            np.array([hash(id_str) % (2**63 - 1) for id_str in ids])
        )
        
        for i, id_str in enumerate(ids):
            h_id = hash(id_str) % (2**63 - 1)
            self.faiss_metadata[h_id] = metadata[i]
            self.faiss_ids.append(h_id)
            
        # Enforce limit (FIFO)
        if len(self.faiss_ids) > self.hot_limit:
            to_remove = self.faiss_ids[:len(self.faiss_ids) - self.hot_limit]
            # FAISS doesn't support easy removal from IVFPQ without rebuilding,
            # so we track active IDs in the metadata.
            for rid in to_remove:
                self.faiss_metadata.pop(rid, None)
            self.faiss_ids = self.faiss_ids[len(self.faiss_ids) - self.hot_limit:]

    async def search(self, query_vector: np.ndarray, k: int = 5) -> List[Dict]:
        """
        Performs concurrent search across FAISS and Qdrant.
        Early exits if FAISS score > similarity_threshold.
        """
        results = []
        query_np = query_vector.astype('float32').reshape(1, -1)
        
        async with anyio.create_task_group() as tg:
            # We use a CancelScope to stop Qdrant lookup if FAISS hits the threshold
            scope = anyio.CancelScope()
            
            async def faiss_lookup():
                with scope:
                    start_time = time.time()
                    faiss_temp_results = []
                    try:
                        distances, indices = await anyio.to_thread.run_sync(
                            self.faiss_index.search, query_np, k
                        )
                        for dist, idx in zip(distances[0], indices[0]):
                            if idx in self.faiss_metadata:
                                score = 1.0 / (1.0 + dist) # Convert L2 to pseudo-similarity
                                res = {
                                    "metadata": self.faiss_metadata[idx],
                                    "score": score,
                                    "source": "shadow_cache"
                                }
                                faiss_temp_results.append(res)
                                
                                if score >= self.similarity_threshold:
                                    logger.info(f"Early exit: Shadow Cache hit threshold ({score:.4f})")
                                    scope.cancel() # Cancel other tasks, but this one continues to collect all k FAISS results
                        
                        results.extend(faiss_temp_results)

                    except Exception as e:
                        logger.error(f"FAISS lookup failed: {e}")
                    finally:
                        latency = time.time() - start_time
                        self._record_vector_lookup_latency("shadow_cache", latency)

            async def qdrant_lookup():
                if scope.cancel_called:
                    return
                # No delay here, check cancellation immediately before I/O
                if scope.cancel_called: # Re-check before the actual call
                    return
                start_time = time.time()
                try:
                    q_res = await self.qdrant.search(
                        collection_name="xnai_vectors",
                        query_vector=query_vector.tolist(),
                        limit=k
                    )
                    for hit in q_res:
                        results.append({
                            "metadata": hit.payload,
                            "score": hit.score,
                            "source": "qdrant"
                        })
                except Exception as e:
                    logger.error(f"Qdrant lookup failed: {e}")
                finally:
                    # Record Qdrant latency
                    latency = time.time() - start_time
                    self._record_vector_lookup_latency("qdrant", latency)

            tg.start_soon(faiss_lookup)
            tg.start_soon(qdrant_lookup)

        # Sort and deduplicate results
        # In a real system, we'd use robust ID tracking
        unique_results = []
        seen_content = set()
        for r in sorted(results, key=lambda x: x['score'], reverse=True):
            content_hash = hash(str(r['metadata']))
            if content_hash not in seen_content:
                unique_results.append(r)
                seen_content.add(content_hash)
                
        return unique_results[:k]

    def _record_vector_lookup_latency(self, source: str, latency: float):
        """Record vector lookup latency to Prometheus metrics."""
        try:
            # Import the global metric from the entrypoint
            from ..api.entrypoint import vector_lookup_latency
            vector_lookup_latency.labels(source=source).observe(latency)
        except ImportError:
            # Fallback if import fails
            logger.warning(f"Could not import Prometheus metric for {source} latency: {latency:.4f}s")
        except Exception as e:
            logger.error(f"Failed to record {source} latency metric: {e}")

    async def listen_for_updates(self):
        """Listens to Redis Streams for cache invalidation events."""
        if not self.redis:
            return
            
        logger.info("Subscribing to xnai:vector_updates bus...")
        # Implementation for Redis Stream consumption would go here
        # This would trigger self.faiss_metadata.pop() etc.
        pass
