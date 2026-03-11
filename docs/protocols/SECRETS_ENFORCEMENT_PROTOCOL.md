---
title: Secrets Enforcement Protocol
version: 1.0
status: active
tags: [security, secrets, protocol, metropolis]
last_sync: 2026-03-10
---

# 🔐 Secrets Enforcement Protocol (v1.0)

**Mandate**: ZERO hardcoded secrets in version-controlled files.

## 1. Enforcement Rules
- **NO Hardcoded Passwords**: Never use plain-text passwords or weak defaults (e.g., `changeme123`, `vikunja123`) in code or config.
- **NO Fallbacks in Compose**: Avoid `${VAR:-default}` for sensitive credentials in `docker-compose.yml`. Use `${VAR:?error}` to enforce environment variables.
- **Strict .env Usage**: All credentials must be sourced from `.env` or a secure secrets manager.
- **Mandatory Variable Naming**: Use uppercase, descriptive names (e.g., `REDIS_PASSWORD`, `JWT_PRIVATE_KEY`).

## 2. Verification Steps
- **Pre-Commit Check**: Run `grep` for known weak patterns before staging changes.
- **Agent Initialization**: Every new chat session must verify that the current environment is using the secure secret management pattern.

## 3. Secret Rotation Pattern
To rotate a secret:
1. Generate a new secret: `openssl rand -base64 32`.
2. Update `.env`.
3. Update the running services: `podman-compose up -d`.
4. Update the Master Project Index (MPI) with the rotation date.

---
*Locked by Gemini General. Protocol active across the Metropolis Mesh. 🔱*
