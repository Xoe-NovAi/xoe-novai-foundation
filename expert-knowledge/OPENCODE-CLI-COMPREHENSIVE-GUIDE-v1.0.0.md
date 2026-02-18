# OpenCode CLI Comprehensive Guide for XNAi Foundation

**Version**: 1.0.0 | **Date**: 2026-02-18 | **Status**: ACTIVE

---

## Executive Summary

OpenCode CLI is the **primary AI coding agent** for XNAi Foundation. It provides:
- 75+ LLM provider support via Models.dev
- Native GitHub Copilot integration (requires PAID subscription)
- 5 built-in free models (rate-limited)
- Local model support via Ollama, LM Studio, llama.cpp
- Beautiful TUI with Vim-like keybindings

---

## Free vs Paid Model Access

### OpenCode Built-in Free Models

| Model | Context | Output | Best For | Rate Limit |
|-------|---------|--------|----------|------------|
| `opencode/big-pickle` | 200K | 128K | General coding, reasoning | Shared pool |
| `opencode/glm-5-free` | 200K | 128K | Logic, structured tasks | Shared pool |
| `opencode/gpt-5-nano` | 400K | 128K | Speed, large context | Shared pool |
| `opencode/kimi-k2.5-free` | 262K | 128K | Research, large context | Shared pool |
| `opencode/minimax-m2.5-free` | 204K | 128K | Speed, efficiency | Shared pool |

**Rate Limit Behavior**: 
- Limits are based on **overall OpenCode usage**, not individual
- Can hit rate limits randomly during peak times
- GLM models most commonly rate-limited
- Big Pickle and MiniMax most reliable

### GitHub Copilot Models (Requires PAID Subscription)

**Important**: GitHub Copilot Free tier does NOT work with OpenCode. Requires:
- Copilot Pro ($19/month)
- Copilot Pro+ ($39/month) 
- Copilot Business ($19/user/month)
- Copilot Enterprise ($39/user/month)

| Model | Context | Best For |
|-------|---------|----------|
| `github-copilot/claude-opus-4.6` | 200K | Complex reasoning |
| `github-copilot/claude-sonnet-4.6` | 200K | Balanced tasks |
| `github-copilot/claude-haiku-4.5` | 200K | Fast responses |
| `github-copilot/gpt-5.1-codex` | 200K | Code generation |
| `github-copilot/gpt-5.2-codex` | 200K | Advanced coding |
| `github-copilot/gemini-3-pro-preview` | 1M | Large context |
| `github-copilot/grok-code-fast-1` | 200K | xAI coding |

---

## Provider Configuration

### Built-in Providers (No Setup Required)

1. **OpenCode Free**: Just use `opencode` - no auth needed
2. **GitHub Copilot**: Run `/connect` → GitHub Copilot → Device login

### Adding Google Gemini

**Option 1: Via Google AI Studio (Free Tier)**
```bash
# OpenCode doesn't directly support Google AI Studio
# Use via OpenRouter instead
opencode auth login
# Select OpenRouter
# Enter OpenRouter API key
# Use openrouter/google/gemini-3-flash-preview:free
```

**Option 2: Via Google Vertex AI (Enterprise)**
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
export GOOGLE_CLOUD_PROJECT=your-project-id
export VERTEX_LOCATION=global
opencode
# Then run /models to select Gemini
```

### Adding HuggingFace

```bash
# 1. Create token at huggingface.co/settings/tokens
#    Needs "Make calls to Inference Providers" permission

# 2. Connect
opencode auth login
# Select Hugging Face
# Enter token (starts with hf_)

# 3. Select model
# In OpenCode TUI: /models
# Models available: kimi-k2-instruct, glm-4.6, qwen models, etc.
```

### Adding OpenRouter

```bash
# 1. Get API key from openrouter.ai/keys

# 2. Connect
opencode auth login
# Select OpenRouter
# Enter API key

# 3. Access 31+ free models including:
# - stepfun/step-3.5-flash:free (256K context)
# - deepseek/deepseek-r1-0528:free (164K context)
# - arcee-ai/trinity-large-preview:free (131K context)
# - qwen/qwen3-coder:free (262K context)
# - meta-llama/llama-3.3-70b-instruct:free (128K context)
```

### Adding Local Models (Ollama)

**Prerequisites**: Install Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:7b
ollama pull mistral:7b
```

**Configure OpenCode** (`~/.config/opencode/opencode.json`):
```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "qwen2.5:7b": {
          "name": "Qwen 2.5 7B (local)",
          "limit": {
            "context": 32768,
            "output": 4096
          }
        },
        "mistral:7b": {
          "name": "Mistral 7B (local)",
          "limit": {
            "context": 32768,
            "output": 4096
          }
        }
      }
    }
  }
}
```

---

## Local RAG Integration

### Connecting XNAi RAG to OpenCode

The XNAi Foundation Stack provides local RAG via Qdrant and FAISS. To connect:

**Option 1: Via MCP Server (Recommended)**

OpenCode supports MCP (Model Context Protocol). Create an MCP server that connects to XNAi's Qdrant:

```json
// .opencode/opencode.json
{
  "$schema": "https://opencode.ai/config.json",
  "mcpServers": {
    "xnai-rag": {
      "command": "python",
      "args": ["mcp-servers/xnai-rag/server.py"],
      "env": {
        "QDRANT_URL": "http://localhost:6333"
      }
    }
  }
}
```

**Option 2: Via HTTP Tool**

OpenCode can make HTTP requests to XNAi's search endpoint:
```
GET http://localhost:8000/search?q=query&limit=5
```

**Option 3: File-based Context**

Add documents to OpenCode's context:
```
@file internal_docs/00-system/MASTER-PROJECT-INDEX-v1.0.0.md
@file memory_bank/activeContext.md
```

---

## Multi-Agent Orchestration

### XNAi Agent Bus + OpenCode

The XNAi Agent Bus can orchestrate multiple OpenCode instances:

```python
# Example: Spawn multiple OpenCode agents
import subprocess
import asyncio

async def spawn_opencode_agent(task, model, session_id):
    """Spawn an OpenCode instance for a specific task"""
    proc = await asyncio.create_subprocess_exec(
        "opencode",
        "--model", model,
        "--session", session_id,
        "--prompt", task,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    return proc

# Orchestrate parallel agents
agents = await asyncio.gather(
    spawn_opencode_agent("Research X", "opencode/kimi-k2.5-free", "research-1"),
    spawn_opencode_agent("Implement Y", "opencode/big-pickle", "impl-1"),
    spawn_opencode_agent("Review Z", "opencode/glm-5-free", "review-1"),
)
```

### Model Selection by Task

| Task | Recommended Model | Reason |
|------|-------------------|--------|
| Complex reasoning | `opencode/big-pickle` | Best reasoning quality |
| Research/synthesis | `opencode/kimi-k2.5-free` | 262K context |
| Fast prototyping | `opencode/minimax-m2.5-free` | Speed optimized |
| Code generation | `opencode/gpt-5-nano` | Code-focused |
| Structured tasks | `opencode/glm-5-free` | Logic specialist |
| Offline work | Ollama `qwen2.5:7b` | No network needed |

---

## Recommended Configuration for XNAi

### Primary Config (`~/.config/opencode/opencode.json`)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "big-pickle",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "qwen2.5:7b": {
          "name": "Qwen 2.5 7B (local)",
          "limit": { "context": 32768, "output": 4096 }
        }
      }
    }
  },
  "rules": [
    "Read memory_bank/activeContext.md before starting any task",
    "Read memory_bank/progress.md to understand current phase",
    "Follow the XNAi coding standards in .clinerules/",
    "Update memory_bank after significant changes"
  ]
}
```

### Project Config (`.opencode/opencode.json`)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "big-pickle",
  "skills": [
    "memory-bank-loader",
    "phase-validator",
    "semantic-search"
  ],
  "agents": [
    "xnai-architect",
    "xnai-researcher"
  ]
}
```

---

## Usage Limits Summary

| Model Source | Free Tier | Paid Tier | Notes |
|--------------|-----------|-----------|-------|
| OpenCode built-in | 5 models | N/A | Rate-limited by global usage |
| GitHub Copilot | ❌ No | ✅ Pro+ required | $19-39/month |
| OpenRouter | 31+ models | Pay per token | Free tier available |
| HuggingFace | Limited | Pay per token | Free tier available |
| Google Gemini | Via Vertex only | Via Vertex | Needs GCP account |
| Ollama (local) | ✅ Unlimited | N/A | Your hardware |

---

## Quick Commands

```bash
# Start OpenCode
opencode

# Start with specific model
opencode --model opencode/kimi-k2.5-free

# Continue last session
opencode --continue

# List available models
opencode models

# Check authentication
opencode auth list

# Add provider
opencode auth login

# View usage stats
opencode stats
```

---

## Troubleshooting

### Rate Limit Errors
- **Symptom**: "Rate limit exceeded" or "Overloaded"
- **Solution**: Switch to a different free model, or use local Ollama

### Permission Errors
- **Symptom**: Can't write files
- **Solution**: Check file permissions, OpenCode inherits your user permissions

### MCP Server Not Connecting
- **Symptom**: Skills not loading
- **Solution**: Check `mcpServers` config, ensure Python dependencies installed

### Ollama Not Found
- **Symptom**: "Connection refused" for local models
- **Solution**: Run `ollama serve` in a separate terminal

---

**Document Status**: ACTIVE
**Last Updated**: 2026-02-18
**Maintained By**: XNAi Foundation Team
