# Main API Reference

> **Generated**: 2026-02-21  
> **Source**: FastAPI OpenAPI schema (`app/XNAi_rag_app/api/entrypoint.py`)  
> **Version**: 0.1.0-alpha

---

## Overview

The Main API provides core RAG query capabilities with support for synchronous and streaming responses. It includes tiered degradation, circuit breaker patterns, and comprehensive metrics.

## Base URLs

| Environment | URL |
|-------------|-----|
| Development | `http://localhost:8000` |
| Production | Configure via `RAG_API_URL` env var |

## Endpoints

### POST /query

Synchronous RAG query endpoint with tiered degradation support.

**Endpoint**: `POST /query`  
**Response Model**: [`QueryResponse`](#queryresponse)

#### Request Body

```json
{
  "query": "What is Xoe-NovAi?",
  "use_rag": true,
  "max_tokens": 512,
  "temperature": 0.7,
  "top_p": 0.95
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | Yes | - | User query text (1-2000 chars) |
| `use_rag` | boolean | No | `true` | Enable RAG context retrieval |
| `max_tokens` | integer | No | `512` | Max tokens to generate (1-2048) |
| `temperature` | float | No | `0.7` | Sampling temperature (0.0-2.0) |
| `top_p` | float | No | `0.95` | Nucleus sampling (0.0-1.0) |

#### Response

```json
{
  "response": "Xoe-NovAi is a sovereign, offline-first...",
  "sources": ["doc1.md", "doc2.md"],
  "tokens_generated": 156,
  "duration_ms": 1245.67,
  "token_rate_tps": 42.3
}
```

| Field | Type | Description |
|-------|------|-------------|
| `response` | string | Generated response text |
| `sources` | array[string] | RAG source documents used |
| `tokens_generated` | integer | Number of tokens generated |
| `duration_ms` | float | Total processing time in ms |
| `token_rate_tps` | float | Tokens per second |

#### Example cURL

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Xoe-NovAi?", "max_tokens": 256}'
```

#### Error Responses

| Status | Code | Description |
|--------|------|-------------|
| 400 | `VALIDATION` | Invalid request parameters |
| 500 | `INTERNAL_ERROR` | Server error |
| 503 | `SERVICE_UNAVAILABLE` | LLM circuit breaker open |

---

### POST /stream

Streaming RAG query endpoint using Server-Sent Events (SSE).

**Endpoint**: `POST /stream`  
**Media Type**: `text/event-stream`

#### Request Body

Same as [`/query`](#post-query) - accepts `QueryRequest`.

#### Response Stream

The endpoint streams JSON messages with the following structure:

| Message Type | Format |
|--------------|--------|
| Sources | `{"type": "sources", "sources": [...]}` |
| Token | `{"type": "token", "content": "..."}` |
| Done | `{"type": "done", "tokens": N, "latency_ms": M}` |
| Error | `{"type": "error", "error": "message"}` |

#### Example

```javascript
// Client-side SSE handling
const eventSource = new EventSource('/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: "Explain RAG", max_tokens: 256 })
});

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'token') {
    process.stdout.write(data.content);
  } else if (data.type === 'sources') {
    console.log('Sources:', data.sources);
  }
};
```

#### Example cURL

```bash
curl -X POST http://localhost:8000/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain RAG", "max_tokens": 128}' \
  -N
```

---

### GET /health

System health check endpoint with component status.

**Endpoint**: `GET /health`  
**Response Model**: [`HealthResponse`](#healthresponse)

#### Response

```json
{
  "status": "healthy",
  "version": "0.1.0-alpha",
  "memory_gb": 4.2,
  "vectorstore_loaded": true,
  "components": {
    "llm": "ready",
    "vectorstore": "ready",
    "redis": "ready"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `healthy`, `degraded`, or `partial` |
| `version` | string | Stack version |
| `memory_gb` | float | Current memory usage |
| `vectorstore_loaded` | boolean | Vector store availability |
| `components` | object | Component status map |

#### Example cURL

```bash
curl http://localhost:8000/health
```

---

### GET /metrics

Prometheus metrics endpoint for observability.

**Endpoint**: `GET /metrics`  
**Media Type**: `text/plain; version=0.0.4`

#### Available Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `xnai_queries_total` | Counter | Total queries processed |
| `xnai_tokens_generated_total` | Counter | Total tokens generated |
| `xnai_response_latency_ms` | Histogram | Response latency |
| `xnai_token_rate_tps` | Gauge | Current token rate |
| `xnai_errors_total` | Counter | Total errors by type |
| `xnai_circuit_breaker_state` | Gauge | Circuit breaker state |

#### Example

```bash
curl http://localhost:8000/metrics
```

Output:
```
# HELP xnai_queries_total Total queries processed
# TYPE xnai_queries_total counter
xnai_queries_total{method="query",use_rag="true"} 1234
xnai_queries_total{method="query",use_rag="false"} 56

# HELP xnai_response_latency_ms Response latency in milliseconds
# TYPE xnai_response_latency_ms histogram
xnai_response_latency_ms_bucket{le="100"} 890
xnai_response_latency_ms_bucket{le="500"} 1100
...
```

---

## Response Schemas

### QueryResponse

```python
class QueryResponse(BaseModel):
    response: str                              # Generated response
    sources: List[str] = []                   # RAG sources
    tokens_generated: Optional[int] = None    # Token count
    duration_ms: Optional[float] = None       # Processing time (ms)
    token_rate_tps: Optional[float] = None    # Tokens per second
```

### HealthResponse

```python
class HealthResponse(BaseModel):
    status: str                    # healthy | degraded | partial
    version: str                   # Stack version
    memory_gb: float              # Memory usage
    vectorstore_loaded: bool      # Vector store status
    components: Dict[str, Any]    # Component status
```

### ErrorResponse

```python
class ErrorResponse(BaseModel):
    error_code: str                    # Unique error identifier
    message: str                       # Human-readable message
    category: str                      # Error category
    http_status: int                  # HTTP status code
    timestamp: datetime               # ISO 8601 timestamp
    details: Optional[Dict]           # Subsystem context
    recovery_suggestion: Optional[str] # Recovery guidance
    request_id: Optional[str]         # Request correlation ID
```

---

## Circuit Breaker Integration

The API uses a circuit breaker pattern for resilience:

| State | Behavior |
|-------|----------|
| `CLOSED` | Normal operation, requests pass through |
| `OPEN` | Service unavailable, fast-fail |
| `HALF_OPEN` | Testing recovery, limited requests |

When the LLM circuit is open, `/query` returns:
```json
{
  "error": "LLM service unavailable (circuit open)"
}
```
With HTTP status `503`.

---

## Tiered Degradation

The API supports tier-based configuration for resource-constrained environments:

| Tier | max_tokens | top_k | context_chars |
|------|------------|-------|--------------|
| minimal | 128 | 2 | 1000 |
| standard | 512 | 4 | 4000 |
| performance | 1024 | 8 | 8000 |

Configure via `config.toml` section `[tier.default]`.

---

## Authentication

Currently, the Main API does not require authentication for local development. For production deployment, see the [IAM Service](iam_service.md) documentation.

---

## Rate Limiting

No rate limiting is currently enforced at the API level. Implement via middleware or reverse proxy (e.g., Caddy) for production.

---

## Related Documentation

- [Semantic Search API](SEMANTIC_SEARCH_API.md)
- [IAM Service](iam_service.md)
- [Error Handling](../03-reference/error-handling.md)
- [Configuration](../03-reference/configuration.md)
