#!/bin/bash
# gemini-rotate.sh: Isolated Gemini CLI execution
# ============================================
# Provides 1-to-1 account isolation for the Gemini CLI.
# Usage: ./gemini-rotate.sh <INSTANCE_ID> [ARGS...]

INSTANCE_ID=$1
shift

if [[ -z "$INSTANCE_ID" ]]; then
    echo "Usage: $0 <INSTANCE_ID> [ARGS...]"
    echo "Example: ./gemini-rotate.sh 1 --prompt 'hello'"
    exit 1
fi

# Load environment
ENV_FILE="${XNAI_CONFIG_DIR:-${HOME}/.config/xnai}/.env"
if [[ -f "$ENV_FILE" ]]; then
    source "$ENV_FILE"
else
    echo "Error: .env file not found at $ENV_FILE"
    exit 1
fi

# Determine Key
KEY_VAR="GEMINI_API_KEY_${INSTANCE_ID}"
KEY_VAL="${!KEY_VAR}"

if [[ -z "$KEY_VAL" ]]; then
    echo "Error: $KEY_VAR not found in .env"
    exit 1
fi

# Set isolation and key
# Fallback to /tmp if INSTANCE_ROOT is not set in environment
INSTANCE_ROOT="${INSTANCE_ROOT:-/tmp/xnai-instances}"
export GEMINI_CLI_HOME="${INSTANCE_ROOT}/instance-${INSTANCE_ID}/gemini-cli"
export GEMINI_API_KEY="$KEY_VAL"

# Ensure data directory exists
mkdir -p "$GEMINI_CLI_HOME"

# Execute
gemini "$@"
