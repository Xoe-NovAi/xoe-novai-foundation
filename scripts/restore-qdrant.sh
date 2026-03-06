#!/bin/bash
################################################################################
# XNAi Foundation - Qdrant Restore Script
# Purpose: Restore Qdrant from collection snapshots
################################################################################

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-.}/backups/qdrant"
LOG_DIR="${LOG_DIR:-.}/logs/restore"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESTORE_LOG="${LOG_DIR}/qdrant_restore_${TIMESTAMP}.log"

# Qdrant Configuration
QDRANT_HOST="${QDRANT_HOST:-localhost}"
QDRANT_PORT="${QDRANT_PORT:-6333}"
QDRANT_API_KEY="${QDRANT_API_KEY:-}"
QDRANT_PROTOCOL="${QDRANT_PROTOCOL:-http}"

# Restore mode
RESTORE_MODE="${1:-full}"  # full, collection, or atomic
BACKUP_FILE="${2:-}"
COLLECTION_NAME="${3:-}"

# Create log directory
mkdir -p "${LOG_DIR}"

# Logging function
log() {
    local level=$1
    shift
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [${level}] $*" | tee -a "${RESTORE_LOG}"
}

# Error handling
error_exit() {
    log "ERROR" "$1"
    exit 1
}

trap 'error_exit "Restore script interrupted"' INT TERM

################################################################################
# QDRANT HEALTH CHECK
################################################################################
check_qdrant_health() {
    log "INFO" "Checking Qdrant connectivity..."
    
    local health_cmd="curl -s -X GET '${QDRANT_PROTOCOL}://${QDRANT_HOST}:${QDRANT_PORT}/health'"
    
    if [ -n "${QDRANT_API_KEY}" ]; then
        health_cmd="${health_cmd} -H 'api-key: ${QDRANT_API_KEY}'"
    fi
    
    local response=$(eval "${health_cmd}")
    
    if echo "${response}" | grep -q "\"status\""; then
        log "INFO" "Qdrant health check passed"
        return 0
    else
        error_exit "Qdrant is not responding"
    fi
}

################################################################################
# LIST EXISTING COLLECTIONS
################################################################################
list_collections() {
    local curl_cmd="curl -s -X GET '${QDRANT_PROTOCOL}://${QDRANT_HOST}:${QDRANT_PORT}/collections'"
    
    if [ -n "${QDRANT_API_KEY}" ]; then
        curl_cmd="${curl_cmd} -H 'api-key: ${QDRANT_API_KEY}'"
    fi
    
    eval "${curl_cmd}"
}

################################################################################
# RESTORE COLLECTION FROM SNAPSHOT
################################################################################
restore_collection_snapshot() {
    local snapshot_file=$1
    local collection_name=$2
    
    if [ ! -f "${snapshot_file}" ]; then
        error_exit "Snapshot file not found: ${snapshot_file}"
    fi
    
    log "INFO" "Restoring collection: ${collection_name}"
    log "INFO" "Snapshot file: ${snapshot_file}"
    
    # Verify checksum if available
    if [ -f "${snapshot_file}.sha256" ]; then
        log "INFO" "Verifying snapshot integrity..."
        cd "$(dirname "${snapshot_file}")"
        sha256sum -c "$(basename "${snapshot_file}").sha256" >> "${RESTORE_LOG}" 2>&1 || error_exit "Checksum verification failed"
        cd - > /dev/null
        log "INFO" "Checksum verification passed"
    fi
    
    # Upload snapshot to Qdrant
    log "INFO" "Uploading snapshot to Qdrant..."
    
    local upload_cmd="curl -s -X POST '${QDRANT_PROTOCOL}://${QDRANT_HOST}:${QDRANT_PORT}/collections/${collection_name}/snapshots/upload'"
    
    if [ -n "${QDRANT_API_KEY}" ]; then
        upload_cmd="${upload_cmd} -H 'api-key: ${QDRANT_API_KEY}'"
    fi
    
    upload_cmd="${upload_cmd} -F 'snapshot=@${snapshot_file}'"
    
    local response=$(eval "${upload_cmd}")
    
    if echo "${response}" | grep -q "\"error\""; then
        log "ERROR" "Failed to restore collection: ${collection_name}"
        log "ERROR" "Response: ${response}"
        return 1
    fi
    
    log "INFO" "Collection restored successfully: ${collection_name}"
    return 0
}

################################################################################
# RESTORE FROM FULL BACKUP
################################################################################
restore_full() {
    local backup_dir=$1
    
    if [ ! -d "${backup_dir}" ]; then
        error_exit "Backup directory not found: ${backup_dir}"
    fi
    
    log "INFO" "Starting full Qdrant restore"
    log "INFO" "Backup directory: ${backup_dir}"
    
    # Check health
    check_qdrant_health
    
    # Find all snapshot files
    local snapshots=$(find "${backup_dir}" -name "*.snapshot" -type f | sort)
    
    if [ -z "${snapshots}" ]; then
        error_exit "No snapshot files found in backup directory"
    fi
    
    local restored=0
    local failed=0
    
    # Restore each collection
    while IFS= read -r snapshot_file; do
        # Extract collection name from filename
        # Format: collection_name_snapshot_name.snapshot
        local basename=$(basename "${snapshot_file}")
        local collection_name=$(echo "${basename}" | sed 's/_[^_]*\.snapshot$//')
        
        log "INFO" "Processing: ${basename} -> ${collection_name}"
        
        if restore_collection_snapshot "${snapshot_file}" "${collection_name}"; then
            restored=$((restored + 1))
        else
            failed=$((failed + 1))
        fi
    done <<< "${snapshots}"
    
    log "INFO" "Restore summary: ${restored} collections restored, ${failed} failed"
    
    if [ $failed -gt 0 ]; then
        error_exit "Some collections failed to restore"
    fi
}

################################################################################
# RESTORE SINGLE COLLECTION
################################################################################
restore_collection() {
    local snapshot_file=$1
    local collection_name=$2
    
    if [ -z "${collection_name}" ]; then
        error_exit "Collection name is required"
    fi
    
    if [ ! -f "${snapshot_file}" ]; then
        error_exit "Snapshot file not found: ${snapshot_file}"
    fi
    
    log "INFO" "Restoring single collection: ${collection_name}"
    
    # Check health
    check_qdrant_health
    
    # Restore
    restore_collection_snapshot "${snapshot_file}" "${collection_name}"
    
    log "INFO" "Collection restore completed"
}

################################################################################
# RESTORE FROM ATOMIC BACKUP
################################################################################
restore_atomic() {
    local atomic_dir=$1
    
    if [ ! -d "${atomic_dir}" ]; then
        error_exit "Atomic backup directory not found: ${atomic_dir}"
    fi
    
    log "INFO" "Restoring from atomic backup: ${atomic_dir}"
    
    # Check health
    check_qdrant_health
    
    # Full restore from atomic directory
    restore_full "${atomic_dir}"
}

################################################################################
# INTERACTIVE RESTORE WIZARD
################################################################################
restore_interactive() {
    log "INFO" "Qdrant Restore - Interactive Mode"
    
    echo "Available full backups:"
    ls -d "${BACKUP_DIR}"/full_backup_* 2>/dev/null || echo "No full backups found"
    
    echo ""
    echo "Available atomic backups:"
    ls -d "${BACKUP_DIR}"/atomic_* 2>/dev/null || echo "No atomic backups found"
    
    echo ""
    echo "Available snapshots in current directory:"
    ls -lh *.snapshot 2>/dev/null | head -10 || echo "No snapshots found"
    
    echo ""
    read -p "Enter backup directory or snapshot file: " backup_path
    
    if [ -d "${backup_path}" ]; then
        if grep -q "atomic" <<< "${backup_path}"; then
            restore_atomic "${backup_path}"
        else
            restore_full "${backup_path}"
        fi
    elif [ -f "${backup_path}" ] && [[ "${backup_path}" == *.snapshot ]]; then
        read -p "Enter collection name: " collection_name
        restore_collection "${backup_path}" "${collection_name}"
    else
        error_exit "Invalid backup path: ${backup_path}"
    fi
}

################################################################################
# VERIFY RESTORE
################################################################################
verify_restore() {
    log "INFO" "Verifying Qdrant restore..."
    
    local collections=$(list_collections)
    local collection_count=$(echo "${collections}" | grep -oP '"name"\s*:\s*"\K[^"]+' | wc -l)
    
    log "INFO" "Restored collections count: ${collection_count}"
    log "INFO" "Collection details:"
    echo "${collections}" >> "${RESTORE_LOG}"
}

################################################################################
# MAIN EXECUTION
################################################################################
main() {
    log "INFO" "Qdrant Restore Script Started"
    log "INFO" "Restore mode: ${RESTORE_MODE}"
    
    case "${RESTORE_MODE}" in
        full)
            if [ -z "${BACKUP_FILE}" ]; then
                error_exit "Backup directory required for full restore: $0 full <backup_dir>"
            fi
            restore_full "${BACKUP_FILE}"
            ;;
        collection)
            if [ -z "${BACKUP_FILE}" ] || [ -z "${COLLECTION_NAME}" ]; then
                error_exit "Snapshot file and collection name required: $0 collection <snapshot_file> <collection_name>"
            fi
            restore_collection "${BACKUP_FILE}" "${COLLECTION_NAME}"
            ;;
        atomic)
            if [ -z "${BACKUP_FILE}" ]; then
                error_exit "Atomic backup directory required: $0 atomic <atomic_dir>"
            fi
            restore_atomic "${BACKUP_FILE}"
            ;;
        interactive)
            restore_interactive
            ;;
        *)
            error_exit "Unknown restore mode: ${RESTORE_MODE}"
            ;;
    esac
    
    # Verify restore
    verify_restore
    
    log "INFO" "Qdrant Restore Script Completed Successfully"
}

main "$@"
