---
tool: cline
model: claude-sonnet-4-6
account: arcana-novai
git_branch: xnai-agent-bus/harden-infra
session_id: sprint9-2026-02-22
version: v1.3.0
created: 2026-02-21
updated: 2026-02-22
tags: [research, queue, prioritized, multi-agent]
---

# XNAi Research Jobs Queue v1.3

> **Last Updated**: 2026-02-22 (Cline Session Update)
> **Context**: Sprint 9 In Progress (P-010-B Code Audit)
> **Related**: `memory_bank/activeContext.md`, `memory_bank/strategies/PROJECT-QUEUE.yaml`
> **Handoff**: `memory_bank/recall/handovers/cline-session-2026-02-22-chainlit.md`

## Overview

This document consolidates all pending research tasks from ADDITIONAL-RESEARCH-NEEDED.md, PROJECT-QUEUE.yaml, and strategic documents into a prioritized queue.

---

## Status Summary (Updated 2026-02-23)

| Priority | Total | Completed | In Progress | Pending |
|----------|-------|-----------|-------------|---------|
| P0-CRITICAL | 3 | 2 | 0 | 1 |
| P1-HIGH | 10 | 2 | 0 | 8 |
| P2-MEDIUM | 5 | 0 | 0 | 5 |
| P3-LOW | 1 | 0 | 0 | 1 |
| **Total** | **19** | **4** | **0** | **15** |

---

## Category 1: Infrastructure & Sovereignty (CRITICAL)

### JOB-I1: Cline Context Window Verification
**Priority**: P0-CRITICAL
**Status**: ✅ COMPLETED
**Completion Date**: 2026-02-18
**Deliverable**: `expert-knowledge/research/CLINE-CONTEXT-WINDOW-RESEARCH-2026-02-18.md`
**Findings**: Partial confirmation of shadow 400K; compaction mechanism documented

### JOB-I2: Qdrant Collection State Audit
**Priority**: P0-CRITICAL
**Status**: ✅ COMPLETED
**Completion Date**: 2026-02-23
**Assigned Model**: Copilot CLI (implementation)
**Deliverable**: `memory_bank/infrastructure/QDRANT-STATE-AUDIT.md`
**Method**:
1. ✅ Analyzed docker-compose Qdrant configuration
2. ✅ Documented collection structure (will be created on init)
3. ✅ Recorded service status and health configuration

### JOB-I3: Redis Sentinel vs Standalone Decision
**Priority**: P1-HIGH
**Status**: ✅ COMPLETED
**Completion Date**: 2026-02-23
**Assigned Model**: Copilot CLI (research & decision)
**Deliverable**: `expert-knowledge/infrastructure/REDIS-HA-DECISION.md`
**Key Finding**: ✅ **Recommend Standalone + Watchdog** for XNAi Phase 2

### JOB-I4: Torch Import Remediation (P-010-B)
**Priority**: P0-CRITICAL
**Status**: ✅ COMPLETED
**Completion Date**: 2026-02-22
**Findings**: FALSE POSITIVE - No torch imports found in health_monitoring.py
**Source**: Cline session 2026-02-22 handoff

### JOB-I5: asyncio → anyio Migration (P-010-B)
**Priority**: P1-HIGH
**Status**: ✅ COMPLETED
**Completion Date**: 2026-02-22
**Deliverable**: Migrated files (see handoff)
**Files Migrated**:
- `health_monitoring.py`
- `health_checker.py`
- `degradation.py`
- `redis_state.py`
- Test files (partial)
**Source**: Cline session 2026-02-22 handoff

---

## Category 2: Model & Provider Intelligence (HIGH)

### JOB-M1: Antigravity Complete Model List
**Priority**: P1-HIGH
**Status**: 🔵 PENDING
**Assigned Model**: Gemini CLI (research)
**Deliverable**: Updated `configs/model-router.yaml`

### JOB-M2: Gemini 3 CLI Availability Check
**Priority**: P1-HIGH
**Status**: 🔵 PENDING
**Assigned Model**: User (manual check)
**Deliverable**: `expert-knowledge/gemini-cli/GEMINI-3-AVAILABILITY.md`

### JOB-M3: fastembed + ONNX Version Compatibility
**Priority**: P1-HIGH
**Status**: 🔵 PENDING
**Assigned Model**: Sonnet (implementation)
**Deliverable**: `expert-knowledge/embeddings/FASTEMBED-ONNX-COMPAT.md`

---

## Category 3: Integration & Migration (MEDIUM)

### JOB-INT1: OpenCode to Antigravity Migration Path
**Priority**: P1-HIGH
**Status**: 🔵 PENDING
**Assigned Model**: Gemini Pro (research)
**Deliverable**: `expert-knowledge/opencode/ANTIGRAVITY-MIGRATION-GUIDE.md`

### JOB-INT2: OpenPipe Integration Feasibility
**Priority**: P2-MEDIUM
**Status**: ✅ COMPLETED
**Completion Date**: 2026-02-22
**Findings**: OpenPipe integration created, AWQ removed
**Deliverable**: `app/XNAi_rag_app/core/openpipe_integration.py`

### JOB-INT3: Vikunja MCP Layer Architecture
**Priority**: P2-MEDIUM
**Status**: 🔵 PENDING
**Assigned Model**: Sonnet (planning)
**Deliverable**: `docs/architecture/VIKUNJA-MCP-ARCHITECTURE.md`

### JOB-INT4: Chainlit Architecture Implementation
**Priority**: P1-HIGH
**Status**: 🔵 BLOCKED (awaiting JOB-C1 review)
**Assigned Model**: Sonnet (implementation)
**Deliverable**: Unified `ui/chainlit_app.py`
**Dependencies**: JOB-C1 (Chainlit Architecture Review)
**Estimated Effort**: 3.5 days
**Source**: Cline session 2026-02-22 handoff

---

## Category 4: Security & Compliance (MEDIUM)

### JOB-S1: API Rate Limiting Implementation
**Priority**: P1-HIGH
**Status**: 🔵 PENDING
**Assigned Model**: Sonnet (planning)
**Deliverable**: `docs/architecture/RATE-LIMITING-DESIGN.md`

### JOB-S2: JWT Secret Rotation Procedure
**Priority**: P1-HIGH
**Status**: 🔵 PENDING
**Assigned Model**: Sonnet (implementation)
**Deliverable**: `scripts/rotate-jwt-secrets.sh` + docs

### JOB-S3: Input Validation Bounds
**Priority**: P2-MEDIUM
**Status**: 🔵 PENDING
**Assigned Model**: Gemini Flash (discovery)
**Deliverable**: `docs/security/INPUT-VALIDATION-AUDIT.md`

---

## Category 5: Performance & Optimization (LOW)

### JOB-P1: zRAM Multi-Tier Configuration
**Priority**: P2-MEDIUM
**Status**: 🔵 PENDING
**Assigned Model**: Gemini Pro (research)
**Deliverable**: `expert-knowledge/infrastructure/ZRAM-MULTI-TIER-ANALYSIS.md`

### JOB-P2: Embedding Model Benchmark
**Priority**: P3-LOW
**Status**: 🔵 PENDING
**Assigned Model**: Gemini Flash (execution)
**Deliverable**: `benchmarks/embedding-benchmark-results.md`

### JOB-P3: Context Compaction Strategy
**Priority**: P2-MEDIUM
**Status**: 🔵 PENDING
**Assigned Model**: Opus (strategic review)
**Deliverable**: Updated `memory_bank/strategies/OPUS-TOKEN-STRATEGY.md`

---

## Category 6: Architecture & Design Review (NEW)

### JOB-C1: Chainlit Architecture Review
**Priority**: P0-CRITICAL
**Status**: 🔵 PENDING
**Assigned Model**: OpenCode GLM-5 (MC-Overseer)
**Source**: Cline session 2026-02-22
**Deliverable**: Review + approval of `internal_docs/04-research-and-development/CHAINLIT-ARCHITECTURE-PROPOSAL.md`
**Tasks**:
1. Review proposed architecture
2. Validate alignment with strategic roadmap
3. Check integration with XNAi research pipeline
4. Provide implementation guidance
**Context**: `memory_bank/recall/handovers/cline-session-2026-02-22-chainlit.md`

---

## Execution Priority Order (Updated)

### Immediate (This Session)
1. ~~**JOB-C1**: Chainlit Architecture Review (OpenCode GLM-5)~~ - ✅ DEFERRED
2. ✅ **JOB-I2**: Qdrant Collection State Audit (COMPLETED 2026-02-23)
3. ✅ **JOB-I3**: Redis Sentinel Decision (COMPLETED 2026-02-23)

### Next Priority
4. **JOB-M1**: Antigravity Complete Model List
5. **JOB-S1**: API Rate Limiting Implementation
6. **JOB-INT4**: Chainlit Implementation (awaiting JOB-C1 review)

### Future Sprints
7. All P2-MEDIUM and P3-LOW jobs

---

## Commits Since v1.2

```
9e94f1d OpenPipe integration, AWQ removal
0789f53 health_monitoring.py → AnyIO
d930dcb health_checker.py → AnyIO
c44a395 degradation.py → AnyIO
65f2abc redis_state.py → AnyIO
8dec8f9 test files → AnyIO (partial)
699b3d2 consolidate services_init.py + AnyIO migration
```

---

**Version**: 1.3.0
**Last Updated**: 2026-02-22
**Research Integration**: Complete