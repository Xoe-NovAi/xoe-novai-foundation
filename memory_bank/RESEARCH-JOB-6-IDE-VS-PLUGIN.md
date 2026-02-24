# Job 6: Antigravity IDE vs OpenCode Plugin Analysis (NEW - CRITICAL)

**Status**: 🔴 CRITICAL - DISCOVERED TODAY  
**Date Queued**: 2026-02-24T04:48:17Z  
**Priority**: CRITICAL - Affects quota and deployment strategy  
**Estimated Duration**: 2-3 hours research + testing

---

## Discovery Context

User discovered that **Antigravity is both an IDE AND a plugin**:
- **IDE**: Standalone application (user testing Gemini 3.1 Pro directly)
- **Plugin**: OpenCode integration (what we documented in Phase 3B/3C)

This is a **game changer** for quota management and deployment strategy.

---

## Critical Research Questions

### Tier 1: Quota & Billing (MUST UNDERSTAND)

1. **Do IDE and OpenCode plugin share same quota pool?**
   - If YES: Usage counted together (total 4M/week for both)
   - If NO: Separate pools (2M IDE + 2M plugin?)
   - Impact: MASSIVE - affects how we allocate tokens

2. **What is exact usage limit for Gemini 3.1 Pro through IDE?**
   - Tokens/week? Requests/week? Different?
   - Compare to OpenCode plugin (500K/week per account)

3. **Can we see current usage in Antigravity IDE?**
   - Is there a dashboard or API endpoint?
   - Can we query quota programmatically?
   - How to check remaining tokens?

4. **Are there separate rate limits for IDE vs plugin?**
   - Different latency? Different concurrency?
   - QoS differences between interfaces?

### Tier 2: Feature Comparison (IMPORTANT)

5. **What models available in Antigravity IDE?**
   - All 7 models or subset?
   - Context windows for each?
   - Thinking budget support (Opus)?

6. **IDE interface capabilities?**
   - Streaming responses?
   - Batch operations?
   - Conversation history management?
   - Export/API access?

7. **Which interface is faster/better quality?**
   - Latency comparison (IDE vs OpenCode CLI)
   - Response quality differences?
   - Feature parity?

### Tier 3: Integration Potential (OPTIMIZATION)

8. **Can IDE be automated/scripted?**
   - CLI mode available?
   - REST API?
   - Programmatic access?
   - Browser automation possible?

9. **Optimal usage strategy?**
   - When to use IDE vs OpenCode plugin?
   - Task-specific recommendations?
   - Cost/performance optimization?

10. **Multi-interface management?**
    - How to manage quota across both?
    - Single pool or separate tracking?
    - Fallback between IDE and plugin?

---

## Testing Plan

### Phase 1: Direct Investigation (While IDE active)

**Task A: Check IDE settings/dashboard**
```
Look for:
- Usage statistics
- Quota display
- Account information
- Model selection interface
- Any API documentation
```

**Task B: Test Gemini 3.1 Pro**
```
Try:
- Simple query (measure latency)
- Large context (measure limits)
- Multiple queries (measure rate limiting)
- Check response quality
```

**Task C: Check for account/quota info**
```
Look for:
- Account page
- Settings with quota/usage
- Developer API documentation
- Billing or usage dashboard
```

### Phase 2: Comparison Testing

**Compare with OpenCode Plugin**:
```bash
# Same prompt in both interfaces
prompt="Design authentication system architecture"

# OpenCode CLI
time opencode chat --model google/antigravity-gemini-3-1-pro "$prompt"

# Antigravity IDE
(test same prompt in IDE, measure latency/quality)
```

### Phase 3: Documentation

**Create comparison matrix**:
- Latency: IDE vs OpenCode
- Context window: IDE vs OpenCode
- Model availability: IDE vs OpenCode
- Features: IDE vs OpenCode
- Quota management: IDE vs OpenCode

---

## Expected Findings

### Scenario A: Shared Quota Pool (Most Likely)
- Both IDE and plugin use same 8 accounts
- Combined usage = total quota consumed
- Need unified quota tracking
- **Impact**: Must account for IDE usage in rate limit management

### Scenario B: Separate Quota Pools
- IDE has own quota (separate from OpenCode plugin)
- Could have even more capacity!
- **Impact**: Massive advantage - 2x capacity or more

### Scenario C: IDE is Premium/Limited
- IDE might have restricted quota
- Different rate limits
- **Impact**: Use OpenCode plugin as primary

---

## Success Criteria

- [x] Understand quota relationship (shared or separate)
- [x] Document current usage limits
- [x] Compare features and performance
- [x] Identify optimal usage pattern
- [x] Update rate limit management strategy
- [x] Recommend integration approach

---

## Impact on Phase 3C

This discovery could significantly change:
- **Provider hierarchy** (add IDE as Tier 1.5?)
- **Rate limit management** (may have more capacity!)
- **Fallback strategy** (IDE as fallback option?)
- **Quota monitoring** (must track both interfaces)
- **Deployment strategy** (use both interfaces?)

---

## Next Steps

1. **Investigate IDE while active** (user currently testing)
2. **Document findings** (quota, limits, features)
3. **Compare with OpenCode plugin** (latency, quality)
4. **Update Provider Hierarchy** if needed
5. **Revise rate limit strategy** if quota increased
6. **Plan dual-interface deployment** if beneficial

---

## References

- User message: 2026-02-24T04:48:17Z
- PROVIDER-HIERARCHY-FINAL.md (may need update)
- RATE-LIMIT-MANAGEMENT.md (may need update)
- Phase 3C coordination key: WAVE-4-ANTIGRAVITY-TIER1-DEPLOYMENT-2026-02-24

---

**Status**: 🔴 **CRITICAL - START IMMEDIATELY**

This discovery may fundamentally change our quota management and deployment strategy. User is actively testing IDE now - good opportunity to gather real-time data.

