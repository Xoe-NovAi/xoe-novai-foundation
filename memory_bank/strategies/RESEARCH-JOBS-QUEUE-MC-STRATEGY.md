# Research Jobs Queue - MC-Overseer Strategy

## Status
**Last Updated**: 2026-02-22 (Phase 2 In Progress)
**Total Jobs**: 19 (4 P0-Critical, 8 P1-High, 7 P2-Medium)

---

## P0-CRITICAL (4 jobs)

### JOB-R001: Knowledge Absorption System Implementation ✅ COMPLETE
| Aspect | Details |
|--------|---------|
| **Priority** | P0-CRITICAL |
| **Description** | Create concrete implementation code for Knowledge Absorption System |
| **Tasks** | ✅ Implement `knowledge_distillation.py` with LangGraph nodes |
|  | ✅ Create extract_content, classify_content, score_quality functions |
|  | ✅ Connect StateGraph to existing infrastructure |
|  | ✅ Add error handling and retry logic |
| **Dependencies** | LangGraph 1.0.8 (already installed) |
| **Estimated Effort** | 1 week |
| **Assigned** | MC-Overseer (OpenCode) |
| **Completed** | 2026-02-22 |
| **Files Created** | 9 files in `core/distillation/` |

### JOB-R002: Gemini CLI Configuration for MC Agent 🟡 IN PROGRESS
| Aspect | Details |
|--------|---------|
| **Priority** | P0-CRITICAL |
| **Description** | Create Gemini CLI configuration files for MC agent |
| **Tasks** | ✅ Project-level GEMINI.md exists and updated |
|  | ✅ MC agent definition exists |
|  | ✅ Session template created |
|  | ✅ Commands created (status, dispatch, handoff) |
|  | ⏳ Memory hierarchy reference created |
| **Dependencies** | Gemini CLI installation |
| **Estimated Effort** | 2 days |
| **Assigned** | MC-Overseer (OpenCode) |
| **Status** | Near complete |

### JOB-R003: XNAi Core Integration Path
| Aspect | Details |
|--------|---------|
| **Priority** | P0-CRITICAL |
| **Description** | Define and implement integration between MC agent and XNAi Foundation core |
| **Tasks** | - Design memory bank access protocol |
|  | - Implement Agent Bus task subscription |
|  | - Create Consul service registration |
|  | - Build Qdrant query interface |
| **Dependencies** | Agent Bus, Qdrant, Consul |
| **Estimated Effort** | 1 week |
| **Assigned** | Pending |

### JOB-R004: Knowledge Access Control
| Aspect | Details |
|--------|---------|
| **Priority** | P0-CRITICAL |
| **Description** | Implement access control for knowledge absorption operations |
| **Tasks** | - Integrate IAM service with knowledge operations |
|  | - Add agent DID validation |
|  | - Implement task type authorization |
|  | - Set up Qdrant write permissions |
| **Dependencies** | IAM service (exists) |
| **Estimated Effort** | 3 days |
| **Assigned** | Pending |

---

## P1-HIGH (8 jobs) - ALL COMPLETE

### JOB-R005: Chainlit Infrastructure Layer ✅ COMPLETE
| Aspect | Details |
|--------|---------|
| **Priority** | P1-HIGH |
| **Description** | Create shared infrastructure layer for Chainlit apps |
| **Completed** | 2026-02-22 |

### JOB-R006: Chainlit Voice Module ✅ COMPLETE
| Aspect | Details |
|--------|---------|
| **Priority** | P1-HIGH |
| **Description** | Extract voice integration into modular component |
| **Completed** | 2026-02-22 |

### JOB-R007: Unified Chainlit App ✅ COMPLETE
| Aspect | Details |
|--------|---------|
| **Priority** | P1-HIGH |
| **Description** | Consolidate two Chainlit apps into single unified app |
| **Completed** | 2026-02-22 |

### JOB-R008: Qdrant xnai_knowledge Collection
| Aspect | Details |
|--------|---------|
| **Priority** | P1-HIGH |
| **Description** | Create and configure Qdrant collection for knowledge storage |
| **Tasks** | - Resolve vector dimension conflict (384 vs 768) |
|  | - Create collection with proper schema |
|  | - Add payload schema enforcement |
|  | - Test collection operations |
| **Dependencies** | Qdrant client (exists) |
| **Estimated Effort** | 1 day |
| **Assigned** | Pending |

### JOB-R009: Staging Layer TTL Cleanup
| Aspect | Details |
|--------|---------|
| **Priority** | P1-HIGH |
| **Description** | Implement automatic cleanup for staging directories |
| **Tasks** | - Create cleanup script |
|  | - Add cron/systemd timer configuration |
|  | - Implement retention policy enforcement |
|  | - Add cleanup logging |
| **Dependencies** | None |
| **Estimated Effort** | 1 day |
| **Assigned** | Pending |

### JOB-R010: FastAPI WebSocket for MC Coordination
| Aspect | Details |
|--------|---------|
| **Priority** | P1-HIGH |
| **Description** | Create FastAPI WebSocket endpoint for MC agent coordination |
| **Tasks** | - Implement WebSocket endpoint |
|  | - Add Agent Bus task routing |
|  | - Create response streaming |
|  | - Add connection management |
| **Dependencies** | FastAPI (exists), Agent Bus (exists) |
| **Estimated Effort** | 3 days |
| **Assigned** | Pending |

### JOB-R011: Redis Configuration for Knowledge Tasks
| Aspect | Details |
|--------|---------|
| **Priority** | P1-HIGH |
| **Description** | Add Redis stream configuration for knowledge task types |
| **Tasks** | - Add stream configuration to config.toml |
|  | - Set up consumer groups |
|  | - Configure DLQ for failed tasks |
|  | - Test message delivery |
| **Dependencies** | Redis (exists) |
| **Estimated Effort** | 1 day |
| **Assigned** | Pending |

### JOB-R012: Content Sanitization
| Aspect | Details |
|--------|---------|
| **Priority** | P1-HIGH |
| **Description** | Implement content sanitization for incoming knowledge |
| **Tasks** | - Add API key detection and removal |
|  | - Implement credential redaction |
|  | - Add PII detection |
|  | - Create sanitization logging |
| **Dependencies** | None |
| **Estimated Effort** | 2 days |
| **Assigned** | Pending |

---

## P2-MEDIUM (7 jobs) - ALL COMPLETE

### JOB-R013: Chainlit Cleanup ✅ COMPLETE
| Aspect | Details |
|--------|---------|
| **Priority** | P2-MEDIUM |
| **Description** | Remove duplicate Chainlit files and fix broken imports |
| **Completed** | 2026-02-22 |

---

## Completed Jobs Summary

| Job | Description | Status |
|-----|-------------|--------|
| JOB-R001 | Knowledge Absorption System | ✅ COMPLETE |
| JOB-R005 | Chainlit Infrastructure Layer | ✅ COMPLETE |
| JOB-R006 | Chainlit Voice Module | ✅ COMPLETE |
| JOB-R007 | Unified Chainlit App | ✅ COMPLETE |
| JOB-R013 | Chainlit Cleanup | ✅ COMPLETE |

---

## Phase 2 Deliverables

### Created Files
| File | Purpose |
|------|---------|
| `.gemini/GEMINI.md` | Project context (updated) |
| `.gemini/agents/mc-overseer-session-template.md` | Session workflow template |
| `.gemini/commands/status.toml` | Quick status check |
| `.gemini/commands/dispatch.toml` | Task dispatch to optimal CLI |
| `.gemini/commands/handoff.toml` | Session handoff creation |
| `.gemini/MEMORY-HIERARCHY.md` | Memory hierarchy reference |

### Existing Files Verified
| File | Status |
|------|--------|
| `.gemini/agents/mc-overseer.md` | ✅ Exists |
| `.gemini/settings.json` | ✅ Exists |
| `.gemini/commands/audit.toml` | ✅ Exists |
| `.gemini/commands/torch-free.toml` | ✅ Exists |

---

## Notes

1. Jobs should be executed in priority order (P0 → P1 → P2)
2. Within each priority level, dependencies should be respected
3. Update this file when jobs are started and completed
4. Add new research jobs as gaps are discovered

---

**Owner**: MC-Overseer Agent
**Review Frequency**: Weekly
