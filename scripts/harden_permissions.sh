#!/bin/bash
# 🔱 Omega Stack: Permissions Hardening Script
# Ensures all core directories are aligned with UID 1000.

PROJECT_ROOT=$(pwd)

echo "🔱 Hardening permissions for $PROJECT_ROOT..."

# Directories to harden
DIRS=(".logs" "memory_bank" "artifacts" "app" "scripts" "data")

for DIR in "${DIRS[@]}"; do
    if [ -d "$DIR" ]; then
        echo "  ✅ Hardening $DIR..."
        # We don't use sudo here, assuming we are already running as the project owner (1000)
        chmod -R 775 "$DIR"
        # Only try to chown if we are not the owner
        find "$DIR" ! -user 1000 -exec chown 1000:1000 {} + 2>/dev/null
    fi
done

echo "✅ Permissions Hardening Complete."
