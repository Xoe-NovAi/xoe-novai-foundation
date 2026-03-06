---
tool: opencode
model: gemini-3-pro
account: arcana-novai
git_branch: xnai-agent-bus/harden-infra
session_id: sprint8-gemini-2026-02-19
version: v1.0.0
created: 2026-02-19
tags: [strategy, roadmap, project-management, unified-tracking]
---

# XNAi Ecosystem — Unified Strategy Plan v1.0

## Executive Summary
This document establishes a coherent execution strategy for the XNAi Foundation and the broader Arcana-Nova ecosystem. It unifies disparate roadmaps, research queues, and risk trackers into a single, executable project hierarchy.

**Strategic Core**:
1. **XNAi Foundation**: The "Forge and Anvil" — clean technical infrastructure.
2. **Arcana-Nova**: The "Living Sword" — esoteric superstructure built on Foundation.
3. **Model Delegation**: Tiered model usage to maximize token efficiency and save Opus 4.6 for critical architectural decisions.

---

## 1. Project Hierarchy (Tiers)

### TIER 1: PRODUCTION BLOCKERS (P0) — Immediate Execution
| ID | Project | Focus | Status |
|----|---------|-------|--------|
| P-001 | Agent Bus Stream Unification | Fix Redis stream key split (RISK-001) | Pending |
| P-002 | Permission/UID Cascade Resolution | Rootless Podman volume hardening | Pending |
| P-003 | Phase 5A Host Persistence | zRAM tuning & kernel persistence | Pending |

### TIER 2: FOUNDATION HARDENING (P1) — Next 3 Sprints
| ID | Project | Model Strategy | Status |
|----|---------|----------------|--------|
| P-010 | **Codebase-Wide Review** | Discovery (Flash) -> Plan (Sonnet) -> Review (Opus) | Initiating |
| P-011 | Security Hardening | API Validation, Rate Limiting | Pending |
| P-012 | Error Handling Unification | Consolidate exception hierarchies | Pending |
| P-013 | Cognitive Enhancements | MB improvements (CE-001 through CE-006) | Pending |

### TIER 3: FEATURE EXPANSION (P2) — Weeks 7-12
| ID | Project | Focus | Status |
|----|---------|-------|--------|
| P-020 | OpenCode Fork | Custom XNAi TUI implementation | Planning |
| P-021 | Vikunja Full Integration | Task automation & agent workflows | In Progress |
| P-022 | Qdrant Migration | FAISS to Qdrant vectorstore transition | Planned |

---

## 2. Codebase-Wide Review Pipeline (P-010)

To conserve Opus 4.6 usage, the review follows a tiered model delegation strategy:

### Phase A: Discovery (Gemini 3 Flash / Gemini 2.5 Flash CLI)
- **Scope**: Scan codebase for vulnerabilities, tech debt, and optimization patterns.
- **Output**: Detailed issue inventory with line-number references.

### Phase B: Planning (Claude Sonnet 4.6 / Gemini 3 Pro)
- **Scope**: Generate refactoring plans and implementation specs based on Phase A inventory.
- **Output**: Markdown-based refactoring roadmap.

### Phase C: Review & Hardening (Claude Opus 4.6 Thinking)
- **Scope**: Holistic architectural review of plans. Hardening of critical logic. Strategic sign-off.
- **Output**: Verified implementation guide.

### Phase D: Implementation (Sonnet 4.6 / Gemini 3 Flash)
- **Scope**: Atomic execution of verified plans.
- **Output**: Tested, signed code commits.

---

## 3. Operational Model

### Tracking Hub (Hybrid Model)
- **Vikunja**: The "Master PM Hub" for granular task tracking and agent assignment.
- **Memory Bank**: The "Strategic Narrative" — high-level state, handovers, and context.
- **Sync**: Automated scripts sync Vikunja state to `progress.md` at sprint boundaries.

### Sprint Cadence (2-Week Sprints)
- **Sprint 8**: Clear T1 Blockers + Initiate Codebase Review Phase A.
- **Sprint 9**: Review Phase B (Planning) + Foundation Hardening (Security).
- **Sprint 10**: Opus Review (Phase C) + Initial Implementation.

---

## 4. Model Delegation Matrix

| Task Category | Primary Model | Fallback | Opus Usage |
|---------------|---------------|----------|------------|
| Discovery/Scan | Gemini 3 Flash (Antigravity) | Gemini 2.5 Flash (CLI) | Never |
| Planning | Sonnet 4.6 (Antigravity) | Gemini 3 Pro (Antigravity) | Low |
| Research | Gemini 3 Pro (Antigravity) | Gemini 3 Pro Preview (CLI) | Low |
| Architecture Review | **Opus 4.6 Thinking** | — | **Primary** |
| Implementation | Sonnet 4.6 (Antigravity) | Gemini 3 Flash (Antigravity) | Medium |
| Tests/QA | Gemini 3 Flash (Antigravity) | Gemini 2.5 Flash (CLI) | Low |

---

## 5. Success Metrics (Target v1.0)
- **Test Pass Rate**: >95%
- **Memory Pressure**: <5.5GB (92%)
- **Documentation Fidelity**: 100% (No conflicts)
- **Codebase Review Coverage**: 100% of `app/` and `core/`

---

**Next Steps**: 
1. Finalize `PROJECT-QUEUE.yaml` from research backlogs.
2. Initialize Vikunja task projects.
3. Handover to Opus 4.6 for strategic sign-off.
