# Phase 3: FAISS to Qdrant Vector Database Migration

## Overview

This document describes the migration process from FAISS (in-memory vector index) to Qdrant (persistent vector database) for the XNAi Foundation Stack. The migration implements the **metadata-first strategy** with Redis-based state management and optimizations for the Ryzen 7 5700U.

## Architecture

### Components

1. **Qdrant Service**: Persistent vector database with on-disk storage and memory-mapped payloads
2. **Redis**: Transient source-of-truth for migration state tracking
3. **Migration Script** (`scripts/migrate_to_qdrant.py`): AnyIO-based orchestrator for bulk upsert

### Key Features

- **Metadata-First Strategy**: Payloads indexed immediately for fast metadata queries
- **Memory Optimization**: Monitors and enforces Ryzen 7 memory limits (6.6GB)
- **Batch Processing**: Configurable batch sizes (default: 500 vectors/batch)
- **State Recovery**: Resume interrupted migrations via Redis state
- **AnyIO Compatible**: Structured concurrency using AnyIO task groups
- **On-Disk Persistence**: Vectors stored on disk to minimize memory pressure

## Prerequisites

### Environment Variables

```bash
# Qdrant settings
QDRANT_URL=http://qdrant:6333
QDRANT_API_KEY=  # Optional

# Redis settings (for state management)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_password
REDIS_DB=0

# Migration settings
FAISS_INDEX_PATH=/app/data/faiss_index
VECTOR_SIZE=384
```

### Dependencies

The following packages must be installed:

```
qdrant-client >= 1.10.0
redis >= 7.1.0
faiss-cpu >= 1.13.0
anyio >= 4.12.0
psutil >= 5.10.0
tqdm >= 4.65.0
```

These are included in `requirements-api.in` and will be installed via:

```bash
pip install -r requirements-api.txt
```

## Running the Migration

### Start Docker Services

```bash
# Start Qdrant and Redis services
docker-compose up -d redis qdrant

# Wait for services to be healthy
docker-compose ps

# Verify services
curl http://localhost:6333/health
redis-cli -a $REDIS_PASSWORD ping
```

### Run Migration Script

```bash
# From the project root directory
python3 scripts/migrate_to_qdrant.py

# Or with custom configuration via environment
QDRANT_URL=http://localhost:6333 \
FAISS_INDEX_PATH=./data/faiss_index \
python3 scripts/migrate_to_qdrant.py
```

### Monitor Progress

The script outputs progress to:
- **Console**: Real-time progress bar with memory stats
- **Logs**: `logs/migration.log` with detailed information

Example output:

```
Migration Progress |████████████░░░░░░░░░░░░░░░░░░| 23/100
processed: 11500, failed: 0, memory_mb: 1024
```

## Migration State Management

### Redis State Structure

The migration state is stored in Redis under the key `xnai:migration:faiss_to_qdrant`:

```json
{
  "status": "in_progress|completed|failed",
  "started_at": "2026-02-15T19:11:16Z",
  "total_vectors": 50000,
  "processed_vectors": 23500,
  "failed_vectors": 0,
  "batches_processed": 47,
  "last_batch_id": 47,
  "last_checkpoint": "2026-02-15T19:15:30Z",
  "completed_at": "2026-02-15T19:30:00Z"
}
```

### Resume Capability

If migration is interrupted:

1. The Redis state persists across restarts
2. Re-running the migration script detects existing state
3. Migration resumes from last checkpoint
4. Set `RESUME_MODE=false` in environment to force from beginning

## Memory Optimization

### Ryzen 7 Constraints

The migration is optimized for systems with 6.6GB RAM:

- **Default memory limit**: 60% of available RAM (3.96GB)
- **Batch size**: 500 vectors (adjustable via `BATCH_SIZE` env var)
- **Memory monitoring**: Enforces limits and triggers cleanup

### Configuration

```bash
# Adjust memory limit percentage (default: 0.6)
MAX_MEMORY_PERCENT=0.5 python3 scripts/migrate_to_qdrant.py

# Smaller batches for constrained systems
BATCH_SIZE=250 python3 scripts/migrate_to_qdrant.py
```

## Qdrant Collection Configuration

### Vector Storage

- **On-Disk**: `true` (vectors stored on disk to minimize RAM)
- **Distance Metric**: COSINE (default, configurable)
- **Vector Size**: 384 dimensions (adjustable via `VECTOR_SIZE`)

### Payload Indexing

Metadata fields are automatically indexed for fast queries:

- `source`: KEYWORD (always "faiss" during migration)
- `faiss_id`: INTEGER (original FAISS vector ID)
- `migrated_at`: KEYWORD (ISO 8601 timestamp)
- `batch_num`: INTEGER (batch number for recovery)

### Configuration File

The Qdrant service reads configuration from `config/qdrant_config.yaml`:

```yaml
storage:
  storage_path: ./storage
  wal:
    enabled: true
    wal_capacity_mb: 200

payload_index_limit_mb: 512

performance:
  default_segment_number: 2
  max_batch_size: 100
  indexing_thread_count: 2
```

## Verification

### Check Migration Status

```bash
# View Redis state
redis-cli -a $REDIS_PASSWORD get xnai:migration:faiss_to_qdrant

# View Qdrant collection info
curl http://localhost:6333/collections/xnai_knowledge
```

### Validate Collection

```bash
# Count vectors in collection
curl http://localhost:6333/collections/xnai_knowledge/points/count

# Sample a point with metadata
curl http://localhost:6333/collections/xnai_knowledge/points/0
```

### Health Checks

```bash
# Qdrant health
curl http://localhost:6333/health

# Redis health
redis-cli -a $REDIS_PASSWORD ping

# Memory usage
docker stats xnai_qdrant xnai_redis
```

## Troubleshooting

### Connection Errors

```
Error: Failed to connect to Qdrant
```

**Solution**: Ensure Qdrant service is running and healthy:

```bash
docker-compose logs qdrant
docker-compose up -d qdrant
```

### Memory Exceeded

```
WARNING: Memory limit approaching: 3500MB / 3960MB
```

**Solution**: Reduce batch size and/or memory limit:

```bash
BATCH_SIZE=250 MAX_MEMORY_PERCENT=0.5 python3 scripts/migrate_to_qdrant.py
```

### Failed Upserts

```
ERROR: Failed to upsert batch: ...
```

**Solution**: Check logs for details and verify Qdrant connectivity:

```bash
tail -f logs/migration.log
docker-compose logs qdrant
```

## Performance Tuning

### Optimize for Speed

```bash
BATCH_SIZE=1000 python3 scripts/migrate_to_qdrant.py
```

### Optimize for Memory

```bash
BATCH_SIZE=250 MAX_MEMORY_PERCENT=0.4 python3 scripts/migrate_to_qdrant.py
```

### Parallel Processing

The script uses AnyIO task groups for structured concurrency. To adjust parallelism, modify the script's `CONCURRENCY_FACTOR` constant.

## Docker Compose Integration

### Start All Services

```bash
docker-compose up -d
```

### Verify Service Health

```bash
docker-compose ps

# Expected output:
# NAME                STATUS
# xnai_qdrant         Up (healthy)
# xnai_redis          Up (healthy)
# xnai_rag_api        Up (healthy)
```

### View Logs

```bash
# Qdrant logs
docker-compose logs -f qdrant

# All services
docker-compose logs -f
```

## Integration with RAG API

After successful migration, the RAG API can use Qdrant for vector searches:

```python
from qdrant_client.async_client import AsyncQdrantClient

client = AsyncQdrantClient(url=QDRANT_URL)
results = await client.search(
    collection_name="xnai_knowledge",
    query_vector=embedding,
    limit=10,
)
```

## Phase 3 Completion Checklist

- [ ] Qdrant service deployed and healthy
- [ ] Migration script configured with correct environment variables
- [ ] FAISS index loaded successfully
- [ ] Migration executed without errors
- [ ] All vectors upserted to Qdrant
- [ ] Metadata properly indexed
- [ ] Collection verified with sample queries
- [ ] Cleanup completed (FAISS index can be archived)

## References

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Qdrant Python Client](https://github.com/qdrant/qdrant-client)
- [AnyIO Documentation](https://anyio.readthedocs.io/)
- [XNAi Foundation Architecture](./README.md)
