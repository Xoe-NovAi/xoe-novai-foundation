# Opus 4.6 Resource Index

This index compiles all documents, directories, and notes relevant to the XNAi Foundation project across Waves 4, 5, and 6. Opus can use this list to quickly reference material without re‑ingesting large files, reducing token usage.

## High‑level plans & coordination

- `/plan.md` — master implementation plan and task list.
- `/FLEET-COORDINATION.md` — current fleet status log
- `/IMPLEMENTATION-ROADMAP.md` — high‑level timeline for all waves

## Wave 4 (completed)

- `memory_bank/phase4/*` (phase reports, results, SOPs)
- `memory_bank/activeContext.md` — snapshot of current state after Wave 4
- `memory_bank/progress.md` — progress records

## Wave 5 resources

- `memory_bank/wave5` (drafts, specs)
- `internal_docs/00-system/` (strategic reviews, architecture notes)
- `memory_bank/research/WAVE4-WAVE5-RESEARCH-JOBS.md` — pending research tasks
- `config/` and `configs/` for system configuration relevant to Wave 5

## Wave 6 planning

- `internal_docs/02-research-lab/` — long‑term research results
- `memory_bank/strategies/` (multi‑language, observability, etc.)
- `mc-oversight/` (risk assessments, priority matrix, dashboards)

## Key technical directories

- `app/XNAi_rag_app/` — source code for core application
- `docs/` and `docs-new/` — user/developer documentation
- `scripts/` — helper and automation scripts
- `config.toml`, `docker-compose*.yml`, `Makefile` — deployment setup

## Configuration & schema

- `config/doc-curation-bridge.yaml` — curation configuration
- `pyproject.toml`, `requirements*.txt` — Python environment
- `alembic.ini`, `migrations/` — database migration framework

## Benchmarks & analysis

- `benchmarks/` — latency, cognitive enhancements, etc.
- `benchmarks/ground-truth-baseline.yaml` — answers from Opus onboarding

## Memory bank indices and tools

- `memory_bank/handovers/OPUS-4.6-HANDOFF.md` — current handoff
- `memory_bank/COMPLETE-SYNTHESIS-FOR-OPUS-46-2026-02-25.md` — synthesis
- `memory_bank/strategies/CODE-AGENT-PATTERN-ROADMAP.md` — agent design
- `memory_bank/strategies/SQL-MEMORYBANK-ENHANCEMENTS.md` — recent audit

> **Tip:** When reviewing large documents, use the `grep` or `rg` command in the repo and then open only the relevant sections to limit token consumption.
