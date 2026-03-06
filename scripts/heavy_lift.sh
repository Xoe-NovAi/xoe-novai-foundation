#!/bin/bash
# XNAi Foundation - Heavy Lifting Resource Scheduler
# Purpose: Dedicate system resources to Krikri-8b for GraphRAG Extraction.
# Optimized: 2026 Speculative Decoding + KV Cache Quantization

set -e

# Configuration
MODEL_PATH="models/Krikri-8b-Instruct.gguf"
DRAFT_MODEL_PATH="models/Llama-3.1-FastDraft-150M.gguf"
SERVER_PORT=8085
CONTEXT_SIZE=32768
THREADS=8  # Optimized for Ryzen 5700U physical cores

echo "🚀 Starting Heavy Lifting Mode for Gnosis Engine..."

# 1. Pre-Flight: Stop non-essential services to free RAM
echo "🛑 Suspending background services..."
podman stop xnai_rag_api xnai_crawler xnai_chainlit || true

# 2. Check for Models
if [ ! -f "$MODEL_PATH" ]; then
    echo "⚠️ Target Model not found at $MODEL_PATH"
    podman start xnai_rag_api xnai_crawler xnai_chainlit || true
    exit 1
fi

if [ ! -f "$DRAFT_MODEL_PATH" ]; then
    echo "⚠️ Draft Model not found at $DRAFT_MODEL_PATH"
    echo "Speculative decoding will be disabled. Speedup: 1.0x"
    DRAFT_FLAG=""
else
    echo "✨ Draft Model found. Enabling Speculative Decoding. Speedup: ~2.0x"
    DRAFT_FLAG="-md $DRAFT_MODEL_PATH"
fi

# 3. Start llama-server (Krikri)
echo "🔥 Starting Krikri-8b Inference Server..."
# Optimized for 2026: Flash Attention + Q8_0 KV Cache
llama-server \
    -m "$MODEL_PATH" \
    $DRAFT_FLAG \
    -c $CONTEXT_SIZE \
    --flash-attn \
    --cache-type-k q8_0 \
    --cache-type-v q8_0 \
    --port $SERVER_PORT \
    --threads $THREADS \
    --n-gpu-layers 0 \
    > logs/krikri_server.log 2>&1 &

SERVER_PID=$!
echo "   PID: $SERVER_PID"

# Wait for server to be ready
echo "⏳ Waiting for server health check..."
for i in {1..30}; do
    if curl -s http://localhost:$SERVER_PORT/health > /dev/null; then
        echo "✅ Krikri Server is UP!"
        break
    fi
    sleep 2
done

# 4. Execute Gnosis Graph Extraction
echo "🧪 Running Gnosis Graph Extraction..."
python3 scripts/graph_extractor.py --file library/manuals/redis.md --db-uri "$DATABASE_URL" || echo "⚠️ Extraction encountered errors"

# 5. Cleanup & Restore
echo "🧹 Stopping Krikri Server..."
if ps -p $SERVER_PID > /dev/null; then
    kill $SERVER_PID || true
fi

echo "🔄 Restoring Foundation Stack..."
podman start xnai_rag_api xnai_crawler xnai_chainlit

echo "✅ Heavy Lifting Complete. System restored."
