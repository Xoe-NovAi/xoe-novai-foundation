# Assistant Onboarding — Xoe‑NovAi Foundation

Purpose: give any human or AI assistant a single-page, action-oriented reference to become productive in this repo within 30 minutes.

Quick start
- Repo root: `/home/arcana-novai/Documents/xnai-foundation`
- Important folders:
  - `internal_docs/` — operational & strategy docs (read-first for procedures)
  - `ansible/` — playbooks/roles for system changes
  - `monitoring/` — Grafana/Prometheus dashboards & rules
  - `scripts/` — host-level helpers (health-check, rollback, stress tests)
  - `tests/` — pytest unit/integration tests
  - `memory_bank/` — operational memory and persistent notes

Essential commands
- Run targeted Phase‑5A tests:
  pytest -q tests/test_phase5a_rollback.py tests/test_zram_health_check.py
- Open draft PR (admin account):
  gh pr create --draft --base main --head <branch> -t "<title>" -b "<body>"
- Trigger Phase‑5A integration (privileged runner required):
  gh workflow run phase5a-integration.yml --ref <branch>

Files to read first
- internal_docs/01-strategic-planning/PHASE-5A-EXECUTION-CHECKLIST.md
- internal_docs/01-strategic-planning/PHASE-5A-ZRAM-BEST-PRACTICES.md
- scripts/phase5a-rollback.sh
- ansible/playbooks/phase5a_apply.yml

How assistants should work here
1. Read the checklist and tests for the feature you will change.
2. Make small, well‑scoped edits and add unit tests that run in CI smoke jobs.
3. Add docs under `internal_docs/` and `memory_bank/` for operational playbooks.
4. Use PRs for review; include a staging validation plan and rollback steps.

Where to update this file: keep `internal_docs/assistant_onboarding/*` in sync with `memory_bank/` entries.
