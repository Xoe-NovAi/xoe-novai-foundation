#!/bin/bash
# Antigravity Sovereign Maintenance & Health Monitor
# Part of the Omega Stack (Xoe-NovAi Foundation)
# =================================================

set -euo pipefail

# Configuration
CONFIG_DIR="${HOME}/.config/opencode"
ACCOUNTS_FILE="${CONFIG_DIR}/antigravity-accounts.json"
AUTH_FILE="${HOME}/.local/share/opencode/auth.json"
LOG_DIR="${CONFIG_DIR}/antigravity-logs"
INSTANCE_PREFIX="/tmp/xnai-opencode-instance-"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 1. System Check
check_system() {
    log_info "Performing system integrity check..."
    if ! command -v opencode &> /dev/null; then
        log_error "OpenCode CLI not found in PATH."
        return 1
    fi
    
    if [[ ! -f "$ACCOUNTS_FILE" ]]; then
        log_warn "Antigravity accounts file missing: $ACCOUNTS_FILE"
    else
        log_success "Found Antigravity accounts registry."
    fi
}

# 2. Health Monitor
check_health() {
    log_info "Analyzing account health and quotas..."
    
    if [[ ! -f "$ACCOUNTS_FILE" ]]; then
        log_error "Cannot check health: No accounts configured."
        return 1
    fi
    
    # Extract account info using python workaround
    python3 -c "
import json, sys, os, time
from datetime import datetime

try:
    with open('$ACCOUNTS_FILE', 'r') as f:
        data = json.load(f)
    
    accounts = data.get('accounts', [])
    print(f'Found {len(accounts)} accounts.')
    
    for i, acc in enumerate(accounts):
        email = acc.get('email', 'Unknown')
        status = 'ENABLED' if acc.get('enabled', True) else 'DISABLED'
        last_used = acc.get('lastUsed', 0)
        
        # Calculate human readable time
        if last_used > 0:
            last_used_str = datetime.fromtimestamp(last_used/1000).strftime('%Y-%m-%d %H:%M:%S')
        else:
            last_used_str = 'Never'
            
        print(f' [{i+1}] {email} | Status: {status} | Last Used: {last_used_str}')
        
        # Check for rate limits in cached quota
        quota = acc.get('cachedQuota', {})
        if quota:
            print('     Quota status:')
            for group, gdata in quota.items():
                rem = gdata.get('remainingFraction', 1.0) * 100
                reset = gdata.get('resetTime', 'N/A')
                print(f'      - {group}: {rem:.1f}% remaining (Resets: {reset})')
except Exception as e:
    print(f'Error parsing accounts: {e}')
    sys.exit(1)
"
}

# 3. Instance Sync
sync_instances() {
    log_info "Synchronizing Antigravity credentials to Omega instances..."
    
    if [[ ! -f "$AUTH_FILE" ]]; then
        log_error "Source auth.json not found: $AUTH_FILE"
        return 1
    fi
    
    for i in {1..8}; do
        TARGET_DIR="${INSTANCE_PREFIX}${i}/opencode"
        mkdir -p "$TARGET_DIR"
        cp "$AUTH_FILE" "$TARGET_DIR/auth.json"
        log_info " Sync -> Instance $i"
    done
    log_success "Credential synchronization complete."
}

# 4. Clean Logs
cleanup_logs() {
    log_info "Cleaning up old debug logs..."
    if [[ -d "$LOG_DIR" ]]; then
        find "$LOG_DIR" -name "*.log" -mtime +7 -delete
        log_success "Deleted logs older than 7 days."
    else
        log_info "No log directory found at $LOG_DIR"
    fi
}

# 5. Provision Instances (Minimax Working Memory)
provision_instances() {
    log_info "Provisioning Omega instances with MiniMax configuration..."
    
    # Configuration
    local XNAI_CONF="${XNAI_CONFIG_DIR:-${HOME}/.config/xnai}"
    
    # Check for Opencode API Key
    if [[ -f "${XNAI_CONF}/.env" ]]; then
        source "${XNAI_CONF}/.env"
    fi
    
    # Fallback to direct check if env var not set
    local api_key="${OPENCODE_API_KEY_1:-}"
    if [[ -z "$api_key" ]]; then
        # Try to find it in auth.json
        if [[ -f "$AUTH_FILE" ]]; then
             # Simple grep extract since we lack jq/yq
             api_key=$(grep -o '"opencode":.*"key": *"[^"]*"' "$AUTH_FILE" | cut -d'"' -f6)
        fi
    fi
    
    if [[ -z "$api_key" ]]; then
        log_warn "No OpenCode API key found. Instances will be unauthenticated for MiniMax."
        api_key=""
    fi

    for i in {1..8}; do
        TARGET_DIR="${INSTANCE_PREFIX}${i}/opencode"
        mkdir -p "$TARGET_DIR"
        
        # Create opencode.json
        # Check if specific key exists
        local specific_key_var="OPENCODE_API_KEY_$i"
        local specific_key="${!specific_key_var:-$api_key}"
        
        cat > "$TARGET_DIR/opencode.json" << EOF
{
  "\$schema": "https://opencode.ai/config.json",
  "model": "minimax-m2.5-free",
  "api_key": "$specific_key",
  "port": $((10000 + i))
}
EOF
        log_info " Provisioned -> Instance $i (Port $((10000 + i)))"
        
        # Ensure auth.json is also there
        if [[ -f "$AUTH_FILE" ]]; then
            cp "$AUTH_FILE" "$TARGET_DIR/auth.json"
        fi
    done
    log_success "Instance provisioning complete."
}

# Main
case "${1:-status}" in
    status)
        check_system
        check_health
        ;;
    sync)
        sync_instances
        ;;
    provision)
        provision_instances
        ;;
    cleanup)
        cleanup_logs
        ;;
    all)
        check_system
        check_health
        provision_instances
        sync_instances
        cleanup_logs
        ;;
    *)
        echo "Usage: $0 {status|sync|provision|cleanup|all}"
        exit 1
        ;;
esac
