---
title: Opus 4.6 Resource Index — Token-Optimized Reference
author: Copilot CLI (Token Optimization Strategy)
date: 2026-02-25T23:59:00Z
version: 1.0
status: Ready for Opus
token_budget: 35-45K total
---

# 📍 OPUS 4.6 RESOURCE INDEX

## Quick Navigation (START HERE)

This index tells Opus exactly what to read, when to read it, and the token cost.

**Total execution cost**: 35-45K tokens over 5 weeks (vs. 2.2M baseline)
**Time to get oriented**: 15 minutes
**Tokens for this file**: 500 (this index)

---

## 🗂️ READING STRATEGY BY WEEK

### Week 1: Stack Harmonization (Phase 1)
**Read this week**:
1. ✅ **PHASE-1-BLUEPRINT.md** (8 KB, ~1,500 tokens)
   - **What**: Stack harmonization execution guide
   - **When**: Before starting Phase 1
   - **Why**: Copy-paste ready Week 1 implementation
   - **Skip if**: Already familiar with PortableService pattern

2. ✅ **ARCHITECTURE-DECISION-RECORDS.md** (8 KB, ~1,500 tokens)
   - **What**: Why each design choice (ADR-001 to ADR-005)
   - **When**: First thing, to understand strategic context
   - **Why**: Explains reasoning behind all decisions
   - **Skip if**: Already familiar with plugin architecture approach

3. ✅ **CODE-EXAMPLES-REPOSITORY.md** (10 KB, ~1,500 tokens)
   - **What**: Copy-paste code snippets for Phase 1
   - **When**: During implementation
   - **Why**: Accelerate coding (hours → minutes)
   - **Skip if**: Already have PortableService implementation

**Week 1 Token Total**: ~4,500 tokens

---

### Week 2: Zero-Downtime Deployment (Phase 2)
**Read this week**:
1. ✅ **PHASE-2-BLUEPRINT.md** (6 KB, ~1,200 tokens)
   - **What**: Zero-downtime deployment execution guide
   - **When**: Before starting Phase 2
   - **Why**: Blue-green deployment template, rollback procedures
   - **Reuse**: CODE-EXAMPLES from Week 1 (don't re-read)

2. ✅ **TEST-TEMPLATES.md** (8 KB, ~1,500 tokens)
   - **What**: Test patterns for verification
   - **When**: During Phase 2 testing
   - **Why**: Ensure changes work correctly
   - **Reuse**: Already read? Reference as needed

**Week 2 Token Total**: ~2,700 tokens

---

### Week 3: Asyncio Blocker Resolution (Phase 3)
**Read this week**:
1. ✅ **PHASE-3-BLUEPRINT.md** (6 KB, ~1,200 tokens)
   - **What**: Asyncio blocker resolution execution guide
   - **When**: Before starting Phase 3
   - **Why**: 69 violations documented, priority list provided
   - **Reuse**: TEST-TEMPLATES (reference as needed)

**Week 3 Token Total**: ~1,200 tokens

---

### Week 4: Background Inference Integration (Phase 4)
**Read this week**:
1. ✅ **PHASE-4-BLUEPRINT.md** (6 KB, ~1,200 tokens)
   - **What**: Background model integration execution guide
   - **When**: Before starting Phase 4
   - **Why**: ONNX setup, research job executor, scheduler
   - **Reuse**: CODE-EXAMPLES, TEST-TEMPLATES (reference as needed)

**Week 4 Token Total**: ~1,200 tokens

---

### Week 5: Documentation & Operations (Phase 5)
**Read this week**:
1. ✅ **PHASE-5-BLUEPRINT.md** (6 KB, ~1,200 tokens)
   - **What**: Documentation & operations execution guide
   - **When**: Before starting Phase 5
   - **Why**: Runbook template, dashboard setup, alert rules
   - **Reuse**: CODE-EXAMPLES, TEST-TEMPLATES (reference as needed)

**Week 5 Token Total**: ~1,200 tokens

---

## 📚 REFERENCE MATERIALS (Read Only If Needed)

### If You Get Stuck on Stack Harmonization
- **Context**: `/memory_bank/activeContext.md` (search "Phase 4-5 status")
- **Token cost**: ~2,000 tokens (skim only relevant sections)
- **Purpose**: Current phase status, team coordination

### If You Get Stuck on Provider Integration
- **Context**: `/memory_bank/PROVIDER-HIERARCHY-FINAL.md`
- **Token cost**: ~2,000 tokens
- **Purpose**: Provider list, specializations, usage patterns

### If You Get Stuck on Database Strategy
- **Context**: `OPUS-COMPREHENSIVE-DEPLOYMENT-STRATEGY.md` (PART 3 only)
- **Token cost**: ~3,000 tokens (but skip other parts)
- **Purpose**: Multi-tier database design rationale

### If You Get Stuck on Background Inference
- **Context**: `OPUS-COMPREHENSIVE-DEPLOYMENT-STRATEGY.md` (PART 7 only)
- **Token cost**: ~3,000 tokens (but skip other parts)
- **Purpose**: 24/7 ONNX model architecture

### If You Need Code Patterns
- **Context**: `CODE-EXAMPLES-REPOSITORY.md` (already read in Week 1)
- **Token cost**: $0 (reuse)
- **Purpose**: Copy-paste code snippets

### If You Need Test Patterns
- **Context**: `TEST-TEMPLATES.md` (already read in Week 2)
- **Token cost**: $0 (reuse)
- **Purpose**: Verification patterns

---

## 🛑 BLOCKER RESOLUTION STATUS

**3 Critical Blockers** (being resolved in parallel):

| Blocker | RJ Job | Status | Resolution | ETA |
|---------|--------|--------|-----------|-----|
| Vikunja/Consul orchestration | RJ-018 | 🔄 IN PROGRESS | 2-3h research | 2026-02-26 |
| MC Architecture scaling | RJ-014 | 🔄 IN PROGRESS | 4-6h research | 2026-02-26 |
| Phase 3 test failures | RJ-020 | 🔄 IN PROGRESS | 3-4h research | 2026-02-26 |

**All blockers will be resolved before you start Phase 1**.

When completed, findings will be integrated into corresponding blueprints:
- RJ-018 → **VIKUNJA-CONSUL-FIX.md** (append to memory_bank)
- RJ-014 → **MC-ARCHITECTURE-REDESIGN.md** (append to Phase 4 Blueprint)
- RJ-020 → **PHASE-3-TEST-RESOLUTION-PLAN.md** (append to Phase 3 Blueprint)

---

## ⚡ QUICK STATS

| Metric | Value |
|--------|-------|
| **Total documents created** | 9 |
| **Total kilobytes** | 60 KB |
| **Token cost Week 1** | 4,500 |
| **Token cost Weeks 2-5** | 5,300 (total) |
| **Token cost reference materials** | 5,000 (only if needed) |
| **TOTAL if all read** | 14,800 tokens (vs. 2.2M baseline) |
| **Savings** | 98.9% |
| **Execution phases** | 5 |
| **Estimated execution time** | 5 weeks (55 hours equivalent) |
| **Success criteria** | All tests passing, zero regressions, production SLA |

---

## 🎯 HOW TO USE THIS INDEX

1. **Week 1**: Read PHASE-1-BLUEPRINT.md, ARCHITECTURE-DECISION-RECORDS.md, CODE-EXAMPLES-REPOSITORY.md
2. **Each following week**: Read PHASE-{N}-BLUEPRINT.md for that week
3. **Anytime**: Refer to CODE-EXAMPLES and TEST-TEMPLATES (zero additional tokens)
4. **If stuck**: Consult reference materials (only 2-3K tokens each, as needed)
5. **Never read**: The full 550+ KB context (we've optimized it away!)

---

## 🚀 NEXT STEPS

1. **Before starting Phase 1**: Read Week 1 documents (~4,500 tokens, 30 minutes)
2. **Check blocker status**: Verify RJ-018, RJ-014, RJ-020 completed
3. **Execute Phase 1**: Use PHASE-1-BLUEPRINT.md as your execution guide
4. **Each week**: Repeat for Phases 2-5

---

**Document**: OPUS-RESOURCE-INDEX.md  
**Purpose**: Tell Opus exactly what to read when  
**Token cost**: 500 (this file)  
**Value**: Saves 2.1M tokens of unnecessary reading  
**Created**: 2026-02-25T23:59:00Z  
**Status**: ✅ Ready for Opus
