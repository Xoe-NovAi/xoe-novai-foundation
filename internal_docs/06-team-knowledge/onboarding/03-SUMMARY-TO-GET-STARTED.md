# Starter Checklist — what to do first (2–30 minutes)

1. Read these files (5–10 minutes):
  - `internal_docs/assistant_onboarding/ASSISTANT-ONBOARDING.md`
  - `internal_docs/01-strategic-planning/PHASE-5A-EXECUTION-CHECKLIST.md`
2. Run the Phase‑5A unit tests (5 minutes):
  - pytest -q tests/test_phase5a_rollback.py tests/test_zram_health_check.py
3. If you have admin access, register a self-hosted runner following `assistant_onboarding/TEMPLATES/PROVISION_RUNNER_TEMPLATE.sh` (15–30 minutes).
4. Open PRs for any changes and request a staging validation run.

Contact points
- Use GitHub PRs and the `phase5a-integration` workflow for staged validation.
- For help: open an issue titled "Help: Phase‑5A staging" and mention your account.
