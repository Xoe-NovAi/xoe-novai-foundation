# Gemini Access Guide for Restricted Regions

## Problem
Google AI Studio is not available in US Virgin Islands, preventing direct API key generation.

## Solutions

### Solution 1: Use Existing Account 2 API Key
If you have a Gemini API key from account 2:

1. **Replace the placeholder in `.env`:**
   ```bash
   # Replace this line:
   GEMINI_API_KEY=YOUR_ACTUAL_GEMINI_API_KEY_HERE
   
   # With your actual key:
   GEMINI_API_KEY=your_actual_gemini_api_key_from_account_2
   ```

2. **Replace in `secrets/gemini_api_key.txt`:**
   ```bash
   # Replace the content with your actual API key
   ```

### Solution 2: Alternative API Providers

#### OpenAI API
1. Sign up at [OpenAI](https://platform.openai.com/)
2. Get API key from dashboard
3. Configure in `.env`:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

#### Anthropic Claude API
1. Sign up at [Anthropic](https://docs.anthropic.com/en/docs/quickstart)
2. Get API key from dashboard
3. Configure in `.env`:
   ```bash
   CLAUDE_API_KEY=your_claude_api_key_here
   ```

#### Groq API (Fastest Alternative)
1. Sign up at [Groq](https://console.groq.com/)
2. Get API key from dashboard
3. Configure in `.env`:
   ```bash
   GROQ_API_KEY=your_groq_api_key_here
   ```

### Solution 3: Local Models (No API Key Needed)

#### Option A: Ollama (Recommended)
1. Install Ollama: `curl -fsSL https://ollama.com/install.sh | sh`
2. Pull a model: `ollama pull gemma:2b` or `ollama pull llama2`
3. Configure in `.env`:
   ```bash
   LOCAL_MODEL_PATH=ollama
   OLLAMA_MODEL=gemma:2b
   ```

#### Option B: LM Studio
1. Download LM Studio: https://lmstudio.ai/
2. Load a local model
3. Configure in `.env`:
   ```bash
   LOCAL_MODEL_PATH=http://localhost:1234/v1
   ```

## Testing Your Setup

Once you configure an API key or local model:

```bash
# Test Gemini dispatcher
./scripts/xnai-gemini-dispatcher.sh --architect echo "Hello World"

# Expected output:
# [Omega] Routing to Domain: architect (Instance 1)
# [Success] Should see response from your configured model
```

## Troubleshooting

### Error: "API key not valid"
- Verify your API key is correct
- Check for typos or extra spaces
- Ensure the API key hasn't expired

### Error: "Region not supported"
- Try alternative API providers (OpenAI, Claude, Groq)
- Use local models (Ollama, LM Studio)

### Error: "Rate limit exceeded"
- Check your API plan limits
- Consider using local models for unlimited usage

## Recommended Setup for US Virgin Islands

1. **Primary**: Use your existing Gemini API key from account 2
2. **Backup**: Set up Groq API (fast, generous free tier)
3. **Offline**: Install Ollama with local models

## Quick Start Commands

```bash
# 1. Configure your API key
echo "GEMINI_API_KEY=your_key_here" >> .env

# 2. Test the dispatcher
./scripts/xnai-gemini-dispatcher.sh --architect echo "test"

# 3. If that fails, try alternative providers
# Uncomment and configure in .env:
# OPENAI_API_KEY=your_openai_key
# GROQ_API_KEY=your_groq_key

# 4. For local models, install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma:2b
```

## Support

If you need help:
1. Check the error message in the terminal
2. Verify your API key works on the provider's website
3. Try a different API provider
4. Use local models as fallback