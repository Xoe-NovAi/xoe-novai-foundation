# E4: Memory Bank Minimal
# ========================
# The model receives the project path AND the two most critical memory bank
# files pre-loaded. This is the "minimal" stack-cat pack.

## Setup Instructions

1. Start a fresh agent session
2. Pre-load the following files into the context:
   - `memory_bank/activeContext.md` (156 lines, ~2,000 tokens)
   - `memory_bank/progress.md` (387 lines, ~5,000 tokens)
3. Provide this prompt:

```
You have access to the XNAi Foundation project at:
/home/arcana-novai/Documents/xnai-foundation

Here is the current project context:

=== memory_bank/activeContext.md ===
[INSERT CONTENTS]

=== memory_bank/progress.md ===
[INSERT CONTENTS]

Analyze this project. I will ask you specific questions about it.
```

4. Allow additional exploration if the model requests it
5. Run all 6 tests from test-battery.md

## What This Measures

The value of JUST the two core memory bank files — the current state and the
history. This tests whether the "minimal" context pack provides sufficient
orientation for effective work.

**Hypothesis**: E4 will deliver 60-70% of E5's total score. If this holds,
it validates that activeContext.md + progress.md are the two most valuable
files in the entire project.

## Files Provided

```
memory_bank/activeContext.md    (~2,000 tokens)   → Current sprint, taxonomy, backlog
memory_bank/progress.md         (~5,000 tokens)   → Phase 1-7 history, milestones, metrics
```

**Total context budget**: ~7,000 tokens pre-loaded

## Expected Outcomes

- Models should achieve L3 (Functional Mapping) from these two files alone
- activeContext.md provides: current sprint (7), agent taxonomy, recent fixes, key file paths
- progress.md provides: all phase completions, test counts, open issues, work streams
- Missing from E4 (available in E5): handover file, CONTEXT.md, configs, team protocols, esoteric layer
- T1-T3 should score 6-8 (the files reference services, constraints, and phases)
- T4 should score 5-7 (roadmap partially visible via progress.md)
- T5 should score 2-4 (cross-domain synthesis requires the esoteric layer files)
- T6 should score 4-6 (some gaps visible from progress.md, but cross-domain gaps require deeper context)
