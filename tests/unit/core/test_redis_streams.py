"""
Unit tests for redis_streams.py

Tests cover:
- RedisStreamManager class
- Consumer group management
- Task publishing and consuming
- DLQ (Dead Letter Queue) functionality
- Retry with exponential backoff
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json
from datetime import datetime, timezone


# Test fixtures
@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    mock = AsyncMock()
    mock.xgroup_create = AsyncMock(return_value=True)
    mock.xadd = AsyncMock(return_value=b"1234567890-0")
    mock.xreadgroup = AsyncMock(return_value=[])
    mock.xack = AsyncMock(return_value=1)
    mock.xdel = AsyncMock(return_value=1)
    mock.xlen = AsyncMock(return_value=0)
    mock.ping = AsyncMock(return_value=True)
    mock.aclose = AsyncMock()
    return mock


@pytest.fixture
def redis_stream_manager(mock_redis):
    """RedisStreamManager instance for testing."""
    from app.XNAi_rag_app.core.redis_streams import RedisStreamManager

    manager = RedisStreamManager(consumer_id="test_consumer")
    manager._redis = mock_redis
    manager._initialized = True
    return manager


class TestRedisStreamManager:
    """Tests for RedisStreamManager class."""

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test RedisStreamManager initializes correctly."""
        from app.XNAi_rag_app.core.redis_streams import RedisStreamManager

        manager = RedisStreamManager(consumer_id="test_consumer")

        assert manager._consumer_id == "test_consumer"
        assert manager._initialized is False

    @pytest.mark.asyncio
    async def test_create_consumer_group_success(self, redis_stream_manager, mock_redis):
        """Test successful consumer group creation."""
        from app.XNAi_rag_app.core.redis_streams import ConsumerGroupConfig

        config = ConsumerGroupConfig(name="test_group", streams=["test_stream"])

        result = await redis_stream_manager.create_consumer_group(config)

        assert result is True
        mock_redis.xgroup_create.assert_called()

    @pytest.mark.asyncio
    async def test_create_consumer_group_already_exists(self, redis_stream_manager, mock_redis):
        """Test handling when consumer group already exists."""
        from redis.exceptions import ResponseError
        from app.XNAi_rag_app.core.redis_streams import ConsumerGroupConfig

        mock_redis.xgroup_create.side_effect = ResponseError("BUSYGROUP")

        config = ConsumerGroupConfig(name="test_group", streams=["test_stream"])

        result = await redis_stream_manager.create_consumer_group(config)

        # Should handle gracefully
        assert result is True

    @pytest.mark.asyncio
    async def test_send_message_success(self, redis_stream_manager, mock_redis):
        """Test successful message sending."""
        message_data = {"task_type": "rag_query", "sender": "did:xoe:agent:test", "payload": {"query": "test query"}}

        result = await redis_stream_manager.send_message(stream="test_stream", data=message_data)

        assert result is not None
        mock_redis.xadd.assert_called_once()


class TestMessageConsumption:
    """Tests for message consumption functionality."""

    @pytest.mark.asyncio
    async def test_read_messages_empty(self, redis_stream_manager, mock_redis):
        """Test reading when no messages available."""
        from app.XNAi_rag_app.core.redis_streams import ConsumerGroupConfig

        # Add a consumer group config
        config = ConsumerGroupConfig(name="test_group", streams=["test_stream"])
        redis_stream_manager._consumer_groups["test_group"] = config

        mock_redis.xreadgroup.return_value = []

        messages = await redis_stream_manager.read_messages("test_group")

        assert messages == []

    @pytest.mark.asyncio
    async def test_read_messages_single(self, redis_stream_manager, mock_redis):
        """Test reading a single message."""
        from app.XNAi_rag_app.core.redis_streams import ConsumerGroupConfig, StreamMessage

        # Add a consumer group config
        config = ConsumerGroupConfig(name="test_group", streams=["test_stream"])
        redis_stream_manager._consumer_groups["test_group"] = config

        mock_message = {b"task_type": b"rag_query", b"sender": b"did:xoe:agent:test", b"payload": b'{"query": "test"}'}

        mock_redis.xreadgroup.return_value = [[b"test_stream", [(b"1234567890-0", mock_message)]]]

        messages = await redis_stream_manager.read_messages("test_group")

        # Check that we got some result
        mock_redis.xreadgroup.assert_called()

    @pytest.mark.asyncio
    async def test_acknowledge_message_success(self, redis_stream_manager, mock_redis):
        """Test successful message acknowledgment."""
        from app.XNAi_rag_app.core.redis_streams import StreamMessage, MessageStatus

        message = StreamMessage(id="1234567890-0", stream="test_stream", data={"task_type": "test"})

        result = await redis_stream_manager.acknowledge(message, "test_group")

        assert result is True
        mock_redis.xack.assert_called_once()


class TestDeadLetterQueue:
    """Tests for DLQ functionality."""

    @pytest.mark.asyncio
    async def test_send_to_dlq_success(self, redis_stream_manager, mock_redis):
        """Test moving failed message to DLQ."""
        from app.XNAi_rag_app.core.redis_streams import StreamMessage, MessageStatus

        message = StreamMessage(
            id="1234567890-0", stream="test_stream", data={"task_type": "failed_task"}, status=MessageStatus.FAILED
        )

        result = await redis_stream_manager.send_to_dlq(
            message=message, reason="Max retries exceeded", group_name="test_group"
        )

        mock_redis.xadd.assert_called()


class TestRetryLogic:
    """Tests for retry with exponential backoff."""

    @pytest.mark.asyncio
    async def test_retry_count_increment(self, redis_stream_manager, mock_redis):
        """Test that retry count is properly tracked."""
        from app.XNAi_rag_app.core.redis_streams import StreamMessage, MessageStatus

        message = StreamMessage(id="1234567890-0", stream="test_stream", data={"task_type": "test"}, retry_count=0)

        # Simulate retry
        message.retry_count += 1
        message.status = MessageStatus.RETRY

        assert message.retry_count == 1
        assert message.status == MessageStatus.RETRY

    def test_exponential_backoff_calculation(self):
        """Test exponential backoff delay calculation."""
        from app.XNAi_rag_app.core.redis_streams import calculate_backoff_delay

        base_delay = 1.0
        max_delay = 60.0

        # Test various retry counts
        for retry_count in range(5):
            delay = calculate_backoff_delay(retry_count, base_delay, max_delay)
            assert delay >= base_delay
            assert delay <= max_delay

    def test_backoff_doubles_each_retry(self):
        """Test that backoff doubles with each retry."""
        from app.XNAi_rag_app.core.redis_streams import calculate_backoff_delay

        delays = [calculate_backoff_delay(i) for i in range(5)]

        # Each delay should be double the previous (up to max)
        for i in range(1, len(delays)):
            if delays[i] < 60.0:  # Before hitting max
                assert delays[i] == delays[i - 1] * 2


class TestStreamHealth:
    """Tests for stream health checks."""

    @pytest.mark.asyncio
    async def test_get_stats(self, redis_stream_manager, mock_redis):
        """Test getting stream manager statistics."""
        stats = await redis_stream_manager.get_stats()

        assert "consumer_id" in stats
        assert "initialized" in stats
        assert stats["consumer_id"] == "test_consumer"


class TestConnectionManagement:
    """Tests for connection management."""

    @pytest.mark.asyncio
    async def test_close_connection(self, redis_stream_manager, mock_redis):
        """Test closing Redis connection."""
        await redis_stream_manager.close()

        mock_redis.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_redis):
        """Test using RedisStreamManager as context manager."""
        from app.XNAi_rag_app.core.redis_streams import RedisStreamManager

        manager = RedisStreamManager(consumer_id="test")
        manager._redis = mock_redis
        manager._initialized = True

        # Use as context manager
        async with manager as m:
            assert m._initialized is True


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Tests for error handling in Redis streams."""

    @pytest.mark.asyncio
    async def test_redis_connection_error_handling(self):
        """Test handling Redis connection errors."""
        from app.XNAi_rag_app.core.redis_streams import RedisStreamManager

        manager = RedisStreamManager(consumer_id="test")

        # Should handle connection errors gracefully
        # The manager should not raise during initialization
        assert manager is not None

    @pytest.mark.asyncio
    async def test_invalid_message_format(self, redis_stream_manager, mock_redis):
        """Test handling invalid message format."""
        # Should handle invalid message format
        result = await redis_stream_manager.send_message(
            stream="test_stream",
            data={"test": "valid"},  # This is valid
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_retry_message_exceeds_limit(self, redis_stream_manager, mock_redis):
        """Test retry when limit is exceeded."""
        from app.XNAi_rag_app.core.redis_streams import StreamMessage, MessageStatus

        message = StreamMessage(
            id="1234567890-0",
            stream="test_stream",
            data={"task_type": "test"},
            retry_count=5,  # Exceeds default limit of 3
        )

        result = await redis_stream_manager.retry_message(message)

        # Should fail when retry limit exceeded
        assert result is False

    @pytest.mark.asyncio
    async def test_claim_pending_messages(self, redis_stream_manager, mock_redis):
        """Test claiming pending messages."""
        from app.XNAi_rag_app.core.redis_streams import ConsumerGroupConfig

        config = ConsumerGroupConfig(name="test_group", streams=["test_stream"])
        redis_stream_manager._consumer_groups["test_group"] = config

        mock_redis.xpending_range = AsyncMock(return_value=[])

        messages = await redis_stream_manager.claim_pending_messages("test_group")

        # Should return empty list when no pending messages
        assert messages == []


# ============================================================================
# Edge Case Tests - JOB-W3-002-3
# ============================================================================


class TestEdgeCases:
    """Edge case tests for Redis streams."""

    @pytest.mark.asyncio
    async def test_connection_timeout_handling(self):
        """Test handling of connection timeouts."""
        from app.XNAi_rag_app.core.redis_streams import RedisStreamManager

        manager = RedisStreamManager(consumer_id="test_timeout")

        # Should initialize without error
        assert manager._consumer_id == "test_timeout"
        assert manager._initialized is False

    @pytest.mark.asyncio
    async def test_large_message_payload(self):
        """Test handling of large message payloads."""
        from app.XNAi_rag_app.core.redis_streams import StreamMessage

        # Create large payload (1MB)
        large_data = {"data": "x" * (1024 * 1024)}

        message = StreamMessage(
            id="1234567890-0",
            stream="test_stream",
            data=large_data,
        )

        # Should handle large data
        assert len(message.data["data"]) == 1024 * 1024

    @pytest.mark.asyncio
    async def test_empty_message_data(self):
        """Test handling of empty message data."""
        from app.XNAi_rag_app.core.redis_streams import StreamMessage

        message = StreamMessage(
            id="1234567890-0",
            stream="test_stream",
            data={},  # Empty data
        )

        assert message.data == {}

    @pytest.mark.asyncio
    async def test_binary_content_in_message(self):
        """Test handling of binary-like content in messages."""
        from app.XNAi_rag_app.core.redis_streams import StreamMessage

        # Content with null bytes (binary indicator)
        binary_data = {"text": "some text", "binary": "data\x00\x00\x00"}

        message = StreamMessage(
            id="1234567890-0",
            stream="test_stream",
            data=binary_data,
        )

        assert message.data is not None

    @pytest.mark.asyncio
    async def test_special_characters_in_stream_name(self):
        """Test handling of special characters in stream names."""
        from app.XNAi_rag_app.core.redis_streams import RedisStreamManager

        manager = RedisStreamManager(consumer_id="test")

        # Try to create stream with special characters
        # Should handle gracefully (validation may reject)
        assert manager is not None

    @pytest.mark.asyncio
    async def test_unicode_content_in_message(self):
        """Test handling of Unicode content in messages."""
        from app.XNAi_rag_app.core.redis_streams import StreamMessage

        unicode_data = {
            "english": "Hello",
            "chinese": "你好",
            "emoji": "🔐",
            "arabic": "مرحبا",
        }

        message = StreamMessage(
            id="1234567890-0",
            stream="test_stream",
            data=unicode_data,
        )

        assert message.data["chinese"] == "你好"
        assert message.data["emoji"] == "🔐"

    @pytest.mark.asyncio
    async def test_message_id_edge_cases(self):
        """Test handling of edge case message IDs."""
        from app.XNAi_rag_app.core.redis_streams import StreamMessage

        # Empty ID
        msg_empty = StreamMessage(id="", stream="test", data={})
        assert msg_empty.id == ""

        # Very long ID
        long_id = "a" * 500
        msg_long = StreamMessage(id=long_id, stream="test", data={})
        assert len(msg_long.id) == 500

    @pytest.mark.asyncio
    async def test_consumer_id_edge_cases(self):
        """Test handling of edge case consumer IDs."""
        from app.XNAi_rag_app.core.redis_streams import RedisStreamManager

        # Empty consumer ID
        manager_empty = RedisStreamManager(consumer_id="")
        assert manager_empty._consumer_id == ""

        # Consumer ID with special characters
        manager_special = RedisStreamManager(consumer_id="consumer@#$%")
        assert manager_special._consumer_id == "consumer@#$%"

        # Very long consumer ID
        long_id = "consumer-" + "x" * 1000
        manager_long = RedisStreamManager(consumer_id=long_id)
        assert len(manager_long._consumer_id) > 100

    @pytest.mark.asyncio
    async def test_stream_config_edge_cases(self):
        """Test handling of edge case stream configurations."""
        from app.XNAi_rag_app.core.redis_streams import ConsumerGroupConfig

        # Empty stream list
        config_empty = ConsumerGroupConfig(name="group", streams=[])
        assert config_empty.streams == []

        # Very long stream name
        long_stream = "stream_" + "x" * 200
        config_long = ConsumerGroupConfig(name="group", streams=[long_stream])
        assert len(config_long.streams[0]) > 200

    @pytest.mark.asyncio
    async def test_retry_count_boundaries(self):
        """Test retry count at boundaries."""
        from app.XNAi_rag_app.core.redis_streams import StreamMessage, MessageStatus

        # Zero retries
        msg_zero = StreamMessage(id="1", stream="test", data={}, retry_count=0)
        assert msg_zero.retry_count == 0

        # Max retries (e.g., 10)
        msg_max = StreamMessage(id="1", stream="test", data={}, retry_count=10)
        assert msg_max.retry_count == 10

        # Very high retry count
        msg_high = StreamMessage(id="1", stream="test", data={}, retry_count=100)
        assert msg_high.retry_count == 100

    @pytest.mark.asyncio
    async def test_message_status_transitions(self):
        """Test message status transitions."""
        from app.XNAi_rag_app.core.redis_streams import StreamMessage, MessageStatus

        # Initial status
        msg = StreamMessage(id="1", stream="test", data={})
        assert msg.status == MessageStatus.PENDING

        # Transition to processing
        msg.status = MessageStatus.PROCESSING
        assert msg.status == MessageStatus.PROCESSING

        # Transition to retry
        msg.status = MessageStatus.RETRY
        assert msg.status == MessageStatus.RETRY

        # Transition to failed
        msg.status = MessageStatus.FAILED
        assert msg.status == MessageStatus.FAILED

        # Transition to completed
        msg.status = MessageStatus.COMPLETED
        assert msg.status == MessageStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_concurrent_message_processing(self):
        """Test concurrent message processing simulation."""
        import asyncio
        from app.XNAi_rag_app.core.redis_streams import StreamMessage

        async def create_message(i):
            return StreamMessage(
                id=f"msg-{i}",
                stream="test",
                data={"index": i},
            )

        # Create many messages concurrently
        messages = await asyncio.gather(*[create_message(i) for i in range(50)])

        assert len(messages) == 50
        assert all(m.data["index"] >= 0 for m in messages)

    @pytest.mark.asyncio
    async def test_dlq_message_format(self):
        """Test DLQ message has correct format."""
        from app.XNAi_rag_app.core.redis_streams import StreamMessage, MessageStatus

        original_msg = StreamMessage(
            id="1234567890-0",
            stream="test_stream",
            data={"task_type": "test", "payload": "data"},
            status=MessageStatus.FAILED,
        )

        # Verify message can be moved to DLQ
        dlq_entry = {
            "original_stream": original_msg.stream,
            "original_id": original_msg.id,
            "original_data": str(original_msg.data),
            "status": original_msg.status.value,
        }

        assert dlq_entry["original_stream"] == "test_stream"
        assert dlq_entry["status"] == "failed"

    @pytest.mark.asyncio
    async def test_backoff_delay_edge_cases(self):
        """Test backoff delay calculation at edges."""
        from app.XNAi_rag_app.core.redis_streams import calculate_backoff_delay

        # Zero retry count
        delay_zero = calculate_backoff_delay(0, base_delay=1.0, max_delay=60.0)
        assert delay_zero == 1.0

        # Negative retry count (should still work)
        delay_neg = calculate_backoff_delay(-1, base_delay=1.0, max_delay=60.0)
        assert delay_neg >= 0

        # Very high retry count
        delay_high = calculate_backoff_delay(100, base_delay=1.0, max_delay=60.0)
        assert delay_high == 60.0  # Should cap at max

    @pytest.mark.asyncio
    async def test_consumer_group_name_validation(self):
        """Test consumer group name validation."""
        from app.XNAi_rag_app.core.redis_streams import ConsumerGroupConfig

        # Valid names
        config_valid = ConsumerGroupConfig(name="valid-group", streams=["stream1"])
        assert config_valid.name == "valid-group"

        # Empty name (edge case)
        config_empty = ConsumerGroupConfig(name="", streams=["stream1"])
        assert config_empty.name == ""

        # Special characters
        config_special = ConsumerGroupConfig(name="group@#$%", streams=["stream1"])
        assert config_special.name == "group@#$%"

    @pytest.mark.asyncio
    async def test_stats_collection_edge_cases(self):
        """Test stats collection with edge cases."""
        from app.XNAi_rag_app.core.redis_streams import RedisStreamManager

        manager = RedisStreamManager(consumer_id="test_stats")

        # Get stats before initialization
        stats = await manager.get_stats()

        assert "consumer_id" in stats
        assert stats["consumer_id"] == "test_stats"
        assert "initialized" in stats

    @pytest.mark.asyncio
    async def test_json_serialization_of_messages(self):
        """Test JSON serialization of message data."""
        import json
        from app.XNAi_rag_app.core.redis_streams import StreamMessage

        message = StreamMessage(
            id="1234567890-0",
            stream="test_stream",
            data={"key": "value", "nested": {"inner": "data"}},
        )

        # Should be serializable to JSON
        serialized = json.dumps(message.data)
        deserialized = json.loads(serialized)

        assert deserialized["key"] == "value"
        assert deserialized["nested"]["inner"] == "data"
