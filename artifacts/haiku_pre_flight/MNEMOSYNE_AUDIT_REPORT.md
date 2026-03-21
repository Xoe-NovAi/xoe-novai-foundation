# MNEMOSYNE AUDIT REPORT: Migration Strategy
## Towards a Gnostic Knowledge Vault

**Status**: CRITICAL
**Date**: 2026-03-19
**Scope**: `memory_bank/` (274 files)

---

## 1. THE PROBLEM: FRAGMENTATION & STALENESS
*   **Stale Data**: 85% of files > 48 hours old.
*   **Fragmented Context**: Knowledge is trapped in session logs, not atomic concepts.
*   **Zero Discoverability**: No semantic index. Agents cannot find "related" knowledge.

## 2. THE SOLUTION: ZETTELKASTEN MIGRATION
We are moving from a "File Cabinet" (Folders) to a "Neural Network" (Graph).

### Phase 1: Structure (Week 1)
*   **Current**: `memory_bank/plans/`, `memory_bank/decisions/`
*   **Target**: `memory_bank/atomic/{entities,protocols,decisions,knowledge}`

### Phase 2: Automation (Week 2)
*   **Auto-Index**: `scripts/index_knowledge.py` (Every 6h).
*   **Backlinks**: `scripts/compute_backlinks.py` (Monthly).

## 3. CLOUD HAIKU TASK
**Do NOT rewrite the files manually.**
Instead, design the **Python Migration Scripts**:

1.  `scripts/migrate_to_atomic.py`:
    *   Scans existing `memory_bank/**/*.md`.
    *   Extracts "Concepts" using regex/LLM logic.
    *   Writes atomic files to `memory_bank/atomic/`.
    *   Adds YAML front-matter (tags, date, status).

2.  `scripts/index_knowledge.py`:
    *   Generates `knowledge_graphs/index.json`.
    *   Computes embeddings for Qdrant.

## 4. EXECUTION PLAN
1.  **Haiku** designs the scripts.
2.  **Gemini CLI** reviews and executes locally.
3.  **Archon** verifies the new graph structure.

**Proceed with Script Design.** 🔱
