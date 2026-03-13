# OpenPipe Optimization & LLM Gateway (XNAi Foundation)

**Status**: 🟢 CURRENT  
**Last Updated**: 2026-02-28  
**Owner**: MC-Overseer  
**Domain**: Infrastructure

---

## Overview

In the XNAi Foundation stack, **OpenPipe** (v2.0+) serves as the intelligent LLM Gateway. It provides response caching, request deduplication, enhanced observability, and advanced circuit breaker patterns. In **Sovereign Mode**, it ensures zero telemetry and air-gap capability while delivering 40-60% performance gains.

---

## 🚀 Key Features & Benefits

| Feature | Impact | Benefit |
|---------|--------|---------|
| **Response Caching** | <300ms latency | 60-80% reduction in average response time |
| **Request Deduplication** | 25-40% cost reduction | Prevents redundant parallel LLM calls |
| **Sovereign Mode** | Privacy & Security | Zero external data leakage |
| **Circuit Breakers** | 99.5% Availability | Graceful fallback during provider degradation |
| **Memory Management** | 30-50% RAM reduction | Optimized routing for the 6GB Ryzen constraint |

---

## 🛠 Tuning for XNAi Stack

### 1. Caching Strategy (ShadowCache)
OpenPipe integrates with the `ShadowCacheManager` (FAISS + Redis) to provide multi-tier caching.
- **Semantic Threshold**: 0.95 (matches FAISS similarity)
- **Task-Specific TTLs**:
    - `code_generation`: 600s (Stable patterns)
    - `research`: 300s (Evolving topics)
    - `daily_coding`: 900s (Common utility patterns)

### 2. Request Deduplication
To prevent "Double-Tap" requests from UI interactions or agent loops:
- **Deduplication Window**: 60 seconds.
- **Mechanism**: Redis-based locking (`NX` flag) with a 60s expiry.

### 3. Circuit Breaker Integration
OpenPipe wraps existing `CircuitBreakerProxy` instances to provide "Cache-as-Fallback":
- **Closed**: Normal flow with cache check.
- **Open**: Immediate fallback to most recent similar cached response.
- **Half-Open**: Gradual recovery with 10% traffic sampling.

---

## 📈 Operational Workflows

### 1. Monitoring & Metrics
OpenPipe provides a real-time dashboard for LLM performance:
- **UI Access**: [http://localhost:3001](http://localhost:3001)
- **Top Queries**: Identify memory-heavy or high-latency prompts.
- **Cost Tracking**: Monitor daily spend across Gemini, Copilot, and OpenRouter.

### 2. A/B Testing Prompts
Use OpenPipe to test prompt variants (e.g., "Generate code" vs "Write a function"):
- **Selection**: Multi-armed bandit algorithm.
- **Goal**: Optimize for response quality and token efficiency.

### 3. Health Checks
```bash
wget -q --spider http://localhost:3000/health
```

---

## ⚠️ Known Issues & Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| Stale Cache | TTL too long for dynamic data | Reduce `CACHE_TTL` or use task-specific overrides. |
| Deduplication Lag | Redis latency | Ensure Redis is on the same network/host as OpenPipe. |
| Memory Pressure | Large cache in Redis | Monitor `maxmemory` and eviction policy in `redis.conf`. |

---

## 📚 References
- [OpenPipe Integration Blueprint](OpenPipe_Integration_Blueprint.md)
- [OpenPipe Research Report](OpenPipe_Integration_Research_Report.md)
- [XNAi Infrastructure Strategy](memory_bank/strategies/production-tight-stack/PLAN-PRODUCTION-TIGHT-STACK.md)
