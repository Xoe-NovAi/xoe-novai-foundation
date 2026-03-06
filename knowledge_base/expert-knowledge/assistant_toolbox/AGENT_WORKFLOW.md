# Agent Workflow & Strategy — coordinating assistants

Goal: allow multiple AI agents and human contributors to collaborate reliably on code, docs, and ops.

Core rules for agents
- Read the checklist and tests before making changes.
- Always add or update tests for behavior changes.
- Keep changes small and focused; open draft PRs for larger work.
- Update `memory_bank/` with decision rationale when making non-trivial changes.

Agent handoff pattern
1. Plan mode: agent proposes tasks, required approvals, and expected outcomes.
2. Agent execution: create branch, implement changes, add tests, run local tests, push branch, open PR. (This is what GitHub Copilot does.)
3. Operator validation: human approves and triggers privileged CI or runs Ansible on staging.
4. Post-deploy: agent updates `memory_bank/` with results and lessons learned.

Using other assistants
- For deep research or long-form docs, call Claude.ai or Grok MC and store outputs under `expert-knowledge/`.
- For large-context code synthesis across many files, use Gemini CLI to index the repo and create a summary file under `expert-knowledge/`.
