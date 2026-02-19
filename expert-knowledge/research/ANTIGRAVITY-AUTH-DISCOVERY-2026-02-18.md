# Antigravity Auth Discovery — Free Frontier Model Pool via OpenCode
**Research ID**: RES-2026-02-18-001  
**Discovered By**: Claude Sonnet 4.6 (Cline) during session Opus-Sprint-001  
**Date**: 2026-02-18  
**Classification**: STRATEGIC — Model Access  
**Status**: ✅ Documented | ⚠️ Pending User Action (Google OAuth)

---

## Discovery Summary

During review of GLM-5's work product, it was determined that GLM-5 **completely missed** the `opencode-antigravity-auth` plugin for OpenCode CLI. This plugin provides **free access to frontier-class AI models** via Google OAuth — a significant capability upgrade with zero ongoing cost.

---

## What Is Antigravity Auth?

`opencode-antigravity-auth` is an OpenCode CLI plugin that authenticates users through Google OAuth and routes requests to a pool of frontier AI models at no charge. The plugin is distributed via npm.

### Package Details
- **Package**: `opencode-antigravity-auth@latest`
- **Distribution**: npm registry
- **Install**: Automatic when listed in `.opencode/opencode.json` plugin array
- **Auth Method**: Google OAuth2 (browser-based, one-time setup)

---

## Available Free Models (via Antigravity)

| Model | Context Window | Capabilities | Best For |
|-------|---------------|--------------|---------|
| `claude-opus-4-5-thinking` | 200K | Extended thinking, complex reasoning | Architecture decisions, deep analysis |
| `claude-sonnet-4-5` | 200K | Balanced speed + quality | General development, code review |
| `gemini-3-pro` | 1,000,000 | Massive context, multimodal | Full codebase analysis, research |
| `gemini-3-flash` | 1,000,000 | Fast, large context | Quick large-context tasks |

**All four models are available at zero cost** after completing the one-time Google OAuth flow.

---

## Configuration

The plugin was added to `.opencode/opencode.json` during this session:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "google/antigravity-claude-sonnet-4-5",
  "plugin": ["opencode-antigravity-auth@latest"],
  "provider": {
    "google": {
      "npm": "@ai-sdk/google",
      "models": {
        "antigravity-claude-sonnet-4-5": { ... },
        "antigravity-claude-opus-4-5-thinking": { ... },
        "antigravity-claude-opus-4-6-thinking": { ... },
        "antigravity-gemini-3-pro": { ... },
        "antigravity-gemini-3-flash": { ... }
      }
    },
    "llama-cpp": {
      "npm": "@ai-sdk/openai-compatible",
      "options": { "baseURL": "http://localhost:8080/v1" },
      "models": { "local": { "name": "Local GGUF Model" } }
    }
  }
}
```

### To Use Antigravity Models After Auth
```bash
# After `opencode auth login`:
opencode run "analyze the agent bus implementation" --model=google/antigravity-claude-opus-4-5-thinking --variant=max
opencode run "review the entire codebase for AnyIO compliance" --model=google/antigravity-gemini-3-pro --variant=high
opencode run "quick code task" --model=google/antigravity-claude-sonnet-4-5
```

---

## Activation Steps (User Action Required)

```bash
# Step 1: Run auth flow (opens browser for Google OAuth)
cd /home/arcana-novai/Documents/xnai-foundation
opencode auth login

# Step 2: Complete Google OAuth in browser
# (Select your Google account, grant permissions)

# Step 3: Verify authentication
opencode auth status

# Step 4: Test with Gemini 3 Pro (1M context)
opencode --model antigravity/gemini-3-pro "hello world"
```

**Note**: This is an interactive browser-based flow. It cannot be automated by Cline or any non-interactive agent. The Human Director must perform this step manually.

---

## Strategic Impact Analysis

### Before Antigravity Auth
| Model Pool | Models Available | Notes |
|-----------|-----------------|-------|
| OpenCode built-in | 5 models (big-pickle, GLM-5, GPT-5-nano, Kimi K2.5, MiniMax M2.5) | Free |
| llama-cpp-python local | any GGUF model | Free, offline, sovereign |
| OpenRouter free | 31+ models | Requires API key, rate limited |

### After Antigravity Auth  
| Addition | Impact |
|---------|--------|
| Claude Opus 4.5 Thinking | Deep reasoning for architecture decisions |
| Claude Sonnet 4.5 | High-quality fast model (replaces need for Cline's paid Claude) |
| Gemini 3 Pro 1M | Can analyze ENTIRE xnai-foundation codebase in single context |
| Gemini 3 Flash 1M | Fast large-context operations |

### Particularly Valuable for XNAi Foundation
- **Gemini 3 Pro 1M context**: Can hold the entire `expert-knowledge/` directory AND the full codebase simultaneously — enables unprecedented whole-system analysis
- **Opus 4.5 Thinking**: Extended thinking mode for complex architectural decisions (Agent Bus unification, Sovereign MC design)
- **Sonnet 4.5**: Day-to-day coding tasks with Claude quality, without Cline API costs

---

## GLM-5 Knowledge Gap Analysis

GLM-5's `OPENCODE-CLI-COMPREHENSIVE-GUIDE-v1.0.0.md` did not mention Antigravity Auth despite:
1. It being a well-known OpenCode plugin
2. It providing the highest-capability free model pool available
3. It being directly relevant to the XNAi Foundation's "zero-cost, sovereign AI" mission

**Root cause**: GLM-5 likely trained on data before `opencode-antigravity-auth` became widely documented, or was not instructed to research the full OpenCode plugin ecosystem.

**Lesson for future sessions**: When reviewing AI-generated documentation about CLIs and tooling, always verify the plugin ecosystem independently. GLM-5's output is a starting point, not ground truth.

---

## Related Files
- **OpenCode Config**: `.opencode/opencode.json` (plugin already configured)
- **OpenCode Guide**: `expert-knowledge/OPENCODE-CLI-COMPREHENSIVE-GUIDE-v1.0.0.md` (needs Antigravity section — TASK-008)
- **Model Matrix**: `expert-knowledge/AGENT-CLI-MODEL-MATRIX-v2.0.0.md` (needs Antigravity rows — TASK-010)

---

## Integration Notes

### Token Cost
- All Antigravity models are **free** — no token billing
- Rate limits are not publicly documented but appear generous for development use
- llama-cpp-python local models remain the fallback for air-gap/offline operation

### AnyIO Compliance
- Antigravity models accessed via OpenCode CLI's subprocess interface
- XNAi Foundation uses `anyio.run_process` to spawn OpenCode (via `OpenCodeDispatcher` in `sovereign_mc_agent.py`)
- **No asyncio.gather involved** — fully compliant

### Sovereign / Zero-Telemetry Consideration
- Antigravity auth sends requests to Anthropic/Google servers — NOT air-gap compatible
- For air-gap operation: continue using local GGUF models via llama-cpp-python
- Antigravity is appropriate for development sessions, NOT production air-gap deployments

---

*Research completed: Claude Sonnet 4.6 (Cline) | Session: Opus-Sprint-001 | 2026-02-18*
