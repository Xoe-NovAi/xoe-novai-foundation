#!/bin/bash
# ============================================================================
# Omega Stack Config Bootstrapper (Sovereign & Portable)
# ============================================================================
# Purpose: Ensures ~/.config/xnai/ is correctly set up and follows protocols.
# Supports: XNAI_CONFIG_DIR environment variable for custom locations.

set -euo pipefail

# Configuration
DEFAULT_CONFIG_DIR="${HOME}/.config/xnai"
CONFIG_DIR="${XNAI_CONFIG_DIR:-$DEFAULT_CONFIG_DIR}"
TEMPLATE_DIR="$(pwd)/config/templates"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔱 Omega Stack Bootstrapper${NC}"
echo -e "Target Directory: ${CONFIG_DIR}"

# 1. Create directory structure
mkdir -p "$CONFIG_DIR"
mkdir -p "$CONFIG_DIR/backups"

# 2. Handle .env file
if [[ ! -f "$CONFIG_DIR/.env" ]]; then
    echo -e "${YELLOW}Creating initial .env...${NC}"
    # Use the normalized .env structure we created earlier
    cat > "$CONFIG_DIR/.env" << EOF
# ==========================================================================
# XNAi Foundation - Sovereign Environment Configuration
# ==========================================================================

# Antigravity Authentication (Google OAuth)
export ANTIGRAVITY_CLIENT_ID=""
export ANTIGRAVITY_CLIENT_SECRET=""

# Provider API Keys (8 slots per provider)
$(for p in OPENCODE SAMBANOVA SILICONFLOW GROQ CEREBRAS TOGETHER OPENROUTER HUGGINGFACE; do
    for i in {1..8}; do
        echo "export ${p}_API_KEY_${i}=\"\""
    done
    echo ""
done)
EOF
    echo -e "${GREEN}✅ Created .env with 8 slots for all providers.${NC}"
else
    echo -e "${GREEN}✅ .env already exists.${NC}"
fi

# 3. Set secure permissions
chmod 700 "$CONFIG_DIR"
chmod 600 "$CONFIG_DIR/.env"
echo -e "${GREEN}✅ Secure permissions applied (chmod 600).${NC}"

# 4. Create symlink from project root for convenience (optional)
# if [[ ! -L ".xnai_config" ]]; then
#    ln -s "$CONFIG_DIR" ".xnai_config"
# fi

echo -e "${BLUE}Bootstrap complete. Please edit ${CONFIG_DIR}/.env with your keys.${NC}"
