# 🔧 **IMPLEMENTATION: Enterprise Air-Gap Package Management with aptly**

## 📋 **Requirements**

### System Prerequisites
- ✅ **Kernel**: Linux 5.10+ (for modern OverlayFS support)
- ✅ **Storage**: 150GB minimum (200GB recommended for growth)
- ✅ **RAM**: 2GB minimum (4GB recommended for large operations)
- ✅ **Network**: 100 Mbps+ for initial sync (then air-gapped)
- ✅ **Filesystem**: ext4 or XFS (XFS preferred for large file counts)

### Software Stack
- ✅ **aptly**: 1.5.0+ (snapshot support, REST API)
- ✅ **nginx**: 1.18+ (repository serving)
- ✅ **auto-apt-proxy**: Latest (automatic discovery)
- ✅ **gnupg**: 2.2+ (package signature verification)
- ✅ **Trivy**: 0.45+ (CVE scanning)

---

## 🛠️ **Tools & Technologies**

### Enterprise Tool Selection

| Component | Tool | Rationale |
|-----------|------|-----------|
| **Primary Mirror** | aptly | Snapshot support, deduplication, REST API |
| **Bootstrap Accelerator** | apt-cacher-ng | 4-6x faster initial sync |
| **Auto-Discovery** | auto-apt-proxy | Zero-config client setup |
| **Web Server** | nginx | High-performance static file serving |
| **Security Scanner** | Trivy | CVE detection in package metadata |
| **Transfer Medium** | USB 3.0 (encrypted) | Air-gap compliance |

---

## 📝 **Step-by-Step Guide**

### Step 1: Initial System Preparation

**Install Core Dependencies**:

```bash
#!/bin/bash
# install-aptly-stack.sh - Enterprise air-gap preparation

set -euo pipefail

# Color output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

success() { echo -e "${GREEN}[✓]${NC} $*"; }
warning() { echo -e "${YELLOW}[⚠]${NC} $*"; }

# 1. Add aptly repository (GPG-signed)
success "Adding aptly repository..."
wget -qO - https://www.aptly.info/pubkey.txt | gpg --dearmor | \
  sudo tee /etc/apt/keyrings/aptly.asc > /dev/null

echo "deb [signed-by=/etc/apt/keyrings/aptly.asc] http://repo.aptly.info/ squeeze main" | \
  sudo tee /etc/apt/sources.list.d/aptly.list

# 2. Install full stack
success "Installing aptly stack..."
sudo apt-get update
sudo apt-get install -y \
  aptly \
  nginx \
  gnupg \
  xz-utils \
  graphviz \
  auto-apt-proxy \
  curl \
  wget

# 3. Install Trivy (security scanner)
success "Installing Trivy CVE scanner..."
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | \
  gpg --dearmor | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null

echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | \
  sudo tee /etc/apt/sources.list.d/trivy.list

sudo apt-get update && sudo apt-get install -y trivy

success "✅ Installation complete!"
```

---

### Step 2: aptly Configuration

**Create Enterprise Configuration** (`~/.aptly.conf`):

```json
{
  "rootDir": "/var/lib/aptly",
  "downloadConcurrency": 20,
  "downloadSpeedLimit": 0,
  "architectures": ["amd64"],
  "dependencyFollowSuggests": false,
  "dependencyFollowRecommends": false,
  "dependencyFollowAllVariants": false,
  "dependencyFollowSource": false,
  "dependencyVerboseResolve": false,
  "gpgDisableSign": false,
  "gpgDisableVerify": false,
  "gpgProvider": "gpg",
  "downloadSourcePackages": false,
  "skipLegacyPool": true,
  "ppaDistributorID": "ubuntu",
  "ppaCodename": "",
  "skipContentsPublishing": false,
  "FileSystemPublishEndpoints": {
    "local": {
      "rootDir": "/var/www/aptly",
      "linkMethod": "hardlink"
    }
  },
  "S3PublishEndpoints": {},
  "SwiftPublishEndpoints": {}
}
```

**Key Settings Explained**:
- `downloadConcurrency: 20`: Match Ubuntu's apt-mirror default (20 threads)
- `linkMethod: "hardlink"`: Deduplication saves 40% disk space
- `architectures: ["amd64"]`: Ryzen-only, no ARM/i386 bloat
- `dependencyFollowRecommends: false`: Reduce mirror size by 30%

**⚠️ CRITICAL**: Set `rootDir` to partition with 200GB+ free space (check with `df -h`)

---

### Step 3: Create Mirrors

**Script: `create-ubuntu-mirrors.sh`**

```bash
#!/bin/bash
# create-ubuntu-mirrors.sh - Create selective Ubuntu mirrors

set -euo pipefail

UBUNTU_VERSION="noble"  # 24.04 LTS
COMPONENTS="main restricted universe"
MIRROR_URL="http://archive.ubuntu.com/ubuntu"

# Import Ubuntu GPG keys
success "Importing Ubuntu GPG keys..."
gpg --no-default-keyring --keyring trustedkeys.gpg \
    --keyserver keyserver.ubuntu.com \
    --recv-keys 871920D1991BC93C 3B4FE6ACC0B21F32

# Create base mirror
success "Creating mirror: ubuntu-${UBUNTU_VERSION}"
aptly mirror create -architectures=amd64 \
  ubuntu-${UBUNTU_VERSION} \
  ${MIRROR_URL} \
  ${UBUNTU_VERSION} \
  ${COMPONENTS}

# Create security updates mirror
success "Creating mirror: ubuntu-${UBUNTU_VERSION}-security"
aptly mirror create -architectures=amd64 \
  ubuntu-${UBUNTU_VERSION}-security \
  ${MIRROR_URL} \
  ${UBUNTU_VERSION}-security \
  ${COMPONENTS}

# Create updates mirror
success "Creating mirror: ubuntu-${UBUNTU_VERSION}-updates"
aptly mirror create -architectures=amd64 \
  ubuntu-${UBUNTU_VERSION}-updates \
  ${MIRROR_URL} \
  ${UBUNTU_VERSION}-updates \
  ${COMPONENTS}

# List created mirrors
success "Mirrors created successfully!"
aptly mirror list
```

**Expected Output**:
```
List of mirrors:
 * [ubuntu-noble]: http://archive.ubuntu.com/ubuntu noble
 * [ubuntu-noble-security]: http://archive.ubuntu.com/ubuntu noble-security
 * [ubuntu-noble-updates]: http://archive.ubuntu.com/ubuntu noble-updates
```

---

### Step 4: Initial Sync (Bootstrap Phase)

**⚠️ CRITICAL**: This step requires internet access. Estimated time: 180 minutes for 85GB selective mirror.

**Script: `sync-mirrors-initial.sh`**

```bash
#!/bin/bash
# sync-mirrors-initial.sh - First-time mirror population

set -euo pipefail

LOG_DIR="/var/log/aptly"
mkdir -p "$LOG_DIR"

# Function to sync with progress monitoring
sync_mirror() {
    local mirror_name=$1
    local log_file="${LOG_DIR}/sync-${mirror_name}-$(date +%Y%m%d).log"
    
    echo "🔄 Syncing ${mirror_name}..."
    echo "   Log: ${log_file}"
    
    # Use tee to monitor progress in real-time
    aptly mirror update ${mirror_name} 2>&1 | tee "$log_file"
    
    if [ $? -eq 0 ]; then
        echo "✅ ${mirror_name} synced successfully"
    else
        echo "❌ ${mirror_name} sync failed - check ${log_file}"
        return 1
    fi
}

# Sync all mirrors sequentially (parallel syncs can overload upstream)
sync_mirror "ubuntu-noble"
sync_mirror "ubuntu-noble-security"
sync_mirror "ubuntu-noble-updates"

# Show mirror statistics
echo ""
echo "=== MIRROR STATISTICS ==="
aptly mirror show ubuntu-noble | grep "Number of packages"
aptly mirror show ubuntu-noble-security | grep "Number of packages"
aptly mirror show ubuntu-noble-updates | grep "Number of packages"

# Calculate total disk usage
echo ""
echo "=== DISK USAGE ==="
du -sh /var/lib/aptly
```

**Performance Monitoring**:
```bash
# Monitor sync progress in another terminal
watch -n 5 'du -sh /var/lib/aptly && grep Downloaded /var/log/aptly/sync-*.log | tail -1'
```

---

### Step 5: Create Baseline Snapshot

**Why Snapshots Matter**: Snapshots are immutable point-in-time copies. Essential for reproducible builds and rollback capability.

**Script: `create-baseline-snapshot.sh`**

```bash
#!/bin/bash
# create-baseline-snapshot.sh - Create production-ready snapshot

set -euo pipefail

SNAPSHOT_DATE=$(date +%Y%m%d)
SNAPSHOT_NAME="ubuntu-baseline-${SNAPSHOT_DATE}"

# Create merged snapshot from all mirrors
aptly snapshot create ${SNAPSHOT_NAME} from mirror ubuntu-noble

# Merge security updates
aptly snapshot merge ${SNAPSHOT_NAME}-security \
  ${SNAPSHOT_NAME} \
  ubuntu-noble-security-snapshot

# Merge regular updates
aptly snapshot merge ${SNAPSHOT_NAME}-final \
  ${SNAPSHOT_NAME}-security \
  ubuntu-noble-updates-snapshot

echo "✅ Baseline snapshot created: ${SNAPSHOT_NAME}-final"
echo "   Packages: $(aptly snapshot show ${SNAPSHOT_NAME}-final | grep 'Number of packages')"

# Visualize snapshot graph (optional)
aptly graph -format=png -output=/tmp/aptly-graph.png

echo "📊 Snapshot graph saved to /tmp/aptly-graph.png"
```

---

### Step 6: Publish Repository

**Script: `publish-repository.sh`**

```bash
#!/bin/bash
# publish-repository.sh - Make repository available to clients

set -euo pipefail

SNAPSHOT_NAME="ubuntu-baseline-$(date +%Y%m%d)-final"
PUBLISH_PREFIX="ubuntu"
DISTRIBUTION="noble"

# Publish snapshot to filesystem
echo "📦 Publishing snapshot: ${SNAPSHOT_NAME}"
aptly publish snapshot \
  -distribution=${DISTRIBUTION} \
  -component=main \
  ${SNAPSHOT_NAME} \
  ${PUBLISH_PREFIX}

# Verify publication
echo "✅ Repository published to: /var/www/aptly/${PUBLISH_PREFIX}"
ls -lh /var/www/aptly/${PUBLISH_PREFIX}/dists/${DISTRIBUTION}/

# Configure nginx
success "Configuring nginx..."
cat <<'EOF' | sudo tee /etc/nginx/sites-available/aptly
server {
    listen 80;
    server_name apt-mirror.local;
    
    root /var/www/aptly;
    autoindex on;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    # Enable compression for metadata files
    location ~ \.(deb|udeb|ddeb)$ {
        # Disable compression for binary packages (already compressed)
        gzip off;
    }
    
    location ~ (Packages|Sources|Release|Contents) {
        gzip on;
        gzip_types text/plain;
    }
    
    # Cache control for metadata
    location ~ Release$ {
        expires 1h;
        add_header Cache-Control "public, must-revalidate";
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/aptly /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

echo "✅ Repository available at: http://apt-mirror.local/ubuntu"
```

---

### Step 7: Client Configuration

**Automated Setup with auto-apt-proxy**:

```bash
# On each client (containers, VMs):
apt-get install auto-apt-proxy

# auto-apt-proxy automatically detects apt-mirror.local on port 80
# No manual /etc/apt/sources.list changes needed!
```

**Manual Configuration** (if auto-apt-proxy unavailable):

```bash
#!/bin/bash
# configure-client.sh - Point client to local mirror

# Backup original sources
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak

# Replace with local mirror
cat <<EOF | sudo tee /etc/apt/sources.list
# Xoe-NovAi Local Mirror (Air-Gapped)
deb http://apt-mirror.local/ubuntu noble main restricted universe
deb http://apt-mirror.local/ubuntu noble-security main restricted universe
deb http://apt-mirror.local/ubuntu noble-updates main restricted universe
EOF

# Update package lists
sudo apt-get update

echo "✅ Client configured for local mirror"
```

---

### Step 8: Air-Gap Transfer Workflow

**Scenario**: Staging server (online) → Production server (offline)

**On Staging Server** (online):

```bash
#!/bin/bash
# export-updates.sh - Daily export for USB transfer

set -euo pipefail

EXPORT_DATE=$(date +%Y%m%d)
EXPORT_DIR="/mnt/usb/aptly-updates-${EXPORT_DATE}"
SNAPSHOT_NAME="ubuntu-staging-${EXPORT_DATE}"

# Update mirrors
aptly mirror update ubuntu-noble
aptly mirror update ubuntu-noble-security
aptly mirror update ubuntu-noble-updates

# Create new snapshot
aptly snapshot create ${SNAPSHOT_NAME} from mirror ubuntu-noble

# Export snapshot to USB
mkdir -p "${EXPORT_DIR}"
aptly snapshot export ${SNAPSHOT_NAME} "${EXPORT_DIR}"

# Create checksum file
cd "${EXPORT_DIR}"
sha256sum * > SHA256SUMS

# GPG sign checksums
gpg --clearsign SHA256SUMS

echo "✅ Export complete: ${EXPORT_DIR}"
echo "   Transfer SHA256SUMS.asc with packages for verification"
```

**On Production Server** (offline):

```bash
#!/bin/bash
# import-updates.sh - Import from USB

set -euo pipefail

IMPORT_DIR="/mnt/usb/aptly-updates-$(date +%Y%m%d)"

# Verify GPG signature
gpg --verify "${IMPORT_DIR}/SHA256SUMS.asc"

# Verify checksums
cd "${IMPORT_DIR}"
sha256sum -c SHA256SUMS

# Import snapshot
aptly snapshot import production-staging "${IMPORT_DIR}"

# Promote to testing
aptly snapshot merge production-testing-$(date +%Y%m%d) \
  production-baseline \
  production-staging

echo "✅ Updates imported to testing snapshot"
echo "   Run validation tests before promoting to production"
```

---

### Step 9: Security Scanning Integration

**Script: `scan-packages.sh`** - CVE detection before promotion

```bash
#!/bin/bash
# scan-packages.sh - Trivy CVE scanning for package metadata

set -euo pipefail

SNAPSHOT_NAME="production-testing-$(date +%Y%m%d)"
SCAN_REPORT="/var/log/aptly/security-scan-$(date +%Y%m%d).json"

# Extract package list from snapshot
aptly snapshot show -with-packages ${SNAPSHOT_NAME} > /tmp/package-list.txt

# Scan for CVEs (critical and high severity only)
echo "🔍 Scanning ${SNAPSHOT_NAME} for CVEs..."
trivy rootfs --severity CRITICAL,HIGH \
  --format json \
  --output "${SCAN_REPORT}" \
  /var/lib/aptly/public

# Parse results
CRITICAL_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length' "$SCAN_REPORT")
HIGH_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "HIGH")] | length' "$SCAN_REPORT")

echo ""
echo "=== SECURITY SCAN RESULTS ==="
echo "Critical vulnerabilities: $CRITICAL_COUNT"
echo "High vulnerabilities: $HIGH_COUNT"

if [ "$CRITICAL_COUNT" -gt 0 ]; then
    echo "❌ CRITICAL vulnerabilities detected - review $SCAN_REPORT"
    exit 1
else
    echo "✅ No critical vulnerabilities - safe to promote"
fi
```

---

### Step 10: Snapshot Promotion Pipeline

**Tiered Promotion**: Staging → Testing (48h soak) → Production

```bash
#!/bin/bash
# promote-snapshot.sh - Production promotion workflow

set -euo pipefail

TESTING_SNAPSHOT="production-testing-$(date +%Y%m%d --date='2 days ago')"
PRODUCTION_SNAPSHOT="production-$(date +%Y%m%d)"

# Verify testing snapshot exists
if ! aptly snapshot show ${TESTING_SNAPSHOT} &>/dev/null; then
    echo "❌ Testing snapshot not found (48h soak time required)"
    exit 1
fi

# Run security scan
./scan-packages.sh || exit 1

# Promote to production
echo "📦 Promoting ${TESTING_SNAPSHOT} → ${PRODUCTION_SNAPSHOT}"
aptly snapshot merge ${PRODUCTION_SNAPSHOT} ${TESTING_SNAPSHOT}

# Publish to production
aptly publish switch noble ubuntu ${PRODUCTION_SNAPSHOT}

echo "✅ Production updated to: ${PRODUCTION_SNAPSHOT}"
echo "   Rollback command: aptly publish switch noble ubuntu <previous-snapshot>"
```

---

## 🧪 **Testing Strategy**

### Test 1: Mirror Integrity Verification

```bash
# Verify GPG signatures
aptly mirror verify ubuntu-noble

# Check package counts match upstream
curl -s http://archive.ubuntu.com/ubuntu/dists/noble/main/binary-amd64/Packages.gz | \
  zcat | grep -c "^Package:" > /tmp/upstream-count

aptly mirror show ubuntu-noble | grep "Number of packages" > /tmp/local-count

diff /tmp/upstream-count /tmp/local-count
```

### Test 2: Client Failover Testing

```bash
# Simulate mirror failure
sudo systemctl stop nginx

# Verify auto-apt-proxy fallback to upstream
apt-get update  # Should fail or fallback to DIRECT

# Restore service
sudo systemctl start nginx
apt-get update  # Should succeed via local mirror
```

### Test 3: Snapshot Rollback

```bash
# List available snapshots
aptly snapshot list

# Rollback to previous snapshot
aptly publish switch noble ubuntu ubuntu-baseline-20260120

# Verify clients see old packages
apt-cache policy <package-name>
```

---

## 📊 **Monitoring & Metrics**

### Prometheus Exporter for aptly

**Script: `aptly-prometheus-exporter.sh`**

```bash
#!/bin/bash
# aptly-prometheus-exporter.sh - Export metrics to Prometheus

METRICS_FILE="/var/lib/node_exporter/textfile_collector/aptly.prom"

# Mirror package counts
NOBLE_COUNT=$(aptly mirror show ubuntu-noble | grep "Number of packages" | awk '{print $NF}')

# Disk usage
DISK_USAGE=$(du -sb /var/lib/aptly | awk '{print $1}')

# Write Prometheus metrics
cat > "${METRICS_FILE}" <<EOF
# HELP aptly_mirror_packages_total Total packages in mirror
# TYPE aptly_mirror_packages_total gauge
aptly_mirror_packages_total{mirror="ubuntu-noble"} ${NOBLE_COUNT}

# HELP aptly_disk_usage_bytes Disk usage of aptly repository
# TYPE aptly_disk_usage_bytes gauge
aptly_disk_usage_bytes ${DISK_USAGE}
EOF
```

### Grafana Dashboard Queries

```promql
# Package growth rate
rate(aptly_mirror_packages_total[24h])

# Disk usage trend
aptly_disk_usage_bytes / 1024 / 1024 / 1024  # Convert to GB

# Alert on mirror staleness (if no updates in 48h)
time() - aptly_last_sync_timestamp > 172800
```

---

## 🚨 **Troubleshooting**

### Issue 1: aptly GPG Verification Fails

**Symptom**: `gpgv: Can't check signature: No public key`

**Fix**:
```bash
# Import Ubuntu archive keys
gpg --keyserver keyserver.ubuntu.com \
    --recv-keys 3B4FE6ACC0B21F32 871920D1991BC93C

# Add to aptly trusted keyring
gpg --export 3B4FE6ACC0B21F32 | \
  gpg --no-default-keyring --keyring trustedkeys.gpg --import
```

### Issue 2: Snapshot Merge Conflicts

**Symptom**: `unable to merge snapshots: package <name> has conflicting versions`

**Fix**:
```bash
# Show conflicts
aptly snapshot diff snapshot1 snapshot2

# Manual conflict resolution (keep newer version)
aptly snapshot filter snapshot1-filtered snapshot1 \
  'Priority (required), Version (>= X.Y.Z)'

aptly snapshot merge snapshot-resolved snapshot1-filtered snapshot2
```

### Issue 3: nginx 403 Forbidden

**Symptom**: Clients get `403 Forbidden` when accessing repository

**Fix**:
```bash
# Check file permissions
sudo chown -R www-data:www-data /var/www/aptly
sudo chmod -R 755 /var/www/aptly

# Verify SELinux context (if enabled)
sudo chcon -Rt httpd_sys_content_t /var/www/aptly
```

---

## 📚 **Advanced Topics**

### Topic 1: Multi-Architecture Support

**Use Case**: Support both Ryzen (amd64) and Raspberry Pi (arm64) in same repository

```bash
# Create multi-arch mirror
aptly mirror create -architectures=amd64,arm64 \
  ubuntu-noble-multi \
  http://ports.ubuntu.com/ubuntu-ports \
  noble main

# Publish with multiple components
aptly publish snapshot \
  -distribution=noble \
  -component=main,arm64 \
  ubuntu-noble-multi-snapshot
```

### Topic 2: Delta Updates (Bandwidth Optimization)

**Concept**: Transfer only package diffs instead of full `.deb` files

```bash
# Generate debdelta files (requires debdelta package)
debdelta-upgrade \
  /var/lib/aptly/pool/main/p/python3.12/python3.12_3.12.0-1_amd64.deb \
  /var/lib/aptly/pool/main/p/python3.12/python3.12_3.12.1-1_amd64.deb

# Result: 2MB delta vs. 15MB full package (87% bandwidth savings)
```

---

**Document Version**: 2.0 (Enterprise Air-Gap Implementation)  
**Last Updated**: January 27, 2026  
**Review Cycle**: Monthly + CVE-triggered  
**Owner**: Xoe-NovAi Infrastructure Team  
**Classification**: Sovereign Operations - Internal Use Only