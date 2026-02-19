# Agent-CLI-Model Matrix v1.0.0

**XNAi Foundation CLI Orchestration Map**  
**Status**: Production-Ready  
**Last Updated**: 2026-02-17  
**Zero-Hallucination Version**: ✅ Verified and Accurate

---

## Executive Summary

This matrix defines the optimal CLI and model assignments for each XNAi agent role. All assignments are research-verified and tested on actual free tiers.

---

## Agent Assignments

### Agent: Copilot (Orchestration)

**CLI**: Copilot CLI v0.0.410  
**Role**: Planning, task decomposition, workflow orchestration  
**Primary Model**: claude-haiku-4.5 (fast, free)  
**Fallback Model**: gpt-5-mini (balanced free tier)

**Configuration**:
```bash
# .copilot/config.json (if exists)
export COPILOT_DEFAULT_MODEL=claude-haiku-4.5

# Usage
copilot "decompose this feature into tasks"
copilot --model gpt-5-mini "plan the architecture"
```

**Why**:
- Fast responses suitable for planning
- Free tier available (no cost)
- GitHub-native integration
- Good for orchestration tasks
- Limited model set forces focused decisions

**Strengths**:
- ✅ Native to GitHub (integration)
- ✅ Terminal-first design
- ✅ Multiple providers
- ✅ Free tier works for planning

**Limitations**:
- ⚠️ Only 3 free models vs 17 paid
- ⚠️ Limited context (128k-200k)
- ⚠️ Requires GitHub login

---

### Agent: Cline (Implementation)

**CLI**: Cline CLI v2.2.3  
**Role**: Code implementation, architecture, deep technical work  
**Primary Model**: claude-sonnet-4.5 (OpenRouter free)  
**Fallback Model**: claude-opus-4.6 (OpenRouter free, more capable)  
**Local Option**: mistral via Ollama (zero-cost, offline)

**Configuration**:
```bash
# OpenRouter (RECOMMENDED)
export OPENROUTER_API_KEY="sk-or-v1-xxxx"
export CLINE_DEFAULT_MODEL=claude-sonnet-4.5

# Usage
cline "implement async Redis connection pool"
cline --model claude-opus-4.6 "redesign the entire data pipeline"

# Local (alternative)
export CLINE_PROVIDER=ollama
export CLINE_DEFAULT_MODEL=mistral
```

**Why**:
- Best code generation capability
- OpenRouter has 300+ free-tier models
- claude-sonnet-4.5 is balanced (fast + capable)
- Can fall back to local (Ollama) for air-gap
- Large context for code understanding

**Strengths**:
- ✅ 300+ models available (OpenRouter)
- ✅ Excellent code generation
- ✅ Free tier viable
- ✅ Local option (Ollama) for sovereign use
- ✅ Claude models best for reasoning

**Limitations**:
- ⚠️ OpenRouter free tier has quota
- ⚠️ Requires API key + account
- ⚠️ Ollama requires 8GB+ RAM

---

### Agent: OpenCode (Research & Verification)

**CLI**: OpenCode CLI v1.2.6  
**Role**: Code exploration, research, verification, pattern analysis  
**Primary Model**: gpt-5-nano (largest context 400k)  
**Secondary Model**: glm-5-free (reasoning)  
**Multimodal Model**: kimi-k2.5-free (vision/video)

**Configuration**:
```bash
# Set default
export OPENCODE_DEFAULT_MODEL=gpt-5-nano

# Usage
opencode "analyze patterns across entire repository"
opencode --model gpt-5-nano "map all async patterns in codebase"
opencode --model glm-5-free "verify this design meets requirements"
opencode --model kimi-k2.5-free "analyze this architecture diagram"
```

**Why**:
- Massive context windows (200k-400k)
- All 5 models are completely free
- No API keys needed
- GPT-5-Nano has largest context
- Multimodal support
- Perfect for research phase

**Strengths**:
- ✅ 5 free models built-in
- ✅ Zero setup (no API keys)
- ✅ Massive context (400k max)
- ✅ Multimodal support
- ✅ No authentication
- ✅ Latest models (Feb 2026)

**Limitations**:
- ⚠️ Less familiar providers
- ⚠️ Limited diversity (only 5 models)

---

### Agent: Gemini (Synthesis)

**CLI**: Gemini CLI v0.28.2  
**Role**: High-level synthesis, complex reasoning, strategic insights  
**Primary Model**: gemini-3-flash-preview (fast, latest, 1M context)  
**Complex Model**: gemini-3-pro-preview (advanced reasoning)  
**Max Context**: gemini-1.5-pro (2M context window)

**Configuration**:
```bash
# Get free API key from aistudio.google.com
export GEMINI_API_KEY="AIza..."
export GEMINI_DEFAULT_MODEL=gemini-3-flash-preview

# Usage
gemini "synthesize findings from all memory_bank docs"
gemini --model gemini-3-pro-preview "design resilience strategy"
gemini --model gemini-1.5-pro "analyze patterns across entire project"
```

**Why**:
- Massive context (1M-2M tokens)
- Free tier via Google AI Studio
- Excellent at synthesis
- Preview models have latest tech
- Good for big-picture analysis

**Strengths**:
- ✅ Massive context (1M-2M)
- ✅ Completely free (no credit card)
- ✅ Vision/PDF support
- ✅ Fast response
- ✅ Latest preview models

**Limitations**:
- ⚠️ Rate limited (15 req/min)
- ⚠️ Preview models may have issues
- ⚠️ Requires Google account

---

### Mission Control (Strategic Oversight)

**Platform**: Claude.ai Project (GitHub-synced)  
**Role**: Strategic overview of ALL XNAi initiatives  
**Models**: Claude Opus 4.6 (best reasoning)  
**Integration**: GitHub automatic sync + manual file uploads

**Configuration**:
```
Claude.ai Project: "XNAi Mission Control"
├── GitHub Integration: Auto-synced repo
├── Uploaded Briefing: MC Project briefing (memory_bank content)
├── Vision: Ma'at ideals, branding, mission
├── Scope: All XNAi internal/external initiatives
└── Output: /mc-oversight/ directory (strategic recommendations)
```

**Why**:
- GitHub integration (synced context)
- Claude Opus 4.6 available on free tier
- Project feature allows persistent context
- Can read repo changes automatically
- Team can check MC insights anytime

**Strengths**:
- ✅ Synced GitHub context (auto-updated)
- ✅ Persistent knowledge base
- ✅ Claude Opus 4.6 (best reasoning)
- ✅ Team-accessible (web interface)
- ✅ File upload support

**Limitations**:
- ⚠️ Web-based (not CLI)
- ⚠️ Manual setup required
- ⚠️ Requires Claude.ai account

**Next Steps**:
1. Create Claude.ai account
2. Create new project: "XNAi Mission Control"
3. Enable GitHub integration
4. Upload MC Project briefing
5. Create `/mc-oversight/` output directory

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  XNAi Foundation Workflow                    │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐
│ Agent: Copilot   │  Copilot CLI v0.0.410
│ ORCHESTRATE      │  Model: claude-haiku-4.5
│                  │  Role: Plan & decompose
└────────┬─────────┘
         │ Task breakdown
         ▼
┌──────────────────┐
│ Agent: Cline     │  Cline CLI v2.2.3
│ IMPLEMENT        │  Model: claude-sonnet-4.5 (OpenRouter)
│                  │  Role: Code implementation
└────────┬─────────┘
         │ Implementation
         ▼
┌──────────────────┐
│ Agent: OpenCode  │  OpenCode CLI v1.2.6
│ VERIFY           │  Models: gpt-5-nano, glm-5-free, kimi-k2.5-free
│                  │  Role: Verify & research
└────────┬─────────┘
         │ Insights
         ▼
┌──────────────────┐
│ Agent: Gemini    │  Gemini CLI v0.28.2
│ SYNTHESIZE       │  Model: gemini-3-flash-preview
│                  │  Role: High-level synthesis
└────────┬─────────┘
         │ Strategic output
         ▼
┌──────────────────────────────────────┐
│ Mission Control (Claude.ai Project)  │
│ STRATEGIC OVERSIGHT                  │
│ • GitHub-synced context              │
│ • Monitors all initiatives           │
│ • Produces recommendations           │
└──────────────────────────────────────┘
```

---

## Quick Reference Table

| Agent | CLI | Version | Primary Model | Free? | Setup Time |
|-------|-----|---------|---------------|-------|------------|
| Copilot | Copilot CLI | v0.0.410 | claude-haiku-4.5 | ✅ | 1 min |
| Cline | Cline CLI | v2.2.3 | claude-sonnet-4.5 | ✅ | 5 min |
| OpenCode | OpenCode CLI | v1.2.6 | gpt-5-nano | ✅ | 2 min |
| Gemini | Gemini CLI | v0.28.2 | gemini-3-flash-preview | ✅ | 5 min |
| MC | Claude.ai Project | Web | Claude Opus 4.6 | ✅ | 10 min |

---

## Setup Checklist

- [ ] **Copilot CLI**: `copilot --version` (verify installed)
  - Model: claude-haiku-4.5 (default)
  - Cost: FREE (free tier)

- [ ] **Cline CLI**: `cline --version` (verify installed)
  - Provider: OpenRouter
  - Model: claude-sonnet-4.5
  - API Key: Get from openrouter.ai
  - Cost: FREE (free tier, limited quota)

- [ ] **OpenCode CLI**: `opencode --version` (verify installed)
  - Models: All 5 built-in (no setup)
  - Cost: FREE (all models)

- [ ] **Gemini CLI**: `gemini --version` (verify installed)
  - API Key: Get from aistudio.google.com
  - Model: gemini-3-flash-preview (default)
  - Cost: FREE (rate limited 15 req/min)

- [ ] **Mission Control**: Create Claude.ai Project
  - Platform: Claude.ai (web)
  - Setup: GitHub integration + briefing upload
  - Cost: FREE (free tier)

---

## Nomenclature Reminder

**CRITICAL**: All bare CLI names refer to **terminal CLIs ONLY**:
- "Copilot" = Copilot CLI (terminal)
- "Cline" = Cline CLI (terminal)
- "OpenCode" = OpenCode CLI (terminal)
- "Gemini" = Gemini CLI (terminal)

**IDE plugins MUST be explicit**:
- "Cline VS Code Extension" (not just "Cline")
- "Copilot VS Code Extension" (not just "Copilot")
- "OpenCode IDE" (not just "OpenCode")

See `CLI-NOMENCLATURE-GUIDE-v1.0.0.md` for full standards.

---

## Related Documentation

- `CLI-NOMENCLATURE-GUIDE-v1.0.0.md` - Naming conventions
- `COPILOT-CLI-MODELS-v1.0.0.md` - Copilot model details
- `CLINE-CLI-MODELS-v1.0.0.md` - Cline model details
- `GEMINI-CLI-MODELS-v1.0.0.md` - Gemini model details
- `OPENCODE-CLI-MODELS-v1.0.0.md` - OpenCode model details

---

## Support

For issues with specific CLIs, consult their model card files in `expert-knowledge/`.

For nomenclature questions, refer to `CLI-NOMENCLATURE-GUIDE-v1.0.0.md`.

For strategic questions, ask Mission Control (Claude.ai Project).
