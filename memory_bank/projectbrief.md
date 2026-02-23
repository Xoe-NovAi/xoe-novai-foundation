---
block:
  label: project_brief
  description: Foundation document defining mission, core values, key constraints, and project scope
  chars_limit: 3000
  read_only: false
  tier: core
  priority: 1
created: 2026-02-19
modified: 2026-02-23
version: "1.2"
---

# Project Brief - Xoe-NovAi Foundation Stack

## Mission

Build a **Sovereign AI Foundation Stack** - a production-ready, self-documenting system that combines RAG, LLM capabilities, and robust infrastructure for the Xoe-NovAi ecosystem.

## Core Values

| Value | Description |
|-------|-------------|
| **Sovereignty** | Complete control over data and deployment |
| **Resilience** | Graceful degradation, circuit breakers, health monitoring |
| **Scalability** | Modular architecture, horizontal scaling support |
| **Observability** | Complete visibility into system behavior |
| **Ma'at Alignment** | Ethical AI principles throughout |

## Key Constraints

| Constraint | Requirement |
|------------|-------------|
| Telemetry | Zero external telemetry (air-gap capable) |
| Containerization | Non-root containers (security) |
| Filesystem | Read-only filesystems (immutability) |
| Memory | <6GB memory footprint (resource-constrained) |
| Latency | <500ms API response times (performance) |

## Project Phases

### Completed Infrastructure Phases (2026-02)
| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1-7 | ✅ Complete | Foundation bootstrap, Agent Bus integration |
| Phase 8 | ✅ Complete | Infrastructure Hardening |
| Phase 9 | ✅ Complete | Code Audit & Implementation Fixes |
| Phase 10 | ✅ Complete | OpenPipe Integration |

### Current Strategy Phases (2026-02)
| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ Complete | Chainlit Consolidation (65% code reduction) |
| Phase 2 | ✅ Complete | Gemini CLI MC Setup |
| Phase 3 | ✅ Complete | Knowledge Absorption System |
| Phase 4 | 🔵 In Progress | Core Integration (CLINE executing) |

> **Canonical Source**: `progress.md` for detailed phase status
> **Task Dispatch**: `strategies/ACTIVE-TASK-DISPATCH-2026-02-22.md`

## Related Documents

- `productContext.md` - Why XNAi exists, problems solved
- `techContext.md` - Technology stack and constraints
- `systemPatterns.md` - Architecture patterns

---
**Last Updated**: 2026-02-23
**Owner**: MC-Overseer Agent
