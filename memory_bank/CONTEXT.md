---
block:
  label: context_index
  description: Index and pointer file for strategic context documents
  chars_limit: 2000
  read_only: true
  tier: core
  priority: 0
created: 2026-02-19
modified: 2026-02-20
version: "2.0"
---

# Strategic Context Index

> **Note**: This file has been split into focused memory blocks for better LLM context management. See the individual files below for detailed content.

## Core Memory Blocks

| Block | File | Purpose | Size Limit |
|-------|------|---------|------------|
| Project Brief | `projectbrief.md` | Mission, values, constraints | 3KB |
| Product Context | `productContext.md` | Why XNAi, problems solved, goals | 4KB |
| System Patterns | `systemPatterns.md` | Architecture, design patterns | 8KB |
| Tech Context | `techContext.md` | Stack, dependencies, setup | 5KB |
| Active Context | `activeContext.md` | Current sprint, priorities | 5KB |
| Progress | `progress.md` | Phase status, milestones | 6KB |

## Quick Navigation

### For New Team Members
1. `projectbrief.md` - What is XNAi and why does it exist?
2. `techContext.md` - What technologies does XNAi use?
3. `activeContext.md` - What's being worked on right now?

### For Architects
1. `systemPatterns.md` - How is XNAi built?
2. `techContext.md` - What are the constraints?
3. `strategies/` - Strategic planning documents

### For Operations
1. `OPERATIONS.md` - How to run commands
2. `techContext.md` - Service ports and setup
3. `PHASES/` - Phase-specific documentation

## Related Directories

| Directory | Purpose |
|-----------|---------|
| `PHASES/` | Phase completion documentation |
| `strategies/` | Strategic planning documents |
| `activeContext/` | Session handover documents |
| `recall/` | Searchable session history |
| `archival/` | Long-term reference material |
| `_archive/` | Deprecated content |

## Memory Architecture

XNAi uses a **MemGPT-style hierarchical memory architecture**:

```
┌─────────────────────────────────────┐
│       CORE MEMORY (Always Loaded)   │
│  projectbrief, productContext,      │
│  systemPatterns, techContext,       │
│  activeContext, progress            │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│      RECALL TIER (Searchable)       │
│  Session logs, decisions, handovers │
│  recall/ directory                  │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│     ARCHIVAL TIER (On-Demand)       │
│  Research, benchmarks, strategies   │
│  archival/ directory                │
└─────────────────────────────────────┘
```

See `BLOCKS.yaml` for block definitions and size limits.

---
**Last Updated**: 2026-02-20
**Consolidated From**: projectbrief, techContext, systemPatterns, teamProtocols
