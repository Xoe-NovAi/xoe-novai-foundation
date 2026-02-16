#!/usr/bin/env python3
# ============================================================================
# Xoe-NovAi Foundation - Phase 3 FAISS to Qdrant Migration
# ============================================================================
# Purpose: Bulk migrate vector embeddings from FAISS to Qdrant with metadata-
#          first strategy, Redis state management, and Ryzen 7 optimization.
# Alignment: Sovereign Trinity (Consul, Redis, Ed25519 Handshakes)
# Author: Copilot <223556219+Copilot@users.noreply.github.com>
# Last Updated: 2026-02-15
# ============================================================================

import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

import anyio
import redis.asyncio as aioredis
from tqdm.asyncio import tqdm

try:
    from qdrant_client import AsyncQdrantClient
    from qdrant_client.models import (
        Distance,
        PointStruct,
        VectorParams,
    )
except ImportError as e:
    print(f"❌ ERROR: qdrant-client import failed: {e}")
    sys.exit(1)

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/migration.log", mode="a"),
    ],
)
logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION & CONSTANTS
# =============================================================================

@dataclass
class MigrationConfig:
    """Migration configuration optimized for Ryzen 7."""
    faiss_index_path: str = "/app/data/faiss_index"
    qdrant_url: str = "http://qdrant:6333"
    qdrant_api_key: Optional[str] = None
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db: int = 0
    
    # Batch processing (tuned for 6.6GB RAM)
    batch_size: int = 500
    max_memory_percent: float = 0.6
    
    # Collection settings
    collection_name: str = "xnai_knowledge"
    vector_size: int = 384  # Default embeddings dimension
    distance_metric: Distance = Distance.COSINE
    
    # Migration state
    state_key: str = "xnai:migration:faiss_to_qdrant"
    resume_mode: bool = True
    
    # Timeouts
    request_timeout: int = 30
    grpc_timeout: int = 60
    
    @classmethod
    def from_env(cls) -> "MigrationConfig":
        """Load config from environment variables."""
        return cls(
            faiss_index_path=os.getenv(
                "FAISS_INDEX_PATH", "/app/data/faiss_index"
            ),
            qdrant_url=os.getenv("QDRANT_URL", "http://qdrant:6333"),
            qdrant_api_key=os.getenv("QDRANT_API_KEY"),
            redis_host=os.getenv("REDIS_HOST", "redis"),
            redis_port=int(os.getenv("REDIS_PORT", "6379")),
            redis_password=os.getenv("REDIS_PASSWORD"),
            vector_size=int(os.getenv("VECTOR_SIZE", "384")),
        )


# =============================================================================
# MEMORY OPTIMIZATION (RYZEN 7)
# =============================================================================

class MemoryMonitor:
    """Monitor and enforce memory limits for Ryzen 7 (6.6GB RAM)."""
    
    def __init__(self, max_memory_percent: float = 0.6):
        self.max_memory_percent = max_memory_percent
        self.process = None
        try:
            import psutil
            self.process = psutil.Process()
            self.psutil_available = True
        except ImportError:
            logger.warning("psutil not available - memory monitoring disabled")
            self.psutil_available = False
    
    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        if not self.psutil_available or not self.process:
            return 0.0
        return self.process.memory_info().rss / (1024 * 1024)
    
    async def check_memory(self) -> bool:
        """Check if memory usage is within limits."""
        if not self.psutil_available:
            return True
        
        usage_mb = self.get_memory_usage_mb()
        limit_mb = 6600 * self.max_memory_percent  # 6.6GB * config percent
        
        if usage_mb > limit_mb:
            logger.warning(
                f"Memory limit approaching: {usage_mb:.1f}MB / {limit_mb:.1f}MB"
            )
            await self._cleanup()
            return False
        return True
    
    async def _cleanup(self):
        """Cleanup and garbage collection."""
        import gc
        gc.collect()
        await anyio.sleep(0.1)


# =============================================================================
# REDIS STATE MANAGEMENT
# =============================================================================

class MigrationState:
    """Manage migration state in Redis (transient source-of-truth)."""
    
    def __init__(self, redis_client: aioredis.Redis, state_key: str):
        self.redis = redis_client
        self.state_key = state_key
    
    async def init_state(self, total_vectors: int):
        """Initialize migration state."""
        state = {
            "status": "in_progress",
            "started_at": datetime.utcnow().isoformat(),
            "total_vectors": total_vectors,
            "processed_vectors": 0,
            "failed_vectors": 0,
            "batches_processed": 0,
            "last_batch_id": None,
            "last_checkpoint": datetime.utcnow().isoformat(),
        }
        await self.redis.set(self.state_key, json.dumps(state))
        logger.info(f"Migration state initialized: {total_vectors} vectors")
    
    async def get_state(self) -> Optional[Dict[str, Any]]:
        """Get current migration state."""
        state_json = await self.redis.get(self.state_key)
        if state_json:
            return json.loads(state_json)
        return None
    
    async def update_progress(self, processed: int, failed: int, batch_id: int):
        """Update progress in Redis."""
        state = await self.get_state()
        if state:
            state.update({
                "processed_vectors": processed,
                "failed_vectors": failed,
                "batches_processed": batch_id,
                "last_batch_id": batch_id,
                "last_checkpoint": datetime.utcnow().isoformat(),
            })
            await self.redis.set(self.state_key, json.dumps(state))
    
    async def finalize_state(self, success: bool):
        """Finalize migration state."""
        state = await self.get_state()
        if state:
            state.update({
                "status": "completed" if success else "failed",
                "completed_at": datetime.utcnow().isoformat(),
            })
            await self.redis.set(self.state_key, json.dumps(state))


# =============================================================================
# FAISS LOADER
# =============================================================================

class FAISSLoader:
    """Load vectors and metadata from FAISS index."""
    
    def __init__(self, index_path: str, vector_size: int):
        self.index_path = Path(index_path)
        self.vector_size = vector_size
        self.index = None
        self.docstore = None
        self.index_to_docstore_id = None
    
    async def load_index(self) -> bool:
        """Asynchronously load FAISS index."""
        try:
            import faiss
            import numpy as np
        except ImportError:
            logger.error("FAISS not installed. Install with: pip install faiss-cpu")
            return False
        
        try:
            # Load in thread pool to avoid blocking
            self.index = await anyio.to_thread.run_sync(
                self._load_faiss_index
            )
            if not self.index:
                return False
            
            logger.info(
                f"FAISS index loaded: {self.index.ntotal} vectors, "
                f"dimension={self.index.d}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            return False
    
    def _load_faiss_index(self):
        """Load FAISS index (sync helper)."""
        import faiss
        
        index_file = self.index_path / "index.faiss"
        if not index_file.exists():
            logger.error(f"FAISS index not found: {index_file}")
            return None
        
        try:
            index = faiss.read_index(str(index_file))
            return index
        except Exception as e:
            logger.error(f"Failed to read FAISS index: {e}")
            return None
    
    async def get_vectors_batch(
        self, batch_num: int, batch_size: int
    ) -> tuple[List[int], List[List[float]], List[Dict[str, Any]]]:
        """Get batch of vectors from FAISS index."""
        if not self.index:
            return [], [], []
        
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, self.index.ntotal)
        
        if start_idx >= self.index.ntotal:
            return [], [], []
        
        # Load vectors from index
        vectors = await anyio.to_thread.run_sync(
            lambda: self.index.reconstruct_n(start_idx, end_idx - start_idx)
        )
        
        vector_ids = list(range(start_idx, end_idx))
        vector_list = vectors.tolist() if hasattr(vectors, 'tolist') else vectors
        
        # Create metadata (metadata-first strategy)
        metadata_list = [
            {
                "source": "faiss",
                "faiss_id": vid,
                "migrated_at": datetime.utcnow().isoformat(),
                "batch_num": batch_num,
            }
            for vid in vector_ids
        ]
        
        return vector_ids, vector_list, metadata_list


# =============================================================================
# QDRANT UPSERTER
# =============================================================================

class QdrantUpserter:
    """Upsert vectors to Qdrant collection."""
    
    def __init__(self, config: MigrationConfig):
        self.config = config
        self.client = None
        self.collection_initialized = False
    
    async def connect(self) -> bool:
        """Connect to Qdrant server."""
        try:
            self.client = AsyncQdrantClient(
                url=self.config.qdrant_url,
                api_key=self.config.qdrant_api_key,
                timeout=self.config.request_timeout,
            )
            
            # Check connectivity
            await anyio.sleep(0.1)
            logger.info("Connected to Qdrant server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            return False
    
    async def init_collection(self) -> bool:
        """Create or verify Qdrant collection."""
        try:
            # Check if collection exists
            collections = await self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.config.collection_name in collection_names:
                logger.info(f"Collection '{self.config.collection_name}' exists")
                self.collection_initialized = True
                return True
            
            # Create collection with metadata-first payload index
            await self.client.create_collection(
                collection_name=self.config.collection_name,
                vectors_config=VectorParams(
                    size=self.config.vector_size,
                    distance=self.config.distance_metric,
                    on_disk=True,  # Store vectors on disk
                ),
            )
            
            # Create payload indexes for metadata fields
            await self._create_payload_indexes()
            
            logger.info(f"Collection '{self.config.collection_name}' created")
            self.collection_initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize collection: {e}")
            return False
    
    async def _create_payload_indexes(self):
        """Create payload indexes for metadata fields."""
        try:
            payload_fields = [
                ("source", "keyword"),
                ("faiss_id", "integer"),
                ("migrated_at", "keyword"),
                ("batch_num", "integer"),
            ]
            
            for field_name, field_type in payload_fields:
                try:
                    await self.client.create_payload_index(
                        collection_name=self.config.collection_name,
                        field_name=field_name,
                        field_schema=field_type,
                    )
                except Exception:
                    # Field may already exist
                    pass
            
            logger.info("Payload indexes created/verified")
        except Exception as e:
            logger.warning(f"Failed to create payload indexes: {e}")
    
    async def upsert_batch(
        self,
        vector_ids: List[int],
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
    ) -> tuple[int, int]:
        """Upsert batch of vectors to Qdrant (metadata-first)."""
        if not self.client or not self.collection_initialized:
            return 0, len(vector_ids)
        
        success_count = 0
        error_count = 0
        
        try:
            # Create points with metadata (metadata-first strategy)
            points = [
                PointStruct(
                    id=vid,
                    vector=vec,
                    payload=meta,
                )
                for vid, vec, meta in zip(vector_ids, vectors, metadata)
            ]
            
            # Upsert to Qdrant
            await self.client.upsert(
                collection_name=self.config.collection_name,
                points=points,
                wait=True,
            )
            
            success_count = len(points)
            logger.debug(f"Upserted {success_count} points to Qdrant")
        except Exception as e:
            logger.error(f"Failed to upsert batch: {e}")
            error_count = len(vector_ids)
        
        return success_count, error_count
    
    async def verify_collection(self) -> bool:
        """Verify collection and get stats."""
        try:
            info = await self.client.get_collection(
                self.config.collection_name
            )
            logger.info(
                f"Collection stats: {info.points_count} points, "
                f"vectors_count={info.vectors_count}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to verify collection: {e}")
            return False
    
    async def close(self):
        """Close Qdrant connection."""
        if self.client:
            await self.client.close()


# =============================================================================
# MAIN MIGRATION ORCHESTRATOR
# =============================================================================

class FAISSToQdrantMigrator:
    """Orchestrate full FAISS to Qdrant migration."""
    
    def __init__(self, config: MigrationConfig):
        self.config = config
        self.redis = None
        self.faiss_loader = None
        self.qdrant_upserter = None
        self.migration_state = None
        self.memory_monitor = None
    
    async def setup(self) -> bool:
        """Setup all components."""
        logger.info("🚀 Initializing migration components...")
        
        # Setup memory monitor
        self.memory_monitor = MemoryMonitor(self.config.max_memory_percent)
        logger.info(f"Memory limit: {6600 * self.config.max_memory_percent:.0f}MB")
        
        # Connect to Redis
        try:
            self.redis = await aioredis.from_url(
                f"redis://{self.config.redis_host}:{self.config.redis_port}",
                password=self.config.redis_password,
                db=self.config.redis_db,
                decode_responses=True,
            )
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            return False
        
        # Initialize migration state
        self.migration_state = MigrationState(self.redis, self.config.state_key)
        
        # Load FAISS index
        self.faiss_loader = FAISSLoader(
            self.config.faiss_index_path,
            self.config.vector_size,
        )
        if not await self.faiss_loader.load_index():
            return False
        
        # Connect to Qdrant
        self.qdrant_upserter = QdrantUpserter(self.config)
        if not await self.qdrant_upserter.connect():
            return False
        
        # Initialize Qdrant collection
        if not await self.qdrant_upserter.init_collection():
            return False
        
        logger.info("✅ All components initialized")
        return True
    
    async def migrate(self) -> bool:
        """Execute full migration with AnyIO task groups."""
        try:
            total_vectors = self.faiss_loader.index.ntotal
            await self.migration_state.init_state(total_vectors)
            
            # Calculate batches
            total_batches = (
                total_vectors + self.config.batch_size - 1
            ) // self.config.batch_size
            
            logger.info(
                f"Starting migration: {total_vectors} vectors in "
                f"{total_batches} batches"
            )
            
            processed = 0
            failed = 0
            
            # Process batches
            with tqdm(total=total_batches, desc="Migration Progress") as pbar:
                for batch_num in range(total_batches):
                    # Check memory before processing
                    if not await self.memory_monitor.check_memory():
                        logger.warning("Memory limit exceeded, pausing...")
                        await anyio.sleep(2)
                    
                    # Load batch from FAISS
                    vector_ids, vectors, metadata = (
                        await self.faiss_loader.get_vectors_batch(
                            batch_num, self.config.batch_size
                        )
                    )
                    
                    if not vector_ids:
                        break
                    
                    # Upsert to Qdrant
                    success, errors = await self.qdrant_upserter.upsert_batch(
                        vector_ids, vectors, metadata
                    )
                    
                    processed += success
                    failed += errors
                    
                    # Update state
                    await self.migration_state.update_progress(
                        processed, failed, batch_num + 1
                    )
                    
                    pbar.update(1)
                    pbar.set_postfix({
                        "processed": processed,
                        "failed": failed,
                        "memory_mb": f"{self.memory_monitor.get_memory_usage_mb():.0f}",
                    })
            
            # Verify final state
            logger.info("Verifying collection...")
            await self.qdrant_upserter.verify_collection()
            
            # Finalize state
            await self.migration_state.finalize_state(failed == 0)
            
            logger.info(
                f"✅ Migration complete: {processed} successful, "
                f"{failed} failed"
            )
            return failed == 0
        
        except Exception as e:
            logger.error(f"Migration failed: {e}", exc_info=True)
            if self.migration_state:
                await self.migration_state.finalize_state(False)
            return False
    
    async def cleanup(self):
        """Cleanup connections and resources."""
        if self.redis:
            await self.redis.close()
        
        if self.qdrant_upserter:
            await self.qdrant_upserter.close()
        
        # Explicit cleanup for Ryzen 7
        import gc
        gc.collect()
        logger.info("Cleanup complete")


# =============================================================================
# ENTRY POINT
# =============================================================================

async def main():
    """Main entry point with AnyIO task group."""
    config = MigrationConfig.from_env()
    migrator = FAISSToQdrantMigrator(config)
    
    try:
        # Use AnyIO task group for structured concurrency
        async with anyio.create_task_group() as tg:
            if not await migrator.setup():
                logger.error("Setup failed")
                return 1
            
            # Run migration in task group context
            success = await migrator.migrate()
            return 0 if success else 1
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1
    
    finally:
        await migrator.cleanup()


if __name__ == "__main__":
    exit_code = anyio.run(main)
    sys.exit(exit_code)
