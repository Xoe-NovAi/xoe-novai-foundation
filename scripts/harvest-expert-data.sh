#!/bin/bash
# Omega Metropolis Hierarchical Harvester (v3.0)
# Unified Sovereignty: Gemini, OpenCode, SambaNova, and Shared Souls

INSTANCE_ROOT="/tmp/xnai-instances"
GNOSIS_INGESTOR="app/XNAi_rag_app/services/ingest_library.py"

echo "🏯 Harvesting Knowledge from the Metropolis Matrix..."

for i in {1..8}; do
    echo "🔍 Syncing Expert Cluster $i..."
    
    # 1. Gemini Prime History (Strategy)
    GEMINI_HISTORY="${INSTANCE_ROOT}/instance-${i}/gemini-cli/.gemini/tmp/omega-stack/chats"
    if [[ -d "$GEMINI_HISTORY" ]]; then
        python3 "$GNOSIS_INGESTOR" --mode chats --chat-path "$GEMINI_HISTORY" --label "gemini_prime"
    fi
    
    # 2. OpenCode / Sub-Expert History (Implementation)
    # Using the new isolated XDG_DATA_HOME path
    OC_STORAGE="${INSTANCE_ROOT}/instance-${i}/opencode/.local/share/opencode/project"
    if [[ -d "$OC_STORAGE" ]]; then
        # OpenCode stores history in project slugs (global or project-specific)
        python3 "$GNOSIS_INGESTOR" --mode chats --chat-path "$OC_STORAGE" --label "opencode_subexpert"
    fi
    
    # 3. Local Validation & Shared Soul (Evolution)
    SHARED_SOUL="${INSTANCE_ROOT}/instance-${i}/shared_soul.md"
    if [[ -f "$SHARED_SOUL" ]]; then
        python3 "$GNOSIS_INGESTOR" --mode file --file-path "$SHARED_SOUL" --label "expert_soul"
    fi
done

echo "✅ Metropolis Hierarchical Matrix Synchronized into Gnosis Engine."
