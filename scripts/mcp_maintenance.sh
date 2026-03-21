#!/bin/bash
# MB-MCP Maintenance Script
# This script performs daily maintenance and optimization tasks for the Memory Bank MCP.

# --- Configuration ---
MCP_CONTAINER_NAME="xnai_memory_bank_mcp"
LOG_FILE=".logs/mcp_maintenance.log"
REDIS_PASSWORD="${REDIS_PASSWORD}" # Assumes REDIS_PASSWORD is set in the environment

# --- Logging Functions ---
log_info() {
    echo "[$(date -u)] INFO: $1" | tee -a "$LOG_FILE"
}
log_warning() {
    echo "[$(date -u)] WARNING: $1" | tee -a "$LOG_FILE"
}
log_error() {
    echo "[$(date -u)] ERROR: $1" | tee -a "$LOG_FILE"
}

# --- Main Execution ---
log_info "Starting MB-MCP maintenance routine..."

# 1. Prune stale cache entries in MCP (if available)
# This assumes a prune_stale_cache function exists within the MCP's Python environment.
# If the function is not directly callable like this, it might require a specific call or script.
# For now, attempting a direct call via podman exec.
if podman container exists "$MCP_CONTAINER_NAME"; then
    log_info "Pruning stale cache entries in MCP..."
    podman exec "$MCP_CONTAINER_NAME" python3 -c "from mcp_utils import prune_stale_cache; prune_stale_cache()" || log_warning "Failed to prune stale cache. The function might not be available or script path is incorrect."
else
    log_error "MCP container '$MCP_CONTAINER_NAME' not found. Skipping cache prune."
fi

# 2. Flush Redis DB (for temporary cache/session data, be cautious with production Redis)
# NOTE: This command flushes ALL data in DB 0. Use with caution.
# For more granular control, consider using specific keys or a different DB.
# If Redis is used for critical state, this might need adjustment.
log_info "Flushing Redis DB 0 for MCP cache optimization..."
if [ -n "$REDIS_PASSWORD" ]; then
    podman exec xnai_redis redis-cli -a "$REDIS_PASSWORD" --tls --cacert /tls/ca.crt FLUSHDB || log_error "Failed to flush Redis DB 0. Check connection and credentials."
else
    podman exec xnai_redis redis-cli FLUSHDB || log_error "Failed to flush Redis DB 0. Redis might not require a password or connection failed."
fi
log_info "Redis DB 0 flushed."

# 3. Verify essential memory_bank directories
log_info "Verifying critical memory_bank directories..."
MEMORY_BANK_BASE="/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/memory_bank"
EXPECTED_DIRS=("checkpoints" "sessions" "chronicles" "tasks" "experts")

ALL_DIRS_EXIST=true
for dir in "${EXPECTED_DIRS[@]}"; do
    if [ ! -d "$MEMORY_BANK_BASE/$dir" ]; then
        log_warning "Directory '$MEMORY_BANK_BASE/$dir' is missing. Attempting to create it."
        mkdir -p "$MEMORY_BANK_BASE/$dir"
        if [ $? -ne 0 ]; then
            log_error "Failed to create directory '$MEMORY_BANK_BASE/$dir'."
            ALL_DIRS_EXIST=false
        fi
    fi
done

if $ALL_DIRS_EXIST; then
    log_info "Memory bank directory structure verified and corrected."
else
    log_error "Memory bank directory verification/creation failed."
fi

# 4. Final Log Entry
log_info "MB-MCP maintenance routine completed."
echo "[$(date -u)] MB-MCP Maintenance Routine Completed." >> "$LOG_FILE"

exit 0
