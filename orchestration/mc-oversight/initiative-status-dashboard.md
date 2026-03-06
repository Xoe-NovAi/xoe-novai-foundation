# XNAi Foundation — Initiative Status Dashboard
**Last Updated**: 2026-02-18 | **Session**: Opus-Sprint-001 | **Agent**: Claude Opus 4.6 (Cline)

---

## 🟢 Overall System Health: OPERATIONAL

```
Phase 1:  ✅ COMPLETE   (62/62 tests)
Phase 2:  ✅ COMPLETE   (19/19 tests)
Phase 3:  🟡 75%        (deps blocked → accepted, proceed to Phase 4)
Phase 4:  🔵 READY      (Integration Testing — next sprint)
Phase 5A: ✅ COMPLETE   (zRAM optimized)
Phase 6:  ⏳ PLANNED    (Observability + OAuth2)
```

---

## 📋 TASK-005 — Phase 3 Test Dependencies
**Status**: ✅ RESOLVED (Root Cause Identified)  
**Agent**: Claude Opus 4.6 (Cline) | **Date**: 2026-02-18

**Finding**: All dependencies (`redis`, `opentelemetry-exporter-prometheus`, `qdrant-client`) already exist in `requirements-api.in`. The issue is that they are not installed in the local test virtualenv.

**Fix**: `pip install redis opentelemetry-exporter-prometheus qdrant-client` in the test environment.  
**No file changes required** — requirements files are already correct.

---

## 🤖 TASK-021b — Sovereign MC Agent
**Status**: ✅ IMPLEMENTED  
**Agent**: Claude Opus 4.6 (Cline) | **Date**: 2026-02-18  
**File**: `app/XNAi_rag_app/core/sovereign_mc_agent.py`

**Architecture**:
- `MemoryBankReader` — reads/writes `memory_bank/*.md` for strategic context
- `VikunjaClient` — async httpx client → Vikunja REST API (localhost:3456)
- `QdrantMemory` — AsyncQdrantClient, collection `sovereign_mc_decisions`, dim 384
- `OpenCodeDispatcher` — spawns OpenCode CLI via `anyio.run_process`
- `SovereignMCAgent` — main orchestrator, AnyIO TaskGroups throughout

**Key compliance**: ZERO asyncio.gather, ZERO PyTorch — fully AnyIO + ONNX

---

## 🏗️ Active Initiatives (21 Tasks from STRATEGIC-REVIEW)

| ID | Initiative | Status | Owner | Sprint |
|----|-----------|--------|-------|--------|
| TASK-001 | Agent Bus stream key unification | 🟡 PENDING | Cline | Sprint 2 |
| TASK-002 | MCP server xnai-agentbus registration | 🟡 PENDING | Cline | Sprint 1 |
| TASK-003 | MCP server xnai-rag registration | 🟡 PENDING | Cline | Sprint 1 |
| TASK-004 | MCP server xnai-vikunja registration | 🟡 PENDING | Cline | Sprint 1 |
| TASK-005 | Phase 3 test deps install | ✅ RESOLVED | Cline | Sprint 0 |
| TASK-006 | Vikunja host port exposure | ✅ FIXED | Cline | Sprint 0 |
| TASK-007 | OpenCode guide asyncio.gather fix | 🟡 PENDING | Cline | Sprint 1 |
| TASK-008 | OpenCode guide Antigravity section | 🟡 PENDING | Cline | Sprint 1 |
| TASK-009 | Model matrix MC diagram correction | 🟡 PENDING | Cline | Sprint 1 |
| TASK-010 | Model matrix Antigravity models | 🟡 PENDING | Cline | Sprint 1 |
| TASK-011 | Model matrix OpenRouter rate limits | 🟡 PENDING | Cline | Sprint 1 |
| TASK-012 | Antigravity auth research doc | 🟡 PENDING | Cline | Sprint 1 |
| TASK-013 | Implementation Framework template | ✅ DONE | Cline | Sprint 0 |
| TASK-014 | Sprint Log template | ✅ DONE | Cline | Sprint 0 |
| TASK-015 | opencode.json config upgrade | ✅ DONE | Cline | Sprint 0 |
| TASK-016 | mc-oversight dashboard files (4x) | 🟡 IN PROGRESS | Cline | Sprint 1 |
| TASK-017 | Session sprint log | 🟡 PENDING | Cline | Sprint 1 |
| TASK-018 | Sovereign MC Agent spec doc | 🟡 PENDING | Cline | Sprint 1 |
| TASK-019 | memory_bank/activeContext.md update | 🟡 PENDING | Cline | Sprint 1 |
| TASK-020 | TASK-005 pip install command | ✅ RESOLVED | Cline | Sprint 0 |
| TASK-021b | Sovereign MC Agent implementation | ✅ DONE | Cline | Sprint 0 |

---

## 🔑 Critical Discoveries (This Session)

### 1. Antigravity Auth — FREE Frontier Models
- **Package**: `opencode-antigravity-auth@latest`
- **Access**: Google OAuth → FREE Claude Opus 4.5 Thinking, Sonnet 4.5, Gemini 3 Pro (1M), Gemini 3 Flash (1M)
- **Action**: User must run `opencode auth login` interactively
- **GLM-5 missed this entirely** — significant capability upgrade

### 2. Vikunja Port Not Exposed
- **Issue**: Vikunja container had no host port mapping → Sovereign MC Agent couldn't reach it
- **Fix**: Added `- "3456:3456"` to docker-compose.yml vikunja service ✅

### 3. Agent Bus Stream Key Inconsistency
- **core/agent_bus.py**: publishes to `xnai:agent_bus`
- **mcp-servers/xnai-agentbus/server.py**: publishes to `xnai:tasks`, reads from `xnai:results`
- **Action needed**: Unify to single stream key (TASK-001)

---

## 📊 Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Test Coverage | ~81% | 85% | 🟡 Near |
| RAM Footprint | 5.2GB | <6GB | 🟢 OK |
| Zero-Telemetry | 100% | 100% | 🟢 Perfect |
| Voice Latency | 250ms | <300ms | 🟢 OK |
| AnyIO Compliance | 100% | 100% | 🟢 Perfect |
| ONNX/GGUF Only | 100% | 100% | 🟢 Perfect |

---

*Dashboard owner: Claude Opus 4.6 (Cline) | Next review: Next agent session*
