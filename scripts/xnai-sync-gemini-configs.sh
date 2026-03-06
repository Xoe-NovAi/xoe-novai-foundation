#!/bin/bash
# ============================================================================
# XNAi Gemini Configuration Sync (v1.0.0)
# ============================================================================
# Purpose: Synchronizes settings, instructions, and MCP configs across all 
# 8 isolated expert instances to ensure a consistent UX.

MASTER_CONFIG_DIR="${HOME}/.config/gemini"
# Fallback to /tmp if INSTANCE_ROOT is not set in environment
INSTANCE_ROOT="${INSTANCE_ROOT:-/tmp/xnai-instances}"

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

echo "🔗 Syncing Master Gemini Configurations to 8 Expert Domains..."

for i in {1..8}; do
    TARGET_DIR="${INSTANCE_ROOT}/instance-${i}/gemini-cli/.gemini"
    mkdir -p "$TARGET_DIR"
    
    # 1. Sync Settings (Context usage, theme, etc.)
    if [[ -f "${MASTER_CONFIG_DIR}/settings.json" ]]; then
        ln -sf "${MASTER_CONFIG_DIR}/settings.json" "${TARGET_DIR}/settings.json"
    fi
    
    # 2. Sync MCP Configurations
    if [[ -f "${MASTER_CONFIG_DIR}/mcp_config.json" ]]; then
        ln -sf "${MASTER_CONFIG_DIR}/mcp_config.json" "${TARGET_DIR}/mcp_config.json"
    fi
    
    # 3. Sync Custom Instructions
    if [[ -f "${MASTER_CONFIG_DIR}/instructions.md" ]]; then
        ln -sf "${MASTER_CONFIG_DIR}/instructions.md" "${TARGET_DIR}/instructions.md"
    fi
    
    echo "✅ Instance-${i} synchronized."
done

echo "🎉 All 8 Expert Domains are now unified with Master Settings."
