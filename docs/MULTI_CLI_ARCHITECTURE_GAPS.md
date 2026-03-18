# 🔱 Multi-CLI Architecture Gap Analysis (SESS-26 Audit)
**Date**: Wednesday, March 18, 2026
**Status**: ACTIVE | **Target**: LLM Context Alignment

---

## 1. Executive Summary
This audit compares the "Sovereign Omega" target architecture (as documented) against the current filesystem reality. Significant progress has been made in the core `agent_bus` and `redis_streams` logic, but the high-level "Sync Layer" for the Memory Bank MCP is currently in a **Phase 2 Design** state.

---

## 2. Implemented vs. Planned Matrix

| Feature | Status | Location | Notes |
| :--- | :--- | :--- | :--- |
| **Redis Stream Manager** | ✅ IMPLEMENTED | `app/.../core/redis_streams.py` | Robust `AnyIO` implementation with DLQ and consumer groups. |
| **Agent Bus Client** | ✅ IMPLEMENTED | `app/.../core/agent_bus.py` | Supports IA2 signatures and heartbeats. |
| **Memory Bank Store** | ✅ IMPLEMENTED | `mcp-servers/.../memory_bank_store.py` | SQLite fallback with FTS5 indexing. |
| **Hybrid Storage** | ✅ IMPLEMENTED | `mcp-servers/.../server.py` | Redis Hashes + Filesystem fallback. |
| **Real-time Sync Layer** | ❌ PLANNED | N/A | Integration between `RedisStreamManager` and `MemoryBankMCP` is pending. |
| **Sync-On-Handoff (SOH)** | 🟡 PARTIAL | N/A | Protocol defined in docs; manual execution required via `/agent` scripts. |

---

## 3. Critical Knowledge Gaps & Technical Debt

### **A. Sync Integration Gap**
The `MemoryBankMCP` (`server.py`) successfully writes to Redis Hashes and the filesystem, but it **does not yet listen** to the `xnai:memory_updates` stream. 
- **Impact**: Changes made by one CLI tool are not "pushed" to others in real-time. 
- **Mitigation**: Tools must perform a "pull" (refresh) at the start of every session.

### **B. Python Version Friction**
- **Docker**: Strictly uses `3.12-slim`.
- **Host**: Currently running `3.13.7`.
- **Warning**: This causes `__pycache__` collisions (cpython-313 vs cpython-312).
- **Remedy**: Always run `find . -name "__pycache__" -exec rm -rf {} +` before building images.

### **C. MCP Incompatibility (Historical)**
Previous sessions reported "Memory Bank MCP Incompatibility". 
- **Finding**: Current `server.py` uses `mcp` library (v1.2.0+). 
- **Resolution**: Ensure the calling CLI (e.g., Gemini) uses the `stdio` transport if the `fastapi` SSE layer is unstable.

---

## 4. Immediate Roadmap (Phase 2)
1.  **Unify MCP & Stream Manager**: Update `memory-bank-mcp/server.py` to inherit from or utilize `AgentBusClient`.
2.  **Automated Handover**: Create a `scripts/handoff.py` that automates the generation of `artifacts/HANDOVER_*.md`.
3.  **Schema Hardening**: Align the `MemoryBankStore` (SQLite) schema exactly with the Redis Hash schema for parity.

---
**Audit Hash**: SESS-26.GAPS.V1
