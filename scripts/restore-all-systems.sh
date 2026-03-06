#!/bin/bash
################################################################################
# XNAi Foundation - Atomic Restore Coordinator
# Purpose: Restore all systems (PostgreSQL, Redis, Qdrant) from atomic backup
# RTO: <1 hour
################################################################################

set -euo pipefail

# Configuration
ATOMIC_BACKUP_DIR="${1:-}"
LOG_DIR="${LOG_DIR:-.}/logs/restore"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESTORE_LOG="${LOG_DIR}/atomic_restore_coordinator_${TIMESTAMP}.log"

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
# VALIDATE BACKUP DIRECTORY
################################################################################
validate_backup_dir() {
    local backup_dir=$1
    
    if [ ! -d "${backup_dir}" ]; then
        error_exit "Backup directory not found: ${backup_dir}"
    fi
    
    # Check for required components
    if [ ! -d "${backup_dir}/postgresql" ]; then
        error_exit "PostgreSQL backup component missing"
    fi
    
    if [ ! -d "${backup_dir}/redis" ]; then
        error_exit "Redis backup component missing"
    fi
    
    if [ ! -d "${backup_dir}/qdrant" ]; then
        error_exit "Qdrant backup component missing"
    fi
    
    log "INFO" "Backup directory validated"
}

################################################################################
# RESTORE POSTGRESQL
################################################################################
restore_postgresql() {
    local backup_dir=$1
    
    log "INFO" "=== Starting PostgreSQL Atomic Restore ==="
    
    if [ ! -f "${backup_dir}/postgresql/vikunja.sql.gz" ]; then
        error_exit "PostgreSQL backup file not found"
    fi
    
    # Set environment variables
    export FORCE_RESTORE=true
    
    # Call restore script
    bash "scripts/restore-postgresql.sh" full "${backup_dir}/postgresql/vikunja.sql.gz" || error_exit "PostgreSQL restore failed"
    
    log "INFO" "PostgreSQL restore completed"
}

################################################################################
# RESTORE REDIS
################################################################################
restore_redis() {
    local backup_dir=$1
    
    log "INFO" "=== Starting Redis Atomic Restore ==="
    
    if [ ! -f "${backup_dir}/redis/dump.rdb.gz" ]; then
        error_exit "Redis backup file not found"
    fi
    
    # Call restore script (prepares files, requires restart)
    bash "scripts/restore-redis.sh" rdb "${backup_dir}/redis/dump.rdb.gz" || error_exit "Redis restore staging failed"
    
    # Restart Redis
    log "INFO" "Restarting Redis service..."
    docker-compose restart redis >> "${RESTORE_LOG}" 2>&1 || error_exit "Redis restart failed"
    
    # Wait for Redis to be ready
    sleep 5
    
    log "INFO" "Redis restore completed"
}

################################################################################
# RESTORE QDRANT
################################################################################
restore_qdrant() {
    local backup_dir=$1
    
    log "INFO" "=== Starting Qdrant Atomic Restore ==="
    
    if [ ! -d "${backup_dir}/qdrant" ]; then
        error_exit "Qdrant backup directory not found"
    fi
    
    # Check for snapshot files
    local snapshot_count=$(find "${backup_dir}/qdrant" -name "*.snapshot" | wc -l)
    
    if [ $snapshot_count -eq 0 ]; then
        error_exit "No Qdrant snapshots found"
    fi
    
    log "INFO" "Found ${snapshot_count} Qdrant snapshots"
    
    # Call restore script
    bash "scripts/restore-qdrant.sh" full "${backup_dir}/qdrant" || error_exit "Qdrant restore failed"
    
    log "INFO" "Qdrant restore completed"
}

################################################################################
# HEALTH CHECKS
################################################################################
check_postgresql_health() {
    log "INFO" "Checking PostgreSQL health..."
    
    local db_host="${VIKUNJA_DB_HOST:-vikunja-db}"
    local db_user="${VIKUNJA_DB_USER:-vikunja}"
    local db_password="${VIKUNJA_DB_PASSWORD:-}"
    
    PGPASSWORD="${db_password}" pg_isready \
        -h "${db_host}" \
        -U "${db_user}" \
        -d vikunja \
        >> "${RESTORE_LOG}" 2>&1 || error_exit "PostgreSQL health check failed"
    
    # Count tables
    local table_count=$(PGPASSWORD="${db_password}" psql \
        -h "${db_host}" \
        -U "${db_user}" \
        -d vikunja \
        -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null || echo "0")
    
    log "INFO" "PostgreSQL health check passed (${table_count} tables)"
}

check_redis_health() {
    log "INFO" "Checking Redis health..."
    
    local redis_host="${REDIS_HOST:-localhost}"
    local redis_port="${REDIS_PORT:-6379}"
    local redis_password="${REDIS_PASSWORD:-}"
    
    local redis_cli_cmd="redis-cli -h ${redis_host} -p ${redis_port}"
    if [ -n "${redis_password}" ]; then
        redis_cli_cmd="${redis_cli_cmd} -a ${redis_password}"
    fi
    
    ${redis_cli_cmd} PING >> "${RESTORE_LOG}" 2>&1 || error_exit "Redis health check failed"
    
    log "INFO" "Redis health check passed"
}

check_qdrant_health() {
    log "INFO" "Checking Qdrant health..."
    
    local qdrant_host="${QDRANT_HOST:-localhost}"
    local qdrant_port="${QDRANT_PORT:-6333}"
    local qdrant_api_key="${QDRANT_API_KEY:-}"
    local qdrant_protocol="${QDRANT_PROTOCOL:-http}"
    
    local health_cmd="curl -s -X GET '${qdrant_protocol}://${qdrant_host}:${qdrant_port}/health'"
    if [ -n "${qdrant_api_key}" ]; then
        health_cmd="${health_cmd} -H 'api-key: ${qdrant_api_key}'"
    fi
    
    local response=$(eval "${health_cmd}")
    
    if ! echo "${response}" | grep -q "\"status\""; then
        error_exit "Qdrant health check failed"
    fi
    
    log "INFO" "Qdrant health check passed"
}

################################################################################
# POST-RESTORE VERIFICATION
################################################################################
verify_restore() {
    log "INFO" "=== Post-Restore Verification ==="
    
    check_postgresql_health
    check_redis_health
    check_qdrant_health
    
    log "INFO" "All systems verified and healthy"
}

################################################################################
# MAIN EXECUTION
################################################################################
main() {
    if [ -z "${ATOMIC_BACKUP_DIR}" ]; then
        error_exit "Usage: $0 <atomic_backup_directory>"
    fi
    
    log "INFO" "======================================================"
    log "INFO" "XNAi Atomic Restore Coordinator Started"
    log "INFO" "======================================================"
    log "INFO" "Backup source: ${ATOMIC_BACKUP_DIR}"
    
    # Validate backup
    validate_backup_dir "${ATOMIC_BACKUP_DIR}"
    
    # Confirm restore
    echo ""
    echo "WARNING: This will restore all systems from atomic backup!"
    echo "Backup: ${ATOMIC_BACKUP_DIR}"
    read -p "Continue with restore? (yes/no): " confirm
    
    if [ "${confirm}" != "yes" ]; then
        log "INFO" "Restore cancelled by user"
        exit 0
    fi
    
    # Restore each system
    log "INFO" "Starting multi-system restore..."
    
    restore_postgresql "${ATOMIC_BACKUP_DIR}"
    restore_redis "${ATOMIC_BACKUP_DIR}"
    restore_qdrant "${ATOMIC_BACKUP_DIR}"
    
    # Post-restore verification
    verify_restore
    
    # Summary
    log "INFO" "======================================================"
    log "INFO" "Atomic Restore Completed Successfully"
    log "INFO" "======================================================"
    log "INFO" "Restored From: ${ATOMIC_BACKUP_DIR}"
    log "INFO" "Restore Time: ${TIMESTAMP}"
    log "INFO" "Actual RTO: ${SECONDS} seconds"
    log "INFO" ""
    log "INFO" "System Status:"
    log "INFO" "  - PostgreSQL: OK"
    log "INFO" "  - Redis: OK"
    log "INFO" "  - Qdrant: OK"
    log "INFO" ""
    log "INFO" "Next Steps:"
    log "INFO" "  1. Verify all application functions"
    log "INFO" "  2. Run application health checks"
    log "INFO" "  3. Document recovery completion"
    log "INFO" ""
}

main "$@"
