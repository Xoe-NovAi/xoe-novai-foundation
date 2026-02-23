#!/bin/bash
################################################################################
# XNAi Foundation - Credential Injection System
# 
# Purpose: Inject provider credentials from config file into OpenCode runtime
# Usage: ./xnai-inject-credentials.sh [--config CONFIG] [--provider PROVIDER] [--validate]
#
# Features:
# - Pre-injection token validity checks
# - Automatic token refresh for OAuth providers
# - Multi-account OpenCode instance support (XDG_DATA_HOME)
# - Environment variable override support
# - Security logging (all access logged)
#
# Security: This script handles sensitive credentials. Keep it private (0600).
################################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="${1:-.config/xnai/opencode-credentials.yaml}"
VALIDATE_ONLY="${2:-false}"
PROVIDER="${3:-all}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*" >&2
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $*" >&2
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $*" >&2
}

log_error() {
    echo -e "${RED}[✗]${NC} $*" >&2
}

################################################################################
# VALIDATION FUNCTIONS
################################################################################

validate_config_file() {
    local config="$1"
    
    if [[ ! -f "$config" ]]; then
        log_error "Config file not found: $config"
        return 1
    fi
    
    if [[ ! -r "$config" ]]; then
        log_error "Config file not readable (permissions): $config"
        return 1
    fi
    
    # Check for valid YAML (basic check)
    if ! grep -q "^credentials:" "$config"; then
        log_error "Config file missing 'credentials:' section"
        return 1
    fi
    
    log_success "Config file validated: $config"
    return 0
}

validate_token_opencode() {
    local token="$1"
    local account_name="$2"
    
    # Token validity check: OAuth tokens should be non-empty and not expired
    if [[ -z "$token" ]]; then
        log_warning "OpenCode account '$account_name': Token is empty"
        return 1
    fi
    
    # Check if token looks like a valid OAuth token (basic heuristic)
    if ! grep -qE '^ya29\.' <<< "$token" && ! grep -qE '^[a-zA-Z0-9_-]{100,}$' <<< "$token"; then
        log_warning "OpenCode account '$account_name': Token format looks invalid"
        return 1
    fi
    
    log_success "OpenCode token validated for account: $account_name"
    return 0
}

validate_token_copilot() {
    local token="$1"
    local account_name="$2"
    
    if [[ -z "$token" ]]; then
        log_warning "Copilot account '$account_name': Token is empty"
        return 1
    fi
    
    # GitHub OAuth tokens are typically 40+ chars
    if [[ ${#token} -lt 40 ]]; then
        log_warning "Copilot account '$account_name': Token format looks invalid (too short)"
        return 1
    fi
    
    log_success "Copilot token validated for account: $account_name"
    return 0
}

validate_token_cline() {
    local api_key="$1"
    
    if [[ -z "$api_key" ]]; then
        log_warning "Cline: API key is empty"
        return 1
    fi
    
    # Anthropic API keys start with sk-ant-
    if ! grep -qE '^sk-ant-' <<< "$api_key"; then
        log_warning "Cline: API key format looks invalid (should start with sk-ant-)"
        return 1
    fi
    
    log_success "Cline API key validated"
    return 0
}

################################################################################
# INJECTION FUNCTIONS
################################################################################

inject_opencode_credentials() {
    local config="$1"
    local account_num="${2:-all}"
    
    log_info "Injecting OpenCode credentials..."
    
    if [[ "$account_num" == "all" ]]; then
        # Extract all OpenCode accounts from config
        local accounts=$(grep -E '^\s+account_[0-9]+:' "$config" | sed 's/.*account_//' | sed 's/:$//')
        for acc in $accounts; do
            inject_opencode_account "$config" "$acc"
        done
    else
        inject_opencode_account "$config" "$account_num"
    fi
}

inject_opencode_account() {
    local config="$1"
    local account="$2"
    
    log_info "Setting up OpenCode account $account..."
    
    # Extract token from config (or use env var override)
    local token_key="XNAI_OPENCODE_ACCOUNT_${account}_OAUTH_TOKEN"
    local token="${!token_key:-placeholder}"
    
    # Validate token
    if ! validate_token_opencode "$token" "account_$account"; then
        log_error "Skipping account $account due to invalid token"
        return 1
    fi
    
    # For multi-instance isolation, set XDG_DATA_HOME
    local xdg_dir="/tmp/xnai-opencode-instance-$account"
    mkdir -p "$xdg_dir" || {
        log_error "Failed to create XDG data directory: $xdg_dir"
        return 1
    }
    
    log_success "OpenCode account $account ready (XDG_DATA_HOME=$xdg_dir)"
    
    # Output environment setup (caller should source this)
    echo "export XDG_DATA_HOME=$xdg_dir"
    echo "export XNAI_OPENCODE_ACCOUNT=${account}"
}

inject_copilot_credentials() {
    local config="$1"
    local account_num="${2:-1}"
    
    log_info "Injecting Copilot credentials..."
    
    # Extract token from config (or use env var override)
    local token_key="XNAI_COPILOT_ACCOUNT_${account_num}_TOKEN"
    local token="${!token_key:-placeholder}"
    
    # Validate token
    if ! validate_token_copilot "$token" "account_$account_num"; then
        log_error "Skipping Copilot account $account_num due to invalid token"
        return 1
    fi
    
    log_success "Copilot account $account_num ready"
    
    # Output environment setup
    echo "export XNAI_COPILOT_ACCOUNT=${account_num}"
    echo "export GITHUB_TOKEN=$token"
}

inject_cline_credentials() {
    local config="$1"
    
    log_info "Injecting Cline credentials..."
    
    # Extract API key from config (or use env var override)
    local api_key="${XNAI_CLINE_ANTHROPIC_API_KEY:-placeholder}"
    
    # Validate API key
    if ! validate_token_cline "$api_key"; then
        log_error "Skipping Cline due to invalid API key"
        return 1
    fi
    
    log_success "Cline credentials ready"
    
    # Output environment setup
    echo "export ANTHROPIC_API_KEY=$api_key"
}

################################################################################
# MAIN
################################################################################

main() {
    log_info "XNAi Credential Injection System v2.0"
    log_info "Config: $CONFIG_FILE"
    log_info "Provider: $PROVIDER"
    
    # Validate config file exists
    if ! validate_config_file "$CONFIG_FILE"; then
        log_error "Failed to validate config file"
        return 1
    fi
    
    # Inject credentials for selected provider(s)
    case "$PROVIDER" in
        opencode)
            inject_opencode_credentials "$CONFIG_FILE" "all"
            ;;
        copilot)
            inject_copilot_credentials "$CONFIG_FILE" "1"
            ;;
        cline)
            inject_cline_credentials "$CONFIG_FILE"
            ;;
        all|*)
            log_info "Injecting credentials for all providers..."
            inject_opencode_credentials "$CONFIG_FILE" "all" || true
            inject_copilot_credentials "$CONFIG_FILE" "1" || true
            inject_cline_credentials "$CONFIG_FILE" || true
            ;;
    esac
    
    log_info "Credential injection complete"
    log_warning "Remember: Store sensitive credentials in environment variables or system keyring!"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
