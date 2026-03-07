#!/bin/bash
# Wrapper script to run memory-bank MCP server with correct environment

set -e

# Get the absolute path to omega-stack root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OMEGA_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Set PYTHONPATH to include the omega-stack directory so app module can be found
export PYTHONPATH="${OMEGA_ROOT}:${PYTHONPATH:-}"

# Change to omega-stack directory so relative imports work
cd "${OMEGA_ROOT}"

# Run the server
exec /home/arcana-novai/Documents/Xoe-NovAi/omega-stack/.venv_mcp/bin/python3 "$SCRIPT_DIR/server.py" "$@"
