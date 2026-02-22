#!/bin/bash
PROJECT_ROOT="/home/arcana-novai/Documents/xnai-foundation"
cd "$PROJECT_ROOT"

echo "🚀 Launching Project P-010 Phase A Audit via Gemini CLI..."

# Read the task file as the prompt
PROMPT=$(cat "$PROJECT_ROOT/memory_bank/strategies/TIER2-DISCOVERY-AUDIT-TASK.md")

# Execute Gemini CLI
# Note: Using -p for prompt, output will be captured
/home/arcana-novai/.nvm/versions/node/v25.3.0/bin/gemini -p "$PROMPT"
