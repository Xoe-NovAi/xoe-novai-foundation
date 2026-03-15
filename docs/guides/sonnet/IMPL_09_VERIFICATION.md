---
title: "Omega-Stack Implementation Manual 09: Full Stack Verification & Confidence Assessment"
section: "09"
scope: "Post-implementation verification, cross-section validation, confidence scoring"
status: "Reference — Run After All Other Manuals"
priority: "P2 — Final Quality Gate"
last_updated: "2026-03-13"
---

# IMPL-09 — Full Stack Verification & Confidence Assessment
## Omega-Stack Agent Implementation Manual

> **🤖 AGENT DIRECTIVE:** Run this verification suite after completing all P0 and P1 remediation. Each check returns a pass/fail result. All 10 categories should pass before declaring the stack stable.

---

## Master Verification Script

```bash
#!/usr/bin/env bash
# ~/omega-stack/scripts/verify/full_stack_verify.sh
# Run after all IMPL and SUPP manuals are complete

PASS=0; FAIL=0; WARN=0
ok()   { echo "✅ $1"; PASS=$((PASS+1)); }
fail() { echo "❌ $1"; FAIL=$((FAIL+1)); }
warn() { echo "⚠️  $1"; WARN=$((WARN+1)); }

OMEGA=~/Documents/Xoe-NovAi/omega-stack
REPO_GEMINI="${OMEGA}/.gemini"

echo "╔══════════════════════════════════════════════╗"
echo "║  OMEGA-STACK FULL VERIFICATION SUITE         ║"
echo "║  $(date '+%Y-%m-%d %H:%M:%S')                      ║"
echo "╚══════════════════════════════════════════════╝"

echo ""
echo "── 1. INFRASTRUCTURE ─────────────────────────"
DISK=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
[ "$DISK" -lt 85 ] && ok "Disk <85% (${DISK}%)" || fail "Disk at ${DISK}% — cleanup needed"
SWAP=$(free | grep Swap | awk '{printf "%d", $3/$2*100}')
[ "$SWAP" -lt 60 ] && ok "Swap <60% (${SWAP}%)" || warn "Swap at ${SWAP}%"
loginctl show-user "$(whoami)" | grep -q 'Linger=yes' && ok "User lingering enabled" || fail "Lingering disabled"
grep -q arcana-novai /etc/subuid && ok "subuid mapping present" || fail "subuid missing"

echo ""
echo "── 2. CONTAINER ORCHESTRATION ────────────────"
for SVC in redis postgres memory-bank-mcp; do
  podman healthcheck run "$SVC" &>/dev/null && ok "$SVC: healthy" || fail "$SVC: unhealthy"
done
UNHEALTHY=$(podman ps --filter "health=unhealthy" --format "{{.Names}}" 2>/dev/null | wc -l)
[ "$UNHEALTHY" -eq 0 ] && ok "No unhealthy containers" || warn "$UNHEALTHY containers unhealthy"

echo ""
echo "── 3. PERMISSION LAYERS ──────────────────────"
BAD_OWNER=$(find "$REPO_GEMINI" -not -user arcana-novai 2>/dev/null | wc -l)
[ "$BAD_OWNER" -eq 0 ] && ok "All .gemini files owned by arcana-novai" || fail "$BAD_OWNER files with wrong owner"

getfacl "$REPO_GEMINI" 2>/dev/null | grep -q "default:user:1000:rwx" && \
  ok "Default ACL u:1000:rwx present" || fail "Default ACL missing"

MASK=$(getfacl -p "$REPO_GEMINI" 2>/dev/null | grep '^mask' | cut -d: -f3)
[ "$MASK" = "rwx" ] && ok "ACL mask is rwx" || fail "ACL mask is '${MASK}'"

MODE=$(podman inspect memory-bank-mcp --format '{{.HostConfig.UsernsMode}}' 2>/dev/null || echo "unknown")
[ "$MODE" = "keep-id" ] && ok "memory-bank-mcp: keep-id namespace" || warn "memory-bank-mcp: namespace=$MODE"

systemctl --user is-active acl_drift_monitor.timer &>/dev/null && \
  ok "ACL drift repair timer active" || fail "ACL repair timer NOT active"

echo ""
echo "── 4. MCP SERVER ECOSYSTEM ───────────────────"
for PORT in 8005 8006 8009 8010 8011; do
  curl -sf "http://localhost:${PORT}/health" &>/dev/null && \
    ok "MCP port $PORT responding" || warn "MCP port $PORT not responding"
done

echo ""
echo "── 5. TOOL INTEGRATION ───────────────────────"
GEMINI=~/.gemini
[ -r "${GEMINI}/settings.json" ]      && ok "settings.json readable" || fail "settings.json BLOCKED"
[ -r "${GEMINI}/trustedFolders.json" ] && ok "trustedFolders.json readable" || fail "trustedFolders.json BLOCKED"
[ -w "${GEMINI}/memory" ]             && ok "memory/ writable (Cline)" || fail "memory/ BLOCKED"
CRED_MODE=$(stat -c '%a' "${GEMINI}/oauth_creds.json" 2>/dev/null || echo "missing")
[ "$CRED_MODE" = "600" ] && ok "oauth_creds.json secured (600)" || warn "oauth_creds.json mode: $CRED_MODE"

echo ""
echo "── 6. SECRETS ────────────────────────────────"
! grep -q 'changeme' "${OMEGA}/.env" 2>/dev/null && \
  ok "No default passwords in .env" || fail "Default passwords still present"
grep -q '\.env' "${OMEGA}/.gitignore" 2>/dev/null && \
  ok ".env in .gitignore" || fail ".env not in .gitignore"

echo ""
echo "── 7. MONITORING ─────────────────────────────"
curl -sf http://localhost:8428/health &>/dev/null && ok "VictoriaMetrics healthy" || warn "VictoriaMetrics not responding"
curl -sf http://localhost:3000/health &>/dev/null && ok "Grafana healthy" || warn "Grafana not responding"
systemctl --user is-active omega-alert.timer &>/dev/null && ok "Alert timer active" || warn "Alert timer not installed"

echo ""
echo "── 8. BACKUP ─────────────────────────────────"
mountpoint -q /media/arcana-novai/omega_vault && ok "Vault mounted" || warn "Vault not mounted"
systemctl --user is-active omega-backup-daily.timer &>/dev/null && ok "Daily backup timer active" || warn "Daily backup timer not installed"
LATEST_BACKUP=$(ls -t /media/arcana-novai/omega_vault/backups/daily/ 2>/dev/null | head -1)
[ -n "$LATEST_BACKUP" ] && ok "Recent backup exists: $LATEST_BACKUP" || warn "No backups found"

echo ""
echo "── 9. QUADLETS / SYSTEMD SERVICES ───────────"
systemctl --user is-active acl_drift_monitor.timer &>/dev/null && ok "ACL timer: active" || fail "ACL timer: inactive"
systemctl --user is-active omega-alert.timer &>/dev/null && ok "Alert timer: active" || warn "Alert timer: not installed"

echo ""
echo "╔══════════════════════════════════════════════╗"
printf "║  RESULTS: ✅ %3d pass  ❌ %3d fail  ⚠️  %3d warn ║\n" "$PASS" "$FAIL" "$WARN"
CONFIDENCE=$(awk "BEGIN {printf \"%d\", ($PASS / ($PASS+$FAIL+$WARN)) * 100}" 2>/dev/null || echo "?")
printf "║  CONFIDENCE: %3d%%                            ║\n" "$CONFIDENCE"
echo "╚══════════════════════════════════════════════╝"

[ "$FAIL" -eq 0 ] && echo "🎉 All critical checks passed!" || echo "🔧 $FAIL critical items need attention — see failures above"
```

---

## Known Assumptions & Unknowns

| Assumption | Confidence | Investigation |
|-----------|------------|--------------|
| Crush tool purpose | 50% | Needs documentation review |
| SambaNova API key available | 70% | Check .env for SAMBANOVA_API_KEY |
| Facet specialization vs config | 85% | Verify per-facet MCP assignment in mcp_config.json |
| Memory overcommit intentional | 85% | No documentation found — assume yes but add limits |
