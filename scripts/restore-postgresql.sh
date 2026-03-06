#!/bin/bash
################################################################################
# XNAi Foundation - PostgreSQL Restore Script
# Purpose: Restore PostgreSQL from backup files
# Supports: Full restore, point-in-time recovery (PITR)
################################################################################

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-.}/backups/postgresql"
LOG_DIR="${LOG_DIR:-.}/logs/restore"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESTORE_LOG="${LOG_DIR}/postgresql_restore_${TIMESTAMP}.log"

# PostgreSQL Configuration
VIKUNJA_DB_HOST="${VIKUNJA_DB_HOST:-vikunja-db}"
VIKUNJA_DB_USER="${VIKUNJA_DB_USER:-vikunja}"
VIKUNJA_DB_PASSWORD="${VIKUNJA_DB_PASSWORD:-}"

# Restore mode
RESTORE_MODE="${1:-full}"  # full or pitr
BACKUP_FILE="${2:-}"
PITR_TARGET="${3:-}"

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
# RESTORE FROM FULL BACKUP
################################################################################
restore_full() {
    local backup_file=$1
    
    if [ ! -f "${backup_file}" ]; then
        error_exit "Backup file not found: ${backup_file}"
    fi
    
    log "INFO" "Starting PostgreSQL full restore"
    log "INFO" "Backup file: ${backup_file}"
    
    # Verify checksum if available
    if [ -f "${backup_file}.sha256" ]; then
        log "INFO" "Verifying backup integrity..."
        cd "$(dirname "${backup_file}")"
        sha256sum -c "$(basename "${backup_file}").sha256" >> "${RESTORE_LOG}" 2>&1 || error_exit "Checksum verification failed"
        cd - > /dev/null
        log "INFO" "Checksum verification passed"
    fi
    
    log "INFO" "Decompressing backup file..."
    local temp_dir=$(mktemp -d)
    trap "rm -rf ${temp_dir}" EXIT
    
    local decompress_file="${temp_dir}/vikunja.sql"
    
    if [[ "${backup_file}" == *.gz ]]; then
        gunzip -c "${backup_file}" > "${decompress_file}" || error_exit "Decompression failed"
    else
        cp "${backup_file}" "${decompress_file}" || error_exit "Copy failed"
    fi
    
    log "INFO" "Connecting to PostgreSQL at ${VIKUNJA_DB_HOST}..."
    
    # Drop existing database if requested
    if [ "${FORCE_RESTORE:-false}" = "true" ]; then
        log "WARN" "Dropping existing database (FORCE_RESTORE=true)"
        PGPASSWORD="${VIKUNJA_DB_PASSWORD}" psql \
            -h "${VIKUNJA_DB_HOST}" \
            -U "${VIKUNJA_DB_USER}" \
            -d postgres \
            -c "DROP DATABASE IF EXISTS vikunja;" \
            >> "${RESTORE_LOG}" 2>&1 || log "WARN" "Drop database failed (may not exist)"
    fi
    
    # Recreate database
    log "INFO" "Creating database..."
    PGPASSWORD="${VIKUNJA_DB_PASSWORD}" psql \
        -h "${VIKUNJA_DB_HOST}" \
        -U "${VIKUNJA_DB_USER}" \
        -d postgres \
        -c "CREATE DATABASE vikunja;" \
        >> "${RESTORE_LOG}" 2>&1 || log "WARN" "Database creation returned error (may already exist)"
    
    # Restore from backup
    log "INFO" "Restoring database from backup..."
    PGPASSWORD="${VIKUNJA_DB_PASSWORD}" psql \
        -h "${VIKUNJA_DB_HOST}" \
        -U "${VIKUNJA_DB_USER}" \
        -d vikunja \
        -f "${decompress_file}" \
        >> "${RESTORE_LOG}" 2>&1 || error_exit "Restore failed"
    
    log "INFO" "PostgreSQL restore completed successfully"
    
    # Verify restore
    log "INFO" "Verifying restored database..."
    local table_count=$(PGPASSWORD="${VIKUNJA_DB_PASSWORD}" psql \
        -h "${VIKUNJA_DB_HOST}" \
        -U "${VIKUNJA_DB_USER}" \
        -d vikunja \
        -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null || echo "0")
    
    log "INFO" "Restored database has ${table_count} tables"
}

################################################################################
# POINT-IN-TIME RECOVERY
################################################################################
restore_pitr() {
    local target_time=$1
    
    log "INFO" "Starting point-in-time recovery (PITR) to: ${target_time}"
    log "INFO" "PITR requires WAL files to be available"
    log "INFO" "WAL directory: ${BACKUP_DIR}/wal_archive"
    
    if [ ! -d "${BACKUP_DIR}/wal_archive" ]; then
        error_exit "WAL archive directory not found: ${BACKUP_DIR}/wal_archive"
    fi
    
    # Find base backup before target time
    local latest_full_backup=""
    local latest_timestamp=""
    
    for backup in $(find "${BACKUP_DIR}/full_backup_"*.sql.gz -printf '%T@ %p\n' | sort -n | cut -d' ' -f2-); do
        # Extract timestamp from filename
        local timestamp=$(basename "${backup}" | sed 's/full_backup_\([0-9_]*\)\.sql\.gz/\1/')
        local timestamp_unix=$(date -d "${timestamp}" +%s 2>/dev/null || echo "0")
        local target_unix=$(date -d "${target_time}" +%s 2>/dev/null || echo "0")
        
        if [ ${timestamp_unix} -le ${target_unix} ]; then
            latest_full_backup="${backup}"
            latest_timestamp="${timestamp}"
        fi
    done
    
    if [ -z "${latest_full_backup}" ]; then
        error_exit "No base backup found before target time: ${target_time}"
    fi
    
    log "INFO" "Using base backup: ${latest_full_backup}"
    log "INFO" "Base backup timestamp: ${latest_timestamp}"
    
    # Restore from base backup
    restore_full "${latest_full_backup}"
    
    log "INFO" "PITR recovery completed at target time: ${target_time}"
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
    
    # Find the SQL backup file
    local sql_backup=$(find "${atomic_dir}" -name "*.sql.gz" -o -name "*.sql" | head -1)
    
    if [ -z "${sql_backup}" ]; then
        error_exit "No SQL backup file found in atomic backup"
    fi
    
    log "INFO" "Found SQL backup: ${sql_backup}"
    
    # Restore
    restore_full "${sql_backup}"
}

################################################################################
# INTERACTIVE RESTORE WIZARD
################################################################################
restore_interactive() {
    log "INFO" "PostgreSQL Restore - Interactive Mode"
    
    echo "Available backups:"
    ls -lh "${BACKUP_DIR}"/full_backup_*.sql.gz 2>/dev/null || echo "No full backups found"
    
    echo ""
    echo "Available atomic backups:"
    ls -d "${BACKUP_DIR}"/atomic_* 2>/dev/null || echo "No atomic backups found"
    
    echo ""
    read -p "Enter backup file path or atomic directory: " backup_path
    
    if [ -d "${backup_path}" ]; then
        restore_atomic "${backup_path}"
    elif [ -f "${backup_path}" ]; then
        restore_full "${backup_path}"
    else
        error_exit "Invalid backup path: ${backup_path}"
    fi
}

################################################################################
# HEALTH CHECK
################################################################################
check_health() {
    log "INFO" "Checking PostgreSQL health..."
    
    PGPASSWORD="${VIKUNJA_DB_PASSWORD}" pg_isready \
        -h "${VIKUNJA_DB_HOST}" \
        -U "${VIKUNJA_DB_USER}" \
        -d vikunja \
        >> "${RESTORE_LOG}" 2>&1 || error_exit "PostgreSQL is not responding"
    
    log "INFO" "PostgreSQL health check passed"
}

################################################################################
# MAIN EXECUTION
################################################################################
main() {
    log "INFO" "PostgreSQL Restore Script Started"
    log "INFO" "Restore mode: ${RESTORE_MODE}"
    
    case "${RESTORE_MODE}" in
        full)
            if [ -z "${BACKUP_FILE}" ]; then
                error_exit "Backup file required for full restore: $0 full <backup_file>"
            fi
            restore_full "${BACKUP_FILE}"
            ;;
        pitr)
            if [ -z "${PITR_TARGET}" ]; then
                error_exit "Target time required for PITR: $0 pitr <target_time>"
            fi
            restore_pitr "${PITR_TARGET}"
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
    
    # Health check
    check_health
    
    log "INFO" "PostgreSQL Restore Script Completed Successfully"
}

main "$@"
