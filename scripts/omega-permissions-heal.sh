#!/bin/bash
# ============================================================================
# 🔱 OMEGA STACK: PERMISSIONS HEALER (Epoch 2)
# ============================================================================
# Purpose: Maintain the 4-Layer Permissions Model (UID 1000 + recursive ACLs)
# Integrated with Sonnet IMPL-07 4-Layer Resolution.
# ----------------------------------------------------------------------------
# Layer 1: Ownership correction (chown -R 1000:1000)
# Layer 2: Recursive ACLs for existing and future files (setfacl -R -d -m u:1000:rwx)
# Layer 3: Container identity preservation (userns=keep-id) - Handled in Compose
# Layer 4: Auto-healing (Repairing Mask Drift from chmod)
# ============================================================================

set -e

# Target UID (arcana-novai)
TARGET_UID=1000
# Container UID 999 maps to 100999 in default rootless namespace
SUBUID=100999
ROOT_DIR="/home/arcana-novai/Documents/Xoe-NovAi/omega-stack"

# Check if we are in the root directory
if [ "$(pwd)" != "$ROOT_DIR" ]; then
    echo "⚠️ Not in root directory ($ROOT_DIR). Switching..."
    cd $ROOT_DIR
fi

echo "🔱 Starting Omega Stack Permissions Healing (Sonnet-Aligned)..."

# Layer 1: Ownership
echo "  [Layer 1] Healing Ownership (chown)..."
sudo chown -R $TARGET_UID:$TARGET_UID .

# Layer 2: ACLs (Current & Default)
echo "  [Layer 2] Healing ACLs (setfacl)..."
# We grant both the host user (1000) and the mapped container user (100999) rwx access
sudo setfacl -R -m u:$TARGET_UID:rwx,u:$SUBUID:rwx,m::rwx .
sudo setfacl -R -d -m u:$TARGET_UID:rwx,u:$SUBUID:rwx,m::rwx .

# Layer 4: Mask Drift Repair
echo "  [Layer 4] Repairing Mask Drift (chmod correction)..."
# Force mask to rwx recursively to override any chmod 600/644 drift
sudo setfacl -R -m m::rwx .

# Special case: Vikunja Postgres (UID 999 mapping)
if [ -d "data/vikunja/db" ]; then
    echo "  [Special] Healing Vikunja DB ownership..."
    if command -v podman &> /dev/null; then
        podman unshare chown -R 999:999 data/vikunja/db 2>/dev/null || true
    fi
fi

echo "🔱 Permissions Healing Complete. Omega Stack is Rigid. 🔱"
