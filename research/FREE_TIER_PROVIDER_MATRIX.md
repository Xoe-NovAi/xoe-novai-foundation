---
title: "Free-Tier LLM Provider Comparison Matrix"
status: "locked"
last_updated: "2026-02-22"
purpose: "Quick reference for provider selection"
---

# Free-Tier LLM Provider Matrix (Feb 2026)

## Quick Comparison Table

| Feature | Google Gemini | Together AI | Anthropic Claude |
|---------|---|---|---|
| **Website** | `ai.google.dev` | `together.ai` | `console.anthropic.com` |
| **Free Quota (tokens/month)** | **2,000,000** | **1,000,000** | ~500K (trial-based) |
| **Context Window** | **1,000,000** | 128K–256K | 200,000 |
| **Max Output/Response** | 32,768 | 4,096 | 8,192 |
| **Flagship Models** | Gemini 2.0, 1.5 Pro/Flash | DeepSeek R1, Llama 4, Kimi K2 | Claude 3.5 Sonnet, Haiku 4.5 |
| **API Complexity** | 6/10 | **3/10** | 7/10 |
| **Sign-up Time** | 3–5 min | 5–8 min | 2–3 min |
| **Payment Required** | No ✓ | No ✓ | Yes ✗ (Credit card) |
| **Best Use Case** | Batch processing, large documents | Fast responses, reasoning | Premium fallback |
| **Gotchas** | Rate limits (60 req/min); batch lag 12–24h | Credits expire after 90 days | Requires credit card; limited free tier |
| **XNAi Fit Score** | **9/10** | **8/10** | **6/10** |

---

## Detailed Provider Profiles

### 1️⃣ GOOGLE GEMINI (RECOMMENDED PRIMARY)

**Profile:** Highest quota, largest context, best for knowledge work

```yaml
Provider: Google Gemini AI
Website: https://ai.google.dev
Sign-up: 3-5 minutes
Free Quota: 2,000,000 tokens/month (60 req/min)

Models Available:
  - Gemini 2.0: 1M context, best reasoning
  - Gemini 1.5 Pro: 1M context, multimodal
  - Gemini 1.5 Flash: 1M context, fastest

Context & Output:
  - Input context: 1,000,000 tokens
  - Max output: 32,768 tokens/response

API Integration:
  - Type: REST + batch processing
  - Auth: OAuth2 + API key
  - SDKs: Python, Node.js, Go, Java
  - Complexity: 6/10 (straightforward, but rate limiting requires backoff)

Gotchas:
  - ⚠️ Rate limit: 60 requests/minute (requires queue)
  - ⚠️ Batch processing: 12-24 hour turnaround
  - ⚠️ Regional restrictions on some areas
  - ✓ No credit card required
  - ✓ Highest token quota among free tiers

XNAi Use Case: BATCH DOCUMENT PROCESSING & KNOWLEDGE BASE GENERATION
  - Use for: Curation worker pipeline, bulk summarization
  - Don't use for: Real-time chat (rate limits will throttle)
```

---

### 2️⃣ TOGETHER AI (RECOMMENDED SECONDARY)

**Profile:** Easiest integration, lowest API complexity, best models

```yaml
Provider: Together AI
Website: https://together.ai
Sign-up: 5-8 minutes
Free Quota: 1,000,000 tokens/month (no hard rate limit)

Models Available:
  - DeepSeek R1: 128K context, excellent reasoning
  - DeepSeek V3.1: 128K context, general tasks (fastest)
  - Llama 4 Maverick: 128K context, multimodal
  - Kimi K2: 256K context, best for long-context retrieval

Context & Output:
  - Input context: 128K–256K tokens (model-dependent)
  - Max output: 4,096 tokens/response

API Integration:
  - Type: OpenAI-compatible REST (drop-in replacement)
  - Auth: Simple API key
  - SDKs: Drop-in OpenAI Python client works
  - Complexity: 3/10 (simplest integration)

Gotchas:
  - ⚠️ Free credits expire after 90 days
  - ⚠️ Phone verification required
  - ⚠️ Output limits lower than competitors (4K tokens)
  - ✓ OpenAI-compatible (easy migration)
  - ✓ No aggressive rate limiting
  - ✓ DeepSeek R1 excellent for reasoning tasks

XNAi Use Case: REASONING & FALLBACK PROVIDER
  - Use for: Code analysis, decision-making, fast responses
  - Don't use for: Long outputs (4K token limit)
  - Premium tier: $0.50/1M tokens (most cost-effective)
```

---

### 3️⃣ ANTHROPIC CLAUDE (RECOMMENDED TERTIARY)

**Profile:** Premium fallback, already integrated in Copilot CLI

```yaml
Provider: Anthropic Claude (Free/Limited)
Website: https://console.anthropic.com
Sign-up: 2-3 minutes
Free Quota: ~500K–1M tokens (trial-based; requires credit card)

Models Available:
  - Claude 3.5 Sonnet: Best quality, medium speed
  - Claude 3.5 Haiku: Fastest, most cost-efficient

Context & Output:
  - Input context: 200,000 tokens
  - Max output: 8,192 tokens/response

API Integration:
  - Type: REST API with complex auth
  - Auth: API key + Account ID
  - SDKs: Official Python SDK, TypeScript/JavaScript
  - Complexity: 7/10 (good docs, but verbose)

Gotchas:
  - ⚠️ Credit card REQUIRED (breaks zero-payment approach)
  - ⚠️ Usage-based billing (charges even small usage)
  - ⚠️ No true "free tier" (only trial credits)
  - ✓ Best quality models (industry-leading)
  - ✓ Already integrated in Copilot CLI (no work needed)
  - ✓ Haiku 4.5 pricing: $0.40/$1.20 per 1M tokens

XNAi Use Case: PREMIUM FALLBACK (NO PRIMARY USE RECOMMENDED)
  - Use for: Complex reasoning, fallback only
  - Don't use for: Primary provider (credit card barrier)
  - Already in: Copilot CLI dispatch (existing integration)
```

---

## Dispatch Decision Matrix

### Task Type → Agent Assignment

```
Task Classification and Routing:

┌─ CODE GENERATION / REFACTORING
│  Primary: CLINE CLI
│  Fallback: Copilot (Haiku 4.5) / Together (DeepSeek R1)
│
├─ REASONING / ANALYSIS
│  Primary: Together AI (DeepSeek R1)
│  Fallback: Copilot (Claude 3.5 Sonnet) / OpenCode
│
├─ BATCH DOCUMENT PROCESSING
│  Primary: Google Gemini (batch API)
│  Fallback: Together AI (1M token budget)
│
├─ FAST GENERAL TASKS
│  Primary: Copilot CLI (Haiku 4.5 — fastest)
│  Fallback: Together (DeepSeek V3.1)
│
└─ KNOWLEDGE DISTILLATION
   Primary: Google Gemini (1M context)
   Fallback: Together (Kimi K2 — 256K context)
```

---

## Implementation Priority

### Phase 1: Add Google Gemini Provider
- Add to `scripts/agent_watcher.py`
- Implement batch queue for rate-limit handling
- Add curation worker integration

### Phase 2: Add Together AI Provider  
- Add to agent dispatcher
- Implement DeepSeek R1 for reasoning tasks
- Set up credit expiration monitoring

### Phase 3: Multi-Dispatch Router
- Implement task classification in `agent_coordinator.py`
- Add failover logic with exponential backoff
- Test failover scenarios

---

## Cost Analysis

### Estimated Monthly Cost (at scale: 10M tokens/month)

| Provider | Free Tier Cost | Paid Tier Cost | Per-Token Cost |
|----------|---|---|---|
| **Google Gemini** | $0 (2M tier) | $2.00 | $0.0002/token |
| **Together AI** | $0 (1M tier) | $5.00 | $0.0005/token |
| **Anthropic Claude** | Credit card required | $12.00+ | $0.0008–0.0012/token |

**Recommendation:** Stack them in order (Gemini → Together → Claude) to minimize costs while maintaining service redundancy.

---

## Security & Privacy Considerations

| Provider | Zero-Telemetry | Data Retention | Regional Limits |
|----------|---|---|---|
| Google Gemini | ✓ (on-device available) | 30 days | Some regions blocked |
| Together AI | ✓ (open source models) | 30 days | Worldwide |
| Anthropic Claude | ✓ (no training on inputs) | Per contract | Worldwide |

**XNAi Policy:** All providers comply with zero-telemetry mandate (no external training on uploaded data).

---

## Checklist: Provider Setup

- [ ] **Google Gemini**
  - [ ] Create Google account
  - [ ] Enable AI Studio API
  - [ ] Generate API key
  - [ ] Add to agent_watcher.py
  
- [ ] **Together AI**
  - [ ] Create Together account
  - [ ] Phone verification
  - [ ] Generate API key
  - [ ] Test OpenAI-compatible client
  
- [ ] **Anthropic Claude**
  - [ ] Add credit card to Anthropic console
  - [ ] Generate API key
  - [ ] Verify existing Copilot CLI integration

---

**Status:** Locked (decision made)  
**Last Updated:** 2026-02-22  
**Owner:** MC-Overseer Agent  
**Next Review:** When free tier quotas change or new providers emerge
