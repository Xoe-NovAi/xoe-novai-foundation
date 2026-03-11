#!/bin/bash
# 🏙️ Metropolis Prune: Intelligent Session Sculpting
# Purpose: Uses Qwen3-0.6B to summarize old chat sessions and prevent OOM.

QWEN_URL="http://localhost:8000/v1/chat/completions"
MAX_HISTORY_SIZE=50000 # ~50KB threshold for pruning

echo "🏙️  Metropolis Prune: Searching for high-token sessions..."

# Find .history files or chat logs in .gemini/ or storage/instances/
# For this example, we'll look in the default .gemini/history (adjust as needed)
HISTORY_FILE="$HOME/.gemini/history"

if [ ! -f "$HISTORY_FILE" ]; then
    echo "⚠️  No history file found at $HISTORY_FILE. Skipping."
    exit 0
fi

FILE_SIZE=$(stat -c%s "$HISTORY_FILE")

if [ "$FILE_SIZE" -gt "$MAX_HISTORY_SIZE" ]; then
    echo "🔥 History exceeds $MAX_HISTORY_SIZE bytes. Sculpting with Qwen3..."
    
    # Extract the last 5000 chars for summarization (simplified)
    TAIL_CONTENT=$(tail -c 5000 "$HISTORY_FILE" | jq -Rs .)
    
    # Prompt Qwen for a high-density summary
    RESPONSE=$(curl -s -X POST "$QWEN_URL" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"qwen3-0.6b-q6_k\",
            \"messages\": [
                {\"role\": \"system\", \"content\": \"You are a High-Density Sculpting Agent. Summarize the following technical chat history into a dense, procedural summary for a Memory Bank.\"},
                {\"role\": \"user\", \"content\": $TAIL_CONTENT}
            ]
        }")
    
    SUMMARY=$(echo "$RESPONSE" | jq -r '.choices[0].message.content')
    
    if [ ! -z "$SUMMARY" ] && [ "$SUMMARY" != "null" ]; then
        echo "✅ Summary generated. Pruning history..."
        # Backup and replace (Surgical)
        cp "$HISTORY_FILE" "${HISTORY_FILE}.bak"
        echo "--- SEMANTIC SUMMARY ---" > "$HISTORY_FILE"
        echo "$SUMMARY" >> "$HISTORY_FILE"
        echo "--- END SUMMARY ---" >> "$HISTORY_FILE"
        echo "🏙️  Session sculpted successfully."
    else
        echo "❌ Qwen summarization failed. Is the llama_server running on port 8000?"
    fi
else
    echo "✅ History size is within limits ($FILE_SIZE bytes)."
fi
