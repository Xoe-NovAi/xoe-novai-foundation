#!/bin/bash
# OpenCode Multi-Account Rotation Setup Script
# ===========================================
#
# This script sets up the rotation system for multiple OpenCode accounts
# to distribute usage and avoid hitting free tier limits.
#
# Usage: ./xnai-setup-opencode-rotation.sh

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${HOME}/.config/xnai"
CREDENTIALS_FILE="${CONFIG_DIR}/opencode-credentials.yaml"
ROTATION_RULES_FILE="${CONFIG_DIR}/opencode-rotation-rules.yaml"

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

# Create configuration directory
setup_config_directory() {
    log_info "Setting up configuration directory..."
    
    mkdir -p "$CONFIG_DIR" || {
        log_error "Failed to create configuration directory: $CONFIG_DIR"
        exit 1
    }
    
    log_success "Configuration directory created: $CONFIG_DIR"
}

# Copy credential template
setup_credentials() {
    log_info "Setting up credential templates..."
    
    if [ -f "$SCRIPT_DIR/../config/templates/opencode-credentials.yaml.template" ]; then
        cp "$SCRIPT_DIR/../config/templates/opencode-credentials.yaml.template" "$CONFIG_DIR/opencode-credentials.yaml"
        success "Credential template copied to $CONFIG_DIR/opencode-credentials.yaml"
    elif [ -f "$SCRIPT_DIR/xnai-setup-opencode-credentials.yaml" ]; then
        cp "$SCRIPT_DIR/xnai-setup-opencode-credentials.yaml" "$CONFIG_DIR/opencode-credentials.yaml"
        log_success "Credential template copied to $CONFIG_DIR/opencode-credentials.yaml"
    else
        log_warning "No credential template found, creating basic structure..."
        cat > "$CONFIG_DIR/opencode-credentials.yaml" << EOF
# OpenCode Multi-Account Configuration
# Copy this file and fill in your actual credentials
credentials:
  opencode:
    accounts:
      account_1:
        name: "OpenCode Account 1"
        email: "user1@example.com"
        api_key: "your-api-key-here"
        xdg_data_home: "/tmp/xnai-opencode-instance-1"
        port: 10001
        status: "active"
      account_2:
        name: "OpenCode Account 2"
        email: "user2@example.com"
        api_key: "your-api-key-here"
        xdg_data_home: "/tmp/xnai-opencode-instance-2"
        port: 10002
        status: "active"
EOF
        log_success "Basic credential template created at $CONFIG_DIR/opencode-credentials.yaml"
    fi
    
    # Set secure permissions
    chmod 0600 "$CONFIG_DIR/opencode-credentials.yaml"
    log_success "Set secure permissions (0600) on credential file"
}

# Copy rotation rules template
setup_rotation_rules() {
    log_info "Setting up rotation rules..."
    
    if [ -f "$SCRIPT_DIR/../config/templates/opencode-rotation-rules.yaml.template" ]; then
        cp "$SCRIPT_DIR/../config/templates/opencode-rotation-rules.yaml.template" "$CONFIG_DIR/opencode-rotation-rules.yaml"
        success "Rotation rules template copied to $CONFIG_DIR/opencode-rotation-rules.yaml"
    else
        log_warning "No rotation rules template found, creating basic structure..."
        cat > "$CONFIG_DIR/opencode-rotation-rules.yaml" << EOF
# OpenCode Account Rotation Rules
# ===============================
#
# This file defines the rotation strategy for multiple OpenCode accounts
# to distribute usage and avoid hitting free tier limits.

rotation:
  enabled: true
  strategy: "round_robin"  # Options: round_robin, lowest_usage_first, random
  check_interval: 300      # Check rotation every 300 seconds (5 minutes)
  
  # Account selection criteria
  selection:
    priority: "usage_based"  # Options: usage_based, random, sequential
    min_usage_threshold: 10  # Minimum usage percentage before considering rotation
    max_usage_threshold: 80  # Maximum usage percentage before forcing rotation
    
  # Fallback configuration
  fallback:
    enabled: true
    strategy: "sequential"   # Try accounts in order when primary fails
    max_retries: 3
    retry_delay: 60          # Wait 60 seconds between retries
    
  # Usage tracking
  tracking:
    enabled: true
    metrics_file: "~/.config/xnai/opencode-usage-metrics.json"
    update_interval: 60      # Update usage metrics every 60 seconds
    
  # Account health monitoring
  health_check:
    enabled: true
    check_interval: 300      # Check account health every 5 minutes
    timeout: 30              # Timeout for health check requests
    max_failures: 3          # Mark account as unhealthy after 3 consecutive failures
    
  # Notification settings
  notifications:
    enabled: true
    threshold_warning: 70    # Warn when usage reaches 70%
    threshold_critical: 90   # Critical alert when usage reaches 90%
    log_file: "~/.config/xnai/opencode-rotation.log"

# Account-specific rules
accounts:
  account_1:
    priority: 1
    enabled: true
    max_daily_requests: 1000
    max_hourly_requests: 100
    
  account_2:
    priority: 2
    enabled: true
    max_daily_requests: 1000
    max_hourly_requests: 100
    
  account_3:
    priority: 3
    enabled: true
    max_daily_requests: 1000
    max_hourly_requests: 100
    
  account_4:
    priority: 4
    enabled: true
    max_daily_requests: 1000
    max_hourly_requests: 100
    
  account_5:
    priority: 5
    enabled: true
    max_daily_requests: 1000
    max_hourly_requests: 100
    
  account_6:
    priority: 6
    enabled: true
    max_daily_requests: 1000
    max_hourly_requests: 100
    
  account_7:
    priority: 7
    enabled: true
    max_daily_requests: 1000
    max_hourly_requests: 100
    
  account_8:
    priority: 8
    enabled: true
    max_daily_requests: 1000
    max_hourly_requests: 100
EOF
        log_success "Basic rotation rules created at $CONFIG_DIR/opencode-rotation-rules.yaml"
    fi
    
    # Set secure permissions
    chmod 0600 "$CONFIG_DIR/opencode-rotation-rules.yaml"
    log_success "Set secure permissions (0600) on rotation rules file"
}

# Create systemd service for rotation monitoring
setup_systemd_service() {
    log_info "Setting up systemd service for rotation monitoring..."
    
    local service_file="/etc/systemd/system/xnai-opencode-rotation.service"
    local timer_file="/etc/systemd/system/xnai-opencode-rotation.timer"
    
    # Check if running as root for system-wide service
    if [ "$EUID" -eq 0 ]; then
        log_info "Installing system-wide systemd service..."
        
        cat > "$service_file" << EOF
[Unit]
Description=XNAi OpenCode Account Rotation Monitor
After=network.target

[Service]
Type=oneshot
User=$SUDO_USER
WorkingDirectory=/home/$SUDO_USER
ExecStart=$SCRIPT_DIR/xnai-monitor-rotation.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

        cat > "$timer_file" << EOF
[Unit]
Description=Run XNAi OpenCode Account Rotation Monitor
Requires=xnai-opencode-rotation.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min
Persistent=true

[Install]
WantedBy=timers.target
EOF

        systemctl daemon-reload
        systemctl enable xnai-opencode-rotation.timer
        systemctl start xnai-opencode-rotation.timer
        
        log_success "System-wide systemd service installed and started"
    else
        log_info "Installing user systemd service..."
        
        local user_service_file="$HOME/.config/systemd/user/xnai-opencode-rotation.service"
        local user_timer_file="$HOME/.config/systemd/user/xnai-opencode-rotation.timer"
        
        mkdir -p "$HOME/.config/systemd/user"
        
        cat > "$user_service_file" << EOF
[Unit]
Description=XNAi OpenCode Account Rotation Monitor
After=network.target

[Service]
Type=oneshot
ExecStart=$SCRIPT_DIR/xnai-monitor-rotation.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF

        cat > "$user_timer_file" << EOF
[Unit]
Description=Run XNAi OpenCode Account Rotation Monitor
Requires=xnai-opencode-rotation.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min
Persistent=true

[Install]
WantedBy=timers.target
EOF

        systemctl --user daemon-reload
        systemctl --user enable xnai-opencode-rotation.timer
        systemctl --user start xnai-opencode-rotation.timer
        
        log_success "User systemd service installed and started"
    fi
}

# Create rotation monitoring script
create_monitoring_script() {
    log_info "Creating rotation monitoring script..."
    
    cat > "$SCRIPT_DIR/xnai-monitor-rotation.sh" << 'EOF'
#!/bin/bash
# OpenCode Account Rotation Monitor
# ================================
#
# This script monitors OpenCode account usage and performs rotation
# when necessary to avoid hitting free tier limits.

set -euo pipefail

CONFIG_DIR="${HOME}/.config/xnai"
CREDENTIALS_FILE="${CONFIG_DIR}/opencode-credentials.yaml"
ROTATION_RULES_FILE="${CONFIG_DIR}/opencode-rotation-rules.yaml"
METRICS_FILE="${CONFIG_DIR}/opencode-usage-metrics.json"

# Load rotation rules
if [ -f "$ROTATION_RULES_FILE" ]; then
    source <(grep -E '^[a-zA-Z_]+:' "$ROTATION_RULES_FILE" | sed 's/: /=/')
fi

# Check if rotation is enabled
if [ "${enabled:-false}" != "true" ]; then
    exit 0
fi

# Function to check account health
check_account_health() {
    local account="$1"
    local xdg_dir="$2"
    local port="$3"
    
    # Test the account with a simple request
    timeout 30 bash -c "XDG_DATA_HOME=$xdg_dir opencode chat --json 'health check' 2>&1" || {
        echo "Account $account is unhealthy"
        return 1
    }
    
    echo "Account $account is healthy"
    return 0
}

# Function to rotate accounts
perform_rotation() {
    log_info "Performing account rotation..."
    
    # Get current active account
    current_account=$(cat /tmp/xnai-opencode-current-account 2>/dev/null || echo "account_1")
    
    # Determine next account based on strategy
    case "${strategy:-round_robin}" in
        "round_robin")
            case "$current_account" in
                "account_1") next_account="account_2" ;;
                "account_2") next_account="account_3" ;;
                "account_3") next_account="account_4" ;;
                "account_4") next_account="account_5" ;;
                "account_5") next_account="account_6" ;;
                "account_6") next_account="account_7" ;;
                "account_7") next_account="account_8" ;;
                "account_8") next_account="account_1" ;;
                *) next_account="account_1" ;;
            esac
            ;;
        "lowest_usage_first")
            # Implement usage-based rotation logic
            next_account="account_1"  # Placeholder
            ;;
        *)
            next_account="account_1"
            ;;
    esac
    
    # Check if next account is healthy
    if check_account_health "$next_account"; then
        echo "$next_account" > /tmp/xnai-opencode-current-account
        log_success "Rotated to account: $next_account"
    else
        log_warning "Next account $next_account is unhealthy, keeping current account"
    fi
}

# Main execution
main() {
    log_info "Starting OpenCode account rotation monitor..."
    
    # Perform rotation if needed
    perform_rotation
    
    # Update usage metrics
    if [ -f "$CREDENTIALS_FILE" ]; then
        # Extract account information and update metrics
        # This is a simplified implementation
        echo "$(date): Rotation check completed" >> "$METRICS_FILE"
    fi
}

main "$@"
EOF

    chmod +x "$SCRIPT_DIR/xnai-monitor-rotation.sh"
    log_success "Rotation monitoring script created"
}

# Main execution
main() {
    log_info "Starting OpenCode multi-account rotation setup..."
    
    # Check dependencies
    if ! command -v yq &> /dev/null; then
        log_warning "yq is not installed. Some features may not work properly."
        log_info "Install with: pip install yq or brew install yq"
    fi
    
    # Setup configuration
    setup_config_directory
    setup_credentials
    setup_rotation_rules
    create_monitoring_script
    
    # Setup systemd service
    setup_systemd_service
    
    log_success "Setup completed successfully!"
    
    echo ""
    log_info "Next Steps:"
    echo "=========="
    log_info "1. Edit credentials: $CONFIG_DIR/opencode-credentials.yaml"
    echo "2. Review rotation rules: $CONFIG_DIR/opencode-rotation-rules.yaml"
    echo "3. Run manual test: $SCRIPT_DIR/xnai-inject-credentials.sh"
    echo "4. Monitor rotation: journalctl -u xnai-opencode-rotation.service -f"
    echo ""
    log_info "Usage:"
    echo "======"
    log_info "To use a specific account:"
    echo "  XDG_DATA_HOME=/tmp/xnai-opencode-instance-1 opencode chat 'Your prompt'"
    echo ""
    log_info "To test all accounts:"
    for i in {1..8}; do
        echo "  XDG_DATA_HOME=/tmp/xnai-opencode-instance-$i opencode chat --json 'test' 2>&1 | head -3"
    done
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
EOF