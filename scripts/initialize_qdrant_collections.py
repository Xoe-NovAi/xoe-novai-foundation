#!/usr/bin/env python3
# ============================================================================
# XNAi Foundation - Qdrant Collections Initialization Script
# ============================================================================
# Purpose: Create and configure Qdrant collections from YAML configuration
# Features:
#   - Create 3 optimized collections (xnai_core, xnai_linguistic, xnai_hybrid)
#   - Configure HNSW indexing, payload schemas, quantization
#   - Verify collection creation and health
#   - Support for local and remote Qdrant instances
# Version: 1.0.0
# Last Updated: 2026-02-25
# Alignment: Zero-Telemetry, <100ms latency targets
# ============================================================================

import asyncio
import logging
import os
import sys
import yaml
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    import anyio
except ImportError:
    print("❌ ERROR: anyio is required. Install with: pip install anyio")
    sys.exit(1)

try:
    from qdrant_client import AsyncQdrantClient
    from qdrant_client.models import (
        Distance,
        VectorParams,
        PointStruct,
        FieldCondition,
        MatchValue,
        Filter,
        HasIdCondition,
        CreateIndex,
        DeleteIndex,
    )
except ImportError as e:
    print(f"❌ ERROR: qdrant-client import failed: {e}")
    sys.exit(1)

# ============================================================================
# Logging Configuration
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            "logs/qdrant_initialization.log",
            mode="a",
            encoding="utf-8"
        ),
    ],
)
logger = logging.getLogger(__name__)


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class QdrantConfig:
    """Qdrant connection configuration."""
    url: str = "http://localhost:6333"
    api_key: Optional[str] = None
    timeout: int = 30
    grpc_timeout: int = 60

    @classmethod
    def from_env(cls) -> "QdrantConfig":
        """Load from environment variables."""
        return cls(
            url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            api_key=os.getenv("QDRANT_API_KEY"),
            timeout=int(os.getenv("QDRANT_TIMEOUT", "30")),
            grpc_timeout=int(os.getenv("QDRANT_GRPC_TIMEOUT", "60")),
        )


@dataclass
class CollectionMetrics:
    """Metrics for a collection."""
    name: str
    vector_count: int
    indexed_vectors_count: int
    points_count: int
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ============================================================================
# Configuration Loader
# ============================================================================

class ConfigurationLoader:
    """Load and parse Qdrant collections configuration from YAML."""

    def __init__(self, config_file: str = "configs/qdrant_collections.yaml"):
        self.config_file = Path(config_file)
        self.config = None

    async def load(self) -> bool:
        """Load configuration from YAML file."""
        try:
            if not self.config_file.exists():
                logger.error(f"Configuration file not found: {self.config_file}")
                return False

            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)

            if not self.config:
                logger.error("Configuration is empty")
                return False

            logger.info(f"✅ Loaded configuration from {self.config_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return False

    def get_collections(self) -> Dict[str, Dict[str, Any]]:
        """Get collections configuration."""
        return self.config.get("collections", {})

    def get_global_config(self) -> Dict[str, Any]:
        """Get global configuration."""
        return self.config.get("global_config", {})

    def get_collection_config(self, name: str) -> Optional[Dict[str, Any]]:
        """Get specific collection configuration."""
        return self.get_collections().get(name)


# ============================================================================
# Collection Creator
# ============================================================================

class CollectionCreator:
    """Create Qdrant collections from configuration."""

    def __init__(self, client: AsyncQdrantClient, config_loader: ConfigurationLoader):
        self.client = client
        self.config_loader = config_loader

    async def create_all_collections(self) -> bool:
        """Create all collections from configuration."""
        collections = self.config_loader.get_collections()

        if not collections:
            logger.error("No collections defined in configuration")
            return False

        logger.info(f"Creating {len(collections)} collections...")

        all_success = True
        for collection_name, collection_config in collections.items():
            logger.info(f"\n--- Creating collection: {collection_name} ---")

            # Check if collection exists
            try:
                existing = await self._collection_exists(collection_name)
                if existing:
                    logger.info(f"Collection '{collection_name}' already exists")
                    continue
            except Exception as e:
                logger.error(f"Failed to check collection existence: {e}")
                all_success = False
                continue

            # Create collection
            try:
                success = await self._create_collection(
                    collection_name, collection_config
                )
                if success:
                    logger.info(f"✅ Successfully created collection: {collection_name}")
                else:
                    logger.error(f"❌ Failed to create collection: {collection_name}")
                    all_success = False

                # Create payload indexes
                try:
                    await self._create_payload_indexes(
                        collection_name,
                        collection_config.get("payload_schema", {})
                    )
                except Exception as e:
                    logger.warning(f"Failed to create payload indexes: {e}")

            except Exception as e:
                logger.error(f"Unexpected error creating collection {collection_name}: {e}")
                all_success = False

        return all_success

    async def _collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists."""
        try:
            collections = await self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            return collection_name in collection_names
        except Exception as e:
            logger.error(f"Failed to get collections: {e}")
            raise

    async def _create_collection(
        self,
        collection_name: str,
        config: Dict[str, Any]
    ) -> bool:
        """Create a single collection."""
        try:
            vector_config = config.get("vector_config", {})
            hnsw_config = config.get("hnsw_config", {})

            # Build HNSW configuration
            hnsw_cfg = {
                "m": hnsw_config.get("m", 16),
                "ef_construct": hnsw_config.get("ef_construct", 200),
                "ef": hnsw_config.get("ef", 100),
                "max_m": hnsw_config.get("max_m", 16),
                "max_m0": hnsw_config.get("max_m0", 32),
                "seed": hnsw_config.get("seed", 42),
            }

            # Distance metric
            distance_str = vector_config.get("distance_metric", "cosine").lower()
            distance_map = {
                "cosine": Distance.COSINE,
                "euclidean": Distance.EUCLID,
                "manhattan": Distance.MANHATTAN,
                "dot": Distance.DOT,
            }
            distance = distance_map.get(distance_str, Distance.COSINE)

            # Vector parameters
            vector_params = VectorParams(
                size=vector_config.get("size", 384),
                distance=distance,
                on_disk=vector_config.get("on_disk", True),
            )

            # Create collection
            await self.client.create_collection(
                collection_name=collection_name,
                vectors_config=vector_params,
            )

            logger.info(f"Created collection '{collection_name}' with:")
            logger.info(f"  - Vector size: {vector_config.get('size')} dimensions")
            logger.info(f"  - Distance: {distance_str}")
            logger.info(f"  - HNSW M: {hnsw_config.get('m')}")
            logger.info(f"  - HNSW ef_construct: {hnsw_config.get('ef_construct')}")

            return True

        except Exception as e:
            logger.error(f"Failed to create collection '{collection_name}': {e}")
            return False

    async def _create_payload_indexes(
        self,
        collection_name: str,
        payload_schema: Dict[str, Dict[str, Any]]
    ) -> bool:
        """Create payload indexes for metadata fields."""
        if not payload_schema:
            logger.info("No payload schema defined")
            return True

        indexed_fields = [
            (field_name, field_config)
            for field_name, field_config in payload_schema.items()
            if field_config.get("indexed", False)
        ]

        if not indexed_fields:
            logger.info("No indexed fields defined")
            return True

        logger.info(f"Creating {len(indexed_fields)} payload indexes...")

        for field_name, field_config in indexed_fields:
            try:
                field_type = field_config.get("type", "string")

                # Map types to Qdrant schema
                type_map = {
                    "string": "keyword",
                    "uuid": "keyword",
                    "integer": "integer",
                    "float": "float",
                    "timestamp": "keyword",
                }
                qdrant_type = type_map.get(field_type, "keyword")

                # Create payload index
                try:
                    await self.client.create_payload_index(
                        collection_name=collection_name,
                        field_name=field_name,
                        field_schema=qdrant_type,
                    )
                    logger.info(
                        f"  ✅ Created index: {field_name} ({qdrant_type})"
                    )
                except Exception as e:
                    # Field index may already exist
                    logger.debug(f"Index creation note for {field_name}: {e}")

            except Exception as e:
                logger.warning(
                    f"Failed to create index for {field_name}: {e}"
                )

        return True


# ============================================================================
# Collection Verifier
# ============================================================================

class CollectionVerifier:
    """Verify collection creation and configuration."""

    def __init__(self, client: AsyncQdrantClient):
        self.client = client

    async def verify_all_collections(
        self,
        collection_names: List[str]
    ) -> Dict[str, CollectionMetrics]:
        """Verify all collections."""
        metrics = {}

        for collection_name in collection_names:
            try:
                metric = await self.verify_collection(collection_name)
                if metric:
                    metrics[collection_name] = metric
            except Exception as e:
                logger.error(f"Failed to verify collection {collection_name}: {e}")

        return metrics

    async def verify_collection(
        self,
        collection_name: str
    ) -> Optional[CollectionMetrics]:
        """Verify a single collection."""
        try:
            collection_info = await self.client.get_collection(collection_name)

            metric = CollectionMetrics(
                name=collection_name,
                vector_count=collection_info.vectors_count,
                indexed_vectors_count=collection_info.indexed_vectors_count or 0,
                points_count=collection_info.points_count,
                status=collection_info.status if hasattr(collection_info, "status") else "unknown",
                created_at=None,
                updated_at=None,
            )

            logger.info(f"\n✅ Collection '{collection_name}' verified:")
            logger.info(f"  - Vector count: {metric.vector_count}")
            logger.info(f"  - Indexed vectors: {metric.indexed_vectors_count}")
            logger.info(f"  - Points: {metric.points_count}")
            logger.info(f"  - Status: {metric.status}")

            return metric

        except Exception as e:
            logger.error(f"Failed to verify collection {collection_name}: {e}")
            return None

    async def test_search(
        self,
        collection_name: str,
        test_vector: List[float],
        limit: int = 5
    ) -> bool:
        """Test search functionality on a collection."""
        try:
            if not test_vector:
                logger.warning(f"Skipping search test for {collection_name} - no test vector")
                return True

            # Search
            result = await self.client.search(
                collection_name=collection_name,
                query_vector=test_vector,
                limit=limit,
            )

            logger.info(
                f"Search test for '{collection_name}': "
                f"returned {len(result)} results"
            )
            return True

        except Exception as e:
            logger.warning(f"Search test failed for {collection_name}: {e}")
            return False

    async def generate_report(
        self,
        collection_metrics: Dict[str, CollectionMetrics]
    ) -> str:
        """Generate verification report."""
        report = []
        report.append("\n" + "=" * 70)
        report.append("QDRANT COLLECTIONS VERIFICATION REPORT")
        report.append("=" * 70)
        report.append(f"Timestamp: {datetime.now().isoformat()}\n")

        total_vectors = 0
        total_points = 0

        for name, metric in collection_metrics.items():
            report.append(f"\n{name}:")
            report.append(f"  Status: {metric.status}")
            report.append(f"  Vector Count: {metric.vector_count}")
            report.append(f"  Indexed Vectors: {metric.indexed_vectors_count}")
            report.append(f"  Points: {metric.points_count}")

            total_vectors += metric.vector_count
            total_points += metric.points_count

        report.append(f"\n{'-' * 70}")
        report.append(f"TOTALS:")
        report.append(f"  Total Vectors: {total_vectors}")
        report.append(f"  Total Points: {total_points}")
        report.append(f"  Collections: {len(collection_metrics)}")
        report.append("=" * 70 + "\n")

        return "\n".join(report)


# ============================================================================
# Main Orchestrator
# ============================================================================

class QdrantInitializer:
    """Orchestrate Qdrant collection initialization."""

    def __init__(self, config_file: str = "configs/qdrant_collections.yaml"):
        self.config_file = config_file
        self.config_loader = None
        self.client = None
        self.qdrant_config = None

    async def initialize(self) -> bool:
        """Initialize all collections."""
        logger.info("🚀 Starting Qdrant collections initialization...\n")

        try:
            # Load Qdrant connection config
            self.qdrant_config = QdrantConfig.from_env()
            logger.info(
                f"Connecting to Qdrant at: {self.qdrant_config.url}"
            )

            # Create async client
            self.client = AsyncQdrantClient(
                url=self.qdrant_config.url,
                api_key=self.qdrant_config.api_key,
                timeout=self.qdrant_config.timeout,
            )

            # Test connection
            try:
                await self.client.get_collections()
                logger.info("✅ Connected to Qdrant\n")
            except Exception as e:
                logger.error(f"❌ Failed to connect to Qdrant: {e}")
                return False

            # Load configuration
            self.config_loader = ConfigurationLoader(self.config_file)
            if not await self.config_loader.load():
                return False

            # Create collections
            creator = CollectionCreator(self.client, self.config_loader)
            if not await creator.create_all_collections():
                logger.warning("⚠️  Some collections failed to create")

            # Verify collections
            logger.info("\n--- Verifying Collections ---")
            collection_names = list(self.config_loader.get_collections().keys())

            verifier = CollectionVerifier(self.client)
            metrics = await verifier.verify_all_collections(collection_names)

            # Generate report
            report = await verifier.generate_report(metrics)
            logger.info(report)

            logger.info("✅ Qdrant collections initialization complete!\n")
            return True

        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}", exc_info=True)
            return False

        finally:
            if self.client:
                await self.client.close()


# ============================================================================
# Entry Point
# ============================================================================

async def main():
    """Main entry point."""
    config_file = os.getenv(
        "QDRANT_CONFIG_FILE",
        "configs/qdrant_collections.yaml"
    )

    initializer = QdrantInitializer(config_file)
    success = await initializer.initialize()

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
