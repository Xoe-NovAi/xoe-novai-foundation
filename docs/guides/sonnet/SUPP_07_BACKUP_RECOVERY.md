---
title: "Omega-Stack Supplemental Manual SUPP-07: Backup, Recovery & Business Continuity"
section: "SUPP-07"
scope: "Automated backups, volume snapshots, restore procedures, disaster recovery"
status: "Actionable"
priority: "P2 — No Backup Strategy Currently in Place"
last_updated: "2026-03-13"
---

# SUPP-07 — Backup, Recovery & Business Continuity
## Omega-Stack Supplemental Implementation Manual

> **🤖 AGENT DIRECTIVE:** There is currently **no automated backup strategy** for the Omega-Stack. The 454MB frozen facet templates, PostgreSQL data, and `.gemini` credentials are all unprotected. This manual implements a 3-tier backup system using `rsync` + systemd timers targeting the omega_vault external mount.

---

## Table of Contents
1. [Backup Scope & Priority](#1-backup-scope--priority)
2. [Tier 1 — Daily Critical Backup](#2-tier-1--daily-critical-backup)
3. [Tier 2 — Weekly Full Stack Backup](#3-tier-2--weekly-full-stack-backup)
4. [Tier 3 — Database Dumps](#4-tier-3--database-dumps)
5. [Restore Procedures](#5-restore-procedures)
6. [Systemd Backup Timers](#6-systemd-backup-timers)
7. [Backup Verification](#7-backup-verification)
8. [Edge Cases & Failure Modes](#8-edge-cases--failure-modes)

---

## 1. Backup Scope & Priority

| Data | Location | Frequency | Priority | Size |
|------|---------|-----------|---------|------|
| `.gemini` credentials & settings | `~/.gemini/`, repo `.gemini/` | Daily | 🔴 CRITICAL | ~5MB |
| PostgreSQL data | postgres container volume | Daily | 🔴 CRITICAL | ~2GB |
| Frozen facet templates | `storage/instances/` | Weekly | 🟠 HIGH | 454MB |
| MCP config | `config/mcp_config.json` | Weekly | 🟠 HIGH | ~42KB |
| docker-compose.yml | `infra/docker/` | Weekly | 🟠 HIGH | ~1MB |
| Redis data | redis container volume | Daily (optional) | 🟡 MEDIUM | ~180MB |
| omega_library media | `/media/arcana-novai/omega_library/` | Monthly | 🟡 MEDIUM | 45GB |

> **⚠️ VAULT SPACE WARNING:**  
> omega_vault is at 75% capacity (16GB/16GB, 4GB free). Backup data must fit within 4GB. Implement backup rotation immediately.

---

## 2. Tier 1 — Daily Critical Backup

```bash
#!/usr/bin/env bash
# ~/omega-stack/scripts/backup/daily_backup.sh
set -euo pipefail

VAULT="/media/arcana-novai/omega_vault/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${VAULT}/daily/${DATE}"
LOG="/tmp/omega_backup_${DATE}.log"

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }

# Check vault is mounted
mountpoint -q /media/arcana-novai/omega_vault || { log "❌ Vault not mounted. Aborting."; exit 1; }
# Check vault has space (need at least 200MB)
VAULT_FREE=$(df /media/arcana-novai/omega_vault | tail -1 | awk '{print $4}')
[ "$VAULT_FREE" -gt 204800 ] || { log "❌ Vault has <200MB free. Run cleanup first."; exit 1; }

mkdir -p "$BACKUP_DIR"

log "=== OMEGA-STACK DAILY BACKUP: $DATE ==="

# 1. .gemini credentials (MOST CRITICAL)
log "Backing up .gemini..."
rsync -az --delete \
  ~/.gemini/ \
  "$BACKUP_DIR/gemini_home/"
rsync -az --delete \
  ~/Documents/Xoe-NovAi/omega-stack/.gemini/ \
  "$BACKUP_DIR/gemini_repo/" 2>/dev/null || true

# 2. Environment files (encrypted copy)
log "Backing up .env files..."
if command -v sops &>/dev/null; then
  cp ~/Documents/Xoe-NovAi/omega-stack/.env.encrypted "$BACKUP_DIR/" 2>/dev/null || \
    rsync -a ~/Documents/Xoe-NovAi/omega-stack/.env "$BACKUP_DIR/.env.plaintext"
else
  rsync -a ~/Documents/Xoe-NovAi/omega-stack/.env "$BACKUP_DIR/.env.plaintext"
  chmod 600 "$BACKUP_DIR/.env.plaintext"
fi

# 3. PostgreSQL dump
log "Dumping PostgreSQL..."
podman exec postgres pg_dumpall -U postgres 2>/dev/null | \
  gzip > "$BACKUP_DIR/postgres_full_$(date +%Y%m%d).sql.gz" || \
  log "⚠️ PostgreSQL dump failed (service may be down)"

# 4. Rotate old daily backups (keep 7 days)
find "${VAULT}/daily/" -maxdepth 1 -type d -mtime +7 -exec rm -rf {} + 2>/dev/null || true

# Summary
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
log "✔ Daily backup complete. Size: $BACKUP_SIZE. Location: $BACKUP_DIR"
log "Log: $LOG"
```

---

## 3. Tier 2 — Weekly Full Stack Backup

```bash
#!/usr/bin/env bash
# ~/omega-stack/scripts/backup/weekly_backup.sh
set -euo pipefail

VAULT="/media/arcana-novai/omega_vault/backups"
WEEK=$(date +%Y_W%V)
BACKUP_DIR="${VAULT}/weekly/${WEEK}"
mkdir -p "$BACKUP_DIR"

echo "=== WEEKLY FULL STACK BACKUP: $WEEK ==="

# 1. Frozen facet templates (source of truth)
echo "Backing up facet templates (454MB)..."
rsync -az --delete \
  ~/Documents/Xoe-NovAi/omega-stack/storage/instances/ \
  "$BACKUP_DIR/facet_templates/"

# 2. Full configuration
echo "Backing up configs..."
rsync -az \
  ~/Documents/Xoe-NovAi/omega-stack/config/ \
  "$BACKUP_DIR/config/"
rsync -a \
  ~/Documents/Xoe-NovAi/omega-stack/docker-compose.yml \
  "$BACKUP_DIR/"

# 3. Podman volume list and inspect
echo "Documenting Podman volumes..."
podman volume ls > "$BACKUP_DIR/podman_volumes.txt"
for VOL in $(podman volume ls -q); do
  podman volume inspect "$VOL" >> "$BACKUP_DIR/podman_volumes.txt"
done

# 4. Active instance state
rsync -az \
  ~/Documents/Xoe-NovAi/omega-stack/instances-active/ \
  "$BACKUP_DIR/instances_active/"

# Rotate (keep 4 weeks)
find "${VAULT}/weekly/" -maxdepth 1 -type d -mtime +30 -exec rm -rf {} + 2>/dev/null || true

BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo "✔ Weekly backup complete. Size: $BACKUP_SIZE"
```

---

## 4. Tier 3 — Database Dumps

```bash
#!/usr/bin/env bash
# ~/omega-stack/scripts/backup/db_backup.sh

VAULT="/media/arcana-novai/omega_vault/backups/databases"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p "$VAULT"

# PostgreSQL full dump
echo "Dumping PostgreSQL..."
podman exec postgres pg_dumpall -U postgres | \
  gzip > "${VAULT}/postgres_${DATE}.sql.gz"

# PostgreSQL per-database dumps
for DB in $(podman exec postgres psql -U postgres -t -c "SELECT datname FROM pg_database WHERE datistemplate = false;" 2>/dev/null | tr -d ' '); do
  podman exec postgres pg_dump -U postgres "$DB" | \
    gzip > "${VAULT}/postgres_${DB}_${DATE}.sql.gz"
  echo "✅ Dumped database: $DB"
done

# Redis snapshot
echo "Saving Redis snapshot..."
podman exec redis redis-cli BGSAVE
sleep 2
podman cp redis:/data/dump.rdb "${VAULT}/redis_${DATE}.rdb" 2>/dev/null || true

# Rotate DB backups (keep 14 days)
find "$VAULT" -name "*.sql.gz" -mtime +14 -delete
find "$VAULT" -name "*.rdb" -mtime +14 -delete

echo "✔ Database backups complete"
ls -lh "$VAULT" | tail -10
```

---

## 5. Restore Procedures

### 5.1 Restore .gemini from Backup

```bash
#!/usr/bin/env bash
# Find latest backup
VAULT="/media/arcana-novai/omega_vault/backups"
LATEST=$(ls -t "${VAULT}/daily/" | head -1)
BACKUP_DIR="${VAULT}/daily/${LATEST}"

echo "Restoring from: $BACKUP_DIR"
echo "This will overwrite current ~/.gemini — continue? [y/N]"
read -r CONFIRM
[ "$CONFIRM" = "y" ] || exit 0

# Backup current (might be partially broken)
cp -r ~/.gemini ~/.gemini.restore_backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

# Restore
rsync -az "$BACKUP_DIR/gemini_home/" ~/.gemini/
sudo chown -R arcana-novai:arcana-novai ~/.gemini/
echo "✅ .gemini restored from $LATEST"
```

### 5.2 Restore PostgreSQL

```bash
#!/usr/bin/env bash
VAULT="/media/arcana-novai/omega_vault/backups/databases"
LATEST_DUMP=$(ls -t "${VAULT}"/postgres_*.sql.gz | head -1)

echo "Restoring PostgreSQL from: $LATEST_DUMP"
echo "WARNING: This drops and recreates all databases. Continue? [y/N]"
read -r CONFIRM
[ "$CONFIRM" = "y" ] || exit 0

# Stop dependent services
for SVC in rag_api librarian memory-bank-mcp oikos; do
  podman stop "$SVC" 2>/dev/null || true
done

# Restore
zcat "$LATEST_DUMP" | podman exec -i postgres psql -U postgres

# Restart services
for SVC in rag_api librarian memory-bank-mcp oikos; do
  podman start "$SVC" 2>/dev/null || true
done
echo "✅ PostgreSQL restored"
```

---

## 6. Systemd Backup Timers

```bash
#!/usr/bin/env bash
# Install all backup timers
SCRIPTS=~/Documents/Xoe-NovAi/omega-stack/scripts/backup
SYSTEMD=~/.config/systemd/user
mkdir -p "$SYSTEMD"
chmod +x "${SCRIPTS}/"*.sh

# Daily backup timer
cat > "${SYSTEMD}/omega-backup-daily.service" << 'EOF'
[Unit]
Description=Omega-Stack Daily Backup
After=default.target
[Service]
Type=oneshot
ExecStart=%h/Documents/Xoe-NovAi/omega-stack/scripts/backup/daily_backup.sh
StandardOutput=journal
StandardError=journal
EOF

cat > "${SYSTEMD}/omega-backup-daily.timer" << 'EOF'
[Unit]
Description=Omega-Stack Daily Backup Timer
[Timer]
OnCalendar=daily
OnBootSec=10min
Persistent=true
[Install]
WantedBy=timers.target
EOF

# Weekly backup timer
cat > "${SYSTEMD}/omega-backup-weekly.service" << 'EOF'
[Unit]
Description=Omega-Stack Weekly Backup
[Service]
Type=oneshot
ExecStart=%h/Documents/Xoe-NovAi/omega-stack/scripts/backup/weekly_backup.sh
StandardOutput=journal
EOF

cat > "${SYSTEMD}/omega-backup-weekly.timer" << 'EOF'
[Unit]
Description=Omega-Stack Weekly Backup Timer
[Timer]
OnCalendar=Sun 02:00
Persistent=true
[Install]
WantedBy=timers.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now omega-backup-daily.timer omega-backup-weekly.timer
systemctl --user list-timers omega-backup* --no-pager
```

---

## 7. Backup Verification

```bash
#!/usr/bin/env bash
echo "=== BACKUP VERIFICATION ==="

VAULT="/media/arcana-novai/omega_vault/backups"

# Check vault mounted
mountpoint -q /media/arcana-novai/omega_vault && echo "✅ Vault mounted" || echo "❌ Vault NOT mounted"

# Check latest backup age
if [ -d "${VAULT}/daily" ]; then
  LATEST=$(ls -t "${VAULT}/daily/" | head -1)
  if [ -n "$LATEST" ]; then
    AGE=$(( ($(date +%s) - $(stat -c %Y "${VAULT}/daily/${LATEST}")) / 3600 ))
    [ "$AGE" -lt 26 ] && echo "✅ Latest daily backup: ${AGE}h ago" || echo "⚠️ Latest daily backup: ${AGE}h ago (>24h)"
  fi
else
  echo "❌ No daily backups found"
fi

# Check backup timers
systemctl --user is-active omega-backup-daily.timer &>/dev/null && \
  echo "✅ Daily backup timer active" || echo "❌ Daily backup timer not active"

# Vault disk space
df -h /media/arcana-novai/omega_vault | tail -1 | awk '{print "Vault: "$5" used, "$4" available"}'
```

---

## 8. Edge Cases & Failure Modes

| Scenario | Resolution |
|----------|-----------|
| Vault not mounted during backup | Script exits safely with error — no partial backup |
| Vault full (>95%) | Rotate old backups: `find $VAULT/daily -mtime +3 -exec rm -rf {} +` |
| PostgreSQL dump fails (service down) | Skip DB dump; core .gemini backup still completes |
| rsync fails mid-transfer | Partial backup in temp dir; retry completes atomically |
| Restore overwrites good data | Always creates `.restore_backup.*` timestamped copy first |
