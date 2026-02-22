# P-017 Group A: AWQ Removal File Audit & Execution Plan

**Date**: 2026-02-21
**Status**: AUDIT COMPLETE
**Executor**: Gemini CLI
**Context**: Removing PyTorch and AWQ dependencies to enforce Torch-Free Mandate.

---

## 1. Executive Summary
The audit has confirmed that the core application (`requirements.txt`, `pyproject.toml`) is already largely torch-free. The AWQ components are isolated in specific files (`Dockerfile.awq`, `awq_quantizer.py`) and tests. The primary task is the removal of these isolated components and the refactoring of one test file.

## 2. Files for Deletion / Archival
These files contain direct PyTorch/AWQ logic and must be removed from the active codebase. They will be archived first.

| File Path | Description | Action |
|-----------|-------------|--------|
| `Dockerfile.awq` | Container definition for AWQ quantization | **ARCHIVE & DELETE** |
| `app/XNAi_rag_app/core/awq_quantizer.py` | Core logic for AWQ quantization | **ARCHIVE & DELETE** |
| `tests/test_awq_exceptions.py` | Unit tests for AWQ exceptions | **ARCHIVE & DELETE** |

## 3. Files for Refactoring
These files contain references to AWQ that must be removed, but the files themselves must be preserved.

| File Path | Logic to Remove |
|-----------|-----------------|
| `tests/test_error_path_coverage.py` | Remove `class TestAWQQuantizationErrorPaths` and related imports. |
| `README.md` | Remove line: "- **Experimental features** — AWQ quantization..." |
| `AGENTS.md` | (Review) Ensure mandates are clear. |

## 4. Documentation & Research Artifacts
These files contain references to AWQ or Torch that are informational (e.g., benchmark tensions, model cards).

| File Path | Recommendation |
|-----------|----------------|
| `benchmarks/ground-truth-baseline.yaml` | **KEEP**. The "Torch-free vs LoRA" tension is a valid architectural constraint to document. |
| `benchmarks/scoring-rubric.yaml` | **KEEP**. references the tension above. |
| `scripts/phase_b_model_research_generator.py` | **KEEP**. Mentions `torch` in a data dictionary for model card generation (informational). |
| `expert-knowledge/architect/architect-expert-knowledge-base.md` | **KEEP**. Discusses "Torch-free inference". |

## 5. Execution Sequence (Proposed)

### Step 1: Archival (Group B & C)
Create `expert-knowledge/_archive/gpu-research/` and move the following files there (renaming to preserve context if needed, or keeping original names in the archive folder):
- `Dockerfile.awq` -> `expert-knowledge/_archive/gpu-research/Dockerfile.awq`
- `app/XNAi_rag_app/core/awq_quantizer.py` -> `expert-knowledge/_archive/gpu-research/awq_quantizer.py`
- `tests/test_awq_exceptions.py` -> `expert-knowledge/_archive/gpu-research/test_awq_exceptions.py`

### Step 2: Deletion
Remove the original files from the source tree.

### Step 3: Refactoring
- Edit `tests/test_error_path_coverage.py` to remove AWQ tests.
- Edit `README.md` to remove AWQ feature listing.

### Step 4: Verification
- Run `pytest tests/test_error_path_coverage.py` to ensure no regressions.
- Scan `requirements.txt` one last time (completed during audit: Clean).

## 6. Dependencies Verification
- `requirements.txt`: **CLEAN** (No `torch`, `autoawq`).
- `pyproject.toml`: **CLEAN**.

---

**Next Step**: Approval to proceed with **Step 1: Archival**.
