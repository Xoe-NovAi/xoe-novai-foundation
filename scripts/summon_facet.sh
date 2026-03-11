#!/bin/bash
# ============================================================================
# XNAi Facet Summoner (v0.1.0)
# ============================================================================
# Purpose: Spawns a full, persistent Gemini CLI instance for a specific Facet.
#          Ensures unique Souls and persistent memory per agent.
# ============================================================================

FACET_ID=$1
PROMPT=$2

if [ -z "$FACET_ID" ]; then
    echo "Usage: $0 <facet_number_1_to_8> \"Your prompt here\""
    exit 1
fi

INSTANCE_DIR="/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/storage/instances/facets/instance-$FACET_ID"

if [ ! -d "$INSTANCE_DIR" ]; then
    echo "❌ Error: Facet $FACET_ID directory not found at $INSTANCE_DIR"
    exit 1
fi

# Export instance-specific home for Gemini CLI
export GEMINI_CLI_HOME="$INSTANCE_DIR/gemini-cli"
export PYTHONPATH="/home/arcana-novai/Documents/Xoe-NovAi/omega-stack:$PYTHONPATH"

# --- AUTHENTICATION & MODEL HARDENING ---
# Clear ALL potentially conflicting keys and models
unset GOOGLE_API_KEY
unset GEMINI_API_KEY
unset OPENAI_API_KEY
unset ANTHROPIC_API_KEY
unset GEMINI_MODEL

# Force the High-Quota Flash Model for all Facets
export GEMINI_MODEL="gemini-2.5-flash-lite"

# Source primary key from the PROJECT .env file
DOTENV_PATH="/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/.env"
if [ -f "$DOTENV_PATH" ]; then
    export GEMINI_API_KEY=$(grep "^GEMINI_API_KEY=" "$DOTENV_PATH" | cut -d'=' -f2)
fi
# --------------------------------

echo "🧙 Summoning Facet $FACET_ID (Archon Mode)..."

MAX_RELAYS=5
COUNT=0

while [ $COUNT -lt $MAX_RELAYS ]; do
    # Check if there are any previous sessions to resume
    SESSION_COUNT=$(ls -1 "$INSTANCE_DIR/gemini-cli/.gemini/chats/" 2>/dev/null | wc -l)
    
    if [ "$SESSION_COUNT" -gt 0 ]; then
        echo "🔄 Relay $((COUNT+1)): Resuming latest soul session..."
        # We capture output to detect the MAXS_TURNS string
        gemini -r latest --prompt "$PROMPT" 2>&1 | tee /tmp/facet_output.log
    else
        echo "🌱 First Run: Starting new persistent soul session..."
        gemini --prompt "$PROMPT" 2>&1 | tee /tmp/facet_output.log
    fi

    # Check for specific failure patterns
    if grep -q "MAXS_TURNS" /tmp/facet_output.log; then
        echo "⚠️ Interruption detected (MAXS_TURNS). Initiating Relay..."
        COUNT=$((COUNT+1))
        sleep 2
    elif grep -q "Quota exceeded" /tmp/facet_output.log; then
        echo "🛑 QUOTA EXCEEDED: The current account has reached its daily limit."
        exit 42
    elif grep -q "Validation failed" /tmp/facet_output.log; then
        echo "❌ VALIDATION ERROR: The agent definition or settings are invalid."
        exit 1
    else
        echo "✅ Task finished or unknown exit condition."
        break
    fi
done

if [ $COUNT -eq $MAX_RELAYS ]; then
    echo "🛑 Max Relays reached. Manual intervention required."
fi
