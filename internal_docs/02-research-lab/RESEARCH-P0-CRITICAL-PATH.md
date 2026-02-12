# RESEARCH P0: CRITICAL PATH

**Sessions 1-6: Foundation for Scholar Platform Production**

← [Back to RESEARCH-MASTER-INDEX](../RESEARCH-MASTER-INDEX.md)

---

## P0 Overview

**Priority**: P0 (Critical Path - Cannot Skip)  
**Sessions**: 1-6  
**Duration**: 18-24 hours total research  
**Timeline**: Weeks 1-4 (or parallel with Phase 5A-5E implementation)  
**Outcome**: Production-grade infrastructure ready for Phase 5A-5E execution

**Key Context**: P0 research directly supports Pillar 1 implementation. These sessions establish the foundation that all subsequent phases depend on.

---

## Table of Contents

1. [Execution Timeline](#execution-timeline)
2. [Session 1: Memory Optimization](#session-1-memory--performance-optimization)
3. [Session 2: Library Curation APIs](#session-2-library-curation-system-architecture)
4. [Session 3: Ancient Greek BERT](#session-3-ancient-greek-bert--embeddings)
5. [Session 4: Vikunja Integration](#session-4-vikunja-memorybank-integration)
6. [Session 5: Observable Stack](#session-5-observable-prometheus--grafana)
7. [Session 6: Authentication](#session-6-authentication--authorization-design)
8. [Quick Reference](#quick-reference)

---

## Execution Timeline

| Week | Session | Title | Duration | Team | Output |
|------|---------|-------|----------|------|--------|
| 1-2 | 1 | Memory Optimization | 2-3h | Gemini CLI, Cline | Tuning recommendations |
| 1-2 | 2 | Library APIs | 4-5h | Grok MCA, Cline | API comparison matrix |
| 2-3 | 3 | Ancient Greek BERT | 3-4h | Grok MCA, Cline | Model evaluation report |
| 2-3 | 4 | Vikunja Memory | 3-4h | Gemini CLI, Cline | Integration architecture |
| 3-4 | 5 | Observable | 3-4h | Cline-Trinity | Dashboard specification |
| 3-4 | 6 | Authentication | 2-3h | Cline-Kat | Auth implementation guide |

**Parallelization**: Sessions 1-6 can run in parallel; focus on completing all by week 4

---

## PHASE 0: DOCUMENTATION SYSTEM FOUNDATION 📚

**Priority**: P0 (Blocking - Must Complete First)  
**Duration**: 2-4 hours  
**Timeline**: Week 1 (parallel with Session 1-2 research)  
**Outcome**: Centralized MkDocs system for all research, strategic plans, and implementation guides  
**Owner**: Documentation Lead (Arcana-NovAi)

### Critical Tasks

This foundation must be in place BEFORE executing research sessions and pillar implementation:

1. **Consolidate All Meta Files** (1 hour)
   - ✅ Move 15 _meta/ files to internal_docs/00-system/
   - ✅ Organize into categories (strategic, research, infrastructure, code quality)
   - ✅ Preserve genealogy tracking files (GENEALOGY.md, GENEALOGY-TRACKER.yaml)
   - **Location**: `internal_docs/00-system/`

2. **Create MkDocs Internal Configuration** (1 hour)
   - ✅ Generate mkdocs-internal.yml configuration file
   - ✅ Define navigation structure with 7-level taxonomy
   - ✅ Configure search plugin and material theme
   - **Location**: `/mkdocs-internal.yml` (repo root)

3. **Organize Research & Strategic Documents** (1 hour)
   - ✅ Place PILLAR docs in `01-strategic-planning/PILLARS/`
   - ✅ Place RESEARCH docs in `02-research-lab/`
   - ✅ Create master indices linking all documents
   - ✅ Update PILLAR documents with MkDocs integration sections

4. **Create Knowledge Base Index** (30 min)
   - ✅ Generate `internal_docs/index.md` homepage
   - ✅ Create role-based navigation shortcuts
   - ✅ Document search patterns and quick references
   - **Location**: `internal_docs/index.md`

5. **Enable Local MkDocs Build** (30 min)
   - ✅ Test: `mkdocs serve -f mkdocs-internal.yml`
   - ✅ Verify navigation structure renders correctly
   - ✅ Confirm search indexing works
   - **Success Criteria**: Load homepage at http://127.0.0.1:8001

### Why This Is Critical Path

- 🔗 **Information Access**: If docs aren't centralized, research findings get lost and duplicate work occurs
- 📊 **Team Coordination**: PILLAR and RESEARCH documents must be accessible to all team members simultaneously
- 🚀 **Implementation Speed**: Developers need < 30 second lookup time for implementation guides
- 🔄 **Continuous Updates**: MkDocs system must be ready BEFORE research sessions generate new findings
- 📈 **Scalability**: As we extract P1, P2, P3 research phases, documentation system must be stable

### Integration with Research Sessions

Each research session outputs to:
- **Session findings** → `02-research-lab/RESEARCH-SESSIONS/`
- **Implementation guides** → `04-code-quality/IMPLEMENTATION-GUIDES/`
- **Cross-references** → Updated in PILLAR documents automatically
- **Search index** → Regenerated on `git push` (CI/CD ready)

### Success Criteria

- ✅ All 15 meta files consolidated
- ✅ MkDocs internal config working (`mkdocs serve -f mkdocs-internal.yml`)
- ✅ Both public (`docs/`) and internal (`internal_docs/`) MkDocs building successfully
- ✅ PILLAR documents updated with MkDocs sections
- ✅ Knowledge base searchable and navigable
- ✅ Team can find any document in < 30 seconds

### Next Steps After Phase 0 Complete

1. Proceed with Sessions 1-6 research documentation
2. Extract RESEARCH-P1, P2, P3 with knowledge base support
3. Add emerging findings to organized section
4. Update PILLAR documents with research outputs
5. Generate implementation guides for each phase

---

## SESSION 1: MEMORY & PERFORMANCE OPTIMIZATION

**Duration**: 2-3 hours | **Priority**: P0 | **Blocking**: Phase 5A execution

### Research Areas

1. **zRAM Optimization for ML Workloads**
   - Expected compression ratios (code, models, embeddings)
   - Best practices for vm.swappiness (ML-specific recommendations)
   - Container memory limit strategies
   - Background service prioritization

2. **LLM Memory Footprint Analysis**
   - Qwen-0.6B memory breakdown
   - Memory usage patterns (startup vs. steady state)
   - Context window impact
   - Batch processing requirements

3. **Distributed Memory Architecture (Future)**
   - Multi-machine memory pooling options
   - Remote memory access patterns
   - When to add RAM vs. scale horizontally

### Deliverables Expected
- zRAM tuning recommendations (specific sysctl values: vm.swappiness=35 target)
- Container memory allocation formula
- Memory monitoring baseline (what to measure)
- Phase 5A implementation guide refinements

### Key Decisions to Make
- vm.swappiness value (default 60 vs. ML-optimized 35)
- Container memory splits (RAG: 4GB vs. other services)
- OOM event handling strategy

---

## SESSION 2: LIBRARY CURATION SYSTEM ARCHITECTURE

**Duration**: 4-5 hours | **Priority**: P0 | **Blocking**: Phase 5E execution

### Research Areas

#### 1. Multi-Library API Integration Strategy
- **OpenLibrary**: Coverage, rate limits (100/min), offline caching
- **WorldCat**: OCLC access, Ancient Greek coverage, bibliographic quality
- **Perseus Digital Library**: CTS URN system, TEI XML, legal considerations
- **arXiv**: Categories, rate limits (100/5min), metadata completeness
- **CrossRef**: DOI resolution, journal metrics, licensing

#### 2. Domain-Specific Classification
- **Classics**: Ancient Greek normalization, dialect handling, TLG integration
- **Philosophy**: Era classification, school mapping, SEP linking
- **Esoteric**: Symbol extraction, cross-tradition mapping
- **Technical**: API endpoint extraction, version tracking
- **Science**: Paper classification, peer review status

#### 3. Metadata Enrichment Strategy
- Authority scoring algorithm (what signals quality?)
- Dewey Decimal mapping approach
- Citation extraction patterns
- Quality assessment gates

#### 4. Storage & Retrieval Design
- Directory structure (`/library/classics/greek/...`)
- Metadata JSON schema
- Embedding storage organization
- Retrieval latency targets

### Deliverables Expected
- API comparison matrix (coverage, rate limits, data quality, cost)
- Integration architecture (parallel vs. sequential)
- Caching strategy (TTL, refresh policy)
- Error handling for API failures
- Legal considerations per API (terms of service)
- Domain classification hierarchy

### Key Decisions to Make
- Which libraries to prioritize (OpenLibrary + Perseus first?)
- Ancient Greek text source ranking
- Authority score weighting
- Storage path structure

---

## SESSION 3: ANCIENT GREEK BERT & EMBEDDINGS

**Duration**: 3-4 hours | **Priority**: P0 | **Blocking**: Phase 6A preparatory

### Research Areas

#### 1. Model Evaluation
- **Ancient-Greek-BERT**: Accuracy, vocabulary coverage, diacritics handling
- **Krikri-7B-Instruct**: Ancient + Modern Greek, 4096 token context, resource usage
- **Science BERT, Philosophy BERT**: Domain specialization trade-offs
- **Multilingual Fallback**: When to use, accuracy vs. specialization

#### 2. Dynamic Selection Logic
- Language detection (grc vs. el vs. multilingual)
- Domain inference algorithms
- Model recommendation confidence
- Multi-embedding hybrid retrieval (RRF scoring)

#### 3. Embedding Storage & Management
- Storage format (NumPy vs. HDF5 vs. database)
- Lazy loading strategy (LRU cache sizing)
- Versioning approach
- Update strategy when models change

#### 4. Specialized Processing
- Greek text normalization (σ/ς sigma handling)
- Diacritic preservation (polytonic expected)
- Tokenization edge cases
- Morphological feature extraction

### Deliverables Expected
- Model capability matrix (context, dimensions, speed, accuracy)
- Dynamic selection algorithm (flowchart/pseudocode)
- Embedding storage architecture
- Normalization preprocessing pipeline
- Performance baseline (tokens/second, memory usage)

### Key Decisions to Make
- Primary model for Ancient Greek (Ancient-Greek-BERT vs. Krikri)
- Fallback strategy (multilingual for safety?)
- Hybrid retrieval complexity (worth RRF?)
- Storage format (NumPy for simplicity vs. database for scale?)

---

## SESSION 4: VIKUNJA MEMORY_BANK INTEGRATION

**Duration**: 3-4 hours | **Priority**: P0 | **Blocking**: Phase 6C execution

### Research Areas

#### 1. Vikunja API Capabilities
- Current operational status and availability
- API authentication methods
- Rate limits (note: **local installation = no external limits**)
- Task schema and custom fields support

#### 2. Memory Types & Storage
- Conversation memory (store chat history as tasks)
- Context snippets (decisions, learnings)
- Handoff memory (agent transitions)
- Reference memory (links, documentation)

#### 3. Integration Patterns
- Task creation from conversations
- Retrieval queries and filtering
- Async operations (non-blocking)
- Error handling and retries

#### 4. Scalability & Performance
- Query latency expectations (< 500ms target)
- Concurrent access handling  
- Storage growth projections
- Memory bank size management

### Deliverables Expected
- Vikunja integration architecture
- Task schema for each memory type
- API client implementation plan
- Conversation archival strategy
- Context retrieval algorithms
- Performance SLAs

### Key Decisions to Make
- Task vs. comment for memory storage?
- Index strategy for fast retrieval
- Retention policies (auto-archive old tasks?)
- Synchronization with memory_bank files

---

## SESSION 5: OBSERVABLE (PROMETHEUS + GRAFANA)

**Duration**: 3-4 hours | **Priority**: P0 | **Blocking**: Phase 5B execution

### Research Areas

#### 1. Metrics Architecture
- OpenTelemetry SDK integration (Python libraries)
- Custom metric types (Counter, Gauge, Histogram)
- Metric naming conventions (sovereign-ai-*)
- Label cardinality management
- Retention policies

#### 2. Prometheus Deployment
- Podman container setup
- Service discovery (scrape config)
- Storage requirements and tuning
- Security (API auth, TLS)
- Data retention (default 15 days)

#### 3. Grafana Dashboards
- Panel types (graph, heatmap, table)
- Query language (PromQL)
- Dashboard layout (system, services, ML, library, UX)
- Alert integration
- Threshold and alert rules

#### 4. Instrumentation Points
- Request/response timing (middleware)
- LLM inference metrics (pre/post)
- Vector DB queries (FAISS/Qdrant)
- Async tasks (queue depth)
- Library operations (ingestion rate, accuracy)

### Deliverables Expected
- Observable architecture diagram
- Prometheus deployment spec (docker-compose)
- Grafana dashboard specifications (6+)
- Instrumentation checklist (30+ metrics)
- Alert rule definitions (Critical/Warning/Info)
- Performance overhead estimate

### Key Decisions to Make
- Scrape interval (15s vs. 30s?)
- Storage size needed (calculate based on metrics)
- Dashboard priority (which to build first?)
- Alert thresholds (OOM alert at 80%? 85%?)

---

## SESSION 6: AUTHENTICATION & AUTHORIZATION DESIGN

**Duration**: 2-3 hours | **Priority**: P0 | **Blocking**: Phase 5C execution

### Research Areas

#### 1. OAuth2 & JWT Architecture
- OAuth2 flow selection (Authorization Code + PKCE)
- JWT structure (claims, expiry times)
- Token refresh strategy
- External IdP prep (Auth0/Keycloak)

#### 2. API Key Management
- Key generation (UUID vs. random)
- Rotation policy (90 days default?)
- Scope-based permissions
- Rate limiting per key
- Audit logging

#### 3. RBAC Implementation
- Role definitions (user, admin, service, agent)
- Permission matrix (per-endpoint)
- Database schema
- Group management (future)

#### 4. FastAPI Integration
- Middleware for JWT validation
- Dependency injection vs. decorators
- Exception handling (401, 403)
- Rate limiting middleware

### Deliverables Expected
- OAuth2 flow diagram
- JWT token structure (JSON schema)
- API key generation script
- RBAC permission matrix (endpoints × roles)
- FastAPI implementation template
- Security audit checklist

### Key Decisions to Make
- JWT expiry time (15min vs. 1hour?)
- API key rotation frequency
- Store secrets in Redis vs. database?
- RBAC complexity (simple roles vs. fine-grained?)

---

## Quick Reference

### Fast Track: P0 Only (10 weeks)
**Minimum research**: Sessions 1-6 (complete all)  
**Minimum implementation**: Phases 5A-5E  
**Outcome**: Scholar MVP with 1,000+ texts

### Standard Track: P0 → P1 (24 weeks)
**First phase**: Sessions 1-6 (P0)  
**Second phase**: Sessions 7-11 (P1)  
**Outcome**: Ancient Greek mastery + academic credibility

### Full Track: All Research (36+ weeks)
**All sessions** 1-17 across all priorities  
**All phases** 5A-7E across all pillars  
**Outcome**: Complete modular scholar platform

---

## Success Criteria

All P0 research is successful when:
- ✅ All 6 sessions completed with documented findings
- ✅ Clear implementation paths for Phase 5A-5E
- ✅ No critical unknowns blocking implementation
- ✅ Team agrees on approach for each technology
- ✅ Vikunja tasks created for next phase

---

## Related Documents

- [← Back to RESEARCH-MASTER-INDEX](../RESEARCH-MASTER-INDEX.md)
- [PILLAR 1: Operational Stability](../roadmap-phases/PILLAR-1-OPERATIONAL-STABILITY.md)
- [Full Research Framework](../xoe-novai-research-phases-v2-COMPLETE.md)

---

**Status**: Complete P0 Research Framework  
**Last Updated**: February 12, 2026  
**Sessions Added**: 17 total (added Session 7: Cline CLI as P1)  
**Next**: Move to [P1 Research](RESEARCH-P1-SCHOLAR-DIFFERENTIATION.md) after P0 completion
