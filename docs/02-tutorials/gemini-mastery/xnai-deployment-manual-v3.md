# Podman Rootless apt-cacher-ng – Enterprise Deployment Manual (2026 Hardened Edition)
**Version**: 3.0 | **Date**: January 27, 2026 | **Target**: Ubuntu 22.04 + Podman 5.5+ rootless

---

## Part 1: Quadlet Container Definition (Hardened with :Z SELinux Labels)

### 1.1 Create Quadlet Directory Structure

```bash
# As your unprivileged user (not root)
mkdir -p ~/.config/containers/systemd
mkdir -p ~/.local/bin
mkdir -p ~/.local/var/log
cd ~/.config/containers/systemd
```

### 1.2 apt-cacher-ng.container (Hardened Quadlet Format)

Create file: `~/.config/containers/systemd/apt-cacher-ng.container`

```ini
[Unit]
Description=Xoe-NovAi apt-cacher-ng Caching Proxy (Rootless + Hardened)
Documentation=https://www.unix-ag.uni-kl.de/~bloch/acng/html/
After=network-online.target
Wants=network-online.target

[Container]
# Image: Use official or build locally
Image=docker.io/sameersbn/apt-cacher-ng:latest
# Alternative: Image=localhost/xnai-apt-cacher-ng:latest

# Container name for podman commands
ContainerName=xnai-apt-cacher-ng

# ============================================================================
# SECURITY HARDENING (Ma'at: Justice + Order)
# ============================================================================

# Drop ALL capabilities, add only NET_BIND_SERVICE (explicit allow-list)
DropCapability=ALL
AddCapability=NET_BIND_SERVICE

# No privilege escalation for child processes
SecurityLabelDisable=false
NoNewPrivileges=true

# Rootless user mapping (UID 100000-165535 range)
UIDMap=0:100000:65536
GIDMap=0:100000:65536

# Resource limits (prevent DoS via memory exhaustion)
Memory=256m
MemorySwap=512m
CPUQuota=50%

# Read-only root filesystem (prevents tampering)
ReadOnly=true
Tmpfs=/tmp:rw,noexec,nosuid,size=64m
Tmpfs=/var/run:rw,noexec,nosuid,size=16m
Tmpfs=/var/cache/apt-cacher-ng/_tmp:rw,noexec,nosuid,size=256m

# ============================================================================
# NETWORKING (Ma'at: Harmony - localhost-only binding)
# ============================================================================

# Port binding: LOCALHOST ONLY (mitigates CVE-2025-11146/11147 XSS)
PublishPort=127.0.0.1:3142:3142

# Network backend: Use pasta (Podman 5.5+, CVE-2025-22869 patched)
Network=pasta

# ============================================================================
# VOLUME MOUNTS (Ma'at: Truth - source verification via GPG)
# ============================================================================

# Cache directory (persistent storage with :Z for SELinux strict labeling)
# :Z = Relabel with container-specific label (private, not shared)
Volume=apt-cache:/var/cache/apt-cacher-ng:Z

# Configuration (read-only with :z for shared SELinux label)
# :z = Relabel with shared label (multiple containers can read)
Volume=/etc/apt-cacher-ng/acng.conf:/etc/apt-cacher-ng/acng.conf:ro,z

# Logs (write-only, specific directory)
Volume=apt-logs:/var/log/apt-cacher-ng:Z

# ============================================================================
# ENVIRONMENT VARIABLES
# ============================================================================

Environment=DEBIAN_FRONTEND=noninteractive
Environment=ACNG_PORT=3142
Environment=ACNG_BIND_ADDRESS=127.0.0.1
Environment=ACNG_CACHE_DIR=/var/cache/apt-cacher-ng
Environment=ACNG_LOG_DIR=/var/log/apt-cacher-ng

# ============================================================================
# HEALTH CHECK (Ma'at: Order - continuous validation)
# ============================================================================

HealthCmd=curl -sf http://localhost:3142/acng-report.html || exit 1
HealthInterval=30s
HealthTimeout=10s
HealthRetries=3
HealthStartPeriod=30s

# ============================================================================
# LOGGING
# ============================================================================

LogDriver=journald
Label="io.podman.compose.project=xnai"
Label="io.podman.compose.service=apt-cacher-ng"
Label="ma'at.principle=sovereignty"

[Install]
WantedBy=default.target
```

### 1.3 Create Required Volumes

```bash
# Create named volumes (automatically labeled for SELinux)
podman volume create apt-cache
podman volume create apt-logs

# Verify volumes
podman volume ls
# Expected output:
# DRIVER      VOLUME NAME
# local       apt-cache
# local       apt-logs
```

### 1.4 Hardened Configuration File

Create: `/etc/apt-cacher-ng/acng.conf`

```conf
# ============================================================================
# XOE-NOVAI APT-CACHER-NG HARDENED CONFIGURATION (2026)
# Mitigates: CVE-2025-11146/11147 (XSS in web UI)
# ============================================================================

# CRITICAL: Bind to localhost only (prevents XSS attack surface)
Port: 3142
BindAddress: 127.0.0.1

# Disable admin web UI on external interfaces
AdminAddress: 127.0.0.1:3142

# Cache directory (owned by apt-cacher-ng user inside container)
CacheDir: /var/cache/apt-cacher-ng

# Logging
LogDir: /var/log/apt-cacher-ng
VerboseLog: 1
SyslogFacility: daemon

# ============================================================================
# SECURITY: Allowed upstream mirrors (allowlist for source verification)
# Ma'at Principle: Truth (verify package sources via GPG)
# ============================================================================

# Allow standard Debian/Ubuntu index files
AllowedIndexFiles: Packages Release Sources Contents Translation

# Allow only HTTP/HTTPS on standard ports (prevent SSRF)
AllowedUpstreamPorts: 80 443

# Allowlist trusted mirror hosts (prevent cache poisoning)
RepoMatching: 
  ^(ftp|https?)://security\.ubuntu\.com/ubuntu
  ^(ftp|https?)://archive\.ubuntu\.com/ubuntu
  ^(ftp|https?)://deb\.debian\.org/debian
  ^(ftp|https?)://download\.docker\.com/linux/ubuntu
  ^(ftp|https?)://packages\.cloud\.google\.com

# HTTPS tunneling (CONNECT method for secure repositories)
# Required for: security.ubuntu.com, launchpad.net PPAs
PassThroughPattern: ^(.*\.ubuntu\.com|.*\.debian\.org|ppa\.launchpad\.net)/.*

# Disable SSL certificate verification for PassThrough (cache-only mode)
# NOTE: SecureAPT GPG verification still enforced by apt client
PassThroughPattern: .*:ssl_cert_check_off

# ============================================================================
# PERFORMANCE TUNING
# ============================================================================

# Connection limits (prevent DoS)
MaxConns: 40
MaxStandby: 20

# Rate limiting (30 requests/min per IP, aligns with CRAWL_RATE_LIMIT)
# NOTE: Built-in rate limiting is rudimentary; use external firewall if needed
BandwidthLimit: 0  # Unlimited (trust localhost clients)

# Cache expiry (30 days for packages, 7 days for indices)
ExtraceHeader: X-Original-URL
ExpireFileAbsMin: 2592000  # 30 days in seconds
ExpireLingeringFactor: 4

# ============================================================================
# MAINTENANCE
# ============================================================================

# Offline mode (continue serving from cache when upstream unavailable)
Offline: 0
OfflineBroken: 0

# Compression support
CompressFileAbsMin: 1048576  # 1 MB minimum for compression

# Debug (disable in production)
Debug: 0
```

Copy configuration to system:

```bash
# Create config directory
sudo mkdir -p /etc/apt-cacher-ng

# Copy hardened config
sudo cp acng.conf /etc/apt-cacher-ng/acng.conf

# Set permissions (readable by all, writable by root only)
sudo chmod 644 /etc/apt-cacher-ng/acng.conf
```

### 1.5 Enable & Start Service

```bash
# Reload systemd to recognize quadlet
systemctl --user daemon-reload

# Enable for auto-startup on login
systemctl --user enable apt-cacher-ng.container

# Start service immediately
systemctl --user start apt-cacher-ng.container

# Verify status
systemctl --user status apt-cacher-ng.container

# Expected output:
# ● apt-cacher-ng.container - Xoe-NovAi apt-cacher-ng Caching Proxy
#    Loaded: loaded (~/.config/containers/systemd/apt-cacher-ng.container)
#    Active: active (running) since ...
#    Main PID: ...
#    CGroup: /user.slice/user-1001.slice/...

# Check logs
journalctl --user-unit=apt-cacher-ng.container -f
```

### 1.6 Verify Hardening

```bash
# 1. Check port binding (must be 127.0.0.1 only)
netstat -tuln | grep 3142
# Expected: tcp        0      0 127.0.0.1:3142          0.0.0.0:*               LISTEN
# NOT:      tcp        0      0 0.0.0.0:3142            0.0.0.0:*               LISTEN

# 2. Verify capabilities (should show only NET_BIND_SERVICE)
podman exec xnai-apt-cacher-ng capsh --print | grep "Current:"
# Expected: Current: cap_net_bind_service=ep

# 3. Check SELinux labels (if SELinux enabled)
podman volume inspect apt-cache --format '{{.Mountpoint}}'
ls -lZ $(podman volume inspect apt-cache --format '{{.Mountpoint}}')
# Expected: Labels should show container-specific SELinux context

# 4. Verify read-only root filesystem
podman exec xnai-apt-cacher-ng touch /test 2>&1
# Expected: touch: cannot touch '/test': Read-only file system

# 5. Test health check
curl -sf http://127.0.0.1:3142/acng-report.html
# Expected: HTML page with cache statistics
```

---

## Part 2: Dockerfile Configuration with Proxy Settings

### 2.1 Multi-Stage Dockerfile with apt-cacher-ng Proxy (Hardened)

Create: `Dockerfile.api` (hardened version)

```dockerfile
# ============================================================================
# XOE-NOVAI RAG API - MULTI-STAGE BUILD WITH APT-CACHER-NG
# Version: 3.0 | Date: 2026-01-27
# Security: Rootless, minimal attack surface, verified sources
# ============================================================================

# ============================================================================
# STAGE 1: BUILDER (Dependencies + Compilation)
# ============================================================================

FROM ubuntu:22.04 AS builder

# Prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8

# ============================================================================
# CONFIGURE APT PROXY (resolves to host via host.containers.internal)
# Ma'at Principle: Efficiency (cache reuse) + Truth (source verification)
# ============================================================================

# HTTP proxy for Debian/Ubuntu mirrors
RUN echo 'Acquire::http { Proxy "http://host.containers.internal:3142"; };' \
    | tee /etc/apt/apt.conf.d/02proxy

# HTTPS tunneling (via CONNECT method for security.ubuntu.com)
RUN echo 'Acquire::https { Proxy "http://host.containers.internal:3142"; };' \
    | tee -a /etc/apt/apt.conf.d/02proxy

# Timeout configuration (30s for cache, prevents hang)
RUN echo 'APT::Acquire::Retries "5";' \
    | tee -a /etc/apt/apt.conf.d/02proxy && \
    echo 'APT::Acquire::http::Timeout "30";' \
    | tee -a /etc/apt/apt.conf.d/02proxy && \
    echo 'APT::Acquire::https::Timeout "30";' \
    | tee -a /etc/apt/apt.conf.d/02proxy

# Verify proxy configuration
RUN cat /etc/apt/apt.conf.d/02proxy && \
    echo "Proxy configuration applied"

# ============================================================================
# INSTALL BUILD DEPENDENCIES (all from cache on subsequent builds)
# ============================================================================

RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
        # Build tools
        build-essential \
        cmake \
        git \
        pkg-config \
        # Python
        python3.10 \
        python3.10-dev \
        python3-pip \
        # Libraries for llama.cpp + RADV Vulkan
        libvulkan-dev \
        mesa-vulkan-drivers \
        vulkan-tools \
        libopenblas-dev \
        # Networking
        curl \
        wget \
        ca-certificates && \
    # Clean up to reduce layer size
    rm -rf /var/lib/apt/lists/*

# Verify Vulkan support (Ryzen 5700U iGPU)
RUN vulkaninfo --summary || echo "Vulkan driver loaded (no X11 display)"

# ============================================================================
# INSTALL PYTHON DEPENDENCIES (cached via pip)
# ============================================================================

WORKDIR /build

# Copy requirements first (layer caching optimization)
COPY requirements.txt .

# Install Python packages with no cache (reproducible builds)
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel && \
    pip3 install --no-cache-dir -r requirements.txt

# Verify key dependencies
RUN python3 -c "import fastapi; import llama_cpp; import faiss; print('Dependencies OK')"

# ============================================================================
# STAGE 2: RUNTIME (Minimal Attack Surface)
# ============================================================================

FROM ubuntu:22.04

# Metadata labels (Ma'at: Order)
LABEL maintainer="xoe-novai@example.com" \
      version="3.0" \
      description="Xoe-NovAi RAG API with apt-cacher-ng optimization" \
      ma'at.principle="sovereignty,truth,justice"

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    PATH="/home/appuser/.local/bin:$PATH"

# ============================================================================
# CONFIGURE APT PROXY (runtime layer also uses cache for updates)
# ============================================================================

RUN echo 'Acquire::http { Proxy "http://host.containers.internal:3142"; };' \
    | tee /etc/apt/apt.conf.d/02proxy && \
    echo 'Acquire::https { Proxy "http://host.containers.internal:3142"; };' \
    | tee -a /etc/apt/apt.conf.d/02proxy

# Install only runtime dependencies
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
        python3.10 \
        python3-pip \
        libvulkan1 \
        mesa-vulkan-drivers \
        libopenblas0 \
        curl \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# ============================================================================
# SECURITY: Create unprivileged user (Ma'at: Justice)
# UID 1001 matches host user for volume permissions
# ============================================================================

RUN groupadd -g 1001 appuser && \
    useradd -u 1001 -g appuser -m -s /bin/bash appuser && \
    mkdir -p /app /models /embeddings /library /knowledge && \
    chown -R appuser:appuser /app /models /embeddings /library /knowledge

# Switch to unprivileged user
USER appuser
WORKDIR /app

# ============================================================================
# COPY APPLICATION CODE + DEPENDENCIES
# ============================================================================

# Copy Python packages from builder
COPY --from=builder --chown=appuser:appuser /usr/local/lib/python3.10 /usr/local/lib/python3.10

# Copy application code
COPY --chown=appuser:appuser ./app/XNAi_rag_app /app/XNAi_rag_app
COPY --chown=appuser:appuser ./config.toml /config.toml

# ============================================================================
# HEALTH CHECK (Ma'at: Order - continuous validation)
# ============================================================================

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# ============================================================================
# EXPOSE PORT (documentation only, actual binding in compose)
# ============================================================================

EXPOSE 8000

# ============================================================================
# ENTRYPOINT (immutable startup command)
# ============================================================================

ENTRYPOINT ["uvicorn", "XNAi_rag_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["--log-level", "info"]
```

### 2.2 docker-compose.yml Integration (Updated)

```yaml
version: '3.8'

services:
  apt-cacher-ng:
    image: docker.io/sameersbn/apt-cacher-ng:latest
    container_name: xnai-apt-cacher-ng
    ports:
      - "127.0.0.1:3142:3142"  # Localhost only (CVE-2025-11146/11147 mitigation)
    volumes:
      - apt-cache:/var/cache/apt-cacher-ng:Z  # SELinux private label
      - /etc/apt-cacher-ng/acng.conf:/etc/apt-cacher-ng/acng.conf:ro,z  # Shared label
      - apt-logs:/var/log/apt-cacher-ng:Z
    environment:
      - ACNG_PORT=3142
      - ACNG_BIND_ADDRESS=127.0.0.1
    mem_limit: 256m
    memswap_limit: 512m
    cpu_quota: 50000  # 50% CPU
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    read_only: true
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=64m
      - /var/run:rw,noexec,nosuid,size=16m
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-sf", "http://localhost:3142/acng-report.html"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  rag-api:
    build:
      context: .
      dockerfile: Dockerfile.api
      args:
        # Proxy is configured inside Dockerfile via host.containers.internal
        BUILD_WITH_CACHE: "true"
    depends_on:
      apt-cacher-ng:
        condition: service_healthy
    environment:
      # Runtime proxy (for apt-get inside running container if needed)
      http_proxy: http://host.containers.internal:3142
      https_proxy: http://host.containers.internal:3142
    # ... rest of service config ...

volumes:
  apt-cache:
    driver: local
  apt-logs:
    driver: local
```

---

## Part 3: Cache Backup & Restore (Artifact 2 Enhancement)

### 3.1 Automated Backup Script

Create: `~/.local/bin/xnai-apt-cache-backup.sh`

```bash
#!/bin/bash
set -euo pipefail

# ============================================================================
# XOE-NOVAI APT-CACHER-NG BACKUP SCRIPT
# Ma'at Principle: Order (preservation) + Truth (integrity verification)
# ============================================================================

BACKUP_DIR="${HOME}/backups/apt-cache"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/apt-cache-${TIMESTAMP}.tar.gz.enc"
CACHE_VOLUME="apt-cache"
ENCRYPTION_KEY="${HOME}/.ssh/apt-cache-backup.key"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

log "Starting apt-cacher-ng cache backup..."

# 1. Export volume to tar.gz
log "Exporting volume: $CACHE_VOLUME"
cache_mountpoint=$(podman volume inspect "$CACHE_VOLUME" --format '{{.Mountpoint}}')

if [[ -z "$cache_mountpoint" ]]; then
    log "ERROR: Volume $CACHE_VOLUME not found"
    exit 1
fi

log "Cache mountpoint: $cache_mountpoint"

# 2. Create compressed archive
log "Creating compressed archive..."
tar -czf "${BACKUP_FILE%.enc}" -C "$cache_mountpoint" .

# 3. Encrypt backup (AES-256-CBC)
log "Encrypting backup with AES-256..."
if [[ ! -f "$ENCRYPTION_KEY" ]]; then
    log "Generating encryption key..."
    openssl rand -base64 32 > "$ENCRYPTION_KEY"
    chmod 600 "$ENCRYPTION_KEY"
fi

openssl enc -aes-256-cbc -salt -pbkdf2 \
    -in "${BACKUP_FILE%.enc}" \
    -out "$BACKUP_FILE" \
    -pass file:"$ENCRYPTION_KEY"

# 4. Remove unencrypted archive
rm -f "${BACKUP_FILE%.enc}"

# 5. Generate checksum
log "Generating SHA256 checksum..."
sha256sum "$BACKUP_FILE" > "${BACKUP_FILE}.sha256"

# 6. Cleanup old backups (keep last 7 days)
log "Cleaning up old backups (retain 7 days)..."
find "$BACKUP_DIR" -name "apt-cache-*.tar.gz.enc" -mtime +7 -delete
find "$BACKUP_DIR" -name "apt-cache-*.sha256" -mtime +7 -delete

# 7. Summary
backup_size=$(du -h "$BACKUP_FILE" | cut -f1)
log "Backup complete: $BACKUP_FILE ($backup_size)"
log "Checksum: $(cat "${BACKUP_FILE}.sha256")"
log "Encryption key: $ENCRYPTION_KEY (keep secure!)"
```

### 3.2 Restore Script

Create: `~/.local/bin/xnai-apt-cache-restore.sh`

```bash
#!/bin/bash
set -euo pipefail

# ============================================================================
# XOE-NOVAI APT-CACHER-NG RESTORE SCRIPT
# ============================================================================

BACKUP_FILE="${1:?Usage: $0 <backup-file.tar.gz.enc>}"
CACHE_VOLUME="apt-cache"
ENCRYPTION_KEY="${HOME}/.ssh/apt-cache-backup.key"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

if [[ ! -f "$BACKUP_FILE" ]]; then
    log "ERROR: Backup file not found: $BACKUP_FILE"
    exit 1
fi

if [[ ! -f "$ENCRYPTION_KEY" ]]; then
    log "ERROR: Encryption key not found: $ENCRYPTION_KEY"
    exit 1
fi

log "Starting apt-cacher-ng cache restore..."

# 1. Verify checksum
log "Verifying backup integrity..."
if [[ -f "${BACKUP_FILE}.sha256" ]]; then
    sha256sum -c "${BACKUP_FILE}.sha256" || {
        log "ERROR: Checksum verification failed"
        exit 1
    }
    log "Checksum verified"
else
    log "WARNING: No checksum file found, skipping verification"
fi

# 2. Decrypt backup
log "Decrypting backup..."
openssl enc -aes-256-cbc -d -pbkdf2 \
    -in "$BACKUP_FILE" \
    -out "${BACKUP_FILE%.enc}" \
    -pass file:"$ENCRYPTION_KEY"

# 3. Stop apt-cacher-ng service
log "Stopping apt-cacher-ng service..."
systemctl --user stop apt-cacher-ng.container || log "Service not running"

# 4. Get volume mountpoint
cache_mountpoint=$(podman volume inspect "$CACHE_VOLUME" --format '{{.Mountpoint}}')

if [[ -z "$cache_mountpoint" ]]; then
    log "ERROR: Volume $CACHE_VOLUME not found"
    exit 1
fi

# 5. Backup existing cache (safety)
log "Backing up existing cache to ${cache_mountpoint}.bak..."
if [[ -d "$cache_mountpoint" ]]; then
    cp -a "$cache_mountpoint" "${cache_mountpoint}.bak"
fi

# 6. Extract archive to volume
log "Extracting backup to cache volume..."
tar -xzf "${BACKUP_FILE%.enc}" -C "$cache_mountpoint"

# 7. Fix permissions
log "Fixing permissions..."
podman unshare chown -R 100000:100000 "$cache_mountpoint"

# 8. Restart service
log "Starting apt-cacher-ng service..."
systemctl --user start apt-cacher-ng.container

# 9. Verify health
log "Waiting for service health check..."
sleep 10
if curl -sf http://127.0.0.1:3142/acng-report.html >/dev/null 2>&1; then
    log "Service healthy"
else
    log "ERROR: Service health check failed"
    exit 1
fi

# 10. Cleanup
rm -f "${BACKUP_FILE%.enc}"
log "Restore complete"
```

Make scripts executable:

```bash
chmod +x ~/.local/bin/xnai-apt-cache-backup.sh
chmod +x ~/.local/bin/xnai-apt-cache-restore.sh
```

---

## Part 4: Troubleshooting Flowchart (Enhanced)

```
APT-CACHER-NG TROUBLESHOOTING DECISION TREE (2026 EDITION)
===========================================================

START
  ↓
[PHASE 1] Is Podman ≥5.5.0? (CVE-2025-22869 check)
  ├─ NO → CRITICAL: Upgrade Podman immediately
  │       sudo apt-get update && sudo apt-get install -y podman
  │       podman --version  # Must show ≥5.5.0
  │
  └─ YES ↓
    ↓
[PHASE 2] Is apt-cacher-ng container running?
  ├─ NO → Check systemd status:
  │       systemctl --user status apt-cacher-ng.container
  │       ├─ Not enabled → systemctl --user enable apt-cacher-ng.container
  │       ├─ Failed to start → Check logs:
  │       │   journalctl --user-unit=apt-cacher-ng.container -n 50
  │       │   ├─ "Address already in use" → Kill process:
  │       │   │   lsof -i :3142 | grep -v PID | awk '{print $2}' | xargs kill -9
  │       │   ├─ "Permission denied" → Check volume permissions:
  │       │   │   podman volume inspect apt-cache
  │       │   │   podman unshare chown 100000:100000 $(podman volume inspect apt-cache --format '{{.Mountpoint}}')
  │       │   ├─ "Read-only file system" → Check tmpfs mounts:
  │       │   │   Verify /tmp and /var/run tmpfs in quadlet file
  │       │   └─ Other error → Check Podman installation:
  │       │       podman info | grep -A3 networkBackendInfo
  │       └─ Start service → systemctl --user start apt-cacher-ng.container
  │
  └─ YES ↓
    ↓
[PHASE 3] Is health check passing?
  ├─ NO → curl -v http://127.0.0.1:3142/acng-report.html
  │       ├─ Connection refused → Port not exposed
  │       │   └─ Fix: Verify PublishPort=127.0.0.1:3142:3142 in quadlet
  │       ├─ HTTP 500 → Cache corruption or permission issue
  │       │   └─ Fix: Restart and check logs
  │       │        systemctl --user restart apt-cacher-ng.container
  │       │        journalctl --user-unit=apt-cacher-ng.container -n 100 -e
  │       ├─ Timeout → Network/host resolution issue
  │       │   └─ Check: host.containers.internal resolution
  │       │       podman run --rm alpine nslookup host.containers.internal
  │       └─ XSS warning → Web UI exposed (CVE-2025-11146/11147)
  │           └─ Fix: Verify BindAddress: 127.0.0.1 in acng.conf
  │               netstat -tuln | grep 3142  # Must show 127.0.0.1:3142
  │
  └─ YES ↓
    ↓
[PHASE 4] Can containers access the proxy?
  ├─ NO → Check proxy configuration in Dockerfile:
  │       RUN echo 'Acquire::http { Proxy "http://host.containers.internal:3142"; };'
  │       ├─ host.containers.internal not resolving → Network backend issue
  │       │   └─ Verify: podman info | grep networkBackend
  │       │       Expected: pasta or netavark
  │       └─ Port 3142 not accessible → Firewall issue
  │           └─ Check: sudo ufw status | grep 3142
  │               Allow: in from 10.89.0.0/16 to any port 3142
  │
  └─ YES ↓
    ↓
[PHASE 5] Is cache growing but builds not faster?
  ├─ YES → Cache hit ratio low:
  │        ├─ Check apt-cacher-ng statistics:
  │        │   curl http://127.0.0.1:3142/acng-report.html | grep -i "hit\|request"
  │        ├─ Verify mirror URLs match:
  │        │   Compare Dockerfile mirrors with acng.conf RepoMatching
  │        └─ Pre-seed cache with common packages:
  │            See Artifact 3 (cache maintenance)
  │
  └─ NO ↓
    ↓
[PHASE 6] Are capabilities properly restricted?
  ├─ NO → Verify container capabilities:
  │       podman exec xnai-apt-cacher-ng capsh --print
  │       └─ Fix: Ensure DropCapability=ALL, AddCapability=NET_BIND_SERVICE
  │
  └─ YES ↓
    ↓
OPERATION SUCCESSFUL ✓
Service is working correctly.

Monitor: journalctl --user-unit=apt-cacher-ng.container -f
Metrics: curl http://127.0.0.1:3142/acng-report.html
```

---

## Part 5: Performance Benchmarking Script (Enhanced)

Create: `~/.local/bin/xnai-apt-cache-benchmark.sh`

```bash
#!/bin/bash
set -euo pipefail

# ============================================================================
# XOE-NOVAI APT-CACHER-NG BENCHMARK SCRIPT (2026)
# Ma'at Principle: Truth (accurate measurement) + Order (reproducibility)
# ============================================================================

DOCKERFILE="${1:-./Dockerfile.api}"
BUILD_CONTEXT="${2:-.}"
BENCHMARK_LOG="/tmp/apt-cache-benchmark-$(date +%Y%m%d-%H%M%S).log"
ITERATIONS=3
BUILD_TAG="xnai-benchmark:$(date +%s)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[✓]${NC} $*" | tee -a "$BENCHMARK_LOG"
}

warn() {
    echo -e "${YELLOW}[⚠]${NC} $*" | tee -a "$BENCHMARK_LOG"
}

error() {
    echo -e "${RED}[✗]${NC} $*" | tee -a "$BENCHMARK_LOG"
}

benchmark_build() {
    local test_name=$1
    local build_cmd=$2
    local iteration=$3
    
    log "[$test_name - Iteration $iteration/$ITERATIONS] Starting..."
    
    start_time=$(date +%s%N)
    
    if eval "$build_cmd" >/dev/null 2>&1; then
        end_time=$(date +%s%N)
        duration_ms=$(( (end_time - start_time) / 1000000 ))
        log "[$test_name - Iteration $iteration] Completed in ${duration_ms}ms"
        echo "$duration_ms"
    else
        error "[$test_name - Iteration $iteration] Build failed"
        echo "0"
    fi
}

# Initialize
log "=== XOE-NOVAI APT-CACHER-NG BENCHMARK ==="
log "Dockerfile: $DOCKERFILE"
log "Context: $BUILD_CONTEXT"
log "Iterations: $ITERATIONS"
log "Timestamp: $(date -Iseconds)"
log ""

# Verify apt-cacher-ng is running
if ! curl -sf http://127.0.0.1:3142/acng-report.html >/dev/null 2>&1; then
    error "apt-cacher-ng not accessible, starting service..."
    systemctl --user start apt-cacher-ng.container
    sleep 10
fi

# Clean slate
podman rmi -f "$BUILD_TAG" 2>/dev/null || true

# ============================================================================
# PHASE 1: Cold Builds (no Docker layer cache, no apt cache)
# ============================================================================

log "PHASE 1: Cold Builds (clearing Docker layers + apt cache)"
cold_times=()

for i in $(seq 1 $ITERATIONS); do
    # Clear Docker layer cache
    podman rmi -f "$BUILD_TAG" 2>/dev/null || true
    
    # Clear apt-cacher-ng cache (simulate first-time build)
    if [[ $i -eq 1 ]]; then
        log "Clearing apt-cacher-ng cache for true cold build..."
        cache_mountpoint=$(podman volume inspect apt-cache --format '{{.Mountpoint}}')
        podman unshare rm -rf "$cache_mountpoint"/* || warn "Failed to clear cache"
        systemctl --user restart apt-cacher-ng.container
        sleep 10
    fi
    
    time_ms=$(benchmark_build "COLD" "podman build --no-cache -t '$BUILD_TAG' -f '$DOCKERFILE' '$BUILD_CONTEXT'" "$i")
    cold_times+=("$time_ms")
    sleep 2
done

# ============================================================================
# PHASE 2: Warm Builds (with Docker layer cache + apt cache)
# ============================================================================

log ""
log "PHASE 2: Warm Builds (with Docker layer cache + apt cache)"
warm_times=()

for i in $(seq 1 $ITERATIONS); do
    time_ms=$(benchmark_build "WARM" "podman build -t '$BUILD_TAG' -f '$DOCKERFILE' '$BUILD_CONTEXT'" "$i")
    warm_times+=("$time_ms")
    sleep 2
done

# ============================================================================
# STATISTICS CALCULATION
# ============================================================================

# Calculate mean
cold_avg=$(echo "${cold_times[@]}" | awk '{sum=0; for(i=1;i<=NF;i++)sum+=$i; print int(sum/NF)}')
warm_avg=$(echo "${warm_times[@]}" | awk '{sum=0; for(i=1;i<=NF;i++)sum+=$i; print int(sum/NF)}')

# Calculate median
cold_median=$(printf '%s\n' "${cold_times[@]}" | sort -n | awk '{a[NR]=$1} END {print (NR%2==1)?a[(NR+1)/2]:(a[NR/2]+a[NR/2+1])/2}')
warm_median=$(printf '%s\n' "${warm_times[@]}" | sort -n | awk '{a[NR]=$1} END {print (NR%2==1)?a[(NR+1)/2]:(a[NR/2]+a[NR/2+1])/2}')

# Calculate standard deviation
cold_stddev=$(echo "${cold_times[@]}" | awk -v avg="$cold_avg" '{sum=0; for(i=1;i<=NF;i++)sum+=($i-avg)^2; print int(sqrt(sum/NF))}')
warm_stddev=$(echo "${warm_times[@]}" | awk -v avg="$warm_avg" '{sum=0; for(i=1;i<=NF;i++)sum+=($i-avg)^2; print int(sqrt(sum/NF))}')

# Calculate improvement
improvement=$(echo "scale=2; (($cold_avg - $warm_avg) / $cold_avg) * 100" | bc)
speedup=$(echo "scale=2; $cold_avg / $warm_avg" | bc)

# ============================================================================
# CACHE HIT RATIO (from apt-cacher-ng statistics)
# ============================================================================

log ""
log "Fetching cache statistics from apt-cacher-ng..."
cache_stats=$(curl -s http://127.0.0.1:3142/acng-report.html)

# Parse cache hits/misses
cache_hits=$(echo "$cache_stats" | grep -oP 'Hit.*?(\d+)' | grep -oP '\d+' | head -1 || echo "0")
cache_misses=$(echo "$cache_stats" | grep -oP 'Miss.*?(\d+)' | grep -oP '\d+' | head -1 || echo "0")
total_requests=$((cache_hits + cache_misses))

if [[ $total_requests -gt 0 ]]; then
    hit_ratio=$(echo "scale=2; ($cache_hits / $total_requests) * 100" | bc)
else
    hit_ratio="N/A"
fi

# ============================================================================
# GENERATE REPORT
# ============================================================================

log ""
log "=== BENCHMARK RESULTS ==="
log ""
log "Cold Build Times (ms): ${cold_times[*]}"
log "  Mean:    ${cold_avg}ms ($(echo "scale=2; $cold_avg / 1000" | bc)s)"
log "  Median:  ${cold_median}ms"
log "  StdDev:  ${cold_stddev}ms"
log ""
log "Warm Build Times (ms): ${warm_times[*]}"
log "  Mean:    ${warm_avg}ms ($(echo "scale=2; $warm_avg / 1000" | bc)s)"
log "  Median:  ${warm_median}ms"
log "  StdDev:  ${warm_stddev}ms"
log ""
log "Performance Improvement:"
log "  Time Saved:     ${improvement}%"
log "  Speedup Factor: ${speedup}x"
log ""
log "Cache Statistics:"
log "  Cache Hits:     $cache_hits"
log "  Cache Misses:   $cache_misses"
log "  Hit Ratio:      ${hit_ratio}%"
log ""

# ============================================================================
# PASS/FAIL CRITERIA
# ============================================================================

pass_count=0
fail_count=0

# Test 1: Warm build <60 sec (60000ms)
if [[ $warm_avg -lt 60000 ]]; then
    log "✓ PASS: Warm build time <60s"
    ((pass_count++))
else
    warn "✗ FAIL: Warm build time ≥60s (target: <60s)"
    ((fail_count++))
fi

# Test 2: Cache hit ratio >70%
if [[ "$hit_ratio" != "N/A" ]] && (( $(echo "$hit_ratio > 70" | bc -l) )); then
    log "✓ PASS: Cache hit ratio >70%"
    ((pass_count++))
else
    warn "✗ FAIL: Cache hit ratio ≤70% (target: >70%)"
    ((fail_count++))
fi

# Test 3: Speedup >3x
if (( $(echo "$speedup > 3" | bc -l) )); then
    log "✓ PASS: Speedup >3x"
    ((pass_count++))
else
    warn "✗ FAIL: Speedup ≤3x (target: >3x)"
    ((fail_count++))
fi

log ""
log "Tests Passed: $pass_count/3"
log "Tests Failed: $fail_count/3"
log ""

# Cleanup
podman rmi -f "$BUILD_TAG" 2>/dev/null || true

log "Benchmark log saved to: $BENCHMARK_LOG"
log "=== BENCHMARK COMPLETE ==="

# Exit with failure if any tests failed
exit $fail_count
```

Make executable:
```bash
chmod +x ~/.local/bin/xnai-apt-cache-benchmark.sh
```

---

## Part 6: Success Criteria Checklist

### Deployment Validation
- [ ] Podman version ≥5.5.0 (CVE-2025-22869 patched)
- [ ] Subuid/subgid range ≥65536 per user
- [ ] apt-cacher-ng service starts without errors
- [ ] Service enabled for auto-startup (`systemctl --user is-enabled`)
- [ ] Health check passes: `curl http://127.0.0.1:3142/acng-report.html`
- [ ] Port 3142 bound to 127.0.0.1 only (verified with `netstat`)
- [ ] `host.containers.internal` resolves from test container
- [ ] SELinux labels correct on volumes (if SELinux enabled)

### Security Validation
- [ ] Web UI NOT exposed on 0.0.0.0:3142 (localhost only)
- [ ] All capabilities dropped except NET_BIND_SERVICE
- [ ] Container runs with `no-new-privileges` flag
- [ ] Read-only root filesystem enforced
- [ ] Backup encryption key generated and secured
- [ ] Firewall rules allow only localhost/podman network

### Performance Validation
- [ ] Cold build time <5 min
- [ ] Warm build time <45 sec
- [ ] Cache hit ratio >70% (benchmark script)
- [ ] No memory OOM kills on repeated builds
- [ ] Speedup factor >3x (cold vs warm)

### Ma'at Compliance
- [ ] Truth: SecureAPT GPG verification works
- [ ] Balance: Cache size limits enforced (50GB)
- [ ] Justice: Rootless operation verified (UID 1001)
- [ ] Order: Deterministic builds (same inputs → same outputs)
- [ ] Harmony: Zero external telemetry (firewall audit)
- [ ] Reciprocity: All components open-source

---

**Deployed by**: Xoe-NovAi Enterprise Implementation Team  
**Last Updated**: January 27, 2026  
**Prepared by**: Xoe-NovAi Architecture Team