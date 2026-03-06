# Qdrant Collections - Quick Start Guide

**Task**: 1-3-qdrant-collections  
**Status**: ✅ COMPLETE  
**Version**: 1.0.0  
**Last Updated**: 2026-02-25

---

## 📋 What Was Created

This task completed the design phase for 3 optimized Qdrant vector collections:

### Collections

1. **xnai_core** (384-dim FastEmbed)
   - General semantic search
   - Balanced performance
   - Target: <50ms search latency
   - Capacity: 500K+ vectors

2. **xnai_linguistic** (768-dim Ancient-Greek-BERT)
   - Specialized linguistic search
   - Memory-optimized with quantization
   - Target: ~60ms search latency
   - Capacity: 500K+ vectors

3. **xnai_hybrid** (1152-dim concatenated)
   - Multi-model ensemble
   - Highest accuracy
   - Target: ~70ms search latency
   - Capacity: 500K+ vectors

---

## 📁 Files Created

### Configuration
- **`configs/qdrant_collections.yaml`** (14 KB)
  - Complete YAML definition of all 3 collections
  - HNSW index parameters
  - Payload schemas with indexed fields
  - Query strategy definitions
  - Performance benchmarks

### Scripts
- **`scripts/initialize_qdrant_collections.py`** (19 KB, executable)
  - Create collections from YAML
  - Set up payload indexes
  - Verify collection health
  - Generate status report

### Documentation
- **`docs/01-infrastructure/qdrant-query-strategy.md`** (17 KB)
  - 5 query strategies with examples
  - HNSW parameter tuning guide
  - Filtering best practices
  - Performance optimization tips
  - Monitoring and troubleshooting

- **`internal_docs/qdrant-collections-design.md`** (11 KB)
  - Design summary
  - Technical specifications
  - Memory estimates
  - Implementation roadmap
  - Testing recommendations

---

## 🚀 Quick Start

### 1. Review Configuration

```bash
cat configs/qdrant_collections.yaml
```

### 2. Deploy Collections

```bash
# Set environment variables (optional)
export QDRANT_URL="http://localhost:6333"
export QDRANT_API_KEY=""

# Run initialization script
python3 scripts/initialize_qdrant_collections.py
```

### 3. Verify Collections

```bash
# The script will output status:
# ✅ Collection 'xnai_core' verified:
#   - Vector count: 0
#   - Points: 0
#   - Status: green
# (and similar for other collections)
```

---

## 📊 Collection Specifications

### xnai_core
```
Vector Size: 384 (all-MiniLM-L6-v2)
Distance: Cosine similarity
HNSW M: 16, ef_construct: 200, ef: 100
Payload Fields: 8 (chunk_id, doc_id, domain, source, chunk_num, created_at, token_count, embedding_model)
Quantization: None (full precision)
Est. Size: ~2.9 GB @ 500K vectors
```

### xnai_linguistic
```
Vector Size: 768 (Ancient-Greek-BERT)
Distance: Cosine similarity
HNSW M: 12, ef_construct: 150, ef: 100
Payload Fields: 9 (+ language_code)
Quantization: Scalar (99th percentile, -50% memory)
Est. Size: ~2.3 GB @ 500K vectors
```

### xnai_hybrid
```
Vector Size: 1152 (384 + 768 concatenated)
Distance: Cosine similarity
HNSW M: 14, ef_construct: 180, ef: 100
Payload Fields: 11 (+ hybrid weights)
Quantization: None (full precision)
Est. Size: ~4.2 GB @ 500K vectors
```

**Total Estimated**: ~9.4 GB for all collections with 500K vectors each

---

## 🔍 Query Strategies

### Strategy 1: Basic Semantic Search
```python
# General knowledge retrieval
results = await client.search(
    collection_name="xnai_core",
    query_vector=query_vector,
    limit=10,
    score_threshold=0.7,
)
# Latency: ~50ms, P99: 100ms
```

### Strategy 2: Domain-Filtered Search
```python
# Search within domain
results = await client.search(
    collection_name="xnai_core",
    query_vector=query_vector,
    query_filter=Filter(
        must=[FieldCondition(key="domain", match=MatchValue(value="research"))]
    ),
    limit=20,
    score_threshold=0.65,
)
# Latency: ~70ms
```

### Strategy 3: Linguistic Search
```python
# Ancient Greek texts
results = await client.search(
    collection_name="xnai_linguistic",
    query_vector=query_vector,
    query_filter=Filter(
        must=[FieldCondition(key="language_code", match=MatchValue(value="grc"))]
    ),
    limit=20,
    score_threshold=0.60,
)
# Latency: ~60ms
```

### Strategy 4: Ensemble Search (High Precision)
```python
# Parallel search across all collections
# Normalize and weight scores
# Rerank and return top-k
# Latency: ~150ms (parallel)
```

### Strategy 5: Range Filter Search
```python
# Search chunk number ranges
results = await client.search(
    collection_name="xnai_core",
    query_vector=query_vector,
    query_filter=Filter(
        must=[FieldCondition(key="chunk_num", range=Range(gte=0, lte=100))]
    ),
    limit=20,
)
# Latency: ~80ms
```

---

## ⚙️ HNSW Parameter Tuning

| Parameter | Default | Impact |
|-----------|---------|--------|
| `ef` | 100 | Search effort; 50=fast, 100=balanced, 200=accurate |
| `top_k` | 10 | Results to return; more = slower |
| `score_threshold` | 0.7 | Minimum similarity; lower = more results |

**Latency Trade-offs**:
- **Low Latency** (<50ms): ef=50, score_threshold=0.75, top_k=5
- **Balanced** (50-80ms): ef=100, score_threshold=0.70, top_k=10
- **High Accuracy** (>100ms): ef=200, score_threshold=0.60, top_k=20

---

## 📈 Performance Targets

### Latency
- **P50** (median): 30ms
- **P95**: 80ms
- **P99**: 100ms

### Throughput
- **Max RPS**: 1,000 requests/second
- **Concurrent searches**: 50 active queries
- **Batch operations**: 1,000 vectors/batch

### Memory
- **xnai_core**: ~2.9 GB
- **xnai_linguistic**: ~2.3 GB (quantized)
- **xnai_hybrid**: ~4.2 GB
- **Total**: ~9.4 GB

---

## 🔐 Zero-Telemetry & Torch-Free

✅ **Zero-Telemetry**: All processing is local to Qdrant instance  
✅ **Torch-Free**: Uses FastEmbed (ONNX-based, no PyTorch dependency)  
✅ **AMD GPU Ready**: Vulkan-compatible embedding models  
✅ **6.6GB RAM Target**: Scalar quantization for memory optimization

---

## 📚 Documentation

### For Query Development
→ Read: `docs/01-infrastructure/qdrant-query-strategy.md`

### For Technical Details
→ Read: `internal_docs/qdrant-collections-design.md`

### For Configuration
→ Reference: `configs/qdrant_collections.yaml`

---

## 🛠️ Next Steps

1. **Deploy Collections**
   ```bash
   python3 scripts/initialize_qdrant_collections.py
   ```

2. **Populate with Embeddings**
   - Use existing migration script: `scripts/migrate_to_qdrant.py`
   - Or create custom embedding pipeline

3. **Benchmark Performance**
   - Measure actual P50/P95/P99 latencies
   - Optimize parameters based on results
   - Monitor memory usage

4. **Integrate with Application**
   - Update `KnowledgeClient` for multi-collection support
   - Implement ensemble search strategy
   - Add query metrics collection

5. **Production Deployment**
   - Set up monitoring and alerting
   - Configure backups
   - Plan scaling strategy

---

## 🐛 Troubleshooting

### High Latency (>100ms)
- Reduce `ef` from 100 to 50
- Verify indexed fields are actually indexed
- Check server memory usage
- Monitor CPU usage

### Low Recall (Missing Results)
- Lower `score_threshold` (0.6 instead of 0.7)
- Increase `ef` from 100 to 200
- Try xnai_hybrid for higher precision
- Verify embeddings use same model as indexed vectors

### Memory Issues
- Use xnai_linguistic (quantized) for memory savings
- Reduce batch size during indexing
- Enable on_disk storage
- Monitor collection growth

### Collection Creation Failed
- Verify Qdrant server is running: `curl http://localhost:6333/readyz`
- Check QDRANT_URL environment variable
- Review logs in `logs/qdrant_initialization.log`
- Ensure YAML configuration is valid

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review `docs/01-infrastructure/qdrant-query-strategy.md`
3. Check Qdrant logs: `logs/qdrant_initialization.log`
4. Consult Qdrant documentation: https://qdrant.tech/documentation/

---

## 📝 Version History

### v1.0.0 (2026-02-25)
- ✅ Completed design phase
- ✅ 3 collections designed and configured
- ✅ 5 query strategies documented
- ✅ Initialization script created
- ✅ Performance targets defined
- Status: **Ready for deployment**

---

**Created by**: MC-Overseer Agent  
**Task**: 1-3-qdrant-collections  
**Co-authored-by**: Copilot <223556219+Copilot@users.noreply.github.com>
