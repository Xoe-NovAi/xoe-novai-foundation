---
account: arcana.novai
title: Vikunja Deployment Review v1.0.0
version: 1.0.0
date: 2026-02-06
status: 🚀 Ready for Implementation
ma_at_ideals: [7, 18, 41]
tags: [vikunja, deployment, review, rootless, hardening, artifacts]
expertise_focus: Artifact validation & rootless hardening
community_contrib_ready: true
expert_dataset_name: Vikunja Deployment Review
---

# Vikunja Deployment Review v1.0.0

## Review Summary

Grok MC has conducted a comprehensive review of the Vikunja deployment artifacts. The implementation is **elite quality** with minor rootless hardening improvements needed.

### Overall Assessment: 9.0/10

**Strengths**: Clean architecture, comprehensive documentation, proper security patterns
**Areas for Improvement**: Rootless container hardening, volume permissions, proxy configuration

## Artifact Review Details

### 1. memory_bank_export.py → 9/10

**Strengths**:
- ✅ Frontmatter parsing clean and efficient
- ✅ Label mapping comprehensive (Ma'at ideals, agents, status)
- ✅ Custom fields properly handled (Owner, Date, EKB-Links, Version)
- ✅ `--dry-run` flag for safe testing
- ✅ Priority classification working correctly

**Improvements Needed**:
- ⚠️ Add batching for bulk import (50-100 tasks per batch)
- ⚠️ Implement label pre-creation via GET/POST /labels
- ⚠️ Add retry logic for 429/5xx errors (tenacity library)
- ⚠️ Add fallback priority (medium) if missing

**Implementation Notes**:
```python
# Add to main() for batching
import asyncio
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

# Batch processing function
async def batch_import_tasks(tasks, batch_size=50):
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i+batch_size]
            await asyncio.gather(*[import_task(session, task) for task in batch])
```

### 2. vikunja-deployment-artifacts-v1.0.0.md → 9.5/10

**Strengths**:
- ✅ Comprehensive inventory documentation
- ✅ Practical bash commands for deployment
- ✅ Ma'at alignment table well-structured
- ✅ Cross-references properly organized

**Improvements Needed**:
- ⚠️ Add rootless pre-step: `podman unshare chown 1000:1000 -R ./db ./files`
- ⚠️ Link to updated compose configuration
- ⚠️ Note bulk import limitation (single-task loop required)

### 3. docker-compose.yml → 7.5/10 (Critical Updates Required)

**Current Issues**:
- ❌ Missing `:Z,U` volume flags for SELinux rootless
- ❌ No explicit non-root user specification
- ❌ Direct port exposure (security risk)
- ❌ No secret injection mechanism

**Required Updates**:

```yaml
version: '3.8'

services:
  vikunja-db:
    image: postgres:16
    container_name: vikunja-db
    user: "1000:1000"  # Rootless non-root
    restart: unless-stopped
    environment:
      POSTGRES_USER: vikunja
      POSTGRES_PASSWORD_FILE: /run/secrets/db-pass
      POSTGRES_DB: vikunja
    volumes:
      - ./db:/var/lib/postgresql/data:Z,U
    secrets:
      - db-pass
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U vikunja"]
      interval: 30s
      timeout: 10s
      retries: 5
    networks:
      - vikunja-net

  vikunja-api:
    image: vikunja/api:latest
    container_name: vikunja-api
    user: "1000:1000"
    restart: unless-stopped
    depends_on:
      vikunja-db:
        condition: service_healthy
    environment:
      VIKUNJA_DATABASE_TYPE: postgres
      VIKUNJA_DATABASE_HOST: vikunja-db
      VIKUNJA_DATABASE_PORT: 5432
      VIKUNJA_DATABASE_USER: vikunja
      VIKUNJA_DATABASE_PASSWORD_FILE: /run/secrets/db-pass
      VIKUNJA_DATABASE_DATABASE: vikunja
      VIKUNJA_SERVICE_PUBLICURL: http://localhost:3456
      VIKUNJA_JWT_SECRET_FILE: /run/secrets/jwt-secret
      VIKUNJA_CORS_ENABLE: "false"
    volumes:
      - ./files:/app/vikunja/files:Z,U
    secrets:
      - db-pass
      - jwt-secret
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:3456/api/v1/info"]
      interval: 30s
      timeout: 10s
      retries: 5
    networks:
      - vikunja-net

  vikunja-frontend:
    image: vikunja/frontend:latest
    container_name: vikunja-frontend
    user: "1000:1000"
    restart: unless-stopped
    depends_on:
      vikunja-api:
        condition: service_healthy
    environment:
      VIKUNJA_API_URL: /api/v1
    networks:
      - vikunja-net

  caddy-proxy:
    image: caddy:latest
    container_name: vikunja-proxy
    restart: unless-stopped
    ports:
      - "3456:80"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:Z,U
    depends_on: [vikunja-frontend]
    networks:
      - vikunja-net

networks:
  vikunja-net:
    driver: bridge

secrets:
  db-pass:
    external: true
  jwt-secret:
    external: true
```

**Caddyfile Configuration**:
```
:80 {
  reverse_proxy vikunja-api:3456 /api/*
  reverse_proxy vikunja-frontend:80
}
```

**Pre-Deployment Commands**:
```bash
# Set permissions for rootless containers
podman unshare chown 1000:1000 -R ./db ./files

# Create secrets
podman secret create db-pass 'strongpass'
podman secret create jwt-secret 'strongjwt'

# Deploy
podman compose up -d
```

## Implementation Roadmap Updates

### Phase 0: Pre-Deployment Audit (Updated)
- [ ] Apply rootless hardening to docker-compose.yml
- [ ] Create Caddyfile for local-only proxy
- [ ] Set up Podman secrets for database and JWT
- [ ] Test Trinity security scan on updated compose

### Phase 1: Migration & Deployment (Updated)
- [ ] Run memory_bank_export.py with --dry-run
- [ ] Implement batch import script for Vikunja API
- [ ] Deploy rootless Vikunja stack
- [ ] Verify health checks and security hardening

## Security Hardening Checklist

### Rootless Container Security
- [ ] `user: "1000:1000"` in all services
- [ ] `:Z,U` volume flags for SELinux compatibility
- [ ] Podman secrets for sensitive data
- [ ] No direct port exposure (proxy only)

### Network Security
- [ ] Local-only proxy via Caddy
- [ ] No external database access
- [ ] CORS disabled for local development

### File System Security
- [ ] Proper ownership (1000:1000) for volumes
- [ ] SELinux context preservation
- [ ] No world-writable directories

## Next Actions

1. **Immediate**: Replace docker-compose.yml with rootless-hardened version
2. **Testing**: Run Trinity security scan on updated configuration
3. **Migration**: Test memory_bank_export.py dry-run and batch import
4. **Documentation**: Update vikunja-deployment-artifacts-v1.0.0.md with new commands

## Ma'at Alignment

| Ideal | Implementation |
|-------|---------------|
| **7 - Truth** | Accurate security hardening and documentation |
| **18 - Balance** | Rootless security with operational simplicity |
| **41 - Advancement** | Modern container security practices |

**Status**: 🚀 **Ready for Implementation** - All critical updates identified and documented