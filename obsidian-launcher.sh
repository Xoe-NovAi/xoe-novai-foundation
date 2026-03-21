#!/bin/bash
# Obsidian AppImage Launcher with vault support
# This script handles AppArmor issues and vault location

APPIMAGE_PATH="/home/arcana-novai/Documents/Xoe-NovAi/local-machine-apps/Obsidian-1.12.4.AppImage"
VAULT_PATH="/home/arcana-novai/Documents/Xoe-NovAi/local-machine-apps"

# Check if AppImage exists
if [ ! -f "$APPIMAGE_PATH" ]; then
    echo "Error: Obsidian AppImage not found at $APPIMAGE_PATH"
    exit 1
fi

# Make AppImage executable if needed
chmod +x "$APPIMAGE_PATH"

# Launch with AppArmor workaround and vault
# Use --no-sandbox as a fallback for AppArmor issues
"$APPIMAGE_PATH" --no-sandbox --folder "$VAULT_PATH"
