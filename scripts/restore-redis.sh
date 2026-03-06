#!/bin/bash
################################################################################
# XNAi Foundation - Redis Restore Script
# Purpose: Restore Redis from RDB snapshots and AOF files
################################################################################

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-.}/backups/redis"
LOG_DIR="${LOG_DIR:-.}/logs/restore"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESTORE_LOG="${LOG_DIR}/redis_restore_${TIMESTAMP}.log"

# Redis Configuration
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_PASSWORD="${REDIS_PASSWORD:-}"
REDIS_DATA_DIR="${REDIS_DATA_DIR:-./data/redis}"

# Restore mode
RESTORE_MODE="${1:-rdb}"  # rdb, aof, or atomic
BACKUP_FILE="${2:-}"

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
# REDIS HEALTH CHECK
################################################################################
check_redis_health() {
    log "INFO" "Checking Redis connectivity..."
    
    local redis_cli_cmd="redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT}"
    
    if [ -n "${REDIS_PASSWORD}" ]; then
        redis_cli_cmd="${redis_cli_cmd} -a ${REDIS_PASSWORD}"
    fi
    
    ${redis_cli_cmd} PING >> "${RESTORE_LOG}" 2>&1 || error_exit "Redis is not responding"
    
    log "INFO" "Redis health check passed"
}

################################################################################
# RESTORE FROM RDB SNAPSHOT
################################################################################
restore_rdb() {
    local backup_file=$1
    
    if [ ! -f "${backup_file}" ]; then
        error_exit "Backup file not found: ${backup_file}"
    fi
    
    log "INFO" "Starting Redis RDB restore"
    log "INFO" "Backup file: ${backup_file}"
    
    # Verify checksum if available
    if [ -f "${backup_file}.sha256" ]; then
        log "INFO" "Verifying backup integrity..."
        cd "$(dirname "${backup_file}")"
        sha256sum -c "$(basename "${backup_file}").sha256" >> "${RESTORE_LOG}" 2>&1 || error_exit "Checksum verification failed"
        cd - > /dev/null
        log "INFO" "Checksum verification passed"
    fi
    
    # Create temporary directory for decompression
    local temp_dir=$(mktemp -d)
    trap "rm -rf ${temp_dir}" EXIT
    
    local decompress_file="${temp_dir}/dump.rdb"
    
    # Decompress if needed
    if [[ "${backup_file}" == *.gz ]]; then
        log "INFO" "Decompressing backup file..."
        gunzip -c "${backup_file}" > "${decompress_file}" || error_exit "Decompression failed"
    else
        cp "${backup_file}" "${decompress_file}" || error_exit "Copy failed"
    fi
    
    # Stop Redis to avoid conflicts
    log "WARN" "Stopping Redis server for restore..."
    local redis_cli_cmd="redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT}"
    if [ -n "${REDIS_PASSWORD}" ]; then
        redis_cli_cmd="${redis_cli_cmd} -a ${REDIS_PASSWORD}"
    fi
    
    ${redis_cli_cmd} SHUTDOWN NOSAVE >> "${RESTORE_LOG}" 2>&1 || log "WARN" "Redis shutdown may have failed"
    
    # Wait for Redis to stop
    sleep 2
    
    # Backup existing dump.rdb
    if [ -f "${REDIS_DATA_DIR}/dump.rdb" ]; then
        log "INFO" "Backing up existing dump.rdb to dump.rdb.bak"
        cp "${REDIS_DATA_DIR}/dump.rdb" "${REDIS_DATA_DIR}/dump.rdb.bak"
    fi
    
    # Replace with restore file
    log "INFO" "Restoring RDB file to ${REDIS_DATA_DIR}/dump.rdb"
    cp "${decompress_file}" "${REDIS_DATA_DIR}/dump.rdb" || error_exit "Failed to copy RDB file"
    
    # Fix permissions
    chmod 644 "${REDIS_DATA_DIR}/dump.rdb"
    
    log "INFO" "RDB restore file staged. Redis server needs to be started."
    log "INFO" "Command: docker-compose restart redis"
}

################################################################################
# RESTORE FROM AOF
################################################################################
restore_aof() {
    local backup_file=$1
    
    if [ ! -f "${backup_file}" ]; then
        error_exit "Backup file not found: ${backup_file}"
    fi
    
    log "INFO" "Starting Redis AOF restore"
    log "INFO" "Backup file: ${backup_file}"
    
    # Create temporary directory
    local temp_dir=$(mktemp -d)
    trap "rm -rf ${temp_dir}" EXIT
    
    local decompress_file="${temp_dir}/appendonly.aof"
    
    # Decompress if needed
    if [[ "${backup_file}" == *.gz ]]; then
        log "INFO" "Decompressing backup file..."
        gunzip -c "${backup_file}" > "${decompress_file}" || error_exit "Decompression failed"
    else
        cp "${backup_file}" "${decompress_file}" || error_exit "Copy failed"
    fi
    
    # Backup existing AOF
    if [ -f "${REDIS_DATA_DIR}/appendonly.aof" ]; then
        log "INFO" "Backing up existing appendonly.aof"
        cp "${REDIS_DATA_DIR}/appendonly.aof" "${REDIS_DATA_DIR}/appendonly.aof.bak"
    fi
    
    # Copy restored AOF
    log "INFO" "Restoring AOF file"
    cp "${decompress_file}" "${REDIS_DATA_DIR}/appendonly.aof" || error_exit "Failed to copy AOF"
    
    # Fix permissions
    chmod 644 "${REDIS_DATA_DIR}/appendonly.aof"
    
    log "INFO" "AOF restore file staged"
    log "INFO" "Note: AOF restore requires Redis restart and may take time to load"
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
    
    # Priority: RDB first, then AOF
    local rdb_file=$(find "${atomic_dir}" -name "dump.rdb.gz" -o -name "dump.rdb" | head -1)
    local aof_file=$(find "${atomic_dir}" -name "appendonly.aof.gz" -o -name "appendonly.aof" | head -1)
    
    if [ -n "${rdb_file}" ]; then
        log "INFO" "Found RDB file in atomic backup"
        restore_rdb "${rdb_file}"
    fi
    
    if [ -n "${aof_file}" ]; then
        log "WARN" "AOF file found but RDB takes precedence for restore"
        log "WARN" "To restore from AOF instead, use: $0 aof ${aof_file}"
    fi
    
    if [ -z "${rdb_file}" ] && [ -z "${aof_file}" ]; then
        error_exit "No RDB or AOF files found in atomic backup"
    fi
}

################################################################################
# INTERACTIVE RESTORE WIZARD
################################################################################
restore_interactive() {
    log "INFO" "Redis Restore - Interactive Mode"
    
    echo "Available RDB backups:"
    ls -lh "${BACKUP_DIR}"/rdb_snapshot_*.rdb.gz 2>/dev/null || echo "No RDB backups found"
    
    echo ""
    echo "Available AOF backups:"
    ls -lh "${BACKUP_DIR}"/aof_backup_*.aof.gz 2>/dev/null || echo "No AOF backups found"
    
    echo ""
    echo "Available atomic backups:"
    ls -d "${BACKUP_DIR}"/atomic_* 2>/dev/null || echo "No atomic backups found"
    
    echo ""
    read -p "Enter backup file path or atomic directory: " backup_path
    
    if [ -d "${backup_path}" ]; then
        restore_atomic "${backup_path}"
    elif [[ "${backup_path}" == *"rdb"* ]]; then
        restore_rdb "${backup_path}"
    elif [[ "${backup_path}" == *"aof"* ]]; then
        restore_aof "${backup_path}"
    else
        error_exit "Could not determine restore type from path: ${backup_path}"
    fi
}

################################################################################
# VERIFY RESTORE
################################################################################
verify_restore() {
    log "INFO" "Verifying Redis restore..."
    
    # Wait for Redis to be available
    local retry_count=0
    local max_retries=30
    
    while [ $retry_count -lt $max_retries ]; do
        if check_redis_health 2>/dev/null; then
            break
        fi
        sleep 1
        retry_count=$((retry_count + 1))
    done
    
    if [ $retry_count -ge $max_retries ]; then
        error_exit "Redis did not become available after restore"
    fi
    
    # Check data
    local redis_cli_cmd="redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT}"
    if [ -n "${REDIS_PASSWORD}" ]; then
        redis_cli_cmd="${redis_cli_cmd} -a ${REDIS_PASSWORD}"
    fi
    
    log "INFO" "Redis restore verification:"
    ${redis_cli_cmd} INFO stats >> "${RESTORE_LOG}" 2>&1
}

################################################################################
# MAIN EXECUTION
################################################################################
main() {
    log "INFO" "Redis Restore Script Started"
    log "INFO" "Restore mode: ${RESTORE_MODE}"
    
    case "${RESTORE_MODE}" in
        rdb)
            if [ -z "${BACKUP_FILE}" ]; then
                error_exit "Backup file required for RDB restore: $0 rdb <backup_file>"
            fi
            restore_rdb "${BACKUP_FILE}"
            ;;
        aof)
            if [ -z "${BACKUP_FILE}" ]; then
                error_exit "Backup file required for AOF restore: $0 aof <backup_file>"
            fi
            restore_aof "${BACKUP_FILE}"
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
    
    log "INFO" "Redis Restore Script Completed Successfully"
    log "INFO" "To start Redis: docker-compose restart redis"
}

main "$@"
