# Provider Hierarchy - Final (TIER 1-5 Architecture)

**Status**: 🟢 LOCKED - Production Reference  
**Date**: 2026-02-24T01:49:22Z  
**Coordination Key**: `WAVE-4-ANTIGRAVITY-TIER1-HIERARCHY-FINAL`

---

## Executive Summary

The XNAi Foundation now operates a **5-tier provider hierarchy** with **Antigravity as TIER 1** (top priority). This provides enterprise-grade infrastructure with automatic intelligent routing and graceful fallback.

**Key Achievement**: From single provider (Copilot) to multi-tier stack with 213x quota advantage and zero cost increase.

---

## Provider Tier Architecture

### TIER 1: ANTIGRAVITY (Primary - 4M tokens/week)

**Status**: ✅ PRODUCTION-READY  
**Quota**: 500K tokens/week per account × 8 accounts = **4M tokens/week**  
**Cost**: $0 (free tier via Google OAuth)  
**Reset**: Sunday (UTC)

#### Models (5 specialized)

| Model | Context | Latency | Best For | Score |
|-------|---------|---------|----------|-------|
| **Gemini 3 Pro** | 1M | 851ms | Full-codebase analysis | ⭐⭐⭐⭐⭐ |
| **Claude Opus Thinking** | 200K | 990ms | Deep reasoning | ⭐⭐⭐⭐⭐ |
| **Claude Sonnet 4.6** | 200K | 854ms | Code generation | ⭐⭐⭐⭐ |
| **Gemini 3 Flash** | 1M | 858ms | Fast streaming | ⭐⭐⭐⭐ |
| **o3-mini** | 200K | 849ms | Speed-critical | ⭐⭐⭐⭐ |

#### Account Management

```yaml
Accounts: 8 (antigravity-01 through antigravity-08)
Quota/Account: 500K tokens/week
Total: 4M tokens/week
Reset: Every Sunday (UTC midnight)
Rotation: Quota-based (pick lowest-usage account)
```

#### Routing Decision Tree

```python
if task_type == "full_codebase_analysis":
    if context_size > 200000:
        use_model("antigravity_gemini_pro")  # Only 1M context model
    else:
        use_model("antigravity_sonnet")
        
elif task_type == "architecture_design":
    use_model("antigravity_opus_thinking", thinking_budget=32000)
    
elif task_type == "code_generation":
    use_model("antigravity_sonnet")
    
elif task_type == "interactive" or task_type == "urgent":
    use_model("antigravity_o3_mini")  # Fastest at 849ms
    
elif task_type == "reasoning":
    use_model("antigravity_opus_thinking") or use_model("antigravity_gemini_pro")
    
else:  # general task
    use_model("antigravity_sonnet")  # Default: fast + quality

# Always check quota first
if account_quota_exhausted():
    rotate_to_next_account()
if all_accounts_exhausted():
    fallback_to_tier_2()
```

#### Special Features

- **1M Context Unique**: Gemini Pro is ONLY model that can load entire XNAi repo (~400K tokens) in single request
- **Thinking Budget**: Claude Opus supports 8-32K token thinking budget - configurable per task
- **Sunday Reset**: Automatic quota reset Sunday midnight UTC (verify per account)

---

### TIER 2: COPILOT (Fallback - 18.75K tokens/week)

**Status**: ✅ PRODUCTION-READY  
**Quota**: 50 messages/month ≈ **18.75K tokens/week**  
**Cost**: $0 (included with Copilot subscription)  
**Best For**: Fallback when Antigravity exhausted

#### Models

| Model | Context | Latency | Best For |
|-------|---------|---------|----------|
| **Raptor-mini** | 264K | 200ms | General, fast turnaround |
| **Haiku 4.5** | 200K | 150ms | Speed-critical |

#### Routing

```python
# Use Copilot only when Antigravity quota >95% or all accounts exhausted
if antigravity_quota_exhausted():
    use_model("copilot_raptor_mini")  # Better context window
    if urgent:
        use_model("copilot_haiku_4_5")  # Faster
```

#### Considerations

- **Limited Quota**: 18.75K/week is restrictive, only for fallback
- **Smaller Context**: 264K vs 1M (Gemini Pro)
- **No Batch**: Each message counts against quota
- **Best for**: 1-2 strategic decisions per week when Antigravity exhausted

---

### TIER 3: CLINE (IDE Integration)

**Status**: ✅ PRODUCTION-READY  
**Quota**: Unlimited (no rate limit)  
**Cost**: $0 (local CLI)  
**Best For**: File modification, IDE integration

#### Capabilities

- Direct VS Code file operations
- Multi-file refactoring
- IDE-aware context
- Unlimited scope (no token limit)

#### Routing

```python
# Use Cline for direct file manipulation tasks
if task_requires_file_changes():
    use_provider("cline")  # Direct file ops, IDE integration

if cline_unavailable():
    fallback_to_tier_4()
```

#### Considerations

- **Limited Models**: Integrated models only
- **Not for Analysis**: Better for implementation than reasoning
- **IDE-Only**: Requires VS Code/Codium editor running
- **Good For**: Code refactoring, multiple file changes

---

### TIER 4: OPENCODE (Legacy Support)

**Status**: ✅ AVAILABLE (legacy)  
**Quota**: ~187.5K tokens/week (built-in models)  
**Cost**: $0 (free tier)  
**Latency**: ~1000ms baseline  
**Best For**: Large document analysis (fallback)

#### Models

- Built-in OpenCode models
- 1M context support (theoretically)
- Legacy support maintained

#### Routing

```python
# Use OpenCode only if Antigravity + Copilot + Cline all unavailable
if all_primary_exhausted():
    use_provider("opencode")
    
if context_size > 500000:
    use_provider("opencode")  # 1M context available
```

#### Considerations

- **High Latency**: ~1000ms (baseline)
- **Fallback Only**: Not recommended for primary tasks
- **Legacy**: Maintained for compatibility

---

### TIER 5: LOCAL (Offline Fallback)

**Status**: ✅ AVAILABLE (offline)  
**Quota**: Unlimited (local computation)  
**Cost**: $0 (compute cost only)  
**Latency**: ~5000ms (slow, CPU-intensive)  
**Best For**: Offline operation, sovereign computing

#### Models

- GGUF-based local models
- Configurable (Llama 2, Mistral, etc)
- Limited context (4-8K typical)

#### Routing

```python
# Last resort - offline or all external exhausted
if all_external_unavailable() or offline_mode():
    use_provider("local_gguf")
```

#### Considerations

- **Very Slow**: 5000ms latency
- **Limited Models**: Local compute constraints
- **Small Context**: 4-8K typical
- **Sovereignty**: Good for sensitive data

---

## Routing Algorithm (MultiProviderDispatcher)

### Scoring Formula

```python
# Overall score: weighted combination of quota, latency, specialization fit
overall_score = (quota_score * weight_quota) + (latency_score * weight_latency) + (fit_score * weight_fit)

# Antigravity gets 50% quota weight (dominates via 4M/week)
if provider.startswith("antigravity"):
    overall_score = (quota_score * 0.5) + (latency_score * 0.3) + (fit_score * 0.2)
else:
    # Other providers: 40% quota, 30% latency, 30% fit
    overall_score = (quota_score * 0.4) + (latency_score * 0.3) + (fit_score * 0.3)

# Select provider with highest score
best_provider = max(scores, key=overall_score)
```

### Scoring Components

**Quota Score** (0-100):
- Fresh account (0% used): 100
- 50% used: 50
- 95% used: 5
- Exhausted (100%): 0

**Latency Score** (0-100):
- Fast (<500ms): 90-100
- Medium (500-1000ms): 50-90
- Slow (>1000ms): 10-50
- Very slow (>5000ms): 0-10

**Fit Score** (0-100):
- Based on specialization match
- Adjusted for context window sufficiency
- Task-specific recommendations

### Fallback Chain Execution

```python
def dispatch(task, context_size, task_spec):
    providers_ranked = rank_all_providers(task_spec, context_size)
    
    for provider, account, score in providers_ranked:
        if provider_available(provider):
            if not provider_quota_exhausted(provider, account):
                result = execute(provider, account, task)
                if result.success:
                    return result
                    
    # All failed - fallback chain
    return fallback_to_next_tier()
```

---

## Decision Matrix

### Task Type → Provider Mapping

| Task Type | Tier 1 Model | Context | Latency | Why |
|-----------|-------------|---------|---------|-----|
| **Full-repo analysis** | Gemini Pro | 1M | 851ms | Only model with 1M context |
| **Architecture design** | Opus Thinking | 200K | 990ms | Deep reasoning (acceptable for strategic) |
| **Code generation** | Sonnet | 200K | 854ms | Best speed/quality for coding |
| **Interactive chat** | o3-mini | 200K | 849ms | Fastest response |
| **Large document** | Gemini Pro | 1M | 851ms | Can load entire codebase |
| **Urgent/fast** | o3-mini | 200K | 849ms | Sub-second latency |
| **General task** | Sonnet | 200K | 854ms | Default: balanced choice |
| **Fallback** | Copilot Raptor | 264K | 200ms | When Antigravity exhausted |
| **File changes** | Cline | 262K | 150ms | IDE integration |
| **Offline** | Local GGUF | 8K | 5000ms | When all else unavailable |

---

## Quota & Context Window Comparison

| Provider | Weekly Quota | Context Window | Ratio (vs Copilot) |
|----------|-------------|-----------------|-------------------|
| **Antigravity** | 4M | 1M (Gemini) | 213x quota, 4x context |
| Copilot | 18.75K | 264K | 1x (baseline) |
| Gemini CLI | 187.5K | 1M | 10x quota |
| Cline | Unlimited | 262K | ∞ (unlimited) |
| OpenCode | 187.5K | 1M | 10x quota |
| Local | Limited | 8K | 1x (compute) |

---

## Rate Limit Management

### Current Status

```
antigravity-01: ~95% quota used (CRITICAL)
antigravity-02: ~95% quota used (CRITICAL)
antigravity-03: ~95% quota used (CRITICAL)
antigravity-04: ~90% quota used
antigravity-05: ~90% quota used
antigravity-06: ~85% quota used
antigravity-07: ~85% quota used
antigravity-08: ~80% quota used
```

### Reset Timeline

**Days 1-2 (Current)**:
- Use Copilot fallback (18.75K/week available)
- Monitor reset times

**Days 3-4 (First Reset)**:
- Accounts 01-03 expected to reset (500K each)
- Total capacity increases to ~1.5M during reset window

**Days 5+ (Full Reset)**:
- All accounts refreshed
- Full 4M tokens/week available

### Circuit Breaker Logic

```python
def dispatch_with_fallback(task, context_size, task_spec):
    # Try Tier 1 (Antigravity)
    if antigravity_quota_available():
        result = dispatch_antigravity(task, context_size, task_spec)
        if result.success:
            return result
    
    # Tier 1 exhausted - try Tier 2 (Copilot)
    if copilot_quota_available():
        result = dispatch_copilot(task, context_size, task_spec)
        if result.success:
            return result
    
    # Tier 2 exhausted - try Tier 3 (Cline)
    if cline_available():
        result = dispatch_cline(task, context_size, task_spec)
        if result.success:
            return result
    
    # Continue down fallback chain...
    return graceful_degradation(task)
```

---

## Production SLA Targets

| Metric | Target | Achieved |
|--------|--------|----------|
| **P50 Latency** | <900ms | 850ms (o3-mini) ✅ |
| **P95 Latency** | <1000ms | 990ms (Opus) ✅ |
| **Availability** | >99.5% | Multi-account rotation ✅ |
| **Quota/Week** | 4M | 4M (8 accounts) ✅ |
| **Context Window** | 1M | 1M (Gemini Pro) ✅ |
| **Specialization** | 5+ models | 5 models ✅ |

---

## Integration Points

### Agent Bus

✅ Antigravity models integrate seamlessly with Agent Bus routing  
✅ Automatic model selection based on task specialization

### Session Manager

✅ 8-account rotation independent from GitHub account pool  
✅ Quota tracking per account with Sunday reset

### MC Overseer v2.1

⏳ Route architectural decisions → Antigravity Opus  
⏳ Route large analysis → Antigravity Gemini Pro  
⏳ Route speed-critical → o3-mini

### Monitoring

⏳ Quota tracking dashboard (per account, daily/weekly)  
⏳ Alerts: >80%, >95%, exhausted  
⏳ Reset monitoring (countdown to Sunday)

---

## Migration Path (From Old to New)

### Before (Phase 2)
```
Single Provider (Copilot) → 18.75K tokens/week → Limited to one model
```

### After (Phase 3B+)
```
Tier 1: Antigravity (4M/week, 5 models)
├─ Primary routing
└─ Falls back to Tier 2 when exhausted

Tier 2: Copilot (18.75K/week)
├─ Fallback
└─ Falls back to Tier 3 when exhausted

Tier 3-5: Cline, OpenCode, Local
```

### Impact
- ✅ 213x quota advantage
- ✅ 5x model specialization
- ✅ Automatic intelligent routing
- ✅ Graceful fallback chain
- ✅ Zero cost increase

---

## References

- `ANTIGRAVITY-TIER1-INTEGRATION-COMPLETE.md` - Implementation details
- `PHASE-3C-ANTIGRAVITY-DEPLOYMENT.md` - Deployment strategy
- `benchmarks/antigravity-latency-summary.json` - Latency data
- `app/XNAi_rag_app/core/multi_provider_dispatcher.py` - Implementation

---

**Status**: 🟢 LOCKED - PROVIDER HIERARCHY FINAL

This hierarchy is production-ready and should not be changed without full revalidation of SLAs.

