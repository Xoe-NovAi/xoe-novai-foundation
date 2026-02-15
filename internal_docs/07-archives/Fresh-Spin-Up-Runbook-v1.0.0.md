# Fresh Spin-Up Runbook (Rootless Podman) - Vikunja v1.0.0

Overview
- Deterministic, idempotent sequence to spin up Vikunja with a fresh DB in a rootless Podman environment.

Prerequisites
- Podman installed; user in podman group (or run with SKIP_DOCKER_PERMISSIONS)
- Secrets: db-pass and jwt-secret created as Podman secrets
- docker-compose.vikunja.yml present
- Python scripts available: memory_bank_export.py, vikunja_importer.py, and recovery script

Spin-Up Steps (idempotent)
- Prune existing Vikunja resources (pods, containers, networks, volumes)
- Create secrets if missing (db-pass, jwt-secret)
- Spin up Vikunja with docker-compose.vikunja.yml
- Health-check loop to ensure API is reachable
- Export memory_bank to vikunja-import.json
- Run importer (dry-run first, then live with token)

Health Checks
- API: http://localhost:3456/api/v1/info
- UI: http://localhost:3456/
- DB connectivity: ensure the Vikunja API can reach its Postgres backend

Rollback
- If spin-up fails, tear down, prune, recreate secrets, and re-run spin-up

Note
- This runbook is designed for automation and can be wired into CI for repeatable spins.
