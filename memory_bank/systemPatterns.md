---
block:
  label: system_patterns
  description: Architecture patterns, design decisions, code standards, and system design principles
  chars_limit: 8000
  read_only: false
  tier: core
  priority: 3
created: 2026-02-20
modified: 2026-02-20
version: "1.0"
---

# System Patterns - Xoe-NovAi Foundation Stack

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Client Layer                      │
│  (Web UI, Voice, CLI, Mobile)                       │
└────────────┬────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────┐
│              Caddy Reverse Proxy (8000)              │
│  - Request routing                                   │
│  - TLS termination                                   │
│  - Rate limiting                                     │
│  - Metrics aggregation                               │
└────────────┬────────────────────────────────────────┘
             │
    ┌────────┼────────┬──────────┐
    │        │        │          │
┌───▼──┐ ┌──▼──┐ ┌──▼──┐ ┌───▼──┐
│ RAG  │ │ CLI │ │Voice│ │ Docs │
│ API  │ │ App │ │ API │ │Server│
└───┬──┘ └──┬──┘ └──┬──┘ └───┬──┘
    │       │       │        │
    └───────┼───────┼────────┘
            │       │
    ┌───────▼───────▼────────────┐
    │   Circuit Breaker Layer     │
    │ - State persistence (Redis) │
    │ - Health monitoring         │
    │ - Graceful degradation      │
    └───────┬───────┬────────────┘
            │       │
    ┌───────▼──┐ ┌──▼──────┐
    │  Redis   │ │Postgres │
    │ (Cache)  │ │(Primary)│
    └──────────┘ └─────────┘
```

## Service Orchestration

| Principle | Implementation |
|-----------|----------------|
| Service Order | Dependencies initialized in sequence |
| Graceful Startup | Health checks before serving traffic |
| Graceful Shutdown | Cleanup before termination |
| Dependency Injection | Runtime configuration binding |
| Circuit Breakers | Per-service failure isolation |

## Design Patterns

### 1. Circuit Breaker Pattern

**Purpose**: Prevent cascading failures

| Aspect | Implementation |
|--------|----------------|
| State Machine | Redis-backed with in-memory fallback |
| States | CLOSED → OPEN → HALF_OPEN → CLOSED |
| Metrics | Request count, error rate, latency percentiles |
| Recovery | Automatic with configurable thresholds |

### 2. Health Monitoring Pattern

**Purpose**: Detect failures, trigger recovery

| Aspect | Implementation |
|--------|----------------|
| Checkers | Multi-service with configurable intervals |
| Recovery Actions | Service restart, cache clearing, DB reconnection |
| Alert Routes | Logging, metrics, email (extensible) |
| GPU Monitoring | pynvml-based (torch-free) |

### 3. Graceful Degradation Pattern

**Purpose**: Continue serving when services fail

| Strategy | Description |
|----------|-------------|
| Fallback | Use default response |
| Cache-First | Serve stale data if available |
| Degraded Mode | Limited functionality |
| Configuration | Per-endpoint degradation rules |

### 4. Error Handling Chain

**Purpose**: Consistent error responses across all APIs

| Aspect | Implementation |
|--------|----------------|
| Base Class | XNAiException with category mapping |
| Categories | 19 error types → HTTP status codes |
| Context | Request ID correlation for tracing |

### 5. Async Safety Pattern

**Purpose**: Thread-safe initialization and state management

| Aspect | Implementation |
|--------|----------------|
| Runtime | AnyIO (not asyncio) per AGENTS.md |
| Locking | AsyncLock with double-check pattern |
| Use Cases | LLM init, service startup, state updates |

### 6. Redis Resilience Pattern

**Purpose**: Handle Redis unavailability gracefully

| Aspect | Implementation |
|--------|----------------|
| Primary | Redis for distributed state |
| Fallback | In-memory for circuit breaker state |
| Sync | Periodic re-sync when Redis recovers |

## Code Standards

### Async Runtime
- **Use AnyIO** - Never asyncio.gather, use TaskGroups
- **Cancellation** - Use `anyio.get_cancelled_exc_class()`
- **Sleep** - Use `anyio.sleep()`, not `asyncio.sleep()`

### Torch-Free Mandate
- **No PyTorch** - Use ONNX, GGUF, Vulkan, pynvml
- **GPU Monitoring** - pynvml for memory stats

### Container Security
- **Rootless** - Services run as UID 1001
- **Read-Only** - Immutable runtime filesystem
- **No New Privileges** - CAP_DROP all

## Ecosystem Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      ARCANA-NOVA STACK                           │
│              (Esoteric Consciousness Layer)                      │
│  • 10 Pillars • Dual Flame • Pantheon Model • 42 Ideals         │
│  • SEPARATE REPOSITORY - Built ON TOP OF Foundation             │
└───────────────────────────────┬─────────────────────────────────┘
                                │ Depends On
┌───────────────────────────────▼─────────────────────────────────┐
│                    XNAi FOUNDATION STACK                         │
│                (Sovereign AI Infrastructure)                     │
│  • RAG Engine • Voice Interface • Security Trinity               │
│  • Multi-Agent Orchestration • Vikunja PM Hub                    │
│  • THIS REPOSITORY - Clean technical foundation                  │
└───────────────────────────────┬─────────────────────────────────┘
                                │ Sync Layer
┌───────────────────────────────▼─────────────────────────────────┐
│                       xoe-novai-sync                             │
│                  (External AI Context Hub)                       │
│  • Context packs for Grok/Claude/Gemini • EKB exports            │
└─────────────────────────────────────────────────────────────────┘
```

## Related Documents

- `techContext.md` - Technology choices
- `AGENTS.md` - Agent rules and constraints
- `OPERATIONS.md` - Operational procedures

---
**Last Updated**: 2026-02-20
**Owner**: Architect
