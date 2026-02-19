# XNAi Foundation — Strategic Recommendations
**Last Updated**: 2026-02-18 | **Session**: Opus-Sprint-001 | **Agent**: Claude Opus 4.6 (Cline)

---

## Executive Summary

This session (Opus-Sprint-001) delivered the Sovereign MC Agent implementation, upgraded the OpenCode toolchain with Antigravity auth, fixed the Vikunja port blockage, and established the implementation framework for future autonomous sessions. Key strategic insight: **the XNAi Foundation stack is now self-directing-capable** pending three infrastructure unlocks.

---

## REC-001: Immediate — Unlock Antigravity Auth (User Action Required)
**Priority**: P0 | **Effort**: 2 minutes | **Impact**: MASSIVE

The `opencode-antigravity-auth@latest` plugin gives **free access** to:
- Claude Opus 4.5 Thinking (complex reasoning)
- Claude Sonnet 4.5 (balanced, fast)
- Gemini 3 Pro 1M context (research, large codebases)
- Gemini 3 Flash 1M context (fast, large context)

**Action**: Open terminal → run `opencode auth login` → complete Google OAuth flow.

This single 2-minute action unlocks a **4-model free frontier pool** that dramatically expands autonomous agent capability for zero ongoing cost.

---

## REC-002: Sprint 2 — Fix Agent Bus Stream Key Split (P0 Technical)
**Priority**: P0 Technical | **Effort**: 1 hour | **Impact**: Critical

The core AgentBus and MCP AgentBus are on different Redis streams. Until TASK-001 is executed, MCP tool routing and core application routing are completely separate.

**Recommended approach**: 
1. Standardize ALL streams to `xnai:agent_bus` (main), `xnai:agent_bus:results` (responses)
2. Update `mcp-servers/xnai-agentbus/server.py` to match
3. Update `sovereign_mc_agent.py` route_via_agent_bus to use unified key
4. Test end-to-end with a test task

---

## REC-003: Sprint 1 — Register MCP Servers in Cline (Quick Win)
**Priority**: P1 | **Effort**: 10 minutes | **Impact**: HIGH

Three MCP servers exist in `mcp-servers/` but are NOT registered in Cline's MCP settings. Until registered, Cline cannot use Agent Bus, RAG, or Vikunja tools natively.

**Action**: Add to `~/.config/VSCodium/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`:
- `xnai-agentbus` (node `mcp-servers/xnai-agentbus/server.py` via tsx)
- `xnai-rag` (node `mcp-servers/xnai-rag/server.py`)
- `xnai-vikunja` (node `mcp-servers/xnai-vikunja/server.py`)

---

## REC-004: Architecture — Deprecate memory_bank_integration.py
**Priority**: P2 | **Effort**: 2 hours | **Impact**: Medium

Two memory bank reading implementations now exist:
1. `core/memory_bank_integration.py` — basic event logger (OLD)
2. `sovereign_mc_agent.MemoryBankReader` — full structured context reader (NEW)

**Recommendation**: 
- Deprecate `memory_bank_integration.py`
- Extract `MemoryBankReader` to `core/memory_bank.py` as standalone module
- Migrate all callers to the new implementation
- This gives ALL services access to structured memory bank context

---

## REC-005: Architecture — Sovereign MC Auto-Boot on Stack Start
**Priority**: P2 | **Effort**: 4 hours | **Impact**: HIGH (enables true autonomy)

Currently `sovereign_mc_agent.py` is a library — it must be explicitly invoked. To enable the XNAi Foundation to "direct itself", the Sovereign MC Agent should start automatically with the stack.

**Recommendation**:
1. Create `app/XNAi_rag_app/services/sovereign_mc_service.py` as a FastAPI lifespan service
2. Start `SovereignMCAgent` in background on API startup
3. Expose `/mc/status`, `/mc/dispatch`, `/mc/context` REST endpoints
4. Register as Consul service `sovereign-mc` for health monitoring

---

## REC-006: Security — Rotate Vikunja JWT Secret
**Priority**: P1 | **Effort**: 5 minutes | **Impact**: HIGH (security)

Default JWT secret `changeme_jwt` is a security risk.

**Action**:
```bash
# Generate secure secret
python3 -c "import secrets; print(secrets.token_hex(32))"
# Add to .env file as VIKUNJA_JWT_SECRET=<generated value>
```

Ensure `.env` is in `.gitignore` (it is — already verified).

---

## REC-007: Sprint 3 — Write Sovereign MC Tests
**Priority**: P2 | **Effort**: 2 hours | **Impact**: Medium

`sovereign_mc_agent.py` has no tests. Given its role as the system's self-direction engine, tests are important.

**Recommended test coverage**:
- `test_memory_bank_reader` — mock filesystem reads
- `test_vikunja_client` — mock httpx responses
- `test_qdrant_memory` — mock AsyncQdrantClient
- `test_opencode_dispatcher` — mock anyio.run_process
- `test_sovereign_mc_orchestration` — full integration test (requires stack running)

---

## REC-008: Documentation — Consolidate Expert Knowledge (Ongoing)
**Priority**: P3 | **Effort**: Ongoing | **Impact**: Strategic

`expert-knowledge/` has become the primary knowledge repository but lacks:
- Index / table of contents
- Tagging system for quick retrieval
- Freshness tracking (some docs may be stale)

**Recommendation**: Assign this to the Documentation Excellence Initiative (already active). Add `expert-knowledge/` to the MkDocs internal build.

---

## Strategic Trajectory

```
NOW (Sprint 0-1):    Unlock Antigravity → Fix Agent Bus → Register MCPs
                     → Sovereign MC operational
                          ↓
NEAR TERM (Sprint 2-3): Integration Testing Phase 4 → Agent Bus unified
                         → Sovereign MC auto-boot service
                              ↓
MEDIUM TERM (Phase 4-5): Full autonomous operation → Qdrant migration complete
                          → Observability live
                               ↓
TARGET STATE: XNAi Foundation directs itself, audits itself,
              curates its own knowledge, and delegates to AI agents
              — all with zero telemetry, air-gap capable, sovereign.
```

---

*Recommendations owner: Claude Opus 4.6 (Cline) | Review: Per session or on major discovery*
