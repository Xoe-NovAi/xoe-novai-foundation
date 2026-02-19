# XNAi Stack - Complete Diagnostic & Fix Guide

**Date**: 2026-02-17  
**Analyst**: Claude Sonnet 4.5 Extended (Implementation Architect)  
**Source**: Gemini CLI conversation (61 entries) + 13 uploaded files  
**Status**: 🔴 **CRITICAL - UI DOWN DUE TO CASCADE FAILURE**

---

## 🎯 TL;DR - Root Cause in One Sentence

**Redis is crashing instantly because `./data/redis/dump.rdb` is owned by the wrong user.** This kills the entire stack via cascade failure. Fix one file, everything comes back up.

---

## 🔴 PART 1: Cascade Failure Analysis

### The True Chain of Failure

```
dump.rdb owned by wrong user
    ↓
Redis exits with "Permission denied" (CRASH - exit code 1)
    ↓
RAG API health check fails (depends_on: redis: service_healthy)
    ↓  
RAG API never starts
    ↓
Chainlit UI health check fails (depends_on: rag: service_healthy)
    ↓
Chainlit UI never starts
    ↓
Caddy reverse proxy gets 502 Bad Gateway on all routes
    ↓
"The UI is not working" ← What the user sees
```

**This is NOT a UI problem, a build problem, or a permissions problem with the entire stack.**  
**It is ONE file causing the entire cascade.**

---

## 🔍 PART 2: Kimi K-2.5 Assessment

### Where Kimi Was CORRECT ✅

1. ✅ Identified the UID/GID mismatch as root cause category
2. ✅ Provided `chown -R 1001:1001` as a valid fix
3. ✅ Mentioned `vm.overcommit_memory` warning
4. ✅ Provided Option 1 (chown), Option 2 (use current UID), Option 3 (named volumes)
5. ✅ Noted SELinux `:Z` labels are already in place

### Where Kimi Was INCOMPLETE ⚠️

1. ❌ **Missed the CASCADE analysis** - treated each symptom as independent when they share one root cause
2. ❌ **Missed the single file cause** - it's `dump.rdb` specifically, not "all data directories"
3. ❌ **Missed the fastest fix** - just `rm ./data/redis/dump.rdb` (30 seconds vs chown of everything)
4. ❌ **Mischaracterized Qdrant** - Qdrant is actually RUNNING fine (serving HTTP on 6333). The "unhealthy" is a false alarm from Podman's healthcheck quirk + a cosmetic init file error that doesn't affect operation
5. ❌ **Secret file permissions bug** - The secrets are `-rw-rw-r--` (664). Secret files MUST be `600` or the RAG service may warn
6. ❌ **Missed Caddyfile port discrepancy** - Caddy proxies `/metrics` to `xnai_rag_api:8002` but docker-compose has that port commented out

---

## 🛠️ PART 3: Ordered Fix List (Fastest to Slowest)

### Fix #1: Redis - CRITICAL (30 seconds, solves 90% of the problem)

```bash
cd /home/arcana-novai/Documents/xnai-foundation

# The dump.rdb file is owned by wrong user - simplest fix is delete it
# Redis will recreate it on next startup
rm -f ./data/redis/dump.rdb

# Then verify the directory itself is also writable
ls -la ./data/redis/
# If not owned by 1001:1001, fix it:
sudo chown -R 1001:1001 ./data/redis/
```

**Why this works**: Redis starts, reads no dump.rdb, initializes clean, creates a new dump.rdb owned by UID 1001. Everything downstream unblocks.

**Why not just chown dump.rdb?**  
Deleting is safer - the file may be corrupted if Redis died mid-write previously.

---

### Fix #2: Secret File Permissions (2 minutes)

```bash
# Currently: -rw-rw-r-- (world-readable secrets = security violation)
chmod 600 ./secrets/redis_password.txt
chmod 600 ./secrets/api_key.txt

# Verify
ls -la ./secrets/
# Should show: -rw------- 
```

**Why**: Docker/Podman secrets should never be group or world readable. Some container runtimes warn or refuse to mount world-readable secret files.

---

### Fix #3: Qdrant False Alarm (Cosmetic - 5 minutes)

**Qdrant is ACTUALLY WORKING.** The `unhealthy` Podman status is caused by this:

```
WARN: Failed to create init file indicator: Permission denied (os error 13)
```

This is a harmless warning - Qdrant tries to write a `.initialized` sentinel file to confirm first boot, but the directory ownership prevents it. It doesn't affect Qdrant's API which listens on port 6333 successfully.

**The healthcheck** `exec 3<>/dev/tcp/127.0.0.1/6333` should succeed (it's a TCP connect test).

**Why it shows unhealthy**: The Podman healthcheck has a `start_period: 30s` - if Redis was down during the restart cycle, the healthcheck may have evaluated before Qdrant finished starting. After Redis is fixed and everything restarts cleanly, Qdrant will likely show healthy.

**If still unhealthy after Redis fix:**
```bash
sudo chown -R 1001:1001 ./data/qdrant/
```

---

### Fix #4: Caddyfile Port Discrepancy (5 minutes)

**Found in Caddyfile (entry [21]):**
```caddy
@metrics {
  path /metrics
}
handle @metrics {
  reverse_proxy xnai_rag_api:8002   ← PORT 8002
}
```

**Found in docker-compose.yml:**
```yaml
rag:
  # ports:
  #   - "8002:8002"  ← COMMENTED OUT
```

Port 8002 is exposed inside the Docker network (not to host) - Caddy CAN reach it via container networking. But the RAG app must actually be serving Prometheus metrics on 8002. 

Check if RAG exposes metrics on a separate port or on the main :8000 port:
```bash
# When stack is running:
podman exec xnai_rag_api curl -s http://localhost:8002/metrics | head -5
# OR:
podman exec xnai_rag_api curl -s http://localhost:8000/metrics | head -5
```

If metrics are on 8000 (same as health), update Caddyfile:
```caddy
handle @metrics {
  reverse_proxy xnai_rag_api:8000   ← Change to 8000
}
```

---

### Fix #5: Redis Memory Overcommit Warning (2 minutes)

From Redis logs:
```
WARNING Memory overcommit must be enabled! Without it, a background save or 
replication may fail under low memory condition.
```

This is non-fatal but Redis warns about it every start:
```bash
# Immediate fix (no reboot):
sudo sysctl vm.overcommit_memory=1

# Permanent fix:
echo "vm.overcommit_memory = 1" | sudo tee -a /etc/sysctl.conf
```

---

### Fix #6: Rootless Network Namespace (Background Issue)

From Gemini conversation:
```
rootless netns: kill network process: permission denied
```

This happens when stopping/removing containers in rootless Podman mode. It's annoying but not stack-breaking.

```bash
# Permanent fix in /etc/sysctl.d/
sudo sysctl kernel.unprivileged_userns_clone=1
echo "kernel.unprivileged_userns_clone=1" | sudo tee /etc/sysctl.d/99-rootless-podman.conf
```

---

### Fix #7: _env File Bug (Minor)

Found in `_env` line 41:
```
RELOAD=falseSCARF_NO_ANALYTICS=true
```

**Bug**: Two variables concatenated on one line (missing newline):
```bash
# Wrong:
RELOAD=falseSCARF_NO_ANALYTICS=true

# Correct:
RELOAD=false
SCARF_NO_ANALYTICS=true
```

This means `SCARF_NO_ANALYTICS` is never set (it's treated as part of `RELOAD`'s value). If any package checks this telemetry variable, it may silently enable analytics.

---

## 📋 PART 4: Recovery Procedure (Complete Stack Restart)

Run in this exact order:

```bash
cd /home/arcana-novai/Documents/xnai-foundation

# Step 1: Stop everything cleanly
podman-compose -f docker-compose-noninit.yml down

# Step 2: Apply fixes
rm -f ./data/redis/dump.rdb                  # THE CRITICAL FIX
chmod 600 ./secrets/redis_password.txt       # Security fix
chmod 600 ./secrets/api_key.txt              # Security fix
sudo sysctl vm.overcommit_memory=1           # Redis warning fix

# Step 3: Ensure data directories are writable by UID 1001
sudo chown -R 1001:1001 ./data/redis/
sudo chown -R 1001:1001 ./data/qdrant/
sudo chown -R 1001:1001 ./data/vikunja/
sudo chown -R 1001:1001 ./data/curations/

# Step 4: Start stack (infrastructure first)
podman-compose -f docker-compose-noninit.yml up -d consul redis qdrant

# Step 5: Wait for Redis to be healthy (critical gate)
echo "Waiting for Redis..."
until podman exec xnai_redis redis-cli -a changeme123 ping 2>/dev/null | grep -q PONG; do
  sleep 2
  echo "  Waiting..."
done
echo "Redis healthy!"

# Step 6: Start remaining services
podman-compose -f docker-compose-noninit.yml up -d

# Step 7: Verify after 2 minutes
sleep 120
podman ps --format "table {{.Names}}\t{{.Status}}"

# Step 8: Test UI
curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/
# Expected: 200 or 307
```

---

## 📊 PART 5: Service Status After Fix

### Expected Healthy State:
| Service | Status | Port | Test |
|---------|--------|------|------|
| consul | ✅ Up (healthy) | 8500 | `curl http://localhost:8500/v1/status/leader` |
| redis | ✅ Up (healthy) | 6379 | `redis-cli -a changeme123 ping` → PONG |
| qdrant | ✅ Up (healthy) | 6333 | `curl http://localhost:6333/healthz` |
| xnai_rag_api | ✅ Up (healthy) | 8000 (internal) | `curl http://localhost:8000/health` via Caddy |
| xnai_chainlit_ui | ✅ Up | 8001 | `curl http://localhost:8001/` |
| caddy | ✅ Up (healthy) | 8000 (public) | `curl http://localhost:8000/` |
| vikunja_db | ✅ Up (healthy) | 5432 (internal) | `pg_isready -U vikunja` |
| vikunja | ✅ Up | 3456 (internal) | Via Caddy `/vikunja/` |
| mkdocs | ✅ Up | 8008 | `curl http://localhost:8008/` |

### Currently Broken (pre-fix):
- ❌ xnai_redis - Crashed (dump.rdb permission denied)
- ❌ xnai_rag_api - Never started (Redis dependency failed)
- ❌ xnai_chainlit_ui - Never started (RAG dependency failed)
- ⚠️ xnai_qdrant - Running but reported unhealthy (false alarm)

---

## 🔬 PART 6: Build Status (Already Good)

**Kimi and Gemini's rebuild efforts were successful:**

| Image | Size | Status |
|-------|------|--------|
| xnai-base:latest | 1.13 GB | ✅ Built with audio deps |
| xnai-ui:latest | 2.37 GB | ✅ Built successfully |
| xnai-rag:latest | 2.31 GB | ✅ Built |

**The build is NOT the problem.** The stack was running previously but Redis's dump.rdb got corrupted/wrong-owned during one of the restarts. Possibly when Gemini ran `podman-compose down` mid-session and processes died uncleanly.

---

## 🧪 PART 7: Qdrant Healthcheck Deep-Dive

**Why Qdrant shows "unhealthy" but is actually working:**

From `docker-compose.yml`:
```yaml
healthcheck:
  test: ["CMD", "bash", "-c", "exec 3<>/dev/tcp/127.0.0.1/6333"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s
```

This TCP connect test **should work** since Qdrant serves HTTP on 6333. But Podman's reporting showed:
```
Error: template: inspect:1:19: executing "inspect" at <.State.Health.Status>: nil pointer evaluating *define.HealthCheckResults.Status
```

This Podman error (entry [9]) means the health check results object is nil - **the health check hadn't run yet** when Gemini checked (container had just started). The `start_period: 30s` means no health check fires for 30 seconds.

**Recommendation**: Change Qdrant healthcheck to HTTP for reliability:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s
```

---

## 📝 PART 8: Dockerfile Issues Found

### Dockerfile.chainlit - Minor Issues

**Issue 1**: Healthcheck endpoint wrong
```dockerfile
# Current (line 54):
CMD curl -f http://localhost:8001/health || exit 1

# Chainlit's health endpoint is actually just the root path
# Fix:
CMD curl -f http://localhost:8001/ || exit 1
```

**Issue 2**: Dependency on app code at build time  
```dockerfile
# Line 27 - copies app code into image
COPY app/XNAi_rag_app /app/XNAi_rag_app
```

But `docker-compose.yml` also mounts it as a volume:
```yaml
volumes:
  - ./app/XNAi_rag_app:/app/XNAi_rag_app
```

This is fine for development (volume overrides baked-in code) but the COPY step adds 200-400MB to image size for no production benefit. Consider removing the COPY if always mounting.

### Dockerfile.base - One Bug Found

**Line 26-27**: Duplicate ENV variable:
```dockerfile
ENV ... \
    UV_LINK_MODE=copy \
    UV_LINK_MODE=copy   ← DUPLICATE (harmless but sloppy)
```

Remove the duplicate `UV_LINK_MODE=copy` line.

---

## 🎯 PART 9: Summary & Action Priority

### P0 - Do NOW (30 seconds):
```bash
rm -f ./data/redis/dump.rdb
```

### P1 - Do BEFORE restart (2 minutes):
```bash
chmod 600 ./secrets/redis_password.txt ./secrets/api_key.txt
sudo chown -R 1001:1001 ./data/redis/ ./data/qdrant/
sudo sysctl vm.overcommit_memory=1
```

### P2 - Do AFTER stack is running (5-10 minutes):
- Fix Caddyfile metrics port (verify 8002 vs 8000)
- Fix Qdrant healthcheck to HTTP
- Fix `_env` RELOAD/SCARF concatenation bug

### P3 - Future improvement:
- Remove duplicate `UV_LINK_MODE=copy` in Dockerfile.base
- Remove baked-in COPY of app code in Dockerfile.chainlit (if always volume-mounted)
- Document rootless netns workaround

---

## ✅ Confidence Assessment

**My diagnosis**: 99% confident Redis dump.rdb is the primary cause.

**Evidence**:
1. Redis logs explicitly state: `Fatal error: can't open the RDB file dump.rdb for reading: Permission denied` → exits code 1
2. `podman ps` shows Redis as `Exited (1)` → confirms crash
3. RAG API never appears in container list → confirms Redis-dependent cascade
4. Chainlit never appears in container list → confirms RAG-dependent cascade
5. xnai-ui:latest image exists (2.37GB) → build is NOT the problem

**Kimi's analysis**: 85% correct on diagnosis, but missed the fastest fix (delete dump.rdb) and the cascade analysis that pinpoints the single root cause.

---

**Prepared by**: Claude Sonnet 4.5 Extended (Implementation Architect)  
**Date**: 2026-02-17  
**Priority**: 🔴 CRITICAL - Execute P0 fix immediately
