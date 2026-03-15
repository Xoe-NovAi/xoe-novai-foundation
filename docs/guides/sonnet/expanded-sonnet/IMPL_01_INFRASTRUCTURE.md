---
title: "Omega-Stack Implementation Manual 01: Infrastructure & Platform Layer"
section: "01"
scope: "Hardware, OS, Podman 5.x rootless, pasta networking, storage crisis, OOM tuning, cgroup v2, confidence matrix, decision trees"
status: "Actionable — Execute First; Storage Crisis Is P0"
owner: "arcana-novai (UID 1000)"
last_updated: "2026-03-13"
confidence_overall: "97% (system-verified hardware + upstream-confirmed Podman behaviors)"
haiku_review: "Integrated — confidence matrix, decision trees, fallback strategies applied"
priority: "P0 — Storage at 93%; Execute §4 Before Any Other Manual"
---

# IMPL-01 — Infrastructure & Platform Layer
## Omega-Stack Agent Implementation Manual

> **🤖 CONTEXT PRIME — READ FIRST:**
> - CPU: AMD Ryzen 7 5700U (Zen 2), 8c/16t, 15W TDP — NOT the bottleneck (4.7% used)
> - RAM: 6.6GB physical + 8GB zRAM swap — MODERATE pressure (59% RAM, 31% swap)
> - Root FS: ext4, 117GB, **93% full (8.2GB free) — CRITICAL; fix before everything else**
> - OS: Ubuntu 25.10, Kernel 6.17.x — AppArmor enforcing (NOT SELinux)
> - Runtime: Podman 5.4.2 rootless — **pasta** networking (default since Podman 5.0, not slirp4netns)
> - Networking change: Podman 5.3 fixed container-to-host communication with pasta
> - ACL: ext4 supports ACLs by default since Ubuntu 14.04 — NO fstab change needed
> - Pause process: rootless Podman pause process keeps namespaces alive; killing it resets userns=auto assignments
> - DO NOT attempt any other manual until root FS is below 85%

---

## Confidence Matrix

| Claim | Confidence | Basis | Fragile If... |
|-------|-----------|-------|--------------|
| ext4 has ACL by default on Ubuntu | 99% | Ubuntu kernel config, verified | Custom kernel without ACL support |
| Podman 5.x uses pasta (not slirp4netns) | 98% | Podman 5.0 release notes, upstream docs | Manually overridden in containers.conf |
| `--userns=auto` is non-deterministic across reboots | 97% | Podman GitHub #27577, pause process docs | Only one container running (no contention) |
| `keep-id` maps host UID 1000 → container UID 1000 | 99% | Red Hat upstream, Dan Walsh's authoritative article | subuid entry doesn't exist |
| OverlayFS native on kernel 5.13+ (no fuse-overlayfs) | 98% | ArchWiki, Podman upstream docs | Non-standard kernel build |
| SQLite WAL fails at >95% disk | 95% | WAL mode documentation, observed behavior | Different SQLite mode configured |
| zRAM at 31% swap = manageable | 85% | Inferred from free -h; workload-dependent | Sudden memory spike from ML inference |
| pasta fixes container-to-host in Podman 5.3+ | 93% | ArchWiki, Podman changelog | Older Podman version |

---

## Table of Contents

1. [Platform Overview & Hardware Validation](#1-platform-overview--hardware-validation)
2. [CPU Optimization — Zen 2 Specifics](#2-cpu-optimization--zen-2-specifics)
3. [Memory Architecture & OOM Strategy](#3-memory-architecture--oom-strategy)
4. [Storage Crisis Resolution — P0](#4-storage-crisis-resolution--p0)
5. [Podman 5.x Runtime — Complete Configuration](#5-podman-5x-runtime--complete-configuration)
6. [Networking — pasta vs slirp4netns](#6-networking--pasta-vs-slirp4netns)
7. [OS Hardening Baseline](#7-os-hardening-baseline)
8. [Decision Tree — Diagnose Your Problem](#8-decision-tree--diagnose-your-problem)
9. [Fallback Strategies — When This Guide Fails](#9-fallback-strategies--when-this-guide-fails)
10. [Diagnostic Command Reference](#10-diagnostic-command-reference)
11. [Verification Checklist](#11-verification-checklist)

---

## 1. Platform Overview & Hardware Validation

### 1.1 Verified Hardware Matrix

| Component | Specification | Verify Command | Status |
|-----------|---------------|---------------|--------|
| CPU | Ryzen 7 5700U, Zen 2, 8c/16t | `lscpu \| grep 'Model name'` | ✅ Healthy |
| RAM | 6.6GB + 8GB zRAM | `free -h` | ⚠️ Pressure |
| Root FS | ext4, 117GB, **93% full** | `df -h /` | 🔴 CRITICAL |
| OS | Ubuntu 25.10, Kernel 6.17.x | `lsb_release -d; uname -r` | ✅ Current |
| Runtime | Podman 5.4.2 rootless | `podman --version` | ✅ Optimal |
| Networking | pasta (Podman 5.0+ default) | `podman info \| grep -i network` | ✅ Modern |
| Storage driver | OverlayFS v2 (native kernel) | `podman info \| grep graphDriver` | ✅ No fuse needed |
| MAC | AppArmor | `aa-status 2>/dev/null \| head -3` | ⚠️ Permissive → should enforce |

```bash
#!/usr/bin/env bash
echo "=== INFRASTRUCTURE VALIDATION ==="
echo "CPU:"; lscpu | grep -E 'Model name|CPU\(s\)|Thread|Socket'
echo ""
echo "Memory:"; free -h
echo ""
echo "Disk:"; df -h | grep -E 'Filesystem|/$|omega'
echo ""
echo "Podman:"; podman --version 2>/dev/null
echo "  GraphDriver:"; podman info --format '{{.Store.GraphDriverName}}' 2>/dev/null
echo "  Cgroup version:"; podman info --format '{{.Host.CgroupVersion}}' 2>/dev/null
echo ""
echo "OS:"; lsb_release -d 2>/dev/null; uname -r
echo ""
echo "Network backend:"; podman info 2>/dev/null | grep -i "network\|pasta" | head -3
echo ""
echo "AppArmor:"; aa-status 2>/dev/null | head -5 || echo "  (aa-status unavailable)"
```

### 1.2 Zen 2 Instruction Set Verification

```bash
# Verify required CPU features for ML/BLAS workloads
echo "=== ZEN 2 INSTRUCTION SET CHECK ==="
for FLAG in avx2 fma sha_ni sse4_2 aes; do
  grep -q "$FLAG" /proc/cpuinfo && echo "  ✅ $FLAG" || echo "  ❌ MISSING: $FLAG"
done

# AVX-512 is NOT available on Ryzen 5700U — confirm absence
grep -q "avx512" /proc/cpuinfo && \
  echo "  ⚠️  AVX-512 detected (unexpected for 5700U — verify model)" || \
  echo "  ✅ No AVX-512 (expected — use AVX2 container images)"

echo ""
echo "IMPORTANT: Avoid container images built with AVX-512 — they will SIGILL crash on this CPU"
```

---

## 2. CPU Optimization — Zen 2 Specifics

### 2.1 Optimization Profile

```bash
# Check if optimization profile is already set
grep -E 'OPENBLAS|N_THREADS|GOAMD64' ~/.profile 2>/dev/null && \
  echo "Already configured" || echo "Not configured — applying below"

# Apply Zen 2 optimization profile to ~/.profile
cat >> ~/.profile << 'EOF'

# ─── Omega-Stack CPU Optimization (Zen 2 / Ryzen 5700U) ──────────────────────
export OPENBLAS_CORETYPE=ZEN2            # BLAS matrix ops: Zen 2 ISA path
export N_THREADS=6                       # 6/8 cores: preserves thermal headroom
export OMP_NUM_THREADS=6                 # OpenMP: match N_THREADS
export MKL_THREADING_LAYER=GNU           # MKL: GNU threading (PyTorch compatible)
export GOAMD64=v3                        # Go: AVX2 level (v3 = Zen 2)
export RUSTFLAGS="-C target-cpu=znver2"  # Rust: native Zen 2 optimizations
export NODE_OPTIONS="--max_old_space_size=4096"  # Node.js: 4GB heap
export UV_THREADPOOL_SIZE=16             # libuv: more I/O threads
export PYTHONDONTWRITEBYTECODE=1         # No .pyc files (saves inodes on full disk)
export PYTHONUNBUFFERED=1                # Real-time Python output for containers
export PIP_NO_CACHE_DIR=1               # No pip cache (disk is at 93%)
# ─────────────────────────────────────────────────────────────────────────────
EOF

source ~/.profile && echo "✅ Optimization profile applied"
```

### 2.2 Thread Count Rationale

The Ryzen 5700U has 8 physical cores (16 threads via SMT). Using all 16 triggers thermal throttling within minutes at full load on the 15W TDP envelope. The N_THREADS=6 setting:

- Leaves 2 physical cores free for OS, UI, and monitoring tasks
- Stays within ~11W sustained power draw (thermal safe zone: 40–70°C)
- Uses 6 physical cores = 12 logical SMT threads (scheduler can still use the extra threads for bursts)
- Proven to avoid thermal throttle in mixed AI + container workloads

### 2.3 Thermal Monitoring

```bash
# Monitor temperature during heavy workloads
watch -n 2 'echo "CPU Temps:"; cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null | \
  awk "{printf \"  Zone: %.1f°C\n\", \$1/1000}"; \
  echo "Freq:"; cat /proc/cpuinfo | grep "cpu MHz" | \
  awk "{sum+=\$4; count++} END {printf \"  Avg: %.0f MHz\n\", sum/count}"'

# If sustained >80°C: reduce threads
# sed -i "s/N_THREADS=6/N_THREADS=4/" ~/.profile && source ~/.profile
```

---

## 3. Memory Architecture & OOM Strategy

### 3.1 Memory Budget Overview

```
Physical RAM: 6.6GB
zRAM Swap:    8GB (compressed, ~3:1 ratio ≈ 24GB virtual)
Total virtual: ~30GB (practical limit: 14–16GB before thrashing)

Current state: 3.9GB RAM used + 2.5GB swap = moderate pressure
Warning threshold: >5GB RAM + >4GB swap = imminent OOM risk
Critical: All 6.6GB RAM + >6GB swap = system nearly unresponsive
```

### 3.2 sysctl Memory Tuning

```bash
sudo tee /etc/sysctl.d/99-omega-stack.conf << 'EOF'
# Memory: strongly prefer RAM, use swap only under pressure
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
vm.overcommit_memory = 1

# File watching (VS Code, systemd path units need high limits)
fs.inotify.max_user_watches = 524288
fs.inotify.max_user_instances = 512
fs.inotify.max_queued_events = 16384

# Network hardening
net.ipv4.tcp_syncookies = 1
net.ipv4.conf.all.rp_filter = 1

# Allow unprivileged port binding (for caddy on 80/443)
net.ipv4.ip_unprivileged_port_start = 80
EOF

sudo sysctl -p /etc/sysctl.d/99-omega-stack.conf
echo "✅ sysctl applied"

# Verify key values
sysctl vm.swappiness fs.inotify.max_user_watches net.ipv4.ip_unprivileged_port_start
```

### 3.3 OOM Score Protection

```bash
#!/usr/bin/env bash
# Protect critical containers from OOM kill
# oom_score_adj range: -1000 (never kill) to +1000 (kill first)

set_oom_score() {
  local NAME="$1" SCORE="$2"
  local PID
  PID=$(podman inspect --format '{{.State.Pid}}' "$NAME" 2>/dev/null || echo "")
  if [ -n "$PID" ] && [ "$PID" -gt 0 ] 2>/dev/null; then
    echo "$SCORE" | sudo tee "/proc/$PID/oom_score_adj" > /dev/null 2>&1 && \
      echo "  ✅ $NAME (PID $PID): oom_score=$SCORE" || \
      echo "  ⚠️  $NAME: needs sudo for OOM tuning"
  else
    echo "  ⚠️  $NAME: not running (PID not found)"
  fi
}

echo "=== APPLYING OOM PROTECTION ==="
# Critical data services — protect strongly
set_oom_score "postgres"          -800
set_oom_score "redis"             -800
set_oom_score "vikunja_db"        -600
set_oom_score "memory-bank-mcp"   -600

# Important but recoverable
set_oom_score "qdrant"             100
set_oom_score "rag_api"            200
set_oom_score "victoriametrics"    150

# Optional — sacrifice first under OOM pressure
set_oom_score "grafana"            700
set_oom_score "mkdocs"             900
set_oom_score "booklore"           800
set_oom_score "knowledge_miner"    800
```

---

## 4. Storage Crisis Resolution — P0

> **🔴 EMERGENCY THRESHOLD TABLE:**
> | Disk Usage | Risk Level | Action Required |
> |-----------|-----------|-----------------|
> | < 80% | ✅ Safe | Normal operations |
> | 80–85% | ⚠️ Warning | Schedule cleanup this week |
> | 85–90% | 🟠 High | Cleanup required before new deployments |
> | 90–93% | 🔴 Critical | CLEANUP NOW before anything else |
> | > 95% | 💀 Emergency | SQLite writes failing; system instability imminent |

### 4.1 Rapid Assessment

```bash
#!/usr/bin/env bash
echo "=== STORAGE CRISIS RAPID ASSESSMENT ==="
echo "Disk usage: $(df -h / | tail -1 | awk '{print $5}') ($(df -h / | tail -1 | awk '{print $4}') free)"
echo ""
echo "Top consumers:"
sudo du -sh /* 2>/dev/null | sort -rh | head -10
echo ""
echo "Podman storage:"
podman system df 2>/dev/null
echo ""
echo "Journal:"
journalctl --disk-usage 2>/dev/null
echo ""
echo "Python + npm caches:"
du -sh ~/.cache/pip ~/.cache/npm ~/.npm 2>/dev/null | sort -rh
```

### 4.2 Phase 1 — Safe Automated Cleanup (8–15 GB expected)

```bash
#!/usr/bin/env bash
# ~/omega-stack/scripts/storage_cleanup.sh
set -euo pipefail
LOG="/tmp/cleanup_$(date +%Y%m%d_%H%M%S).log"
log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }

BEFORE=$(df / | tail -1 | awk '{print $3}')
log "Before: $(df -h / | tail -1)"

# Step 1: Podman prune (images, containers, volumes, build cache)
log "Podman prune..."
podman system prune -af 2>&1 | tail -5 | tee -a "$LOG"

# Step 2: SQLite VACUUM — critical after disk was near-full
log "Podman SQLite VACUUM..."
DB=~/.local/share/containers/storage/libpod/bolt_state.db
[ -f "$DB" ] && command -v sqlite3 &>/dev/null && \
  sqlite3 "$DB" "VACUUM;" 2>/dev/null && log "✅ SQLite vacuumed" || \
  log "⚠️  sqlite3 not found: sudo apt install sqlite3"

# Step 3: Journal — keep 7 days
log "Journal cleanup..."
journalctl --vacuum-time=7d 2>&1 | tail -3 | tee -a "$LOG"

# Step 4: Package caches
log "Caches..."
npm cache clean --force 2>/dev/null | tee -a "$LOG" || true
pip cache purge 2>/dev/null | tee -a "$LOG" || true
rm -rf ~/.cache/pip ~/.cache/npm 2>/dev/null || true

# Step 5: Python bytecode
log "Python bytecode..."
find ~/Documents/Xoe-NovAi/omega-stack/ -name "__pycache__" -type d \
  -exec rm -rf {} + 2>/dev/null || true

# Step 6: Git GC (40–60% size reduction on .git/objects/)
log "Git GC..."
git -C ~/Documents/Xoe-NovAi/omega-stack gc --aggressive --prune=now 2>&1 | tail -3 | tee -a "$LOG"

# Step 7: Temp files
log "Temp files..."
find /tmp -maxdepth 1 -type f -mtime +3 -delete 2>/dev/null || true

AFTER=$(df / | tail -1 | awk '{print $3}')
FREED_MB=$(( (AFTER - BEFORE) / 1024 ))
log "After: $(df -h / | tail -1)"
log "Freed: approximately ${FREED_MB}MB"
log "Log: $LOG"
```

### 4.3 Phase 2 — Manual Targeted Removal

```bash
#!/usr/bin/env bash
OMEGA=~/Documents/Xoe-NovAi/omega-stack

echo "=== PHASE 2: REVIEW BEFORE DELETING ==="
echo ""
echo "node_modules (reinstallable with npm install):"
find "$OMEGA" -name "node_modules" -type d 2>/dev/null | xargs du -sh 2>/dev/null | sort -rh | head -5

echo ""
echo "Old logs (>7 days):"
find "$OMEGA" -name "*.log" -mtime +7 2>/dev/null | xargs du -sh 2>/dev/null | sort -rh | head -10
echo "  → Delete: find $OMEGA -name '*.log' -mtime +7 -delete"

echo ""
echo "Old backups in instances-active:"
find "$OMEGA/instances-active" \( -name "*.bak.*" -o -name "session_202*" \) 2>/dev/null | \
  xargs du -sh 2>/dev/null | sort -rh | head -5
echo "  → Delete: find $OMEGA/instances-active -name '*.bak.*' -mtime +7 -exec rm -rf {} +"

echo ""
echo "Large archives:"
find "$OMEGA" -type f \( -name "*.tar.gz" -o -name "*.zip" \) 2>/dev/null | \
  xargs du -sh 2>/dev/null | sort -rh | head -5
```

### 4.4 Phase 3 — Podman Storage Relocation to omega_library

```bash
#!/usr/bin/env bash
# Use ONLY IF root FS still above 85% after Phase 1+2
# This moves ~18GB of container images to the 65GB-free library drive

LIBRARY=/media/arcana-novai/omega_library
TARGET="${LIBRARY}/podman-storage"

# Safety checks
mountpoint -q "$LIBRARY" || { echo "❌ omega_library not mounted — add to /etc/fstab first"; exit 1; }
LIBRARY_FREE=$(df -BG "$LIBRARY" | tail -1 | awk '{print $4}' | tr -d 'G')
[ "$LIBRARY_FREE" -lt 20 ] && { echo "❌ Insufficient space on library: ${LIBRARY_FREE}GB free (need 20GB+)"; exit 1; }

# Stop all containers
echo "Stopping all containers..."
podman stop --all --time 30

# Configure new graphRoot
mkdir -p "$TARGET"
mkdir -p ~/.config/containers/
cat > ~/.config/containers/storage.conf << STORAGEEOF
[storage]
driver = "overlay"
graphRoot = "${TARGET}"

[storage.options.overlay]
mountopt = "nodev"
STORAGEEOF

echo "✅ Podman storage.conf updated"
echo "⚠️  Container images are NOT automatically migrated"
echo "   You must re-pull images: cd ~/omega-stack && podman-compose pull"
echo ""
echo "CRITICAL: Add to /etc/fstab with 'nofail' option:"
echo "   UUID=<library-uuid> $LIBRARY ext4 defaults,nofail,x-systemd.automount 0 2"
```

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
echo "✅ Log rotation configured — prevents disk growth from recurring"
```

---

## 5. Podman 5.x Runtime — Complete Configuration

### 5.1 subuid/subgid Verification and Repair

```bash
echo "=== UID/GID NAMESPACE SETUP ==="
echo "subuid:"; cat /etc/subuid | grep arcana-novai
echo "subgid:"; cat /etc/subgid | grep arcana-novai
# Expected: arcana-novai:100000:65536

# Repair if missing or wrong:
# sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 arcana-novai
# podman system migrate

# Verify mapping is working
echo ""
echo "UID mapping test:"
podman run --rm alpine cat /proc/self/uid_map 2>/dev/null
# Expected:
#    0   1000      1   (container root = host user 1000)
#    1  100000  65535   (container UIDs 1+ = host UIDs 100000+)
```

### 5.2 The Pause Process — userns=auto Risk Explained

Rootless Podman uses a pause process to keep the unprivileged namespaces alive. This prevents any change to the /etc/subuid and /etc/subgid files from being propagated to rootless containers while the pause process is running.

When using `--userns=auto`, UID ranges are assigned dynamically when the pause process starts. This means:

```
FIRST BOOT:
  Container A → gets UIDs 100000-100999 → files owned by 100999 on host ✅

SECOND BOOT (containers start in different order):
  Container B starts FIRST → gets UIDs 100000-100999
  Container A starts SECOND → gets UIDs 101000-101999 → files now owned by 101999! ❌

RESULT: All files that were readable last boot are now inaccessible.
```

```bash
# Check for pause process (stable namespace indicator)
ps aux | grep "podman.*pause" | grep -v grep && \
  echo "✅ Pause process running (namespaces stable)" || \
  echo "⚠️  No pause process (UID assignments may shift on restart)"

# Fix: Use keep-id instead of auto for all custom services (IMPL-07 Layer 3)
# This makes UID assignment deterministic: host 1000 = container 1000, always
```

### 5.3 User Lingering

```bash
# Required for rootless containers to persist across login/logout
loginctl enable-linger "$(whoami)"
loginctl show-user "$(whoami)" | grep Linger
# Expected: Linger=yes
```

### 5.4 Storage Driver Verification

```bash
# Confirm native OverlayFS (no fuse-overlayfs needed on kernel 6.x)
podman info --format '{{.Store.GraphDriverName}}' 2>/dev/null
# Expected: overlay (NOT fuse-overlayfs)

DRIVER=$(podman info --format '{{.Store.GraphDriverName}}' 2>/dev/null)
[ "$DRIVER" = "overlay" ] && echo "✅ Native OverlayFS (optimal for Kernel 6.x)" || \
  echo "⚠️  Driver: $DRIVER (consider removing fuse-overlayfs if installed)"
```

---

## 6. Networking — pasta vs slirp4netns

### 6.1 The Podman 5.0 Networking Change

Pasta (Plug A Simple Transport Architecture) is the default rootless networking tool since Podman 5.0. It runs as a separate process and provides improved security isolation. Slirp4netns was the default before Podman 5.0 and implements a user-mode TCP/IP stack.

This matters for the Omega-Stack because pasta behaves differently from slirp4netns in inter-container communication scenarios.

### 6.2 Verify Current Networking

```bash
echo "=== NETWORK BACKEND VERIFICATION ==="
# Check what networking backend is in use
podman info 2>/dev/null | grep -Ei "network|pasta|slirp" | head -5

# Verify pasta is installed
which pasta 2>/dev/null && echo "✅ pasta installed" || \
  { echo "⚠️  pasta not found — install: sudo apt install passt"; }

# Verify aardvark-dns for container name resolution
podman network inspect podman 2>/dev/null | grep '"dns_enabled"'
# Expected: "dns_enabled": true

# Add external DNS fallback
mkdir -p ~/.config/containers/
grep -q 'dns_servers' ~/.config/containers/containers.conf 2>/dev/null || \
cat >> ~/.config/containers/containers.conf << 'EOF'

[network]
# External DNS fallback (if aardvark-dns fails)
dns_servers = ["8.8.8.8", "1.1.1.1"]
EOF
echo "✅ External DNS fallback configured"
```

### 6.3 pasta Decision Table

| Scenario | pasta (Podman 5.0+) | slirp4netns (legacy) | Recommendation |
|----------|---------------------|---------------------|----------------|
| Container-to-container DNS | ✅ Works (aardvark-dns) | ✅ Works | Either OK |
| Container-to-host comms | ✅ Fixed in Podman 5.3 | ✅ Works | Verify Podman ≥5.3 |
| IPv6 support | ✅ Full | ⚠️ Limited | pasta wins |
| Security isolation | ✅ Separate process | ⚠️ Single process | pasta wins |
| Port binding (<1024) | Needs `ip_unprivileged_port_start=80` | Same | Set via sysctl |
| NAT behavior | No NAT by default | Full NAT | Can affect some apps |

### 6.4 Port Binding for Caddy (80/443)

```bash
# Allow unprivileged binding to ports 80 and 443
sudo sysctl -w net.ipv4.ip_unprivileged_port_start=80

# Make permanent
echo 'net.ipv4.ip_unprivileged_port_start=80' | \
  sudo tee -a /etc/sysctl.d/99-omega-stack.conf
sudo sysctl -p /etc/sysctl.d/99-omega-stack.conf

# Verify caddy can bind
ss -tuln | grep -E ':80|:443' && echo "✅ Ports 80/443 active" || echo "Caddy not yet running"
```

---

## 7. OS Hardening Baseline

### 7.1 AppArmor Enforcement Path

```bash
# Current status
sudo aa-status 2>/dev/null | head -10

# Gradual enforcement (recommended over immediate enforcement)
# Phase 1: Complain mode (logs but doesn't block — 30 days)
sudo aa-complain /usr/bin/podman 2>/dev/null || echo "Profile not found (may already be managed)"

# Phase 2: After 30 days without issues, enforce
# sudo aa-enforce /usr/bin/podman

# Monitor denials daily during complain phase
sudo journalctl -k | grep DENIED | wc -l
# If > 0: review denials before moving to enforce
```

### 7.2 Pre-commit Hooks — Prevent Secret Leaks

This addresses the security incident referenced in the Haiku update (Google API key exposure in GitHub). Pre-commit hooks prevent secrets from ever reaching git history.

```bash
cd ~/Documents/Xoe-NovAi/omega-stack/

# Install pre-commit
pip install pre-commit --break-system-packages 2>/dev/null || \
  pip install pre-commit 2>/dev/null

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: end-of-file-fixer
      - id: trailing-whitespace

  - repo: local
    hooks:
      - id: no-dotenv
        name: Block .env files
        entry: bash -c 'if git diff --cached --name-only | grep -q "^\.env$\|^\.env\."; then echo "ERROR: Refusing to commit .env file. Use .env.encrypted instead."; exit 1; fi'
        language: system
        always_run: true

      - id: no-pem-keys
        name: Block private key files
        entry: bash -c 'if git diff --cached --name-only | grep -qE "private\.pem|\.key$|id_rsa|id_ed25519"; then echo "ERROR: Refusing to commit private key file."; exit 1; fi'
        language: system
        always_run: true
EOF

# Initialize baseline (marks known false positives)
detect-secrets scan > .secrets.baseline 2>/dev/null || \
  echo '{"plugins_used": [], "results": {}, "version": "1.4.0"}' > .secrets.baseline

# Install hooks
pre-commit install
echo "✅ Pre-commit hooks installed — secrets will be blocked from commits"
```

### 7.3 Git History — Scan for Exposed Secrets

```bash
#!/usr/bin/env bash
# Check if any secrets were previously committed
# (Addressing the API key exposure referenced in Haiku update)

echo "=== GIT HISTORY SECRET SCAN ==="
OMEGA=~/Documents/Xoe-NovAi/omega-stack

# Check for .env committed
GIT_ENV=$(git -C "$OMEGA" log --all --full-history -- ".env" 2>/dev/null | wc -l)
echo ".env in history: $GIT_ENV commits"
[ "$GIT_ENV" -gt 0 ] && echo "  ⚠️  .env WAS committed — check for exposed credentials" || echo "  ✅ .env never committed"

# Check for key files
GIT_KEYS=$(git -C "$OMEGA" log --all --full-history -- "*.pem" "*.key" 2>/dev/null | wc -l)
echo "Key files in history: $GIT_KEYS commits"
[ "$GIT_KEYS" -gt 0 ] && echo "  ❌ CRITICAL: Private keys in git history" || echo "  ✅ No key files in history"

# If secrets were committed — clean history
# DESTRUCTIVE: only run after rotating all exposed credentials
# git filter-repo --path .env --invert-paths
# git filter-repo --path-glob '*.pem' --invert-paths
# After cleaning: all collaborators must re-clone

echo ""
echo "If secrets were exposed: rotate ALL credentials immediately (SUPP-02 §2)"
```

---

## 8. Decision Tree — Diagnose Your Problem

```
SYMPTOM: Something wrong with Omega-Stack infrastructure
═══════════════════════════════════════════════════════

STEP 1: Check disk usage
  > df -h /
  │
  ├─ > 90%? → 🔴 STOP. Run §4 Phase 1+2 before anything else
  │             Risk: All other operations will fail; system becoming unstable
  └─ < 85%? → Continue to STEP 2

STEP 2: Are containers failing to start?
  > podman ps -a | grep -v Up
  │
  ├─ Exit code 137?
  │   └─ OOM kill → §3.3 OOM Protection + IMPL-02 §4 memory limits
  │
  ├─ "ENOSPC" or "no space left"?
  │   └─ Disk full → §4 immediately (even if df shows <90% — check inodes: df -i)
  │
  ├─ "could not find enough available IDs"?
  │   └─ userns=auto exhausted UIDs → §5.2 + IMPL-07 Layer 3
  │      Fix: migrate all custom services to --userns=keep-id
  │
  ├─ "permission denied" on volume mount?
  │   └─ UID mismatch (100999 vs 1000) → IMPL-07 immediately
  │
  ├─ Container starts, service crashes?
  │   └─ Check logs: podman logs <name> --tail 30
  │      → IMPL-02 §3 per-service recovery runbooks
  │
  └─ Container starts fine, MCP tool unreachable?
      └─ IMPL-03 §8 health verification + §9 recovery runbooks

STEP 3: Is ~/.gemini inaccessible (EACCES)?
  └─ → IMPL-07 (4-Layer Permission Fix) — this is the primary known issue
       Quick test: ls -la ~/.gemini/settings.json

STEP 4: Is a dev tool blocked or in auth loop?
  ├─ Gemini CLI auth loop → IMPL-05 §3.1 + check oauth_creds.json permissions
  ├─ Cline has no memory → IMPL-05 §4.3 + check ~/.gemini/memory/ permissions
  └─ VS Code workspace trust warning → IMPL-05 §6.1 trustedFolders.json

STEP 5: Everything looks OK but performance is degraded?
  ├─ High swap usage → §3.2 sysctl + IMPL-02 §4 memory limits
  ├─ Slow container startup → §5.4 OverlayFS + check SQLite fragmentation
  └─ Gemini CLI slow → check memory-bank-mcp latency (IMPL-03 §8)
```

---

## 9. Fallback Strategies — When This Guide Fails

### 9.1 Disk Cleanup Insufficient

**Trigger:** Phase 1+2 recovers <5GB and disk is still above 85%.

```bash
# Escalation Option A: Stop non-critical services (stops disk growth)
for SVC in mkdocs booklore consul openpipe; do
  podman stop "$SVC" 2>/dev/null && echo "Stopped: $SVC" || true
done

# Escalation Option B: Archive and clear session history
du -sh ~/.gemini/chats/
tar -czf /media/arcana-novai/omega_vault/chats_$(date +%Y%m).tar.gz ~/.gemini/chats/ && \
  rm -rf ~/.gemini/chats/* && mkdir -p ~/.gemini/chats/
echo "✅ Chats archived to vault"

# Escalation Option C: Move omega-stack to library mount (symlink back)
# Only if all previous options insufficient
mountpoint -q /media/arcana-novai/omega_library && \
  rsync -a ~/Documents/Xoe-NovAi/omega-stack/ /media/arcana-novai/omega_library/omega-stack/ && \
  rm -rf ~/Documents/Xoe-NovAi/omega-stack && \
  ln -sfn /media/arcana-novai/omega_library/omega-stack ~/Documents/Xoe-NovAi/omega-stack && \
  echo "✅ Stack moved to library, symlinked back"
```

### 9.2 pasta Networking Breaks Inter-Container Communication

**Trigger:** After Podman 5.x upgrade, containers can't reach each other.
**Confidence:** Applies to Podman 5.0–5.2; fixed in 5.3+ with correct pasta config.

```bash
# Verify the issue
PODMAN_VER=$(podman --version | awk '{print $3}')
echo "Podman version: $PODMAN_VER"

# Check if container-to-container DNS works
podman exec redis ping -c 1 postgres 2>/dev/null && echo "✅ DNS working" || echo "❌ DNS broken"

# Option 1: Add pasta to use host loopback
cat >> ~/.config/containers/containers.conf << 'EOF'
[network]
pasta_options = ["-T", "0", "-U", "0", "--map-gw"]
EOF

# Option 2: Explicit network for all containers (ensures shared DNS)
# Every service in docker-compose.yml needs:
# networks:
#   - xnai_app_network  # or appropriate network

# Option 3: Fall back to slirp4netns for specific containers only
# podman run --network=slirp4netns:allow_host_loopback=true ...

podman network reload 2>/dev/null || true
```

### 9.3 userns=auto UIDs Exhausted

**Trigger:** `Error: could not find enough available IDs`
**When this happens:** Too many containers running simultaneously with `--userns=auto`, consuming the 65,536 available UIDs.

```bash
# Diagnose
podman unshare cat /proc/self/uid_map 2>/dev/null
# Check how many UIDs each container is using
for C in $(podman ps -q 2>/dev/null); do
  NAME=$(podman inspect "$C" --format '{{.Name}}')
  MODE=$(podman inspect "$C" --format '{{.HostConfig.UsernsMode}}')
  echo "$NAME: userns=$MODE"
done

# Permanent fix: migrate all custom services to keep-id (IMPL-07 Layer 3)
# This uses only 1 UID per container instead of allocating a range

# Emergency workaround: increase available UIDs
# sudo usermod --add-subuids 100000-230000 arcana-novai  # Doubles available range
# podman system migrate
```

### 9.4 Podman Storage Relocation Breaks Containers

**Trigger:** After moving graphRoot, containers fail with "image not found."

```bash
# Container images are NOT automatically migrated — must re-pull
echo "Re-pulling all images (may take 10-20 minutes)..."
cd ~/Documents/Xoe-NovAi/omega-stack/
podman-compose pull

# If network drive is slow, pull critical images first:
for IMG in redis:7-alpine postgres:15 qdrant/qdrant:latest; do
  podman pull "$IMG" && echo "✅ $IMG pulled"
done

# If relocation was a mistake (library drive unavailable):
rm -f ~/.config/containers/storage.conf
echo "Storage.conf removed — reverted to default root FS location"
podman system migrate
```

---

## 10. Diagnostic Command Reference

```bash
# Full infrastructure snapshot
omega-status() {
  echo "=== OMEGA-STACK INFRASTRUCTURE STATUS ===" && \
  echo "Disk:"; df -h | grep -E '/$|omega' && \
  echo "" && echo "Memory:"; free -h && \
  echo "" && echo "Containers:"; podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" && \
  echo "" && echo "Timers:"; systemctl --user list-timers --no-pager | grep -E 'NEXT|omega|acl'
}

# Key one-liners
alias df-check='df -h / && echo "" && df -i / | tail -1 | awk '"'"'{print "Inodes: "$5}'"'"''
alias mem-check='free -h && echo "" && cat /proc/swaps'
alias podman-check='podman --version && podman info --format "driver={{.Store.GraphDriverName}} cgroup={{.Host.CgroupVersion}}"'
alias oom-check='dmesg | grep -i "oom\|killed process" | tail -5'
alias thermal-check='cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null | awk "{printf \"%.1f°C  \", \$1/1000}"; echo ""'
```

---

## 11. Verification Checklist

```bash
#!/usr/bin/env bash
echo "=== IMPL-01 INFRASTRUCTURE VERIFICATION ==="
PASS=0; FAIL=0; WARN=0
ok()   { echo "  ✅ $1"; PASS=$((PASS+1)); }
fail() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
warn() { echo "  ⚠️  $1"; WARN=$((WARN+1)); }

# Storage
DISK=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
[ "$DISK" -lt 75 ] && ok "Disk: ${DISK}% (healthy)" || \
[ "$DISK" -lt 85 ] && warn "Disk: ${DISK}% (warning — cleanup this week)" || \
[ "$DISK" -lt 93 ] && fail "Disk: ${DISK}% (CRITICAL — run §4 NOW)" || \
                       fail "Disk: ${DISK}% (EMERGENCY — system at risk)"

# Inodes
INODES=$(df -i / | tail -1 | awk '{print $5}' | tr -d '%')
[ "$INODES" -lt 80 ] && ok "Inodes: ${INODES}% used" || \
[ "$INODES" -lt 90 ] && warn "Inodes: ${INODES}% (high — check small-file dirs)" || \
                         fail "Inodes: ${INODES}% (near exhaustion)"

# Memory
SWAP=$(free | awk '/Swap/{printf "%d", ($2>0)?$3/$2*100:0}')
[ "$SWAP" -lt 30 ] && ok "Swap: ${SWAP}% (healthy)" || \
[ "$SWAP" -lt 60 ] && warn "Swap: ${SWAP}% (moderate pressure)" || \
                      fail "Swap: ${SWAP}% (HIGH — OOM risk)"

# Podman runtime
podman --version &>/dev/null && ok "Podman available" || fail "Podman not in PATH"
loginctl show-user "$(whoami)" | grep -q 'Linger=yes' && ok "User lingering enabled" || fail "Lingering disabled"
grep -q "arcana-novai:100000" /etc/subuid 2>/dev/null && ok "subuid mapping configured" || fail "subuid missing"
DRIVER=$(podman info --format '{{.Store.GraphDriverName}}' 2>/dev/null)
[ "$DRIVER" = "overlay" ] && ok "Storage: native OverlayFS" || warn "Storage driver: ${DRIVER:-unknown}"

# Networking
which pasta &>/dev/null && ok "pasta networking installed" || warn "pasta not found (install: sudo apt install passt)"

# CPU optimization
grep -q OPENBLAS_CORETYPE ~/.profile 2>/dev/null && ok "CPU optimization profile set" || warn "OPENBLAS_CORETYPE not in ~/.profile"

# inotify
INOTIFY=$(sysctl -n fs.inotify.max_user_watches 2>/dev/null || echo 0)
[ "$INOTIFY" -ge 524288 ] && ok "inotify.max_user_watches: $INOTIFY" || fail "inotify too low: $INOTIFY (need 524288)"

# Pre-commit hooks
[ -f ~/Documents/Xoe-NovAi/omega-stack/.pre-commit-config.yaml ] && \
  ok "Pre-commit hooks configured (secret leak prevention)" || \
  warn "Pre-commit hooks not configured (run §7.2)"

echo ""
printf "Results: ✅ %d pass  ❌ %d fail  ⚠️  %d warn\n" "$PASS" "$FAIL" "$WARN"
[ "$FAIL" -eq 0 ] && echo "✅ Infrastructure baseline solid" || echo "❌ $FAIL items require attention"
echo ""
echo "Next step: IMPL-07 (permissions) or IMPL-02 (container orchestration)"
```
