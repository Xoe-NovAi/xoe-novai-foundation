---
tool: opencode
model: glm-5
account: arcana-novai
git_branch: xnai-agent-bus/harden-infra
session_id: sprint8-glm5-2026-02-19
version: v1.0.0
created: 2026-02-19
tags: [strategy, roadmap, unified-tracking, project-management]
---

# XNAi Ecosystem — Unified Strategy Plan v1.0

## Executive Summary

This document consolidates all development plans, roadmaps, and task queues across the XNAi ecosystem into a single coherent strategy. It establishes the tracking hierarchy, defines project priorities, and creates a clear execution path for the next 6 sprints.

**Key Decisions:**
- **Vikunja** is the primary task hub (now fixed: Redis disabled)
- **Memory Bank** provides strategic narrative and cross-links
- **Phase 1-7** are COMPLETE; **Phase 8** is next
- **Roadmap phases 5A-8C** are a SEPARATE planning track for future features

---

## 1. Ecosystem Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ARCANA-NOVA STACK                                  │
│                    (Esoteric Consciousness Layer)                           │
│   • 10 Pillars • Dual Flame • Pantheon Model • 42 Ideals of Ma'at          │
│   • SEPARATE REPOSITORY - Built ON TOP OF Foundation                        │
│   • Status: Design Phase                                                    │
│   • NOT TRACKED IN THIS DOCUMENT                                            │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │ Depends On
┌───────────────────────────────▼─────────────────────────────────────────────┐
│                          XNAi FOUNDATION STACK                               │
│                      (Sovereign AI Infrastructure)                          │
│   • RAG Engine • Voice Interface • Security Trinity                         │
│   • Multi-Agent Orchestration • Vikunja PM Hub                              │
│   • THIS REPOSITORY - Primary focus of this strategy                        │
│   • Status: Phase 7 Complete, Phase 8 Next                                  │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │ Sync Layer
┌───────────────────────────────▼─────────────────────────────────────────────┐
│                           xoe-novai-sync                                     │
│                   (External AI Context Hub)                                 │
│   • Context packs for Grok/Claude/Gemini                                    │
│   • EKB exports • Receipt tracking                                          │
│   • Status: Operational                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Tracking Hierarchy (Hybrid Model)

```
┌─────────────────────────────────────────────────────────────────┐
│                        VIKUNJA (Primary Hub)                     │
│                                                                  │
│   Projects:                                                      │
│   ├── TIER-1-BLOCKERS (P0) — Immediate                          │
│   ├── TIER-2-HARDENING (P1) — Weeks 1-6                         │
│   ├── TIER-3-FEATURES (P2) — Weeks 7+                           │
│   └── TIER-4-STRATEGIC (P3) — Future                            │
│                                                                  │
│   Labels: tier:P0-P3, project:PROJECT-NNN, phase:A-D,          │
│           model:gemini|sonnet|opus, status:backlog|progress|... │
│                                                                  │
│   API: Scripts query Vikunja for task assignment                │
└────────────────────────────────┬────────────────────────────────┘
                                 │ Cross-links
┌────────────────────────────────▼────────────────────────────────┐
│                     MEMORY BANK (Strategic Layer)                │
│                                                                  │
│   activeContext.md:                                             │
│   ├── Current sprint summary (links to Vikunja project view)   │
│   └── Key files reference                                       │
│                                                                  │
│   progress.md:                                                   │
│   ├── Phase completion criteria                                 │
│   └── Milestone history                                         │
│                                                                  │
│   strategies/UNIFIED-STRATEGY-v1.0.md:                          │
│   └── This document — master strategy                           │
│                                                                  │
│   strategies/PROJECT-QUEUE.yaml:                                │
│   └── Consolidated task list for Vikunja import                │
└─────────────────────────────────────────────────────────────────┘
```

**Sync Protocol**: At each sprint close, update memory bank with Vikunja state summary. Memory bank tells the *story*; Vikunja tracks the *tasks*.

---

## 3. Project Priority Tiers

### TIER 1: PRODUCTION BLOCKERS (P0) — Immediate

| ID | Project | Source | Status | Est. Effort |
|----|---------|--------|--------|-------------|
| P-001 | Agent Bus Stream Key Fix | RISK-001 | PENDING | 2-4 hours |
| P-002 | Permission/UID Cascade Resolution | Security Audit | PENDING | 4-8 hours |
| P-003 | Phase 5A Host Persistence | Roadmap | PENDING | 2-4 hours |
| P-004 | Hardcoded Chinese Mirror Fix | Security Audit | PENDING | 1 hour |

**Sprint 8 Target**: Complete all P0 items.

---

### TIER 2: FOUNDATION HARDENING (P1) — Weeks 1-6

| ID | Project | Description | Model Strategy |
|----|---------|-------------|----------------|
| P-010 | **Codebase-Wide Review** | Security, performance, test coverage | Tiered (see Section 4) |
| P-011 | Security Hardening | API validation, rate limiting, input bounds | Sonnet/Gemini |
| P-012 | Test Coverage Expansion | 30% → 60% | Gemini Flash |
| P-013 | Error Handling Unification | Single exception hierarchy | Sonnet |
| P-014 | Cognitive Enhancements | CE-001 through CE-006 | Sonnet |
| P-015 | MC Oversight Tasks | 14 pending tasks | Mixed |
| P-016 | Research Queue Resolution | R1-R7 (CRITICAL/HIGH) | Gemini Pro |

---

### TIER 3: FEATURE EXPANSION (P2) — Weeks 7+

| ID | Project | Description |
|----|---------|-------------|
| P-020 | OpenCode Fork | Phases 1-5 (Minimal fork → XNAi TUI) |
| P-021 | Vikunja Full Integration | MCP layer, agent workflow |
| P-022 | Qdrant Migration | FAISS → Qdrant |
| P-023 | FORGE Remediation | 13 tactical tasks |
| P-024 | Phase 6 Fine-Tuning Prep | Dataset curation, LoRA research |

---

### TIER 4: STRATEGIC GROWTH (P3) — Future

| ID | Project | Description |
|----|---------|-------------|
| P-030 | Arcana-Nova Stack | Separate repo, esoteric layer |
| P-031 | Phase 8 Market Positioning | Scholar community, publishing |
| P-032 | Specialized Stacks | Scientific, Creative, CAD, Music |

---

## 4. Codebase-Wide Review Pipeline (P-010)

### Tiered Model Delegation Strategy

```
PHASE A: SECURITY DISCOVERY
━━━━━━━━━━━━━━━━━━━━━━━━━━
Model: Gemini 3 Flash (free, 1M context)
Duration: 2 sessions
Input: Codebase structure, known issues from audits
Output: Security vulnerability inventory, severity ranking

Why Security First?
  → Security issues can block deployment
  → Informs test coverage priorities
  → Shapes error handling requirements
          │
          ▼

PHASE B: ARCHITECTURE + PERFORMANCE PLANNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Model: Claude Sonnet 4.6 (balanced capability)
Duration: 2-3 sessions
Input: Phase A output + existing architecture docs
Output: Refactoring plans, performance profiling targets,
        error handling unification strategy, test coverage map

Why Architecture Second?
  → Builds on security findings
  → Creates implementation roadmap
  → Prepares clear questions for Opus review
          │
          ▼

PHASE C: OPUS STRATEGIC REVIEW (CONSERVED)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Model: Claude Opus 4.6 Thinking
Duration: 1 session (target: <60K tokens)
Input: Phase A + B synthesized reports (~10K tokens)
Output: 
  → Priority conflicts resolved
  → Architecture decisions locked
  → Implementation sequence approved
  → Risk acceptance/risk mitigation decisions

Why Opus Last?
  → Receives pre-digested context (not raw code)
  → Resolves conflicts (doesn't find them)
  → One authoritative pass, no iteration
          │
          ▼

PHASE D: IMPLEMENTATION
━━━━━━━━━━━━━━━━━━━━━━
Model: Sonnet 4.6 / Gemini 3 Pro (implementation-capable)
Duration: Ongoing sprints
Input: Phase C approved plans
Output: Code changes, tests, documentation

Why Distributed Implementation?
  → Lower cost models for execution
  → Opus reserved for next review cycle
```

### Opus Conservation Protocol

| Rule | Rationale |
|------|-----------|
| 1. Opus never does discovery | Discovery is token-expensive; Gemini/Kimi are free |
| 2. Opus receives pre-digested context | Use stack-cat.py + benchmark E5 packs |
| 3. Opus reviews plans, not raw code | Plans are 10x more compact than codebases |
| 4. Opus resolves conflicts, doesn't find them | Other models surface conflicts; Opus decides |
| 5. Opus signs off, doesn't iterate | One review pass, one decision, move on |

---

## 5. Model Delegation Matrix

| Task Category | Primary | Fallback | Opus? |
|---------------|---------|----------|-------|
| Security scan | Gemini Flash | Kimi K2.5 | Never |
| Research | Gemini Pro | Sonnet | Never |
| Planning | Sonnet | Gemini Pro | Never |
| Architecture review | — | — | **Yes** |
| Implementation | Sonnet | Gemini Pro | Never |
| Testing | Gemini Flash | GPT-5 Nano | Never |
| Quick fixes | Gemini CLI | — | Never |
| Strategic decisions | — | — | **Yes** |

---

## 6. Sprint Cadence

| Sprint | Duration | Focus | Key Deliverables |
|--------|----------|-------|------------------|
| Sprint 8 | Week 1-2 | Tier 1 Blockers + Review Phase A | P-001 through P-004 complete, Security inventory |
| Sprint 9 | Week 3-4 | Tier 2 Hardening + Review Phase B | Architecture plans, P-011 start |
| Sprint 10 | Week 5-6 | Review Phase C (Opus) | Strategic review complete, implementation begins |
| Sprint 11+ | Ongoing | Tier 2 completion | Test coverage, error handling, cognitive enhancements |

---

## 7. Known Conflicts (Resolved)

### Phase Numbering Conflict
**Status**: RESOLVED

Three phase numbering systems existed:
- `progress.md`: Phases 1-7 (implementation phases)
- `CONTEXT.md`: Phases 1-5 (outdated, different meanings)
- `roadmap-v2.md`: Phases 5A-8C (future feature roadmap)

**Resolution**: 
- `progress.md` is the canonical source for implementation phases
- `roadmap-v2.md` phases are a SEPARATE planning track for future features
- `CONTEXT.md` updated to reference `progress.md` as source of truth

### Vikunja Redis Crash
**Status**: RESOLVED

Vikunja 0.24.1 crashed on startup with "missing port in address" Redis error.

**Resolution**: Disabled Redis for Vikunja (`VIKUNJA_REDIS_ENABLED: "false"`) since Redis is optional caching. Vikunja will now start and can serve as the primary task hub.

### Documentation Staleness
**Status**: PARTIALLY RESOLVED

Multiple documents were stale (5-7 days old) with conflicting status markers.

**Resolution**: `CONTEXT.md` updated to current state. Remaining documents to be updated as part of Sprint 8 backlog.

---

## 8. File Structure

```
memory_bank/
├── activeContext.md          ← Sprint status, links to Vikunja
├── progress.md               ← Phase history, milestones (CANONICAL)
├── CONTEXT.md                ← Strategic context (now synced)
├── activeContext/
│   └── sprint-N-handover.md  ← Session handovers
└── strategies/
    ├── UNIFIED-STRATEGY-v1.0.md    ← This document
    └── PROJECT-QUEUE.yaml          ← Consolidated task list

internal_docs/01-strategic-planning/
├── ROADMAP-MASTER-INDEX.md   ← Future roadmap (5A-8C)
└── project-tracking/         ← (to be created) Tier-specific docs
```

---

## 9. Next Steps

### Immediate (This Session)
1. ✅ Fix Vikunja Redis connection — DONE
2. ✅ Update CONTEXT.md phase numbering — DONE
3. ✅ Create UNIFIED-STRATEGY-v1.0.md — DONE
4. 🔲 Create PROJECT-QUEUE.yaml
5. 🔲 Generate handover for Opus review

### Sprint 8 Week 1
1. Start Vikunja: `podman-compose up -d vikunja`
2. Create admin account via UI at `http://localhost:3456`
3. Import tasks from PROJECT-QUEUE.yaml
4. Execute P-001 through P-004

### Sprint 8 Week 2
1. Begin P-010 Phase A (Security Discovery with Gemini Flash)
2. Update memory bank with Vikunja cross-links

---

## 10. Changelog

| Date | Version | Change |
|------|---------|--------|
| 2026-02-19 | v1.0.0 | Initial creation — consolidation of all planning documents |
