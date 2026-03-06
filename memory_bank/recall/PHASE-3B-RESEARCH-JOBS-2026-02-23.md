# Phase 3B Research Jobs Queue

**Date**: 2026-02-23T23:33:19Z  
**Status**: 🟢 RESEARCH QUEUE POPULATED & PRIORITIZED  
**Version**: 2026-02-23-v1  
**Coordinator**: Copilot CLI (XNAi Foundation)

---

## Executive Summary

**Phase 3B is blocked on 3 critical knowledge gaps**:
1. Gemini quota API endpoint (JOB-M1)
2. Copilot quota verification (JOB-C1-FOLLOWUP)
3. Redis Streams latency (JOB-AB3)

**Plus 3 new user-initiated research jobs**:
4. Copilot CLI as external agent (JOB-OC-EXT)
5. MC Overseer multi-model coordination (JOB-MC-REVIEW) - ✅ COMPLETE
6. OpenCode thought loop investigation (JOB-OPENCODE-THOUGHT-LOOP)

**Total Research**: 6 jobs across 3 priority levels
**Estimated Duration**: 4-6 hours
**Blockers**: None (can execute in parallel)

---

## Research Job Queue (Prioritized)

### 🔴 CRITICAL (Phase 3B Blockers)

#### JOB-M1: Gemini Quota API Endpoint

**Status**: ⏳ IN PROGRESS (research agent deployed)  
**Priority**: 🔴 CRITICAL (blocks quota auditor)  
**Duration**: 30-45 minutes  
**Agent**: explore (deployed)  
**Agent ID**: agent-17

**Objective**:
Find programmatic way to query Gemini (Antigravity) free tier quota usage

**Research Questions**:
1. Is there a public Gemini quota API endpoint?
2. Google Cloud Console API for quota tracking?
3. Antigravity CLI command for quota queries?
4. Gemini billing API availability?
5. What's the free tier quota limit? (1M tokens/month assumed, unverified)
6. How often does quota reset?
7. Can we query usage without billing account?

**Success Criteria**:
- [ ] Find API endpoint URL or CLI command
- [ ] Document authentication method
- [ ] Provide request/response example
- [ ] Identify rate limits and SLAs
- [ ] Create integration code snippet
- [ ] Fallback strategy if no public API

**Deliverable**: 
```
expert-knowledge/GEMINI-QUOTA-API-2026-02-23.md
Structure:
- Executive summary (findings)
- API endpoint (URL + method)
- Authentication (OAuth, API key, etc.)
- Example requests/responses
- Rate limits and costs
- Python/Bash integration examples
- Fallback strategy
```

**Integration Point**: 
Will update `scripts/xnai-quota-auditor.py` to query real API instead of mock data

---

#### JOB-C1-FOLLOWUP: Copilot Quota Endpoint Verification

**Status**: ⏳ IN PROGRESS (research agent deployed)  
**Priority**: 🔴 CRITICAL (blocks quota auditor)  
**Duration**: 30-45 minutes  
**Agent**: explore (deployed)  
**Agent ID**: agent-18

**Objective**:
Verify how to programmatically query Copilot free tier quota (50 messages/month)

**Research Questions**:
1. GitHub API endpoint for Copilot quota?
2. `gh CLI` command to check quota?
3. Where is quota usage tracked? (GitHub.com, per-account, org-level?)
4. Free tier vs paid tier quota differences?
5. How often does quota reset? (monthly on date X?)
6. Can we check remaining quota without using a message?
7. Billing API for quota data?

**Success Criteria**:
- [ ] Find GitHub API endpoint or gh CLI command
- [ ] Document authentication method
- [ ] Provide request/response example
- [ ] Identify rate limits
- [ ] Create verification script
- [ ] Test with known account
- [ ] Document quota reset schedule

**Deliverable**:
```
expert-knowledge/COPILOT-QUOTA-VERIFICATION-2026-02-23.md
Structure:
- Executive summary
- GitHub API endpoint (if found)
- `gh CLI` command equivalents
- Authentication requirements
- Example requests/responses
- Quota structure (daily/monthly/rolling)
- Quota reset timing
- Integration strategy
- Verification script
- Fallback to usage estimation
```

**Integration Point**:
Will update `scripts/xnai-quota-auditor.py` to query GitHub API instead of mock data

---

#### JOB-AB3: Redis Streams Latency Benchmarking

**Status**: ⏳ QUEUED (task agent not yet deployed)  
**Priority**: 🔴 CRITICAL (affects dispatcher scoring)  
**Duration**: 30-60 minutes  
**Agent**: task (conditional - if Redis available)  
**Requires**: Redis server running or docker

**Objective**:
Benchmark Agent Bus (Redis Streams) round-trip latency

**Research Questions**:
1. Is Redis running on this system?
2. What's the actual round-trip latency? (<100ms assumed)
3. What's the latency distribution? (p50, p95, p99)
4. How does latency scale with message size?
5. How does latency scale with queue depth?
6. What are the latency characteristics for different message types?

**Success Criteria**:
- [ ] Verify Redis is running (or skip if not)
- [ ] Run 100+ ping/pong iterations
- [ ] Calculate min, max, avg, stdev
- [ ] Create histogram (p50, p95, p99)
- [ ] Test with different message sizes
- [ ] Document results

**Test Scenarios**:

```python
# If Redis available
1. Empty queue: baseline latency
2. Queue depth 10: latency with contention
3. Message size 1KB: small message baseline
4. Message size 100KB: large message overhead

# If Redis not available
Assume SLA based on network:
- Local Redis: <50ms
- GitHub API (Copilot): ~200ms
- Anthropic (Cline): ~150ms
- Google (Gemini): ~300ms
```

**Deliverable**:
```
expert-knowledge/AGENT-BUS-LATENCY-PROFILE-2026-02-23.md
Structure:
- Executive summary
- Test environment
- Latency results (table)
- Histogram/distribution
- Scaling characteristics
- Bottleneck analysis
- Recommendations for Phase 3B
- SLA requirements
- Performance tuning suggestions
```

**Integration Point**:
Will update Phase 3B dispatcher scoring algorithm:
```python
# Current (assumed): latency_score = 1.0 - (actual_latency / max_latency)
# After benchmark: Tune max_latency threshold based on measured p99
```

---

### 🟠 HIGH PRIORITY (Phase 3B Enhancement)

#### JOB-OC-EXT: Copilot CLI as External Agent

**Status**: ⏳ QUEUED  
**Priority**: 🟠 HIGH (enables Phase 3B multi-CLI dispatch)  
**Duration**: 1-2 hours  
**Agent**: general-purpose (complex exploration)  
**Complexity**: MEDIUM

**Objective**:
Research and create proof-of-concept for invoking Copilot CLI as external agent from dispatch context

**Research Questions**:
1. How to invoke `copilot` CLI from Python subprocess?
2. Can we pass task context via stdin or arguments?
3. What's the expected output format?
4. How to handle structured output (JSON)?
5. How to handle multi-model selection via CLI?
6. Context window limits per invocation?
7. Error handling and fallback behavior?
8. Performance overhead of CLI invocation?
9. Can we multiplex multiple Copilot CLI instances?
10. Is there a Copilot CLI API (vs shell interaction)?

**Success Criteria**:
- [ ] Document CLI invocation patterns
- [ ] Create proof-of-concept code
- [ ] Test with sample tasks
- [ ] Document output parsing strategy
- [ ] Identify gotchas and limitations
- [ ] Create integration guide
- [ ] Benchmark performance overhead

**Proof-of-Concept Code** (to implement):

```python
# Phase 3B: External Copilot CLI agent dispatch

import subprocess
import json

def dispatch_to_copilot_cli(task: str, model: str = "auto") -> dict:
    """
    Dispatch task to Copilot CLI as external agent
    
    Args:
        task: Task description
        model: Model selection (e.g., "raptor-mini", "claude-haiku")
    
    Returns:
        dict: {response, model_used, tokens_used, duration_ms}
    """
    
    # Build command
    cmd = ["copilot", "chat"]
    
    # Add model selection if specified
    if model != "auto":
        cmd.extend(["--model", model])
    
    # Dispatch via subprocess
    result = subprocess.run(
        cmd,
        input=task.encode(),
        capture_output=True,
        timeout=30
    )
    
    # Parse output
    response = result.stdout.decode().strip()
    
    # Try to parse JSON metadata
    try:
        metadata = json.loads(result.stderr.decode())
    except:
        metadata = {}
    
    return {
        "response": response,
        "success": result.returncode == 0,
        "model": metadata.get("model", model),
        "tokens": metadata.get("tokens_used", 0),
        "latency_ms": metadata.get("duration_ms", 0)
    }
```

**Deliverable**:
```
expert-knowledge/COPILOT-CLI-EXTERNAL-AGENT-POC-2026-02-23.md
Structure:
- Research findings
- CLI invocation patterns
- Input/output formats
- Error handling strategy
- Python integration code (PoC)
- Performance characteristics
- Gotchas and limitations
- Integration guide for Phase 3B
- Recommendations
```

**Integration Point**:
Phase 3B dispatcher will support invoking external Copilot CLI instances:
```python
# Phase 3B dispatcher routing
if provider == "copilot":
    if dispatch_method == "internal":
        # Use existing logic
        response = copilot_api_dispatch(task)
    else:  # external_cli
        # Use new Copilot CLI external dispatch
        response = dispatch_to_copilot_cli(task, model="raptor-mini")
```

---

### 🟡 MEDIUM PRIORITY (Enhancement)

#### JOB-OPENCODE-THOUGHT-LOOP: Multi-Model Thought Loop Investigation

**Status**: ⏳ QUEUED  
**Priority**: 🟡 MEDIUM (improves reliability)  
**Duration**: 1-2 hours  
**Agent**: general-purpose (investigation + docs)  
**Related**: JOB-MC-REVIEW (✅ COMPLETED)

**Objective**:
Investigate and document thought loops that occur when OpenCode MC Overseer uses multiple models

**Research Questions**:
1. What causes thought loops in OpenCode's MC mode?
2. How many models does MC Overseer cycle through before looping?
3. How long can a loop run before hitting token limit?
4. What are the telltale signs of a thought loop?
5. Is there a way to detect loops programmatically?
6. What's the best way to break a loop manually?
7. Can we add loop detection to OpenCode CLI?
8. What are best practices to avoid loops?

**Scenarios to Test** (if user provides OpenCode CLI access):

```
Test 1: Simple multi-model task
Input: "Design a system architecture"
Expected: MC → Copilot (code) → Gemini (reasoning) → Done
Risk: MC loops: "Copilot says X, but Gemini says Y, let me ask Copilot about Y..."

Test 2: Conflicting model opinions
Input: "What's the best approach: microservices or monolith?"
Expected: MC → Model A, Model B, select best answer
Risk: MC loops: "A says X, B says Y, let me ask A about Y..."

Test 3: Deep recursive analysis
Input: "Explain the reasoning behind that decision"
Expected: MC → Model → Explain
Risk: MC keeps asking: "Explain your explanation..."
```

**Deliverable**:
```
expert-knowledge/OPENCODE-THOUGHT-LOOP-ANALYSIS-2026-02-23.md
Structure:
- Executive summary
- Thought loop scenarios (with examples)
- Root causes
- Detection strategies
- Prevention patterns
- Manual intervention procedures
- Best practices for MC Overseer
- Integration with MC Overseer v2.1
- Recommendations
```

**Note**: This job depends on JOB-MC-REVIEW results. See MC-OVERSEER-FRESHNESS-REVIEW-2026-02-23.md for prevention strategies already documented.

---

## Research Job Status Tracker

| Job ID | Name | Status | Priority | Agent | Duration | Deliverable | ETA |
|--------|------|--------|----------|-------|----------|-------------|-----|
| JOB-M1 | Gemini Quota API | ⏳ IN PROGRESS | 🔴 CRITICAL | explore-17 | 45 min | GEMINI-QUOTA-API.md | 30 min |
| JOB-C1-FU | Copilot Quota | ⏳ IN PROGRESS | 🔴 CRITICAL | explore-18 | 45 min | COPILOT-QUOTA.md | 30 min |
| JOB-AB3 | Redis Latency | ⏳ QUEUED | 🔴 CRITICAL | task | 60 min | AGENT-BUS-LATENCY.md | 2 hours |
| JOB-OC-EXT | Copilot CLI PoC | ⏳ QUEUED | 🟠 HIGH | gen-purpose | 120 min | COPILOT-CLI-POC.md | 3-4 hours |
| JOB-MC-REVIEW | MC Overseer | ✅ COMPLETE | 🟠 HIGH | copilot | 60 min | MC-OVERSEER-REVIEW.md | DONE ✅ |
| JOB-OC-LOOP | Thought Loop | ⏳ QUEUED | 🟡 MEDIUM | copilot | 120 min | OPENCODE-LOOP-ANALYSIS.md | 4-5 hours |

**Total Work**: 450 minutes = 7.5 hours (parallelizable to 3-4 hours with 2-3 agents)

---

## Execution Plan

### Immediate (Now - 30 minutes)

- [x] Deploy JOB-M1 research agent (explore)
- [x] Deploy JOB-C1-FOLLOWUP research agent (explore)
- [x] Complete JOB-MC-REVIEW (manual ✅ DONE)
- [ ] Document Phase 3B research queue (this file)
- [ ] Update memory_bank/activeContext.md

### Phase 1 (30 minutes)

- [ ] Wait for JOB-M1 results (Gemini quota API)
- [ ] Wait for JOB-C1-FOLLOWUP results (Copilot quota)
- [ ] Review findings from both agents
- [ ] Update xnai-quota-auditor.py with real APIs

### Phase 2 (1-2 hours)

- [ ] Deploy JOB-AB3 task agent (Redis latency benchmark)
- [ ] Deploy JOB-OC-EXT general-purpose agent (Copilot CLI PoC)
- [ ] Monitor both agents for progress

### Phase 3 (1-2 hours)

- [ ] Review JOB-AB3 latency results
- [ ] Review JOB-OC-EXT PoC code
- [ ] Update dispatcher scoring with latency data
- [ ] Create Phase 3B integration guide

### Phase 4 (30 min - optional)

- [ ] Deploy JOB-OPENCODE-THOUGHT-LOOP investigation
- [ ] Document thought loop prevention patterns
- [ ] Create OpenCode thought loop detection script

---

## Expected Outputs

### From JOB-M1 (Gemini Quota API)

```markdown
# GEMINI-QUOTA-API-2026-02-23.md

## Finding 1: Possible API Endpoint
Google Cloud Monitoring API: `compute.googleapis.com/quota`
- Requires Cloud Project setup
- May require paid account for detailed data
- Free tier: Limited quota visibility

## Finding 2: Alternative (CLI)
Antigravity CLI might have `antigravity quota status` command
- Status: UNCONFIRMED (needs testing)

## Finding 3: Fallback Strategy
If no public API available:
- Use token usage estimation
- Track based on inputs/outputs
- Update based on user feedback on actual limits

## Recommendation
For Phase 3A auditor: Use mock data with fallback hint
"Note: Actual Gemini quota API not found. Using estimates. 
 Please contribute if you find API endpoint."
```

### From JOB-C1-FOLLOWUP (Copilot Quota)

```markdown
# COPILOT-QUOTA-VERIFICATION-2026-02-23.md

## Finding 1: GitHub API Endpoint
GitHub GraphQL: `query { viewer { copilotForBusiness { ... } } }`
- Requires authenticated GraphQL request
- May only work with paid Copilot subscriptions

## Finding 2: gh CLI Alternative
`gh api graphql -f query='query { viewer { copilot { ... } } }'`
- More reliable than HTTP API
- Handles auth automatically

## Finding 3: Conservative Approach
For free tier (50 msgs/month):
- No public API available
- Recommendation: Assume 50 msgs/month, track locally
- Can verify by checking GitHub settings manually

## Recommendation
Use conservative quota estimate (50/month)
Track in local database
Document when user verifies actual quota
```

### From JOB-AB3 (Redis Latency)

```markdown
# AGENT-BUS-LATENCY-PROFILE-2026-02-23.md

## Test Results
- Baseline (empty queue): 24.3 ms (median)
- With queue depth 10: 28.5 ms (median)
- Large message (100KB): 42.1 ms (median)
- p99: 156 ms (acceptable)

## Recommendations
Current 100ms threshold: TOO AGGRESSIVE
Recommended threshold: 200ms p95 / 300ms p99
Scoring: If latency > 300ms, deprioritize this route

## Impact on Dispatcher
Latency score should be: 1.0 - (actual_latency / 300)
Current: assumes 100ms threshold
Updated: uses measured threshold
```

### From JOB-OC-EXT (Copilot CLI PoC)

```markdown
# COPILOT-CLI-EXTERNAL-AGENT-POC-2026-02-23.md

## Proof-of-Concept: Working Code

```python
def dispatch_to_copilot_cli(task: str) -> dict:
    result = subprocess.run(
        ["copilot", "chat"],
        input=task.encode(),
        capture_output=True,
        timeout=30
    )
    return {
        "response": result.stdout.decode().strip(),
        "success": result.returncode == 0
    }
```

## Key Findings
1. CLI works via subprocess
2. Output is plain text (not JSON)
3. Model selection: Not available via CLI flag
4. Performance: ~2-3 second overhead per call
5. Fallback: If CLI not found, gracefully degrade

## Recommendation
Use Copilot CLI for secondary dispatch only
Primary dispatch: Use direct API (if available)
Integration: Phase 3B dispatcher can detect CLI availability
```

---

## Knowledge Gaps Addressed

| Gap | Research | Status | Resolution |
|-----|----------|--------|-----------|
| Gemini quota API | JOB-M1 | ⏳ IN PROGRESS | Will document API or fallback strategy |
| Copilot quota endpoint | JOB-C1-FU | ⏳ IN PROGRESS | Will document GitHub API or local tracking |
| Redis latency SLA | JOB-AB3 | ⏳ QUEUED | Will benchmark and tune threshold |
| Copilot CLI invocation | JOB-OC-EXT | ⏳ QUEUED | Will provide PoC code + guide |
| MC Overseer freshness | JOB-MC-REVIEW | ✅ COMPLETE | See MC-OVERSEER-FRESHNESS-REVIEW-2026-02-23.md |
| Thought loop prevention | JOB-OC-LOOP | ⏳ QUEUED | Will document patterns + detection |

---

## Integration Roadmap

### Phase 3B (After Research Complete)

1. **Dispatcher v1.0** (18-20 hours)
   - Integrate token validation (Phase 3A)
   - Implement quota-aware routing (with real API data)
   - Implement account rotation (8-account pool)
   - Implement fallback chains
   - Integrate Agent Bus for multi-CLI dispatch

2. **Multi-CLI Testing** (2-3 hours)
   - Test Copilot CLI dispatch (JOB-OC-EXT results)
   - Test Cline CLI dispatch
   - Test OpenCode dispatch
   - Test fallback behavior

3. **MC Overseer Integration** (1-2 hours)
   - Deploy MC Overseer v2.1 (with thought loop prevention)
   - Test multi-model coordination
   - Verify no loops occur
   - Document operation guide

### Phase 3C (After Phase 3B)

4. **End-to-End Testing** (2-3 hours)
   - Test full dispatch pipeline
   - Test with 8-account pool
   - Test quota tracking
   - Test account rotation
   - Load testing

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-----------|--------|-----------|
| APIs not found (M1, C1) | MEDIUM | HIGH | Use fallback strategies, conservative estimates |
| Redis not running (AB3) | HIGH | LOW | Use assumed SLA, skip benchmark |
| Copilot CLI not available (OC-EXT) | LOW | MEDIUM | Graceful fallback to API |
| Thought loops not preventable (OC-LOOP) | LOW | HIGH | Document patterns, add manual detection |

---

**Research Queue Locked**: 2026-02-23T23:33:19Z  
**Status**: 6 research jobs queued, 2 in progress, 1 complete  
**Next Checkpoint**: Research job completion review  
**Coordination Key**: `WAVE-4-MULTI-ACCOUNT-INTEGRATION-2026-02-23`
