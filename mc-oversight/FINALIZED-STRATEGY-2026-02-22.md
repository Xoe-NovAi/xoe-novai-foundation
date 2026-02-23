# XNAi Foundation — Finalized Strategy Document

## Status: LOCKED FOR EXECUTION
**Last Updated**: 2026-02-22
**Status**: READY FOR IMPLEMENTATION
**Owner**: MC-Overseer Agent

---

## Executive Summary

This document consolidates all strategic decisions, research findings, and implementation plans for the XNAi Foundation. The strategy has been reviewed, corrected, and finalized for immediate execution.

---

## Strategic Decisions (LOCKED)

### 1. MC Agent Environment: Gemini CLI
| Decision | Rationale |
|----------|-----------|
| **Primary**: Gemini CLI | 1M context, AI compression, hierarchical memory |
| **Alternative**: OpenCode + GLM-5 | 200K context, user's current setup |
| **Future**: Local MC | When hardware permits |

### 2. Knowledge Absorption System: LangGraph Pipeline
| Component | Status |
|-----------|--------|
| Architecture | ✅ Designed |
| Quality Gates | ✅ Defined (0.6 threshold) |
| Storage Targets | ✅ Qdrant + Memory Bank + Expert-Knowledge |
| Implementation | ⏳ Pending |

### 3. UI Layer: Multi-Interface Strategy
| Interface | Priority | Purpose |
|-----------|----------|---------|
| **Chainlit** | P1 (Immediate) | Quick unified UI, infrastructure layer |
| FastAPI + PWA | P2 (Future) | Custom MC agent interface |
| Gemini CLI | P1 (Parallel) | Research/strategic work |

### 4. Feature Flags (CONFIRMED)
| Flag | Default | Description |
|------|---------|-------------|
| `FEATURE_VOICE` | `false` | Voice responses disabled by default |
| `FEATURE_REDIS_SESSIONS` | `true` | Redis session persistence |
| `FEATURE_QDRANT` | `true` | Qdrant vector search |
| `FEATURE_LOCAL_FALLBACK` | `true` | Local LLM fallback |

---

## Development Pipeline (LOCKED)

### Phase 1: Chainlit Consolidation (3.5 days)
**Start**: Immediately
**Branch**: `xnai-agent-bus/harden-infra`

| Day | Task | Files |
|-----|------|-------|
| 1 | Infrastructure Layer | `core/infrastructure/session_manager.py`, `core/infrastructure/knowledge_client.py` |
| 2 | Voice Module | `services/voice/voice_module.py` |
| 3 | Unified Chainlit App | `ui/chainlit_app.py` |
| 3.5 | Cleanup | Delete duplicates, fix imports |

**Benefits**:
- Eliminates 90% code duplication (1685 → 900 lines)
- Creates reusable infrastructure for all interfaces
- Voice module ready for future MC interface

### Phase 2: Gemini CLI MC Setup (2 days, parallel)
**Start**: Immediately (parallel with Chainlit)

| Task | Deliverable |
|------|-------------|
| Config files | `~/.gemini/config` |
| Project context | `GEMINI.md` |
| Memory hierarchy | Global/project/subdirectory files |
| Session templates | MC agent session templates |

### Phase 3: Knowledge Absorption System (1 week)
**Start**: After Phase 1

| Task | Deliverable |
|------|-------------|
| LangGraph pipeline | `knowledge_distillation.py` |
| Quality scoring | Scoring functions |
| Staging layer | `library/_staging/` |
| Qdrant integration | `xnai_knowledge` collection |

### Phase 4: FastAPI Interface (3 days)
**Start**: After Phase 3

| Task | Deliverable |
|------|-------------|
| WebSocket endpoint | MC coordination |
| Agent Bus routing | Task routing |
| Response streaming | Real-time responses |
| Connection management | Multi-session support |

---

## Research Jobs Queue Summary

**Total**: 19 jobs (4 P0, 10 P1, 5 P2)
**Full Details**: `memory_bank/strategies/RESEARCH-JOBS-QUEUE-MC-STRATEGY.md`

### Priority Order
1. **P0-CRITICAL**: Knowledge Absorption, Gemini Config, Core Integration, Access Control
2. **P1-HIGH**: Chainlit (R005-R008), Qdrant, FastAPI, Redis, Sanitization
3. **P2-MEDIUM**: Cleanup, Version Conflicts, Documentation, Testing

---

## Context Limits (CORRECTED)

### OpenCode Zen Free Models
| Model | Context Window | Best For |
|-------|---------------|----------|
| **GLM-5 Free** (current) | 200K tokens | Complex coding |
| Kimi K2.5 Free | 262K tokens | Vision-to-code |
| MiniMax M2.5 Free | 196K-1M tokens | Highest SWE-bench (80.2%) |

### GitHub Copilot Free Models
| Model | Context Window | Best For |
|-------|---------------|----------|
| Raptor mini | 264K tokens | Multi-file, refactoring |
| Claude Haiku 4.5 | 200K tokens | Fast routine tasks |
| GPT-4.1/GPT-4o/GPT-5 mini | 128K tokens | General-purpose |

### Gemini CLI
| Model | Context Window | Best For |
|-------|---------------|----------|
| Gemini 3 Flash | 1M tokens | Fast, large context |
| Gemini 3 Pro | 1M tokens | Research, complex tasks |

**Critical Distinction**: Model context window ≠ CLI internal memory management. OpenCode's compaction triggers at ~75% of model context, NOT at a fixed 10K.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                         │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Chainlit UI   │  │  FastAPI + PWA  │  │   Gemini CLI    │ │
│  │  (Phase 1: NOW) │  │ (Phase 4)       │  │ (Phase 2)       │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                    │                    │           │
└───────────┼────────────────────┼────────────────────┼───────────┘
            │                    │                    │
            ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                   INFRASTRUCTURE LAYER                          │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ SessionManager  │  │ KnowledgeClient │  │   VoiceModule   │ │
│  │ (Redis+Memory)  │  │ (Qdrant+FAISS)  │  │  (Optional)     │ │
│  │                 │  │                 │  │                 │ │
│  │ JOB-R005        │  │ JOB-R005        │  │ JOB-R006        │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                  │
│  ** CREATED IN PHASE 1 - REUSED BY ALL INTERFACES **            │
└─────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   KNOWLEDGE ABSORPTION LAYER                    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              LangGraph Distillation Pipeline            │    │
│  │  Extract → Classify → Score → Distill → Store          │    │
│  │                                                         │    │
│  │  Quality Gate: Reject if score < 0.6                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ** PHASE 3 - KNOWLEDGE INTEGRATION **                          │
└─────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    XNAi FOUNDATION CORE                         │
│                                                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ Memory Bank  │ │  Agent Bus   │ │   Qdrant     │            │
│  │ (Core/Recall)│ │(Redis Streams)│ │  (Vectors)  │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│                                                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │   Consul     │ │   Vikunja    │ │  OpenPipe    │            │
│  │ (Discovery)  │ │ (Tasks)      │ │  (Caching)   │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Documents Reference

| Document | Location | Purpose |
|----------|----------|---------|
| AI Model Reference | `expert-knowledge/model-reference/AI-MODEL-REFERENCE-2026-02-22.md` | Accurate model specs |
| Knowledge Absorption Design | `memory_bank/strategies/KNOWLEDGE-ABSORPTION-SYSTEM-DESIGN.md` | Pipeline architecture |
| Research Jobs Queue | `memory_bank/strategies/RESEARCH-JOBS-QUEUE-MC-STRATEGY.md` | 19 pending jobs |
| Chainlit Architecture Proposal | `internal_docs/04-research-and-development/CHAINLIT-ARCHITECTURE-PROPOSAL.md` | UI consolidation plan |
| CLI Session Management | `expert-knowledge/research/CLI-SESSION-MANAGEMENT-ANALYSIS.md` | CLI research |
| AGENTS.md | Root | CLI environment architecture |

---

## Completed Work (Cline Session 2026-02-22)

| Job | Description | Commit(s) |
|-----|-------------|-----------|
| AnyIO Migration | health_monitoring, health_checker, degradation, redis_state | `0789f53`, `d930dcb`, `c44a395`, `65f2abc` |
| Services Init Consolidation | Merged into single file | `699b3d2` |
| Chainlit Research | Architecture proposal | Proposal document created |
| OpenPipe Integration | Core module + Docker service | Complete |

---

## Ready for Execution

### Immediate Actions (This Session)
1. ✅ Merge `xnai-agent-bus/harden-infra` branch
2. ✅ Begin JOB-R005: Chainlit Infrastructure Layer
3. ✅ Begin Gemini CLI MC Setup (parallel)

### Dependencies Verified
- ✅ LangGraph 1.0.8 installed
- ✅ FastAPI installed
- ✅ Qdrant client installed
- ✅ Redis available
- ✅ Branch pushed to remote

---

## Next Session Priorities

1. **Review Voice App** (NEW DIRECTION)
   - Analyze Mac Mini voice app for Foundation integration
   - Identify XNAi principles to integrate
   - Extract standalone tools for community sharing

2. **Continue Chainlit Implementation**
   - Infrastructure layer
   - Voice module
   - Unified app

---

**STRATEGY LOCKED. READY FOR EXECUTION.**

---

**Next Action**: Begin Chainlit Infrastructure Layer (JOB-R005)