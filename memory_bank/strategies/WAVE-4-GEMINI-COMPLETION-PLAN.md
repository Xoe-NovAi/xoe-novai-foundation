# WAVE 4 PHASE 1: Gemini Onboarding Continuation Plan

**Status**: BLOCKING ITEM - Needs completion THIS WAVE  
**Priority**: P0 CRITICAL  
**Estimated Time**: 3-4 hours total  
**Coordination Key**: `GEMINI-ONBOARDING-COMPLETION-WAVE-4`

---

## Executive Summary

Previous Gemini MC session (2026-02-21/02-22) created comprehensive onboarding handbook and identified critical blockers. This document tracks what needs to be resumed and completed to unblock the project.

---

## Previous Session Deliverables (COMPLETED)

✅ **GEMINI-ONBOARDING-HANDBOOK.md** (internal_docs/00-system/)
- Comprehensive PM onboarding for Gemini 3 Flash agent
- Phase 1: Foundation Consolidation - **COMPLETE**
- 15 fragmented meta files consolidated
- Clear roadmap for Phase 2 & 3

✅ **GEMINI-ONBOARDING-2026-02-21.md** (expert-knowledge/gemini-inbox/)
- CLI task specification
- Task priorities established
- Resource maps provided

✅ **AGENT-ONBOARDING-PROTOCOL-V1.md** (memory_bank/strategies/)
- Error prevention protocol
- Addresses faulty onboarding issues
- System state verification steps

---

## Phase 2: PENDING - MkDocs Internal Configuration

**What Needs to Happen**:

1. **Create mkdocs-internal.yml** (at project root)
   - Template provided in handbook
   - Configures navigation structure
   - Enables `docs/` → MkDocs transformation

2. **Test build locally**:
   ```bash
   mkdocs serve -f mkdocs-internal.yml
   ```

3. **Validate navigation**:
   - Check all internal docs appear
   - Verify no broken links
   - Confirm sidebar structure

**Estimated Time**: 1 hour

---

## Critical Blockers (MUST FIX THIS WAVE)

### 1. Test Import Errors ⛔

**File**: `tests/unit/core/test_redis_streams.py`  
**Lines**: 6, 172  
**Issue**: Missing `RedisStreamClient` class and `calculate_backoff_delay` function  
**Impact**: Test suite blocked from running  
**Fix Time**: 30 minutes

```python
# Line 6 - Import error:
from XNAi_rag_app.core.redis_streams import RedisStreamClient  # MISSING

# Line 172 - Function call:
backoff = calculate_backoff_delay(attempt=2)  # UNDEFINED

# Solution: Check if class/function exist in redis_streams.py, or implement if missing
```

### 2. Asyncio Violations ⛔

**Location**: `app/XNAi_rag_app/` (19 instances across files)  
**Requirement**: AGENTS.md mandates AnyIO for structured concurrency  
**Current**: Using `asyncio.gather()` and `asyncio.create_task()`  
**Fix Required**: Migrate to `anyio.create_task_group()`  
**Impact**: Code quality violation  
**Fix Time**: 2 hours

```python
# Wrong (asyncio):
tasks = [asyncio.create_task(func()) for func in tasks]
results = await asyncio.gather(*tasks)

# Right (anyio):
async with anyio.create_task_group() as tg:
    for func in tasks:
        tg.start_soon(func)
```

### 3. Security CI/CD Permissive ⚠️

**File**: `.github/workflows/security.yml`  
**Issue**: `continue-on-error: true` hides vulnerabilities  
**Fix**: Should fail PRs on security issues  
**Fix Time**: 15 minutes  
**Impact**: Medium (quality, not blocking)

---

## Pending Gemini Tasks (Queue)

| Task | Status | Est. Time |
|------|--------|-----------|
| Security Audit Research | 🔵 In Progress | 1 hour |
| Performance Benchmarking | 🔵 In Progress | 1 hour |
| User Documentation | ⏳ Pending | 1.5 hours |
| Edge Cases & Error Handling | ⏳ Pending | 1 hour |

---

## Recommended Execution Order (THIS SESSION)

### Step 1: Onboarding Protocol (5 min)
Read `memory_bank/strategies/AGENT-ONBOARDING-PROTOCOL-V1.md` to understand verification steps.

### Step 2: Quick Wins (1 hour total)
- [ ] Fix test import errors (30 min) — Opens test suite
- [ ] Fix security CI permissive (15 min) — Quick quality win
- [ ] Run test suite (15 min) — Validate fixes

### Step 3: Phase 2 Implementation (1 hour)
- [ ] Create mkdocs-internal.yml
- [ ] Test local build
- [ ] Validate navigation

### Step 4: Complete Gemini Tasks (2-3 hours)
- [ ] Finish Security Audit Research
- [ ] Complete Performance Benchmarking
- [ ] Create User Documentation
- [ ] Implement Edge Cases & Error Handling

### Step 5: Finalize & Document
- [ ] Run full test suite
- [ ] Update memory_bank with completion status
- [ ] Lock findings into GEMINI-ONBOARDING-HANDBOOK.md (Phase 3 notes)

---

## Files to Reference

| Document | Purpose |
|----------|---------|
| `internal_docs/00-system/GEMINI-ONBOARDING-HANDBOOK.md` | Primary reference - Phase 2 instructions |
| `expert-knowledge/gemini-inbox/GEMINI-ONBOARDING-2026-02-21.md` | Task specifications |
| `memory_bank/strategies/AGENT-ONBOARDING-PROTOCOL-V1.md` | System state verification |
| `memory_bank/BLOCKERS-AND-GAPS-2026-02-22.md` | Blocker list |
| `tests/unit/core/test_redis_streams.py` | Test file with errors |
| `app/XNAi_rag_app/` | Files with asyncio violations |

---

## Success Criteria

✅ **Phase 2 Complete**:
- [ ] mkdocs-internal.yml created
- [ ] Local build succeeds
- [ ] All internal docs discoverable

✅ **Blockers Fixed**:
- [ ] Test import errors resolved
- [ ] All asyncio violations migrated to anyio
- [ ] Security CI appropriately strict

✅ **Gemini Tasks Complete**:
- [ ] Security Audit Research finished
- [ ] Performance Benchmarking complete
- [ ] User Documentation done
- [ ] Edge Cases addressed

✅ **Validation**:
- [ ] Full test suite passes
- [ ] No CI/CD warnings
- [ ] Documentation comprehensive

---

## Integration with Wave 4

This Gemini onboarding work is **Phase 3 todo** (`P3-complete-gemini-onboarding`) in the comprehensive Wave 4 strategy. However, it should be tackled **early** because:

1. **Unblocks testing** (needed for validation phases)
2. **Improves project quality** (code standards compliance)
3. **Enables better documentation** (for all future work)

---

**Coordination Key**: `GEMINI-ONBOARDING-COMPLETION-WAVE-4`  
**Target Completion**: This session (within 4 hours)  
**Owner**: MC-Overseer (with Cline/Copilot sub-dispatch for implementation)
