---
title: "Phase 4.2 Scouting Report: Sovereign Trinity Hardening"
last_updated: 2026-02-15T03:00:00Z
status: in-progress
persona_focus: [ops-lead, infrastructure-architect]
phase: "4.2"
---

# Phase 4.2 Scouting Report: Sovereign Trinity Hardening

**Objective:** Preliminary research and knowledge gap identification for Service Discovery & Failover integration with Query Flow hardening on Ryzen 7 5700U rootless Podman infrastructure.

**Issued:** 2026-02-15  
**Version:** 1.0  
**Classification:** Internal Strategic Planning

---

## Executive Summary

The XNAi Foundation's current architecture demonstrates solid foundational patterns (circuit breakers, graceful degradation, resource steering) but lacks formal service discovery, dynamic failover, and comprehensive query flow hardening for the Sovereign Trinity system (STT → RAG → TTS pipeline).

**Key Findings:**
- ✅ **Solid:** Container-based service location, health checks, circuit breaker protection
- ⚠️ **Gaps:** No dynamic service discovery, manual failover, limited end-to-end flow instrumentation
- 🔴 **Blockers:** Service dependencies hardcoded; no runtime service registry; query flow lacks atomicity guarantees

**Recommended Phase 4.2 Focus:** Implement Consul-based service discovery with weighted failover, integrate end-to-end query flow coordination, and harden voice pipeline against 6.6GB RAM constraints.

---

## 1. Research: Consul/Eureka Integration for Rootless Podman

### 1.1 Current State Analysis

**Architecture:**
- Services deployed via `docker-compose.yml` with static DNS (container names)
- Health checks via HTTP endpoints (`/health` on RAG, circuit breaker monitoring on Redis)
- No service registry—service locations hardcoded in environment variables
- No automatic service deregistration on failures
- No metadata-based service tagging

**Existing Test Infrastructure:**
- `tests/integration/test_service_discovery.py` demonstrates Consul patterns:
  - Service registration with TTL-based health checks
  - Failover scenario testing
  - Query timeout handling with fallback routing
  - Metadata tagging (e.g., `service_version`, `region`)

### 1.2 Consul Integration Pattern for Rootless Podman

**Recommended Approach: Consul Agent + Client SDK**

#### **Why Consul over Eureka?**
| Criterion | Consul | Eureka | Winner |
|-----------|--------|--------|--------|
| Multi-protocol support | DNS, gRPC, HTTP | HTTP only | **Consul** |
| Container-native | Native Podman integration | Requires Spring | **Consul** |
| Lightweight | 100MB image, minimal deps | 300MB+ | **Consul** |
| Rootless Podman | No privilege requirements | Works fine | **Tie** |
| Failover patterns | Built-in load balancing | Manual | **Consul** |

#### **Consul Deployment Topology**

```yaml
# Consul server: runs on host or privileged container
consul-server:
  image: consul:1.18
  ports:
    - "8500:8500"    # HTTP API (for clients)
    - "8600:8600/udp" # DNS (port forwarding)
  environment:
    CONSUL_BIND_ADDR: "0.0.0.0"
    CONSUL_CLIENT_ADDR: "0.0.0.0"
  command: agent -server -ui -bootstrap-expect=1 -client=0.0.0.0
  volumes:
    - consul-data:/consul/data

# Services (RAG, Redis, UI) register via HTTP API
rag:
  environment:
    CONSUL_HOST: consul-server
    CONSUL_PORT: 8500
    SERVICE_ID: "rag-${HOSTNAME}"
    SERVICE_NAME: "rag-api"
    SERVICE_PORT: "8000"
  depends_on:
    - consul-server
```

**Service Registration Flow (Python):**
```python
# In FastAPI startup
import consul

consul_client = consul.Consul(host='consul-server', port=8500)

consul_client.agent.service.register(
    name='rag-api',
    service_id='rag-api-instance-1',
    address='rag',
    port=8000,
    check=consul.Check.http(
        'http://localhost:8000/health',
        interval='10s',
        timeout='5s',
        deregister='30s'  # Auto-deregister if 3 checks fail
    ),
    meta={'version': '4.2', 'region': 'primary'}
)
```

#### **DNS-based Service Discovery**

After registration, services accessible via:
```bash
# In containers:
curl http://rag-api.service.consul:8000/health

# Consul returns:
# {
#   "Address": "10.0.0.5",
#   "Port": 8000
# }
```

#### **Integration Points for XNAi**

| Service | Current | Phase 4.2 Approach |
|---------|---------|-------------------|
| **RAG API** | Static: `RAG_API_URL=http://rag:8000` | Dynamic: Resolve `rag-api.service.consul:8000` |
| **Redis** | Static: `REDIS_HOST=redis` | Dynamic: Resolve `redis.service.consul:6379` with weight-based selection |
| **UI** | Static: `BACKEND_URL=http://rag:8000` | Query Consul for available RAG instances, round-robin |
| **Crawler** | Hardcoded `redis` | Consul-aware with fallback to local cache |

### 1.3 Failover Scenarios for Rootless Podman

**Scenario 1: RAG API Instance Failure**

```
Time T0: RAG health check passes
  └─ Consul keeps RAG registered

Time T1: RAG crashes (OOM or unhandled exception)
  └─ /health endpoint times out

Time T2: Consul detects failure (after 3 * 10s = 30s)
  ├─ Marks RAG as "critical"
  └─ Clients stop routing to RAG

Time T3: Pod restart triggered (by Podman supervisor)
  ├─ RAG re-registers with Consul
  └─ Health checks resume

Action: UI/Client queries rerouted to alternate RAG (if multiple) or queued with circuit breaker
```

**Scenario 2: Redis Connection Loss**

```
Current (No Consul):
  └─ Circuit breaker in-memory fallback only
  └─ Lost state on process restart
  └─ No detection of Redis availability change

With Consul:
  ├─ Circuit breaker monitors Consul Redis health tag
  ├─ If Redis "critical" → disable caching, use in-memory only
  ├─ If Redis recovers → re-enable distributed state
  └─ Cross-instance state not lost
```

**Scenario 3: Network Partition (RAG ↔ Redis)**

```
Recommended Pattern:
1. RAG detects Redis timeout via Consul health checks
2. Gracefully degrade:
   ├─ Disable cache lookups
   ├─ Use local LLM in-memory circuit breaker state
   ├─ Batch query responses (queue for later sync)
3. On reconnection:
   ├─ Query Consul for Redis endpoint
   ├─ Sync cached queries from in-memory queue
   └─ Resume normal operation
```

### 1.4 Knowledge Gaps to Address in Phase 4.2

- [ ] **Consul persistence model** in rootless Podman (data durability across restarts)
- [ ] **DNS query caching** at application level (avoid Consul DNS bottleneck)
- [ ] **Multi-region failover** (if future expansion to multiple hosts)
- [ ] **Consul token management** for rootless containers (mTLS setup)

---

## 2. Failover Analysis: RAG API & Redis in 6.6GB RAM

### 2.1 Current Memory Allocation

**System Resource Budget:**

| Component | Memory | CPU | Status |
|-----------|--------|-----|--------|
| **Host OS + systemd** | ~800MB | 0.2 | Overhead |
| **Podman daemon** | ~200MB | 0.1 | Runtime |
| **Redis container** | 512MB | 0.5 | Hard limit |
| **RAG API container** | 4GB | 2.0 | Hard limit |
| **UI (Chainlit) container** | 2GB | 1.0 | Hard limit |
| **Crawler worker** | 2GB | 1.0 | Hard limit |
| **Curation worker** | 1GB | 0.5 | Hard limit |
| **Other services** | 512MB | 0.6 | mkdocs, caddy, etc. |
| **Buffer / Thermal headroom** | ~500MB | – | Safety margin |
| **TOTAL** | ~11GB | 6.3 | System at ~95% capacity |

**Actual host available:** 6.6GB (with zRAM and tmpfs)

### 2.2 Failover Triggers Under Memory Pressure

**Scenario A: RAG OOM (Out of Memory)**

```
Condition: RAG at 4GB limit, new query requires 200MB context
├─ Python OOM killer triggers
├─ Process killed (SIGKILL)
└─ Container enters "Exited" state

Detection:
├─ Consul health check fails (HTTP timeout)
└─ After 3 checks (30s) → marked "critical"

Response:
├─ Circuit breaker rejects new queries → 503 Service Unavailable
├─ Podman supervisor restarts container
├─ RAG re-registers after 90s startup
└─ Requests resume (or queue if timeout-configured)
```

**Scenario B: Redis Memory Pressure (512MB allocated)**

```
Condition: Circuit breaker states + LRU cache filling Redis
├─ Redis reaches 512MB limit
├─ LRU eviction kicks in (allkeys-lru policy)
└─ Oldest cache entries + circuit breaker state discarded

Side Effect:
├─ Loss of circuit breaker persistence
├─ Cache misses increase (more LLM calls)
└─ Token rate drops (inference backpressure)

Detection:
├─ Prometheus metric: redis_memory_used_bytes
├─ Application logs: "Cache miss ratio > 0.5"

Mitigation:
├─ Reduce cache TTL from 3600s → 600s
├─ Disable circuit breaker Redis persistence → in-memory only
├─ Trigger query rate limiting
```

### 2.3 Failover Strategy: Tiered Degradation

**Tier 1 (Normal):** 5.5GB available
- Redis: Full cache + distributed circuit breaker state
- RAG: Full context window + streaming enabled
- Token rate: 20 TPS target

**Tier 2 (Constrained):** 4.5GB available
- Action: Reduce RAG context window (2048 → 1024 tokens)
- Action: Disable streaming (buffer full response)
- Result: Token rate 15 TPS (acceptable)

**Tier 3 (Critical):** 3.5GB available
- Action: Minimize RAG cache (top 10% queries only)
- Action: Disable circuit breaker Redis sync
- Action: Queue long queries (defer to batch processing)
- Result: Token rate 10 TPS (degraded but operational)

**Tier 4 (Failover):** <3GB available
- Action: Reject non-priority queries (circuit open)
- Action: Redis cache offline (in-memory only)
- Action: RAG limited to cached documents only
- Result: Read-only mode (fallback to pre-computed responses)

### 2.4 Failover Coordination via Redis Streams

**Proposed Pattern: Distributed Degradation Signal**

```python
# On RAG startup:
redis_client.xadd(
    'xnai_degradation',
    {
        'source': 'rag-api',
        'tier': 1,
        'memory_available_mb': 4000,
        'timestamp': time.time()
    }
)

# Other services subscribe to stream:
async def listen_degradation_signal():
    last_id = '0'
    while True:
        messages = redis_client.xread(
            {'xnai_degradation': last_id},
            count=1,
            block=0
        )
        for stream, data in messages:
            for msg_id, msg_data in data:
                tier = int(msg_data[b'tier'])
                if tier >= 3:
                    logger.warning(f"Critical tier: reducing cache, disabling streams")
                    cache_enabled = False
                last_id = msg_id
```

**Benefits:**
- ✅ All services aware of degradation state in <100ms
- ✅ Coordinator (Redis Streams) is the degradation source (single source of truth)
- ✅ Rootless Podman compatible (no privilege escalation needed)

### 2.5 Knowledge Gaps for Phase 4.2

- [ ] **Memory profiling** of RAG at peak load (max context, concurrent queries)
- [ ] **Redis eviction impact** on circuit breaker correctness (can we lose state safely?)
- [ ] **Container restart behavior** under OOM (immediate restart vs. backoff?)
- [ ] **Streaming response memory** efficiency (buffer sizing for 1-10 concurrent users)

---

## 3. Query Flow Bottleneck Analysis

### 3.1 End-to-End Path: STT → RAG → TTS

```
┌─────────────────────────────────────────────────────────┐
│ VOICE REQUEST FLOW (Current Architecture)               │
└─────────────────────────────────────────────────────────┘

T0: User speaks "What is the Ma'at framework?"
    └─ Audio stream captured (16kHz PCM)

T1-T2 (STT): Faster Whisper processes audio
    ├─ Quantized CTranslate2 model (CPU-only)
    ├─ Latency: 500-800ms for 5s audio
    └─ Output: "What is the Ma'at framework?"

T3-T4 (RAG Query):
    ├─ Parse command: intent="query", subject="Ma'at framework"
    ├─ [GATE 1] Circuit breaker check (Redis)
    │   └─ If OPEN: skip to TTS with "Service unavailable"
    ├─ [GATE 2] Rate limit check (10 req/min)
    │   └─ If exceeded: return error
    ├─ [GATE 3] Memory check (threshold 5.5GB)
    │   └─ If exceeded: degrade context window
    │
    ├─ FAISS semantic search (Redis cache check first)
    │   ├─ Cache hit: 50ms (Redis round-trip)
    │   └─ Cache miss: 200-400ms (FAISS + LLM embedding)
    │
    ├─ Prompt construction (2048 token limit)
    │   └─ Latency: 20ms
    │
    ├─ LLM inference (llama.cpp with GGUF quantized)
    │   ├─ Latency: 3-5s for ~100 token response (20 TPS)
    │   └─ Token generation: streaming via SSE
    │
    └─ Response: JSON with sources + tokens

T5-T6 (TTS): Piper ONNX TTS
    ├─ Input: RAG response text
    ├─ Inference: Real-time (25ms per 100 tokens at 6x speed)
    ├─ Latency: 200-500ms for typical response
    └─ Output: Audio stream (16kHz PCM)

T7: User hears response
    └─ Total latency: 1.2-2.5 seconds (STT + RAG + TTS)
```

### 3.2 Bottleneck Identification

| Bottleneck | Latency | Cause | Impact on 6.6GB |
|------------|---------|-------|-----------------|
| **LLM Inference** | 3-5s | Token generation rate (20 TPS) | High when RAM full (paging) |
| **FAISS Search** | 200-400ms | Vectorstore similarity (no GPU) | Increases with doc count (linear scaling) |
| **STT (Whisper)** | 500-800ms | Real-time factor ~1.5x (CPU) | Memory: 800MB-1GB spike during inference |
| **TTS (Piper)** | 200-500ms | Mel-spectrogram + vocoder | Memory: 300-500MB (low overhead) |
| **Redis Cache Hit** | 50ms | Network round-trip | Negligible (~1-2% of STT latency) |
| **Prompt Construction** | 20ms | Token encoding | Negligible |
| **Circuit Breaker Check** | <10ms | Redis PING + state lookup | Negligible |

**Primary Bottleneck:** **LLM Inference (3-5s)** accounts for 60-75% of total latency.

### 3.3 Flow Atomicity Issues

**Current Gaps:**

| Issue | Scenario | Consequence |
|-------|----------|-------------|
| **Incomplete Query Log** | RAG crashes after LLM response, before saving to Redis | Conversation history lost; no retry capability |
| **Cache Inconsistency** | RAG returns result but Redis write fails | Next query re-runs inference (wasted compute) |
| **Circuit Breaker State Loss** | Redis crash during critical state update | LLM called in open state (cascading failure) |
| **No Query Idempotency** | Duplicate STT results routed twice | Double-processed, potential side effects |
| **Streaming Abort** | Client disconnects mid-response stream | Tokens wasted, no cleanup |

### 3.4 Proposed Query Flow Hardening

**Pattern: Distributed Transaction Log**

```python
# Step 0: Assign transaction ID
txn_id = uuid.uuid4()  # e.g., "query-abc123"

# Step 1: Log intent (Redis Streams)
redis_client.xadd('xnai_queries', {
    'txn_id': txn_id,
    'source': 'voice',
    'text': "What is Ma'at?",
    'status': 'initiated'
})

# Step 2: Execute RAG (with circuit breaker)
try:
    result = await rag_service.query("What is Ma'at?")
except ServiceUnavailable:
    redis_client.xadd('xnai_queries', {
        'txn_id': txn_id,
        'status': 'failed',
        'error': 'rag_unavailable'
    })
    return error_response()

# Step 3: Cache result (with txn ID)
redis_client.set(
    f"query_result:{txn_id}",
    json.dumps(result),
    ex=3600,
    xx=False  # Only set if not exists (idempotence)
)

# Step 4: Mark completion
redis_client.xadd('xnai_queries', {
    'txn_id': txn_id,
    'status': 'completed',
    'tokens': result['tokens_generated'],
    'duration_ms': result['duration_ms']
})

# Step 5: Stream TTS (with abort-on-disconnect)
async with asyncio.timeout(30):
    async for chunk in tts_service.synthesize_stream(result['text']):
        try:
            await response.write(chunk)
        except ClientDisconnectError:
            redis_client.xadd('xnai_queries', {
                'txn_id': txn_id,
                'status': 'aborted',
                'reason': 'client_disconnect'
            })
            break
```

**Benefits:**
- ✅ Full traceability (audit log in Redis Streams)
- ✅ Idempotent queries (dedup on txn_id)
- ✅ Crash recovery (re-execute from last checkpoint)
- ✅ Metrics visibility (query lifecycle tracking)

### 3.5 Knowledge Gaps for Phase 4.2

- [ ] **Profiling data** on LLM inference variance (quantiles: p50, p95, p99)
- [ ] **Vectorstore scaling** behavior (latency impact at 10k, 100k, 1M documents)
- [ ] **Concurrent query limits** under memory pressure (max parallelism at 6.6GB)
- [ ] **STT + LLM + TTS overlap** opportunity (pipeline parallelization gains)

---

## 4. Preliminary Hardening Spec for Sovereign Trinity

### 4.1 Architecture Changes (Phase 4.2)

#### **Component 1: Consul Service Discovery**

**What:** Deploy Consul server + client SDK in all services

**Where:** 
- Server: Privileged host container or separate VM
- Client SDK: In RAG, UI, Crawler, Redis

**When:** Startup (before service binding)

**How:**
```yaml
# Add to docker-compose.yml
consul:
  image: consul:1.18-alpine
  ports:
    - "8500:8500"
    - "8600:8600/udp"
  command: agent -server -ui -bootstrap-expect=1 -client=0.0.0.0
  volumes:
    - consul-data:/consul/data
  networks:
    - xnai_network
```

**Success Criteria:**
- [ ] All services register within 10s of startup
- [ ] Health check failures detected within 30s
- [ ] DNS queries resolve within 50ms (median)

---

#### **Component 2: Degradation Tier Management**

**What:** Centralized memory/CPU monitoring with automatic tier transitions

**Where:** New service `degradation_monitor` (or in RAG)

**When:** Every 5 seconds (polling) or event-driven (Redis pub/sub)

**How:**

```python
class DegradationTierManager:
    """Manages resource-based failover tiers."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.current_tier = 1  # Normal
    
    async def monitor_resources(self):
        """Periodically check available memory + CPU."""
        while True:
            available_mb = self.get_available_memory()
            tier = self._select_tier(available_mb)
            
            if tier != self.current_tier:
                await self._transition_tier(tier)
                self.current_tier = tier
            
            await asyncio.sleep(5)
    
    async def _transition_tier(self, new_tier):
        """Broadcast tier change to all services."""
        self.redis.xadd('xnai_degradation', {
            'tier': new_tier,
            'timestamp': time.time(),
            'available_mb': self.get_available_memory()
        })
```

**Success Criteria:**
- [ ] Tier changes trigger within 10s of resource threshold
- [ ] All services adapt to new tier within 30s
- [ ] No query failures due to tier transitions

---

#### **Component 3: Query Transaction Log (QTL)**

**What:** Redis Streams-based audit + recovery log for all queries

**Where:** Redis (append-only stream `xnai_queries`)

**When:** Query lifecycle (initiated → executing → completed/failed)

**How:**

```python
# Middleware in FastAPI
@app.middleware("http")
async def query_transaction_middleware(request: Request, call_next):
    if request.url.path in ["/query", "/stream"]:
        txn_id = str(uuid.uuid4())
        request.state.txn_id = txn_id
        
        # Log query initiation
        await redis.xadd('xnai_queries', {
            'txn_id': txn_id,
            'path': request.url.path,
            'method': request.method,
            'status': 'initiated',
            'timestamp': time.time()
        })
        
        response = await call_next(request)
        
        # Log query completion
        await redis.xadd('xnai_queries', {
            'txn_id': txn_id,
            'status': 'completed',
            'status_code': response.status_code,
            'timestamp': time.time()
        })
        
        return response
```

**Success Criteria:**
- [ ] All queries logged with unique txn_id
- [ ] Recovery from crash using QTL within 1 minute
- [ ] No duplicate processing of same query (idempotence verified)

---

#### **Component 4: Voice Pipeline Hardening**

**What:** Enhanced STT/TTS error handling + memory-aware degradation

**Where:** `/app/XNAi_rag_app/services/voice/`

**When:** On voice request + degradation tier change

**How:**

```python
class HardenedVoiceInterface:
    """Voice pipeline with failover + tier-aware degradation."""
    
    async def process_speech(self, audio_stream, tier=1):
        """
        Process STT → RAG → TTS with tier-aware degradation.
        
        Tier 1: Full quality (streaming enabled)
        Tier 2: Buffered response (reduce memory footprint)
        Tier 3: Cached responses only
        """
        
        # Step 1: STT with tier-aware memory limit
        try:
            text = await self.stt_service.transcribe(
                audio_stream,
                memory_budget_mb=800 if tier <= 2 else 400
            )
        except MemoryError:
            return {"error": "STT failed: insufficient memory", "tier": tier}
        
        # Step 2: RAG with circuit breaker + tier
        result = await self.rag_service.query(
            text,
            tier=tier,
            use_cache=True,
            stream=True if tier <= 2 else False
        )
        
        if result is None:  # Circuit open
            return {
                "error": "RAG service unavailable",
                "fallback": "I'm temporarily unable to answer. Try again soon."
            }
        
        # Step 3: TTS with abort handling
        try:
            async for audio_chunk in self.tts_service.synthesize_stream(
                result['text'],
                speed_factor=1.5 if tier >= 3 else 1.0  # Faster TTS in critical tier
            ):
                yield audio_chunk
        except ClientDisconnectError:
            logger.info(f"Voice response aborted mid-stream")
```

**Success Criteria:**
- [ ] Voice response latency <2.5s at Tier 1
- [ ] Graceful fallback to cached responses at Tier 3
- [ ] No OOM crashes during voice processing

---

### 4.2 Monitoring & Observability (Phase 4.2)

**New Metrics to Add:**

| Metric | Type | Source | Alert Threshold |
|--------|------|--------|-----------------|
| `consul_service_health` | Gauge | Consul API | Any service not "passing" |
| `degradation_tier` | Gauge | DegradationManager | Tier > 2 (warning), Tier > 3 (critical) |
| `query_txn_log_lag` | Gauge | Redis Streams | >1000 msgs unprocessed |
| `voice_pipeline_latency_ms` | Histogram | Voice service | p95 > 3000ms |
| `rag_context_window_utilization` | Gauge | RAG API | >90% of limit |
| `redis_memory_lru_evictions` | Counter | Redis info | >10 evictions/sec |
| `circuit_breaker_state_sync_failures` | Counter | RAG API | >5 failures/min |

**Observability Improvements:**

```python
# Example: Add trace IDs to all logs + metrics

from pythonjsonlogger import jsonlogger
import logging

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(timestamp)s %(level)s %(name)s %(txn_id)s %(span_id)s %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# In FastAPI request:
@app.middleware("http")
async def add_trace_context(request: Request, call_next):
    txn_id = request.headers.get("X-Transaction-ID", str(uuid.uuid4()))
    span_id = str(uuid.uuid4())
    
    # Add to logs
    structlog.contextvars.set("txn_id", txn_id)
    structlog.contextvars.set("span_id", span_id)
    
    response = await call_next(request)
    response.headers["X-Transaction-ID"] = txn_id
    response.headers["X-Span-ID"] = span_id
    return response
```

---

### 4.3 Hardening Checklist (Phase 4.2)

**Infrastructure:**
- [ ] Deploy Consul server + integrate with all services
- [ ] Implement DegradationTierManager with Redis Streams signaling
- [ ] Add health check endpoints to Redis (via `redis-cli PING`)
- [ ] Configure Consul DNS (`:8600/udp`) for service resolution

**Application:**
- [ ] Add QueryTransactionLog middleware to RAG API
- [ ] Implement idempotent query caching (dedup on txn_id)
- [ ] Enhance voice pipeline with tier-aware degradation
- [ ] Add memory profiling to identify leak sources

**Observability:**
- [ ] Instrument Consul service registration/deregistration
- [ ] Export degradation tier as Prometheus metric
- [ ] Log all query lifecycle events (initiated, executing, completed, failed)
- [ ] Add distributed trace correlation (trace_id + span_id)

**Testing:**
- [ ] Chaos test: Kill RAG instance, verify failover via Consul
- [ ] Chaos test: Fill memory to Tier 3, verify degradation behavior
- [ ] Chaos test: Redis unavailable, verify circuit breaker fallback
- [ ] Chaos test: Voice stream abort mid-response, verify cleanup

---

## 5. Implementation Roadmap (Phase 4.2)

### **Sprint 4.2.1 (Week 1): Consul Integration**
- Deploy Consul server in docker-compose
- Integrate Python consul client library
- Service registration for RAG, Redis, UI
- DNS-based service discovery in all containers
- **Deliverable:** `docs/consul-setup.md`

### **Sprint 4.2.2 (Week 2): Degradation Tier Manager**
- Implement DegradationTierManager service
- Redis Streams signaling for tier transitions
- Update RAG + voice services to respect tier configuration
- **Deliverable:** `app/XNAi_rag_app/services/degradation_monitor.py`

### **Sprint 4.2.3 (Week 3): Query Transaction Log + Hardening**
- Add QueryTransactionLog middleware
- Implement idempotent query handling
- Enhance voice pipeline error recovery
- **Deliverable:** `internal_docs/query-transaction-log-spec.md`

### **Sprint 4.2.4 (Week 4): Observability + Testing**
- Add Prometheus metrics for Consul, degradation, queries
- Implement distributed tracing (trace_id + span_id)
- Chaos engineering tests (failover, memory pressure, network partitions)
- **Deliverable:** `tests/chaos/test_failover_scenarios.py`

---

## 6. Risk Assessment & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| **Consul network partition** | Medium | Service discovery fails | Fallback to cached service list + health checks |
| **Memory budget miscalculation** | Medium | Unexpected OOM at Tier 2+ | Empirical profiling + conservative limits |
| **Redis Streams lag** | Low | Degradation signal delayed | Use Redis pub/sub for real-time tier broadcast |
| **QTL audit log explosion** | Medium | Redis storage exhausted | Implement log rotation (keep 1 week, archive to disk) |
| **Distributed txn conflict** | Low | Duplicate query execution | UUID-based txn_id uniqueness (virtually impossible collision) |
| **Voice pipeline regression** | Medium | Latency increase from changes | Baseline benchmarking before/after (target: <2.5s) |

---

## 7. Knowledge Gaps & Open Questions

### **Consul & Rootless Podman**
- [ ] Can Consul server run unprivileged? (Check official Consul documentation)
- [ ] What's the overhead of DNS queries on Consul `:8600/udp`?
- [ ] How does Consul behave with Podman's slirp4netns networking?

### **Memory Profiling**
- [ ] Peak memory usage of RAG with max context window (2048 tokens)?
- [ ] How does FAISS memory scale with document count (10k, 100k, 1M)?
- [ ] What's the footprint of concurrent streaming responses (1, 5, 10 users)?

### **Query Flow Optimization**
- [ ] Can we parallelize STT + RAG embedding generation?
- [ ] What's the win from query result caching (hit rate at typical usage)?
- [ ] How much latency is lost in Redis round-trips vs. in-memory cache?

### **Failover Behavior**
- [ ] How long does Podman take to restart a container on OOM?
- [ ] Can we trigger graceful shutdown before OOM to clean up state?
- [ ] What's the max rate of service registration/deregistration in Consul?

---

## 8. Conclusion

**Phase 4.2: Sovereign Trinity Hardening** is feasible with Consul service discovery, degradation tier management, and query transaction logging. The 6.6GB RAM constraint is manageable with tiered degradation—normal operation at Tier 1, graceful degradation to Tier 3, and read-only fallback at Tier 4.

**Critical Success Factors:**
1. **Consul deployment** before service changes (decouple service location from container names)
2. **Empirical memory profiling** to set accurate tier thresholds
3. **Distributed transaction logging** for crash recovery and audit trails
4. **Chaos testing** to validate failover behavior under stress

**Estimated Effort:** 4-6 weeks (with parallel team work on Consul + RAG hardening)

**Next Steps:**
1. Approve this scouting report
2. Begin Sprint 4.2.1 (Consul integration)
3. Schedule architecture review with Ops team (Consul DNS performance)
4. Start empirical memory profiling of RAG workloads

---

**Report Prepared By:** Copilot CLI  
**Date:** 2026-02-15  
**Status:** Ready for team review  
**Next Review:** Upon completion of Sprint 4.2.1
