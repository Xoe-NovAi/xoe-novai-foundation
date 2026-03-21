---
last_updated: 2026-02-14
status: active
persona_focus: Gemini
agent_impact: critical
related_phases: Phase-4.1
---

# AI Agent Pipeline Strategy: The Triple-Model Core

We utilize a three-tiered model pipeline to ensure velocity, quality, and ground truth integrity.

## 1. The Implementation Pipeline
Contrary to typical assumptions, we utilize our strongest SWE-bench model (**Kimi K2.5**) for the **Initial Implementation** and our fastest model (**Haiku 4.5**) for **Tactical Reviews** and snippets.

### Step A: Specification (Gemini 3 Flash)
- **Role**: Scribe & Reasoner.
- **Input**: User vision + Full Project Context (1M tokens).
- **Output**: `spec.md` + `plan.md`.
- **Why Flash 3?**: High speed + "Thinking" reasoning for complex SDD.

### Step B: Tactical Review (Scout: Haiku 4.5)
- **Agent**: Copilot CLI.
- **Process**: 
  - Automated trigger via `gh copilot -p "..." --silent`.
  - Structured JSON review written to `internal_docs/communication_hub/outbox/`.
  - Review of `spec.md` for technical feasibility and security.

### Step C: Finalization (Gemini 3 Flash)
- **Role**: Scribe & Reasoner.
- **Process**: Merges Copilot feedback into `spec.md` and signals `spec_finalized`.

### Step D: Execution (Engineer: Kimi K2.5)
- **Agent**: Cline CLI.
- **Process**: 
  - Triggered by `spec_finalized` message.
  - Loads workspace rules from `.clinerules/`.
  - Implements logic and tests.
  - Reports completion to `outbox/`.

### Step E: Ground Truth Synthesis (Gemini 3 Flash)
- **Role**: Ground Truth Executor.
- **Process**: Final audit of code + docs. Updates `memory_bank/` and `internal_docs/00-system/INDEX.md`.

## 2. Automation Logic
- **Haiku** handles the "small" (snippets, shell help, quick fixes).
- **Kimi** handles the "large" (new features, refactors, logic changes).
- **Gemini** handles the "meta" (strategy, audits, taxonomy).
