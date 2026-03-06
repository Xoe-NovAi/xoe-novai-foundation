# Opus Strategic Review — Consolidated Findings & Templates

> **Reviewer**: Claude Opus 4.6 Thinking
> **Date**: 2026-02-19
> **Scope**: UNIFIED-STRATEGY-v1.0.md, PROJECT-QUEUE.yaml, OPUS-TOKEN-STRATEGY.md, antigravity-accounts.json, opencode.json, progress.md, activeContext.md, CONTEXT.md

---

## Part 1: Review Verdict

### Approved (with corrections applied)
The strategy is **architecturally sound**. The 4-tier hierarchy, ecosystem isolation (XNAi vs Arcana-Nova), and tiered model delegation are correct. Six rounds of review have produced a workable framework.

### Corrections Applied This Session

| # | Issue | Severity | Fix |
|---|-------|----------|-----|
| 1 | `total_items: 16` should be 19 | Data error | Fixed in PROJECT-QUEUE.yaml |
| 2 | progress.md:243 "Phase 6 In Progress" | Split-brain | Fixed to "Phase 6/7 Complete" |
| 3 | Phantom models (GPT-5 Nano, Kimi, Haiku) | Config drift | Replaced with actual opencode.json models |
| 4 | OPUS-TOKEN-STRATEGY generic/no data | Incomplete | Rewrote as v2.0 with account quotas |

### Remaining Items for Architect Decision

| # | Item | Decision Needed |
|---|------|----------------|
| A | P-024 torch-free conflict | LoRA/QLoRA requires PyTorch. Options: (1) exception for fine-tuning only, (2) ONNX-native fine-tuning via Olive, (3) defer to cloud-hosted fine-tuning |
| B | RISK-007 gap | Intentional skip or missing entry? If missing, what was it? |
| C | Gemini CLI vs AI Studio | Current two-channel (Antigravity + CLI) is sufficient. AI Studio API key is a future enhancement only if needed. Confirm. |

---

## Part 2: Reusable Templates

### Template 1: Session Startup Protocol
```markdown
## Session Startup Checklist
1. [ ] Read `memory_bank/activeContext.md`
2. [ ] Read `memory_bank/strategies/OPUS-TOKEN-STRATEGY.md` (Section 1.3 for budgets)
3. [ ] Declare session goal and model being used
4. [ ] Set token budget: Opus=80K, Sonnet=120K, Gemini=400K
5. [ ] If resuming: read the latest `CONTEXT-STATE-RECOVERY-*.md`
```

### Template 2: Context Checkpoint Format
```markdown
# Context State Recovery — [DATE]-[SESSION-ID]

## Decisions Made
- [bullet point each decision, max 10]

## Files Modified
- [path only, no content]

## Open Questions
- [numbered list]

## Next Actions
- [numbered list with assigned model]

## Token Stats
- Context at checkpoint: [X]K / [limit]K
- Tool calls this session: [N]
```

### Template 3: Handover Document Format
```markdown
# Handover: [Source Model] → [Target Model]

## Context
[2-3 sentences on what happened]

## Completed
- [bullet points]

## Blocked / Needs Input
- [bullet points with specific questions]

## Files to Read First
1. [most important file]
2. [second most important]
3. [third — rarely need more than 3]

## Explicit Instructions
[What the target model should do, in imperative form]
```

### Template 4: Sprint Boundary Protocol
```markdown
## Sprint [N] Boundary Checklist

### Close-out
- [ ] Update `progress.md` with deliverables table
- [ ] Write handover doc in `memory_bank/activeContext/`
- [ ] Update `activeContext.md` sprint status table
- [ ] Tag git if milestone reached

### Kick-off
- [ ] Read previous sprint handover
- [ ] Review PROJECT-QUEUE.yaml for next tier items
- [ ] Create sprint backlog in Vikunja (when operational)
- [ ] Assign models per delegation matrix
```

### Template 5: Project Queue Item (YAML)
```yaml
- id: P-NNN
  title: "Short descriptive title"
  description: |
    What needs to be done and why.
    Include context on blockers or dependencies.
  source:
    - path/to/source/document.md
  tier: P0|P1|P2|P3
  status: pending|in_progress|completed|blocked
  labels:
    - tier:P0
    - project:P-NNN
    - domain-tag
  assigned_model: opus|sonnet|gemini-flash|gemini-cli|mixed|tiered
  estimated_effort: "N hours|sprints"
  depends_on: [P-NNN]  # NEW: explicit dependency
  acceptance_criteria:
    - Testable condition 1
    - Testable condition 2
```

---

## Part 3: Dependency Graph (Enhancement)

```
TIER 1 (Parallel — no dependencies):
  P-001 ──┐
  P-002 ──┼── All must complete before Tier 2 starts
  P-003 ──┤
  P-004 ──┘

TIER 2 (Sequential chains):
  P-010 Phase A (Discovery) ──→ P-010 Phase B (Planning)
       └──→ P-011 (Security Hardening, depends on P-010A findings)
       └──→ P-012 (Test Coverage, can parallel with P-011)
  P-010 Phase B ──→ P-010 Phase C (Opus Review) ──→ P-010 Phase D (Impl)
  P-013 (Error Handling) ── independent, can run parallel
  P-014 (Cognitive Enhancements) ── independent, can run parallel
  P-015 (MC Oversight) ── independent, can run parallel
  P-016 (Research Queue) ── independent, can run parallel

TIER 3 (After Tier 2 completion):
  P-020 (OpenCode Fork) ── independent
  P-021 (Vikunja) ── independent
  P-022 (Qdrant) ── independent
  P-023 (FORGE) ── may overlap with P-010D
  P-024 (Fine-Tuning) ── BLOCKED on architect decision (torch-free)
```

---

## Part 4: Process Observations Worth Codifying

### Observed Anti-Pattern: "Split-Brain Documentation"
**Description**: Multiple files claim authority over the same data (phase status).
**Prevention**: The `progress.md` canonical-source rule exists but wasn't enforced. Add a validation step to the Sprint Boundary Protocol: grep all `*.md` files for phase status indicators and verify they match `progress.md`.

### Observed Anti-Pattern: "Phantom Model References"
**Description**: Strategy documents reference models not in the actual configuration.
**Prevention**: The Model Delegation Matrix should be auto-validated against `opencode.json` at sprint boundaries. A simple script could parse both files and flag mismatches.

### Observed Good Pattern: "Context State Recovery"
**Description**: The checkpoint-and-recover approach saved this session from total context loss.
**Codify**: Make it a mandatory protocol (done in OPUS-TOKEN-STRATEGY v2.0).

### Observed Good Pattern: "Tiered Review Pipeline"
**Description**: Flash→Sonnet→Opus pipeline is correct and should be the default for all code review.
**Codify**: Already in UNIFIED-STRATEGY. Approved.

---
**End of Review**
