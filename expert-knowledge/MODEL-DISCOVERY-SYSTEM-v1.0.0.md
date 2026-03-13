# XNAi Model Discovery & Intelligence System

**Version**: 1.0.0 | **Date**: 2026-02-18 | **Author**: Cline (Claude Sonnet 4.6)  
**Status**: AUTHORITATIVE — Based on direct web research: HuggingFace, OpenRouter API, provider docs  
**Purpose**: Fix agent model blindness. Establish perpetual model intelligence system.

---

## 🔴 ROOT CAUSE ANALYSIS: Why Agents Fail at Model Discovery

This is the most important section. Every XNAi agent must read this before making ANY claims about model availability.

### The Core Problem

AI agents (including Cline, OpenCode-dispatched agents, and this very document's author) systematically fail to identify real, widely-available open-source models for one primary reason:

> **"Not in my training data" ≠ "Doesn't exist"**

### The 5 Failure Modes

| Failure Mode | Example | Root Cause | Remediation |
|--------------|---------|------------|-------------|
| **Training cutoff blindness** | "Kimi K2.5 doesn't exist" | Model released after training cutoff | ALWAYS verify via live APIs before claiming non-existence |
| **Over-correction from hallucination** | "Claude Opus 4.6 doesn't exist" (our v1.0 error) | Trying to correct a hallucination by denying real things | Verify BOTH the hallucination AND the correction via authoritative sources |
| **Conflating public API with public existence** | "GPT-5.2 doesn't exist publicly" | Model may be on OpenRouter/Copilot without being on OpenAI's main API | Check ALL distribution channels |
| **Provider label confusion** | "Gemini 3 Pro is Antigravity-internal only" | Didn't check OpenRouter where it IS public | Check OpenRouter as ground truth for availability |
| **Version uncertainty paralysis** | Marking Kimi K2.5, MiniMax M2.5, GLM 5 as "version uncertain" | HuggingFace was not checked | HuggingFace is the authoritative source for open-source models |

### The Remediation Rule (MANDATORY for all agents)

**Before claiming any model doesn't exist or is uncertain:**
1. Check `https://openrouter.ai/models` (JSON API: `https://openrouter.ai/api/v1/models`)
2. Check `https://huggingface.co/{org}/{model}` directly
3. Check provider's official docs page
4. Only after all 3 return nothing: mark as "unverified"

**Never say "X model doesn't exist" based solely on training data.**

---

## Part 1: Authoritative Model Intelligence Sources

### 1.1 Primary Sources (Ranked by Reliability)

| Source | URL | What It Covers | Update Frequency | API Available |
|--------|-----|----------------|-----------------|---------------|
| **OpenRouter Models** | https://openrouter.ai/models | ALL models from ALL providers, free/paid, live pricing | Real-time | ✅ REST API |
| **HuggingFace Models** | https://huggingface.co/models | Open-source models, weights, papers, usage | Real-time | ✅ REST API |
| **Anthropic Models** | https://docs.anthropic.com/en/docs/about-claude/models/all-models | Claude models only | Per release | ❌ Manual |
| **Google AI Studio** | https://ai.google.dev/gemini-api/docs/models | Gemini public models | Per release | ❌ Manual |
| **Moonshot AI API** | https://platform.moonshot.ai/docs | Kimi models | Per release | ✅ OpenAI-compatible |
| **OpenCode Models** | `/models` command in OpenCode TUI | OpenCode built-in + connected providers | Real-time | ✅ REST API |
| **Gemini CLI** | `gemini --list-models` or Google AI Studio | Gemini models | Per release | ✅ Via gemini-cli |

### 1.2 The OpenRouter API: Ground Truth for Model Availability

OpenRouter is the MOST comprehensive and MOST reliably updated source for what AI models are publicly accessible. It aggregates 300+ models from 50+ providers.

```bash
# Get ALL models (JSON)
curl https://openrouter.ai/api/v1/models | jq '.data[] | {id: .id, name: .name, context: .context_length, input: .pricing.prompt, output: .pricing.completion}'

# Get FREE models only
curl "https://openrouter.ai/api/v1/models?supported_parameters=free" | jq '.data[] | select(.pricing.prompt == "0") | {id: .id, name: .name, context: .context_length}'

# Get models by provider (e.g., Anthropic)
curl https://openrouter.ai/api/v1/models | jq '.data[] | select(.id | startswith("anthropic/")) | {id: .id, name: .name}'

# Get newest models (sorted by creation date)
curl https://openrouter.ai/api/v1/models | jq '.data | sort_by(.created) | reverse | .[0:20] | .[] | {id: .id, name: .name, created: .created}'
```

### 1.3 HuggingFace API: Ground Truth for Open-Source Models

```bash
# Get trending models
curl "https://huggingface.co/api/models?sort=downloads&direction=-1&limit=20" | jq '.[] | {id: .id, downloads: .downloads, likes: .likes}'

# Search for specific model
curl "https://huggingface.co/api/models?search=kimi-k2" | jq '.[] | {id: .id, downloads: .downloads}'

# Get model card info
curl https://huggingface.co/api/models/moonshotai/Kimi-K2.5 | jq '{id: .id, downloads: .downloads, tags: .tags}'

# Get inference providers for a model
curl https://huggingface.co/api/models/moonshotai/Kimi-K2.5 | jq '.inference'
```

### 1.4 Provider-Specific Discovery Commands

#### Anthropic (Claude models)
```bash
# List models via API (requires API key)
curl https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" | jq '.data[] | {id: .id, display_name: .display_name}'
```

#### Google Gemini
```bash
# Via Gemini CLI (lists available models for your account)
gemini --list-models

# Via Google AI API (requires API key)
curl "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" | jq '.models[] | {name: .name, displayName: .displayName, supportedGenerationMethods: .supportedGenerationMethods}'
```

#### OpenCode (Built-in + Connected)
```bash
# In OpenCode TUI
/models           # Lists all available models for current session

# Via REST API (when opencode serve is running)
curl http://localhost:3000/models | jq '.'

# Check specific provider models
opencode --list-models google  # If supported
```

#### Moonshot AI (Kimi)
```bash
# List Kimi models (OpenAI-compatible)
curl https://api.moonshot.cn/v1/models \
  -H "Authorization: Bearer $MOONSHOT_API_KEY" | jq '.data[] | {id: .id}'
```

---

## Part 2: Confirmed Model Cards — Corrected from Previous Audit

### CORRECTION: Models Previously Marked "Uncertain" Are Confirmed Real

The following models were incorrectly marked as "version uncertain" or "unconfirmed" in prior XNAi documents. They are ALL confirmed real models:

---

#### Kimi K2.5 ✅ CONFIRMED REAL (was: "version uncertain")

**Source**: HuggingFace `moonshotai/Kimi-K2.5` — 855,279 downloads last month, arXiv paper 2602.02276

| Attribute | Value |
|-----------|-------|
| **Developer** | Moonshot AI (China) |
| **HuggingFace** | https://huggingface.co/moonshotai/Kimi-K2.5 |
| **Architecture** | Mixture-of-Experts (MoE) |
| **Total Parameters** | 1 Trillion |
| **Active Parameters** | 32B per forward pass |
| **Context Window** | **256,000 tokens** (256K) |
| **Modes** | Thinking mode (temp=1.0) AND Instant mode (disable thinking) |
| **Multimodal** | ✅ Text, Images, Video (native, pre-trained on 15T mixed visual+text tokens) |
| **Vision Encoder** | MoonViT (400M params) |
| **Agentic** | ✅ Agent Swarm paradigm — decomposes tasks to parallel sub-agents |
| **Coding** | ✅ 76.8% SWE-Bench Verified, 73.0% SWE-Bench Multilingual |
| **License** | Modified MIT (open weights) |
| **API** | platform.moonshot.ai (OpenAI-compatible) |
| **OpenRouter ID** | `moonshotai/kimi-k2.5` — $0.23/M input, $3/M output, 262K context |
| **Inference Providers** | Together AI, Novita, Fireworks |
| **Paper** | arxiv.org/abs/2602.02276 |
| **Published** | January 2026 |

**XNAi Benchmark Context**: In Kimi K2.5's own benchmark table, it's compared against GPT-5.2, Claude 4.5 Opus, Gemini 3 Pro, and DeepSeek V3.2 — confirming all of these are real, production models as of early 2026.

**XNAi Role**: `opencode/kimi-k2.5-free` in OpenCode is the free tier version. For paid access, use `moonshotai/kimi-k2.5` via OpenRouter ($0.23/$3). Excellent for: large context research synthesis (256K), multi-agent orchestration, visual coding tasks.

---

#### MiniMax M2.5 ✅ CONFIRMED REAL (was: "version uncertain")

**Source**: OpenRouter `minimax/minimax-m2.5` — 2.71 TRILLION tokens served (massive usage)

| Attribute | Value |
|-----------|-------|
| **Developer** | MiniMax (China) |
| **Architecture** | MoE (details not disclosed) |
| **Context Window** | 197,000 tokens |
| **Focus** | Real-world productivity, coding agents, office work |
| **SWE-Bench Verified** | 80.2% (leading score) |
| **Multi-SWE-Bench** | 51.3% |
| **BrowseComp** | 76.3% |
| **OpenRouter ID** | `minimax/minimax-m2.5` — $0.30/M input, $1.10/M output |
| **OpenCode ID** | `opencode/minimax-m2.5-free` (free tier) |
| **XNAi Role** | Fast prototyping, office document tasks, web browsing agents |

**Also real in the MiniMax family**: M2.1, M2, M1 — all on OpenRouter with massive token volumes.

---

#### GLM 5 ✅ CONFIRMED REAL (was: "version uncertain — may be GLM-4")

**Source**: OpenRouter `z-ai/glm-5` — 938B tokens served. Also confirmed: Z.ai is Zhipu AI's consumer brand.

| Attribute | Value |
|-----------|-------|
| **Developer** | Z.ai (Zhipu AI, China) |
| **OpenRouter ID** | `z-ai/glm-5` — $0.30/M input, $2.55/M output, 205K context |
| **Architecture** | Dense (not MoE) |
| **Context Window** | 205,000 tokens |
| **Focus** | Complex systems design, long-horizon agent workflows, production coding |
| **Coding** | Rivals leading closed-source models per Z.ai claims |
| **OpenCode ID** | `opencode/glm-5-free` (free tier) |

**Also real in the Z.ai/GLM family**: GLM 4.7, GLM 4.6, GLM 4.5, GLM 4.5 Air (FREE on OpenRouter), GLM 4.5V, GLM 4.6V, GLM 4.7 Flash — all confirmed on OpenRouter.

**FREE**: `z-ai/glm-4.5-air:free` — FREE on OpenRouter, 131K context, MoE, thinking+non-thinking modes.

---

#### Gemini 3 Flash Preview ✅ CONFIRMED PUBLIC (was: "Antigravity-internal only")

**Source**: OpenRouter `google/gemini-3-flash-preview` — 865 BILLION tokens served, public pricing

| Attribute | Value |
|-----------|-------|
| **Developer** | Google |
| **OpenRouter ID** | `google/gemini-3-flash-preview` — $0.50/M input, $3/M output |
| **Context Window** | 1,050,000 tokens (1.05M) |
| **Status** | ✅ PUBLIC — available on OpenRouter, NOT just Antigravity-internal |
| **Multimodal** | Text, images, audio, video, PDFs |
| **Thinking** | Yes — configurable levels (minimal, low, medium, high) |
| **Tool Use** | Yes — strong agentic capabilities |
| **OpenCode** | Available via `google/antigravity-gemini-3-flash` (Antigravity) AND `google/gemini-3-flash-preview` (OpenRouter) |

**Note**: Gemini 3 Flash is NOW publicly available, not just through Antigravity's internal Google API. Copilot's "gemini-3-flash-preview" label MATCHES the real OpenRouter model ID.

---

#### Gemini 3 Pro Preview ✅ CONFIRMED PUBLIC (was: "Antigravity-internal only")

**Source**: OpenRouter `google/gemini-3-pro-preview` — 181B tokens served, public pricing

| Attribute | Value |
|-----------|-------|
| **Developer** | Google |
| **OpenRouter ID** | `google/gemini-3-pro-preview` — $2/M input, $12/M output |
| **Context Window** | 1,050,000 tokens (1.05M) |
| **Status** | ✅ PUBLIC — available on OpenRouter |
| **Multimodal** | Text, images, audio, video, PDFs |
| **Thinking** | Yes — high-precision reasoning |
| **SWE-Bench** | Competitive with Claude and GPT-5 class |
| **OpenCode** | `google/antigravity-gemini-3-pro` (Antigravity, FREE) or `google/gemini-3-pro-preview` (OpenRouter, $2/$12) |

**IMPORTANT IMPLICATION**: The Antigravity auth gives FREE access to models that cost $2-12/M tokens on OpenRouter. This makes Antigravity significantly more valuable than previously documented.

---

#### DeepSeek V3.2 ✅ CONFIRMED PUBLIC
- **OpenRouter**: `deepseek/deepseek-v3.2` — $0.26/M input, $0.38/M output, 164K context
- Introduces DeepSeek Sparse Attention (DSA), IMO/IOI gold-medal performance
- Also: V3.2 Speciale, V3.1 Terminus, V3.0324, R1 0528 (FREE on OpenRouter)

---

#### GPT-5 Series ✅ ALL CONFIRMED PUBLIC ON OPENROUTER

| Model | OpenRouter ID | Context | Input | Output |
|-------|--------------|---------|-------|--------|
| GPT-5 | `openai/gpt-5` | 400K | $1.25/M | $10/M |
| GPT-5 Mini | `openai/gpt-5-mini` | 400K | $0.25/M | $2/M |
| GPT-5 Nano | `openai/gpt-5-nano` | 400K | $0.05/M | $0.40/M |
| GPT-5 Pro | `openai/gpt-5-pro` | 400K | $15/M | $120/M |
| GPT-5.1 | `openai/gpt-5.1` | 400K | $1.25/M | $10/M |
| GPT-5.1-Codex | `openai/gpt-5.1-codex` | 400K | $1.25/M | $10/M |
| GPT-5.1-Codex-Mini | `openai/gpt-5.1-codex-mini` | 400K | $0.25/M | $2/M |
| GPT-5.2 | `openai/gpt-5.2` | 400K | $1.75/M | $14/M |
| GPT-5.2-Codex | `openai/gpt-5.2-codex` | 400K | $1.75/M | $14/M |
| GPT-5.2-Pro | `openai/gpt-5.2-pro` | 400K | $21/M | $168/M |

---

### Currently FREE Models on OpenRouter (High-Quality, Agent-Ready)

These are CONFIRMED free on OpenRouter as of 2026-02-18:

| Model | OpenRouter ID | Context | Quality | Best For |
|-------|--------------|---------|---------|---------|
| **DeepSeek R1 0528** | `deepseek/deepseek-r1-0528:free` | 164K | ⭐⭐⭐⭐⭐ | Deep reasoning, coding |
| **Kimi K2.5** | `moonshotai/kimi-k2.5:free` (check availability) | 262K | ⭐⭐⭐⭐⭐ | Agentic, multimodal |
| **GLM 4.5 Air** | `z-ai/glm-4.5-air:free` | 131K | ⭐⭐⭐⭐ | Coding, reasoning |
| **Qwen3 Coder 480B** | `qwen/qwen3-coder:free` | 262K | ⭐⭐⭐⭐ | Coding, agentic |
| **Qwen3 235B Thinking 2507** | `qwen/qwen3-235b-a22b-thinking-2507` | 131K | ⭐⭐⭐⭐ | Complex reasoning |
| **Qwen3 Next 80B Instruct** | `qwen/qwen3-next-80b-a3b-instruct:free` | 262K | ⭐⭐⭐⭐ | General, fast |
| **gpt-oss-120b** | `openai/gpt-oss-120b:free` | 131K | ⭐⭐⭐⭐ | General, agentic |
| **gpt-oss-20b** | `openai/gpt-oss-20b:free` | 131K | ⭐⭐⭐ | Lightweight |
| **Llama 3.3 70B** | `meta-llama/llama-3.3-70b-instruct:free` | 128K | ⭐⭐⭐⭐ | General purpose |
| **Hermes 3 405B** | `nousresearch/hermes-3-llama-3.1-405b:free` | 131K | ⭐⭐⭐⭐ | Instruction following |
| **Arcee Trinity Large** | `arcee-ai/trinity-large-preview:free` | 131K | ⭐⭐⭐⭐ | Coding, agentic (Cline-optimized!) |
| **Step 3.5 Flash** | `stepfun/step-3.5-flash:free` | 256K | ⭐⭐⭐ | Fast reasoning |
| **NVIDIA Nemotron 3 Nano 30B** | `nvidia/nemotron-3-nano-30b-a3b:free` | 256K | ⭐⭐⭐ | Agentic systems |
| **Mistral Small 3.1 24B** | `mistralai/mistral-small-3.1-24b-instruct:free` | 128K | ⭐⭐⭐ | General |
| **Qwen3 VL 235B Thinking** | `qwen/qwen3-vl-235b-a22b-thinking` | 131K | ⭐⭐⭐⭐ | Multimodal |
| **Qwen3 VL 30B Thinking** | `qwen/qwen3-vl-30b-a3b-thinking` | 131K | ⭐⭐⭐ | Fast multimodal |
| **Gemma 3 27B** | `google/gemma-3-27b-it:free` | 131K | ⭐⭐⭐ | General |
| **Gemma 3 12B** | `google/gemma-3-12b-it:free` | 33K | ⭐⭐⭐ | Fast |
| **Llama 3.2 3B** | `meta-llama/llama-3.2-3b-instruct:free` | 131K | ⭐⭐ | Routing/classification |
| **Venice Uncensored** | `cognitivecomputations/dolphin-mistral-24b-venice-edition:free` | 33K | ⭐⭐⭐ | Creative, uncensored |

> **Access via OpenRouter**: Configure OpenRouter as a provider in OpenCode with your OpenRouter API key, then use these model IDs directly.

---

## Part 3: Cline Free Tier Status

### Current Status (2026-02-18)

The user is on a **limited-time special offer** from Anthropic/Cline that provides free access to Claude Sonnet 4.6 through the Cline extension. This is NOT the standard Cline pricing model.

**Standard Cline**: Requires a paid Anthropic API key (billing per token at $3/$15 per MTok)  
**Current user status**: Limited-time special — free tier for Claude Sonnet 4.6 via Cline  
**Expiry**: Unknown — treat as potentially temporary; have API key ready as fallback

### Contingency Planning

When the free tier expires, options:
1. **Add Anthropic API key** to Cline settings — standard paid access
2. **Switch Cline provider to OpenRouter** — use free models like DeepSeek R1 0528, Qwen3 Coder, or Arcee Trinity
3. **Switch to OpenCode** as primary IDE agent — Antigravity auth provides free frontier models

**Configuration for OpenRouter in Cline**:
- Settings → API Provider: OpenRouter
- API Key: `$OPENROUTER_API_KEY`
- Model: `deepseek/deepseek-r1-0528` (free, excellent quality) or `qwen/qwen3-coder:free`

---

## Part 4: Model Update Automation System

### 4.1 The Problem with Manual Updates

The root failures documented in this report all stem from stale knowledge. We need **automated, frequent model intelligence updates** fed into the XNAi RAG system.

### 4.2 CLI Commands Agents Can Run RIGHT NOW

Any agent with terminal access can run these to get current model info:

```bash
# ===== DISCOVER FREE MODELS ON OPENROUTER =====
curl -s "https://openrouter.ai/api/v1/models" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
free = [m for m in data['data'] if m.get('pricing', {}).get('prompt') == '0']
free.sort(key=lambda x: x.get('context_length', 0), reverse=True)
for m in free[:20]:
    print(f\"{m['id']:60} ctx={m.get('context_length', 0)//1000}K\")
"

# ===== GET ALL CLAUDE MODELS ON OPENROUTER =====
curl -s "https://openrouter.ai/api/v1/models" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
claude = [m for m in data['data'] if 'claude' in m['id'].lower() or 'anthropic' in m['id'].lower()]
for m in claude:
    print(f\"{m['id']:50} \${m['pricing']['prompt']}/M in, \${m['pricing']['completion']}/M out, ctx={m.get('context_length',0)//1000}K\")
"

# ===== CHECK IF SPECIFIC MODEL EXISTS =====
MODEL_ID="moonshotai/kimi-k2.5"
curl -s "https://openrouter.ai/api/v1/models" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
model = next((m for m in data['data'] if m['id'] == '${MODEL_ID}'), None)
if model:
    print('CONFIRMED:', model['id'], '-', model.get('name'))
else:
    print('NOT FOUND:', '${MODEL_ID}')
"

# ===== GET NEWEST MODELS (last 30 days) =====
curl -s "https://openrouter.ai/api/v1/models" | \
  python3 -c "
import json, sys, time
data = json.load(sys.stdin)
cutoff = time.time() - (30 * 86400)
new = [m for m in data['data'] if m.get('created', 0) > cutoff]
new.sort(key=lambda x: x.get('created', 0), reverse=True)
for m in new[:20]:
    print(f\"{m['id']:60} created={m.get('created')}\")
"

# ===== LIST AVAILABLE GEMINI MODELS =====
gemini --list-models 2>/dev/null || \
  curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=${GEMINI_API_KEY}" | \
  python3 -c "import json,sys; [print(m['name']) for m in json.load(sys.stdin).get('models',[])]"

# ===== CHECK ANTHROPIC AVAILABLE MODELS =====
curl -s "https://api.anthropic.com/v1/models" \
  -H "x-api-key: ${ANTHROPIC_API_KEY}" \
  -H "anthropic-version: 2023-06-01" | \
  python3 -c "import json,sys; [print(m['id']) for m in json.load(sys.stdin).get('data',[])]"
```

### 4.3 Scheduled Model Intelligence Update Script

Create as `scripts/update-model-intelligence.sh`:

```bash
#!/bin/bash
# XNAi Model Intelligence Update Script
# Run: cron daily or weekly
# Output: expert-knowledge/model-updates/YYYY-MM-DD.json

set -euo pipefail
DATE=$(date +%Y-%m-%d)
OUTPUT_DIR="/home/arcana-novai/Documents/xnai-foundation/expert-knowledge/model-updates"
mkdir -p "$OUTPUT_DIR"

echo "=== XNAi Model Intelligence Update: $DATE ==="

# 1. Fetch all OpenRouter models
echo "Fetching OpenRouter models..."
curl -s "https://openrouter.ai/api/v1/models" > "$OUTPUT_DIR/openrouter-$DATE.json"

# 2. Extract free models
echo "Extracting free models..."
cat "$OUTPUT_DIR/openrouter-$DATE.json" | python3 -c "
import json, sys
data = json.load(sys.stdin)
free = [{
    'id': m['id'],
    'name': m.get('name', ''),
    'context': m.get('context_length', 0),
    'provider': m['id'].split('/')[0],
} for m in data['data'] if m.get('pricing', {}).get('prompt') == '0']
print(json.dumps(free, indent=2))
" > "$OUTPUT_DIR/free-models-$DATE.json"

FREE_COUNT=$(cat "$OUTPUT_DIR/free-models-$DATE.json" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
echo "Found $FREE_COUNT free models"

# 3. Check for new models since last run
if [ -f "$OUTPUT_DIR/openrouter-latest.json" ]; then
    echo "Checking for new models..."
    python3 -c "
import json
with open('$OUTPUT_DIR/openrouter-latest.json') as f:
    old = {m['id'] for m in json.load(f)['data']}
with open('$OUTPUT_DIR/openrouter-$DATE.json') as f:
    new_data = json.load(f)['data']
    new_ids = {m['id'] for m in new_data}
    added = new_ids - old
    if added:
        print('NEW MODELS DETECTED:')
        for mid in sorted(added):
            m = next(x for x in new_data if x['id'] == mid)
            print(f'  + {mid}: {m.get(\"name\", \"\")} (ctx={m.get(\"context_length\",0)//1000}K)')
    else:
        print('No new models detected')
"
fi

# 4. Update latest snapshot
cp "$OUTPUT_DIR/openrouter-$DATE.json" "$OUTPUT_DIR/openrouter-latest.json"
echo "Saved to $OUTPUT_DIR/openrouter-$DATE.json"

# 5. Generate summary report
python3 -c "
import json
with open('$OUTPUT_DIR/openrouter-$DATE.json') as f:
    data = json.load(f)['data']

providers = {}
for m in data:
    p = m['id'].split('/')[0]
    providers[p] = providers.get(p, 0) + 1

free = [m for m in data if m.get('pricing', {}).get('prompt') == '0']

print('=== MODEL INTELLIGENCE SUMMARY ===')
print(f'Total models: {len(data)}')
print(f'Free models: {len(free)}')
print(f'Providers: {len(providers)}')
print()
print('Top providers by model count:')
for p, c in sorted(providers.items(), key=lambda x: -x[1])[:10]:
    print(f'  {p}: {c}')
" 
echo "=== Update complete: $DATE ==="
```

### 4.4 GitHub Actions CI — Automated Weekly Model Check

Create as `.github/workflows/model-intelligence-update.yml`:

```yaml
name: Model Intelligence Update

on:
  schedule:
    - cron: '0 8 * * 1'  # Every Monday at 8am UTC
  workflow_dispatch:      # Allow manual trigger

jobs:
  update-model-intelligence:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Fetch OpenRouter Models
        run: |
          mkdir -p expert-knowledge/model-updates
          DATE=$(date +%Y-%m-%d)
          curl -s "https://openrouter.ai/api/v1/models" > "expert-knowledge/model-updates/openrouter-$DATE.json"
          
      - name: Detect New Models
        id: detect
        run: |
          # Compare with last known snapshot
          if [ -f expert-knowledge/model-updates/openrouter-latest.json ]; then
            NEW=$(python3 -c "
          import json
          with open('expert-knowledge/model-updates/openrouter-latest.json') as f:
            old = {m['id'] for m in json.load(f)['data']}
          import glob
          latest = sorted(glob.glob('expert-knowledge/model-updates/openrouter-2*.json'))[-1]
          with open(latest) as f:
            new = {m['id'] for m in json.load(f)['data']}
          added = new - old
          print(len(added))
          ")
            echo "new_models=$NEW" >> $GITHUB_OUTPUT
          fi
          
      - name: Update Latest Snapshot
        run: |
          DATE=$(date +%Y-%m-%d)
          cp "expert-knowledge/model-updates/openrouter-$DATE.json" \
             expert-knowledge/model-updates/openrouter-latest.json
             
      - name: Generate Free Models Report
        run: |
          python3 -c "
          import json, datetime
          with open('expert-knowledge/model-updates/openrouter-latest.json') as f:
              data = json.load(f)['data']
          free = [m for m in data if m.get('pricing', {}).get('prompt') == '0']
          free.sort(key=lambda x: x.get('context_length', 0), reverse=True)
          report = {
              'generated': datetime.date.today().isoformat(),
              'total_free': len(free),
              'models': [{
                  'id': m['id'],
                  'name': m.get('name', ''),
                  'context_length': m.get('context_length', 0),
                  'description': m.get('description', '')[:200]
              } for m in free]
          }
          with open('expert-knowledge/model-updates/free-models-latest.json', 'w') as f:
              json.dump(report, f, indent=2)
          print(f'Generated report: {len(free)} free models')
          "
          
      - name: Commit and Push
        run: |
          git config user.name 'XNAi Model Bot'
          git config user.email 'bot@xnai.dev'
          git add expert-knowledge/model-updates/
          git diff --staged --quiet || git commit -m "chore: weekly model intelligence update $(date +%Y-%m-%d)"
          git push
          
      - name: Create Issue if New Models Detected
        if: steps.detect.outputs.new_models != '0'
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `New AI models detected - model cards need update`,
              body: `${{ steps.detect.outputs.new_models }} new models detected on OpenRouter. Review expert-knowledge/model-updates/ and update model cards.`,
              labels: ['model-intelligence', 'needs-review']
            });
```

### 4.5 RAG Ingestion Pipeline for Model Intelligence

The XNAi RAG system should routinely ingest model data. Add to the curation pipeline:

```python
# app/XNAi_rag_app/model_intelligence_ingestion.py
"""
Routine ingestion of model intelligence data into XNAi RAG.
Run weekly via cron or as part of ingest_library.py
"""

import httpx
import json
from pathlib import Path
from datetime import date

OPENROUTER_API = "https://openrouter.ai/api/v1/models"
HUGGINGFACE_API = "https://huggingface.co/api/models"
OUTPUT_DIR = Path("expert-knowledge/model-updates")

async def fetch_openrouter_models() -> dict:
    """Fetch all models from OpenRouter."""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(OPENROUTER_API)
        r.raise_for_status()
        return r.json()

async def fetch_trending_hf_models(limit: int = 50) -> list:
    """Fetch trending open-source models from HuggingFace."""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(
            f"{HUGGINGFACE_API}?sort=downloads&direction=-1&limit={limit}&filter=text-generation"
        )
        r.raise_for_status()
        return r.json()

async def generate_model_intelligence_doc() -> str:
    """Generate a markdown document summarizing current model landscape."""
    models = await fetch_openrouter_models()
    free_models = [m for m in models["data"] if m.get("pricing", {}).get("prompt") == "0"]
    
    doc = f"""# Model Intelligence Report — {date.today().isoformat()}

Auto-generated by XNAi RAG ingestion pipeline.

## Free Models Available ({len(free_models)} total)

| Model ID | Provider | Context | Name |
|----------|----------|---------|------|
"""
    for m in sorted(free_models, key=lambda x: x.get("context_length", 0), reverse=True)[:30]:
        provider = m["id"].split("/")[0]
        ctx = f"{m.get('context_length', 0)//1000}K"
        doc += f"| `{m['id']}` | {provider} | {ctx} | {m.get('name', '')} |\n"
    
    return doc

async def ingest_model_intelligence():
    """Main ingestion function — call from cron or pipeline."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Fetch and save latest
    models = await fetch_openrouter_models()
    today = date.today().isoformat()
    (OUTPUT_DIR / f"openrouter-{today}.json").write_text(json.dumps(models, indent=2))
    (OUTPUT_DIR / "openrouter-latest.json").write_text(json.dumps(models, indent=2))
    
    # 2. Generate markdown doc for RAG
    doc = await generate_model_intelligence_doc()
    doc_path = OUTPUT_DIR / f"model-landscape-{today}.md"
    doc_path.write_text(doc)
    
    # 3. Ingest into RAG (hook into existing ingest_library.py)
    # from app.XNAi_rag_app.ingest_library import ingest_document
    # await ingest_document(str(doc_path), metadata={"type": "model_intelligence", "date": today})
    
    print(f"Model intelligence updated: {len(models['data'])} models, {today}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(ingest_model_intelligence())
```

---

## Part 5: Model Card Strategy for Agents

### 5.1 Where Agents Must Look for Model Info

Agents should follow this exact lookup order when they need model information:

```
LOOKUP PRIORITY ORDER:
1. expert-knowledge/model-updates/openrouter-latest.json  (most current)
2. expert-knowledge/XNAI-MODEL-INTELLIGENCE-REPORT-*.md  (curated cards)
3. expert-knowledge/AGENT-CLI-MODEL-MATRIX-v*.md         (routing strategy)
4. Live API: curl https://openrouter.ai/api/v1/models     (real-time)
5. HuggingFace: https://huggingface.co/{org}/{model}      (open-source details)

NEVER rely solely on training data to determine if a model exists.
```

### 5.2 Model Card Minimum Standard

Every model card in XNAi documentation MUST include:

```markdown
#### [Model Name] [STATUS BADGE: ✅/⚠️/❌]
- **Source**: [URL where verified — HuggingFace, OpenRouter, provider docs]
- **API ID**: `exact-model-id-here`
- **Context Window**: N tokens
- **Modes**: [thinking/instant/etc.]
- **Pricing**: $X/M input, $Y/M output (or FREE)
- **Free Access**: [OpenRouter free tier / OpenCode built-in / Antigravity / None]
- **Verified**: [Date verified] via [source]
- **XNAi Role**: [What we use it for]
```

### 5.3 Status Badges for Model Cards

| Badge | Meaning | Criteria |
|-------|---------|----------|
| ✅ CONFIRMED | Verified from primary source | Checked on OpenRouter API or provider docs |
| ⭐ FREE | Free access confirmed | Pricing is $0/$0 on OpenRouter or free tier exists |
| ⚠️ UNCERTAIN | Cannot currently verify | Neither OpenRouter nor HuggingFace return results |
| 🔄 INTERNAL | Provider-internal only | Not on OpenRouter, only via specific auth |
| ❌ DEPRECATED | Confirmed removed | Provider docs say deprecated |

---

## Part 6: Updated XNAi Strategy (Based on Real Discoveries)

### 6.1 OpenRouter as Strategic Layer

With the confirmed availability of FREE models on OpenRouter, XNAi should add OpenRouter as an explicit tier:

```
REVISED PROVIDER HIERARCHY (2026-02-18):

TIER 1a — ANTIGRAVITY AUTH (OpenCode)         → FREE frontier (Gemini 3 Pro/Flash, Sonnet 4.6, Opus 4.6)
TIER 1b — OPENROUTER FREE TIER                → FREE high-quality open-source
           Best: DeepSeek R1 0528, Qwen3 Coder 480B, Arcee Trinity Large
           Add OpenRouter API key to OpenCode → access all these free
           
TIER 2  — GEMINI CLI                          → Specialized 1M Gemini 2.5 Pro
TIER 3  — COPILOT CLI (free plan)             → GitHub-native
TIER 4  — OPENCODE BUILT-IN FREE              → Rate-limit fallback (same models as OpenRouter)
TIER 5  — LLAMA-CPP-PYTHON (local)            → Air-gap / sovereign
```

### 6.2 Updated Task Routing (With Real Models)

| Task | Best Free Option | Best Paid Option | Why |
|------|-----------------|-----------------|-----|
| **Full codebase audit** | Antigravity Gemini 3 Pro (1M ctx, FREE) | Gemini 3 Pro Preview via OpenRouter ($2/$12) | 1M context |
| **Architecture decisions** | Antigravity Claude Opus 4.6 (FREE via Antigravity) | Claude Opus 4.6 ($5/$25) | 128K output, strongest reasoning |
| **Daily coding** | Cline + Sonnet 4.6 (limited-time FREE) | Claude Sonnet 4.6 ($3/$15) | IDE integration |
| **Multi-agent tasks** | Kimi K2.5 via OpenCode (`moonshotai/kimi-k2.5` on OpenRouter) | Same | Agent Swarm, 256K ctx |
| **Agentic coding** | Qwen3 Coder 480B (FREE on OpenRouter) | `qwen/qwen3-coder` ($0.22/$1) | SWE-Bench competitive |
| **Deep reasoning** | DeepSeek R1 0528 (FREE on OpenRouter) | DeepSeek R1 0528 ($0.40/$1.75) | Open-source o1-equivalent |
| **Fast tasks** | Qwen3 Next 80B (FREE), Gemini 3 Flash (Antigravity FREE) | Same | Speed-optimized |
| **Offline/sovereign** | llama-cpp-python (Qwen 2.5 7B) | Same | Air-gap |

### 6.3 When to Use Each Kimi K2 Variant

| Model | Best For | Cost |
|-------|---------|------|
| `opencode/kimi-k2.5-free` | Quick agent tasks (free OpenCode built-in) | Free |
| `moonshotai/kimi-k2.5` (OpenRouter) | Production agentic coding, visual inputs | $0.23/$3 |
| `moonshotai/kimi-k2-thinking` (OpenRouter) | Complex reasoning chains | $0.40/$1.75 |
| `moonshotai/kimi-k2-0905` (OpenRouter) | SWE-Bench coding tasks | $0.40/$2 |

---

## Part 7: Agent Onboarding Protocol

Every new agent session should execute this checklist:

### 7.1 Quick Model Discovery (Run at Session Start)

```bash
# 1. Check current free models (takes <5 seconds)
curl -s "https://openrouter.ai/api/v1/models" | \
  python3 -c "
import json,sys
d=json.load(sys.stdin)['data']
free=[m for m in d if m.get('pricing',{}).get('prompt')=='0']
print(f'Free models available: {len(free)}')
for m in sorted(free, key=lambda x: x.get('context_length',0), reverse=True)[:5]:
    print(f'  {m[\"id\"]:50} ctx={m.get(\"context_length\",0)//1000}K')
"

# 2. Verify key models exist
for model_id in "anthropic/claude-sonnet-4.6" "moonshotai/kimi-k2.5" "deepseek/deepseek-r1-0528" "google/gemini-3-flash-preview"; do
  curl -s "https://openrouter.ai/api/v1/models/$model_id" | python3 -c "
import json,sys
try:
  d=json.load(sys.stdin)
  print(f'✅ {d.get(\"id\",\"$model_id\")}: \${d.get(\"pricing\",{}).get(\"prompt\",\"?\")}/M')
except:
  print(f'❓ $model_id: not found on OpenRouter')
"
done
```

### 7.2 Knowledge Files Priority Order

When answering questions about models, agents should read these files in order:

1. `expert-knowledge/model-updates/openrouter-latest.json` (if exists)
2. `expert-knowledge/MODEL-DISCOVERY-SYSTEM-v1.0.0.md` (this file)
3. `expert-knowledge/XNAI-MODEL-INTELLIGENCE-REPORT-2026-02-18.md`
4. `expert-knowledge/AGENT-CLI-MODEL-MATRIX-v3.0.0.md`

---

## Document Metadata

**Last verified**: 2026-02-18  
**Sources used**:
- HuggingFace `moonshotai/Kimi-K2.5` — direct scrape
- OpenRouter `/models?order=newest` — direct scrape (367 models, real-time)
- Kimi K2.5 arXiv paper 2602.02276

**Verification commands**:
```bash
curl -s https://openrouter.ai/api/v1/models | jq '.data | length'
# Should return: 300+ (as of 2026-02-18, 367 models)

curl -s https://openrouter.ai/api/v1/models | jq '.data[] | select(.id == "moonshotai/kimi-k2.5") | {id, name}'
# Should return: {"id": "moonshotai/kimi-k2.5", "name": "MoonshotAI: Kimi K2.5"}
```

**Next scheduled update**: Automate via CI (see Part 4.4)  
**Maintainer**: XNAi sovereign_mc_agent + Cline sessions
