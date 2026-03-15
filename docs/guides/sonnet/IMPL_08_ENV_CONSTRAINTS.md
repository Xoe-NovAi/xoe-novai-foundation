---
title: "Omega-Stack Implementation Manual 08: Environment Constraints & Resource Optimization"
section: "08"
scope: "Memory management, disk constraints, resource limits, scaling paths"
status: "Actionable"
priority: "P1 — Memory 350% Overcommitted, Disk 93% Full"
last_updated: "2026-03-13"
---

# IMPL-08 — Environment Constraints & Resource Optimization
## Omega-Stack Agent Implementation Manual

> **🤖 AGENT DIRECTIVE:** The Omega-Stack operates in a **memory-constrained, disk-critical environment**. This manual provides specific, calibrated resource settings for the Ryzen 5700U + 6.6GB RAM platform. Do not use generic "enterprise" resource settings — they will cause OOM cascade on this hardware.

---

## Table of Contents
1. [Constraint Summary](#1-constraint-summary)
2. [Memory Tier Management](#2-memory-tier-management)
3. [Service Priority Classification](#3-service-priority-classification)
4. [cgroup Resource Controls](#4-cgroup-resource-controls)
5. [Disk I/O Optimization](#5-disk-io-optimization)
6. [Scaling Paths](#6-scaling-paths)
7. [Thermal Management](#7-thermal-management)
8. [Edge Cases](#8-edge-cases)

---

## 1. Constraint Summary

| Resource | Total | Used | Available | Status |
|---------|-------|------|-----------|--------|
| RAM | 6.6 GB | ~3.9 GB (59%) | 2.7 GB | ⚠️ Moderate |
| Swap | 8 GB | 2.5 GB (31%) | 5.5 GB | ⚠️ Active |
| CPU | 8c/16t @ 4.37GHz | 4.7% | 95.3% | ✅ Ample |
| Root FS | 117 GB | 109 GB | 8 GB | 🔴 CRITICAL |
| Memory requested by services | 23.5 GB | — | — | 🔴 350% overcommit |

---

## 2. Memory Tier Management

### Calibrated Service Memory Budget (6.6 GB Total)

```
CRITICAL RESERVE (always available): 1.2 GB
  → Kernel + OS: 400MB
  → User headroom: 400MB
  → Safety buffer: 400MB

TIER 1 — Infrastructure (allocated: 1.8 GB):
  redis:            384 MB  (current: 256MB — increase for session load)
  postgres:         768 MB  (current: 512MB — increase for complex queries)
  victoriametrics:  384 MB
  vikunja_db:       384 MB

TIER 2 — Core APIs (allocated: 1.6 GB):
  memory-bank-mcp:  768 MB  (CRITICAL — must never OOM)
  qdrant:           768 MB  (vector DB — needs burst capacity)

TIER 3 — Integration (allocated: 2.0 GB — OVERCOMMITTED):
  rag_api:         1024 MB  (reduce from 2048MB default)
  xnai-rag:         512 MB  (reduce from 2048MB)
  xnai-sambanova:   512 MB  (reduce from 2048MB)

REMAINING for 10 MCP servers + optional: ~2.0 GB (~200MB/server)

TOTAL ALLOCATED: 5.4 GB (82% of 6.6 GB) ← SAFE RANGE
```

### Apply Memory Budget

```bash
# Script to apply all memory limits to running containers
# These match the values in IMPL-02 §4 docker-compose.yml block

LIMITS=(
  "redis:384m"
  "postgres:768m"
  "victoriametrics:384m"
  "vikunja_db:384m"
  "memory-bank-mcp:768m"
  "qdrant:768m"
  "rag_api:1024m"
  "xnai-rag:512m"
  "xnai-sambanova:512m"
  "xnai-memory:384m"
  "grafana:384m"
  "caddy:192m"
)

for ENTRY in "${LIMITS[@]}"; do
  SVC="${ENTRY%%:*}"
  MEM="${ENTRY##*:}"
  if podman ps --format '{{.Names}}' | grep -q "^${SVC}$"; then
    podman update --memory "$MEM" "$SVC" 2>/dev/null && echo "✅ $SVC: memory=${MEM}" || echo "⚠️ $SVC: update failed"
  fi
done
```

---

## 3. Service Priority Classification

```bash
# OOM priority scoring — lower = protected from kill, higher = kill first
# Run as root or via sudo

set_oom_score() {
  local NAME="$1" SCORE="$2"
  local PID=$(podman inspect --format '{{.State.Pid}}' "$NAME" 2>/dev/null)
  [ -n "$PID" ] && [ "$PID" -gt 0 ] && \
    echo "$SCORE" | sudo tee "/proc/$PID/oom_score_adj" > /dev/null && \
    echo "Set $NAME OOM score: $SCORE"
}

# Never kill (critical data services)
set_oom_score postgres     -900
set_oom_score redis        -900
set_oom_score vikunja_db   -500

# Protect (core AI services)
set_oom_score memory-bank-mcp -300
set_oom_score qdrant          -100

# Neutral (important but replaceable)
set_oom_score rag_api      100
set_oom_score xnai-rag     200

# Kill first (optional/regenerable)
set_oom_score mkdocs       800
set_oom_score grafana      600
set_oom_score caddy        400
```

---

## 4. cgroup Resource Controls

```bash
# Verify cgroup v2 is active (required for Podman memory limits on Ubuntu 25.10)
mount | grep cgroup2
# Expected: cgroup2 on /sys/fs/cgroup type cgroup2

# Check if memory controller is enabled
cat /sys/fs/cgroup/cgroup.controllers | grep memory
# Expected: memory (among others)

# Verify Podman uses cgroup v2
podman info | grep -i cgroupVersion
# Expected: cgroupVersion: v2

# If cgroup v1 reported, enable v2:
# sudo grubby --update-kernel=ALL --args="systemd.unified_cgroup_hierarchy=1"
# (reboot required)
```

---

## 5. Disk I/O Optimization

```bash
# Check current I/O scheduler (NVMe prefers none or mq-deadline)
cat /sys/block/nvme0n1/queue/scheduler 2>/dev/null || \
  cat /sys/block/sda/queue/scheduler 2>/dev/null
# For NVMe, 'none' is optimal

# Set I/O scheduler persistently
DRIVE=$(df / | tail -1 | awk '{print $1}' | sed 's|/dev/||;s|[0-9]*||')
echo none | sudo tee "/sys/block/${DRIVE}/queue/scheduler" 2>/dev/null || true

# Limit Podman's I/O to prevent a single container from saturating the SSD
# Add to high-I/O containers in docker-compose.yml:
# blkio_config:
#   weight: 300  # Lower = lower priority (default 500)
```

---

## 6. Scaling Paths

### Path 1: RAM Upgrade (Best ROI)

| Upgrade | Cost | Impact |
|---------|------|--------|
| 8 GB → 12 GB | ~$40–60 | Marginal — 182% overcommit vs 350% |
| 8 GB → 16 GB | ~$80–120 | **Recommended** — 147% overcommit, swap drops to <500MB |
| 8 GB → 32 GB | ~$200+ | Full allocation, no overcommit |

```bash
# After RAM upgrade: remove memory limits from non-critical services
# and increase Tier 2 (qdrant, rag_api) to their optimal sizes:
# qdrant:   2GB
# rag_api:  3GB
# xnai-rag: 2GB
```

### Path 2: Podman graphRoot Relocation

Move Podman's image storage to omega_library (65GB free):

```bash
# Already documented in IMPL-01 §4.4 — use if root FS stays critical
```

### Path 3: Reduce Active Services

```bash
# Disable optional services to reclaim ~2GB RAM
OPTIONAL_SERVICES=(mkdocs vikunja booklore consul openpipe knowledge_miner)
for SVC in "${OPTIONAL_SERVICES[@]}"; do
  podman stop "$SVC" 2>/dev/null && echo "Stopped $SVC" || true
done
# Total freed: ~1.5–2.5 GB RAM, ~500MB disk (containers removed)
```

---

## 7. Thermal Management

```bash
# Monitor CPU temperature (critical on 15W TDP mobile chip)
cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null | \
  awk '{printf "%.1f°C\n", $1/1000}'

# Check current P-state (frequency scaling)
cat /proc/cpuinfo | grep 'cpu MHz' | head -4

# If sustained >80°C: reduce N_THREADS
echo "If thermal throttling: reduce N_THREADS from 6 to 4 in ~/.profile"
```

---

## 8. Edge Cases

| Scenario | Detection | Resolution |
|----------|-----------|------------|
| OOM cascade (multiple services killed) | `dmesg | grep -i oom` | Stop optionals immediately; check `free -h`; restart in tier order |
| Swap exhaustion | `free -h` shows 0 swap free | Emergency: `podman stop mkdocs vikunja grafana`; investigate memory leak |
| NVMe SSD write throttling (TBW limit) | I/O latency spikes to 100ms+ | Reduce `vm.dirty_ratio`; implement log rotation |
| cgroup memory limit causes crash loop | Container exits with OOM code 137 | Increase limit by 25%; investigate leak with `podman stats` |
| Zen 2 CPU thermal throttle | Frequency drops to 1.8GHz sustained | Reduce `OMP_NUM_THREADS`; check laptop cooling |
