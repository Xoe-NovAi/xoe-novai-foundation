#!/bin/bash
# Wrapper script to run memory-bank MCP server with correct environment

# Get the absolute path to omega-stack root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OMEGA_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Set PYTHONPATH to include the omega-stack directory so app module can be found
export PYTHONPATH="${OMEGA_ROOT}:${OMEGA_ROOT}/app:${PYTHONPATH:-}"

# Source .env file for Redis password and other secrets
# Filter out readonly vars (UID, EUID, etc.) that cause bash errors
if [ -f "${OMEGA_ROOT}/.env" ]; then
    while IFS= read -r line; do
        # Skip comments and empty lines
        [[ -z "$line" || "$line" =~ ^# ]] && continue
        # Extract variable name
        varname="${line%%=*}"
        # Skip bash readonly variables
        case "$varname" in
            UID|EUID|PPID|BASHPID|BASH_*|SHELLOPTS|BASHOPTS|GROUPS) continue ;;
        esac
        export "$line" 2>/dev/null || true
    done < "${OMEGA_ROOT}/.env"
fi

# Change to omega-stack directory so relative imports work
cd "${OMEGA_ROOT}"

# Run the server
PYTHON="${OMEGA_ROOT}/.venv_mcp/bin/python3"
if [[ ! -x "$PYTHON" ]]; then
    echo "ERROR: Python venv not found at $PYTHON" >&2
    echo "Run: python3 -m venv ${OMEGA_ROOT}/.venv_mcp && ${PYTHON} -m pip install -e ${OMEGA_ROOT}/mcp-servers/memory-bank-mcp/" >&2
    exit 1
fi
exec "$PYTHON" "$SCRIPT_DIR/server.py" "$@"
