# Project P-010 Phase A: Codebase Audit Findings

> **Auditor**: GLM-5 (OpenCode)
> **Date**: 2026-02-20
> **Scope**: app/, scripts/

---

## Critical Findings Summary

| Severity | Category | Count | Status |
|----------|----------|-------|--------|
| 🔴 HIGH | Torch Import Violation | 1 | BLOCKING |
| 🟠 HIGH | AsyncIO Violations | 41 | NEEDS FIX |
| 🟡 MEDIUM | Generic Exception Handlers | 413 | NEEDS REVIEW |
| 🟢 LOW | Hardcoded Secrets | 0* | PASS |

*Note: 36 matches for `password`/`token`/`api_key` patterns found, but all use environment variables - this is correct practice.

---

## 🔴 CRITICAL: Torch-Free Violation

**Location**: `app/XNAi_rag_app/core/health/health_monitoring.py:227`

```python
import torch
```

**Issue**: Direct violation of the "Torch-Free Mandate" (AGENTS.md constraint).

**Fix Required**: 
- If used for GPU memory monitoring, replace with `pynvml` or `psutil`
- If used for tensor operations, replace with ONNX/NumPy

---

## 🟠 HIGH: AsyncIO Pattern Violations (41 instances)

### Pattern 1: `asyncio.run()` - Should use `anyio.run()`

| File | Line | Fix |
|------|------|-----|
| `api/semantic_search_agent_bus.py` | 335 | `anyio.run(main)` |
| `ui/chainlit_app_voice.py` | 848 | `anyio.run(setup_voice_interface)` |
| `ui/chainlit_curator_interface.py` | 297 | `anyio.run(...)` |
| `workers/crawl.py` | 1203 | `anyio.run(main_async)` |
| `health/health_monitoring.py` | 567 | `anyio.run(...)` |
| `health/health_checker.py` | 517 | `anyio.run(example_usage)` |
| `health/recovery_manager.py` | 539 | `anyio.run(example_usage)` |
| `iam_service.py` | 776 | `anyio.run(demo)` |
| `circuit_breakers/graceful_degradation.py` | 404 | `anyio.run(example_usage)` |
| `services_init.py` | 129 | Use TaskGroup for background tasks |

### Pattern 2: `asyncio.create_task()` - Should use TaskGroups

| File | Line | Issue |
|------|------|-------|
| `services_init.py` | 129 | Background task creation without TaskGroup |
| `health/health_monitoring.py` | 125, 129 | Two tasks created without TaskGroup |
| `health/health_checker.py` | 273 | Monitor task without TaskGroup |
| `degradation.py` | 48 | Monitor task without TaskGroup |
| `circuit_breakers/redis_state.py` | 105 | Health check task without TaskGroup |

### Pattern 3: `asyncio.gather()` - Should use TaskGroups

| File | Line | Context |
|------|------|---------|
| `tests/test_integration.py` | 397 | Test file - acceptable but migrate |
| `tests/validate_phase1.py` | 376 | Test file - acceptable but migrate |
| `tests/test_circuit_breakers.py` | 537 | Test file - acceptable but migrate |
| `scripts/vikunja_importer.py` | 147 | Script - should use TaskGroup |

---

## 🟡 MEDIUM: Generic Exception Handlers (413 instances)

**Top files needing attention**:

| File | Count | Priority |
|------|-------|----------|
| `services/voice/voice_interface.py` | 34 | HIGH - Voice processing core |
| `core/sovereign_mc_agent.py` | 15 | HIGH - Agent core |
| `conversation_ingestion.py` | 6 | MEDIUM |
| `tests/validate_phase1.py` | 13 | LOW - Test file |

**Recommendation**: Replace bare `except Exception:` with specific exception types or XNAiException hierarchy.

---

## Scripts AsyncIO Issues (9 instances)

| Script | Line | Issue |
|--------|------|-------|
| `phase5_vector_indexing.py` | 358 | `asyncio.run(main())` |
| `retry_failed_services.py` | 194 | `asyncio.run(main())` |
| `execute_autonomous_phase4.py` | 264 | `asyncio.run(main())` |
| `execute_autonomous_phase3.py` | 282 | `asyncio.run(main())` |
| `execute_autonomous_phase2.py` | 341 | `asyncio.run(main())` |
| `execute_phase2.py` | 114 | `asyncio.run(main())` |
| `curate.py` | 90 | `asyncio.run(main())` |
| `vikunja_importer.py` | 147, 308 | `asyncio.gather` + `asyncio.run` |

---

## Immediate Blockers for Tier 2

1. **P-010-B-001**: Remove `import torch` from `health_monitoring.py` 🔴
2. **P-010-B-002**: Migrate `asyncio.run()` → `anyio.run()` in production code
3. **P-010-B-003**: Create shutdown handlers for background tasks

---

## Execution Priority

1. **NOW**: Fix torch violation (5 min)
2. **Phase B**: Migrate entry points to AnyIO (2-4 hours)
3. **Phase C**: Exception handler audit (ongoing)

---

**Audit Complete. Ready for Phase B (Planning).**
