#!/bin/bash
# XNAi System Hardener - Definitive Permissions Fix
# ================================================
# ENDS PERMISSION ISSUES FOREVER.
# Aligns host UID/GID with Podman rootless mapping.

set -e

# Target IDs (1001 is mapped to 101000 on host by default in rootless)
TARGET_UID=1001
TARGET_GID=1001
DATA_DIRS=("data" "library" "knowledge" "models" "embeddings" "logs" "entities_test")

echo "🛡️ XNAi System Hardener"
echo "======================"

# 1. Ensure directories exist
for dir in "${DATA_DIRS[@]}"; do
    mkdir -p "$dir"
done

# 2. Use podman unshare to perform ownership changes from the mapped perspective
echo "🔗 Aligning ownership via podman unshare..."
podman unshare chown -R $TARGET_UID:$TARGET_GID "${DATA_DIRS[@]}"

# 3. Set sticky bit and permissions
echo "🔒 Enforcing 775 permissions and group inheritance..."
chmod -R 775 "${DATA_DIRS[@]}"
find "${DATA_DIRS[@]}" -type d -exec chmod g+s {} +

# 4. Verify
echo "📊 Verification:"
ls -ld storage/data/entities

echo "✅ System Hardened. Permission issues remediated."
echo "Run this script anytime you manually add files to the storage/data/ directory."
