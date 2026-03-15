---
title: "Omega-Stack Implementation Manual 10: Master Deployment Orchestration"
section: "10"
scope: "End-to-end deployment, ordered startup, rollback, CI/CD hooks"
status: "Actionable — Final Integration Reference"
priority: "P0-P2 — All Layers"
last_updated: "2026-03-13"
---

# IMPL-10 — Master Deployment Orchestration
## Omega-Stack Agent Implementation Manual

> **🤖 AGENT DIRECTIVE:** This is the final integration manual. It provides the complete, ordered deployment sequence for a fresh start or full recovery. All other IMPL and SUPP manuals are prerequisites. Use this as the single source of truth for "how to bring the stack up from scratch."

---

## Table of Contents
1. [Pre-Deployment Checklist](#1-pre-deployment-checklist)
2. [Ordered Boot Sequence](#2-ordered-boot-sequence)
3. [Full Recovery Procedure](#3-full-recovery-procedure)
4. [Rollback Procedures](#4-rollback-procedures)
5. [Post-Deployment Validation](#5-post-deployment-validation)
6. [Maintenance Schedule](#6-maintenance-schedule)

---

## 1. Pre-Deployment Checklist

```bash
#!/usr/bin/env bash
echo "=== PRE-DEPLOYMENT CHECKS ==="

OMEGA=~/Documents/Xoe-NovAi/omega-stack

# Storage
DISK=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
[ "$DISK" -lt 85 ] || { echo "❌ ABORT: Disk at ${DISK}% — run IMPL-01 §4 first"; exit 1; }
echo "✅ Disk: ${DISK}%"

# Podman
podman --version > /dev/null || { echo "❌ ABORT: Podman not available"; exit 1; }
echo "✅ Podman available"

# subuid
grep -q arcana-novai /etc/subuid || { echo "❌ ABORT: subuid not configured"; exit 1; }
echo "✅ subuid configured"

# .env exists
[ -f "${OMEGA}/.env" ] || { echo "❌ ABORT: .env missing"; exit 1; }
echo "✅ .env present"

echo ""
echo "Pre-deployment checks passed. Ready to deploy."
```

---

## 2. Ordered Boot Sequence

```bash
#!/usr/bin/env bash
# ~/omega-stack/scripts/omega_start.sh
set -euo pipefail
OMEGA=~/Documents/Xoe-NovAi/omega-stack
LOG="/tmp/omega_start_$(date +%Y%m%d_%H%M%S).log"
log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }

wait_http() {
  local NAME="$1" URL="$2" MAX="${3:-60}"
  log -n "Waiting for $NAME..."
  for i in $(seq 1 "$MAX"); do
    curl -sf "$URL" &>/dev/null && log " ✅" && return 0
    sleep 1; printf "."
  done
  log " ❌ TIMEOUT"
  return 1
}

cd "$OMEGA"

log "═══ PHASE 1: Infrastructure ═══"
podman-compose up -d redis postgres vikunja_db victoriametrics
sleep 8
podman exec redis redis-cli ping | grep -q PONG && log "✅ redis ready"
podman exec postgres psql -U postgres -c "SELECT 1" &>/dev/null && log "✅ postgres ready"

log "═══ PHASE 2: Core APIs ═══"
podman-compose up -d qdrant memory-bank-mcp
wait_http "memory-bank-mcp" "http://localhost:8005/health" 60
wait_http "qdrant" "http://localhost:6333/health" 90

log "═══ PHASE 3: MCP Servers ═══"
podman-compose up -d xnai-github xnai-stats-mcp xnai-websearch \
  xnai-gnosis xnai-agentbus xnai-memory xnai-rag
sleep 10

log "═══ PHASE 4: Integration APIs ═══"
podman-compose up -d rag_api librarian oikos
sleep 10

log "═══ PHASE 5: Observability & Proxy ═══"
podman-compose up -d grafana caddy node-exporter 2>/dev/null || true

log "═══ PHASE 6: Permission Verification ═══"
bash "${OMEGA}/scripts/permissions/acl_repair.sh"
BAD=$(find "${OMEGA}/.gemini" -not -user arcana-novai 2>/dev/null | wc -l)
[ "$BAD" -eq 0 ] && log "✅ Permissions clean" || log "⚠️ $BAD files with wrong owner"

log ""
log "═══ STARTUP COMPLETE ═══"
podman ps --format "table {{.Names}}\t{{.Status}}" | tee -a "$LOG"
log "Log: $LOG"
```

---

## 3. Full Recovery Procedure

When the entire stack needs to be rebuilt from scratch:

```bash
#!/usr/bin/env bash
# Full recovery from backup — use after catastrophic failure

echo "=== FULL STACK RECOVERY ==="
echo "This will reset all containers and restore from backup."
echo "Continue? [y/N]"; read -r CONFIRM
[ "$CONFIRM" = "y" ] || exit 0

VAULT="/media/arcana-novai/omega_vault/backups"
OMEGA=~/Documents/Xoe-NovAi/omega-stack

# 1. Stop everything
podman stop --all --time 30

# 2. Restore .gemini from latest backup
LATEST=$(ls -t "${VAULT}/daily/" | head -1)
rsync -az "${VAULT}/daily/${LATEST}/gemini_repo/" "${OMEGA}/.gemini/"
sudo chown -R arcana-novai:arcana-novai "${OMEGA}/.gemini/"

# 3. Restore database
LATEST_DB=$(ls -t "${VAULT}/databases/postgres_*.sql.gz" | head -1)
podman-compose up -d postgres
sleep 15
zcat "$LATEST_DB" | podman exec -i postgres psql -U postgres
echo "✅ Database restored from: $LATEST_DB"

# 4. Apply all permission layers
bash "${OMEGA}/scripts/permissions/layer1_restore.sh"
bash "${OMEGA}/scripts/permissions/layer2_acl_setup.sh"

# 5. Start stack in order
bash "${OMEGA}/scripts/omega_start.sh"

# 6. Verify
bash "${OMEGA}/scripts/verify/full_stack_verify.sh"
```

---

## 4. Rollback Procedures

### Layer-by-Layer Rollback

```bash
# Rollback Layer 2 (remove ACLs)
rollback_acls() {
  setfacl -R -b ~/Documents/Xoe-NovAi/omega-stack/.gemini/
  setfacl -R -b ~/.gemini/ 2>/dev/null || true
  echo "ACLs removed — standard permission model restored"
}

# Rollback Layer 3 (revert to default namespace)
rollback_userns() {
  # Edit docker-compose.yml to remove userns_mode: keep-id
  sed -i '/userns_mode: keep-id/d' ~/Documents/Xoe-NovAi/omega-stack/docker-compose.yml
  sed -i '/user: "1000:1000"/d' ~/Documents/Xoe-NovAi/omega-stack/docker-compose.yml
  podman-compose up -d
  echo "Namespace mode reverted to default"
}

# Rollback Layer 4 (disable timer)
rollback_timer() {
  systemctl --user disable --now acl_drift_monitor.timer 2>/dev/null || true
  echo "ACL repair timer disabled"
}
```

---

## 5. Post-Deployment Validation

```bash
# Run full verification suite
bash ~/Documents/Xoe-NovAi/omega-stack/scripts/verify/full_stack_verify.sh

# Then test each dev tool manually:
echo "Manual tool tests to complete:"
echo "  1. Open VS Code in omega-stack/ — should see no workspace trust warnings"
echo "  2. Run: gemini --version  — should respond without auth errors"  
echo "  3. Run Cline task — should persist memory to ~/.gemini/memory/"
echo "  4. Check Copilot CLI — should not enter login loop"
echo "  5. Restart containers and re-verify — permissions should survive"
```

---

## 6. Maintenance Schedule

| Task | Frequency | Script | Automated? |
|------|-----------|--------|-----------|
| ACL drift repair | Every 15 min | `acl_repair.sh` | ✅ systemd timer |
| Health alerts | Every 5 min | `alert_check.sh` | ✅ systemd timer |
| Daily backup | Daily 2:00 AM | `daily_backup.sh` | ✅ systemd timer |
| Weekly backup | Sunday 2:00 AM | `weekly_backup.sh` | ✅ systemd timer |
| DB dump | Daily | `db_backup.sh` | ✅ via daily backup |
| Storage cleanup | Monthly | IMPL-01 §4 | ❌ Manual |
| Credential rotation | Quarterly | SUPP-02 §2 | ❌ Manual |
| Log rotation | Daily | `/etc/logrotate.d/omega-stack` | ✅ logrotate |
| Full verification | Weekly | `full_stack_verify.sh` | ❌ Manual |
