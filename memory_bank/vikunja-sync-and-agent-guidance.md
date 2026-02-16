---
title: "Vikunja Sync & Agent Guidance"
last_updated: 2026-02-16
status: draft
---

Purpose
- Central guidance for exporting memory_bank items to Vikunja and making memory_bank agent-friendly (Grok MC, Claude, Gemini CLI).

Key conventions (memory_bank frontmatter standard)
- Mandatory frontmatter fields for agent-sync:
  - title: string
  - date: YYYY-MM-DD
  - author: string
  - agents: ["agent:gemini-cli","agent:cline-kat"]
  - status: status:backlog|in-progress|review|complete
  - priority: critical|high|medium|low
  - ma_at_ideals: [7,18,41]
  - ekb_links: [] (optional)
  - domains: []
  - embed: true|false  # mark item for embedding ingestion
  - embedding_model: embeddinggemma-300M-GGUF (optional placeholder)
  - frq_score: 0-100  # FRQ boosting score
  - sync_project: "XOH-Sync"  # default project name in Vikunja

Label mapping (export)
- agents -> Vikunja label(s) (e.g., agent:gemini-cli)
- status -> Vikunja status label
- priority -> priority-<value>
- ma_at_ideals -> maat:<n> labels

Export procedure (recommended)
1. Dry run: `python3 scripts/memory_bank_export.py memory_bank vikunja-import.json --dry-run`
2. Review sample `vikunja-import.json` generated in repo root or internal_docs archive.
3. Create target project in Vikunja (e.g., "XOH-Sync") via UI or API.
4. Upload with migrator (vikunja-file) if available, or POST tasks in conservative batches (5-20 tasks).

Manual Grok MC delivery (no GitHub connection)
- For Grok MC, prepare `vikunja-import.json` and manually upload to the Grok Project workspace under Files / Import.
- Tag uploaded tasks/files with `agent:grok-mc` and project `XOH-Sync`.

FRQ + Embeddings guidance
- Add `frq_score` in frontmatter to indicate the importance of the record (used by curation worker to boost similarity scoring).
- Use `embed: true` to mark for embedding; store `embedding_model` in metadata so downstream workers pick the correct embedding runner.
- Suggest periodic background curation job to (a) embed new items, (b) deduplicate semantically similar entries, (c) update FRQ ranks.

Operational constraints
- Keep batches small (5–20) for hosts ~6–8GB RAM; attachments increase memory and I/O needs significantly.
- Prefer no-attachment imports for initial smoke tests.

Agent consumption
- Agents should query Vikunja tasks by label and project, and pull attached metadata fields: frq_score, embedding_model.
- Agents should not assume API tokens exist — request operator to provide token or to run the provided scripts with local secrets.

End of guidance
