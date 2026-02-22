Vikunja Access & Authorization Instructions

Purpose
- Short guide to obtain an admin/service token for Vikunja so the XNAi Agent Bus can import tasks and use the migrator API.

Steps (UI)
1. Open your Vikunja web UI as an administrator (default port 3456 or as configured).
2. Sign in with an admin account.
3. Navigate to Settings or Admin > API Keys / Service Tokens (UI location may vary by Vikunja version).
4. Create a new token with appropriate scope (service or admin scope for imports).
5. Copy the token value immediately and set it in your environment: export VIKUNJA_URL=http://<host>:<port> export VIKUNJA_TOKEN=<token>

Steps (CLI/container)
- If Vikunja is running in Docker, you can exec into the container and inspect logs or run admin utilities. Example:
  docker-compose exec vikunja sh
  # consult Vikunja documentation for creating admin tokens via CLI or db

If you cannot create a token via UI
- Inspect the database (vikunja's postgres) for api_keys table or consult Vikunja docs; prefer UI creation for safety.

Using the helper script
- scripts/vikunja_api_helper.py will try common endpoints and header schemes to diagnose 401/403 and help verify a token.

Security
- Store VIKUNJA_TOKEN in a secure, local-only secrets store or systemd environment. Do not commit tokens to source control.

If you need me to attempt an authenticated dry-run import, provide a Vikunja service token and VIKUNJA_URL in the environment and I will run the import test.
