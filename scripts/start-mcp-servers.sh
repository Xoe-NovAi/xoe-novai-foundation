#!/bin/bash
# Start all 4 Omega MCP servers for Copilot CLI integration
# Usage: ./scripts/start-mcp-servers.sh [options]
#   --foreground    Keep servers in foreground (for debugging)
#   --logs          Show logs from all servers
#   --check         Only verify servers are running

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_BIN="${PROJECT_ROOT}/.venv_mcp/bin/python3"
LOGS_DIR="${PROJECT_ROOT}/.logs/mcp-servers"
PID_DIR="${PROJECT_ROOT}/.server.pids"

# Create directories
mkdir -p "$LOGS_DIR" "$PID_DIR"

# Source environment
cd "$PROJECT_ROOT"
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

FOREGROUND=0
SHOW_LOGS=0
CHECK_ONLY=0

while [[ $# -gt 0 ]]; do
    case $1 in
        --foreground) FOREGROUND=1; shift ;;
        --logs) SHOW_LOGS=1; shift ;;
        --check) CHECK_ONLY=1; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

echo "🚀 Omega MCP Server Launcher"
echo "======================================"
echo "Servers: memory-bank, github, stats, websearch"
echo "Logs: $LOGS_DIR"
echo "Pids: $PID_DIR"
echo ""

# Function to start a server
start_server() {
    local name=$1
    local server_path=$2
    local log_file="$LOGS_DIR/${name}.log"
    local pid_file="$PID_DIR/${name}.pid"
    
    echo -n "Starting $name... "
    
    if [ -f "$pid_file" ]; then
        local old_pid=$(cat "$pid_file")
        if kill -0 "$old_pid" 2>/dev/null; then
            echo "✓ Already running (PID $old_pid)"
            return 0
        fi
    fi
    
    if [ $FOREGROUND -eq 1 ]; then
        echo "✓ Starting in foreground"
        "$VENV_BIN" "$server_path" 2>&1 | tee -a "$log_file"
    else
        "$VENV_BIN" "$server_path" > "$log_file" 2>&1 &
        local new_pid=$!
        echo "$new_pid" > "$pid_file"
        sleep 1
        
        # Check if process is still running
        if kill -0 "$new_pid" 2>/dev/null; then
            echo "✓ Started (PID $new_pid)"
        else
            echo "✗ Failed to start (see $log_file)"
            cat "$log_file"
            return 1
        fi
    fi
}

# Function to check server status
check_server() {
    local name=$1
    local pid_file="$PID_DIR/${name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "✓ $name is running (PID $pid)"
            return 0
        else
            echo "✗ $name is not running (stale PID $pid)"
            rm -f "$pid_file"
            return 1
        fi
    else
        echo "✗ $name is not running (no PID file)"
        return 1
    fi
}

if [ $CHECK_ONLY -eq 1 ]; then
    echo "Status Check:"
    echo "============="
    check_server "memory-bank" || true
    check_server "github" || true
    check_server "stats" || true
    check_server "websearch" || true
    exit 0
fi

# Start all servers
start_server "memory-bank" "mcp-servers/memory-bank-mcp/server.py"
start_server "github" "mcp-servers/xnai-github/server.py"
start_server "stats" "mcp-servers/xnai-stats-mcp/server.py"
start_server "websearch" "mcp-servers/xnai-websearch/server.py"

echo ""
echo "✓ All servers started successfully!"
echo ""
echo "Next steps:"
echo "  1. Launch Copilot CLI: copilot"
echo "  2. Load MCP config: /mcp"
echo "  3. Verify servers: /mcp list"
echo "  4. Test tools: Use any memory-bank, github, stats, or websearch tools"
echo ""
echo "View logs:"
echo "  tail -f $LOGS_DIR/*.log"
echo ""
echo "Stop servers:"
echo "  pkill -f 'mcp-servers'"
echo ""

if [ $SHOW_LOGS -eq 1 ]; then
    echo "Recent log output:"
    for log in "$LOGS_DIR"/*.log; do
        if [ -f "$log" ]; then
            echo ""
            echo "=== $(basename "$log") ==="
            tail -5 "$log"
        fi
    done
fi
