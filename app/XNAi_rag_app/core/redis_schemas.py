#!/usr/bin/env python3
"""
Redis Schema Implementation for XNAi Foundation
================================================

Implements Redis key patterns, serialization, and cache operations.

Features:
- Unified schema interface for all cache tiers
- Automatic serialization/deserialization (JSON, MessagePack, gzip)
- TTL management with cascade invalidation
- Stream-based event publishing
- Metrics collection

CLAUDE STANDARD: Uses AnyIO for structured concurrency.
TORCH-FREE: No PyTorch dependencies.
"""

import json
import msgpack
import gzip
import logging
import hashlib
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, asdict
import anyio

try:
    import redis.asyncio as redis
    from redis.asyncio import Redis, ConnectionPool
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMERATIONS
# ============================================================================


class SerializationFormat(str, Enum):
    """Supported serialization formats"""
    JSON = "json"
    MSGPACK = "msgpack"
    GZIP = "gzip"
    AUTO = "auto"


class CacheTier(str, Enum):
    """Cache tier types"""
    HOT = "hot"          # Documents (frequent access)
    WARM = "warm"        # Embeddings (medium access)
    COLD = "cold"        # Query results (occasional access)
    LEARNING = "learning"  # Persona state (persistent)


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class DocumentCacheEntry:
    """Document cache structure"""
    content: str
    metadata: Dict[str, Any]
    embedding_id: Optional[str] = None
    updated_at: Optional[str] = None
    version: str = "1"
    size_bytes: Optional[int] = None


@dataclass
class SessionCacheEntry:
    """Session state structure"""
    session_id: str
    agent_type: str
    conversation_history: List[Dict[str, str]]
    context_window: Dict[str, Any]
    active_tools: List[str]
    last_activity: str
    context_tokens: int = 0
    state: str = "active"


@dataclass
class EmbeddingCacheEntry:
    """Embedding vector structure"""
    vector: List[float]
    chunk_id: str
    chunk_hash: str
    model: str
    dimension: int
    norm: float
    timestamp: str


@dataclass
class QueryCacheEntry:
    """Query result cache structure"""
    query: str
    results: List[Dict[str, Any]]
    confidence_score: float
    result_count: int
    execution_time_ms: float
    model: str
    timestamp: str
    cache_hit_count: int = 0


@dataclass
class PersonaLearningState:
    """Persona learning state structure"""
    expertise_scores: Dict[str, float]
    interaction_count: int
    total_tokens_processed: int
    success_rate: float
    last_update: str
    learning_rate: float
    domain_focus: str
    preferred_languages: List[str]
    adaptations: Dict[str, str]


# ============================================================================
# SERIALIZER
# ============================================================================


class RedisSerializer:
    """Unified serialization for Redis values"""

    @staticmethod
    def serialize(value: Any, format: str = SerializationFormat.AUTO) -> bytes:
        """Serialize value for Redis storage"""

        if format == SerializationFormat.AUTO:
            # Auto-detect format based on value type
            if isinstance(value, bytes):
                format = SerializationFormat.GZIP
            elif isinstance(value, (dict, list)) and len(json.dumps(value, default=str)) < 10000:
                format = SerializationFormat.JSON
            elif isinstance(value, list) and all(isinstance(x, (int, float)) for x in value):
                format = SerializationFormat.MSGPACK
            else:
                format = SerializationFormat.JSON

        if format == SerializationFormat.JSON:
            serialized = json.dumps(value, default=str).encode("utf-8")
            return serialized

        elif format == SerializationFormat.MSGPACK:
            serialized = msgpack.packb(value, use_bin_type=True)
            # Compress if > 1KB
            if len(serialized) > 1024:
                return b"\x1f\x8b" + gzip.compress(serialized)[2:]
            return serialized

        elif format == SerializationFormat.GZIP:
            if isinstance(value, str):
                value = value.encode("utf-8")
            return gzip.compress(value)

        else:
            return json.dumps(value, default=str).encode("utf-8")

    @staticmethod
    def deserialize(data: bytes, format: str = SerializationFormat.AUTO) -> Any:
        """Deserialize value from Redis storage"""

        if format == SerializationFormat.AUTO:
            # Auto-detect format
            if data.startswith(b"{") or data.startswith(b"["):
                format = SerializationFormat.JSON
            elif data.startswith(b"\x1f\x8b"):  # gzip magic number
                format = SerializationFormat.GZIP
            elif data[0:1] in (b"\x82", b"\x83", b"\x84"):  # msgpack array/map start
                format = SerializationFormat.MSGPACK
            else:
                format = SerializationFormat.JSON

        try:
            if format == SerializationFormat.JSON:
                return json.loads(data.decode("utf-8"))

            elif format == SerializationFormat.MSGPACK:
                return msgpack.unpackb(data, use_list=True)

            elif format == SerializationFormat.GZIP:
                decompressed = gzip.decompress(data)
                try:
                    return msgpack.unpackb(decompressed, use_list=True)
                except:
                    return decompressed.decode("utf-8")

        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            return None


# ============================================================================
# REDIS SCHEMA MANAGER
# ============================================================================


class RedisSchemaManager:
    """Manages Redis key patterns and schema operations"""

    # Key patterns
    DOC_PATTERN = "doc:{id}"
    SESSION_PATTERN = "session:{agent_id}"
    EMBED_PATTERN = "embed:{embedding_type}:{chunk_id}"
    QUERY_PATTERN = "query:{query_hash}"
    PERSONA_PATTERN = "persona:{agent_id}:learning"

    # Stream names
    KNOWLEDGE_UPDATES_STREAM = "knowledge:updates"

    # TTLs (seconds)
    TTL_DOC = 86400  # 24 hours
    TTL_SESSION = 172800  # 48 hours
    TTL_EMBED = 3600  # 1 hour
    TTL_QUERY = 3600  # 1 hour
    TTL_PERSONA = 0  # Permanent

    def __init__(self, redis_client: Optional[Redis] = None):
        """Initialize schema manager"""
        self.redis = redis_client

    # ========================================================================
    # DOCUMENT CACHE
    # ========================================================================

    async def set_document(
        self,
        doc_id: str,
        content: str,
        metadata: Dict[str, Any],
        embedding_id: Optional[str] = None,
        ttl: int = TTL_DOC
    ) -> bool:
        """Store document in cache"""

        if not self.redis:
            logger.warning("Redis not available - skipping document cache")
            return False

        try:
            key = self.DOC_PATTERN.replace("{id}", doc_id)
            now = datetime.now(timezone.utc).isoformat()

            mapping = {
                "content": content,
                "metadata": json.dumps(metadata),
                "updated_at": now,
                "version": "1",
                "size_bytes": len(content)
            }

            if embedding_id:
                mapping["embedding_id"] = embedding_id

            await self.redis.hset(key, mapping=mapping)
            await self.redis.expire(key, ttl)

            logger.debug(f"Stored document: {key}")
            return True

        except Exception as e:
            logger.error(f"Error storing document: {e}")
            return False

    async def get_document(self, doc_id: str) -> Optional[DocumentCacheEntry]:
        """Retrieve document from cache"""

        if not self.redis:
            return None

        try:
            key = self.DOC_PATTERN.replace("{id}", doc_id)
            data = await self.redis.hgetall(key)

            if not data:
                return None

            metadata = json.loads(data.get(b"metadata", b"{}"))
            return DocumentCacheEntry(
                content=data[b"content"].decode("utf-8"),
                metadata=metadata,
                embedding_id=data.get(b"embedding_id", b"").decode("utf-8") or None,
                updated_at=data.get(b"updated_at", b"").decode("utf-8"),
                version=data.get(b"version", b"1").decode("utf-8"),
                size_bytes=int(data.get(b"size_bytes", 0))
            )

        except Exception as e:
            logger.error(f"Error retrieving document: {e}")
            return None

    # ========================================================================
    # SESSION CACHE
    # ========================================================================

    async def set_session(
        self,
        agent_id: str,
        session_data: Dict[str, Any],
        ttl: int = TTL_SESSION
    ) -> bool:
        """Store session state in cache"""

        if not self.redis:
            logger.warning("Redis not available - skipping session cache")
            return False

        try:
            key = self.SESSION_PATTERN.replace("{agent_id}", agent_id)

            mapping = {
                "session_id": session_data.get("session_id", ""),
                "agent_type": session_data.get("agent_type", ""),
                "conversation_history": json.dumps(session_data.get("conversation_history", [])),
                "context_window": json.dumps(session_data.get("context_window", {})),
                "active_tools": json.dumps(session_data.get("active_tools", [])),
                "last_activity": datetime.now(timezone.utc).isoformat(),
                "context_tokens": str(session_data.get("context_tokens", 0)),
                "state": session_data.get("state", "active")
            }

            await self.redis.hset(key, mapping=mapping)
            await self.redis.expire(key, ttl)

            # Update activity index
            await self.redis.zadd(
                "sessions:by_activity",
                {agent_id: datetime.now(timezone.utc).timestamp()}
            )

            logger.debug(f"Stored session: {key}")
            return True

        except Exception as e:
            logger.error(f"Error storing session: {e}")
            return False

    async def get_session(self, agent_id: str) -> Optional[SessionCacheEntry]:
        """Retrieve session from cache"""

        if not self.redis:
            return None

        try:
            key = self.SESSION_PATTERN.replace("{agent_id}", agent_id)
            data = await self.redis.hgetall(key)

            if not data:
                return None

            return SessionCacheEntry(
                session_id=data[b"session_id"].decode("utf-8"),
                agent_type=data[b"agent_type"].decode("utf-8"),
                conversation_history=json.loads(data.get(b"conversation_history", b"[]")),
                context_window=json.loads(data.get(b"context_window", b"{}")),
                active_tools=json.loads(data.get(b"active_tools", b"[]")),
                last_activity=data.get(b"last_activity", b"").decode("utf-8"),
                context_tokens=int(data.get(b"context_tokens", 0)),
                state=data.get(b"state", b"active").decode("utf-8")
            )

        except Exception as e:
            logger.error(f"Error retrieving session: {e}")
            return None

    # ========================================================================
    # EMBEDDING CACHE
    # ========================================================================

    async def set_embedding(
        self,
        embedding_type: str,
        chunk_id: str,
        vector: List[float],
        metadata: Dict[str, Any],
        ttl: int = TTL_EMBED
    ) -> bool:
        """Store embedding vector in cache"""

        if not self.redis:
            return False

        try:
            key = self.EMBED_PATTERN.replace("{embedding_type}", embedding_type).replace(
                "{chunk_id}", chunk_id
            )

            embedding_data = {
                "vector": vector,
                "chunk_id": chunk_id,
                "chunk_hash": hashlib.sha256(chunk_id.encode()).hexdigest(),
                "model": metadata.get("model", "unknown"),
                "dimension": len(vector),
                "norm": 1.0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            # Serialize with MessagePack
            serialized = RedisSerializer.serialize(
                embedding_data,
                format=SerializationFormat.MSGPACK
            )

            await self.redis.set(key, serialized)
            await self.redis.expire(key, ttl)

            logger.debug(f"Stored embedding: {key}")
            return True

        except Exception as e:
            logger.error(f"Error storing embedding: {e}")
            return False

    async def get_embedding(
        self,
        embedding_type: str,
        chunk_id: str
    ) -> Optional[List[float]]:
        """Retrieve embedding vector from cache"""

        if not self.redis:
            return None

        try:
            key = self.EMBED_PATTERN.replace("{embedding_type}", embedding_type).replace(
                "{chunk_id}", chunk_id
            )

            data = await self.redis.get(key)
            if not data:
                return None

            embedding_data = RedisSerializer.deserialize(
                data,
                format=SerializationFormat.AUTO
            )

            return embedding_data.get("vector") if embedding_data else None

        except Exception as e:
            logger.error(f"Error retrieving embedding: {e}")
            return None

    # ========================================================================
    # QUERY CACHE
    # ========================================================================

    @staticmethod
    def hash_query(query: str) -> str:
        """Generate hash for query"""
        return hashlib.sha256(query.encode()).hexdigest()[:16]

    async def set_query_result(
        self,
        query: str,
        results: List[Dict[str, Any]],
        confidence_score: float,
        execution_time_ms: float,
        model: str = "bge-large-en",
        ttl: int = TTL_QUERY
    ) -> bool:
        """Cache query results"""

        if not self.redis:
            return False

        try:
            query_hash = self.hash_query(query)
            key = self.QUERY_PATTERN.replace("{query_hash}", query_hash)

            mapping = {
                "query": query,
                "results": json.dumps(results),
                "confidence_score": str(confidence_score),
                "result_count": str(len(results)),
                "execution_time_ms": str(execution_time_ms),
                "model": model,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cache_hit_count": "0"
            }

            await self.redis.hset(key, mapping=mapping)
            await self.redis.expire(key, ttl)

            logger.debug(f"Cached query result: {key}")
            return True

        except Exception as e:
            logger.error(f"Error caching query: {e}")
            return False

    async def get_query_result(self, query: str) -> Optional[QueryCacheEntry]:
        """Retrieve cached query results"""

        if not self.redis:
            return None

        try:
            query_hash = self.hash_query(query)
            key = self.QUERY_PATTERN.replace("{query_hash}", query_hash)

            data = await self.redis.hgetall(key)
            if not data:
                return None

            # Increment hit count
            await self.redis.hincrby(key, "cache_hit_count", 1)

            return QueryCacheEntry(
                query=data[b"query"].decode("utf-8"),
                results=json.loads(data.get(b"results", b"[]")),
                confidence_score=float(data.get(b"confidence_score", 0)),
                result_count=int(data.get(b"result_count", 0)),
                execution_time_ms=float(data.get(b"execution_time_ms", 0)),
                model=data.get(b"model", b"").decode("utf-8"),
                timestamp=data.get(b"timestamp", b"").decode("utf-8"),
                cache_hit_count=int(data.get(b"cache_hit_count", 0))
            )

        except Exception as e:
            logger.error(f"Error retrieving query: {e}")
            return None

    # ========================================================================
    # PERSONA LEARNING STATE
    # ========================================================================

    async def set_persona_state(
        self,
        agent_id: str,
        expertise_scores: Dict[str, float],
        interaction_count: int,
        success_rate: float,
        domain_focus: str = "general",
        preferred_languages: Optional[List[str]] = None
    ) -> bool:
        """Store persona learning state"""

        if not self.redis:
            return False

        try:
            key = self.PERSONA_PATTERN.replace("{agent_id}", agent_id)

            mapping = {
                "expertise_scores": json.dumps(expertise_scores),
                "interaction_count": str(interaction_count),
                "total_tokens_processed": "0",
                "success_rate": str(success_rate),
                "last_update": datetime.now(timezone.utc).isoformat(),
                "learning_rate": "0.002",
                "domain_focus": domain_focus,
                "preferred_languages": json.dumps(preferred_languages or ["python", "bash"]),
                "adaptations": json.dumps({"code_style": "claude", "verbosity": "concise"})
            }

            await self.redis.hset(key, mapping=mapping)
            # No TTL for persona state

            logger.debug(f"Stored persona state: {key}")
            return True

        except Exception as e:
            logger.error(f"Error storing persona state: {e}")
            return False

    async def get_persona_state(self, agent_id: str) -> Optional[PersonaLearningState]:
        """Retrieve persona learning state"""

        if not self.redis:
            return None

        try:
            key = self.PERSONA_PATTERN.replace("{agent_id}", agent_id)
            data = await self.redis.hgetall(key)

            if not data:
                return None

            return PersonaLearningState(
                expertise_scores=json.loads(data.get(b"expertise_scores", b"{}")),
                interaction_count=int(data.get(b"interaction_count", 0)),
                total_tokens_processed=int(data.get(b"total_tokens_processed", 0)),
                success_rate=float(data.get(b"success_rate", 0)),
                last_update=data.get(b"last_update", b"").decode("utf-8"),
                learning_rate=float(data.get(b"learning_rate", 0.002)),
                domain_focus=data.get(b"domain_focus", b"general").decode("utf-8"),
                preferred_languages=json.loads(data.get(b"preferred_languages", b"[]")),
                adaptations=json.loads(data.get(b"adaptations", b"{}"))
            )

        except Exception as e:
            logger.error(f"Error retrieving persona state: {e}")
            return None

    # ========================================================================
    # CACHE INVALIDATION
    # ========================================================================

    async def invalidate_document(self, doc_id: str, cascade: bool = True) -> int:
        """Invalidate document cache and related entries"""

        if not self.redis:
            return 0

        deleted_count = 0

        try:
            # Delete document
            key = self.DOC_PATTERN.replace("{id}", doc_id)
            if await self.redis.delete(key):
                deleted_count += 1

            if cascade:
                # Delete query results containing this doc
                query_keys = await self.redis.keys("query:*")
                for key in query_keys:
                    data = await self.redis.hgetall(key)
                    results = json.loads(data.get(b"results", b"[]"))

                    if any(doc_id in str(r) for r in results):
                        if await self.redis.delete(key):
                            deleted_count += 1

                # Delete embeddings for this doc
                embed_keys = await self.redis.keys(f"embed:*:{doc_id}*")
                deleted_count += await self.redis.delete(*embed_keys)

            # Publish invalidation event
            await self.publish_knowledge_update({
                "event_type": "cache_invalidated",
                "doc_id": doc_id,
                "cascade": str(cascade),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

            logger.info(f"Invalidated {deleted_count} cache entries for doc {doc_id}")
            return deleted_count

        except Exception as e:
            logger.error(f"Error invalidating document cache: {e}")
            return deleted_count

    # ========================================================================
    # KNOWLEDGE UPDATES STREAM
    # ========================================================================

    async def publish_knowledge_update(self, event: Dict[str, Any]) -> bool:
        """Publish event to knowledge updates stream"""

        if not self.redis:
            return False

        try:
            await self.redis.xadd(self.KNOWLEDGE_UPDATES_STREAM, event)
            logger.debug(f"Published knowledge update: {event.get('event_type')}")
            return True

        except Exception as e:
            logger.error(f"Error publishing knowledge update: {e}")
            return False

    async def setup_stream_consumer(
        self,
        consumer_group: str,
        consumer_name: str
    ) -> bool:
        """Setup consumer group for knowledge updates stream"""

        if not self.redis:
            return False

        try:
            await self.redis.xgroup_create(
                self.KNOWLEDGE_UPDATES_STREAM,
                consumer_group,
                id="0",
                mkstream=True
            )
            logger.info(f"Created consumer group: {consumer_group}")
            return True

        except redis.ResponseError as e:
            if "BUSYGROUP" in str(e):
                logger.info(f"Consumer group already exists: {consumer_group}")
                return True
            logger.error(f"Error creating consumer group: {e}")
            return False

        except Exception as e:
            logger.error(f"Error setting up stream consumer: {e}")
            return False

    # ========================================================================
    # UTILITY
    # ========================================================================

    async def health_check(self) -> bool:
        """Check Redis connectivity"""

        if not self.redis:
            return False

        try:
            await self.redis.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False

    async def clear_cache(self) -> bool:
        """Clear all cache entries (dev/test only)"""

        if not self.redis:
            return False

        try:
            # Only clear cache keys, not stream or persona data
            keys_to_clear = [
                "doc:*",
                "session:*",
                "embed:*",
                "query:*",
                "sessions:by_activity"
            ]

            for pattern in keys_to_clear:
                keys = await self.redis.keys(pattern)
                if keys:
                    await self.redis.delete(*keys)

            logger.info("Cache cleared")
            return True

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False


async def create_schema_manager(redis_url: Optional[str] = None) -> RedisSchemaManager:
    """Factory function to create schema manager with Redis client"""

    if not redis_url:
        import os
        redis_url = os.getenv("REDIS_URL", "rediss://redis:6379")

    try:
        pool = ConnectionPool.from_url(redis_url, max_connections=50, decode_responses=True)
        redis_client = redis.Redis(connection_pool=pool)

        # Test connection
        await redis_client.ping()

        manager = RedisSchemaManager(redis_client)
        logger.info("Redis schema manager initialized")
        return manager

    except Exception as e:
        logger.warning(f"Redis not available, using fallback: {e}")
        return RedisSchemaManager(None)
