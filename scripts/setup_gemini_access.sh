#!/bin/bash
# ============================================================================
# Gemini Access Setup Script
# ============================================================================
# Purpose: Help users in restricted regions get Gemini --arch working
# Usage: ./scripts/setup_gemini_access.sh

set -e

echo "🚀 Gemini Access Setup for Restricted Regions"
echo "=============================================="

# Function to test API key
test_api_key() {
    local api_key="$1"
    local provider="$2"
    
    echo "Testing $provider API key..."
    
    case "$provider" in
        "gemini")
            # Test Gemini API
            curl -s -H "Authorization: Bearer $api_key" \
                 -H "Content-Type: application/json" \
                 "https://generativelanguage.googleapis.com/v1/models?key=$api_key" \
                 -o /dev/null || return 1
            ;;
        "openai")
            # Test OpenAI API
            curl -s -H "Authorization: Bearer $api_key" \
                 "https://api.openai.com/v1/models" \
                 -o /dev/null || return 1
            ;;
        "groq")
            # Test Groq API
            curl -s -H "Authorization: Bearer $api_key" \
                 "https://api.groq.com/openai/v1/models" \
                 -o /dev/null || return 1
            ;;
    esac
    return 0
}

# Function to configure API key
configure_api_key() {
    local api_key="$1"
    local provider="$2"
    
    echo "Configuring $provider API key..."
    
    # Update .env file
    sed -i "s/GEMINI_API_KEY=.*/GEMINI_API_KEY=$api_key/" .env
    sed -i "s/YOUR_ACTUAL_GEMINI_API_KEY_HERE/$api_key/" secrets/gemini_api_key.txt
    
    echo "✅ $provider API key configured!"
}

# Function to setup local models
setup_local_models() {
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
    cat >> .env << EOF

# Local Model Configuration
LOCAL_MODEL_PATH=ollama
OLLAMA_MODEL=gemma:2b
EOF

    echo "✅ Local models configured!"
}

# Main setup menu
echo ""
echo "Choose your setup option:"
echo "1) Use existing Gemini API key from account 2"
echo "2) Set up Groq API (recommended alternative)"
echo "3) Set up OpenAI API"
echo "4) Set up local models (no API key needed)"
echo "5) Test current configuration"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo "🔑 Setting up Gemini API key..."
        read -s -p "Enter your Gemini API key from account 2: " gemini_key
        echo ""
        
        if test_api_key "$gemini_key" "gemini"; then
            configure_api_key "$gemini_key" "Gemini"
            echo "🎉 Gemini --arch should now work!"
        else
            echo "❌ Invalid Gemini API key. Please try again."
        fi
        ;;
    2)
        echo "🔗 Setting up Groq API..."
        echo "Please sign up at: https://console.groq.com/"
        echo "Then get your API key from the dashboard."
        read -s -p "Enter your Groq API key: " groq_key
        echo ""
        
        if test_api_key "$groq_key" "groq"; then
            configure_api_key "$groq_key" "Groq"
            echo "🎉 Groq API configured! Gemini --arch will use Groq as fallback."
        else
            echo "❌ Invalid Groq API key. Please try again."
        fi
        ;;
    3)
        echo "🔗 Setting up OpenAI API..."
        echo "Please sign up at: https://platform.openai.com/"
        echo "Then get your API key from the dashboard."
        read -s -p "Enter your OpenAI API key: " openai_key
        echo ""
        
        if test_api_key "$openai_key" "openai"; then
            configure_api_key "$openai_key" "OpenAI"
            echo "🎉 OpenAI API configured! Gemini --arch will use OpenAI as fallback."
        else
            echo "❌ Invalid OpenAI API key. Please try again."
        fi
        ;;
    4)
        setup_local_models
        echo "🎉 Local models configured! Gemini --arch will use local models."
        ;;
    5)
        echo "🧪 Testing current configuration..."
        
        # Test current Gemini key
        current_key=$(grep "GEMINI_API_KEY=" .env | cut -d'=' -f2)
        if [[ "$current_key" != "YOUR_ACTUAL_GEMINI_API_KEY_HERE" ]] && [[ -n "$current_key" ]]; then
            if test_api_key "$current_key" "gemini"; then
                echo "✅ Current Gemini API key is working!"
            else
                echo "❌ Current Gemini API key is not working."
            fi
        else
            echo "⚠️  No valid Gemini API key configured."
        fi
        
        # Check for alternative providers
        if grep -q "OPENAI_API_KEY=" .env && grep -q "your_openai_key_here" .env; then
            echo "⚠️  OpenAI API key not configured."
        fi
        
        if grep -q "GROQ_API_KEY=" .env && grep -q "your_groq_key_here" .env; then
            echo "⚠️  Groq API key not configured."
        fi
        
        # Check for local models
        if command -v ollama &> /dev/null; then
            echo "✅ Ollama is installed."
            if ollama list | grep -q "gemma:2b"; then
                echo "✅ Gemma 2B model is available."
            else
                echo "⚠️  Gemma 2B model not found. Run: ollama pull gemma:2b"
            fi
        else
            echo "⚠️  Ollama not installed. Run: curl -fsSL https://ollama.com/install.sh | sh"
        fi
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎯 Testing Gemini --arch..."
echo "Run this command to test: ./scripts/xnai-gemini-dispatcher.sh --architect echo 'Hello World'"
echo ""
echo "📖 For more help, see: docs/GEMINI_ACCESS_GUIDE.md"