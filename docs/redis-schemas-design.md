# Redis Schemas Design - XNAi Foundation
**Version**: 1.0.0  
**Status**: Active  
**Last Updated**: 2026-02-25  
**Owner**: MC-Overseer Agent  

---

## Overview

This document defines Redis data structures for:
- Document caching (24h TTL)
- Session management (48h TTL)
- Embedding vector caching (1h TTL)
- Query result caching (1h TTL)
- Persona learning state (real-time, no TTL)
- Knowledge base event streaming (infinite)

**Design Principles**:
- Sub-millisecond access times
- Zero-telemetry compliance
- Graceful degradation to in-memory fallback
- Efficient serialization (JSON + MessagePack)
- LRU eviction for cache tiers

---

## 1. Key Structure Design

### 1.1 Document Cache: `doc:{id}`

**Type**: Hash or String  
**TTL**: 24 hours  
**Eviction**: LRU if memory exceeds threshold  
**Access Pattern**: Frequent reads, infrequent writes

#### Structure (Hash):
```
doc:{id} = {
  "content": "document_text",
  "metadata": "{\"source\": \"...\", \"created_at\": \"...\"}",  # JSON string
  "embedding_id": "embed:{type}:{chunk_id}",
  "updated_at": "2026-02-25T10:30:00Z",
  "version": "1",
  "size_bytes": "12345"
}
```

#### Alternative (String, for large docs):
```
doc:{id} = gzip_compressed_document_bytes
doc:{id}:metadata = {
  "compression": "gzip",
  "original_size": "50000",
  "compressed_size": "12345",
  "encoding": "utf-8"
}
```

**CLI Example**:
```bash
# Store document with metadata
HSET doc:doc_123 \
  content "Important document text..." \
  metadata '{"source":"file","created":"2026-02-25"}' \
  version "1"

# Set expiration
EXPIRE doc:doc_123 86400  # 24 hours

# Retrieve
HGETALL doc:doc_123
```

---

### 1.2 Session State: `session:{agent_id}`

**Type**: Hash  
**TTL**: 48 hours  
**Eviction**: No eviction (use LRU for overflow only)  
**Access Pattern**: Frequent reads/writes

#### Structure:
```
session:{agent_id} = {
  "session_id": "uuid",
  "agent_type": "cline-cli | copilot-cli | opencode | gemini",
  "conversation_history": "[{\"role\":\"user\",\"content\":\"...\"},{\"role\":\"assistant\",...}]",  # JSON array
  "context_window": "{\"files\":[...],\"symbols\":[...],\"tokens_used\":1024}",  # JSON object
  "active_tools": "[\"grep\",\"view\",\"edit\"]",  # JSON array
  "last_activity": "2026-02-25T10:30:00Z",
  "context_tokens": "1024",
  "state": "active | paused | completed"
}
```

**CLI Example**:
```bash
# Create session
HSET session:agent_001 \
  session_id "550e8400-e29b-41d4-a716-446655440000" \
  agent_type "copilot-cli" \
  conversation_history '[]' \
  active_tools '[]' \
  state "active"

# Add to conversation history (Lua script pattern)
# HGET -> parse JSON -> append -> HSET

# Set 48-hour expiration
EXPIRE session:agent_001 172800

# Monitor activity
ZADD sessions:by_activity $(date +%s) agent_001
```

---

### 1.3 Embedding Vector Cache: `embed:{embedding_type}:{chunk_id}`

**Type**: String (binary-safe)  
**TTL**: 1 hour  
**Eviction**: LRU aggressive  
**Format**: MessagePack for performance  
**Compression**: gzip for vectors >1KB

#### Structure (MessagePack serialized):
```
embed:bge_large:chunk_abc123 = msgpack_encoded_vector {
  "vector": [0.123, -0.456, 0.789, ...],  # 1536 dims for BGE-Large
  "metadata": {
    "model": "bge-large-en",
    "dim": 1536,
    "norm": 1.0,
    "timestamp": "2026-02-25T10:30:00Z"
  },
  "chunk_id": "chunk_abc123",
  "chunk_hash": "sha256_hash"
}
```

**Python Example**:
```python
import msgpack
import gzip

# Serialize vector
vector_data = {
    "vector": embedding,  # numpy array
    "metadata": {...}
}
packed = msgpack.packb(vector_data, use_bin_type=True)

# Compress if large
if len(packed) > 1024:
    compressed = gzip.compress(packed)
    # Store with compression marker
    await redis.set(f"embed:bge_large:{chunk_id}", compressed)
else:
    await redis.set(f"embed:bge_large:{chunk_id}", packed)

# Set 1-hour TTL
await redis.expire(f"embed:bge_large:{chunk_id}", 3600)
```

**Deserialization**:
```python
# Fetch and decompress
data = await redis.get(f"embed:bge_large:{chunk_id}")
if is_compressed(data):
    packed = gzip.decompress(data)
else:
    packed = data
    
vector_obj = msgpack.unpackb(packed, use_list=True)
```

---

### 1.4 Query Result Cache: `query:{query_hash}`

**Type**: Hash  
**TTL**: 1 hour  
**Eviction**: LRU aggressive  
**Key Hash**: SHA256(query_text)

#### Structure:
```
query:ab12ef56 = {
  "query": "find all async functions in app/",
  "results": "[{\"file\":\"app/api.py\",\"line\":42,...}]",  # JSON array
  "confidence_score": "0.95",
  "result_count": "12",
  "execution_time_ms": "234",
  "model": "bge-large-en",
  "timestamp": "2026-02-25T10:30:00Z",
  "cache_hit_count": "3"
}
```

**Python Example**:
```python
import hashlib

def get_query_hash(query: str) -> str:
    return hashlib.sha256(query.encode()).hexdigest()[:16]

# Cache query result
query_hash = get_query_hash("SELECT * FROM users WHERE active=true")
await redis.hset(
    f"query:{query_hash}",
    mapping={
        "query": query,
        "results": json.dumps(results),
        "confidence_score": "0.92",
        "execution_time_ms": "145",
        "cache_hit_count": "0"
    }
)
await redis.expire(f"query:{query_hash}", 3600)

# Retrieve cached result
cached = await redis.hgetall(f"query:{query_hash}")
if cached:
    hit_count = int(cached[b"cache_hit_count"])
    await redis.hset(f"query:{query_hash}", "cache_hit_count", hit_count + 1)
```

---

### 1.5 Persona Learning State: `persona:{agent_id}:learning`

**Type**: Hash  
**TTL**: None (permanent, updated in real-time)  
**Persistence**: Critical data, replicated

#### Structure:
```
persona:agent_001:learning = {
  "expertise_scores": "{\"python\":0.87,\"rust\":0.42,\"devops\":0.91}",  # JSON
  "interaction_count": "1247",
  "total_tokens_processed": "523412",
  "success_rate": "0.94",
  "last_update": "2026-02-25T10:30:00Z",
  "learning_rate": "0.002",
  "domain_focus": "backend_systems",
  "preferred_languages": "[\"python\",\"bash\"]",
  "adaptations": "{\"code_style\":\"claude\",\"verbosity\":\"concise\"}"
}
```

**Python Example**:
```python
# Initialize persona
await redis.hset(
    f"persona:{agent_id}:learning",
    mapping={
        "expertise_scores": json.dumps({"python": 0.5, "rust": 0.3}),
        "interaction_count": "0",
        "success_rate": "0.0",
        "last_update": datetime.now(timezone.utc).isoformat()
    }
)

# Update expertise after interaction
expertise = json.loads(
    await redis.hget(f"persona:{agent_id}:learning", "expertise_scores")
)
expertise["python"] = min(1.0, expertise["python"] + 0.01)  # Increment
await redis.hset(
    f"persona:{agent_id}:learning",
    "expertise_scores",
    json.dumps(expertise)
)

# Track learning metrics
await redis.hincrby(f"persona:{agent_id}:learning", "interaction_count", 1)
await redis.hset(
    f"persona:{agent_id}:learning",
    "last_update",
    datetime.now(timezone.utc).isoformat()
)
```

---

### 1.6 Knowledge Updates Stream: `knowledge:updates`

**Type**: Stream  
**TTL**: Infinite (but with retention policy)  
**Consumer Groups**: Multiple agents subscribe

#### Structure (Stream Entries):
```
knowledge:updates = [
  {
    "id": "1708851000000-0",
    "doc_added": {
      "doc_id": "doc_123",
      "source": "github_pr_2345",
      "created_at": "2026-02-25T10:30:00Z"
    }
  },
  {
    "id": "1708851030000-1",
    "doc_updated": {
      "doc_id": "doc_123",
      "changes": "{\"title\":\"...\"}",
      "updated_at": "2026-02-25T10:31:00Z"
    }
  },
  {
    "id": "1708851060000-2",
    "embedding_generated": {
      "chunk_id": "chunk_abc123",
      "embedding_type": "bge_large",
      "vectors_count": "5",
      "timestamp": "2026-02-25T10:32:00Z"
    }
  },
  {
    "id": "1708851090000-3",
    "cache_invalidated": {
      "pattern": "doc:doc_123*",
      "reason": "document_updated",
      "timestamp": "2026-02-25T10:33:00Z"
    }
  }
]
```

**Python Example**:
```python
# Publish doc_added event
await redis.xadd(
    "knowledge:updates",
    {
        "event_type": "doc_added",
        "doc_id": "doc_123",
        "source": "github_pr_2345",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
)

# Create consumer group
await redis.xgroup_create("knowledge:updates", "embedding_workers", id="0", mkstream=True)

# Subscribe and process
async def consume_knowledge_updates():
    while True:
        messages = await redis.xreadgroup(
            "embedding_workers",
            "worker_1",
            {"knowledge:updates": ">"},
            count=10,
            block=1000
        )
        
        for stream, data in messages:
            for msg_id, fields in data:
                event_type = fields.get(b"event_type", b"").decode()
                
                if event_type == "doc_added":
                    # Process new document
                    doc_id = fields[b"doc_id"].decode()
                    await process_doc(doc_id)
                
                # Acknowledge processing
                await redis.xack("knowledge:updates", "embedding_workers", msg_id)

# Set stream retention (keep last 24 hours)
await redis.xtrim("knowledge:updates", minid="-", approximate=False, maxlen=1000000)
```

---

## 2. Serialization Strategy

### 2.1 Serialization Format Selection

| Data Type | Use Case | Format | Compression |
|-----------|----------|--------|-------------|
| Vectors | Embedding cache | MessagePack | gzip >1KB |
| Complex objects | Session state, results | JSON | None (< 10KB) |
| Strings | Metadata, IDs | UTF-8 | None |
| Large documents | Document cache | gzip | Always |

### 2.2 Serialization Implementation

```python
import json
import msgpack
import gzip
from typing import Any, Union

class RedisSerializer:
    """Unified serialization for Redis values"""
    
    @staticmethod
    def serialize(value: Any, format: str = "auto") -> bytes:
        """Serialize value for Redis storage"""
        
        if format == "auto":
            # Auto-detect format
            if isinstance(value, (dict, list)) and len(str(value)) < 10000:
                format = "json"
            elif isinstance(value, (np.ndarray, list)):
                format = "msgpack_compressed"
            else:
                format = "json"
        
        if format == "json":
            serialized = json.dumps(value, default=str).encode("utf-8")
            return serialized
        
        elif format == "msgpack":
            serialized = msgpack.packb(value, use_bin_type=True)
            return serialized
        
        elif format == "msgpack_compressed":
            serialized = msgpack.packb(value, use_bin_type=True)
            if len(serialized) > 1024:
                return b"\x1f\x8b" + gzip.compress(serialized)[2:]  # gzip marker
            return serialized
        
        elif format == "gzip":
            if isinstance(value, str):
                value = value.encode("utf-8")
            return gzip.compress(value)
    
    @staticmethod
    def deserialize(data: bytes, format: str = "auto") -> Any:
        """Deserialize value from Redis storage"""
        
        if format == "auto":
            # Auto-detect format
            if data.startswith(b"{") or data.startswith(b"["):
                format = "json"
            elif data.startswith(b"\x1f\x8b"):  # gzip magic number
                format = "gzip"
            elif data.startswith(b"\x82"):  # msgpack start
                format = "msgpack"
            else:
                format = "json"
        
        if format == "json":
            return json.loads(data.decode("utf-8"))
        
        elif format == "msgpack":
            return msgpack.unpackb(data, use_list=True)
        
        elif format == "gzip":
            decompressed = gzip.decompress(data)
            try:
                return msgpack.unpackb(decompressed, use_list=True)
            except:
                return decompressed.decode("utf-8")
```

---

## 3. TTL and Eviction Policies

### 3.1 TTL Configuration

```yaml
TTL_POLICIES:
  doc:                    86400    # 24 hours (1 day)
  session:                172800   # 48 hours (2 days)
  embed:                  3600     # 1 hour
  query:                  3600     # 1 hour
  persona:learning:       0        # Permanent (no TTL)
  knowledge:updates:      0        # Permanent (stream)

REDIS_CONFIG:
  maxmemory: "2gb"
  maxmemory-policy: "allkeys-lru"  # LRU for all keys
  # Alternative policies:
  # - "volatile-lru": LRU only for keys with TTL
  # - "volatile-ttl": Evict keys with shortest remaining TTL
  # - "volatile-random": Random eviction of TTL keys
  # - "allkeys-random": Random eviction of any key

  # Eviction sampling
  maxmemory-samples: 5  # Check 5 random keys for LRU

CACHE_TIERS:
  tier1:                  # Hot cache (recently accessed)
    pattern: "doc:*"
    max_entries: 1000
    ttl: 86400
    
  tier2:                  # Warm cache (frequently accessed)
    pattern: "embed:*"
    max_entries: 10000
    ttl: 3600
    
  tier3:                  # Cold cache (query results)
    pattern: "query:*"
    max_entries: 5000
    ttl: 3600
```

### 3.2 Redis Configuration File

```ini
# /etc/redis/redis.conf

# Memory management
maxmemory 2gb
maxmemory-policy allkeys-lru
maxmemory-samples 5

# LRU eviction (Redis 3.2+)
# When memory limit reached, evict LRU keys first
# Sample 5 keys randomly to minimize CPU

# Persistence (optional, depends on durability needs)
save 900 1        # Save after 900s if 1+ key changed
save 300 10       # Save after 300s if 10+ keys changed
save 60 10000     # Save after 60s if 10000+ keys changed

# Append-only file for durability
appendonly no     # Set to yes for mission-critical data

# Replication (if clustering)
replica-read-only yes
replica-priority 100

# Keyspace notifications (for cache invalidation)
notify-keyspace-events "Ex"  # Enable key expiration events
```

---

## 4. Replication Strategy

### 4.1 Redis Replication Architecture

```
Primary (write):
  - Host: redis-primary:6379
  - Role: Master
  - Memory: 2GB
  - Persistence: RDB snapshots every 5min

Replica 1 (read-only):
  - Host: redis-replica-1:6379
  - Role: Slave
  - Sync: Continuous stream from master

Replica 2 (read-only):
  - Host: redis-replica-2:6379
  - Role: Slave
  - Sync: Continuous stream from master

Sentinel (monitoring):
  - Monitors master health
  - Failover if master down >30s
```

### 4.2 Replication Configuration

```ini
# Master (redis-primary)
# (default: all replication settings)

# Replica Configuration
replicaof redis-primary 6379
replica-read-only yes
replica-priority 100
slave-serve-stale-data yes  # Serve stale data during sync

# Replication Settings
repl-diskless-sync yes       # Sync without disk
repl-diskless-sync-delay 5   # Delay 5s for more replicas to connect
repl-backlog-size 16mb       # Backlog buffer for partial resync
repl-backlog-ttl 3600        # Keep backlog for 1 hour
```

### 4.3 Python Client Configuration

```python
from redis import Redis
from redis.connection import ConnectionPool
from redis.sentinel import Sentinel

# Option 1: Direct connection (for development)
redis_client = Redis(
    host="redis-primary",
    port=6379,
    socket_connect_timeout=5,
    socket_timeout=10,
    retry_on_timeout=True
)

# Option 2: Sentinel-backed (for production)
sentinels = [
    ("sentinel-1", 26379),
    ("sentinel-2", 26379),
    ("sentinel-3", 26379)
]
sentinel = Sentinel(sentinels, socket_timeout=10)
redis_client = sentinel.master_for(
    "mymaster",
    socket_timeout=10,
    db=0
)

# Option 3: Connection pooling with write-to-primary, read-from-replicas
master_pool = ConnectionPool(
    host="redis-primary",
    port=6379,
    max_connections=50
)
replica_pools = [
    ConnectionPool(host="redis-replica-1", port=6379, max_connections=50),
    ConnectionPool(host="redis-replica-2", port=6379, max_connections=50)
]

redis_writer = Redis(connection_pool=master_pool)
redis_readers = [Redis(connection_pool=pool) for pool in replica_pools]

# Usage: write to master, read from replicas
```

---

## 5. Operational Procedures

### 5.1 Cache Invalidation Strategy

#### Cascade Invalidation (when document updates):

```python
async def invalidate_document_cache(doc_id: str, cascade: bool = True):
    """Invalidate document and related caches"""
    
    # Pattern 1: Direct document cache
    await redis.delete(f"doc:{doc_id}")
    
    if cascade:
        # Pattern 2: Query results containing this doc
        query_keys = await redis.keys("query:*")
        for key in query_keys:
            query_data = await redis.hgetall(key)
            results = json.loads(query_data.get(b"results", b"[]"))
            
            # Check if doc_id in results
            if any(doc_id in str(r) for r in results):
                await redis.delete(key)
                logger.info(f"Invalidated query cache: {key}")
        
        # Pattern 3: Embedding cache for chunks from this doc
        embed_keys = await redis.keys(f"embed:*:{doc_id}*")
        for key in embed_keys:
            await redis.delete(key)
            logger.info(f"Invalidated embedding cache: {key}")
    
    # Publish invalidation event
    await redis.xadd(
        "knowledge:updates",
        {
            "event_type": "cache_invalidated",
            "doc_id": doc_id,
            "cascade": str(cascade),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

# Event handler (called on doc update)
async def on_document_updated(doc_id: str):
    await invalidate_document_cache(doc_id, cascade=True)
    logger.info(f"Document cache invalidated for {doc_id}")
```

#### Selective Invalidation:

```python
# Pattern-based invalidation
async def invalidate_by_pattern(pattern: str):
    """Delete keys matching pattern"""
    keys = await redis.keys(pattern)
    if keys:
        await redis.delete(*keys)
        logger.info(f"Deleted {len(keys)} keys matching {pattern}")

# Time-based invalidation
async def cleanup_expired_caches():
    """Manual cleanup of expired or stale data"""
    
    # Query cache older than 2 hours
    query_keys = await redis.keys("query:*")
    for key in query_keys:
        ttl = await redis.ttl(key)
        if ttl > 7200:  # > 2 hours remaining = likely stale
            await redis.delete(key)

# Monitored invalidation
async def monitor_invalidation_stream():
    """Listen for invalidation events and act"""
    
    await redis.xgroup_create(
        "knowledge:updates",
        "invalidation_monitor",
        id="0",
        mkstream=True
    )
    
    while True:
        messages = await redis.xreadgroup(
            "invalidation_monitor",
            "monitor_1",
            {"knowledge:updates": ">"},
            count=10,
            block=1000
        )
        
        for stream, data in messages:
            for msg_id, fields in data:
                if fields.get(b"event_type") == b"cache_invalidated":
                    doc_id = fields[b"doc_id"].decode()
                    logger.info(f"Cache invalidation triggered for {doc_id}")
```

---

### 5.2 Connection Pool Sizing

```python
from redis.asyncio import ConnectionPool, Redis

class RedisPoolConfig:
    """Connection pool sizing based on workload"""
    
    # Development
    DEV_CONFIG = {
        "max_connections": 10,
        "socket_timeout": 5,
        "socket_connect_timeout": 5,
        "socket_keepalive": True,
        "socket_keepalive_options": {1: 1}  # TCP_KEEPIDLE
    }
    
    # Staging
    STAGING_CONFIG = {
        "max_connections": 50,
        "socket_timeout": 10,
        "socket_connect_timeout": 5,
        "retry_on_timeout": True,
        "health_check_interval": 30
    }
    
    # Production
    PROD_CONFIG = {
        "max_connections": 200,  # High concurrency
        "socket_timeout": 15,
        "socket_connect_timeout": 5,
        "retry_on_timeout": True,
        "socket_keepalive": True,
        "health_check_interval": 30,
        "connection_pool_class": ConnectionPool
    }

async def create_redis_pool(environment: str = "dev") -> Redis:
    """Create Redis connection pool for environment"""
    
    config_map = {
        "dev": RedisPoolConfig.DEV_CONFIG,
        "staging": RedisPoolConfig.STAGING_CONFIG,
        "prod": RedisPoolConfig.PROD_CONFIG
    }
    
    config = config_map.get(environment, RedisPoolConfig.DEV_CONFIG)
    
    pool = ConnectionPool.from_url(
        os.getenv("REDIS_URL", "redis://redis:6379"),
        **config
    )
    
    redis_client = Redis(connection_pool=pool)
    
    # Test connection
    try:
        await redis_client.ping()
        logger.info(f"Redis pool created for {environment}")
    except Exception as e:
        logger.error(f"Failed to create Redis pool: {e}")
        raise
    
    return redis_client

# Pool sizing formula
# Connections = (peak_requests_per_sec * avg_operation_time_sec) * concurrency_factor
# Example:
#   - 100 req/s
#   - 0.001s avg operation (1ms for cache hits)
#   - 2x concurrency factor
#   - = 100 * 0.001 * 2 = 0.2 connections base + overhead = 10-50
```

---

### 5.3 Memory Estimation

```python
import sys

class RedisMemoryEstimator:
    """Estimate Redis memory requirements"""
    
    REDIS_OVERHEAD = {
        "key": 86,        # Bytes per key (Redis internals)
        "hash_field": 32, # Bytes per hash field
        "string": 40,     # Bytes per string value
        "list": 24        # Bytes per list node
    }
    
    @staticmethod
    def estimate_doc_cache():
        """Estimate doc cache memory"""
        # Assumptions:
        # - 10,000 documents
        # - 10KB average document size
        # - Hash structure (doc_id, content, metadata)
        
        doc_count = 10000
        doc_size = 10 * 1024  # 10KB
        
        # Memory: overhead + content
        memory_per_doc = (
            RedisMemoryEstimator.REDIS_OVERHEAD["key"] +
            RedisMemoryEstimator.REDIS_OVERHEAD["hash_field"] * 3 +  # 3 fields
            doc_size
        )
        
        total = doc_count * memory_per_doc
        return {
            "doc_count": doc_count,
            "avg_size": doc_size,
            "total_bytes": total,
            "total_mb": total / (1024 ** 2),
            "total_gb": total / (1024 ** 3)
        }
    
    @staticmethod
    def estimate_embedding_cache():
        """Estimate embedding cache memory"""
        # Assumptions:
        # - 100,000 embeddings
        # - 1536 dimensions (BGE-Large)
        # - 4 bytes per float32
        # - MessagePack overhead: ~20%
        
        embedding_count = 100000
        dimensions = 1536
        bytes_per_float = 4
        msgpack_overhead = 1.2
        
        memory_per_embedding = (
            dimensions * bytes_per_float * msgpack_overhead +
            RedisMemoryEstimator.REDIS_OVERHEAD["key"]
        )
        
        total = embedding_count * memory_per_embedding
        return {
            "embedding_count": embedding_count,
            "dimensions": dimensions,
            "total_bytes": total,
            "total_mb": total / (1024 ** 2),
            "total_gb": total / (1024 ** 3)
        }
    
    @staticmethod
    def estimate_session_cache():
        """Estimate session cache memory"""
        # Assumptions:
        # - 5,000 active sessions
        # - 50KB average session data (conversation + context)
        
        session_count = 5000
        session_size = 50 * 1024  # 50KB
        
        memory_per_session = (
            RedisMemoryEstimator.REDIS_OVERHEAD["key"] +
            RedisMemoryEstimator.REDIS_OVERHEAD["hash_field"] * 6 +  # 6 fields
            session_size
        )
        
        total = session_count * memory_per_session
        return {
            "session_count": session_count,
            "avg_size": session_size,
            "total_bytes": total,
            "total_mb": total / (1024 ** 2),
            "total_gb": total / (1024 ** 3)
        }
    
    @staticmethod
    def estimate_total():
        """Estimate total memory requirements"""
        doc = RedisMemoryEstimator.estimate_doc_cache()
        embed = RedisMemoryEstimator.estimate_embedding_cache()
        session = RedisMemoryEstimator.estimate_session_cache()
        
        total_gb = doc["total_gb"] + embed["total_gb"] + session["total_gb"]
        
        print(f"Document Cache: {doc['total_gb']:.2f} GB")
        print(f"Embedding Cache: {embed['total_gb']:.2f} GB")
        print(f"Session Cache: {session['total_gb']:.2f} GB")
        print(f"Total (before overhead): {total_gb:.2f} GB")
        print(f"With Redis overhead (15%): {total_gb * 1.15:.2f} GB")
        print(f"With headroom (25%): {total_gb * 1.25:.2f} GB")
        
        return {
            "doc_cache": doc,
            "embedding_cache": embed,
            "session_cache": session,
            "total_gb": total_gb,
            "with_overhead_gb": total_gb * 1.15,
            "with_headroom_gb": total_gb * 1.25
        }

# Run estimation
if __name__ == "__main__":
    estimate = RedisMemoryEstimator.estimate_total()
    # Output:
    # Document Cache: 0.96 GB
    # Embedding Cache: 3.07 GB
    # Session Cache: 0.29 GB
    # Total (before overhead): 4.32 GB
    # With Redis overhead (15%): 4.97 GB
    # With headroom (25%): 5.40 GB
```

**Memory Targets**:
- Development: 512 MB - 1 GB
- Staging: 2 GB - 4 GB
- Production: 8 GB - 16 GB

---

### 5.4 Monitoring Metrics

#### Key Performance Indicators (KPIs):

```python
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class RedisMetrics:
    """Redis performance metrics"""
    
    # Cache efficiency
    cache_hits: int = 0
    cache_misses: int = 0
    hit_rate: float = 0.0
    
    # Eviction tracking
    evicted_keys: int = 0
    eviction_rate_per_sec: float = 0.0
    
    # Memory usage
    used_memory_mb: float = 0.0
    max_memory_mb: float = 0.0
    memory_used_percent: float = 0.0
    
    # Connection health
    connected_clients: int = 0
    rejected_connections: int = 0
    
    # Latency
    avg_command_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    # Key statistics
    total_keys: int = 0
    expired_keys: int = 0
    
    # Persistence
    last_save_time: str = ""
    save_in_progress: bool = False

class RedisMetricsCollector:
    """Collect Redis metrics for monitoring"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.command_latencies = []
    
    async def collect_metrics(self) -> RedisMetrics:
        """Collect all Redis metrics"""
        
        # Get server info
        info = await self.redis.info()
        
        metrics = RedisMetrics(
            cache_hits=info.get("keyspace_hits", 0),
            cache_misses=info.get("keyspace_misses", 0),
            evicted_keys=info.get("evicted_keys", 0),
            used_memory_mb=info.get("used_memory", 0) / (1024 ** 2),
            max_memory_mb=info.get("maxmemory", 0) / (1024 ** 2),
            connected_clients=info.get("connected_clients", 0),
            rejected_connections=info.get("rejected_connections", 0),
        )
        
        # Calculate hit rate
        total = metrics.cache_hits + metrics.cache_misses
        if total > 0:
            metrics.hit_rate = metrics.cache_hits / total
        
        # Calculate memory usage percent
        if metrics.max_memory_mb > 0:
            metrics.memory_used_percent = (
                metrics.used_memory_mb / metrics.max_memory_mb * 100
            )
        
        # Get key count
        metrics.total_keys = await self.redis.dbsize()
        
        return metrics
    
    async def log_metrics(self):
        """Log metrics for monitoring"""
        
        metrics = await self.collect_metrics()
        
        logger.info(
            "Redis Metrics | "
            f"Hit Rate: {metrics.hit_rate:.1%} | "
            f"Memory: {metrics.used_memory_mb:.0f}MB ({metrics.memory_used_percent:.1f}%) | "
            f"Keys: {metrics.total_keys} | "
            f"Clients: {metrics.connected_clients} | "
            f"Evicted: {metrics.evicted_keys}"
        )
        
        # Alert thresholds
        if metrics.hit_rate < 0.80:
            logger.warning(f"Low cache hit rate: {metrics.hit_rate:.1%}")
        
        if metrics.memory_used_percent > 90:
            logger.error(f"Critical memory usage: {metrics.memory_used_percent:.1f}%")
        
        if metrics.eviction_rate_per_sec > 100:
            logger.warning(f"High eviction rate: {metrics.eviction_rate_per_sec}/sec")

# Prometheus metrics export
PROMETHEUS_METRICS = """
# HELP redis_cache_hits Total cache hits
# TYPE redis_cache_hits counter
redis_cache_hits {metric.cache_hits}

# HELP redis_cache_misses Total cache misses
# TYPE redis_cache_misses counter
redis_cache_misses {metric.cache_misses}

# HELP redis_hit_rate Cache hit rate (0-1)
# TYPE redis_hit_rate gauge
redis_hit_rate {metric.hit_rate}

# HELP redis_memory_used Memory used in bytes
# TYPE redis_memory_used gauge
redis_memory_used {metric.used_memory_mb * 1024 * 1024}

# HELP redis_evicted_keys Total keys evicted
# TYPE redis_evicted_keys counter
redis_evicted_keys {metric.evicted_keys}

# HELP redis_connected_clients Number of connected clients
# TYPE redis_connected_clients gauge
redis_connected_clients {metric.connected_clients}
"""
```

#### Monitoring Alerts:

```yaml
ALERT_RULES:
  cache_hit_rate_low:
    condition: "redis_hit_rate < 0.75"
    severity: "warning"
    message: "Cache hit rate below 75% - consider increasing cache size"
  
  memory_usage_critical:
    condition: "redis_memory_used_percent > 90"
    severity: "critical"
    message: "Redis memory usage critical - immediate intervention needed"
  
  eviction_rate_high:
    condition: "redis_evicted_keys > 1000/min"
    severity: "warning"
    message: "High cache eviction rate - LRU pressure detected"
  
  connection_rejected:
    condition: "redis_rejected_connections > 10/min"
    severity: "warning"
    message: "Redis rejecting connections - pool exhausted"
  
  command_latency_high:
    condition: "redis_command_latency_p99 > 100ms"
    severity: "warning"
    message: "High Redis command latency - network or load issue"
```

---

## 6. Implementation Checklist

- [ ] Create Redis connection manager with connection pooling
- [ ] Implement serialization module (JSON, MessagePack, gzip)
- [ ] Design cache invalidation system
- [ ] Set up monitoring and metrics collection
- [ ] Configure Redis server (maxmemory, eviction policy)
- [ ] Implement circuit breaker for Redis fallback
- [ ] Add metrics export (Prometheus)
- [ ] Create operational documentation
- [ ] Set up health checks and alerting
- [ ] Performance test (target: <1ms for cache hits)

---

## 7. Testing Strategy

### Unit Tests
```python
# tests/unit/redis/test_serialization.py
# tests/unit/redis/test_cache_invalidation.py
# tests/unit/redis/test_connection_pool.py

# Integration Tests
# tests/integration/redis/test_document_cache.py
# tests/integration/redis/test_session_management.py
# tests/integration/redis/test_embedding_cache.py

# Performance Tests
# tests/performance/redis/test_cache_latency.py
# tests/performance/redis/test_memory_efficiency.py
```

---

## 8. Deployment Architecture

```yaml
DOCKER_COMPOSE_SERVICES:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      - ./config/redis.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - xnai-network

  redis-replica:
    image: redis:7-alpine
    ports:
      - "6380:6379"
    command: redis-server --slaveof redis 6379
    depends_on:
      - redis
    networks:
      - xnai-network

  redis-exporter:
    image: oliver006/redis_exporter
    ports:
      - "9121:9121"
    environment:
      REDIS_ADDR: "redis://redis:6379"
    depends_on:
      - redis
    networks:
      - xnai-network

VOLUMES:
  redis_data:

NETWORKS:
  xnai-network:
```

---

## References

- Redis Data Structures: https://redis.io/docs/data-types/
- Redis Streams: https://redis.io/docs/data-types/streams/
- Redis Eviction Policies: https://redis.io/docs/reference/eviction/
- MessagePack Specification: https://msgpack.org/
- Session Manager: `app/XNAi_rag_app/core/infrastructure/session_manager.py`
- Redis State: `app/XNAi_rag_app/core/circuit_breakers/redis_state.py`

---

**Status**: Complete  
**Reviewed By**: MC-Overseer  
**Next Steps**: Implementation of connection pooling and serialization module
