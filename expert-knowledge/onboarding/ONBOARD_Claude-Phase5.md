# Onboarding — Claude.ai (Phase‑5 update)

Purpose
- Bring Claude.ai up to date with the Phase‑5A strategy, artifacts, and current implementation scaffolding so Claude can re‑join the cooperative execution and research workflow.

Files to read (priority)
- `expert-knowledge/phase5a-best-practices.md`
- `expert-knowledge/agent-tooling/copilot-ask_question-research.md`
- `memory_bank/PHASE-5A-DEPLOYED.md`
- `expert-knowledge/gemini-inbox/INBOX_Phase5A_Agent-Collab.md`
- `projects/foundation-observability/README.md`
- `monitoring/prometheus/rules/phase-5a-alerts.yml` (alerts & runbooks)

Tasks for Claude (first pass)
1. Review Phase‑5A documents and propose any missing test cases or runbook steps.
2. Produce a high‑confidence technical brief (1–2 pages) summarizing remaining risks and mitigation steps for staging→production promotion.
3. Draft detailed implementation steps for Vikunja orchestration tasks and CLI agent sync.
4. Assist in writing `TEMPLATE-RUNBOOK.md` entries for zRAM operations and rollback.

Notes for Claude
- Claude does NOT have local file access here, but can read repository files via your connected GitHub account; reference the exact paths above when querying the repo.
- Save outputs to `expert-knowledge/agent-tooling/claude-phase5/` and tag draft outputs `TODO: verify` where assumptions were required.
