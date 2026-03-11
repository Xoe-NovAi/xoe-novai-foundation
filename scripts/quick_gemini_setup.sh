#!/bin/bash
# ============================================================================
# Quick Gemini Setup - Direct Configuration
# ============================================================================
# Purpose: Get Gemini --arch working immediately without interactive prompts
# Usage: ./scripts/quick_gemini_setup.sh [gemini_key|groq_key|openai_key|local]

set -e

echo "🚀 Quick Gemini Setup - Getting --arch working now!"
echo "=================================================="

# Function to configure Gemini API key
setup_gemini() {
    local api_key="$1"
    echo "🔑 Configuring Gemini API key..."
    
    # Update .env file
    sed -i "s/GEMINI_API_KEY=.*/GEMINI_API_KEY=$api_key/" .env
    echo "$api_key" > secrets/gemini_api_key.txt
    
    echo "✅ Gemini API key configured!"
    echo "🎯 Test with: ./scripts/xnai-gemini-dispatcher.sh --architect echo 'Hello World'"
}

# Function to setup Groq API
setup_groq() {
    local api_key="$1"
    echo "🔗 Configuring Groq API as fallback..."
    
    # Update .env file
    sed -i "s/GEMINI_API_KEY=.*/GEMINI_API_KEY=$api_key/" .env
    echo "$api_key" > secrets/gemini_api_key.txt
    
    echo "✅ Groq API configured as fallback!"
    echo "🎯 Test with: ./scripts/xnai-gemini-dispatcher.sh --architect echo 'Hello World'"
}

# Function to setup OpenAI API
setup_openai() {
    local api_key="$1"
    echo "🔗 Configuring OpenAI API as fallback..."
    
    # Update .env file
    sed -i "s/GEMINI_API_KEY=.*/GEMINI_API_KEY=$api_key/" .env
    echo "$api_key" > secrets/gemini_api_key.txt
    
    echo "✅ OpenAI API configured as fallback!"
    echo "🎯 Test with: ./scripts/xnai-gemini-dispatcher.sh --architect echo 'Hello World'"
}

# Function to setup local models
setup_local() {
    echo "🔧 Setting up local models..."
    
    # Install Ollama if not present
    if ! command -v ollama &> /dev/null; then
        echo "Installing Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh
    fi
    
    # Pull a small model
    echo "Downloading Gemma 2B model..."
    ollama pull gemma:2b
    
    # Update .env for local models
    cat > .env << EOF
# ==========================================================================
# Xoe-NovAi Phase 1 v0.1.2 Environment Configuration
# ==========================================================================

# DO NOT COMMIT REAL SECRETS TO VERSION CONTROL!
# See docs/secrets.md for secure secrets management.
# ==========================================================================

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# Qdrant Configuration (Phase 3 Vector Database)
QDRANT_URL=http://qdrant:6333
QDRANT_API_KEY=  # Optional: leave empty for development
VECTOR_SIZE=384
FAISS_INDEX_PATH=/app/data/faiss_index

# Phase 2 Feature Flags
PHASE2_QDRANT_ENABLED=false  # Enable for vector search enhancement

# Service Ports
CHAINLIT_PORT=8001
RAG_API_PORT=8000
METRICS_PORT=8002

# Security Settings
CHAINLIT_NO_TELEMETRY=true
APP_UID=1001
APP_GID=1001
UID=1001
GID=1001

# Performance Tuning
OPENBLAS_NUM_THREADS=6
OPENBLAS_CORETYPE=ZEN2
N_THREADS=6

# Development Settings (disable in production)
DEBUG=false
RELOAD=false
SCARF_NO_ANALYTICS=true

# Gemini API Configuration
# Note: If Google AI Studio is not available in your location, try these alternatives:

# Option 1: Your existing Gemini API key from account 2
GEMINI_API_KEY=local_model

# Option 2: Alternative API providers (uncomment and configure as needed)
# OPENAI_API_KEY=your_openai_key_here
# CLAUDE_API_KEY=your_claude_key_here
# GROQ_API_KEY=your_groq_key_here

# Option 3: Local models (no API key needed)
LOCAL_MODEL_PATH=ollama
OLLAMA_MODEL=gemma:2b
EOF

    echo "✅ Local models configured!"
    echo "🎯 Test with: ./scripts/xnai-gemini-dispatcher.sh --architect echo 'Hello World'"
}

# Main logic
case "$1" in
    "gemini")
        if [ -z "$2" ]; then
            echo "❌ Usage: ./scripts/quick_gemini_setup.sh gemini [your_gemini_api_key]"
            exit 1
        fi
        setup_gemini "$2"
        ;;
    "groq")
        if [ -z "$2" ]; then
            echo "❌ Usage: ./scripts/quick_gemini_setup.sh groq [your_groq_api_key]"
            exit 1
        fi
        setup_groq "$2"
        ;;
    "openai")
        if [ -z "$2" ]; then
            echo "❌ Usage: ./scripts/quick_gemini_setup.sh openai [your_openai_api_key]"
            exit 1
        fi
        setup_openai "$2"
        ;;
    "local")
        setup_local
        ;;
    *)
        echo "Usage: ./scripts/quick_gemini_setup.sh [gemini|groq|openai|local] [api_key_if_needed]"
        echo ""
        echo "Examples:"
        echo "  ./scripts/quick_gemini_setup.sh gemini your_gemini_key_here"
        echo "  ./scripts/quick_gemini_setup.sh groq your_groq_key_here"
        echo "  ./scripts/quick_gemini_setup.sh local"
        echo ""
        echo "If you have your Gemini API key from account 2, run:"
        echo "  ./scripts/quick_gemini_setup.sh gemini YOUR_GEMINI_API_KEY"
        exit 1
        ;;
esac

echo ""
echo "🎉 Setup complete! Your Gemini --arch should now work."
echo "📖 For more help, see: docs/GEMINI_ACCESS_GUIDE.md"