# Vikunja Fresh Spin-Up Runbook (Rootless Podman)

Purpose
- Provide a deterministic, non-interactive flow to spin up Vikunja with a fresh DB and rootless Podman, ready for data import from memory_bank.

Prerequisites
- Podman installed and user in podman group or run with SKIP_DOCKER_PERMISSIONS
- Secrets: db-pass and jwt-secret created as Podman secrets
- docker-compose.yml available with proper secret references
- Python environment with memory_bank_export.py and Vikunja importer available

Run Sequence (idempotent)
- Prune existing Vikunja-related resources (pods, containers, networks, volumes)
- Create secrets if missing (db-pass, jwt-secret)
- Bring up Vikunja using docker-compose.yml
- Wait for API to be reachable at http://localhost:3456/api/v1/info
- Export memory_bank to vikunja-import.json (one-time or on demand)
- Import data via the Vikunja importer (dry-run first, then live with token)

Health Checks
- Vikunja API health: curl -sSf http://localhost:3456/api/v1/info
- UI health: curl -sSf http://localhost:3456/  | grep -i Vikunja or open in browser
- DB connectivity: ensure Vikunja can connect to its Postgres backend

Rollback Plan
- If Vikunja fails to boot, tear down containers, prune volumes, re-create secrets, and re-run spin-up.
- If data import fails, revert to a clean DB and re-import with a fresh vikunja-import.json

Operational Notes
- All actions are logged in docs/06-development-log/vikunja-integration/recovery-log.md (or specific recovery logs).
