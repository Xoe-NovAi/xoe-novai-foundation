---
title: "Omega-Stack Supplemental Manual SUPP-06: Monitoring, Alerting & Observability"
section: "SUPP-06"
scope: "VictoriaMetrics, Grafana recovery, Alerting rules, Journald, Health dashboards"
status: "Actionable — Restore Visibility to Degraded Stack"
owner: "arcana-novai (UID 1000)"
last_updated: "2026-03-13"
confidence: "95%"
priority: "P1 — No Monitoring Active While Stack is Degraded"
---

# SUPP-06 — Monitoring, Alerting & Observability
## Omega-Stack Supplemental Implementation Manual

> **🤖 AGENT DIRECTIVE:** Grafana is currently **unhealthy** and Caddy (the reverse proxy for the monitoring dashboard) is also down. This means there is **zero visibility** into the stack while it is in a degraded state. This manual restores observability and implements alerting rules for the four critical failure modes: disk crisis, memory cascade, service down, and permission drift.

---

## Table of Contents

1. [Observability Gap Assessment](#1-observability-gap-assessment)
2. [VictoriaMetrics — Confirm Metrics Collection](#2-victoriametrics--confirm-metrics-collection)
3. [Grafana Recovery & Dashboard Setup](#3-grafana-recovery--dashboard-setup)
4. [Critical Alert Rules](#4-critical-alert-rules)
5. [Journald Structured Logging](#5-journald-structured-logging)
6. [Omega-Stack Health Check Script](#6-omega-stack-health-check-script)
7. [Systemd Status Monitoring](#7-systemd-status-monitoring)
8. [Edge Cases & Failure Modes](#8-edge-cases--failure-modes)
9. [Verification Checklist](#9-verification-checklist)

---

## 1. Observability Gap Assessment

| Component | Status | Gap |
|-----------|--------|-----|
| VictoriaMetrics | ✅ Running (port 8428) | Metrics collecting; no alerts |
| Grafana | ❌ Unhealthy (port 3000) | Dashboard inaccessible |
| Caddy | ❌ Unhealthy (port 80/443) | No external proxy |
| Alerting | ❌ None configured | No notification of failures |
| Log aggregation | ⚠️ journald only | No central log view |
| Container health events | ⚠️ Unmonitored | OOM kills go unnoticed |

---

## 2. VictoriaMetrics — Confirm Metrics Collection

VictoriaMetrics is healthy but needs scrape targets configured.

### 2.1 Verify VictoriaMetrics

```bash
curl -sf http://localhost:8428/health && echo "✅ VictoriaMetrics healthy"
curl -sf http://localhost:8428/metrics | head -20  # Should show metric names
```

### 2.2 Configure Scrape Targets

```yaml
# ~/Documents/Xoe-NovAi/omega-stack/config/victoriametrics/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'podman-containers'
    static_configs:
      - targets: ['localhost:8005']  # memory-bank-mcp
        labels: { service: 'memory-bank-mcp', tier: 'api' }
      - targets: ['localhost:6333']  # qdrant
        labels: { service: 'qdrant', tier: 'api' }
      - targets: ['localhost:8102']  # rag_api
        labels: { service: 'rag_api', tier: 'integration' }
      - targets: ['localhost:8428']  # victoriametrics self
        labels: { service: 'victoriametrics', tier: 'observability' }

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']  # Add node_exporter for host metrics
        labels: { service: 'host', tier: 'infrastructure' }
```

### 2.3 Add Node Exporter for Host Metrics

```bash
# Add node_exporter to docker-compose.yml for host metrics
# This is critical for disk/memory alerts

cat >> ~/Documents/Xoe-NovAi/omega-stack/docker-compose.yml << 'EOF'

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    pid: host
    network_mode: host
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.ignored-mount-points=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped
    deploy:
      resources:
        limits: { memory: 64M }
EOF

podman-compose up -d node-exporter
```

---

## 3. Grafana Recovery & Dashboard Setup

### 3.1 Recover Grafana

```bash
# Check why Grafana is unhealthy
podman logs grafana --tail 30

# Common causes:
# 1. Database file locked (postgres dependency)
# 2. Config file missing
# 3. Memory limit exceeded

# Recovery
podman stop grafana
podman rm grafana 2>/dev/null || true
podman-compose up -d grafana

timeout 30 bash -c 'until curl -sf http://localhost:3000/health; do sleep 2; done' && \
  echo "✅ Grafana recovered" || echo "❌ Grafana still failing — check logs"
```

### 3.2 Grafana Datasource Configuration (API)

```bash
# Configure VictoriaMetrics as datasource via API
GRAFANA_PASS=$(grep GRAFANA_ADMIN_PASSWORD ~/Documents/Xoe-NovAi/omega-stack/.env 2>/dev/null | cut -d= -f2 || echo "admin")

curl -sf -X POST "http://admin:${GRAFANA_PASS}@localhost:3000/api/datasources" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "VictoriaMetrics",
    "type": "prometheus",
    "url": "http://victoriametrics:8428",
    "access": "proxy",
    "isDefault": true,
    "jsonData": {
      "timeInterval": "15s"
    }
  }' && echo "✅ Datasource configured"
```

### 3.3 Omega-Stack Dashboard JSON

```bash
# Create a minimal but functional dashboard via API
curl -sf -X POST "http://admin:${GRAFANA_PASS}@localhost:3000/api/dashboards/import" \
  -H "Content-Type: application/json" \
  -d '{
    "dashboard": {
      "title": "Omega-Stack Health",
      "panels": [
        {
          "title": "Disk Usage %",
          "type": "gauge",
          "datasource": "VictoriaMetrics",
          "targets": [{"expr": "100 - ((node_filesystem_avail_bytes{mountpoint=\"/\"} / node_filesystem_size_bytes{mountpoint=\"/\"}) * 100)", "legendFormat": "Root FS"}],
          "fieldConfig": {"defaults": {"thresholds": {"steps": [{"color":"green","value":0},{"color":"yellow","value":70},{"color":"orange","value":85},{"color":"red","value":93}]}}},
          "gridPos": {"x": 0, "y": 0, "w": 6, "h": 8}
        },
        {
          "title": "Memory Usage %",
          "type": "gauge",
          "datasource": "VictoriaMetrics",
          "targets": [{"expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100", "legendFormat": "RAM"}],
          "gridPos": {"x": 6, "y": 0, "w": 6, "h": 8}
        }
      ],
      "refresh": "30s",
      "schemaVersion": 30
    },
    "overwrite": true,
    "folderId": 0
  }' && echo "✅ Dashboard imported"
```

---

## 4. Critical Alert Rules

### 4.1 VictoriaMetrics Alert Rules

```yaml
# ~/Documents/Xoe-NovAi/omega-stack/config/victoriametrics/alerts.yaml
groups:
  - name: omega_stack_critical
    interval: 30s
    rules:

      # DISK ALERTS
      - alert: DiskCritical
        expr: 100 - ((node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100) > 90
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Root filesystem above 90%"
          description: "Disk usage is {{ $value | humanize }}%. Immediate cleanup required."

      - alert: DiskWarning
        expr: 100 - ((node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Root filesystem above 80%"

      # MEMORY ALERTS
      - alert: MemoryCritical
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Memory usage above 85%"

      - alert: SwapHigh
        expr: (node_memory_SwapTotal_bytes - node_memory_SwapFree_bytes) / node_memory_SwapTotal_bytes * 100 > 60
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Swap usage above 60% — performance degrading"

      # SERVICE ALERTS
      - alert: CriticalServiceDown
        expr: up{job="podman-containers", service=~"redis|postgres|memory-bank-mcp"} == 0
        for: 30s
        labels:
          severity: critical
        annotations:
          summary: "Critical service {{ $labels.service }} is DOWN"

      - alert: ServiceUnhealthy
        expr: up{job="podman-containers"} == 0
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Service {{ $labels.service }} unreachable for 2 minutes"

      # OOM ALERTS
      - alert: OOMKillDetected
        expr: increase(node_vmstat_oom_kill[5m]) > 0
        labels:
          severity: critical
        annotations:
          summary: "OOM kill event detected — a container was killed due to memory"
```

### 4.2 Lightweight Shell-Based Alerting (No Grafana Required)

If Grafana is still down, use this systemd-based alert system:

```bash
#!/usr/bin/env bash
# ~/omega-stack/scripts/monitoring/alert_check.sh
# Runs every 5 minutes via systemd timer

DISK_PCT=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
SWAP_USED=$(free | grep Swap | awk '{print int($3/$2*100)}')
MEM_USED=$(free | grep Mem | awk '{print int($3/$2*100)}')
UNHEALTHY=$(podman ps --filter "health=unhealthy" --format "{{.Names}}" | wc -l)

alert() {
  local LEVEL="$1" MSG="$2"
  echo "[$(date '+%Y-%m-%dT%H:%M:%S')] [$LEVEL] $MSG" | \
    systemd-cat -t omega-alert -p "$([[ $LEVEL == CRITICAL ]] && echo err || echo warning)"
}

# Check conditions
[ "$DISK_PCT" -gt 90 ]   && alert CRITICAL "Disk usage ${DISK_PCT}%  — IMMEDIATE ACTION REQUIRED"
[ "$DISK_PCT" -gt 80 ]   && alert WARNING  "Disk usage ${DISK_PCT}% — cleanup soon"
[ "$MEM_USED" -gt 85 ]   && alert CRITICAL "Memory usage ${MEM_USED}% — OOM risk"
[ "$SWAP_USED" -gt 60 ]  && alert WARNING  "Swap usage ${SWAP_USED}% — performance degraded"
[ "$UNHEALTHY" -gt 0 ]   && alert CRITICAL "$UNHEALTHY containers unhealthy: $(podman ps --filter 'health=unhealthy' --format '{{.Names}}' | tr '\n' ',')"

# Check for OOM kills in last 5 minutes
sudo dmesg --since "5min ago" 2>/dev/null | grep -qi 'oom\|killed process' && \
  alert CRITICAL "OOM kill detected in kernel log"
```

```ini
# ~/.config/systemd/user/omega-alert.timer
[Unit]
Description=Omega-Stack Health Alert Check

[Timer]
OnBootSec=1min
OnUnitActiveSec=5min
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
# Install alerting timer
cat > ~/.config/systemd/user/omega-alert.service << 'EOF'
[Unit]
Description=Omega-Stack Health Alert Check
[Service]
Type=oneshot
ExecStart=%h/Documents/Xoe-NovAi/omega-stack/scripts/monitoring/alert_check.sh
EOF

chmod +x ~/Documents/Xoe-NovAi/omega-stack/scripts/monitoring/alert_check.sh
systemctl --user daemon-reload
systemctl --user enable --now omega-alert.timer

# View alerts
journalctl --user -t omega-alert -f
```

---

## 5. Journald Structured Logging

### 5.1 Configure Persistent Journal

```bash
# Make journald retain logs across reboots
sudo mkdir -p /var/log/journal
sudo systemd-tmpfiles --create --prefix /var/log/journal

# Set log size limits
sudo tee -a /etc/systemd/journald.conf << 'EOF'

# Omega-Stack journal configuration
SystemMaxUse=2G
SystemKeepFree=1G
MaxRetentionSec=30days
MaxFileSec=1week
Compress=yes
EOF

sudo systemctl restart systemd-journald
```

### 5.2 Container Log Forwarding

```bash
# Forward container logs to journald (add to docker-compose.yml)
# Under each service that needs log retention:
#   logging:
#     driver: journald
#     options:
#       tag: "{{.Name}}"

# Query container logs from journald
journalctl -t qdrant --since "1 hour ago" --no-pager | tail -30
journalctl -t rag_api --since "1 hour ago" --no-pager | tail -30
```

---

## 6. Omega-Stack Health Check Script

```bash
#!/usr/bin/env bash
# ~/omega-stack/scripts/monitoring/omega_health.sh
# Comprehensive health report — run anytime

echo "╔═══════════════════════════════════════════════╗"
echo "║      OMEGA-STACK HEALTH REPORT                ║"
echo "║      $(date '+%Y-%m-%d %H:%M:%S')                  ║"
echo "╚═══════════════════════════════════════════════╝"

section() { echo ""; echo "── $1 ──────────────────────────────────────"; }

section "STORAGE"
df -h / /media/arcana-novai/omega_library /media/arcana-novai/omega_vault 2>/dev/null | \
  awk 'NR==1 || /\/$|omega/ {print}'

section "MEMORY"
free -h | grep -E 'Mem|Swap'

section "CONTAINER STATUS"
printf "%-25s %-15s %-10s\n" "SERVICE" "STATUS" "HEALTH"
printf "%-25s %-15s %-10s\n" "───────────────────────" "──────────────" "──────────"
podman ps -a --format "{{.Names}}\t{{.Status}}\t{{.Health}}" 2>/dev/null | \
  awk -F'\t' '{printf "%-25s %-15s %-10s\n", $1, $2, $3}'

section "SYSTEMD TIMERS"
systemctl --user list-timers --no-pager 2>/dev/null | grep -E '(NEXT|omega|acl)'

section "PERMISSION STATUS"
REPO_GEMINI="${HOME}/Documents/Xoe-NovAi/omega-stack/.gemini"
BAD=$(find "${REPO_GEMINI}" -not -user arcana-novai 2>/dev/null | wc -l)
echo "Files with wrong ownership: $BAD"
getfacl "${REPO_GEMINI}" 2>/dev/null | grep -E '(default:user|mask)' || echo "No ACLs set on .gemini"

section "ALERT SUMMARY"
journalctl --user -t omega-alert --since "1 hour ago" --no-pager 2>/dev/null | tail -10 || \
  echo "(Alert system not yet installed)"

echo ""
echo "════════════════════════════════════════════════"
```

---

## 7. Systemd Status Monitoring

```bash
# Check all omega-stack user services
systemctl --user status 'omega-*' 2>/dev/null || echo "No omega systemd services found"

# View recent failures
systemctl --user list-units --state=failed --no-pager

# Follow all omega logs in real time
journalctl --user -f -t omega-alert -t acl_drift_monitor
```

---

## 8. Edge Cases & Failure Modes

| Scenario | Detection | Resolution |
|----------|-----------|------------|
| Grafana PostgreSQL lock | `podman logs grafana` shows "database locked" | `podman exec grafana rm /var/lib/grafana/grafana.db-journal` then restart |
| VictoriaMetrics disk full | Metrics stop updating; `ENOSPC` in logs | Run storage cleanup (IMPL-01); VictoriaMetrics auto-recovers |
| node-exporter can't read /proc | Container permission denied | Requires `pid: host` in compose; restart with correct config |
| Alert timer stops after suspend | Timer not Persistent | Add `Persistent=true` to timer unit; already in template above |
| No `/health` endpoint on service | `curl: (7) Failed to connect` | Use TCP check instead: `nc -z localhost PORT` |

---

## 9. Verification Checklist

```bash
#!/usr/bin/env bash
echo "=== SUPP-06 MONITORING VERIFICATION ==="

curl -sf http://localhost:8428/health &>/dev/null && echo "✅ VictoriaMetrics healthy" || echo "❌ VictoriaMetrics down"
curl -sf http://localhost:3000/health &>/dev/null && echo "✅ Grafana healthy" || echo "❌ Grafana down"
curl -sf http://localhost:9100/metrics &>/dev/null | head -1 | grep -q "HELP" && echo "✅ node-exporter running" || echo "❌ node-exporter not running"
systemctl --user is-active omega-alert.timer &>/dev/null && echo "✅ Alert timer active" || echo "❌ Alert timer not installed"
systemctl --user is-active acl_drift_monitor.timer &>/dev/null && echo "✅ ACL repair timer active" || echo "❌ ACL repair timer not installed"

echo "=== END VERIFICATION ==="
```
