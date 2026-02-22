# XNAi Foundation — Risk Assessment
**Last Updated**: 2026-02-18 | **Session**: Opus-Sprint-001 | **Agent**: Claude Opus 4.6 (Cline)

---

## Risk Classification

| Severity | Label | Description |
|----------|-------|-------------|
| 🔴 CRITICAL | System-breaking or data-loss risk |
| � HIGH | Major functional degradation |
| 🟡 MEDIUM | Partial capability loss or compliance concern |
| 🟢 LOW | Minor, well-mitigated |

---

## Active Risks

### RISK-001 — Agent Bus Stream Key Split 🔴 CRITICAL
**Description**: `core/agent_bus.py` publishes to `xnai:agent_bus` but `mcp-servers/xnai-agentbus/server.py` publishes to `xnai:tasks` and reads from `xnai:results`. These streams never connect.  
**Impact**: MCP Agent Bus tools and core application are completely decoupled — task routing fails silently.  
**Likelihood**: HIGH (already broken)  
**Mitigation**: Unify to `xnai:agent_bus` in TASK-001 (next sprint).  
**Owner**: Cline | **Target**: Sprint 2

---

### RISK-002 — GLM-5 asyncio.gather in OpenCode Guide 🟠 HIGH
**Description**: The multi-agent orchestration example in `expert-knowledge/OPENCODE-CLI-COMPREHENSIVE-GUIDE-v1.0.0.md` uses `asyncio.gather()` — which is banned per XNAi AnyIO-only policy and breaks under AnyIO backends (trio).  
**Impact**: Any agent or developer following the guide will introduce concurrency bugs.  
**Likelihood**: HIGH (guide is actively used)  
**Mitigation**: Replace with AnyIO TaskGroup pattern (TASK-007 — pending this session).  
**Owner**: Cline | **Target**: Sprint 1

---

### RISK-003 — Vikunja PUBLICURL Mismatch 🟡 MEDIUM
**Description**: `VIKUNJA_SERVICE_PUBLICURL` is set to `http://localhost:8000/vikunja` (through Caddy) but the Sovereign MC Agent uses direct `localhost:3456` access. If Caddy routing for `/vikunja` is not configured, the UI will not function.  
**Impact**: Vikunja UI inaccessible through Caddy, but API still works via port 3456.  
**Likelihood**: MEDIUM (depends on Caddyfile config)  
**Mitigation**: Verify Caddyfile has `/vikunja` reverse proxy entry. Port 3456 direct access is now enabled.  
**Owner**: Human Director | **Target**: Next stack restart

---

### RISK-004 — Sovereign MC Agent Qdrant Collection Init 🟡 MEDIUM
**Description**: `QdrantMemory` in `sovereign_mc_agent.py` calls `recreate_collection` if it doesn't exist. If Qdrant is not running when the agent starts, the factory function raises and the agent fails to initialize.  
**Impact**: Sovereign MC Agent unusable if Qdrant not healthy.  
**Likelihood**: LOW in production (Qdrant has healthcheck), MEDIUM in dev.  
**Mitigation**: Factory function `create_sovereign_mc()` should catch `QdrantException` and continue with degraded mode. Add retry logic.  
**Owner**: Cline | **Target**: Sprint 2 (post-stabilization)

---

### RISK-005 — Memory Bank Integration Is Stub 🟡 MEDIUM
**Description**: `app/XNAi_rag_app/core/memory_bank_integration.py` is a basic event logger, NOT the full MemoryBankReader pattern implemented in `sovereign_mc_agent.py`. Two divergent implementations exist.  
**Impact**: Any module using the old `memory_bank_integration.py` gets degraded context reading.  
**Likelihood**: MEDIUM (module is imported by other services)  
**Mitigation**: Deprecate `memory_bank_integration.py`, migrate callers to `sovereign_mc_agent.MemoryBankReader`.  
**Owner**: Cline | **Target**: Sprint 3

---

### RISK-006 — Vikunja JWT Secret Default 🟠 HIGH
**Description**: `VIKUNJA_JWT_SECRET` defaults to `changeme_jwt` in docker-compose.yml. If never changed, any party can forge Vikunja JWTs.  
**Impact**: Authentication bypass for project management system.  
**Likelihood**: MEDIUM (dev env), LOW (production should set env var)  
**Mitigation**: Add to `.env.example`, enforce via startup check in sovereign agent.  
**Owner**: Human Director | **Target**: Before production deployment

---

### RISK-007 — Phase 3 Tests Blocked 🟢 LOW (Managed)
**Description**: Test environment missing `redis`, `opentelemetry-exporter-prometheus`, `qdrant-client`.  
**Impact**: Phase 3 tests cannot run locally.  
**Likelihood**: ALREADY OCCURRED — managed risk  
**Mitigation**: Root cause identified. Fix: `pip install redis opentelemetry-exporter-prometheus qdrant-client`. Dependencies already in `requirements-api.in`.  
**Owner**: Cline/Human Director | **Target**: Current session

---

### RISK-008 — OpenCode Antigravity Auth Not Configured 🟢 LOW (User Action)
**Description**: `opencode-antigravity-auth@latest` plugin is configured in `.opencode/opencode.json` but Google OAuth hasn't been run yet.  
**Impact**: Antigravity free model pool (Opus 4.5 Thinking, Sonnet 4.5, Gemini 3 Pro/Flash) unavailable.  
**Likelihood**: Will remain unavailable until user runs `opencode auth login`.  
**Mitigation**: User action only. Local Ollama models (`qwen2.5:7b`) available as fallback.  
**Owner**: Human Director | **Target**: User's convenience

---

## Risk Trend

```
RISK-001 (Agent Bus)     ████████████ CRITICAL - unchanged
RISK-002 (asyncio)       ██████████   HIGH      - pending fix this session
RISK-003 (Vikunja URL)   ████████     MEDIUM    - new discovery this session
RISK-004 (Qdrant init)   ████████     MEDIUM    - new (from sovereign_mc impl)
RISK-005 (MB stub)       ██████       MEDIUM    - pre-existing
RISK-006 (JWT secret)    ██████████   HIGH      - pre-existing, needs attention
RISK-007 (tests)         ████         LOW       - resolved
RISK-008 (Antigravity)   ██           LOW       - user action required
```

---

## Security Posture (No Change)
- ✅ Zero-telemetry maintained  
- ✅ Rootless Podman  
- ✅ UID 1001 non-root  
- ✅ Read-only containers where applicable  
- ⚠️ Vikunja JWT default secret — must be rotated before production  

---

*Risk register owner: Claude Opus 4.6 (Cline) | Review cycle: Per session*
