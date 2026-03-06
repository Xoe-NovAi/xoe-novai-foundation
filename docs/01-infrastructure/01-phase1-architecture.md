---
title: Phase 1 Infrastructure Architecture
description: Comprehensive architecture overview for XNAi Foundation Phase 1
last_updated: 2026-02-25
status: active
persona_focus: DevOps, SRE, Infrastructure Engineers
---

# Phase 1 Infrastructure Architecture

## Overview

Phase 1 of the XNAi Foundation Stack is built on a modern, horizontally-scalable microservices architecture optimized for AMD Ryzen processors (Zen 2+) and rootless Podman. The stack emphasizes zero-telemetry, ethical guardrails (Maat's 42 Ideals), and resilience through graceful degradation.

**Stack Version:** 0.1.7 (BuildKit Optimized)
**Target Hardware:** AMD Ryzen 5700U (8 cores / 16 threads) or equivalent
**Container Runtime:** Rootless Podman
**Orchestration:** Docker Compose v3.9+

---

## High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     External Sources                         │
│         (Documents, APIs, Knowledge Feeds, Crawlers)        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
    ┌────────────────────────────────┐
    │   Crawler Service              │
    │  - Web scraping                │
    │  - Document ingestion          │
    │  - Content normalization       │
    └────────┬───────────────────────┘
             │
             ▼
    ┌─────────────────────────────────┐
    │  Curation Worker                │
    │  - Chunking strategy selection  │
    │  - Duplicate detection          │
    │  - Quality scoring              │
    │  - Domain classification        │
    └────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│            PostgreSQL (Primary Store)                │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐                │
│  │ Documents    │  │ Chunks       │                │
│  │ Tables       │  │ Tables       │                │
│  ├──────────────┤  ├──────────────┤                │
│  │ Domains      │  │ Embeddings   │                │
│  │ Relations    │  │ Query Cache  │                │
│  │ Audit Logs   │  │ Stats Views  │                │
│  └──────────────┘  └──────────────┘                │
└──────────┬────────────────────────┬──────────────────┘
           │                        │
           ▼                        ▼
    ┌─────────────┐       ┌──────────────┐
    │   Redis     │       │  Qdrant      │
    │  (Cache &   │       │ (Vector DB)  │
    │  Sessions)  │       │              │
    │             │       │ Collections: │
    │ - Sessions  │       │ - Embeddings │
    │ - Streams   │       │ - Payloads   │
    │ - Pub/Sub   │       │ - Metadata   │
    └──────┬──────┘       └──────┬───────┘
           │                     │
           └──────────┬──────────┘
                      │
                      ▼
          ┌─────────────────────────┐
          │   RAG API Service       │
          │ (/knowledge/query)      │
          │ (/knowledge/retrieve)   │
          └─────────┬───────────────┘
                    │
                    ▼
          ┌─────────────────────────┐
          │  User Interfaces        │
          │ ┌──────────────────┐    │
          │ │ Chainlit UI      │    │
          │ │ (Chat/Voice)     │    │
          │ │                  │    │
          │ │ REST API Clients │    │
          │ └──────────────────┘    │
          └─────────────────────────┘
```

---

## Component Architecture

### 1. Service Discovery & Health Monitoring
**Service:** Consul
**Role:** Central service registry and health monitoring
**Responsibilities:**
- Service discovery for all containers
- Health check aggregation
- DNS-based service routing
- Configuration management

```
Consul (Port 8500 UI, 8600 DNS)
├── Service Registration
│   ├── PostgreSQL health checks
│   ├── Redis health checks
│   ├── Qdrant health checks
│   └── API service endpoints
└── Health Monitoring
    ├── Periodic health checks
    ├── Automatic failover triggers
    └── Alert generation
```

### 2. Caching & Stream Coordination
**Service:** Redis
**Role:** High-speed cache, session store, and event stream coordinator
**Responsibilities:**
- Session persistence with TTL
- Query result caching
- Pub/Sub event streams
- Rate limiting and throttling
- Graceful fallback: In-memory cache when Redis unavailable

```
Redis (Port 6379)
├── Data Structures
│   ├── Strings (sessions, cache)
│   ├── Hashes (user state)
│   ├── Streams (event log)
│   └── Sets (deduplication)
└── LRU Memory Policy
    ├── 512MB max memory
    ├── allkeys-lru eviction
    └── Persistent RDB snapshots
```

### 3. Time-Series Metrics Storage
**Service:** VictoriaMetrics
**Role:** Metrics collection and long-term storage
**Responsibilities:**
- Metrics ingestion from all services
- Time-series data compression (10x vs Prometheus)
- Long-term storage (1 year retention)
- Query interface for dashboards

```
VictoriaMetrics (Port 8428)
├── Metrics Collection
│   ├── API request latencies
│   ├── Database query times
│   ├── Vector search latencies
│   ├── Cache hit rates
│   └── Error rates per service
└── Storage
    ├── 365-day retention
    ├── High compression
    └── Single binary deployment
```

### 4. Vector Database
**Service:** Qdrant
**Role:** Semantic search and embedding storage
**Responsibilities:**
- Store and index embeddings from multiple models
- HNSW-based approximate nearest neighbor search
- Multi-payload support for metadata
- Automatic backups

```
Qdrant (Port 6333 API, 6334 gRPC)
├── Collections
│   ├── fastembed-model (384-dim)
│   ├── ancient-bert-model (768-dim)
│   └── onnx-minilm-model (384-dim)
├── Indexing Strategy
│   ├── HNSW M=16, ef_construct=200
│   ├── Quantization: int8 for memory efficiency
│   └── Dynamic thresholds based on collection size
└── Payload Fields
    ├── chunk_id (UUID)
    ├── document_id (UUID)
    ├── model_type (string)
    └── metadata (JSON)
```

### 5. Primary Data Store
**Service:** PostgreSQL
**Role:** Primary operational database
**Responsibilities:**
- Document and chunk storage
- Embedding metadata tracking
- Agent personas and learning states
- Audit logs and compliance
- Full-text search indices
- Materialized views for analytics

```
PostgreSQL (Port 5432)
├── Core Tables
│   ├── knowledge_domains (hierarchical taxonomy)
│   ├── documents (with content + metadata)
│   ├── chunks (token-aware segments)
│   ├── embeddings (reference to vectors)
│   ├── knowledge_relations (graph links)
│   ├── agent_personas (agent state)
│   └── audit_log (compliance trail)
├── Materialized Views
│   ├── document_stats_by_domain
│   ├── chunk_stats_by_model
│   └── agent_interaction_metrics
└── Full-Text Indexes
    ├── documents_fts (GIN index on title+content)
    └── chunks_fts (GIN index on content)
```

### 6. RAG API Service
**Service:** xnai_rag_api
**Role:** Core query interface and knowledge retrieval
**Responsibilities:**
- RESTful API for queries and retrieval
- Semantic search via Qdrant
- Ranking and re-ranking of results
- Session management
- Authentication and authorization

```
RAG API (Port 8000)
├── Endpoints
│   ├── POST /knowledge/query
│   ├── GET /knowledge/retrieve/{doc_id}
│   ├── POST /knowledge/ingest
│   ├── GET /health
│   └── GET /metrics
├── Request Pipeline
│   ├── Input validation (Pydantic)
│   ├── Session lookup (Redis)
│   ├── Vector search (Qdrant)
│   ├── Semantic ranking
│   └── Response formatting
└── Error Handling
    ├── Graceful degradation
    ├── Fallback search paths
    └── Structured error responses
```

### 7. User Interface
**Service:** Chainlit UI
**Role:** Multi-modal chat interface
**Responsibilities:**
- Real-time chat with streaming responses
- Voice interface integration (optional)
- Session persistence
- Message history management
- File upload and processing

```
Chainlit UI (Port 8501)
├── Frontend
│   ├── React-based chat interface
│   ├── WebSocket connection to API
│   ├── Message streaming
│   └── File upload handlers
├── Backend
│   ├── Session manager
│   ├── Message processing pipeline
│   └── Redis persistence
└── Features
    ├── Real-time typing indicators
    ├── Message history
    ├── File attachment support
    └── Voice interface (optional)
```

### 8. Content Ingestion Pipeline
**Service:** Crawler
**Role:** Extract and normalize external content
**Responsibilities:**
- Web scraping with rate limiting
- Document format normalization
- Metadata extraction
- Quality filtering

**Service:** Curation Worker
**Role:** Intelligent content processing
**Responsibilities:**
- Dynamic chunking strategy selection
- Duplicate content detection
- Domain classification
- Quality scoring and filtering

```
Ingestion Pipeline
├── Source Detection
│   ├── Web URLs
│   ├── Local files
│   ├── API feeds
│   └── Database exports
├── Normalization
│   ├── Format conversion (PDF, HTML, DOCX, MD, etc.)
│   ├── Encoding detection
│   ├── Layout preservation
│   └── Metadata extraction
├── Chunking
│   ├── Semantic boundaries (paragraphs, sentences)
│   ├── Token limit respect (512-1024 tokens)
│   ├── Overlap strategy (sliding windows)
│   └── Positional tracking
├── Deduplication
│   ├── Content hash comparison
│   ├── Semantic similarity detection
│   └── URL-based deduplication
└── Quality Scoring
    ├── Readability metrics
    ├── Content freshness
    ├── Source reputation
    └── Language detection
```

### 9. Monitoring & Analytics
**Service:** Grafana
**Role:** Metrics visualization and alerting
**Responsibilities:**
- Real-time dashboard creation
- Alert rule management
- Historical metrics analysis
- Multi-datasource support

```
Grafana (Port 3000)
├── Data Sources
│   ├── VictoriaMetrics (metrics)
│   ├── PostgreSQL (custom queries)
│   └── Consul (service health)
├── Dashboards
│   ├── Service Health Overview
│   ├── Performance Metrics
│   ├── Database Activity
│   ├── Cache Hit Rates
│   └── Vector Search Latency
└── Alert Rules
    ├── High error rates
    ├── Connection pool exhaustion
    ├── Redis memory pressure
    ├── Query latency p99 > threshold
    └── Service unavailability
```

### 10. LLM Optimization Layer
**Service:** OpenPipe
**Role:** Intelligent request caching and circuit breaking
**Responsibilities:**
- Request deduplication (50-60% hit rate typical)
- Intelligent response caching
- Circuit breakers for external APIs
- Cost tracking and optimization
- Zero-telemetry sovereign mode

```
OpenPipe (Port 3001)
├── Caching
│   ├── 5-min TTL (configurable)
│   ├── Semantic deduplication
│   ├── Request normalization
│   └── Redis-backed persistence
├── Circuit Breakers
│   ├── Error threshold: 5 consecutive failures
│   ├── Recovery: exponential backoff
│   ├── Fallback: local model inference
│   └── Metrics: failure tracking
└── Optimization
    ├── Request compression
    ├── Batch processing
    ├── Model selection optimization
    └── Cost tracking
```

---

## Data Flow: Query Processing

### Request Path (Query Processing)

```
┌──────────────────────────────────────────────────────────┐
│ 1. User Query (Chainlit UI / REST Client)                 │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 2. RAG API Receives Request                               │
│    - Validate input (Pydantic schema)                     │
│    - Extract session context                             │
│    - Normalize query text                                │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 3. Session Lookup (Redis)                                 │
│    - Check session existence                             │
│    - Verify authentication                               │
│    - Retrieve conversation context                       │
│    - Fallback: in-memory if Redis unavailable            │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 4. Query Cache Check (Redis)                              │
│    - Compute query hash                                  │
│    - Check cache hit                                     │
│    - If hit: return cached results                       │
│    - If miss: proceed to semantic search                 │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 5. Semantic Search (Qdrant)                               │
│    - Embed query using FastEmbed                         │
│    - Vector search: k-NN + filtering                     │
│    - Retrieval: top-k similar chunks (configurable)      │
│    - Score normalization (0-1 range)                     │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 6. Result Enrichment (PostgreSQL)                         │
│    - Fetch full documents and chunks                     │
│    - Retrieve domain context                             │
│    - Apply access control filters                        │
│    - Score aggregation                                   │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 7. Response Ranking                                       │
│    - Multi-factor scoring:                               │
│      • Semantic similarity (Qdrant score: 70%)           │
│      • Recency (document age: 15%)                       │
│      • Authority (domain reputation: 15%)                │
│    - Deduplication (exact + near-duplicates)             │
│    - Top-K selection (default: 10)                       │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 8. Cache Storage (Redis)                                  │
│    - Store results with query hash                       │
│    - Set TTL: 5 minutes (configurable)                   │
│    - Track cache hit metrics                             │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 9. Response Formatting                                    │
│    - Serialize to JSON                                   │
│    - Include metadata and scores                         │
│    - Add trace IDs for debugging                         │
│    - Include performance metrics                         │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 10. Audit Logging (PostgreSQL)                            │
│     - Log query execution                                │
│     - Record user session                                │
│     - Store query and result counts                      │
│     - Track response time                                │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 11. Response Delivery                                     │
│     - Stream to client (WebSocket / HTTP)                │
│     - Include performance metrics                        │
│     - Signal completion                                  │
└──────────────────────────────────────────────────────────┘
```

### Ingestion Path (Document Processing)

```
┌──────────────────────────────────────────────────────────┐
│ 1. Content Source                                         │
│    - Web URLs / Files / API Feeds                         │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 2. Crawler Service                                        │
│    - Download/fetch content                              │
│    - Extract metadata                                    │
│    - Normalize format                                    │
│    - Rate limiting enforcement                           │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 3. Content Storage (PostgreSQL)                           │
│    - Insert document record                              │
│    - Compute content hash                                │
│    - Store raw content                                   │
│    - Set initial status: 'processing'                    │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 4. Curation Worker Processes                              │
│    - Poll documents with 'processing' status             │
│    - Deduplication check (content hash)                  │
│    - Quality scoring                                     │
│    - Domain classification                               │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 5. Intelligent Chunking                                   │
│    - Analyze document structure                          │
│    - Select chunking strategy:                           │
│      • Semantic: paragraph boundaries                    │
│      • Hybrid: size + semantic                           │
│      • Fixed: size-based (fallback)                      │
│    - Create chunks with overlap                          │
│    - Track token counts (BPE tokenizer)                  │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 6. Embedding Generation                                   │
│    - Generate embeddings for chunks:                     │
│      • FastEmbed (384-dim, local, fast)                  │
│      • Optional: Ancient-BERT (768-dim)                  │
│    - Normalize embedding vectors (L2)                    │
│    - Store metadata in PostgreSQL                        │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 7. Vector Indexing (Qdrant)                               │
│    - Upload vectors to appropriate collection             │
│    - Attach metadata payloads                            │
│    - Build HNSW indices                                  │
│    - Quantize for memory efficiency                      │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 8. Metadata Updates (PostgreSQL)                          │
│    - Update document status: 'active'                    │
│    - Set chunk_count                                     │
│    - Record embedding_ids in embedding table             │
│    - Update indexed_at timestamp                         │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 9. Event Publishing (Redis Streams)                       │
│    - Publish to: xnai:events:document:indexed            │
│    - Payload: document_id, chunk_count, model_type       │
│    - Subscribers: cache invalidators, analytics          │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┘
│ 10. Ingestion Complete                                    │
│     - Visible in semantic search                         │
│     - Available for queries                              │
└──────────────────────────────────────────────────────────┘
```

---

## Failure Scenarios & Fallback Flows

### Scenario 1: PostgreSQL Connection Failure

**Impact:** Core database unavailable
**Symptoms:** Query timeouts, document storage failures

**Fallback Flow:**

```
┌─ Query Request
│
├─ Try: PostgreSQL (primary)
│  └─ FAIL: Connection refused / timeout
│
├─ Fallback 1: Cached Query Results (Redis)
│  ├─ Check query hash in Redis cache
│  ├─ If hit: Return cached results
│  │  └─ Valid for 5 minutes
│  └─ If miss: Continue to Fallback 2
│
├─ Fallback 2: Vector-Only Search (Qdrant)
│  ├─ Perform semantic search directly
│  ├─ Return results with limited metadata
│  ├─ Cache results to Redis
│  └─ Notify: "Using degraded mode (limited metadata)"
│
└─ If all fail: Return error with retry guidance
   └─ Alert: PostgreSQL unavailability
```

**Actions:**
1. Alert OPS team
2. Check PostgreSQL health: `docker-compose logs postgres`
3. Verify network connectivity: `docker-compose exec postgres pg_isready`
4. Check disk space: `docker exec xnai_postgres du -sh /var/lib/postgresql/data`
5. Restart if needed: `docker-compose restart postgres`

---

### Scenario 2: Redis Connection Failure

**Impact:** Session loss, cache unavailable
**Symptoms:** Session timeouts, slower query performance

**Fallback Flow:**

```
┌─ Query Request
│
├─ Try: Redis (session + cache)
│  └─ FAIL: Connection refused / timeout
│
├─ Fallback 1: In-Memory Session Cache
│  ├─ Store sessions in application memory
│  ├─ Bounded to 100 sessions (configurable)
│  ├─ LRU eviction on overflow
│  └─ Lost on API restart
│
├─ Fallback 2: Query Execution Only
│  ├─ Skip cache lookup
│  ├─ Execute semantic search (Qdrant)
│  ├─ Fetch results from PostgreSQL
│  └─ Cache in in-memory (volatile)
│
└─ Notify: "Session state unavailable (using volatile storage)"
   └─ Alert: Redis unavailability
```

**Actions:**
1. Alert OPS team
2. Check Redis health: `docker-compose logs redis`
3. Check Redis memory: `redis-cli info memory`
4. Flush Redis if corrupted: `redis-cli flushall` (WARNING: loses all cache)
5. Restart if needed: `docker-compose restart redis`

---

### Scenario 3: Qdrant Connection Failure

**Impact:** Semantic search unavailable
**Symptoms:** All vector search fails, query results empty

**Fallback Flow:**

```
┌─ Query Request
│
├─ Try: Qdrant (vector search)
│  └─ FAIL: Connection refused / timeout
│
├─ Fallback 1: Full-Text Search (PostgreSQL)
│  ├─ Execute FTS on PostgreSQL tsvector index
│  ├─ Results ranked by BM25 (PostgreSQL default)
│  ├─ Return top matches by relevance
│  └─ Quality: 40-60% of semantic search
│
├─ Fallback 2: Keyword Search (PostgreSQL)
│  ├─ Execute simple LIKE/ILIKE queries
│  ├─ Results ranked by string distance
│  └─ Quality: 20-30% of semantic search
│
└─ Notify: "Using keyword search (limited semantic understanding)"
   └─ Alert: Qdrant unavailability
```

**Actions:**
1. Alert OPS team
2. Check Qdrant health: `docker-compose logs qdrant`
3. Check Qdrant disk space: `docker exec xnai_qdrant df -h /qdrant/storage`
4. Check collection status: `curl http://localhost:6333/collections`
5. Rebuild collections if corrupted: See Qdrant Troubleshooting section

---

## Network Architecture

### Internal Network Topology

```
┌─────────────────────────────────────────────────────┐
│              xnai_network (Docker Bridge)            │
│                                                      │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐    │
│  │Consul  │──│PostgreSQL│ │Redis   │  │Qdrant  │    │
│  │8500 UI │  │5432 TCP  │ │6379 TCP│  │6333 API│    │
│  └────────┘  └────────┘  └────────┘  └────────┘    │
│      │           │           │          │           │
│      └───────────┼───────────┼──────────┘           │
│                  │           │                       │
│  ┌────────┐      │           │      ┌────────┐     │
│  │RAG API ├──────┼───────────┼──────│VMetrics│    │
│  │8000    │      │           │      │8428    │     │
│  └────────┘      │           │      └────────┘     │
│      │           │           │           │          │
│      └───────────┼───────────┼───────────┘          │
│                  │           │                       │
│  ┌────────────────────────────────────┐            │
│  │   Chainlit UI / Crawler / Workers   │            │
│  │   (All internal Docker hosts)       │            │
│  └────────────────────────────────────┘            │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### External Access Points

```
┌──────────────────────────────────┐
│   Host Machine (AMD Ryzen)        │
│                                    │
│  Ports:                            │
│  ├─ 8500 ─→ Consul UI             │
│  ├─ 8000 ─→ RAG API               │
│  ├─ 8501 ─→ Chainlit UI           │
│  ├─ 6333 ─→ Qdrant API            │
│  ├─ 5432 ─→ PostgreSQL            │
│  ├─ 6379 ─→ Redis                │
│  ├─ 8428 ─→ VMetrics             │
│  ├─ 3000 ─→ Grafana UI           │
│  └─ 8080 ─→ Caddy (reverse proxy)│
│                                    │
│  localhost:8080 ──→               │
│       ├─ /ui ──→ Chainlit         │
│       ├─ /api ──→ RAG API         │
│       ├─ /qdrant ──→ Qdrant       │
│       └─ /console ──→ Consul      │
└──────────────────────────────────┘
```

### DNS Resolution (Consul)

Services can be referenced by DNS name in the docker network:

```
postgres.service.consul:5432
redis.service.consul:6379
qdrant.service.consul:6333
xnai_rag_api.service.consul:8000
victoriametrics.service.consul:8428
```

**Usage Example (from inside container):**
```bash
curl http://xnai_rag_api.service.consul:8000/health
```

---

## Security Architecture

### Zero-Trust Principles

1. **Network Isolation**
   - All services in isolated Docker network
   - No direct access from external networks
   - Firewall rules: Deny all, Allow only necessary ports

2. **Authentication & Authorization**
   - API: Bearer token (JWT) required for all requests
   - PostgreSQL: Username/password (no anonymous access)
   - Redis: Password required (REDIS_PASSWORD env var)
   - Qdrant: Read-only API (no authentication in Phase 1)

3. **Data Encryption**
   - PostgreSQL: Enable SSL in production
   - Redis: Use AUTH + SSL in production
   - Network: All inter-service traffic unencrypted (isolated network)
   - At-rest: PostgreSQL native encryption recommended

4. **Audit & Compliance**
   - PostgreSQL audit_log table: All operations recorded
   - API request logging: trace_id + span_id in all logs
   - Immutable audit log (append-only semantics)
   - GDPR-compliant: Data retention policies enforced

---

## Performance Characteristics

### Latency SLOs

| Operation | P50 | P95 | P99 |
|-----------|-----|-----|-----|
| Query (cache hit) | 10ms | 30ms | 50ms |
| Query (semantic search) | 150ms | 300ms | 500ms |
| Document ingestion | 2s | 5s | 10s |
| Vector indexing | 500ms | 1s | 2s |

### Throughput Targets

- API: 100 req/s sustained (with 10s spike to 500 req/s)
- PostgreSQL: 1000 query/s
- Redis: 10000 op/s
- Qdrant: 500 search/s

### Resource Utilization

- PostgreSQL: 512MB-2GB (configurable)
- Redis: 512MB max
- Qdrant: 2GB max (configurable)
- API: 512MB typical, 1GB under load
- Total stack: ~5-6GB with headroom

---

## Next Steps

1. **Connection Guide** → See `02-connection-guide.md`
2. **Database Schema** → See `03-database-schema.md`
3. **Troubleshooting** → See `04-troubleshooting.md`
4. **Operational Runbooks** → See `05-operational-runbooks.md`
5. **Performance Tuning** → See `06-performance-tuning.md`

---

**Document Version:** 1.0
**Last Updated:** 2026-02-25
**Status:** Active
**Audience:** DevOps, SRE, Infrastructure Engineers, Platform Teams
