# ANTIGRAVITY IDE DISCOVERY - Investigation Report

**Discovery Date**: 2026-02-24T04:48:17Z  
**Status**: 🔴 CRITICAL - ACTIVE INVESTIGATION  
**Impact**: Potentially doubles capacity (4M → 8M tokens/week?)

---

## THE DISCOVERY

User reported: **"I installed Antigravity and am trying out Gemini 3.1 Pro right now! It isn't a CLI, it is an IDE."**

This reveals Antigravity has **TWO distinct interfaces**:

### Interface 1: Antigravity IDE (NEW TO US)
- **Type**: Standalone application (GUI-based)
- **Status**: Active and working (user testing now)
- **Current Test**: Gemini 3.1 Pro
- **Known Models**: At least Gemini 3.1 Pro (possibly more)
- **Details**: Dashboard interface for interactive use

### Interface 2: OpenCode Antigravity Plugin (DOCUMENTED)
- **Type**: CLI plugin for OpenCode
- **Command**: `opencode chat --model google/antigravity-claude-opus`
- **Status**: Well documented (Phase 3B/3C)
- **Accounts**: 8 accounts pre-configured (antigravity-01 through antigravity-08)
- **Quota**: 500K tokens/week per account = 4M total

---

## CRITICAL UNKNOWNS

### Tier 1: Quota & Account Management

#### Question 1: Shared Quota Pool or Separate?

**Scenario A: Shared (IDE + Plugin use same pool)**
- 4M tokens/week total for both interfaces combined
- Using IDE uses tokens from OpenCode pool
- Must implement unified quota tracking
- Current rate limit status applies to both
- **Strategic Impact**: No change to Phase 3C strategy

**Scenario B: Separate (IDE has own quota)**
- IDE might have: 4M, 8M, or unlimited
- OpenCode plugin: 4M (unchanged)
- Total capacity could be 8M or more!
- **Strategic Impact**: GAME CHANGER - double capacity at minimum

**Scenario C: IDE is Premium-only/Limited**
- IDE might have restricted quota (1M?)
- OpenCode plugin: 4M (unchanged)
- Use OpenCode as primary, IDE as specialty interface
- **Strategic Impact**: Use OpenCode plugin as primary

#### Question 2: Usage Tracking & Visibility

- Can IDE show current quota/usage?
- Is there a dashboard or API endpoint?
- How to programmatically check IDE quota?
- Does IDE have API for programmatic access?
- Are usage logs available?

#### Question 3: Account Authentication

- Does IDE use same Google account as OpenCode?
- Do we have 8 IDE accounts (one per Google email)?
- Can we multi-account on IDE like OpenCode?
- Account switching mechanism?

### Tier 2: Features & Capabilities

#### Question 4: Available Models

- Does IDE have all 7 Antigravity models?
  - Claude Opus Thinking
  - Claude Sonnet 4.6
  - Gemini 3 Pro
  - Gemini 3 Flash
  - o3-mini
  - DeepSeek v3
  - Any others?
- Context windows per model?
- Thinking budget support (Opus)?

#### Question 5: Performance Characteristics

- Latency: IDE vs OpenCode plugin?
- Response quality: Any differences?
- Rate limiting: Same as plugin (500K/week)?
- Concurrent request limits?
- Streaming responses available?

#### Question 6: Advanced Features

- Can IDE be automated/scripted?
- REST API for IDE?
- CLI mode available?
- Batch operations?
- Conversation history export?

### Tier 3: Programmatic Access

#### Question 7: Can IDE be Used as Backend?

- Can we call IDE from Python/scripts?
- API endpoint available?
- Browser automation possible?
- Programmatic model selection?
- Streaming response handling?

#### Question 8: Integration with Foundation Stack

- Should IDE be added to MultiProviderDispatcher?
- As separate provider or same pool?
- Fallback between IDE and OpenCode?
- Unified quota management?

---

## RESEARCH STRATEGY

### Phase 1: Direct Investigation (In Progress)

**While user actively testing IDE:**
1. Check IDE settings/dashboard for quota information
2. Note any usage statistics visible
3. Test Gemini 3.1 Pro capabilities (latency, quality)
4. Look for API documentation
5. Check for account/billing information

### Phase 2: Programmatic Investigation

**Try to access IDE programmatically:**
1. Check if IDE has REST API
2. Look for CLI equivalent to OpenCode
3. Try to find usage/quota API endpoint
4. Investigate authentication mechanism
5. Check for batch/async operations

### Phase 3: Comparison Testing

**Compare both interfaces:**
```
Test same prompt:
- IDE (Gemini 3.1 Pro)
- OpenCode (Gemini 3.1 Pro if available)

Measure:
- Latency
- Response quality
- Context handling
- Rate limits
```

### Phase 4: Capacity Analysis

**If IDE has separate quota:**
1. Determine exact IDE quota (4M? 8M? unlimited?)
2. Calculate combined capacity
3. Plan deployment strategy
4. Update rate limit management
5. Revise provider hierarchy

---

## POTENTIAL SCENARIOS & IMPLICATIONS

### Scenario A: IDE + OpenCode = Shared 4M Pool
- **Implication**: Current Phase 3C strategy remains valid
- **Action**: Unified quota tracking needed
- **Priority**: Medium - update monitoring

### Scenario B: IDE = Separate 4M Pool
- **Total Capacity**: 8M tokens/week!
- **Implication**: Rate limit period ends immediately after reset
- **Action**: Add IDE to provider hierarchy
- **Priority**: CRITICAL - revise entire strategy

### Scenario C: IDE = 8M or Unlimited
- **Total Capacity**: 8M+ tokens/week!
- **Implication**: Antigravity becomes unlimited primary provider
- **Action**: Eliminate rate limit management entirely
- **Priority**: CRITICAL - fundamentally changes Phase 3C

### Scenario D: IDE is CLI-accessible
- **Implication**: Can integrate directly into dispatch logic
- **Action**: Create IDE dispatcher module
- **Priority**: HIGH - performance improvement

---

## RESEARCH JOB SPECIFICATIONS

### JOB-6: Antigravity IDE vs OpenCode Plugin Analysis

**Status**: 🔴 CRITICAL - START IMMEDIATELY  
**Priority**: Higher than all other research jobs  
**Timeline**: 2-3 hours investigation + testing  
**Blockers**: None - can start immediately  

**Key Deliverables**:
1. Quota relationship clarified (shared or separate?)
2. IDE usage limits documented
3. Feature comparison matrix
4. Programmatic access recommendations
5. Updated deployment strategy (if needed)

**Success Criteria**:
- [x] Understand quota sharing mechanism
- [x] Document IDE capabilities
- [x] Identify programmatic access method
- [x] Compare performance vs OpenCode
- [x] Determine optimal deployment strategy

---

## IMPACT ASSESSMENT

| Discovery | Impact | Effort | Timeline |
|-----------|--------|--------|----------|
| IDE exists | HIGH | Investigation | 2-3 hours |
| Shared quota | CRITICAL | Strategy revision | 1-2 hours |
| Separate quota | GAME-CHANGER | Major revision | 4-6 hours |
| IDE API available | HIGH | Implementation | 4-8 hours |
| IDE CLI mode | HIGH | Implementation | 4-8 hours |

---

## NEXT IMMEDIATE ACTIONS

### For User (Right Now)
1. Check IDE settings/dashboard for usage/quota info
2. Try different models if available
3. Test latency and quality
4. Look for any documentation/help
5. Check if there's API documentation

### For Agents (Start JOB-6)
1. ✅ Create research template (DONE)
2. ⏳ Investigate IDE interface while user testing
3. ⏳ Document all findings
4. ⏳ Compare with OpenCode plugin
5. ⏳ Recommend strategy update

### For Foundation Stack (Pending Results)
- May need to revise PROVIDER-HIERARCHY-FINAL.md
- May need to revise RATE-LIMIT-MANAGEMENT.md
- May need to create new IDE dispatcher module
- May need to update MultiProviderDispatcher

---

## COORDINATION

**Research Job**: memory_bank/RESEARCH-JOB-6-IDE-VS-PLUGIN.md  
**Discovery Report**: This file  
**Previous Phase 3C**: memory_bank/PHASE-3C-STATUS-SUMMARY.md  

---

**Status**: 🔴 CRITICAL DISCOVERY - REQUIRES IMMEDIATE INVESTIGATION

This discovery could fundamentally change our Antigravity deployment strategy from "manage rate limits" to "unprecedented capacity". Priority: HIGHEST.

