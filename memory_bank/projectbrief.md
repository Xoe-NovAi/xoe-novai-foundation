---
block:
  label: project_brief
  description: Foundation document defining mission, core values, key constraints, and project scope
  chars_limit: 3000
  read_only: false
  tier: core
  priority: 1
created: 2026-02-19
modified: 2026-02-20
version: "1.1"
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

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ Complete | Import Standardization & Module Skeleton |
| Phase 2 | ✅ Complete | Service Layer & Rootless Infrastructure |
| Phase 3 | ✅ Complete | Documentation & Stack Alignment |
| Phase 4 | ✅ Complete | Integration Testing & Stack Validation |
| Phase 5 | ✅ Complete | Sovereign Multi-Agent Cloud |
| Phase 7 | ✅ Complete | Deployment & Agent Bus Integration |
| Phase 8 | 🔵 Next | Advanced Features |

> **Canonical Source**: `progress.md` for detailed phase status

## Related Documents

- `productContext.md` - Why XNAi exists, problems solved
- `techContext.md` - Technology stack and constraints
- `systemPatterns.md` - Architecture patterns

---
**Last Updated**: 2026-02-20
**Owner**: Architect
