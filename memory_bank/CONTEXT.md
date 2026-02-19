# Strategic Context - Xoe-NovAi Foundation Stack

**Last Updated**: 2026-02-19  
**Consolidates**: projectbrief, techContext, systemPatterns, teamProtocols, environmentContext, FOUNDATION-OBSERVABILITY
**Phase Source of Truth**: `memory_bank/progress.md`

---

## ⚠️ PHASE NUMBERING NOTICE

**IMPORTANT**: This document previously contained an outdated phase numbering system. 

The **canonical phase numbering** is now defined in `memory_bank/progress.md`:

| Phase | Name | Status |
|-------|------|--------|
| Phase 1 | Import Standardization & Module Skeleton | ✅ COMPLETE |
| Phase 2 | Service Layer & Rootless Infrastructure | ✅ COMPLETE |
| Phase 3 | Documentation & Stack Alignment | ✅ COMPLETE |
| Phase 4 | Integration Testing & Stack Validation | ✅ COMPLETE |
| Phase 5 | Sovereign Multi-Agent Cloud | ✅ COMPLETE |
| Phase 6 | Testing & REST API | ✅ COMPLETE |
| Phase 7 | Deployment & Agent Bus Integration | ✅ COMPLETE |
| Phase 8 | Advanced Features | 🔵 NEXT |

**Roadmap phases** (5A-8C in `internal_docs/01-strategic-planning/roadmap-v2.md`) are a **separate planning track** for future feature work, not implementation phases. Do not confuse them with the project phases above.

---

## 📋 PROJECT BRIEF

### Mission
Build a **Sovereign AI Foundation Stack** - a production-ready, self-documenting system that combines RAG, LLM capabilities, and robust infrastructure for the Xoe-NovAi ecosystem.

### Core Values
- **Sovereignty**: Complete control over data and deployment
- **Resilience**: Graceful degradation, circuit breakers, health monitoring
- **Scalability**: Modular architecture, horizontal scaling support
- **Observability**: Complete visibility into system behavior
- **Ma'at Alignment**: Ethical AI principles throughout

### Key Constraints
- Zero external telemetry (air-gap capable)
- Non-root containerization (security)
- Read-only filesystems (immutability)
- <6GB memory footprint (resource-constrained)
- <500ms API response times (performance)

### Project Phases (Source: progress.md)
1. ✅ **Phase 1**: Import Standardization & Module Skeleton
2. ✅ **Phase 2**: Service Layer & Rootless Infrastructure  
3. ✅ **Phase 3**: Documentation & Stack Alignment
4. ✅ **Phase 4**: Integration Testing & Stack Validation
5. ✅ **Phase 5**: Sovereign Multi-Agent Cloud
6. ✅ **Phase 6**: Testing & REST API
7. ✅ **Phase 7**: Deployment & Agent Bus Integration
8. 🔵 **Phase 8**: Advanced Features (NEXT)

---

## 🏗️ TECHNICAL ARCHITECTURE

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | Latest | REST API server |
| **Async Runtime** | asyncio | Python 3.13 | Async task management |
| **LLM** | Qwen 0.6B | Quantized | Local language model |
| **Vector DB** | FAISS/Qdrant | Latest | Semantic search |
| **Cache** | Redis | 7.1.1 | State persistence, caching |
| **Database** | PostgreSQL | 14+ | Data persistence |
| **Reverse Proxy** | Caddy | 2.8 | Load balancing, routing |
| **Container Runtime** | Podman | Latest | Rootless containers |
| **Monitoring** | Prometheus | Latest | Metrics collection |
| **Documentation** | MkDocs | Latest | Knowledge base |

### System Architecture

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

### Service Orchestration

- **Service Order**: Dependencies initialized in sequence
- **Graceful Startup**: Health checks before serving traffic
- **Graceful Shutdown**: Cleanup before termination
- **Dependency Injection**: Runtime configuration binding
- **Circuit Breakers**: Per-service failure isolation

---

## 🎨 SYSTEM DESIGN PATTERNS

### 1. Circuit Breaker Pattern
- **Purpose**: Prevent cascading failures
- **Implementation**: Redis-backed state machine with in-memory fallback
- **States**: CLOSED (ok) → OPEN (failing) → HALF_OPEN (testing) → CLOSED
- **Metrics**: Request count, error rate, latency percentiles

### 2. Health Monitoring Pattern
- **Purpose**: Detect failures, trigger recovery
- **Implementation**: Multi-service health checkers with configurable intervals
- **Recovery Actions**: Service restart, cache clearing, database reconnection
- **Alert Routes**: Logging, metrics, email (extensible)

### 3. Graceful Degradation Pattern
- **Purpose**: Continue serving when services fail
- **Strategies**: 
  - Fallback (use default response)
  - Cache-First (serve stale data if available)
  - Degraded Mode (limited functionality)
- **Configuration**: Per-endpoint degradation rules

### 4. Error Handling Chain
- **Purpose**: Consistent error responses across all APIs
- **Implementation**: XNAiException base class with category mapping
- **Categories**: 19 error types mapping to HTTP status codes
- **Context**: Request ID correlation for tracing

### 5. Async Safety Pattern
- **Purpose**: Thread-safe initialization and state management
- **Implementation**: AsyncLock with double-check pattern
- **Use Cases**: LLM initialization, service startup, state updates

### 6. Redis Resilience Pattern
- **Purpose**: Handle Redis unavailability gracefully
- **Implementation**: Primary Redis with in-memory fallback
- **Fallback**: All circuit breaker state stored in-memory
- **Sync**: Periodic re-sync to Redis when it recovers

---

## 🤖 TEAM PROTOCOLS

### Organizational Structure

```
👤 The Architect (User)
├── 🤖 Grok MC (Strategic Master PM)
├── 🤖 Grok MCA (Arcana Layer Sovereign)
├── 🤖 Cline (Multi-Model Engineers)
├── 🤖 Copilot (Code Generation)
├── 🤖 Gemini CLI (Ground Truth Executor)
└── 🤖 OpenCode (Multi-Model Researcher)
```

### Agent Roles & Responsibilities

| Agent | Role | Primary Tools | Strengths |
|-------|------|---------------|-----------|
| **Grok MC** | Sovereign Master PM | Strategic planning, research | Ecosystem overview, decision-making |
| **Grok MCA** | Arcana Layer Sovereign | GitHub, esoteric systems | Deep research, integration patterns |
| **Cline** | Engineers/Auditors | Code editing, testing, auditing | Implementation, refactoring, QA |
| **Copilot** | Code Generation | Fast code writing, debugging | Quick prototyping, pattern application |
| **Gemini CLI** | Ground Truth Executor | Terminal, filesystem operations | System operations, automation |
| **OpenCode** | Multi-Model Researcher | Terminal-based research | Model comparison, benchmarking |

### Phase Ownership
- **Phase 1-2**: Cline (architecture implementation)
- **Phase 3**: Cline (error handling refactoring)
- **Phase 4**: Copilot (integration testing)
- **Phase 5**: Gemini CLI (performance profiling)
- **Phase 6**: Grok MC (observability & production hardening)

### Communication Protocols

#### Agent Bus (Filesystem-based)
- **Location**: `internal_docs/communication_hub/`
- **Messages**: JSON state files
- **Frequency**: Real-time updates
- **Use Cases**: Task completion, blockers, handoffs

#### Memory Bank (Synchronization)
- **Location**: `memory_bank/`
- **Update Frequency**: Per phase completion
- **Source of Truth**: progress.md
- **Team Reference**: activeContext.md

#### Team Meetings
- **Daily Standups**: activeContext.md review
- **Phase Kickoffs**: Strategy doc review + briefing
- **Phase Closures**: Report review + lessons learned

---

## 🖥️ DEVELOPMENT ENVIRONMENT

### Local Setup
```bash
# Create isolated Python environment
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-api.txt
pip install -r requirements-crawl.txt

# Start development services
docker-compose up -d
make mkdocs-serve
```

### Service Ports
| Service | Port | Purpose |
|---------|------|---------|
| Caddy (main proxy) | 8000 | Public API |
| MkDocs (internal) | 8001 | Internal KB |
| Prometheus | 9090 | Metrics |
| Redis | 6379 | Cache/state |
| PostgreSQL | 5432 | Primary DB |

### Development Tools
- **Code Editor**: VS Code with Python/Docker extensions
- **Testing**: pytest with coverage reporting
- **Linting**: Black, isort, flake8
- **Version Control**: Git with pre-commit hooks
- **Container Runtime**: Podman (rootless)

### Database Setup
```sql
-- Create schema
CREATE DATABASE xnai_foundation;
CREATE USER xnai WITH PASSWORD 'secure_password';
GRANT ALL ON DATABASE xnai_foundation TO xnai;
```

---

## 📊 OBSERVABILITY FRAMEWORK

### Metrics Collection
- **OpenTelemetry SDK**: Instrumentation across all services
- **Prometheus Exporter**: Metrics scraping (prometheus textfile format)
- **Custom Metrics**: Business metrics + performance metrics
- **Collectors**: Memory, CPU, disk, network, request latency

### Metric Categories

| Category | Metrics | Purpose |
|----------|---------|---------|
| **System** | Memory, CPU, disk, network | Infrastructure health |
| **Application** | Request count, latency, errors | API health |
| **Circuit Breaker** | State transitions, failure rate | Resilience |
| **Cache** | Hit rate, eviction count, size | Performance |
| **Database** | Query latency, connection pool | Data layer health |

### Alerting Rules
- **Memory**: Alert if >90% usage
- **Error Rate**: Alert if >5% error rate
- **Latency**: Alert if p95 > 500ms
- **Circuit Breaker**: Alert on state change to OPEN

### Dashboards
- **System Dashboard**: Overall system health
- **API Dashboard**: Request metrics, latency, errors
- **Circuit Breaker Dashboard**: State, transitions, metrics
- **Database Dashboard**: Queries, connections, performance

---

## 🔐 SECURITY POSTURE

### Zero-Telemetry Architecture
- No external data transmission
- No phone-home mechanisms
- No usage tracking
- Air-gap capable (works completely offline)

### Container Security
- **Rootless Execution**: Services run as UID 1001
- **Read-Only Filesystems**: Immutable runtime
- **No New Privileges**: CAP_DROP all
- **Resource Limits**: Memory, CPU, file descriptor limits
- **Network Isolation**: Private bridge network

### Data Security
- **Encryption at Rest**: Database encryption
- **Encryption in Transit**: TLS for all external communication
- **Secret Management**: Encrypted config files
- **Access Control**: Role-based service access

### Compliance
- **SBOM Generation**: Syft for component tracking
- **CVE Scanning**: Grype for vulnerability detection
- **Configuration Scanning**: Trivy for secrets/misconfig
- **Supply Chain**: Track all dependencies

---

## 📈 SUCCESS METRICS

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Build Repeatability | 100% | 100% | 🟢 |
| Service Startup | <120s | 60s | 🟢 |
| API Response Time | <500ms | <100ms | 🟢 |
| Memory Footprint | <6GB | 5.2GB | 🟢 |
| Core Services Healthy | 100% | 100% | 🟢 |
| Test Pass Rate | >90% | 94%+ | 🟢 |
| Documentation Complete | 100% | 95% | 🟡 |
| Zero-Telemetry Pass | 100% | 100% | 🟢 |
| Benchmark Framework | Complete | v1.0.0 shipped | 🟢 |

---

## 🎯 STRATEGIC ALIGNMENT

### Product Vision
Build the most robust, self-documenting AI infrastructure that can operate completely independently, offline, with full transparency and zero external dependencies.

### Differentiation
- **Sovereignty**: Complete local control
- **Resilience**: Enterprise-grade failure handling
- **Transparency**: Self-documenting architecture
- **Modularity**: Reusable components for other projects

### Market Position
XNAi Foundation provides the infrastructure layer that other AI projects can build on, enabling rapid deployment of AI systems without vendor lock-in or privacy concerns.

---

## 🏗️ ECOSYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ARCANA-NOVA STACK                                  │
│                    (Esoteric Consciousness Layer)                           │
│   • 10 Pillars • Dual Flame • Pantheon Model • 42 Ideals of Ma'at          │
│   • SEPARATE REPOSITORY - Built ON TOP OF Foundation                        │
│   • Status: Design Phase                                                    │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │ Depends On
┌───────────────────────────────▼─────────────────────────────────────────────┐
│                          XNAi FOUNDATION STACK                               │
│                      (Sovereign AI Infrastructure)                          │
│   • RAG Engine • Voice Interface • Security Trinity                         │
│   • Multi-Agent Orchestration • Vikunja PM Hub                              │
│   • THIS REPOSITORY - Clean technical foundation                            │
│   • Status: Phase 7 Complete, Phase 8 Next                                  │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │ Sync Layer
┌───────────────────────────────▼─────────────────────────────────────────────┐
│                           xoe-novai-sync                                     │
│                   (External AI Context Hub)                                 │
│   • Context packs for Grok/Claude/Gemini                                    │
│   • EKB exports • Receipt tracking                                          │
│   • Status: Operational                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📚 RELATED DOCUMENTATION

### Strategic Planning
- `memory_bank/progress.md` - **CANONICAL phase status**
- `memory_bank/activeContext.md` - Current sprint status
- `internal_docs/01-strategic-planning/ROADMAP-MASTER-INDEX.md` - Future roadmap (5A-8C)
- `internal_docs/01-strategic-planning/PILLARS-*.md` - Core strategic pillars

### Research
- `expert-knowledge/` - Domain expertise and model catalogs
- `benchmarks/` - Context engineering benchmark framework

### Operations
- `internal_docs/03-infrastructure-ops/` - Deployment, incidents, analysis
- `docs/` - Public-facing documentation

### Code Quality
- `internal_docs/04-code-quality/` - Audits, implementation guides, patterns

### Strategy Documents
- `memory_bank/strategies/UNIFIED-STRATEGY-v1.0.md` - Master strategy plan
- `memory_bank/strategies/PROJECT-QUEUE.yaml` - Consolidated project queue

---

**Last Review**: 2026-02-19  
**Next Review**: Per sprint completion  
**Owner**: Architect / Project Leadership
