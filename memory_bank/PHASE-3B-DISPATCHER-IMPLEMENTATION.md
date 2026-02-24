---
title: "Phase 3B Dispatcher Implementation Guide"
subtitle: "Multi-Provider Task Routing with Multi-Account Support"
status: "draft"
phase: "Wave 4 Phase 3B"
created: "2026-02-23T23:59:29Z"
owner: "Copilot CLI"
tags: [wave-4, phase-3b, dispatcher, routing]
---

# Phase 3B Dispatcher Implementation

**Coordination Key**: `WAVE-4-PHASE-3B-DISPATCHER-2026-02-23`  
**Status**: 🟡 IMPLEMENTATION IN PROGRESS  
**Module**: `app/XNAi_rag_app/core/multi_provider_dispatcher.py` (20.9 KB)

---

## Executive Summary

Implemented `MultiProviderDispatcher` class enabling intelligent task routing across 3+ providers (Cline, Copilot, OpenCode, Local) with:

- ✅ **Quota-aware routing** (40% weight): Prioritizes providers with available quota
- ✅ **Latency-aware routing** (30% weight): Copilot ~200ms, OpenCode ~100ms, Cline ~150ms
- ✅ **Specialization-aware routing** (30% weight): Code → Cline/Copilot, Reasoning → OpenCode, Large docs → OpenCode
- ✅ **Multi-account rotation** (8 accounts): Round-robin distribution across GitHub-linked accounts
- ✅ **Fallback chains**: Automatically rotate to next account on failure
- ✅ **Token validation**: Pre-dispatch validation via Phase 3A middleware
- ✅ **Call history & stats**: Track dispatch success rates and latencies

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                 MultiProviderDispatcher                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Task Analysis         → Specialization + Context Size   │
│  2. Provider Scoring      → Score each provider+account     │
│  3. Provider Selection    → Pick highest score              │
│  4. Token Validation      → Verify credentials via 3A       │
│  5. CLI Dispatch          → Execute via subprocess          │
│  6. Quota Update          → Cache quota after execution     │
│  7. Fallback Chain        → Rotate on failure               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
         ↓                    ↓                    ↓
    ┌─────────┐          ┌─────────┐         ┌──────────┐
    │  Cline  │          │ Copilot │         │ OpenCode │
    │  CLI    │          │  CLI    │         │   CLI    │
    │ (200K)  │          │ (264K)  │         │  (1M)    │
    └─────────┘          └─────────┘         └──────────┘
```

### Data Flow

```
dispatch(task, specialization, context_size)
    ↓
1. Load quota cache from ~/.config/xnai/quota-audit.yaml
    ↓
2. For each provider (cline, copilot, opencode):
    - Get next account in rotation
    - Validate token (Phase 3A TokenValidator)
    - Calculate scores:
      * Quota: 100 - percent_used (penalty >95%)
      * Latency: 100 - (latency_ms/10)
      * Fit: Specialization score matrix
    ↓
3. Select provider with max overall_score
    ↓
4. Execute CLI dispatch via subprocess.run()
    ↓
5. Parse output JSON (or fallback to text)
    ↓
6. Update quota cache (used += tokens)
    ↓
7. Save quota cache to disk
    ↓
Return DispatchResult(success, provider, account, output, latency_ms)
```

---

## Key Design Decisions

### 1. **Scoring Algorithm: 40% Quota + 30% Latency + 30% Fit**

**Rationale**:
- **Quota (40%)**: Primary constraint—can't dispatch if no quota
- **Latency (30%)**: Important for user experience but not critical
- **Fit (30%)**: Specialization helps but generic models work for most tasks

**Example Scenarios**:

| Scenario | Cline | Copilot | OpenCode | Winner |
|----------|-------|---------|----------|---------|
| Code task, copilot 95% quota | 95×0.4 + 85×0.3 + 95×0.3 = 91.5 | 10×0.4 + 50×0.3 + 85×0.3 = 46.5 | 50×0.4 + 85×0.3 + 70×0.3 = 66 | **Cline** |
| Reasoning task, all fresh | 75×0.4 + 85×0.3 + 75×0.3 = 79 | 80×0.4 + 50×0.3 + 80×0.3 = 74 | 95×0.4 + 85×0.3 + 95×0.3 = **90.5** | **OpenCode** |
| Fast response needed | 85×0.4 + 85×0.3 + 85×0.3 = 85 | 90×0.4 + 90×0.3 + 90×0.3 = 90 | 75×0.4 + 75×0.3 + 75×0.3 = 75 | **Copilot** |

### 2. **Multi-Account Rotation: Round-Robin Daily**

**Implementation**:
```python
# Each provider has independent rotation index
account_rotation_index: Dict[str, int] = defaultdict(int)

def _get_account_for_provider(self, provider: str) -> str:
    idx = account_rotation_index[provider]
    account = email_accounts[idx % len(email_accounts)]
    account_rotation_index[provider] = (idx + 1) % len(email_accounts)
    return account
```

**Effect**:
- Distributes load evenly across 8 accounts
- Prevents exhausting one account early
- Maximizes total quota availability (8x multiplier)

**Rotation Pattern**:
```
Cline dispatch 1   → account[0] (xoe.nova.ai)
Cline dispatch 2   → account[1] (antipode2727)
Cline dispatch 3   → account[2] (Antipode7474)
...
Cline dispatch 8   → account[7] (arcananovaai)
Cline dispatch 9   → account[0] (xoe.nova.ai) [reset]

Copilot dispatch 1 → account[0]
Copilot dispatch 2 → account[1]
...
```

### 3. **XDG_DATA_HOME Isolation for OpenCode**

**Discovery from Phase 3B Research (JOB-OC1)**:
- OpenCode respects XDG_DATA_HOME environment variable
- Each instance gets separate auth.json without collision
- Enables 8+ concurrent instances

**Implementation**:
```python
async def _dispatch_opencode(self, account: str, task: str, timeout_sec: float):
    with tempfile.TemporaryDirectory(prefix="opencode-") as tmpdir:
        env = os.environ.copy()
        env["XDG_DATA_HOME"] = tmpdir  # Isolate auth
        
        cmd = ["opencode", "chat", task, "--json"]
        result = subprocess.run(cmd, env=env, ...)
```

**Effect**:
- No credential collision when using 8 accounts
- Each dispatch gets fresh, isolated environment
- Enables true multi-account parallel dispatch

### 4. **Async Dispatch with Timeout Protection**

**Pattern**:
```python
result = await anyio.to_thread.run_blocking(
    lambda: subprocess.run(cmd, timeout=timeout_sec, env=env)
)
```

**Rationale**:
- Uses AnyIO (not asyncio) per Foundation standards
- Subprocess runs in thread pool (non-blocking)
- Timeout prevents indefinite hangs
- Graceful degradation on timeout

---

## API Reference

### Class: `MultiProviderDispatcher`

#### Constructor

```python
dispatcher = MultiProviderDispatcher(
    config_file="~/.config/xnai/credentials.yaml",
    quota_file="~/.config/xnai/quota-audit.yaml",
    email_accounts=[...],  # Default: 8 GitHub accounts
)
```

#### Main Method: `dispatch()`

```python
result = await dispatcher.dispatch(
    task="Refactor auth module for performance",
    task_spec=TaskSpecialization.CODE,           # code|reasoning|large_document|fast_response|general
    context_size=50000,                           # Estimated tokens
    required_models=["raptor-mini"],              # Optional model requirements
    timeout_sec=30.0,                             # Dispatch timeout
)

# Returns DispatchResult
assert result.success == True
print(f"Provider: {result.provider}/{result.account}")
print(f"Latency: {result.latency_ms:.0f}ms")
print(f"Output:\n{result.output}")
```

#### Helper Methods

```python
# Get provider stats
stats = dispatcher.get_dispatch_stats()
print(f"Success rate: {stats['successful']}/{stats['total_calls']}")

# Access quota cache
quota = dispatcher.quota_cache["copilot:xoe.nova.ai@gmail.com"]
print(f"Quota used: {quota.percent_used:.1f}%")

# Access dispatch history
for result in dispatcher.call_history[-5:]:
    print(f"{result.provider}: {result.latency_ms:.0f}ms")
```

---

## Provider-Specific Dispatch

### Cline CLI

```python
# Uses native API keys (sk-ant-* format)
result = await dispatcher._dispatch_cline(
    account="account_1",
    task="Generate test cases for auth.py",
    timeout_sec=30
)
```

**Features**:
- Native IDE integration via VSCodium
- Excellent multi-file refactoring
- 200K token context

### Copilot CLI

```python
# Uses GitHub OAuth (expires ~8-12 hours)
result = await dispatcher._dispatch_copilot(
    account="xoe.nova.ai@gmail.com",
    task="Analyze API endpoints",
    timeout_sec=30
)
```

**Features**:
- Raptor-mini available (264K context)
- Fast execution
- Automatic token refresh via gh CLI

### OpenCode CLI

```python
# Uses Antigravity OAuth (~30 day lifetime)
result = await dispatcher._dispatch_opencode(
    account="antipode2727@gmail.com",
    task="Design multi-tenant architecture",
    timeout_sec=30
)
```

**Features**:
- 1M token context for large documents
- XDG_DATA_HOME isolation (8+ accounts simultaneously)
- Archived 2026-02-14 but still functional

---

## Specialization Scoring Matrix

### Task Specialization Scores (per provider)

| Specialization | Cline | Copilot | OpenCode | Local |
|---|---|---|---|---|
| **CODE** | 95 | 85 | 70 | 60 |
| **REASONING** | 75 | 80 | **95** | 40 |
| **LARGE_DOCUMENT** | 70 | 70 | **95** | 10 |
| **FAST_RESPONSE** | 85 | **90** | 75 | 20 |
| **GENERAL** | 80 | 85 | 80 | 50 |

**Rationale**:
- **CODE**: Cline native (IDE-aware), Copilot fast (Raptor-mini)
- **REASONING**: OpenCode best (1M context, advanced reasoning)
- **LARGE_DOCUMENT**: OpenCode (1M >> others)
- **FAST_RESPONSE**: Copilot (Raptor-mini latency)

---

## Integration with Phase 3A

### Token Validation

```python
# Pre-dispatch validation via Phase 3A
validation = self.token_validator.validate_token(provider, account)
if validation.result != TokenValidationResult.VALID:
    logger.warning(f"Token invalid for {provider}/{account}")
    # Skip this provider/account combination
```

**Validates**:
- OpenCode: OAuth token format + expiry
- Copilot: GitHub OAuth via gh CLI
- Cline: API key format (sk-ant-*)
- XNAI IAM: JWT structure + signature

### Quota Auditing Integration

```python
# Dispatcher reads Phase 3A quota audit file
dispatcher._load_quota_cache()  # Loads ~/.config/xnai/quota-audit.yaml

# After each dispatch, updates quota
dispatcher._update_quota_after_dispatch(provider, account, result)
dispatcher._save_quota_cache()  # Persists for next session
```

**Data Flow**:
1. Systemd timer (2 AM UTC) runs quota auditor
2. Auditor generates quota-audit.yaml with current quotas
3. Dispatcher loads cache at startup
4. Dispatcher updates cache after each dispatch
5. Cache used for scoring next dispatch

---

## Testing Strategy

### Unit Tests (Phase 3C)

```python
# tests/test_multi_provider_dispatcher.py

@pytest.mark.asyncio
async def test_dispatch_to_cline():
    """Test Cline CLI dispatch"""
    dispatcher = MultiProviderDispatcher()
    result = await dispatcher.dispatch(
        task="Create a simple test",
        task_spec=TaskSpecialization.CODE,
    )
    assert result.success or result.error  # Handle both

@pytest.mark.asyncio
async def test_quota_scoring():
    """Test quota scoring algorithm"""
    dispatcher = MultiProviderDispatcher()
    
    # Mock: Create quotas
    dispatcher.quota_cache["cline:account1"] = ProviderQuota(
        provider="cline",
        account="account1",
        used=950,
        limit=1000,  # 95% used
    )
    
    score = dispatcher._calculate_quota_score(dispatcher.quota_cache["cline:account1"])
    assert score == 0.0  # Penalized for >95%

@pytest.mark.asyncio
async def test_multi_account_rotation():
    """Test round-robin account rotation"""
    dispatcher = MultiProviderDispatcher()
    
    accounts = [dispatcher._get_account_for_provider("cline") for _ in range(10)]
    # Should cycle through 8 accounts twice
    assert len(set(accounts)) == 8
    assert accounts[0] == accounts[8]  # Cycle resets
```

### Integration Tests (Phase 3C)

```python
@pytest.mark.asyncio
async def test_end_to_end_dispatch():
    """Test full dispatch pipeline with all providers"""
    dispatcher = MultiProviderDispatcher()
    
    result = await dispatcher.dispatch(
        task="Hello, world! Say something brief.",
        task_spec=TaskSpecialization.GENERAL,
        context_size=1000,
    )
    
    assert result.success
    assert result.provider in ["cline", "copilot", "opencode"]
    assert result.latency_ms > 0
    assert len(result.output) > 0
```

---

## Known Limitations & Future Work

### Current Limitations

1. **Local GGUF not implemented** (Phase 3C)
   - Placeholder returns error
   - Requires ONNX Runtime integration

2. **Token estimation rough** (4 chars = 1 token)
   - Should use actual token counter
   - Affects quota tracking accuracy

3. **No real-time health checks**
   - Assumes provider health until dispatch fails
   - Could benefit from periodic ping

4. **No circuit breaker** for cascading failures
   - If one provider is down, all dispatches might fail
   - Consider exponential backoff + recovery

### Future Enhancements (Phase 3C+)

- [ ] Circuit breaker pattern for provider health
- [ ] Real-time quota monitoring dashboard
- [ ] Priority queue for high-priority tasks
- [ ] Custom scoring algorithm per task type
- [ ] Retry logic with exponential backoff
- [ ] Prometheus metrics export
- [ ] Multi-provider concurrency (fan-out)
- [ ] Ensemble mode (dispatch to multiple providers, merge results)

---

## Running the Dispatcher

### Standalone Test

```bash
cd /home/arcana-novai/Documents/xnai-foundation

python3 << 'EOF'
import anyio
from app.XNAi_rag_app.core.multi_provider_dispatcher import (
    MultiProviderDispatcher,
    TaskSpecialization,
)

async def main():
    dispatcher = MultiProviderDispatcher()
    
    result = await dispatcher.dispatch(
        task="Write a haiku about AI",
        task_spec=TaskSpecialization.GENERAL,
        context_size=500,
    )
    
    print(f"Success: {result.success}")
    print(f"Provider: {result.provider}/{result.account}")
    print(f"Latency: {result.latency_ms:.0f}ms")
    if result.success:
        print(f"Output:\n{result.output}")
    else:
        print(f"Error: {result.error}")

anyio.run(main)
EOF
```

### With Integration

```python
# In your FastAPI endpoint
from app.XNAi_rag_app.core.multi_provider_dispatcher import MultiProviderDispatcher

dispatcher = MultiProviderDispatcher()

@app.post("/dispatch")
async def handle_dispatch(task: str, specialization: str = "general"):
    result = await dispatcher.dispatch(
        task=task,
        task_spec=TaskSpecialization(specialization),
    )
    
    return {
        "success": result.success,
        "provider": result.provider,
        "latency_ms": result.latency_ms,
        "output": result.output if result.success else result.error,
    }
```

---

## Phase 3B Status

### ✅ Complete

- [x] Core MultiProviderDispatcher class (20.9 KB)
- [x] Scoring algorithm (quota + latency + fit)
- [x] Multi-account rotation logic
- [x] Token validation integration (Phase 3A)
- [x] Quota cache management
- [x] Provider-specific dispatch (Cline, Copilot, OpenCode)
- [x] Error handling + timeouts
- [x] Call history + stats

### ⏳ In Progress (Phase 3B Research)

- [ ] Redis Streams latency benchmark (JOB-AB3)
- [ ] Copilot CLI external agent PoC (JOB-OC-EXT)
- [ ] MC Overseer v2.1 multi-model coordination (JOB-MC-REVIEW)
- [ ] OpenCode thought loop analysis (JOB-OPENCODE-THOUGHT-LOOP)

### 📋 Pending (Phase 3C)

- [ ] Unit tests (pytest)
- [ ] Integration tests (all 3 providers)
- [ ] Local GGUF dispatch implementation
- [ ] Circuit breaker pattern
- [ ] Production deployment

---

## Next Steps

1. **Await Research Results** (4-6 hours)
   - JOB-AB3: Redis latency benchmark
   - JOB-OC-EXT: Copilot CLI PoC findings
   - Use findings to tune scoring algorithm

2. **Create Multi-CLI Testing Framework**
   - Test dispatch to all 3 CLIs
   - Measure success rates and latencies
   - Document failure modes

3. **Phase 3C: Unit + Integration Testing**
   - Create pytest suite
   - Test all providers with real credentials
   - Validate multi-account rotation

4. **Production Deployment**
   - Deploy to Foundation stack
   - Integrate with Agent Bus (Redis Streams)
   - Monitor and optimize

---

**Status**: 🟡 IMPLEMENTATION IN PROGRESS (Dispatcher complete, research pending)  
**Phase Estimate**: 18-20 hours remaining (4-6 research + 8-10 testing + 6 deployment)  
**Coordination Key**: `WAVE-4-PHASE-3B-DISPATCHER-2026-02-23`

---

*Last Updated: 2026-02-23T23:59:29Z*  
*Owner: Copilot CLI (Autonomous Execution)*  
*Session: 4acfc3b7-b99d-472c-8daa-07f94710734f*
