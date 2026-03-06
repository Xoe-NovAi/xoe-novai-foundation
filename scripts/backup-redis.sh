#!/bin/bash
################################################################################
# XNAi Foundation - Redis Backup Script
# Purpose: RDB snapshots and AOF backup strategy
# Retention: 7 days
# Execution: Daily
################################################################################

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-.}/backups/redis"
RETENTION_DAYS=${RETENTION_DAYS:-7}
LOG_DIR="${LOG_DIR:-.}/logs/backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_LOG="${LOG_DIR}/redis_backup_${TIMESTAMP}.log"

# Redis Configuration
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_PASSWORD="${REDIS_PASSWORD:-}"
REDIS_DB="${REDIS_DB:-0}"

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
# REDIS RDB SNAPSHOT BACKUP
################################################################################
backup_rdb() {
    log "INFO" "Starting Redis RDB snapshot backup"
    
    # Construct redis-cli command
    local redis_cli_cmd="redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT}"
    
    if [ -n "${REDIS_PASSWORD}" ]; then
        redis_cli_cmd="${redis_cli_cmd} -a ${REDIS_PASSWORD}"
    fi
    
    # Trigger BGSAVE (background save)
    log "INFO" "Triggering BGSAVE on Redis"
    ${redis_cli_cmd} BGSAVE >> "${BACKUP_LOG}" 2>&1 || error_exit "BGSAVE failed"
    
    # Wait for background save to complete (max 5 minutes)
    local wait_time=0
    local max_wait=300
    while [ $wait_time -lt $max_wait ]; do
        local last_save=$(${redis_cli_cmd} LASTSAVE 2>/dev/null || echo "0")
        local current_time=$(date +%s)
        local time_diff=$((current_time - last_save))
        
        if [ $time_diff -lt 5 ]; then
            log "INFO" "BGSAVE completed (LASTSAVE was ${time_diff} seconds ago)"
            break
        fi
        
        sleep 2
        wait_time=$((wait_time + 2))
    done
    
    if [ $wait_time -ge $max_wait ]; then
        error_exit "BGSAVE did not complete within timeout"
    fi
    
    # Get Redis dump file location
    local redis_dump_dir=$(${redis_cli_cmd} CONFIG GET dir | tail -1)
    local redis_dump_file="${redis_dump_dir}/dump.rdb"
    
    log "INFO" "Redis RDB file location: ${redis_dump_file}"
    
    if [ ! -f "${redis_dump_file}" ]; then
        error_exit "Redis dump file not found at ${redis_dump_file}"
    fi
    
    # Copy and compress RDB snapshot
    local backup_file="${BACKUP_DIR}/rdb_snapshot_${TIMESTAMP}.rdb.gz"
    gzip -c "${redis_dump_file}" > "${backup_file}" || error_exit "Compression failed"
    
    local backup_size=$(du -h "${backup_file}" | cut -f1)
    log "INFO" "RDB backup completed: ${backup_file} (${backup_size})"
    
    # Generate checksum
    sha256sum "${backup_file}" > "${backup_file}.sha256"
    log "INFO" "Checksum generated: ${backup_file}.sha256"
    
    # Cleanup old backups
    log "INFO" "Cleaning up backups older than ${RETENTION_DAYS} days"
    find "${BACKUP_DIR}/rdb_snapshot_"*.rdb.gz -mtime "+${RETENTION_DAYS}" -delete 2>/dev/null || true
    find "${BACKUP_DIR}/rdb_snapshot_"*.sha256 -mtime "+${RETENTION_DAYS}" -delete 2>/dev/null || true
    
    echo "${backup_file}"
}

################################################################################
# REDIS AOF BACKUP (Optional)
################################################################################
backup_aof() {
    log "INFO" "Backing up Redis AOF (Append-Only File)"
    
    # Construct redis-cli command
    local redis_cli_cmd="redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT}"
    
    if [ -n "${REDIS_PASSWORD}" ]; then
        redis_cli_cmd="${redis_cli_cmd} -a ${REDIS_PASSWORD}"
    fi
    
    # Check if AOF is enabled
    local aof_enabled=$(${redis_cli_cmd} CONFIG GET appendonly | tail -1)
    
    if [ "${aof_enabled}" != "yes" ]; then
        log "WARN" "AOF is not enabled on Redis server"
        return 0
    fi
    
    # Get AOF file location
    local redis_aof_dir=$(${redis_cli_cmd} CONFIG GET dir | tail -1)
    local redis_aof_file="${redis_aof_dir}/appendonly.aof"
    
    if [ ! -f "${redis_aof_file}" ]; then
        log "WARN" "AOF file not found at ${redis_aof_file}"
        return 0
    fi
    
    # Rewrite AOF to optimize
    log "INFO" "Triggering BGREWRITEAOF"
    ${redis_cli_cmd} BGREWRITEAOF >> "${BACKUP_LOG}" 2>&1 || log "WARN" "BGREWRITEAOF may have failed"
    
    # Copy and compress AOF
    local backup_file="${BACKUP_DIR}/aof_backup_${TIMESTAMP}.aof.gz"
    gzip -c "${redis_aof_file}" > "${backup_file}" || error_exit "AOF compression failed"
    
    local backup_size=$(du -h "${backup_file}" | cut -f1)
    log "INFO" "AOF backup completed: ${backup_file} (${backup_size})"
    
    # Generate checksum
    sha256sum "${backup_file}" > "${backup_file}.sha256"
    
    echo "${backup_file}"
}

################################################################################
# REDIS MEMORY STATISTICS
################################################################################
log_redis_stats() {
    local redis_cli_cmd="redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT}"
    
    if [ -n "${REDIS_PASSWORD}" ]; then
        redis_cli_cmd="${redis_cli_cmd} -a ${REDIS_PASSWORD}"
    fi
    
    log "INFO" "Redis Memory Statistics:"
    ${redis_cli_cmd} INFO memory >> "${BACKUP_LOG}" 2>&1 || true
    log "INFO" "Redis Keyspace:"
    ${redis_cli_cmd} INFO keyspace >> "${BACKUP_LOG}" 2>&1 || true
}

################################################################################
# ATOMIC BACKUP
################################################################################
backup_atomic() {
    log "INFO" "Starting atomic Redis backup"
    
    local atomic_dir="${BACKUP_DIR}/atomic_${TIMESTAMP}"
    mkdir -p "${atomic_dir}"
    
    # Backup RDB
    local redis_cli_cmd="redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT}"
    if [ -n "${REDIS_PASSWORD}" ]; then
        redis_cli_cmd="${redis_cli_cmd} -a ${REDIS_PASSWORD}"
    fi
    
    # Trigger BGSAVE
    ${redis_cli_cmd} BGSAVE >> "${BACKUP_LOG}" 2>&1
    
    # Wait for completion
    local wait_time=0
    while [ $wait_time -lt 300 ]; do
        local last_save=$(${redis_cli_cmd} LASTSAVE 2>/dev/null || echo "0")
        local current_time=$(date +%s)
        if [ $((current_time - last_save)) -lt 5 ]; then
            break
        fi
        sleep 2
        wait_time=$((wait_time + 2))
    done
    
    # Get dump location and copy
    local redis_dump_dir=$(${redis_cli_cmd} CONFIG GET dir | tail -1)
    local redis_dump_file="${redis_dump_dir}/dump.rdb"
    
    gzip -c "${redis_dump_file}" > "${atomic_dir}/dump.rdb.gz" || error_exit "RDB backup failed"
    
    # Backup AOF if enabled
    local aof_enabled=$(${redis_cli_cmd} CONFIG GET appendonly 2>/dev/null | tail -1 || echo "no")
    if [ "${aof_enabled}" = "yes" ]; then
        local redis_aof_file="${redis_dump_dir}/appendonly.aof"
        if [ -f "${redis_aof_file}" ]; then
            gzip -c "${redis_aof_file}" > "${atomic_dir}/appendonly.aof.gz" || log "WARN" "AOF backup failed"
        fi
    fi
    
    # Write metadata
    cat > "${atomic_dir}/MANIFEST" << EOF
Atomic Redis Backup Manifest
=============================
Timestamp: $(date -u +'%Y-%m-%dT%H:%M:%SZ')
Backup Type: Atomic
Components:
  - dump.rdb.gz (Redis RDB Snapshot)
  - appendonly.aof.gz (Redis AOF, if enabled)
  
Restoration: Use scripts/restore-redis.sh to restore
EOF
    
    log "INFO" "Atomic Redis backup completed: ${atomic_dir}"
    
    echo "${atomic_dir}"
}

################################################################################
# MAIN EXECUTION
################################################################################
main() {
    log "INFO" "Redis Backup Script Started"
    
    # Backup RDB
    rdb_file=$(backup_rdb)
    
    # Backup AOF (optional)
    if [ "${BACKUP_AOF:-true}" = "true" ]; then
        aof_file=$(backup_aof) || log "WARN" "AOF backup skipped"
    fi
    
    # Log statistics
    log_redis_stats
    
    # Log summary
    log "INFO" "Redis backup completed successfully"
    log "INFO" "RDB backup: ${rdb_file}"
}

main "$@"
