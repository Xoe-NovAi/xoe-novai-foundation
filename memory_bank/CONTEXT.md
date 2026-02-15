# Strategic Context - Xoe-NovAi Foundation Stack

**Last Updated**: 2026-02-14  
**Consolidates**: projectbrief, techContext, systemPatterns, teamProtocols, environmentContext, FOUNDATION-OBSERVABILITY

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

### Project Phases
1. ✅ **Phase 1**: Circuit Breakers & Health Monitoring
2. ✅ **Phase 2**: Service Layer & Infrastructure  
3. 🟡 **Phase 3**: Documentation & Error Handling (75% complete)
4. 🔵 **Phase 4**: Integration Testing & Stack Validation (In Progress)
5. 🔵 **Phase 5**: Performance Profiling & Optimization (Staged)

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
| Memory Footprint | <6GB | 5.6GB | 🟢 |
| Core Services Healthy | 100% | 85% | 🟡 |
| Test Pass Rate | >90% | 94%+ | 🟢 |
| Documentation Complete | 100% | 95% | 🟢 |
| Zero-Telemetry Pass | 100% | 100% | 🟢 |

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
Xoe-NovAi Foundation provides the infrastructure layer that other AI projects can build on, enabling rapid deployment of AI systems without vendor lock-in or privacy concerns.

---

## 📚 RELATED DOCUMENTATION

### Strategic Planning
- `internal_docs/01-strategic-planning/PILLARS-*.md` - Core strategic pillars
- `internal_docs/01-strategic-planning/PHASE-*.md` - Phase-specific strategies
- `internal_docs/01-strategic-planning/ROADMAP.md` - Long-term roadmap

### Research
- `internal_docs/02-research-lab/` - Research findings and analyses
- `expert-knowledge/` - Domain expertise and model catalogs

### Operations
- `internal_docs/03-infrastructure-ops/` - Deployment, incidents, analysis
- `docs/` - Public-facing documentation

### Code Quality
- `internal_docs/04-code-quality/` - Audits, implementation guides, patterns

---

**Last Review**: 2026-02-14  
**Next Review**: Per phase completion  
**Owner**: Architect / Project Leadership
