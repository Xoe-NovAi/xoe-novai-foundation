# Agent-CLI-Model Matrix v2.0.0

**XNAi Foundation CLI Orchestration Map**  
**Status**: Production-Ready  
**Last Updated**: 2026-02-18  
**Primary CLI**: **OpenCode CLI** (replaces Copilot CLI)
**Zero-Hallucination Version**: ✅ Verified and Accurate

---

## Executive Summary

This matrix defines the optimal CLI and model assignments for each XNAi agent role. **OpenCode CLI is now the primary CLI** due to:
- Best terminal UX/UI
- 5 built-in free models
- GitHub Copilot integration (with PAID subscription)
- 75+ LLM provider support
- Multi-session capability

---

## ⚠️ Critical Finding: GitHub Copilot Requires PAID Subscription

**GitHub Copilot Free tier does NOT work with OpenCode.** To access `github-copilot/*` models, you need:
- Copilot Pro ($19/month)
- Copilot Pro+ ($39/month)
- Copilot Business/Enterprise

**Workaround**: Use OpenCode free models or OpenRouter for free access to similar models.

---

## Agent Assignments

### Agent: OpenCode (PRIMARY CLI)

**CLI**: OpenCode CLI v1.2.6  
**Role**: **Primary CLI for all tasks** - orchestration, implementation, research  
**Built-in Free Models**: 5 (no setup required)

#### Primary Model Assignments by Task

| Task Type | Model | Context | Why |
|-----------|-------|---------|-----|
| Complex reasoning | `opencode/big-pickle` | 200K | Best reasoning quality |
| Research/synthesis | `opencode/kimi-k2.5-free` | 262K | Large context, frontier |
| Fast prototyping | `opencode/minimax-m2.5-free` | 204K | Speed optimized |
| Large context | `opencode/gpt-5-nano` | 400K | Largest free context |
| Structured tasks | `opencode/glm-5-free` | 200K | Logic specialist |

#### Configuration

```bash
# No setup required - built-in models work immediately
opencode

# With specific model
opencode --model opencode/big-pickle

# Continue session
opencode --continue

# View available models
opencode models
```

#### Adding GitHub Copilot (PAID Required)

```bash
# In OpenCode TUI
/connect
# Select GitHub Copilot
# Complete device login at github.com/login/device
# Models available: claude-opus-4.6, gpt-5.2-codex, gemini-3-pro, etc.
```

#### Adding OpenRouter (31+ Free Models)

```bash
# In OpenCode TUI
/connect
# Select OpenRouter
# Enter API key from openrouter.ai/keys
# Models: step-3.5-flash:free, deepseek-r1:free, trinity-large-preview:free, etc.
```

#### Adding Local Models (Ollama)

```bash
# Install Ollama first
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:7b

# Configure in ~/.config/opencode/opencode.json
{
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "options": { "baseURL": "http://localhost:11434/v1" },
      "models": {
        "qwen2.5:7b": { "name": "Qwen 2.5 7B (local)" }
      }
    }
  }
}
```

#### Adding Google Gemini

```bash
# Option 1: Via OpenRouter (recommended for free tier)
# Add OpenRouter provider, then use openrouter/google/gemini-3-flash-preview:free

# Option 2: Via Google Vertex AI (enterprise)
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
export GOOGLE_CLOUD_PROJECT=your-project-id
# Then in TUI: /models → select gemini
```

#### Adding HuggingFace

```bash
# In OpenCode TUI
/connect
# Select Hugging Face
# Enter token from huggingface.co/settings/tokens
# Needs "Make calls to Inference Providers" permission
# Models: kimi-k2-instruct, glm-4.6, qwen models
```

**Strengths**:
- ✅ Best terminal UX/UI
- ✅ 5 free models built-in (no setup)
- ✅ 75+ provider support
- ✅ GitHub Copilot integration
- ✅ OpenRouter, HuggingFace, Ollama support
- ✅ Multi-session capability
- ✅ LSP enabled
- ✅ MCP server support
- ✅ Skills and agents framework

**Limitations**:
- ⚠️ Free models have shared rate limits
- ⚠️ GitHub Copilot requires PAID subscription
- ⚠️ Some providers need API keys

---

### Agent: Cline Extension (VS Code)

**Platform**: VS Code Extension  
**Role**: IDE-based implementation with Claude Opus 4.6  
**Special**: **FREE Claude Opus 4.6 access** (limited-time promo)

#### Current Free Access

⚠️ **IMPORTANT**: Cline VS Code extension currently has **FREE access to Claude Opus 4.6**. This is a limited-time promotion.

| Model | Context | Status | Notes |
|-------|---------|--------|-------|
| Claude Opus 4.6 | 200K | **FREE (promo)** | Limited time |
| OpenRouter models | Various | FREE via OpenRouter | 31+ free models |

#### Configuration

```bash
# In VS Code
# 1. Install Cline extension
# 2. Open Cline sidebar
# 3. Click gear icon → settings
# 4. Select provider: Anthropic or OpenRouter
# 5. Enter API key if needed
```

**Why Keep Cline Extension**:
- ✅ FREE Claude Opus 4.6 (while promo lasts)
- ✅ IDE integration with code context
- ✅ OpenRouter access for model diversity
- ✅ Auto-approve for autonomous work

---

### Agent: Gemini CLI (Synthesis)

**CLI**: Gemini CLI v0.28.2  
**Role**: High-level synthesis, complex reasoning  
**Primary Model**: gemini-3-flash-preview (1M context)

**Configuration**:
```bash
# Get free API key from aistudio.google.com
export GEMINI_API_KEY="AIza..."
gemini
```

**Why Gemini CLI**:
- ✅ 1M context window
- ✅ Free via Google AI Studio
- ✅ Fast responses
- ✅ Vision/PDF support

**Limitations**:
- ⚠️ Rate limited (15 req/min)
- ⚠️ Requires Google account

---

### Mission Control (Strategic Oversight)

**Platform**: Claude.ai Project (GitHub-synced)  
**Role**: Strategic overview of ALL XNAi initiatives  
**Models**: Claude Opus 4.6 (best reasoning)

**Configuration**:
```
Claude.ai Project: "XNAi Mission Control"
├── GitHub Integration: Auto-synced repo
├── Uploaded Briefing: MC Project briefing (memory_bank content)
├── Output: /mc-oversight/ directory (strategic recommendations)
```

---

## Workflow Diagram (UPDATED)

```
┌─────────────────────────────────────────────────────────────┐
│                  XNAi Foundation Workflow v2.0               │
│                Primary CLI: OpenCode                         │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│              OpenCode CLI (Primary)                          │
│  ┌────────────┬────────────┬────────────┬────────────┐      │
│  │ big-pickle │ kimi-k2.5  │ gpt-5-nano │ minimax    │      │
│  │ reasoning  │ research   │ 400K ctx   │ speed      │      │
│  └────────────┴────────────┴────────────┴────────────┘      │
│                                                              │
│  Providers: GitHub Copilot (paid) | OpenRouter | HuggingFace │
│  Local: Ollama | LM Studio | llama.cpp                       │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│              Cline VS Code Extension                         │
│  Model: Claude Opus 4.6 (FREE promo!)                        │
│  Role: IDE implementation, code context                      │
│  Provider: Anthropic | OpenRouter (31+ free models)          │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│              Gemini CLI (Supplementary)                      │
│  Model: gemini-3-flash-preview (1M context)                  │
│  Role: Synthesis, large document analysis                    │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│              Mission Control (Claude.ai)                     │
│  Role: Strategic oversight, GitHub-synced                    │
│  Output: /mc-oversight/ recommendations                      │
└──────────────────────────────────────────────────────────────┘
```

---

## Quick Reference Table (UPDATED)

| CLI | Version | Primary Model | Free? | Paid Options | Setup |
|-----|---------|---------------|-------|--------------|-------|
| **OpenCode** | v1.2.6 | big-pickle | ✅ 5 models | Copilot, OpenRouter | 0 min |
| Cline Ext | v0.31+ | claude-opus-4.6 | ✅ (promo) | OpenRouter | 2 min |
| Gemini CLI | v0.28.2 | gemini-3-flash | ✅ | N/A | 5 min |
| Claude.ai MC | Web | claude-opus-4.6 | ✅ | N/A | 10 min |

---

## Model Selection by Task (Quick Guide)

| Task | CLI | Model | Cost |
|------|-----|-------|------|
| Complex reasoning | OpenCode | `big-pickle` | FREE |
| Research (262K ctx) | OpenCode | `kimi-k2.5-free` | FREE |
| Large context (400K) | OpenCode | `gpt-5-nano` | FREE |
| Fast prototyping | OpenCode | `minimax-m2.5-free` | FREE |
| IDE + code context | Cline Ext | `claude-opus-4.6` | FREE (promo) |
| Multi-provider | Cline Ext | OpenRouter models | FREE |
| 1M context synthesis | Gemini CLI | `gemini-3-flash` | FREE |
| Offline/air-gap | OpenCode + Ollama | `qwen2.5:7b` | FREE |

---

## Setup Checklist (UPDATED)

- [x] **OpenCode CLI**: Already installed
  - Built-in models: big-pickle, glm-5-free, gpt-5-nano, kimi-k2.5-free, minimax-m2.5-free
  - Cost: FREE

- [ ] **Add OpenRouter to OpenCode**:
  - Get key: openrouter.ai/keys
  - In TUI: `/connect` → OpenRouter → paste key
  - Access 31+ free models

- [ ] **Add HuggingFace to OpenCode**:
  - Get token: huggingface.co/settings/tokens
  - In TUI: `/connect` → Hugging Face → paste token

- [ ] **Install Ollama for local models**:
  - `curl -fsSL https://ollama.com/install.sh | sh`
  - `ollama pull qwen2.5:7b`

- [x] **Cline Extension**: Claude Opus 4.6 FREE access
  - Maximize usage while promo lasts

---

## Rate Limits Summary

| Source | Rate Limit | Notes |
|--------|------------|-------|
| OpenCode free models | Shared pool | Can hit randomly |
| OpenRouter free | Per-model | Usually generous |
| HuggingFace free | Limited | Varies by model |
| Gemini free | 15 req/min | Hard limit |
| Cline Opus promo | Unknown | Limited time |

---

## Related Documentation

- `expert-knowledge/OPENCODE-CLI-COMPREHENSIVE-GUIDE-v1.0.0.md` - Full OpenCode guide
- `expert-knowledge/CLI-NOMENCLATURE-GUIDE-v1.0.0.md` - Naming conventions
- `session-state-archives/2026-02-17-comprehensive-import/copilot-session-b601691a/USER-DECISIONS-2026-02-17.md` - User decisions

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| v2.0.0 | 2026-02-18 | OpenCode as primary CLI, GitHub Copilot paid requirement |
| v1.0.0 | 2026-02-17 | Initial release |
