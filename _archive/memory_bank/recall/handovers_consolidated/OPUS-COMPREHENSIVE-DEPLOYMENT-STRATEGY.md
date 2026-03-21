# OPUS 4.6: COMPREHENSIVE DEPLOYMENT & STACK OPTIMIZATION STRATEGY

**Prepared for**: Opus 4.6 Model  
**Date**: 2026-02-25T22:48:25Z  
**Status**: 🟢 READY FOR HANDOVER & EXECUTION  
**Scope**: Complete stack refactoring, service harmonization, continuous background inference

---

## 📋 EXECUTIVE SUMMARY

The XNAi Foundation stack has completed comprehensive planning for:

1. **Advanced Scholarly RAG System** (56 tasks, 6 phases, currently deploying)
2. **Wave 4-5 Multi-Account Integration** (ready for Phase 3B implementation)
3. **Stack Service Harmonization** (all services cataloged, plugin architecture defined)
4. **Continuous Background Inference Model** (for research, curation, maintenance)
5. **Maximum Uptime Deployment Strategy** (rolling updates, graceful degradation)

Your role: **Prioritize, structure, and execute the complete roadmap with zero-downtime**

---

## 🏗️ PART 1: CURRENT STACK SERVICES INVENTORY

### Core Infrastructure Services

```
📦 app/XNAi_rag_app/
├─ api/                      # FastAPI endpoints (REST, WebSocket)
├─ core/
│  ├─ infrastructure/        # Session manager, knowledge client, connection pooling
│  ├─ distillation/          # LangGraph state machine for knowledge synthesis
│  └─ token_validation.py    # Multi-provider token validation
├─ schemas/                  # Pydantic models (requests, responses, entities)
├─ services/
│  ├─ voice/                 # Voice module (Chainlit integration)
│  ├─ library_api_*          # Library integrations (OpenLibrary, Internet Archive, LoC, Gutenberg)
│  └─ [other services]       # TBD additional services
├─ workers/                  # Background job processors
├─ ui/                       # Frontend integration (Chainlit, Streamlit)
└─ logs/                     # Logging infrastructure
```

### External Service Integrations

| Service | Purpose | Status | Health | Notes |
|---------|---------|--------|--------|-------|
| PostgreSQL | Primary datastore | Active | ✅ | ACID, FTS, vector support |
| Redis | Caching, sessions, pub/sub | Active | ✅ | Sub-ms latency required |
| Qdrant | Vector search | Active | ✅ | HNSW indices, 3 collections |
| Gemini 1M | Context analysis | Available | ✅ | Full codebase fits |
| Copilot CLI | Multi-CLI dispatch | Available | ✅ | Quota management ready |
| OpenCode | Multi-account LLM | Available | ✅ | XDG_DATA_HOME isolation |
| Cline CLI | Code agent dispatch | Available | ✅ | Integration verified |
| Chainlit | UI framework | Active | ✅ | Voice integration ready |

### Data & Knowledge Assets

| Asset | Count | Status | Last Updated |
|-------|-------|--------|--------------|
| Foundation Documents | 500+ | Indexed | Phase 2 in progress |
| Research Documents | 200+ | Cataloged | Wave 4-5 audit complete |
| Code Samples | 100+ | Available | Throughout stack |
| Configuration Schemas | 50+ | Documented | Phase 3A locked |
| Expert Knowledge | 8 domains | Curated | Memory bank current |

---

## 🎯 PART 2: COMPLETE REFACTORING ROADMAP FOR OPUS

### Strategic Priorities (Tier 1: Critical Path)

**Tier 1A: Stack Harmonization (11.5 hours)**
1. ✅ Service API standardization (all services expose unified interface)
2. ✅ Plugin architecture implementation (zero coupling between services)
3. ✅ Configuration management (centralized, injectable)
4. ✅ Error handling unification (XNAiException base class everywhere)
5. ✅ Logging standardization (JSON, trace IDs, spans)
6. ✅ Health check endpoints (all services)
7. ✅ Metrics exposure (Prometheus-compatible)

**Tier 1B: Zero-Downtime Deployment (8.5 hours)**
1. ✅ Blue-green deployment templates
2. ✅ Graceful shutdown procedures (drain connections)
3. ✅ Database migration scripts (non-blocking)
4. ✅ Feature flags for new functionality
5. ✅ Automated rollback procedures
6. ✅ Health check automation (circuit breakers)
7. ✅ Load balancer configuration

**Tier 1C: Asyncio Blocker Resolution (11 hours - CRITICAL)**
1. ✅ Audit of 69 asyncio violations
2. ✅ Migration to proper async/await patterns
3. ✅ Event loop management fix
4. ✅ Thread pool integration where needed
5. ✅ Testing of async correctness
6. ✅ Documentation of async patterns

**Total Tier 1: 31 hours**

---

## 🤖 PART 3: CONTINUOUS BACKGROUND INFERENCE MODEL STRATEGY

### Architecture Design

```
┌─────────────────────────────────────────────────────────────┐
│ BACKGROUND INFERENCE ENGINE                                 │
├─────────────────────────────────────────────────────────────┤
│ Always-On Model Service                                      │
│ ├─ Model: Lightweight ONNX or GGUF (6GB RAM target)         │
│ ├─ Runtime: Vulkan GPU acceleration (AMD RADV)             │
│ ├─ Memory: zRAM (2-tier lz4+zstd)                           │
│ └─ CPU: <30% idle, spike to 60% on tasks                    │
├─────────────────────────────────────────────────────────────┤
│ TASK SCHEDULER (Redis-backed queue)                          │
│ ├─ Research jobs (explore knowledge gaps)                   │
│ ├─ Curation tasks (classify, tag, summarize docs)           │
│ ├─ Maintenance jobs (clean indices, optimize DBs)           │
│ ├─ Pattern discovery (cross-domain connections)             │
│ └─ Quality assurance (verify data consistency)              │
├─────────────────────────────────────────────────────────────┤
│ KNOWLEDGE UPDATE PIPELINE                                    │
│ ├─ Incremental ingestion (new/modified docs)                │
│ ├─ Re-ranking algorithms (improve search quality)           │
│ ├─ Domain classification (update knowledge map)             │
│ └─ Relationship mapping (find connections)                  │
├─────────────────────────────────────────────────────────────┤
│ STACK MAINTENANCE                                            │
│ ├─ Cache invalidation (intelligent TTL adjustment)          │
│ ├─ Index optimization (periodic rebuilds)                   │
│ ├─ Data integrity checks (verify checksums)                 │
│ └─ Performance profiling (find bottlenecks)                 │
└─────────────────────────────────────────────────────────────┘
```

### Background Tasks Design

#### 1. Research & Gap Filling (8 hours/week)
```yaml
Research_Job_Queue:
  - RQ-161: PostgreSQL FTS tuning (optimize search quality)
  - RQ-162: Ancient-BERT fine-tuning (domain-specific embeddings)
  - RQ-163: Knowledge graph construction (entity relationships)
  - RQ-164: Multi-agent learning metrics (expertise tracking)
  - RQ-165: RAG system evaluation (accuracy, latency, relevance)
  - RQ-166: Embedding visualization (t-SNE projections)
  - RQ-167: Query optimization patterns (common queries)
  - RQ-168: Persona evolution metrics (track agent growth)
  
Execution:
  - Priority: High-impact research gaps
  - Frequency: Continuous (whenever GPU idle)
  - Storage: Results in memory_bank/research/
  - Integration: Auto-update knowledge base
```

#### 2. Knowledge Curation (6 hours/week)
```yaml
Curation_Tasks:
  - Auto-extract key concepts from new documents
  - Tag documents with expertise levels
  - Generate one-liners and summaries
  - Classify into knowledge domains
  - Extract relationships and connections
  - Flag low-quality or outdated content
  
Workflow:
  - Trigger: New documents added to ingestion queue
  - Parallelization: Multiple curators running
  - Quality gate: Human review for confidence <0.85
  - Storage: Updated document_catalog table
```

#### 3. Stack Maintenance (4 hours/week)
```yaml
Maintenance_Tasks:
  - PostgreSQL: VACUUM, ANALYZE, reindex FTS
  - Redis: Memory optimization, key expiration review
  - Qdrant: Index optimization, collection cleanup
  - Cache: Invalidate stale entries, warm hot queries
  - Metrics: Collect performance data, detect anomalies
  
Automation:
  - Frequency: During low-traffic periods (2-4am)
  - Monitoring: Alert on performance degradation
  - Rollback: Snapshot before each major operation
```

#### 4. Quality Assurance (4 hours/week)
```yaml
QA_Tasks:
  - Verify data consistency across databases
  - Test query latency (spot-check performance)
  - Validate embeddings (ensure quality)
  - Check for duplicate documents
  - Audit access logs for security issues
  
Results:
  - Weekly health report
  - Anomaly alerts
  - Optimization recommendations
```

### Model Selection for Background Inference

**Primary (Research & Analysis):**
- **Model**: Raptor Mini or equivalent lightweight model
- **Framework**: ONNX Runtime (no PyTorch/Torch)
- **Memory**: 4-6GB (fits on system with zRAM)
- **GPU**: Vulkan (AMD RADV on Radeon)
- **Latency**: <500ms per inference

**Secondary (Classification):**
- **Model**: DistilBERT or TinyBERT
- **Framework**: ONNX Runtime
- **Memory**: 1-2GB
- **Use case**: Document tagging, domain classification

**Fallback (Always Available):**
- **Model**: Keyword-based heuristics
- **Latency**: <10ms
- **Reliability**: 100% (no model)

### Resource Management

```
Memory Budget:
├─ Model: 5GB (GGUF with offloading)
├─ Cache: 1GB (recent results, hot queries)
├─ Buffers: 1-2GB (task queues, intermediate results)
└─ System: 1GB (OS and utilities)
Total: 8-9GB (leaving 1-2GB buffer on 16GB system)

GPU Utilization:
├─ Idle (<10% usage): Background tasks
├─ Active (<30% usage): Maintain background model
├─ Spike (>50% usage): User queries take priority
└─ Overload (>80% usage): Queue background tasks

CPU Budget:
├─ Idle: Run all maintenance
├─ 20-40%: Background research
├─ 40-70%: Parallel curation tasks
└─ >70%: User-facing only

Scheduling:
├─ Peak hours (9am-5pm): User queries only
├─ Off-peak (5pm-9am): Full background suite
├─ Weekends: Heavier maintenance, research
└─ Emergency: Pause background, reserve resources
```

---

## 🔌 PART 4: PLUGIN-STYLE PORTABILITY ARCHITECTURE

### Interface Standards (All Services Must Implement)

```python
# All services implement this base interface
class PortableService(ABC):
    """Plugin-style service interface for complete portability."""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize service, return health status."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """Graceful shutdown, cleanup resources."""
        pass
    
    @abstractmethod
    async def health_check(self) -> ServiceHealth:
        """Return current health metrics."""
        pass
    
    @abstractmethod
    async def get_capabilities(self) -> Dict[str, Any]:
        """Declare what this service can do."""
        pass
    
    @abstractmethod
    async def handle_request(self, req: ServiceRequest) -> ServiceResponse:
        """Process any service request."""
        pass
    
    def on_config_change(self, new_config: Dict) -> None:
        """React to configuration changes."""
        pass
    
    def on_dependency_available(self, dep_name: str) -> None:
        """React to new dependencies becoming available."""
        pass
    
    def on_dependency_lost(self, dep_name: str) -> None:
        """React to dependencies going down."""
        pass
```

### Service Dependency Graph

```
User Queries
    ↓
[Query API] ←→ Feature Flags, Config
    ↓
[Agent Orchestration]
    ├─→ [Vector Search] (Qdrant, depends on embeddings)
    ├─→ [Keyword Search] (PostgreSQL FTS)
    ├─→ [Query Cache] (Redis)
    ├─→ [Agent Personas] (6 independent services)
    │   └─→ [Agent Learning] (Redis)
    └─→ [Synthesis Engine]
        ├─→ [Multi-perspective] (Agent outputs)
        ├─→ [Distillation] (Knowledge compression)
        └─→ [Gap Analysis] (Research tracker)

Background Services:
├─→ [Background Inference] (Model + task queue)
│   ├─→ [Research Job Queue] (Redis)
│   ├─→ [Curation Tasks] (PostgreSQL jobs table)
│   └─→ [Maintenance Tasks] (Scheduled jobs)
└─→ [Monitoring] (Prometheus metrics)
```

### Deployment Units (Can Deploy Independently)

```yaml
Deployment_Unit_1: "Query System"
  services:
    - query-api
    - query-router
    - vector-search
    - keyword-search
    - hybrid-search
  dependencies:
    - postgresql
    - qdrant
    - redis
  startup_order: [postgresql, qdrant, redis, query-*]
  health_endpoint: /health/query-system
  version: 1.0.0

Deployment_Unit_2: "Agent Layer"
  services:
    - agent-orchestration
    - scholar-agent
    - polymath-agent
    - specialist-agent
    - tutor-agent
    - critic-agent
    - creator-agent
  dependencies:
    - query-system
    - redis (for learning state)
  startup_order: [query-system, agent-orchestration, agents]
  health_endpoint: /health/agents

Deployment_Unit_3: "Synthesis"
  services:
    - synthesis-engine
    - multi-perspective
    - distillation
    - gap-analyzer
  dependencies:
    - agent-layer
    - knowledge-base
  startup_order: [agent-layer, synthesis]
  health_endpoint: /health/synthesis

Deployment_Unit_4: "Background"
  services:
    - background-inference
    - research-executor
    - curation-worker
    - maintenance-scheduler
  dependencies:
    - postgresql (for task storage)
    - redis (for queues)
  startup_order: [postgresql, redis, background-*]
  health_endpoint: /health/background
  isolation: "Can run on separate hardware"
```

---

## 📈 PART 5: ZERO-DOWNTIME DEPLOYMENT STRATEGY

### Rolling Deployment Process

```
Time  Phase              Status
────  ──────────────────────────────────────────────────────
T+0   Current State      V1 running, serving 100% traffic
      
T+5   Startup V2         V2 starting, health checks running
      
T+10  Drain V1           V1 no longer accepts new requests
      
T+15  Migrate State      V1 → V2 state transfer (hot migration)
      
T+20  Validation         V2 responding to health checks ✓
      
T+25  Cutover            Load balancer routes to V2
      
T+30  Monitor            V2 serves 100% traffic, V1 monitored
      
T+35  Rollback Ready     If issues detected, instant rollback
      
T+60  Decommission       V1 shutdown, cleanup
```

### Health Check Protocol

```python
Endpoint: GET /health/system

Response: {
  "status": "healthy|degraded|unhealthy",
  "timestamp": "2026-02-25T22:48:25Z",
  "services": {
    "query-system": {
      "status": "healthy",
      "latency_p95_ms": 85,
      "error_rate": 0.0001
    },
    "agent-layer": {
      "status": "healthy",
      "agents_online": 6,
      "learning_state_synced": true
    },
    "synthesis": {
      "status": "healthy",
      "synthesis_latency_p95_ms": 1800
    },
    "background": {
      "status": "healthy",
      "research_jobs_queued": 23,
      "model_memory_mb": 4821
    }
  },
  "dependencies": {
    "postgresql": {"status": "healthy", "connection_pool": "48/50"},
    "redis": {"status": "healthy", "memory_used": "621MB"},
    "qdrant": {"status": "healthy", "collections": 3}
  },
  "circuit_breakers": {
    "vector_search": "closed",
    "keyword_search": "closed",
    "external_apis": "half-open"
  }
}
```

### Graceful Degradation Modes

| Scenario | Response |
|----------|----------|
| Redis down | Use PostgreSQL cache, increase latency to <500ms |
| Qdrant down | Keyword search only, note degradation in response |
| PostgreSQL slow | Query cache hit rate boost, reduce FTS queries |
| Background model unavailable | Skip research tasks, continue maintenance |
| External API rate limit | Circuit breaker, use cached responses |
| Memory pressure | Reduce cache sizes, pause background tasks |
| GPU unavailable | Fall back to CPU inference, slower but works |

---

## 🎛️ PART 6: OPUS EXECUTION PLAN

### Phase 1: Stack Harmonization (Weeks 1-2)

**Objective**: Make all services interchangeable, independently deployable

```
Week 1:
├─ Day 1-2: Audit all service interfaces
├─ Day 3-4: Implement unified base classes
├─ Day 5: Error handling standardization
└─ Day 6-7: Logging & metrics infrastructure

Week 2:
├─ Day 1-3: Plugin architecture implementation
├─ Day 4-5: Configuration injection system
├─ Day 6-7: Health check endpoints for all services
└─ Testing: Full integration test suite
```

### Phase 2: Zero-Downtime Deployment (Weeks 2-3)

**Objective**: Enable production-grade deployments with 99.99% uptime

```
Week 2-3:
├─ Deployment templates (Docker/K8s/Podman)
├─ Database migration framework (non-blocking)
├─ Feature flag system (gradual rollout)
├─ Automated rollback procedures
├─ Load balancer configuration
└─ Documentation & runbooks
```

### Phase 3: Asyncio Blocker Fix (Week 3-4)

**Objective**: Resolve critical asyncio violations (69 issues)

```
Week 3:
├─ Complete audit of violations
├─ Design refactoring strategy
└─ Begin refactoring

Week 4:
├─ Complete refactoring
├─ Comprehensive testing
└─ Performance validation
```

### Phase 4: Background Inference Integration (Weeks 4-5)

**Objective**: Deploy always-on model service

```
Week 4:
├─ Model selection & optimization
├─ Task scheduler implementation
└─ Research job pipeline

Week 5:
├─ Curation tasks integration
├─ Maintenance scheduler
├─ Quality assurance automation
└─ Production deployment
```

### Phase 5: Documentation & Handoff (Week 5+)

**Objective**: Production-ready with complete documentation

```
Deliverables:
├─ Implementation manuals
├─ Operational runbooks
├─ Performance tuning guide
├─ Troubleshooting guide
├─ Architecture diagrams
└─ Ops team training
```

---

## 📊 PART 7: SUCCESS METRICS & MONITORING

### Key Performance Indicators

```
Uptime Metrics:
├─ System availability: >99.95% (target)
├─ Average response time: <500ms
├─ p95 latency: <1s
├─ p99 latency: <2s

Query Performance:
├─ Vector search: <100ms p95
├─ Keyword search: <50ms p95
├─ Hybrid search: <200ms p95
├─ Cache hit rate: >60%

Agent Metrics:
├─ Response quality score: >0.85
├─ Learning velocity: +5% per week
├─ Agent collaboration success: >90%
├─ Persona distinctiveness: >0.8

Background Inference:
├─ Model latency: <500ms per inference
├─ Memory usage: <6GB
├─ GPU utilization: <30% (idle)
├─ Research job throughput: >5 jobs/hour

Data Quality:
├─ Document coverage: 500+ docs
├─ Embedding freshness: >95% up-to-date
├─ Relationship accuracy: >90%
├─ Domain classification confidence: >0.85
```

### Automated Monitoring Dashboard

```yaml
Dashboard_Views:
  - System_Health: Overall status, alerts
  - Performance: Latency distributions, throughput
  - Resources: CPU, memory, GPU, disk
  - Queries: Top queries, slow queries, errors
  - Agents: Agent performance, learning progress
  - Background: Research jobs, curation status, maintenance
  - Alerts: Real-time issues, trend analysis
```

---

## 🚀 PART 8: IMMEDIATE NEXT ACTIONS FOR OPUS

### Week 1 Tasks (Priority Order)

1. **[ ] Review Current State**
   - Read `memory_bank/activeContext.md` (current status)
   - Review `COMPLETE-SYNTHESIS-FOR-OPUS-46-2026-02-25.md` (Wave 4-5)
   - Check `OPUS-4.6-INDEX.md` (resource map)

2. **[ ] Validate Stack Readiness**
   - Verify all services in app/XNAi_rag_app/ can be harmonized
   - Check async/await patterns (69 violations identified)
   - Confirm database schemas are compatible

3. **[ ] Plan Harmonization**
   - Design unified service interface
   - Map current service implementations
   - Identify dependencies and conflicts

4. **[ ] Begin Phase 1 Execution**
   - Implement base service class
   - Start error handling standardization
   - Set up logging infrastructure

### Ongoing Tasks (Background)

1. **Review RAG Deployment** (Phases 2-6 executing)
   - Monitor agents in `/tasks`
   - Review deliverables in `/tmp/`
   - Integrate learnings into stack

2. **Research & Gap Filling**
   - Use background inference for RQ-161 through RQ-168
   - Document findings in memory_bank/research/
   - Update knowledge base

3. **Stakeholder Communication**
   - Weekly progress reports
   - Risk mitigation for blockers
   - Collaboration with team

---

## 📚 PART 9: RESOURCES & REFERENCES

### Key Documents

| Document | Purpose | Location |
|----------|---------|----------|
| Implementation Plan | Complete 56-task breakdown | Session workspace/plan.md |
| Deployment Status | Real-time tracking | Session workspace/FLEET-DEPLOYMENT-COMPLETE.md |
| API Spec | Service interfaces | Opus deliverables in /tmp/ |
| Operations Manual | Day-to-day runbooks | Phase 6 deliverables |
| Architecture Guide | System design | memory_bank/handovers/ |

### Code Locations

```
Core Stack: /app/XNAi_rag_app/
├─ API: /api/
├─ Services: /services/
├─ Core: /core/ (infrastructure, distillation, token validation)
└─ Schemas: /schemas/

Configuration:
├─ Main: /app/config.toml
├─ Credentials: /app/.xnai_credentials.yaml (git-ignored)
└─ Feature Flags: /app/feature_flags.yaml

Tests:
├─ Unit: /tests/unit/
├─ Integration: /tests/integration/
└─ E2E: /tests/e2e/

Documentation:
├─ Guides: /docs/
├─ API Docs: /docs/api/
└─ Internal: /internal_docs/
```

### Command Reference

```bash
# Monitor RAG deployment
/tasks

# Check system health
curl http://localhost:8000/health/system

# View SQL progress
SELECT phase, COUNT(*), status FROM knowledge_todos GROUP BY phase, status

# Run background maintenance
python scripts/xnai-maintenance-scheduler.py

# Deploy new version
./scripts/xnai-deploy-blue-green.sh

# Rollback if needed
./scripts/xnai-rollback.sh
```

---

## ✅ CHECKLIST FOR OPUS

- [ ] Read and understand entire deployment strategy
- [ ] Review current stack services (app/XNAi_rag_app/)
- [ ] Validate asyncio violations (69 identified)
- [ ] Design service harmonization approach
- [ ] Create implementation timeline
- [ ] Set up monitoring/observability
- [ ] Begin Phase 1: Stack Harmonization
- [ ] Monitor RAG deployment progress
- [ ] Queue background inference research
- [ ] Weekly progress reviews
- [ ] Production deployment execution

---

## 📞 ESCALATION & SUPPORT

**For Technical Questions**: Review memory_bank/ and internal_docs/  
**For Code Questions**: Check /app/ and run tests  
**For Research Gaps**: Queue as background research job  
**For Blockers**: Escalate to agent bus (topic: xnai-research)  

---

**Status**: 🟢 READY FOR OPUS EXECUTION  
**Next Review**: Upon Phase 1 completion (Week 1-2)  
**Escalation Path**: Agent Bus → XNAi Foundation Team

