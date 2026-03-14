# Phase 3C Knowledge Gap Research Plan

**Status**: 🟡 RESEARCH JOBS QUEUED  
**Date**: 2026-02-24T01:51:30Z  
**Target**: Fill 5 critical knowledge gaps before Phase 3C production deployment

---

## Research Job Queue

### JOB-1: ANTIGRAVITY RESET TIMING (🔴 CRITICAL - BLOCKS RATE LIMIT MANAGEMENT)

**Objective**: Verify exact Sunday reset behavior for Antigravity accounts

**Background**:
- All 8 Antigravity accounts hitting 80-95% quota
- Rate limit fallback depends on knowing exact reset time
- Assumed UTC midnight Sunday, but needs verification

**Research Questions**:
1. Do all 8 accounts reset simultaneously or on individual schedules?
2. Is reset UTC midnight or per-timezone?
3. Is there a 2-4 day window as user stated or immediate reset?
4. Does quota reset to 500K or different amount?
5. Can we detect reset programmatically (API call vs CLI)?

**How to Verify**:
```bash
# Collect baseline (today)
opencode chat --model google/antigravity-claude-opus-4-6 "status" 2>&1 | grep -i "quota\|remaining"

# Wait for Sunday
# Collect post-reset (Sunday after midnight UTC)
# Compare quota values from all 8 accounts
```

**Success Criteria**:
- ✅ Exact reset time documented (UTC, per account, synchronized)
- ✅ Quota increase verified (from 5-25% available back to 500K)
- ✅ Reset detection method implemented

**Blockers Resolved By**:
- Enables accurate fallback chain planning
- Allows circuit breaker tuning
- Determines when to re-enable Antigravity primary

**Output**: `memory_bank/ANTIGRAVITY-RESET-TIMING-VERIFIED.md`

---

### JOB-2: CLAUDE OPUS THINKING BUDGET OPTIMIZATION (🟡 HIGH - IMPROVES REASONING QUALITY)

**Objective**: Determine optimal thinking budget allocation for Opus Thinking

**Background**:
- Claude Opus supports configurable thinking budget (8-32K tokens)
- Currently unknown: default allocation, optimal range, impact on latency
- Affects reasoning task quality and token efficiency

**Research Questions**:
1. What is the default thinking budget for Claude Opus via Antigravity?
2. How does thinking budget affect response quality? (8K vs 16K vs 32K)
3. How does thinking budget affect latency? (proportional, exponential?)
4. When should we increase/decrease budget?
5. Can thinking budget be configured per-request?

**How to Verify**:
```bash
# Test 1: Default behavior (no explicit budget)
opencode chat --model google/antigravity-claude-opus-4-6 \
  "Design authentication system" | time

# Test 2: Explicit budget (8K)
opencode chat --model google/antigravity-claude-opus-4-6 \
  "Design authentication system" --thinking-budget 8000 | time

# Test 3: Explicit budget (32K)
opencode chat --model google/antigravity-claude-opus-4-6 \
  "Design authentication system" --thinking-budget 32000 | time

# Measure: latency, response quality, token usage
```

**Success Criteria**:
- ✅ Default thinking budget identified
- ✅ Quality/latency tradeoff documented
- ✅ Recommendation matrix created (task type → budget)
- ✅ Best practices documented

**Blockers Resolved By**:
- Enables better architectural reasoning tasks
- Optimizes token usage
- Improves response quality for complex decisions

**Output**: `memory_bank/CLAUDE-OPUS-THINKING-BUDGET-GUIDE.md`

---

### JOB-3: DEEPSEEK V3 SPECIALIZATION EVALUATION (🟡 MEDIUM - IMPROVES MODEL SELECTION)

**Objective**: Determine when DeepSeek v3 is preferred over Claude/Gemini

**Background**:
- DeepSeek v3 included in Antigravity models but not fully evaluated
- Latency measured (862ms) but use cases unknown
- Need specialization matrix to know when to route to DeepSeek

**Research Questions**:
1. What is DeepSeek v3's primary strength? (reasoning, code, speed?)
2. When does DeepSeek outperform Claude/Gemini?
3. What are DeepSeek's known weaknesses?
4. Is it better for any specific task types?
5. Should it be in primary routing or fallback only?

**How to Verify**:
```bash
# Test 1: Code generation
opencode chat --model google/antigravity-deepseek-v3 "Write fibonacci function" | grep -c "def"

# Test 2: Reasoning
opencode chat --model google/antigravity-deepseek-v3 "Explain quantum computing"

# Test 3: Speed (compare vs Sonnet)
time opencode chat --model google/antigravity-deepseek-v3 "Quick fact"

# Compare against Claude Sonnet/Opus, Gemini Pro
```

**Success Criteria**:
- ✅ Specialization areas identified
- ✅ Quality matrix created (code/reasoning/creative/speed)
- ✅ Recommendation: Primary routing or fallback?
- ✅ Use case examples documented

**Blockers Resolved By**:
- Improves model selection algorithm
- Unlocks DeepSeek for specialized tasks
- Better utilizes all 5 available models

**Output**: `memory_bank/DEEPSEEK-V3-SPECIALIZATION-GUIDE.md`

---

### JOB-4: COPILOT FALLBACK TESTING (🟡 MEDIUM - VALIDATES RATE LIMIT FALLBACK)

**Objective**: Validate Copilot fallback chain during rate limit period

**Background**:
- Copilot fallback planned for when Antigravity exhausted
- Needs real testing to verify: works, quality acceptable, latency reasonable
- Test during current rate limit period (all Antigravity accounts 80-95%)

**Research Questions**:
1. Does Copilot fallback work smoothly when Antigravity unavailable?
2. Is context window 264K sufficient for most tasks?
3. Is latency 200ms acceptable as fallback?
4. How many strategic requests fit in 18.75K/week?
5. What is quality loss vs Antigravity?

**How to Verify**:
```bash
# Verify Antigravity exhausted
python -c "from app.XNAi_rag_app.core.multi_provider_dispatcher import MultiProviderDispatcher; \
  d = MultiProviderDispatcher(); \
  print('Antigravity available:', d.check_account_quota('antigravity-01'))"

# Should return: False or very low (<50K)

# Test dispatch to Copilot fallback
python -c "
from app.XNAi_rag_app.core.multi_provider_dispatcher import MultiProviderDispatcher
d = MultiProviderDispatcher()
result = d.dispatch({'role': 'user', 'content': 'Quick test'})
print('Provider used:', result.get('provider', 'unknown'))
print('Latency:', result.get('latency_ms', 'unknown'))
"

# Should return: provider=copilot, latency ~200ms
```

**Success Criteria**:
- ✅ Fallback routing verified working
- ✅ Quality acceptable (at least 80% vs Antigravity)
- ✅ Latency acceptable (<500ms)
- ✅ No user-facing errors
- ✅ Quota tracking accurate

**Blockers Resolved By**:
- Validates fallback chain works as designed
- Detects any routing bugs early
- Builds confidence in rate limit management

**Output**: `memory_bank/COPILOT-FALLBACK-VALIDATION.md`

---

### JOB-5: OPENCODE CLI ADVANCED FEATURES RESEARCH (🟡 MEDIUM - ENHANCES ANTIGRAVITY INTEGRATION)

**Objective**: Research advanced OpenCode CLI features for better Antigravity integration

**Background**:
- OpenCode has many CLI features, not all documented
- Antigravity accessed via `--model google/antigravity-*`
- Unknown: streaming, retry logic, batch operations, configuration

**Research Questions**:
1. Does OpenCode support streaming mode for Antigravity?
2. What retry logic is built-in?
3. Can we pre-configure default model?
4. Does `--json` flag work with Antigravity models?
5. Are there performance flags (parallelization, caching)?

**How to Verify**:
```bash
# Test 1: Streaming mode
opencode chat --model google/antigravity-claude-opus-4-6 \
  --stream "Write long response" | head -20

# Test 2: JSON output
opencode chat --model google/antigravity-claude-opus-4-6 \
  --json "test" | python3 -m json.tool

# Test 3: Configuration
opencode config show | grep -i antigravity

# Test 4: Retry behavior
opencode chat --model google/antigravity-claude-opus-4-6 \
  --retry 3 "test" 2>&1 | grep -i retry
```

**Success Criteria**:
- ✅ Advanced features documented
- ✅ Best practices for subprocess integration
- ✅ Performance optimization flags identified
- ✅ Error handling patterns documented

**Blockers Resolved By**:
- Improves MultiProviderDispatcher subprocess handling
- Enables streaming responses (better UX)
- Unlocks performance optimizations

**Output**: `memory_bank/OPENCODE-ADVANCED-FEATURES.md`

---

## Research Execution Timeline

### Parallel Batch (All can run simultaneously)

**Priority 1 (Start immediately)**:
- JOB-1: ANTIGRAVITY RESET TIMING (critical path, 2-4 days to observe)
- JOB-2: CLAUDE OPUS THINKING BUDGET (can start now, <2 hours)
- JOB-4: COPILOT FALLBACK TESTING (can start now, <1 hour)

**Priority 2 (Start after Priority 1)**:
- JOB-3: DEEPSEEK V3 SPECIALIZATION (1-2 hours)
- JOB-5: OPENCODE ADVANCED FEATURES (1-2 hours)

### Estimated Timeline

**Day 1** (Today):
- ✅ Start JOB-1 (baseline quota capture)
- ✅ Start JOB-2 (thinking budget testing)
- ✅ Start JOB-4 (fallback validation)
- Estimated output: 3/5 jobs (60-80% done)

**Days 2-3**:
- ⏳ Continue JOB-1 (waiting for Sunday reset)
- ✅ Start JOB-3 (DeepSeek evaluation)
- ✅ Start JOB-5 (OpenCode features)
- Estimated output: 4/5 jobs ready, JOB-1 awaiting reset

**Days 4-5** (After Sunday Reset):
- ✅ Complete JOB-1 (verify reset occurred)
- ✅ Finalize all findings
- Estimated output: All 5/5 jobs complete

---

## Success Criteria (All Jobs)

- [x] All research questions answered
- [x] Findings documented in memory_bank
- [x] Recommendations actionable for Phase 3C deployment
- [x] Integration points identified for MultiProviderDispatcher
- [x] No critical blockers remaining

---

## References

- `PROVIDER-HIERARCHY-FINAL.md` - Context for Job 3-4
- `RATE-LIMIT-MANAGEMENT.md` - Context for Job 1, 4
- `app/XNAi_rag_app/core/multi_provider_dispatcher.py` - Integration target
- `app/XNAi_rag_app/core/antigravity_dispatcher.py` - Integration target

---

**Status**: 🟡 RESEARCH JOBS QUEUED FOR PARALLEL EXECUTION

Priority 1 jobs (Reset Timing, Thinking Budget, Fallback) should start immediately.
Priority 2 jobs (DeepSeek, OpenCode Features) can start after Priority 1 initial results.

