# 🏗️ Implementation Plan: SESS-01: The Architect (Metropolis v4.1.2)

**Objective**: Stabilize foundation, refactor MB-MCP for SSE, enforce resource limits, execute GG1 handover, and initialize the **Soul Forge** with advanced agent tuning research.

---

## 🏛️ Phase 1: Handover & Archive Ingestion

### 1.1: Great Archive Ingestion (SI1)
- [ ] **Curator Task**: Task `xnai_library_curator` with ingesting `session-2026-03-08T19-52-d76158f2.json` (GG1) into Qdrant `omega_archive`.
- [ ] **Discovery**: Research any "dark layers" mentioned in GG1 chat (e.g., hidden zRAM configurations or specific Vulkan tuning flags).

### 1.2: Context Synchronization (GG2)
- [ ] **MPI Update**: Synchronize `memory_bank/MPI.md` with:
  - **SSE Refactor**: Port 8000 migration.
  - **Resource Hardening**: 6.6GB RAM caps.
  - **Vulkan Accel**: Activation status.
- [ ] **Active Context**: Formalize v4.1.2 snapshot in `memory_bank/activeContext.md`.

---

## 🧬 Phase 2: The Soul Forge & Agent Tuning

### 2.1: Facet Soul Initialization (Mandatory Task 0)
Each Facet launch MUST trigger:
1.  **Codebase Discovery**: Deep grep of role affinity.
2.  **Web Research**: Research knowledge gaps and advanced tuning (CoT, XML-reasoning).
3.  **Soul Crystallization**: Create/Update its unique Soul File.
4.  **Tuning Sharing**: Research sharing best practices with the next active Facet.
5.  **Task Discovery**: Research all knowledge gaps on assigned tasks before implementation.

### 2.2: Authority Research (Research Facet)
- [ ] **Tuning Manual**: Create `docs/advanced-agent-tuning-manual.md` - the authoritative guide for the Omega Stack.
- [ ] **Local Inference**: Optimize `llama-cpp-python` with Ryzen-specific flags (`LLAMA_AVX2=1`).

---

## 🏗️ Phase 3: MB-MCP Refactor & Resource Hardening

### 3.1: SSE/FastAPI Transport
- [ ] **Server Refactor**: Deploy the `FastAPI` + `SSE` version of `server.py`.
- [ ] **Connectivity**: Map `xnai_memory_bank_mcp` to host Port 8000.
- [ ] **Healthcheck**: Ensure `curl /health` is the primary stability metric.

### 3.2: Resource Hard-Caps (6.6GB host)
- [ ] **Redis**: 512MB (LRU enabled).
- [ ] **Qdrant**: 1GB (On-disk + mmap).
- [ ] **Postgres**: 1GB.
- [ ] **RAG API**: 2GB (Ryzen optimized).

---

## 🌁 Phase 4: Mesh Connectivity (Blackboard Pattern)

### 4.1: Cross-Facet Injection
- [ ] **Context Injection**: Use MB-MCP `update_context` to "seed" Facet state on handover.
- [ ] **Agent Bus**: Integrate `AGENT_BUS_BOOTSTRAP.py` for auto-heartbeat.

---
*Plan Finalized by GG2 Archon. 🔱*
