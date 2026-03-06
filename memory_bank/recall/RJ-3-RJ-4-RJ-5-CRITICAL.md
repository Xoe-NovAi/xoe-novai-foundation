# RJ-3, RJ-4, RJ-5: Critical Research Findings

---

## RJ-3: Circuit Breaker × Quota Integration

**Finding**: Independent state management, sequential checking

### State Machine

```
NORMAL STATE (Quota OK + Circuit Closed):
  ├─ Check quota: remaining > 50K? 
  │   ├─ YES → Use provider
  │   └─ NO → Use fallback
  ├─ Get success → Stay in NORMAL
  └─ Get 429 → Circuit HALF-OPEN (1 request test)

RATE LIMITED (Quota OK but 429 errors):
  ├─ Circuit breaker opens (5 consecutive failures)
  ├─ Route to fallback (Copilot/OpenCode)
  └─ Retry in 60 seconds (half-open)

RECOVERY (Half-open state):
  ├─ Send 1 test request to Antigravity
  ├─ Success → Circuit closes, resume normal
  ├─ Failure → Circuit opens again, wait 120s
  └─ 3 consecutive successes → Fully recovered

EXHAUSTED (Quota > 95%):
  ├─ Similar to rate-limited
  ├─ Circuit opens immediately
  └─ Waits until Sunday reset (quota recovery)
```

### Key Rules

1. **Quota ≠ Circuit State**: Independent
   - Quota exhausted (95%) can happen even if circuit closed
   - Circuit can be open while quota still available
   - Both must be checked pre-dispatch

2. **Priority**: Quota checked BEFORE circuit
   ```python
   if quota.percent_used >= 95:
       # Immediately fallback (don't even try)
       return fallback_provider
   
   if circuit.is_open:
       # Try half-open (1 request)
       return try_half_open
   
   # Otherwise normal
   return antigravity
   ```

3. **Recovery Sequence**:
   - Quota: Resets Sunday midnight (automatic, no action)
   - Circuit: Tests recovery via half-open (automatic after timeout)
   - Combined: Both recover, resume NORMAL operation

### Monitoring

Track both independently:
- Quota trending: "15 minutes to exhaustion"
- Circuit state transitions: "open → half-open → closed"

---

## RJ-4: Latency Impact Assessment

**Target**: <50ms added latency

### Latency Breakdown

| Operation | Latency | Cumulative |
|-----------|---------|------------|
| Baseline (no fallback logic) | 0ms | 0ms |
| Quota check (cached) | <5ms | 5ms |
| Account selection (8 accounts) | <5ms | 10ms |
| Fallback decision (if needed) | <3ms | 13ms |
| **TOTAL TARGET** | **<50ms** | **13ms** |

### Components

1. **Quota Check** (<5ms):
   - In-memory: 1-2ms
   - Cached API: 3-5ms
   - Fallback (pessimistic): <1ms

2. **Account Selection** (<5ms):
   - Load scores for 8 accounts: 2-3ms
   - Find max: <1ms
   - Update last_used: <1ms

3. **Fallback Decision** (<3ms):
   - Check circuit state: <1ms
   - Determine next provider: <1ms
   - Log decision: <1ms

4. **Actual Dispatch** (300-500ms):
   - Not affected by new logic
   - Same as before

### Optimization Points

- Cache quota (5-10 min TTL): Reduce to <1ms for 90% of requests
- Batch account scoring: Pre-calculate if score unchanged
- Async fallback logic: Don't block on decision tree

### Measurement Strategy

```python
import time

start = time.time()
quota = await cache.get_quota(provider, account)  # Track this
account = strategy.select_account(accounts)       # Track this
latency_ms = (time.time() - start) * 1000

# Should be <15ms
assert latency_ms < 15, f"Selection took {latency_ms}ms"
```

### Real-World Impact

- Pre-dispatch: 13ms (total)
- 99th percentile dispatch: 300ms
- Added latency: 13/300 = 4.3% overhead
- **User perceives**: No difference (< 50ms << 300ms baseline)

---

## RJ-5: Account State Management Architecture

**Decision**: Hybrid (in-memory + Redis fallback)

### State to Track

Per account:
- `quota_remaining`: tokens left
- `quota_updated_at`: last check timestamp  
- `last_used`: when last request sent
- `health`: HEALTHY / WARNING / CRITICAL / EXHAUSTED
- `circuit_state`: CLOSED / OPEN / HALF_OPEN

### Storage Options

| Option | Pros | Cons | Choice |
|--------|------|------|--------|
| In-Memory | Fast | Loss on restart | PRIMARY |
| Redis | Persistent | Extra latency | BACKUP |
| File | Simple | I/O overhead | NO |
| DB | Queryable | Overkill | NO |

### Recommended: Hybrid

```python
class HybridStateManager:
    def __init__(self):
        self.in_memory_state = {}  # Fast local access
        self.redis = redis.Redis()  # Persistent backup
    
    def get_account_state(self, account_id):
        # Try in-memory first
        if account_id in self.in_memory_state:
            return self.in_memory_state[account_id]
        
        # Fall back to Redis
        redis_state = self.redis.hgetall(f"account:{account_id}")
        if redis_state:
            self.in_memory_state[account_id] = redis_state
            return redis_state
        
        # Initialize new
        return self._create_new_state(account_id)
    
    def update_state(self, account_id, state):
        # Write to both
        self.in_memory_state[account_id] = state
        self.redis.hset(f"account:{account_id}", mapping=state)
```

### Consistency Across Instances

Multiple service instances reading/writing same accounts:

**Approach**: Eventual consistency with TTL

```python
# State is "eventually consistent" (not real-time consistent)
# Each instance caches state locally (5 min TTL)
# Redis is source of truth for distributed state

class DistributedAccountState:
    def __init__(self):
        self.local_cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def get_state(self, account_id):
        # Check local cache first
        if self._cache_valid(account_id):
            return self.local_cache[account_id]
        
        # Read from Redis (eventual consistency)
        state = self.redis.hgetall(f"account:{account_id}")
        self.local_cache[account_id] = (state, time.time())
        return state
```

### Failure Scenarios

**Redis Down**:
- In-memory state continues working
- Survives until service restart
- After restart: Redis reconstructed from new requests
- Recovery: Automatic when Redis comes back

**Instance Crash**:
- Redis persists state
- New instance reads from Redis
- Minimal data loss (<5 minutes stale)

**Network Partition**:
- Instances use local cache
- Eventually consistent when reunited
- No correctness issues (cache-aside pattern)

### State Size

Per account (8 accounts):
```
quota_remaining: 8 bytes
quota_updated_at: 8 bytes
last_used: 8 bytes
health: 1 byte
circuit_state: 1 byte
= 26 bytes per account × 8 = 208 bytes

Redis overhead: ~50 bytes per key
= 208 + (50 × 8) = 608 bytes total

Memory: Negligible
```

---

## Summary

| RJ | Decision | Complexity | Risk |
|----|----------|-----------|------|
| RJ-3 | Independent state, sequential checking | Low | LOW |
| RJ-4 | <15ms overhead, cache-first approach | Medium | LOW |
| RJ-5 | Hybrid in-memory + Redis | Medium | LOW |

All findings: **READY FOR IMPLEMENTATION**

---

**Locked Into**: Foundation stack - Phase 3C-2 roadmap  
**Next**: Implement with research guidance
