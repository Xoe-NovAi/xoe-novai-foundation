---
title: Gemini CLI — strategy & processes proposal
status: draft
---

## Objective
Make the Gemini CLI the authoritative agent-side interface for environment introspection, workflow orchestration, and safe staging-only automation for the Xoe-NovAi Foundation stack.

## Core responsibilities
- Query `runtime_probe.json` and answer environment questions.
- Trigger staging-only playbooks (Ansible) with human approval flows.
- Provide per-agent quotas and telemetry for `ask_question` usage.

## Design principles
- Read-only by default; any state change requires explicit `--approve` + human review.
- Idempotent commands with predictable outputs and strict rate limits.
- All CLI actions logged to `memory_bank/agent_actions.log` for audit & RAG ingestion.

## Agent account naming & protocol
- Follow the Foundation standard: `[plugin-name]-[model-name]-[account-delineator]` (examples: `Copilot-Haiku-27`, `Raptor-74`, `Cline-X`).
- The CLI must accept `--account <identifier>` to indicate which agent identity to use and must enforce per-account quotas/telemetry.
- All onboarding and handoff files for accounts live in `expert-knowledge/onboarding/` and must be referenced by the CLI `status` and `help` commands.

## Minimal command set (examples)
- `gemini status --json` → prints `runtime_probe.json` filtered for requested keys.
- `gemini ask --question '...' --model copilot` → calls Copilot `ask_question` with caching and quota enforcement.
- `gemini deploy --playbook phase5a --staging --approve` → stage-only runbook executor (requires human token).

## Safety & governance
- Staging-only automation by default; `--production` available only with multi-signature approval recorded in `memory_bank/approvals/`.
- Per-agent daily caps for expensive operations; alerts if caps near exhaustion.

## Integration points
- `scripts/runtime_probe.py` (source of truth for environment state)
- Prometheus/Grafana for telemetry
- GitHub Actions for CI smoke checks and gated PRs

## Next steps
1. Implement `gemini status --json` to read `runtime_probe.json` (PoC).
2. Add caching layer and per-agent quota enforcement for `ask_question` calls.
3. Draft CLI acceptance tests and add to CI.
4. Train Gemini (RAG) on `projects/foundation-observability/README.md` and memory_bank entries.
