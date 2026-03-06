---
title: PHASE 2 Blueprint — Zero-Downtime Deployments (Week 2)
author: Copilot CLI (Token Optimization)
date: 2026-02-25T23:59:00Z
phase: 2
week: 2
effort: 8.5 hours
token_cost: 1200
---

# 📋 PHASE 2 BLUEPRINT: Zero-Downtime Deployments

## ⚡ Quick Summary

**What**: Deploy Phase 1 changes to production with zero downtime  
**When**: Week 2  
**Why**: Enable continuous delivery without service interruptions  
**Effort**: 8.5 hours (1-2 deployment cycles)  
**Success**: Instant switchover <30s, automatic rollback on failure, 99.95% uptime  

---

## ✅ EXECUTION CHECKLIST

### Task 1: Setup Blue-Green Infrastructure (2-2.5h)
- [ ] Create two identical environments: BLUE (current), GREEN (new)
- [ ] Copy all services from BLUE to GREEN environment
- [ ] Verify all GREEN services are healthy
- [ ] Setup load balancer to route 100% to BLUE initially
- [ ] Test: Load balancer can switch to GREEN instantly

### Task 2: Deploy Phase 1 Changes to GREEN (2-2.5h)
- [ ] Deploy PortableService updates to GREEN services
- [ ] Deploy unified error handling to GREEN services
- [ ] Deploy unified logging to GREEN services
- [ ] Deploy service registry to GREEN services
- [ ] Run harmony tests in GREEN environment
- [ ] Verify: All GREEN services pass 100% of tests

### Task 3: Smoke Testing GREEN (1-1.5h)
- [ ] Test primary flows: voice module, multi-provider dispatch, knowledge queries
- [ ] Test degradation scenarios: Redis down, Qdrant down, provider down
- [ ] Test circuit breakers: verify they trip and recover correctly
- [ ] Load test: 5x normal load on GREEN (target: no errors, <500ms latency)
- [ ] Verify: All metrics within SLA (uptime, latency, error rate)

### Task 4: Switch to GREEN (0.5h)
- [ ] Pre-switch validation: final health checks on BLUE and GREEN
- [ ] Switch load balancer: 0% BLUE → 100% GREEN (instant, <1s)
- [ ] Monitor: Verify traffic now flows through GREEN
- [ ] Verify: Service metrics stable, no errors, latency normal
- [ ] Timeline: Switch to GREEN execution <5 minutes total

### Task 5: Monitor GREEN for 30 Minutes (1-1.5h)
- [ ] Watch metrics: uptime, latency, error rate, throughput
- [ ] Watch logs: no unexpected errors, all JSON formatted
- [ ] Watch health: all service health checks passing
- [ ] Watch users: no reported issues
- [ ] Criteria: If all green, consider deployment successful

### Task 6: Rollback Plan (1-1.5h)
- [ ] If issues detected on GREEN:
    - [ ] Switch load balancer: 100% GREEN → 100% BLUE (instant, <1s)
    - [ ] Investigate: Review logs, metrics, errors on GREEN
    - [ ] Fix: Implement hotfix, test in GREEN
    - [ ] Retry: Switch to GREEN again (repeat Task 4)
- [ ] If critical issues: Keep BLUE running, debug GREEN in parallel
- [ ] Ensure: Rollback can execute in <30s

### Task 7: Promote BLUE → GREEN (1-1.5h)
- [ ] After 1 hour successful operation on GREEN:
    - [ ] Copy BLUE configuration to become new GREEN
    - [ ] BLUE remains as new BLUE (for next deployment)
    - [ ] Update DNS/load balancer state files
- [ ] Verify: Both BLUE and GREEN are ready for next deployment

---

## 🎯 SUCCESS CRITERIA

- ✅ Deployment completes in <30 seconds
- ✅ Zero downtime (all requests completed successfully during switch)
- ✅ All tests pass on GREEN environment before switch
- ✅ Rollback can execute in <30 seconds if needed
- ✅ 99.95% uptime SLA maintained during deployment
- ✅ No data loss during switch
- ✅ Graceful degradation working post-switch

---

## 🚨 COMMON PITFALLS

### Pitfall 1: Load Balancer Sticky Sessions
- **Problem**: Some requests stuck to BLUE, never reach GREEN
- **Solution**: Use connection draining before switch
- **Check**: Monitor request distribution: should be 0/100 (BLUE/GREEN)

### Pitfall 2: Database Migrations Not Applied
- **Problem**: GREEN services can't talk to database because schema outdated
- **Solution**: Run migrations on shared database BEFORE switching
- **Check**: Verify schema version matches code version on GREEN

### Pitfall 3: Environment Variables Mismatched
- **Problem**: GREEN services have old config files
- **Solution**: Ensure all env vars copied to GREEN
- **Check**: Compare env: `diff <(sort .env.blue) <(sort .env.green)`

### Pitfall 4: Deployment Too Fast to Monitor
- **Problem**: Issues appear after switch, but too fast to detect
- **Solution**: Keep GREEN "warmup" period, monitor before switch
- **Check**: Watch metrics for 5 minutes pre-switch

### Pitfall 5: Rollback Instructions Lost
- **Problem**: Can't remember how to rollback, panic sets in
- **Solution**: Automated rollback script in `/scripts/rollback.sh`
- **Check**: Run `./scripts/rollback.sh --dry-run` to test

---

## 📞 CRITICAL NOTES

**From RJ-020 (Phase 3 Test Blocker Resolution)**:
- *When available, append Phase 3 test fix findings here*
- *These may impact Phase 2 smoke testing requirements*
- *Current status: Pending completion*
- *ETA: 2026-02-26 EOD*

---

## 🔗 REFERENCE

- **Blue-green pattern**: See CODE-EXAMPLES-REPOSITORY.md (Deployment Pattern section)
- **Test patterns**: See TEST-TEMPLATES.md (Integration Test section)
- **Monitoring**: See ARCHITECTURE-DECISION-RECORDS.md (ADR-003 Multi-tier DB)
- **Previous depl**: `docs/deployments/phase1-deployment-report.md`

---

**Effort**: 8.5 hours  
**Week**: 2  
**Token cost**: 1,200 tokens (this doc)  
**Success metric**: Zero-downtime deployment to production  
**Status**: ✅ Ready for execution
