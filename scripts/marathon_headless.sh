#!/bin/bash
# marathon_headless.sh
# ====================
# Runs the Gemini CLI in headless mode for Autonomous Marathons.
# Monitors 'scripts/amr_steering.md' for user input.

SESSION_ID=$(uuidgen)
LOG_FILE="logs/amr_${SESSION_ID}.log"
STEERING_FILE="scripts/amr_steering.md"

echo "💎 STARTING JEM MARATHON (HEADLESS)"
echo "Session ID: $SESSION_ID"
echo "Log File: $LOG_FILE"
echo "Steering File: $STEERING_FILE"

# Initialize steering file if missing
if [ ! -f "$STEERING_FILE" ]; then
    echo "**Current Directive**: Initializing Marathon..." > "$STEERING_FILE"
fi

# Function to read steering directive
get_directive() {
    grep "**Current Directive**" "$STEERING_FILE" | cut -d':' -f2 | xargs
}

# Main Loop
while true; do
    DIRECTIVE=$(get_directive)
    echo "[$(date '+%H:%M:%S')] Current Directive: $DIRECTIVE" | tee -a "$LOG_FILE"
    
    # Run Gemini CLI with the directive (mocked for script)
    # In real usage, this would pipe the directive to the CLI process or Agent Bus
    # python -m gemini_cli --task "$DIRECTIVE" --headless >> "$LOG_FILE" 2>&1
    
    # Heartbeat
    python app/XNAi_rag_app/core/xnai_heartbeat.py >> "$LOG_FILE" 2>&1
    
    sleep 60 # Check every minute
done
