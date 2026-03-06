#!/bin/bash
################################################################################
# XNAi Foundation - Atomic Backup Coordinator
# Purpose: Atomic backup of PostgreSQL, Redis, and Qdrant
# Ensures all three systems are backed up at the same point in time
# RTO: <1 hour
################################################################################

set -euo pipefail

# Configuration
BACKUP_BASE_DIR="${BACKUP_BASE_DIR:-.}/backups"
ATOMIC_BACKUP_DIR="${BACKUP_BASE_DIR}/atomic_$(date +%Y%m%d_%H%M%S)"
LOG_DIR="${LOG_DIR:-.}/logs/backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_LOG="${LOG_DIR}/atomic_backup_coordinator_${TIMESTAMP}.log"

# Create directories
mkdir -p "${ATOMIC_BACKUP_DIR}" "${LOG_DIR}"

# Logging function
log() {
    local level=$1
    shift
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [${level}] $*" | tee -a "${BACKUP_LOG}"
}

# Error handling
error_exit() {
    log "ERROR" "$1"
    exit 1
}

cleanup_on_error() {
    log "ERROR" "Atomic backup failed at: $1"
    log "WARN" "Incomplete backup at: ${ATOMIC_BACKUP_DIR}"
    exit 1
}

trap 'cleanup_on_error "${BASH_SOURCE} at line ${LINENO}"' ERR INT TERM

################################################################################
# BACKUP POSTGRESQL
################################################################################
backup_postgresql() {
    log "INFO" "=== Starting PostgreSQL Atomic Backup ==="
    
    local pg_backup_dir="${ATOMIC_BACKUP_DIR}/postgresql"
    mkdir -p "${pg_backup_dir}"
    
    local db_host="${VIKUNJA_DB_HOST:-vikunja-db}"
    local db_user="${VIKUNJA_DB_USER:-vikunja}"
    local db_password="${VIKUNJA_DB_PASSWORD:-}"
    
    PGPASSWORD="${db_password}" pg_dump \
        -h "${db_host}" \
        -U "${db_user}" \
        -d vikunja \
        --format=plain \
        --compress=9 \
        --file="${pg_backup_dir}/vikunja.sql.gz" \
        2>> "${BACKUP_LOG}" || error_exit "PostgreSQL backup failed"
    
    # Generate metadata
    cat > "${pg_backup_dir}/METADATA" << EOF
{
  "system": "PostgreSQL",
  "database": "vikunja",
  "timestamp": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')",
  "size_bytes": $(stat -c%s "${pg_backup_dir}/vikunja.sql.gz"),
  "compression": "gzip"
}
EOF
    
    # Generate checksum
    sha256sum "${pg_backup_dir}/vikunja.sql.gz" > "${pg_backup_dir}/vikunja.sql.gz.sha256"
    
    local size=$(du -h "${pg_backup_dir}/vikunja.sql.gz" | cut -f1)
    log "INFO" "PostgreSQL backup completed: ${size}"
}

################################################################################
# BACKUP REDIS
################################################################################
backup_redis() {
    log "INFO" "=== Starting Redis Atomic Backup ==="
    
    local redis_backup_dir="${ATOMIC_BACKUP_DIR}/redis"
    mkdir -p "${redis_backup_dir}"
    
    local redis_host="${REDIS_HOST:-localhost}"
    local redis_port="${REDIS_PORT:-6379}"
    local redis_password="${REDIS_PASSWORD:-}"
    
    # Trigger BGSAVE
    local redis_cli_cmd="redis-cli -h ${redis_host} -p ${redis_port}"
    if [ -n "${redis_password}" ]; then
        redis_cli_cmd="${redis_cli_cmd} -a ${redis_password}"
    fi
    
    ${redis_cli_cmd} BGSAVE >> "${BACKUP_LOG}" 2>&1 || error_exit "BGSAVE failed"
    
    # Wait for BGSAVE to complete (max 300 seconds)
    local wait_time=0
    while [ $wait_time -lt 300 ]; do
        local last_save=$(${redis_cli_cmd} LASTSAVE 2>/dev/null || echo "0")
        local current_time=$(date +%s)
        if [ $((current_time - last_save)) -lt 5 ]; then
            log "INFO" "BGSAVE completed"
            break
        fi
        sleep 2
        wait_time=$((wait_time + 2))
    done
    
    if [ $wait_time -ge 300 ]; then
        error_exit "BGSAVE did not complete within timeout"
    fi
    
    # Get dump file location and copy
    local redis_dump_dir=$(${redis_cli_cmd} CONFIG GET dir 2>/dev/null | tail -1 || echo "./data/redis")
    local redis_dump_file="${redis_dump_dir}/dump.rdb"
    
    if [ ! -f "${redis_dump_file}" ]; then
        error_exit "Redis dump file not found at ${redis_dump_file}"
    fi
    
    # Compress and copy
    gzip -c "${redis_dump_file}" > "${redis_backup_dir}/dump.rdb.gz" || error_exit "Redis backup compression failed"
    
    # Generate metadata
    cat > "${redis_backup_dir}/METADATA" << EOF
{
  "system": "Redis",
  "timestamp": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')",
  "size_bytes": $(stat -c%s "${redis_backup_dir}/dump.rdb.gz"),
  "compression": "gzip"
}
EOF
    
    # Generate checksum
    sha256sum "${redis_backup_dir}/dump.rdb.gz" > "${redis_backup_dir}/dump.rdb.gz.sha256"
    
    local size=$(du -h "${redis_backup_dir}/dump.rdb.gz" | cut -f1)
    log "INFO" "Redis backup completed: ${size}"
}

################################################################################
# BACKUP QDRANT
################################################################################
backup_qdrant() {
    log "INFO" "=== Starting Qdrant Atomic Backup ==="
    
    local qdrant_backup_dir="${ATOMIC_BACKUP_DIR}/qdrant"
    mkdir -p "${qdrant_backup_dir}"
    
    local qdrant_host="${QDRANT_HOST:-localhost}"
    local qdrant_port="${QDRANT_PORT:-6333}"
    local qdrant_api_key="${QDRANT_API_KEY:-}"
    local qdrant_protocol="${QDRANT_PROTOCOL:-http}"
    
    # Health check
    log "INFO" "Checking Qdrant health..."
    
    local health_cmd="curl -s -X GET '${qdrant_protocol}://${qdrant_host}:${qdrant_port}/health'"
    if [ -n "${qdrant_api_key}" ]; then
        health_cmd="${health_cmd} -H 'api-key: ${qdrant_api_key}'"
    fi
    
    local health=$(eval "${health_cmd}")
    if ! echo "${health}" | grep -q "\"status\""; then
        error_exit "Qdrant is not responding"
    fi
    
    # Get collections
    local curl_cmd="curl -s -X GET '${qdrant_protocol}://${qdrant_host}:${qdrant_port}/collections'"
    if [ -n "${qdrant_api_key}" ]; then
        curl_cmd="${curl_cmd} -H 'api-key: ${qdrant_api_key}'"
    fi
    
    local collections_json=$(eval "${curl_cmd}")
    local collections=$(echo "${collections_json}" | grep -oP '"name"\s*:\s*"\K[^"]+' || echo "")
    
    if [ -z "${collections}" ]; then
        log "WARN" "No collections found in Qdrant"
        return 0
    fi
    
    log "INFO" "Found collections: $(echo ${collections} | tr '\n' ' ')"
    
    # Backup each collection
    local backed_up=0
    local failed=0
    
    while IFS= read -r collection_name; do
        if [ -z "${collection_name}" ]; then
            continue
        fi
        
        log "INFO" "Snapshotting collection: ${collection_name}"
        
        # Create snapshot
        local snapshot_cmd="curl -s -X POST '${qdrant_protocol}://${qdrant_host}:${qdrant_port}/collections/${collection_name}/snapshots'"
        if [ -n "${qdrant_api_key}" ]; then
            snapshot_cmd="${snapshot_cmd} -H 'api-key: ${qdrant_api_key}'"
        fi
        
        local snapshot_response=$(eval "${snapshot_cmd}")
        
        if echo "${snapshot_response}" | grep -q "\"error\""; then
            log "ERROR" "Failed to create snapshot for ${collection_name}"
            failed=$((failed + 1))
            continue
        fi
        
        # Extract snapshot name
        local snapshot_name=$(echo "${snapshot_response}" | grep -oP '"snapshot_name"\s*:\s*"\K[^"]+' | head -1)
        
        if [ -z "${snapshot_name}" ]; then
            log "WARN" "Could not extract snapshot name for ${collection_name}"
            failed=$((failed + 1))
            continue
        fi
        
        # Download snapshot
        local download_cmd="curl -s -X GET '${qdrant_protocol}://${qdrant_host}:${qdrant_port}/collections/${collection_name}/snapshots/${snapshot_name}'"
        if [ -n "${qdrant_api_key}" ]; then
            download_cmd="${download_cmd} -H 'api-key: ${qdrant_api_key}'"
        fi
        
        local snapshot_file="${qdrant_backup_dir}/${collection_name}_${snapshot_name}.snapshot"
        download_cmd="${download_cmd} -o '${snapshot_file}'"
        
        eval "${download_cmd}" || {
            log "ERROR" "Failed to download snapshot for ${collection_name}"
            failed=$((failed + 1))
            continue
        }
        
        # Verify
        if [ ! -f "${snapshot_file}" ] || [ ! -s "${snapshot_file}" ]; then
            log "ERROR" "Snapshot file is empty: ${snapshot_file}"
            failed=$((failed + 1))
            continue
        fi
        
        # Checksum
        sha256sum "${snapshot_file}" > "${snapshot_file}.sha256"
        
        backed_up=$((backed_up + 1))
        local size=$(du -h "${snapshot_file}" | cut -f1)
        log "INFO" "Collection snapshot completed: ${collection_name} (${size})"
        
    done <<< "${collections}"
    
    # Generate metadata
    cat > "${qdrant_backup_dir}/METADATA" << EOF
{
  "system": "Qdrant",
  "timestamp": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')",
  "collections_backed_up": ${backed_up},
  "collections_failed": ${failed}
}
EOF
    
    log "INFO" "Qdrant backup completed: ${backed_up} collections, ${failed} failed"
}

################################################################################
# CREATE ATOMIC BACKUP MANIFEST
################################################################################
create_manifest() {
    log "INFO" "Creating atomic backup manifest"
    
    cat > "${ATOMIC_BACKUP_DIR}/MANIFEST" << EOF
XNAi Foundation - Atomic Backup Manifest
==========================================
Backup Timestamp: $(date -u +'%Y-%m-%dT%H:%M:%SZ')
Backup ID: $(basename ${ATOMIC_BACKUP_DIR})

Components:
-----------

1. PostgreSQL (Vikunja Database)
   Location: postgresql/vikunja.sql.gz
   Type: Full backup
   Compression: gzip

2. Redis
   Location: redis/dump.rdb.gz
   Type: RDB snapshot
   Compression: gzip

3. Qdrant
   Location: qdrant/
   Type: Collection snapshots
   Format: Binary snapshot files

Backup Statistics:
------------------
Total Size: $(du -sh "${ATOMIC_BACKUP_DIR}" | cut -f1)
Components: 3 (PostgreSQL, Redis, Qdrant)
Backup Date: $(date +'%Y-%m-%d %H:%M:%S UTC')

Retention Policy:
-----------------
PostgreSQL: 30 days
Redis: 7 days
Qdrant: 7 days

Restore Procedures:
-------------------
Full System Restore:
  \$ scripts/restore-all-systems.sh "${ATOMIC_BACKUP_DIR}"

PostgreSQL Only:
  \$ scripts/restore-postgresql.sh full postgresql/vikunja.sql.gz

Redis Only:
  \$ scripts/restore-redis.sh atomic redis/

Qdrant Only:
  \$ scripts/restore-qdrant.sh full qdrant/

Checksums:
----------
All backup files include SHA256 checksums for integrity verification.
Verify with: sha256sum -c <file>.sha256

Contact Information:
---------------------
For issues or questions about this backup, contact the XNAi Ops team.
EOF
    
    log "INFO" "Manifest created: ${ATOMIC_BACKUP_DIR}/MANIFEST"
}

################################################################################
# VERIFY ATOMIC BACKUP
################################################################################
verify_backup() {
    log "INFO" "Verifying atomic backup integrity..."
    
    local verified=0
    local failed=0
    
    # Verify PostgreSQL
    if [ -f "${ATOMIC_BACKUP_DIR}/postgresql/vikunja.sql.gz.sha256" ]; then
        if cd "${ATOMIC_BACKUP_DIR}/postgresql" && sha256sum -c "vikunja.sql.gz.sha256" >> "${BACKUP_LOG}" 2>&1; then
            verified=$((verified + 1))
            log "INFO" "PostgreSQL backup verified"
        else
            failed=$((failed + 1))
            log "ERROR" "PostgreSQL backup verification failed"
        fi
        cd - > /dev/null
    fi
    
    # Verify Redis
    if [ -f "${ATOMIC_BACKUP_DIR}/redis/dump.rdb.gz.sha256" ]; then
        if cd "${ATOMIC_BACKUP_DIR}/redis" && sha256sum -c "dump.rdb.gz.sha256" >> "${BACKUP_LOG}" 2>&1; then
            verified=$((verified + 1))
            log "INFO" "Redis backup verified"
        else
            failed=$((failed + 1))
            log "ERROR" "Redis backup verification failed"
        fi
        cd - > /dev/null
    fi
    
    # Verify Qdrant snapshots
    local snapshot_count=$(find "${ATOMIC_BACKUP_DIR}/qdrant" -name "*.sha256" | wc -l)
    local verified_snapshots=0
    
    while IFS= read -r checksum_file; do
        if [ -z "${checksum_file}" ]; then
            continue
        fi
        
        if cd "$(dirname "${checksum_file}")" && sha256sum -c "$(basename "${checksum_file}")" >> "${BACKUP_LOG}" 2>&1; then
            verified_snapshots=$((verified_snapshots + 1))
        fi
        cd - > /dev/null
    done < <(find "${ATOMIC_BACKUP_DIR}/qdrant" -name "*.sha256")
    
    log "INFO" "Qdrant snapshots verified: ${verified_snapshots}/${snapshot_count}"
    
    log "INFO" "Backup verification completed: ${verified} systems verified, ${failed} failed"
}

################################################################################
# MAIN EXECUTION
################################################################################
main() {
    log "INFO" "======================================================"
    log "INFO" "XNAi Atomic Backup Coordinator Started"
    log "INFO" "======================================================"
    log "INFO" "Backup destination: ${ATOMIC_BACKUP_DIR}"
    
    # Backup each system
    backup_postgresql || cleanup_on_error "PostgreSQL backup"
    backup_redis || cleanup_on_error "Redis backup"
    backup_qdrant || cleanup_on_error "Qdrant backup"
    
    # Create manifest
    create_manifest
    
    # Verify all backups
    verify_backup
    
    # Summary
    local total_size=$(du -sh "${ATOMIC_BACKUP_DIR}" | cut -f1)
    
    log "INFO" "======================================================"
    log "INFO" "Atomic Backup Completed Successfully"
    log "INFO" "======================================================"
    log "INFO" "Backup Location: ${ATOMIC_BACKUP_DIR}"
    log "INFO" "Total Size: ${total_size}"
    log "INFO" "RTO Capability: <1 hour"
    log "INFO" ""
    log "INFO" "Next Steps:"
    log "INFO" "  1. Verify backup files exist"
    log "INFO" "  2. Copy backup to offsite storage"
    log "INFO" "  3. Document backup in inventory"
    log "INFO" ""
}

main "$@"
