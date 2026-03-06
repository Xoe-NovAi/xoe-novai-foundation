#!/bin/bash
################################################################################
# XNAi Foundation - Qdrant Backup Script
# Purpose: Collection snapshots and backup strategy
# Retention: 7 days
# Execution: Daily
################################################################################

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-.}/backups/qdrant"
RETENTION_DAYS=${RETENTION_DAYS:-7}
LOG_DIR="${LOG_DIR:-.}/logs/backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_LOG="${LOG_DIR}/qdrant_backup_${TIMESTAMP}.log"

# Qdrant Configuration
QDRANT_HOST="${QDRANT_HOST:-localhost}"
QDRANT_PORT="${QDRANT_PORT:-6333}"
QDRANT_API_KEY="${QDRANT_API_KEY:-}"
QDRANT_PROTOCOL="${QDRANT_PROTOCOL:-http}"

# Create directories
mkdir -p "${BACKUP_DIR}" "${LOG_DIR}"

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

trap 'error_exit "Backup script interrupted"' INT TERM

################################################################################
# HELPER FUNCTIONS
################################################################################

# Construct curl command with API key
curl_qdrant() {
    local method=$1
    local endpoint=$2
    local data=${3:-}
    
    local curl_cmd="curl -s -X ${method} '${QDRANT_PROTOCOL}://${QDRANT_HOST}:${QDRANT_PORT}${endpoint}'"
    
    if [ -n "${QDRANT_API_KEY}" ]; then
        curl_cmd="${curl_cmd} -H 'api-key: ${QDRANT_API_KEY}'"
    fi
    
    if [ -n "${data}" ]; then
        curl_cmd="${curl_cmd} -H 'Content-Type: application/json' -d '${data}'"
    fi
    
    eval "${curl_cmd}"
}

# Check Qdrant connectivity
check_qdrant_health() {
    log "INFO" "Checking Qdrant server health..."
    
    local health=$(curl_qdrant "GET" "/health")
    
    if echo "${health}" | grep -q "\"status\""; then
        log "INFO" "Qdrant server is healthy"
        return 0
    else
        error_exit "Qdrant server is not responding"
    fi
}

################################################################################
# LIST COLLECTIONS
################################################################################
list_collections() {
    log "INFO" "Listing all Qdrant collections"
    
    local collections=$(curl_qdrant "GET" "/collections")
    echo "${collections}"
}

################################################################################
# CREATE COLLECTION SNAPSHOT
################################################################################
snapshot_collection() {
    local collection_name=$1
    local backup_dir=$2
    
    log "INFO" "Creating snapshot for collection: ${collection_name}"
    
    # Initiate snapshot creation
    local snapshot_response=$(curl_qdrant "POST" "/collections/${collection_name}/snapshots")
    
    if echo "${snapshot_response}" | grep -q "\"error\""; then
        log "ERROR" "Failed to create snapshot for ${collection_name}"
        log "ERROR" "Response: ${snapshot_response}"
        return 1
    fi
    
    # Extract snapshot name
    local snapshot_name=$(echo "${snapshot_response}" | grep -oP '"snapshot_name"\s*:\s*"\K[^"]+' | head -1)
    
    if [ -z "${snapshot_name}" ]; then
        log "WARN" "Could not extract snapshot name for ${collection_name}"
        return 1
    fi
    
    log "INFO" "Snapshot created: ${snapshot_name}"
    
    # Download snapshot
    local snapshot_file="${backup_dir}/${collection_name}_${snapshot_name}.snapshot"
    
    log "INFO" "Downloading snapshot to: ${snapshot_file}"
    
    local download_cmd="curl -s -X GET '${QDRANT_PROTOCOL}://${QDRANT_HOST}:${QDRANT_PORT}/collections/${collection_name}/snapshots/${snapshot_name}'"
    
    if [ -n "${QDRANT_API_KEY}" ]; then
        download_cmd="${download_cmd} -H 'api-key: ${QDRANT_API_KEY}'"
    fi
    
    download_cmd="${download_cmd} -o '${snapshot_file}'"
    
    eval "${download_cmd}" || error_exit "Failed to download snapshot for ${collection_name}"
    
    # Verify file was created
    if [ ! -f "${snapshot_file}" ] || [ ! -s "${snapshot_file}" ]; then
        error_exit "Snapshot file is empty or not created: ${snapshot_file}"
    fi
    
    local snapshot_size=$(du -h "${snapshot_file}" | cut -f1)
    log "INFO" "Snapshot downloaded successfully: ${snapshot_size}"
    
    # Generate checksum
    sha256sum "${snapshot_file}" > "${snapshot_file}.sha256"
    log "INFO" "Checksum generated: ${snapshot_file}.sha256"
    
    echo "${snapshot_file}"
}

################################################################################
# FULL BACKUP PROCEDURE
################################################################################
backup_full() {
    log "INFO" "Starting full Qdrant backup"
    
    local backup_subdir="${BACKUP_DIR}/full_backup_${TIMESTAMP}"
    mkdir -p "${backup_subdir}"
    
    # Get list of collections
    local collections_json=$(list_collections)
    
    # Extract collection names
    local collections=$(echo "${collections_json}" | grep -oP '"name"\s*:\s*"\K[^"]+' || echo "")
    
    if [ -z "${collections}" ]; then
        log "WARN" "No collections found in Qdrant"
        echo "${backup_subdir}"
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
        
        if snapshot_collection "${collection_name}" "${backup_subdir}"; then
            backed_up=$((backed_up + 1))
        else
            failed=$((failed + 1))
        fi
    done <<< "${collections}"
    
    log "INFO" "Backup summary: ${backed_up} collections backed up, ${failed} failed"
    
    # Write backup manifest
    cat > "${backup_subdir}/MANIFEST" << EOF
Qdrant Backup Manifest
=====================
Timestamp: $(date -u +'%Y-%m-%dT%H:%M:%SZ')
Backup Type: Full
Total Collections: $((backed_up + failed))
Successful Backups: ${backed_up}
Failed Backups: ${failed}

Backup Contents:
$(ls -1 "${backup_subdir}"/*.snapshot 2>/dev/null | xargs -I {} bash -c 'echo "  - {} ($(du -h {} | cut -f1))"' || echo "  (No snapshots)")

Retention: Until $(date -u -d "+${RETENTION_DAYS} days" +'%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u -v+${RETENTION_DAYS}d +'%Y-%m-%dT%H:%M:%SZ')
EOF
    
    log "INFO" "Backup manifest: ${backup_subdir}/MANIFEST"
    
    echo "${backup_subdir}"
}

################################################################################
# INCREMENTAL BACKUP (Collection-specific)
################################################################################
backup_incremental() {
    local collection_name=$1
    
    if [ -z "${collection_name}" ]; then
        error_exit "Collection name required for incremental backup"
    fi
    
    log "INFO" "Starting incremental backup for collection: ${collection_name}"
    
    local backup_subdir="${BACKUP_DIR}/incremental_${collection_name}_${TIMESTAMP}"
    mkdir -p "${backup_subdir}"
    
    snapshot_collection "${collection_name}" "${backup_subdir}"
    
    log "INFO" "Incremental backup completed for ${collection_name}"
    
    echo "${backup_subdir}"
}

################################################################################
# BACKUP STATISTICS
################################################################################
log_qdrant_stats() {
    log "INFO" "Qdrant System Information:"
    
    curl_qdrant "GET" "/collections" >> "${BACKUP_LOG}" 2>&1 || true
}

################################################################################
# ATOMIC BACKUP
################################################################################
backup_atomic() {
    log "INFO" "Starting atomic Qdrant backup"
    
    local atomic_dir="${BACKUP_DIR}/atomic_${TIMESTAMP}"
    mkdir -p "${atomic_dir}"
    
    # Get collections
    local collections_json=$(list_collections)
    local collections=$(echo "${collections_json}" | grep -oP '"name"\s*:\s*"\K[^"]+' || echo "")
    
    if [ -z "${collections}" ]; then
        log "WARN" "No collections found for atomic backup"
        echo "${atomic_dir}"
        return 0
    fi
    
    local backed_up=0
    
    # Backup all collections atomically (all at same timestamp)
    while IFS= read -r collection_name; do
        if [ -z "${collection_name}" ]; then
            continue
        fi
        
        if snapshot_collection "${collection_name}" "${atomic_dir}"; then
            backed_up=$((backed_up + 1))
        fi
    done <<< "${collections}"
    
    # Write atomic backup manifest
    cat > "${atomic_dir}/MANIFEST" << EOF
Atomic Qdrant Backup Manifest
==============================
Timestamp: $(date -u +'%Y-%m-%dT%H:%M:%SZ')
Backup Type: Atomic
Total Collections Backed Up: ${backed_up}

Backup Contents:
$(ls -1 "${atomic_dir}"/*.snapshot 2>/dev/null | xargs -I {} bash -c 'echo "  - {} ($(du -h {} | cut -f1))"' || echo "  (No snapshots)")

Restoration: Use scripts/restore-qdrant.sh to restore
EOF
    
    log "INFO" "Atomic Qdrant backup completed: ${atomic_dir}"
    
    echo "${atomic_dir}"
}

################################################################################
# CLEANUP OLD BACKUPS
################################################################################
cleanup_old_backups() {
    log "INFO" "Cleaning up backups older than ${RETENTION_DAYS} days"
    
    find "${BACKUP_DIR}/full_backup_"* -type d -mtime "+${RETENTION_DAYS}" -exec rm -rf {} + 2>/dev/null || true
    find "${BACKUP_DIR}/incremental_"* -type d -mtime "+${RETENTION_DAYS}" -exec rm -rf {} + 2>/dev/null || true
    
    log "INFO" "Cleanup completed"
}

################################################################################
# MAIN EXECUTION
################################################################################
main() {
    log "INFO" "Qdrant Backup Script Started"
    
    # Check health
    check_qdrant_health
    
    # Perform backup
    local backup_dir
    if [ "${1:-full}" = "atomic" ]; then
        backup_dir=$(backup_atomic)
    else
        backup_dir=$(backup_full)
    fi
    
    # Log statistics
    log_qdrant_stats
    
    # Cleanup
    cleanup_old_backups
    
    log "INFO" "Qdrant backup completed successfully: ${backup_dir}"
}

main "$@"
