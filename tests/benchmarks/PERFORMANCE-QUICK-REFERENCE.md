---
title: Database Performance Quick Reference
last_updated: 2026-02-25
---

# Database Performance Quick Reference Card

## Performance Targets (SLA)

### Response Time SLOs
```
Operation          P50       P95        P99        Success Rate
─────────────────────────────────────────────────────────────
Cache Read         <1ms      <2ms       <5ms       99.95%
Metadata Query     <10ms     <25ms      <50ms      99.9%
Full-Text Search   <50ms     <100ms     <200ms     99.9%
Vector Search      <100ms    <200ms     <400ms     99.5%
Write Operations   <25ms     <50ms      <100ms     99.9%
```

## PostgreSQL Quick Facts

| Metric | Value | Notes |
|--------|-------|-------|
| Connection time | 15ms p50 | Pre-warm pool at startup |
| Simple SELECT | 2-5ms | Indexed queries |
| INSERT latency | 3ms | Per row, batching 10x faster |
| FTS (1K docs) | 8-25ms | Requires GIN index |
| Max connections | 100-200 | Per instance |
| Throughput | 5-10K qps | Single instance |

**Best Practices:**
- ✅ Index on filter columns
- ✅ Use COPY for bulk inserts
- ✅ Monitor query plans
- ❌ N+1 queries
- ❌ Large result sets

## Redis Quick Facts

| Metric | Value | Notes |
|--------|-------|-------|
| GET latency | 0.3ms p50 | Cache hits |
| SET latency | 0.4ms p50 | Per operation |
| HGETALL (100 fields) | 1.2ms | Good for documents |
| Memory overhead | ~20% | Per cached document |
| Max memory | 256GB | Single instance |
| Throughput | 50K ops/s | Single threaded |

**Best Practices:**
- ✅ Use connection pooling
- ✅ Batch operations
- ✅ Set TTLs
- ✅ Monitor eviction
- ❌ Single connection
- ❌ Large values (>1MB)

## Qdrant Quick Facts

| Metric | Value | Notes |
|--------|-------|-------|
| Search (384-dim, 10K) | 8ms p50 | HNSW index |
| Search (768-dim, 100K) | 50ms p50 | Standard config |
| Search (1152-dim, 500K) | 250ms p50 | Larger vectors |
| Insert (batch 100) | 0.5-1.2ms/vec | Per vector |
| Index build (100K) | 25-55s | Scales O(n log n) |
| Memory per 1M vectors | 3.5-9.5GB | 384-1152 dims |
| Max vectors | ~100M | Per instance |

**Best Practices:**
- ✅ Use batch inserts
- ✅ Tune ef_search
- ✅ Enable quantization for large sets
- ✅ Monitor index size
- ❌ Single vector inserts
- ❌ Oversized vectors

## Scaling Guide

### When to Scale

**PostgreSQL** (add read replica when):
- Single instance doing >5K queries/sec
- Read latency increasing (>50ms p95)
- CPU >75% consistently

**Redis** (cluster when):
- Memory usage >80% consistently
- Eviction rate >1% of operations
- Single instance throughput >50K ops/sec

**Qdrant** (replicate when):
- Collection size >100M vectors
- Search latency degrading
- Need 99.99% availability

### Scaling Options

| Component | Scaling | Limit | Cost |
|-----------|---------|-------|------|
| PostgreSQL | Read replicas | ~50K qps | Linear |
| Redis | Clustering | ~500K ops/s | Linear |
| Qdrant | Replication | ~1B vectors | Linear |

## Monitoring Checklist

### Daily
- [ ] PostgreSQL cache hit ratio >90%
- [ ] Redis memory <80% of max
- [ ] Query latencies within SLA
- [ ] No cascading failures

### Weekly
- [ ] Database disk growth normal
- [ ] Index fragmentation <20%
- [ ] Replication lag <5s
- [ ] Backup completion success

### Monthly
- [ ] Run benchmarks, compare to baseline
- [ ] Review slow query logs
- [ ] Update statistics
- [ ] Test failover procedures

## Common Issues & Solutions

### PostgreSQL Slow
```sql
-- Check for missing indexes
SELECT schemaname, tablename, indexname 
FROM pg_stat_user_indexes 
WHERE idx_scan = 0;

-- Analyze query plan
EXPLAIN ANALYZE <query>;
```

### Redis Memory Full
```
Memory is filling up:
1. Check eviction rate: INFO stats
2. Review TTL settings
3. Enable quantization or compression
4. Add cluster nodes
```

### Qdrant Search Slow
```python
# Check collection stats
from qdrant_client import QdrantClient
client = QdrantClient("localhost", port=6333)
stats = client.get_collection("my_collection")
print(f"Vectors: {stats.vectors_count}")
print(f"Memory: {stats.memory_usage}")
```

## Configuration Templates

### PostgreSQL (8GB system)
```ini
shared_buffers = 2GB
effective_cache_size = 6GB
work_mem = 50MB
random_page_cost = 1.1
```

### Redis (512MB cache)
```
maxmemory 512mb
maxmemory-policy allkeys-lru
timeout 300
tcp-keepalive 60
```

### Qdrant (1GB limit)
```yaml
vectors:
  hnsw_config:
    ef_construct: 200
    ef_search: 100
    M: 16
```

## Alert Thresholds

```
ALERT: PostgreSQL_HighLatency
  IF: P99_latency > 200ms
  ACTION: Check query logs, add indexes

ALERT: Redis_MemoryHigh
  IF: used_memory > 90% of maxmemory
  ACTION: Review TTLs, enable eviction

ALERT: Qdrant_SearchSlow
  IF: search_latency_p95 > SLA_target
  ACTION: Check load, consider sharding
```

## Performance Math

### Query Latency Budget (100ms total)

```
Router Decision    →  1ms   (1%)
Query Execution   → 80ms  (80%)  ← Bottleneck
Result Formatting →  2ms   (2%)
Network RTT        → 17ms  (17%)
─────────────────────────────
TOTAL               100ms
```

### Throughput Calculations

```
PostgreSQL: 5000 qps / 100ms p99 = 500 concurrent users
Redis: 50000 ops/s / 1ms latency = 50 concurrent connections
Qdrant: 100 searches/s / 10ms latency = 1 active query
```

### Memory Calculation

```
PostgreSQL: 10K connections × 10MB = 100GB
Redis: 1M keys × 15KB per key = 15GB
Qdrant: 100M vectors × 7KB each = 700GB
```

## Tools & Commands

### PostgreSQL Diagnostics
```bash
# Top slow queries
SELECT mean_exec_time, query FROM pg_stat_statements 
ORDER BY mean_exec_time DESC LIMIT 10;

# Cache hit ratio
SELECT sum(heap_blks_read) as heap_read, 
       sum(heap_blks_hit) as heap_hit,
       sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
FROM pg_statio_user_tables;
```

### Redis Diagnostics
```bash
redis-cli INFO stats        # Get stats
redis-cli --bigkeys        # Find large keys
redis-cli --memkeys        # Memory usage by key
```

### Qdrant Diagnostics
```python
from qdrant_client import QdrantClient
client = QdrantClient("localhost")
client.get_collections()  # List collections
info = client.get_collection("coll_name")  # Stats
```

## Emergency Procedures

### PostgreSQL Connection Pool Exhausted
```
1. Check active connections: SELECT count(*) FROM pg_stat_activity;
2. Kill idle connections: SELECT pg_terminate_backend(pid) FROM ...;
3. Increase pool size or restart application
4. Review query timeouts
```

### Redis Out of Memory
```
1. Check memory: INFO memory
2. Enable eviction if not set
3. Review dataset size vs allocation
4. Scale horizontally (cluster)
5. Consider compression/quantization
```

### Qdrant Index Corruption
```
1. Check collection health: get_collection()
2. Rebuild index: recreate collection
3. Re-upload vectors from backup
4. Monitor for issues
5. Consider replication
```

## Contact & Escalation

- **Performance Issues**: Check dashboards, run diagnostics
- **Data Loss**: Stop writes, restore from backup
- **Availability**: Check service health, failover if needed
- **Capacity**: Scale horizontally or upgrade instance

---

**Print this card for quick reference!**  
Last Updated: 2026-02-25
