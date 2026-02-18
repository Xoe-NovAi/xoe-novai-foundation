# Cline CLI Model Card v1.0.0

**CLI**: Cline CLI  
**Version**: v2.2.3  
**Free Tier**: Yes (OpenRouter or local models)  
**Last Updated**: 2026-02-17  
**Persona Focus**: Code Implementation, Architecture, Deep Reasoning

---

## Overview

Cline CLI is a multi-provider terminal-based AI assistant supporting multiple model providers through a unified interface. For free tier access, OpenRouter is the recommended provider with 300+ models available.

---

## Free Tier Models

### OpenRouter (RECOMMENDED for XNAi)

**Provider**: OpenRouter  
**Free Tier**: Yes (limited quota, no credit card required)  
**Setup**: Free account at openrouter.ai + API key

| Model | Provider | Context | Best For |
|-------|----------|---------|----------|
| **gpt-4o-mini** | OpenAI | 128k | Fast, balanced |
| **gpt-5-mini** | OpenAI | 128k | Better reasoning |
| **claude-opus-4.6** | Anthropic | 200k | Complex code |
| **claude-sonnet-4.5** | Anthropic | 200k | Balanced (BEST) |
| **qwen-32b-vision** | Alibaba | 32k | Vision tasks |
| **llama-3.3-70b** | Meta | 128k | Fast reasoning |
| **mistral-large** | Mistral | 128k | Code generation |
| ... **300+ more models** | Various | Various | Various |

**Recommended Primary**: claude-sonnet-4.5 (best balance for code)

---

### Local Models (Alternative - ZERO API Cost)

**Provider**: Ollama or LM Studio (local execution)  
**Free Tier**: Yes (completely free, runs on hardware)  
**Setup**: Install Ollama or LM Studio + download model

| Model | Type | Context | Hardware |
|-------|------|---------|----------|
| **llama2-13b** | Open source | 4k | 8GB RAM |
| **mistral-7b** | Open source | 32k | 8GB RAM |
| **neural-chat-7b** | Open source | 32k | 8GB RAM |
| **codeup-13b** | Open source | 4k | 8GB RAM |
| **orca-13b** | Open source | 4k | 8GB RAM |

**Setup** (Ollama example):
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download model
ollama pull mistral

# Use with Cline CLI
cline --provider ollama --model mistral "your prompt"
```

---

## Paid Tier Models

### Direct API Access (Trial/Paid)
- OpenAI (gpt-4-turbo, o1) - $20+ paid
- Anthropic Claude 3 - $20+ paid  
- Google Gemini Pro - $20+ paid

---

## Setup Instructions

### Option 1: OpenRouter (RECOMMENDED)

**Step 1**: Create free account
```bash
# Visit openrouter.ai and sign up (no credit card needed)
# Copy your API key
```

**Step 2**: Configure Cline CLI
```bash
# Set environment variable
export OPENROUTER_API_KEY="sk-or-v1-xxxx..."

# Or create config file
mkdir -p ~/.cline
cat > ~/.cline/config.json << 'EOF'
{
  "provider": "openrouter",
  "apiKey": "sk-or-v1-xxxx...",
  "defaultModel": "claude-sonnet-4.5"
}
EOF
```

**Step 3**: Verify setup
```bash
cline --list-models
cline --test-connection
```

**Step 4**: Use Cline CLI
```bash
# Basic usage
cline "implement a TypeScript utility function"

# With specific model
cline --model claude-opus-4.6 "review this architecture"

# Interactive mode
cline --interactive
```

### Option 2: Local Models (Ollama)

**Step 1**: Install Ollama
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Step 2**: Download a model
```bash
# Mistral (7B, ~4GB download)
ollama pull mistral

# Or: Neural Chat (7B, optimized for code)
ollama pull neural-chat
```

**Step 3**: Configure Cline CLI
```bash
export CLINE_PROVIDER=ollama
export CLINE_BASE_URL=http://localhost:11434/api
export CLINE_DEFAULT_MODEL=mistral
```

**Step 4**: Use with Cline CLI
```bash
cline "implement this feature"
```

**Step 5**: Keep Ollama running (background)
```bash
# Start in background (one time)
ollama serve &

# Or use systemd
systemctl --user enable ollama
systemctl --user start ollama
```

---

## Best Use Cases for XNAi

### claude-sonnet-4.5 (RECOMMENDED - OpenRouter Free)
- **Use**: Main implementation, architecture decisions, code review
- **Why**: Best balance of reasoning, speed, cost (free tier)
- **Strengths**: Excellent code understanding, clean refactoring
- **Limitations**: None significant for free tier
- **Example**:
  ```bash
  export OPENROUTER_API_KEY="sk-or-v1-xxx"
  cline --model claude-sonnet-4.5 "implement async Redis connection pool"
  ```

### claude-opus-4.6 (OpenRouter Free, More Capable)
- **Use**: Complex architecture, hard problems, refinement
- **Why**: Most capable model available on free tier
- **Strengths**: Superior reasoning, handles complex requirements
- **Limitations**: May be slower than Sonnet
- **Example**:
  ```bash
  cline --model claude-opus-4.6 "redesign the entire data pipeline"
  ```

### llama2-13b (Local/Ollama, Zero API Cost)
- **Use**: Local-only work, air-gap requirements, high-frequency calls
- **Why**: Completely free, runs locally, no rate limits
- **Strengths**: Unlimited usage, privacy, offline
- **Limitations**: Lower quality than paid models, needs 8GB RAM
- **Example**:
  ```bash
  export CLINE_PROVIDER=ollama
  cline "generate documentation for this module"
  ```

---

## Integration with XNAi

### Recommended Workflow
```
Agent: Copilot (plans)
  ↓
Agent: Cline (implements via OpenRouter)
  │
  ├─ Primary: claude-sonnet-4.5 (free, balanced)
  ├─ Fallback: claude-opus-4.6 (free, complex tasks)
  └─ Local: mistral via Ollama (zero-cost, air-gap safe)
  ↓
Agent: OpenCode (verifies)
```

### Strengths for XNAi
- ✅ Multi-provider flexibility (OpenRouter covers 300+ models)
- ✅ Free tier available ($0)
- ✅ Local execution option (Ollama - completely offline)
- ✅ Excellent code generation and architecture
- ✅ Large context windows
- ✅ Supports vision models (multimodal)

### Challenges
- ⚠️ OpenRouter free tier has quota limits (monitor usage)
- ⚠️ Local models (Ollama) require hardware
- ⚠️ API key management (store securely)

---

## Commands Reference

```bash
# List available models (OpenRouter)
cline --list-models

# Check configuration
cline --version
cline --info

# Use specific model
cline --model claude-opus-4.6 "Your prompt"

# Interactive mode
cline --interactive

# Set provider
export CLINE_PROVIDER=openrouter
export CLINE_PROVIDER=ollama

# Test connection
cline --test-connection

# Help
cline --help
```

---

## Rate Limits & Quotas

### OpenRouter Free Tier
- **Daily limit**: Varies by model (typically 100+ requests)
- **Concurrent**: 1 request at a time
- **Rate**: Check openrouter.ai/status for current limits
- **Exceeded**: Wait or upgrade to paid

### Local Models (Ollama)
- **Limit**: No limits (runs locally)
- **Speed**: Depends on hardware
- **Concurrent**: Can run multiple models

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key invalid" | Verify key at openrouter.ai, ensure export is correct |
| "Model not available" | Check `cline --list-models`, key may have limited access |
| "Rate limited" | Wait 1 hour or use local model (Ollama) |
| "Connection refused" | Ensure Ollama running: `ollama serve` in another terminal |
| "Out of memory" | Use smaller model (7B instead of 13B) or more RAM |

---

## Cost Comparison

| Option | Cost | Speed | Quality | Setup |
|--------|------|-------|---------|-------|
| OpenRouter free | FREE | Fast | Excellent | 5 min |
| Ollama local | FREE | Slower | Good | 10 min |
| OpenRouter paid | $5-50/mo | Fast | Excellent | 5 min |
| Direct API | $20+/mo | Fast | Excellent | 5 min |

**Recommendation**: Start with OpenRouter free tier, upgrade to paid if needed.

---

## Related Documentation

- `AGENT-CLI-MODEL-MATRIX-v1.0.0.md` - Agent role assignments
- `COPILOT-CLI-MODELS-v1.0.0.md` - Copilot CLI models
- `OPENCODE-CLI-MODELS-v1.0.0.md` - OpenCode CLI models
- `GEMINI-CLI-MODELS-v1.0.0.md` - Gemini CLI models
- `CLI-NOMENCLATURE-GUIDE-v1.0.0.md` - Naming conventions
