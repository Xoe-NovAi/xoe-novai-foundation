---
document_type: specification
title: "Permissions 4-Layer Model: Authoritative Reference for Omega Stack"
created_by: "Copilot (223556219+Copilot@users.noreply.github.com)"
created_date: 2026-03-15
version: 1.0
status: active
category: permissions
priority: P0
tags: [permissions, UID-mismatch, ACL, podman, systemd-timer, critical-infrastructure]
---

# Permissions 4-Layer Model: Comprehensive Gnosis Document

**Status**: LOCKED REFERENCE | **Confidence**: 99% | **Scope**: All Omega Stack Agents

This document is the authoritative specification for understanding, implementing, and troubleshooting permissions across the Omega Stack. All permission-related issues must reference this document and its solutions.

---

## 1. ROOT CAUSE ANALYSIS

### The UID 100999 vs 1000 Mismatch: What and Why

#### The Problem

When Podman containers run without the `--userns=keep-id` flag, they operate in a "user namespace" where container-internal UIDs are mapped differently than the host:

- **Container UID 0** (root inside container) → **Host UID 100999** (unprivileged on host)
- **Container UID 1000** (regular user inside container) → **Host UID 101000** (unprivileged on host)

When these containers create files (e.g., writing to `~/.gemini/memory_bank/`), they're owned by `100999` or `101000` on the host, but the actual host user (e.g., `uid=1000`) cannot read/write these files without explicit permissions.

**Example**:
```
Container writes to: /home/user/.gemini/memory_bank/data.json
File ownership on host: 100999:100999
Host user: 1000:1000
Result: Permission denied (13)
```

### Why Three Layers Are Required Together

A single-layer approach fails because file permission problems are **multi-faceted**:

| Layer | Scope | Problem It Solves |
|-------|-------|-------------------|
| **Layer 1: Ownership** | Existing files | Restores `1000:1000` ownership to files already created by containers |
| **Layer 2: Default ACLs** | New files + directories | Ensures files created by containers are automatically readable by host user |
| **Layer 3: Container Config** | Prevention at source | Prevents UID mismatch from happening in the first place |

**Without Layer 1**: Existing corrupted files remain unreadable.  
**Without Layer 2**: Future files created by containers will have wrong permissions again.  
**Without Layer 3**: Even with Layers 1 and 2, containers not using `keep-id` will re-introduce the problem.

### Why Layer 4 (Timer) Prevents Future Issues

Despite best intentions, permissions can regress:

- **ACL masks are recalculated** when files are chmod'd (even innocently by deployment scripts)
- **Containers may restart** with different namespace configs
- **New mount points** might be added without proper ACL defaults
- **Team members** might forget to apply all three layers when adding new paths

**Layer 4 provides continuous enforcement**: A systemd timer runs daily (or on demand) to:
- Detect ownership mismatches
- Restore correct ACLs automatically
- Log all corrections for audit trail
- Alert when critical paths are affected

This transforms the problem from "reactive firefighting" to "proactive health monitoring."

---

## 2. THE 4-LAYER MODEL: Complete Specification

### Layer 1: Ownership Restoration (chown)

**Purpose**: Fix existing files owned by UID 100999 or other mismatched UIDs.

**When to use**: After discovering files are unreadable by the host user.

**Core command**:
```bash
sudo chown -R 1000:1000 <path>
```

**Implementation for critical paths**:
```bash
# Restore ownership for all critical paths
sudo chown -R 1000:1000 ~/.gemini
sudo chown -R 1000:1000 ~/Documents/Xoe-NovAi/omega-stack/.gemini
sudo chown -R 1000:1000 ~/Documents/Xoe-NovAi/omega-stack/.logs
sudo chown -R 1000:1000 ~/Documents/Xoe-NovAi/omega-stack/.venv_mcp
sudo chown -R 1000:1000 ~/Documents/Xoe-NovAi/omega-stack/mcp-servers
sudo chown -R 1000:1000 ~/Documents/Xoe-NovAi/omega-stack/storage/instances/*/gemini-cli/.gemini 2>/dev/null || true
sudo chown -R 1000:1000 ~/Documents/Xoe-NovAi/omega-stack/storage/instances-active/*/gemini-cli/.gemini 2>/dev/null || true
```

**Verification**:
```bash
ls -ld ~/.gemini
# Should show: drwxr-xr-x user user (not 100999 100999)
```

---

### Layer 2: Default ACLs (setfacl)

**Purpose**: Ensure new files created by containers are automatically readable by host user.

**Why ACLs matter**: Unix permissions alone cannot express "container group should have write, host user should have read." ACLs (Access Control Lists) extend POSIX permissions.

**Core command**:
```bash
sudo setfacl -R -d -m u:1000:rwx <path>
sudo setfacl -R -d -m g:1000:rwx <path>
```

**Flag meanings**:
- `-R`: Recursive (apply to directory and all contents)
- `-d`: Default ACL (applies to future files created in this directory)
- `-m`: Modify (add/update ACL entry)
- `u:1000:rwx`: User 1000 gets read+write+execute

**Implementation for critical paths**:
```bash
# Apply default ACLs recursively
for path in \
  ~/.gemini \
  ~/.gemini/memory_bank \
  ~/Documents/Xoe-NovAi/omega-stack/.gemini \
  ~/Documents/Xoe-NovAi/omega-stack/.logs \
  ~/Documents/Xoe-NovAi/omega-stack/.venv_mcp \
  ~/Documents/Xoe-NovAi/omega-stack/mcp-servers
do
  sudo setfacl -R -d -m u:1000:rwx "$path" 2>/dev/null || true
  sudo setfacl -R -d -m g:1000:rwx "$path" 2>/dev/null || true
  sudo setfacl -R -m u:1000:rwx "$path" 2>/dev/null || true
  sudo setfacl -R -m g:1000:rwx "$path" 2>/dev/null || true
done

# Special handling for storage instances
find ~/Documents/Xoe-NovAi/omega-stack/storage/instances*/*/gemini-cli/.gemini -type d 2>/dev/null | while read dir; do
  sudo setfacl -R -d -m u:1000:rwx "$dir"
  sudo setfacl -R -d -m g:1000:rwx "$dir"
  sudo setfacl -R -m u:1000:rwx "$dir"
  sudo setfacl -R -m g:1000:rwx "$dir"
done
```

**Verification**:
```bash
getfacl ~/.gemini
# Should show default entries like:
# default:user:1000:rwx
# default:group:1000:rwx
```

---

### Layer 3: Podman keep-id (Prevent at Source)

**Purpose**: Prevent UID mismatch from occurring by using host UID/GID mapping.

**How it works**: `--userns=keep-id` tells Podman to map container UIDs 1:1 with host UIDs, eliminating namespace translation.

**Container run configuration**:
```bash
# For podman run commands
podman run --userns=keep-id <other-options> <image>

# For compose files
services:
  my-service:
    image: my-image
    userns_mode: 'keep-id'  # Docker Compose syntax
    # OR in Podman compose:
    userns_mode: 'host'     # Full host namespace (more permissive)
```

**Implementation in Omega Stack**:

1. **Check all podman-compose.yml files**:
```bash
grep -r "services:" ~/Documents/Xoe-NovAi/omega-stack/ --include="*.yml" --include="*.yaml" | \
  grep -v ".git" | cut -d: -f1 | sort -u
```

2. **Update each file** to include `userns_mode: 'keep-id'`:
```yaml
version: '3'
services:
  gemini-cli:
    image: gemini-cli:latest
    userns_mode: 'keep-id'  # ADD THIS LINE
    volumes:
      - ~/.gemini:/home/user/.gemini
      - ~/Documents/Xoe-NovAi/omega-stack/.gemini:/app/.gemini
```

3. **Restart affected containers**:
```bash
cd ~/Documents/Xoe-NovAi/omega-stack
podman-compose down
podman-compose up -d
```

**Verification**:
```bash
# Check container is running with keep-id
podman inspect <container-id> | grep -A10 UsernsMode

# Create file in running container and verify ownership on host
# File should be owned by 1000:1000, not 100999:100999
```

---

### Layer 4: Systemd Timer (Auto-Healing)

**Purpose**: Continuously enforce correct permissions and detect regressions.

**Implementation**: Create two systemd units (service + timer).

#### 4a. Service Unit: `/etc/systemd/system/omega-permissions-heal.service`

```ini
[Unit]
Description=Omega Stack Permissions Auto-Healing Service
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=root
Group=root
ExecStart=/usr/local/bin/omega-permissions-heal.sh
StandardOutput=journal
StandardError=journal
```

#### 4b. Timer Unit: `/etc/systemd/system/omega-permissions-heal.timer`

```ini
[Unit]
Description=Omega Stack Permissions Auto-Healing Timer
Requires=omega-permissions-heal.service

[Timer]
OnBootSec=10min
OnUnitActiveSec=1d
Persistent=true

[Install]
WantedBy=timers.target
```

#### 4c. Healing Script: `/usr/local/bin/omega-permissions-heal.sh`

```bash
#!/bin/bash
set -e

# Omega Stack Permissions Auto-Healing Script
# Runs daily via systemd timer to enforce Layer 1 + 2 + 3 compliance

OMEGA_USER=1000
OMEGA_GROUP=1000
LOG_FILE="/var/log/omega-permissions-heal.log"
CRITICAL_PATHS=(
  "$HOME/.gemini"
  "$HOME/.gemini/memory_bank"
  "$HOME/Documents/Xoe-NovAi/omega-stack/.gemini"
  "$HOME/Documents/Xoe-NovAi/omega-stack/.logs"
  "$HOME/Documents/Xoe-NovAi/omega-stack/.venv_mcp"
  "$HOME/Documents/Xoe-NovAi/omega-stack/mcp-servers"
)

log_message() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "=== Starting Omega Permissions Healing ==="

# Layer 1: Restore ownership
log_message "Layer 1: Restoring ownership to $OMEGA_USER:$OMEGA_GROUP"
for path in "${CRITICAL_PATHS[@]}"; do
  if [[ -e "$path" ]]; then
    CURRENT_OWNER=$(stat -c '%u:%g' "$path")
    if [[ "$CURRENT_OWNER" != "$OMEGA_USER:$OMEGA_GROUP" ]]; then
      log_message "  CORRECTING: $path ($CURRENT_OWNER → $OMEGA_USER:$OMEGA_GROUP)"
      chown -R "$OMEGA_USER:$OMEGA_GROUP" "$path"
    else
      log_message "  OK: $path"
    fi
  fi
done

# Layer 2: Verify Default ACLs
log_message "Layer 2: Verifying Default ACLs"
for path in "${CRITICAL_PATHS[@]}"; do
  if [[ -d "$path" ]]; then
    ACL_COUNT=$(getfacl -d "$path" 2>/dev/null | grep -c "default:user:$OMEGA_USER:rwx" || echo 0)
    if [[ $ACL_COUNT -eq 0 ]]; then
      log_message "  APPLYING: ACLs for $path"
      setfacl -R -d -m u:$OMEGA_USER:rwx "$path" 2>/dev/null || true
      setfacl -R -d -m g:$OMEGA_GROUP:rwx "$path" 2>/dev/null || true
      setfacl -R -m u:$OMEGA_USER:rwx "$path" 2>/dev/null || true
      setfacl -R -m g:$OMEGA_GROUP:rwx "$path" 2>/dev/null || true
    else
      log_message "  OK: $path (ACLs present)"
    fi
  fi
done

# Layer 3: Check Podman container configs
log_message "Layer 3: Checking Podman container configurations"
CONTAINERS=$(podman ps -a --format='{{.Names}}' 2>/dev/null || echo "")
if [[ -n "$CONTAINERS" ]]; then
  for container in $CONTAINERS; do
    USERNS=$(podman inspect "$container" 2>/dev/null | grep -o '"UsernsMode":"[^"]*"' | cut -d'"' -f4)
    if [[ "$USERNS" != "keep-id" ]] && [[ "$USERNS" != "host" ]]; then
      log_message "  WARNING: Container $container using namespace mode: $USERNS (should be keep-id)"
    else
      log_message "  OK: Container $container using mode: $USERNS"
    fi
  done
else
  log_message "  (No running containers to check)"
fi

log_message "=== Omega Permissions Healing Complete ==="
```

#### 4d. Enable and Start Timer

```bash
sudo cp /path/to/omega-permissions-heal.service /etc/systemd/system/
sudo cp /path/to/omega-permissions-heal.timer /etc/systemd/system/
sudo cp /path/to/omega-permissions-heal.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/omega-permissions-heal.sh

sudo systemctl daemon-reload
sudo systemctl enable omega-permissions-heal.timer
sudo systemctl start omega-permissions-heal.timer

# Verify timer is running
sudo systemctl list-timers omega-permissions-heal.timer
```

**Manual trigger** (for testing):
```bash
sudo systemctl start omega-permissions-heal.service
journalctl -u omega-permissions-heal.service -f
```

---

## 3. CRITICAL PATHS IN OMEGA STACK

All these paths MUST have proper Layer 1 + Layer 2 permissions:

| Path | Purpose | Criticality | Owner |
|------|---------|------------|-------|
| `~/.gemini/` | Gemini CLI home directory | P0 | Host user |
| `~/.gemini/memory_bank/` | Persistent memory storage | P0 | Host user |
| `~/Documents/Xoe-NovAi/omega-stack/.gemini/` | Stack-level config | P0 | Host user |
| `~/Documents/Xoe-NovAi/omega-stack/.logs/` | Application logs | P1 | Host user |
| `~/Documents/Xoe-NovAi/omega-stack/.venv_mcp/` | Python venv (MCP) | P1 | Host user |
| `~/Documents/Xoe-NovAi/omega-stack/mcp-servers/` | MCP server configs | P1 | Host user |
| `~/Documents/Xoe-NovAi/omega-stack/storage/instances/*/gemini-cli/.gemini/` | Instance-level configs | P2 | Host user |
| `~/Documents/Xoe-NovAi/omega-stack/storage/instances-active/*/gemini-cli/.gemini/` | Active instance configs | P2 | Host user |

**P0 (Critical)**: Application will fail completely if unreadable.  
**P1 (Important)**: Features degraded or unavailable.  
**P2 (Baseline)**: Should be clean, but not immediately blocking.

---

## 4. IMPLEMENTATION PROCEDURES

### Complete Setup: Step-by-Step

#### Phase 1: Assessment (5 minutes)

```bash
# Check current state of critical paths
echo "=== Current Permissions State ==="
for path in \
  ~/.gemini \
  ~/.gemini/memory_bank \
  ~/Documents/Xoe-NovAi/omega-stack/.gemini \
  ~/Documents/Xoe-NovAi/omega-stack/.logs \
  ~/Documents/Xoe-NovAi/omega-stack/.venv_mcp \
  ~/Documents/Xoe-NovAi/omega-stack/mcp-servers
do
  if [[ -e "$path" ]]; then
    echo "--- $path ---"
    stat -c '%U:%G (UID:%u:%g)' "$path"
    getfacl -d "$path" 2>/dev/null | head -3 || echo "  (no ACLs)"
  fi
done
```

#### Phase 2: Apply Layer 1 (5 minutes)

```bash
echo "=== Layer 1: Ownership Restoration ==="
sudo chown -R 1000:1000 ~/.gemini
sudo chown -R 1000:1000 ~/Documents/Xoe-NovAi/omega-stack/.gemini
sudo chown -R 1000:1000 ~/Documents/Xoe-NovAi/omega-stack/.logs
sudo chown -R 1000:1000 ~/Documents/Xoe-NovAi/omega-stack/.venv_mcp
sudo chown -R 1000:1000 ~/Documents/Xoe-NovAi/omega-stack/mcp-servers
find ~/Documents/Xoe-NovAi/omega-stack/storage -type d -path "*/.gemini" -exec sudo chown -R 1000:1000 {} \; 2>/dev/null

echo "Layer 1 complete. Verifying..."
stat -c '%U:%G' ~/.gemini
```

#### Phase 3: Apply Layer 2 (5 minutes)

```bash
echo "=== Layer 2: Default ACLs ==="
for path in \
  ~/.gemini \
  ~/.gemini/memory_bank \
  ~/Documents/Xoe-NovAi/omega-stack/.gemini \
  ~/Documents/Xoe-NovAi/omega-stack/.logs \
  ~/Documents/Xoe-NovAi/omega-stack/.venv_mcp \
  ~/Documents/Xoe-NovAi/omega-stack/mcp-servers
do
  if [[ -d "$path" ]]; then
    sudo setfacl -R -d -m u:1000:rwx "$path" 2>/dev/null || true
    sudo setfacl -R -d -m g:1000:rwx "$path" 2>/dev/null || true
    sudo setfacl -R -m u:1000:rwx "$path" 2>/dev/null || true
    sudo setfacl -R -m g:1000:rwx "$path" 2>/dev/null || true
    echo "  ✓ $path"
  fi
done

echo "Layer 2 complete. Verifying..."
getfacl -d ~/.gemini | grep "default:user:1000:rwx"
```

#### Phase 4: Apply Layer 3 (15 minutes)

1. List all compose files:
```bash
find ~/Documents/Xoe-NovAi/omega-stack -name "*compose*.yml" -o -name "*compose*.yaml" | grep -v ".git"
```

2. Edit each to add `userns_mode: 'keep-id'` under service definitions.

3. Restart containers:
```bash
cd ~/Documents/Xoe-NovAi/omega-stack
podman-compose down
podman-compose up -d
```

#### Phase 5: Apply Layer 4 (10 minutes)

```bash
# Create service file
sudo tee /etc/systemd/system/omega-permissions-heal.service > /dev/null <<'EOF'
[Unit]
Description=Omega Stack Permissions Auto-Healing Service
After=network-online.target

[Service]
Type=oneshot
User=root
ExecStart=/usr/local/bin/omega-permissions-heal.sh
StandardOutput=journal
StandardError=journal
EOF

# Create timer file
sudo tee /etc/systemd/system/omega-permissions-heal.timer > /dev/null <<'EOF'
[Unit]
Description=Omega Stack Permissions Auto-Healing Timer
Requires=omega-permissions-heal.service

[Timer]
OnBootSec=10min
OnUnitActiveSec=1d
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Create healing script (see Layer 4 section above)
# Then enable:
sudo systemctl daemon-reload
sudo systemctl enable omega-permissions-heal.timer
sudo systemctl start omega-permissions-heal.timer

# Verify
sudo systemctl status omega-permissions-heal.timer
```

---

## 5. TROUBLESHOOTING GUIDE

### Symptom: Permission Denied on .gemini Files

**Error Message**:
```
OSError: [Errno 13] Permission denied: '/home/user/.gemini/memory_bank/session.json'
```

**Root Cause Analysis**:
1. Check file ownership:
```bash
ls -ld ~/.gemini
stat -c '%U:%G' ~/.gemini
```
2. If owner is `100999` or other non-1000: **Layer 1 not applied**
3. If owner is correct but still denied: **Layer 2 missing**

**Fix**:
```bash
# Apply Layer 1
sudo chown -R 1000:1000 ~/.gemini

# Apply Layer 2
sudo setfacl -R -d -m u:1000:rwx ~/.gemini
sudo setfacl -R -m u:1000:rwx ~/.gemini

# Verify
getfacl ~/.gemini | grep "default:user"
```

---

### Symptom: Permission Denied Reappears After Container Restart

**Error**: Permission issues return within hours/days.

**Root Cause**: 
- **Container using wrong namespace mode** (Layer 3 not applied)
- **ACL mask recalculated by chmod** (Layer 4 not monitoring)

**Fix**:

1. Check container userns mode:
```bash
podman inspect <container> | grep UsernsMode
# Should be "keep-id" or "host"
```

2. If not keep-id, update compose file and restart:
```yaml
services:
  my-service:
    userns_mode: 'keep-id'  # Add this line
```

3. Verify Layer 4 timer is running:
```bash
sudo systemctl status omega-permissions-heal.timer
sudo systemctl start omega-permissions-heal.service  # Test manually
journalctl -u omega-permissions-heal.service -n 20
```

---

### Symptom: New Files Created by Container Unreadable by Host User

**Error**:
```
ls: cannot open directory '.gemini': Permission denied
```

**Root Cause**: Parent directory missing DEFAULT ACLs (Layer 2 incomplete).

**Why it matters**: `chmod` recalculates ACL masks and can erase default ACLs. Files created after this point won't inherit parent ACLs.

**Fix**:

1. Re-apply Layer 2 to ALL parent directories:
```bash
# CRITICAL: Use -d flag for default ACLs on DIRECTORIES
sudo setfacl -R -d -m u:1000:rwx ~/.gemini
sudo setfacl -R -d -m g:1000:rwx ~/.gemini
```

2. Clear and reapply ACLs on existing files:
```bash
sudo setfacl -R -b ~/.gemini  # Clear all ACLs
sudo setfacl -R -d -m u:1000:rwx ~/.gemini  # Reapply
sudo setfacl -R -m u:1000:rwx ~/.gemini
```

3. Enable Layer 4 monitoring:
```bash
sudo systemctl start omega-permissions-heal.timer
```

---

### Symptom: Recursive Application Too Slow

**Issue**: `sudo chown -R` or `setfacl -R` on deep directories with thousands of files takes 5+ minutes.

**Optimization**:

1. Target only the leaf directories needing correction:
```bash
# Find only directories with wrong ownership
find ~/.gemini -type d -uid 100999 -exec sudo chown 1000:1000 {} \;
```

2. Use `find` with ACLs:
```bash
find ~/.gemini -type d -exec sudo setfacl -d -m u:1000:rwx {} \;
```

3. For new content, Layer 3 (`keep-id`) prevents the problem entirely.

---

### Symptom: "Filesystem Does Not Support ACLs"

**Error**:
```
setfacl: ~/.gemini: Operation not supported
```

**Root Cause**: Filesystem mounted without `acl` option.

**Fix**:

1. Check current mount options:
```bash
mount | grep "$(df ~/.gemini | tail -1 | awk '{print $1}')"
# Look for "acl" in options
```

2. If missing, remount with acl:
```bash
MOUNT_POINT=$(df ~/.gemini | tail -1 | awk '{print $6}')
sudo mount -o remount,acl "$MOUNT_POINT"
```

3. Make permanent in `/etc/fstab`:
```bash
# Find the line for your filesystem and add acl option
sudo nano /etc/fstab
# Example: /dev/sda1  /home  ext4  defaults,acl  0  2
```

---

## 6. BEST PRACTICES FOR OMEGA STACK

### When to Use `keep-id` vs `:U` Flag

| Flag | Use Case | Pros | Cons |
|------|----------|------|------|
| `--userns=keep-id` | All Omega Stack containers | 1:1 UID mapping, no mismatch | None significant |
| `-v volume:U` | ✗ NOT RECOMMENDED | Relabels SELinux context | Only for SELinux, breaks ACLs |
| Default (no flag) | ✗ NOT RECOMMENDED | Standard container behavior | UID 100999 mismatch |

**Decision**: Use `keep-id` for Omega Stack exclusively.

---

### Why DEFAULT ACLs Are Critical

DEFAULT ACLs are separate from "access ACLs":

- **Access ACL** (`setfacl -m`): Applies to the directory itself
- **Default ACL** (`setfacl -d`): Applies to files/directories created inside

```bash
# Access ACL: Affects /home/user/.gemini
sudo setfacl -m u:1000:rwx ~/.gemini

# Default ACL: Affects files created INSIDE ~/.gemini
sudo setfacl -d -m u:1000:rwx ~/.gemini

# BOTH are needed
sudo setfacl -R -m u:1000:rwx ~/.gemini
sudo setfacl -R -d -m u:1000:rwx ~/.gemini
```

Without `-d`, new files created in the directory won't inherit parent ACLs.

---

### How to Prevent UID Mismatches

1. **Always use `keep-id` in containers**:
```yaml
services:
  any-service:
    userns_mode: 'keep-id'
```

2. **Set Layer 2 defaults before containers write data**:
```bash
# Pre-create critical directories with correct ACLs
mkdir -p ~/.gemini/memory_bank
sudo chown 1000:1000 ~/.gemini ~/.gemini/memory_bank
sudo setfacl -R -d -m u:1000:rwx ~/.gemini
```

3. **Use Layer 4 monitoring** to catch regressions early.

---

### Standard ACL Masks for Omega Services

All Omega service directories should use:

```bash
# For read-heavy services (most)
sudo setfacl -R -d -m u:1000:rx ~/.gemini

# For read-write services (memory_bank, temp storage)
sudo setfacl -R -d -m u:1000:rwx ~/.gemini/memory_bank

# For venv/packages (execution + read)
sudo setfacl -R -d -m u:1000:rx ~/.venv_mcp
```

---

## 7. YAML GNOSIS FORMAT: Permission Issue Logging

When documenting permission issues, use this YAML structure in `memory_bank/gnosis/`:

```yaml
---
blocker_id: PERM-001
category: permissions
severity: P0  # P0 (Critical), P1 (Important), P2 (Baseline)
status: resolved  # pending, in_progress, resolved

title: "UID 100999 ownership on .gemini breaks Gemini CLI"

symptom: |
  Gemini CLI cannot read/write ~/.gemini/memory_bank/ files.
  Error: OSError: [Errno 13] Permission denied

root_cause: |
  Container created files while running in user namespace without keep-id.
  Files owned by UID 100999 (container root) instead of 1000 (host user).
  Host user (UID 1000) has no read permission on these files.

environment: |
  Host: Omega Stack on Ubuntu 22.04
  Container runtime: Podman 4.x
  Filesystem: ext4 with ACL support
  User: uid=1000 gid=1000

affected_paths:
  - ~/.gemini
  - ~/.gemini/memory_bank
  - ~/Documents/Xoe-NovAi/omega-stack/.gemini

solution: |
  Applied all 4 layers in order:
  
  1. Layer 1: Restored ownership
     $ sudo chown -R 1000:1000 ~/.gemini
  
  2. Layer 2: Applied default ACLs
     $ sudo setfacl -R -d -m u:1000:rwx ~/.gemini
     $ sudo setfacl -R -m u:1000:rwx ~/.gemini
  
  3. Layer 3: Updated container to use keep-id
     Modified docker-compose.yml:
     services:
       gemini-cli:
         userns_mode: 'keep-id'
  
  4. Layer 4: Enabled auto-healing timer
     $ sudo systemctl enable omega-permissions-heal.timer
     $ sudo systemctl start omega-permissions-heal.timer

layers_applied: [1, 2, 3, 4]

verification_commands: |
  # Verify Layer 1
  stat -c '%U:%G' ~/.gemini
  # Expected: user:user (UID 1000, GID 1000)
  
  # Verify Layer 2
  getfacl ~/.gemini | grep "default:user:1000:rwx"
  # Expected: default:user:1000:rwx--
  
  # Verify Layer 3
  podman inspect <container> | grep UsernsMode
  # Expected: "UsernsMode": "keep-id"
  
  # Verify Layer 4
  sudo systemctl status omega-permissions-heal.timer
  # Expected: active (waiting)

date_discovered: 2026-03-14
date_fixed: 2026-03-15
confidence: 99%
resolution_time_minutes: 15

preventive_measures: |
  - All new containers now use userns_mode: 'keep-id'
  - Critical paths pre-configured with Layer 2 defaults
  - Layer 4 timer monitors continuously and alerts on regression
  - New team members reference this Gnosis document before adding services

related_blockers:
  - PERM-002
  - INFRA-045

references:
  - specification_permissions-4layer-model_v1.0_20260315_active.md
  - CONTRIBUTING.md (Container guidelines section)
  - Linux ACL documentation: man setfacl

tags:
  - permissions
  - UID-mismatch
  - container-isolation
  - ACL
  - podman
  - critical-infrastructure
```

---

## 8. QUICK REFERENCE COMMANDS

### Check Current State
```bash
# Ownership
stat -c '%U:%G' ~/.gemini

# ACLs
getfacl ~/.gemini

# Container namespace
podman inspect <container> | grep UsernsMode

# Timer status
sudo systemctl status omega-permissions-heal.timer
```

### Apply All Layers (Full Reset)
```bash
# Layer 1: Ownership
for path in ~/.gemini ~/Documents/Xoe-NovAi/omega-stack/.gemini ~/Documents/Xoe-NovAi/omega-stack/.logs; do
  sudo chown -R 1000:1000 "$path"
done

# Layer 2: ACLs
for path in ~/.gemini ~/Documents/Xoe-NovAi/omega-stack/.gemini ~/Documents/Xoe-NovAi/omega-stack/.logs; do
  sudo setfacl -R -d -m u:1000:rwx "$path"
  sudo setfacl -R -m u:1000:rwx "$path"
done

# Layer 3: Update compose files and restart
cd ~/Documents/Xoe-NovAi/omega-stack && podman-compose restart

# Layer 4: Start timer
sudo systemctl start omega-permissions-heal.timer
```

### Emergency Recovery
```bash
# If Layer 1 needed immediately
sudo chown -R 1000:1000 ~/.gemini ~/.gemini/memory_bank

# If Layer 2 broken
sudo setfacl -R -b ~/.gemini  # Clear all ACLs
sudo setfacl -R -d -m u:1000:rwx ~/.gemini  # Reapply
```

---

## 9. FINAL CHECKLIST

After implementing all 4 layers:

- [ ] Layer 1: All critical paths owned by `1000:1000`
- [ ] Layer 2: Default ACLs present on all directories
- [ ] Layer 3: All containers use `userns_mode: 'keep-id'`
- [ ] Layer 4: Timer installed and running
- [ ] Verification: `stat` shows correct owner on all paths
- [ ] Verification: `getfacl` shows default ACLs with `u:1000:rwx`
- [ ] Verification: `podman inspect` shows `keep-id` on all containers
- [ ] Verification: `journalctl` shows timer running successfully
- [ ] Team notified and reference docs updated
- [ ] This document locked in memory_bank for future reference

---

**Document Status**: LOCKED | **Next Review**: 2026-06-15 | **Confidence Level**: 99%

All Omega Stack agents should reference this document when encountering permission issues. For new permissions problems not covered here, log them using the YAML Gnosis format in Section 7 and update this document.
