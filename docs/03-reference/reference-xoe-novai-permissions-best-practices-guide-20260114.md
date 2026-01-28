# 🚀 Xoe-NovAi Permissions Best Practices Guide
## Enterprise-Grade Directory & Container Permissions (Ryzen Local Deployment)

**Guide Version**: 1.0 Permissions Edition  
**Date**: January 27, 2026  
**Status**: 🟢 Production-Ready  
**Purpose**: Resolve common permission issues in Xoe-NovAi Foundation stack (non-root containers, mounted volumes, Redis system user). This guide enforces **principle of least privilege**, zero-trust patterns, and Ryzen-safe ownership (UID/GID matching host user).

**Critical Constraints Honored**:
- Non-root execution (appuser:1001 for most services, 999 for Redis)
- Writeable logs/tmp (777 where needed)
- Read-only config.toml
- No privilege escalation
- Local-only data sovereignty

---

## 🎯 Why Permissions Matter in Xoe-NovAi

Common issues observed:
- Containers can't write to /library, /knowledge, /faiss_index (PermissionError)
- Logs not generated (logs/ directory inaccessible)
- Redis persistence fails (data/redis ownership mismatch)
- FAISS backups fail (backups/ directory)

Root cause: Podman runs as non-root (security best practice), but host directories often owned by root or different UID.

**Best Practice Principles**:
1. **Match Host UID/GID** → Avoid permission mismatches
2. **Least Privilege** → USER non-root in Podmanfiles
3. **Explicit Ownership** → chown before build/start
4. **Immutable Where Possible** → ro mounts for config/docs

---

## 📋 Step-by-Step Permissions Setup (Run Once)

### 1. Configure .env (Critical - 2 min)
```bash
# Edit .env
nano .env

# SET THESE TO YOUR HOST USER (prevents all permission issues)
APP_UID=$(id -u)      # e.g., 1000 or 1001
APP_GID=$(id -g)      # e.g., 1000 or 1001

# Redis uses system user 999 - no change needed
REDIS_PASSWORD=strong_password_here
```

**Why**: Containers run as APP_UID:APP_GID. Matching host prevents "Permission denied" on volume mounts.

### 2. Create & Own Directories (Host Level - 3 min)
```bash
# Create all required directories
sudo mkdir -p library knowledge data/faiss_index data/cache backups logs app/XNAi_rag_app/logs data/redis

# Ownership: appuser (matches container)
sudo chown -R ${APP_UID}:${APP_GID} library knowledge data/faiss_index data/cache backups logs app/XNAi_rag_app/logs

# Redis: system redis user (999)
sudo chown -R 999:999 data/redis

# Permissions: readable/executable, logs writeable
sudo chmod -R 755 library knowledge data/faiss_index data/cache backups
sudo chmod -R 777 app/XNAi_rag_app/logs  # Container needs write
sudo chmod -R 755 data/redis
```

**Directory Permissions Table**:
| Directory         | Owner:Group     | Permissions | Purpose              | Notes                   |
| ----------------- | --------------- | ----------- | -------------------- | ----------------------- |
| library/          | APP_UID:APP_GID | 755         | Document storage     | Read/write by container |
| knowledge/        | APP_UID:APP_GID | 755         | Curated knowledge    | Crawler writes here     |
| data/faiss_index/ | APP_UID:APP_GID | 755         | Vectorstore index    | FAISS read/write        |
| data/cache/       | APP_UID:APP_GID | 755         | Redis/Chainlit cache | Ephemeral               |
| backups/          | APP_UID:APP_GID | 755         | FAISS backups        | Auto-managed (max 5)    |
| logs/             | APP_UID:APP_GID | 777         | JSON structured logs | All services write      |
| data/redis/       | 999:999         | 755         | Redis persistence    | System redis user       |

### 3. Podmanfile USER & Permissions (Verify - No Changes Needed)
All Podmanfiles (api, chainlit, crawl, curation_worker) already:
```dockerfile
# Create appuser if not exists
RUN addgroup --gid 1001 appuser && \
    adduser --uid 1001 --gid 1001 --disabled-password --gecos "" appuser

# Switch to non-root
USER appuser
```

**Best Practice**: Never use USER root in production images.

### 4. docker-compose.yml Volume Mounts (Verify ro Where Possible)
From stack:
- config.toml:ro → Immutable
- docs/:ro → Documentation
- Writeable volumes use host-owned dirs from Step 2

**Security Enhancement** (Optional PR):
Add `:ro` to read-only mounts explicitly.

---

## 🛠️ Troubleshooting Permissions Issues

**Debugging Protocol** (Run in Order):

1. **Check Container User**:
   ```bash
   podman exec xnai_rag_api id
   # Expected: uid=1001(appuser) gid=1001(appuser)
   ```

2. **Inspect Host Directory Ownership**:
   ```bash
   ls -ld library/ knowledge/ logs/
   # Expected: owned by your APP_UID:APP_GID
   ```

3. **Inspect Inside Container**:
   ```bash
   podman exec xnai_rag_api ls -la /library
   # Should show writeable files
   ```

4. **Temporary Debug (Root User - ONLY FOR TESTING)**:
   In docker-compose.yml service:
   ```yaml
   user: "0:0"  # root - REMOVE AFTER DEBUG
   ```
   Rebuild: `podman compose up --build -d`

5. **Common Errors & Fixes**:
   | Error Message               | Cause                      | Fix                                    |
   | --------------------------- | -------------------------- | -------------------------------------- |
   | PermissionError: [Errno 13] | UID mismatch               | Re-run Step 2 with correct APP_UID/GID |
   | Can't write to /logs        | logs/ not 777              | chmod 777 app/XNAi_rag_app/logs        |
   | Redis persistence failed    | data/redis wrong owner     | chown 999:999 data/redis               |
   | FAISS can't save index      | faiss_index/ not writeable | chown APP_UID:APP_GID data/faiss_index |

---

## 🔐 Security Best Practices

- **Never Run as Root**: Enforced in all Podmanfiles
- **Zero-Trust**: No exposed ports except 8000/8001; rate limiting (slowapi)
- **Audit Logging**: All file operations logged (JSON structured)
- **Production Hardening**:
  ```bash
  # Add to docker-compose.yml (all services)
  read_only: true
  tmpfs:
    - /tmp:noexec,nosuid,size=100m
  ```
- **SELinux/AppArmor**: If enabled, allow container access to volumes

---

## ✅ Verification Checklist

- [ ] .env has correct APP_UID/GID
- [ ] All directories created and owned (Step 2)
- [ ] `podman compose up -d` succeeds with no permission errors
- [ ] `podman logs xnai_rag_api` shows startup without PermissionError
- [ ] Write test: `podman exec xnai_rag_api touch /library/test.txt`
- [ ] Health checks pass: `make health`
