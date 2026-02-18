# Priority Matrix

**Generated**: 2026-02-18T05:30:00Z  
**Framework**: Impact × Effort / Risk

---

## Phase 8 Priority Matrix

| Component | Impact | Effort | Risk | Dependencies | Score | Priority |
|-----------|--------|--------|------|--------------|-------|----------|
| **8B: Qdrant Migration** | HIGH (5) | MEDIUM (3) | LOW (2) | None | 2.5 | **1st** |
| **8A: Redis Streams** | MEDIUM (3) | MEDIUM (3) | MEDIUM (3) | Phase 5B | 1.0 | **2nd** |
| **8C: Fine-Tuning** | HIGH (5) | HIGH (5) | MEDIUM (3) | Phase 6D | 0.6 | **3rd** |

**Score Formula**: Impact / (Effort × Risk)

**Recommended Order**: 8B → 8A → 8C

---

## Current Sprint Priorities

### P0: Blockers (Immediate)
| Task | Why Blocking | Assignee | Status |
|------|--------------|----------|--------|
| Fix permissions | Redis/Qdrant can't start | User (sudo) | ⏳ Pending |
| Start services | All operations blocked | User | ⏳ Pending |

### P1: Critical (This Week)
| Task | Impact | Assignee | Status |
|------|--------|----------|--------|
| TASK-021a: MC Agent Spec | Architecture foundation | OpenCode/GLM-5 | 🟡 In Progress |
| TASK-021b: MC Agent Core | Core implementation | Cline/Opus 4.6 | ⏳ Pending |
| TASK-005: Phase 3 Test Deps | Unblock testing | Cline | ⏳ Pending |

### P2: High (Next Week)
| Task | Impact | Assignee | Status |
|------|--------|----------|--------|
| TASK-011: Phase 8B Qdrant | Vector migration | Cline | ⏳ Pending |
| TASK-009: mc-oversight files | MC outputs | OpenCode | ✅ Complete |
| TASK-006: REQ-DOC-001 | Doc audit | Gemini CLI | ⏳ Pending |

### P3: Medium (Weeks 3-4)
| Task | Impact | Assignee | Status |
|------|--------|----------|--------|
| TASK-012: Phase 8A Redis Streams | Event architecture | Cline | ⏳ Pending |
| TASK-007: REQ-DOC-002 | Multi-agent protocols | OpenCode | ⏳ Pending |
| TASK-014: GitHub Actions CI/CD | Automation | Cline | ⏳ Pending |

---

## Model Assignment Priority

| Task Type | Primary Model | Fallback | Notes |
|-----------|--------------|----------|-------|
| Complex implementation | **Cline + Opus 4.6 FREE** | OpenCode/big-pickle | **Use NOW while promo lasts** |
| Research/synthesis | OpenCode/kimi-k2.5-free | Gemini CLI | 262K context |
| Structured analysis | OpenCode/glm-5-free | OpenCode/big-pickle | Reasoning specialist |
| Validation | OpenCode/big-pickle | OpenCode/glm-5-free | Reasoning variants |
| Fast prototyping | OpenCode/minimax-m2.5-free | OpenCode/gpt-5-nano | Speed |
| Offline/sovereign | Ollama + GGUF | N/A | Air-gap capable |

---

## Dependency Graph

```
Permissions Fix (P0)
       ↓
Services Start (P0)
       ↓
┌──────────────────┬──────────────────┐
│                  │                  │
▼                  ▼                  ▼
MC Agent (P1)   Phase 8B (P2)     Research Queue (P2)
       │              │                  │
       ▼              ▼                  ▼
MC Operational   Qdrant Ready    Docs Improved
       │              │                  │
       └──────────────┴──────────────────┘
                      ↓
              Phase 8A Redis Streams (P3)
                      ↓
              Phase 8C Fine-Tuning (P3)
```

---

## Resource Constraints

| Resource | Constraint | Impact |
|----------|------------|--------|
| RAM | 6.6GB available | Limits local model size |
| Sudo | Required for permissions | Blocking service start |
| Opus 4.6 Free | Limited-time promo | High-priority tasks only |
| OpenCode Rate Limits | Shared pool | May need fallback models |

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Opus promo ends | HIGH | HIGH | Prioritize complex tasks NOW |
| Permissions recur | MEDIUM | HIGH | Document fix in scripts/ |
| Rate limits hit | MEDIUM | MEDIUM | Use Ollama fallback |
| Merge conflicts | LOW | MEDIUM | Clean git debt before Phase 8 |

---

*Matrix will be updated weekly or on priority changes*
