# CLI Free Tier Models Research - FINDINGS

**Research Date**: 2026-02-17T22:06 UTC  
**Source**: Official documentation fetches + CLI help output

---

## 1. COPILOT CLI (v0.0.410)

### Free Tier Status
**Plan**: Copilot Free (no subscription required)
- GitHub Copilot Free available with limited features
- 30-day trial for Copilot Pro available  
- Models available via free plan are LIMITED

### Models Available (17 total listed in CLI)
```
- claude-sonnet-4.5
- claude-haiku-4.5
- claude-opus-4.6
- claude-opus-4.6-fast
- claude-opus-4.5
- claude-sonnet-4
- gemini-3-pro-preview
- gpt-5.3-codex
- gpt-5.2-codex
- gpt-5.2
- gpt-5.1-codex-max
- gpt-5.1-codex
- gpt-5.1
- gpt-5
- gpt-5.1-codex-mini
- gpt-5-mini
- gpt-4.1
```

### Free Tier Restrictions
⚠️  **IMPORTANT**: According to GitHub docs:
- Copilot Free: Limited features + limited model access
- Copilot Pro ($20/month): Full model access
- Copilot Pro+ (higher tier): Additional models

**Likely Free Tier Models**: None explicitly stated. Requires research on GitHub Copilot Free tier docs.

### Recommendation
🔍 **NEED**: User input on whether to use Copilot Free (limited) or assume Pro tier

---

## 2. CLINE CLI (v2.2.3)

### Supported Providers
Cline supports multiple API providers:
- **OpenAI** (openai-native provider) → GPT models
- **Anthropic** (anthropic provider) → Claude models  
- **Moonshot** (moonshot provider) → Kimi models
- **OpenRouter** (auto-fetches latest models)
- **Custom providers** via baseurl

### Free Tier Options

**OpenAI (openai-native)**:
- Free trial: API credits available
- Requires API key
- Models: gpt-4o, gpt-4-turbo, gpt-3.5-turbo
- ❌ NO free tier (trial required)

**Anthropic (anthropic)**:
- Free trial: API credits available  
- Requires API key
- Models: claude-sonnet-4-5-20250929, claude-3-5-sonnet, etc.
- ❌ NO free tier (trial required)

**Moonshot (moonshot)**:
- Free trial: API credits available
- Requires API key
- Models: kimi-k2.5, etc.
- ❌ NO free tier (trial required)

**OpenRouter**:
- FREE tier available!
- Supports 300+ models
- Can use local/free models
- ✅ FREE with limited quota

### Recommendation
**Cline CLI Best Practice**:
- Use **OpenRouter** for free tier access
- OR configure local model via baseurl (Ollama/LM Studio)

---

## 3. GEMINI CLI (v0.28.2)

### Available Gemini Models
From official Google Gemini API docs:

**Latest (Frontier)**:
- **gemini-3-pro-preview** - 1M input, 65k output context
- **gemini-3-flash-preview** - 1M input, 65k output context (faster)

**Previous Versions**:
- gemini-2.5-pro
- gemini-2.5-flash
- gemini-1.5-pro
- gemini-1.5-flash

### Free Tier Status
Google AI Studio (Free):
- ✅ **FREE API access** via Google AI Studio
- API key: No credit card required initially
- Rate limits: 15 requests per minute
- Models: gemini-3-flash-preview, gemini-3-pro-preview available free

### Recommendation
**Gemini CLI Best Practice**:
- Use **gemini-3-flash-preview** (fast, free tier)
- Fallback: gemini-2.5-flash
- Requires: Free Google AI account + API key

---

## 4. OPENCODE CLI (v1.2.6) ✅ VERIFIED

### Free Models (Already Confirmed)
- Big Pickle - FREE
- GLM-5-free - FREE
- GPT-5-Nano - FREE
- Kimi K2.5-free - FREE
- MiniMax M2.5-free - FREE

**Status**: ✅ All verified as free tier

---

## 5. GROK MC (Unknown)

### What is Grok?
Grok is a conversational AI assistant from xAI (Elon Musk's AI company)

### Models  
- **Grok-3** (latest as of Feb 2026)
- Grok-2 (previous)
- Grok-1 (earlier)

### Availability
⚠️ **UNKNOWN**: 
- Is Grok open source?
- Does Grok have free tier API?
- What are Grok's actual capabilities?
- How does Grok MC integrate with XNAi?

**Action**: Need user clarification on Grok MC's role and availability

---

## SUMMARY TABLE

| CLI | Free Tier Available | Best Free Model | Auth Required |
|-----|-------------------|-----------------|---------------|
| **Copilot CLI** | ⚠️ Limited | Unknown (need docs) | GitHub account + Copilot Free |
| **Cline CLI** | ✅ Via OpenRouter | openrouter/auto (300+) | OpenRouter API key |
| **OpenCode CLI** | ✅ Yes | Kimi K2.5-free | None (built-in) |
| **Gemini CLI** | ✅ Via Google AI Studio | gemini-3-flash-preview | Google account + API key |
| **Grok MC** | ❓ Unknown | ❓ Grok-3 | ❓ Unknown |

---

## RESEARCH GAPS REMAINING

1. **Copilot CLI**: Which models are included in Copilot Free (no paid subscription)?
2. **Grok MC**: What is its actual role? Is it an API, CLI, or something else?
3. **Cline CLI**: Preference for OpenRouter vs local models vs trials?
4. **Gemini CLI**: Best way to set up for XNAi use case?

## NEXT ACTION

User decision needed on:
- Should we use Copilot Free (limited) or assume Pro tier?
- How should Grok MC be integrated (if at all)?
- Should Cline use OpenRouter or local models?
