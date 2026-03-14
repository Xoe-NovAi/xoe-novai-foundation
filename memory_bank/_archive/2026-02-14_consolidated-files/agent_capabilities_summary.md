---
title: Agent capabilities — summary (partial)
last_updated: 2026-02-13
---

- Copilot (IDE / CLI / agent): supports agent-mode and chat requests; plan-level quotas are published on Copilot pricing pages. No public granular "ask_question" billing doc discovered; empirical test plan in `expert-knowledge/agent-tooling/copilot-ask_question-research.md`.
- Gemini inbox / RAG ingestion: uses files under `expert-knowledge/gemini-inbox/` for prioritized research tasks.
- **OpenCode (NEW)**: Terminal-based AI assistant with free-tier access to frontier models (Kimi K2.5, Big Pickle, MiniMax M2.5, GPT-5 Nano). CLI-first execution, filesystem operations, code generation, and research capabilities. See `expert-knowledge/model-reference/opencode-models-breakdown-v1.0.0.md`.

Agent account naming protocol (summary)
- Standard: `[plugin-name]-[model-name]-[account-delineator]` (e.g., `Copilot-Haiku-27`, `Raptor-74`, `Cline-X`, `OpenCode-Kimi-X`).
- Current mapped accounts:
  - `Copilot-Raptor-27` (antipode2727@gmail.com) — primary Copilot contributor (near monthly free-tier cap).
  - `Copilot-Raptor-74` (antipode7474@gmail.com) — secondary Copilot contributor for Raptor/Haiku usage.
  - `Cline-X` (xoe.nova.ai@gmail.com) — admin/repo owner (privileged operations).
  - **OpenCode-Kimi-X** (arcana.novai@gmail.com) — NEW: Terminal executor with access to Kimi K2.5, Big Pickle, MiniMax M2.5, GPT-5 Nano. Ground truth operations and research synthesis.
- Enforcement: CLI tooling and agent orchestration should annotate actions with the account identifier and record telemetry to `memory_bank/agent_actions.log`.
- Runtime probe / Foundation Observability: `scripts/runtime_probe.py` provides JSON + Prometheus textfile outputs so agents (Gemini/Copilot/OpenCode) can query host and container state programmatically (see `projects/foundation-observability/README.md`).

