# OpenCode CLI Comprehensive Guide for XNAi Foundation

**Version**: 1.2.0 | **Date**: 2026-02-18 | **Status**: ACTIVE  
**Sprint 2 Fixes**: asyncio.gather → AnyIO TaskGroup; `--prompt` → `-p`; Added Antigravity auth section  
**Sprint 3 Fixes**: Correct Antigravity model IDs; Ollama → llama-cpp-python; mcpServers schema note; 3-account auth; projectId fix

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

### Antigravity Auth — Free Premium Models ⭐ OPERATIONAL

> **Full guide**: `expert-knowledge/research/ANTIGRAVITY-OAUTH-QUICKGUIDE-2026-02-18.md`  
> **Status**: ✅ 3 accounts authenticated | 2026-02-18

The `opencode-antigravity-auth` npm plugin provides **completely free access** to premium models via Google OAuth. No credit card, no API key — just a Google account.

**Plugin is already configured** in `.opencode/opencode.json`. To authenticate:
```bash
cd /home/arcana-novai/Documents/xnai-foundation
opencode auth login
# → Select Google → OAuth with Google (Antigravity)
# → Leave Project ID blank (press Enter)
# → Open URL in browser → sign in → Allow
# → Copy redirect URL from browser address bar → paste into terminal
```

**Free models unlocked (use `google/` prefix):**

| Model ID | Context | Thinking Variants | Best For |
|----------|---------|-------------------|---------|
| `google/antigravity-gemini-3-pro` | 1M | `low`, `high` | Full codebase analysis |
| `google/antigravity-gemini-3-flash` | 1M | `minimal`→`high` | Fast large-context tasks |
| `google/antigravity-claude-sonnet-4-5` | 200K | — | General dev |
| `google/antigravity-claude-sonnet-4-5-thinking` | 200K | `low`, `max` | Balanced reasoning |
| `google/antigravity-claude-opus-4-5-thinking` | 200K | `low`, `max` | Deep architecture work |
| `google/antigravity-claude-opus-4-6-thinking` | 200K | `low`, `max` | Latest Opus, deep reasoning |

**Usage:**
```bash
# Default model (from opencode.json "model" key)
opencode -p "your task"

# Specific model
opencode -m google/antigravity-claude-sonnet-4-5 -p "fix this bug"

# With extended thinking variant
opencode run "complex task" --model=google/antigravity-claude-opus-4-6-thinking --variant=max

# Gemini 3 Pro — 1M context, ideal for full codebase review
opencode run "review AnyIO compliance" --model=google/antigravity-gemini-3-pro --variant=high
```

**Account management:**
```bash
opencode auth login        # add another account (more quota)
opencode auth status       # check authenticated accounts
# Reset: rm ~/.config/opencode/antigravity-accounts.json && opencode auth login
```

**⚠️ ToS Warning**: Using an established Google account reduces ban risk. Fresh/new accounts frequently flagged.

**XNAi Foundation impact**: Sovereign MC Agent can use Opus 4.6 Thinking for high-value delegations at zero cost.

---

### Adding Local Models (llama-cpp-python) ⭐ PRIMARY LOCAL ENGINE

XNAi Foundation uses **llama-cpp-python** as the primary local inference engine (not Ollama). It runs any GGUF model with Vulkan GPU acceleration on the Ryzen 5700U iGPU.

> **Full protocol**: `expert-knowledge/protocols/LLAMA-CPP-PYTHON-SERVICE-PROTOCOL.md`

**Installation:**
```bash
# With Vulkan support (for Ryzen RDNA2 iGPU)
pip install llama-cpp-python[server] --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/vulkan
```

**Start the server:**
```bash
python -m llama_cpp.server \
  --model /path/to/your-model.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  --n_ctx 32768 \
  --n_gpu_layers -1 \
  --verbose False
```

**OpenCode config** (already in `.opencode/opencode.json`):
```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "llama-cpp": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "llama-cpp-python (local sovereign)",
      "options": {
        "baseURL": "http://localhost:8080/v1"
      },
      "models": {
        "local": {
          "name": "Local GGUF Model",
          "limit": { "context": 32768, "output": 4096 }
        }
      }
    }
  }
}
```

**Usage:**
```bash
# Start server (Terminal 1), then:
opencode -m llama-cpp/local -p "your task"
```

---

## Local RAG Integration

### Connecting XNAi RAG to OpenCode

The XNAi Foundation Stack provides local RAG via Qdrant and FAISS. To connect:

**Option 1: Via MCP Server (Recommended)**

> ⚠️ **SCHEMA NOTE**: `"mcpServers"` is **NOT a valid key** in `opencode.json` — it causes `Configuration is invalid: Unrecognized keys` error. MCP servers for OpenCode are configured in **Cline's MCP settings** (`~/.config/VSCodium/.../cline_mcp_settings.json`), which registers them globally for all tools. The three XNAi MCP servers (`xnai-agentbus`, `xnai-vikunja`, `xnai-rag`) are already registered there.

To add new MCP servers that OpenCode can use, edit Cline's MCP settings, NOT opencode.json.

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

The XNAi Agent Bus can orchestrate multiple OpenCode instances.

> ⚠️ **AnyIO Policy**: NEVER use `asyncio.gather` or `asyncio.create_subprocess_exec`.  
> Always use `anyio.create_task_group` and `anyio.run_process`.

```python
# Example: Spawn multiple OpenCode agents (AnyIO-compliant)
import anyio

async def spawn_opencode_agent(
    task: str, model: str, session_id: str
) -> dict:
    """
    Spawn an OpenCode instance for a specific task.
    Uses anyio.run_process — NOT asyncio.create_subprocess_exec.
    Uses -p flag — NOT --prompt (archived syntax).
    """
    result = await anyio.run_process(
        [
            "opencode",
            "--model", model,
            "--session", session_id,
            "-q",        # suppress spinner
            "-p", task,  # non-interactive prompt (NOT --prompt, NOT --print)
        ],
        check=False,
    )
    return {
        "session_id": session_id,
        "model": model,
        "status": "completed" if result.returncode == 0 else "failed",
        "output": result.stdout.decode("utf-8", errors="replace"),
    }

# Orchestrate parallel agents with AnyIO TaskGroup (NOT asyncio.gather)
results: dict[str, dict] = {}

async def _run_research():
    results["research"] = await spawn_opencode_agent(
        "Research X", "opencode/kimi-k2.5-free", "research-1"
    )

async def _run_impl():
    results["impl"] = await spawn_opencode_agent(
        "Implement Y", "opencode/big-pickle", "impl-1"
    )

async def _run_review():
    results["review"] = await spawn_opencode_agent(
        "Review Z", "opencode/glm-5-free", "review-1"
    )

async with anyio.create_task_group() as tg:
    tg.start_soon(_run_research)
    tg.start_soon(_run_impl)
    tg.start_soon(_run_review)

# results now has all three completed sessions
```

**Key AnyIO rules for OpenCode orchestration:**
- `anyio.run_process(cmd, check=False)` — runs subprocess, captures stdout/stderr
- `anyio.create_task_group()` — structured concurrency (replaces `asyncio.gather`)
- `-p task` flag — non-interactive prompt mode (NOT `--prompt`, NOT `--print`)
- `-q` flag — suppress TUI spinner in non-interactive mode

### Model Selection by Task

| Task | Recommended Model | Source | Reason |
|------|-------------------|--------|--------|
| Complex reasoning (online) | `google/antigravity-claude-opus-4-6-thinking` + `--variant=max` | Antigravity | Best reasoning, extended thinking |
| Full codebase review | `google/antigravity-gemini-3-pro` + `--variant=high` | Antigravity | 1M context window |
| Fast online coding | `google/antigravity-claude-sonnet-4-5` | Antigravity | Balanced, no thinking overhead |
| Built-in free fallback | `opencode/big-pickle` | OpenCode | When Antigravity rate-limited |
| Research/synthesis | `opencode/kimi-k2.5-free` | OpenCode | 262K context, free |
| Fast prototyping | `opencode/minimax-m2.5-free` | OpenCode | Speed optimized |
| Air-gap / offline | `llama-cpp/local` | llama-cpp-python | Sovereign, no network |

---

## Recommended Configuration for XNAi

### Project Config (`.opencode/opencode.json`) — LIVE CONFIGURATION

> ⚠️ **Schema rules** (validated by `$schema`):
> - `"rules"` is **NOT valid** — causes `Unrecognized keys` error. Use `.opencode/RULES.md` instead.
> - `"mcpServers"` is **NOT valid** — MCP servers go in Cline's MCP settings only.
> - `"plugin"` key is singular (NOT `"plugins"`).

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "google/antigravity-claude-sonnet-4-5",
  "plugin": ["opencode-antigravity-auth@latest"],
  "provider": {
    "google": {
      "npm": "@ai-sdk/google",
      "models": {
        "antigravity-gemini-3-pro": { "name": "Gemini 3 Pro (Antigravity)", "limit": { "context": 1048576, "output": 65535 } },
        "antigravity-claude-sonnet-4-5": { "name": "Claude Sonnet 4.5 (Antigravity)", "limit": { "context": 200000, "output": 64000 } },
        "antigravity-claude-opus-4-6-thinking": { "name": "Claude Opus 4.6 Thinking (Antigravity)", "limit": { "context": 200000, "output": 64000 } }
      }
    },
    "llama-cpp": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "llama-cpp-python (local sovereign)",
      "options": { "baseURL": "http://localhost:8080/v1" },
      "models": {
        "local": { "name": "Local GGUF Model", "limit": { "context": 32768, "output": 4096 } }
      }
    }
  }
}
```

> **Agent rules** live in `.opencode/RULES.md` — see that file for the 9 XNAi coding standards.

---

## Usage Limits Summary

| Model Source | Free Tier | Paid Tier | Notes |
|--------------|-----------|-----------|-------|
| **Antigravity** ⭐ | ✅ 8 models (Claude+Gemini) | N/A | **OPERATIONAL** — 3 accounts; auto-rotates quota |
| OpenCode built-in | 5 models | N/A | Rate-limited by global usage |
| GitHub Copilot | ❌ No | ✅ Pro+ required | $19-39/month |
| OpenRouter | 31+ models | Pay per token | Free tier available |
| HuggingFace | Limited | Pay per token | Free tier available |
| llama-cpp-python | ✅ Unlimited | N/A | Local GGUF, Vulkan, sovereign |

---

## Quick Commands

```bash
# Start OpenCode (uses default model from opencode.json)
opencode

# Non-interactive mode (for scripting/agents)
opencode -q -p "your task"

# Specific Antigravity model with thinking
opencode run "complex task" --model=google/antigravity-claude-opus-4-6-thinking --variant=max

# Gemini 3 Pro (1M context)
opencode run "review codebase" --model=google/antigravity-gemini-3-pro --variant=high

# Local sovereign model (start llama-cpp server first)
opencode -m llama-cpp/local -p "offline task"

# Built-in free fallback
opencode -m opencode/big-pickle -p "fallback task"

# Continue last session
opencode --continue

# Auth management
opencode auth login              # add/re-auth Google account
opencode auth status             # check authenticated accounts
opencode auth list               # list all credentials

# Reset Antigravity auth
rm ~/.config/opencode/antigravity-accounts.json && opencode auth login
```

---

## Troubleshooting

### `Configuration is invalid: Unrecognized keys`
- **Cause**: `mcpServers`, `rules`, or `plugins` (plural) in `opencode.json`
- **Solution**: Remove invalid keys. MCP servers → Cline settings. Rules → `.opencode/RULES.md`. Use `plugin` (singular).

### Rate Limit Errors
- **Symptom**: "Rate limit exceeded" or "Overloaded"
- **Solution**: Plugin auto-rotates between 3 accounts. If all rate-limited, switch to `opencode/big-pickle` or `llama-cpp/local`

### Antigravity 403 Error
- **Symptom**: `Permission 'cloudaicompanion...' denied on resource '...rising-fact-p41fc...'`
- **Cause**: Using Gemini CLI quota models with no/invalid GCP project
- **Solution**: Use `antigravity-*` models (not `gemini-3-pro-preview`/`gemini-2.5-pro`) OR set up real GCP project

### Local Model Not Found
- **Symptom**: "Connection refused" at `localhost:8080`
- **Solution**: Start llama-cpp-python server: `python -m llama_cpp.server --model /path/model.gguf --port 8080`

### Permission Errors
- **Symptom**: Can't write files
- **Solution**: OpenCode inherits your user permissions — check file ownership

---

**Document Status**: ACTIVE
**Last Updated**: 2026-02-18
**Maintained By**: XNAi Foundation Team
