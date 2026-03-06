#!/bin/bash
################################################################################
# XNAi Foundation - PostgreSQL Backup Script
# Purpose: Full and incremental backup strategy for PostgreSQL
# Retention: 30 days
# Execution: Daily at 2 AM UTC (full), Hourly (WAL archival)
################################################################################

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-.}/backups/postgresql"
RETENTION_DAYS=${RETENTION_DAYS:-30}
LOG_DIR="${LOG_DIR:-.}/logs/backup"
BACKUP_TYPE="${1:-full}"  # full or wal
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_LOG="${LOG_DIR}/postgresql_backup_${TIMESTAMP}.log"

# PostgreSQL Configuration
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${POSTGRES_USER:-postgres}"
DB_PASSWORD="${POSTGRES_PASSWORD:-}"
VIKUNJA_DB_HOST="${VIKUNJA_DB_HOST:-vikunja-db}"
VIKUNJA_DB_USER="${VIKUNJA_DB_USER:-vikunja}"
VIKUNJA_DB_PASSWORD="${VIKUNJA_DB_PASSWORD:-}"

# Create backup directory
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
# FULL BACKUP PROCEDURE
################################################################################
backup_full() {
    log "INFO" "Starting full PostgreSQL backup (Vikunja DB)"
    
    local backup_file="${BACKUP_DIR}/full_backup_${TIMESTAMP}.sql.gz"
    
    # Backup Vikunja database with all objects
    PGPASSWORD="${VIKUNJA_DB_PASSWORD}" pg_dump \
        -h "${VIKUNJA_DB_HOST}" \
        -U "${VIKUNJA_DB_USER}" \
        -d vikunja \
        --verbose \
        --format=plain \
        --compress=9 \
        --file="${backup_file}" \
        2>> "${BACKUP_LOG}" || error_exit "pg_dump failed"
    
    local backup_size=$(du -h "${backup_file}" | cut -f1)
    log "INFO" "Full backup completed: ${backup_file} (${backup_size})"
    
    # Generate checksum for integrity verification
    sha256sum "${backup_file}" > "${backup_file}.sha256"
    log "INFO" "Checksum generated: ${backup_file}.sha256"
    
    # Cleanup old backups (beyond 30 days)
    log "INFO" "Cleaning up backups older than ${RETENTION_DAYS} days"
    find "${BACKUP_DIR}/full_backup_"*.sql.gz -mtime "+${RETENTION_DAYS}" -delete 2>/dev/null || true
    find "${BACKUP_DIR}/full_backup_"*.sha256 -mtime "+${RETENTION_DAYS}" -delete 2>/dev/null || true
    
    echo "${backup_file}"
}

################################################################################
# WAL ARCHIVAL PROCEDURE
################################################################################
backup_wal() {
    log "INFO" "WAL archival is managed by PostgreSQL server configuration"
    log "INFO" "Ensure postgresql.conf has: archive_mode = on"
    log "INFO" "And: archive_command = 'test ! -f ${BACKUP_DIR}/wal_archive/%f && cp %p ${BACKUP_DIR}/wal_archive/%f'"
    
    # Create WAL archive directory if it doesn't exist
    mkdir -p "${BACKUP_DIR}/wal_archive"
    
    log "INFO" "WAL archive directory: ${BACKUP_DIR}/wal_archive"
    
    # Cleanup old WAL files (beyond 7 days for archives)
    find "${BACKUP_DIR}/wal_archive" -type f -mtime +7 -delete 2>/dev/null || true
    log "INFO" "Old WAL files cleaned up (older than 7 days)"
}

################################################################################
# BACKUP METADATA
################################################################################
write_backup_metadata() {
    local backup_file=$1
    local metadata_file="${backup_file}.metadata"
    
    cat > "${metadata_file}" << EOF
{
  "backup_timestamp": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')",
  "backup_type": "${BACKUP_TYPE}",
  "database": "vikunja",
  "host": "${VIKUNJA_DB_HOST}",
  "size_bytes": $(stat -f%z "${backup_file}" 2>/dev/null || stat -c%s "${backup_file}"),
  "compression": "gzip",
  "retention_until": "$(date -u -d "+${RETENTION_DAYS} days" +'%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u -v+${RETENTION_DAYS}d +'%Y-%m-%dT%H:%M:%SZ')",
  "postgres_version": "$(psql --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+' || echo 'unknown')"
}
EOF
    
    log "INFO" "Metadata written to: ${metadata_file}"
}

################################################################################
# ATOMIC BACKUP OF DATABASES
################################################################################
backup_atomic() {
    log "INFO" "Starting atomic backup of all databases"
    
    local atomic_dir="${BACKUP_DIR}/atomic_${TIMESTAMP}"
    mkdir -p "${atomic_dir}"
    
    # Backup Vikunja database
    PGPASSWORD="${VIKUNJA_DB_PASSWORD}" pg_dump \
        -h "${VIKUNJA_DB_HOST}" \
        -U "${VIKUNJA_DB_USER}" \
        -d vikunja \
        --format=plain \
        --compress=9 \
        --file="${atomic_dir}/vikunja.sql.gz" \
        2>> "${BACKUP_LOG}" || error_exit "Vikunja backup failed"
    
    log "INFO" "Atomic backup completed in: ${atomic_dir}"
    
    # Write metadata for atomic backup
    write_backup_metadata "${atomic_dir}/vikunja.sql.gz"
    
    # Generate atomic backup manifest
    cat > "${atomic_dir}/MANIFEST" << EOF
Atomic Backup Manifest
======================
Timestamp: $(date -u +'%Y-%m-%dT%H:%M:%SZ')
Backup Type: Atomic
Components:
  - vikunja.sql.gz (Vikunja PostgreSQL Database)
  
Restoration: Use scripts/restore-postgresql.sh to restore
EOF
    
    log "INFO" "Atomic backup manifest: ${atomic_dir}/MANIFEST"
    
    echo "${atomic_dir}"
}

################################################################################
# MAIN EXECUTION
################################################################################
main() {
    log "INFO" "PostgreSQL Backup Script Started"
    log "INFO" "Backup Type: ${BACKUP_TYPE}"
    
    case "${BACKUP_TYPE}" in
        full)
            backup_file=$(backup_full)
            write_backup_metadata "${backup_file}"
            ;;
        wal)
            backup_wal
            ;;
        atomic)
            atomic_dir=$(backup_atomic)
            ;;
        *)
            error_exit "Unknown backup type: ${BACKUP_TYPE}"
            ;;
    esac
    
    log "INFO" "PostgreSQL Backup Script Completed Successfully"
}

main "$@"
