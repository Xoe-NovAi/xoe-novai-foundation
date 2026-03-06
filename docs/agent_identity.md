# Agent Identity & Memory

Agents are registered in PostgreSQL (`agents` table) and maintain
persistent memory in the filesystem and vector store.

## Registry Schema
- `id`: UUID primary key.
- `name`: human‑readable label.
- `email`, `model`, `runtime`: operational metadata.
- `priority`: computed score for task routing.
- `personality_version`: increments when the agent profile changes.
- `status`: active, idle, retired, etc.
- `last_seen`, `created_at`, `updated_at` timestamps.

## Memory Bank Structure
Each agent has its own folder under `memory_bank/agents/<agent_id>/`:
- `memories.json` – short‑term facts and session logs.
- `personality.json` – evolving profile and preferences.
- `protocols.md` – agent‑specific rules.

Nightly jobs construct a Qdrant/FAISS collection named `mem_<agent_id>` to
support fast retrieval. When an agent starts up it loads both the filesystem
and vector store.

## Personality Evolution
A background service (`agent_evolver`) periodically reviews metrics and
memory to modify the agent’s personality. Changes are recorded in
`personality_history` table.

Agents may also self‑update by appending to `personality.json` during sessions.
