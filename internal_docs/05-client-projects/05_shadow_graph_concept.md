# 🌑 The Shadow Graph: Semantic Ethical Mapping

**Status**: 💡 CONCEPTUAL / IN-PROGRESS
**Last Updated**: January 25, 2026
**Purpose**: To provide a technical substrate (SQLite) that maps the **42 Ideals of Ma'at** to specific **Stack Functions** and **Agent Behaviors**.

## Overview

The Shadow Graph acts as the "unconscious" or "shadow" of the XNAi Foundation Stack. While the primary RAG index handles explicit technical knowledge, the Shadow Graph manages the relational weights between ethics and implementation.

## Technical Implementation (Planned)

- **Storage**: SQLite 3 with `fts5` for semantic search.
- **Initialization**: `scripts/init_sqlite.py` (Pending).
- **Core Tables**:
    - `ideals`: The 42 Ideals of Ma'at.
    - `functions`: Core technical functions (e.g., Ingestion, Retrieval, Orchestration).
    - `alignments`: Bidirectional links between ideals and functions with weight/justification.
    - `agent_logs`: Audit trail of how agents (Cline, Grok, etc.) invoked specific ideals.

## Conceptual Mapping (Examples)

| Ma'at Ideal | Technical Function | Justification |
|-------------|-------------------|---------------|
| **7. I live in truth** | Hallucination Check | Ensuring RAG outputs are grounded in source documents. |
| **10. I consume only my fair share** | Core Steering / ZRAM | Respecting host resource limits (Ryzen Zen 2 optimization). |
| **36. I keep the waters pure** | Zero-Telemetry | Maintaining strict data privacy and local-only processing. |
| **40. I achieve with integrity** | Atomic Builds | Ensuring reproducible and verifiable build artifacts. |

## Future Tasks

- [ ] Create `scripts/init_sqlite.py` to scaffold the database.
- [ ] Implement `ShadowGraphConnector` in the RAG API to allow agents to query ethical alignments.
- [ ] Integrate "The Vizier" (Auditor) to populate `agent_logs` during production audits.
