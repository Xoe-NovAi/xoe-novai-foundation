# Omega Stack Documentation

This directory contains the high-level documentation used by agents and
contributors. Sections:

- `architecture/` – architectural diagrams and design notes
- `research_workflow.md` – scholarly research project process
- `agent_identity.md` – how agents are registered and persist memory
- `agent_collaboration.md` – protocols for claiming and inviting tasks
- `metrics_promotion.md` – metric definitions and ranking logic

To add new documentation:
1. Create or edit the relevant Markdown file under `docs/` or subfolder.
2. Run `omega doc lint` (placeholder) to ensure formatting.
3. Commit and notify via Vikunja `documentation` task.

Agents are required to update documentation along with code changes. The
`doc-sync.sh` script (in `scripts/`) is responsible for syncing tasks and
creating reminders or PRs. This is currently a stub and should be extended
as part of the `vikunja-automation` research project.
