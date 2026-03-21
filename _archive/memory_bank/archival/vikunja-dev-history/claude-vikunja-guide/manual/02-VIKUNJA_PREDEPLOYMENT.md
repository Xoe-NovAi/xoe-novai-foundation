# Vikunja Implementation Manual - Part 2: Pre-Deployment Setup

**Version**: 1.0  
**Updated**: 2026-02-07  
**Estimated Time**: 1 hour  
**Target Audience**: Cline (Local Developer Assistant)

---

## Table of Contents

1. [Environment Validation](#environment-validation)
2. [Directory Structure Preparation](#directory-structure-preparation)
3. [Secrets Initialization](#secrets-initialization)
4. [Configuration Files](#configuration-files)
5. [Pre-Flight Checks](#pre-flight-checks)

---

## Environment Validation

### Check 1: Podman Version & Installation

```bash
# Cline: Execute this validation
podman --version

# Expected output: podman version 4.0.0 or higher
# If not installed: https://podman.io/docs/installation
```

**What Cline needs to verify**:
- ✅ Version ≥ 4.0.0 (4.2+ recommended)
- ✅ `podman compose` plugin installed (`podman compose version`)
- ✅ Podman socket running: `podman info` returns valid JSON

**If fails**: 
```bash
# Ubuntu/Debian
sudo apt-get install -y podman podman-compose

# Fedora/RHEL
sudo dnf install -y podman podman-compose

# Verify
podman unshare id  # Should show uid=0(root) inside userns
```

---

### Check 2: User Namespace Configuration

```bash
# Cline: Validate subuid/subgid mappings
grep "^$(whoami):" /etc/subuid /etc/subgid

# Expected output (example):
# /etc/subuid:appuser:100000:65536
# /etc/subgid:appuser:100000:65536
```

**What Cline needs to verify**:
- ✅ Your user has at least 65536 subordinate UIDs
- ✅ Your user has at least 65536 subordinate GIDs
- ✅ Range covers UID 1000-1100 (for containers)

**If insufficient**:
```bash
# Add larger ranges (requires root or admin)
sudo usermod --add-subuids 100000-165535 $(whoami)
sudo usermod --add-subgids 100000-165535 $(whoami)

# Restart Podman daemon
podman system reset  # WARNING: removes all containers/volumes!
```

---

### Check 3: SELinux Status

```bash
# Cline: Check if SELinux is enabled
getenforce  # or: sestatus

# Possible outputs:
# - "Enforcing" (strict security)
# - "Permissive" (warnings only)
# - "Disabled" (no SELinux)
```

**What Cline needs to know**:
- ✅ If "Enforcing" or "Permissive": Must use `:Z` volume flags
- ✅ If "Disabled": `:Z` flag is harmless (no-op)
- ✅ Recommended: Keep SELinux enabled (adds no complexity with :Z)

**Impact on volume mounting**:
- ✅ All volumes MUST include `:Z` flag (handled automatically in compose)
- ✅ Pre-chown with `podman unshare` (prevents permission errors)

---

### Check 4: Disk Space & Filesystem

```bash
# Cline: Verify disk space
df -h $(pwd)
# Need at least 10GB free for: OS + containers + data

# Check filesystem type
df -T $(pwd)
# ext4/btrfs/xfs recommended (NOT FAT32/NTFS)

# Check mount flags
mount | grep "$(pwd)"
# Should NOT have 'nodev' (blocks device files)
```

**What Cline needs to verify**:
- ✅ At least 10GB free space
- ✅ Native Linux filesystem (ext4, btrfs, xfs, etc.)
- ✅ No restrictive mount flags (noexec, nodev should not be present)

---

### Check 5: SELinux Relabeling Permission

```bash
# Cline: Test if :Z flag will work
mkdir -p /tmp/podman-test
podman run --rm -v /tmp/podman-test:/test:Z busybox touch /test/hello
ls -la /tmp/podman-test/hello

# If succeeds: ✅ :Z flag works
# If "Permission denied": ⚠️ SELinux misconfiguration
```

---

## Directory Structure Preparation

### Step 1: Create Base Directory Tree

```bash
# Cline: Run this block to set up all directories
cd ~/xoe-novai  # Your project root

mkdir -p \
  data/vikunja/{db,files} \
  data/redis \
  data/faiss_index \
  config \
  secrets \
  backups \
  logs/vikunja

# Verify structure
tree -L 3 data/ config/ secrets/ -I '__pycache__|*.pyc'
# Should show:
# ├── data/
# │   ├── vikunja/
# │   │   ├── db
# │   │   └── files
# │   ├── redis
# │   └── faiss_index
# ├── config/
# │   ├── postgres.conf
# │   ├── vikunja-config.yaml
# │   └── (others)
# └── secrets/
#     ├── redis_password.txt
#     └── (others - created next)
```

### Step 2: Set Correct Permissions (Pre-Podman)

```bash
# Cline: Fix permissions BEFORE Podman touches volumes
# (This prevents: "Operation not permitted" errors later)

# Use podman unshare to set permissions in container's userns
podman unshare chown 1000:1000 -R data/vikunja

# Verify from host perspective
ls -la data/vikunja/
# Should show: drwxr-xr-x (owned by your user)

# Verify from inside userns
podman unshare ls -la data/vikunja/
# Should show: drwxr-xr-x root:root (because your UID maps to 0 in userns)
```

**Why this matters**:
- ✅ Container UID 1000 maps to your host UID (via userns)
- ✅ Pre-chowning prevents: "Permission denied" when Vikunja writes to /app/vikunja/files
- ✅ **Must be done BEFORE container first start**

### Step 3: Initialize Database Directory

```bash
# Cline: PostgreSQL needs special setup
mkdir -p data/vikunja/db
chmod 700 data/vikunja/db  # PostgreSQL requires 700

# Verify
ls -la data/vikunja/
# db should show: drwx------ (not drwxr-xr-x)

# Fix with unshare if needed
podman unshare chmod 700 data/vikunja/db
```

**Why 700 permissions**:
- PostgreSQL refuses to start with world-readable data directory (security)
- Container processes run as UID 1000 inside container
- Host sees as your UID (outside userns)

---

## Secrets Initialization

### Step 1: Generate & Store Secrets

```bash
# Cline: Create secure secrets
# These will be injected as Podman secrets (not in plaintext compose!)

# Create secrets directory if not exists
mkdir -p secrets

# 1. Redis password (already exists from Foundation, reuse)
if [ ! -f secrets/redis_password.txt ]; then
    cat secrets/redis_password.txt > /dev/null 2>&1 && \
        echo "✅ Redis password exists (from Foundation)" || \
        echo "⚠️ Redis password missing (should exist from Foundation setup)"
fi

# 2. Vikunja Database password (NEW)
openssl rand -base64 32 > secrets/vikunja_db_password.txt
chmod 600 secrets/vikunja_db_password.txt
echo "✅ Created: vikunja_db_password.txt"

# 3. Vikunja JWT secret (NEW)
openssl rand -base64 64 > secrets/vikunja_jwt_secret.txt
chmod 600 secrets/vikunja_jwt_secret.txt
echo "✅ Created: vikunja_jwt_secret.txt"

# Verify all secrets exist and are readable only by you
ls -la secrets/
# All should show: -rw------- (600 permissions)
```

**Secret Values Reference** (for troubleshooting only):
```bash
# Cline: If you need to view a secret value (for verification)
cat secrets/vikunja_db_password.txt

# Display as env var (for debugging compose)
echo "VIKUNJA_DATABASE_PASSWORD=$(cat secrets/vikunja_db_password.txt)"
```

### Step 2: Create Podman Secrets

```bash
# Cline: Import secrets into Podman's secret store
# This makes them injectable without plaintext in compose files

# Remove old secrets if re-initializing
podman secret rm redis_password vikunja_db_password vikunja_jwt_secret 2>/dev/null || true

# Create fresh secrets from files
podman secret create redis_password < secrets/redis_password.txt
podman secret create vikunja_db_password < secrets/vikunja_db_password.txt
podman secret create vikunja_jwt_secret < secrets/vikunja_jwt_secret.txt

# Verify
podman secret list
# Should show:
# ID                          NAME                          DRIVER
# abc123...                   redis_password                file
# def456...                   vikunja_db_password           file
# ghi789...                   vikunja_jwt_secret            file

echo "✅ All Podman secrets created"
```

**Security Notes**:
- ✅ Secrets are stored in Podman's private store (not in docker-compose.yml)
- ✅ Only containers can access them (via `/run/secrets/name` inside container)
- ✅ Host filesystem doesn't expose secrets directly
- ⚠️ Still store `secrets/*.txt` files safely (git-ignored via .gitignore)

---

## Configuration Files

### Configuration File 1: PostgreSQL Tuning (`config/postgres.conf`)

```bash
# Cline: Create PostgreSQL optimization config
cat > config/postgres.conf << 'EOF'
# ============================================================================
# PostgreSQL 16 - Ryzen 5700U Optimization (Containerized)
# ============================================================================
# Target: Vikunja with <200MB footprint
# Hardware: AMD Ryzen 5700U (8 cores, 16GB system max)
# Update: 2026-02-07
# ============================================================================

# ========== MEMORY ==========
shared_buffers = 128MB              # 1/4 system RAM for Vikunja workload
effective_cache_size = 256MB        # Estimate total available cache
work_mem = 8MB                      # Per-operation memory (light sessions)
maintenance_work_mem = 32MB         # VACUUM/CREATE INDEX memory

# ========== CONNECTIONS ==========
max_connections = 20                # Vikunja + monitoring
max_prepared_transactions = 0       # Not used by Vikunja

# ========== WRITE PERFORMANCE ==========
synchronous_commit = off            # Trade durability for throughput (dev/test OK)
wal_level = minimal                 # No streaming replication needed
max_wal_senders = 0                 # No replication
wal_buffers = 4MB
checkpoint_timeout = 15min
checkpoint_completion_target = 0.9

# ========== QUERY TUNING ==========
random_page_cost = 1.1              # SSD/NVME (Ryzen laptop typical)
effective_io_concurrency = 200      # Ryzen L3 cache optimization
jit = off                           # JIT adds startup overhead (small queries)

# ========== LOGGING ==========
log_min_duration_statement = 1000   # Log slow queries >1s
log_connections = on
log_disconnections = on
log_duration = off

# ========== CRASH RECOVERY ==========
fsync = on                          # Keep enabled (data safety)
full_page_writes = on               # Crash recovery essential

# ========== TEMPORARY ==========
temp_buffers = 8MB
EOF

echo "✅ Created: config/postgres.conf"
```

### Configuration File 2: Vikunja Configuration (`config/vikunja-config.yaml`)

```bash
# Cline: Create Vikunja config file
cat > config/vikunja-config.yaml << 'EOF'
# ============================================================================
# Vikunja Configuration - Xoe-NovAi Integration
# ============================================================================
# Reference: https://vikunja.io/docs/config-options/
# Note: Environment variables (VIKUNJA_*) take precedence over this file
# Update: 2026-02-07
# ============================================================================

service:
  # Public URL for task/calendar sharing and frontend configuration
  publicurl: "http://localhost/vikunja"
  
  # Interface to bind to (handled by Docker, leave as default)
  interface: ":3456"
  
  # Task management features
  enablecalendar: true              # Calendar sync support
  enablesync: false                 # CalDAV disabled (air-gap)
  
  # File attachments
  maxfilesize: "20MB"               # Per Vikunja task

# Database configuration (overridden by env vars)
database:
  # Type handled by env vars, default to PostgreSQL
  maxopenconnections: 20            # Keep low for small systems
  maxidleconnections: 5
  connmaxlifetime: 0

# Authentication
auth:
  # JWT handled via environment variables
  local:
    enabled: true                   # Local accounts enabled
  openid:
    enabled: false                  # Disable external OAuth (sovereignty)

# File storage
files:
  basepath: "/app/vikunja/files"

# CORS (disabled, Caddy handles proxy)
cors:
  enabled: false

# Redis (optional, for sessions/cache)
redis:
  enabled: true
  host: "redis"
  port: 6379
  db: 5                             # Use DB 5 (Foundation uses 0-4)

# Logging
logger:
  level: "info"

# Mailer (disabled for air-gapped deployment)
mailer:
  enabled: false

# Legal/Branding
legalurl: ""
privacyurl: ""
EOF

echo "✅ Created: config/vikunja-config.yaml"
```

### Configuration File 3: Environment Variables (`.env` Update)

```bash
# Cline: Append Vikunja-specific environment variables to .env
cat >> .env << 'EOF'

# ============================================================================
# Vikunja Configuration (Phase 1)
# ============================================================================

# Database
VIKUNJA_DATABASE_TYPE=postgres
VIKUNJA_DATABASE_HOST=vikunja-db
VIKUNJA_DATABASE_PORT=5432
VIKUNJA_DATABASE_USER=vikunja
VIKUNJA_DATABASE_DATABASE=vikunja
# Password injected via Podman secret: /run/secrets/vikunja_db_password

# Service
VIKUNJA_SERVICE_PUBLICURL=http://localhost/vikunja
VIKUNJA_SERVICE_JWTEXPIRATION=86400  # 24h sessions
# JWT secret injected via Podman secret: /run/secrets/vikunja_jwt_secret

# Features
VIKUNJA_ENABLECALENDAR=true
VIKUNJA_ENABLESYNC=false            # Air-gapped (no external sync)

# Files
VIKUNJA_FILES_MAXSIZE=20971520      # 20MB

# Logging
VIKUNJA_LOGGER_LEVEL=info

# Mailer (disabled)
VIKUNJA_MAILER_ENABLED=false

# Redis (optional session backend)
VIKUNJA_REDIS_ENABLED=true
VIKUNJA_REDIS_HOST=redis
VIKUNJA_REDIS_PORT=6379
VIKUNJA_REDIS_DB=5
# Password injected via Podman secret: /run/secrets/redis_password
EOF

echo "✅ Appended Vikunja env vars to .env"
```

---

## Pre-Flight Checks

### Check List Before Deployment

```bash
# Cline: Run this validation script before `make up`

echo "🔍 Vikunja Pre-Deployment Checklist"
echo "======================================"

# 1. Directories exist
[ -d data/vikunja/db ] && echo "✅ data/vikunja/db exists" || echo "❌ MISSING: data/vikunja/db"
[ -d data/vikunja/files ] && echo "✅ data/vikunja/files exists" || echo "❌ MISSING: data/vikunja/files"
[ -d config ] && echo "✅ config/ exists" || echo "❌ MISSING: config/"
[ -d secrets ] && echo "✅ secrets/ exists" || echo "❌ MISSING: secrets/"

# 2. Configuration files exist
[ -f config/postgres.conf ] && echo "✅ config/postgres.conf exists" || echo "❌ MISSING: config/postgres.conf"
[ -f config/vikunja-config.yaml ] && echo "✅ config/vikunja-config.yaml exists" || echo "❌ MISSING: config/vikunja-config.yaml"

# 3. Secret files exist
[ -f secrets/redis_password.txt ] && echo "✅ secrets/redis_password.txt exists" || echo "❌ MISSING: secrets/redis_password.txt"
[ -f secrets/vikunja_db_password.txt ] && echo "✅ secrets/vikunja_db_password.txt exists" || echo "❌ MISSING: secrets/vikunja_db_password.txt"
[ -f secrets/vikunja_jwt_secret.txt ] && echo "✅ secrets/vikunja_jwt_secret.txt exists" || echo "❌ MISSING: secrets/vikunja_jwt_secret.txt"

# 4. Podman secrets created
podman secret list | grep -q "redis_password" && echo "✅ Podman secret: redis_password" || echo "❌ MISSING: Podman secret redis_password"
podman secret list | grep -q "vikunja_db_password" && echo "✅ Podman secret: vikunja_db_password" || echo "❌ MISSING: Podman secret vikunja_db_password"
podman secret list | grep -q "vikunja_jwt_secret" && echo "✅ Podman secret: vikunja_jwt_secret" || echo "❌ MISSING: Podman secret vikunja_jwt_secret"

# 5. Permissions set correctly
stat data/vikunja/db | grep -q "700" && echo "✅ data/vikunja/db has 700 permissions" || echo "⚠️  data/vikunja/db permissions not 700"
stat config/postgres.conf | grep -q "644" && echo "✅ config/postgres.conf is readable" || echo "⚠️  config/postgres.conf permissions issue"

# 6. Podman version check
PODMAN_VER=$(podman --version | grep -oP '(?<=version\s)\d+' | head -1)
[ "$PODMAN_VER" -ge 4 ] && echo "✅ Podman version ≥ 4.0" || echo "❌ FAIL: Podman version < 4.0"

# 7. Disk space check
DISK_FREE=$(df $(pwd) | awk 'NR==2 {print $4}')  # in KB
[ "$DISK_FREE" -gt 10485760 ] && echo "✅ At least 10GB free" || echo "❌ FAIL: Less than 10GB free"

# 8. .env file sourced
[ -f .env ] && echo "✅ .env exists" || echo "⚠️  .env not found (may be OK if in shell)"

echo ""
echo "Pre-flight check complete!"
```

**Run this check**:
```bash
# Cline: Copy the script above into a file
cat > pre-flight-check.sh << 'SCRIPT_EOF'
# [paste script above]
SCRIPT_EOF

chmod +x pre-flight-check.sh
./pre-flight-check.sh
```

**If any check fails**:
1. Review the section that corresponds to the failed check
2. Re-run that setup step
3. Re-run `./pre-flight-check.sh` to confirm fix

---

## Safety Checklist

- [ ] Podman version ≥ 4.0 verified
- [ ] SELinux status known (Enforcing/Permissive/Disabled)
- [ ] User subuid/subgid ranges adequate (≥65536)
- [ ] Disk space ≥ 10GB available
- [ ] All directories created with correct permissions
- [ ] All configuration files created with correct syntax
- [ ] All secrets generated and stored
- [ ] All Podman secrets created
- [ ] `.env` file updated with Vikunja variables
- [ ] Pre-flight checks passing
- [ ] **Git status clean**: `git status` shows no uncommitted changes to track

---

## Cleanup (If Starting Over)

```bash
# Cline: Complete cleanup (DESTRUCTIVE - removes all data)
# Only use if you need to completely reset

# Stop all containers
podman compose -f docker-compose.yml down
podman compose -f docker-compose.yml down 2>/dev/null || true

# Remove volumes and data
rm -rf data/vikunja/

# Remove Podman secrets
podman secret rm redis_password vikunja_db_password vikunja_jwt_secret 2>/dev/null || true

# Remove Podman networks (if needed)
podman network rm xnai_network 2>/dev/null || true

# Prune unused containers/images
podman system prune -af

echo "✅ Complete cleanup done (all data removed!)"
```

---

**Next Step**: Proceed to Part 3 (Docker Compose Configuration)

---

## Troubleshooting Pre-Deployment Issues

### Issue: "Permission denied" on data/vikunja/db

**Cause**: Permissions not set correctly for Podman userns

**Solution**:
```bash
podman unshare chown 1000:1000 -R data/vikunja/db
podman unshare chmod 700 data/vikunja/db
ls -la data/vikunja/  # Verify
```

### Issue: "Cannot create subvolumes"

**Cause**: Insufficient subuid/subgid ranges

**Solution**:
```bash
sudo usermod --add-subuids 100000-165535 $(whoami)
sudo usermod --add-subgids 100000-165535 $(whoami)
podman system reset  # WARNING: destructive
```

### Issue: Compose syntax error (invalid YAML)

**Solution**:
```bash
# Validate each file
podman compose -f docker-compose.yml config > /dev/null
podman compose -f docker-compose.yml config > /dev/null

# Check for common YAML issues:
# - Tabs instead of spaces (YAML doesn't allow tabs)
# - Inconsistent indentation
# - Unclosed quotes or colons
```

---

**Ready for Part 3**? Proceed when pre-flight checks pass ✅
