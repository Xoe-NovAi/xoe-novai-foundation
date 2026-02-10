# Grok MC Findings Brief: Vikunja Integration

Summary
- Rootless Podman-based Vikunja deployment is blocked by secrets lifecycle, network teardown, and container lifecycle hygiene on initial spin-up. A structured runbook and automation are needed to achieve a reliable fresh spin-up.

Pain Points Observed
- Missing secrets (db-pass, jwt-secret) prevent up; rootless Podman requires secrets to exist prior to startup.
- Orphaned pods/networks after interruptions block clean spin-ups (xnai_network, rootless network namespaces).
- Interactive prompts and manual steps slow down recovery and automation.

Root Causes
- Secrets provisioning not automated or guaranteed before up.
- Residual resources from aborted runs block new deployments.
- Lack of an end-to-end automation path for fresh setups.

Recommendations (Concrete Actions)
- Implement a deterministic, idempotent recovery/reboot script that:
  - Prunes stale resources safely
  - Creates Podman secrets if missing (db-pass, jwt-secret)
  - Starts Vikunja stack with a clean DB
  - Exposes a non-interactive import path for memory_bank data
- Add a runbook for fresh spin-ups (step-by-step) and ensure it’s versioned and auditable.
- Provide a frontmatter-to-Vikunja-mapping guide to automate memory_bank→Vikunja imports reliably.

Impact and Severity
- Improves reliability of Vikunja integration and reduces MTTR for fresh spin-ups.
- Enables automation that lowers manual toil during onboarding and upgrades.

Risks
- Secrets leakage risk if run outside secure CI; mitigate with proper secret handling and rotation.
- If volumes persist, data may not align with new DB schema; ensure clean DB initialization.

Dependencies
- Podman 3+ with rootless mode, BuildKit cache for speed, and network isolation patterns.
- Availability of memory_bank export (vikunja-import.json) and importer script.

Next Steps
- Grok MC to deliver the Findings Brief to the broader team and finalize the runbook.

References
- See docs/06-development-log/vikunja-integration/grok-mc-research-plan.md for scope and research questions.
