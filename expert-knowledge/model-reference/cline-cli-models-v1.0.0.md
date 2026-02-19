---
title: Cline IDE Free-Tier Models Reference
version: 1.0.0
last_updated: 2026-02-17
status: active
persona_focus: "Cline users, IDE-based engineers, VS Code developers"
ma_at_ideals: [7, 18, 41]
cost_status: "Mix of free & paid (free tier robust)"
---

# Cline IDE Free-Tier Models – Complete Reference

**Version**: 1.0.0  
**Date**: 2026-02-17  
**Provider**: Cline IDE Extension + Third-party API providers  
**Status**: ✅ Production-Ready  

---

## Overview

Cline is a VS Code extension that orchestrates autonomous coding tasks via API-routed frontier models. Unlike local inference, Cline delegates to provider APIs (Moonshot, OpenAI, Anthropic, etc.) but provides a unified interface within VS Code. This document catalogs the **free-tier models** available to Cline users as of Feb 2026.

| Model | Provider | Context | Output | Reasoning | Tool-Use | Vision | Free Tier | Cost |
|-------|----------|---------|--------|-----------|----------|--------|-----------|------|
| **Kimi K2.5** | Moonshot | 262k | 262k | ✅ | ✅ | ✅ | Yes (~10 calls/day) | FREE |
| **Claude Haiku 4.5** | Anthropic | 128k | 4k | ✅ | ✅ | ✅ | Yes (preview) | FREE |
| **Claude Opus 4.6** | Anthropic | 128k | 4k | ✅ | ✅ | ✅ | Via GitHub Copilot | FREE |
| **GPT-5 Mini** | OpenAI | 128k | 4k | ✅ | ✅ | ✅ | Limited | FREE* |
| **GPT-5.1-Codex** | OpenAI | 128k | 8k | ✅ | ✅ | ❌ | Limited | FREE* |
| **Grok Code Fast 1** | xAI | 128k | 8k | ✅ | ✅ | ❌ | Preview | FREE |
| **Gemini 2.5 Pro** | Google | 128k | 4k | ✅ | ✅ | ✅ | Preview | FREE |
| **Trinity Large** | Arcee | 128k | 4k | ✅ | ✅ | ❌ | Preview | FREE |
| **MiniMax M2.1** | MiniMax | 128k | 4k | ✅ | ✅ | ❌ | Preview | FREE |

**Legend**: *LIMITED = very small daily quotas; FREE = generous free-tier  

---

## Primary Free-Tier Models

### 1. Kimi K2.5 (via Moonshot)

**Provider**: Moonshot AI  
**Cline Integration**: Via API key (moonshot.ai)  
**Context**: 262k tokens  
**Output**: 262k tokens  

#### Overview
Native frontier model accessible through Cline with multimodal vision, agentic reasoning, and strong coding capabilities. Direct provider integration (not via GitHub proxy).

#### Capabilities
| Capability | Rating | Notes |
|------------|--------|-------|
| Code Generation | ⭐⭐⭐⭐⭐ | Best-in-class for VS Code IDE context |
| Visual-to-Code | ⭐⭐⭐⭐⭐ | Screenshots → full implementations |
| Agentic Autonomy | ⭐⭐⭐⭐⭐ | Excellent tool-use & planning |
| Context Window | ⭐⭐⭐⭐⭐ | 262k ideal for large projects |
| Speed | ⭐⭐⭐ | 20-40s typical (API latency) |
| Reasoning | ⭐⭐⭐⭐⭐ | Frontier-class |

#### Strengths
- ✅ Largest context in free tier (262k)
- ✅ Exceptional for complex refactors
- ✅ Visual coding (UI specs → code)
- ✅ Strong agentic planning
- ✅ Free daily quota (no credit card)

#### Weaknesses
- ❌ Limited daily quota (~10 calls/day)
- ❌ Higher latency (API-dependent)
- ❌ Requires Moonshot API key

#### Cline Configuration
```json
{
  "provider": "moonshot",
  "model": "kimi-k2.5-free",
  "api_key": "sk-...",
  "max_tokens": 4000,
  "temperature": 0.7
}
```

#### When to Use in Cline
- Complex refactoring tasks requiring 262k context
- Visual design specifications → implementation
- Multi-file coordinate changes
- When daily quota allows

---

### 2. Claude Haiku 4.5 (via Anthropic Preview)

**Provider**: Anthropic  
**Cline Integration**: Via Anthropic API key  
**Context**: 128k tokens  
**Output**: 4k tokens  
**Status**: Preview/Free

#### Overview
Lightweight Claude model with extended thinking capability. Fastest inference with extended thinking, good for quick iterations and architectural decisions.

#### Capabilities
| Capability | Rating | Notes |
|------------|--------|-------|
| Speed | ⭐⭐⭐⭐⭐ | Fastest Claude variant |
| Coding | ⭐⭐⭐⭐ | Good for standard patterns |
| Thinking Mode | ⭐⭐⭐⭐ | Excellent for complex decisions |
| Context | ⭐⭐⭐⭐ | 128k adequate for most files |
| Cost | ⭐⭐⭐⭐⭐ | Free via preview |

#### Strengths
- ✅ Very fast (2-5s typical)
- ✅ Extended thinking for reasoning
- ✅ 128k context sufficient
- ✅ Free preview access
- ✅ Anthropic reliability

#### Weaknesses
- ❌ Limited output (4k tokens)
- ❌ Preview status (may change)
- ❌ Weaker on very complex reasoning vs Opus
- ❌ Requires Anthropic API key

#### Cline Configuration
```json
{
  "provider": "anthropic",
  "model": "claude-3-5-haiku-20250514",
  "api_key": "sk-ant-...",
  "thinking": true,
  "budget_tokens": 2000
}
```

#### When to Use in Cline
- Daily driver for iterative coding
- Quick architectural decisions
- Testing & validation
- When latency matters

---

### 3. Claude Opus 4.6 (via GitHub Copilot)

**Provider**: Anthropic (via GitHub proxy)  
**Cline Integration**: Via GitHub Copilot API  
**Context**: 128k tokens  
**Output**: 4k tokens  
**Status**: Free via GitHub Copilot subscription

#### Overview
Frontier Claude with extended thinking, available free through GitHub Copilot integration. Most capable Claude variant in Cline's free tier.

#### Capabilities
| Capability | Rating | Notes |
|------------|--------|-------|
| Reasoning | ⭐⭐⭐⭐⭐ | Frontier-class |
| Code Generation | ⭐⭐⭐⭐⭐ | Best-in-class |
| Thinking Mode | ⭐⭐⭐⭐⭐ | Deep reasoning |
| Multi-File | ⭐⭐⭐⭐⭐ | Excellent coordination |
| Reliability | ⭐⭐⭐⭐⭐ | Anthropic quality |

#### Strengths
- ✅ Most capable Claude model
- ✅ Extended thinking with deep reasoning
- ✅ Free via Copilot subscription (if you have it)
- ✅ Excellent for complex tasks
- ✅ 128k context for large files

#### Weaknesses
- ❌ Requires GitHub Copilot subscription
- ❌ API routing adds latency
- ❌ Limited output (4k tokens)
- ❌ Quota limits (Copilot dependent)

#### Cline Configuration
```json
{
  "provider": "github-copilot",
  "model": "claude-opus-4.6",
  "thinking": true,
  "budget_tokens": 3000
}
```

#### When to Use in Cline
- Most complex coding tasks
- When deep reasoning required
- Multi-file architectural changes
- Premium choice (if Copilot subscribed)

---

### 4. GPT-5 Mini (via OpenAI)

**Provider**: OpenAI  
**Cline Integration**: Via OpenAI API key  
**Context**: 128k tokens  
**Output**: 4k tokens  
**Status**: Free tier limited

#### Overview
Lightweight OpenAI model, efficient and fast. Free tier has daily limits but includes basic coding capability.

#### Capabilities
| Capability | Rating | Notes |
|------------|--------|-------|
| Speed | ⭐⭐⭐⭐⭐ | Very fast inference |
| Coding | ⭐⭐⭐⭐ | Solid for standard code |
| Cost | ⭐⭐⭐ | Free tier limited |
| Reasoning | ⭐⭐⭐ | Adequate for practical tasks |

#### Strengths
- ✅ Very fast response times
- ✅ Free tier available
- ✅ Good for prototyping
- ✅ Reliable OpenAI quality

#### Weaknesses
- ❌ Small daily quotas in free tier
- ❌ Limited reasoning depth
- ❌ 4k output limit
- ❌ Not ideal for complex problems

#### When to Use in Cline
- Quick prototyping sessions
- Simple code generation
- When quota is available
- Speed-critical iterations

---

### 5. GPT-5.1-Codex (via OpenAI)

**Provider**: OpenAI  
**Cline Integration**: Via OpenAI API key  
**Context**: 128k tokens  
**Output**: 8k tokens  
**Specialization**: Code-optimized

#### Overview
Code-specialized variant of GPT-5.1, optimized for software engineering tasks. Better output limit (8k) than standard variants.

#### Capabilities
| Capability | Rating | Notes |
|------------|--------|-------|
| Code Generation | ⭐⭐⭐⭐⭐ | Purpose-built for coding |
| Speed | ⭐⭐⭐⭐ | Fast (slower than Mini) |
| Output | ⭐⭐⭐⭐ | 8k tokens (better than Mini) |
| Tool-Use | ⭐⭐⭐⭐ | Good agentic capability |

#### Strengths
- ✅ Code-optimized architecture
- ✅ 8k output (larger than base GPT-5 Mini)
- ✅ Free tier available
- ✅ Good for SWE-Bench style tasks

#### Weaknesses
- ❌ Free tier quota limits
- ❌ No vision capability
- ❌ Requires OpenAI API key

#### When to Use in Cline
- Pure coding tasks
- When larger output needed
- Code-specific optimizations
- Engineering-focused work

---

### 6. Grok Code Fast 1 (via xAI)

**Provider**: xAI (Elon Musk's AI)  
**Cline Integration**: Via xAI API  
**Context**: 128k tokens  
**Output**: 8k tokens  
**Status**: Preview (free)

#### Overview
Frontier code-specialized model from xAI, optimized for software engineering. Fast inference with good coding capability.

#### Capabilities
| Capability | Rating | Notes |
|------------|--------|-------|
| Code Quality | ⭐⭐⭐⭐⭐ | Frontier coding benchmark |
| Speed | ⭐⭐⭐⭐⭐ | Very fast (xAI infrastructure) |
| Tool-Use | ⭐⭐⭐⭐ | Good agentic support |
| Reasoning | ⭐⭐⭐⭐ | Solid general reasoning |

#### Strengths
- ✅ Code-optimized frontier model
- ✅ Very fast inference
- ✅ Free preview status
- ✅ 8k output limit
- ✅ Good for complex coding

#### Weaknesses
- ❌ Preview status (may change)
- ❌ New provider (less proven)
- ❌ Smaller community
- ❌ No vision capability

#### When to Use in Cline
- Complex coding challenges
- When speed + quality matters
- Code-specific engineering tasks
- Alternative frontier option to Kimi

---

### 7. Gemini 2.5 Pro (via Google)

**Provider**: Google  
**Cline Integration**: Via Google AI API  
**Context**: 128k tokens  
**Output**: 4k tokens  
**Status**: Preview (free)

#### Overview
Google's frontier model with multimodal vision. Excellent for visual-to-code workflows and complex analysis.

#### Capabilities
| Capability | Rating | Notes |
|------------|--------|-------|
| Multimodal Vision | ⭐⭐⭐⭐⭐ | Best-in-class |
| Reasoning | ⭐⭐⭐⭐ | Solid frontier reasoning |
| Code Generation | ⭐⭐⭐⭐ | Good but not specialized |
| Audio Understanding | ⭐⭐⭐⭐ | Novel capability |

#### Strengths
- ✅ Best multimodal vision in free tier
- ✅ Audio understanding (unique)
- ✅ Free preview access
- ✅ Google reliability
- ✅ Good for design handoff workflows

#### Weaknesses
- ❌ Preview status
- ❌ 4k output limit
- ❌ Not code-specialized
- ❌ Requires Google API key

#### When to Use in Cline
- Design/UI mockup → code generation
- Visual specifications
- Multi-modal analysis tasks
- When vision is critical

---

## Secondary Free Models

### Trinity Large (Arcee) - Code-Specialized
- **Specialization**: Agentic coding, SWE-Bench optimized
- **Context**: 128k
- **Status**: Preview/Free
- **Best For**: Deep repo surgery, multi-file refactors

### MiniMax M2.1 (MiniMax) - Lightweight
- **Specialization**: Lightweight coding, fast
- **Context**: 128k
- **Status**: Preview/Free
- **Best For**: Quick iterations, interactive sessions

---

## Cline Model Selection Strategy

### By Task Type in VS Code

**Quick Code Generation**
1. GPT-5.1-Codex (if quota available)
2. Grok Code Fast 1
3. MiniMax M2.1

**Complex Refactoring**
1. Kimi K2.5 (262k context!)
2. Claude Opus 4.6
3. Claude Haiku 4.5 (extended thinking)

**Visual Design → Code**
1. Kimi K2.5 (visual + 262k context)
2. Gemini 2.5 Pro
3. Claude Opus 4.6

**Interactive Iteration**
1. Claude Haiku 4.5 (fast + thinking)
2. Grok Code Fast 1
3. GPT-5 Mini

**Deep Analysis & Planning**
1. Claude Opus 4.6 (thinking mode)
2. Kimi K2.5
3. Grok Code Fast 1

### Escalation Ladder for Cline
```
Simple change → GPT-5.1-Codex
Standard refactor → Haiku (thinking)
Complex refactor → Grok Code Fast 1
Multi-file architect → Kimi K2.5
Design to code → Gemini 2.5 Pro
Deep reasoning needed → Claude Opus 4.6
```

---

## Free-Tier Quota Reality Check

| Model | Daily Free Quota | Duration | Renewal |
|-------|-----------------|----------|---------|
| Kimi K2.5 | ~10 calls | 24h | Daily 00:00 UTC |
| Claude Haiku | Preview (generous) | Unlimited | Via subscription |
| Claude Opus | Via GitHub Copilot | Copilot limit | Monthly |
| GPT-5 Mini | $5/month free | Monthly | Calendar month |
| GPT-5.1-Codex | $5/month free | Monthly | Calendar month |
| Grok Code Fast | Preview (generous) | Ongoing | While in preview |
| Gemini 2.5 Pro | Preview (generous) | Ongoing | While in preview |
| Trinity Large | Preview (unlimited) | Ongoing | While in preview |
| MiniMax M2.1 | Preview (unlimited) | Ongoing | While in preview |

**Note**: Check Cline settings → API keys → Rate Limits for live quota status

---

## Integration with XNAi Foundation

### Cline Role in Multi-Agent Stack
```
OpenCode (research)
    ↓
Cline (VS Code IDE implementation)
    ↓
Copilot (validation + supplementary coding)
    ↓
Gemini CLI (final verification)
```

### When to Use Cline vs Other Agents
| Task | Cline | OpenCode | Copilot | Gemini |
|------|-------|----------|---------|--------|
| VS Code integration | ✅ | ❌ | ✅ | ❌ |
| Terminal first | ❌ | ✅ | ✅ | ✅ |
| Large context (262k) | ✅ | ✅ | ❌ | ✅ |
| IDE refactoring | ✅ | ❌ | ✅ | ❌ |
| Multi-model research | ❌ | ✅ | ❌ | ❌ |

### Recommended Cline Workflow for XNAi
1. **Daily coding**: Claude Haiku 4.5 (fast + thinking)
2. **Complex tasks**: Kimi K2.5 (262k context)
3. **Design handoff**: Gemini 2.5 Pro
4. **Code-heavy**: Grok Code Fast 1
5. **Second opinion**: Switch between models for validation

---

## Cline Configuration Template

```json
{
  "cline": {
    "default_model": "claude-3-5-haiku-20250514",
    "models": {
      "fast_path": "gpt-5.1-codex",
      "deep_analysis": "claude-opus-4.6",
      "large_context": "kimi-k2.5-free",
      "visual_tasks": "gemini-2.5-pro",
      "code_specialist": "grok-code-fast-1"
    },
    "api_keys": {
      "anthropic": "sk-ant-...",
      "openai": "sk-...",
      "moonshot": "sk-...",
      "google": "...",
      "xai": "..."
    }
  }
}
```

---

## Ma'at Alignment

**Ideal 7 (Truth)**: Multiple models in Cline enable verification through diverse implementations  
**Ideal 18 (Balance)**: Free-tier options balance cost with capability  
**Ideal 41 (Advance)**: Frontier models expand IDE capabilities through modern AI  

---

## Next Steps

1. ✅ Document Cline free-tier models (THIS DOC)
2. ⏳ Document Copilot CLI models via GitHub integration
3. ⏳ Create unified CLI model selection strategy
4. ⏳ Update agent role assignments with Cline model preferences
5. ⏳ Update core context with Cline integration guidance

---

**Status**: ✅ **Complete - Production Ready**  
**Last Updated**: 2026-02-17  
**Maintained By**: Cline-Kat (implementation), Copilot (documentation)  
**Related Documents**:
- `opencode-free-models-v1.0.0.md`
- `copilot-cli-models-v1.0.0.md`
- `cli-model-selection-strategy-v1.0.0.md`
