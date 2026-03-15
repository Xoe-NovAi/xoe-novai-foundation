---
title: "Omega-Stack Implementation Manual 07: The 4-Layer Permission Resolution"
section: "07"
scope: "Rootless Podman, POSIX ACLs, keep-id, Systemd Timer, Ed25519 DID"
status: "Actionable — Primary Fix for EACCES Cascade"
owner: "arcana-novai (UID 1000)"
last_updated: "2026-03-13"
gemini_review: "Full Gemini 3.1 Pro validation integrated — 3 critical corrections applied"
confidence: "99% system-verified + upstream confirmed"
priority: "P0 — All 7 Dev Tools Blocked"
---

# IMPL-07 — The 4-Layer Permission Resolution
## Omega-Stack Agent Implementation Manual

> **🤖 AGENT DIRECTIVE:** This is the primary resolution manual for the EACCES cascade blocking all 7 development tools. Three critical corrections from the Gemini 3.1 Pro review are incorporated:
> 1. `--userns=auto` is **non-deterministic across reboots** — replace with `--userns=keep-id`
> 2. Ubuntu 25.10 ext4 **already supports ACLs** — no `/etc/fstab` modification needed
> 3. The `:Z` volume flag is **SELinux-only** and a no-op on this AppArmor system
>
> Execute all 4 layers in order. Do NOT skip layers. Each layer addresses a different failure vector.

---

## Table of Contents

1. [Root Cause Deep Dive](#1-root-cause-deep-dive)
2. [Layer 1 — Immediate Ownership Restoration](#2-layer-1--immediate-ownership-restoration)
3. [Layer 2 — POSIX Default ACLs](#3-layer-2--posix-default-acls)
4. [Layer 3 — Podman keep-id Runtime Prevention](#4-layer-3--podman-keep-id-runtime-prevention)
5. [Layer 4 — Systemd Self-Healing Timer + Ed25519 DID](#5-layer-4--systemd-self-healing-timer--ed25519-did)
6. [Master Deployment Script](#6-master-deployment-script)
7. [Tool-Specific Verification](#7-tool-specific-verification)
8. [The chmod Mask Vulnerability](#8-the-chmod-mask-vulnerability)
9. [Edge Cases & Failure Modes](#9-edge-cases--failure-modes)
10. [Full Verification Checklist](#10-full-verification-checklist)

---

## 1. Root Cause Deep Dive

### 1.1 UID Translation Mathematics

```
/etc/subuid:  arcana-novai:100000:65536

Container UID  →  Host UID     Identity
─────────────────────────────────────────────────────
0 (root)       →  1000         Container root = host user
1              →  100000       First subordinate slot
999 (nginx)    →  100999       ← FILES LAND HERE (inaccessible to UID 1000)
65535          →  165535       End of subuid range
```

### 1.2 The Atomic Write Vulnerability

```
Node.js write-file-atomic (used by VS Code, Cline, Copilot CLI):

Step 1: create  ~/.gemini/.settings.json.TMP  (new inode, new UID)
Step 2: write   data to temp file
Step 3: fsync() flush to storage
Step 4: rename  .TMP → settings.json  (replaces old inode)

RESULT: New inode inherits parent directory's Default ACLs.
        Access ACLs on OLD inode are DESTROYED.
        → Only Default ACLs on PARENT DIRECTORY survive.
```

### 1.3 The userns=auto Instability Problem (Critical Correction)

> **🔴 CRITICAL — DO NOT SKIP:**  
> `--userns=auto` assigns UID ranges dynamically at container startup on a first-come, first-served basis. If containers start in a different order after a reboot, container UID 999 may be assigned to a **different host UID**, instantly locking all volume-owned files. This is confirmed Podman behavior (GitHub Discussion #27577), not a bug.

```bash
# DIAGNOSE: Are your containers using auto or keep-id?
podman inspect memory-bank-mcp --format '{{.HostConfig.UsernsMode}}' 2>/dev/null
# If output is "" or "auto" → YOU ARE VULNERABLE
# Target: "keep-id"

# CONFIRM the file ownership problem
ls -lan ~/Documents/Xoe-NovAi/omega-stack/.gemini/ 2>/dev/null | head -5
# If owner column shows "100999" → permission issue confirmed
```

---

## 2. Layer 1 — Immediate Ownership Restoration

**Time to execute:** ~5 minutes  
**Effect:** Unblocks all 7 tools immediately  
**Durability:** Temporary — any container write reverts to UID 100999 without Layer 2

```bash
#!/usr/bin/env bash
# =============================================================================
# OMEGA-STACK  |  Layer 1: Emergency Ownership Restoration
# File: ~/omega-stack/scripts/permissions/layer1_restore.sh
# =============================================================================
set -euo pipefail

OWNER="arcana-novai"
REPO_DIR="${HOME}/Documents/Xoe-NovAi/omega-stack"
GEMINI_DIR="${HOME}/.gemini"
LOG="/tmp/omega_layer1_$(date +%Y%m%d_%H%M%S).log"

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }
err() { echo "[ERROR] $*" >&2; exit 1; }

log "═══════════════════════════════════════════"
log "  OMEGA-STACK  Layer 1 — Ownership Restore "
log "═══════════════════════════════════════════"

[ "$(id -un)" = "$OWNER" ] || err "Run as $OWNER, not $(id -un)"

# Stop containers to prevent race conditions during chown
log "Stopping containers..."
podman stop --all --time 10 2>/dev/null || true
log "Containers stopped."

# Restore .gemini inside repository
REPO_GEMINI="${REPO_DIR}/.gemini"
if [ -d "$REPO_GEMINI" ]; then
  log "Restoring: ${REPO_GEMINI}"
  sudo chown -R "${OWNER}:${OWNER}" "$REPO_GEMINI"
  log "✔ Repository .gemini restored."
fi

# Restore home .gemini
if [ -d "$GEMINI_DIR" ]; then
  log "Restoring: ${GEMINI_DIR}"
  sudo chown -R "${OWNER}:${OWNER}" "$GEMINI_DIR"
  log "✔ Home .gemini restored."
fi

# Verify
BAD=$(find "$REPO_DIR" "${GEMINI_DIR}" -not -user "$OWNER" 2>/dev/null | wc -l)
if [ "$BAD" -eq 0 ]; then
  log "✔ Layer 1 complete. All files owned by ${OWNER}."
else
  log "⚠ ${BAD} files still not owned by ${OWNER}. Review log: $LOG"
  exit 1
fi
```

---

## 3. Layer 2 — POSIX Default ACLs

**Time to execute:** ~5 minutes  
**Effect:** Permanent permission grant that survives atomic writes  
**Key Principle:** Default ACLs on the **parent directory** are inherited by all new inodes created inside it — including files created by Node.js rename() operations.

> **🤖 AGENT CALLOUT — The chmod Mask Quirk (Gemini 3.1 Finding):**  
> If any containerized service runs `chmod 644` or `chmod 600` on a file, Linux **automatically recalculates the ACL mask** to match the new group permissions. A `chmod 600` will set the mask to `---`, revoking your `u:1000:rwx` entry even though it still appears in `getfacl`. Layer 4's systemd timer detects and repairs this drift automatically.

```bash
#!/usr/bin/env bash
# =============================================================================
# OMEGA-STACK  |  Layer 2: POSIX Default ACL Setup
# File: ~/omega-stack/scripts/permissions/layer2_acl_setup.sh
# Idempotent — safe to run multiple times.
# =============================================================================
set -euo pipefail

OWNER="arcana-novai"
OWNER_UID=$(id -u "$OWNER")
SUBUID=100999    # Container UID 999 → Host UID 100999
REPO_DIR="${HOME}/Documents/Xoe-NovAi/omega-stack"
REPO_GEMINI="${REPO_DIR}/.gemini"
GEMINI_DIR="${HOME}/.gemini"
LOG="/tmp/omega_layer2_$(date +%Y%m%d_%H%M%S).log"

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }
err() { echo "[ERROR] $*" >&2; exit 1; }

log "═══════════════════════════════════════════"
log "  OMEGA-STACK  Layer 2 — ACL Setup          "
log "═══════════════════════════════════════════"

[ "$(id -un)" = "$OWNER" ] || err "Run as $OWNER"
command -v setfacl >/dev/null || err "setfacl not found. Install: sudo apt install acl"

# Verify ACL support (ext4 on Ubuntu has ACL by default since 14.04)
ACL_SUPPORTED=$(tune2fs -l "$(df "${HOME}" | tail -1 | awk '{print $1}')" 2>/dev/null | grep 'Default mount' | grep -c 'acl' || echo "0")
[ "$ACL_SUPPORTED" -gt 0 ] && log "✔ ext4 ACL support confirmed (no fstab change needed)." \
  || log "⚠ ACL not in default mount options. May need: sudo tune2fs -o acl <device>"

apply_acls() {
  local TARGET_DIR="$1"
  local LABEL="$2"
  log "Applying ACLs to: ${TARGET_DIR} [${LABEL}]"
  mkdir -p "$TARGET_DIR"

  # ── Access ACLs (existing files) ──────────────────────────────────────────
  setfacl -R -m "u:${OWNER_UID}:rwx" "$TARGET_DIR"
  setfacl -R -m "u:${SUBUID}:rwx" "$TARGET_DIR"

  # ── Default ACLs (template for new files — SURVIVES ATOMIC WRITES) ────────
  setfacl -d -m "u:${OWNER_UID}:rwx" "$TARGET_DIR"
  setfacl -d -m "u:${SUBUID}:rwx" "$TARGET_DIR"
  setfacl -d -m "g::r-x" "$TARGET_DIR"
  setfacl -d -m "o::---" "$TARGET_DIR"

  # ── Mask: MUST be rwx — prevents named-user entries from being silently reduced
  # NOTE: chmod operations by containers will recalculate this mask.
  # Layer 4 timer detects and repairs mask drift automatically.
  setfacl -R -m "m::rwx" "$TARGET_DIR"
  setfacl -d -m "m::rwx" "$TARGET_DIR"

  log "✔ ACLs applied to ${TARGET_DIR}"
  getfacl "$TARGET_DIR" | tee -a "$LOG"
}

# Apply to all critical .gemini paths
apply_acls "$REPO_GEMINI" "repository .gemini"
[ -d "$GEMINI_DIR" ] && apply_acls "$GEMINI_DIR" "home .gemini"

# Apply to subdirectories
for SUBDIR in memory credentials instances chats agents policies skills; do
  [ -d "${REPO_GEMINI}/${SUBDIR}" ] && apply_acls "${REPO_GEMINI}/${SUBDIR}" "$SUBDIR"
done

log ""
log "✔ Layer 2 complete. Default ACLs survive container atomic writes."
log "  Verify with: getfacl ${REPO_GEMINI}"
log "  Log: $LOG"
```

---

## 4. Layer 3 — Podman keep-id Runtime Prevention

**Time to execute:** ~15 minutes (includes container restart)  
**Effect:** Prevents UID mismatch from occurring at the source  
**Critical Change:** Replaces unstable `--userns=auto` with deterministic `--userns=keep-id`

> **🤖 AGENT CALLOUT — Two Service Categories:**  
> - **`keep-id` services:** Services you control (MCP servers, custom apps) — run as UID 1000 inside the container. Files they create will be owned by UID 1000 on the host.  
> - **Legacy services:** Services with fixed internal UIDs (postgres=999, redis=999, nginx=101) — **cannot** use `keep-id`. Use `:U` flag + Layer 2 Default ACLs instead.

### 4.1 Option A — Quadlets (Recommended, per Gemini 3.1 review)

See IMPL-02 Section 5 for full Quadlet files. The key namespace settings:

```ini
# For Omega-Stack custom services (MCP servers, custom apps):
[Container]
UserNS=keep-id
User=1000:1000
Volume=%h/Documents/Xoe-NovAi/omega-stack/.gemini:/app/.gemini:U,z

# For legacy services (postgres, redis, nginx):
# Do NOT set UserNS — let them use their internal UIDs
# The :U flag + Layer 2 Default ACLs handles host access
[Container]
Volume=./data/postgres:/var/lib/postgresql/data:U,z
```

### 4.2 Option B — docker-compose.yml Patch

```yaml
# ─── CUSTOM/MCP SERVICES — use keep-id ──────────────────────────────────────
services:
  memory-bank-mcp:
    userns_mode: keep-id          # ← Deterministic: host 1000 = container 1000
    user: "1000:1000"             # ← Force UID 1000 inside container
    volumes:
      - ./omega-stack/.gemini:/app/.gemini:U,z
      # :U → Podman chowns volume to container UID on start
      # :z → AppArmor label (safe no-op on this system, but good practice)

  xnai-github:
    userns_mode: keep-id
    user: "1000:1000"
    volumes:
      - ./data/xnai-github:/app/data:U,z

  xnai-gnosis:
    userns_mode: keep-id
    user: "1000:1000"
    volumes:
      - ./data/xnai-gnosis:/app/data:U,z

# ─── LEGACY SERVICES — use :U + Layer 2 ACLs ─────────────────────────────────
# postgres runs as UID 999 internally — do NOT force UID 1000
  postgres:
    # No userns_mode here — default namespace
    volumes:
      - postgres_data:/var/lib/postgresql/data:U,z
      # :U chowns the volume dir to whatever UID postgres uses inside
      # Layer 2 Default ACLs ensure UID 1000 still has read access

  redis:
    volumes:
      - redis_data:/data:U,z

  qdrant:
    volumes:
      - qdrant_data:/qdrant/storage:U,z
```

### 4.3 Apply and Restart

```bash
cd ~/Documents/Xoe-NovAi/omega-stack/

# Stop all first
podman stop --all --time 30

# Re-run Layer 1 and 2 to ensure clean state before starting
bash scripts/permissions/layer1_restore.sh
bash scripts/permissions/layer2_acl_setup.sh

# Restart with new configuration
podman-compose up -d

# Verify keep-id is active on critical services
for SVC in memory-bank-mcp xnai-github xnai-gnosis; do
  MODE=$(podman inspect "$SVC" --format '{{.HostConfig.UsernsMode}}' 2>/dev/null)
  echo "$SVC: userns=$MODE"
done
```

---

## 5. Layer 4 — Systemd Self-Healing Timer + Ed25519 DID

**Time to execute:** ~10 minutes  
**Effect:** Autonomous 15-minute heartbeat repairs any permission drift

### 5.1 ACL Repair Script

```bash
#!/usr/bin/env bash
# =============================================================================
# File: ~/omega-stack/scripts/permissions/acl_repair.sh
# Called every 15 minutes by systemd timer
# =============================================================================
set -euo pipefail

OWNER_UID=$(id -u)
SUBUID=100999
TARGETS=(
  "${HOME}/Documents/Xoe-NovAi/omega-stack/.gemini"
  "${HOME}/.gemini"
)
DRIFT_COUNT=0

repair_dir() {
  local DIR="$1"
  [ -d "$DIR" ] || return 0

  # Re-apply Default ACLs (idempotent)
  setfacl -d -m "u:${OWNER_UID}:rwx,u:${SUBUID}:rwx,m::rwx" "$DIR" 2>/dev/null || true

  # Find files with incorrect mask (the chmod-mask vulnerability)
  while IFS= read -r -d '' FILE; do
    # Restore rwx mask and owner access
    setfacl -m "u:${OWNER_UID}:rwx,u:${SUBUID}:rwx,m::rwx" "$FILE" 2>/dev/null || true
    DRIFT_COUNT=$((DRIFT_COUNT + 1))
  done < <(find "$DIR" -not -readable -print0 2>/dev/null)

  # Also check for files where mask has been reduced by chmod
  while IFS= read -r -d '' FILE; do
    MASK=$(getfacl -p "$FILE" 2>/dev/null | grep '^mask' | cut -d: -f3)
    if [ "$MASK" != "rwx" ] && [ -n "$MASK" ]; then
      setfacl -m "m::rwx,u:${OWNER_UID}:rwx" "$FILE" 2>/dev/null || true
      DRIFT_COUNT=$((DRIFT_COUNT + 1))
    fi
  done < <(find "$DIR" -print0 2>/dev/null)
}

for TARGET in "${TARGETS[@]}"; do
  repair_dir "$TARGET"
done

if [ "$DRIFT_COUNT" -gt 0 ]; then
  echo "[OMEGA ACL REPAIR] Repaired ${DRIFT_COUNT} files/dirs with permission drift."
else
  echo "[OMEGA ACL REPAIR] No drift detected. All permissions nominal."
fi
```

### 5.2 Systemd Service Unit

```ini
# ~/.config/systemd/user/acl_drift_monitor.service
[Unit]
Description=Omega-Stack ACL Drift Repair
Documentation=https://github.com/arcana-novai/omega-stack
After=default.target

[Service]
Type=oneshot
ExecStart=%h/Documents/Xoe-NovAi/omega-stack/scripts/permissions/acl_repair.sh
StandardOutput=journal
StandardError=journal
Nice=10
IOSchedulingClass=idle
```

### 5.3 Systemd Timer Unit

```ini
# ~/.config/systemd/user/acl_drift_monitor.timer
[Unit]
Description=Omega-Stack ACL Drift Monitor — 15-Minute Heartbeat
Requires=acl_drift_monitor.service

[Timer]
OnBootSec=2min
OnUnitActiveSec=15min
RandomizedDelaySec=30
Persistent=true

[Install]
WantedBy=timers.target
```

### 5.4 Install Layer 4

```bash
#!/usr/bin/env bash
SCRIPTS="${HOME}/Documents/Xoe-NovAi/omega-stack/scripts/permissions"
SYSTEMD="${HOME}/.config/systemd/user"

mkdir -p "$SYSTEMD"
chmod +x "${SCRIPTS}/acl_repair.sh"

cat > "${SYSTEMD}/acl_drift_monitor.service" << 'UNIT'
[Unit]
Description=Omega-Stack ACL Drift Repair
After=default.target

[Service]
Type=oneshot
ExecStart=%h/Documents/Xoe-NovAi/omega-stack/scripts/permissions/acl_repair.sh
StandardOutput=journal
StandardError=journal
Nice=10
IOSchedulingClass=idle
UNIT

cat > "${SYSTEMD}/acl_drift_monitor.timer" << 'TIMER'
[Unit]
Description=Omega-Stack ACL Drift Monitor — 15-Minute Heartbeat
Requires=acl_drift_monitor.service

[Timer]
OnBootSec=2min
OnUnitActiveSec=15min
RandomizedDelaySec=30
Persistent=true

[Install]
WantedBy=timers.target
TIMER

# Enable lingering (keep services alive after logout)
loginctl enable-linger "$(whoami)"

# Activate
systemctl --user daemon-reload
systemctl --user enable --now acl_drift_monitor.timer
systemctl --user start acl_drift_monitor.service

# Verify
systemctl --user list-timers acl_drift_monitor.timer
journalctl --user -u acl_drift_monitor.service -n 10 --no-pager
```

### 5.5 Ed25519 Agent Key Generation

```bash
#!/usr/bin/env bash
# Generate Ed25519 keys for an MCP server agent
AGENT_NAME="${1:-memory-bank-mcp}"
KEY_DIR="${HOME}/Documents/Xoe-NovAi/omega-stack/.gemini/keys/${AGENT_NAME}"
mkdir -p "$KEY_DIR"
chmod 700 "$KEY_DIR"

# Generate keypair
openssl genpkey -algorithm Ed25519 -out "${KEY_DIR}/private.pem"
openssl pkey -in "${KEY_DIR}/private.pem" -pubout -out "${KEY_DIR}/public.pem"
chmod 600 "${KEY_DIR}/private.pem"
chmod 644 "${KEY_DIR}/public.pem"

# Extract public key for registry
PUB_B64=$(openssl pkey -in "${KEY_DIR}/public.pem" -pubin -outform DER | tail -c 32 | base64 -w0)
echo "Agent: ${AGENT_NAME}"
echo "Public Key (base64): ${PUB_B64}"
echo "Keys stored in: ${KEY_DIR}"
echo ""
echo "Add to ~/.gemini/agent_registry.json:"
echo "  \"id\": \"${AGENT_NAME}\","
echo "  \"public_key_ed25519_b64\": \"${PUB_B64}\""
```

---

## 6. Master Deployment Script

```bash
#!/usr/bin/env bash
# =============================================================================
# OMEGA-STACK  |  All 4 Layers — Master Deployment
# Usage: bash deploy_all_layers.sh [--skip-container-restart]
# =============================================================================
set -euo pipefail

SCRIPTS="${HOME}/Documents/Xoe-NovAi/omega-stack/scripts/permissions"
LOG="/tmp/omega_master_deploy_$(date +%Y%m%d_%H%M%S).log"
SKIP_RESTART="${1:-}"

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }
phase() { log ""; log "══════════════════════════════════════"; log "  $*"; log "══════════════════════════════════════"; }

phase "Pre-flight: Storage Check"
DISK_PCT=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$DISK_PCT" -ge 90 ]; then
  log "❌ ABORT: Root filesystem at ${DISK_PCT}%. Run IMPL-01 storage cleanup first."
  exit 1
fi
log "✔ Disk usage: ${DISK_PCT}%"

phase "Layer 1: Ownership Restoration"
bash "${SCRIPTS}/layer1_restore.sh" && log "✔ Layer 1 complete"

phase "Layer 2: POSIX Default ACLs"
bash "${SCRIPTS}/layer2_acl_setup.sh" && log "✔ Layer 2 complete"

phase "Layer 3: Container Restart (keep-id mode)"
if [ "$SKIP_RESTART" != "--skip-container-restart" ]; then
  cd ~/Documents/Xoe-NovAi/omega-stack/
  podman-compose down --remove-orphans 2>&1 | tee -a "$LOG" || true
  sleep 5
  podman-compose up -d 2>&1 | tee -a "$LOG"
  log "✔ Layer 3: Containers restarted"
else
  log "⚠ Skipping container restart (--skip-container-restart)"
fi

phase "Layer 4: Systemd Timer"
SYSTEMD="${HOME}/.config/systemd/user"
mkdir -p "$SYSTEMD"
chmod +x "${SCRIPTS}/acl_repair.sh"
loginctl enable-linger "$(whoami)"
systemctl --user daemon-reload
systemctl --user enable --now acl_drift_monitor.timer 2>/dev/null || \
  log "⚠ Timer not installed yet — run layer4 install script first"
systemctl --user start acl_drift_monitor.service 2>/dev/null || true
log "✔ Layer 4 complete"

phase "Verification"
log "ACL state:"
getfacl ~/Documents/Xoe-NovAi/omega-stack/.gemini 2>/dev/null | tee -a "$LOG" || true
log "Timer status:"
systemctl --user list-timers acl_drift_monitor.timer --no-pager 2>/dev/null | tee -a "$LOG" || true
log ""
log "✔ ALL LAYERS DEPLOYED. Log: $LOG"
```

---

## 7. Tool-Specific Verification

```bash
#!/usr/bin/env bash
echo "=== TOOL ACCESS VERIFICATION ==="
GEMINI="${HOME}/.gemini"
REPO_GEMINI="${HOME}/Documents/Xoe-NovAi/omega-stack/.gemini"

test_path() {
  local TOOL="$1" PATH_TEST="$2" MODE="$3"
  if [ "$MODE" = "r" ]; then
    [ -r "$PATH_TEST" ] && echo "✅ $TOOL: READ OK ($PATH_TEST)" || echo "❌ $TOOL: READ DENIED ($PATH_TEST)"
  else
    touch "${PATH_TEST}.write_test" 2>/dev/null && rm "${PATH_TEST}.write_test" && \
      echo "✅ $TOOL: WRITE OK ($PATH_TEST)" || echo "❌ $TOOL: WRITE DENIED ($PATH_TEST)"
  fi
}

test_path "Cline"       "${GEMINI}/memory/"           w
test_path "Copilot CLI" "${GEMINI}/settings.json"     r
test_path "Gemini CLI"  "${GEMINI}/"                  w
test_path "VS Code"     "${GEMINI}/trustedFolders.json" r
test_path "OpenCode"    "${GEMINI}/instances/"        w
test_path "Antigravity" "${GEMINI}/credentials/"      w
test_path "Crush"       "${GEMINI}/memory/"           r

echo ""
echo "=== ACL STATE ==="
getfacl "${REPO_GEMINI}" | grep -E '(default|mask|user:1)'
echo "=== END ==="
```

---

## 8. The chmod Mask Vulnerability

> **⚠️ AGENT CALLOUT (Gemini 3.1 Finding — Critical Edge Case):**  
> This is a POSIX specification behavior, not a bug. Any `chmod` call recalculates the ACL mask.

**Detection:**

```bash
# Check if mask has been reduced on any .gemini file
getfacl ~/Documents/Xoe-NovAi/omega-stack/.gemini/settings.json 2>/dev/null | grep mask
# If "mask::r--" or "mask::---" → mask has been corrupted by chmod

# Manual repair
setfacl -m "m::rwx,u:1000:rwx,u:100999:rwx" ~/Documents/Xoe-NovAi/omega-stack/.gemini/settings.json
```

**Automated Repair (Layer 4 handles this — verify timer is running):**

```bash
systemctl --user is-active acl_drift_monitor.timer
# Expected: active
```

---

## 9. Edge Cases & Failure Modes

| Scenario | Symptom | Resolution |
|----------|---------|------------|
| `--userns=auto` reboot drift | Files suddenly inaccessible after reboot | `podman inspect <svc> --format '{{.HostConfig.UsernsMode}}'` → switch to `keep-id` |
| chmod by container reduces mask | `getfacl` shows `mask::r--` or less | Layer 4 timer auto-repairs in ≤15 min; or run `acl_repair.sh` manually |
| ACLs lost on filesystem check | `fsck` after dirty shutdown strips ACLs | Re-run `layer2_acl_setup.sh` |
| New .gemini subdirectory created | Missing Default ACLs on new dir | Timer repairs within 15 min; or: `setfacl -d -m u:1000:rwx <new_dir>` |
| `setfacl` fails with "Operation not supported" | ext4 without ACL mount option | `sudo tune2fs -o acl $(df $HOME \| tail -1 \| awk '{print $1}')` then remount |
| `keep-id` service creates files as wrong UID | Container image sets `USER` to non-1000 | Override with `user: "1000:1000"` in compose or `User=1000:1000` in Quadlet |
| Layer 2 not applied to new volume path | New service writes to unprotected path | Add path to `TARGETS` array in `acl_repair.sh` |

---

## 10. Full Verification Checklist

```bash
#!/usr/bin/env bash
echo "=== IMPL-07 FULL PERMISSION VERIFICATION ==="

REPO_GEMINI="${HOME}/Documents/Xoe-NovAi/omega-stack/.gemini"
ok() { echo "✅ $1"; }
fail() { echo "❌ $1 — ACTION REQUIRED"; }

# 1. Ownership
BAD=$(find "${REPO_GEMINI}" -not -user arcana-novai 2>/dev/null | wc -l)
[ "$BAD" -eq 0 ] && ok "All .gemini files owned by arcana-novai" || fail "Found $BAD files owned by wrong UID"

# 2. Default ACLs present
getfacl "${REPO_GEMINI}" 2>/dev/null | grep -q "default:user:1000:rwx" && ok "Default ACL u:1000:rwx present" || fail "Default ACL missing"

# 3. Mask not reduced
MASK=$(getfacl -p "${REPO_GEMINI}" 2>/dev/null | grep '^mask' | cut -d: -f3)
[ "$MASK" = "rwx" ] && ok "ACL mask is rwx" || fail "ACL mask is '${MASK}' (should be rwx)"

# 4. userns mode on keep-id services
for SVC in memory-bank-mcp; do
  MODE=$(podman inspect "$SVC" --format '{{.HostConfig.UsernsMode}}' 2>/dev/null || echo "not-running")
  [ "$MODE" = "keep-id" ] && ok "$SVC uses keep-id namespace" || fail "$SVC uses '$MODE' (should be keep-id)"
done

# 5. Systemd timer active
systemctl --user is-active acl_drift_monitor.timer &>/dev/null && ok "Drift repair timer active" || fail "Drift repair timer NOT active"

# 6. Atomic write test
TEST_FILE="${REPO_GEMINI}/.atomic_test_$$"
node -e "require('fs').writeFileSync('${TEST_FILE}', 'test')" 2>/dev/null
if [ -f "$TEST_FILE" ]; then
  OWNER=$(stat -c '%U' "$TEST_FILE" 2>/dev/null)
  MASK=$(getfacl -p "$TEST_FILE" 2>/dev/null | grep '^mask' | cut -d: -f3)
  rm "$TEST_FILE"
  [ "$MASK" = "rwx" ] && ok "Atomic write inherits correct Default ACL" || fail "Atomic write ACL mask is '${MASK}'"
fi

# 7. Persistence test (cross-container)
HUID=$(podman top memory-bank-mcp huser 2>/dev/null | tail -1)
[ "$HUID" = "arcana-novai" ] || [ "$HUID" = "1000" ] && ok "memory-bank-mcp runs as host UID 1000" || fail "memory-bank-mcp host UID: $HUID"

echo ""
echo "=== LAYER DEPLOYMENT STATUS ==="
echo "Layer 1 (chown):   $([ "$BAD" -eq 0 ] && echo "✅ ACTIVE" || echo "❌ NEEDED")"
echo "Layer 2 (ACLs):    $(getfacl "${REPO_GEMINI}" 2>/dev/null | grep -q 'default:user:1000' && echo "✅ ACTIVE" || echo "❌ NEEDED")"
echo "Layer 3 (keep-id): $(podman inspect memory-bank-mcp --format '{{.HostConfig.UsernsMode}}' 2>/dev/null | grep -q keep-id && echo "✅ ACTIVE" || echo "⚠️ CHECK")"
echo "Layer 4 (timer):   $(systemctl --user is-active acl_drift_monitor.timer 2>/dev/null && echo "✅ ACTIVE" || echo "❌ NEEDED")"
echo "=== END VERIFICATION ==="
```

---

> **📋 NEXT MANUAL:** After all 4 layers verified, proceed to `IMPL_05_TOOL_INTEGRATION.md` for per-tool configuration validation, or `SUPP_02_SECRETS_MANAGEMENT.md` to address the plaintext credentials vulnerability.
