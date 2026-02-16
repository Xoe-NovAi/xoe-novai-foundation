Doc Consolidation Recommendations (Non-Destructive)

Purpose
- Provide concise, non-destructive recommendations to consolidate and optimize documentation for speed, clarity, and maintainability.

Core Principles
- Non-destructive: Never delete; archive and preserve originals with metadata.
- Traceability: Store decisions with reasoning and diffs (Redis + remediation log).
- Reversibility: Keep archived copies and commit history so merges can be reversed.
- Minimal friction: Automate detection (Qdrant) and suggest merges; human-in-the-loop (Cline) approves.
- Performance: Cache a small master index in Redis and maintain a FAISS local backup.

High-level Pipeline (recommended)
1. Semantic Analysis (Copilot)
   - Embed all docs into Qdrant collection `phase-5-audit-documents`.
   - Run similarity queries to produce an overlap matrix (doc pairs + similarity scores).
2. Batch Audit (Cline-led)
   - Group docs into batches (core planning, indexes, summaries, Claude materials, status, supporting).
   - Cline reviews batches, writes findings to PHASE-0-AUDIT-FINDINGS.md and stores decisions in Redis keys (doc-consolidation:*, doc-update:*, doc-archive:*).
3. Consolidation (Copilot executes, non-destructive)
   - For merge decisions: create merged target, preserve unique sections, archive source to /internal_docs/_archive/ (or /02-archived-phases/), record merge diff in PHASE-0-REMEDIATION-LOG.md.
   - For archive decisions: move files to archive with metadata frontmatter and an archive note in Redis.
   - For updates: apply targeted edits, add an "updated_by" metadata line and store decision in Redis.
4. Validation & MkDocs build
   - Run link-check, build MkDocs audit site, run quick smoke tests, and produce a final audit report.

Practical Rules & Conventions
- Frontmatter standard (YAML) required at top of every doc:
  ---
  last_updated: 2026-02-16T13:50:00Z
  status: draft|current|archived
  owner: <agent-or-human>
  persona_focus: <developer|operator|user>
  tags: [phase-5, planning, readiness]
  ---
- Naming: Prefer single canonical MASTER-PLAN or EXPANDED-PLAN; avoid duplicate "FINAL-" variants — consolidate under one canonical name and keep previous versions archived.
- Indexing: Maintain exactly one master index (MASTER-INDEX-PHASE-5-FINAL.md) and generate per-phase quick-reference sheets in /PHASE-EXECUTION-INDEXES/ for fast lookups.
- Archival: Move obsolete files to /internal_docs/02-archived-phases/ with metadata and a reason; never delete from repository history.

Automations & Tests
- Pre-commit hook: enforce frontmatter presence, validate YAML, run link-checker (mkdocs linkcheck or custom script).
- CI: run `mkdocs build` and `linkcheck`; fail PRs that introduce broken links or missing frontmatter.
- Periodic re-index: nightly or on-demand Qdrant re-index job to refresh vector embeddings.
- Backup: After consolidation, build FAISS index and store under session folder as an offline fallback.

Non-destructive safeguards
- Always create an "archive/merged-from" copy before any merge.
- Store decision metadata in Redis for auditability and to allow Copilot/Cline to resume.
- Keep remediation log with diffs and timestamps (PHASE-0-REMEDIATION-LOG.md).

Quick Wins (30-90 minutes)
- Run Qdrant semantic overlap for the 31 files and produce the overlap matrix.
- Consolidate obvious index duplicates (MASTER-INDEX-* files) by archiving one and keeping canonical index.
- Create per-phase 1-page quick-reference sheets for the 16 phases to reduce lookup time.
- Add frontmatter to top 10 high-traffic docs where missing.

Next recommended action
- Start Stage 1 (embed documents to Qdrant, generate overlap matrix). Copilot can run this immediately; Cline will be fed batches for review.

Files created (session-state)
- /home/arcana-novai/.copilot/session-state/600a4354-1bd2-4f7c-aacd-366110f48273/doc_consolidation_recs.md

Notes
- These recommendations mirror the PHASE-0-EXTENDED plan and prioritize non-destructive behavior, traceability, and rapid semantic-driven consolidation.
- Will iteratively refine this file using the memory_bank_onboarding.md context and subsequent audit outputs.
