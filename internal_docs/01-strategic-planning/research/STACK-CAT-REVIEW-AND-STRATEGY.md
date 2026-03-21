Stack-Cat (grok-pack) — Review & Enhancement Strategy

Summary of current script (scripts/stack-cat.py)
- Purpose: context-pack generator that produces Markdown "packs" from configured file lists; supports delta-mode, EKB index updates, archiving, and receipts.
- Strengths: config-driven, delta generation, EKB indexing hooks, progress metadata, receipt generation.
- Observed outputs: `grok-pack-latest.md`, `ekb-exports/receipt-ack-*.md`, and optional sync-protocol updates.

Immediate rename suggestion
- Rename to: `grok-pack-generator.py` or `context-pack-generator.py` (more accurate to its evolved role)

High-level enhancement strategy (for memory_bank + FRQ + multi-agent)
1. Output plugins (priority)
   - Add output format plugins: `markdown-pack` (existing), `vikunja-migrator-json` (produces `vikunja-import.json`), and `agent-package` (per-agent zipped package with metadata).
2. Agent-focused manifests
   - Produce per-agent manifests that annotate each included file with agent labels, frq_score, embed flag, and suggested embedding_model.
3. Direct migrator support
   - Add `--to=vikunja-file` option that emits the exact JSON structure acceptable by Vikunja migrator (or per-task batch scripts) to enable automated uploads.
4. FRQ enhancements
   - Compute `frq_score` heuristically (frontmatter priority + age + tag matches), attach to manifest, and optionally include an embeddings stub (embedding placeholder or actual short vectors when available).
5. Integration with memory_bank_export.py
   - Add a `pack` -> `migrator` handshake: memory_bank_export.py populates standardized frontmatter; stack-cat converts to migrator JSON directly.
6. Tests & CI
   - Add unit tests to verify output format, delta-mode behavior, and migrator JSON schema compatibility.
7. UX & CLI
   - Subcommands: `generate pack`, `export vikunja`, `package agent`, `update-ekb`.
8. Archiving & provenance
   - Improve receipts to include commit hash, pack manifest, and a short validation report (count of tasks, missing files, errors).

Suggested short-term roadmap (3 sprints)
- Sprint 1: Rename script + add `--to=vikunja-file` plugin that writes a simple per-task JSON based on frontmatter mapping.
- Sprint 2: Add per-agent packaging and FRQ_score calculation; integrate with memory_bank_export.py to produce end-to-end migrator JSON.
- Sprint 3: Add unit tests, CI checks, and a `scripts/vikunja_migrator_upload.py` helper that authenticates and POSTs the migrator file (with placeholders for credentials).

Acceptance criteria for enhancement
- `grok-pack-generator.py --to=vikunja-file --output=vikunja-import.json` produces a validated migrator JSON that can be uploaded via Vikunja UI or API (admin token required).
- Per-agent packages include a manifest.json with labels, frq_score, and list of included files.
- Documentation updated (stack-cat guide & user guide) with new commands and examples.

End of strategy
