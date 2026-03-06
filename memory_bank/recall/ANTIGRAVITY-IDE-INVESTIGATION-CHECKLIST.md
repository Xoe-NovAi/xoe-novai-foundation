# ANTIGRAVITY IDE QUICK INVESTIGATION CHECKLIST

**Date**: 2026-02-24T04:48:17Z  
**User Status**: Testing Gemini 3.1 Pro in IDE right now  
**Objective**: Gather critical data about IDE vs OpenCode plugin

---

## IMMEDIATE CHECKS (While IDE Active)

### Check 1: IDE Settings/Dashboard
- [ ] Open Settings or Preferences
- [ ] Look for "Usage", "Quota", "Billing", or "Account" section
- [ ] Screenshot any visible quota/usage information
- [ ] Look for model list (which models are available?)
- [ ] Check for API key or API documentation reference

### Check 2: Current Usage Display
- [ ] Is there a usage counter or quota display?
- [ ] Does it show tokens/week or requests/week?
- [ ] Any rate limit information visible?
- [ ] Can you see account information (email, account name)?

### Check 3: Model Selection
- [ ] List all available models in IDE
- [ ] For each model, note context window if shown
- [ ] Is thinking budget configurable (for Opus)?
- [ ] Any performance/latency info available?

### Check 4: Test Gemini 3.1 Pro
- [ ] Send simple query, measure response time
- [ ] Send medium prompt (~5K tokens), measure latency
- [ ] Check response quality
- [ ] Look for any quota warnings after requests

### Check 5: IDE Documentation/Help
- [ ] Is there Help menu or documentation link?
- [ ] Does it mention quota, billing, or API?
- [ ] Any information about free tier limits?
- [ ] Links to external documentation?

### Check 6: IDE Advanced Settings
- [ ] Export or download options?
- [ ] API access configuration?
- [ ] Streaming mode toggle?
- [ ] Batch operation support?
- [ ] Conversation history management?

---

## COMPARISON DATA NEEDED

Once you have IDE information, compare with OpenCode plugin:

**For each:**
- [ ] Available models
- [ ] Context window per model
- [ ] Latency (measure same prompt)
- [ ] Response quality (qualitative)
- [ ] Quota visible (yes/no)
- [ ] API access (yes/no)

**Matrix template:**
```
Interface    | Gemini Pro | Latency | Context | API Access
-------------|-----------|---------|---------|------------
IDE          | ✓         | ?ms     | ?       | ?
OpenCode     | ✓         | ~851ms  | 1M      | Yes (CLI)
```

---

## CRITICAL QUESTIONS TO ANSWER

**Tier 1 (Quota & Capacity):**
1. What is your IDE quota usage? (Can you see current usage?)
2. Is there quota information anywhere in IDE?
3. Does IDE help/docs mention quota limits?
4. Any information about free tier limits in documentation?

**Tier 2 (Relationship):**
5. Does IDE have same account as your Google OAuth (used for OpenCode)?
6. If you could check, does IDE show different accounts available?

**Tier 3 (Capabilities):**
7. Does IDE have any visible API or CLI integration options?
8. Any mention of programmatic access or REST API?

---

## QUICK TESTING (Easy Verification)

### Test: Same Prompt Performance
```
Copy this prompt and test in IDE (note time):
"Design a scalable microservices architecture for 1M users"

Then test same in OpenCode:
opencode chat --model google/antigravity-gemini-3-1-pro "Design a scalable..."

Compare latency, quality, and any differences.
```

### Test: Context Handling
```
Try with a ~200K token context (large codebase):
"Analyze this [large file] for performance issues"

Check if IDE handles it or shows context limits.
```

---

## DATA TO RECORD

**Please capture/note:**
1. IDE version (if visible)
2. Available models list
3. Current usage/quota display (screenshot if possible)
4. Latency for test prompts
5. Any error messages or warnings
6. Links to help/documentation
7. Account information (if visible)

---

## EXPECTED SCENARIOS & WHAT TO LOOK FOR

**Scenario A: Shared Quota**
- IDE would show usage like "450K/500K tokens used"
- Would mention account quota
- Would be same accounts as OpenCode

**Scenario B: Separate IDE Quota**
- IDE would show different usage (like "450K/???? tokens")
- Might have very high limit (4M, 8M, or unlimited)
- Different account system potentially

**Scenario C: IDE is API-accessible**
- Settings would mention API key or endpoint
- Documentation would reference REST API or CLI
- Help would show programmatic access examples

---

## NEXT: Compare Findings with OpenCode Plugin

Once you gather IDE data, we'll:
1. Compare side-by-side features
2. Determine quota relationship (shared or separate)
3. Identify programmatic access possibilities
4. Decide on deployment strategy
5. Update foundation stack documentation

---

**Goal**: Understand if Antigravity IDE is a major capacity expansion (8M/week?) or same as OpenCode plugin.

**Timeline**: 30-60 minutes to gather this data while IDE active.

