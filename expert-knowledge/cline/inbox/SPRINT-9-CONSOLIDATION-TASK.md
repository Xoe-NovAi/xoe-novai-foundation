# SPRINT 9 CONSOLIDATION MASTER TASK

**Priority**: CRITICAL (P0)
**Context**: Post-Gemini Research Handoff
**Assigned To**: Cline (claude-sonnet-4-6)

---

## 🎯 OBJECTIVE
Execute the "Sprint 9 Consolidation" plan prepared by Gemini CLI. This involves four distinct sub-tasks that must be executed in sequence.

## 📂 SUB-TASK 1: P-017 AWQ REMOVAL (EXECUTION)
**Source Plan**: `plans/awq-removal-file-audit.md`
**Goal**: Enforce the Torch-Free mandate by removing PyTorch/AWQ dependencies.

### Actions:
1.  **ARCHIVE**: Move the following files to `expert-knowledge/_archive/gpu-research/`:
    -   `Dockerfile.awq`
    -   `app/XNAi_rag_app/core/awq_quantizer.py`
    -   `tests/test_awq_exceptions.py`
2.  **DELETE**: Remove the original files from the source tree.
3.  **REFACTOR**:
    -   Edit `tests/test_error_path_coverage.py`: Remove `class TestAWQQuantizationErrorPaths` and related imports.
    -   Edit `README.md`: Remove the line "- **Experimental features** — AWQ quantization..."
4.  **VERIFY**: Run `pytest tests/test_error_path_coverage.py`.

## 📂 SUB-TASK 2: SESSION-STATE CONSOLIDATION
**Source Plan**: `session-state-archives/2026-02-17-comprehensive-import/GEMINI-HANDOFF-2026-02-21.md`
**Goal**: Consolidate 38+ session files into the Diataxis project structure.

### Actions:
1.  **Phase 0 (2 files)**: Move audit/impl plans to `docs/02-tutorials` or `docs/03-how-to-guides`.
2.  **Phase 7 (30+ files)**: Categorize Agent Bus implementation files into `docs/` subdirectories (Explanation, Reference, etc.).
3.  **Phase 8 (6 files)**: Move CLI hardening research to `docs/03-reference`.
4.  **Update Links**: Grep for references to moved files and update internal links in `memory_bank/activeContext.md` and `docs/index.md`.

## 📂 SUB-TASK 3: MC OVERSEER CREATION (CLINE)
**Goal**: Establish the `mc-overseer` agent for Cline.

### Actions:
1.  Read `.opencode/agents/mc-overseer.md` (Source of Truth).
2.  Create `.clinerules/agents/mc-overseer.md` with identical content.
3.  Ensure Cline knows to "activate" this agent when high-level coordination is needed.

## 📂 SUB-TASK 4: CLI ECOSYSTEM AUDIT (FOUNDATION)
**Goal**: Ensure `.clinerules` and `.opencode/RULES.md` are congruent.

### Actions:
1.  **Compare**: Read `.clinerules/rules/` and `.opencode/RULES.md`.
2.  **Identify Divergence**: specific attention to:
    -   Torch-free mandate (Must be present in both).
    -   Memory Bank Protocol (Must be identical).
    -   Model Matrix (v3.0.0).
3.  **Report**: Create `plans/CLI-ECOSYSTEM-AUDIT-REPORT.md` listing any discrepancies found.

---

## 📢 COMPLETION PROTOCOL
1.  Update `memory_bank/activeContext.md` to mark P-017 as **Complete**.
2.  Update `memory_bank/progress.md` to mark Sprint 9 items as **Verified**.
3.  Commit changes with message: "feat: sprint 9 consolidation and awq removal".
