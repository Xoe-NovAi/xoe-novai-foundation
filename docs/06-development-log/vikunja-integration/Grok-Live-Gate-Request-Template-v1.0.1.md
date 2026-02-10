# Grok Live Gate Research Request Template v1.0.1

Overview
- Purpose: Detail the data Grok needs to fill the Live Gate Remediation (v1.0.1).

What Grok needs to collect from the local stack (data payload)
- Host/Env: OS, kernel, Podman version, compose version, subuid/subgid status, user namespaces, security contexts
- Podman state: pods, containers, networks, and secrets; any ghost resources; logs from failing components
- Docker compose: content excerpt (sanitized) for vikunja docker-compose.yml and external secrets
- Vikunja: container health status; DB status; API readiness; proxy status
- Secrets: presence, mounting behavior, and how they're consumed by services
- Tokens: admin bootstrap token, migration-live token, and rotation policy; exact scopes
- Importer: dry-run output, sample payloads, and counts; any encountered validation errors
- vikunja-import.json: size, sample payloads, and shape confirmation
- Health signals: curl /info responses in sandbox or live gate
- Logs: tail/sequence of startup logs around health checks
- Preflight: results of any preflight checks (prereqs met, port availability, secrets mounted)
- Project/Namespace plan: how importer will ensure projects/namespaces exist or auto-create

What success looks like
- The gate transitions from dry-run green to live import with a healthy Vikunja API in a sandbox, then to a live gate with a successful import.
- All steps are idempotent; re-running the gate yields identical outcomes.

Data to be delivered to Grok (format: markdown, with embedded logs or snippets)
- A few representative payload samples from the dry-run importer
- The exact Podman state dump (ps -a, pod ls, network ls, secret ls)
- The docker-compose.vikunja.yml excerpt and token handling notes
- API token policy summary from Vikunja UI (scope, expiry, revocation)
- Health-check results and timestamps
- A short risk assessment and mitigation notes for the live gate

Timeline
- 1–2 days to fill; wire into repository docs for review
