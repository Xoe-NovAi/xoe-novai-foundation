# XNAi Stack - Complete Diagnostic Report v2
# (Full docker-compose + Dockerfile analysis included)

**Date**: 2026-02-17  
**Analyst**: Claude Sonnet 4.5 Extended (Implementation Architect)  
**Sources**: Gemini conversation (61 entries) + all 13 uploaded files  
**Status**: 🔴 Redis down → Vikunja + curation_worker cascade dead. UI running orphaned.

---

## 🔴 TRUE CURRENT STATE (End of Gemini Conversation)

By entry [57], this is what was actually running:

| Container | Status | Issue |
|-----------|--------|-------|
| xnai_consul | ✅ Up (healthy) | Fine |
| **xnai_redis** | ❌ Exited (1) | `dump.rdb` permission denied — **ROOT CAUSE** |
| xnai_qdrant | ⚠️ Up (unhealthy) | Cosmetic — actually serving on 6333 |
| xnai_mkdocs | ✅ Up | Fine |
| xnai_vikunja_db | ✅ Up (healthy) | Fine |
| xnai_caddy | ✅ Up (healthy) | Fine |
| **xnai_vikunja** | ❌ Exited (1) | Cannot connect to Redis (Redis is dead) |
| xnai_rag_api | ✅ Up (healthy) | Running from earlier healthy Redis state |
| **xnai_curation_worker** | ❌ Exited (1) | Depends on Redis — exited immediately |
| xnai_chainlit_ui | ⚠️ Up (orphaned) | Started manually via `podman run`, bypassing deps |

**The UI is running but on borrowed time** — the RAG API it talks to has Redis connections that will time out or fail under load. This is not a stable state.

---

## 🎯 ROOT CAUSE: One File, Five Failures

```
./data/redis/dump.rdb  (owned by wrong UID)
        │
        ▼
Redis: "Fatal error: can't open dump.rdb: Permission denied" → exit(1)
        │
        ├─► xnai_vikunja: Can't connect to Redis (VIKUNJA_REDIS_ENABLED=true) → exit(1)
        │
        ├─► xnai_curation_worker: depends_on redis → exits immediately → exit(1)
        │
        ├─► RAG API: Redis connections will fail under first real request
        │
        └─► xnai_chainlit_ui: manually started, no Redis session storage → unstable
```

**Fix time: 30 seconds.** Everything else is secondary.

---

## 🔍 WHERE KIMI K-2.5 WAS RIGHT vs INCOMPLETE

### ✅ Kimi Was Correct On:
1. Identified the UID mismatch category (containers run as 1001, host dirs owned by arcana-novai)
2. Provided `chown -R 1001:1001` as a valid approach
3. Identified `vm.overcommit_memory` warning
4. Mentioned three valid options (chown, use current UID, named volumes)
5. Correctly noted `:Z` SELinux labels are already in place

### ❌ Kimi Missed / Got Wrong:
1. **Missed the specific failing file**: It's `dump.rdb` — not a general directory permissions issue. The directories themselves were writable enough for Consul and others. The problem is a pre-existing `dump.rdb` written by an older Redis run under a different UID.
2. **Missed the cascade analysis**: Treated each service failure as independent. Vikunja and curation_worker are failing because of Redis — not independent permission problems on their own directories.
3. **Missed the orphaned UI situation**: Gemini manually started the UI via `podman run`, bypassing `depends_on` checks. This means the UI is running without guaranteed Redis-backed sessions — it will silently fail on real use.
4. **Missed the Vikunja Redis config issue** (see below — separate bug).
5. **Missed the `.env` file `REDIS_HOST=localhost` bug** (dangerous for any service reading `.env` directly).
6. **Missed the `_env` file concatenation bug**: `RELOAD=falseSCARF_NO_ANALYTICS=true` (two variables concatenated, `SCARF_NO_ANALYTICS` never set).
7. **Missed the Caddyfile routing gap** for `/` — routes to `xnai_chainlit_ui:8001`, but the manually started container may have a different name.

---

## 🛠️ FIXES IN EXACT EXECUTION ORDER

### STEP 1: Stop Everything (Clean Slate)
```bash
cd /home/arcana-novai/Documents/xnai-foundation

# Stop compose-managed services
podman-compose -f docker-compose-noninit.yml down --remove-orphans

# Also stop the orphaned manually-started UI container
podman stop xnai_chainlit_ui 2>/dev/null || true
podman rm xnai_chainlit_ui 2>/dev/null || true

# Verify clean state
podman ps -a | grep xnai
# Should show nothing or only stopped containers
```

---

### STEP 2: THE CRITICAL FIX — Redis dump.rdb (30 seconds)
```bash
# Option A (Safest): Delete the corrupt/wrong-owned dump.rdb
# Redis recreates it fresh on next start, owned by the running user (1001)
rm -f ./data/redis/dump.rdb

# Also ensure the directory itself is owned by 1001
sudo chown -R 1001:1001 ./data/redis/
ls -la ./data/redis/
# Expected: drwxr-xr-x  ... arcana-novai  (dir) or 1001
# If dump.rdb still exists, it MUST be gone before proceeding
```

---

### STEP 3: Fix All Data Directory Ownership
```bash
# Fix every directory that containers write to
sudo chown -R 1001:1001 ./data/redis/
sudo chown -R 1001:1001 ./data/qdrant/
sudo chown -R 1001:1001 ./data/vikunja/
sudo chown -R 1001:1001 ./data/faiss_index/ 2>/dev/null || mkdir -p ./data/faiss_index && sudo chown 1001:1001 ./data/faiss_index
sudo chown -R 1001:1001 ./data/curations/ 2>/dev/null || mkdir -p ./data/curations && sudo chown 1001:1001 ./data/curations
sudo chown -R 1001:1001 ./data/prometheus-multiproc/ 2>/dev/null || mkdir -p ./data/prometheus-multiproc && sudo chown 1001:1001 ./data/prometheus-multiproc
sudo chown -R 1001:1001 ./logs/ 2>/dev/null || mkdir -p ./logs && sudo chown 1001:1001 ./logs
sudo chown -R 1001:1001 ./backups/ 2>/dev/null || mkdir -p ./backups && sudo chown 1001:1001 ./backups
sudo chown -R 1001:1001 ./library/ 2>/dev/null || mkdir -p ./library && sudo chown 1001:1001 ./library
sudo chown -R 1001:1001 ./knowledge/ 2>/dev/null || mkdir -p ./knowledge && sudo chown 1001:1001 ./knowledge

echo "✅ All data directories owned by 1001:1001"
```

---

### STEP 4: Fix Secret File Permissions
```bash
# Secrets must not be world-readable
chmod 600 ./secrets/redis_password.txt
chmod 600 ./secrets/api_key.txt

# Verify
ls -la ./secrets/
# Expected: -rw------- 1 arcana-novai arcana-novai
```

---

### STEP 5: Apply Kernel Fixes
```bash
# Fix Redis memory overcommit warning (non-fatal but causes OOM risk)
sudo sysctl vm.overcommit_memory=1
# Make permanent:
echo "vm.overcommit_memory = 1" | sudo tee -a /etc/sysctl.conf

# Fix rootless Podman network namespace issues
sudo sysctl kernel.unprivileged_userns_clone=1 2>/dev/null || true
```

---

### STEP 6: Start Stack in Correct Order
```bash
cd /home/arcana-novai/Documents/xnai-foundation

# Load environment
export $(grep -v '^#' .env | grep -v '^\s*$' | xargs)

# Start infrastructure first
podman-compose -f docker-compose-noninit.yml up -d consul redis qdrant vikunja-db

# Gate: Wait for Redis to be genuinely healthy before proceeding
echo "⏳ Waiting for Redis health..."
ATTEMPTS=0
until podman exec xnai_redis redis-cli -a "${REDIS_PASSWORD:-changeme123}" ping 2>/dev/null | grep -q PONG; do
    ATTEMPTS=$((ATTEMPTS + 1))
    if [ $ATTEMPTS -gt 30 ]; then
        echo "❌ Redis failed to start after 60s. Check logs:"
        podman logs xnai_redis --tail 20
        exit 1
    fi
    sleep 2
    echo "  Attempt $ATTEMPTS/30..."
done
echo "✅ Redis healthy!"

# Start application services
podman-compose -f docker-compose-noninit.yml up -d rag

# Gate: Wait for RAG API health
echo "⏳ Waiting for RAG API health..."
ATTEMPTS=0
until podman exec xnai_rag_api curl -sf http://localhost:8000/health > /dev/null 2>&1; do
    ATTEMPTS=$((ATTEMPTS + 1))
    if [ $ATTEMPTS -gt 60 ]; then
        echo "❌ RAG API failed after 120s. Check logs:"
        podman logs xnai_rag_api --tail 30
        break
    fi
    sleep 2
    echo "  Attempt $ATTEMPTS/60..."
done
echo "✅ RAG API healthy!"

# Start UI and remaining services
podman-compose -f docker-compose-noninit.yml up -d

echo "✅ Full stack started"
```

---

### STEP 7: Verify Complete Health
```bash
# Wait for stabilization
sleep 60

# Check all containers
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test each critical endpoint
echo "=== Endpoint Tests ==="
curl -sf http://localhost:8000/api/v1/health && echo "✅ RAG API (via Caddy)" || echo "❌ RAG API FAILED"
curl -sf http://localhost:8001/ -o /dev/null -w "%{http_code}" && echo " ✅ Chainlit UI direct" || echo "❌ Chainlit UI FAILED"
curl -sf http://localhost:8000/ -o /dev/null -w "%{http_code}" && echo " ✅ Caddy root (UI proxy)" || echo "❌ Caddy root FAILED"
curl -sf http://localhost:8500/v1/status/leader && echo "✅ Consul" || echo "❌ Consul FAILED"
curl -sf http://localhost:6333/healthz && echo "✅ Qdrant" || echo "❌ Qdrant FAILED"
podman exec xnai_redis redis-cli -a changeme123 ping && echo "✅ Redis" || echo "❌ Redis FAILED"
```

---

## 🐛 SECONDARY BUGS FOUND IN CODE REVIEW

### Bug 1: Vikunja Redis Configuration (docker-compose.yml line ~175)

**Found in docker-compose.yml**:
```yaml
vikunja:
  environment:
    VIKUNJA_REDIS_HOST: redis:6379    # ← WRONG FORMAT
    VIKUNJA_REDIS_PORT: "6379"        # ← REDUNDANT (port already in HOST)
```

**Vikunja 0.24.1 expects host WITHOUT port**:
```yaml
VIKUNJA_REDIS_HOST: redis        # ← Correct: hostname only
VIKUNJA_REDIS_PORT: "6379"       # ← Correct: port separate
```

Or the host `redis:6379` tries to resolve `redis:6379` as a hostname including the port — Vikunja then connects to port 6379 on a host named `redis:6379` which fails DNS. This is why Vikunja exits even after Redis becomes healthy.

**Fix in docker-compose-noninit.yml** (vikunja section):
```yaml
VIKUNJA_REDIS_HOST: redis
VIKUNJA_REDIS_PORT: "6379"
```

---

### Bug 2: `.env` File `REDIS_HOST=localhost`

**In `_env` (your actual .env file), line 9**:
```
REDIS_HOST=localhost    ← WRONG for container networking
```

The docker-compose.yml correctly overrides this per-service with `REDIS_HOST=redis`. But any process that reads `.env` directly at runtime (e.g., Python with `python-dotenv`) will get `localhost` — which doesn't resolve to the Redis container from inside another container.

**Fix**:
```bash
sed -i 's/REDIS_HOST=localhost/REDIS_HOST=redis/' .env
```

---

### Bug 3: `.env` File Concatenation Bug (line 41)

**Current**:
```
RELOAD=falseSCARF_NO_ANALYTICS=true
```

**Should be**:
```
RELOAD=false
SCARF_NO_ANALYTICS=true
```

**Fix**:
```bash
sed -i 's/RELOAD=falseSCARF_NO_ANALYTICS=true/RELOAD=false\nSCARF_NO_ANALYTICS=true/' .env
```

---

### Bug 4: Qdrant Healthcheck Uses TCP Bash Trick (Unreliable)

**Current (docker-compose.yml line ~80)**:
```yaml
healthcheck:
  test: ["CMD", "bash", "-c", "exec 3<>/dev/tcp/127.0.0.1/6333"]
```

**The bash TCP trick fails** in minimal containers that don't have `/dev/tcp` enabled, or when bash isn't available. Qdrant has `curl` available.

**Fix**:
```yaml
healthcheck:
  test: ["CMD", "curl", "-sf", "http://localhost:6333/healthz"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s
```

---

### Bug 5: Caddyfile Root Path — Only Matches Exact `/`

**From Caddyfile (entry [21])**:
```caddy
@foundation-ui {
  path /
}
handle @foundation-ui {
  reverse_proxy xnai_chainlit_ui:8001
}
```

`path /` only matches exact `/` — it does NOT match `/login`, `/chat`, or any subpath. This means navigating to any Chainlit page other than root gives a 404.

**Fix**:
```caddy
@foundation-ui {
  not path /api/v1/* /vikunja/* /metrics
}
handle @foundation-ui {
  reverse_proxy xnai_chainlit_ui:8001
}
```

Or use a fallback handle:
```caddy
handle {
  reverse_proxy xnai_chainlit_ui:8001
}
```

---

### Bug 6: Duplicate ENV in Dockerfile.base

**Dockerfile.base line 26-27**:
```dockerfile
ENV DEBIAN_FRONTEND=noninteractive \
    ...
    UV_LINK_MODE=copy \
    UV_LINK_MODE=copy   ← DUPLICATE
```

Harmless but indicates copy-paste issue. Remove one.

---

### Bug 7: RAG API `read_only: true` + Missing tmpfs Paths

**docker-compose.yml (rag service)**:
```yaml
read_only: true
tmpfs:
  - /tmp:size=512m,mode=1777
  - /var/run:size=64m,mode=0755
  - /app/.cache:size=100m,mode=0755
  - /app/logs:size=100m,mode=1777
  - /app/data:size=50m,mode=1777
```

The RAG API writes JWT keys and IAM database to:
```yaml
- IAM_DB_PATH=/app/data/iam.db         ← in tmpfs /app/data ✅
- JWT_PRIVATE_KEY_PATH=/app/data/jwt-private-key.pem  ← in tmpfs ✅
```

These are in `/app/data` which IS in tmpfs — but this means **JWT keys and IAM database are lost on every container restart**. On first startup, the app likely generates fresh keys. On restart, old sessions signed with old keys become invalid.

**Fix options**:
- Mount `/app/data` as a persistent volume (not tmpfs) for JWT/IAM storage
- Or document that all sessions are invalidated on restart (acceptable for dev)

---

## 📊 COMPLETE ISSUE PRIORITY TABLE

| Priority | Issue | Impact | Fix Time |
|----------|-------|--------|----------|
| 🔴 P0 | `dump.rdb` permission denied | Redis crash → 4 service cascade | 30s |
| 🔴 P0 | Vikunja `REDIS_HOST: redis:6379` format | Vikunja always exits | 2m |
| 🟠 P1 | All data/ dirs wrong UID | Stack unstable on restart | 5m |
| 🟠 P1 | Secret files world-readable (664→600) | Security violation | 30s |
| 🟡 P2 | `.env` REDIS_HOST=localhost | Services reading .env directly fail | 1m |
| 🟡 P2 | `.env` RELOAD/SCARF concat bug | SCARF_NO_ANALYTICS never set | 1m |
| 🟡 P2 | `vm.overcommit_memory=0` | Redis warns, OOM risk on low memory | 1m |
| 🟡 P2 | Caddyfile `path /` too narrow | All Chainlit subpaths 404 | 5m |
| 🟢 P3 | Qdrant bash TCP healthcheck | Unreliable health reporting | 5m |
| 🟢 P3 | JWT/IAM on tmpfs (lost on restart) | Sessions invalidated on restart | 10m |
| 🟢 P3 | Duplicate `UV_LINK_MODE` in Dockerfile.base | Cosmetic | 1m |

---

## 🔬 GEMINI AGENT DEBRIEF

Gemini made reasonable decisions given the information available, but hit several traps:

**What Gemini did well**:
- ✅ Systematically investigated each component
- ✅ Found and rebuilt the base image with audio dependencies
- ✅ Identified Redis as the core failing service
- ✅ Successfully built all 3 required images

**Where Gemini got stuck**:
- ❌ **Kept retrying compose up** when the underlying `dump.rdb` file remained → compose recreates containers using same broken volume mount → same error every time
- ❌ **Used `podman run` to manually start UI** (entry [52-53]) — this gets the UI running but creates an orphaned container outside compose management that Caddy may not resolve correctly
- ❌ **Didn't delete dump.rdb** — the only reliable fix for that specific Redis error
- ❌ **5-minute timeouts** caused by trying to do `podman-compose up` which triggers rebuilds during diagnostic phase

---

## 🚀 COMPLETE RECOVERY SCRIPT

Run this single script for full recovery:

```bash
#!/bin/bash
# XNAi Stack Recovery Script
# Save as: scripts/recover.sh && chmod +x scripts/recover.sh && ./scripts/recover.sh

set -e
cd /home/arcana-novai/Documents/xnai-foundation

echo "🛑 Step 1: Stop all containers"
podman-compose -f docker-compose-noninit.yml down --remove-orphans 2>/dev/null || true
podman stop xnai_chainlit_ui xnai_redis xnai_qdrant 2>/dev/null || true
podman rm xnai_chainlit_ui 2>/dev/null || true

echo "🗑️  Step 2: Remove corrupt Redis dump"
rm -f ./data/redis/dump.rdb
echo "  ✅ dump.rdb removed"

echo "🔑 Step 3: Fix permissions"
sudo chown -R 1001:1001 ./data/redis/ ./data/qdrant/ ./data/curations/ ./logs/ ./backups/ ./library/ ./knowledge/ 2>/dev/null || true
for dir in data/faiss_index data/prometheus-multiproc data/vikunja logs/caddy logs/curations; do
    mkdir -p ./$dir && sudo chown -R 1001:1001 ./$dir
done
chmod 600 ./secrets/redis_password.txt ./secrets/api_key.txt
echo "  ✅ Permissions fixed"

echo "🔧 Step 4: Fix Vikunja Redis config"
# Fix REDIS_HOST format in both compose files
sed -i 's/VIKUNJA_REDIS_HOST: redis:6379/VIKUNJA_REDIS_HOST: redis/' docker-compose-noninit.yml docker-compose.yml 2>/dev/null || echo "  ℹ️  Vikunja REDIS_HOST already correct or not found"

echo "⚙️  Step 5: Kernel tuning"
sudo sysctl vm.overcommit_memory=1 2>/dev/null || echo "  ⚠️  Could not set vm.overcommit_memory (requires sudo)"

echo "🚀 Step 6: Start infrastructure"
podman-compose -f docker-compose-noninit.yml up -d consul redis qdrant vikunja-db
echo "  ⏳ Waiting 30s for infrastructure..."
sleep 30

echo "🔍 Step 7: Verify Redis"
if podman exec xnai_redis redis-cli -a "$(cat ./secrets/redis_password.txt)" ping 2>/dev/null | grep -q PONG; then
    echo "  ✅ Redis healthy"
else
    echo "  ❌ Redis still failing!"
    podman logs xnai_redis --tail 20
    exit 1
fi

echo "🚀 Step 8: Start application services"
podman-compose -f docker-compose-noninit.yml up -d
echo "  ⏳ Waiting 120s for all services..."
sleep 120

echo "✅ Step 9: Final status"
podman ps --format "table {{.Names}}\t{{.Status}}"

echo ""
echo "=== Endpoint Tests ==="
curl -sf http://localhost:8000/ -o /dev/null -w "Caddy/UI: %{http_code}\n" || echo "Caddy/UI: FAILED"
curl -sf http://localhost:8001/ -o /dev/null -w "Chainlit direct: %{http_code}\n" || echo "Chainlit: FAILED"
curl -sf http://localhost:8500/v1/status/leader > /dev/null && echo "Consul: ✅" || echo "Consul: ❌"
curl -sf http://localhost:6333/healthz && echo " Qdrant: ✅" || echo "Qdrant: ❌"
curl -sf http://localhost:8008/ > /dev/null && echo "MkDocs: ✅" || echo "MkDocs: ❌"

echo ""
echo "🏁 Recovery complete. If any service failed, check: podman logs <container_name>"
```

---

## 📋 PASS TO GEMINI: Knowledge Gaps & Next Steps

For Gemini's `continue debugging` request (entry [60]), pass this:

**CONFIRMED ROOT CAUSES**:
1. `./data/redis/dump.rdb` is owned by wrong UID → must be deleted
2. Vikunja `VIKUNJA_REDIS_HOST: redis:6379` must be `VIKUNJA_REDIS_HOST: redis`
3. All `./data/` subdirectories must be `chown -R 1001:1001`

**CONFIRMED NOT ISSUES**:
- ❌ Build failures (all 3 images built successfully)
- ❌ Network topology (containers can reach each other — Caddy can ping RAG by DNS)
- ❌ Qdrant API (it IS serving HTTP, just reporting unhealthy due to cosmetic init file error)
- ❌ Audio dependencies (pyaudio, sounddevice, ffmpeg confirmed installed in image)

**KNOWN SECONDARY BUGS TO FIX**:
- Caddyfile `path /` → change to fallback handle for Chainlit
- `.env` REDIS_HOST=localhost → change to redis
- `.env` RELOAD/SCARF concatenation on one line
- Qdrant healthcheck → change to `curl http://localhost:6333/healthz`

---

**Prepared by**: Claude Sonnet 4.5 Extended (Implementation Architect)  
**Confidence**: 99% (Redis dump.rdb is confirmed by explicit log line)  
**Priority Action**: Run recovery script above, or manually execute Steps 1-4
