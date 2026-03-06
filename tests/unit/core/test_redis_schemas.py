#!/usr/bin/env python3
"""
Unit tests for Redis Schema Manager

Tests serialization, deserialization, and schema operations.
"""

import json
import pytest
import hashlib
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any

# Import schema classes
from app.XNAi_rag_app.core.redis_schemas import (
    RedisSerializer,
    RedisSchemaManager,
    SerializationFormat,
    DocumentCacheEntry,
    SessionCacheEntry,
    EmbeddingCacheEntry,
    QueryCacheEntry,
    PersonaLearningState,
)


class TestRedisSerializer:
    """Test serialization and deserialization"""

    def test_json_serialization(self):
        """Test JSON serialization"""
        data = {"key": "value", "nested": {"inner": 42}}
        serialized = RedisSerializer.serialize(data, format=SerializationFormat.JSON)

        assert isinstance(serialized, bytes)
        deserialized = RedisSerializer.deserialize(serialized, format=SerializationFormat.JSON)
        assert deserialized == data

    def test_msgpack_serialization(self):
        """Test MessagePack serialization"""
        data = [1, 2, 3, 4.5, "text"]
        serialized = RedisSerializer.serialize(data, format=SerializationFormat.MSGPACK)

        assert isinstance(serialized, bytes)
        deserialized = RedisSerializer.deserialize(serialized, format=SerializationFormat.MSGPACK)
        assert deserialized == data

    def test_gzip_serialization(self):
        """Test gzip compression"""
        data = "x" * 5000  # Large string
        serialized = RedisSerializer.serialize(data, format=SerializationFormat.GZIP)

        assert isinstance(serialized, bytes)
        assert len(serialized) < len(data.encode())  # Should be compressed

        deserialized = RedisSerializer.deserialize(serialized, format=SerializationFormat.GZIP)
        assert deserialized == data

    def test_auto_format_detection(self):
        """Test automatic format detection"""
        # JSON detection
        json_data = {"key": "value"}
        serialized = RedisSerializer.serialize(json_data)
        deserialized = RedisSerializer.deserialize(serialized)
        assert deserialized == json_data

        # Vector detection (MessagePack)
        vector_data = [0.1, 0.2, 0.3, 0.4]
        serialized = RedisSerializer.serialize(vector_data)
        deserialized = RedisSerializer.deserialize(serialized)
        assert deserialized == vector_data


class TestRedisSchemaManager:
    """Test schema manager operations"""

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client"""
        return AsyncMock()

    @pytest.fixture
    def manager(self, mock_redis):
        """Create schema manager with mock Redis"""
        return RedisSchemaManager(mock_redis)

    @pytest.mark.asyncio
    async def test_set_document(self, manager, mock_redis):
        """Test document storage"""
        mock_redis.hset = AsyncMock(return_value=1)
        mock_redis.expire = AsyncMock(return_value=True)

        result = await manager.set_document(
            doc_id="doc_123",
            content="Test content",
            metadata={"source": "test", "created": "2026-02-25"}
        )

        assert result is True
        mock_redis.hset.assert_called_once()
        mock_redis.expire.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_document(self, manager, mock_redis):
        """Test document retrieval"""
        mock_redis.hgetall = AsyncMock(return_value={
            b"content": b"Test content",
            b"metadata": b'{"source": "test"}',
            b"version": b"1",
            b"size_bytes": b"12"
        })

        result = await manager.get_document("doc_123")

        assert result is not None
        assert result.content == "Test content"
        assert result.metadata == {"source": "test"}
        assert result.version == "1"

    @pytest.mark.asyncio
    async def test_set_session(self, manager, mock_redis):
        """Test session storage"""
        mock_redis.hset = AsyncMock(return_value=1)
        mock_redis.expire = AsyncMock(return_value=True)
        mock_redis.zadd = AsyncMock(return_value=1)

        session_data = {
            "session_id": "sess_001",
            "agent_type": "copilot-cli",
            "conversation_history": [],
            "context_window": {},
            "active_tools": ["grep"],
            "context_tokens": 1024,
            "state": "active"
        }

        result = await manager.set_session("agent_001", session_data)

        assert result is True
        mock_redis.hset.assert_called_once()
        mock_redis.expire.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_session(self, manager, mock_redis):
        """Test session retrieval"""
        mock_redis.hgetall = AsyncMock(return_value={
            b"session_id": b"sess_001",
            b"agent_type": b"copilot-cli",
            b"conversation_history": b"[]",
            b"context_window": b"{}",
            b"active_tools": b'["grep"]',
            b"context_tokens": b"1024",
            b"state": b"active",
            b"last_activity": b"2026-02-25T10:30:00Z"
        })

        result = await manager.get_session("agent_001")

        assert result is not None
        assert result.session_id == "sess_001"
        assert result.agent_type == "copilot-cli"
        assert result.context_tokens == 1024

    @pytest.mark.asyncio
    async def test_set_embedding(self, manager, mock_redis):
        """Test embedding storage"""
        mock_redis.set = AsyncMock(return_value=True)
        mock_redis.expire = AsyncMock(return_value=True)

        vector = [0.1, 0.2, 0.3] * 512  # 1536 dims

        result = await manager.set_embedding(
            embedding_type="bge_large",
            chunk_id="chunk_abc",
            vector=vector,
            metadata={"model": "bge-large-en"}
        )

        assert result is True
        mock_redis.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_embedding(self, manager, mock_redis):
        """Test embedding retrieval"""
        vector = [0.1, 0.2, 0.3, 0.4]
        embedding_data = {
            "vector": vector,
            "chunk_id": "chunk_abc",
            "model": "bge-large-en",
            "dimension": 4
        }

        serialized = RedisSerializer.serialize(embedding_data, format=SerializationFormat.MSGPACK)
        mock_redis.get = AsyncMock(return_value=serialized)

        result = await manager.get_embedding("bge_large", "chunk_abc")

        assert result == vector

    @pytest.mark.asyncio
    async def test_hash_query(self):
        """Test query hashing"""
        query = "find async functions"
        hash_result = RedisSchemaManager.hash_query(query)

        assert isinstance(hash_result, str)
        assert len(hash_result) == 16  # SHA256 first 16 chars
        assert hash_result == RedisSchemaManager.hash_query(query)  # Deterministic

    @pytest.mark.asyncio
    async def test_set_query_result(self, manager, mock_redis):
        """Test query result caching"""
        mock_redis.hset = AsyncMock(return_value=1)
        mock_redis.expire = AsyncMock(return_value=True)
        mock_redis.xadd = AsyncMock(return_value=b"123-0")

        results = [{"file": "app.py", "line": 42}]

        result = await manager.set_query_result(
            query="async functions",
            results=results,
            confidence_score=0.95,
            execution_time_ms=145
        )

        assert result is True
        mock_redis.hset.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_query_result(self, manager, mock_redis):
        """Test query result retrieval"""
        mock_redis.hgetall = AsyncMock(return_value={
            b"query": b"async functions",
            b"results": b'[{"file": "app.py"}]',
            b"confidence_score": b"0.95",
            b"result_count": b"1",
            b"execution_time_ms": b"145",
            b"model": b"bge-large-en",
            b"timestamp": b"2026-02-25T10:30:00Z",
            b"cache_hit_count": b"0"
        })
        mock_redis.hincrby = AsyncMock(return_value=1)

        result = await manager.get_query_result("async functions")

        assert result is not None
        assert result.query == "async functions"
        assert result.confidence_score == 0.95
        assert result.result_count == 1

    @pytest.mark.asyncio
    async def test_set_persona_state(self, manager, mock_redis):
        """Test persona learning state storage"""
        mock_redis.hset = AsyncMock(return_value=1)

        result = await manager.set_persona_state(
            agent_id="agent_001",
            expertise_scores={"python": 0.9, "rust": 0.4},
            interaction_count=100,
            success_rate=0.95,
            domain_focus="backend"
        )

        assert result is True
        mock_redis.hset.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_persona_state(self, manager, mock_redis):
        """Test persona learning state retrieval"""
        mock_redis.hgetall = AsyncMock(return_value={
            b"expertise_scores": b'{"python": 0.9}',
            b"interaction_count": b"100",
            b"success_rate": b"0.95",
            b"learning_rate": b"0.002",
            b"domain_focus": b"backend",
            b"preferred_languages": b'["python"]',
            b"adaptations": b"{}",
            b"last_update": b"2026-02-25T10:30:00Z",
            b"total_tokens_processed": b"50000"
        })

        result = await manager.get_persona_state("agent_001")

        assert result is not None
        assert result.expertise_scores == {"python": 0.9}
        assert result.interaction_count == 100
        assert result.success_rate == 0.95

    @pytest.mark.asyncio
    async def test_invalidate_document(self, manager, mock_redis):
        """Test document cache invalidation"""
        mock_redis.delete = AsyncMock(return_value=1)
        mock_redis.keys = AsyncMock(return_value=[])
        mock_redis.xadd = AsyncMock(return_value=b"123-0")

        result = await manager.invalidate_document("doc_123", cascade=True)

        assert result >= 0
        mock_redis.delete.assert_called()

    @pytest.mark.asyncio
    async def test_publish_knowledge_update(self, manager, mock_redis):
        """Test knowledge update stream publishing"""
        mock_redis.xadd = AsyncMock(return_value=b"123-0")

        event = {
            "event_type": "doc_added",
            "doc_id": "doc_123",
            "timestamp": "2026-02-25T10:30:00Z"
        }

        result = await manager.publish_knowledge_update(event)

        assert result is True
        mock_redis.xadd.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_success(self, manager, mock_redis):
        """Test Redis health check (success)"""
        mock_redis.ping = AsyncMock(return_value=True)

        result = await manager.health_check()

        assert result is True
        mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_failure(self, manager, mock_redis):
        """Test Redis health check (failure)"""
        mock_redis.ping = AsyncMock(side_effect=Exception("Connection failed"))

        result = await manager.health_check()

        assert result is False

    @pytest.mark.asyncio
    async def test_no_redis_client(self):
        """Test operations with no Redis client"""
        manager = RedisSchemaManager(None)

        result = await manager.set_document("doc_123", "content", {})
        assert result is False

        result = await manager.get_document("doc_123")
        assert result is None


class TestRedisSchemaDataClasses:
    """Test data class structures"""

    def test_document_cache_entry(self):
        """Test DocumentCacheEntry"""
        entry = DocumentCacheEntry(
            content="Test",
            metadata={"source": "test"},
            version="1",
            size_bytes=4
        )

        assert entry.content == "Test"
        assert entry.metadata["source"] == "test"
        assert entry.version == "1"

    def test_session_cache_entry(self):
        """Test SessionCacheEntry"""
        entry = SessionCacheEntry(
            session_id="sess_001",
            agent_type="copilot-cli",
            conversation_history=[],
            context_window={},
            active_tools=["grep"],
            last_activity="2026-02-25T10:30:00Z",
            context_tokens=1024
        )

        assert entry.session_id == "sess_001"
        assert entry.agent_type == "copilot-cli"
        assert entry.context_tokens == 1024

    def test_persona_learning_state(self):
        """Test PersonaLearningState"""
        state = PersonaLearningState(
            expertise_scores={"python": 0.9},
            interaction_count=100,
            total_tokens_processed=50000,
            success_rate=0.95,
            last_update="2026-02-25T10:30:00Z",
            learning_rate=0.002,
            domain_focus="backend",
            preferred_languages=["python"],
            adaptations={}
        )

        assert state.expertise_scores["python"] == 0.9
        assert state.interaction_count == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
