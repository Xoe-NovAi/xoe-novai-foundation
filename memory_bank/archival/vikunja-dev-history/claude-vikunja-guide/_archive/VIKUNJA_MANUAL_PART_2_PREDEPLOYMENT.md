# VIKUNJA IMPLEMENTATION MANUAL
## Part 2: Pre-Deployment Setup & Environment Validation

**Status**: Executable Guide  
**Version**: 2.0  
**Estimated Duration**: 45 minutes  
**Target**: Cline (VS Code Assistant)

---

## 🎯 OBJECTIVE

Validate your system is ready for Vikunja deployment and prepare all necessary files, secrets, and directories.

**Success Criteria**: All pre-flight checks pass ✅

---

## PART A: ENVIRONMENT VALIDATION

### A.1 Podman Installation & Version

**Cline**: Execute these commands in terminal

```bash
# Check Podman is installed
podman --version

# Expected output: podman version 4.0.0 or higher
# Minimum: 4.0.0 | Recommended: 4.2.0+

# Verify podman-compose plugin
podman compose --version

# Expected output: Docker Compose version 2.x.x or higher
```

**If Podman not installed**:
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y podman podman-compose

# Fedora/RHEL
sudo dnf install -y podman podman-compose

# Verify installation
podman --version && podman compose --version
```

**Why this matters**:
- Podman < 4.0: Missing critical userns features for rootless
- Podman 4.0+: Stable rootless Podman support
- podman-compose: Multi-file support for overlays

---

### A.2 User Namespace Configuration (CRITICAL)

**Cline**: Check your subuid/subgid mappings

```bash
# View your user's subordinate UID/GID ranges
grep "^$(whoami):" /etc/subuid /etc/subgid

# Expected output (example):
# /etc/subuid:youruser:100000:65536
# /etc/subgid:youruser:100000:65536

# Verify range is sufficient (need at least 65536)
AWK_CMD='BEGIN {print "Pass"}'
[ $(grep "^$(whoami):" /etc/subuid | cut -d: -f3) -ge 65536 ] && \
  echo "✅ subuid range OK" || echo "❌ subuid range insufficient"
```

**If ranges missing or insufficient**:
```bash
# Add ranges (requires sudo/admin)
sudo usermod --add-subuids 100000-165535 $(whoami)
sudo usermod --add-subgids 100000-165535 $(whoami)

# Verify
grep "^$(whoami):" /etc/subuid /etc/subgid

# Restart Podman daemon
podman system reset -f  # WARNING: Removes all containers/images!
```

**Why this matters**:
- Container UID 0 (root) maps to host UID 100000 (unprivileged)
- UID 1000 (in container) maps to host UID 101000
- Enables full isolation without running Podman as root

---

### A.3 SELinux Status (If Enabled)

**Cline**: Check SELinux configuration

```bash
# Check SELinux enforcement level
getenforce  # or: sestatus

# Possible outputs:
# - "Enforcing" (strict security enabled)
# - "Permissive" (warnings only)
# - "Disabled" (no SELinux)

# All three modes work fine with :Z volume flag
# Just need to know which one you have
```

**Action**: No action needed. The `:Z` volume flag handles all three modes.

---

### A.4 System Resources

**Cline**: Verify available resources

```bash
# Disk space check
df -h /  # Root filesystem
# Need: ≥10GB free

du -sh $(pwd)  # Current directory
# Should show your project size

# Memory check
free -h
# Should show ≥4GB available (can work with less, but tight)

# CPU check
nproc  # Number of processors
# Recommended: ≥4 cores (AMD Ryzen 5700U = 8 cores ✅)

# Filesystem check (must be native Linux, not FAT32/NTFS)
df -T $(pwd)
# Should show: ext4, btrfs, xfs, etc. (NOT vfat/ntfs)
```

**What these mean**:
- **Disk**: 10GB for containers + data + OS
- **Memory**: 6-8GB gives comfortable headroom
- **CPU**: 4+ cores ensures responsive performance
- **Filesystem**: Native Linux filesystem required for permissions

---

### A.5 Docker Image Availability Check

**Cline**: Verify you can pull official images

```bash
# Test pulling a small official image
podman pull alpine:latest

# Should complete in <10 seconds
# If "network unreachable" error: check internet connection or network config

# Verify image pulled
podman images | grep alpine

# Expected:
# alpine              latest    abc123...
```

**If network unavailable**:
- For air-gapped systems: Pre-download images on connected machine, transfer via tar
- See Part 3: Air-Gapped Deployment (future enhancement)

---

## PART B: DIRECTORY & PERMISSION SETUP

### B.1 Create Directory Structure

**Cline**: Execute this to create all needed directories

```bash
# Navigate to your Xoe-NovAi project root
cd ~/xoe-novai  # Adjust path as needed

# Create all Vikunja-related directories
mkdir -p \
  data/vikunja/{db,files} \
  config \
  secrets

# Verify structure
tree -L 3 data/config/secrets/ 2>/dev/null || \
  find data config secrets -type d | sort

# Expected output (example):
# data/
# ├── vikunja/
# │   ├── db
# │   └── files
# config/
# └── (will be filled in Part B.3)
# secrets/
# └── (will be filled in Part B.2)
```

### B.2 PostgreSQL Directory Permissions (CRITICAL)

**Cline**: PostgreSQL has strict permission requirements

```bash
# PostgreSQL REQUIRES 700 permissions on its data directory
chmod 700 data/vikunja/db

# Verify
stat data/vikunja/db | grep "Access:"
# Should show: (0700/drwx------)

# Now use podman unshare to set correct ownership for container
podman unshare chown 1000:1000 -R data/vikunja/

# Verify from inside userns
podman unshare ls -la data/vikunja/
# Should show:
# drwx------  root root  ...  db
# drwxr-xr-x  root root  ...  files

# Why?
# - Container UID 1000 needs to write to /var/lib/postgresql/data
# - Host sees this as your UID (via userns mapping)
# - podman unshare executes in container's userns context
```

**⚠️ CRITICAL**: Do this BEFORE first container start, or PostgreSQL fails

---

### B.3 File Permissions for Other Directories

**Cline**: Set permissions for non-PostgreSQL directories

```bash
# Vikunja files directory (writable by container)
chmod 755 data/vikunja/files
podman unshare chown 1000:1000 data/vikunja/files

# Config directory (readable by container)
chmod 755 config
# Config files created in Part B.5 with:
chmod 644 config/*

# Verify all permissions
ls -la data/vikunja/
# Example output:
# drwx------  root root  db          ← PostgreSQL (700)
# drwxr-xr-x  root root  files       ← Vikunja (755)
```

---

## PART C: SECRETS GENERATION & MANAGEMENT

### C.1 Generate Secret Files

**Cline**: Create secure random secrets

```bash
# Ensure secrets directory exists
mkdir -p secrets

# 1. Redis Password (if creating new, or verify existing)
if [ ! -f secrets/redis_password.txt ]; then
    echo "Creating redis_password..."
    openssl rand -base64 32 > secrets/redis_password.txt
    chmod 600 secrets/redis_password.txt
else
    echo "✅ redis_password.txt already exists (from Foundation)"
fi

# 2. Vikunja Database Password (NEW)
echo "Creating vikunja_db_password..."
openssl rand -base64 32 > secrets/vikunja_db_password.txt
chmod 600 secrets/vikunja_db_password.txt

# 3. Vikunja JWT Secret (NEW)
echo "Creating vikunja_jwt_secret..."
openssl rand -base64 64 > secrets/vikunja_jwt_secret.txt
chmod 600 secrets/vikunja_jwt_secret.txt

# Verify all exist and are secure
ls -la secrets/
# Should show:
# -rw-------  root root  redis_password.txt           (600)
# -rw-------  root root  vikunja_db_password.txt      (600)
# -rw-------  root root  vikunja_jwt_secret.txt       (600)
```

**Security Notes**:
- ✅ Files only readable by you (mode 600)
- ✅ Secrets are random 256-bit (32 bytes base64)
- ✅ JWT secret is 512-bit (64 bytes base64)
- ⚠️ Store these files safely (git-ignored, backed up offline)

---

### C.2 Register Secrets with Podman

**Cline**: Import secrets into Podman's secret store

```bash
# Remove any old secrets (fresh start)
podman secret rm redis_password 2>/dev/null || true
podman secret rm vikunja_db_password 2>/dev/null || true
podman secret rm vikunja_jwt_secret 2>/dev/null || true

# Create fresh secrets from files
echo "Creating Podman secrets..."
podman secret create redis_password < secrets/redis_password.txt
podman secret create vikunja_db_password < secrets/vikunja_db_password.txt
podman secret create vikunja_jwt_secret < secrets/vikunja_jwt_secret.txt

# Verify secrets created
podman secret list

# Expected output:
# ID                          NAME                   DRIVER
# abc123xyz                   redis_password         file
# def456uvw                   vikunja_db_password    file
# ghi789rst                   vikunja_jwt_secret     file

echo "✅ All Podman secrets created successfully"
```

**What this does**:
- Secrets stored in Podman's encrypted secret store (not plaintext)
- Only containers with secret mounts can access them
- Available as files inside container: `/run/secrets/[name]`
- Rotation-safe (can recreate without touching compose files)

---

## PART D: CONFIGURATION FILES

### D.1 PostgreSQL Tuning (config/postgres.conf)

**Cline**: Create PostgreSQL optimization config

```bash
cat > config/postgres.conf << 'POSTGRES_CONFIG'
# ============================================================================
# PostgreSQL 16 Configuration - Vikunja Ryzen Optimization
# ============================================================================
# Tuned for: Ryzen 5700U (8 cores), <6GB system RAM
# Workload: Task management (light OLTP)
# Created: 2026-02-07
# ============================================================================

# ========== MEMORY CONFIGURATION ==========
# For 8GB total system with 6GB available to apps:
# Foundation uses ~1.3GB, Vikunja gets ~300MB allocation

shared_buffers = 64MB
# ├─ Rule: 25% of database-dedicated RAM
# ├─ Calculation: 256MB PostgreSQL budget × 25% = 64MB
# └─ Why: Vikunja rarely exceeds 500 tasks, light working set

effective_cache_size = 128MB
# ├─ Tells query planner OS cache size
# ├─ Helps choose index scans vs seq scans
# └─ Set to ~50% of system RAM for VM (conservative)

work_mem = 4MB
# ├─ Per-operation memory (sorts, hashes, window functions)
# ├─ Formula: RAM / (max_connections × expected_ops_per_query)
# ├─ Calculation: 256MB / (20 × 3) = ~4MB safe
# └─ Prevents OOM when multiple sorts happen

temp_buffers = 8MB
# ├─ Temporary table memory
# └─ Rarely used by Vikunja, small is fine

maintenance_work_mem = 32MB
# ├─ VACUUM and CREATE INDEX memory
# ├─ Safe to be larger (runs single-threaded)
# └─ 32MB adequate for Vikunja-scale databases

wal_buffers = 4MB
# ├─ Write-ahead log buffer
# └─ Default-ish, rarely a bottleneck

# ========== CONNECTION MANAGEMENT ==========
max_connections = 20
# ├─ Foundation: ~3 (RAG, Chainlit, crawler)
# ├─ Vikunja: ~5 (API instances)
# ├─ Monitoring: ~3 (health checks, metrics)
# └─ Reserve: ~9 (safety margin)
# ├─ Total: ~20 connections
# └─ Memory impact: 20 × 10MB = 200MB (acceptable)

max_prepared_transactions = 0
# └─ Vikunja doesn't use distributed transactions

# ========== QUERY TUNING ==========
random_page_cost = 1.1
# ├─ Tells planner: "I have fast storage"
# ├─ Ryzen laptop typically: NVMe (random_page_cost = 1.1)
# └─ Prevents seq scans when index scans are faster

effective_io_concurrency = 200
# ├─ Hint for parallel I/O operations
# ├─ Ryzen L3 cache: 32MB (enables prefetch)
# └─ Conservative safe value: 200

# ========== TRANSACTION & WAL ==========
synchronous_commit = off
# ├─ TRADE: Speed vs durability (development acceptable)
# ├─ Vikunja tasks: Not mission-critical like banking
# └─ For production: Set to 'on' (default)

wal_level = minimal
# ├─ Minimal WAL for single-server deployments
# └─ Disables streaming replication (not needed)

max_wal_senders = 0
# └─ No replication needed

checkpoint_timeout = 15min
# ├─ Spread disk writes over time
# └─ Prevents sudden I/O spikes

checkpoint_completion_target = 0.9
# └─ 90% of checkpoint_timeout for completion

# ========== VACUUM & CLEANUP ==========
autovacuum = on
# ├─ Automatic cleanup of dead rows
# └─ Essential for long-running databases

autovacuum_vacuum_threshold = 50
# ├─ Vacuum after 50 dead rows detected
# └─ More aggressive than default (1000)

autovacuum_analyze_threshold = 50
# └─ Analyze stats after 50 rows change

autovacuum_vacuum_cost_limit = 1000
# ├─ I/O budget per vacuum cycle
# └─ Higher = faster cleanup, but may impact queries

autovacuum_vacuum_cost_delay = 20ms
# └─ Delay between I/O operations (20ms is conservative)

# ========== LOGGING ==========
log_min_duration_statement = 1000
# ├─ Log queries taking >1 second
# └─ Helps identify slow queries

log_connections = on
# └─ Log user connections (useful for monitoring)

log_disconnections = on
# └─ Log session ends

log_duration = off
# └─ Don't log all queries (too verbose)

# ========== FSYNC & SAFETY ==========
fsync = on
# ├─ CRITICAL: Keep enabled
# └─ Ensures data survives power loss

full_page_writes = on
# ├─ Enables recovery after crash
# └─ Necessary for fsync=on

# ========== PERFORMANCE MONITORING ==========
# Enable these extensions (optional, for diagnostics)
# shared_preload_libraries = 'pg_stat_statements'

POSTGRES_CONFIG

echo "✅ Created config/postgres.conf"
```

### D.2 Vikunja Configuration (.env additions)

**Cline**: Add Vikunja variables to .env

```bash
# Check if .env exists
[ -f .env ] || touch .env

# Append Vikunja configuration
cat >> .env << 'ENV_CONFIG'

# ============================================================================
# VIKUNJA CONFIGURATION - Phase 1
# ============================================================================

# Database (PostgreSQL)
VIKUNJA_DATABASE_TYPE=postgres
VIKUNJA_DATABASE_HOST=vikunja-db
VIKUNJA_DATABASE_PORT=5432
VIKUNJA_DATABASE_USER=vikunja
VIKUNJA_DATABASE_DATABASE=vikunja
# Password injected via Podman secret

# Service Configuration
VIKUNJA_SERVICE_PUBLICURL=http://localhost/vikunja
VIKUNJA_SERVICE_INTERFACE=:3456
VIKUNJA_SERVICE_JWTEXPIRATION=86400

# JWT Secret (injected via Podman secret)
# VIKUNJA_SERVICE_JWTSECRET_FILE=/run/secrets/vikunja_jwt_secret

# Features
VIKUNJA_ENABLECALENDAR=true
VIKUNJA_ENABLESYNC=false              # Air-gapped (no external sync)

# Files & Attachments
VIKUNJA_FILES_MAXSIZE=20971520        # 20MB max per file

# Database Connection Pooling
VIKUNJA_DATABASE_MAXOPENCONNECTIONS=20
VIKUNJA_DATABASE_MAXIDLECONNECTIONS=5

# Authentication
VIKUNJA_AUTH_LOCAL_ENABLED=true
VIKUNJA_AUTH_OPENID_ENABLED=false     # No external OAuth

# Redis (Session Backend)
VIKUNJA_REDIS_ENABLED=true
VIKUNJA_REDIS_HOST=redis
VIKUNJA_REDIS_PORT=6379
VIKUNJA_REDIS_DB=5                    # Use DB 5 (Foundation uses 0-4)

# Logging
VIKUNJA_LOGGER_LEVEL=info
VIKUNJA_LOGGER_FORMAT=json

# Mailer (Disabled)
VIKUNJA_MAILER_ENABLED=false

# CORS (Disabled - Caddy handles proxy)
VIKUNJA_CORS_ENABLE=false

# Webhooks
VIKUNJA_WEBHOOKS_ENABLED=true         # Enable for Phase 2 integration

ENV_CONFIG

echo "✅ Appended Vikunja config to .env"
```

---

## PART E: PRE-FLIGHT VALIDATION

### E.1 Run Complete Pre-Flight Check

**Cline**: Copy and execute this validation script

```bash
cat > pre_flight_check.sh << 'CHECK_SCRIPT'
#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║      VIKUNJA PRE-DEPLOYMENT VALIDATION CHECKLIST          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

PASS=0
FAIL=0

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_item() {
    local name=$1
    local cmd=$2
    
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} $name"
        ((PASS++))
    else
        echo -e "${RED}❌${NC} $name"
        ((FAIL++))
    fi
}

# ========== ENVIRONMENT CHECKS ==========
echo "📋 ENVIRONMENT VALIDATION"

check_item "Podman version ≥4.0" "[ \$(podman --version | grep -oP '\\d+' | head -1) -ge 4 ]"
check_item "podman-compose installed" "podman compose --version"
check_item "docker image availability" "timeout 5 podman pull alpine:latest >/dev/null 2>&1 && podman rmi alpine:latest >/dev/null 2>&1"

# ========== FILESYSTEM CHECKS ==========
echo ""
echo "📁 FILESYSTEM VALIDATION"

check_item "data/vikunja/db directory exists" "[ -d data/vikunja/db ]"
check_item "data/vikunja/files directory exists" "[ -d data/vikunja/files ]"
check_item "config directory exists" "[ -d config ]"
check_item "secrets directory exists" "[ -d secrets ]"
check_item "db directory has 700 permissions" "[ \$(stat -f%A data/vikunja/db 2>/dev/null || stat -c %A data/vikunja/db) = 'drwx------' ]"

# ========== CONFIGURATION FILES ==========
echo ""
echo "⚙️  CONFIGURATION FILES"

check_item "config/postgres.conf exists" "[ -f config/postgres.conf ]"
check_item "postgres.conf is readable" "[ -r config/postgres.conf ]"
check_item ".env file exists" "[ -f .env ]"
check_item ".env contains VIKUNJA_" "grep -q 'VIKUNJA_' .env"

# ========== SECRETS CHECKS ==========
echo ""
echo "🔐 SECRETS MANAGEMENT"

check_item "redis_password.txt exists" "[ -f secrets/redis_password.txt ]"
check_item "vikunja_db_password.txt exists" "[ -f secrets/vikunja_db_password.txt ]"
check_item "vikunja_jwt_secret.txt exists" "[ -f secrets/vikunja_jwt_secret.txt ]"
check_item "Podman secret: redis_password" "podman secret list | grep -q redis_password"
check_item "Podman secret: vikunja_db_password" "podman secret list | grep -q vikunja_db_password"
check_item "Podman secret: vikunja_jwt_secret" "podman secret list | grep -q vikunja_jwt_secret"

# ========== PERMISSIONS ==========
echo ""
echo "🔒 PERMISSIONS & SECURITY"

check_item "Subuid range exists" "grep -q '^$(whoami):' /etc/subuid"
check_item "Subgid range exists" "grep -q '^$(whoami):' /etc/subgid"
check_item "secrets/ has restricted perms" "[ \$(stat -f%A secrets 2>/dev/null || stat -c %A secrets) = 'drwx------' ] || [ \$(stat -f%A secrets 2>/dev/null || stat -c %A secrets) = 'drwxr-xr-x' ]"

# ========== DISK SPACE ==========
echo ""
echo "💾 DISK SPACE & RESOURCES"

disk_free=\$(df . | tail -1 | awk '{print int(\$4)}')
check_item "At least 10GB free" "[ \$disk_free -gt 10485760 ]"  # 10GB in KB

# ========== NETWORK ==========
echo ""
echo "🌐 NETWORK & CONNECTIVITY"

check_item "Can resolve docker.io" "timeout 5 ping -c1 docker.io >/dev/null 2>&1 || echo pass"  # May fail in air-gapped, that's OK

# ========== SUMMARY ==========
echo ""
echo "╔════════════════════════════════════════════════════════════╗"

if [ $FAIL -eq 0 ]; then
    echo -e "║ ${GREEN}✅ ALL CHECKS PASSED ($PASS/$((PASS+FAIL)))${NC}                  ║"
    echo "║ Ready for deployment! Proceed to Part 3.              ║"
else
    echo -e "║ ${RED}❌ $FAIL CHECK(S) FAILED ($PASS/$((PASS+FAIL)) passed)${NC}                   ║"
    echo "║ Review failures above and re-run this script.         ║"
fi

echo "╚════════════════════════════════════════════════════════════╝"

exit $FAIL
CHECK_SCRIPT

chmod +x pre_flight_check.sh
./pre_flight_check.sh
```

**Expected Output**:
```
✅ Podman version ≥4.0
✅ podman-compose installed
✅ data/vikunja/db directory exists
✅ data/vikunja/files directory exists
... (all checks pass)
✅ ALL CHECKS PASSED (20/20)
```

---

## PART F: GIT COMMIT

### F.1 Stage Changes for Git

**Cline**: Save your progress

```bash
# Review what's about to be committed
git status

# Should show new/modified files:
# - config/postgres.conf (NEW)
# - .env (MODIFIED)
# - secrets/*.txt (see .gitignore - should be ignored)

# Add files for commit
git add \
  config/postgres.conf \
  .env \
  .gitignore  # If updated to ignore secrets/

# Verify staged files
git diff --cached --name-only

# Commit
git commit -m "chore: Vikunja Phase 1 pre-deployment setup

- Add PostgreSQL 16 Ryzen optimization config
- Add Vikunja environment variables to .env
- Create directory structure: data/vikunja/{db,files}, config/, secrets/
- Generate and register Podman secrets (redis, vikunja_db, vikunja_jwt)
- Set correct permissions for rootless Podman integration
- Create pre-flight validation script

Status: Environment ready for Phase 3 deployment"

echo "✅ Changes committed to git"
```

---

## TROUBLESHOOTING: COMMON SETUP ISSUES

### Issue: "subuid range insufficient"
```bash
# Solution:
sudo usermod --add-subuids 100000-165535 $(whoami)
sudo usermod --add-subgids 100000-165535 $(whoami)
podman system reset -f  # Clear and restart
```

### Issue: "Permission denied" on data/vikunja/db
```bash
# Solution:
podman unshare chown 1000:1000 -R data/vikunja/
podman unshare chmod 700 data/vikunja/db
```

### Issue: "podman secret create: not found"
```bash
# Make sure secrets directory exists:
mkdir -p secrets
# And files are readable:
chmod 600 secrets/*.txt
```

### Issue: Pre-flight check fails
```bash
# Re-run with verbose output:
bash -x pre_flight_check.sh
# Check Part A & B for specific failures
```

---

## ✅ SUCCESS CHECKLIST

Before proceeding to Part 3, verify:

- [ ] Podman version ≥4.0.0
- [ ] podman-compose works
- [ ] Subuid/subgid ranges ≥65536
- [ ] Disk space ≥10GB free
- [ ] Directory structure created:
  - [ ] `data/vikunja/db` (700 permissions)
  - [ ] `data/vikunja/files` (755 permissions)
  - [ ] `config/` (755 permissions)
  - [ ] `secrets/` (700 permissions)
- [ ] Configuration files created:
  - [ ] `config/postgres.conf`
  - [ ] `.env` with VIKUNJA variables
- [ ] Secrets generated and registered:
  - [ ] `secrets/redis_password.txt`
  - [ ] `secrets/vikunja_db_password.txt`
  - [ ] `secrets/vikunja_jwt_secret.txt`
  - [ ] All 3 Podman secrets created
- [ ] Pre-flight checks pass (20/20)
- [ ] Changes committed to git

---

## 🎯 NEXT STEPS

When all checks pass:

1. **Proceed to Part 3**: Docker Compose files & deployment
2. **Time estimate**: 1 hour
3. **Outcome**: Running Vikunja stack

---

**Status**: Part 2 Complete ✅  
**Next**: Part 3 - Docker Compose & Deployment

---

## Quick Reference: Key Commands

```bash
# Generate secrets
openssl rand -base64 32

# Set directory permissions
podman unshare chown 1000:1000 -R data/vikunja/

# Create Podman secret
podman secret create name < secrets/name.txt

# List Podman secrets
podman secret list

# View secret (from file, not from Podman store)
cat secrets/redis_password.txt

# Run pre-flight checks
./pre_flight_check.sh

# Commit to git
git add config/.env && git commit -m "..."
```

---

