#!/bin/bash
# xnai-dispatcher.sh - Universal Omega Stack Dispatcher
# Supports: gemini, opencode, copilot, cline
# Usage: ln -sf xnai-dispatcher.sh xnai-gemini-dispatcher.sh

set -u

# 1. Resolve OMEGA_ROOT and Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OMEGA_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
source "${SCRIPT_DIR}/xnai-resolve-domain.sh"

# 2. Detect Tool Name
TOOL_CMD="$(basename "$0")"
TOOL="${TOOL_CMD#xnai-}"
TOOL="${TOOL%-dispatcher.sh}"

# 3. Handle Domain Resolution
DOMAIN_FLAG=""
if [[ $# -gt 0 && "$1" =~ ^-- ]]; then
    DOMAIN_FLAG="$1"
    if resolve_domain "$DOMAIN_FLAG"; then
        shift
    else
        # Fallback to general if flag not a domain
        resolve_domain "--general"
    fi
else
    resolve_domain "--general"
fi

# 4. Load Tool Configuration
CONF_FILE="${SCRIPT_DIR}/dispatcher.d/${TOOL}.conf"
if [[ -f "$CONF_FILE" ]]; then
    source "$CONF_FILE"
else
    echo "Error: Configuration for tool '$TOOL' not found at $CONF_FILE"
    exit 1
fi

# 5. Set Isolation Environment
set_tool_env

# 6. Tool-Specific Hooks
if declare -f pre_hook > /dev/null; then
    pre_hook
fi

# 7. Gemini-Specific API Key Rotation (If applicable)
if [[ "$TOOL" == "gemini" ]]; then
    # Use Cline's oauth_credentials if available, otherwise fallback to .env
    ENV_FILE="${OMEGA_ROOT}/config/.env"
    ROTATION_STATE="${HOME}/.local/state/xnai/gemini_rotation_idx"
    mkdir -p "$(dirname "$ROTATION_STATE")"

    if [[ -f "$ENV_FILE" ]]; then
        source "$ENV_FILE"
        KEYS=()
        while IFS='=' read -r key value; do
            if [[ "$key" =~ ^GEMINI_API_KEY_[0-9]+$ ]]; then
                KEYS+=("${value//\"/}")
            fi
        done < "$ENV_FILE"

        if [[ ${#KEYS[@]} -gt 0 ]]; then
            IDX=$(cat "$ROTATION_STATE" 2>/dev/null || echo 0)
            export GEMINI_API_KEY="${KEYS[$((IDX % ${#KEYS[@]}))]}"
            echo $(( (IDX + 1) % ${#KEYS[@]} )) > "$ROTATION_STATE"
        fi
    fi
fi

# 8. Pulse Filter (Output scrubbing)
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}[Omega] Routing ${TOOL} to Domain: ${CYAN}${DOMAIN_NAME}${BLUE} (Instance ${INSTANCE_ID})${NC}"

# 9. Execute Original Binary
if [[ "$*" == *"--format json"* ]]; then
    # Headless pulse active
    "$TOOL_BINARY" "$@" | grep --line-buffered -E '"type":"(step_start|tool_use|error|step_finish)"' | sed -u "s/.*\"type\":\"\([^\"]*\)\".*/[Pulse: $TOOL: \1]/"
else
    "$TOOL_BINARY" "$@"
fi
