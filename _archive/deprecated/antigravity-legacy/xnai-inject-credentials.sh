#!/bin/bash
# OpenCode Multi-Account Credential Injection Script
# ================================================
#
# This script injects credentials for multiple OpenCode accounts
# and sets up the XDG_DATA_HOME isolation pattern for multi-instance support.
#
# Usage: ./xnai-inject-credentials.sh [CONFIG_FILE] [ACCOUNT|all]
# Example: ./xnai-inject-credentials.sh ~/.config/xnai/opencode-credentials.yaml all

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${1:-.config/xnai/opencode-credentials.yaml}"
ACCOUNT="${2:-all}"
VALIDATE_ONLY="${3:-false}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validation functions
validate_token_opencode() {
    local token="$1"
    local account="$2"
    
    if [[ -z "$token" ]]; then
        log_error "Empty token for account $account"
        return 1
    fi
    
    # Basic token format validation (OpenCode tokens typically start with sk-)
    if [[ ! "$token" =~ ^sk- ]]; then
        log_error "Invalid token format for account $account"
        return 1
    fi
    
    log_success "Token validation passed for account $account"
    return 0
}

# Credential injection functions
inject_opencode_credentials() {
    local config="$1"
    local accounts="$2"
    
    if [[ "$accounts" == "all" ]]; then
        accounts=$(yq eval '.credentials.opencode.accounts | keys | .[]' "$config" 2>/dev/null || echo "")
    fi
    
    if [[ -z "$accounts" ]]; then
        log_error "No accounts found in configuration"
        return 1
    fi
    
    for acc in $accounts; do
        inject_opencode_account "$config" "$acc"
    done
}

inject_opencode_account() {
    local config="$1"
    local account_num="$2"
    
    local name email api_key xdg_dir port status
    
    # Extract account details from YAML
    name=$(yq eval ".credentials.opencode.accounts.${account_num}.name" "$config" 2>/dev/null || echo "")
    email=$(yq eval ".credentials.opencode.accounts.${account_num}.email" "$config" 2>/dev/null || echo "")
    api_key=$(yq eval ".credentials.opencode.accounts.${account_num}.api_key" "$config" 2>/dev/null || echo "")
    xdg_dir=$(yq eval ".credentials.opencode.accounts.${account_num}.xdg_data_home" "$config" 2>/dev/null || echo "")
    port=$(yq eval ".credentials.opencode.accounts.${account_num}.port" "$config" 2>/dev/null || echo "")
    status=$(yq eval ".credentials.opencode.accounts.${account_num}.status" "$config" 2>/dev/null || echo "")
    
    if [[ -z "$name" || -z "$email" || -z "$api_key" || -z "$xdg_dir" || -z "$port" ]]; then
        log_error "Incomplete configuration for account $account_num"
        return 1
    fi
    
    if [[ "$status" != "active" ]]; then
        log_warning "Account $account_num is not active, skipping"
        return 0
    fi
    
    # Expand environment variables in api_key
    api_key_expanded="${api_key//\$\{/\${}"
    api_key_expanded="${api_key_expanded//\}/}"
    api_key_expanded="${api_key_expanded//\$/\$}"
    api_key_expanded=$(eval echo "$api_key_expanded")
    
    # Validate token
    if ! validate_token_opencode "$api_key_expanded" "$account_num"; then
        log_error "Skipping account $account_num due to invalid token"
        return 1
    fi
    
    # Create XDG_DATA_HOME directory
    mkdir -p "$xdg_dir" || {
        log_error "Failed to create XDG_DATA_HOME directory: $xdg_dir"
        return 1
    }
    
    # Create isolated opencode directory structure
    mkdir -p "$xdg_dir/opencode" || {
        log_error "Failed to create opencode directory in: $xdg_dir"
        return 1
    }
    
    # Create opencode.json configuration for this instance
    cat > "$xdg_dir/opencode/opencode.json" << EOF
{
  "\$schema": "https://opencode.ai/config.json",
  "model": "minimax-m2.5-free",
  "api_key": "$api_key_expanded",
  "email": "$email",
  "port": $port
}
EOF
    
    # Set secure permissions
    chmod 0600 "$xdg_dir/opencode/opencode.json"
    
    log_success "Injected credentials for account $account_num ($name)"
    log_info "  XDG_DATA_HOME: $xdg_dir"
    log_info "  Port: $port"
    log_info "  Model: minimax-m2.5-free"
}

# Main execution
main() {
    log_info "Starting OpenCode credential injection..."
    
    # Check if yq is available
    if ! command -v yq &> /dev/null; then
        log_error "yq is required but not installed. Please install yq first."
        log_info "Install with: pip install yq or brew install yq"
        exit 1
    fi
    
    # Check if config file exists
    if [[ ! -f "$CONFIG_FILE" ]]; then
        log_error "Configuration file not found: $CONFIG_FILE"
        log_info "Please copy scripts/xnai-setup-opencode-credentials.yaml to $CONFIG_FILE and edit with your credentials"
        exit 1
    fi
    
    # Validate configuration file
    if ! yq eval '.' "$CONFIG_FILE" &> /dev/null; then
        log_error "Invalid YAML configuration file: $CONFIG_FILE"
        exit 1
    fi
    
    # Check if OpenCode is available
    if ! command -v opencode &> /dev/null; then
        log_error "OpenCode CLI is not installed or not in PATH"
        exit 1
    fi
    
    log_info "Using configuration file: $CONFIG_FILE"
    log_info "Target account(s): $ACCOUNT"
    
    # Inject credentials based on provider
    case "$PROVIDER" in
        "opencode")
            inject_opencode_credentials "$CONFIG_FILE" "$ACCOUNT"
            ;;
        "all")
            inject_opencode_credentials "$CONFIG_FILE" "$ACCOUNT"
            ;;
        *)
            log_error "Unknown provider: $PROVIDER"
            log_info "Supported providers: opencode, all"
            exit 1
            ;;
    esac
    
    log_success "Credential injection completed successfully!"
    
    # Display usage instructions
    log_info ""
    log_info "Usage Instructions:"
    log_info "=================="
    log_info "To use a specific account instance:"
    log_info "  XDG_DATA_HOME=/tmp/xnai-opencode-instance-1 opencode chat 'Your prompt'"
    log_info ""
    log_info "To start a server with a specific account:"
    log_info "  XDG_DATA_HOME=/tmp/xnai-opencode-instance-1 opencode serve --port 10001"
    log_info ""
    log_info "To test all accounts:"
    for i in {1..8}; do
        log_info "  XDG_DATA_HOME=/tmp/xnai-opencode-instance-$i opencode chat --json 'test' 2>&1 | head -5"
    done
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi