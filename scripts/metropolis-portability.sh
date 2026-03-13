#!/bin/bash
# ============================================================================
# Omega Metropolis Portability Tool (v1.0.0)
# ============================================================================
# Purpose: Manages the lifecycle of isolated expert instances.
# Features: Checkpoint (Persist /tmp to disk), Restore (Load disk to /tmp).

set -euo pipefail

# Fallback to /tmp if INSTANCE_ROOT is not set in environment
INSTANCE_ROOT="${INSTANCE_ROOT:-/tmp/xnai-instances}"
STORAGE_DIR="/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/storage/instances"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

usage() {
    echo "Usage: $0 {checkpoint|restore}"
    echo "  checkpoint: Save current /tmp instances to persistent storage."
    echo "  restore:    Load persistent instances into /tmp for execution."
    exit 1
}

if [[ $# -lt 1 ]]; then usage; fi

case "$1" in
    checkpoint)
        echo -e "${CYAN}💾 Checkpointing Metropolis Instances to persistent storage...${NC}"
        mkdir -p "$STORAGE_DIR"
        for i in {1..8}; do
            if [[ -d "${INSTANCE_ROOT}/instance-${i}" ]]; then
                echo "📦 Archiving Instance ${i}..."
                # Use rsync for efficiency, preserving permissions and symlinks
                rsync -av --delete "${INSTANCE_ROOT}/instance-${i}/" "${STORAGE_DIR}/instance-${i}/"
            fi
        done
        echo -e "${GREEN}✅ Checkpoint complete. All 8 domains persisted to ${STORAGE_DIR}${NC}"
        ;;
        
    restore)
        echo -e "${CYAN}🔄 Restoring Metropolis Instances to /tmp execution area...${NC}"
        mkdir -p "$INSTANCE_ROOT"
        for i in {1..8}; do
            if [[ -d "${STORAGE_DIR}/instance-${i}" ]]; then
                echo "🚀 Deploying Instance ${i}..."
                rsync -av --delete "${STORAGE_DIR}/instance-${i}/" "${INSTANCE_ROOT}/instance-${i}/"
            fi
        done
        # Ensure proper permissions after restore
        chmod -R 700 "$INSTANCE_ROOT"
        echo -e "${GREEN}✅ Restore complete. Metropolis is ready for execution.${NC}"
        ;;
        
    *)
        usage
        ;;
esac
