#!/bin/bash
# Xoe-NovAi Safe Log Viewer
# Prevents Gemini CLI crashes by capping log output

SERVICE=$1
LINES=${2:-100}

if [ -z "$SERVICE" ]; then
    echo "Usage: ./scripts/safe_logs.sh <service_name> [lines]"
    echo "Active services:"
    podman ps --format "{{.Names}}"
    exit 1
fi

podman logs --tail "$LINES" "$SERVICE"
