#!/bin/bash
# ============================================================================
# XNAi Gemini Configuration Sync (v1.0.0)
# ============================================================================
# Purpose: Synchronizes settings, instructions, and MCP configs across all 
# 8 isolated expert instances to ensure a consistent UX.

MASTER_CONFIG_DIR="${HOME}/.config/gemini"
# Fallback to persistent storage if INSTANCE_ROOT is not set in environment
INSTANCE_ROOT="${INSTANCE_ROOT:-${HOME}/Documents/Xoe-NovAi/omega-stack/storage/instances}"

# Ensure master exists
mkdir -p "$MASTER_CONFIG_DIR"

# --- Hardening: Create defaults if missing ---
if [[ ! -f "${MASTER_CONFIG_DIR}/mcp_config.json" ]]; then
    echo "📦 Creating default master MCP config..."
    cat > "${MASTER_CONFIG_DIR}/mcp_config.json" << 'EOF'
{
  "mcpServers": {
    "memory-bank": {
      "command": "python3",
      "args": ["/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/mcp-servers/memory-bank-mcp/server.py"]
    }
  }
}
EOF
fi

if [[ ! -f "${MASTER_CONFIG_DIR}/settings.json" ]]; then
    echo "⚙️ Creating default master settings..."
    cat > "${MASTER_CONFIG_DIR}/settings.json" << 'EOF'
{
  "ui": {
    "showContextUsage": true,
    "showTokenPercentage": true
  }
}
EOF
fi
# ---------------------------------------------

# Master Overrides
MASTER_SETTINGS_FILE="${MASTER_CONFIG_DIR}/settings.json"
export GEMINI_CLI_SYSTEM_SETTINGS_PATH="${MASTER_SETTINGS_FILE}"

echo "🔗 Syncing Master Gemini Configurations to 9 Expert Domains (0-8)..."

# 1. Sync Instance 0 (General / Oversoul)
TARGET_DIR_0="${INSTANCE_ROOT}/general/gemini-cli/.gemini"
mkdir -p "$TARGET_DIR_0"
for f in settings.json mcp_config.json instructions.md; do
    if [[ -f "${MASTER_CONFIG_DIR}/$f" ]]; then
        ln -sf "${MASTER_CONFIG_DIR}/$f" "${TARGET_DIR_0}/$f"
    fi
done
echo "✅ Instance-0 (General) synchronized."

# 2. Sync Instances 1-8 (Facets)
for i in {1..8}; do
    TARGET_DIR="${INSTANCE_ROOT}/facets/instance-${i}/gemini-cli/.gemini"
    mkdir -p "$TARGET_DIR"
    
    for f in settings.json mcp_config.json instructions.md; do
        if [[ -f "${MASTER_CONFIG_DIR}/$f" ]]; then
            ln -sf "${MASTER_CONFIG_DIR}/$f" "${TARGET_DIR}/$f"
        fi
    done
    
    echo "✅ Instance-${i} synchronized."
done

echo "🎉 All Expert Domains are now unified with Master Settings."
