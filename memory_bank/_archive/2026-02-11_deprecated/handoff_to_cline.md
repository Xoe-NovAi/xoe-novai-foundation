# Handoff to Cline - Vikunja Live Gate (Handoff v1.0.0)

Overview
- This document describes the handoff from the current memory_bank context to the Cline engineering cohort for executing the live gate remediation, seed work, and post-migration validation against Vikunja.

Scope of handoff
- Spin-up remediation in a rootless Podman environment: fix prune/network issues, ensure secrets provisioning, bring Vikunja online, obtain a migration-live API token, and perform a dry-run then live import.
- Seed active projects/workspaces in Vikunja as needed for gating and test imports (Xoe-NovAi Foundation, Foundation migration project, Memory Bank Sync workspace).
- Implement importer enhancements: automatic namespace/project creation, enhanced logging, and robust dry-run → live flow.
- Define preflight checks and acceptance criteria for gate transition.

Artifacts to transfer (current state)
- Finalization Pack v1.0.x artifacts (Remediation, Findings, Runbooks) so you can replicate the live gate steps.
- The 17-task dry-run payloads (vikunja-import.json) and the importer script outputs stored in the repo.
- Token handling plan: token creation, rotation policy, and how to apply tokens during live gate.
- Active memory_bank context (activeContext.md) with a handoff_to_ceiling for traceability.

Data to seed in Vikunja (sandbox)
- Workspace: Xoe-NovAi Foundation
- Projects: Foundation (Migration), Memory Bank Sync, Documentation & Governance
- Namespaces: If your policy requires a namespace per project, seed accordingly.
- Admin bootstrap steps: how to create the admin user and migration-live token in the sandbox.

Preflight and gating plan (handoff expectations)
- Preflight script execution results: secrets mounted, network clean, Vikunja API reachable (sandbox), vikunja-import.json present
- Dry-run importer results in sandbox: 17 payloads prepared, no POSTs performed
- If dry-run passes, proceed to live import in sandbox and verify via API/UI

Acceptance criteria for successful handoff
- Sandbox gate completes a dry-run with 17 payloads printed and no writes
- Sandbox gate completes a live gate sequence up to a safe point (e.g., token established) with no production risk
- All steps are idempotent and auditable; runbooks updated with actual logs and outcomes

Roles and responsibilities (handoff owners)
- Architect: overall handoff owner and verification authority
- Cline: execute live-gate remediation, seed projects, run importer in sandbox, validate results
- Gemini CLI: provide automation hooks and ensure repo tooling supports the handoff

Next steps for the receiving team
- Review this handoff doc, the included artifacts, and the proposed sandbox seed plan
- Confirm sandbox environment access and provide admin credentials or a sandbox URL
- Execute the handoff playbook in the sandbox and report back with logs and results
