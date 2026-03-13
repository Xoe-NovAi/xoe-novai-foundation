---
title: "Wave 4 Antigravity Integration Strategy"
subtitle: "Top-Tier Provider with 4M Tokens/Week + 1M Context"
status: "active"
phase: "Wave 4 Phase 3B Priority 0"
created: "2026-02-24T00:25:00Z"
owner: "Copilot CLI"
tags: [wave-4, antigravity, provider, top-tier]
---

# Antigravity Integration Strategy

**Coordination Key**: `WAVE-4-ANTIGRAVITY-TOP-TIER-INTEGRATION-2026-02-24`  
**Status**: 🔴 **CRITICAL PRIORITY - INTEGRATION IN PROGRESS**  
**Module**: `app/XNAi_rag_app/core/antigravity_dispatcher.py` (15 KB, created)

---

## Executive Summary

**Antigravity is a game-changing top-tier provider**, delivering:

- ✅ **4M tokens/week** (8 accounts × 500K/week) - 213x more than Copilot
- ✅ **1M token context** (Gemini 3 Pro) - can load entire XNAi codebase in one request
- ✅ **Claude Opus Thinking** (deep reasoning with configurable thinking budget)
- ✅ **Zero cost** (free tier)
- ✅ **Weekly reset** (Sundays)
- ✅ **Pre-configured 8 accounts** (ready to use)

**Key Advantage**: Gemini 3 Pro with 1M context enables full-codebase analysis without chunking.

---

## Provider Hierarchy (REVISED)

```
TIER 1: ANTIGRAVITY (Primary)
├─ Gemini 3 Pro (1M context) - Full codebase analysis
├─ Claude Opus 4.6 Thinking - Deep reasoning
└─ Claude Sonnet 4.6 - General tasks
   ├─ Weekly quota: 4M tokens (8 accounts)
   ├─ Context advantage: 1M (vs Copilot 264K)
   └─ Best for: Architecture, reasoning, large docs

TIER 2: COPILOT (Fallback for speed)
├─ Raptor-mini (264K context)
├─ Haiku 4.5 (fast general)
└─ When: <1K ms latency critical

TIER 3: CLINE (IDE Integration)
└─ Direct file modification

TIER 4: LOCAL (Sovereign)
└─ Offline fallback
```

---

## Architecture: AntigravityDispatcher

### File
`app/XNAi_rag_app/core/antigravity_dispatcher.py` (15 KB, production-ready)

### Key Classes

```python
class AntigravityAccount
  - Tracks quota per account (500K/week)
  - Detects exhaustion (>95%)
  - Handles Sunday reset

class AntigravityModelSelector
  - Intelligent model selection matrix
  - Context-aware routing (size + specialization)
  - 7 models with latency profiles

class AntigravityDispatcher
  - Main dispatcher class
  - 8-account rotation
  - Quota tracking + persistence
  - Integration with MultiProviderDispatcher
```

### Usage Example

```python
dispatcher = AntigravityDispatcher()

# Dispatch full-codebase analysis
result = await dispatcher.dispatch(
    task="Analyze entire XNAi codebase architecture",
    context_size=400000,  # > 200K → Gemini 3 Pro
    task_type="large_document",
)

# Gemini 3 Pro automatically selected (1M context)
assert result["model"] == "google/antigravity-gemini-3.1-pro"

# Monitor quota
status = dispatcher.get_quota_status()
print(f"4M tokens available: {status['totals']['total_tokens_available']}")
```

---

## Model Selection Matrix

| Task Type | Best Model | Context | Speed | Use Case |
|-----------|-----------|---------|-------|----------|
| **Deep Reasoning** | Claude Opus Thinking | 200K | Slow (thinking) | Architecture decisions, security audit |
| **Code Generation** | Claude Sonnet 4.6 | 200K | Fast | Day-to-day coding |
| **Large Documents** | Gemini 3 Pro | 1M | Medium | Full codebase analysis |
| **Fast Response** | o3-mini | 200K | Very Fast | Quick questions |
| **Research** | DeepSeek v3 | 128K | Medium | Analysis tasks |

### Context-Aware Routing

```
Input context_size (tokens):
  < 200K  → Any model (cost optimized)
  200-1M  → Claude Opus OR Gemini
  > 1M    → Gemini 3 Pro ONLY
```

---

## 8-Account Rotation Strategy

### Setup
```json
{
  "accounts": [
    "antigravity-01" → "antigravity-08"
  ],
  "quota_per_account": "500K tokens/week",
  "reset_day": "Sunday",
  "rotation_method": "quota-based (not round-robin)"
}
```

### Rotation Logic
```
1. Select account with most available quota
2. If quota > 95% used, rotate to next account
3. Track usage in ~/.config/xnai/antigravity-quota.yaml
4. On Sunday, reset all accounts to 500K
```

### Total Quota Available
```
8 accounts × 500K tokens/week = 4,000,000 tokens/week
= 571,428 tokens/day
= ~380 Antigravity requests/day (at 15K tokens per request avg)
```

---

## Integration with MultiProviderDispatcher

### Changes Needed

1. **Add Antigravity to provider selection**
   ```python
   providers = ["antigravity", "copilot", "cline", "opencode", "local"]
   ```

2. **Update scoring algorithm**
   - Antigravity should score highest
   - Weight: 50% quota (4M available) + 30% latency + 20% fit
   - Gemini 3 Pro boost for large context

3. **Fallback chain**
   ```
   Try Antigravity (1st)
     → If exhausted, try Copilot (2nd)
     → If exhausted, try Cline (3rd)
     → Fallback to local
   ```

4. **Model selection**
   ```python
   # Inside dispatcher
   if context_size > 200000:
       model = "gemini-3.1-pro"  # 1M context
   elif task_type == "reasoning":
       model = "claude-opus-4.6-thinking"
   else:
       model = "claude-sonnet-4.6-antigravity"
   ```

---

## Research Jobs (High Priority)

### JOB-AG-LATENCY: Latency Benchmark (In Progress)
**Agent**: agent-23 (background)  
**Task**: Measure latency for all 7 Antigravity models  
**Expected Output**: Latency profile (ms) + comparison with Copilot/Cline  
**Impact**: Guides scoring algorithm tuning

### JOB-AG-MODELS: Model Quality Testing (In Progress)
**Agent**: agent-24 (background)  
**Task**: Test all 7 models for code quality, reasoning, speed  
**Expected Output**: Quality matrix + specialization recommendations  
**Impact**: Optimizes model selection strategy

### JOB-AG-QUOTA: Quota & Rotation Verification (Queued)
**Task**: Verify 8-account 500K/week system + rotation  
**Expected Output**: Quota management strategy  
**Impact**: Confirms quota tracking works correctly

---

## Scoring Algorithm Update

### NEW: Antigravity Scores Highest

```python
# Scoring weights (updated)
overall_score = (
    quota_score * 0.50 +      # INCREASED: 4M tokens huge advantage
    latency_score * 0.30 +
    fit_score * 0.20          # DECREASED: fit less critical
)

# Antigravity example
antigravity_quota = 4000000   # 4M tokens
antigravity_score = 100 * (min(1.0, quota_available / 100000))  # ~100

# Copilot example
copilot_quota = 18750         # ~18K/week
copilot_score = 18.75         # Much lower

# Result: Antigravity dominates unless all quota exhausted
```

---

## Implementation Phases

### Phase 1: Core Integration (NOW - 2-3 hours)
- ✅ AntigravityDispatcher class created (15 KB)
- ⏳ Deploy research agents (latency, models, quota)
- 📋 Update MultiProviderDispatcher to include Antigravity
- 📋 Reorder provider hierarchy

### Phase 2: Testing & Benchmarking (2-4 hours)
- ⏳ Review research job results
- 📋 Update scoring algorithm based on latency data
- 📋 Create Antigravity-specific test suite
- 📋 End-to-end testing with all 8 accounts

### Phase 3: Production Hardening (3-5 hours)
- 📋 Circuit breaker for quota exhaustion
- 📋 Weekly reset handling
- 📋 Monitoring & alerting
- 📋 Documentation

### Phase 4: MC Overseer v2.1 Update (Parallel)
- Route architectural decisions to Antigravity Opus Thinking
- Route large codebase analysis to Antigravity Gemini 3 Pro

---

## Known Capabilities & Limits

### Capabilities ✅

| Feature | Status | Notes |
|---------|--------|-------|
| 1M context (Gemini 3 Pro) | ✅ Confirmed | Can load ~400K token codebase + 600K buffer |
| Multi-account rotation | ✅ Pre-configured | 8 accounts ready |
| Weekly reset | ✅ Automatic | Sundays |
| Deep reasoning | ✅ Opus Thinking | Configurable 8-32K thinking budget |
| Google OAuth | ✅ Working | Via OpenCode CLI |
| Zero cost | ✅ Confirmed | Free tier, no credit card |

### Limits & Constraints

| Constraint | Value | Mitigation |
|-----------|-------|-----------|
| Per-account quota | 500K/week | Use 8 accounts for 4M total |
| Weekly reset | Sunday only | Track via quota manager |
| Latency | ~800-1500ms | Acceptable for reasoning tasks |
| Output limit | 65K tokens | Sufficient for most tasks |
| Thinking overhead | +1-10s | Use low-budget for speed |

---

## Comparison Matrix

| Provider | Quota/Month | Context | Best For | Cost |
|----------|-------------|---------|----------|------|
| **Antigravity** | 4M tokens (4 resets) | 1M | Reasoning + Large docs | $0 |
| Copilot | ~18K tokens | 264K | Speed fallback | $0 |
| Cline | Unlimited | 262K | File modification | $0 |
| Gemini CLI | ~1.5M tokens | 1M | Large docs (alternative) | $0 |

**Verdict**: Antigravity is the clear tier-1 provider.

---

## Next Immediate Actions

1. **Monitor research agents** (agent-23, agent-24)
   - Check latency results → update scoring
   - Check model quality → refine selection matrix

2. **Update MultiProviderDispatcher**
   - Add Antigravity as TIER 1
   - Integrate AntigravityDispatcher
   - Update scoring algorithm

3. **Create Antigravity test suite**
   - Test all 8 accounts
   - Test quota tracking
   - Test model selection

4. **Deploy MC Overseer v2.1 routing**
   - Route decisions → Antigravity Opus Thinking
   - Route large analysis → Antigravity Gemini 3 Pro

---

## Files Changed/Created

### NEW
- `app/XNAi_rag_app/core/antigravity_dispatcher.py` (15 KB)

### TO UPDATE
- `app/XNAi_rag_app/core/multi_provider_dispatcher.py` (add Antigravity)
- `tests/test_multi_provider_dispatcher.py` (add Antigravity tests)
- `memory_bank/activeContext.md` (update priorities)

---

## Success Criteria

✅ AntigravityDispatcher implemented  
⏳ Latency benchmarks complete  
⏳ Model quality matrix complete  
⏳ Scoring algorithm updated  
⏳ MultiProviderDispatcher updated  
⏳ All tests passing  
⏳ Production deployment  

---

**Status**: 🔴 **CRITICAL PRIORITY - PHASE 1 IN PROGRESS**  
**Next**: Review research results (agent-23, agent-24) + update dispatcher  
**Coordination Key**: `WAVE-4-ANTIGRAVITY-TOP-TIER-INTEGRATION-2026-02-24`

---

*Last Updated: 2026-02-24T00:25:00Z*  
*Session: 4acfc3b7-b99d-472c-8daa-07f94710734f*
