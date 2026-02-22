---
tool: opencode
model: claude-opus-4-6-thinking
account: arcana-novai
git_branch: main
session_id: sprint7-opus-2026-02-19
version: v1.0.0
created: 2026-02-19
tags: [benchmark, cognitive-architecture, feedback-loop, memory-bank]
---

# Cognitive System Enhancement Tracker

Tracks improvements to the XNAi memory bank, handover system, context packing, and related cognitive architecture components. This tracker forms the **feedback loop** between benchmark results and system evolution.

**Relationship to existing trackers:**

- `ADDITIONAL-RESEARCH-NEEDED.md` — tracks technical/implementation research gaps (Rule 22)
- `expert-knowledge/research/index.json` — formal 7-state research queue
- **This file** — tracks improvements to the cognitive architecture itself (Rule 22b)

## Categories

| Code | Category | Scope |
|------|----------|-------|
| MB | Memory Bank | activeContext, progress, CONTEXT, handover files, INDEX.md |
| HO | Handover | Sprint handover format, state transfer fidelity, handover checklists |
| CF | Config | agent-identity.yaml, model-router.yaml, stack-cat-config.yaml, RULES.md |
| CP | Context Packing | stack-cat.py, pack definitions, token budget optimization |
| AC | Agent Coordination | teamProtocols.md, agent taxonomy, bus coordination patterns |
| BM | Benchmark | Test battery, rubric, ground truth, runner, scoring methodology |

## Status Codes

| Status | Meaning |
|--------|---------|
| proposed | Identified but not yet analyzed |
| validated | Confirmed via benchmark data or agent feedback |
| in-progress | Implementation underway |
| completed | Implemented and verified |
| deferred | Acknowledged but deprioritized |

## Enhancement Template

```yaml
- id: CE-NNN
  category: MB|HO|CF|CP|AC|BM
  source: benchmark-run|agent-feedback|architect-directive|gap-analysis
  priority: critical|high|medium|low
  status: proposed|validated|in-progress|completed|deferred
  benchmark_version: v1.0.0
  description: >
    One-line summary of the enhancement.
  evidence: >
    What data or observation triggered this? Include benchmark scores,
    agent failures, or architect observations.
  impact: >
    Expected improvement and which benchmark tests/environments it affects.
  related_files:
    - path/to/file.md
  resolved_in: sprint-N  # filled when completed
```

## Active Enhancements

### CE-001: Add explicit phase number disambiguation to activeContext.md

```yaml
- id: CE-001
  category: MB
  source: gap-analysis
  priority: high
  status: proposed
  benchmark_version: v1.0.0
  description: >
    Triple phase numbering (Vikunja, memory_bank, roadmap) causes confusion.
    activeContext.md should include a disambiguation table mapping all three
    numbering systems with a single canonical reference.
  evidence: >
    Opus 4.6 onboarding identified this as a tension. Previous agents
    (Gemini 2.5 Pro, Sonnet 4.6) have misidentified current phase in past
    sprints. Expected to depress T1 (Project Identity) scores in E4/E5.
  impact: >
    Improves T1/T2 scores across E4 and E5 by reducing ambiguity.
    Reduces hallucinated phase numbers in cold-start (E1/E2) environments.
  related_files:
    - memory_bank/activeContext.md
    - memory_bank/progress.md
```

### CE-002: Formalize onboarding protocol as a standalone config file

```yaml
- id: CE-002
  category: CP
  source: benchmark-run
  priority: high
  status: proposed
  benchmark_version: v1.0.0
  description: >
    The XNAi Onboarding Protocol v1.0.0 (defined in case study Section 6)
    should be extracted into a standalone config file that stack-cat.py can
    consume directly, with phase ordering and token budget metadata.
  evidence: >
    E5 pack currently defined in stack-cat-config.yaml as a flat file list.
    Protocol phases (1-4) and reading order are only documented in prose.
    Automated benchmark runner cannot enforce reading order without config.
  impact: >
    Enables automated E5 environment setup. Allows token budget tracking
    per phase. Supports future protocol versioning (v1.1, v2.0).
  related_files:
    - configs/stack-cat-config.yaml
    - expert-knowledge/research/OPUS-ONBOARDING-CASE-STUDY-2026-02-18.md
    - scripts/stack-cat.py
```

### CE-003: Add memory_bank/INDEX.md cross-reference validation

```yaml
- id: CE-003
  category: MB
  source: gap-analysis
  priority: medium
  status: proposed
  benchmark_version: v1.0.0
  description: >
    INDEX.md serves as the entry point for the memory bank but has no
    automated validation that all referenced files exist or that all
    memory_bank/ files are listed in the index.
  evidence: >
    Manual inspection during onboarding revealed no broken links, but
    as files are added/removed across sprints, drift is inevitable.
    A validation script would catch staleness before it affects benchmarks.
  impact: >
    Prevents E4/E5 context packs from referencing missing files.
    Reduces onboarding friction for new agents.
  related_files:
    - memory_bank/INDEX.md
    - scripts/stack-cat.py
```

### CE-004: Standardize handover file naming and discovery

```yaml
- id: CE-004
  category: HO
  source: gap-analysis
  priority: medium
  status: proposed
  benchmark_version: v1.0.0
  description: >
    Handover files use sprint-N-handover-YYYY-MM-DD.md naming but there is
    no programmatic discovery mechanism. stack-cat.py hardcodes the latest
    handover filename. An auto-discovery pattern (glob for latest) or a
    symlink (memory_bank/activeContext/latest.md) would improve reliability.
  evidence: >
    benchmark-e5 pack in stack-cat-config.yaml hardcodes
    sprint-7-handover-2026-02-18.md. When Sprint 8 begins, this will be
    stale unless manually updated.
  impact: >
    Prevents E5 context pack staleness across sprints.
    Reduces manual config maintenance burden.
  related_files:
    - memory_bank/activeContext/
    - configs/stack-cat-config.yaml
```

### CE-005: Add esoteric layer summary to CONTEXT.md

```yaml
- id: CE-005
  category: MB
  source: benchmark-run
  priority: medium
  status: proposed
  benchmark_version: v1.0.0
  description: >
    The esoteric/philosophical layer (Ma'at's 42 Ideals, Ten Pillars,
    Dual Flame, Pantheon Model) is load-bearing architecture but is not
    referenced in CONTEXT.md. Adding a brief summary with pointers to
    expert-knowledge/esoteric/ would improve discoverability.
  evidence: >
    No previous agent (across 12 months, ~70 sprints) surfaced the esoteric
    layer until Opus 4.6 with full E5 context. This suggests the layer is
    insufficiently cross-referenced from primary context files.
    Expected to improve T6 (Hidden Layer Discovery) scores significantly.
  impact: >
    Directly improves T6 scores across all environments.
    Makes philosophical grounding discoverable without deep exploration.
  related_files:
    - memory_bank/CONTEXT.md
    - expert-knowledge/esoteric/maat_ideals.md
    - app/XNAi_rag_app/core/maat_guardrails.py
```

### CE-006: Token budget metadata for context packs

```yaml
- id: CE-006
  category: CP
  source: benchmark-run
  priority: low
  status: proposed
  benchmark_version: v1.0.0
  description: >
    stack-cat.py should report estimated token counts per file and total
    pack size. This enables budget-aware pack design and helps identify
    which files contribute most to context window consumption.
  evidence: >
    Opus 4.6 onboarding consumed 79.7K tokens for E5. No tooling exists
    to predict or optimize this. Models with smaller context windows
    (e.g., GPT-5 Mini at 128K) may need optimized packs.
  impact: >
    Enables context window optimization for smaller models.
    Supports future E5-lite variants for constrained contexts.
  related_files:
    - scripts/stack-cat.py
    - configs/stack-cat-config.yaml
```

### CE-007: Foundation stack integration for benchmark automation

```yaml
- id: CE-007
  category: BM
  source: architect-directive
  priority: high
  status: completed
  benchmark_version: v1.1.0
  description: >
    Integrate run-benchmark.sh with Foundation stack services: pre-flight
    health check (stack_health_check.sh), Redis result publishing
    (xnai:benchmark_results stream), context pack ingestion into RAG
    (ingest_library.py), CLI session harvesting (harvest-cli-sessions.sh),
    and run manifest generation (manifest.json per run).
  evidence: >
    Stack exploration revealed 11 services and 10+ scripts that the
    benchmark runner can leverage. All integrations are optional flags
    that degrade gracefully if services are unavailable.
  impact: >
    Enables automated benchmark pipelines. Results are discoverable via
    Redis streams. Context packs are searchable in RAG. Session data is
    preserved for future analysis. Health-gated runs prevent false negatives
    from stack outages.
  related_files:
    - scripts/run-benchmark.sh
    - scripts/stack_health_check.sh
    - scripts/ingest_library.py
    - scripts/harvest-cli-sessions.sh
  resolved_in: sprint-7
```

## Completed Enhancements

- **CE-007** (v1.1.0): Foundation stack integration — completed Sprint 7

## Changelog

| Date | Enhancement | Action |
|------|-------------|--------|
| 2026-02-19 | CE-001 through CE-006 | Initial population from Opus 4.6 onboarding analysis |
| 2026-02-19 | CE-007 | Stack integration implemented in run-benchmark.sh v1.1.0 |
