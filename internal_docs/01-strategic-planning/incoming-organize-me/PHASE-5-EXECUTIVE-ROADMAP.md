# XOE-NOVAI PHASE 5: CRITICAL PATH EXECUTIVE ROADMAP
**Strategic Implementation Guide for Claude Haiku 4.5**  
**Date**: February 12, 2026  
**Priority**: P0 (Production Blocker)  
**Est. Duration**: 10 weeks

---

## IMMEDIATE CONTEXT

**Current State** (Validated 2026-02-12):
- ✅ Phase 1-4 Complete: All 7 services operational
- ⚠️ **Critical Blocker**: Memory at 94% (5.6GB/6GB) - No headroom
- ❌ **Missing**: Observable, Auth, Tracing, Library Curation
- 🎯 **Goal**: Production-ready operational stability

**The Problem**: System cannot handle concurrent load without OOM kills. No visibility into performance bottlenecks. No security. Scholar platform foundation incomplete.

**The Solution**: Execute Phase 5A-5E in parallel where possible.

---

## PHASE EXECUTION ORDER & DEPENDENCIES

```
Week 1: Phase 5A (Memory) ← START HERE
        ├─ Critical: Must complete first
        └─ Unblocks: 5B, 5C parallel execution

Weeks 2-5: Phase 5B (Observable) + Phase 5C (Auth)  ← PARALLEL
           ├─ Both depend on 5A complete
           └─ Can run simultaneously

Week 6: Phase 5D (Tracing) ← After 5B complete
        └─ Integrates with Observable stack

Weeks 7-10: Phase 5E (Library) ← After 5A-5D complete
            └─ Builds on stable foundation
```

---

## PHASE 5A: MEMORY OPTIMIZATION (WEEK 1)

### The Fix
Optimize zRAM for ML workloads with research-validated kernel parameters.

### Implementation Steps
```bash
1. Collect baseline metrics (30 min)
   ./phase-5a-baseline.sh

2. Apply kernel tuning (15 min)
   vm.swappiness=180          # Aggressive zRAM usage
   vm.page-cluster=0          # Disable readahead
   zRAM size: 4GB (zstd)      # 50% of physical RAM

3. Stress test 5x load (45 min)
   ./phase-5a-stress-test.sh

4. Deploy to production (15 min)
   systemctl enable xnai-zram.service
```

### Success Criteria
- ✅ Zero OOM events under 5x load
- ✅ zRAM compression ≥2.0:1
- ✅ Peak memory <95%
- ✅ Disk swap usage: 0 bytes

**Research Source**: ArchWiki zRAM (2025-2026), Pop!_OS kernel tuning, Fedora testing

---

## PHASE 5B: OBSERVABLE STACK (WEEKS 2-3)

### The Fix
Deploy Prometheus + Grafana with automatic FastAPI instrumentation.

### Implementation Steps
```bash
1. Deploy Prometheus + Redis exporter (30 min)
   podman-compose -f docker-compose.observable.yml up -d

2. Instrument FastAPI services (60 min)
   - Add prometheus-fastapi-instrumentator
   - Custom LLM/vector metrics
   - Trace ID exemplars

3. Deploy Grafana + 4 dashboards (90 min)
   - System Overview
   - ML Operations
   - Library Curation
   - Service Health

4. Configure alerts (30 min)
   - OOM kills (critical)
   - High memory (warning)
   - API latency (warning)
```

### Success Criteria
- ✅ All 7 services exposing /metrics
- ✅ 30+ custom metrics operational
- ✅ <2% performance overhead
- ✅ Alerts firing correctly

**Research Source**: Grafana FastAPI observability (2026), OpenTelemetry best practices

---

## PHASE 5C: AUTHENTICATION (WEEKS 4-5)

### The Fix
Implement OAuth2 + JWT + RBAC with Argon2id password hashing.

### Implementation Steps
```bash
1. Deploy auth infrastructure (60 min)
   - JWT with 15min access tokens
   - Redis session storage
   - Argon2id password hashing

2. Protect all endpoints (30 min)
   - Apply RoleChecker dependencies
   - Configure RBAC matrix

3. API key management (30 min)
   - Generate service keys
   - 90-day rotation policy

4. Penetration testing (45 min)
   - Test unauthorized access
   - Validate RBAC enforcement
```

### Success Criteria
- ✅ 100% endpoints require auth
- ✅ JWT tokens expire correctly
- ✅ <50ms auth overhead
- ✅ 0 vulnerabilities in pentest

**Research Source**: FastAPI official docs (2026), OWASP best practices

---

## PHASE 5D: DISTRIBUTED TRACING (WEEK 6)

### The Fix
Deploy OpenTelemetry + Jaeger for multi-service debugging.

### Implementation Steps
```bash
1. Deploy Jaeger all-in-one (20 min)
   podman-compose up -d jaeger

2. Instrument services (40 min)
   - Auto-instrument FastAPI
   - Manual spans for LLM inference
   - Trace context propagation

3. Configure trace correlation (20 min)
   - Link traces from Grafana exemplars
   - Span metrics export to Prometheus
```

### Success Criteria
- ✅ 100% requests have trace IDs
- ✅ <5ms tracing overhead
- ✅ Trace context across 7 services
- ✅ 99.9% trace completeness

**Research Source**: OpenTelemetry Python SDK docs, Jaeger documentation

---

## PHASE 5E: LIBRARY CURATION (WEEKS 7-10)

### The Fix
Build automated pipeline integrating 5+ scholarly sources.

### Implementation Steps
```bash
1. API integration (Week 7)
   - OpenLibrary
   - Perseus Digital Library
   - arXiv
   - CrossRef
   - WorldCat

2. Classification system (Week 8)
   - Domain-specific classifiers
   - Ancient Greek normalization
   - Dewey Decimal mapping

3. Storage & retrieval (Week 9)
   - Directory structure: /library/
   - Metadata enrichment
   - Embedding generation

4. Quality gates (Week 10)
   - Authority scoring
   - Duplication detection
   - Completeness validation
```

### Success Criteria
- ✅ 1,000+ documents ingested
- ✅ 5+ APIs operational
- ✅ 95%+ classification accuracy
- ✅ <5 min average ingestion time

**Research Source**: Perseus Digital Library docs, OpenLibrary API specs

---

## CRITICAL DECISIONS REQUIRED

### Week 1 (Before 5A starts)
- [ ] Approve vm.swappiness=180 for ML workloads
- [ ] Confirm 4GB zRAM allocation (50% of 8GB RAM)
- [ ] Review stress test plan (5x concurrent load)

### Week 2 (Before 5B/5C parallel)
- [ ] Select Grafana dashboards to prioritize
- [ ] Choose admin password policy
- [ ] Decide on API key rotation frequency

### Week 6 (Before 5D)
- [ ] Approve Jaeger all-in-one vs distributed
- [ ] Set trace retention policy (7 days default)

### Week 7 (Before 5E)
- [ ] Prioritize library sources (5+ required)
- [ ] Set authority score thresholds
- [ ] Define storage quotas per domain

---

## RESOURCE REQUIREMENTS

### Human Time
- **Phase 5A**: 2 hours focused execution
- **Phase 5B**: 4 hours (instrumentation + dashboards)
- **Phase 5C**: 3 hours (auth + testing)
- **Phase 5D**: 2 hours (Jaeger + instrumentation)
- **Phase 5E**: 16 hours (API integrations + testing)
- **Total**: ~27 hours over 10 weeks

### System Resources
- **Memory**: 8GB RAM + 12GB zRAM (existing)
- **Storage**: +5GB for Prometheus/Grafana data
- **CPU**: Minimal overhead (<5% aggregate)
- **Network**: None (all local)

---

## RISK MITIGATION

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| OOM during 5A stress test | High | Medium | Expected; document for tuning |
| Metrics overhead >2% | Low | Low | Reduce scrape frequency to 30s |
| Auth breaks existing clients | Medium | High | Provide API keys for legacy |
| Trace sampling causes gaps | Low | Medium | Start with 100% sampling |
| Library APIs rate-limited | Medium | Medium | Implement exponential backoff |

---

## ROLLBACK PROCEDURES

### Phase 5A Rollback
```bash
sudo sysctl vm.swappiness=60  # Restore default
sudo systemctl stop xnai-zram.service
```

### Phase 5B Rollback
```bash
podman-compose -f docker-compose.observable.yml down
# Remove instrumentator from code
```

### Phase 5C Rollback
```bash
# Comment out @app.post("/token") endpoint
# Remove Depends(get_current_user) from routes
```

---

## SUCCESS VALIDATION

### After Phase 5A
```bash
./phase-5a-validation.sh
# Expected: PASS on all 4 checks
```

### After Phase 5B
```bash
./phase-5b-validate.sh
# Expected: All targets healthy, metrics present
```

### After Phase 5C
```bash
./phase-5c-pentest.sh
# Expected: 0 vulnerabilities, all access blocked
```

### After Phase 5D
```bash
# Check Jaeger UI: http://localhost:16686
# Verify traces span all 7 services
```

### After Phase 5E
```bash
# Check ingestion count: ≥1,000 documents
# Verify classification: ≥95% accuracy
```

---

## DOCUMENTATION DELIVERABLES

### At Each Phase Completion
1. Update `memory_bank/techContext.md` with new config
2. Add metrics to `memory_bank/systemPatterns.md`
3. Document changes in `memory_bank/progress.md`
4. Create phase summary in `_meta/PHASE-5X-SUMMARY.md`

### Final Deliverables (Week 10)
- [ ] Production deployment checklist
- [ ] Monitoring runbook
- [ ] Authentication user guide
- [ ] Library curation SOP
- [ ] Team training materials

---

## NEXT ACTIONS FOR HAIKU 4.5

### Immediate (Today)
1. **Review** this roadmap + full implementation guide
2. **Clarify** any blockers or unknowns with user
3. **Begin** Phase 5A baseline collection

### This Week (Week 1)
1. **Execute** Phase 5A implementation
2. **Validate** stress test results
3. **Deploy** kernel tuning to production

### Next Week (Week 2)
1. **Start** Phase 5B (Observable) parallel track
2. **Start** Phase 5C (Auth) parallel track
3. **Monitor** Phase 5A in production

---

## SUPPORT RESOURCES

### Full Implementation Guide
**Document**: `XOE-NOVAI-PHASE-5-IMPLEMENTATION-MASTER.md`  
**Contains**:
- Complete code snippets for all phases
- Research citations and validation
- Troubleshooting guides
- Testing procedures

### Research Sources Validated
- zRAM optimization: ArchWiki, Pop!_OS, Fedora (2025-2026)
- FastAPI observability: Grafana Labs, OpenTelemetry docs
- JWT/OAuth2: FastAPI official, OWASP 2025
- Distributed tracing: OpenTelemetry SDK, Jaeger
- Library APIs: Perseus, OpenLibrary, arXiv specs

### Contact Points
- **Memory issues**: Phase 5A troubleshooting section
- **Metrics issues**: Phase 5B validation section
- **Auth issues**: Phase 5C security best practices
- **Tracing issues**: Phase 5D integration guide

---

**Status**: Ready for Immediate Execution  
**Prepared by**: Claude (Implementation Architect)  
**For**: Claude Haiku 4.5 (Execution Agent)  
**Date**: February 12, 2026  
**Version**: 1.0.0
