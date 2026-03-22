# Claude Integration Protocol (CIP)

**Version**: 1.0.0
**Date**: 2026-03-21
**Status**: ACTIVE
**Domain**: `/docs/protocols`

---

## 1. Overview
This protocol defines the hierarchical integration of the **Claude Family** (Haiku, Sonnet, Opus) into the Omega Stack workflow. It establishes a clear chain of command and responsibility to optimize token usage, leverage specific model strengths, and respect system constraints (16GB RAM, Local Sovereignty).

## 2. The Hierarchy (The "Triad")

### ☁️ Tier 1: Cloud Haiku (The Architect)
*   **Role**: Strategic Planner, Rapid Prototyper, Documentation Drafter.
*   **Access**: Read-Only (GitHub Context). No local execution.
*   **Responsibility**:
    *   Analyze complex problems and architectural requirements.
    *   Draft implementation plans and Python scripts (e.g., `migrate_to_atomic.py`).
    *   Create "Execution Guides" for Tier 2 agents.
    *   Generate artifacts for user download.
*   **Constraint**: Cannot execute code or access local files directly.
*   **Token Strategy**: High-volume context processing (GitHub Repo) -> Low-volume output (Plans).

### ⚡ Tier 2: Gemini CLI / Copilot (The Builder)
*   **Role**: Executor, Implementer, "Hands-on" Engineer.
*   **Access**: Full Local Read/Write (File System, Shell, Git).
*   **Responsibility**:
    *   Execute the plans and scripts drafted by Tier 1.
    *   Handle "mundane," high-token tasks (e.g., mass file moves, refactoring, running migrations).
    *   Perform Git operations (add, commit, branch).
    *   Run validation suites and fix immediate errors.
*   **Constraint**: Focus on execution; defers high-level architectural decisions to Tier 1/3.
*   **Token Strategy**: High-volume output (Code generation/modification) -> Local execution.

### 🧠 Tier 3: Local Antigravity (The Sage)
*   **Models**: Sonnet / Opus (Local or API-bridged).
*   **Role**: Strategic Reviewer, Quality Assurance, Deep Thinker.
*   **Access**: Local Context (via User/Gemini provision) or API.
*   **Responsibility**:
    *   Review completed implementations for architectural integrity.
    *   Draft "Strategic Implementation Manuals" for complex future phases.
    *   Optimize code quality and system performance.
    *   Resolve deep, systemic blockers that Tier 1/2 cannot solve.
*   **Constraint**: Low-volume, high-value input. Expensive per token.
*   **Token Strategy**: Precision strikes. Refines the work of Tier 2.

## 3. Workflow Example: "Gnostic Vault Ignition"

1.  **Haiku (Cloud)**: Reads the `MANIFEST.md` and `MNEMOSYNE_AUDIT_REPORT.md`. Drafts the `migrate_to_atomic.py` script and a step-by-step "Migration Guide" for Gemini.
2.  **Gemini (Local)**: Downloads the script. Runs it. Handles the file moves. Verifies the output. Commits the changes.
3.  **Antigravity (Local)**: Reviews the new Zettelkasten structure. Suggests optimizations for the `MAP_OF_CONTENT.json`. Updates the long-term roadmap.

## 4. Interaction Guidelines

*   **Handoffs**: Always provide a clear "Context Pack" (Manifests, Reports) when moving from Tier 2 to Tier 1.
*   **Artifacts**: Tier 1 output must be *actionable* (e.g., valid Python code, ready-to-paste prompts).
*   **Validation**: Tier 2 must validate Tier 1's code before committing.
