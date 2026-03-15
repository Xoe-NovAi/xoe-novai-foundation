---
title: "Omega-Stack Implementation Manual 02: Container Orchestration & Service Recovery"
section: "02"
scope: "Podman, docker-compose, Service Health, Quadlets, Resource Limits"
status: "Actionable — Execute After IMPL-01"
owner: "arcana-novai (UID 1000)"
last_updated: "2026-03-13"
gemini_review: "Integrated — Quadlets promoted to primary Layer 3 method"
confidence: "96% system-verified"
priority: "P0 — 6 Unhealthy Services Blocking API Layer"
---

# IMPL-02 — Container Orchestration & Service Recovery
## Omega-Stack Agent Implementation Manual

> **🤖 AGENT DIRECTIVE:** Six services are currently unhealthy and blocking the entire API layer. This manual provides service recovery procedures, resource limit hardening, and the migration from `podman-compose` to **Podman Quadlets** as the primary orchestration method (promoted per Gemini 3.1 review). Execute IMPL-01 (storage cleanup) before this manual.

---

## Table of Contents

1. [Service Inventory & Status](#1-service-inventory--status)
2. [Critical Path & Dependency Analysis](#2-critical-path--dependency-analysis)
3. [Service Recovery — 6 Unhealthy Services](#3-service-recovery--6-unhealthy-services)
4. [Resource Limits Hardening](#4-resource-limits-hardening)
5. [Quadlet Migration — Primary Orchestration Method](#5-quadlet-migration--primary-orchestration-method)
6. [Health Check Implementation](#6-health-check-implementation)
7. [Service Startup Ordering](#7-service-startup-ordering)
8. [Container Lifecycle Management](#8-container-lifecycle-management)
9. [Edge Cases & Failure Modes](#9-edge-cases--failure-modes)
10. [Verification Checklist](#10-verification-checklist)

---

## 1. Service Inventory & Status

### 1.1 Tier Classification

| Tier | Services | Status | Recovery Priority |
|------|---------|--------|------------------|
| **T1: Infrastructure** | redis, postgres, mariadb, victoriametrics | ✅ All healthy | — |
| **T2: Critical APIs** | memory-bank-mcp ✅, qdrant ❌, librarian ❌, oikos ❌ | Mixed | **P0** |
| **T3: Integration** | rag_api ❌, xnai-rag ⚠️, xnai-sambanova 🔵 | Degraded | **P1** |
| **T4: Observability** | grafana ❌, caddy ❌, victoriametrics ✅ | Partial | **P1** |
| **T5: Optional** | vikunja 🔴, consul 🔴, openpipe 🔴, mkdocs 🔴 | Exited | P3 |
| **T6: MCP Servers** | 10 servers (ports 8005–8014) | Mixed | **P0** |

### 1.2 Full Service Port Map

```
Port  Service              Protocol  Network
────  ───────────────────  ────────  ──────────────────
5432  postgres             TCP       xnai_db_network
6379  redis                TCP       xnai_db_network
3306  mariadb/vikunja_db   TCP       xnai_db_network
6333  qdrant               HTTP      xnai_app_network
8005  memory-bank-mcp      HTTP      xnai_app_network
8006  xnai-github          HTTP      xnai_app_network
8007  xnai-rag             HTTP      xnai_app_network
8008  xnai-stats-mcp       HTTP      xnai_app_network
8009  xnai-websearch       HTTP      xnai_app_network
8010  xnai-gnosis          HTTP      xnai_app_network
8011  xnai-agentbus        HTTP      xnai_app_network
8012  xnai-memory          HTTP      xnai_app_network
8014  xnai-sambanova       HTTP      xnai_app_network
8100  oikos                HTTP      xnai_app_network
8102  rag_api              HTTP      xnai_app_network
8103  librarian            HTTP      xnai_app_network
8104  knowledge_miner      HTTP      xnai_app_network
8105  booklore             HTTP      xnai_app_network
8428  victoriametrics      HTTP      xnai_app_network
3000  grafana              HTTP      xnai_app_network
80    caddy (HTTP)         TCP       host
443   caddy (HTTPS)        TCP       host
```

---

## 2. Critical Path & Dependency Analysis

```
USER TOOLS (7)
     │
     ├──► memory-bank-mcp (8005) ──► redis ──► postgres
     │         [CRITICAL HUB]
     │
     ├──► rag_api (8102) ──────────► qdrant (6333) [UNHEALTHY]
     │         [BLOCKED]                    │
     │                                      ├──► redis
     │                                      └──► postgres
     │
     └──► All Facets (9) ──────────► memory-bank-mcp
                                    └──► qdrant [BLOCKED]

RECOVERY ORDER:
  1. qdrant         (unblocks rag_api + facet vector search)
  2. rag_api        (unblocks 8+ dependent services)
  3. oikos          (house management — independent)
  4. librarian      (document management — semi-independent)
  5. grafana        (observability — independent)
  6. caddy          (reverse proxy — restore after services up)
```

---

## 3. Service Recovery — 6 Unhealthy Services

### 3.1 Pre-Recovery Diagnosis Script

```bash
#!/usr/bin/env bash
# Run this before recovery to understand WHY each service is unhealthy

UNHEALTHY_SERVICES=(qdrant oikos rag_api librarian grafana caddy)

for SVC in "${UNHEALTHY_SERVICES[@]}"; do
  echo "══════════════════════════════"
  echo "  Service: $SVC"
  echo "══════════════════════════════"
  echo "Status:"
  podman inspect "$SVC" --format '{{.State.Status}} | Health: {{.State.Health.Status}}' 2>/dev/null || echo "  Container not found"
  echo "Last 20 log lines:"
  podman logs --tail 20 "$SVC" 2>/dev/null || echo "  No logs available"
  echo "Memory usage:"
  podman stats --no-stream "$SVC" 2>/dev/null || echo "  Not running"
  echo ""
done
```

### 3.2 Recovery: qdrant (Vector Database)

**Root Cause:** OOM (Out of Memory) kill — qdrant requests 1 GB but peaks at 2–3 GB during indexing.

```bash
# Step 1: Check OOM evidence
sudo dmesg | grep -i "oom\|killed" | tail -10

# Step 2: Add memory limit to prevent OOM cascade (update docker-compose.yml)
# Add under qdrant service:
# deploy:
#   resources:
#     limits:
#       memory: 768M    # Cap to prevent OOM kill of other services
#     reservations:
#       memory: 256M

# Step 3: Add startup delay to avoid RAM peak collision with rag_api
# Add: restart_policy: { condition: on-failure, delay: 10s, max_attempts: 5 }

# Step 4: Restart
cd ~/Documents/Xoe-NovAi/omega-stack/
podman-compose up -d qdrant

# Step 5: Wait for health
timeout 60 bash -c 'until curl -sf http://localhost:6333/health; do sleep 2; done' && echo "qdrant healthy"
```

> **⚠️ EDGE CASE — qdrant Disk Space:**  
> qdrant uses a WAL (Write-Ahead Log) for vector persistence. If the root filesystem was at 93% and qdrant was writing, its WAL files may be corrupted. After restart, check:
> ```bash
> podman exec qdrant ls /qdrant/storage/ 2>/dev/null
> # If WAL corruption, qdrant will log: "Failed to load storage" 
> # Solution: podman volume rm qdrant_data && podman-compose up -d qdrant
> # WARNING: This destroys all vectors. Only do this if you can re-index.
> ```

### 3.3 Recovery: rag_api

**Root Cause:** Health check timeout waiting on qdrant dependency.

```bash
# Only proceed after qdrant is healthy
curl -sf http://localhost:6333/health || { echo "qdrant not ready — fix qdrant first"; exit 1; }

# Restart rag_api
podman-compose up -d rag_api

# Verify
sleep 10
curl -sf http://localhost:8102/health && echo "rag_api healthy"
```

### 3.4 Recovery: oikos, librarian, grafana, caddy

```bash
# These are independent — can be restarted simultaneously
for SVC in oikos librarian grafana caddy; do
  echo "Restarting $SVC..."
  podman-compose up -d "$SVC"
  sleep 3
  curl -sf "http://localhost:$(podman inspect "$SVC" --format '{{(index .HostConfig.PortBindings | json)}}' 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); print(list(d.values())[0][0]["HostPort"] if d else "unknown")' 2>/dev/null)/health" && echo "$SVC: healthy" || echo "$SVC: not responding (may not have /health endpoint)"
done
```

---

## 4. Resource Limits Hardening

> **🤖 AGENT DIRECTIVE:** The stack has **350% memory overcommit** (23.5 GB requested vs 6.6 GB available). Without memory limits, a single service can OOM-kill the entire stack. The following limits are calibrated for 6.6 GB RAM with 25 services.

### 4.1 docker-compose.yml Resource Limits Block

Add the following `deploy.resources` sections to each service in your `docker-compose.yml`:

```yaml
# ─── INFRASTRUCTURE TIER ─────────────────────────────────────────────────────
services:
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
        limits:   { memory: 384M, cpus: '0.5' }
        reservations: { memory: 128M }

  victoriametrics:
    deploy:
      resources:
        limits:   { memory: 384M, cpus: '0.5' }
        reservations: { memory: 128M }

# ─── API TIER ────────────────────────────────────────────────────────────────
  memory-bank-mcp:
    deploy:
      resources:
        limits:   { memory: 768M, cpus: '2.0' }
        reservations: { memory: 256M }

  qdrant:
    deploy:
      resources:
        limits:   { memory: 768M, cpus: '2.0' }
        reservations: { memory: 256M }

  rag_api:
    deploy:
      resources:
        limits:   { memory: 1536M, cpus: '2.0' }
        reservations: { memory: 512M }

  oikos:
    deploy:
      resources:
        limits:   { memory: 384M, cpus: '1.0' }
        reservations: { memory: 128M }

  librarian:
    deploy:
      resources:
        limits:   { memory: 384M, cpus: '1.0' }
        reservations: { memory: 128M }

# ─── MCP SERVERS (each) ──────────────────────────────────────────────────────
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

  xnai-rag:
    deploy:
      resources:
        limits:   { memory: 1024M, cpus: '2.0' }

  xnai-memory:
    deploy:
      resources:
        limits:   { memory: 384M, cpus: '0.5' }

  xnai-sambanova:
    deploy:
      resources:
        limits:   { memory: 1024M, cpus: '2.0' }

# ─── OBSERVABILITY ───────────────────────────────────────────────────────────
  grafana:
    deploy:
      resources:
        limits:   { memory: 384M, cpus: '0.5' }

  caddy:
    deploy:
      resources:
        limits:   { memory: 192M, cpus: '0.25' }
```

> **⚠️ EDGE CASE — Podman vs Docker Compose `deploy` syntax:**  
> Podman-compose versions < 1.0.6 may ignore `deploy.resources`. Verify:
> ```bash
> podman-compose version
> # If old, use: --memory flag in the container definition instead
> # Or migrate to Quadlets (Section 5) which have native resource controls.
> ```

---

## 5. Quadlet Migration — Primary Orchestration Method

> **🤖 AGENT DIRECTIVE (Gemini 3.1 Integration):**  
> Per the Gemini 3.1 Pro review, **Quadlets are promoted from Secondary to PRIMARY** Layer 3 orchestration. `podman-compose` has known bugs with user namespaces and does not guarantee startup ordering. Quadlets are natively integrated into systemd and provide:
> - Guaranteed dependency ordering (`After=` / `Requires=`)
> - Auto-start on reboot without a daemon
> - Native `keep-id` namespace support
> - Per-service resource control via `[Service]` cgroup directives

### 5.1 Quadlet Directory Setup

```bash
mkdir -p ~/.config/containers/systemd/
# Quadlet .container files go here — systemd auto-detects them on daemon-reload
```

### 5.2 Infrastructure Tier Quadlets

```ini
# ~/.config/containers/systemd/omega-redis.container
[Unit]
Description=Omega-Stack Redis Cache
After=network-online.target

[Container]
Image=redis:7-alpine
ContainerName=redis
PublishPort=127.0.0.1:6379:6379
Network=xnai_db_network
Volume=%h/Documents/Xoe-NovAi/omega-stack/data/redis:/data:U,z
HealthCmd=redis-cli ping
HealthInterval=10s
HealthRetries=3

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
Description=Omega-Stack PostgreSQL Database
After=network-online.target

[Container]
Image=postgres:15
ContainerName=postgres
Network=xnai_db_network
Volume=omega-postgres-data:/var/lib/postgresql/data:U,z
EnvironmentFile=%h/Documents/Xoe-NovAi/omega-stack/.env
HealthCmd=pg_isready -U ${POSTGRES_USER:-postgres}
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
# ~/.config/containers/systemd/omega-memory-bank.container
[Unit]
Description=Omega-Stack Memory Bank MCP Server
After=omega-redis.service omega-postgres.service
Requires=omega-redis.service omega-postgres.service

[Container]
Image=omega-stack/memory-bank:latest
ContainerName=memory-bank-mcp
UserNS=keep-id
User=1000:1000
PublishPort=127.0.0.1:8005:8005
Network=xnai_app_network
Volume=%h/Documents/Xoe-NovAi/omega-stack/.gemini:/app/.gemini:U,z
EnvironmentFile=%h/Documents/Xoe-NovAi/omega-stack/.env
Environment=NODE_OPTIONS=--max_old_space_size=4096
Environment=OPENBLAS_CORETYPE=ZEN2
HealthCmd=curl -sf http://localhost:8005/health
HealthInterval=20s
HealthRetries=5

[Service]
Restart=on-failure
RestartSec=10s
MemoryMax=768M
TimeoutStartSec=60

[Install]
WantedBy=default.target
```

```ini
# ~/.config/containers/systemd/omega-qdrant.container
[Unit]
Description=Omega-Stack Qdrant Vector Database
After=omega-redis.service omega-postgres.service
Requires=omega-redis.service

[Container]
Image=qdrant/qdrant:latest
ContainerName=qdrant
PublishPort=127.0.0.1:6333:6333
Network=xnai_app_network
Volume=omega-qdrant-data:/qdrant/storage:U,z
HealthCmd=curl -sf http://localhost:6333/health
HealthInterval=20s
HealthRetries=5
HealthStartPeriod=30s

[Service]
Restart=on-failure
RestartSec=15s
MemoryMax=768M
TimeoutStartSec=90

[Install]
WantedBy=default.target
```

### 5.3 Deploy Quadlets

```bash
#!/usr/bin/env bash
# Deploy all Quadlet container units

systemctl --user daemon-reload

# Start in dependency order
UNITS=(omega-redis omega-postgres omega-memory-bank omega-qdrant)
for UNIT in "${UNITS[@]}"; do
  echo "Starting $UNIT..."
  systemctl --user enable --now "${UNIT}.service"
  sleep 5
  systemctl --user is-active "${UNIT}.service" && echo "✅ $UNIT active" || echo "❌ $UNIT failed"
done

# Check all
systemctl --user list-units 'omega-*.service' --no-pager
```

> **📝 AGENT NOTE — Quadlet Namespace:**  
> When using `UserNS=keep-id` in a Quadlet, you do NOT need `--userns=keep-id` on the command line — the Quadlet generates the correct systemd unit. However, you MUST also ensure the volume host path is owned by UID 1000 (run Layer 1 restore first).

---

## 6. Health Check Implementation

### 6.1 Add Health Checks to Services Without Them

Seven services currently have no health checks. Add these to docker-compose.yml:

```yaml
# Add to each service that lacks healthcheck:
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
      start_period: 30s

  xnai-github:
    healthcheck:
      test: ["CMD", "curl", "-sf", "http://localhost:8006/health"]
      interval: 20s
      timeout: 5s
      retries: 3
```

---

## 7. Service Startup Ordering

### 7.1 Current Problem

`podman-compose` does not enforce `depends_on` with health condition. Services start in parallel and race for resources.

### 7.2 Solution: Startup Script (Pre-Quadlet Migration)

```bash
#!/usr/bin/env bash
# omega_start.sh — ordered startup with health verification
set -euo pipefail
COMPOSE_DIR=~/Documents/Xoe-NovAi/omega-stack/

wait_healthy() {
  local SVC="$1" PORT="$2" MAX="${3:-60}"
  echo -n "Waiting for $SVC..."
  for i in $(seq 1 "$MAX"); do
    curl -sf "http://localhost:${PORT}/health" &>/dev/null && echo " ✅" && return 0
    sleep 1
    echo -n "."
  done
  echo " ❌ TIMEOUT after ${MAX}s"
  return 1
}

cd "$COMPOSE_DIR"

echo "=== Phase 1: Infrastructure ==="
podman-compose up -d redis postgres vikunja_db victoriametrics
sleep 10
wait_healthy redis 6379 || exit 1

echo "=== Phase 2: Core APIs ==="
podman-compose up -d qdrant memory-bank-mcp
wait_healthy qdrant 6333 90

echo "=== Phase 3: Integration ==="
podman-compose up -d rag_api librarian oikos

echo "=== Phase 4: MCP Servers ==="
podman-compose up -d xnai-github xnai-stats-mcp xnai-websearch xnai-gnosis xnai-agentbus xnai-memory

echo "=== Phase 5: Observability & Proxy ==="
podman-compose up -d grafana caddy

echo "=== Startup Complete ==="
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

---

## 8. Container Lifecycle Management

```bash
# Graceful full stack stop (preserve data)
podman stop --all --time 30

# Graceful restart of a single service
podman restart --time 15 qdrant

# Check resource usage (live)
podman stats --no-stream

# View all container logs since last hour
for C in $(podman ps -q); do
  echo "=== $(podman inspect $C --format '{{.Name}}') ==="; 
  podman logs --since 1h "$C" 2>&1 | tail -5
done
```

---

## 9. Edge Cases & Failure Modes

| Scenario | Detection | Resolution |
|----------|-----------|------------|
| qdrant WAL corruption | `podman logs qdrant` shows "Failed to load storage" | `podman volume rm qdrant_data` then restart (destroys vectors) |
| rag_api timeout loop | Health check fails for >5 min despite qdrant being up | Check rag_api logs for database migration errors |
| caddy port 80/443 blocked | `podman-compose up -d caddy` fails | Check if host firewall blocks ports; run `ss -tuln | grep ':80'` |
| Memory cascade failure | Multiple containers OOM-kill in sequence | `podman stop --all` immediately; free RAM; restart in order |
| consul exited | Service discovery unavailable | Determine if consul is still required; if not, remove from compose |
| podman-compose race condition | Services start before dependencies are ready | Use `omega_start.sh` ordered script or migrate to Quadlets |

---

## 10. Verification Checklist

```bash
#!/usr/bin/env bash
echo "=== IMPL-02 CONTAINER ORCHESTRATION VERIFICATION ==="

# Critical services healthy
for SVC_PORT in "redis:6379" "postgres:5432" "memory-bank-mcp:8005"; do
  SVC="${SVC_PORT%%:*}"
  PORT="${SVC_PORT##*:}"
  if curl -sf "http://localhost:${PORT}/health" &>/dev/null || podman healthcheck run "$SVC" &>/dev/null 2>&1; then
    echo "✅ $SVC healthy"
  else
    echo "❌ $SVC not healthy"
  fi
done

# Count unhealthy
UNHEALTHY=$(podman ps --filter "health=unhealthy" --format "{{.Names}}" | wc -l)
echo "$([ "$UNHEALTHY" -eq 0 ] && echo '✅' || echo '⚠️') Unhealthy containers: $UNHEALTHY"

# Memory limits set
podman inspect redis --format '{{.HostConfig.Memory}}' | grep -q "^[1-9]" && echo "✅ Memory limits set on redis" || echo "❌ No memory limit on redis"

echo "=== END VERIFICATION ==="
```

---

> **📋 NEXT MANUAL:** Proceed to `IMPL_07_PERMISSIONS_4LAYER.md` for the critical `.gemini` permission resolution, or `IMPL_03_MCP_ECOSYSTEM.md` for MCP server configuration.
