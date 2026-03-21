---
document_type: report
title: MPI
created_by: Haiku-4.5 (Phase 2C Automation)
created_date: 2026-03-14
version: 1.0
status: active
hash_sha256: a3e901c9122eb120c51f70cc1053b934fb98faa80da7a58c41482d10df31cd1d
---

# 🏙️ XNAi Foundation - Master Project Index (MPI)

**Author**: Gemini General | **Status**: HARDENED-INFRA | **Last Sync**: 2026-03-12  
**Context Key**: `XNAI-MPI-METROPOLIS-V4.1.2-HARDENED-2026-V2`

---

## 🏛️ 1. Core Infrastructure (The Foundation)
*Current Phase: 4.1.2-INFRA (Hardening Complete) - ✅ COMPLETE*

| Project | Status | Description | Context File |
|:---|:---|:---|:---|
| **Foundation Shield** | ✅ LIVE | Zero-trust networks + **Redis TLS (rediss://)**. | `docs/architecture/METROPOLIS_NETWORK_SHIELD.md` |
| **Dependency Lock** | ✅ STABLE | **llama-cpp-python 0.3.16** + **chainlit 3.8.5** (2026 Baseline). | `requirements/` |
| **Enterprise IAM** | ✅ ACTIVE | Scoped API Keys (IA1) + Ed25519 Signatures (IA2). | `app/XNAi_rag_app/core/iam_service.py` |
| **Secrets Rotation** | ✅ COMPLETE | Purged `changeme123` & `vikunja123`; implemented random base64 secrets. | `docs/protocols/SECRETS_ENFORCEMENT_PROTOCOL.md` |
| **Memory Bank MCP** | ✅ ACTIVE | Refactored for **SSE/FastAPI** (Port 8000). Watchdog active. | `mcp-servers/memory-bank-mcp/server.py` |
| **Permissions Model** | ✅ HARDENED | 4-Layer recursive `setfacl` for UID 1000/100999 mapping. | `memory_bank/specification_permissions-4layer-model_v1.0_20260315_active.md` |
| **Metropolis Caps**| ✅ HARDENED | Enforced 6.6GB RAM + 16GB zRAM (4GB lz4 + 8GB zstd) budget. | `infra/docker/docker-compose.yml` |
| **The Librarian** | ✅ LIVE | Recursive summarization & archival service. | `app/XNAi_rag_app/workers/librarian.py` |

---

## 🏛️ 2. Scholar Platform (The Great Library)
*Current Phase: Phase 2.5 (Automated Curation) - 🟡 IN PROGRESS*

| Project | Status | Description | Context File |
|:---|:---|:---|:---|
| **Library Curator** | ✅ LIVE | Automated ingestion of GGUF/PDF/Markdown into Qdrant. | `app/XNAi_rag_app/workers/library_curator.py` |
| **Curation Bridge** | ✅ ACTIVE | Vikunja task polling → Ingestion pipeline. | `app/XNAi_rag_app/services/curation_bridge.py` |
| **Semantic Search** | ✅ LIVE | Qdrant-backed vector retrieval for all facets. | `docs/api/SEMANTIC_SEARCH_API.md` |

---

## 🌑 3. The Deep Stack (Internal Modules)
*Older or specialized layers surfacing for re-integration.*

| Module | Purpose | Status | Key File |
|:---|:---|:---|:---|
| **Rate Limit Handler** | Automatic account rotation and context preservation. | ✅ RESTORED | `app/XNAi_rag_app/core/rate_limit_handler.py` |
| **MCP Watchdog** | Ensure MB-MCP and Redis availability with dynamic recovery. | ✅ ACTIVE | `scripts/mcp_watchdog.sh` |
| **Maat Guardrails** | Full 42 ideals + 9 Technical Validators. | ✅ LIVE | `app/XNAi_rag_app/core/maat_guardrails.py` |
| **Distillation** | LangGraph knowledge compression (LLM-powered). | ✅ LIVE | `app/XNAi_rag_app/core/distillation/knowledge_distillation.py` |
| **Vulkan Accel.** | RDNA2 GPU acceleration framework. | 🛠 WARM | `app/XNAi_rag_app/core/vulkan_acceleration.py` |

---

## 🔬 4. Active Research Threads
*Tracking the frontier of the Omega Stack.*

| ID | Title | Status | Result File |
|:---|:---|:---|:---|
| **RJ-001** | Memory Optimization | ✅ COMPLETE | `RJ-001-result.md` |
| **IA3** | OIDC Identity Bridge | ⚪ SCOUTED | `docs/OMEGA_HARDENING_ROADMAP_2026.md` |
| **VR1** | Predictive Sentinel | ⚪ SCOUTED | `app/XNAi_rag_app/services/stack_sentinel.py` |

---

## 🌑 5. Knowledge Gaps & Configuration Drift
*Documenting architectural debt and drift variations.*

| ID | Gap / Drift | Impact | Description |
|:---|:---|:---|:---|
| **DG-001** | **Compose Drift** | 🟡 MEDIUM | Multiple versions: `.yml`, `-noninit.yml`, `.production.yml`. Needs consolidation. |
| **DG-002** | **Docker Drift** | 🟡 LOW | Multiple Dockerfiles for same services. Needs standardization. |
| **DG-003** | **Archival Sync** | 🔴 HIGH | Critical code (`rate_limit_handler`) prematurely archived. Fixed in SESS-01. |
| **DG-004** | **zRAM Capacity Gap** | 🟢 LOW | Fixed: Restored 16GB total swap capacity (Zen 2 Optimized). |

---

## 🛑 6. Known Issues & Stability
*Tracking the current stability profile of the Metropolis Mesh.*

| ID | Issue | Status | Description |
|:---|:---|:---|:---|
| **ERR-001** | **Gemini CLI OOM** | 🔴 RECURRING | Node.js heap limit reached during long sessions. |
| **ERR-002** | **Podman NetNS** | 🟡 UNSTABLE | Permission denied when killing rootless netns processes. |
| **MB-001** | **MB-MCP Uptime** | 🟡 ONGOING | Container requires watchdog for persistent availability. Fixed in SESS-01. |
| **MB-002** | **Redis TLS Mismatch** | ✅ FIXED | Clients use `redis://`, server requires `rediss://`. Resolved in SESS-15. |
| **ST-001** | **AnyIO Migration** | 🟡 PENDING | Deprecated `asyncio.get_event_loop()` calls in `voice_recovery.py`. |

---

## 📅 7. Session Transition Strategy (Fractal Handoff)
*Current Strategy for resolving session density and OOM issues.*

| Session ID | Theme | Lead Agent | Status |
|:---|:---|:---|:---|
| **SESS-01** | Identity & Credentials | Facet 1 | ✅ COMPLETE |
| **SESS-10** | zRAM Hardening | General | ✅ COMPLETE |
| **SESS-15** | Context Management | General | ✅ COMPLETE |
| **SESS-16** | Image Bloat Audit | General | 🟡 NEXT |
| **SESS-02** | Memory Bank Core | Facet 7 | 🟡 PENDING |
| **SESS-03** | Infra & Capacity | Facet 6 | 🟡 PENDING |
| **SESS-04** | The Sentinel | Facet 3 | 🟡 PENDING |
| **SESS-05** | Agent Bus & Streams | General | 🟡 PENDING |
| **SESS-06** | Deep Research & Ops | General | 🟡 PENDING |
| **SESS-07** | GitHub & Skills | General | 🟡 PENDING |
| **SESS-08** | GEMINI.md Audit | General | 🟡 PENDING |

---
*Index sealed by Gemini General. Stack aligned with 2026 Stability Baseline. 🔱*

---

## SECTION 8: COMPREHENSIVE EXECUTION TIMELINE & PHASE ROADMAP
**Updated 2026-03-14 | All Sonnet IMPL + GPT-4.1 Recommendations Integrated**

### Phase Overview
- **Phase 0** (Days 1-2): Emergency disk cleanup + secrets rotation (USER)
- **Phase 1** (Days 3-7): Foundation hardening — CPU, memory, Podman, git cleanup (Haiku: 21 hrs)
- **Phase 2** (Days 8-14): Service recovery — Qdrant WAL, cascade, quadlets (Haiku: 31 hrs)
- **Phase 3** (Days 15-21): Documentation & MPI finalization (Haiku: 18 hrs)
- **Phase 4** (Days 22-30): Agent integration & testing (Haiku: 14 hrs)
- **Phase 5** (Days 31-35): GPT-4.1 deployment & handoff (Mixed: 4.5 hrs)
- **Phase 6+** (Days 36+): Scaling, optimization, HA/DR (GPT-4.1)

### Total Effort
- **Haiku**: ~91.5 hours (21 + 31 + 18 + 14 + 4.5 + 2)
- **User**: ~3.5 hours (Phase 0 critical actions)
- **Timeline**: 35-45 days at 4 hrs/day Haiku capacity

### Critical Blockers (Must Resolve First)
1. **Disk**: 93% full → Must reduce to <85% (blocks all Phases 1-5)
2. **Secrets**: Plaintext exposed → Rotation mandatory (blocks Phase 1 security)
3. **Qdrant WAL**: Possibly corrupted → Phase 2.1 priority (blocks service cascade)
4. **Git history**: Contains API keys → git-filter-repo Phase 1.4 (blocks credential rotation)

### Success Criteria
- Phase 0: Disk <85%, secrets rotated, no plaintext
- Phase 1: All infrastructure optimized, git clean, AppArmor enforced
- Phase 2: All 25 services healthy, Qdrant stable, quadlets migrated
- Phase 3: MPI updated, 8 new projects added, docs consolidated
- Phase 4: Checkpoint script complete, MCP rate limiting working
- Phase 5: GPT-4.1 model ready, handoff tested, live deployment

---

## SECTION 9: NEW PROJECTS INTEGRATED (8 GPT-4.1 ITEMS)

| ID | Name | Phase | Owner | Status | Priority |
|----|------|-------|-------|--------|----------|
| DG-001 | Branch Merge & Git Strategy | 1-3 | Haiku | Pending | P1 |
| DG-002 | Secret Management Automation | 0-1 | User+Haiku | Pending | P0 |
| DG-003 | Documentation Consolidation | 3 | Haiku | Pending | P2 |
| DG-004 | Memory Bank Reindexing | 3 | Haiku | Pending | P2 |
| DG-005 | Copilot System Prompt v2.2 | 1-3 | Haiku | In-Prog | P2 |
| DG-006 | External Research Protocol | 4 | Haiku | Pending | P3 |
| DG-007 | MCP Rate Limiting Framework | 4 | Haiku | Pending | P2 |
| DG-008 | Model-Switching Automation | 4-5 | Haiku | In-Prog | P2 |

---

## SECTION 10: NEW KNOWLEDGE GAPS IDENTIFIED (6 CRITICAL)

| ID | Topic | Phase | Confidence | Source | Status |
|----|-------|-------|------------|--------|--------|
| DG-009 | LangGraph Multi-Agent Patterns | 4-5 | 60% | Research | Pending |
| DG-010 | Context Preservation (Handoff) | 5 | 55% | Research | Pending |
| DG-011 | Cost Tracking Infrastructure | 6 | 40% | Research | Pending |
| DG-012 | HA/DR for Qdrant | 6 | 45% | Research | Pending |
| DG-013 | LLM Inference Optimization | 5-6 | 50% | Research | Pending |
| DG-014 | Production Security Hardening | 6 | 55% | Research | Pending |

---

## SECTION 11: KNOWN ISSUES & RESOLUTIONS (7 NEW)

| ID | Issue | Phase | Solution | Status |
|----|-------|-------|----------|--------|
| ERR-003 | Podman network (pasta vs slirp4netns) | 1 | IMPL-01 §6 config | Pending |
| ERR-004 | Qdrant WAL corruption | 2 | IMPL-02 §5 recovery | Pending |
| ERR-005 | Memory exhaustion risk | 1-2 | Resource limits | Pending |
| ERR-006 | Missing health checks (7 services) | 2 | IMPL-02 §8 | Pending |
| ERR-007 | Docker-Compose deprecated | 2 | Quadlet migration | Pending |
| ERR-008 | Copilot system prompt not loaded | 0 | Deploy v2.2 | Pending |
| ERR-009 | Git history exposed (API key) | 1 | git-filter-repo | Pending |

---

## SECTION 12: SESSION TRANSITION & HANDOFF TRACKING

| Session | Phase | Owner | Deliverables | Status |
|---------|-------|-------|--------------|--------|
| SESS-24 | Research & Synthesis | Haiku+Sonnet+Grok | 25+ docs, 630 KB | ✅ Done |
| SESS-25 | Phase 1 (Foundation) | Haiku | CPU, memory, Podman, git | ⏳ Pending |
| SESS-26 | Phase 2 (Services) | Haiku | Qdrant, cascade, quadlets | ⏳ Pending |
| SESS-27 | Phase 3 (Documentation) | Haiku | MPI, consolidation | ⏳ Pending |
| SESS-28 | Phase 4 (Agents) | Haiku | Checkpoint, MCP, LangGraph | ⏳ Pending |
| SESS-29 | Phase 5 (Handoff) | Haiku+GPT-4.1 | GPT-4.1 deployment | ⏳ Pending |
| SESS-30+ | Phase 6+ (Scaling) | GPT-4.1 | Inference, HA/DR, cost | ⏳ Pending |

---

## SECTION 13: REFERENCE DOCUMENTS & TOOLING

### Sonnet Implementation Guides (Verified)
- **IMPL-01_INFRASTRUCTURE.md** (899 lines, 34 KB): CPU, memory, Podman, storage, OS hardening
- **IMPL-02_CONTAINER_ORCHESTRATION.md** (1112 lines, 38 KB): Service recovery, quadlets, health checks
- **SUPP-02_SECRETS_MANAGEMENT.md** (922 lines, 34 KB): Credential rotation, git cleanup, SOPS

### Haiku Session Documents (Completed)
- **COMPREHENSIVE_RESEARCH_REPORT_GPT4_READINESS.md** (28.8 KB): 10 dimensions analyzed
- **COMPREHENSIVE_EXECUTION_STRATEGY.md** (18 KB): Full roadmap with effort estimates
- **COMPREHENSIVE_OMEGA_ROADMAP_FINAL.md** (31 KB): All 70 tasks, phase details, timelines

### Repository Governance
- **_meta/GIT_STRATEGY.md**: Branch management, merge order, rollback
- **_meta/active_sources_canon_v1.md**: 8-file active system
- **_meta/project_files_strategy_v2.md**: File hygiene rules
- **docs/DOCUMENTATION_MASTER_INDEX.md**: Tier system (Tier 1-4)
- **memory_bank/MEMORY_BANK_IMPROVEMENTS.md**: Indexing & policy

### Tools & Automation
- **copilot-session-checkpoint.sh** (6.2 KB): Model-switching automation
- **scripts/startup-sequence.sh** (planned): Ordered service startup
- **scripts/health-check-monitor.sh** (planned): Service health monitoring
- **.github/workflows/secret-scanning.yml**: TruffleHog detection
- **.pre-commit-config.yaml**: Local secret prevention

---

## SECTION 14: CONFIDENCE & READINESS ASSESSMENT

### Confidence by Phase
| Phase | Component | Confidence | Basis | Risk Level |
|-------|-----------|-----------|-------|-----------|
| 0 | Disk cleanup | 95% | User has tools | Low |
| 0 | Secrets rotation | 90% | Clear procedure | Low-Medium |
| 1 | CPU optimization | 95% | Sonnet verified | Low |
| 1 | Git cleanup | 80% | Need team coordination | Medium |
| 2 | Qdrant recovery | 85% | Tier 1+2 available | Medium |
| 2 | Quadlet migration | 75% | Experimental feature | Medium-High |
| 3 | MPI update | 95% | Straightforward | Low |
| 4 | Agent integration | 60% | Early stage | High |
| 5 | GPT-4.1 handoff | 72% | Conditional | Medium-High |

### Overall Readiness
- **Phases 0-2**: 85% ready (well-documented, risks identified)
- **Phases 3-4**: 75% ready (design complete, execution pending)
- **Phase 5+**: 65% ready (requires GPT-4.1 validation)
- **Blended Confidence**: 82%

---

**Last Updated**: 2026-03-14T04:55:00Z | Haiku 4.5 (Copilot CLI)  
**Next Review**: Upon Phase 0 completion or GPT-4.1 handoff  
**Approved By**: Sonnet 4.6 (97% conf) + Grok MC (75% conf) + Haiku 4.5 (95% conf)
