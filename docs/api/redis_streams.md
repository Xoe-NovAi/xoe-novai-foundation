# Redis Stream Manager API

> **Module**: `XNAi_rag_app.core.redis_streams`
> **Version**: 1.0.0
> **Last Updated**: 2026-02-22

---

## Overview

Manages Redis Streams for multi-agent coordination with consumer groups and dead letter queue (DLQ) support. Provides message acknowledgment, automatic retry, and stream health monitoring.

---

## Classes

### RedisStreamManager

Main class for managing Redis Streams.

```python
from XNAi_rag_app.core.redis_streams import RedisStreamManager

# Initialize
manager = RedisStreamManager(
    redis=redis_client,    # Optional: creates new connection if None
    consumer_id="cline-1"  # Optional: defaults to consumer_<pid>
)

# Initialize connection
await manager.initialize()
```

---

## Stream Types

### Predefined Streams

```python
from XNAi_rag_app.core.redis_streams import StreamType

class StreamType(str, Enum):
    AGENT_BUS = "xnai:agent_bus"        # Agent coordination
    TASK_UPDATES = "xnai:task_updates"  # Task status updates
    MEMORY_UPDATES = "xnai:memory_updates"  # Memory bank changes
    ALERTS = "xnai:alerts"              # Alerts and escalations
    DLQ = "xnai:dlq"                    # Dead Letter Queue
```

---

## Methods

### Consumer Group Management

#### `create_consumer_group()`

Create a consumer group for specified streams.

```python
from XNAi_rag_app.core.redis_streams import ConsumerGroupConfig

config = ConsumerGroupConfig(
    name="agent_wavefront",
    streams=["xnai:agent_bus", "xnai:task_updates"],
    consumer_prefix="consumer_",
    block_ms=5000,
    batch_size=10,
    claim_idle_ms=60000
)

await manager.create_consumer_group(config)
```

---

### Message Operations

#### `read_messages()`

Read messages from consumer group.

```python
messages = await manager.read_messages(
    group_name="agent_wavefront",
    count=10,
    block_ms=5000
)

for message in messages:
    print(f"ID: {message.id}")
    print(f"Stream: {message.stream}")
    print(f"Data: {message.data}")
```

---

#### `send_message()`

Send a message to a stream.

```python
message_id = await manager.send_message(
    stream="xnai:agent_bus",
    data={
        "agent_id": "cline-1",
        "action": "task_complete",
        "task_id": "R003-1"
    },
    max_len=1000
)
```

---

#### `acknowledge()`

Acknowledge message processing.

```python
await manager.acknowledge(message, group_name="agent_wavefront")
```

---

### Dead Letter Queue

#### `send_to_dlq()`

Send failed message to Dead Letter Queue.

```python
await manager.send_to_dlq(
    message=message,
    reason="Processing failed: timeout",
    group_name="agent_wavefront"  # Optional: acknowledges original
)
```

---

#### `retry_message()`

Retry a failed message with exponential backoff.

```python
success = await manager.retry_message(message)
# Returns False if retry limit exceeded
```

---

### Pending Messages

#### `claim_pending_messages()`

Claim pending messages that have been idle too long.

```python
claimed = await manager.claim_pending_messages(
    group_name="agent_wavefront",
    idle_ms=60000  # Messages idle > 60 seconds
)

for message in claimed:
    await process_message(message)
```

---

### Statistics

#### `get_stats()`

Get stream manager statistics.

```python
stats = await manager.get_stats()
# {
#     "messages_read": 150,
#     "messages_acknowledged": 148,
#     "messages_failed": 2,
#     "dlq_entries": 2,
#     "consumer_id": "consumer_12345",
#     "consumer_groups": ["agent_wavefront", "memory_sync"],
#     "initialized": True
# }
```

---

## Data Classes

### StreamMessage

```python
@dataclass
class StreamMessage:
    id: str                    # Redis message ID
    stream: str                # Stream name
    data: Dict[str, Any]       # Message data
    timestamp: str             # ISO 8601 timestamp
    retry_count: int           # Number of retries
    status: MessageStatus      # Current status
    error: Optional[str]       # Error message if failed
    
    @classmethod
    def from_redis(cls, stream, message_id, data) -> "StreamMessage":
        """Create from Redis XREADGROUP response."""
        ...
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        ...
```

### MessageStatus

```python
class MessageStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    DLQ = "dlq"
```

---

## Configuration

### ConsumerGroupConfig

```python
@dataclass
class ConsumerGroupConfig:
    name: str                  # Consumer group name
    streams: List[str]         # Streams to consume
    consumer_prefix: str = "consumer_"
    block_ms: int = 5000       # Block time for reads
    batch_size: int = 10       # Max messages per read
    claim_idle_ms: int = 60000 # Idle time for claiming
```

### DLQConfig

```python
@dataclass
class DLQConfig:
    enabled: bool = True
    max_retention_seconds: int = 86400  # 24 hours
    retry_limit: int = 3
    retry_backoff_seconds: int = 60
    dlq_prefix: str = "xnai:dlq"
    max_len: int = 10000
```

---

## Usage Patterns

### Context Manager

```python
async with RedisStreamManager(consumer_id="cline-1") as manager:
    messages = await manager.read_messages("agent_wavefront")
    for message in messages:
        await process_message(message)
        await manager.acknowledge(message, "agent_wavefront")
```

### Message Processing Loop

```python
async def process_messages():
    manager = RedisStreamManager()
    await manager.initialize()
    
    while True:
        messages = await manager.read_messages("agent_wavefront")
        
        for message in messages:
            try:
                await process_message(message)
                await manager.acknowledge(message, "agent_wavefront")
            except Exception as e:
                await manager.send_to_dlq(message, str(e), "agent_wavefront")
        
        # Claim abandoned messages
        claimed = await manager.claim_pending_messages("agent_wavefront")
        for message in claimed:
            await process_message(message)
            await manager.acknowledge(message, "agent_wavefront")
```

### Agent Coordination

```python
# Agent publishes task update
await manager.send_message("xnai:task_updates", {
    "agent_id": "cline-1",
    "task_id": "R003-1",
    "status": "in_progress",
    "progress": "50%",
    "timestamp": datetime.now(timezone.utc).isoformat()
})

# MC-Overseer reads updates
updates = await manager.read_messages("agent_wavefront")
```

---

## Integration with Agent Bus

```python
from XNAi_rag_app.core.redis_streams import RedisStreamManager, StreamType

class AgentBusClient:
    def __init__(self):
        self.stream_manager = RedisStreamManager()
    
    async def publish_task(self, agent_id: str, task: dict):
        await self.stream_manager.send_message(
            StreamType.AGENT_BUS,
            {"agent_id": agent_id, "task": task}
        )
    
    async def subscribe_tasks(self, agent_id: str):
        async for message in self.stream_manager.read_messages("agent_wavefront"):
            if message.data.get("agent_id") == agent_id:
                yield message
```

---

## Error Handling

```python
try:
    messages = await manager.read_messages("agent_wavefront")
except Exception as e:
    logger.error(f"Failed to read messages: {e}")
    # Implement fallback or retry logic
```

---

## Convenience Functions

### `create_stream_manager()`

Create and initialize a stream manager.

```python
from XNAi_rag_app.core.redis_streams import create_stream_manager

manager = await create_stream_manager(consumer_id="cline-1")
```

---

## Related Modules

- [`knowledge_access`](./knowledge_access.md) - Knowledge access control
- [`sanitization`](./sanitization.md) - Content sanitization

---

**Source**: `app/XNAi_rag_app/core/redis_streams.py`
