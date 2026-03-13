#!/usr/bin/env python3
"""
Redis Stream Manager for XNAi Foundation
=========================================

Manages Redis Streams for multi-agent coordination with consumer groups
and dead letter queue (DLQ) support.

CLAUDE STANDARD: Uses AnyIO for structured concurrency.
Pattern: Multi-Agent Coordination (Phase 4.2.6)
Version: 1.0.0

Features:
- Consumer group management
- Message processing with acknowledgment
- Dead Letter Queue (DLQ) for failed tasks
- Automatic retry with exponential backoff
- Stream health monitoring
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

import anyio
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMERATIONS
# ============================================================================


class StreamType(str, Enum):
    """Redis stream types."""

    AGENT_BUS = "xnai:agent_bus"
    TASK_UPDATES = "xnai:task_updates"
    MEMORY_UPDATES = "xnai:memory_updates"
    ALERTS = "xnai:alerts"
    DLQ = "xnai:dlq"


class MessageStatus(str, Enum):
    """Message processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    DLQ = "dlq"


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class StreamMessage:
    """A message from Redis stream."""

    id: str
    stream: str
    data: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    retry_count: int = 0
    status: MessageStatus = MessageStatus.PENDING
    error: Optional[str] = None

    @classmethod
    def from_redis(cls, stream: str, message_id: bytes, data: Dict[bytes, bytes]) -> "StreamMessage":
        """Create from Redis XREADGROUP response."""
        decoded_data = {}
        for k, v in data.items():
            key = k.decode("utf-8") if isinstance(k, bytes) else k
            value = v.decode("utf-8") if isinstance(v, bytes) else v

            # Try to parse JSON
            try:
                decoded_data[key] = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                decoded_data[key] = value

        return cls(
            id=message_id.decode("utf-8") if isinstance(message_id, bytes) else message_id, stream=stream, data=decoded_data
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "stream": self.stream,
            "data": self.data,
            "timestamp": self.timestamp,
            "retry_count": self.retry_count,
            "status": self.status.value,
            "error": self.error,
        }


@dataclass
class DLQEntry:
    """Entry in the Dead Letter Queue."""

    original_message: StreamMessage
    failure_reason: str
    failed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_message": self.original_message.to_dict(),
            "failure_reason": self.failure_reason,
            "failed_at": self.failed_at,
            "retry_count": self.retry_count,
        }


@dataclass
class ConsumerGroupConfig:
    """Configuration for a consumer group."""

    name: str
    streams: List[str]
    consumer_prefix: str = "consumer_"
    block_ms: int = 5000
    batch_size: int = 10
    claim_idle_ms: int = 60000


@dataclass
class DLQConfig:
    """Dead Letter Queue configuration."""

    enabled: bool = True
    max_retention_seconds: int = 86400  # 24 hours
    retry_limit: int = 3
    retry_backoff_seconds: int = 60
    dlq_prefix: str = "xnai:dlq"
    max_len: int = 10000


# ============================================================================
# REDIS STREAM MANAGER
# ============================================================================


class RedisStreamManager:
    """
    Manages Redis Streams for multi-agent coordination.

    Features:
    - Consumer group creation and management
    - Message reading with acknowledgment
    - Dead Letter Queue for failed messages
    - Automatic retry with exponential backoff
    - Stream health monitoring

    Usage:
        manager = RedisStreamManager()
        await manager.initialize()

        # Read messages
        async for message in manager.read_messages("agent_wavefront"):
            try:
                await process_message(message)
                await manager.acknowledge(message)
            except Exception as e:
                await manager.send_to_dlq(message, str(e))
    """

    def __init__(self, redis: Optional[Redis] = None, consumer_id: Optional[str] = None):
        """Initialize stream manager."""
        self._redis = redis
        self._consumer_id = consumer_id or f"consumer_{os.getpid()}"
        self._initialized = False

        # Configuration
        self._consumer_groups: Dict[str, ConsumerGroupConfig] = {}
        self._dlq_config = DLQConfig()

        # Statistics
        self._stats = {"messages_read": 0, "messages_acknowledged": 0, "messages_failed": 0, "dlq_entries": 0}

    async def initialize(self) -> bool:
        """Initialize Redis connection and consumer groups."""
        if self._initialized:
            return True

        # Create Redis connection if not provided
        if not self._redis:
            host = os.getenv("REDIS_HOST", "localhost")
            port = int(os.getenv("REDIS_PORT", 6379))
            password = os.getenv("REDIS_PASSWORD") or None

            self._redis = Redis(host=host, port=port, password=password, decode_responses=False)

        # Create default consumer groups
        await self._create_default_consumer_groups()

        self._initialized = True
        logger.info(f"Redis stream manager initialized: {self._consumer_id}")
        return True

    async def _create_default_consumer_groups(self) -> None:
        """Create default consumer groups."""
        default_groups = [
            ConsumerGroupConfig(name="agent_wavefront", streams=[StreamType.AGENT_BUS.value, StreamType.TASK_UPDATES.value]),
            ConsumerGroupConfig(name="memory_sync", streams=[StreamType.MEMORY_UPDATES.value]),
            ConsumerGroupConfig(name="alert_handlers", streams=[StreamType.ALERTS.value]),
        ]

        for group in default_groups:
            await self.create_consumer_group(group)

    async def create_consumer_group(self, config: ConsumerGroupConfig) -> bool:
        """
        Create a consumer group for specified streams.

        Args:
            config: Consumer group configuration

        Returns:
            True if created successfully
        """
        try:
            for stream in config.streams:
                # Ensure stream exists
                try:
                    await self._redis.xadd(stream, {"_init": "true"})
                except Exception:
                    pass

                # Create consumer group
                try:
                    await self._redis.xgroup_create(name=stream, groupname=config.name, id="0", mkstream=True)
                    logger.info(f"Created consumer group: {config.name} for stream: {stream}")
                except Exception as e:
                    if "BUSYGROUP" not in str(e):
                        logger.warning(f"Consumer group creation failed: {e}")

            self._consumer_groups[config.name] = config
            return True

        except Exception as e:
            logger.error(f"Failed to create consumer group {config.name}: {e}")
            return False

    async def read_messages(
        self, group_name: str, count: Optional[int] = None, block_ms: Optional[int] = None
    ) -> List[StreamMessage]:
        """
        Read messages from consumer group.

        Args:
            group_name: Name of the consumer group
            count: Number of messages to read
            block_ms: Block time in milliseconds

        Returns:
            List of StreamMessage objects
        """
        if not self._initialized:
            await self.initialize()

        config = self._consumer_groups.get(group_name)
        if not config:
            logger.error(f"Consumer group not found: {group_name}")
            return []

        count = count or config.batch_size
        block_ms = block_ms or config.block_ms

        messages = []

        try:
            # Build streams dict for XREADGROUP
            streams = {stream: ">" for stream in config.streams}

            # Read new messages
            response = await self._redis.xreadgroup(
                groupname=group_name, consumername=self._consumer_id, streams=streams, count=count, block=block_ms
            )

            if response:
                for stream_name, stream_messages in response:
                    for msg_id, msg_data in stream_messages:
                        message = StreamMessage.from_redis(
                            stream=stream_name.decode("utf-8"), message_id=msg_id, data=msg_data
                        )
                        messages.append(message)
                        self._stats["messages_read"] += 1

        except Exception as e:
            logger.error(f"Failed to read messages: {e}")

        return messages

    async def acknowledge(self, message: StreamMessage, group_name: str) -> bool:
        """
        Acknowledge message processing.

        Args:
            message: The message to acknowledge
            group_name: The consumer group name

        Returns:
            True if acknowledged successfully
        """
        try:
            await self._redis.xack(message.stream, group_name, message.id)
            self._stats["messages_acknowledged"] += 1
            logger.debug(f"Acknowledged message: {message.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to acknowledge message {message.id}: {e}")
            return False

    async def send_to_dlq(self, message: StreamMessage, reason: str, group_name: Optional[str] = None) -> bool:
        """
        Send failed message to Dead Letter Queue.

        Args:
            message: The failed message
            reason: Failure reason
            group_name: Optional consumer group for acknowledgment

        Returns:
            True if sent to DLQ successfully
        """
        if not self._dlq_config.enabled:
            logger.warning(f"DLQ disabled, dropping message: {message.id}")
            return False

        try:
            # Create DLQ entry
            dlq_entry = DLQEntry(original_message=message, failure_reason=reason, retry_count=message.retry_count)

            # Determine DLQ stream
            dlq_stream = f"{self._dlq_config.dlq_prefix}:{message.stream}"

            # Add to DLQ
            await self._redis.xadd(
                dlq_stream,
                {"entry": json.dumps(dlq_entry.to_dict()), "failed_at": dlq_entry.failed_at, "original_id": message.id},
                maxlen=self._dlq_config.max_len,
            )

            # Acknowledge original message if group provided
            if group_name:
                await self.acknowledge(message, group_name)

            self._stats["messages_failed"] += 1
            self._stats["dlq_entries"] += 1

            logger.warning(
                f"Message sent to DLQ: {message.id} - {reason}",
                extra={"operation": "dlq_send", "message_id": message.id, "stream": message.stream, "reason": reason},
            )

            return True

        except Exception as e:
            logger.error(f"Failed to send message to DLQ: {e}")
            return False

    async def retry_message(self, message: StreamMessage) -> bool:
        """
        Retry a failed message.

        Args:
            message: The message to retry

        Returns:
            True if retry was initiated
        """
        if message.retry_count >= self._dlq_config.retry_limit:
            logger.warning(f"Message exceeded retry limit: {message.id}")
            return False

        try:
            # Increment retry count
            message.retry_count += 1
            message.status = MessageStatus.RETRY

            # Calculate backoff
            backoff = self._dlq_config.retry_backoff_seconds * (2 ** (message.retry_count - 1))

            # Re-add to stream with retry metadata
            retry_data = {**message.data, "_retry_count": str(message.retry_count), "_original_id": message.id}

            await self._redis.xadd(message.stream, retry_data)

            logger.info(
                f"Message retry initiated: {message.id} (attempt {message.retry_count})",
                extra={
                    "operation": "message_retry",
                    "message_id": message.id,
                    "retry_count": message.retry_count,
                    "backoff_seconds": backoff,
                },
            )

            return True

        except Exception as e:
            logger.error(f"Failed to retry message: {e}")
            return False

    async def send_message(self, stream: str, data: Dict[str, Any], max_len: int = 1000) -> str:
        """
        Send a message to a stream.

        Args:
            stream: Target stream name
            data: Message data
            max_len: Maximum stream length

        Returns:
            Message ID
        """
        try:
            # Encode data
            encoded_data = {}
            for k, v in data.items():
                if isinstance(v, (dict, list)):
                    encoded_data[k] = json.dumps(v)
                else:
                    encoded_data[k] = str(v)

            # Add to stream
            message_id = await self._redis.xadd(stream, encoded_data, maxlen=max_len)

            logger.debug(f"Message sent to {stream}: {message_id}")
            return message_id.decode("utf-8") if isinstance(message_id, bytes) else message_id

        except Exception as e:
            logger.error(f"Failed to send message to {stream}: {e}")
            raise

    async def claim_pending_messages(self, group_name: str, idle_ms: Optional[int] = None) -> List[StreamMessage]:
        """
        Claim pending messages that have been idle too long.

        Args:
            group_name: Consumer group name
            idle_ms: Idle time threshold

        Returns:
            List of claimed messages
        """
        config = self._consumer_groups.get(group_name)
        if not config:
            return []

        idle_ms = idle_ms or config.claim_idle_ms
        messages = []

        try:
            for stream in config.streams:
                # Get pending messages
                pending = await self._redis.xpending_range(name=stream, groupname=group_name, min="-", max="+", count=10)

                if not pending:
                    continue

                # Claim idle messages
                for entry in pending:
                    if entry.get("time_since_delivered", 0) > idle_ms:
                        msg_id = entry["message_id"]

                        claimed = await self._redis.xclaim(
                            name=stream,
                            groupname=group_name,
                            consumername=self._consumer_id,
                            min_idle_time=idle_ms,
                            message_ids=[msg_id],
                        )

                        if claimed:
                            for msg_id, msg_data in claimed:
                                message = StreamMessage.from_redis(stream, msg_id, msg_data)
                                message.status = MessageStatus.PROCESSING
                                messages.append(message)

        except Exception as e:
            logger.error(f"Failed to claim pending messages: {e}")

        return messages

    async def get_stats(self) -> Dict[str, Any]:
        """Get stream manager statistics."""
        return {
            **self._stats,
            "consumer_id": self._consumer_id,
            "consumer_groups": list(self._consumer_groups.keys()),
            "initialized": self._initialized,
        }

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.aclose()
            self._redis = None

        self._initialized = False
        logger.info("Redis stream manager closed")

    async def __aenter__(self) -> "RedisStreamManager":
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


def calculate_backoff_delay(retry_count: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """
    Calculate exponential backoff delay with maximum cap.

    Args:
        retry_count: Current retry attempt number (0-indexed, first retry is 0)
        base_delay: Base delay in seconds for first retry
        max_delay: Maximum delay cap in seconds

    Returns:
        Calculated delay in seconds

    Example:
        >>> calculate_backoff_delay(0)  # First retry
        1.0
        >>> calculate_backoff_delay(1)  # Second retry
        2.0
        >>> calculate_backoff_delay(2)  # Third retry
        4.0
        >>> calculate_backoff_delay(10)  # Capped at max
        60.0
    """
    # Use retry_count directly as exponent (0-indexed)
    return min(base_delay * (2 ** max(0, retry_count)), max_delay)


async def create_stream_manager(consumer_id: Optional[str] = None) -> RedisStreamManager:
    """Create and initialize a stream manager."""
    manager = RedisStreamManager(consumer_id=consumer_id)
    await manager.initialize()
    return manager
