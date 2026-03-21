# 🧹 GNOSTIC MEMORY CURATOR (GMC) WORKER SPEC
**Status**: DEFINED | **Target**: Immediate Implementation
**Role**: Hygiene & Curation

## 1. Overview
The **GMC Worker** is the "Janitor" of the Omega Stack. It ensures data hygiene, prevents "Backslash Bloat", and maintains the Chat Index.

## 2. Core Functions

### A. The "Backslash Stripper"
**Problem**: JSON serialization often double-escapes backslashes, leading to `\\\\\\\\n` bloat.
**Logic**:
```python
def clean_content(content: str) -> str:
    # Recursively reduce backslashes to single
    while "\\\\" in content:
        content = content.replace("\\\\", "\\")
    return content
```
**Trigger**: Pre-save hook on any `write_file` operation in the `memory_bank`.

### B. The Chat Indexer
**Goal**: Instant search of past sessions.
**Output**: `DISCOVERY_INDEX.md` (or JSON).
**Fields**:
-   `session_id`
-   `date`
-   `user_intent` (Summary)
-   `key_decisions` (List)
-   `files_modified` (List)

### C. The Pruner
**Logic**:
-   If `session_date` > 30 days AND `status` != "pinned":
    -   Move to `_archive/sessions/<year>/<month>/`.
-   Update Index to point to new location.

## 3. Implementation
-   **Script**: `scripts/gmc_worker.py`.
-   **Service**: Runs as a sidecar to `xnai_memory_bank_mcp`.
