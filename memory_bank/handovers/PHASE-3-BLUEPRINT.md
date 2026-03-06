---
title: PHASE 3 Blueprint — Asyncio Blocker Resolution (Week 3)
author: Copilot CLI (Token Optimization)
date: 2026-02-25T23:59:00Z
phase: 3
week: 3
effort: 11 hours
token_cost: 1200
---

# 📋 PHASE 3 BLUEPRINT: Asyncio Blocker Resolution

## ⚡ Quick Summary

**What**: Fix all 69 asyncio violations documented in codebase  
**When**: Week 3  
**Why**: Enable Phase 4 background inference (24/7 ONNX model) without deadlocks  
**Effort**: 11 hours (systematic violation fixing)  
**Success**: Zero asyncio violations, background tasks run stably, <30s response times  

---

## ✅ EXECUTION CHECKLIST

### Task 1: Identify All 69 Violations (1-1.5h)
- [ ] Run violation scanner: `scripts/audit-asyncio-violations.py`
- [ ] Generate report: `violations-report-2026-02-XX.txt`
- [ ] Categorize by type:
    - [ ] CPU-bound in async context (estimated: 25-30 violations)
    - [ ] Blocking I/O in async context (estimated: 20-25 violations)
    - [ ] Proper async but missing await (estimated: 10-15 violations)
    - [ ] Mixed sync/async (estimated: 5-10 violations)
- [ ] Prioritize: Fix CPU-bound first, then blocking I/O, then others
- [ ] Verify: All 69 violations in report

### Task 2: Fix CPU-Bound Violations (3-4h)
- [ ] For each CPU-bound violation (25-30 items):
    - [ ] Move to thread pool: `executor = ThreadPoolExecutor(max_workers=4)`
    - [ ] Wrap call: `await loop.run_in_executor(executor, func, arg)`
    - [ ] Test: Verify CPU doesn't spike above 60% during operation
- [ ] Metrics: Measure latency before/after (target: no increase)
- [ ] Test: Run concurrent requests (target: no deadlocks)

### Task 3: Fix Blocking I/O Violations (3-3.5h)
- [ ] For each blocking I/O (20-25 items):
    - [ ] Replace with async version: `aiohttp` instead of `requests`, etc.
    - [ ] Add proper await keywords
    - [ ] Add error handling (see XNAiException in CODE-EXAMPLES)
- [ ] Metrics: Measure latency improvement (target: 50-70% faster)
- [ ] Test: Run concurrent I/O operations (target: no deadlocks)

### Task 4: Fix Mixed Sync/Async (2-2.5h)
- [ ] For each mixed pattern (5-10 items):
    - [ ] Ensure consistent async pattern
    - [ ] Remove sync-blocking operations
    - [ ] Add proper error propagation
- [ ] Verify: All entry points are async
- [ ] Test: Trace async path from FastAPI → completion

### Task 5: Run Async Correctness Tests (2-2.5h)
- [ ] Copy TEST-TEMPLATES.md "Async Correctness" template
- [ ] Create `tests/test_phase3_asyncio_correctness.py`
- [ ] Add tests for:
    - [ ] No deadlocks under concurrent load
    - [ ] Proper error propagation
    - [ ] Event loop not blocked (latency <100ms p99)
    - [ ] CPU not spiking (background task <30% CPU)
    - [ ] Memory not leaking (stable <500MB delta over 1h test)
- [ ] Run: `pytest tests/test_phase3_asyncio_correctness.py -v -s --timeout=300`
- [ ] Target: 100% pass rate

### Task 6: Update Documentation (1-1.5h)
- [ ] Create `docs/phase3-asyncio-fixes.md`
- [ ] Document: Each violation type, fix pattern, test results
- [ ] Add: Before/after metrics, performance improvements
- [ ] Update: `docs/IMPLEMENTATION-GUIDE.md` with Phase 3 summary

---

## 🎯 SUCCESS CRITERIA

- ✅ All 69 violations fixed (zero remaining)
- ✅ CPU-bound operations in thread pool (<60% CPU spike)
- ✅ Blocking I/O operations async (<200ms latency)
- ✅ No mixed sync/async patterns
- ✅ 100% async correctness test pass rate
- ✅ No deadlocks under 10x concurrent load
- ✅ Memory stable over 1-hour test (<500MB delta)
- ✅ Background inference can run 24/7

---

## 🚨 COMMON PITFALLS

### Pitfall 1: Thread Pool Too Small
- **Problem**: All CPU-bound operations queue up, latency increases
- **Solution**: Set `max_workers` based on CPU count (4-8 typically)
- **Check**: Monitor thread pool queue length in metrics

### Pitfall 2: Forgot to Await
- **Problem**: Async function called but not awaited, function returns immediately
- **Solution**: Grep for `await` missing: `grep -n "= .*async.*(" app/`
- **Check**: Static analysis tools (mypy with --strict)

### Pitfall 3: Event Loop Blocked by Sync Call
- **Problem**: One service still has blocking I/O, blocks all others
- **Solution**: Use `asyncio.iscoroutinefunction()` to verify
- **Check**: Monitor event loop lag: target <100ms p99

### Pitfall 4: Error Not Propagated
- **Problem**: Error in background task silently swallowed
- **Solution**: Ensure all coroutines have proper error handling
- **Check**: Review exception logs, verify all errors logged

### Pitfall 5: Deadlock on Shutdown
- **Problem**: Graceful shutdown hangs because background task waiting on lock
- **Solution**: Add timeout to all locks, properly cleanup on shutdown
- **Check**: Test shutdown: `kill -TERM <pid>` should complete <30s

---

## 📞 CRITICAL NOTES

**From RJ-020 (Phase 3 Test Blocker Resolution)**:
- *When available, append specific asyncio fixes discovered in RJ-020*
- *May include specific violations or patterns not detected by scanner*
- *Current status: Pending completion*
- *ETA: 2026-02-26 EOD*

---

## 🔗 REFERENCE

- **Asyncio patterns**: See CODE-EXAMPLES-REPOSITORY.md (Async Pattern section)
- **Test patterns**: See TEST-TEMPLATES.md (Async Correctness section)
- **Architecture**: See ARCHITECTURE-DECISION-RECORDS.md (ADR-004 Background Model)
- **Current violations**: `internal_docs/01-strategic-planning/PHASE-4.1-RESEARCH-DEEP-DIVE.md` (line 456+)

---

**Effort**: 11 hours  
**Week**: 3  
**Token cost**: 1,200 tokens (this doc)  
**Success metric**: Zero asyncio violations, stable background inference  
**Status**: ✅ Ready for execution
