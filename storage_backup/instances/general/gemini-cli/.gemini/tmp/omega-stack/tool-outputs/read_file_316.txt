#!/bin/bash
# ============================================================================
# XNAi Foundation Stack - Permissions Remediation Script
# ============================================================================
# Purpose: PERMANENTLY fix the recurring permissions issues
# Issue: Containers run as UID 1001, but data dirs have wrong ownership
# Solution: Create data dirs with correct ownership BEFORE container start
# 
# Usage: ./scripts/fix-permissions.sh [--reset]
#   --reset: Delete all data and start fresh (WARNING: destroys data)
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== XNAi Permissions Fix Script ===${NC}"

# Define the correct UID/GID from .env or default
APP_UID=${APP_UID:-1001}
APP_GID=${APP_GID:-1001}

# Load from .env if exists
if [ -f ".env" ]; then
    export $(grep -E "^APP_UID|^APP_GID" .env | xargs)
fi

echo -e "Target UID:GID = ${YELLOW}${APP_UID}:${APP_GID}${NC}"

# Check if --reset flag provided
RESET_MODE=false
if [ "$1" == "--reset" ]; then
    RESET_MODE=true
    echo -e "${RED}RESET MODE: All data will be deleted!${NC}"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Aborted."
        exit 1
    fi
fi

# Stop all containers first
echo "Stopping containers..."
podman-compose down 2>/dev/null || docker-compose down 2>/dev/null || true

# Function to fix directory ownership
fix_directory() {
    local dir=$1
    local target_uid=$2
    local target_gid=$3
    local needs_reset=$4
    
    if [ -d "$dir" ]; then
        current_uid=$(stat -c '%u' "$dir" 2>/dev/null || echo "unknown")
        current_gid=$(stat -c '%g' "$dir" 2>/dev/null || echo "unknown")
        
        if [ "$RESET_MODE" = true ] || [ "$needs_reset" = true ]; then
            echo -e "${YELLOW}Resetting $dir${NC}"
            sudo rm -rf "$dir"
            sudo mkdir -p "$dir"
            sudo chown -R ${target_uid}:${target_gid} "$dir"
            sudo chmod -R 755 "$dir"
        elif [ "$current_uid" != "$target_uid" ] || [ "$current_gid" != "$target_gid" ]; then
            echo -e "${YELLOW}Fixing ownership for $dir (current: $current_uid:$current_gid, target: $target_uid:$target_gid)${NC}"
            sudo chown -R ${target_uid}:${target_gid} "$dir"
            sudo chmod -R 755 "$dir"
        else
            echo -e "${GREEN}$dir ownership correct${NC}"
        fi
    else
        echo -e "${YELLOW}Creating $dir${NC}"
        sudo mkdir -p "$dir"
        sudo chown -R ${target_uid}:${target_gid} "$dir"
        sudo chmod -R 755 "$dir"
    fi
}

# Fix Redis data directory
echo ""
echo "=== Redis ==="
fix_directory "data/redis" $APP_UID $APP_GID true

# Fix Qdrant data directory
echo ""
echo "=== Qdrant ==="
fix_directory "data/qdrant" $APP_UID $APP_GID true

# Fix Consul data directory (runs as root)
echo ""
echo "=== Consul ==="
if [ -d "data/consul" ]; then
    current_uid=$(stat -c '%u' "data/consul" 2>/dev/null || echo "unknown")
    if [ "$current_uid" != "0" ]; then
        echo -e "${YELLOW}Fixing Consul ownership (needs root)${NC}"
        sudo chown -R root:root data/consul
        sudo chmod -R 755 data/consul
    else
        echo -e "${GREEN}data/consul ownership correct (root)${NC}"
    fi
else
    sudo mkdir -p data/consul
    sudo chown -R root:root data/consul
    sudo chmod -R 755 data/consul
fi

# Fix Vikunja data directory
echo ""
echo "=== Vikunja ==="
fix_directory "data/vikunja" $APP_UID $APP_GID false

# Fix FAISS index directory
echo ""
echo "=== FAISS ==="
if [ -d "data/faiss_index" ]; then
    sudo chown -R $APP_UID:$APP_GID data/faiss_index
    echo -e "${GREEN}data/faiss_index ownership set${NC}"
fi

# Fix IAM database
echo ""
echo "=== IAM Database ==="
if [ -f "data/iam_agents.db" ]; then
    sudo chown $APP_UID:$APP_GID data/iam_agents.db
    echo -e "${GREEN}data/iam_agents.db ownership set${NC}"
fi

# NOTE: Rootless Podman uses UID mapping (subuid/subgid).
# Container UID 1001 maps to host UID = 1001 + subuid_offset.
# We set host ownership to 1001 because docker-compose.yml sets
# user: "${APP_UID:-1001}:${APP_GID:-1001}"

# Fix Caddy logs
echo ""
echo "=== Caddy ==="
fix_directory "logs/caddy" $APP_UID $APP_GID false

# Fix Curation Worker
echo ""
echo "=== Curation Worker ==="
fix_directory "data/curations" $APP_UID $APP_GID false
fix_directory "logs/curations" $APP_UID $APP_GID false

# Fix Prometheus metrics
echo ""
echo "=== Prometheus ==="
fix_directory "data/prometheus-multiproc" $APP_UID $APP_GID false

# Fix Cache
echo ""
echo "=== Cache ==="
fix_directory "data/cache" $APP_UID $APP_GID false

# Fix Library and Knowledge (read-only OK, but containers need access)
echo ""
echo "=== Library & Knowledge ==="
if [ -d "library" ]; then
    sudo chown -R $APP_UID:$APP_GID library
    echo -e "${GREEN}library ownership set${NC}"
fi
if [ -d "knowledge" ]; then
    sudo chown -R $APP_UID:$APP_GID knowledge
    echo -e "${GREEN}knowledge ownership set${NC}"
fi

# Fix Vikunja PostgreSQL (runs as postgres user UID 999 inside container)
echo ""
echo "=== Vikunja PostgreSQL ==="
if [ -d "data/vikunja/db" ]; then
    # Use podman unshare to handle rootless UID mapping correctly for postgres (999)
    echo -e "${YELLOW}Setting ownership for Vikunja DB via podman unshare (UID 999)${NC}"
    podman unshare chown -R 999:999 data/vikunja/db || \
    sudo chown -R 999:999 data/vikunja/db 2>/dev/null || \
    sudo chown -R $APP_UID:$APP_GID data/vikunja/db
    echo -e "${GREEN}data/vikunja/db ownership processed${NC}"
fi

echo ""
echo -e "${GREEN}=== Permissions Fixed ===${NC}"
echo ""
echo "To start services: make up"
echo "To verify: podman ps"
