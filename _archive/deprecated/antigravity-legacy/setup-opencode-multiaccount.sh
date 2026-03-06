#!/bin/bash
# OpenCode Multi-Account Setup Script
# ==================================
#
# This script sets up the complete OpenCode multi-account system
# with MiniMax m2.5 prime working memory and Antigravity integration.
#
# Usage: ./setup-opencode-multiaccount.sh [STEP]
# Example: ./setup-opencode-multiaccount.sh all

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_DIR="${HOME}/.config/xnai"
LOG_FILE="${CONFIG_DIR}/setup.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Helper function to convert YAML to JSON for jq
# Using Python as a workaround for missing yq
yaml2json() {
    python3 -c "import yaml, json, sys; print(json.dumps(yaml.safe_load(sys.stdin)))"
}

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    local missing_deps=()
    
    # Check for required tools
    command -v opencode &> /dev/null || missing_deps+=("opencode")
    # command -v yq &> /dev/null || missing_deps+=("yq") # yq is missing, using python workaround
    command -v jq &> /dev/null || missing_deps+=("jq")
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_info "Please install missing dependencies and try again"
        exit 1
    fi
    
    log_success "All dependencies are available"
}

# Setup configuration directory
setup_config_directory() {
    log_info "Setting up configuration directory..."
    
    mkdir -p "$CONFIG_DIR" || {
        log_error "Failed to create configuration directory: $CONFIG_DIR"
        exit 1
    }
    
    # Set secure permissions
    chmod 0700 "$CONFIG_DIR"
    
    log_success "Configuration directory created: $CONFIG_DIR"
}

# Copy configuration files
copy_configurations() {
    log_info "Copying configuration files..."
    
    # Copy credential template
    if [ -f "$SCRIPT_DIR/xnai-setup-opencode-credentials.yaml" ]; then
        cp "$SCRIPT_DIR/xnai-setup-opencode-credentials.yaml" "$CONFIG_DIR/opencode-credentials.yaml"
        chmod 0600 "$CONFIG_DIR/opencode-credentials.yaml"
        log_success "Copied credential template to $CONFIG_DIR/opencode-credentials.yaml"
    else
        log_error "Credential template not found"
        exit 1
    fi
    
    # Copy rotation rules
    if [ -f "$SCRIPT_DIR/xnai-setup-opencode-rotation.sh" ]; then
        cp "$SCRIPT_DIR/xnai-setup-opencode-rotation.sh" "$CONFIG_DIR/opencode-rotation-setup.sh"
        chmod +x "$CONFIG_DIR/opencode-rotation-setup.sh"
        log_success "Copied rotation setup script"
    fi
    
    # Copy working memory configuration
    if [ -f "$PROJECT_ROOT/config/minimax-working-memory.yaml" ]; then
        cp "$PROJECT_ROOT/config/minimax-working-memory.yaml" "$CONFIG_DIR/"
        chmod 0600 "$CONFIG_DIR/minimax-working-memory.yaml"
        log_success "Copied working memory configuration"
    fi
    
    # Copy handoff protocol
    if [ -f "$PROJECT_ROOT/config/working-memory-handoff-protocol.yaml" ]; then
        cp "$PROJECT_ROOT/config/working-memory-handoff-protocol.yaml" "$CONFIG_DIR/"
        chmod 0600 "$CONFIG_DIR/working-memory-handoff-protocol.yaml"
        log_success "Copied handoff protocol configuration"
    fi
    
    # Copy Antigravity configuration
    if [ -f "$PROJECT_ROOT/config/antigravity-free-frontier.yaml" ]; then
        cp "$PROJECT_ROOT/config/antigravity-free-frontier.yaml" "$CONFIG_DIR/"
        chmod 0600 "$CONFIG_DIR/antigravity-free-frontier.yaml"
        log_success "Copied Antigravity configuration"
    fi
    
    # Copy performance optimization
    if [ -f "$PROJECT_ROOT/config/performance-optimization.yaml" ]; then
        cp "$PROJECT_ROOT/config/performance-optimization.yaml" "$CONFIG_DIR/"
        chmod 0600 "$CONFIG_DIR/performance-optimization.yaml"
        log_success "Copied performance optimization configuration"
    fi
}

# Setup environment variables
setup_environment() {
    log_info "Setting up environment variables..."
    
    local env_file="$CONFIG_DIR/.env"
    
    # Create environment file template
    cat > "$env_file" << 'EOF'
# OpenCode Multi-Account Environment Variables
# ==========================================

# OpenCode API Keys (replace with actual values)
export OPENCODE_API_KEY_1="your-api-key-1-here"
export OPENCODE_API_KEY_2="your-api-key-2-here"
export OPENCODE_API_KEY_3="your-api-key-3-here"
export OPENCODE_API_KEY_4="your-api-key-4-here"
export OPENCODE_API_KEY_5="your-api-key-5-here"
export OPENCODE_API_KEY_6="your-api-key-6-here"
export OPENCODE_API_KEY_7="your-api-key-7-here"
export OPENCODE_API_KEY_8="your-api-key-8-here"

# Antigravity Authentication
export ANTIGRAVITY_CLIENT_ID="your-antigravity-client-id"
export ANTIGRAVITY_CLIENT_SECRET="your-antigravity-client-secret"

# Dashboard Credentials
export DASHBOARD_USERNAME="admin"
export DASHBOARD_PASSWORD="your-secure-password"

# Performance Monitoring
export PROMETHEUS_ENABLED="true"
export GRAFANA_ENABLED="true"
EOF

    chmod 0600 "$env_file"
    log_success "Environment variables template created at $env_file"
    log_warning "Please edit $env_file with your actual credentials"
}

# Setup systemd services
setup_systemd_services() {
    log_info "Setting up systemd services..."
    
    # Check if running as root for system-wide service
    if [ "$EUID" -eq 0 ]; then
        log_info "Installing system-wide systemd services..."
        
        # Rotation monitor service
        cat > "/etc/systemd/system/xnai-opencode-rotation.service" << EOF
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

        cat > "/etc/systemd/system/xnai-opencode-rotation.timer" << EOF
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
        
        log_success "System-wide systemd services installed and started"
    else
        log_info "Installing user systemd services..."
        
        local user_service_dir="$HOME/.config/systemd/user"
        mkdir -p "$user_service_dir"
        
        # Rotation monitor service
        cat > "$user_service_dir/xnai-opencode-rotation.service" << EOF
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

        cat > "$user_service_dir/xnai-opencode-rotation.timer" << EOF
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
        
        log_success "User systemd services installed and started"
    fi
}

# Setup monitoring dashboard
setup_monitoring_dashboard() {
    log_info "Setting up monitoring dashboard..."
    
    # Create dashboard startup script
    cat > "$CONFIG_DIR/start-dashboard.sh" << 'EOF'
#!/bin/bash
# Start the performance monitoring dashboard

CONFIG_DIR="${HOME}/.config/xnai"
source "$CONFIG_DIR/.env"

# Start dashboard server (placeholder - would need actual implementation)
log_info "Starting performance monitoring dashboard on port 8080..."
echo "Dashboard URL: http://localhost:8080"
echo "Username: $DASHBOARD_USERNAME"
echo "Password: [hidden]"

# Placeholder for actual dashboard startup
# python3 -m dashboard.server --port 8080 --config "$CONFIG_DIR/performance-optimization.yaml"
EOF

    chmod +x "$CONFIG_DIR/start-dashboard.sh"
    log_success "Dashboard startup script created"
}

# Validate setup
validate_setup() {
    log_info "Validating setup..."
    
    local validation_errors=0
    
    # Check configuration files
    for config in "opencode-credentials.yaml" "minimax-working-memory.yaml" "working-memory-handoff-protocol.yaml" "antigravity-free-frontier.yaml" "performance-optimization.yaml"; do
        if [ ! -f "$CONFIG_DIR/$config" ]; then
            log_error "Missing configuration file: $config"
            ((validation_errors++))
        fi
    done
    
    # Check environment file
    if [ ! -f "$CONFIG_DIR/.env" ]; then
        log_error "Missing environment file: .env"
        ((validation_errors++))
    fi
    
    # Check systemd service
    if systemctl --user is-active --quiet xnai-opencode-rotation.timer 2>/dev/null || systemctl is-active --quiet xnai-opencode-rotation.timer 2>/dev/null; then
        log_success "Rotation timer is active"
    else
        log_warning "Rotation timer is not active"
    fi
    
    # Validate YAML if python is available
    if command -v python3 &> /dev/null; then
        for config in "opencode-credentials.yaml" "minimax-working-memory.yaml" "working-memory-handoff-protocol.yaml" "antigravity-free-frontier.yaml" "performance-optimization.yaml"; do
            if [ -f "$CONFIG_DIR/$config" ]; then
                if ! python3 -c "import yaml; yaml.safe_load(open('$CONFIG_DIR/$config'))" &> /dev/null; then
                    log_error "Invalid YAML in $config"
                    ((validation_errors++))
                fi
            fi
        done
    fi
    
    if [ $validation_errors -eq 0 ]; then
        log_success "Setup validation completed successfully"
        return 0
    else
        log_error "Setup validation failed with $validation_errors errors"
        return 1
    fi
}

# Display completion summary
display_summary() {
    log_info ""
    log_info "Setup completed successfully!"
    log_info "================================"
    log_info ""
    log_info "Configuration Files:"
    log_info "  - $CONFIG_DIR/opencode-credentials.yaml"
    log_info "  - $CONFIG_DIR/minimax-working-memory.yaml"
    log_info "  - $CONFIG_DIR/working-memory-handoff-protocol.yaml"
    log_info "  - $CONFIG_DIR/antigravity-free-frontier.yaml"
    log_info "  - $CONFIG_DIR/performance-optimization.yaml"
    log_info ""
    log_info "Environment Variables:"
    log_info "  - $CONFIG_DIR/.env (EDIT WITH YOUR CREDENTIALS)"
    log_info ""
    log_info "Next Steps:"
    log_info "1. Edit $CONFIG_DIR/.env with your actual credentials"
    log_info "2. Edit $CONFIG_DIR/opencode-credentials.yaml with your API keys"
    log_info "3. Run: $SCRIPT_DIR/xnai-inject-credentials.sh"
    log_info "4. Start monitoring: $CONFIG_DIR/start-dashboard.sh"
    log_info "5. Monitor rotation: journalctl -u xnai-opencode-rotation.service -f"
    log_info ""
    log_info "Usage Examples:"
    log_info "  # Use working memory with account 1"
    log_info "  XDG_DATA_HOME=/tmp/xnai-opencode-instance-1 opencode chat --model minimax-m2.5-free --json 'Your prompt'"
    log_info ""
    log_info "  # Use Antigravity Opus 4.6"
    log_info "  XDG_DATA_HOME=/tmp/xnai-opencode-instance-1 opencode chat --model 'google/antigravity-claude-opus-4-6-thinking' --json 'Your prompt'"
    log_info ""
    log_info "  # Test all accounts"
    for i in {1..8}; do
        log_info "  XDG_DATA_HOME=/tmp/xnai-opencode-instance-$i opencode chat --json 'test' 2>&1 | head -3"
    done
    log_info ""
    log_info "Log file: $LOG_FILE"
}

# Main execution function
main() {
    local step="${1:-all}"
    
    log_info "Starting OpenCode Multi-Account Setup..."
    log_info "Step: $step"
    log_info "Project Root: $PROJECT_ROOT"
    log_info "Config Directory: $CONFIG_DIR"
    
    # Initialize log file
    mkdir -p "$CONFIG_DIR"
    echo "OpenCode Multi-Account Setup Log - $(date)" > "$LOG_FILE"
    
    case "$step" in
        "dependencies")
            check_dependencies
            ;;
        "config")
            setup_config_directory
            copy_configurations
            ;;
        "environment")
            setup_environment
            ;;
        "services")
            setup_systemd_services
            ;;
        "dashboard")
            setup_monitoring_dashboard
            ;;
        "validate")
            validate_setup
            ;;
        "all")
            check_dependencies
            setup_config_directory
            copy_configurations
            setup_environment
            setup_systemd_services
            setup_monitoring_dashboard
            validate_setup
            display_summary
            ;;
        *)
            log_error "Unknown step: $step"
            log_info "Available steps: dependencies, config, environment, services, dashboard, validate, all"
            exit 1
            ;;
    esac
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi