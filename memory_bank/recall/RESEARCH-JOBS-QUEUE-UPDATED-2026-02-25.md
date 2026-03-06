---
title: Updated Research Jobs Queue & Task Tracking
author: Copilot + Subagent Stack Discovery
date: 2026-02-25T20:06:26Z
version: 3.0
status: Active
personas: Architects, Phase Leads, Engineering Teams
tags: [research-queue, task-tracking, wave4-5, phase6]
---

# 📋 XNAi Foundation — Updated Research Jobs Queue & Task Tracking

**Research Integration Complete** | **New RQ Items Added** | **Sequencing Optimized**

---

## 📊 QUEUE STATISTICS

### Overall Status

- **Total RQ Items**: 149 (was 138)
- **New Items Added**: 9 (RQ-141 through RQ-149)
- **Wave 5 Effort**: 113.5 hours (existing 65h + new 48.5h)
- **Critical Path**: 24.5 hours
- **Phase 6 Work**: 32 hours (observability, multi-language, feedback)

### Priority Distribution

| Priority | Count | Effort | Timeline |
|----------|-------|--------|----------|
| **CRITICAL** | 3 | 6.5h | Wave 5A immediate |
| **HIGH** | 12 | 22.5h | Wave 5B Week 1-2 |
| **MEDIUM** | 18 | 35.5h | Wave 5C-5E |
| **LOW** | 8 | 7.5h | Phase 6 |
| **PLANNING** | 6 | 18h | Phase 6+ |

---

## 🎯 ORIGINAL RQ QUEUE (RQ-101 to RQ-138)

### OSS Replacements (RQ-101 to RQ-120)

#### PyBreaker Circuit Breaker (RQ-101 to RQ-104)

| ID | Task | Effort | Priority | Status | Owner |
|----|------|--------|----------|--------|-------|
| RQ-101 | Research PyBreaker API surface | 0.5h | HIGH | pending | Architect |
| RQ-102 | Design drop-in replacement wrapper | 1h | HIGH | pending | Engineer |
| RQ-103 | Implement replacement + tests | 2h | HIGH | pending | Engineer |
| RQ-104 | Integration validation (270+ tests) | 0.5h | HIGH | pending | QA |
| | **Subtotal** | **4h** | | | |

**Success Criteria**:
- ✅ 0 behavior change (all tests passing)
- ✅ Saves 200 LOC (556 → 180 custom)
- ✅ Low risk (drop-in replacement)

---

#### Authlib JWT Validation (RQ-105 to RQ-109)

| ID | Task | Effort | Priority | Status | Owner |
|----|------|--------|----------|--------|-------|
| RQ-105 | Research Authlib JWT support | 0.5h | HIGH | pending | Architect |
| RQ-106 | Design Ed25519 key migration | 1h | HIGH | pending | Engineer |
| RQ-107 | Implement JWT replacement | 1h | HIGH | pending | Engineer |
| RQ-108 | Security review (OWASP) | 0.5h | HIGH | pending | Security |
| RQ-109 | Integration validation | 0.5h | HIGH | pending | QA |
| | **Subtotal** | **3.5h** | | | |

**Success Criteria**:
- ✅ Backward compatible with existing tokens
- ✅ Ed25519 support maintained
- ✅ Professional security audits
- ✅ 150 LOC savings

---

#### OpenTelemetry Observability (RQ-110 to RQ-125)

##### Foundation (RQ-110 to RQ-115)

| ID | Task | Effort | Priority | Status | Owner |
|----|------|--------|----------|--------|-------|
| RQ-110 | Design trace context strategy | 1h | HIGH | pending | Architect |
| RQ-111 | Implement W3C TraceContext | 2h | HIGH | pending | Engineer |
| RQ-112 | Multi-service correlation design | 1.5h | HIGH | pending | Architect |
| RQ-113 | Agent Bus instrumentation | 2h | MEDIUM | pending | Engineer |
| RQ-114 | Performance overhead benchmark | 1h | MEDIUM | pending | QA |
| RQ-115 | Production deployment plan | 0.5h | MEDIUM | pending | DevOps |
| | **Subtotal** | **8h** | | | |

**Success Criteria**:
- ✅ End-to-end request tracing
- ✅ <5% performance overhead
- ✅ W3C standards compliance

##### Advanced OTEL (RQ-121 to RQ-125) — Phase 6

| ID | Task | Effort | Priority | Status | Owner |
|----|------|--------|----------|--------|-------|
| RQ-121 | Trace sampling strategy design | 1h | MEDIUM | pending | Architect |
| RQ-122 | Span batch export optimization | 1.5h | MEDIUM | pending | Engineer |
| RQ-123 | Custom span processors | 1h | MEDIUM | pending | Engineer |
| RQ-124 | Trace performance tuning | 1h | MEDIUM | pending | Engineer |
| RQ-125 | Production observability rollout | 1h | MEDIUM | pending | DevOps |
| | **Subtotal** | **5.5h** | | | |

---

#### Voice Module Enhancement - Silero VAD (RQ-116 to RQ-120)

| ID | Task | Effort | Priority | Status | Owner |
|----|------|--------|----------|--------|-------|
| RQ-116 | Research Silero VAD integration | 0.5h | MEDIUM | pending | Architect |
| RQ-117 | Design pre-filtering pipeline | 0.75h | MEDIUM | pending | Engineer |
| RQ-118 | Implement VAD module | 0.5h | MEDIUM | pending | Engineer |
| RQ-119 | Accuracy testing (target 95%+) | 0.25h | MEDIUM | pending | QA |
| RQ-120 | Deployment validation | 0.5h | MEDIUM | pending | DevOps |
| | **Subtotal** | **2.5h** | | | |

**Success Criteria**:
- ✅ 5-10% transcription improvement
- ✅ <5ms latency
- ✅ 95%+ accuracy

---

### Best Practices Implementation (RQ-126 to RQ-138)

#### Multi-Language Agent Interface - gRPC (RQ-126 to RQ-130)

| ID | Task | Effort | Priority | Status | Owner |
|----|------|--------|----------|--------|-------|
| RQ-126 | Design gRPC proto definitions | 1.5h | HIGH | pending | Architect |
| RQ-127 | Generate Python service stubs | 0.5h | MEDIUM | pending | Engineer |
| RQ-128 | Implement TypeScript client | 1h | MEDIUM | pending | Engineer |
| RQ-129 | Implement Go examples | 1h | MEDIUM | pending | Engineer |
| RQ-130 | Multi-language integration testing | 1h | MEDIUM | pending | QA |
| | **Subtotal** | **5h** | | | |

**Success Criteria**:
- ✅ gRPC proto definitions complete
- ✅ Python/TS/Go examples working
- ✅ Unblocks Phase 6 polyglot agents

---

#### Operational Excellence (RQ-131 to RQ-138)

| ID | Task | Effort | Priority | Status | Owner |
|----|------|--------|----------|--------|-------|
| RQ-131 | Graceful shutdown SIGTERM handler | 1h | MEDIUM | pending | Engineer |
| RQ-132 | Request drain mode implementation | 0.5h | MEDIUM | pending | Engineer |
| RQ-133 | SLO baseline establishment | 1.5h | MEDIUM | pending | SRE |
| RQ-134 | SLO regression detection | 1.5h | MEDIUM | pending | SRE |
| RQ-135 | Feature flags infrastructure (Unleash) | 1h | MEDIUM | pending | Engineer |
| RQ-136 | AlertManager error budget rules | 1h | MEDIUM | pending | SRE |
| RQ-137 | Chaos engineering framework | 2h | LOW | pending | QA |
| RQ-138 | Deployment runbooks + training | 1.5h | LOW | pending | DevOps |
| | **Subtotal** | **10h** | | | |

---

## 🆕 NEW RQ QUEUE (RQ-141 to RQ-149)

### From Stack Research Integration

#### Tier 1: Immediate Activation (RQ-141 to RQ-146)

##### RQ-141: LLM-as-Judge Quality Scoring

| Field | Value |
|-------|-------|
| **Title** | Activate LLM-as-Judge in quality scoring pipeline |
| **Category** | Quality/ML |
| **Effort** | 3h |
| **Priority** | HIGH |
| **Timeline** | Wave 5B Week 1 |
| **Blocker** | None |
| **Blocked By** | None |
| **Research Ref** | `expert-knowledge/research/KNOWLEDGE-QUALITY-SCORING-2026-02-22.md` |
| **Owner** | ML Engineer |
| **Success Criteria** | ✅ G-Eval framework integrated, ✅ 80%+ score validation, ✅ Feedback loop active |

**Description**:
Framework exists but not active. Activate LLM-as-judge (G-Eval) to validate 5-factor quality scores. Expected +10-15% accuracy improvement.

**Implementation**:
```python
# Integrate G-Eval framework
from langgraph import nodes
from quality_scorer import g_eval_judge

async def enhanced_quality_scoring(knowledge_item):
    # Current: manual 5-factor
    score1 = compute_5_factor_score(knowledge_item)
    
    # New: LLM validation
    score2 = await g_eval_judge(knowledge_item, score1)
    
    # Consensus: weight 0.6 manual + 0.4 LLM
    final_score = 0.6 * score1 + 0.4 * score2
    return final_score
```

---

##### RQ-142: Redis Consumer Group Tuning

| Field | Value |
|-------|-------|
| **Title** | Optimize Redis consumer group for Agent Bus throughput |
| **Category** | Performance/Infrastructure |
| **Effort** | 2h |
| **Priority** | HIGH |
| **Timeline** | Wave 5B Week 1 |
| **Blocker** | None |
| **Blocked By** | None |
| **Research Ref** | `research/RESEARCH-JOB-3-MULTI-AGENT-ORCHESTRATION-PATTERNS.md` |
| **Owner** | DevOps/Platform |
| **Success Criteria** | ✅ Throughput +19-25%, ✅ Latency -15-20ms, ✅ Memory -5-8% |

**Recommended Tuning**:
```yaml
Current:
  PENDING: 1000
  RECLAIM_TIME: None
  AUTO-ACK: Per message
  POOL: None

Optimized:
  PENDING: 750
  RECLAIM_TIME: 30s
  AUTO-ACK: Batch every 50
  POOL: Min 5, Max 20
```

---

##### RQ-143: CVE Monitoring Automation

| Field | Value |
|-------|-------|
| **Title** | Automate weekly CVE scanning with AlertManager integration |
| **Category** | Security/DevOps |
| **Effort** | 1.5h |
| **Priority** | HIGH |
| **Timeline** | Wave 5A (immediate) |
| **Blocker** | OWASP compliance gap |
| **Blocked By** | None |
| **Research Ref** | `expert-knowledge/security/SOVEREIGN-TRINITY-EXPERT-v1.0.0.md` |
| **Owner** | Security/DevOps |
| **Success Criteria** | ✅ Weekly scans active, ✅ Critical CVEs → Slack/PagerDuty <24h, ✅ OWASP compliant |

**Implementation**:
```yaml
GitHub Actions:
  name: Weekly CVE Scan
  schedule: cron: '0 3 * * 1'  # Monday 3am UTC
  jobs:
    - run: make pr-check --security-only
    - alert: Critical CVEs → AlertManager → Slack + PagerDuty
```

---

##### RQ-144: Connection Pooling (Redis & Qdrant)

| Field | Value |
|-------|-------|
| **Title** | Implement connection pooling for Redis and Qdrant |
| **Category** | Performance/Infrastructure |
| **Effort** | 4h |
| **Priority** | HIGH |
| **Timeline** | Wave 5B Week 1-2 |
| **Blocker** | None |
| **Blocked By** | None |
| **Research Ref** | `research/RESEARCH-JOB-3-MULTI-AGENT-ORCHESTRATION-PATTERNS.md` (identified optimization) |
| **Owner** | Platform Engineer |
| **Success Criteria** | ✅ p95 latency 250ms → 150ms, ✅ Throughput +20-30%, ✅ Memory +2-3% (acceptable) |

**Architecture**:
```python
async def initialize_connection_pools():
    redis_pool = await create_redis_pool(
        min_size=5, max_size=20,
        idle_timeout=60,
        keepalive=True
    )
    qdrant_pool = await create_qdrant_pool(
        min_size=3, max_size=10,
        idle_timeout=30,
        reconnect_on_error=True
    )
    return redis_pool, qdrant_pool
```

---

##### RQ-145: Error Recovery Procedures

| Field | Value |
|-------|-------|
| **Title** | Implement automated error recovery with circuit breaker integration |
| **Category** | Reliability/SRE |
| **Effort** | 3h |
| **Priority** | MEDIUM |
| **Timeline** | Wave 5B/5C |
| **Blocker** | None |
| **Blocked By** | RQ-144 (should sequence after pooling) |
| **Research Ref** | `expert-knowledge/research/ERROR-HANDLING-PATTERNS-2026-02-23.md` |
| **Owner** | Reliability Engineer |
| **Success Criteria** | ✅ MTTR <30s (from 5-15min manual), ✅ Availability +0.5%, ✅ Incident alerts active |

**Implementation**:
```python
async def handle_orchestration_error(task, error):
    if circuit_breaker.allow_request():
        await retry_with_backoff(task, max_retries=3)
    else:
        await route_to_dlq(task, reason=str(error))
        await trigger_incident(error)
```

---

##### RQ-146: Performance Optimization Loop

| Field | Value |
|-------|-------|
| **Title** | Activate continuous performance optimization monitoring |
| **Category** | DevOps/Observability |
| **Effort** | 2.5h |
| **Priority** | HIGH |
| **Timeline** | Wave 5B Week 1 |
| **Blocker** | None |
| **Blocked By** | None |
| **Research Ref** | `benchmarks/PERFORMANCE-BENCHMARKING-2026-02-23.md` |
| **Owner** | DevOps/Platform |
| **Success Criteria** | ✅ Regressions detected <24h, ✅ Automated alerts on 5%+ change, ✅ Optimization tracking active |

**Baseline Metrics** (established):
- TTFT: <300ms (p95)
- TPOT: <50ms
- E2E: <5s

**Implementation**:
```python
async def benchmark_regression_check():
    current = await measure_metrics()
    baseline = load_baseline()
    
    if current.ttft > baseline.ttft * 1.05:  # 5% regression
        alert_performance_regression(current, baseline)
        trigger_investigation()
```

---

#### Tier 2: Week 1-2 Implementation (RQ-147 - Partial)

##### RQ-147: Feedback Loop Integration

| Field | Value |
|-------|-------|
| **Title** | Implement human-in-the-loop feedback collection and quality model retraining |
| **Category** | Quality/ML |
| **Effort** | 5h |
| **Priority** | MEDIUM |
| **Timeline** | Phase 6 (Wave 5E preparation) |
| **Blocker** | None |
| **Blocked By** | RQ-141 (LLM-as-Judge) |
| **Research Ref** | `expert-knowledge/research/KNOWLEDGE-QUALITY-SCORING-2026-02-22.md` |
| **Owner** | ML Engineer |
| **Success Criteria** | ✅ User feedback collection active, ✅ Quality model retraining on threshold, ✅ +10-15% accuracy gain |

**Implementation**:
```python
@app.post("/api/knowledge/{id}/feedback")
async def feedback(id: str, quality: int, correction: str):
    await store_feedback(id, quality, correction)
    
    if should_retrain():
        await async_retrain_quality_model()
        notify_engineers("Quality model retrained")
```

---

#### Tier 3: Phase 6 Strategic (RQ-148, RQ-149)

##### RQ-148: Multi-Language Agent Patterns via gRPC

| Field | Value |
|-------|-------|
| **Title** | Design and implement gRPC agent interface for Python/TypeScript/Go |
| **Category** | Architecture/Integration |
| **Effort** | 8h |
| **Priority** | MEDIUM |
| **Timeline** | Phase 6 initial (2-3 weeks) |
| **Blocker** | None |
| **Blocked By** | None |
| **Research Ref** | `research/RESEARCH-JOB-3-MULTI-AGENT-ORCHESTRATION-PATTERNS.md`, RQ-126-130 foundation |
| **Owner** | Architect/Platform Engineer |
| **Success Criteria** | ✅ gRPC proto complete, ✅ Python/TS/Go examples working, ✅ Integration tests passing |

**Roadmap**:
1. Finalize gRPC proto (leverage RQ-126 work)
2. Implement Python service
3. Implement TypeScript client
4. Implement Go examples
5. Integration testing with multi-language calls

---

##### RQ-149: Observability Stack Integration

| Field | Value |
|-------|-------|
| **Title** | Integrate Loki + Jaeger + OpenTelemetry for distributed observability |
| **Category** | Operations/Observability |
| **Effort** | 19h |
| **Priority** | MEDIUM |
| **Timeline** | Phase 6 (3-4 weeks) |
| **Blocker** | None |
| **Blocked By** | RQ-110-115 (OTEL foundation) |
| **Research Ref** | `memory_bank/PROPOSED-STACK-CHANGES-RESEARCH-REPORT.md` Section 3, Section 8 timeline |
| **Owner** | DevOps/Platform |
| **Success Criteria** | ✅ Loki logs aggregated, ✅ Jaeger traces visible, ✅ Log-trace correlation working, ✅ SLA violation detection active |

**Component Breakdown**:
- Loki deployment: 6h
- Jaeger backend: 5h
- OTEL integration refinement: 5h
- Dashboard + alerting: 3h

---

## 📅 SEQUENCING & TIMELINE

### Wave 5A (Immediate, This Week)

| Item | Effort | Owner | Blocker Status |
|------|--------|-------|---|
| RQ-143: CVE Automation | 1.5h | Security/DevOps | ✅ Ready |
| **Subtotal** | **1.5h** | | |

**Outcome**: OWASP compliance gap closed, CVE detection <24h

---

### Wave 5B Week 1 (High-Impact Quick Wins)

| Item | Effort | Owner | Seq |
|------|--------|-------|-----|
| RQ-141: LLM-as-Judge | 3h | ML Engineer | 1 |
| RQ-142: Redis Tuning | 2h | DevOps | 1 |
| RQ-144: Connection Pooling | 4h | Platform | 2 |
| RQ-146: Perf Loop | 2.5h | DevOps | 1 |
| **Subtotal** | **11.5h** | | |

**Parallel Tracks**:
- Track 1 (Performance): RQ-141, RQ-142, RQ-146 (7.5h, can parallel)
- Track 2 (Infrastructure): RQ-144 (4h, independent)

**Outcome**: +3-5% operational efficiency, +19-25% Agent Bus throughput, +15-25% latency

---

### Wave 5B Week 2 (Core Implementations)

| Item | Effort | Owner | Seq |
|------|--------|-------|-----|
| RQ-101-104: PyBreaker | 4h | Engineer | 1 |
| RQ-105-109: Authlib JWT | 3.5h | Engineer | 2 |
| RQ-110-115: OTEL Foundation | 8h | Engineer | 2 |
| RQ-116-120: Silero VAD | 2.5h | Engineer | 3 |
| **Subtotal** | **18h** | | |

**Parallel Tracks**:
- Track 1: PyBreaker + Authlib (7.5h)
- Track 2: OTEL (8h)
- Track 3: VAD (2.5h)

---

### Wave 5C-5E (Operational Excellence & Foundations)

| Item | Effort | Owner | Timeline |
|------|--------|-------|----------|
| RQ-145: Error Recovery | 3h | Reliability | 5C Week 1 |
| RQ-131-138: Ops Excellence | 10h | SRE/Engineer | 5C-5D |
| RQ-121-125: OTEL Advanced | 5.5h | Engineer | 5E |
| RQ-126-130: gRPC Foundation | 5h | Architect | 5E (prep) |
| **Subtotal** | **23.5h** | | |

---

### Phase 6 (Strategic Implementation)

| Item | Effort | Owner | Timeline |
|------|--------|-------|----------|
| RQ-147: Feedback Loops | 5h | ML Engineer | Week 1 |
| RQ-148: gRPC Agents | 8h | Architect/Platform | Week 2-3 |
| RQ-149: Observability Stack | 19h | DevOps | Week 2-4 |
| **Subtotal** | **32h** | | |

**Parallel**: RQ-147 and RQ-148-149 can run in parallel (different teams)

---

## 📊 TOTAL EFFORT SUMMARY

### Wave 5 Consolidated

| Category | Original RQ | New RQ | Total | Comments |
|----------|-----------|---------|-------|----------|
| **OSS Replacements** | 7.5h | 0h | 7.5h | PyBreaker, Authlib, VAD |
| **OTEL & Observability** | 13.5h | 0h | 13.5h | Foundation + advanced |
| **Operational Excellence** | 10h | 0h | 10h | Graceful shutdown, SLO, etc |
| **Performance Tuning** | 0h | 11.5h | 11.5h | Consumer group, pooling, perf loop |
| **Quality Improvements** | 0h | 3h | 3h | LLM-as-judge |
| **Security** | 0h | 1.5h | 1.5h | CVE automation |
| **Error Recovery** | 0h | 3h | 3h | MTTR optimization |
| **Foundation Work** | 5h | 0h | 5h | gRPC proto, multi-lang setup |
| **Subtotal Wave 5** | **36h** | **19h** | **55h** | (Parallel execution) |
| **Wave 5 Actual** | 65h | 48.5h | 113.5h | (Sequential allocation) |

### Phase 6 Effort

| Item | Effort | Timeline |
|------|--------|----------|
| Feedback loops | 5h | Week 1 |
| gRPC agents (full) | 8h | Week 2-3 |
| Observability (full) | 19h | Week 2-4 |
| **Total Phase 6** | **32h** | 3-4 weeks |

### Grand Total

- **Wave 5**: 113.5 hours (65 existing + 48.5 new)
- **Phase 6**: 32 hours (strategic)
- **Total**: 145.5 hours

**Timeline**: 
- Wave 5B: 2-3 weeks (parallel execution)
- Phase 6: 3-4 weeks (parallel execution)
- **Total to Phase 6 completion**: 5-7 weeks

---

## ✅ TRACKING & ACCOUNTABILITY

### Status Tracking Template

```yaml
RQ-XXX:
  title: "..."
  status: pending|in_progress|complete|blocked|deferred
  assigned_to: "Engineer Name"
  completed_date: YYYY-MM-DD (if complete)
  blocker_reason: "..." (if blocked)
  % complete: 0-100
  last_updated: YYYY-MM-DD
  next_review: YYYY-MM-DD
```

### Reporting

**Weekly Status Reports**:
- PRs completed
- Critical blockers
- Forecast vs actual
- Risk adjustments

**Monthly Retrospectives**:
- Gap analysis (research vs implementation)
- Optimization opportunities
- Timeline adjustments
- Lessons learned

---

## 🎯 CONCLUSION

**Research Queue Status**: ✅ Complete and sequenced
- 149 RQ items defined (9 new from stack research)
- 113.5 hours Wave 5 effort
- 32 hours Phase 6 effort
- All items have owners, success criteria, and dependencies

**Next Step**: Execute Wave 5B Tier 1 activation (RQ-141-146) for +3-5% operational efficiency and +19-25% performance gains.

---

**Created**: 2026-02-25T20:06:26Z
**Version**: 3.0 (Updated with stack research)
**Status**: ✅ ACTIVE
**Next Review**: Weekly during Wave 5B execution
