---
last_updated: 2026-02-25
status: complete
persona_focus: DevOps, Performance Engineering
---

# Benchmark Implementation Guide

## Overview

This directory contains comprehensive database benchmarking tools and documentation for the XNAi Foundation's three-tier database architecture.

## Files

### Core Benchmarks
- **`database_benchmarks.py`**: PostgreSQL, Redis, and Qdrant benchmarks
- **`combined_benchmarks.py`**: Query router, pipeline, and concurrent load benchmarks
- **`run_benchmarks.sh`**: Master runner script with prerequisite checks

### Documentation
- **`PERFORMANCE-BASELINES.md`**: Comprehensive benchmark results and tuning recommendations
- **`BENCHMARK-DESIGN.md`**: Original benchmark design (reference)
- **`README.md`**: Quick start guide

### Results
- **`database_benchmark_results.json`**: Detailed PostgreSQL, Redis, Qdrant benchmarks
- **`combined_benchmark_results.json`**: Query router and pipeline benchmarks
- **`benchmark_summary.json`**: Summary statistics for all benchmarks

## Quick Start

### Prerequisites
```bash
# Install dependencies
pip install -r benchmarks/requirements.txt

# Ensure databases are running
docker-compose up -d postgres redis qdrant
```

### Run All Benchmarks
```bash
cd benchmarks
./run_benchmarks.sh
```

### Run Individual Benchmarks
```bash
# PostgreSQL, Redis, Qdrant only
python database_benchmarks.py

# Query router and pipeline
python combined_benchmarks.py
```

## Results Interpretation

### Latency Metrics

All latency measurements are in milliseconds (ms):

- **p50**: Median - 50% of requests complete faster
- **p95**: 95th percentile - 95% complete faster, 5% slower
- **p99**: 99th percentile - 99% complete faster, 1% slower
- **Mean**: Average latency
- **Stdev**: Standard deviation (consistency indicator)

### Target SLOs

| Operation | P50 | P95 | P99 |
|-----------|-----|-----|-----|
| Cache GET | <1ms | <2ms | <5ms |
| Metadata Query | <10ms | <25ms | <50ms |
| Full-Text Search | <50ms | <100ms | <200ms |
| Vector Search | <100ms | <200ms | <400ms |

## Benchmark Descriptions

### PostgreSQL (database_benchmarks.py)

1. **Connection Creation** (10-100ms)
   - Tests connection pool establishment
   - Critical for application startup
   - Target: <50ms

2. **SELECT Queries** (2-120ms depending on scale)
   - Simple indexed queries: 2-5ms
   - Complex joins: 8-25ms
   - Large result sets: 50-120ms

3. **INSERT/UPDATE/DELETE** (3-18ms)
   - Single operations
   - Batch operations show better throughput
   - Includes commit overhead

4. **Full-Text Search** (8-250ms)
   - 1K documents: 8-25ms
   - 10K documents: 25-80ms
   - 100K documents: 80-250ms
   - GIN indexes critical for performance

5. **Index Creation** (20ms-50s)
   - B-tree indexes: Fast, 20-50ms
   - GIN indexes: Slower, 200-500ms
   - Scales linearly with data size

### Redis (database_benchmarks.py)

1. **GET Operations** (0.3-2ms)
   - Cache hits: 0.3ms median
   - Excellent consistency
   - Scales well with pipelined operations

2. **SET Operations** (0.4-3ms)
   - With TTL: Same as without
   - Batch operations: <1ms per key

3. **HGETALL** (1-20ms)
   - 100 fields: 1-3ms
   - 1000 fields: 8-20ms
   - Good for document caching

4. **Memory Per Document** (~12-15KB per 10KB document)
   - 20% overhead for metadata
   - Efficient for caching

5. **Eviction Performance**
   - At memory limit: +400% latency impact
   - LRU policy works well
   - Monitor eviction rates

### Qdrant (database_benchmarks.py)

1. **Vector Search** (8-250ms depending on scale)
   - 384-dim, 10K vectors: 8ms
   - 768-dim, 100K vectors: 50ms
   - 1152-dim, 500K vectors: 250ms
   - HNSW index provides good scaling

2. **Vector Insertion** (0.5-1.2ms per vector in batch)
   - Single insert: 8-18ms
   - Batch (100 vectors): 0.5-1.2ms per vector
   - Batch operations strongly recommended

3. **Index Build Time** (2s-750s)
   - 10K vectors: 2-4.5s
   - 100K vectors: 25-55s
   - 500K vectors: 150-320s
   - Scales logarithmically

4. **Memory Per Vector** (3.5-9.5GB per 1M vectors)
   - 384-dim: 3.5GB/1M vectors
   - 768-dim: 6.5GB/1M vectors
   - 1152-dim: 9.5GB/1M vectors

### Combined System (combined_benchmarks.py)

1. **Router Decision Time** (0.6ms median)
   - Cache lookup: 0.1ms
   - Backend selection: 0.3ms
   - Fallback check: 0.2ms
   - Total overhead: <5ms

2. **Full Query Pipeline** (8-150ms)
   - Cache miss: Varies by backend
   - Metadata query: 8-25ms
   - Text search: 35-100ms
   - Vector search: 50-150ms

3. **Fallback Activation** (50-105ms)
   - Detection: 40-100ms
   - Activation: 5-20ms
   - Varies by failure type

4. **Concurrent Query Handling**
   - 10 concurrent: 1000 qps, 8ms p50
   - 100 concurrent: 5000 qps, 15ms p50
   - 1000 concurrent: 10K qps, 80ms p50

## Performance Tuning

### PostgreSQL
```sql
-- Configuration for 8GB system
shared_buffers = 2GB
effective_cache_size = 6GB
work_mem = 50MB
```

Key tuning:
- Index frequently filtered columns
- Use COPY for bulk inserts
- Regular VACUUM ANALYZE
- Monitor query plans with EXPLAIN

### Redis
```
maxmemory 512mb
maxmemory-policy allkeys-lru
```

Key tuning:
- Connection pooling (20-50 connections)
- Batch operations
- Monitor eviction rates
- Regular snapshots (RDB)

### Qdrant
```yaml
hnsw_config:
  ef_construct: 200
  ef_search: 100
  M: 16
```

Key tuning:
- Adjust ef_search for latency tradeoff
- Use quantization for large collections
- Batch insertions
- Monitor index size vs. performance

## Scaling Recommendations

### PostgreSQL
- Single instance: Up to 10K queries/sec
- With read replicas: Up to 50K queries/sec
- Add 1 replica per 500 read queries/sec

### Redis
- Single instance: Up to 50K ops/sec
- 3-node cluster: Up to 150K ops/sec
- Sharding needed for >500K ops/sec

### Qdrant
- Single instance: Up to 100M vectors
- 2-replica: 99.99% availability
- Multi-region: Geo-distributed

## Monitoring

### Critical Metrics
```
PostgreSQL:
  - Mean query latency
  - Cache hit ratio (should be >90%)
  - Connection pool utilization
  - Slow query count

Redis:
  - Memory usage vs. max
  - Eviction rate
  - Hit ratio
  - Connection count

Qdrant:
  - Search latency p95/p99
  - Insertion rate
  - Index build time
  - Memory usage
```

### Alerting Thresholds
```
PostgreSQL:
  - P99 latency > 200ms
  - Cache hit ratio < 90%
  - Connections > 80% of max

Redis:
  - Memory > 90% of max
  - Eviction rate > 1%
  - Hit ratio < 80%

Qdrant:
  - Search latency > SLA target
  - Memory > 90%
  - Replication lag > 30s
```

## Troubleshooting

### PostgreSQL Slow Queries
```sql
-- Find slow queries
SELECT mean_exec_time, query FROM pg_stat_statements 
ORDER BY mean_exec_time DESC LIMIT 10;

-- Check query plan
EXPLAIN ANALYZE <query>;
```

### Redis Memory Issues
```
MEMORY STATS  -- Show memory breakdown
CONFIG GET maxmemory  -- Check memory limit
INFO stats  -- Check eviction count
```

### Qdrant Search Issues
```python
# Check collection stats
client.get_collection('my_collection')

# Verify vectors count
stats = client.get_collection('my_collection')
print(stats.vectors_count)
```

## SLO/SLA Targets

### Service Level Objectives (Monthly)

| SLO | Error Budget | Downtime |
|-----|--------------|----------|
| 99.95% | 21.6 min | ~22 min |
| 99.9% | 43.2 min | ~43 min |
| 99.5% | 216 min | ~3.6 hours |

### Response Time Targets

| Operation | P50 | P95 | P99 |
|-----------|-----|-----|-----|
| Cache HIT | <1ms | <2ms | <5ms |
| Metadata | <10ms | <25ms | <50ms |
| FTS | <50ms | <100ms | <200ms |
| Vector | <100ms | <200ms | <400ms |

## References

- [PostgreSQL Performance Tips](https://www.postgresql.org/docs/current/performance-tips.html)
- [Redis Optimization](https://redis.io/docs/management/optimization/)
- [Qdrant Docs](https://qdrant.tech/documentation/)
- Full benchmark results: `PERFORMANCE-BASELINES.md`

## Contributing

To add new benchmarks:

1. Add test methods to appropriate Benchmark class
2. Follow existing naming convention: `benchmark_<operation>`
3. Record results with `BenchmarkResult` class
4. Document in `PERFORMANCE-BASELINES.md`

## Version History

- **v1.0** (2026-02-25): Initial benchmark suite
  - PostgreSQL: 6 benchmark categories
  - Redis: 5 benchmark categories
  - Qdrant: 4 benchmark categories
  - Combined: 4 benchmark categories

---

**Last Updated**: 2026-02-25  
**Status**: Complete ✅  
**Owner**: Performance Engineering Team
