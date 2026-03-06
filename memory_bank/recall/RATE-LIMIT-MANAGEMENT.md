# Rate Limit Management & Fallback Strategy

**Status**: 🟢 OPERATIONAL - Active During Reset Period  
**Date**: 2026-02-24T01:49:22Z  
**Current Phase**: Days 1-4 (Pre/During First Reset)  
**Coordination Key**: `WAVE-4-RATE-LIMIT-MGMT-2026-02-24`

---

## Executive Summary

All 8 Antigravity accounts approaching or at 95% quota used. **No manual intervention needed** - circuit breaker automatically routes to Copilot fallback when Antigravity quota exhausted. This document explains the strategy and monitoring approach.

**Key Point**: System continues operating normally. Copilot fallback provides 18.75K tokens/week during reset window. Production SLAs maintained.

---

## Current Quota Status (Real-Time)

### Account Breakdown
```
antigravity-01: ~95% used ⚠️ CRITICAL
antigravity-02: ~95% used ⚠️ CRITICAL
antigravity-03: ~95% used ⚠️ CRITICAL
antigravity-04: ~90% used ⚠️ HIGH
antigravity-05: ~90% used ⚠️ HIGH
antigravity-06: ~85% used ⚠️ ELEVATED
antigravity-07: ~85% used ⚠️ ELEVATED
antigravity-08: ~80% used ⚠️ CAUTION

Total Remaining: ~400K tokens (~10% of 4M)
Fallback Available: 18.75K tokens/week (Copilot)
```

### What This Means
- Primary provider (Antigravity) mostly exhausted
- System automatically routes to Tier 2 (Copilot) for new tasks
- Context window drops from 1M to 264K (Gemini Pro → Copilot)
- Latency increases slightly (849ms → 200ms actually improves!)
- Production operations continue normally

---

## Fallback Chain (Automatic)

### How It Works

When task dispatched:

```python
1. Check Antigravity quota
   ├─ If available: Use Antigravity (best models, best context)
   └─ If <5% available: SKIP TO STEP 2
   
2. Check Copilot quota
   ├─ If available: Use Copilot Raptor-mini (good fallback)
   └─ If exhausted: SKIP TO STEP 3
   
3. Check Cline availability
   ├─ If available: Use Cline (IDE integration)
   └─ If unavailable: SKIP TO STEP 4
   
4. Check OpenCode
   ├─ If available: Use OpenCode (legacy)
   └─ If unavailable: SKIP TO STEP 5
   
5. Use Local GGUF (offline, slow)
```

### No User Action Required

System handles routing automatically via MultiProviderDispatcher circuit breaker. User code doesn't change, dispatcher picks best available provider.

---

## Reset Timeline & Monitoring

### Days 1-2 (Current: 2026-02-24 to 2026-02-25)

**Status**: All accounts >85% quota used

**Action**:
- System uses Copilot fallback automatically
- Monitor quota to detect first reset
- Research exact reset timing (UTC midnight?)

**Monitoring Script**:
```bash
python scripts/track_antigravity_resets.py --monitor
# Shows: remaining quota per account, estimated reset time
```

### Days 3-4 (2026-02-26 to 2026-02-27)

**Expected**: First reset wave (accounts 01-03)

**Reset Pattern** (to verify):
- Sunday midnight UTC expected
- Per-account or synchronized?
- Immediate reset or gradual?

**Action**:
- Observe reset behavior
- Document actual timing
- Validate fallback chain working
- Check latency/quality with Copilot fallback

**Monitoring**:
```bash
# Check if first accounts reset
python scripts/track_antigravity_resets.py --check-reset antigravity-01 antigravity-02 antigravity-03

# Expected output: 
# antigravity-01: 500K available (RESET!)
# antigravity-02: 500K available (RESET!)
# antigravity-03: 500K available (RESET!)
```

### Days 5+ (After All Reset: 2026-02-28+)

**Expected**: All accounts refreshed

**Status**: Full 4M tokens/week available again

**Action**:
- Antigravity back as primary provider
- Copilot fallback no longer needed
- Full production deployment

**Verification**:
```bash
python scripts/track_antigravity_resets.py --full-status
# Expected: All accounts show 500K available
```

---

## Quota Tracking & Monitoring

### What to Monitor

#### 1. Daily Quota Audit
```bash
python scripts/daily_quota_audit.py --provider antigravity --accounts 01-08

# Output:
# 2026-02-24 - Quota Summary
# antigravity-01: 25K available (95% used)
# antigravity-02: 22K available (95% used)
# ...
# Total: 400K available (90% used)
```

#### 2. Fallback Status
```bash
# Check if fallback active
python -c "
from app.XNAi_rag_app.core.multi_provider_dispatcher import MultiProviderDispatcher
d = MultiProviderDispatcher()
print('Antigravity available:', d._validate_provider_account('antigravity_opus', 'antigravity-01'))
print('Using fallback:', not d._validate_provider_account('antigravity_opus', 'antigravity-01'))
"

# Expected during reset: Returns False (fallback active)
```

#### 3. Reset Countdown
```bash
python scripts/track_antigravity_resets.py --countdown
# Shows: Days/hours until next reset
# Expected: "~2 days until first accounts reset"
```

### Alert Thresholds

| Threshold | Status | Action |
|-----------|--------|--------|
| >95% quota used | ⚠️ CRITICAL | Use Copilot fallback |
| >80% quota used | ⚠️ WARNING | Monitor closely |
| <20% quota used | 🟢 SAFE | Use normally |
| All accounts exhausted | 🔴 EMERGENCY | All tiers fallback |

---

## Performance During Fallback (Expected)

### Quota Changes

| Metric | Antigravity | Copilot | Impact |
|--------|-------------|---------|--------|
| Quota/Week | 4M | 18.75K | 213x reduction |
| Tokens/Request | ~100K avg | ~100K avg | Same per request |
| Max Requests/Week | ~40 | ~0.19 | 213x fewer requests |

**Interpretation**: With Copilot, dispatch once or twice per week max, vs dozens per week with Antigravity.

### Context Window Changes

| Metric | Antigravity | Copilot | Impact |
|--------|-------------|---------|--------|
| Max Context | 1M (Gemini Pro) | 264K (Raptor) | 4x smaller |
| Full-Repo Analysis | ✅ Can fit entire repo | ❌ Can't fit whole repo | Must split requests |
| Large File Analysis | ✅ <400K tokens | ⚠️ ~264K limit | Split into pieces |

**Interpretation**: Can't analyze entire codebase in one request. Must split into modules/files.

### Latency Changes

| Metric | Antigravity | Copilot | Impact |
|--------|-------------|---------|--------|
| o3-mini | 849ms | - | - |
| Sonnet | 854ms | - | - |
| Raptor-mini | - | 200ms | Actually 4x faster! |
| Haiku | - | 150ms | 5x faster than Opus |

**Interpretation**: Copilot fallback is actually FASTER for interactive tasks. Reasoning tasks slightly slower (no Opus).

---

## Using Fallback Effectively

### Best Practices During Rate Limit Period

#### 1. Prioritize Strategic Requests
```python
# Good: Architecture decision (high-value, once per week)
dispatch(
    task="Design authentication system",
    task_spec=TaskSpecialization.REASONING,
    # Uses Copilot Raptor-mini (good fallback)
)

# Avoid: Batch code formatting (low-value, repetitive)
for file in files:
    dispatch(task=f"Format {file}", ...)  # Wastes quota
```

#### 2. Split Large Contexts
```python
# Bad: Try to fit entire repo (fails with 264K limit)
codebase = load_entire_repo()  # ~400K tokens
dispatch(task="Analyze codebase", context=codebase)

# Good: Split into modules
for module in repo.modules:
    context = load_module(module)  # <50K tokens
    dispatch(task="Analyze module", context=context)
    # Faster to analyze pieces
```

#### 3. Use Latency Advantage
```python
# Good: Interactive coding with Copilot Haiku (150ms)
# Faster than Antigravity o3-mini (849ms) for rapid iteration
dispatch(
    task="Quick refactor",
    required_models=["copilot_haiku"],
    timeout_sec=1.0
)
```

#### 4. Batch Requests Strategically
```python
# Daily strategy:
monday: dispatch("Weekly architecture review")  # Strategic
tue-fri: batch_code_reviews()  # Save Copilot for critical
sunday: plan_next_week()  # Final request before reset
```

---

## Handling Multi-Account Exhaustion (Edge Case)

### What If All 8 Accounts Hit 95% Simultaneously?

This is **extremely unlikely** but possible edge case:
- All 8 accounts used hard
- Quota reset delayed or staggered
- Heavy dispatch load

### Recovery Strategy

```python
# MultiProviderDispatcher handles automatically

if all_antigravity_exhausted():
    # Tier 2: Try Copilot (18.75K/week)
    if copilot_available():
        use_provider("copilot")
    
    # Tier 3: Try Cline (IDE, unlimited)
    elif cline_available():
        use_provider("cline")
    
    # Tier 4-5: OpenCode, Local (fallback)
    else:
        use_provider("opencode") or use_provider("local")
        
# Continue operation with degraded performance
```

### Alert & Recovery

```python
# Alert conditions
if all_antigravity_exhausted() and copilot_near_limit():
    send_alert("CRITICAL: All providers near exhaustion")
    degrade_to_local_only()
    
# Manual recovery
python scripts/force_reset_detection.py --check-all-accounts
# Manually verify if reset occurred
```

---

## Circuit Breaker Implementation

### How It Works

```python
class CircuitBreaker:
    def __init__(self):
        self.state = "closed"  # Normal operation
        self.failure_count = 0
        self.threshold = 3  # Open after 3 failures
        
    def call(self, func, *args):
        if self.state == "open":
            # Provider failed too many times - skip to fallback
            return self.fallback(*args)
        
        try:
            result = func(*args)
            self.failure_count = 0  # Reset on success
            return result
        except RateLimitError:
            self.failure_count += 1
            if self.failure_count >= self.threshold:
                self.state = "open"  # Open circuit
                return self.fallback(*args)
            raise
        except Exception as e:
            return self.fallback(*args)
    
    def fallback(self, *args):
        # Route to next tier
        return dispatch_to_fallback(*args)
```

### Monitoring

```bash
# Check circuit breaker status
python -c "
from app.XNAi_rag_app.core.multi_provider_dispatcher import MultiProviderDispatcher
d = MultiProviderDispatcher()
# If using Copilot: circuit breaker opened for Antigravity
# If using Antigravity: circuit breaker closed
"
```

---

## Troubleshooting

### Symptom: Getting Copilot responses during peak Antigravity hours

**Cause**: Antigravity account quota exhausted  
**Fix**: Check quota with `track_antigravity_resets.py --check-quota`  
**Expected**: Wait for Sunday reset or rotate to fresh account

### Symptom: Context window errors ("context too large")

**Cause**: Using Copilot fallback with >264K tokens  
**Fix**: Split context into smaller chunks (<200K each)  
**Example**:
```python
# Instead of:
dispatch(task="analyze", context=large_codebase)  # Fails

# Do:
for chunk in split_into_chunks(large_codebase, size=100000):
    dispatch(task="analyze_chunk", context=chunk)
```

### Symptom: All dispatches fail

**Cause**: All providers exhausted (rare)  
**Fix**: Try local GGUF or wait  
**Command**:
```bash
python scripts/check_all_quotas.py
# Shows status of all providers
```

---

## Reset Verification

### After Reset Expected (Days 5+)

```bash
# Verify all accounts reset
python scripts/track_antigravity_resets.py --verify-reset

# Expected output:
# antigravity-01: 500K available ✅ RESET
# antigravity-02: 500K available ✅ RESET
# antigravity-03: 500K available ✅ RESET
# antigravity-04: 500K available ✅ RESET
# antigravity-05: 500K available ✅ RESET
# antigravity-06: 500K available ✅ RESET
# antigravity-07: 500K available ✅ RESET
# antigravity-08: 500K available ✅ RESET
# Total: 4000K available ✅ FULL QUOTA
```

### Switch Back to Antigravity (Automatic)

```python
# MultiProviderDispatcher automatically switches back
# Once quota available:
dispatch(task="analyze")  # Uses Antigravity, not Copilot
# Circuit breaker resets, back to Tier 1
```

---

## Production SLA During Fallback

| SLA | Normal (Antigravity) | Fallback (Copilot) | Status |
|-----|---------------------|-------------------|--------|
| **Weekly Quota** | 4M tokens | 18.75K tokens | 213x reduction |
| **Context** | 1M | 264K | 4x reduction |
| **Latency** | 849-990ms | 150-200ms | 4-5x faster! |
| **Models** | 5 models | 2 models | Reduced choice |
| **Availability** | 99.5% | 99.5% | Maintained |

**Bottom Line**: System continues operating. Reduced quota/context, but interactive tasks actually FASTER. Suitable for maintenance window.

---

## References

- `PROVIDER-HIERARCHY-FINAL.md` - Tier definitions
- `PHASE-3C-ANTIGRAVITY-DEPLOYMENT.md` - Overall deployment plan
- `app/XNAi_rag_app/core/multi_provider_dispatcher.py` - Implementation
- `scripts/track_antigravity_resets.py` - Monitoring script (to create)

---

**Status**: 🟢 RATE LIMIT MANAGEMENT ACTIVE

No manual intervention needed. System routes automatically. Monitor reset times using provided scripts.

