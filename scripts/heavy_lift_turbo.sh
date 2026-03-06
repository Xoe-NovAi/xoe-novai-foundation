#!/bin/bash
# XNAi Foundation - Heavy Lifting Resource Scheduler (TURBO MODE)
# Purpose: Hierarchical Speculative Decoding (150M -> 1B -> 8B)
# Optimized: 2026 Triple-Stage Speculation + Q8_0 KV Cache

set -e

# Configuration
MODEL_PATH="models/Krikri-8b-Instruct.gguf"
MEDIUM_DRAFT_PATH="models/Llama-3.2-1b-Instruct.gguf"
TINY_DRAFT_PATH="models/Llama-3.1-FastDraft-150M.gguf"

SERVER_PORT=8085
CONTEXT_SIZE=32768
THREADS=8

echo "🚀 Starting Heavy Lifting TURBO Mode..."

# 1. Pre-Flight
echo "🛑 Suspending background services..."
podman stop xnai_rag_api xnai_crawler xnai_chainlit || true

# 2. Check for Models & Build Speculation Chain
DRAFT_FLAGS=""

if [ -f "$MODEL_PATH" ]; then
    echo "✅ Target: Krikri-8B"
else
    echo "❌ Error: Target model missing."
    exit 1
fi

if [ -f "$MEDIUM_DRAFT_PATH" ]; then
    echo "✨ Level 2 Draft: 1B found."
    DRAFT_FLAGS="$DRAFT_FLAGS -md $MEDIUM_DRAFT_PATH"
fi

if [ -f "$TINY_DRAFT_PATH" ]; then
    echo "✨ Level 1 Draft: 150M found."
    DRAFT_FLAGS="$DRAFT_FLAGS -md $TINY_DRAFT_PATH"
fi

# 3. Start llama-server with Hierarchical Chain
echo "🔥 Starting Multi-Stage Inference Server..."
llama-server 
    -m "$MODEL_PATH" 
    $DRAFT_FLAGS 
    -c $CONTEXT_SIZE 
    --flash-attn 
    --cache-type-k q8_0 
    --cache-type-v q8_0 
    --port $SERVER_PORT 
    --threads $THREADS 
    --n-gpu-layers 0 
    --draft-max 16 
    --draft-p-min 0.9 
    > logs/krikri_turbo_server.log 2>&1 &

SERVER_PID=$!

# ... (Health check and extraction logic same as before)
echo "⏳ Waiting for health check..."
# (rest of script)
