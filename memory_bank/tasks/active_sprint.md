# 🏃 Active Sprint: Phase 3.0 — The Sovereign Gnosis (Metropolis Hardening)

**Status**: Active | **Start**: 2026-03-08 | **Author**: Facet 1 (Omega-Stack Coordinator)

## 🎯 Current Objectives
1.  **Harden Intelligence**: Complete 'The Sovereign Upgrade' of the Memory Bank MCP.
2.  **Activate Telepathy**: Enable A2A Handshake between Facets.
3.  **Secure Storage**: Reclaim another 5GB+ from caches and old layers.
4.  **Metropolis Stability**: Finalize Jaeger telemetry and Llama Server robustness.
5.  **Memory Guard**: Implement Chat Trimming to prevent OOM.

## 📋 Task List

| ID | Task | Owner | Priority | Status |
| :--- | :--- | :--- | :--- | :--- |
| PM-001 | Implement Pydantic Schema in MB-MCP | General | Critical | ✅ Done |
| PM-002 | Implement A2A Handshake in MB-MCP | General | High | ✅ Done |
| SESS-14 | Stabilize Llama Server & Mesh Standards | Facet 1 | High | ✅ Done |
| SESS-14b| Configure OTLP to Jaeger & Registry | Facet 1 | High | ✅ Done |
| SESS-15 | Implement Chat Trimming Protocol | Facet 1 | Critical | ⏳ Pending |
| SESS-15.b | Verify & Benchmark KV Cache Optimization (n_ctx=32k, q4_0) | Facet 1 | High | ⏳ Pending |
| PM-003 | Rebuild MB-MCP Podman Image | General | High | ⏳ Pending |
| PM-004 | Create Sentinel Prototype (Python) | General | Medium | ⏳ Pending |
| PM-005 | Deep Storage Sweep (~/.cache, ~/.npm) | General | Medium | 🔮 Planned |

## 🚧 Blockers
- **RAM Constraints**: 6.6GB limit. History bloat in Node.js services is a risk.
- **Image Size**: `xnai-ui` and others are approaching the 2GB danger zone.

## 🗒️ Notes
- SESS-14 successfully recovered `llama_server` and established mesh standards.
- SESS-15 will focus on "Chat Trimming" to ensure long-running sessions don't crash the host.
