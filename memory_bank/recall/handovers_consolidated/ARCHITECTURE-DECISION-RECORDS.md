---
title: Architecture Decision Records (ADRs)
author: Copilot CLI (Strategic Design)
date: 2026-02-25T23:59:00Z
version: 1.0
token_cost: 1500
---

# 📋 ARCHITECTURE DECISION RECORDS (ADRs)

**Purpose**: Document the "why" behind each strategic architecture choice  
**Audience**: Opus 4.6, future maintainers, design review  
**Token cost**: 1,500 tokens (read once, reference as needed)

---

## ADR-001: Plugin Architecture Over Monolith

### Status
✅ ACCEPTED (Wave 4, Phase 1)

### Context
The XNAi Foundation stack has 10+ services (voice, dispatch, knowledge, session, health, etc.) that need to be independently deployable, testable, and scalable.

### Decision
Adopt plugin architecture where:
- Each service implements `PortableService` base class
- Services can be enabled/disabled via feature flags
- Services have well-defined interfaces (FastAPI endpoints)
- Services can fail independently without cascading failures

### Rationale
- **Scalability**: Scale individual services based on demand
- **Testability**: Test each service in isolation
- **Resilience**: Service failure doesn't crash entire stack
- **Deployment**: Zero-downtime deployments per service
- **Team autonomy**: Teams can own individual services

### Consequences
- **Good**: Enables blue-green deployments, graceful degradation
- **Bad**: More complex to setup initially (Phase 1 effort)
- **Mitigation**: PortableService base class reduces complexity

### Alternatives Considered
1. **Monolith**: Single app with all services
   - Pros: Simpler initially
   - Cons: Can't scale individual services, deployments block all teams
2. **Microservices**: Full microservices architecture
   - Pros: Maximum isolation
   - Cons: Network latency, operational complexity

### Decision
**CHOSE**: Plugin architecture (middle ground between monolith and microservices)

---

## ADR-002: ONNX Runtime Over PyTorch

### Status
✅ ACCEPTED (Zero-Telemetry Mandate)

### Context
Foundation stack needs local inference without external API calls. Options: PyTorch, ONNX Runtime, or CTranslate2.

### Decision
Use ONNX Runtime for background inference (research jobs, curation, maintenance).

### Rationale
- **Torch-free mandate**: Zero PyTorch, CUDA, or Triton imports
- **Memory efficient**: <6GB RAM target (vs. PyTorch 16GB+)
- **Vulkan support**: Works with AMD RADV on current hardware
- **Zero-telemetry**: Runs completely locally, no external APIs

### Consequences
- **Good**: Complies with mandate, lower memory footprint
- **Bad**: Limited model selection (must be ONNX format)
- **Mitigation**: Curate model library, convert as needed

### Alternatives Considered
1. **PyTorch**: Larger ecosystem, more models
   - Pros: More models available
   - Cons: Violates torch-free mandate, 16GB+ RAM
2. **CTranslate2**: Optimized for inference
   - Pros: Fast inference
   - Cons: Specialized for language models only

### Decision
**CHOSE**: ONNX Runtime (complies with mandate, efficient)

---

## ADR-003: Multi-Tier Database (PostgreSQL + Redis + Qdrant)

### Status
✅ ACCEPTED (Wave 4, Phase 2)

### Context
Stack needs to handle:
- ACID transactions (credentials, session state)
- Sub-millisecond caching (provider quotas)
- Vector search (semantic knowledge retrieval)

### Decision
Use 3-tier database:
- **PostgreSQL**: Primary ACID store (credentials, sessions, audit logs)
- **Redis**: In-memory cache (quotas, feature flags, rate limits)
- **Qdrant**: Vector database (semantic search on knowledge base)

### Rationale
- **Reliability**: Each tier has single responsibility
- **Performance**: Cascading fallback (Qdrant down? Use PostgreSQL full-text search)
- **Scalability**: Each tier scales independently
- **Resilience**: Redis down? Use local cache. Qdrant down? Use keyword search.

### Consequences
- **Good**: Robust, performant, resilient
- **Bad**: More operational complexity (3 systems to manage)
- **Mitigation**: Degradation handlers built into each service

### Alternatives Considered
1. **Single database (PostgreSQL only)**:
   - Pros: Simpler
   - Cons: Can't do sub-ms caching, no vector search
2. **Document database (MongoDB)**:
   - Pros: Schema-less
   - Cons: No ACID transactions (we need them for credentials)

### Decision
**CHOSE**: Multi-tier (PostgreSQL + Redis + Qdrant)

---

## ADR-004: 24/7 Background ONNX Model Over Event-Driven

### Status
✅ ACCEPTED (Wave 5, Phase 4)

### Context
Stack needs to continuously:
- Execute research jobs (RQ-161 through RQ-168)
- Curate documents (generate embeddings, tags)
- Maintain indices (Qdrant optimization, cleanup)

### Decision
Always-on ONNX model that:
- Starts on app boot
- Runs continuously in background
- Processes job queue from database
- Resource-limited: <6GB RAM, 50% CPU quota

### Rationale
- **Knowledge**: Continuous curation improves stack knowledge
- **Efficiency**: Batch processing more efficient than per-request
- **Research**: Can execute long-running research jobs without blocking users
- **Maintenance**: Stack self-optimizes (defragment indices, cleanup logs)

### Consequences
- **Good**: Stack improves continuously, research jobs execute
- **Bad**: Additional resource consumption (6GB RAM)
- **Mitigation**: Resource-limited with circuit breakers

### Alternatives Considered
1. **Event-driven (Lambda-style)**:
   - Pros: Minimal resources
   - Cons: Cold start delays, can't do long-running jobs
2. **Scheduled jobs only (cron)**:
   - Pros: Simple to understand
   - Cons: Can't respond to ad-hoc research requests

### Decision
**CHOSE**: 24/7 background ONNX model (continuous improvement + research execution)

---

## ADR-005: Blue-Green Deployments Over Canary

### Status
✅ ACCEPTED (Wave 4, Phase 2)

### Context
Stack needs zero-downtime deployments with instant rollback capability.

### Decision
Use blue-green deployments:
- **BLUE**: Current production environment
- **GREEN**: New production environment
- **Switch**: Instant switchover <30s
- **Rollback**: Instant rollback <30s if issues detected

### Rationale
- **Zero downtime**: Instant switch, no gradual rollout
- **Fast rollback**: Issues? Switch back immediately
- **Testable**: Can fully test GREEN before switch
- **Clear state**: Always know which version is live

### Consequences
- **Good**: Fast rollback, zero downtime, instant switch
- **Bad**: Requires duplicate infrastructure (cost 2x infrastructure)
- **Mitigation**: Can share persistent storage (PostgreSQL, Redis, Qdrant)

### Alternatives Considered
1. **Canary deployments**:
   - Pros: Gradual rollout catches issues slowly
   - Cons: Complex orchestration, slower issue detection
2. **Rolling deployments**:
   - Pros: Saves infrastructure cost
   - Cons: Slower rollback, more complex state management

### Decision
**CHOSE**: Blue-green deployments (instant rollback, zero downtime)

---

## Summary Table

| ADR | Decision | Rationale | Trade-off |
|-----|----------|-----------|-----------|
| ADR-001 | Plugin architecture | Scalability, resilience | Complex setup |
| ADR-002 | ONNX Runtime | Mandate compliance, efficient | Limited models |
| ADR-003 | Multi-tier database | Robust, resilient, scalable | Operational complexity |
| ADR-004 | 24/7 background model | Continuous improvement | 6GB RAM consumption |
| ADR-005 | Blue-green deployments | Zero downtime, fast rollback | Double infrastructure cost |

---

## How to Use These ADRs

1. **Design Review**: Reference ADRs when proposing changes
2. **Onboarding**: Share with new team members to understand strategy
3. **Decision Making**: Use ADR format when making new architecture decisions
4. **Trade-offs**: Explicitly document what we're trading off

---

**Document**: ARCHITECTURE-DECISION-RECORDS.md  
**Purpose**: Strategic design rationale  
**Token cost**: 1,500 (this file)  
**Status**: ✅ Ready for reference
