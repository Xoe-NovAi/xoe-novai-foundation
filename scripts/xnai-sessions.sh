#!/bin/bash
LIMIT=${1:-10}
echo -e "\033[0;36m🏙️  Omega Metropolis: Recent Sessions (BardRY)\033[0m"
find "$INSTANCE_ROOT" -name "session-*.json" -printf "%T+ %p\n" 2>/dev/null | sort -r | head -n "$LIMIT"
