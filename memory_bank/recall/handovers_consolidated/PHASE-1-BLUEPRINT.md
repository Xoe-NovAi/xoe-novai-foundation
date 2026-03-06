---
title: PHASE 1 Blueprint — Stack Harmonization (Week 1)
author: Copilot CLI (Token Optimization)
date: 2026-02-25T23:59:00Z
phase: 1
week: 1
effort: 11.5 hours
token_cost: 1500
---

# 📋 PHASE 1 BLUEPRINT: Stack Harmonization

## ⚡ Quick Summary

**What**: Standardize all Foundation stack services to use plugin architecture  
**When**: Week 1  
**Why**: Enable zero-downtime deployments, graceful degradation, independent scaling  
**Effort**: 11.5 hours (distributed over week)  
**Success**: All services pass harmony tests, zero regressions, production-ready SLA  

---

## ✅ EXECUTION CHECKLIST

### Task 1: Implement PortableService Base Class (2-3h)
- [ ] Create `app/XNAi_rag_app/core/portable_service.py`
- [ ] Copy code from CODE-EXAMPLES-REPOSITORY.md (PortableService section)
- [ ] Add to all services: voice_module.py, llm_router.py, session_manager.py, etc.
- [ ] Update imports in `app/XNAi_rag_app/services/__init__.py`
- [ ] Verify: All services inherit from PortableService
- [ ] Test: Basic instantiation works for all services

### Task 2: Implement Unified Error Handling (1.5-2h)
- [ ] Create `app/XNAi_rag_app/core/exceptions.py` (XNAiException hierarchy)
- [ ] Copy code from CODE-EXAMPLES-REPOSITORY.md (XNAiException section)
- [ ] Update all service error handlers to use XNAiException
- [ ] Add logging with trace_id, span_id (JSON format)
- [ ] Test: Error scenarios produce correct exception types and logs

### Task 3: Implement Unified Logging (1-1.5h)
- [ ] Update `app/XNAi_rag_app/core/logging.py`
- [ ] Add JSON structured logging to all services
- [ ] Include: timestamp, level, service name, trace_id, message, context
- [ ] Test: Log output is valid JSON, searchable

### Task 4: Create Service Registry (1-1.5h)
- [ ] Create `app/XNAi_rag_app/core/service_registry.py`
- [ ] Auto-discover services in `app/XNAi_rag_app/services/`
- [ ] Create registry with: service name, version, health endpoint, port
- [ ] Add to startup: register all services on app startup
- [ ] Test: Registry contains all services, each with metadata

### Task 5: Implement Health Check Aggregation (1.5-2h)
- [ ] Create `app/XNAi_rag_app/services/health_aggregator.py`
- [ ] Copy code from CODE-EXAMPLES-REPOSITORY.md (health check section)
- [ ] Query all service health endpoints
- [ ] Return: overall status (green/yellow/red), per-service status
- [ ] Add endpoint: `/health` (aggregate), `/health/{service_name}` (individual)
- [ ] Test: Health checks respond <200ms, aggregate works

### Task 6: Implement Feature Flags (1-1.5h)
- [ ] Create `app/XNAi_rag_app/core/feature_flags.py`
- [ ] Copy code from CODE-EXAMPLES-REPOSITORY.md (feature flag section)
- [ ] Add flags for: FEATURE_VOICE, FEATURE_REDIS, FEATURE_QDRANT, FEATURE_LOCAL_FALLBACK
- [ ] Allow runtime toggling via environment or endpoint
- [ ] Test: Feature flags work, services degrade gracefully when disabled

### Task 7: Implement Graceful Shutdown (1-1.5h)
- [ ] Create `app/XNAi_rag_app/core/shutdown_handler.py`
- [ ] Copy code from CODE-EXAMPLES-REPOSITORY.md (graceful shutdown section)
- [ ] Add to FastAPI app: sigterm/sigint handlers
- [ ] On shutdown: finish in-flight requests, close connections, persist state
- [ ] Test: Shutdown completes in <30s, no data loss

### Task 8: Implement Graceful Degradation (2-2.5h)
- [ ] Create `app/XNAi_rag_app/core/degradation_modes.py`
- [ ] For each service tier:
    - Redis down? Use in-memory cache
    - Qdrant down? Use keyword search
    - LLM provider down? Use fallback provider
- [ ] Add circuit breaker patterns (see CODE-EXAMPLES)
- [ ] Test: Each degradation scenario works, no cascading failures

### Task 9: Run Harmony Test Suite (1-1.5h)
- [ ] Copy TEST-TEMPLATES.md "Service Harmony" test template
- [ ] Create `tests/test_phase1_service_harmony.py`
- [ ] Add tests for:
    - [ ] All services inherit PortableService
    - [ ] All services use XNAiException
    - [ ] All services implement health endpoint
    - [ ] All services support feature flags
    - [ ] Graceful shutdown completes <30s
    - [ ] Degradation modes work correctly
    - [ ] No regressions in existing tests
- [ ] Run: `pytest tests/test_phase1_service_harmony.py -v`
- [ ] Target: 100% pass rate

### Task 10: Update Documentation (1-1.5h)
- [ ] Create `docs/phase1-stack-harmonization.md`
- [ ] Document: PortableService pattern, error handling, logging, service registry
- [ ] Add: Architecture diagrams, code examples, common pitfalls
- [ ] Update: `docs/IMPLEMENTATION-GUIDE.md` with Phase 1 summary
- [ ] Test: All code examples runnable, no broken links

---

## 🎯 SUCCESS CRITERIA

- ✅ All 10+ services inherit from PortableService
- ✅ All error handlers use XNAiException (zero try/except antipatterns)
- ✅ All logs are JSON structured (searchable)
- ✅ Service registry auto-discovers all services
- ✅ Health checks aggregate <200ms
- ✅ Feature flags toggleable at runtime
- ✅ Graceful shutdown <30s
- ✅ Graceful degradation scenarios working
- ✅ 100% harmony test pass rate
- ✅ Zero regressions (all existing tests pass)
- ✅ Documentation complete (architecture diagrams, code examples)

---

## 🚨 COMMON PITFALLS

### Pitfall 1: Services Not Inheriting PortableService
- **Problem**: Some services still have custom init/shutdown logic
- **Solution**: Use consistent inheritance pattern from CODE-EXAMPLES
- **Check**: `isinstance(service, PortableService)` for all services

### Pitfall 2: Mixed Error Handling
- **Problem**: Some functions use try/except, others use XNAiException
- **Solution**: Always wrap errors in XNAiException
- **Check**: Grep for `except Exception:` and replace with XNAiException handling

### Pitfall 3: Logging Not JSON
- **Problem**: Some services still use print() or old logger format
- **Solution**: Use new JSON logger (see CODE-EXAMPLES)
- **Check**: `grep -r "print(" app/ | wc -l` should be 0

### Pitfall 4: Health Checks Too Slow
- **Problem**: Health aggregator takes >200ms because queries are serial
- **Solution**: Parallelize health checks with asyncio.gather()
- **Check**: Time `/health` endpoint: `time curl http://localhost:8000/health`

### Pitfall 5: Feature Flags Hardcoded
- **Problem**: Feature flags only readable at startup, not toggleable
- **Solution**: Add runtime endpoint to toggle flags
- **Check**: Can toggle `FEATURE_VOICE` via `POST /feature-flags/FEATURE_VOICE/toggle`

---

## 📞 CRITICAL NOTES

**From RJ-020 (Phase 3 Test Blocker Resolution)**:
- *When available, append findings here about any Phase 3 test failures that impact Phase 1*
- *Current status: Pending completion of RJ-020 research job*
- *ETA: 2026-02-26 EOD*

---

## 🔗 REFERENCE

- **Code examples**: See CODE-EXAMPLES-REPOSITORY.md
- **Test patterns**: See TEST-TEMPLATES.md (Service Harmony section)
- **Architecture**: See ARCHITECTURE-DECISION-RECORDS.md (ADR-001)
- **Existing code**: `app/XNAi_rag_app/services/health_monitoring.py` (example)

---

**Effort**: 11.5 hours  
**Week**: 1  
**Token cost**: 1,500 tokens (this doc)  
**Total Phase 1 token budget**: 4,500 (includes index + ADRs + code examples)  
**Status**: ✅ Ready for execution
