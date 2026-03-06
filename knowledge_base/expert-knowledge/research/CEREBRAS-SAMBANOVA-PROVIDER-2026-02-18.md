# ---
# tool: cline
# model: claude-sonnet-4-6
# account: arcana-novai
# git_branch: main
# session_id: sprint7-2026-02-18
# version: v1.0.0
# created: 2026-02-18
# ---

# Cerebras & SambaNova: Critical New Free Tier Providers

**Research Date**: 2026-02-18
**Priority**: 🔴 HIGH — Immediate addition to free-providers-catalog.yaml
**Verdict**: Both providers offer genuinely free tiers with exceptional value

---

## Executive Summary

Two major AI infrastructure providers have emerged with **genuinely free API tiers** that significantly expand the XNAi stack's capabilities:

| Provider | Killer Feature | Free Models | Speed |
|----------|---------------|-------------|-------|
| **Cerebras** | Fastest inference on Earth | llama-3.3-70b, qwen-3-32b | 2,000-3,000 t/s |
| **SambaNova** | Full DeepSeek-R1 671B FREE | DeepSeek-R1, DeepSeek-V3, Llama models | Fast |

These are **not** limited trials — they're ongoing free tiers with generous daily limits.

---

## Cerebras Cloud

### Overview
- **URL**: cloud.cerebras.ai
- **API Endpoint**: `https://api.cerebras.ai/v1` (OpenAI-compatible)
- **SDK**: `pip install cerebras-cloud-sdk`
- **Architecture**: Wafer-Scale Engine (WSE) — purpose-built AI inference chip

### Free Tier
- **Cost**: Free signup, no credit card required
- **Credits**: ~$30 credit on signup; ongoing free tier after
- **Rate Limits**: ~10K-30K tokens/min during business hours (soft limits)

### Models Available (Free)
| Model ID | Context | Notes |
|----------|---------|-------|
| `llama-3.3-70b` | 128K | Best Llama model, exceptional quality |
| `llama-4-scout-17b-16e-instruct` | 128K | New Llama 4 Scout model |
| `qwen-3-32b` | 128K | Excellent coding model |

### Speed Comparison
| Provider | Tokens/Second (70B model) |
|----------|--------------------------|
| **Cerebras** | 2,000-3,000 t/s |
| Groq | ~800 t/s |
| Anthropic (Claude) | ~150 t/s |
| OpenAI (GPT-4) | ~80 t/s |

**Implication**: Cerebras is ~20x faster than Claude for similar-quality models. Real-time streaming at production scale.

### XNAi Integration
```yaml
# configs/model-router.yaml addition
cerebras:
  base_url: "https://api.cerebras.ai/v1"
  env_var: CEREBRAS_API_KEY
  free_models:
    - llama-3.3-70b
    - qwen-3-32b
  best_for:
    - fast_iteration
    - bulk_processing
    - real_time_streaming
```

### Use Cases
1. **Rapid iteration loops**: When you need instant feedback
2. **Bulk code generation**: High-volume tasks where speed matters
3. **Pipeline processing**: Pair with `mods` for fast AI pipelines
4. **Testing/experimentation**: Free tier encourages exploration

---

## SambaNova Cloud

### Overview
- **URL**: cloud.sambanova.ai
- **API Endpoint**: OpenAI-compatible
- **Architecture**: Custom Reconfigurable Dataflow Unit (RDU)

### Free Tier
- **Cost**: Free signup, no credit card required
- **Limits**: Generous daily limits (exact numbers vary)

### Models Available (Free)
| Model ID | Context | Notes |
|----------|---------|-------|
| `DeepSeek-R1` | 128K | **Full 671B parameter model** — not distilled |
| `DeepSeek-V3` | 128K | Frontier reasoning model |
| `Meta-Llama-3.1-405B-Instruct` | 128K | Largest open model |
| `Meta-Llama-3.3-70B-Instruct` | 128K | Standard Llama 70B |

### The DeepSeek-R1 671B Advantage
DeepSeek-R1 is the **best open reasoning model** available — comparable to Claude Opus for complex reasoning tasks. Having the full 671B parameter model (not a distilled version) for free is extraordinary.

**Use cases**:
- Architecture decisions
- Complex debugging
- Research synthesis
- Code review at depth
- Multi-step reasoning tasks

### XNAi Integration
```yaml
# configs/model-router.yaml addition
sambanova:
  base_url: "https://api.sambanova.ai/v1"
  env_var: SAMBANOVA_API_KEY
  free_models:
    - DeepSeek-R1
    - DeepSeek-V3
  best_for:
    - complex_reasoning
    - architecture_decisions
    - research_tasks
```

---

## Updated Free Rate Limit Waterfall

**Recommended order of fallback** (all free):

| Step | Provider | Model | Why |
|------|----------|-------|-----|
| 1 | Gemini CLI | gemini-2.0-flash | Best default — 1M context, 1500 req/day |
| 2 | OpenCode/Antigravity | claude-sonnet-4-6 | Coding quality, GitHub OAuth free |
| 3 | **SambaNova** | DeepSeek-R1 671B | Complex reasoning — **NEW** |
| 4 | **Cerebras** | llama-3.3-70b | Speed king — **NEW** |
| 5 | Groq | llama-3.3-70b | Fast inference |
| 6 | OpenRouter free | Kimi K2.5, GLM-5 | Frontier models |
| 7 | llama-cpp-python | Qwen3-0.6B | Local fallback |

---

## API Key Setup

### Cerebras
```bash
# Sign up at cloud.cerebras.ai
# Get API key from dashboard
export CEREBRAS_API_KEY="your-key-here"

# Test
curl https://api.cerebras.ai/v1/chat/completions \
  -H "Authorization: Bearer $CEREBRAS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama-3.3-70b", "messages": [{"role": "user", "content": "Hello"}]}'
```

### SambaNova
```bash
# Sign up at cloud.sambanova.ai
# Get API key from dashboard
export SAMBANOVA_API_KEY="your-key-here"
```

---

## Sovereignty Assessment

| Provider | Data Processing | Telemetry | Open Source | Sovereign-Compatible |
|----------|-----------------|-----------|-------------|---------------------|
| Cerebras | US-based cloud | Yes | No (proprietary chip) | ⚠️ Non-sovereign |
| SambaNova | US-based cloud | Yes | No (proprietary chip) | ⚠️ Non-sovereign |

**Note**: Both are US-based cloud providers with telemetry. For sovereign-sensitive work, continue using local models (llama-cpp-python, ollama). For non-sensitive tasks, these providers offer exceptional free value.

---

## Action Items

- [x] Research complete
- [ ] Add to `configs/free-providers-catalog.yaml`
- [ ] Add to `configs/model-router.yaml`
- [ ] Test API connectivity
- [ ] Document in FREE-AI-PROVIDERS-COMPLETE-GUIDE.md

---

## References

- Cerebras Cloud: https://cloud.cerebras.ai
- SambaNova Cloud: https://cloud.sambanova.ai
- Cerebras API Docs: https://inference-docs.cerebras.ai
- SambaNova API Docs: https://docs.sambanova.ai

---

*Research conducted: 2026-02-18*
*Next review: 2026-03-18 or when free tier terms change*