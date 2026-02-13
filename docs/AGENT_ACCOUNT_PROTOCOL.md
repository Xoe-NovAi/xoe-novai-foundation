# Agent Account Naming & Usage Protocol

Purpose
- Standardize how agent/service accounts are named, referenced, and used across the Foundation stack for auditability, quota management, and clear handoffs.

Naming convention
- Format: `[plugin-name]-[model-name]-[account-delineator]`
  - Examples: `Copilot-Haiku-27`, `Copilot-Raptor-74`, `Cline-X`.
- Use the full identifier when account differentiation matters (billing, quota, audit). If not critical, `Copilot-[model]` shorthand is acceptable.

Primary account mapping (current)
- `Copilot-Raptor-27` — antipode2727@gmail.com (primary active Copilot account; near monthly free‑tier cap)
- `Copilot-Raptor-74` — antipode7474@gmail.com (secondary; use when `-27` is rate‑limited)
- `Cline-X` — xoe.nova.ai@gmail.com (admin / repo owner; privileged operations)

Operational rules
- CLI and agent tooling MUST accept `--account <identifier>` to indicate which identity to use.
- All agent actions must be logged with account identifier and recorded in `memory_bank/agent_actions.log`.
- Per‑account quotas must be enforced in staging before production use.

Onboarding & handoff
- Per‑account onboarding documents are stored in `expert-knowledge/onboarding/` and include:
  - Role & responsibilities
  - Allowed operations & limits
  - Key files & runbooks to read
  - Handoff checklist

Telemetry & billing
- Track `ask_question` counts per account and expose daily quotas in the agent dashboard.
- If an account reaches 90% of its monthly quota, alert the owner and automatically throttle non‑critical agent usage.

Audit & governance
- `CODEOWNERS` should include owners for account-level automation directories.
- Any privilege escalation or use of `Cline-X` must require two human approvals documented in `memory_bank/approvals/`.

Where this is referenced
- `CONTRIBUTING.md`, `memory_bank/agent_capabilities_summary.md`, `expert-knowledge/gemini-cli/strategy-proposal.md` (search for "account" or "Copilot-" to find references).
