---
last_updated: 2026-02-14
status: draft
persona_focus: Human Director
agent_impact: high
related_phases: All
---

# Team CLI Mastery: Roles & Responsibilities

In the Xoe-NovAi ecosystem, each CLI tool corresponds to a specific persona.

## 1. The Orchestrator (Gemini CLI)
- **Role**: Ground Truth Executor.
- **Mastery**: 1M token context, spec-writing, auditing.
- **When to use**: Planning sessions, deep code reviews, cross-repo synthesis, documentation indexing.

## 2. The Engineer (Cline CLI)
- **Role**: Autonomous Implementation.
- **Mastery**: Python excellence, multi-file refactors, test-driven development.
- **When to use**: Feature implementation, bug fixing, repo-wide search and replace.

## 3. The Tactical Assist (Copilot CLI)
- **Role**: Support & Verification.
- **Mastery**: Snippet generation, shell command suggestions, PR review comments.
- **When to use**: One-liner generation, quick syntax checks, shell command debugging.

## 🛠️ Combined Mastery Workflow
1.  **Director** provides vision.
2.  **Gemini** generates `spec.md`.
3.  **Cline** implements code per `spec.md`.
4.  **Copilot** verifies implementation with a "Second Eye" review.
5.  **Gemini** performs final "Truth Audit" and merges documentation.
