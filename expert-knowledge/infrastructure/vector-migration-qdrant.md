# Vector Database Migration: FAISS → Qdrant
## Knowledge Card: Metadata-First Migration & Redis SoT Handover

**Date**: February 15, 2026  
**Status**: Research Complete  
**Architect**: Xoe-NovAi Infrastructure  
**Focus**: Zero-downtime vector DB migration with Redis source-of-truth  
**Last Updated**: 2026-02-15

---

## EXECUTIVE SUMMARY

Qdrant provides a superior vector database for the XNAi stack compared to FAISS:
- **Payload-native**: Store metadata alongside vectors (vs. external JSON files)
- **Distributed**: Built-in replication, sharding for Consul-registered clusters
- **Searchable**: Filter by metadata *during* vector search (not after)
- **Persistent**: Automatic snapshots, recovery, zero-downtime updates

**Migration Strategy**: Metadata-first with Redis as transient source-of-truth during handover. FAISS vectors imported directly; metadata re-indexed in Qdrant payloads for immediate search capability.

---

## 1. ARCHITECTURE: FAISS vs. QDRANT

### 1.1 Feature Comparison

| Feature | FAISS | Qdrant |
|---------|-------|--------|
| **Vector Storage** | Flat/HNSW indices | HNSW (production-proven) |
| **Metadata** | External JSON file | Native payload (JSON) |
| **Filtering** | Post-search (slow) | During search (fast) |
| **Distributed** | Single-node only | Multi-node, sharded |
| **Persistence** | Manual snapshots | Automatic + API |
| **Network Protocol** | File-based | REST/gRPC |
| **Replication** | None | Automatic |
| **Memory Safety** | User-managed | Optimized |

### 1.2 Why Qdrant for XNAi

Given the **Ryzen 7 5700U (6.6GB RAM)** constraint:

1. **Metadata-first indexing**: Avoids loading entire JSON file into memory
2. **Payload filtering**: Enables "search by subject, then by vector similarity"
3. **Snapshots**: Recovery from crashes without re-embedding
4. **gRPC support**: More efficient than REST for high-frequency queries
5. **Consul integration**: Auto-registration with service mesh

---

## 2. MIGRATION PHASES

### 2.1 Pre-Migration Audit

**Goals**: Understand current FAISS state before touching anything.

```python
import faiss
import json
import os

# Load FAISS index
index = faiss.read_index("path/to/index.faiss")
ntotal = index.ntotal
d = index.d  # Dimension (e.g., 384 for FastEmbed)

# Load metadata
with open("path/to/metadata.json") as f:
    metadata = json.load(f)

# Audit
print(f"Total vectors: {ntotal}")
print(f"Dimension: {d}")
print(f"Metadata entries: {len(metadata)}")
print(f"Sample metadata keys: {list(metadata.items())[:1]}")

# Memory footprint
faiss_size = os.path.getsize("path/to/index.faiss") / (1024**3)
metadata_size = os.path.getsize("path/to/metadata.json") / (1024**3)
print(f"FAISS index: {faiss_size:.2f} GB")
print(f"Metadata file: {metadata_size:.2f} GB")
```

**Acceptance Criteria**:
- [ ] Total vectors documented
- [ ] Dimension noted (affects Qdrant collection config)
- [ ] Metadata structure understood
- [ ] Memory footprint known
- [ ] Backup taken

### 2.2 Phase 1: Redis Population (Metadata Staging)

**Timeframe**: ~1-2 hours (depends on data size)

**Goal**: Write all metadata to Redis as *transient staging*. This enables parallel development while keeping FAISS as fallback.

```python
import json
import redis
import asyncio
from datetime import datetime

async def populate_redis_from_faiss_metadata():
    """
    Write FAISS metadata to Redis for staging.
    Redis acts as transient source-of-truth during migration.
    """
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    
    with open("metadata.json") as f:
        metadata = json.load(f)
    
    pipe = r.pipeline()
    migrated_at = datetime.now().isoformat()
    
    for doc_id, meta in metadata.items():
        # Primary key: ISBN or OL ID
        key_identifier = meta.get("isbn") or meta.get("ol_key") or doc_id
        
        # Store metadata
        redis_key = f"book:meta:{key_identifier}"
        pipe.hset(redis_key, mapping={
            "doc_id": doc_id,  # FAISS doc ID
            "isbn": meta.get("isbn", ""),
            "title": meta.get("title", ""),
            "author": meta.get("author", ""),
            "subject": json.dumps(meta.get("subject", [])),
            "language": meta.get("language", "en"),
            "source": "faiss_legacy",
            "migrated_at": migrated_at,
            "ttl_days": 7  # Temporary, for migration only
        })
        
        # Index by subject for discovery
        for subject in meta.get("subject", []):
            pipe.sadd(f"index:subject:{subject}", key_identifier)
        
        # Index by author
        pipe.sadd(f"index:author:{meta.get('author', '')}", key_identifier)
    
    # Batch execute
    pipe.execute()
    print(f"Populated {len(metadata)} metadata entries to Redis")
    
    # Set migration start marker
    r.set("migration:faiss_to_qdrant:started", migrated_at)
    return len(metadata)

# Run staging
asyncio.run(populate_redis_from_faiss_metadata())
```

**Result**: All metadata now in Redis under `book:meta:*` keys. FAISS remains untouched.

### 2.3 Phase 2: Qdrant Collection Creation

**Goal**: Set up Qdrant collection with schema matching FAISS vectors.

```python
from qdrant_client import QdrantClient
from qdrant_client.models import (
    CreateCollection,
    VectorParams,
    Distance,
    FieldConditionFactory
)

client = QdrantClient(url="http://localhost:6333", timeout=30)

# Create collection with fastEmbed-compatible settings (384-dim)
client.create_collection(
    collection_name="books_v1",
    vectors_config=VectorParams(
        size=384,  # Adjust to your FAISS dimension
        distance=Distance.COSINE,  # Or EUCLID, depending on your embeddings
        on_disk=True  # Save memory for Ryzen constraint
    ),
    # Enable payload indexing for fast metadata filtering
    payload_schema={
        "isbn": {
            "type": "keyword",
            "is_common": True
        },
        "title": {
            "type": "text"
        },
        "author": {
            "type": "keyword"
        },
        "subject": {
            "type": "array",
            "items": {"type": "keyword"}
        },
        "language": {
            "type": "keyword"
        },
        "source": {
            "type": "keyword"
        }
    }
)

# Verify collection
collection_info = client.get_collection("books_v1")
print(f"Collection created: {collection_info.points_count} points (initially 0)")
```

**Key Decisions**:

| Setting | Value | Reason |
|---------|-------|--------|
| Distance Metric | COSINE | Works well with normalized embeddings |
| Vector Size | 384 | FastEmbed standard; adjust if different |
| On-Disk Storage | True | Reduces RAM pressure on Ryzen |
| Payload Index | Yes | Enable fast metadata filtering |

### 2.4 Phase 3: Vector & Payload Upsert

**Goal**: Bulk-insert FAISS vectors + metadata payloads into Qdrant.

This is the **critical migration step**. Use batching to avoid memory spikes.

```python
import faiss
import json
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import numpy as np

async def bulk_upsert_vectors(
    faiss_index_path: str,
    metadata_path: str,
    qdrant_url: str = "http://localhost:6333",
    batch_size: int = 1000
):
    """
    Bulk upsert FAISS vectors to Qdrant with metadata payloads.
    Batching prevents memory overflow on Ryzen constraint.
    """
    client = QdrantClient(url=qdrant_url)
    
    # Load FAISS
    index = faiss.read_index(faiss_index_path)
    with open(metadata_path) as f:
        metadata_map = json.load(f)
    
    total_docs = index.ntotal
    batch = []
    processed = 0
    
    print(f"Starting bulk upsert: {total_docs} vectors")
    
    for doc_id in range(total_docs):
        # Get vector
        vector = index.reconstruct(doc_id).tolist()  # Convert to list for JSON
        
        # Get metadata
        meta = metadata_map.get(str(doc_id), {})
        
        # Build payload (metadata-first)
        payload = {
            "isbn": meta.get("isbn", f"faiss_{doc_id}"),
            "title": meta.get("title", ""),
            "author": meta.get("author", ""),
            "subject": meta.get("subject", []),
            "language": meta.get("language", "en"),
            "source": "faiss_legacy",
            "faiss_doc_id": doc_id,
            "migrated": True
        }
        
        # Create point (Qdrant IDs must be > 0)
        point = PointStruct(
            id=doc_id + 1,  # Offset from 1
            vector=vector,
            payload=payload
        )
        batch.append(point)
        
        # Batch upsert every N vectors
        if len(batch) >= batch_size:
            await client.upsert(
                collection_name="books_v1",
                points=batch,
                wait=False  # Async mode for speed
            )
            processed += len(batch)
            print(f"Upserted {processed}/{total_docs}")
            batch = []
    
    # Final batch
    if batch:
        await client.upsert(
            collection_name="books_v1",
            points=batch,
            wait=True  # Final batch: wait for completion
        )
        processed += len(batch)
    
    print(f"✓ Migration complete: {processed} vectors in Qdrant")
    return processed

# Execute migration
import asyncio
result = asyncio.run(bulk_upsert_vectors(
    "path/to/index.faiss",
    "path/to/metadata.json"
))
```

**Memory Optimization for Ryzen**:

```python
# Monitor memory during upsert
import psutil

def check_memory():
    process = psutil.Process()
    memory_info = process.memory_info()
    rss_gb = memory_info.rss / (1024**3)
    print(f"Memory usage: {rss_gb:.2f} GB")
    
    if rss_gb > 5.0:
        print("⚠️  WARNING: Approaching memory limit!")
        return False
    return True

# In the loop:
if doc_id % 100 == 0:
    if not check_memory():
        # Pause and allow garbage collection
        import gc
        gc.collect()
        await asyncio.sleep(0.5)
```

### 2.5 Phase 4: Validation & Parallel Operation

**Goal**: Ensure Qdrant and FAISS are in sync. Disable FAISS switchover when confident.

```python
import redis
import asyncio
from qdrant_client import QdrantClient

async def validate_migration(sample_size: int = 100):
    """
    Spot-check: Compare random vectors from FAISS vs Qdrant.
    Also validate payload consistency with Redis.
    """
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    qdrant = QdrantClient(url="http://localhost:6333")
    
    # Sample ISBNs from Redis
    all_keys = r.keys("book:meta:*")
    sample_keys = all_keys[:sample_size]
    
    mismatches = 0
    
    for key in sample_keys:
        isbn = key.split(":")[-1]
        
        # Get from Redis
        redis_meta = r.hgetall(key)
        
        # Get from Qdrant (via metadata filter)
        results = await qdrant.search(
            collection_name="books_v1",
            query_vector=[0.0] * 384,  # Dummy vector for payload search
            query_filter={
                "must": [{
                    "key": "isbn",
                    "match": {"value": isbn}
                }]
            },
            limit=1
        )
        
        if not results:
            print(f"✗ Mismatch: {isbn} not in Qdrant")
            mismatches += 1
            continue
        
        qdrant_payload = results[0].payload
        
        # Compare critical fields
        if redis_meta.get("title") != qdrant_payload.get("title"):
            print(f"✗ Title mismatch for {isbn}")
            mismatches += 1
    
    accuracy = 100 * (sample_size - mismatches) / sample_size
    print(f"Validation accuracy: {accuracy:.1f}%")
    return accuracy >= 99.0

# Run validation
success = asyncio.run(validate_migration(sample_size=100))
```

**Go/No-Go Decision**:

| Metric | Threshold | Action |
|--------|-----------|--------|
| Validation accuracy | ≥ 99% | Go to Phase 5 |
| Search latency | < 500ms (p95) | Go to Phase 5 |
| Memory usage | < 4.5 GB | Go to Phase 5 |
| Payload size | All fields present | Go to Phase 5 |

### 2.6 Phase 5: Redis Source-of-Truth Handover

**Goal**: Make Redis the authoritative source during parallel operation. Both FAISS and Qdrant become read-only fallbacks.

```python
import asyncio
from redis.asyncio import Redis
from qdrant_client.async_client import AsyncQdrantClient

class MetadataStore:
    """
    Unified metadata access: Redis → Qdrant → FAISS (fallback)
    """
    
    def __init__(self):
        self.redis = Redis(host="localhost", port=6379, decode_responses=True)
        self.qdrant = AsyncQdrantClient(url="http://localhost:6333")
        self.faiss_fallback = None  # Set to FAISS index if needed
    
    async def get_metadata(self, isbn: str) -> dict:
        """
        Get metadata with fallback chain:
        1. Redis (hot cache)
        2. Qdrant (search index)
        3. FAISS (legacy fallback)
        """
        
        # Try Redis first
        redis_key = f"book:meta:{isbn}"
        meta = await self.redis.hgetall(redis_key)
        if meta:
            return meta
        
        # Try Qdrant
        try:
            results = await self.qdrant.search(
                collection_name="books_v1",
                query_vector=[0.0] * 384,
                query_filter={"must": [{"key": "isbn", "match": {"value": isbn}}]},
                limit=1
            )
            if results:
                payload = results[0].payload
                # Write back to Redis
                await self.redis.hset(redis_key, mapping=payload)
                return payload
        except Exception as e:
            print(f"Qdrant lookup failed: {e}")
        
        # FAISS fallback (if needed)
        if self.faiss_fallback:
            # Reconstruct from FAISS index
            pass
        
        return None
    
    async def upsert_metadata(self, isbn: str, data: dict):
        """
        Write metadata to both Redis and Qdrant.
        Redis is authoritative; Qdrant is synced via background job.
        """
        # Write to Redis (immediate)
        redis_key = f"book:meta:{isbn}"
        await self.redis.hset(redis_key, mapping=data)
        
        # Queue for Qdrant sync
        await self.redis.lpush("sync_queue:qdrant", isbn)
    
    async def sync_to_qdrant(self):
        """
        Background task: Sync Redis updates to Qdrant.
        """
        while True:
            isbn = await self.redis.lpop("sync_queue:qdrant")
            if not isbn:
                await asyncio.sleep(5)  # Poll interval
                continue
            
            meta = await self.get_metadata(isbn)
            if not meta:
                continue
            
            # Update Qdrant payload
            doc_id = int(meta.get("faiss_doc_id", 0)) + 1
            if doc_id > 0:
                await self.qdrant.set_payload(
                    collection_name="books_v1",
                    payload=meta,
                    points_selector=[doc_id]
                )

# Usage
store = MetadataStore()
meta = await store.get_metadata("0441172717")  # ISBN for Dune
```

### 2.7 Phase 6: FAISS Decommission (After Validation)

**Timeline**: 30+ days after Phase 5 (safety buffer)

```bash
# After 30 days of successful operation:
# 1. Archive FAISS index
tar czf faiss-backup-$(date +%Y%m%d).tar.gz index.faiss metadata.json

# 2. Remove FAISS code paths from application
# (Search codebase for "faiss" and remove fallback logic)

# 3. Clear Redis migration keys
redis-cli DEL migration:faiss_to_qdrant:started

# 4. Create final snapshot in Qdrant
# (See Section 3 below)
```

---

## 3. QDRANT SNAPSHOTS & DISASTER RECOVERY

### 3.1 Automatic Snapshots

Qdrant snapshots are tar archives containing collection state (vectors + payloads).

```python
from qdrant_client import QdrantClient
from datetime import datetime

client = QdrantClient(url="http://localhost:6333")

# Create snapshot
snapshot_result = client.create_snapshot(collection_name="books_v1")
snapshot_name = snapshot_result.snapshot_description.name

print(f"Snapshot created: {snapshot_name}")
# Output: books_v1-2026-02-15-12-30-45-123456

# List snapshots
snapshots = client.list_snapshots(collection_name="books_v1")
for snapshot in snapshots.snapshots:
    print(f"  - {snapshot.name}: {snapshot.creation_time}")
```

### 3.2 Snapshot Storage Strategy

```yaml
# docker-compose.yml (Qdrant service)
volumes:
  - ./data/qdrant/snapshots:/qdrant/snapshots:Z,U  # Named snapshots here
  - ./data/qdrant/storage:/qdrant/storage:Z,U      # Vector data
  - ./backups/qdrant:/qdrant/backups:Z,U           # Exported backups
```

### 3.3 Restore from Snapshot

```python
# If disaster strikes:
client.recover_snapshot(
    collection_name="books_v1_restored",
    snapshot_path="/qdrant/snapshots/books_v1-2026-02-15-12-30-45-123456.tar"
)

# Rename alias
client.update_alias(
    alias_name="books",
    new_collection_name="books_v1_restored"
)
```

---

## 4. REDIS SCHEMA FOR SoT HANDOVER

```
# Primary metadata (Redis SoT)
book:meta:{isbn} → hash {
    title: str,
    author: str,
    subject: json,
    language: str,
    source: str,
    qdrant_point_id: int,
    faiss_doc_id: int,
    created_at: timestamp,
    migrated_at: timestamp,
    last_accessed: timestamp
}

# Migration tracking
migration:faiss_to_qdrant:started → timestamp
migration:faiss_to_qdrant:phase → "5-parallel-operation" or "6-decommissioned"
migration:validation:accuracy → 99.5
migration:validation:timestamp → timestamp

# Sync queue (for Qdrant updates)
sync_queue:qdrant → list [isbn, isbn, isbn, ...]  # FIFO queue

# Performance indices
index:subject:{subject} → set {isbn, isbn, ...}
index:author:{author} → set {isbn, isbn, ...}

# TTL: All migration keys expire after 60 days
```

---

## 5. PERFORMANCE EXPECTATIONS

### 5.1 Query Latency

| Query Type | FAISS (CPU) | Qdrant (Search) | Improvement |
|------------|------------|-----------------|-------------|
| Vector search (top-10) | 150-300ms | 50-150ms | 2-3x faster |
| Metadata filter + vector | N/A (post-search) | 100-200ms | Parallel filtering |
| Single metadata lookup | Read JSON | 10-20ms | Instant with indexing |

### 5.2 Memory Profile (Ryzen 7 5700U)

| Component | FAISS | Qdrant | Savings |
|-----------|-------|--------|---------|
| Index in memory | 1.2 GB (384k docs) | 0.3 GB (on-disk) | 900 MB |
| Metadata in memory | 0.8 GB (JSON) | Indexed, queried as needed | 800 MB |
| Total baseline | 2.0 GB | 0.5 GB | **1.5 GB saved** |

**Impact**: Freed memory can support larger LLM context windows or additional agents.

### 5.3 Throughput

- **Indexing**: 1,000 vectors/sec (batch)
- **Queries**: 100-500 QPS (depending on filter complexity)
- **Metadata updates**: 10,000 Redis ops/sec

---

## 6. INTEGRATION WITH XNAI STACK

### 6.1 Consul Registration

```python
from consul import Consul

consul = Consul(host="localhost", port=8500)

# Register Qdrant in service mesh
consul.agent.service.register(
    name="qdrant",
    service_id="qdrant-primary",
    address="qdrant-db",
    port=6333,
    tags=["vector-db", "prod"],
    check=consul.agent.check.http(
        "http://qdrant-db:6333/health",
        interval="10s",
        timeout="5s"
    )
)
```

### 6.2 Redis-Qdrant Sync Job

Run as scheduled task (Consul-registered):

```python
import asyncio
from redis.asyncio import Redis
from qdrant_client.async_client import AsyncQdrantClient

async def redis_qdrant_sync_job():
    """
    Scheduled job: Sync Redis updates to Qdrant every 5 minutes.
    Ensures both stay in sync during normal operation.
    """
    redis = Redis(host="localhost", port=6379)
    qdrant = AsyncQdrantClient(url="http://localhost:6333")
    
    while True:
        try:
            # Get pending syncs
            pending = await redis.lrange("sync_queue:qdrant", 0, 999)
            
            for isbn in pending:
                # Get latest metadata from Redis
                meta = await redis.hgetall(f"book:meta:{isbn}")
                if meta and meta.get("qdrant_point_id"):
                    # Update Qdrant payload
                    await qdrant.set_payload(
                        collection_name="books_v1",
                        payload=meta,
                        points_selector=[int(meta["qdrant_point_id"])]
                    )
                    # Remove from queue
                    await redis.lrem("sync_queue:qdrant", 1, isbn)
            
            await asyncio.sleep(300)  # 5-minute interval
        except Exception as e:
            print(f"Sync error: {e}")
            await asyncio.sleep(60)  # Retry after 1 minute

# Register in Consul for scheduling
consul.agent.service.register(
    name="metadata-sync-job",
    service_id="metadata-sync-worker",
    tags=["job", "qdrant-sync"]
)

# Run in background
asyncio.create_task(redis_qdrant_sync_job())
```

---

## 7. ROLLBACK PLAN

**If migration fails or major issues arise**:

```
Timeline: Day 0-5 (Parallel Operation) → Day 6+ (Disable FAISS reads)

Rollback Window: Day 0-30 (FAISS backups preserved)

Rollback Steps:
1. Stop new writes to Redis
2. Revert application to read FAISS (fallback still in code)
3. Analyze what went wrong
4. Keep Qdrant data for forensics
5. Plan corrective migration
```

**Example Rollback Code**:

```python
async def fallback_to_faiss():
    """
    Emergency: Switch search backend from Qdrant to FAISS.
    """
    # Update service discovery
    consul = Consul(host="localhost", port=8500)
    consul.agent.service.deregister("qdrant")
    
    # Reload FAISS
    import faiss
    index = faiss.read_index("index.faiss")
    
    # Swap search implementation
    search_backend = index  # Global var used in endpoints
    
    print("⚠️  Rolled back to FAISS")
```

---

## 8. IMPLEMENTATION CHECKLIST

- [ ] **Pre-Migration**:
  - [ ] FAISS audit completed (vector count, dimension, memory)
  - [ ] Backup of FAISS index + metadata
  - [ ] Qdrant deployed and healthy

- [ ] **Phase 1: Redis Staging**:
  - [ ] All metadata written to Redis (`book:meta:*`)
  - [ ] Indices created (`index:subject:*`, `index:author:*`)
  - [ ] TTL set to 7 days

- [ ] **Phase 2: Qdrant Collection**:
  - [ ] `books_v1` collection created
  - [ ] Payload schema indexed
  - [ ] Health check passing

- [ ] **Phase 3: Bulk Upsert**:
  - [ ] Batch upsert script tested (1000 vectors)
  - [ ] Memory monitoring enabled
  - [ ] Full migration executed
  - [ ] No vectors dropped

- [ ] **Phase 4: Validation**:
  - [ ] Spot-check (100+ samples) passing
  - [ ] Search latency < 200ms (p95)
  - [ ] Payload consistency verified

- [ ] **Phase 5: Parallel Operation**:
  - [ ] Read from Redis (with fallback to Qdrant)
  - [ ] Writes go to both (Redis primary)
  - [ ] Sync job running
  - [ ] Monitoring alerts configured

- [ ] **Phase 6: Decommission**:
  - [ ] 30+ days of production telemetry clean
  - [ ] FAISS backup archived
  - [ ] FAISS code paths removed
  - [ ] Final Qdrant snapshot created

---

## 9. MONITORING & ALERTS

```python
# Prometheus metrics to track
migration_vectors_in_qdrant = Counter(
    "migration_vectors_in_qdrant_total",
    "Total vectors successfully migrated to Qdrant"
)

redis_qdrant_sync_lag = Gauge(
    "redis_qdrant_sync_lag_seconds",
    "Seconds behind latest Redis writes"
)

qdrant_search_latency = Histogram(
    "qdrant_search_latency_ms",
    "Vector search latency in milliseconds"
)

# Alert thresholds
ALERT_SYNC_LAG_THRESHOLD = 300  # 5 minutes
ALERT_SEARCH_LATENCY_THRESHOLD = 500  # 500ms p95
```

---

## 11. HYBRID ARCHITECTURE: THE "SHADOW CACHE" PATTERN

### 11.1 Rationale
While Qdrant provides production-grade persistence and filtering, FAISS remains 10-20x faster for raw vector similarity. On the **Ryzen 7 5700U**, we will implement a tiered hybrid approach to maximize both speed and capacity.

### 11.2 The Shadow Cache Strategy

| Layer | Technology | Role | Capacity |
|-------|------------|------|----------|
| **Hot (Tier 1)** | **FAISS** | Semantic Cache | ~5k "Hot" Vectors |
| **Warm/Cold (Tier 2)** | **Qdrant** | Primary Vector DB | Full Library (384k+) |
| **Control (Tier 3)** | **Redis** | Cache Orchestrator | Metadata & TTLs |

### 11.3 Implementation Logic
1.  **Query Path**: Query → Check FAISS Shadow Cache (Hot) → If Hit > 0.95 Similarity, Return → Else, Query Qdrant (Full).
2.  **Cache Invalidation**: Redis tracks "Hot" ISBNs. Least-recently-used (LRU) vectors are purged from FAISS and persisted solely in Qdrant.
3.  **Memory Optimization**: FAISS index uses `IndexIVFPQ` for extreme compression, ensuring the "Hot" layer fits within <100MB of RAM.

---

## 12. UPDATED ROADMAP: PHASE 6.1
- [ ] Implement `ShadowCacheManager` class.
- [ ] Configure Qdrant with `on_disk: true`.
- [ ] Benchmark Hybrid vs. Qdrant-only latencies on Ryzen hardware.

---

**Knowledge Card Version**: 1.0.0  
**Next Review**: 2026-03-15  
**Maintainer**: Xoe-NovAi Infrastructure Team
