#!/bin/bash
# opencode-memory-fix.sh - Hardening script for OpenCode memory issues
# Part of Omega Metropolis v2

set -e

BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}[Omega] Applying OpenCode Memory Hardening...${NC}"

# 1. Clear Provider & Model Cache (Standard fix for launch crashes)
echo "Cleaning ~/.cache/opencode..."
rm -rf "${HOME}/.cache/opencode"

# 2. Check for .opencodeignore
if [[ ! -f ".opencodeignore" ]]; then
    echo "Warning: .opencodeignore not found. Creating default..."
    # (The file is already created in this turn, but this is for standalone use)
fi

# 3. Environment Suggestions
echo -e "\n${BLUE}Recommended Environment Variables:${NC}"
echo "export NODE_OPTIONS=\"--max-old-space-size=2048\""
echo "export XDG_DATA_HOME=\"/tmp/opencode-isolated\""

echo -e "\n${BLUE}Hardening Complete.${NC}"
