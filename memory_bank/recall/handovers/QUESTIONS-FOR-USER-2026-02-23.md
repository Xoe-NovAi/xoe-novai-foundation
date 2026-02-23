# 🎯 Questions for User - 2026-02-23

> **Context**: Please answer these before the next session to maximize productivity.
> **Return to**: `memory_bank/recall/handovers/autonomous-session-2026-02-23.md`

---

## 🔴 URGENT - Blocking Issues

### Q1: Should I fix the test import errors NOW?

**Context**: The test files created by Cline have 2 import errors that will cause tests to fail:

| File | Line | Error | Impact |
|------|------|-------|--------|
| `test_redis_streams.py` | 6 | Imports `RedisStreamClient` | `ImportError` - class doesn't exist |
| `test_redis_streams.py` | 172 | Imports `calculate_backoff_delay` | `ImportError` - function doesn't exist |
| `test_knowledge_access.py` | 83-155 | Tests classes from wrong source file | Tests may fail |

**Fix Options**:
1. **Create missing classes/functions** - Update source code to match tests (15 min)
2. **Update test files** - Fix imports to match source code (30 min)
3. **Leave for later** - Document the issue and fix later

**Recommendation**: Option 2 (update test files to match source) - tests should match actual code, not the other way around.

**Your Choice**: [ ] Option 1, [X] Option 2  [ ] Option 3

---

### Q2: Should I create the missing test cases NOW?

**Context**: Current test coverage is ~60%, target is 80%.

**Missing Critical Tests**:
- `RedisStreamManager.initialize()` - No test
- `RedisStreamManager.retry_message()` - No test
- `RedisStreamManager.send_message()` - No test
- `RedisStreamManager.claim_pending_messages()` - No test
- `KnowledgeAccessControl.check_access()` - No test
- `KnowledgeAccessControl._validate_agent()` - No test
- `ContentSanitizer` edge cases - Missing

**Recommendation**: Fix import errors first, then add missing tests.

**Your Choice**: [X] Yes, add tests now  [ ] No, fix imports first  [ ] Skip for now

---

## 🟡 MEDIUM PRIORITY

### Q3: Should I consolidate duplicate WebSocket documentation?

**Context**: 4 files contain nearly identical `ConnectionManager` code:
- `FASTAPI-WEBSOCKET-PATTERNS-2026-02-22.md`
- `CLINE-TASKS-RESEARCH-SYNTHESIS-2026-02-23.md`
- `WEB-BASED-CHAT-INTERFACE-SOLUTIONS.md`
- `STAGING-CLEANUP-ARCH-AND-CONN-MGMT.md`

**Recommendation**: Create single `WEBSOCKET-PATTERNS-AUTHORITATIVE.md` and reference from other documents.

**Your Choice**: [X] Yes, consolidate  [ ] No, keep separate  [ ] Later

---

### Q4: Should I create the missing documentation files?

**Missing Files**:
1. `docs/01-start/USER-FAQ.md` - User FAQ
2. `docs/03-reference/TROUBLESHOOTING-GUIDE.md` - Troubleshooting
3. `expert-knowledge/security/SECURITY-CHECKLIST.md` - Security checklist
4. `docs/03-reference/QUICK-REFERENCE-CARD.md` - Quick reference

**Recommendation**: Create these files now while context is fresh.

**Your Choice**: [X] Yes, create all  [ ] Create priority files only (FAQ, Troubleshooting)  [ ] Skip for now

---

### Q5: Should I implement missing benchmark files?

**Context**: `PERFORMANCE-BENCHMARKING-2026-02-23.md` references:
- `benchmarks/BENCHMARK-DESIGN.md` ✅ (exists)
- `app/XNAi_rag_app/core/metrics.py` ❌ (missing)
- `scripts/benchmark_runner.py` ❌ (missing)

**Recommendation**: Create `metrics.py` first (used by multiple components).

**Your Choice**: [X] Yes, create all  [ ] Create metrics.py only  [ ] Skip for now

---

## 🟢 LOW PRIORITY

### Q6: Should I enable stricter security gating in CI?

**Current State**: Security scan has `continue-on-error: true`, so issues won't block PRs.

**Options**:
1. **Remove `continue-on-error`** - Security issues will block PRs
2. **Add separate `security-gate` job** - Blocks merge if issues found
3. **Keep current** - Security is informational only

**Recommendation**: Option 2 - separate gate that runs after tests pass.

**Your Choice**: [ ] Option 1  [X] Option 2  [ ] Option 3

---

### Q7: Should I refactor large classes?

**Context**: `RedisStreamManager` is 601 lines.

**Refactor Options**:
1. **Split into 3 classes** (`StreamConnection`, `MessageReader`, `DLQManager`)
2. **Extract methods to helper functions** (less invasive)
3. **Leave as-is** (works fine, just large)

**Recommendation**: Option 3 - leave as-is until there's a specific need to change it.

**Your Choice**: [X] Option 1  [ ] Option 2  [ ] Option 3

---

### Q8: What's the priority for remaining Gemini tasks?

**Remaining**:
- JOB-W2-007: User Documentation (4 tasks)
- JOB-W2-008: Edge Cases & Error Handling (4 tasks)

**Priority Options**:
1. **High** - Complete before Cline gets more work
2. **Medium** - Work on them after Cline finishes
3. **Low** - Defer to future sessions

**Recommendation**: Medium - Cline can work in parallel.

**Your Choice**: [X] High  [ ] Medium  [ ] Low

---

## 🔧 TECHNICAL DECISIONS

### Q9: Should I implement `calculate_backoff_delay` function?

**Context**: Test imports this, it's not in source. Uses simple formula:
```python
def calculate_backoff_delay(retry_count: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    return min(base_delay * (2 ** (retry_count - 1)), max_delay)
```

**Recommendation**: Yes, it's a 5-minute addition that makes the code better.

**Your Choice**: [X] Yes, implement  [ ] No, remove import from test

---

### Q10: Should I add `py.typed` for proper type checking?

**Current State**: Using `--ignore-missing-imports` hides type errors.

**Options**:
1. **Add `py.typed`** - Enables proper type checking for users of the package
2. **Switch to Pydantic models** - Adds validation
3. **Keep current approach** - Works, just less strict

**Recommendation**: Option 1 - simple and improves developer experience.

**Your Choice**: [X] Option 1  [ ] Option 2  [ ] Option 3

---

## 📋 SUMMARY

| Question | Recommendation | Your Choice |
|----------|---------------|--------------|
| Q1: Fix test imports | Option 2 (update tests) | [ ] |
| Q2: Add missing tests | Fix imports first | [ ] |
| Q3: Consolidate duplicate docs | Yes, consolidate | [ ] |
| Q4: Create missing docs | Yes, create priority files | [ ] |
| Q5: Implement benchmark files | Create metrics.py only | [ ] |
| Q6: Enable security gate | Option 2 (separate gate) | [ ] |
| Q7: Refactor large classes | Leave as-is | [ ] |
| Q8: Gemini task priority | Medium | [ ] |
| Q9: Implement backoff function | Yes, implement | [ ] |
| Q10: Add py.typed | Option 1 (add py.typed) | [ ] |

---

## 🎯 Quick Start for Next Session

If you select all "Yes" options, I will:

1. Fix test import errors (30 min)
2. Create missing priority docs (30 min)
3. Create `metrics.py` (15 min)
4. Implement `calculate_backoff_delay` (5 min)
5. Add `py.typed` (5 min)
6. Consolidate duplicate docs (30 min)

**Total Time**: ~2.5 hours

---

###### **Please mark your choices with [x] and return this file to the next session.**
