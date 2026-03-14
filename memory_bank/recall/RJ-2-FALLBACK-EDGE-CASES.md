# RJ-2: Fallback Decision Tree - Edge Cases

**Status**: RESEARCH COMPLETE | **Deliverable**: Decision tree + recovery paths

## Cascading Fallback Chain

```
Request arrives
  ↓
Check quota (pre-dispatch)
  ├─ Antigravity available (>10%)? YES → Use Antigravity, continue
  │   └─ Get 429? (rate limited) → Fallback to next
  └─ NO → Continue to next

  ↓
Antigravity all accounts >80% OR 429 received
  ├─ Copilot available (<80%)? YES → Use Copilot, continue
  │   └─ Get error? → Fallback to next
  └─ NO → Continue to next

  ↓
Copilot unavailable/rate limited
  ├─ OpenCode available? YES → Use OpenCode
  │   └─ Get error? → Fallback to next
  └─ NO → Continue to next

  ↓
All external providers exhausted
  └─ Local GGUF (always available)
      └─ Return response (limited context, slower)
```

## Edge Cases & Recovery

### EC-1: All Antigravity Accounts >80%

**Scenario**: All 8 accounts at 80-95% quota

**Decision**:
- If Copilot available: Use Copilot (18.75K/week)
- Else: Continue to OpenCode
- Last resort: Local GGUF

**Recovery Path**:
- Wait for Sunday reset (automatic)
- Manually trigger account refresh (if available)
- Return context-exceeded error if GGUF also full

### EC-2: Antigravity API Down (500 Error)

**Scenario**: Antigravity service temporarily unavailable

**Decision**:
- Mark Antigravity as circuit-open (50-error threshold)
- Route ALL requests to Copilot/OpenCode
- Retry Antigravity in 60 seconds (half-open)

**Recovery Path**:
- Circuit half-opens after timeout
- Single request tests recovery
- Full recovery: 3 consecutive successful requests

### EC-3: Copilot CLI Not Installed

**Scenario**: Quota check fails (copilot CLI missing)

**Decision**:
- Pessimistic fallback: assume 80% quota used
- Still available but risky
- Use for fallback only (non-critical tasks)

**Recovery Path**:
- Log warning
- Continue to OpenCode if Copilot fails
- Admin should install CLI

### EC-4: Rate Limit During Fallback

**Scenario**: Request to Copilot returns 429 (also rate limited)

**Decision**:
- Both Antigravity and Copilot exhausted
- Switch to OpenCode if available
- Cascade to local GGUF

**Recovery Path**:
- Queue task for later retry
- Return "rate-limited" error to user
- Retry after 5 minutes

### EC-5: Rapid Account Exhaustion

**Scenario**: Multiple instances exhaust all accounts within seconds

**Decision**:
- Already handled by circuit breaker
- Circuit opens on 429 errors
- Routes to Copilot immediately

**Recovery Path**:
- Wait for Sunday reset (automatic)
- Or manually refresh via admin API

### EC-6: Multiple Fallback Failures

**Scenario**: Antigravity (429) → Copilot (429) → OpenCode (timeout)

**Decision**:
- Fall back to Local GGUF
- If GGUF also fails: return error

**Recovery Path**:
- Log complete failure chain
- Alert admin
- Return clear error to user

## Decision Tree Pseudocode

```python
async def dispatch_with_fallback(task, context_size):
    # Try Antigravity first
    if is_antigravity_available():
        account = select_best_account()
        try:
            result = await dispatch_to_antigravity(task, account)
            return result
        except RateLimitError:
            logger.warning(f"Antigravity rate limited: {account}")
            # Fall through to next
        except APIError as e:
            if is_temporary(e):
                # Circuit breaker will handle
                logger.warning(f"Antigravity error: {e}")
            # Fall through to next
    
    # Try Copilot
    if is_copilot_available():
        try:
            result = await dispatch_to_copilot(task)
            return result
        except RateLimitError:
            logger.warning("Copilot rate limited")
            # Fall through to next
        except CLINotFoundError:
            logger.error("Copilot CLI not installed")
            # Fall through to next
    
    # Try OpenCode
    if is_opencode_available():
        try:
            result = await dispatch_to_opencode(task)
            return result
        except TimeoutError:
            logger.warning("OpenCode timeout")
            # Fall through to next
    
    # Last resort: Local GGUF
    try:
        result = await dispatch_to_gguf(task)
        return result
    except Exception as e:
        logger.error(f"All providers exhausted: {e}")
        raise AllProvidersExhaustedError()
```

## Monitoring Edge Cases

| Edge Case | Signal | Action |
|-----------|--------|--------|
| All accounts >80% | Quota warning | Prepare fallback |
| Antigravity circuit open | Circuit open event | Route to Copilot |
| Copilot 429 | Rate limit error | Route to OpenCode |
| GGUF timeout | Timeout error | Queue task |
| All providers down | All failures | Alert admin |

## Recovery Patterns

### Pattern 1: Circuit Breaker Recovery
- State: OPEN → Wait 60 sec
- State: HALF-OPEN → Try 1 request
- If success: CLOSED, resume normal
- If failure: OPEN again, wait 120 sec

### Pattern 2: Quota Recovery (Sunday Reset)
- Automatic: Quota resets Sunday midnight UTC
- Detection: Quota API shows reset
- Resume: Circuit breaker tests recovery automatically

### Pattern 3: Manual Recovery
- Admin can manually refresh account quotas
- Admin can force circuit breaker reset
- Admin can disable provider temporarily

---

**Ready for**: Implementation in multi_provider_dispatcher.py  
**Complexity**: High (complex control flow)  
**Test cases**: 8+ edge case scenarios
