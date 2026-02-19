# Agent-CLI-Model Matrix v3.0.0

**XNAi Foundation CLI Orchestration Map**  
**Status**: AUTHORITATIVE — Verified + Hallucination-audited  
**Last Updated**: 2026-02-18 (Sprint 3, v3.0.1 patch)  
**Supersedes**: v2.0.0 (contained hallucinated model names and Cline promo claims)  
**Primary Reference**: `expert-knowledge/XNAI-MODEL-INTELLIGENCE-REPORT-2026-02-18.md`

---

## ⚠️ Corrections from v2.0.0

| v2.0.0 Claim | v3.0.0 Reality |
|--------------|----------------|
| "Cline FREE Claude Opus 4.6 promo" | ❌ REMOVED — Cline uses paid `claude-sonnet-4-6` via API key |
| Ollama as local engine | ❌ REPLACED — llama-cpp-python is the actual local engine |
| "claude-opus-4.6, gpt-5.2-codex" as Copilot paid | ⚠️ NOTED — claude-opus-4.6 IS a confirmed public Anthropic model; gpt-5.2-codex is Copilot-internal |
| Mission Control = Claude.ai | ❌ UPDATED — Mission Control = Sovereign MC Agent |
| "Gemini 3 Pro" as public Google model | ⚠️ CLARIFIED — Antigravity-internal label only |

> **v3.0.1 Patch (2026-02-18)**: Corrected Cline model throughout — Cline uses `claude-sonnet-4-6` (not 4-5). Confirmed via status bar `cline:anthropic/claude-sonnet-4.6`. Also confirmed `claude-opus-4-6` is a real public Anthropic model ($5/$25, 128K output).

---

## Executive Summary

XNAi Foundation operates a **tiered AI orchestration model** across 5 tool layers:

```
┌─────────────────────────────────────────────────────────────────┐
│                 XNAi AI Orchestration Stack v3.0                │
│                                                                 │
│  TIER 1: Antigravity Auth (OpenCode)  — FREE frontier models    │
│  TIER 2: Gemini CLI                   — Free 1M context         │
│  TIER 3: Copilot CLI (free plan)      — GitHub-native agent     │
│  TIER 4: OpenCode Built-in Free       — Rate-limit fallback     │
│  TIER 5: llama-cpp-python             — Air-gap / sovereign     │
│                                                                 │
│  IDE LAYER: Cline (VSCodium)         — claude-sonnet-4-6        │
└─────────────────────────────────────────────────────────────────┘
```

---

## CLI Reference Table

| CLI | Version | Free Models | Paid Required | Installed | Use For |
|-----|---------|-------------|---------------|-----------|---------|
| **OpenCode** | v1.2.6 | ✅ 5 built-in + Antigravity | For Copilot provider | ✅ Yes | Primary multi-model agent |
| **Gemini CLI** | v0.28.2 | ✅ 25 req/day Gemini 2.5 Pro | No | ✅ Yes | 1M context analysis |
| **Copilot CLI** | v0.0.411 | ✅ 3 models (free plan) | For premium models | ✅ Yes (`/home/arcana-novai/.copilot/`) | GitHub-native tasks |
| **gh copilot** | built-in gh | ✅ command suggest/explain | No | ✅ Yes | Basic shell help ONLY |
| **Cline (IDE)** | v0.31+ | ❌ Uses API key | Yes (API key) | ✅ Yes (VSCodium) | IDE-integrated dev |

---

## Tier 1: OpenCode + Antigravity Auth (PRIMARY)

**CLI**: `opencode` v1.2.6  
**Plugin**: `opencode-antigravity-auth@latest` v1.5.1  
**Auth Status**: ✅ 3 accounts authenticated (2026-02-18)  
**Config**: `.opencode/opencode.json` + `.opencode/RULES.md`

### Antigravity Free Frontier Models

| OpenCode Model ID | Name | Context | Thinking | Best For |
|-------------------|------|---------|----------|---------|
| `google/antigravity-gemini-3-pro` | Gemini [2.5] Pro (internal) | **1M** | `low`, `high` | Full codebase audit, massive context |
| `google/antigravity-gemini-3-flash` | Gemini [2.5] Flash (internal) | **1M** | `minimal`→`high` | Fast large-context tasks |
| `google/antigravity-claude-sonnet-4-6` | Claude Sonnet 4.6 | 200K | — | Default: fast quality dev (Jan 2026 cutoff) |
| `google/antigravity-claude-sonnet-4-6-thinking` | Claude Sonnet 4.6 Thinking | 200K | `low`, `max` | Balanced reasoning |
| `google/antigravity-claude-opus-4-5-thinking` | Claude Opus 4.5 Thinking | 200K | `low`, `max` | Deep architecture decisions |
| `google/antigravity-claude-opus-4-6-thinking` | Claude Opus 4.6 Thinking | 200K | `low`, `max` | Latest Opus-class reasoning (128K output) |

> **⚠️ Model name notes**: "Gemini 3" = Antigravity's internal label for Google's internal API model (may be Gemini 2.5 Pro or successor). "Claude Opus 4.6" and "Claude Sonnet 4.6" = confirmed public Anthropic models, also accessible via Antigravity's routing. These are REAL model IDs that route to real models through Antigravity's API.

### OpenCode Usage

```bash
# Default (sonnet-4-6, update opencode.json if needed)
opencode -p "your task"

# Specific models
opencode -m google/antigravity-claude-opus-4-6-thinking --variant=max -p "architecture task"
opencode -m google/antigravity-gemini-3-pro --variant=high -p "review entire codebase"
opencode -m google/antigravity-claude-sonnet-4-6 -p "fix this bug"

# Non-interactive (for Agent Bus / scripting)
opencode -q -p "task"

# Interactive TUI (Vim-style navigation)
opencode

# Headless server mode (for REST API)
opencode serve
```

### OpenCode Architecture Highlights

OpenCode is the **most feature-rich** terminal AI agent due to its **client/server architecture**:

| Feature | Details |
|---------|---------|
| **REST API** | Full HTTP API via `opencode serve` — enables Agent Bus orchestration |
| **Multiple clients** | TUI, web (`opencode web`), remote attach (`opencode attach <url>`) |
| **75+ providers** | OpenRouter, HuggingFace, Anthropic, Copilot, Vertex, etc. |
| **npm plugins** | `opencode-antigravity-auth`, custom plugins |
| **MCP support** | Connects to all registered MCP servers |
| **RULES.md** | Project-level persistent AI instructions |
| **LSP integration** | Code-aware completions |
| **Named sessions** | `--session <name>` for parallel work |
| **Vim keybindings** | hjkl navigation, `i` insert, `Esc` normal |
| **`/connect`** | Add new providers interactively |
| **`/models`** | Switch models mid-session |
| **`-q -p "task"`** | Scriptable non-interactive mode |
| **`--variant=max`** | Extended thinking budgets |

### OpenCode Built-in Fallback Models (Tier 4)

When Antigravity is rate-limited, fall back to these (no auth required):

| Model ID | Context | Notes |
|----------|---------|-------|
| `opencode/big-pickle` | 200K | Best quality built-in; opaque underlying model |
| `opencode/kimi-k2.5-free` | 262K | Largest context built-in; likely Kimi K2-based |
| `opencode/gpt-5-nano` | 400K | Largest context built-in; NOT public GPT-5 |
| `opencode/minimax-m2.5-free` | 204K | Fastest built-in; good for quick tasks |
| `opencode/glm-5-free` | 200K | Structured/logical tasks; most rate-limited |

> **Fallback order**: `big-pickle` → `kimi-k2.5-free` → `gpt-5-nano` → `minimax-m2.5-free` → `glm-5-free`

---

## Tier 2: Gemini CLI (1M Context Specialist)

**CLI**: `gemini` v0.28.2  
**Install**: Already installed on system  
**Free quota**: 25 requests/day (Gemini 2.5 Pro) via personal Google account

### Available Models

| Model | Context | Notes |
|-------|---------|-------|
| Gemini 2.5 Pro | 1M | Default; 25 req/day free; deep thinking |
| Gemini 2.5 Flash | 1M | Faster; higher rate limits |

### Gemini CLI Unique Features

| Feature | Details |
|---------|---------|
| **Google Search grounding** | Native web search integrated into responses |
| **GEMINI.md** | Per-project persistent instructions |
| **Extensions + Skills** | `gemini extensions install`, `gemini skills` — GitHub MCP already installed |
| **Hooks** | `gemini hooks` — lifecycle automation |
| **Sandboxing** | `-s/--sandbox` for safe execution |
| **Approval modes** | `default`, `auto_edit`, `yolo`, `plan` (read-only) |
| **Session checkpoints** | `--resume latest` |

### When to Use Gemini CLI

- Full codebase audit when Antigravity is unavailable
- Google Search grounding needed (live web research during task)
- Reading large documentation sets (PDFs, multiple docs)
- When you want Gemini 2.5 Pro separate from Antigravity quota

```bash
# Start Gemini CLI (uses stored Google account)
gemini

# Non-interactive
gemini -p "review entire expert-knowledge directory"

# Auto-edit mode (approve all changes)
gemini --approval=auto_edit -p "refactor all tests to AnyIO"

# With search grounding
gemini -p "research latest fastembed ONNX optimizations and apply to EmbeddingEngine"
```

---

## Tier 3: Copilot CLI (GitHub-native Agent)

**CLI**: `copilot` v0.0.411  
**Location**: `/home/arcana-novai/.copilot/`  
**Subscription**: Active Copilot free plan = valid "active subscription"

### ⚠️ TWO DIFFERENT TOOLS — Do Not Confuse

| Tool | Command | What It Is | Agent? |
|------|---------|-----------|--------|
| **Copilot CLI** | `copilot` | Full agentic coding assistant | ✅ YES |
| **gh copilot** | `gh copilot explain/suggest` | Basic shell command helper | ❌ NO |

**Use `copilot` (not `gh copilot`) for actual AI coding work.**

### Free Tier Models (Copilot free plan)

| Copilot Label | Context | Likely Underlying | Best For |
|---------------|---------|------------------|---------|
| `claude-haiku-4.5` | 200K | Claude Haiku 4.5 (confirmed) | Fast routing, simple tasks, quick fixes |
| `gpt-5-mini` | 128K | ⚠️ Internal label (likely o4-mini class) | Balanced general tasks |
| `gemini-3-flash-preview` | 1M | ⚠️ Internal label (likely Gemini 2.5 Flash) | Large context tasks |

> **Free tier limits**: ~50 chat messages/day, 2,000 code completions/month

### Copilot CLI Features

| Feature | Details |
|---------|---------|
| **GitHub MCP** | Ships with GitHub MCP server — native issues, PRs, repo access |
| **File editing** | Full terminal-based file read/write/edit |
| **Preview mode** | Shows all planned actions before execution |
| **MCP extensible** | Supports custom MCP servers |
| **GitHub context** | Understands repo structure, issues, PR diffs natively |

### When to Use Copilot CLI

- GitHub-integrated tasks (PR reviews, issue triage, commit messages)
- When you need `gemini-3-flash-preview` 1M context as Antigravity fallback
- Quick Claude Haiku 4.5 tasks without spinning up OpenCode
- GitHub Actions debugging

```bash
# Start interactive
copilot

# Direct prompt
copilot "fix the failing test in tests/test_sovereign_mc_agent.py"

# Specific model
copilot --model claude-haiku-4.5 "summarize recent git changes"
copilot --model gemini-3-flash-preview "review the entire codebase for AnyIO compliance"
```

---

## IDE Layer: Cline Extension (VSCodium)

**Platform**: VSCodium extension  
**Model**: `claude-sonnet-4-6` (API ID: `claude-sonnet-4-6`)  
**Provider**: Anthropic API (requires API key) or OpenRouter  
**Confirmed**: Status bar shows `cline:anthropic/claude-sonnet-4.6`

### Cline Model — CORRECTED (v3.0.1)

> **❌ v2.0.0 ERROR**: Earlier docs claimed "FREE Claude Opus 4.6 promo" for Cline. This was hallucinated.  
> **❌ v3.0.0 ERROR**: Said Cline uses `claude-sonnet-4-5`. Also WRONG — confirmed via status bar.  
> **✅ v3.0.1 REALITY**: Cline uses `claude-sonnet-4-6` via paid Anthropic API key. No promo. No Opus. No 4.5.

### Claude Sonnet 4.6 Specs

| Attribute | Value |
|-----------|-------|
| API ID | `claude-sonnet-4-6` |
| Context | 200,000 tokens (1M extended beta) |
| Max Output | 64,000 tokens |
| Extended Thinking | ✅ Yes |
| Vision | ✅ Yes (images, PDFs) |
| Training Cutoff | January 2026 |
| Pricing | ~$3/M input, ~$15/M output |
| Strengths | Coding, agentic tasks, tool use, instruction following, latest knowledge |

### Why Cline + Sonnet 4.6 for IDE Work

- **IDE integration**: Full VSCodium file tree, diff view, terminal access
- **Jan 2026 knowledge**: Most recent training cutoff of any Sonnet model
- **Auto-approve**: Autonomous file editing with Cline's approval system
- **OpenRouter**: 31+ free models available as fallback (needs OpenRouter API key)
- **MCP servers**: Accesses all 3 XNAi MCP servers (agentbus, vikunja, rag)
- **Context files**: Reads `memory_bank/activeContext.md` on each session

---

## Tier 5: Local Sovereign Layer (llama-cpp-python)

**Engine**: llama-cpp-python (NOT Ollama — different tool)  
**API**: OpenAI-compatible at `http://localhost:8080/v1`  
**GPU**: Vulkan acceleration (Ryzen 5700U RDNA2 iGPU)

### Recommended GGUF Models (8GB RAM budget)

| Model | VRAM | Context | Best For | Download |
|-------|------|---------|---------|---------|
| **Qwen 2.5 7B Q4_K_M** | 4.4GB | 32K | Code + multilingual, recommended default | huggingface.co |
| **Phi-3.5-mini Q4_K_M** | 2.2GB | 128K | Minimal footprint, surprising quality | huggingface.co |
| **DeepSeek-R1-Distill-Qwen-7B Q4** | 4.5GB | 32K | Reasoning tasks | huggingface.co |
| **Llama 3.1 8B Q4_K_M** | 4.7GB | 128K | General, instruction following | huggingface.co |

### Usage

```bash
# Start server (Terminal 1)
python -m llama_cpp.server \
  --model /path/to/qwen2.5-7b-instruct-q4_k_m.gguf \
  --host 0.0.0.0 --port 8080 \
  --n_ctx 32768 --n_gpu_layers -1

# OpenCode (Terminal 2)
opencode -m llama-cpp/local -p "offline task"

# Copilot CLI cannot access local models (cloud-only)
# Gemini CLI cannot access local models (Gemini-only)
# Only OpenCode + Cline + direct API access support local models
```

### When to Use Local Models

| Scenario | Why |
|----------|-----|
| Air-gap production deployment | Zero network, zero telemetry |
| Rate limit exhaustion (all tiers) | Always available |
| Offline development sessions | Works without internet |
| Zero-telemetry compliance | Code never leaves machine |
| Testing RAG pipeline locally | Direct integration with Qdrant/FAISS |

---

## Task Routing Quick Reference

| Task | Tier | CLI | Model | Notes |
|------|------|-----|-------|-------|
| **Full codebase audit** | 1 | OpenCode | `google/antigravity-gemini-3-pro --variant=high` | 1M context |
| **Architecture decision** | 1 | OpenCode | `google/antigravity-claude-opus-4-6-thinking --variant=max` | Extended thinking |
| **Daily coding** | IDE | Cline | `claude-sonnet-4-6` | IDE integration, Jan 2026 knowledge |
| **Bug fix (fast)** | 3 | Copilot CLI | `claude-haiku-4.5` | Sub-second response |
| **Large doc synthesis** | 2 | Gemini CLI | Gemini 2.5 Pro | Native search grounding |
| **GitHub PR review** | 3 | Copilot CLI | `claude-haiku-4.5` | GitHub MCP native |
| **Rate limited fallback** | 4 | OpenCode | `opencode/big-pickle` | No quota |
| **Air-gap / offline** | 5 | OpenCode | `llama-cpp/local` | Zero network |
| **Agent Bus orchestration** | 1 | OpenCode (subprocess) | Antigravity Sonnet 4.6 | AnyIO compliant |
| **Quick shell help** | — | gh copilot | N/A | NOT a coding agent |

---

## Sovereign MC Agent Model Routing

The `sovereign_mc_agent.py` `OpenCodeDispatcher` should use this routing:

```python
# Recommended model routing for sovereign_mc_agent.py
TASK_MODEL_ROUTING = {
    # High-value tasks — extended thinking
    "architecture": "google/antigravity-claude-opus-4-6-thinking",
    "security_audit": "google/antigravity-claude-opus-4-6-thinking",
    
    # Large context tasks
    "full_codebase_review": "google/antigravity-gemini-3-pro",
    "documentation_synthesis": "google/antigravity-gemini-3-flash",
    
    # General development
    "general": "google/antigravity-claude-sonnet-4-6",
    "code_review": "google/antigravity-claude-sonnet-4-6",
    
    # Speed priority
    "fast": "opencode/minimax-m2.5-free",
    "routing": "opencode/minimax-m2.5-free",
    
    # Fallback
    "fallback_1": "opencode/big-pickle",
    "fallback_2": "opencode/kimi-k2.5-free",
    
    # Air-gap
    "offline": "llama-cpp/local",
    "sovereign": "llama-cpp/local",
}
```

---

## Context Window Decision Tree

```
How much context does your task require?

< 8K tokens?
  → Use opencode/minimax-m2.5-free (fastest)

8K – 50K tokens?
  → Use google/antigravity-claude-sonnet-4-6 (best quality/speed)
  → Fallback: opencode/big-pickle

50K – 200K tokens?
  → Needs reasoning? → google/antigravity-claude-opus-4-6-thinking
  → Speed fine?      → google/antigravity-claude-sonnet-4-6

200K – 1M tokens?
  → Use google/antigravity-gemini-3-pro (1M, best reasoning)
  → OR: Gemini CLI (separate quota)
  → OR: copilot --model gemini-3-flash-preview (Copilot free)

> 1M tokens?
  → Must chunk input OR use summarization pipeline
  → Not supported by any single model
```

---

## Rate Limit Waterfall

```
Antigravity rate limited?
  → Plugin auto-rotates between 3 accounts
  → All 3 accounts limited? → OpenCode built-in (big-pickle)
  → big-pickle limited? → Gemini CLI (separate quota)
  → Gemini CLI limited? → Copilot CLI (separate quota)
  → All cloud limited? → llama-cpp/local (unlimited, offline)
```

---

## Document History

| Version | Date | Agent | Changes |
|---------|------|-------|---------|
| v3.0.1 | 2026-02-18 | Cline (claude-sonnet-4-6) | Corrected Cline model from 4-5 → 4-6; confirmed claude-opus-4-6 as real public model; updated Antigravity routing to 4-6 models |
| v3.0.0 | 2026-02-18 | Cline (claude-sonnet-4-6) | Full hallucination audit; Copilot CLI documented; llama-cpp-python; verified model specs; tiered strategy |
| v2.0.0 | 2026-02-18 | Cline (prev session) | OpenCode as primary; Copilot paid note |
| v1.0.0 | 2026-02-17 | Copilot CLI | Initial release |

**Full research basis**: `expert-knowledge/XNAI-MODEL-INTELLIGENCE-REPORT-2026-02-18.md`
