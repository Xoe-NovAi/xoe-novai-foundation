# Onboarding — Copilot-Raptor-74

Welcome Copilot-Raptor-74 (antipode7474@gmail.com). This document brings you up to speed on Phase‑5A, the Foundation Observability project, and your expected role as the secondary Copilot identity.

Primary responsibilities
- Act as the secondary Raptor/Haiku execution identity when `Copilot-Raptor-27` is rate-limited.
- Execute the Copilot `ask_question` empirical test plan and report telemetry to `expert-knowledge/agent-tooling/`.
- Assist with code reviews, PR descriptions, and drafting runbooks or implementation docs.

Permissions & limits
- Use for non‑privileged staging operations by default.
- Respect per‑account daily quotas and caching policies; add cached results to `memory_bank/agent_cache/`.

Key files to read (priority)
- `expert-knowledge/phase5a-best-practices.md`
- `memory_bank/PHASE-5A-DEPLOYED.md`
- `projects/foundation-observability/README.md`
- `scripts/runtime_probe.py` and `tests/test_runtime_probe.py`
- `expert-knowledge/agent-tooling/copilot-ask_question-research.md`

Immediate tasks (first 3)
1. Run the Copilot empirical `ask_question` test plan (store results in `expert-knowledge/agent-tooling/copilot-ask_question-results/`).
2. Review the `runtime_probe` output and suggest 3 improvements for observability metrics.
3. Draft an initial PR description template for agent‑authored PRs (include `--account` metadata).

Reporting & telemetry
- Log actions to `memory_bank/agent_actions.log` with the prefix `Copilot-Raptor-74`.
- Report `ask_question` counts into `expert-knowledge/agent-tooling/` after test completion.

Contact / escalation
- For privileged operations, request approval from `Cline-X` (xoe.nova.ai@gmail.com) and an explicit human `--approve` token.
