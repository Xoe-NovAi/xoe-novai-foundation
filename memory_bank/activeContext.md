# XNAi Foundation — Active Context

> **Last updated**: 2026-02-19 (Sprint 7 complete)
> **Current agent**: OpenCode CLI (Antigravity) — model: `claude-opus-4-6-thinking`
> **Handover doc**: `memory_bank/activeContext/sprint-7-handover-2026-02-19.md`

---

## Current Sprint Status

| Sprint | Status | Summary |
|--------|--------|---------|
| Sprint 1 | ✅ Complete | Foundation bootstrap |
| Sprint 2 | ✅ Complete | Core infrastructure |
| Sprint 3 | ✅ Complete | RAG pipeline |
| Sprint 4 | ✅ Complete | Sovereign MC agent spec |
| Sprint 5 | ✅ Complete | Systematization layer (configs, protocols, scripts, Python modules) |
| Sprint 6 | ✅ Complete | Corrections: model sigs, Antigravity taxonomy, OpenCode active status |
| **Sprint 7** | ✅ **Complete** | Research (Crush/iFlow/Cerebras), Opus onboarding, context engineering benchmark |

---

## Authoritative Agent Taxonomy (ENFORCED)

```
IDE Agent:
  Cline (VSCodium Extension)
    model: claude-sonnet-4-6
    account: arcana-novai
    context: 200K (shadow 400K unconfirmed)

Terminal Agents:
  OpenCode CLI — PRIMARY TUI — ACTIVE (fork planned: arcana-novai/opencode-xnai)
    └─ Antigravity Auth Plugin (opencode-antigravity-auth@latest)
         TYPE: OAuth plugin inside OpenCode — NOT a separate CLI
         AUTH: GitHub OAuth (NOT Google OAuth)
         MODELS: claude-sonnet-4-6, claude-opus-4-5-thinking, gemini-3-pro (1M), gemini-3-flash (1M)
    └─ Built-in Free Models (no auth):
         big-pickle (200K), kimi-k2.5-free (262K), gpt-5-nano (400K),
         minimax-m2.5-free (204K), glm-5-free (200K)
  Gemini CLI — Google OAuth, 1M context, search grounding
  GitHub Copilot CLI — GitHub OAuth, code/PR focus
  llama-cpp-python — Sovereign local, Vulkan/RDNA2, no network
```

**Registry**: `configs/agent-identity.yaml`
**Taxonomy diagram**: `docs/architecture/XNAI-AGENT-TAXONOMY.md`

---

## Sprint 7 — What Was Completed

### Session 1: New Tools Research (Cline, 2026-02-18)

1. ✅ **Crush/Charm ecosystem research**: `expert-knowledge/research/CRUSH-CHARM-ECOSYSTEM-2026-02-18.md`
2. ✅ **Cerebras & SambaNova research**: `expert-knowledge/research/CEREBRAS-SAMBANOVA-PROVIDER-2026-02-18.md`
3. ✅ **iFlow CLI research**: `expert-knowledge/research/IFLOW-CLI-ANALYSIS-2026-02-18.md`
4. ✅ **free-providers-catalog.yaml** updated to v1.1.0
5. ✅ **XNAI-AGENT-TAXONOMY.md** updated to v1.1.0

### Session 2: Opus Onboarding & Context Engineering Benchmark (OpenCode, 2026-02-18–19)

6. ✅ **Full project onboarding**: 5 parallel agents read 200+ files. L5 Architectural Intuition achieved in 2 prompts / 79.7K tokens. First agent to surface the esoteric layer.
7. ✅ **Case study**: `expert-knowledge/research/OPUS-ONBOARDING-CASE-STUDY-2026-02-18.md` (593 lines)
8. ✅ **Benchmark framework**: `expert-knowledge/research/XNAI-CONTEXT-ENGINEERING-BENCHMARK-2026-02-19.md` (646 lines)
9. ✅ **Benchmark directory**: `benchmarks/` — 10 files (test battery, ground truth, rubric, 5 context packs, cognitive enhancement tracker)
10. ✅ **Benchmark runner**: `scripts/run-benchmark.sh` v1.1.0 — git worktree isolation + Foundation stack integration (`--preflight`, `--publish`, `--ingest`, `--harvest`, `--integrate`)
11. ✅ **Cognitive enhancement tracker**: `benchmarks/COGNITIVE-ENHANCEMENTS.md` — CE-001 through CE-007
12. ✅ **Rule 22b**: Added cognitive feedback loop rule to `.opencode/RULES.md`
13. ✅ **Benchmark tag**: `benchmark/context-engineering-v1.0.0` created and pushed

### Key Decisions Locked In
- **OpenCode remains primary CLI** — Antigravity free access irreplaceable
- **Crush = experimental only** — no free tier, early stage
- **iFlow = excluded from waterfall** — CN backend sovereignty concern
- **Cerebras/SambaNova = immediate adds** — exceptional free value
- **Memory bank = LLM context engine** — 8 differentiators identified
- **Benchmark feedback loop = closed** — BENCHMARK → ANALYZE → ENHANCE → RE-BENCHMARK

---

## Sprint 7 Backlog → Sprint 8

### Deferred from Sprint 6
- [ ] `docs/architecture/XNAI-STACK-OVERVIEW.md` — C4 Mermaid system diagram
- [ ] `docs/tutorials/FREE-AI-PROVIDERS-COMPLETE-GUIDE.md` — tutorial
- [ ] `expert-knowledge/AGENT-CLI-MODEL-MATRIX-v3.0.0.md` — verify Antigravity taxonomy
- [ ] README.md update
- [ ] MkDocs superfences Mermaid config verification

### Cognitive Enhancements (from benchmarks/COGNITIVE-ENHANCEMENTS.md)
- [ ] CE-001: Phase number disambiguation in activeContext.md
- [ ] CE-002: Onboarding protocol as standalone config file
- [ ] CE-003: INDEX.md cross-reference validation script
- [ ] CE-004: Handover file auto-discovery (latest.md symlink)
- [ ] CE-005: Esoteric layer summary in CONTEXT.md
- [ ] CE-006: Token budget metadata for context packs

### Enhanced Strategy Package (NEW - Sprint 8)
- [x] `memory_bank/strategies/UNIFIED-STRATEGY-ENHANCED-v1.1.md` — Enhanced strategy with Vikunja integration
- [x] `memory_bank/strategies/PROJECT-QUEUE.yaml` — Enhanced project queue with resource allocation
- [x] `memory_bank/strategies/IMPLEMENTATION-PLAYBOOK-v1.0.md` — Comprehensive execution guidance
- [x] `memory_bank/strategies/FINAL-STRATEGY-PACKAGE-v1.0.md` — Consolidation document for Opus review

### Incoming (User queue)
- [ ] High priority items — architect to define

---

## Key Files — Quick Reference

| Purpose | File |
|---------|------|
| Agent model registry | `configs/agent-identity.yaml` |
| Model router (all providers) | `configs/model-router.yaml` |
| Free providers catalog | `configs/free-providers-catalog.yaml` |
| Agent behavioral rules | `.opencode/RULES.md` |
| Document signing | `scripts/sign-document.sh` |
| Session harvest | `scripts/harvest-cli-sessions.sh` |
| Context packing | `scripts/stack-cat.py` + `configs/stack-cat-config.yaml` |
| Benchmark runner | `scripts/run-benchmark.sh` |
| Benchmark framework | `benchmarks/README.md` |
| Cognitive enhancements | `benchmarks/COGNITIVE-ENHANCEMENTS.md` |
| Research gap tracker | `ADDITIONAL-RESEARCH-NEEDED.md` |
| Agent taxonomy + Mermaid | `docs/architecture/XNAI-AGENT-TAXONOMY.md` |
| OpenCode fork plan | `internal_docs/01-strategic-planning/OPENCODE-XNAI-FORK-PLAN.md` |
| Case study | `expert-knowledge/research/OPUS-ONBOARDING-CASE-STUDY-2026-02-18.md` |
| Sprint 7 handover (Opus) | `memory_bank/activeContext/sprint-7-handover-2026-02-19.md` |
| Sprint 7 handover (Cline) | `memory_bank/activeContext/sprint-7-handover-2026-02-18.md` |
| Sprint 6 handover | `memory_bank/activeContext/sprint-6-handover-2026-02-18.md` |

---

## Signing Protocol

All new files must be signed. Use:
```bash
./scripts/sign-document.sh <file.md> --tool cline --session sprint8-2026-MM-DD
# --model is auto-resolved from configs/agent-identity.yaml
```

For .py/.sh files, add manually:
```python
# ---
# tool: cline
# model: claude-sonnet-4-6
# session_id: sprint8-2026-MM-DD
# version: v1.0.0
# created: YYYY-MM-DD
# ---
```
