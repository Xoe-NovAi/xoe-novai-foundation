---
document_type: report
title: MPI BACKUP 20260314
created_by: Haiku-4.5 (Phase 2C Automation)
created_date: 2026-03-14
version: 1.0
status: active
hash_sha256: 9b0943e314e70864d39efd7dfe01f56340622d3142c4cb04f40a901c6d79d6c4
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
| **Metropolis Caps**| ✅ ACTIVE | Enforced 6.6GB RAM + 16GB zRAM budget across stack. | `infra/docker/docker-compose.yml` |
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
