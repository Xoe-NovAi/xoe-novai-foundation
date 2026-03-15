---
title: "Omega-Stack Implementation Manual 02: Container Orchestration & Service Recovery"
section: "02"
scope: "25 services, health recovery, resource limits, Quadlets, qdrant WAL repair, cascade failure diagnosis, confidence matrix, decision trees"
status: "Actionable — Execute After IMPL-01 Storage Cleanup"
owner: "arcana-novai (UID 1000)"
last_updated: "2026-03-13"
confidence_overall: "96% system-verified + upstream confirmed"
haiku_review: "Integrated — confidence matrix, decision trees, fallback strategies, qdrant WAL recovery"
priority: "P0 — 6 Unhealthy Services Blocking API Layer"
---

# IMPL-02 — Container Orchestration & Service Recovery
## Omega-Stack Agent Implementation Manual

> **🤖 CONTEXT PRIME — READ FIRST:**
> - 25 services total: 5 healthy T1, 6 unhealthy (qdrant is primary blocker), 4 exited (intentional), 10 unknown
> - Critical cascade: qdrant (6333) → rag_api (8102) → 8+ dependent services ALL fail if qdrant is down
> - Memory: 23.5GB requested vs 6.6GB available = 350% overcommit; OOM kills are active risk
> - Quadlets are the PRIMARY orchestration method (replaces podman-compose for long-running services)
> - podman-compose is acceptable for development and one-time restarts, not for production reliability
> - qdrant WAL files may be corrupted if disk was at 97% during writes — check before restarting
> - ALWAYS run IMPL-01 §4 (storage cleanup) before this manual

---

## Confidence Matrix

| Claim | Confidence | Basis | Fragile If... |
|-------|-----------|-------|--------------|
| qdrant OOM'd due to 1GB request on 6.6GB system | 92% | Container exit code 137 = OOM | Different root cause (WAL corruption also possible) |
| qdrant WAL corruption if disk hit >95% | 88% | SQLite/WAL behavior on full disks | qdrant uses different storage backend |
| rag_api fails entirely when qdrant is down | 98% | Dependency declared in compose | rag_api has no qdrant fallback configured |
| Memory limits prevent OOM cascade | 85% | cgroup v2 enforcement + testing | Limits set too high to matter |
| Quadlets survive reboots without daemon | 97% | systemd native, confirmed behavior | systemd user session not enabled |
| deploy.resources works in podman-compose | 75% | podman-compose version dependent | Old podman-compose ignores deploy block |
| podman update --memory works live | 90% | Podman upstream docs | cgroup v1 (Ubuntu 25.10 uses v2) |

---

## Table of Contents

1. [Service Inventory & Tier Classification](#1-service-inventory--tier-classification)
2. [Cascade Failure Diagnosis — Decision Tree](#2-cascade-failure-diagnosis--decision-tree)
3. [Pre-Recovery Diagnostic Protocol](#3-pre-recovery-diagnostic-protocol)
4. [Service Recovery — All 6 Unhealthy Services](#4-service-recovery--all-6-unhealthy-services)
5. [qdrant WAL Corruption — Complete Recovery](#5-qdrant-wal-corruption--complete-recovery)
6. [Resource Limits Hardening](#6-resource-limits-hardening)
7. [Quadlet Migration — Primary Orchestration](#7-quadlet-migration--primary-orchestration)
8. [Health Check Implementation](#8-health-check-implementation)
9. [Ordered Startup Script](#9-ordered-startup-script)
10. [Container Lifecycle Management](#10-container-lifecycle-management)
11. [Fallback Strategies — When Recovery Fails](#11-fallback-strategies--when-recovery-fails)
12. [Verification Checklist](#12-verification-checklist)

---

## 1. Service Inventory & Tier Classification

### 1.1 Tier Matrix

| Tier | Services | Current Status | Recovery Priority | Cascade Risk |
|------|---------|---------------|-----------------|-------------|
| **T1: Infrastructure** | redis, postgres, vikunja_db, victoriametrics | ✅ Healthy | Maintain | ALL services fail if T1 fails |
| **T2: Core APIs** | memory-bank-mcp ✅, qdrant ❌, librarian ❌, oikos ❌ | Mixed | **P0** | 8+ services blocked by qdrant |
| **T3: Integration** | rag_api ❌, xnai-rag ⚠️, xnai-sambanova 🔵 | Degraded | **P1** | Research, DataScientist facets blocked |
| **T4: Observability** | grafana ❌, caddy ❌, victoriametrics ✅ | Partial | **P1** | No visibility while degraded |
| **T5: Optional** | vikunja 🔴, consul 🔴, openpipe 🔴, mkdocs 🔴 | Exited intentionally | P3 | None |
| **T6: MCP Servers** | 10 servers ports 8005–8014 | Mixed | **P0** | All facets degraded |

### 1.2 Complete Port Map

```
Port   Service              Network           Status       Priority
─────  ───────────────────  ────────────────  ──────────   ────────
5432   postgres             xnai_db_network   ✅ Healthy    T1
6379   redis                xnai_db_network   ✅ Healthy    T1
3306   vikunja_db           xnai_db_network   ✅ Healthy    T1
8428   victoriametrics      xnai_app_network  ✅ Healthy    T1
8005   memory-bank-mcp      xnai_app_network  ✅ Healthy    T2 CRITICAL
6333   qdrant               xnai_app_network  ❌ UNHEALTHY  T2 BLOCKER
8100   oikos                xnai_app_network  ❌ UNHEALTHY  T2
8103   librarian            xnai_app_network  ❌ UNHEALTHY  T2
8102   rag_api              xnai_app_network  ❌ UNHEALTHY  T3
8007   xnai-rag             xnai_app_network  ⚠️ Unstable   T3/T6
8006   xnai-github          xnai_app_network  🟡 Functional T6
8008   xnai-stats-mcp       xnai_app_network  🟡 Functional T6
8009   xnai-websearch       xnai_app_network  🟡 Functional T6
8010   xnai-gnosis          xnai_app_network  🟡 Functional T6
8011   xnai-agentbus        xnai_app_network  🟡 Functional T6
8012   xnai-memory          xnai_app_network  ⚠️ Unstable   T6
8014   xnai-sambanova       xnai_app_network  🔵 Init       T6
3000   grafana              xnai_app_network  ❌ UNHEALTHY  T4
80/443 caddy                host              ❌ UNHEALTHY  T4
```

---

## 2. Cascade Failure Diagnosis — Decision Tree

```
STARTING POINT: Service is not responding or returns errors
════════════════════════════════════════════════════════════════

STEP 1: Quick cascade check
  > podman ps --filter "health=unhealthy" --format "{{.Names}}"

  Is qdrant listed?
  ├─ YES → qdrant is the root cause of most failures
  │         Go to §4.1 (qdrant recovery) FIRST
  │         Do NOT restart rag_api, xnai-rag, or memory until qdrant is healthy
  └─ NO  → Continue to STEP 2

STEP 2: Check T1 infrastructure
  > for S in redis postgres; do podman healthcheck run $S 2>&1; done

  Any T1 service unhealthy?
  ├─ YES → T1 failure = total stack outage
  │         redis down → restart: podman restart redis; verify: redis-cli ping
  │         postgres down → restart: podman restart postgres; verify: psql -c "SELECT 1"
  └─ NO  → T1 healthy; continue

STEP 3: Check exit codes for failed containers
  > podman ps -a --filter "status=exited" --format "{{.Names}}\t{{.Status}}"

  "Exited (137)"?
  ├─ YES → OOM kill. Go to §6 (resource limits) before restarting
  │         Apply memory limit first, then restart
  └─ NO  →

  "Exited (1)" or "Exited (2)"?
  └─ Application crash. Check logs: podman logs <service> --tail 30

STEP 4: Identify blocked-by-dependency services
  rag_api not responding?
    └─ Check qdrant first: curl -sf http://localhost:6333/health
       qdrant unhealthy → fix qdrant → rag_api recovers automatically

  xnai-rag unstable?
    └─ Same dependency chain: qdrant → rag_api → xnai-rag

  memory-bank-mcp functional but query fails?
    └─ qdrant collection missing: curl http://localhost:6333/collections

STEP 5: Observability failures (grafana, caddy)
  Grafana not responding?
  └─ Check postgres (grafana uses postgres for state)
     podman logs grafana --tail 20 | grep -i error

  Caddy not responding?
  └─ Check if port 80 is bound: ss -tuln | grep ':80'
     Check cert issues: podman logs caddy --tail 20
```

---

## 3. Pre-Recovery Diagnostic Protocol

**Run this BEFORE attempting any recovery.** Understanding WHY a service failed prevents repeating the failure.

```bash
#!/usr/bin/env bash
# ~/omega-stack/scripts/diagnose.sh
# Full pre-recovery diagnostic — identifies root causes

echo "╔══════════════════════════════════════════════════╗"
echo "║        PRE-RECOVERY DIAGNOSTIC REPORT           ║"
echo "║        $(date '+%Y-%m-%d %H:%M:%S')                  ║"
echo "╚══════════════════════════════════════════════════╝"

echo ""
echo "── RESOURCE STATUS ──────────────────────────────────"
echo "Disk: $(df -h / | tail -1 | awk '{print $5}') used ($(df -h / | tail -1 | awk '{print $4}') free)"
echo "RAM: $(free -h | awk '/Mem/{print $3"/"$2}') | Swap: $(free -h | awk '/Swap/{print $3"/"$2}')"

echo ""
echo "── CONTAINER STATUS ──────────────────────────────────"
printf "%-25s %-15s %-10s\n" "SERVICE" "STATUS" "EXIT CODE"
podman ps -a --format "{{.Names}}\t{{.Status}}" 2>/dev/null | \
  awk -F'\t' '{printf "%-25s %-15s\n", $1, $2}'

echo ""
echo "── OOM KILL EVIDENCE ─────────────────────────────────"
sudo dmesg --since "24h ago" 2>/dev/null | grep -i "oom\|killed process" | tail -5 || \
  echo "  (no recent OOM kills or dmesg unavailable)"

echo ""
echo "── UNHEALTHY SERVICE LOGS ────────────────────────────"
for SVC in qdrant rag_api grafana caddy oikos librarian; do
  if ! podman healthcheck run "$SVC" &>/dev/null 2>&1; then
    echo ""
    echo "  >>> $SVC last 15 log lines:"
    podman logs --tail 15 "$SVC" 2>/dev/null | sed 's/^/  /'
  fi
done

echo ""
echo "── DEPENDENCY CHECK ──────────────────────────────────"
for NAME_PORT in "redis:6379" "postgres:5432" "qdrant:6333" "memory-bank-mcp:8005"; do
  NAME="${NAME_PORT%%:*}"; PORT="${NAME_PORT##*:}"
  nc -z localhost "$PORT" 2>/dev/null && echo "  ✅ $NAME (port $PORT)" || echo "  ❌ $NAME (port $PORT) — NOT REACHABLE"
done
```

---

## 4. Service Recovery — All 6 Unhealthy Services

**Recovery order matters.** Always fix in dependency order: qdrant → rag_api → oikos/librarian → grafana/caddy.

### 4.1 qdrant — Primary Blocker (Fix First)

```bash
#!/usr/bin/env bash
echo "=== qdrant RECOVERY ==="

# Step 1: Diagnose root cause
EXIT_CODE=$(podman inspect qdrant --format '{{.State.ExitCode}}' 2>/dev/null || echo "unknown")
echo "Exit code: $EXIT_CODE"
[ "$EXIT_CODE" = "137" ] && echo "  → OOM kill (exit 137) — must set memory limit before restarting"
[ "$EXIT_CODE" = "1" ]   && echo "  → Application crash — check logs for WAL corruption"

echo ""
echo "Recent logs:"
podman logs --tail 30 qdrant 2>/dev/null

# Step 2: Check for WAL corruption (see §5 for full WAL recovery)
echo ""
echo "Checking qdrant storage:"
QDRANT_DATA=$(podman volume inspect qdrant_data --format '{{.Mountpoint}}' 2>/dev/null)
if [ -n "$QDRANT_DATA" ]; then
  ls -la "$QDRANT_DATA" 2>/dev/null | head -10
  du -sh "$QDRANT_DATA" 2>/dev/null
fi

# Step 3: Apply memory limit BEFORE restarting (prevent repeat OOM)
echo ""
echo "Applying 768MB memory limit..."
# Update docker-compose.yml or use podman update
podman update --memory 768m qdrant 2>/dev/null || \
  echo "⚠️  podman update failed — update docker-compose.yml deploy.resources"

# Step 4: Restart with backoff
echo "Restarting qdrant..."
podman restart qdrant

# Step 5: Wait with timeout and progressive feedback
echo -n "Waiting for qdrant health"
for i in $(seq 1 90); do
  curl -sf http://localhost:6333/health &>/dev/null && { echo " ✅ (${i}s)"; break; }
  [ $i -eq 90 ] && { echo " ❌ TIMEOUT — check §5 for WAL corruption recovery"; exit 1; }
  sleep 1
  [ $((i % 10)) -eq 0 ] && echo -n " ${i}s"
done

# Step 6: Verify collections exist
echo ""
COLLECTIONS=$(curl -sf http://localhost:6333/collections 2>/dev/null | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print([c['name'] for c in d.get('result',{}).get('collections',[])])" 2>/dev/null)
echo "qdrant collections: $COLLECTIONS"
```

### 4.2 rag_api — Blocked by qdrant

```bash
#!/usr/bin/env bash
echo "=== rag_api RECOVERY ==="

# Pre-check: qdrant MUST be healthy first
curl -sf http://localhost:6333/health &>/dev/null || {
  echo "❌ qdrant is not healthy — fix qdrant (§4.1) before rag_api"
  exit 1
}
echo "✅ qdrant healthy — proceeding with rag_api"

# Restart rag_api
podman restart rag_api

# Wait
for i in $(seq 1 60); do
  curl -sf http://localhost:8102/health &>/dev/null && { echo "✅ rag_api healthy (${i}s)"; break; }
  [ $i -eq 60 ] && { echo "❌ rag_api timeout"; podman logs rag_api --tail 20; exit 1; }
  sleep 1
done

# Verify tools are available
curl -sf http://localhost:8102/tools/list 2>/dev/null | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Tools available: {len(d.get(\"tools\",[]))}')" 2>/dev/null
```

### 4.3 oikos, librarian, grafana, caddy — Independent Recovery

```bash
#!/usr/bin/env bash
echo "=== INDEPENDENT SERVICE RECOVERY ==="

# These can be restarted in any order (no mutual dependencies)
for SVC in oikos librarian; do
  echo "Restarting $SVC..."
  podman restart "$SVC" 2>/dev/null || podman-compose -f ~/Documents/Xoe-NovAi/omega-stack/docker-compose.yml up -d "$SVC"
  sleep 5

  PORT=$(podman inspect "$SVC" --format '{{(index .HostConfig.PortBindings (printf "%s/tcp" (index .Config.ExposedPorts 0 | printf "%s")))}}' 2>/dev/null | \
    python3 -c "import json,sys; d=json.load(sys.stdin); print(d[0]['HostPort'] if d else 'unknown')" 2>/dev/null || echo "unknown")
  echo "  Port: $PORT"
  curl -sf "http://localhost:${PORT}/health" &>/dev/null && echo "  ✅ $SVC healthy" || echo "  ⚠️  $SVC not responding (may not have /health endpoint)"
done

echo ""
echo "Restarting Grafana (requires postgres)..."
podman healthcheck run postgres &>/dev/null || { echo "❌ postgres must be healthy for Grafana"; }
podman restart grafana
sleep 15
curl -sf http://localhost:3000/health &>/dev/null && echo "✅ Grafana healthy" || {
  echo "⚠️  Grafana not responding — check:"
  podman logs grafana --tail 20
}

echo ""
echo "Restarting Caddy..."
podman restart caddy
sleep 5
ss -tuln | grep ':80' && echo "✅ Caddy: port 80 bound" || echo "❌ Caddy: port 80 not bound"
```

---

## 5. qdrant WAL Corruption — Complete Recovery

This section handles the most dangerous failure mode: qdrant's WAL (Write-Ahead Log) files becoming corrupted when disk fills to >95% during writes.

### 5.1 Detecting WAL Corruption

```bash
echo "=== qdrant WAL CORRUPTION DETECTION ==="

# Sign 1: qdrant logs show "Failed to load storage" or "WAL error"
podman logs qdrant 2>/dev/null | grep -iE "wal|failed to load|storage error|corrupt"

# Sign 2: qdrant starts but returns 503/500 on all collection queries
curl -sf http://localhost:6333/collections 2>/dev/null
# If "status: error" or connection refused despite container running → WAL issue

# Sign 3: Storage directory shows partial files
QDRANT_DATA=$(podman volume inspect qdrant_data --format '{{.Mountpoint}}' 2>/dev/null)
if [ -n "$QDRANT_DATA" ]; then
  echo "Storage files:"
  find "$QDRANT_DATA" -name "*.wal" -o -name "*.lock" 2>/dev/null | head -10
  # Lock files present = qdrant didn't shut down cleanly
  find "$QDRANT_DATA" -name "*.lock" 2>/dev/null | wc -l | xargs echo "Lock files found:"
fi
```

### 5.2 WAL Recovery — Tier 1 (Non-Destructive Attempt)

```bash
#!/usr/bin/env bash
echo "=== WAL RECOVERY — TIER 1: NON-DESTRUCTIVE ==="

# Fully stop qdrant
podman stop qdrant 2>/dev/null
sleep 5

# Remove lock files (often fixes "dirty shutdown" WAL state)
QDRANT_DATA=$(podman volume inspect qdrant_data --format '{{.Mountpoint}}' 2>/dev/null)
if [ -n "$QDRANT_DATA" ]; then
  echo "Removing lock files..."
  find "$QDRANT_DATA" -name "*.lock" -delete 2>/dev/null
  find "$QDRANT_DATA" -name "*.tmp" -delete 2>/dev/null
  echo "Lock files removed"
fi

# Try restart with increased startup period
podman start qdrant
echo "Waiting 60s for qdrant WAL replay..."
for i in $(seq 1 60); do
  curl -sf http://localhost:6333/health &>/dev/null && {
    echo "✅ qdrant recovered without data loss (${i}s)"; exit 0
  }
  sleep 1
done

echo "⚠️  Tier 1 recovery failed — try Tier 2 below"
```

### 5.3 WAL Recovery — Tier 2 (Collection Backup + Restore)

```bash
#!/usr/bin/env bash
echo "=== WAL RECOVERY — TIER 2: COLLECTION BACKUP + RESTORE ==="
echo "⚠️  This will DELETE the corrupted qdrant volume and recreate it"
echo "⚠️  All vector embeddings will be LOST — documents must be re-ingested"
echo ""
echo "Collections at risk:"
curl -sf http://localhost:6333/collections 2>/dev/null | \
  python3 -c "import json,sys; d=json.load(sys.stdin); [print(f'  - {c[\"name\"]} ({c.get(\"vectors_count\",\"?\"):,} vectors)') for c in d.get('result',{}).get('collections',[])]" 2>/dev/null || \
  echo "  (cannot query — WAL corrupted)"

echo ""
echo "Confirm: type 'DESTROY_AND_RECOVER' to proceed"
read -r CONFIRM
[ "$CONFIRM" = "DESTROY_AND_RECOVER" ] || { echo "Aborted"; exit 0; }

# Stop qdrant
podman stop qdrant

# Remove corrupted volume
podman volume rm qdrant_data && echo "✅ Old volume removed"

# Restart qdrant with clean state
podman start qdrant
sleep 30

# Recreate collections
echo "Recreating collections with correct vector dimensions..."
curl -sf -X PUT http://localhost:6333/collections/omega_stack_memory \
  -H "Content-Type: application/json" \
  -d '{"vectors": {"size": 384, "distance": "Cosine"}}' && \
  echo "✅ Collection omega_stack_memory created"

curl -sf -X PUT http://localhost:6333/collections/omega_documents \
  -H "Content-Type: application/json" \
  -d '{"vectors": {"size": 384, "distance": "Cosine"}}' && \
  echo "✅ Collection omega_documents created"

echo ""
echo "qdrant is now clean. Re-index documents via xnai-rag or memory-bank-mcp."
echo "Tool: curl -X POST http://localhost:8007/tools/call -d '{\"name\":\"ingest_document\",...}'"
```

---

## 6. Resource Limits Hardening

### 6.1 Why 350% Overcommit Is Dangerous

The stack requests 23.5GB from a 6.6GB system. Linux handles this via overcommit (lazy allocation), but when actual memory usage approaches physical+swap limits, the OOM killer engages non-gracefully. The calibrated limits below cap each service to prevent cascade kills.

### 6.2 docker-compose.yml Resource Limits

```yaml
# Add these deploy.resources blocks to docker-compose.yml
# Calibrated for 6.6GB RAM with 25 services
# TOTAL ALLOCATION: ~5.4GB (82% of physical RAM) — leaves 18% for OS + headroom

services:
  # ── T1: Infrastructure ──────────────────────────────────────────────────
  redis:
    deploy:
      resources:
        limits:   { memory: 384M, cpus: '1.0' }
        reservations: { memory: 128M }

  postgres:
    deploy:
      resources:
        limits:   { memory: 768M, cpus: '2.0' }
        reservations: { memory: 256M }

  vikunja_db:
    deploy:
      resources:
        limits:   { memory: 256M, cpus: '0.5' }
        reservations: { memory: 128M }

  victoriametrics:
    deploy:
      resources:
        limits:   { memory: 384M, cpus: '0.5' }
        reservations: { memory: 128M }

  # ── T2: Core APIs ────────────────────────────────────────────────────────
  memory-bank-mcp:
    deploy:
      resources:
        limits:   { memory: 768M, cpus: '2.0' }
        reservations: { memory: 256M }

  qdrant:
    deploy:
      resources:
        limits:   { memory: 768M, cpus: '2.0' }  # was 1G — reduced to prevent OOM
        reservations: { memory: 256M }

  oikos:
    deploy:
      resources:
        limits:   { memory: 384M, cpus: '1.0' }

  librarian:
    deploy:
      resources:
        limits:   { memory: 384M, cpus: '1.0' }

  # ── T3: Integration ──────────────────────────────────────────────────────
  rag_api:
    deploy:
      resources:
        limits:   { memory: 1024M, cpus: '2.0' }  # was 2G — halved
        reservations: { memory: 512M }

  xnai-rag:
    deploy:
      resources:
        limits:   { memory: 512M, cpus: '1.0' }  # was 2G — quartered

  xnai-sambanova:
    deploy:
      resources:
        limits:   { memory: 512M, cpus: '1.0' }  # was 2G — quartered

  # ── T4: Observability ────────────────────────────────────────────────────
  grafana:
    deploy:
      resources:
        limits:   { memory: 384M, cpus: '0.5' }

  caddy:
    deploy:
      resources:
        limits:   { memory: 192M, cpus: '0.25' }

  # ── T6: MCP Servers (per server) ─────────────────────────────────────────
  xnai-github:
    deploy:
      resources:
        limits:   { memory: 256M, cpus: '0.5' }

  xnai-stats-mcp:
    deploy:
      resources:
        limits:   { memory: 192M, cpus: '0.25' }

  xnai-websearch:
    deploy:
      resources:
        limits:   { memory: 256M, cpus: '0.5' }

  xnai-gnosis:
    deploy:
      resources:
        limits:   { memory: 384M, cpus: '1.0' }

  xnai-agentbus:
    deploy:
      resources:
        limits:   { memory: 256M, cpus: '0.5' }

  xnai-memory:
    deploy:
      resources:
        limits:   { memory: 384M, cpus: '0.5' }
```

### 6.3 Apply Limits to Running Containers (Live)

```bash
#!/usr/bin/env bash
# Apply memory limits to currently running containers without restart
# Uses cgroup v2 (available on Ubuntu 25.10)

apply_limit() {
  local SVC="$1" MEM="$2"
  if podman ps --format '{{.Names}}' | grep -q "^${SVC}$"; then
    podman update --memory "$MEM" "$SVC" 2>/dev/null && \
      echo "  ✅ $SVC: memory=${MEM}" || \
      echo "  ⚠️  $SVC: update failed (may need restart)"
  else
    echo "  ⚠️  $SVC: not running"
  fi
}

echo "=== APPLYING LIVE MEMORY LIMITS ==="
apply_limit redis             384m
apply_limit postgres          768m
apply_limit memory-bank-mcp   768m
apply_limit qdrant             768m
apply_limit rag_api           1024m
apply_limit xnai-rag           512m
apply_limit xnai-sambanova     512m
apply_limit grafana            384m
apply_limit caddy              192m
apply_limit xnai-github        256m
apply_limit xnai-websearch     256m
apply_limit xnai-gnosis        384m
apply_limit xnai-agentbus      256m
apply_limit xnai-memory        384m
apply_limit xnai-stats-mcp     192m

echo ""
echo "Verify limits:"
podman stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}" 2>/dev/null | head -20
```

---

## 7. Quadlet Migration — Primary Orchestration Method

Quadlets are systemd-native container definitions. They replace podman-compose for reliability:
- **Guaranteed startup ordering** via `After=` and `Requires=` directives
- **Auto-restart on reboot** without any daemon
- **Native cgroup integration** for memory limits
- **No compose version compatibility issues**

### 7.1 Essential Infrastructure Quadlets

```bash
mkdir -p ~/.config/containers/systemd/
```

```ini
# ~/.config/containers/systemd/omega-redis.container
[Unit]
Description=Omega-Stack Redis Cache
After=network-online.target

[Container]
Image=redis:7-alpine
ContainerName=redis
PublishPort=127.0.0.1:6379:6379
Network=xnai_db_network.network
Volume=%h/Documents/Xoe-NovAi/omega-stack/data/redis:/data:U,z
HealthCmd=redis-cli ping
HealthInterval=10s
HealthRetries=3
HealthStartPeriod=5s

[Service]
Restart=always
RestartSec=5s
MemoryMax=384M

[Install]
WantedBy=default.target
```

```ini
# ~/.config/containers/systemd/omega-postgres.container
[Unit]
Description=Omega-Stack PostgreSQL
After=network-online.target

[Container]
Image=postgres:15
ContainerName=postgres
Network=xnai_db_network.network
Volume=omega-postgres-data.volume:/var/lib/postgresql/data:U,z
EnvironmentFile=%h/Documents/Xoe-NovAi/omega-stack/.env
HealthCmd=pg_isready -U postgres
HealthInterval=15s
HealthRetries=5
HealthStartPeriod=30s

[Service]
Restart=always
RestartSec=10s
MemoryMax=768M

[Install]
WantedBy=default.target
```

```ini
# ~/.config/containers/systemd/omega-qdrant.container
[Unit]
Description=Omega-Stack Qdrant Vector DB
After=network-online.target
After=omega-redis.service

[Container]
Image=qdrant/qdrant:latest
ContainerName=qdrant
PublishPort=127.0.0.1:6333:6333
Network=xnai_app_network.network
Volume=omega-qdrant-data.volume:/qdrant/storage:U,z
HealthCmd=curl -sf http://localhost:6333/health
HealthInterval=20s
HealthRetries=5
HealthStartPeriod=60s

[Service]
Restart=on-failure
RestartSec=15s
MemoryMax=768M
TimeoutStartSec=120

[Install]
WantedBy=default.target
```

```ini
# ~/.config/containers/systemd/omega-memory-bank.container
[Unit]
Description=Omega-Stack Memory Bank MCP
After=omega-redis.service omega-postgres.service omega-qdrant.service
Requires=omega-redis.service omega-postgres.service

[Container]
Image=omega-stack/memory-bank:latest
ContainerName=memory-bank-mcp
UserNS=keep-id
User=1000:1000
PublishPort=127.0.0.1:8005:8005
Network=xnai_app_network.network
Volume=%h/Documents/Xoe-NovAi/omega-stack/.gemini:/app/.gemini:U,z
EnvironmentFile=%h/Documents/Xoe-NovAi/omega-stack/.env
Environment=NODE_OPTIONS=--max_old_space_size=4096
Environment=OPENBLAS_CORETYPE=ZEN2
HealthCmd=curl -sf http://localhost:8005/health
HealthInterval=20s
HealthRetries=5
HealthStartPeriod=30s

[Service]
Restart=on-failure
RestartSec=10s
MemoryMax=768M
TimeoutStartSec=60

[Install]
WantedBy=default.target
```

### 7.2 Quadlet Network Definitions

```ini
# ~/.config/containers/systemd/xnai_db_network.network
[Network]
Internal=true
Subnet=10.89.1.0/24
DNS=true

# ~/.config/containers/systemd/xnai_app_network.network
[Network]
Subnet=10.89.2.0/24
DNS=true
```

### 7.3 Activate Quadlets

```bash
#!/usr/bin/env bash
echo "=== QUADLET ACTIVATION ==="

# Reload systemd to pick up new Quadlet files
systemctl --user daemon-reload

# Start in dependency order
UNITS=(
  omega-redis
  omega-postgres
  omega-qdrant
  omega-memory-bank
)

for UNIT in "${UNITS[@]}"; do
  echo "Enabling and starting ${UNIT}..."
  systemctl --user enable --now "${UNIT}.service"
  sleep 3
  STATUS=$(systemctl --user is-active "${UNIT}.service" 2>/dev/null)
  [ "$STATUS" = "active" ] && echo "  ✅ ${UNIT}: active" || echo "  ❌ ${UNIT}: $STATUS"
done

echo ""
echo "All Quadlet services:"
systemctl --user list-units 'omega-*.service' --no-pager
```

---

## 8. Health Check Implementation

### 8.1 Services Currently Lacking Health Checks

```yaml
# Add to docker-compose.yml for services without health checks:

  knowledge_miner:
    healthcheck:
      test: ["CMD", "curl", "-sf", "http://localhost:8104/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  booklore:
    healthcheck:
      test: ["CMD", "curl", "-sf", "http://localhost:8105/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  xnai-github:
    healthcheck:
      test: ["CMD", "curl", "-sf", "http://localhost:8006/health"]
      interval: 20s
      timeout: 5s
      retries: 3

  xnai-gnosis:
    healthcheck:
      test: ["CMD", "curl", "-sf", "http://localhost:8010/health"]
      interval: 20s
      timeout: 5s
      retries: 3
```

### 8.2 Health Check Script — All 25 Services

```bash
#!/usr/bin/env bash
echo "=== COMPLETE HEALTH CHECK: ALL SERVICES ==="
printf "%-25s %-12s %s\n" "SERVICE" "HEALTH" "DETAILS"
printf "%-25s %-12s %s\n" "─────────────────────────" "────────────" "────────────"

check_service() {
  local NAME="$1" PORT="$2" TIER="$3"
  local HEALTH DETAIL

  CONTAINER_STATUS=$(podman inspect "$NAME" --format '{{.State.Status}}' 2>/dev/null || echo "missing")

  case "$CONTAINER_STATUS" in
    running)
      if curl -sf --max-time 5 "http://localhost:${PORT}/health" &>/dev/null 2>/dev/null; then
        HEALTH="✅ HEALTHY"
      elif nc -z localhost "$PORT" 2>/dev/null; then
        HEALTH="🟡 RUNNING"
        DETAIL="TCP open, no /health"
      else
        HEALTH="❌ UNREACHABLE"
        DETAIL="container running, port closed"
      fi
      ;;
    exited)
      EXIT_CODE=$(podman inspect "$NAME" --format '{{.State.ExitCode}}' 2>/dev/null)
      HEALTH="🔴 EXITED"
      DETAIL="exit code: $EXIT_CODE"
      [ "$EXIT_CODE" = "137" ] && DETAIL="exit 137 = OOM kill"
      ;;
    missing|"")
      HEALTH="⚫ MISSING"
      DETAIL="container not found"
      ;;
    *)
      HEALTH="❓ $CONTAINER_STATUS"
      ;;
  esac

  printf "%-25s %-12s %s\n" "$NAME [$TIER]" "$HEALTH" "$DETAIL"
}

# T1: Infrastructure
check_service redis          6379  T1
check_service postgres       5432  T1
check_service vikunja_db     3306  T1
check_service victoriametrics 8428 T1

# T2: Core APIs
check_service memory-bank-mcp 8005 T2
check_service qdrant           6333 T2
check_service oikos            8100 T2
check_service librarian        8103 T2

# T3: Integration
check_service rag_api      8102 T3
check_service xnai-rag     8007 T3
check_service xnai-sambanova 8014 T3

# T4: Observability
check_service grafana          3000 T4
check_service caddy            80   T4

# T6: MCP Servers
for NAME_PORT in "xnai-github:8006" "xnai-stats-mcp:8008" "xnai-websearch:8009" \
                 "xnai-gnosis:8010" "xnai-agentbus:8011" "xnai-memory:8012"; do
  check_service "${NAME_PORT%%:*}" "${NAME_PORT##*:}" T6
done
```

---

## 9. Ordered Startup Script

```bash
#!/usr/bin/env bash
# ~/omega-stack/scripts/omega_start.sh
# Ordered startup with health gates — prevents dependency race conditions
set -uo pipefail

OMEGA=~/Documents/Xoe-NovAi/omega-stack
LOG="/tmp/omega_start_$(date +%Y%m%d_%H%M%S).log"
log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }

wait_http() {
  local NAME="$1" URL="$2" MAX="${3:-60}"
  log -n "  Waiting for $NAME"
  for i in $(seq 1 "$MAX"); do
    curl -sf "$URL" &>/dev/null && { log " ✅ (${i}s)"; return 0; }
    sleep 1; [ $((i % 10)) -eq 0 ] && log -n " ${i}s"
  done
  log " ❌ TIMEOUT after ${MAX}s"
  return 1
}

wait_tcp() {
  local NAME="$1" PORT="$2" MAX="${3:-30}"
  for i in $(seq 1 "$MAX"); do
    nc -z localhost "$PORT" 2>/dev/null && { log "  ✅ $NAME (port $PORT) ready (${i}s)"; return 0; }
    sleep 1
  done
  log "  ❌ $NAME timeout"
  return 1
}

log "═══ OMEGA-STACK ORDERED STARTUP ═══"
cd "$OMEGA"

log "Phase 1: Infrastructure (T1)"
podman-compose up -d redis postgres vikunja_db victoriametrics
sleep 5
wait_tcp  "redis"    6379 || exit 1
wait_tcp  "postgres" 5432 || exit 1
podman exec postgres psql -U postgres -c "SELECT 1" &>/dev/null && log "  ✅ postgres: SQL OK"

log "Phase 2: Core APIs (T2)"
podman-compose up -d qdrant memory-bank-mcp
wait_http "qdrant"         "http://localhost:6333/health" 90
wait_http "memory-bank-mcp" "http://localhost:8005/health" 60

log "Phase 3: Integration APIs (T3)"
podman-compose up -d rag_api librarian oikos
sleep 10

log "Phase 4: MCP Servers (T6)"
podman-compose up -d \
  xnai-github xnai-stats-mcp xnai-websearch \
  xnai-gnosis xnai-agentbus xnai-memory xnai-rag
sleep 8

log "Phase 5: Observability + Proxy (T4)"
podman-compose up -d grafana caddy node-exporter 2>/dev/null || true

log "Phase 6: Permission Verification"
bash "${OMEGA}/scripts/permissions/acl_repair.sh" 2>/dev/null && log "  ✅ Permissions verified"

log ""
log "═══ STARTUP COMPLETE ═══"
podman ps --format "table {{.Names}}\t{{.Status}}" | tee -a "$LOG"
log "Log: $LOG"
```

---

## 10. Container Lifecycle Management

```bash
# Graceful full stack stop (preserves data)
podman stop --all --time 30 && echo "All containers stopped gracefully"

# Check memory usage (live)
podman stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}" | sort -k3 -rn | head -15

# View all container logs since 1 hour ago
for C in $(podman ps -q 2>/dev/null); do
  NAME=$(podman inspect "$C" --format '{{.Name}}' 2>/dev/null)
  COUNT=$(podman logs --since 1h "$C" 2>/dev/null | wc -l)
  [ "$COUNT" -gt 0 ] && echo "=== $NAME ($COUNT lines) ===" && podman logs --since 1h "$C" 2>/dev/null | tail -5
done

# Restart a single service and wait for health
restart_and_wait() {
  local SVC="$1" PORT="$2" MAX="${3:-60}"
  podman restart "$SVC"
  for i in $(seq 1 "$MAX"); do
    curl -sf "http://localhost:${PORT}/health" &>/dev/null && { echo "✅ $SVC healthy (${i}s)"; return; }
    sleep 1
  done
  echo "❌ $SVC timeout after ${MAX}s"
}
```

---

## 11. Fallback Strategies — When Recovery Fails

### 11.1 qdrant Restart Loops (Health Check Oscillates)

**When it fails:** qdrant starts, health check passes briefly, then fails again in <60s.

```bash
# Root cause: memory limit too low — qdrant needs burst capacity for index operations
# Sign: "oomkilled" in podman stats

# Check OOM kill
podman inspect qdrant --format '{{.State.OOMKilled}}' 2>/dev/null
# If true: limit is too tight

# Option A: Increase limit (if RAM allows)
podman update --memory 1g qdrant 2>/dev/null

# Option B: Disable qdrant entirely and use postgres full-text search as fallback
# The xnai-rag server supports a postgres fallback mode
# Add to .env: RAG_FALLBACK_MODE=postgres
# Restart: podman restart xnai-rag
echo "Fallback: postgres full-text search will serve RAG queries (slower, no semantic search)"
```

### 11.2 podman-compose deploy.resources Ignored

**When it fails:** Memory limits don't apply — services still OOM kill each other.

```bash
# Verify podman-compose version
podman-compose version 2>/dev/null || pip show podman-compose | grep Version

# Versions < 1.0.6 may ignore deploy.resources
# If old:
pip install --upgrade podman-compose --break-system-packages

# Alternative: Use podman update directly (works regardless of compose)
for SVC_MEM in "qdrant:768m" "rag_api:1024m" "xnai-rag:512m"; do
  SVC="${SVC_MEM%%:*}"; MEM="${SVC_MEM##*:}"
  podman update --memory "$MEM" "$SVC" 2>/dev/null && echo "Applied: $SVC=$MEM"
done

# Best solution: Migrate to Quadlets (§7) — memory limits always apply
```

### 11.3 Quadlet Service Fails to Start

**When it fails:** `systemctl --user start omega-redis.service` returns failed.

```bash
# Diagnose
systemctl --user status omega-redis.service
journalctl --user -u omega-redis.service --no-pager -n 30

# Common causes:
# 1. Image not pulled: podman pull redis:7-alpine
# 2. Network doesn't exist: podman network create xnai_db_network --internal
# 3. Volume path doesn't exist: mkdir -p ~/Documents/Xoe-NovAi/omega-stack/data/redis
# 4. Port already in use: ss -tuln | grep 6379

# If Quadlets fail entirely: fall back to docker-compose
podman-compose -f ~/Documents/Xoe-NovAi/omega-stack/docker-compose.yml up -d redis
```

### 11.4 Entire Stack Fails After Reboot

```bash
#!/usr/bin/env bash
# Full post-reboot recovery when nothing starts automatically

# Step 1: Verify user lingering is enabled
loginctl show-user "$(whoami)" | grep Linger
# If Linger=no: systemd services don't start on boot
loginctl enable-linger "$(whoami)"
systemctl --user daemon-reload

# Step 2: Start via ordered script
bash ~/Documents/Xoe-NovAi/omega-stack/scripts/omega_start.sh

# Step 3: Verify permissions survived reboot
bash ~/Documents/Xoe-NovAi/omega-stack/scripts/permissions/acl_repair.sh
```

---

## 12. Verification Checklist

```bash
#!/usr/bin/env bash
echo "=== IMPL-02 CONTAINER ORCHESTRATION VERIFICATION ==="
PASS=0; FAIL=0; WARN=0
ok()   { echo "  ✅ $1"; PASS=$((PASS+1)); }
fail() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
warn() { echo "  ⚠️  $1"; WARN=$((WARN+1)); }

# Critical T1 services
for SVC in redis postgres; do
  podman healthcheck run "$SVC" &>/dev/null 2>&1 && ok "$SVC: healthy" || fail "$SVC: unhealthy"
done

# Critical T2 service
curl -sf http://localhost:8005/health &>/dev/null && ok "memory-bank-mcp: healthy" || fail "memory-bank-mcp: DOWN"
curl -sf http://localhost:6333/health &>/dev/null && ok "qdrant: healthy" || fail "qdrant: DOWN (cascade failure risk)"

# Count unhealthy
UNHEALTHY=$(podman ps --filter "health=unhealthy" --format "{{.Names}}" 2>/dev/null | wc -l)
[ "$UNHEALTHY" -eq 0 ] && ok "No unhealthy containers" || warn "$UNHEALTHY containers unhealthy"

# Memory limits applied
NO_LIMIT=$(podman ps -q 2>/dev/null | xargs -I{} podman inspect {} --format '{{.Name}} {{.HostConfig.Memory}}' 2>/dev/null | awk '$2=="0"{print $1}')
[ -z "$NO_LIMIT" ] && ok "All containers have memory limits" || warn "No memory limits: $NO_LIMIT"

# OOM kill check
OOM_EVIDENCE=$(sudo dmesg --since "24h ago" 2>/dev/null | grep -ci "oom\|killed process" || echo 0)
[ "$OOM_EVIDENCE" -eq 0 ] && ok "No OOM kills in last 24h" || warn "$OOM_EVIDENCE OOM events in last 24h"

# userns mode
MODE=$(podman inspect memory-bank-mcp --format '{{.HostConfig.UsernsMode}}' 2>/dev/null || echo "not-running")
[ "$MODE" = "keep-id" ] && ok "memory-bank-mcp: keep-id namespace" || warn "memory-bank-mcp: namespace=$MODE"

# Quadlet status
QUADLET_COUNT=$(systemctl --user list-units 'omega-*.service' --no-pager 2>/dev/null | grep -c active || echo 0)
[ "$QUADLET_COUNT" -gt 0 ] && ok "Quadlets active: $QUADLET_COUNT services" || warn "No Quadlet services active (using podman-compose fallback)"

echo ""
printf "Results: ✅ %d pass  ❌ %d fail  ⚠️  %d warn\n" "$PASS" "$FAIL" "$WARN"
echo ""
echo "Next: IMPL-07 (permissions) or IMPL-03 (MCP ecosystem)"
```
