# ---
# tool: opencode
# model: claude-opus-4-6-thinking
# account: arcana-novai
# git_branch: main
# session_id: sprint7-opus-2026-02-19
# version: v1.0.0
# created: 2026-02-19
# ---

# XNAi Context Engineering Benchmark

A reproducible test framework for measuring how documentation architecture affects LLM project comprehension.

## What This Measures

This benchmark tests the **XNAi hypothesis**: structured project documentation (memory bank, handover files, config-as-documentation) provides a measurable 10-50x improvement in LLM onboarding depth compared to conventional documentation patterns.

## Structure

```
benchmarks/
  README.md                    ← You are here
  COGNITIVE-ENHANCEMENTS.md    ← Cognitive system improvement tracker (Rule 22b)
  ground-truth-baseline.yaml   ← Verified correct answers (from Opus 4.6 session)
  test-battery.md              ← 6 test prompts with instructions
  scoring-rubric.yaml          ← Quantitative scoring criteria (0-10 per test)
  context-packs/               ← File manifests for each environment condition
    E1-cold-start.md
    E2-readme-only.md
    E3-raw-codebase.md
    E4-minimal.md
    E5-full-protocol.md

scripts/
  run-benchmark.sh             ← Benchmark runner with git worktree isolation
```

## Quick Start

1. Pick a model from the target list (see `test-battery.md`)
2. Pick an environment (E1-E5) from `context-packs/`
3. Set up the context according to the environment spec
4. Run all 6 test prompts from `test-battery.md`
5. Score responses 0-10 using `scoring-rubric.yaml`
6. Record results in the scoring matrix

## Isolation & Reproducibility

Benchmark runs use **git worktree isolation** to guarantee tests run against a frozen snapshot regardless of ongoing development.

### How It Works

```
scripts/run-benchmark.sh
  │
  ├── Resolves benchmark tag (e.g., benchmark/context-engineering-v1.0.0)
  ├── Creates detached git worktree at /tmp/xnai-benchmark-worktree-<ts>
  ├── Generates context packs (E1-E5) from frozen snapshot
  │     └── E5 uses scripts/stack-cat.py with configs/stack-cat-config.yaml
  ├── Outputs evaluator instructions with scoring references
  └── Optionally cleans up worktree (--cleanup flag)
```

### Quick Run

```bash
# Run all environments against latest benchmark tag
./scripts/run-benchmark.sh

# Run specific environment for a specific model
./scripts/run-benchmark.sh -e E5 -m opus-4.6

# Use HEAD for development (no tag required)
./scripts/run-benchmark.sh -t HEAD -e E4 --cleanup

# Generate packs only, skip evaluator output
./scripts/run-benchmark.sh -p -e E5
```

### Tagging Convention

```bash
# Create the initial benchmark snapshot (after committing all work)
git tag -a benchmark/context-engineering-v1.0.0 -m "Initial benchmark snapshot"

# Future versions after cognitive enhancements
git tag -a benchmark/context-engineering-v1.1.0 -m "CE-001: phase disambiguation"
```

## Feedback Loop

Benchmark results drive cognitive system improvements in a closed loop:

```
┌──────────────┐     ┌───────────────┐     ┌──────────────────────┐
│   BENCHMARK  │────>│    ANALYZE    │────>│       ENHANCE        │
│              │     │               │     │                      │
│ Run tests    │     │ Score vs      │     │ Update memory bank,  │
│ across E1-E5 │     │ ground truth  │     │ handover, configs,   │
│ for N models │     │ Compute CSS,  │     │ context packs, or    │
│              │     │ BCS, XAF      │     │ benchmark itself     │
└──────────────┘     └───────────────┘     └──────────────────────┘
       ^                                            │
       │              ┌───────────────┐             │
       └──────────────│  RE-BENCHMARK │<────────────┘
                      │               │
                      │ Tag new       │
                      │ version, re-  │
                      │ run battery   │
                      └───────────────┘
```

### Process

1. **BENCHMARK** — Run `scripts/run-benchmark.sh` against a tagged snapshot
2. **ANALYZE** — Score responses using `scoring-rubric.yaml`, compute derived metrics (CSS, BCS, XAF)
3. **ENHANCE** — Log improvements to `COGNITIVE-ENHANCEMENTS.md`, implement changes, update relevant files
4. **RE-BENCHMARK** — Tag a new version, re-run the battery to measure improvement

Enhancements are tracked in `COGNITIVE-ENHANCEMENTS.md` with categories: Memory Bank (MB), Handover (HO), Config (CF), Context Packing (CP), Agent Coordination (AC), Benchmark (BM).

See Rule 22b in `.opencode/RULES.md` for the agent-facing feedback loop obligation.

## Companion Documents

- **Architecture Analysis**: `expert-knowledge/research/XNAI-CONTEXT-ENGINEERING-BENCHMARK-2026-02-19.md`
- **Case Study**: `expert-knowledge/research/OPUS-ONBOARDING-CASE-STUDY-2026-02-18.md`
- **Onboarding Protocol**: Section 6 of the case study
- **Enhancement Tracker**: `benchmarks/COGNITIVE-ENHANCEMENTS.md`
- **Benchmark Runner**: `scripts/run-benchmark.sh`
- **Agent Rules**: `.opencode/RULES.md` (Rule 22b — cognitive feedback loop)
