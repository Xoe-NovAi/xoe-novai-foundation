# 🔱 STABILIZATION ANCHOR: SESS-26 MARATHON

**Status**: ACTIVE | **Mode**: Autonomous Marathon | **RAM Target**: <8GB Used

## ⚓ The Golden Path
This document serves as the ground truth for the Pioneer Agent (Gemini 3 Auto) during the SESS-26 Marathon. If context noise increases, return to this anchor.

### 1. Resource Constraints
- **Hardware**: 16GB RAM, 16GB zRAM.
- **Mandate**: OOM is failure. Hawksight on `free -h`.
- **Gating**: `ResourceHub` + `zram_monitor` must gate all ingestion.

### 2. Service Topology (Tier-1 Minimal)
- **Caddy**: ACTIVE (Port 8000).
- **RAG API**: ACTIVE (Internal :8002).
- **MCP**: ACTIVE (Internal).
- **Storage**: Redis, Postgres, Qdrant (ACTIVE).
- **Ingestion**: Library Curator (ACTIVE).

**Note**: Podman-compose is currently unstable for orchestration; all services are managed via Native Podman commands during this phase.

### 3. Current Objective: Hellenic Ingestion (Phase 4)
- [x] Create `ResourceHub` singleton.
- [x] Implement zRAM proactive gating.
- [x] Integrate Hub into `curation_worker.py`.
- [x] Integrate Hub into `hellenic_pipeline.py`.
- [x] Restore OpenCode CLI access.
- [x] Establish unified MCP Bridge (Port 8005).
- [x] Stabilize Ingestion Curator (Active/Listening).
- [ ] Begin mass ingestion of Technical Manuals.

**Refinement**: The orchestrator now uses Native Podman for 92%+ confidence in state stability.

## 🧠 Memory Pointers
- Root Protocol: `GEMINI.md`
- Roadmap: `plans/omega-epoch3-autonomous-marathon.md`
- Process Logs: `logs/ARCHON_REFLECTION.jsonl`
