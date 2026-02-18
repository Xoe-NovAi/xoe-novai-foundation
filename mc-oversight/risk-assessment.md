# Risk Assessment

**Generated**: 2026-02-18T05:30:00Z  
**Status**: Active monitoring

---

## Top 5 Risks

### RISK-001: Opus 4.6 Free Promotion Ends
| Attribute | Value |
|-----------|-------|
| **Severity** | 🔴 HIGH |
| **Probability** | HIGH (limited-time promo) |
| **Impact** | Loss of best reasoning model for complex tasks |
| **Affected** | TASK-021b, TASK-011, TASK-012 |
| **Mitigation** | Prioritize all complex implementation tasks for Cline/Opus NOW |
| **Contingency** | Fall back to OpenCode/big-pickle (reasoning variants) |

**Action Items**:
- [ ] Assign TASK-021b (MC Agent Core) to Cline/Opus immediately
- [ ] Assign TASK-011 (Qdrant Migration) to Cline/Opus
- [ ] Assign TASK-012 (Redis Streams) to Cline/Opus

---

### RISK-002: Permission Issues Recur
| Attribute | Value |
|-----------|-------|
| **Severity** | 🟠 MEDIUM |
| **Probability** | MEDIUM |
| **Impact** | Services can't start, stack non-operational |
| **Affected** | All infrastructure |
| **Mitigation** | `scripts/fix-permissions.sh` created and documented |
| **Contingency** | Manual fix with sudo each occurrence |

**Root Cause**: Container UID (1001) vs data directory ownership (100999)

**Permanent Fix Needed**:
- Add fix-permissions.sh to Makefile as pre-start hook
- Or use named volumes instead of bind mounts

---

### RISK-003: OpenCode Rate Limit Exhaustion
| Attribute | Value |
|-----------|-------|
| **Severity** | 🟡 MEDIUM |
| **Probability** | MEDIUM |
| **Impact** | Can't use OpenCode free models during peak times |
| **Affected** | Research tasks, validation |
| **Mitigation** | Multiple fallback models available |
| **Contingency** | Switch to Ollama local models |

**Fallback Chain**:
1. OpenCode free models
2. OpenRouter free tier (31+ models)
3. Ollama local models (unlimited)

---

### RISK-004: Git Debt Merge Conflicts
| Attribute | Value |
|-----------|-------|
| **Severity** | 🟡 MEDIUM |
| **Probability** | LOW |
| **Impact** | Delayed PR merge, lost work |
| **Affected** | Phase 8 start timeline |
| **Mitigation** | Documented commit plan ready |
| **Contingency** | Careful conflict resolution |

**Current State**:
- Branch: `xnai-agent-bus/harden-infra`
- Unpushed commits: 10
- Modified files: Various

**Action Items**:
- [ ] Review all pending changes
- [ ] Batch commit by subsystem
- [ ] Push and create PR

---

### RISK-005: Documentation Staleness
| Attribute | Value |
|-----------|-------|
| **Severity** | 🟢 LOW |
| **Probability** | HIGH |
| **Impact** | Agents work from outdated context |
| **Affected** | All agent decisions |
| **Mitigation** | Memory bank update protocol defined |
| **Contingency** | Manual verification of critical docs |

**Last Update Status**:
- `memory_bank/activeContext.md`: Updated 2026-02-18
- `MASTER-PROJECT-INDEX`: Updated 2026-02-18
- `progress.md`: Updated 2026-02-18

---

## Risk Matrix

```
           │ LOW Impact │ MEDIUM Impact │ HIGH Impact
───────────┼────────────┼───────────────┼─────────────
HIGH Prob  │            │ RISK-003      │ RISK-001
MED Prob   │            │ RISK-002      │
LOW Prob   │ RISK-005   │ RISK-004      │
```

---

## Monitoring Schedule

| Risk | Review Frequency | Owner |
|------|------------------|-------|
| RISK-001 | Daily | User |
| RISK-002 | Per service start | User |
| RISK-003 | Per rate limit hit | OpenCode |
| RISK-004 | Weekly | Cline |
| RISK-005 | Weekly | OpenCode |

---

## Risk Trend

| Week | Total Risks | High Severity | Trend |
|------|-------------|---------------|-------|
| W07  | 5 | 1 | → Stable |
| W08  | 5 | 1 | → Stable |

---

*Assessment will be updated weekly or on risk occurrence*
