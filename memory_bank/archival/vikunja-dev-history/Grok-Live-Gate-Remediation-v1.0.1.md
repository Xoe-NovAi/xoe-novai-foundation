Grok Live Gate Remediation - Vikunja v1.0.0 (Remediation Plan v1.0.1)

Date: 2026-02-07
Author: Architect

Overview
- This document specifies the remediation plan to move from a successful dry-run to a live, write-enabled Vikunja migration gate in a rootless Podman environment. It enumerates the blockers, required stack data, and concrete actions Grok must perform or verify, along with deliverables and acceptance criteria.

Goals
- Stabilize Podman rootless spin-up to achieve a healthy Vikunja API endpoint ready for live imports.
- Automate secrets provisioning, prune/groom processes, and preflight checks to enable deterministic, repeatable gate runs.
- Extend importer with auto-create for projects/namespaces and improved logging for post-run verification.
- Ensure token lifecycle governance and zero telemetry in live runs.

Stack Data to Collect (Inputs for Grok)
- Host/Environment:
  - OS version, kernel, and distribution
  - Podman version and compose version
  - Subuid/Subgid status, user namespaces configuration
  - Current user group memberships
  - Any host firewall or SELinux enforcing mode that could affect Podman networking
- Podman state:
  - podman ps -a
  - podman pod ls
  - podman network ls
  - podman secret ls
  - podman volume ls
- Docker-compose config and stack state:
  - docker-compose.yml contents (sensitive fields redacted as needed)
  - docker-compose.yml contents (if relevant for live gate)
- Vikunja stack state:
  - Vikunja DB container (vikunja-db) status
  - Vikunja API container (vikunja-api) status and healthcheck results
  - Vikunja Frontend container (vikunja-frontend) status
  - Vikunja-proxy (caddy or nginx) status and port mappings
- Secrets:
  - List of Podman secrets present (db-pass, jwt-secret) and how they're mounted
  - Confirm external: true semantics in docker-compose.yml
- Tokens:
  - Admin bootstrap token state and process to create migration-live token
  - Token scope: full access for POST /tasks, plus ability to create projects
  - Token rotation policy and revocation plan
- Data exports/import:
  - vikunja-import.json payloads (size, sample payloads)
  - Importer results from dry-run (log snippets, counts)
- API surface (current):
  - Endpoints currently supported (POST /tasks, POST /projects, etc.)
  - Presence/absence of batch endpoints

Data to Deliver (Grok should produce)
- Grok Live Gate Remediation v1.0.1 (markdown) with:
  - Root cause analysis for Podman blockers and API startup failure
  - Step-by-step remediation actions (idempotent, safe)
  - Podman hardening checklist (group membership, userns keep-id, prune commands)
  - Preflight script outline to validate readiness
  - Importer enhancements spec: auto-create projects/namespaces, better logging
  - Token management guidelines (creation, rotation, revocation)
  - Runbook for live gate (phases: prune, spinup, token, dry-run, live-import)
  - Preflight-runbook (verification of environment, secrets, network)
- Optional: Grok-Live-Gate-Findings-v1.0.1.md that captures root causes and fixes.

Acceptance Criteria (Gate Criteria)
- Podman is configured to allow a clean spin-up with rootless containers (no permission denies, no ghost networks, no dependency graph errors).
- Vikunja API starts and responds at http://localhost:3456/api/v1/info within X minutes of spin-up.
- Admin bootstrap completes in sandbox; migration-live token can be generated with full scope.
- Dry-run importer prints 17 payloads; no HTTP POSTs occur.
- Live importer creates tasks in the target Vikunja instance and validates via API and UI (in sandbox).
- All actions are idempotent; rerunning gate steps yields the same outcome without unexpected writes.

Deliverables (Owner: Grok) 
- Grok-Live-Gate-Remediation-v1.0.1.md (this doc; skeleton ready to fill)
- Grok-Live-Gate-Findings-v1.0.1.md
- Grok-Live-Gate-Runbook-v1.0.1.md
- Grok-Podman-Hardening-v1.0.1.md
- Grok-Importer-Enhancements-v1.0.1.md
- Grok-Token-Management-v1.0.1.md
- Grok-Preflight-Script-v1.0.1.md

Timeline
- Draft: 1 day
- Validate in sandbox: 2–3 days
- Finalize deliverables: 1 day after validation

Notes
- This remediation plan assumes you’ll run these gates in a sandbox environment. If you want to run in this host, ensure you follow Podman rootless hardening steps and have a clean environment before re-run.
