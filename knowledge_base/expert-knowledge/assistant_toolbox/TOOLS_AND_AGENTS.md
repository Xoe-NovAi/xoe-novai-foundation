# Tools & Agents — Xoe‑NovAi Foundation (assistant reference)

This document inventories all tools, agentic capabilities, and external assistants available to contributors and automated agents.

Local repo tools
- Python + pytest — unit & integration tests (run locally and in CI)
- Ansible — idempotent system configuration (playbooks in `ansible/`)
- GitHub Actions — CI workflows (`.github/workflows`)
- Node exporter / Prometheus / Grafana — monitoring stack in `monitoring/`
- scripts/ — host utilities (health-check, stress test, rollback)

Agentic & external assistants
- GitHub Copilot (this assistant) — code edits, tests, PRs, run commands via the workspace
- gh CLI — GitHub automation: PR creation, workflow triggering, runner inspection
- Claude.ai Sonnet / Grok MC — external research & deep-document drafting (use for long-form authoritative docs)
- Gemini CLI (large local context) — use when you need 1M token context & local file indexing

How to pick a tool
- Quick code changes & tests: use Python/pytest + GitHub Copilot
- System changes on hosts: write Ansible playbook + test on a staged runner
- Long-form policy, manuals, or deep research: draft in `internal_docs/` and optionally use Claude/Grok for enrichment
- Large-context synthesis across files: use Gemini CLI and the `expert-knowledge/` directory to store outputs

Agent usage templates
- Research: create `expert-knowledge/research/<topic>.md` with links & concise findings. Use Claude/Grok to populate and cite.
- Code change: create test first (TDD), update docs, open PR with staged CI verification.
- Ops change: add Ansible + runbook + rollback script; add monitoring & alerts; validate on staging runner.

Keeping this up to date
- Update `expert-knowledge/assistant_toolbox/TOOLS_AND_AGENTS.md` when new tools are added.
- Add short `how-to` snippets to `internal_docs/assistant_onboarding/` for any new capability.
