# Phase 4.2.3 Implementation Quick Reference

## Current Status: 🟡 75% Ready (Foundation Complete, Adaptation Logic Missing)

---

## What's Working Now ✅

- **DegradationTierManager**: Monitors memory/CPU, broadcasts tier changes
- **ConsulClient**: Service registration with httpx (async)
- **ServiceOrchestrator**: Auto-registers on startup, lifecycle integration
- **Observability**: Redis Streams audit trail with tier tracking
- **Circuit Breaker Framework**: Degradation patterns foundation

---

## What's Missing ❌ (8 Tasks, 6-8 hours)

### Critical Path (3-4 hours)
1. **Tier Config Factory** - Centralize tier-specific limits
2. **RAG Context Adaptation** - Reduce context window by tier
3. **Whisper Model Switching** - Dynamic STT model selection
4. **Token Budget Management** - Reduce LLM output by tier

### High Value (2-2.5 hours)
5. **Embedding Cache** - Skip vectorstore on Tier 3-4
6. **Tier Change Listener** - Notify services of tier transitions
7. **Health Endpoint** - Report degradation status

### Testing (1.5 hours)
8. **Integration Tests** - Validate all tier transitions

---

## Implementation Priority

```
IMMEDIATE:
├─ Task 4.2.3.1: tier_config.py (factory)
├─ Task 4.2.3.2: query.py + rag_service.py (context adaptation)
├─ Task 4.2.3.3: voice_interface.py (whisper switching)
└─ Task 4.2.3.4: query.py (token budgets)

FOLLOW-UP:
├─ Task 4.2.3.5: embedding_cache.py
├─ Task 4.2.3.6: tier_change_listener.py
├─ Task 4.2.3.7: health.py
└─ Task 4.2.3.8: test_tiered_degradation.py
```

---

## Key Injection Points

| Component | File | Lines | Current Behavior | Tier-Aware Behavior |
|-----------|------|-------|------------------|-------------------|
| RAG Context | query.py | 50-54 | Full size always | T1:2048, T2:1200, T3:500, T4:0 |
| Whisper Model | voice_interface.py | 281 | distil-large | T1:distil, T2:base, T3:tiny, T4:pyttsx3 |
| LLM Tokens | query.py | 63 | User-specified | T1:256, T2:150, T3:100, T4:cached |
| Vector Search | rag_service.py | 44 | top_k=5 | T1:5, T2:3, T3:1, T4:0 |
| Embedding Cache | (missing) | N/A | No cache | T1-2: fresh, T3: 5min TTL, T4: cache-only |

---

## Go/No-Go Decision

```
🟢 GO:  Phase 4.2.1 (Consul) & 4.2.2 (Service Registration)
       Deploy immediately - all infrastructure ready

🟡 CONDITIONAL GO: Phase 4.2.3 (Tiered Degradation)
   • Can START monitoring now (infrastructure ready)
   • MUST implement tasks 1-4 before production
   • SHOULD test in staging with load (verify OOM prevention)
   • REQUIRES all 8 tasks before claiming SLA compliance
```

---

## Success Criteria Status

| Criteria | Status | Notes |
|----------|--------|-------|
| Auto-recovery 30s | ✅ READY | Monitor polls 5s, Redis streams immediate |
| Audit trail | ✅ PARTIAL | xnai_queries logs initiated/completed + tier |
| Zero OOMs | �� DEPENDS | Requires tasks 1-5 for adaptive resource limits |

---

## Files to Create

```
app/XNAi_rag_app/core/tier_config.py          (NEW)
app/XNAi_rag_app/core/embedding_cache.py      (NEW)
app/XNAi_rag_app/core/tier_change_listener.py (NEW)
tests/integration/test_tiered_degradation.py  (NEW)
```

## Files to Modify

```
app/XNAi_rag_app/api/routers/query.py         (adapt context + tokens)
app/XNAi_rag_app/services/rag/rag_service.py  (accept tier config)
app/XNAi_rag_app/services/voice/voice_interface.py (select model)
app/XNAi_rag_app/api/routers/health.py        (report tier)
```

---

## Timeline Estimate

- **Critical Path (Tasks 1-4)**: 3-4 hours
- **High Value (Tasks 5-7)**: 2-2.5 hours
- **Testing (Task 8)**: 1.5 hours
- **Total**: 6-8 hours (can be parallel)

---

## Deployment Sequence

1. ✅ Deploy 4.2.1 + 4.2.2 immediately
2. 🔧 Implement tasks 1-4 in parallel (1-2 day sprint)
3. 🧪 Test in staging with load
4. 🟢 Deploy to production with all 8 tasks complete

---

## Full Audit Report

See: `phase_4_readiness_audit.json` (19KB, 384 lines)

Contains:
- Detailed gap analysis with specific line numbers
- File-by-file implementation guidance
- Pseudo-code for critical components
- Integration test cases
- Risk assessment matrix

