# XNAi Foundation - Qdrant Collections Query Strategy Guide

**Version**: 1.0.0  
**Last Updated**: 2026-02-25  
**Author**: MC-Overseer Agent  
**Purpose**: Comprehensive guide for querying 3 Qdrant collections with optimized search parameters

---

## Overview

This guide defines query strategies for the three Qdrant collections:

1. **xnai_core** - General semantic search (384-dim FastEmbed)
2. **xnai_linguistic** - Ancient Greek and linguistic search (768-dim Ancient-Greek-BERT)
3. **xnai_hybrid** - Multi-model ensemble search (1152-dim concatenated)

### Latency Targets
- **P50**: 30ms
- **P95**: 80ms
- **P99**: 100ms

### Throughput
- **Max RPS**: 1000 requests/second
- **Concurrent searches**: 50 active queries

---

## Collection Selection Matrix

| Use Case | Collection | Reason |
|----------|-----------|--------|
| General knowledge retrieval | `xnai_core` | Fast, balanced performance |
| Ancient Greek texts | `xnai_linguistic` | Specialized embeddings |
| Cross-modal ranking | `xnai_hybrid` | Combined representations |
| Domain-specific filtering | `xnai_core` with filters | Indexed domain field |
| Linguistic analysis | `xnai_linguistic` | Language-aware embeddings |
| High-precision ranking | `xnai_hybrid` | Ensemble of models |

---

## Query Strategies

### Strategy 1: Basic Semantic Search

**Use Case**: General knowledge base queries  
**Collection**: `xnai_core`  
**Latency Target**: <50ms

```python
# Query Configuration
{
  "collection": "xnai_core",
  "top_k": 10,
  "score_threshold": 0.7,
  "ef_search": 100,
  "search_params": {
    "ef": 100,  # Effort factor for search
  }
}

# Search Parameters
- Vector: Generated from query using FastEmbed (all-MiniLM-L6-v2)
- Limit: 10 results
- Score threshold: 0.7 (cosine similarity)
- No filters applied
```

**Implementation**:
```python
async def semantic_search(
    client: AsyncQdrantClient,
    query_vector: List[float],
    top_k: int = 10,
    score_threshold: float = 0.7,
) -> List[SearchResult]:
    results = await client.search(
        collection_name="xnai_core",
        query_vector=query_vector,
        limit=top_k,
        score_threshold=score_threshold,
        search_params=models.SearchParams(ef=100),
    )
    return results
```

---

### Strategy 2: Domain-Filtered Search

**Use Case**: Search within specific knowledge domains  
**Collection**: `xnai_core`  
**Latency Target**: <70ms (slightly higher due to filtering)

```python
# Query Configuration
{
  "collection": "xnai_core",
  "top_k": 20,
  "score_threshold": 0.65,
  "filter": {
    "must": [
      {
        "key": "domain",
        "match": {
          "value": "research"  # Filter by domain
        }
      }
    ]
  },
  "search_params": {
    "ef": 100,
  }
}

# Supported Domains
- "core": Core XNAi documentation
- "research": Research papers and findings
- "archive": Historical/archived documents
- "linguistic": Linguistic and etymological data
```

**Implementation**:
```python
async def domain_search(
    client: AsyncQdrantClient,
    query_vector: List[float],
    domain: str,
    top_k: int = 20,
    score_threshold: float = 0.65,
) -> List[SearchResult]:
    filter_condition = models.Filter(
        must=[
            models.FieldCondition(
                key="domain",
                match=models.MatchValue(value=domain)
            )
        ]
    )
    
    results = await client.search(
        collection_name="xnai_core",
        query_vector=query_vector,
        query_filter=filter_condition,
        limit=top_k,
        score_threshold=score_threshold,
        search_params=models.SearchParams(ef=100),
    )
    return results
```

---

### Strategy 3: Linguistic Search with Language Filter

**Use Case**: Search ancient Greek texts and linguistic data  
**Collection**: `xnai_linguistic`  
**Latency Target**: <60ms

```python
# Query Configuration
{
  "collection": "xnai_linguistic",
  "top_k": 20,
  "score_threshold": 0.60,  # Lower threshold for linguistic variance
  "filter": {
    "must": [
      {
        "key": "language_code",
        "match": {
          "value": "grc"  # Ancient Greek code
        }
      }
    ]
  },
  "search_params": {
    "ef": 100,
  }
}

# Language Codes
- "grc": Ancient Greek
- "lat": Latin
- "eng": English
```

**Implementation**:
```python
async def linguistic_search(
    client: AsyncQdrantClient,
    query_vector: List[float],
    language_code: str = "grc",
    top_k: int = 20,
    score_threshold: float = 0.60,
) -> List[SearchResult]:
    filter_condition = models.Filter(
        must=[
            models.FieldCondition(
                key="language_code",
                match=models.MatchValue(value=language_code)
            )
        ]
    )
    
    results = await client.search(
        collection_name="xnai_linguistic",
        query_vector=query_vector,
        query_filter=filter_condition,
        limit=top_k,
        score_threshold=score_threshold,
        search_params=models.SearchParams(ef=100),
    )
    return results
```

---

### Strategy 4: Multi-Collection Ensemble Search

**Use Case**: High-precision results combining multiple models  
**Collections**: All three (xnai_core, xnai_linguistic, xnai_hybrid)  
**Latency Target**: <150ms (parallel searches)

```python
# Query Configuration
{
  "strategy": "ensemble",
  "parallel": true,
  "collections": [
    {
      "name": "xnai_core",
      "query_vector_model": "fastembed",
      "top_k": 15,
      "score_threshold": 0.7,
      "weight": 0.3,
    },
    {
      "name": "xnai_linguistic",
      "query_vector_model": "ancient-greek-bert",
      "top_k": 15,
      "score_threshold": 0.60,
      "weight": 0.2,
    },
    {
      "name": "xnai_hybrid",
      "query_vector_model": "hybrid",
      "top_k": 15,
      "score_threshold": 0.72,
      "weight": 0.5,
    }
  ],
  "final_top_k": 10,
  "aggregation": "weighted_average",
}

# Aggregation Method
1. Search all collections in parallel
2. Normalize scores to [0, 1]
3. Apply collection weights
4. Compute weighted average score
5. Rerank by ensemble score
6. Return top-k results
```

**Implementation**:
```python
async def ensemble_search(
    client: AsyncQdrantClient,
    query_vectors: Dict[str, List[float]],  # Model -> vector mapping
    final_top_k: int = 10,
) -> List[SearchResult]:
    """
    Search all collections in parallel and ensemble results.
    
    Args:
        client: Qdrant async client
        query_vectors: Dict of model name to vector
        final_top_k: Final number of results to return
    
    Returns:
        Ensemble search results
    """
    collections_config = [
        ("xnai_core", 0.3, 0.7),
        ("xnai_linguistic", 0.2, 0.60),
        ("xnai_hybrid", 0.5, 0.72),
    ]
    
    async def search_collection(name, weight, threshold):
        vector = query_vectors.get(name)
        if not vector:
            return []
        
        results = await client.search(
            collection_name=name,
            query_vector=vector,
            limit=15,
            score_threshold=threshold,
        )
        
        # Normalize scores
        if results:
            max_score = max(r.score for r in results)
            for r in results:
                r.score = (r.score / max_score) * weight
        
        return results
    
    # Search all collections in parallel
    tasks = [
        search_collection(name, weight, threshold)
        for name, weight, threshold in collections_config
    ]
    all_results = await asyncio.gather(*tasks)
    
    # Flatten and aggregate
    aggregated = {}
    for results in all_results:
        for result in results:
            if result.id not in aggregated:
                aggregated[result.id] = result
            else:
                # Average scores
                aggregated[result.id].score = (
                    aggregated[result.id].score + result.score
                ) / 2
    
    # Sort and return top-k
    sorted_results = sorted(
        aggregated.values(),
        key=lambda r: r.score,
        reverse=True
    )[:final_top_k]
    
    return sorted_results
```

---

### Strategy 5: Range Filter Search

**Use Case**: Search within chunk number ranges  
**Collection**: `xnai_core`  
**Latency Target**: <80ms

```python
# Query Configuration
{
  "collection": "xnai_core",
  "top_k": 20,
  "score_threshold": 0.65,
  "filter": {
    "must": [
      {
        "key": "chunk_num",
        "range": {
          "gte": 0,
          "lte": 100
        }
      }
    ]
  },
  "search_params": {
    "ef": 100,
  }
}

# Supported Range Operators
- "gte": Greater than or equal
- "lte": Less than or equal
- "gt": Greater than
- "lt": Less than
```

**Implementation**:
```python
async def range_search(
    client: AsyncQdrantClient,
    query_vector: List[float],
    chunk_num_min: int = 0,
    chunk_num_max: int = 100,
    top_k: int = 20,
    score_threshold: float = 0.65,
) -> List[SearchResult]:
    filter_condition = models.Filter(
        must=[
            models.FieldCondition(
                key="chunk_num",
                range=models.Range(
                    gte=chunk_num_min,
                    lte=chunk_num_max
                )
            )
        ]
    )
    
    results = await client.search(
        collection_name="xnai_core",
        query_vector=query_vector,
        query_filter=filter_condition,
        limit=top_k,
        score_threshold=score_threshold,
        search_params=models.SearchParams(ef=100),
    )
    return results
```

---

## HNSW Search Parameters

### Parameter Tuning

| Parameter | Default | Range | Impact |
|-----------|---------|-------|--------|
| `ef` | 100 | 10-1000 | Search effort factor; higher = more accurate, slower |
| `ef_construct` | 200 (built-in) | 50-500 | Index construction effort |
| `m` | 16 (built-in) | 5-20 | Connections per node |
| `top_k` | 10 | 1-100 | Maximum results |
| `score_threshold` | 0.7 | 0.0-1.0 | Minimum similarity threshold |

### Latency vs Accuracy Trade-offs

**Low Latency (<50ms)**:
```python
search_params = models.SearchParams(ef=50)
score_threshold = 0.75
top_k = 5
```

**Balanced (50-80ms)**:
```python
search_params = models.SearchParams(ef=100)
score_threshold = 0.70
top_k = 10
```

**High Accuracy (>100ms)**:
```python
search_params = models.SearchParams(ef=200)
score_threshold = 0.60
top_k = 20
```

---

## Filtering Best Practices

### 1. Indexed Field Filtering

For best performance, always filter on indexed fields:
- `chunk_id` (UUID, indexed)
- `doc_id` (UUID, indexed)
- `domain` (string, indexed)
- `chunk_num` (integer, indexed)
- `language_code` (string, indexed in xnai_linguistic)

### 2. Filter Optimization

```python
# ✅ GOOD: Filter on indexed field first, then search
filter_condition = models.Filter(
    must=[
        models.FieldCondition(
            key="domain",
            match=models.MatchValue(value="research")
        )
    ]
)

results = await client.search(
    collection_name="xnai_core",
    query_vector=query_vector,
    query_filter=filter_condition,  # Apply before search
    limit=top_k,
)

# ❌ BAD: Filtering on non-indexed fields
# This will scan all vectors before filtering
```

### 3. Complex Filters

```python
# AND condition
filter_and = models.Filter(
    must=[
        models.FieldCondition(
            key="domain",
            match=models.MatchValue(value="research")
        ),
        models.FieldCondition(
            key="language_code",
            match=models.MatchValue(value="eng")
        )
    ]
)

# OR condition
filter_or = models.Filter(
    should=[
        models.FieldCondition(
            key="domain",
            match=models.MatchValue(value="research")
        ),
        models.FieldCondition(
            key="domain",
            match=models.MatchValue(value="core")
        )
    ],
    min_should_match=1
)

# NOT condition
filter_not = models.Filter(
    must_not=[
        models.FieldCondition(
            key="domain",
            match=models.MatchValue(value="archive")
        )
    ]
)
```

---

## Performance Optimization Tips

### 1. Batch Searches

```python
async def batch_search(
    client: AsyncQdrantClient,
    queries: List[str],
    embedding_model,
    batch_size: int = 10,
) -> List[List[SearchResult]]:
    """Search multiple queries efficiently."""
    
    results = []
    
    for i in range(0, len(queries), batch_size):
        batch_queries = queries[i:i + batch_size]
        batch_vectors = [
            await embedding_model.encode(q)
            for q in batch_queries
        ]
        
        # Search in parallel
        batch_results = await asyncio.gather(*[
            client.search(
                collection_name="xnai_core",
                query_vector=vec,
                limit=10,
            )
            for vec in batch_vectors
        ])
        
        results.extend(batch_results)
    
    return results
```

### 2. Caching Strategy

```python
# Cache frequently used searches
search_cache: Dict[str, List[SearchResult]] = {}

async def cached_search(
    client: AsyncQdrantClient,
    query_vector: List[float],
    cache_key: str,
    ttl: int = 3600,
) -> List[SearchResult]:
    if cache_key in search_cache:
        return search_cache[cache_key]
    
    results = await client.search(
        collection_name="xnai_core",
        query_vector=query_vector,
        limit=10,
    )
    
    search_cache[cache_key] = results
    return results
```

### 3. Connection Pooling

```python
# Reuse client connections
class QdrantConnectionPool:
    def __init__(self, url: str, max_connections: int = 10):
        self.url = url
        self.max_connections = max_connections
        self.clients: List[AsyncQdrantClient] = []
        self.available: asyncio.Queue[AsyncQdrantClient] = asyncio.Queue()
    
    async def initialize(self):
        for _ in range(self.max_connections):
            client = AsyncQdrantClient(url=self.url)
            self.clients.append(client)
            self.available.put_nowait(client)
    
    async def get_client(self) -> AsyncQdrantClient:
        return await self.available.get()
    
    async def release_client(self, client: AsyncQdrantClient):
        await self.available.put(client)
```

---

## Monitoring and Metrics

### Query Performance Metrics

```python
@dataclass
class QueryMetrics:
    query_time_ms: float
    embedding_time_ms: float
    search_time_ms: float
    result_count: int
    avg_score: float
    collection: str
    top_k: int

# Track metrics
metrics = QueryMetrics(
    query_time_ms=45.2,
    embedding_time_ms=10.5,
    search_time_ms=34.7,
    result_count=10,
    avg_score=0.82,
    collection="xnai_core",
    top_k=10,
)

# Log percentiles
# P50: 30ms, P95: 80ms, P99: 100ms
```

### Health Checks

```python
async def health_check(client: AsyncQdrantClient) -> Dict[str, Any]:
    """Check Qdrant health and collection stats."""
    try:
        collections = await client.get_collections()
        
        stats = {}
        for collection in collections.collections:
            info = await client.get_collection(collection.name)
            stats[collection.name] = {
                "points": info.points_count,
                "vectors": info.vectors_count,
                "status": info.status,
            }
        
        return {
            "healthy": True,
            "collections": stats,
        }
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
        }
```

---

## Troubleshooting

### High Latency Issues

1. **Check ef parameter** - If search latency >100ms, try reducing `ef` from 100 to 50
2. **Verify indexing** - Ensure indexed fields are actually indexed with `create_payload_index`
3. **Monitor memory** - High memory usage slows searches; check collection size
4. **Tune ef_construct** - For index creation, ensure adequate ef_construct (default 200)

### Low Recall Issues

1. **Increase score_threshold** - If missing relevant results, lower score_threshold (0.6 instead of 0.7)
2. **Try different collections** - Use xnai_hybrid for higher precision
3. **Adjust ef** - Increase ef from 100 to 200 for better accuracy
4. **Check embeddings** - Verify query embeddings are generated with same model as indexed data

### Memory Issues

1. **Enable quantization** - Use xnai_linguistic (scalar quantization) for memory savings
2. **Reduce batch size** - Process smaller batches during indexing
3. **Use on_disk storage** - Ensure `on_disk=true` for vector storage

---

## Summary Table

| Scenario | Collection | Top-K | Score Threshold | EF | Est. Latency |
|----------|-----------|-------|-----------------|----|----|
| General search | xnai_core | 10 | 0.70 | 100 | 50ms |
| Domain filtered | xnai_core | 20 | 0.65 | 100 | 70ms |
| Linguistic | xnai_linguistic | 20 | 0.60 | 100 | 60ms |
| High precision | xnai_hybrid | 10 | 0.72 | 100 | 70ms |
| Ensemble | All 3 | 15 each | varies | 100 | 150ms |
| Low latency | xnai_core | 5 | 0.75 | 50 | 30ms |

---

**Next Steps**:
1. Test with production queries to establish baseline performance
2. Collect P50/P95/P99 latency metrics
3. Adjust ef, score_threshold parameters based on SLA requirements
4. Monitor memory usage and collection growth
5. Implement automated scaling if needed
