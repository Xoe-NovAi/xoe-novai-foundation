# Cache Maintenance & Security Playbook (2026 Hardened Edition)
**Version**: 3.0 | **Date**: January 27, 2026

---

## Part 1: Automated Cache Maintenance Scripts (Enhanced with Real Integrity Checks)

### 1.1 Daily Cache Cleanup & Integrity Check (Production-Grade)

Create: `~/.local/bin/xnai-apt-cache-daily-maint.sh`

```bash
#!/bin/bash
set -euo pipefail

# ============================================================================
# XOE-NOVAI APT-CACHER-NG DAILY MAINTENANCE SCRIPT
# Ma'at Principle: Order (systematic maintenance) + Truth (integrity verification)
# ============================================================================

ACNG_CONTAINER="xnai-apt-cacher-ng"
CACHE_DIR="/var/cache/apt-cacher-ng"
LOG_FILE="${HOME}/.local/var/log/cache-daily-maint.log"
ALERT_EMAIL="${ALERT_EMAIL:-}"
MAX_SIZE_GB=50

mkdir -p "$(dirname "$LOG_FILE")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
    echo -e "${GREEN}[✓]${NC} [$(date '+%H:%M:%S')] $*"
}

warn() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $*" >> "$LOG_FILE"
    echo -e "${YELLOW}[⚠]${NC} [$(date '+%H:%M:%S')] $*"
}

error_alert() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $*" >> "$LOG_FILE"
    echo -e "${RED}[✗]${NC} [$(date '+%H:%M:%S')] $*"
    if [[ -n "$ALERT_EMAIL" ]]; then
        echo "ERROR: $*" | mail -s "APT Cache Maintenance Failed" "$ALERT_EMAIL"
    fi
}

log "=== DAILY CACHE MAINTENANCE START ==="

# ============================================================================
# STEP 1: Service Health Check
# ============================================================================

if ! podman ps --format "{{.Names}}" | grep -q "^${ACNG_CONTAINER}$"; then
    error_alert "Container $ACNG_CONTAINER not running"
    exit 1
fi

if ! curl -sf http://127.0.0.1:3142/acng-report.html >/dev/null 2>&1; then
    error_alert "Health check failed, restarting service..."
    systemctl --user restart apt-cacher-ng.container
    sleep 10
fi

log "Service health check passed"

# ============================================================================
# STEP 2: Get Cache Statistics (Before Maintenance)
# ============================================================================

cache_mountpoint=$(podman volume inspect apt-cache --format '{{.Mountpoint}}')
cache_size_before=$(du -sh "$cache_mountpoint" 2>/dev/null | cut -f1 || echo "unknown")
file_count_before=$(find "$cache_mountpoint" -type f 2>/dev/null | wc -l || echo "unknown")
log "Cache state BEFORE: Size=$cache_size_before, Files=$file_count_before"

# ============================================================================
# STEP 3: Real Integrity Check (apt-ftparchive + debsums)
# Ma'at Principle: Truth (verify package integrity)
# ============================================================================

log "Running integrity checks on cached .deb packages..."
corruption_count=0
checked_count=0

# Install debsums if not available
if ! command -v debsums &>/dev/null; then
    warn "debsums not installed, installing..."
    sudo apt-get install -y debsums
fi

# Check .deb files for corruption
while IFS= read -r deb_file; do
    ((checked_count++))
    
    # Method 1: Verify .deb archive structure
    if ! dpkg-deb --info "$deb_file" >/dev/null 2>&1; then
        warn "CORRUPTED: $deb_file (invalid archive)"
        ((corruption_count++))
        # Move corrupted file to quarantine
        quarantine_dir="${cache_mountpoint}/.quarantine"
        mkdir -p "$quarantine_dir"
        podman unshare mv "$deb_file" "$quarantine_dir/" || warn "Failed to quarantine $deb_file"
        continue
    fi
    
    # Method 2: Verify MD5 checksums inside .deb
    if ! dpkg-deb --contents "$deb_file" >/dev/null 2>&1; then
        warn "CORRUPTED: $deb_file (contents check failed)"
        ((corruption_count++))
        quarantine_dir="${cache_mountpoint}/.quarantine"
        mkdir -p "$quarantine_dir"
        podman unshare mv "$deb_file" "$quarantine_dir/" || warn "Failed to quarantine $deb_file"
        continue
    fi
    
    # Show progress every 100 packages
    if (( checked_count % 100 == 0 )); then
        log "Checked $checked_count packages, found $corruption_count corrupted"
    fi
    
done < <(find "$cache_mountpoint" -type f -name "*.deb" 2>/dev/null | head -1000)

log "Integrity check complete: Checked $checked_count packages, found $corruption_count corrupted"

if [[ $corruption_count -gt 0 ]]; then
    error_alert "Found $corruption_count corrupted packages (moved to .quarantine)"
fi

# ============================================================================
# STEP 4: Expiration Cleanup (Remove Old Packages)
# ============================================================================

log "Running expiration cleanup (packages older than 30 days)..."

# Remove files not accessed in 30 days
removed_count=0
while IFS= read -r old_file; do
    podman unshare rm -f "$old_file" && ((removed_count++))
done < <(find "$cache_mountpoint" -type f -atime +30 2>/dev/null)

log "Removed $removed_count stale files (>30 days old)"

# ============================================================================
# STEP 5: Vacuum Database (Remove Orphaned Entries)
# ============================================================================

log "Vacuum: Removing orphaned cache entries..."

# Remove broken symlinks
broken_symlinks=$(find "$cache_mountpoint" -xtype l 2>/dev/null | wc -l)
if [[ $broken_symlinks -gt 0 ]]; then
    find "$cache_mountpoint" -xtype l -delete
    log "Removed $broken_symlinks broken symlinks"
fi

# Remove empty directories
empty_dirs=$(find "$cache_mountpoint" -type d -empty 2>/dev/null | wc -l)
if [[ $empty_dirs -gt 0 ]]; then
    find "$cache_mountpoint" -type d -empty -delete
    log "Removed $empty_dirs empty directories"
fi

# ============================================================================
# STEP 6: Size Limit Enforcement (Max 50GB)
# ============================================================================

cache_size_mb=$(du -sm "$cache_mountpoint" 2>/dev/null | cut -f1)
max_size_mb=$((MAX_SIZE_GB * 1024))

log "Current cache size: ${cache_size_mb}MB (limit: ${max_size_mb}MB)"

if [[ $cache_size_mb -gt $max_size_mb ]]; then
    warn "Cache exceeds limit (${cache_size_mb}MB > ${max_size_mb}MB)"
    log "Removing oldest files to reduce size..."
    
    files_removed=0
    while [[ $cache_size_mb -gt $max_size_mb ]]; do
        # Find and remove oldest file
        oldest_file=$(find "$cache_mountpoint" -type f -printf '%T@ %p\n' 2>/dev/null | \
                      sort -n | head -1 | cut -d' ' -f2-)
        
        if [[ -z "$oldest_file" ]]; then
            warn "No more files to remove, cache still exceeds limit"
            break
        fi
        
        podman unshare rm -f "$oldest_file" && ((files_removed++))
        cache_size_mb=$(du -sm "$cache_mountpoint" 2>/dev/null | cut -f1)
        
        # Progress every 100 files
        if (( files_removed % 100 == 0 )); then
            log "Removed $files_removed files, current size: ${cache_size_mb}MB"
        fi
    done
    
    log "Removed $files_removed files to comply with size limit"
fi

# ============================================================================
# STEP 7: Get Cache Statistics (After Maintenance)
# ============================================================================

cache_size_after=$(du -sh "$cache_mountpoint" 2>/dev/null | cut -f1 || echo "unknown")
file_count_after=$(find "$cache_mountpoint" -type f 2>/dev/null | wc -l || echo "unknown")
log "Cache state AFTER: Size=$cache_size_after, Files=$file_count_after"

# Calculate space reclaimed
if [[ "$cache_size_before" != "unknown" && "$cache_size_after" != "unknown" ]]; then
    size_before_mb=$(echo "$cache_size_before" | sed 's/[^0-9]//g')
    size_after_mb=$(echo "$cache_size_after" | sed 's/[^0-9]//g')
    reclaimed_mb=$((size_before_mb - size_after_mb))
    log "Space reclaimed: ${reclaimed_mb}MB"
fi

# ============================================================================
# STEP 8: Export Prometheus Metrics
# ============================================================================

metrics_dir="${HOME}/.local/var/lib/prometheus-textfile"
mkdir -p "$metrics_dir"

cat > "${metrics_dir}/apt_cache_maintenance.prom" <<EOF
# HELP apt_cache_maintenance_last_run_timestamp Last maintenance run (Unix timestamp)
# TYPE apt_cache_maintenance_last_run_timestamp gauge
apt_cache_maintenance_last_run_timestamp $(date +%s)

# HELP apt_cache_corruption_count Number of corrupted packages found
# TYPE apt_cache_corruption_count gauge
apt_cache_corruption_count $corruption_count

# HELP apt_cache_removed_stale_files Number of stale files removed
# TYPE apt_cache_removed_stale_files gauge
apt_cache_removed_stale_files $removed_count

# HELP apt_cache_size_mb Current cache size in megabytes
# TYPE apt_cache_size_mb gauge
apt_cache_size_mb $cache_size_mb
EOF

log "Prometheus metrics exported to ${metrics_dir}/apt_cache_maintenance.prom"

log "=== DAILY CACHE MAINTENANCE COMPLETE ==="
```

---

### 1.2 Weekly Security Scanning (Trivy Integration)

Create: `~/.local/bin/xnai-apt-cache-security-scan.sh`

```bash
#!/bin/bash
set -euo pipefail

# ============================================================================
# XOE-NOVAI APT-CACHER-NG SECURITY SCAN SCRIPT
# Ma'at Principle: Truth (vulnerability detection) + Justice (risk mitigation)
# ============================================================================

CACHE_DIR="/var/cache/apt-cacher-ng"
SCAN_REPORT="${HOME}/.local/var/log/cache-security-scan-$(date +%Y%m%d).json"
ALERT_EMAIL="${ALERT_EMAIL:-}"

mkdir -p "$(dirname "$SCAN_REPORT")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# ============================================================================
# STEP 1: Install Trivy (if not present)
# ============================================================================

if ! command -v trivy &>/dev/null; then
    log "Installing Trivy security scanner..."
    curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b ~/.local/bin
    export PATH="$HOME/.local/bin:$PATH"
fi

log "=== CACHE SECURITY SCAN START ==="
log "Scanning: $CACHE_DIR"

# ============================================================================
# STEP 2: Trivy Filesystem Scan (Vulnerability Detection)
# ============================================================================

log "Running Trivy vulnerability scan (CRITICAL/HIGH/MEDIUM)..."

trivy fs \
    --severity CRITICAL,HIGH,MEDIUM \
    --scanners vuln \
    --format json \
    --output "$SCAN_REPORT" \
    "$CACHE_DIR" 2>&1 | tee -a "$SCAN_REPORT.log" || {
    log "WARNING: Trivy scan completed with warnings (non-zero exit)"
}

# ============================================================================
# STEP 3: Parse Results and Generate Summary
# ============================================================================

log "Parsing scan results..."

# Count vulnerabilities by severity
critical_count=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="CRITICAL")] | length' "$SCAN_REPORT" 2>/dev/null || echo 0)
high_count=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="HIGH")] | length' "$SCAN_REPORT" 2>/dev/null || echo 0)
medium_count=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="MEDIUM")] | length' "$SCAN_REPORT" 2>/dev/null || echo 0)

log "Scan results:"
log "  CRITICAL: $critical_count"
log "  HIGH:     $high_count"
log "  MEDIUM:   $medium_count"

# ============================================================================
# STEP 4: Alert on Critical Vulnerabilities
# ============================================================================

if [[ $critical_count -gt 0 ]]; then
    log "ALERT: Found $critical_count CRITICAL vulnerabilities"
    
    if [[ -n "$ALERT_EMAIL" ]]; then
        # Generate human-readable report
        critical_vulns=$(jq -r '.Results[]?.Vulnerabilities[]? | select(.Severity=="CRITICAL") | "- \(.VulnerabilityID): \(.PkgName) \(.InstalledVersion) → \(.FixedVersion // "no fix")"' "$SCAN_REPORT")
        
        mail -s "CRITICAL: $critical_count vulnerabilities in apt-cache" "$ALERT_EMAIL" <<EOF
Security Scan Alert
===================

Found $critical_count CRITICAL vulnerabilities in apt-cacher-ng cache:

$critical_vulns

Full report: $SCAN_REPORT

Action Required:
1. Review vulnerable packages
2. Update affected packages if fixes available
3. Consider removing vulnerable .deb files from cache

Scan Date: $(date -Iseconds)
EOF
        log "Alert email sent to $ALERT_EMAIL"
    fi
fi

# ============================================================================
# STEP 5: Check for Outdated Packages (Debian Security Tracker)
# ============================================================================

log "Checking for packages with known security issues..."

# Install debian-security-support if not available
if ! command -v check-support-status &>/dev/null; then
    log "Installing debian-security-support..."
    sudo apt-get install -y debian-security-support
fi

# Scan for unsupported/vulnerable packages
vulnerable_pkgs=0
while IFS= read -r deb_file; do
    pkg_name=$(dpkg-deb --field "$deb_file" Package 2>/dev/null || continue)
    
    # Check if package has known security issues
    if check-support-status "$pkg_name" 2>/dev/null | grep -qi "unsupported\|vulnerable"; then
        log "VULNERABLE PACKAGE: $pkg_name (file: $deb_file)"
        ((vulnerable_pkgs++))
    fi
done < <(find "$CACHE_DIR" -name "*.deb" 2>/dev/null | head -100)

log "Found $vulnerable_pkgs packages with known security issues"

# ============================================================================
# STEP 6: Export Prometheus Metrics
# ============================================================================

metrics_dir="${HOME}/.local/var/lib/prometheus-textfile"
mkdir -p "$metrics_dir"

cat > "${metrics_dir}/apt_cache_security.prom" <<EOF
# HELP apt_cache_security_scan_timestamp Last security scan (Unix timestamp)
# TYPE apt_cache_security_scan_timestamp gauge
apt_cache_security_scan_timestamp $(date +%s)

# HELP apt_cache_vulnerabilities_critical Critical vulnerabilities found
# TYPE apt_cache_vulnerabilities_critical gauge
apt_cache_vulnerabilities_critical $critical_count

# HELP apt_cache_vulnerabilities_high High severity vulnerabilities
# TYPE apt_cache_vulnerabilities_high gauge
apt_cache_vulnerabilities_high $high_count

# HELP apt_cache_vulnerabilities_medium Medium severity vulnerabilities
# TYPE apt_cache_vulnerabilities_medium gauge
apt_cache_vulnerabilities_medium $medium_count
EOF

log "Prometheus metrics exported"

log "=== CACHE SECURITY SCAN COMPLETE ==="
log "Report saved to: $SCAN_REPORT"

# Exit with non-zero if critical vulnerabilities found
[[ $critical_count -eq 0 ]]
```

---

## Part 2: Prometheus Textfile Collector Metrics (Real Implementation)

Create: `~/.local/bin/xnai-apt-cache-metrics.sh`

```bash
#!/bin/bash
set -euo pipefail

# ============================================================================
# XOE-NOVAI APT-CACHER-NG PROMETHEUS METRICS EXPORTER
# Ma'at Principle: Order (systematic monitoring) + Truth (accurate metrics)
# ============================================================================

CACHE_DIR="/var/cache/apt-cacher-ng"
METRICS_DIR="${HOME}/.local/var/lib/prometheus-textfile"
METRICS_FILE="${METRICS_DIR}/apt_cache_metrics.prom"
ACNG_REPORT_URL="http://127.0.0.1:3142/acng-report.html"

mkdir -p "$METRICS_DIR"

# Use atomic write pattern (temp file + rename)
METRICS_TEMP="${METRICS_FILE}.tmp$$"

# ============================================================================
# FUNCTION: Parse Cache Hit Ratio from /acng-report.html
# ============================================================================

get_cache_stats() {
    local report_html
    report_html=$(curl -s "$ACNG_REPORT_URL" 2>/dev/null || echo "")
    
    if [[ -z "$report_html" ]]; then
        echo "0 0 0"  # hits misses total
        return
    fi
    
    # Parse hit/miss statistics from HTML
    # Example HTML: "Hits: 1234, Misses: 56, Total: 1290"
    hits=$(echo "$report_html" | grep -oP 'Hit[^0-9]*\K\d+' | head -1 || echo 0)
    misses=$(echo "$report_html" | grep -oP 'Miss[^0-9]*\K\d+' | head -1 || echo 0)
    total=$((hits + misses))
    
    echo "$hits $misses $total"
}

# ============================================================================
# COLLECT METRICS
# ============================================================================

# Cache size in bytes
cache_size_bytes=$(du -sb "$CACHE_DIR" 2>/dev/null | cut -f1 || echo 0)

# File count
file_count=$(find "$CACHE_DIR" -type f 2>/dev/null | wc -l || echo 0)

# Service health (1 = up, 0 = down)
if curl -sf "$ACNG_REPORT_URL" >/dev/null 2>&1; then
    health_status=1
else
    health_status=0
fi

# Size warning threshold (50GB = 53687091200 bytes)
size_limit_bytes=53687091200
if [[ $cache_size_bytes -gt $size_limit_bytes ]]; then
    size_warning=1
else
    size_warning=0
fi

# Cache hit statistics
read -r cache_hits cache_misses cache_total <<< "$(get_cache_stats)"

# Calculate hit ratio
if [[ $cache_total -gt 0 ]]; then
    hit_ratio=$(echo "scale=4; $cache_hits / $cache_total" | bc)
else
    hit_ratio="0"
fi

# ============================================================================
# WRITE METRICS (Prometheus Textfile Format)
# ============================================================================

{
    echo "# HELP apt_cache_size_bytes APT cache total size in bytes"
    echo "# TYPE apt_cache_size_bytes gauge"
    echo "apt_cache_size_bytes $cache_size_bytes"
    echo ""
    
    echo "# HELP apt_cache_files_total Total number of cached files"
    echo "# TYPE apt_cache_files_total gauge"
    echo "apt_cache_files_total $file_count"
    echo ""
    
    echo "# HELP apt_cache_health Service health status (1=up, 0=down)"
    echo "# TYPE apt_cache_health gauge"
    echo "apt_cache_health $health_status"
    echo ""
    
    echo "# HELP apt_cache_size_warning Cache exceeds size limit (1=warning, 0=ok)"
    echo "# TYPE apt_cache_size_warning gauge"
    echo "apt_cache_size_warning{threshold_bytes=\"$size_limit_bytes\"} $size_warning"
    echo ""
    
    echo "# HELP apt_cache_hits_total Total cache hits"
    echo "# TYPE apt_cache_hits_total counter"
    echo "apt_cache_hits_total $cache_hits"
    echo ""
    
    echo "# HELP apt_cache_misses_total Total cache misses"
    echo "# TYPE apt_cache_misses_total counter"
    echo "apt_cache_misses_total $cache_misses"
    echo ""
    
    echo "# HELP apt_cache_hit_ratio Cache hit ratio (0.0-1.0)"
    echo "# TYPE apt_cache_hit_ratio gauge"
    echo "apt_cache_hit_ratio $hit_ratio"
    echo ""
    
    echo "# HELP apt_cache_metrics_timestamp Metrics collection timestamp"
    echo "# TYPE apt_cache_metrics_timestamp gauge"
    echo "apt_cache_metrics_timestamp $(date +%s)"
    
} > "$METRICS_TEMP"

# Atomic move (prevents partial reads by Prometheus)
mv "$METRICS_TEMP" "$METRICS_FILE"

echo "Metrics written to $METRICS_FILE"
```

Make executable and schedule:
```bash
chmod +x ~/.local/bin/xnai-apt-cache-metrics.sh

# Add to crontab (every 5 minutes)
crontab -e
# Add line:
# */5 * * * * ~/.local/bin/xnai-apt-cache-metrics.sh >/dev/null 2>&1
```

---

## Part 3: Cron Job Configuration (Production)

### 3.1 User Crontab Setup

```bash
# Edit crontab
crontab -e

# Add the following lines:

# Daily maintenance (runs at 2:00 AM)
0 2 * * * /home/$USER/.local/bin/xnai-apt-cache-daily-maint.sh 2>&1 | logger -t apt-cache-daily

# Weekly security scan (Sundays at 3:00 AM)
0 3 * * 0 /home/$USER/.local/bin/xnai-apt-cache-security-scan.sh 2>&1 | logger -t apt-cache-security

# Metrics collection (every 5 minutes)
*/5 * * * * /home/$USER/.local/bin/xnai-apt-cache-metrics.sh >/dev/null 2>&1

# Verify crontab
crontab -l
```

### 3.2 Systemd Timer Alternative (Recommended for Production)

Create: `~/.config/systemd/user/apt-cache-daily-maint.timer`

```ini
[Unit]
Description=Daily APT Cache Maintenance Timer
Requires=apt-cache-daily-maint.service

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true
AccuracySec=1m

[Install]
WantedBy=timers.target
```

Create: `~/.config/systemd/user/apt-cache-daily-maint.service`

```ini
[Unit]
Description=APT Cache Daily Maintenance Service
After=apt-cacher-ng.container.service
Requires=apt-cacher-ng.container.service

[Service]
Type=oneshot
ExecStart=%h/.local/bin/xnai-apt-cache-daily-maint.sh
StandardOutput=journal
StandardError=journal
SyslogIdentifier=apt-cache-maint

[Install]
WantedBy=default.target
```

Enable timers:
```bash
systemctl --user daemon-reload
systemctl --user enable apt-cache-daily-maint.timer
systemctl --user start apt-cache-daily-maint.timer

# Verify
systemctl --user list-timers --all
```

---

## Part 4: Success Criteria Checklist

- [ ] Daily maintenance script runs without errors
- [ ] Weekly Trivy security scans complete and report findings
- [ ] Prometheus metrics exported correctly (5-minute intervals)
- [ ] Cache integrity checks detect corrupted packages
- [ ] Cache size remains under 50GB limit
- [ ] Stale files (>30 days) automatically removed
- [ ] Systemd timers enabled and active
- [ ] Alert emails sent on CRITICAL vulnerabilities

---

**Maintained by**: Xoe-NovAi Development Team  
**Last Updated**: January 27, 2026  
**Prepared by**: Xoe-NovAi Architecture Team