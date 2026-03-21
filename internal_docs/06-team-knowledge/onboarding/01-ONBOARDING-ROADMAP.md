# Onboarding Roadmap — Xoe‑NovAi Foundation (for humans & AI)

Objective: make a newcomer (technical or non‑technical) able to run, maintain, and extend the stack in 1–2 days.

Phases
1. Quickstart (30 min)
  - Read `ASSISTANT-ONBOARDING.md` and `PHASE-5A-EXECUTION-CHECKLIST.md`.
  - Run the smoke tests: `pytest -q tests/test_phase5a_rollback.py tests/test_zram_health_check.py`.
2. Staging practice (2–4 hours)
  - Provision a staging VM and register a self-hosted runner.
  - Run `internal_docs/ansible/playbooks/phase5a_apply.yml` in staging.
  - Execute `phase-5a-stress-test.py --staging` and validate metrics in Grafana.
3. Production readiness (1 day)
  - Add Alertmanager routing and ticketing integrations.
  - Document runbook in `internal_docs/` and add `memory_bank/PHASE-5A-DEPLOYED.md`.

Deliverables
- Tutorial: `docs/tutorials/phase5a-quickstart.md` (step-by-step with screenshots/snippets)
- Runbooks: `internal_docs/` (checklists + troubleshooting)
- Templates: Ansible/CI/templates and `assistant_onboarding/TEMPLATES`
- Tests: unit & integration tests that run in smoke CI and an optional privileged integration

Roles & responsibilities (who does what)
- Owner/Admin (you): approve privileged runner creation, schedule maintenance windows
- Devs: write tests & docs, open PRs, run staging validation
- Assistants (AI): implement code/docs, create tests, open PRs, orchestrate workflows

Maintenance cadence
- Weekly: run smoke CI and review alerts
- Monthly: run staged stress tests on a dedicated runner
- After any kernel/boot change: schedule a rollback verification within 24 hours
