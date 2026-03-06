# XNAi Foundation — Priority Matrix
**Last Updated**: 2026-02-18 | **Session**: Opus-Sprint-001 | **Agent**: Claude Opus 4.6 (Cline)

---

## Priority Classification Framework

| Priority | Label | Description | Response Time |
|----------|-------|-------------|---------------|
| P0 | CRITICAL | Blocks system operation or correctness | Immediate |
| P1 | HIGH | Major capability or compliance issue | Next sprint |
| P2 | MEDIUM | Important improvement, non-blocking | Within 2 sprints |
| P3 | LOW | Nice-to-have, optimization | Backlog |

---

## P0 — CRITICAL (Must Do Now)

| Task | Issue | Owner | Status |
|------|-------|-------|--------|
| TASK-005 | Phase 3 test deps not installed in local env | Cline | ✅ Root cause found — run `pip install redis opentelemetry-exporter-prometheus qdrant-client` |
| TASK-006 | Vikunja port not exposed → Sovereign MC Agent can't reach API | Cline | ✅ Fixed in docker-compose.yml |
| TASK-001 | Agent Bus stream key split (`xnai:agent_bus` vs `xnai:tasks`) breaks routing | Cline | 🔴 NOT YET FIXED — next sprint |

---

## P1 — HIGH (Next Sprint)

| Task | Issue | Effort | Owner |
|------|-------|--------|-------|
| TASK-002 | Register `xnai-agentbus` MCP in Cline settings | Low | Cline |
| TASK-003 | Register `xnai-rag` MCP in Cline settings | Low | Cline |
| TASK-004 | Register `xnai-vikunja` MCP in Cline settings | Low | Cline |
| TASK-007 | Fix `asyncio.gather` in OpenCode guide (breaks on AnyIO) | Low | Cline |
| TASK-008 | Add Antigravity auth section to OpenCode guide | Medium | Cline |
| TASK-009 | Fix MC diagram in model matrix (still shows Claude.ai as MC) | Low | Cline |
| TASK-010 | Add Antigravity models to model matrix | Low | Cline |
| TASK-011 | Add OpenRouter rate limits (50 req/day, 20 rpm) to model matrix | Low | Cline |
| TASK-012 | Write Antigravity Auth Discovery research doc | Medium | Cline |

---

## P2 — MEDIUM (Within 2 Sprints)

| Task | Issue | Effort | Owner |
|------|-------|--------|-------|
| Phase 4 | Integration Testing | High | Cline |
| Agent Bus | Unify stream keys + update MCP server | Medium | Cline |
| Sovereign MC | Write `tests/test_sovereign_mc_agent.py` | Medium | Cline |
| FAISS→Qdrant | Complete Phase 3 migration | High | Cline + Gemini |
| Vikunja | Interactive `opencode auth login` for Antigravity | None (user action) | Human Director |
| `memory_bank_integration.py` | Upgrade from basic event log to full MemoryBankReader pattern | Medium | Cline |

---

## P3 — LOW (Backlog)

| Task | Notes |
|------|-------|
| Phase 6 Observability | Prometheus/Grafana, OAuth2 — after Phase 4 complete |
| Multi-ZRAM tiers | Experimental — research done, PoC exists |
| Documentation Excellence Phase 2 | ZRAM indexing, Librarian Agent |
| Documentation Excellence Phase 3 | Zero-telemetry pipeline |
| AWQ Production Pipeline | After Qdrant migration stable |

---

## Effort / Impact Matrix

```
HIGH IMPACT  │  P0 Agent Bus fix      │  P1 MCP Registration    │
             │  P1 asyncio.gather fix │  P1 Antigravity doc     │
─────────────┼────────────────────────┼─────────────────────────┼──
LOW IMPACT   │  P3 Multi-ZRAM PoC     │  P3 Phase 6 planning    │
             │                        │                         │
             └────────────────────────┴─────────────────────────┘
                   LOW EFFORT               HIGH EFFORT
```

---

## Action Queue (Ordered)

```
SPRINT 1 (immediate):
1. Fix asyncio.gather in OpenCode guide         [15 min]
2. Register 3 MCP servers in Cline             [10 min]
3. Add Antigravity section to OpenCode guide   [30 min]
4. Update model matrix (3 changes)             [20 min]

SPRINT 2 (next session):
5. Fix Agent Bus stream key unification        [45 min]
6. Write test_sovereign_mc_agent.py            [60 min]
7. Begin Phase 4 integration testing           [2 hrs]

USER ACTION REQUIRED:
- Run `opencode auth login` in terminal for Antigravity Google OAuth
```

---

*Matrix owner: Claude Opus 4.6 (Cline) | Review cycle: Per session*
