#!/bin/bash
# ODES: Antigravity Multi-Account Rotator
# ======================================
# Purpose: Swaps Antigravity sessions without IDE session wipe.

ACCOUNT_ID=$1
SESSION_ROOT="$HOME/.config/antigravity-sessions"
IDE_CONFIG="$HOME/.config/Antigravity/all tokens"

if [[ -z "$ACCOUNT_ID" ]]; then
    echo "Usage: ./xnai-antigravity-rotate.sh <ACCOUNT_ID>"
    exit 1
fi

# 1. Freeze Current Session
mkdir -p "$SESSION_ROOT/current"
rsync -av --delete "$IDE_CONFIG/" "$SESSION_ROOT/current/"

# 2. Swap to Target Account
if [[ -d "$SESSION_ROOT/account-$ACCOUNT_ID" ]]; then
    rsync -av --delete "$SESSION_ROOT/account-$ACCOUNT_ID/" "$IDE_CONFIG/"
    echo "✅ Switched to Antigravity Account $ACCOUNT_ID"
else
    echo "❌ Account $ACCOUNT_ID not found in $SESSION_ROOT"
fi
