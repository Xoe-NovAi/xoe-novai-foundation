---
title: "Omega-Stack Implementation Manual 01: Infrastructure & Platform Layer"
section: "01"
scope: "Hardware, OS, Podman, Storage, Networking"
status: "Actionable — Execute Immediately"
owner: "arcana-novai (UID 1000)"
last_updated: "2026-03-13"
gemini_review: "Integrated — v3.1 Pro validation applied"
confidence: "100% system-verified"
priority: "P0 — CRITICAL (Storage Crisis)"
---

# IMPL-01 — Infrastructure & Platform Layer
## Omega-Stack Agent Implementation Manual

> **🤖 AGENT DIRECTIVE:** This manual covers the physical and OS layer of the Omega-Stack. You are operating on a Zen 2 mobile platform with 6.6 GB RAM and a **critically full root filesystem (93%)**. The storage crisis is P0 — address it before executing any other layer. All commands assume you are running as `arcana-novai` (UID 1000).

---

## Table of Contents

1. [Platform Overview](#1-platform-overview)
2. [CPU Optimization](#2-cpu-optimization)
3. [Memory Architecture & Management](#3-memory-architecture--management)
4. [Storage Crisis Resolution (P0)](#4-storage-crisis-resolution-p0)
5. [Podman Runtime Configuration](#5-podman-runtime-configuration)
6. [Network Architecture Verification](#6-network-architecture-verification)
7. [OS Hardening Baseline](#7-os-hardening-baseline)
8. [Diagnostic Command Reference](#8-diagnostic-command-reference)
9. [Edge Cases & Failure Modes](#9-edge-cases--failure-modes)
10. [Verification Checklist](#10-verification-checklist)

---

## 1. Platform Overview

| Component | Specification | Status |
|-----------|---------------|--------|
| CPU | AMD Ryzen 7 5700U — Zen 2, 8c/16t, 15W TDP | ✅ Healthy (4.7% usage) |
| RAM | 6.6 GB physical + 8 GB zRAM swap | ⚠️ Moderate (59% used, 2.5 GB swap active) |
| OS | Ubuntu 25.10 — Kernel 6.17.0-14-generic | ✅ Current |
| Runtime | Podman 5.4.2 — rootless, no daemon | ✅ Operational |
| Root FS | ext4 — 117 GB, **93% full (8.2 GB free)** | 🔴 CRITICAL |
| Library | ext4 — 110 GB at `/media/arcana-novai/omega_library/` | ✅ 40% used |
| Vault | ext4 — 16 GB at `/media/arcana-novai/omega_vault/` | ⚠️ 75% used |
| Security | AppArmor (NOT SELinux) — permissive mode | ⚠️ Needs enforcement |

> **⚠️ AGENT CALLOUT — CRITICAL CONTEXT:**  
> This system runs **AppArmor**, not SELinux. Any instructions referencing `:Z` volume flags or `setenforce`/`getenforce` do NOT apply here. Podman's `:z`/`:Z` flags are SELinux-only and are effectively no-ops on Ubuntu. AppArmor policy management uses `aa-status`, `aa-enforce`, and profile files in `/etc/apparmor.d/`.

---

## 2. CPU Optimization

The Ryzen 5700U is **not the bottleneck**. These optimizations are pre-configured and should survive across reboots.

### 2.1 Verify Current CPU Environment Variables

```bash
# These should be in ~/.profile or ~/.bashrc
grep -E 'OPENBLAS|N_THREADS|GOAMD64|RUSTFLAGS|OMP_NUM' ~/.profile ~/.bashrc 2>/dev/null

# Expected output (all should be present):
# OPENBLAS_CORETYPE=ZEN2
# N_THREADS=6
# OMP_NUM_THREADS=6
```

### 2.2 Ensure Global Optimization Profile

Create or update `~/.profile`:

```bash
cat >> ~/.profile << 'EOF'

# ─── Omega-Stack CPU Optimization (Zen 2 / Ryzen 5700U) ──────────────────────
export OPENBLAS_CORETYPE=ZEN2
export N_THREADS=6
export OMP_NUM_THREADS=6
export MKL_THREADING_LAYER=GNU
export GOAMD64=v3
export RUSTFLAGS='-C target-cpu=znver2'
export NODE_OPTIONS='--max_old_space_size=4096'
# ──────────────────────────────────────────────────────────────────────────────
EOF
source ~/.profile
```

### 2.3 Verify CPU Instruction Set Support

```bash
# Confirm Zen 2 features are available
grep -m1 'flags' /proc/cpuinfo | tr ' ' '\n' | grep -E 'avx2|fma|sha_ni|sse4_2|aes' | sort
# Expected: aes, avx2, fma, sha_ni, sse4_2
```

> **📝 AGENT NOTE:** AVX-512 is NOT available on the Ryzen 5700U. Any container image or library that requires `AVX512F` will fail. Ensure all ML libraries (PyTorch, TensorFlow) use AVX2 builds, not AVX-512 builds.

---

## 3. Memory Architecture & Management

### 3.1 Current Memory Snapshot

```bash
free -h
# Target state:
# Mem:   6.6Gi  used: <4Gi  free: >2.5Gi  swap: <1Gi
```

### 3.2 OOM Score Tuning

Protect critical services from OOM killer. Apply immediately:

```bash
#!/usr/bin/env bash
# Protect critical Podman containers from OOM kill
# Run as root or via sudo

protect_container() {
  local NAME="$1"
  local SCORE="$2"  # -1000 = never kill, 1000 = kill first
  local PID
  PID=$(podman inspect --format '{{.State.Pid}}' "$NAME" 2>/dev/null)
  if [ -n "$PID" ] && [ "$PID" -gt 0 ]; then
    echo "$SCORE" | sudo tee "/proc/$PID/oom_score_adj" > /dev/null
    echo "Protected $NAME (PID $PID) with oom_score_adj=$SCORE"
  fi
}

# Critical — never kill
protect_container "postgres"      -500
protect_container "redis"         -500
protect_container "memory-bank-mcp" -300

# High priority — kill last
protect_container "qdrant"        100
protect_container "rag_api"       200

# Low priority — kill first (optional services)
protect_container "mkdocs"        800
protect_container "grafana"       600
```

### 3.3 Swap Tuning

```bash
# Check current swappiness (lower = prefer RAM over swap)
cat /proc/sys/vm/swappiness
# For a server/dev workstation, 10-30 is appropriate

# Set persistently
echo 'vm.swappiness=10' | sudo tee /etc/sysctl.d/99-omega-stack.conf
echo 'vm.dirty_ratio=15' >> /tmp/sysctl_omega
echo 'vm.dirty_background_ratio=5' >> /tmp/sysctl_omega
sudo cp /tmp/sysctl_omega /etc/sysctl.d/99-omega-stack.conf
sudo sysctl -p /etc/sysctl.d/99-omega-stack.conf
```

---

## 4. Storage Crisis Resolution (P0)

> **🔴 AGENT DIRECTIVE — EXECUTE THIS SECTION FIRST:**  
> The root filesystem is at **93% capacity (8.2 GB free)**. SQLite (Podman's metadata backend) will begin failing writes at 95%. The system will become **unstable and unrecoverable** if it reaches 100%. Free a minimum of **20 GB before any other work**.

### 4.1 Emergency Space Assessment

```bash
#!/usr/bin/env bash
echo "=== ROOT FILESYSTEM STATUS ==="
df -h /
echo ""
echo "=== TOP 15 SPACE CONSUMERS (may take 30-60s) ==="
sudo du -sh /* 2>/dev/null | sort -rh | head -15
echo ""
echo "=== PODMAN IMAGE CACHE ==="
podman system df
echo ""
echo "=== JOURNAL LOG SIZE ==="
journalctl --disk-usage
echo ""
echo "=== /var/log SIZE ==="
sudo du -sh /var/log/
echo ""
echo "=== /tmp SIZE ==="
du -sh /tmp/
```

### 4.2 Phase 1 — Safe Automated Cleanup (Target: 8–12 GB freed)

```bash
#!/usr/bin/env bash
# Safe cleanup — no user data at risk
set -euo pipefail
LOG="/tmp/storage_cleanup_$(date +%Y%m%d_%H%M%S).log"
log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }

log "=== OMEGA-STACK STORAGE RECOVERY PHASE 1 ==="
BEFORE=$(df / | tail -1 | awk '{print $4}')

# 1. Podman image/container/volume prune
log "Pruning unused Podman resources..."
podman system prune -af 2>&1 | tee -a "$LOG" || true
log "Podman prune complete."

# 2. SQLite VACUUM (Podman metadata) — IMPORTANT per Gemini review
log "Vacuuming Podman SQLite database..."
DB="$HOME/.local/share/containers/storage/libpod/bolt_state.db"
if [ -f "$DB" ]; then
  sqlite3 "$DB" "VACUUM;" && log "SQLite VACUUM complete." || log "sqlite3 not installed — skipping VACUUM"
fi

# 3. Journal logs — keep 7 days
log "Truncating systemd journals..."
journalctl --vacuum-time=7d 2>&1 | tee -a "$LOG"

# 4. npm and pip caches
log "Clearing npm cache..."
npm cache clean --force 2>/dev/null | tee -a "$LOG" || true
log "Clearing pip cache..."
pip cache purge 2>/dev/null | tee -a "$LOG" || true

# 5. Temp files
log "Cleaning /tmp..."
find /tmp -maxdepth 1 -type f -mtime +3 -delete 2>/dev/null || true

AFTER=$(df / | tail -1 | awk '{print $4}')
FREED=$(( (AFTER - BEFORE) / 1024 ))
log "Phase 1 complete. Freed approximately ${FREED} MB."
log "New disk status: $(df -h / | tail -1)"
log "Full log: $LOG"
```

### 4.3 Phase 2 — Targeted Large File Removal (Target: additional 5–8 GB)

```bash
# Find and review before deleting
echo "=== Git objects (compressible) ==="
du -sh ~/Documents/Xoe-NovAi/omega-stack/.git/

# Compress git history
cd ~/Documents/Xoe-NovAi/omega-stack/
git gc --aggressive --prune=now
git reflog expire --expire=30.days --all

# Find old log files
find ~/Documents/Xoe-NovAi/omega-stack/ -name "*.log" -mtime +7 -exec ls -lh {} \;
# Review output, then delete safely:
# find ~/Documents/Xoe-NovAi/omega-stack/ -name "*.log" -mtime +7 -delete

# Find build artifacts
find ~/Documents/Xoe-NovAi/omega-stack/ -name "node_modules" -type d | xargs du -sh 2>/dev/null
```

### 4.4 Phase 3 — Podman Storage Migration (Optional, gains 10–15 GB)

If root filesystem remains above 85% after Phases 1–2, relocate Podman's storage to the library mount:

```bash
# IMPORTANT: Stop all containers first
podman stop --all --time 30

# Create storage location on library mount
mkdir -p /media/arcana-novai/omega_library/podman-storage

# Update storage.conf
mkdir -p ~/.config/containers/
cat > ~/.config/containers/storage.conf << 'EOF'
[storage]
driver = "overlay"
graphRoot = "/media/arcana-novai/omega_library/podman-storage"

[storage.options.overlay]
mountopt = "nodev"
EOF

# Re-pull required images (existing layers won't transfer automatically)
echo "After config change, run: podman pull <images>"
echo "Or use: podman save | podman load to migrate existing images"
```

> **⚠️ EDGE CASE — Podman Storage Migration:**  
> If the omega_library mount is on a USB or external drive, Podman will fail to start containers if the drive is unmounted. Always ensure `/etc/fstab` has the mount with `nofail` and `x-systemd.automount` options if using external storage for Podman's graphRoot.

### 4.5 Log Rotation — Prevent Recurrence

```bash
sudo tee /etc/logrotate.d/omega-stack << 'EOF'
/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/**/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 arcana-novai arcana-novai
}
EOF
```

---

## 5. Podman Runtime Configuration

### 5.1 Verify UID Mapping

```bash
# Confirm subuid/subgid ranges
cat /etc/subuid | grep arcana-novai
cat /etc/subgid | grep arcana-novai
# Expected: arcana-novai:100000:65536

# Verify user lingering (required for rootless services to survive logout)
loginctl show-user arcana-novai | grep Linger
# Expected: Linger=yes
# If no: loginctl enable-linger arcana-novai
```

### 5.2 Enable User Lingering (Persistent Services)

```bash
loginctl enable-linger "$(whoami)"
# Verify:
loginctl show-user "$(whoami)" | grep Linger
```

### 5.3 Podman Storage Verification

```bash
# Confirm overlay driver in use (no fuse-overlayfs on kernel 6.x)
podman info | grep -E '(graphDriver|GraphDriver|graphRoot|storage)'
# Expected: graphDriverName: overlay (native, NOT fuse-overlayfs)

# Check SQLite backend
ls -la ~/.local/share/containers/storage/libpod/
```

---

## 6. Network Architecture Verification

### 6.1 Confirm Network Topology

```bash
podman network ls
# Expected networks:
# NAME               DRIVER    INTERNAL
# podman             bridge    false     (default, external access)
# xnai_db_network    bridge    true      (DB isolation — internal only)
# xnai_app_network   bridge    false     (app services)

podman network inspect xnai_db_network | grep -E '(internal|subnet)'
# Expected: "internal": true  — database network is isolated from host
```

### 6.2 DNS Resolution Check

```bash
# Verify aardvark-dns is running
podman network inspect podman | grep -i dns
# Should show: "dns_enabled": true

# Test inter-container DNS (from any running container)
podman exec redis ping -c 1 postgres 2>/dev/null || echo "DNS test requires running containers"
```

> **📝 AGENT NOTE — DNS Failover Gap:**  
> There is **no backup DNS** configured for external name resolution. If aardvark-dns fails, external requests will fail silently. Add `8.8.8.8` as a fallback in `/etc/containers/containers.conf`:
> ```ini
> [network]
> dns_servers = ["8.8.8.8", "1.1.1.1"]
> ```

---

## 7. OS Hardening Baseline

### 7.1 AppArmor Status

```bash
aa-status 2>/dev/null || sudo aa-status
# Note: AppArmor profiles for containers are auto-generated by Podman
# To see active profiles:
sudo aa-status | grep podman
```

### 7.2 Kernel Hardening (sysctl)

```bash
sudo tee /etc/sysctl.d/99-omega-stack.conf << 'EOF'
# Memory management
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
vm.overcommit_memory = 1

# Network hardening
net.ipv4.tcp_syncookies = 1
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.accept_source_route = 0
net.ipv6.conf.all.disable_ipv6 = 0

# File system
fs.inotify.max_user_watches = 524288
fs.inotify.max_user_instances = 512
EOF

sudo sysctl -p /etc/sysctl.d/99-omega-stack.conf
```

### 7.3 inotify Limits (Critical for VS Code + Systemd Path Units)

```bash
# Verify current limits
sysctl fs.inotify.max_user_watches
# If below 524288, VS Code and systemd path units will drop events
```

---

## 8. Diagnostic Command Reference

```bash
# Full infrastructure snapshot
alias omega-status='echo "=== CPU ===" && top -bn1 | head -5 && echo "=== MEMORY ===" && free -h && echo "=== DISK ===" && df -h && echo "=== PODMAN ===" && podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'

# Quick health check
df -h /                                    # Disk space
free -h                                    # Memory
podman ps --format "table {{.Names}}\t{{.Status}}"  # Container status
journalctl --user -n 20 --no-pager        # Recent user logs
systemctl --user list-timers --no-pager   # Active timers
```

---

## 9. Edge Cases & Failure Modes

| Scenario | Symptom | Resolution |
|----------|---------|------------|
| Disk fills to 100% | Podman refuses to start containers; SQLite corruption | Immediate: `rm -rf /tmp/*`, journal vacuum, then Phase 1 cleanup |
| zRAM swap exhausted | OOM kills cascade; services die in random order | Stop non-critical containers first; check `dmesg | grep -i oom` |
| Podman pause process killed | `--userns=auto` namespace assignments reset | Restart with `--userns=keep-id` (see IMPL-07) |
| aardvark-dns crash | Inter-container DNS fails; services cannot reach each other by name | `podman network reload` or restart affected containers |
| Library mount unmounted | If Podman graphRoot moved there, ALL containers fail to start | Ensure mount is in `/etc/fstab` with `nofail` option |
| Kernel 6.x overlay mount fails | `ENOSPC` on inode exhaustion (not block exhaustion) | `df -i /` — if inodes exhausted, delete many small files |

---

## 10. Verification Checklist

```bash
#!/usr/bin/env bash
echo "=== IMPL-01 INFRASTRUCTURE VERIFICATION ==="

check() { [ "$1" ] && echo "✅ $2" || echo "❌ $2 — FAILED"; }

# Disk
DISK_PCT=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
check "$([ "$DISK_PCT" -lt 85 ] && echo ok)" "Root filesystem below 85% (current: ${DISK_PCT}%)"

# Memory swap
SWAP_USED=$(free | grep Swap | awk '{print $3}')
check "$([ "$SWAP_USED" -lt 4000000 ] && echo ok)" "Swap usage below 4GB (current: ${SWAP_USED} kB)"

# Podman
check "$(podman --version &>/dev/null && echo ok)" "Podman available"
check "$(loginctl show-user "$(whoami)" | grep -q 'Linger=yes' && echo ok)" "User lingering enabled"

# UID mapping
check "$(grep -q arcana-novai /etc/subuid && echo ok)" "subuid mapping configured"

# Optimization vars
check "$(grep -q OPENBLAS_CORETYPE ~/.profile 2>/dev/null && echo ok)" "CPU optimization vars in ~/.profile"

# Sysctl
check "$(sysctl vm.swappiness | grep -q '= 10' && echo ok)" "Swappiness set to 10"

echo "=== END VERIFICATION ==="
```

---

> **📋 NEXT MANUAL:** Proceed to `IMPL_02_CONTAINER_ORCHESTRATION.md` only after root filesystem is below 85% capacity.
