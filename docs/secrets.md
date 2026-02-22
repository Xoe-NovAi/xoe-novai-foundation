# Secrets Management

> **Important**: This guide covers file-based secrets for rootless Podman compatibility.

---

## Overview

XNAi Foundation uses file-based secrets for secure credential management. This approach is required for rootless Podman containers and provides better security than environment variables for sensitive data.

---

## Secret Files

### Redis Password

**File**: `secrets/redis_password.txt`

```bash
# Generate a secure password
openssl rand -base64 32 > secrets/redis_password.txt

# Set permissions (critical!)
chmod 600 secrets/redis_password.txt
```

### API Key

**File**: `secrets/api_key.txt`

```bash
# Generate API key
openssl rand -hex 32 > secrets/api_key.txt
chmod 600 secrets/api_key.txt
```

### Vikunja JWT Secret

**File**: Set via environment variable `VIKUNJA_JWT_SECRET`

```bash
# Generate JWT secret
openssl rand -base64 32
```

Add to `.env`:
```
VIKUNJA_JWT_SECRET=your_generated_secret_here
```

---

## Directory Structure

```
xnai-foundation/
├── secrets/
│   ├── redis_password.txt       # Redis auth (chmod 600)
│   └── api_key.txt             # API key (chmod 600)
├── docker-compose.yml
└── .env                        # Non-sensitive defaults
```

---

## Security Checklist

- [ ] All secret files have `600` permissions
- [ ] No secrets committed to git (check `.gitignore`)
- [ ] `.env` contains only non-sensitive defaults
- [ ] Production uses unique, generated secrets
- [ ] Secrets rotated per schedule

---

## Secret Rotation

| Secret | Rotation Period | Last Rotated |
|--------|----------------|--------------|
| Redis password | 90 days | [UPDATE] |
| API key | 90 days | [UPDATE] |
| JWT secret | 180 days | [UPDATE] |

### Rotation Procedure

```bash
# 1. Generate new secret
openssl rand -base64 32 > secrets/redis_password.txt.new

# 2. Update container
cp secrets/redis_password.txt.new secrets/redis_password.txt

# 3. Restart services
podman-compose restart redis

# 4. Verify
podman-compose logs redis | grep "Ready"

# 5. Remove old file
rm secrets/redis_password.txt.new
```

---

## Docker Secrets (Alternative)

For production, consider Docker secrets:

```yaml
# docker-compose.yml
services:
  redis:
    secrets:
      - redis_password

secrets:
  redis_password:
    file: ./secrets/redis_password.txt
```

---

## Environment Variable Alternative

If file-based secrets aren't feasible, use `_FILE` suffix pattern:

```bash
# Instead of: REDIS_PASSWORD=secret
# Use: REDIS_PASSWORD_FILE=/run/secrets/redis_password

# docker-compose.yml
services:
  redis:
    environment:
      - REDIS_PASSWORD_FILE=/run/secrets/redis_password
    secrets:
      - redis_password
```

---

## Related Documentation

- [Configuration Reference](03-reference/configuration.md)
- [Security Model](04-explanation/security.md)
