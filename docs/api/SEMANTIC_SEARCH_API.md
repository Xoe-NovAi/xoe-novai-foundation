# Semantic Search REST API Documentation

## Overview

The Xoe-NovAi Semantic Search API provides REST endpoints for performing semantic search on technical manuals and documentation. It combines semantic (vector-based) and lexical (keyword-based) search to deliver accurate results.

**Version:** 0.1.0-phase6  
**API Type:** REST with JSON payloads  
**Authentication:** Request ID tracking via `X-Request-ID` header  
**Response Format:** JSON with consistent error handling  

---

## API Endpoints

### 1. POST /search

Performs a semantic search query on indexed documents.

#### Request

**Content-Type:** `application/json`

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: custom-request-id" \
  -d '{
    "query": "How to configure Python for machine learning?",
    "top_k": 5,
    "min_score": 0.5,
    "alpha": 0.5,
    "filters": {"source": "official_docs"}
  }'
```

**Request Body Schema:**

```json
{
  "query": "string (required, 1-2000 chars)",
  "top_k": "integer (optional, default: 5, range: 1-100)",
  "min_score": "number (optional, default: 0.0, range: 0.0-1.0)",
  "alpha": "number (optional, default: 0.5, range: 0.0-1.0)",
  "filters": "object (optional, metadata filters)"
}
```

**Parameter Descriptions:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query text (1-2000 characters) |
| `top_k` | integer | No | 5 | Number of results to return (1-100) |
| `min_score` | float | No | 0.0 | Minimum similarity score filter (0.0-1.0) |
| `alpha` | float | No | 0.5 | Blend factor: 0=pure semantic, 1=pure lexical |
| `filters` | object | No | null | Metadata filters for documents |

**Alpha Parameter Explanation:**
- `alpha = 0.0`: Pure semantic search (embeddings-based)
- `alpha = 0.5`: Balanced hybrid search (default, recommended)
- `alpha = 1.0`: Pure lexical search (keyword-based)

#### Response

**Status Code:** `200 OK`

```json
{
  "request_id": "req_a1b2c3d4e5f6",
  "query": "How to configure Python for machine learning?",
  "result_count": 3,
  "results": [
    {
      "id": "doc_001",
      "rank": 1,
      "score": 0.9523,
      "content": "Python is a versatile programming language widely used in machine learning and data science. To configure Python for ML projects, you need to install essential libraries...",
      "metadata": {
        "source": "official_docs",
        "version": "3.10",
        "category": "tutorial"
      }
    },
    {
      "id": "doc_002",
      "rank": 2,
      "score": 0.8734,
      "content": "Machine learning with Python requires proper environment setup. The most popular framework is TensorFlow or PyTorch. Here's how to set up your environment...",
      "metadata": {
        "source": "guide",
        "difficulty": "intermediate"
      }
    },
    {
      "id": "doc_003",
      "rank": 3,
      "score": 0.7891,
      "content": "Virtual environments in Python are essential for project isolation. Use venv or conda to create isolated environments for your machine learning projects...",
      "metadata": {
        "source": "reference",
        "updated": "2026-02-01"
      }
    }
  ],
  "execution_time_ms": 125.42,
  "timestamp": "2026-02-16T10:30:45.123456Z"
}
```

**Response Schema:**

```json
{
  "request_id": "string",
  "query": "string",
  "result_count": "integer",
  "results": [
    {
      "id": "string",
      "rank": "integer",
      "score": "number",
      "content": "string",
      "metadata": "object"
    }
  ],
  "execution_time_ms": "number",
  "timestamp": "string"
}
```

---

### 2. GET /health

Health check endpoint for service monitoring.

#### Request

```bash
curl -X GET "http://localhost:8000/health"
```

#### Response

**Status Code:** `200 OK`

```json
{
  "status": "healthy",
  "timestamp": "2026-02-16T10:30:45.123456Z",
  "version": "0.1.0-phase6",
  "dependencies": {
    "embeddings": "ready",
    "index": "ready"
  }
}
```

**Status Values:**
- `healthy`: All dependencies ready
- `degraded`: Some dependencies ready, some unavailable
- `unhealthy`: Critical dependencies unavailable

---

## Error Handling

All errors follow a consistent format with structured error information.

### Error Response Format

```json
{
  "error_code": "validation_a3f2",
  "message": "Query cannot be empty",
  "category": "validation",
  "timestamp": 1708082445.123456,
  "details": {
    "field": "query"
  },
  "recovery_suggestion": "Provide a non-empty search query",
  "request_id": "req_a1b2c3d4e5f6"
}
```

### HTTP Status Codes

| Status | Category | Meaning | Recovery |
|--------|----------|---------|----------|
| 400 | validation | Invalid request parameters | Review request and fix parameters |
| 401 | authentication | Authentication required | Provide valid credentials |
| 403 | authorization | Access denied | Check permissions or authenticate |
| 404 | not_found | Resource not found | Verify resource exists |
| 429 | rate_limited | Too many requests | Wait before retrying |
| 500 | internal_error | Server error | Retry after a delay |
| 503 | service_unavailable | Service temporarily unavailable | Retry in a few moments |
| 504 | timeout | Request timeout | Try with smaller query or fewer results |

### Common Error Codes

| Error Code | HTTP Status | Meaning | Solution |
|-----------|------------|---------|----------|
| `validation_a3f2` | 400 | Query validation failed | Ensure query is 1-2000 characters |
| `service_uninitialized` | 503 | Service not ready | Wait for initialization |
| `embedding_failed` | 500 | Embedding computation failed | Retry the request |
| `index_error` | 500 | Index access error | Check index health |
| `timeout_exceeded` | 504 | Search timed out | Try simpler query |

---

## Examples

### Example 1: Basic Search

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "vector database"
  }'
```

Response:
```json
{
  "request_id": "req_1234567890ab",
  "query": "vector database",
  "result_count": 2,
  "results": [
    {
      "id": "vector_db_intro",
      "rank": 1,
      "score": 0.9845,
      "content": "Vector databases are specialized systems for storing and searching high-dimensional vector data...",
      "metadata": {}
    }
  ],
  "execution_time_ms": 89.23,
  "timestamp": "2026-02-16T10:32:15.456789Z"
}
```

### Example 2: Advanced Search with Filters

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "FAISS indexing strategies",
    "top_k": 10,
    "min_score": 0.7,
    "alpha": 0.3,
    "filters": {
      "source": "academic_papers",
      "year": 2024
    }
  }'
```

### Example 3: Lexical-Heavy Search

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "API endpoint documentation",
    "top_k": 5,
    "alpha": 0.9
  }'
```

### Example 4: Semantic-Heavy Search

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning configuration",
    "top_k": 5,
    "alpha": 0.1
  }'
```

### Example 5: Health Check

```bash
curl -X GET "http://localhost:8000/health"
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-16T10:35:22.789012Z",
  "version": "0.1.0-phase6",
  "dependencies": {
    "embeddings": "ready",
    "index": "ready"
  }
}
```

---

## Request/Response Headers

### Request Headers

| Header | Value | Required |
|--------|-------|----------|
| `Content-Type` | `application/json` | Yes (POST) |
| `X-Request-ID` | Custom request ID | No |
| `Accept` | `application/json` | No |

### Response Headers

| Header | Purpose |
|--------|---------|
| `X-Request-ID` | Echoes/generates request ID for tracing |
| `Content-Type` | Always `application/json` |

---

## Performance Characteristics

### Query Execution Time

Expected performance on production servers (6-core CPU, 6.6GB RAM):

| Query Type | Top-K | Avg Time | P95 | P99 |
|-----------|-------|----------|-----|-----|
| Simple keyword | 5 | 45ms | 120ms | 200ms |
| Hybrid search | 5 | 95ms | 250ms | 400ms |
| Semantic-heavy | 5 | 120ms | 350ms | 600ms |
| Large top-k (100) | 100 | 280ms | 800ms | 1200ms |

### Memory Usage

- Per concurrent request: ~50-150MB
- Maximum concurrent requests: Limited by available RAM
- Index size: Depends on document count and embedding dimension

---

## Rate Limiting

Currently, the API does not enforce rate limiting. Future versions may implement:

- Per-API-key limits
- Per-IP address limits
- Burst allowances

---

## Authentication & Security

### Current Implementation

- No authentication required
- Request ID tracking for audit trails
- Error messages are sanitized (no sensitive data)

### Future Enhancements

- API key authentication
- OAuth 2.0 support
- Rate limiting
- Request signing

---

## Integration Guide

### Python

```python
import requests
import json

def semantic_search(query: str, top_k: int = 5):
    """Search using the semantic search API"""
    
    response = requests.post(
        "http://localhost:8000/search",
        headers={"Content-Type": "application/json"},
        json={
            "query": query,
            "top_k": top_k,
            "alpha": 0.5
        }
    )
    
    if response.status_code == 200:
        results = response.json()
        for result in results['results']:
            print(f"Rank {result['rank']}: {result['id']} (score: {result['score']})")
            print(f"  {result['content'][:100]}...\n")
    else:
        print(f"Error: {response.json()}")

# Usage
semantic_search("How to configure embeddings?")
```

### JavaScript

```javascript
async function semanticSearch(query, topK = 5) {
  const response = await fetch('http://localhost:8000/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      top_k: topK,
      alpha: 0.5
    })
  });
  
  if (response.ok) {
    const data = await response.json();
    return data.results;
  } else {
    const error = await response.json();
    console.error('API Error:', error.message);
    throw new Error(error.message);
  }
}

// Usage
semanticSearch('Machine learning setup').then(results => {
  results.forEach(result => {
    console.log(`${result.rank}. ${result.id} (${result.score})`);
  });
});
```

### cURL

See Examples section above.

---

## Monitoring & Logging

### Logging Features

- **Request Logging**: All requests logged with request_id and span_id
- **Performance Logging**: Query execution times tracked
- **Error Logging**: All errors logged with full context
- **Trace Correlation**: Use request_id across distributed systems

### Log Locations

- API logs: `/var/log/xnai/api.log`
- Error logs: `/var/log/xnai/errors.log`
- Debug logs: `/var/log/xnai/debug.log` (if enabled)

### Example Log Entry

```json
{
  "timestamp": "2026-02-16T10:30:45.123456Z",
  "level": "INFO",
  "module": "semantic_search",
  "function": "search",
  "message": "Search completed: returned 5 results",
  "request_id": "req_a1b2c3d4e5f6",
  "span_id": "span_x1y2z3w4v5u6",
  "elapsed_ms": 125.42
}
```

---

## Troubleshooting

### Common Issues

**Issue: "Service not initialized" error**
- **Cause**: Embeddings or index not loaded
- **Solution**: Ensure service initialization is complete; check health endpoint

**Issue: Search returns no results**
- **Cause**: `min_score` threshold too high, or no matching documents
- **Solution**: Lower `min_score`, try different query, check filters

**Issue: Slow queries (> 1 second)**
- **Cause**: Large `top_k` value, complex query, or system under load
- **Solution**: Reduce `top_k`, simplify query, check system resources

**Issue: "Request timeout" error**
- **Cause**: Query too complex or system overloaded
- **Solution**: Retry with simpler query or reduced `top_k`

---

## Version History

### v0.1.0-phase6 (2026-02-16)
- Initial release
- `/search` and `/health` endpoints
- Hybrid semantic/lexical search
- Request ID tracking
- Structured error handling

### Planned Features
- v0.2.0: Authentication & API keys
- v0.3.0: Advanced filtering and faceting
- v0.4.0: Batch search endpoint
- v0.5.0: WebSocket support for streaming results

---

## Support & Feedback

For issues, questions, or feature requests:

- **Documentation**: https://docs.xnai.com/api/semantic-search
- **Issue Tracker**: https://github.com/xnai-foundation/xnai/issues
- **Email**: api-support@xnai.com
- **Community**: https://discord.gg/xnai

---

## License

This API is part of the Xoe-NovAi project and is licensed under the terms defined in the project LICENSE file.
