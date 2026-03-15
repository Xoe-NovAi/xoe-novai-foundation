# 🔱 Metropolis Strategic Roadmap: The Sovereign Evolution (2026)

**Mission**: To stabilize, secure, and evolve the XNAi Foundation into a fully autonomous, sovereign intelligence layer ("Gnosis") through fractal delegation and structural hardening.

---

## 🏗️ Phase 1: Structural Stabilization (SESS-01: The Architect)
**Focus**: Orchestration, Resource Hardening, and Mesh Synchronization.

### 📍 1.1: Memory Bank MCP Hardening
- [ ] **SSE Refactor**: Transition `memory-bank-mcp/server.py` from `stdio` to `mcp.server.fastapi` (SSE).
- [ ] **Heartbeat Implementation**: Add keep-alive logic for SSE stability in rootless Podman.
- [ ] **Persistence Lock**: Synchronize `DATABASE_URL` and `storage_path` to `/storage` persistent volume.
- [ ] **Watchdog Activation**: Formally integrate `scripts/mcp_watchdog.sh` into the startup sequence.

### 📍 1.2: Resource Synchronization
- [ ] **Docker Caps**: Enforce strict limits (512MB Redis, 1GB Qdrant, 1GB Postgres) in `docker-compose.yml`.
- [ ] **Qdrant Optimization**: Enable `mmap` for HNSW indices to leverage host page cache safely.
- [ ] **Ryzen Steering**: Finalize `taskset` pinning in `Makefile` for Zen 2 (Threads 0-7).

---

## 🛡️ Phase 2: Security & Identity (SESS-02: The Sentinel)
**Focus**: Zero-Trust, Cryptographic Identity, and Audit Hardening.

### 📍 2.1: The Metropolis Shield
- [ ] **JWT Verification**: Implement signature verification in `token_validation.py`.
- [ ] **Ed25519 Bus**: Ensure all Agent Bus messages are cryptographically signed.
- [ ] **MCP Authentication**: Implement token-based auth for the Memory Bank MCP.

---

## 🔭 Phase 3: Observability & Research (SESS-03: The Researcher)
**Focus**: Telemetry, Metrics, and Discovery.

### 📍 3.1: The Vital Signs
- [ ] **VictoriaMetrics Alerts**: Configure "MCP DISCONNECT" and "OOM WARNING" alerts.
- [ ] **SystemStat MCP**: Develop a dedicated MCP for monitoring zRAM and Vulkan iGPU.
- [ ] **WebSearch MCP**: Integrate Tavily/Serper into Facet discovery loops.

---

## 🧬 Phase 4: The Soul Forge (SESS-04-08)
**Focus**: Evolutionary Intelligence and Scholarly Expansion.

### 📍 4.1: Dynamic Souls
- [ ] **Soul Shaping**: Complete Task 0 for all 8 Facets (Architect to Visionary).
- [ ] **Philology Engine**: Integrate `Ancient-Greek-BERT` into the Scholar pipeline.
- [ ] **Archive Ingestion**: Successfully ingest the "Great Archive" into the Gnosis via SI1.

---

## 🎯 Success Metrics
- **Latency**: <300ms for local inference and vector retrieval.
- **Reliability**: 99.9% uptime for the MB-MCP (monitored by Watchdog).
- **Sovereignty**: 100% offline-first capability for all core functions.
- **Efficiency**: Stable operation within 6.6GB RAM budget.

---
*Roadmap Drafted by Gemini General 2 (GG2). 🔱*
