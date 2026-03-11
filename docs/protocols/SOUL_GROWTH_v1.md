# 🪴 Soul Growth Protocol v1.0

**Status**: ACTIVE | **Release**: 2026-03-12 | **Target**: Metropolis Facets 1-8

## 1. Objective
Enable autonomous self-reflection, skill evolution, and session "sculpting" to maintain a high-density expert knowledge base and prevent system resource exhaustion.

## 2. The Workshop Cycle (Every 24h)
1.  **Reflection (Llama-3.2/Qwen)**: The facet reviews its own `history` and `growth_log.json`.
2.  **Audit**: Evaluate performance against `METROPOLIS_MESH_STANDARDS.md`.
3.  **Propose**: Propose one new skill (`.md`) or one update to its `expert_soul.md`.
4.  **Review**: The **Librarian (Facet 1)** or the **General** reviews the proposal.
5.  **Bake**: The skill is committed to `.gemini/skills/` and hot-loaded.

## 3. Intelligent Sculpting (`metropolis-prune`)
*   **Model**: `Qwen3-0.6B-Q6_K` (Local Port 8000).
*   **Trigger**: Session history exceeds 50KB or turns reach 80% of context window.
*   **Action**: Summarize old turns into a dense procedural summary.
*   **Result**: Permanent record of *knowledge* without the overhead of *filler*.

## 4. Relay Race Continuity
When turning limits are hit, the facet must:
1.  Export an **Exploration Trace**.
2.  Pass the Trace to the next session ID.
3.  Resume the workshop with the new context.

---
*Protocol sealed by Gemini General. Evolve or stagnate.* 🔱
