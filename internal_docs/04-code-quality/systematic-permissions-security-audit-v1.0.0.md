# Xoe-NovAi Foundation: Systematic Permissions & Security Audit
## Version 1.0.0 | For Gemini CLI Implementation
## Date: 2026-02-10
## Classification: CRITICAL - Build Blocking Issues

---

## Executive Summary

This audit identifies **critical permission and filesystem issues** preventing successful container builds and deployments. These issues affect the Xoe-NovAi Foundation Stack's ability to build and run under Podman/Docker rootless configurations.

**Risk Level:** 🔴 HIGH - Build failures block all deployments
**Affected Systems:** All containerized services (rag, ui, crawler, curation_worker, mkdocs, caddy)
**Remediation Priority:** P0 - Must fix before any deployments

---

## 1. Permission Issues Audit

### 1.1 Container User ID Conflicts

**Issue:** Multiple directories are owned by container user UID/GID 100999 (mapped to "UNKNOWN" in host namespace)

**Affected Directories:**
```
drwxr-xr-x UNKNOWN UNKNOWN data/
drwxrwxr-x UNKNOWN UNKNOWN secrets/
drwxrwxr-x UNKNOWN UNKNOWN backups/
drwxrwxr-x UNKNOWN UNKNOWN library/
drwxrwxr-x UNKNOWN UNKNOWN knowledge/
```

**Root Cause:** 
- Podman containers run with user namespace remapping
- Files created inside containers get mapped UIDs (100999) that don't exist on host
- Docker build context cannot read these files → "can't stat" errors

**Evidence:**
```bash
# Build error:
error checking context: can't stat '/home/arcana-novai/Documents/xnai-foundation/db'
error checking context: no permission to read from '/home/arcana-novai/Documents/xnai-foundation/logs/caddy/access.log'
```

**Remediation Required:**
```bash
# Fix ALL directories with UNKNOWN ownership using podman unshare
podman unshare chown -R 0:0 \
    data/ \
    secrets/ \
    backups/ \
    library/ \
    knowledge/ \
    logs/ \
    db/

# Verify fix:
stat -c '%A %U %G %n' data/ secrets/ backups/ library/ knowledge/ logs/ db/
```

### 1.2 Volume Mount Permission Strategy

**Current Configuration:**
```yaml
# docker-compose.yml uses:
volumes:
  - ./library:/library:Z
  - ./knowledge:/knowledge:Z
```

**Issue:** The `:Z` flag (SELinux relabeling) conflicts with UNKNOWN ownership

**Recommended Fix:**
1. Fix ownership first (see 1.1)
2. Ensure host user matches container user (APP_UID=1001)
3. Consider using `:z` (shared) vs `:Z` (private) based on multi-container access needs

---

## 2. Symlink Issues Audit

### 2.1 Broken Symlink in Build Context

**Issue:** `docs/expert-knowledge` symlink is broken AND invalid for Docker builds

**Current State:**
```bash
lrwxrwxrwx docs/expert-knowledge -> ../../expert-knowledge
# ^ BROKEN: Should be ../expert-knowledge (one level up, not two)

file docs/expert-knowledge
# Result: broken symbolic link to ../../expert-knowledge
```

**Build Impact:**
```
Error response from daemon: invalid symlink "/var/tmp/libpod_builder.../build/docs/expert-knowledge" -> "../../expert-knowledge"
```

**Business Requirement:** User explicitly stated:
> "I do not want a symlink to expert-knowledge/ in docs/ or a copy of them there, only in the root expert-knowledge/ folder."

**Remediation Required:**
```bash
# REMOVE the broken symlink completely
rm docs/expert-knowledge

# Ensure expert-knowledge stays only at root:
ls -la expert-knowledge/  # Should exist
ls -la docs/expert-knowledge  # Should NOT exist

# Update .dockerignore (already correct):
# expert-knowledge/ is already excluded from build context
```

### 2.2 Symlink Audit Results

**All symlinks found:**
```bash
find . -type l
```

| Path | Target | Status | Action |
|------|--------|--------|--------|
| docs/expert-knowledge | ../../expert-knowledge | BROKEN | DELETE |

---

## 3. Docker Build Context Audit

### 3.1 .dockerignore Analysis

**Current .dockerignore:**
```
# Correctly excludes:
- data/
- backups/
- models/*
- embeddings/*
- library/
- knowledge/
- secrets/
- db/
- *.log
```

**Gap Identified:** 
- `docs/expert-knowledge` symlink is NOT excluded but causes build failures
- Even though target (`expert-knowledge/`) is excluded, the symlink itself causes issues

**Remediation Required:**
```bash
# Add to .dockerignore:
docs/expert-knowledge

# Or simply delete the symlink (preferred per user requirement)
```

### 3.2 Build Context Size Optimization

**Current Issues:**
- Build context includes all source code
- Legacy builder being used (BuildKit disabled)
- No `.dockerignore` optimization for build performance

**Recommendation for Gemini CLI:**
```dockerfile
# Enable BuildKit in environment:
export DOCKER_BUILDKIT=1
# OR remove: DOCKER_BUILDKIT=0

# Use BuildKit features in Dockerfile (already present but not utilized):
# syntax=docker/dockerfile:1
# RUN --mount=type=cache,...
```

---

## 4. Docker-Compose Security Audit

### 4.1 Service-by-Service Analysis

| Service | User | Security Issues | Risk Level |
|---------|------|-----------------|------------|
| redis | 1001:1001 | ✅ Proper user | Low |
| rag | 1001:1001 | ✅ no-new-privileges, cap_drop ALL | Low |
| ui | 1001:1001 | ✅ No issues | Low |
| crawler | 1001:1001 | ✅ No issues | Low |
| curation_worker | 1001:1001 | ⚠️ restart: on-failure only | Medium |
| mkdocs | 1001:1001 | ✅ No issues | Low |
| caddy | 1001:1001 | ✅ Proper user | Low |

### 4.2 Volume Mount Security

**Privileged Paths Mounted:**
```yaml
# All services use :Z flag (SELinux private unshared)
# Risk: Changes host file labels, potential conflicts

# Recommendation for shared volumes:
- ./library:/library:z  # Shared (lowercase z) if multiple containers access
- ./knowledge:/knowledge:z
```

### 4.3 Secrets Management

**Current Implementation:**
```yaml
secrets:
  redis_password:
    file: ./secrets/redis_password.txt
  api_key:
    file: ./secrets/api_key.txt
```

**Issue:** 
- `secrets/` directory has UNKNOWN ownership
- Secrets may not be readable during build

**Remediation:**
```bash
# Ensure secrets directory ownership:
podman unshare chown -R 0:0 secrets/

# Verify secrets files exist and are readable:
ls -la secrets/
```

---

## 5. Dockerfile Security Audit

### 5.1 Dockerfile (RAG Service)

**Security Strengths:**
- ✅ Uses non-root user (`appuser`)
- ✅ No secrets in image layers
- ✅ BuildKit cache mounts for performance
- ✅ Health checks configured

**Issues Found:**
- ❌ No `USER` instruction before COPY (but fixed later)
- ⚠️ BuildKit syntax present but may not be enabled

### 5.2 Multi-Service Dockerfile Consistency

**Dockerfiles in Project:**
- `Dockerfile` (RAG service) - Uses `xnai-base:latest`
- `Dockerfile.chainlit` (UI)
- `Dockerfile.crawl` (Crawler)
- `Dockerfile.curation_worker`
- `Dockerfile.docs` (MkDocs)
- `Dockerfile.awq` (AWQ quantizer)
- `Dockerfile.base` (Base image)

**Recommendation:** Audit each for consistent security practices

---

## 6. Environment Variable Security

### 6.1 Exposed in docker-compose.yml

**Non-Secret Environment Variables (Acceptable):**
```yaml
OPENBLAS_CORETYPE=ZEN
LLAMA_CPP_N_THREADS=6
CHAINLIT_NO_TELEMETRY=true
DEBUG_MODE=true
```

**Potential Issues:**
```yaml
DEBUG_MODE=true  # Should be false in production
```

### 6.2 Secrets Properly Externalized

**Correct Implementation:**
```yaml
secrets:
  - redis_password
  - api_key

environment:
  REDIS_PASSWORD_FILE: /run/secrets/redis_password  # ✅ Correct: file path, not value
```

---

## 7. Network Security Audit

### 7.1 Network Configuration

```yaml
networks:
  xnai_network:
    driver: bridge
    name: xnai_network
```

**Issues:**
- ⚠️ No network isolation between services
- ⚠️ No encryption (not required for local)
- ⚠️ No explicit IP range defined

**Recommendation:**
```yaml
networks:
  xnai_network:
    driver: bridge
    internal: false  # Explicit
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### 7.2 Port Exposure

| Service | External Port | Internal Port | Risk |
|---------|--------------|---------------|------|
| redis | None | 6379 | ✅ No external exposure |
| rag | 8002 | 8000 | ⚠️ Exposes API directly |
| ui | 8001 | 8001 | ✅ User interface |
| mkdocs | 8008 | 8000 | ⚠️ Docs exposed |
| caddy | 8000 | 8000 | ✅ Reverse proxy |

**Issue:** RAG API (8002) exposed directly instead of through Caddy only

---

## 8. Resource Limits Audit

### 8.1 Current Resource Configuration

| Service | Memory Limit | CPU Limit | Notes |
|---------|-------------|-----------|-------|
| rag | 4G | 2.0 | With reservations |
| ui | 2G | 1.0 | |
| crawler | None | None | ⚠️ Unbounded |
| curation_worker | None | None | ⚠️ Unbounded |
| mkdocs | None | None | ⚠️ Unbounded |
| caddy | None | None | ⚠️ Unbounded |

**Warning:** Podman warns: `deploy sub-keys are not supported and have been ignored: resources.reservations.cpus`

---

## 9. Remediation Checklist for Gemini CLI

### 9.1 P0 - Critical (Build Blocking)

- [ ] **Fix 1.1:** Run `podman unshare chown -R 0:0` on ALL directories with UNKNOWN ownership:
  ```bash
  podman unshare chown -R 0:0 data/ secrets/ backups/ library/ knowledge/ logs/ db/
  ```

- [ ] **Fix 2.1:** Delete broken symlink:
  ```bash
  rm docs/expert-knowledge
  ```

- [ ] **Fix 3.1:** Add symlink exclusion to .dockerignore (or verify deletion):
  ```
  docs/expert-knowledge
  ```

- [ ] **Fix 5.1:** Verify secrets directory is readable:
  ```bash
  ls -la secrets/
  # Should show: -rw-r--r-- arcana-novai arcana-novai redis_password.txt
  ```

### 9.2 P1 - Security Hardening

- [ ] **Network Isolation:** Add explicit subnet to xnai_network
- [ ] **Resource Limits:** Add memory/cpu limits to crawler, curation_worker, mkdocs, caddy
- [ ] **Port Review:** Consider removing direct RAG API exposure (8002), route through Caddy only
- [ ] **SELinux Labels:** Review :Z vs :z usage for shared volumes

### 9.3 P2 - Build Optimization

- [ ] Enable BuildKit: `export DOCKER_BUILDKIT=1` or remove `DOCKER_BUILDKIT=0`
- [ ] Optimize .dockerignore for faster builds
- [ ] Consider multi-stage builds for smaller images

---

## 10. Validation Commands

After Gemini CLI implements fixes, validate with:

```bash
# 1. Verify permissions fixed:
find . -maxdepth 1 -type d -exec stat -c '%A %U %G %n' {} \; | grep -v "arcana-novai"
# Should return nothing (no UNKNOWN users)

# 2. Verify no broken symlinks:
find . -type l -xtype l
# Should return nothing

# 3. Test build:
podman compose up -d --build

# 4. Verify services health:
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 5. Check logs:
podman logs xnai_rag_api
podman logs xnai_redis
```

---

## 11. Appendices

### Appendix A: File Inventory for Audit

**Key Files Audited:**
- `docker-compose.yml` - Main orchestration
- `Dockerfile` - RAG service build
- `.dockerignore` - Build context exclusions
- `Caddyfile` - Reverse proxy config
- `config.toml` - Application configuration

### Appendix B: User Requirements Documented

**Explicit User Requirements:**
1. NO symlink to expert-knowledge/ in docs/ folder
2. expert-knowledge/ should ONLY exist at root
3. Gemini CLI should implement all fixes systematically

### Appendix C: Error Log Archive

**Build Errors Collected:**
```
1. error checking context: can't stat '/home/.../xnai-foundation/db'
2. error checking context: no permission to read from '/home/.../logs/caddy/access.log'
3. Error response from daemon: invalid symlink "/var/tmp/.../build/docs/expert-knowledge" -> "../../expert-knowledge"
4. Can't add file ...docs/index.json to tar: io: read/write on closed pipe
```

---

## Document Metadata

| Field | Value |
|-------|-------|
| Version | 1.0.0 |
| Date | 2026-02-10 |
| Author | Cline (Audit Mode) |
| Target | Gemini CLI Implementation |
| Status | COMPLETE - Ready for Implementation |
| Classification | CRITICAL |

---

**END OF AUDIT DOCUMENT**

*This document provides complete systematic guidance for Gemini CLI to remediate all identified permission, security, and build issues in the Xoe-NovAi Foundation Stack.*
