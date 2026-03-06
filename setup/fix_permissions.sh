#!/bin/bash
# XNAi Permission Fixer
# =====================
# Aligns host directory permissions with container UID/GID (1001:1001)
# Run this if you encounter "Permission denied" errors in storage/data/ directories.

set -e

# Configuration
TARGET_UID=1001
TARGET_GID=1001
DATA_DIRS=("data" "library" "knowledge" "models" "embeddings" "logs")

echo "🔧 XNAi Permission Fixer"
echo "========================"
echo "Aligning permissions for container user ${TARGET_UID}:${TARGET_GID}..."

# Check for sudo
if [ "$EUID" -ne 0 ]; then 
  echo "⚠️  This script requires sudo to fix ownership."
  SUDO="sudo"
else
  SUDO=""
fi

for dir in "${DATA_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "Processing ./$dir..."
        $SUDO chown -R $TARGET_UID:$TARGET_GID "$dir"
        $SUDO chmod -R 775 "$dir"
    else
        echo "Skipping ./$dir (not found)"
    fi
done

echo "✅ Permissions aligned."
echo "You may now run 'docker-compose up' without permission errors."
