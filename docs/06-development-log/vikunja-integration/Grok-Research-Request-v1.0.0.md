# Grok Research Request - Vikunja Live Gate (v1.0.0)

Date: 2026-02-07
Author: Grok Research Liaison
Version: v1.0.0

Executive goal
- Collect all stack data and define concrete questions so Grok can fill knowledge gaps and drive the live Vikunja gate with a safe, idempotent plan.

Scope and objectives
- Identify remaining blockers preventing a live Vikunja API startup in a rootless Podman environment.
- Define the exact data to collect from the host, stack, and Vikunja surface to diagnose blockers fully.
- Produce an action-oriented remediation plan (Remediation v1.0.1) and a minimal preflight gate.
- Define the required token flow and admin bootstrap steps to enable a real migration token.
- Outline a dry-run → live gate transition with acceptance criteria.

Inputs to Grok (host data to collect)
- Host/OS: distro, kernel, Podman/compose versions, group membership, subuids, user namespaces
- Podman state: current containers, pods, networks, external secrets, volumes
- docker-compose.yml and docker-compose.yml content (sanitized for sensitive fields)
- Vikunja stack state: DB container health, API container health, frontend/container health, proxy status
- Secrets: presence, mounting strategy (file-based vs env), external secrets flags
- Tokens: admin bootstrap status, migration-live token availability and scopes
- Data exports: vikunja-import.json size and payload shapes; sample payloads
- API surface: available endpoints and constraints (e.g., no batch endpoint)
- Logs: startup logs around API readiness and any error traces
- Health checks: curl outputs parsing for /api/v1/info if API comes up
- Preflight: prerequisites readiness (network ports, API token readiness, export presence)

Deliverables for Grok
- Grok-Live-Gate-Remediation-v1.0.1.md
- Grok-Live-Gate-Findings-v1.0.1.md
- Grok-Live-Gate-Runbook-v1.0.1.md
- Grok-Podman-Hardening-v1.0.1.md
- Grok-Importer-Enhancements-v1.0.1.md
- Grok-Token-Management-v1.0.1.md
- Grok-Preflight-Script-v1.0.1.md
- Grok-Research-Plan-v1.0.1.md
- Grok-Research-Plan-Template-v1.0.1.md

Timeline
- Draft within 1–2 days; delivery of Remediation v1.0.1 and Supporting artifacts; then follow-up review.

Data formats and outputs
- Concrete payload samples from dry-run importer (as-is) for review; format remains identical to current Vikunja importer outputs
- Logs with key events (spin-up success/failure, health checks, token creation status)

How to use this request
- Grok will provide fillable artifacts that map the current blockers to actionable steps, including concrete commands and expected outputs.
