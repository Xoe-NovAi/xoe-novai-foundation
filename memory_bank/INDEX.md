# Memory Bank Navigation Index

**Last Updated**: 2026-02-23  
**Status**: Wave 1 Complete - Wave 2 Dispatched  
**Architecture**: MemGPT-style hierarchical memory  
**Purpose**: Single source of truth for Xoe-NovAi Foundation project status and coordination
**Coordination Key**: `ACTIVE-TASK-DISPATCH-2026-02-23`

---

## 📍 Where to Find What

### 🎯 IF YOU NEED TO...
| Need | File | Update Frequency | Purpose |
|------|------|------------------|---------|
| See overall project status | `progress.md` | After each phase | Phases 1-7+, milestones, metrics, roadmap |
| Understand project mission | `projectbrief.md` | Project start | Mission, values, constraints, scope |
| Understand why XNAi exists | `productContext.md` | Monthly | Problems solved, UX goals, success metrics |
| Learn architecture patterns | `systemPatterns.md` | As needed | Design patterns, decisions, code standards |
| Check tech stack | `techContext.md` | As needed | Technologies, dependencies, setup |
| Check what's currently being worked on | `activeContext.md` | Weekly | Active priorities, work streams, blockers |
| Learn project operations | `OPERATIONS.md` | As-needed | MkDocs, build system, common tasks |
| Review Phase N completion | `PHASES/phase-n-*.md` | Per phase | Objectives, deliverables, tests, handoff notes |
| Understand team coordination | `teamProtocols.md` | Monthly | Agent roles, workflows, communication protocols |
| Search historical context | `recall/` | As needed | Sessions, decisions, handovers |
| Find reference material | `archival/` | As needed | Research, benchmarks, strategies |

---

## 📚 CORE MEMORY BANK FILES

### Core Memory Blocks (Always Loaded)

| Block | File | Purpose | Size Limit |
|-------|------|---------|------------|
| Project Brief | `projectbrief.md` | Mission, values, constraints | 3KB |
| Product Context | `productContext.md` | Why XNAi, problems solved, goals | 4KB |
| System Patterns | `systemPatterns.md` | Architecture, design patterns | 8KB |
| Tech Context | `techContext.md` | Stack, dependencies, setup | 5KB |
| Active Context | `activeContext.md` | Current sprint, priorities | 5KB |
| Progress | `progress.md` | Phase status, milestones | 6KB |
| Architecture | `ARCHITECTURE.md` | System architecture with diagrams | 10KB |

### Block Configuration

See `BLOCKS.yaml` for:
- Size limits and descriptions
- Update triggers and relationships
- Memory tool configurations
- MCP server settings

---

## 📂 PHASES DIRECTORY

Located in: `memory_bank/PHASES/`

### Infrastructure Phases (Complete)
| File | Purpose | Status |
|------|---------|--------|
| `phase-1-completion.md` | Circuit breakers & health monitoring | ✅ Complete |
| `phase-3-status.md` | Error handling main status | ✅ Complete |
| `phase-3-error-handling-detailed.md` | Error handling detailed | ✅ Complete |
| `phase-4-status.md` | Integration testing | ✅ Complete |
| `phase-5a-status.md` | zRAM optimization | ✅ Complete |
| `phase6-status.md` | Multi-agent cloud | ✅ Complete |

### Strategy Phases (Current)
| File | Purpose | Status |
|------|---------|--------|
| `PHASE-2-COMPLETION-2026-02-22.md` | Gemini CLI MC Setup | ✅ Complete |

**Use**: Reference specific phase completion details, test results, blockers

---

## 📋 STRATEGIES DIRECTORY

Located in: `memory_bank/strategies/`

| File | Purpose | Status |
|------|---------|--------|
| `UNIFIED-STRATEGY-v1.0.md` | Master strategy plan | Active |
| `PROJECT-QUEUE.yaml` | Consolidated project queue | Active |
| `IMPLEMENTATION-PLAYBOOK-v1.0.md` | Phase execution playbook | Active |
| `OPUS-STRATEGIC-REVIEW-2026-02-19.md` | Architecture review | Active |
| `OPUS-TOKEN-STRATEGY.md` | Token optimization strategy | Active |
| `P-010-AUDIT-FINDINGS.md` | Code audit findings | Active |
| `AI-ASSISTANT-QUICKSTART.md` | Session startup protocol | Active |
| `TIER2-DISCOVERY-AUDIT-TASK.md` | Phase A discovery task | Active |

**Use**: Strategic planning, architectural decisions, roadmap reference

---

## 🔄 RECALL TIER (Searchable History)

Located in: `memory_bank/recall/`

| Directory | Purpose | Retention |
|-----------|---------|-----------|
| `conversations/` | Session logs | 90 days |
| `decisions/` | Architecture decisions | Permanent |
| `handovers/` | Agent handoff documents | 30 days |

**Use**: Search for historical context, past decisions, session continuity

---

## 🗄️ ARCHIVAL TIER (Long-Term Storage)

Located in: `memory_bank/archival/`

| Directory | Purpose | Source |
|-----------|---------|--------|
| `research/` | Research findings | `expert-knowledge/` |
| `benchmarks/` | Benchmark results | `benchmarks/` |
| `strategies/` | Strategic documents | `strategies/` |

**Use**: Semantic search for reference material, deep research

---

## 🔧 OPENCODE INTEGRATION

### Configuration Files
| Path | Purpose |
|------|---------|
| `AGENTS.md` | Project rules for OpenCode CLI |
| `.opencode/opencode.json` | OpenCode configuration |
| `.opencode/skills/*/SKILL.md` | Reusable workflow skills |
| `.opencode/agents/*.md` | Specialized agent definitions |
| `.opencode/commands/*.md` | Custom slash commands |
| `mcp-servers/xnai-*/` | MCP servers for Foundation stack |

### Available Skills
| Skill | Trigger | Purpose |
|-------|---------|---------|
| memory-bank-loader | Session start | Load project context |
| agent-bus-coordinator | Multi-agent tasks | Redis Streams coordination |
| phase-validator | Milestones | Verify phase completion |
| sovereign-security-auditor | Pre-commit | Security hardening check |
| doc-taxonomy-writer | Doc changes | Diátaxis classification |
| vikunja-task-manager | Planning | Task creation/tracking |
| semantic-search | Research | RAG queries |

### MCP Servers
| Server | Endpoint | Purpose |
|--------|----------|---------|
| xnai-rag | localhost:8000 | Semantic search |
| xnai-agentbus | localhost:6379 | Agent coordination |
| xnai-vikunja | localhost:3456 | Task management |

### Documentation
See `internal_docs/05-research/` for:
- `OPENCODE-CLI-BEST-PRACTICES.md` - Usage guide
- `OPENCODE-MCP-RECOMMENDATIONS.md` - MCP server docs
- `OPENCODE-SKILLS-RECOMMENDATIONS.md` - Skill development
- `OPENCODE-FORK-INTEGRATION-RESEARCH.md` - Deep integration research

---

## 🔗 RELATED DOCUMENTATION

### For Detailed Implementation Work
See: `internal_docs/01-strategic-planning/`
- Phase-specific strategy documents
- Research findings and deep dives
- Team handoff documentation
- Implementation patterns

### For Operational Issues
See: `internal_docs/03-infrastructure-ops/`
- Deployment guides
- Incident analysis
- Build reports

### For Code Quality
See: `internal_docs/04-code-quality/`
- Code audits and reviews
- Implementation guides
- Security analysis

### For Knowledge Management
See: `expert-knowledge/`
- Research system and queue
- Agent capabilities and models
- Synchronization patterns

---

## 🚀 QUICK START BY ROLE

### 👤 Project Manager / Architect
1. Read: `progress.md` - overall status
2. Check: `activeContext.md` - current priorities
3. Review: `PHASES/phase-n-status.md` for specific phase details
4. Strategic: `strategies/UNIFIED-STRATEGY-v1.0.md` - master plan

### 🤖 AI Agent / Team Member
1. Read: `projectbrief.md` - understand mission (2 min)
2. Read: `techContext.md` - stack constraints (2 min)
3. Check: `activeContext.md` - what are you assigned to?
4. Reference: `OPERATIONS.md` - how to run commands
5. Details: `PHASES/phase-n-*.md` - phase-specific docs

### 🆕 New Team Member
**For a step-by-step guide, start here: `docs/01-start/ONBOARDING-CHECKLIST.md`**

1. Read: `projectbrief.md` - understand project (2 min)
2. Read: `productContext.md` - understand why (2 min)
3. Read: `techContext.md` - understand stack (2 min)
4. Read: `teamProtocols.md` - understand team (3 min)
5. Read: `progress.md` - see current status (3 min)
6. Total onboarding: ~15 minutes

### 🔍 Researcher / Analyst
1. Check: `activeContext.md` - research requests and queue
2. Search: `recall/` - historical context
3. Search: `archival/` - reference material
4. Reference: `expert-knowledge/` - domain expertise

---

## 📊 MAINTENANCE SCHEDULE

| Task | Frequency | Owner | Checklist |
|------|-----------|-------|-----------|
| Update progress.md | Per phase | Phase lead | See Phase Completion Checklist below |
| Update activeContext.md | Weekly | Coordinator | Update priorities, blockers, metrics |
| Review memory_bank structure | Monthly | Architect | Check for new files, duplicate content |
| Archive old documents | Per quarter | Maintainer | Move obsolete files to _archive/ |
| Verify all links | After updates | Updater | Ensure no broken references |

---

## ✅ PHASE COMPLETION CHECKLIST

**When Phase N completes, ensure these are updated/created:**

### Memory Bank Updates
- [ ] `progress.md` - Add Phase N status, update milestones
- [ ] `activeContext.md` - Update priorities for Phase N+1
- [ ] `PHASES/phase-n-status.md` - Create/update with:
  - [ ] Objectives completed (list all)
  - [ ] Deliverables (code, tests, docs)
  - [ ] Test results and coverage metrics
  - [ ] Known issues or technical debt
  - [ ] Handoff notes for next phase

### Strategic Documentation
- [ ] `internal_docs/01-strategic-planning/PHASE-N-COMPLETION-SUMMARY.md`
- [ ] `internal_docs/01-strategic-planning/PHASE-N-RESEARCH-FINDINGS.md` (if applicable)
- [ ] `internal_docs/01-strategic-planning/PHASE-N-TEAM-HANDOFF.md`

### Code Documentation
- [ ] Update `internal_docs/04-code-quality/IMPLEMENTATION-GUIDES/`
- [ ] Add test results and coverage metrics
- [ ] Document any refactoring or debt

### Team Coordination
- [ ] Update `internal_docs/communication_hub/` with results
- [ ] Send completion summary via Agent Bus
- [ ] Update relevant agent state files

### Public Documentation
- [ ] Update `docs/` release notes if applicable
- [ ] Update feature list if user-facing

---

## 🔄 SYNCHRONIZATION PROTOCOL

### After Major Changes
1. Update relevant memory_bank file immediately
2. Cross-reference with internal_docs/01-strategic-planning/ docs
3. Notify team via activeContext.md update
4. If blocking other work, update activeContext.md blockers section

### For Session Handoffs
1. Review `activeContext.md` - what was I doing?
2. Check `progress.md` - what has changed?
3. Read `PHASES/phase-n-status.md` - what's the current phase?
4. Read relevant `internal_docs/01-strategic-planning/` docs for details

### For New Phases
1. Create PHASES/phase-n-status.md from template
2. Link to internal_docs/01-strategic-planning/ research
3. Update activeContext.md with Phase N as current
4. Update progress.md Phase N section

---

## 📈 KEY METRICS DASHBOARD

See `progress.md` for:
- Phase completion status (1-5+)
- Milestone achievements
- Health metrics (services, memory, CPU)
- Test pass rates
- Success metrics tracking

---

## 🎯 CURRENT STATUS AT A GLANCE

- **Current Wave**: Wave 2 Dispatched (32 tasks)
- **Wave 1**: ✅ Complete (17/17 tasks)
- **Overall Progress**: 35% (17/49 tasks)
- **Overall Health**: 95% ✅
- **Latest Update**: 2026-02-23
- **Critical Blockers**: None
- **Active Agents**: CLINE (implementation), GEMINI-MC (research)
- **Coordination Key**: `ACTIVE-TASK-DISPATCH-2026-02-23`
- **Memory Architecture**: MemGPT-style hierarchical (Core → Recall → Archival)

---

## 🏗️ MEMORY ARCHITECTURE

XNAi uses a **MemGPT-style hierarchical memory architecture**:

```
┌─────────────────────────────────────────────────────┐
│            CORE MEMORY (Always Loaded)              │
│  projectbrief • productContext • systemPatterns    │
│  techContext • activeContext • progress            │
│  Budget: ~25K tokens (~100KB chars)                 │
└─────────────────────────────────────────────────────┘
                         ↓ evict/summarize
┌─────────────────────────────────────────────────────┐
│            RECALL TIER (Searchable)                  │
│  Session logs • Decisions • Handovers              │
│  recall/ directory • 90-day retention               │
│  Indexed for semantic search                        │
└─────────────────────────────────────────────────────┘
                         ↓ archive
┌─────────────────────────────────────────────────────┐
│           ARCHIVAL TIER (On-Demand)                 │
│  Research • Benchmarks • Strategies                 │
│  archival/ directory • Permanent storage            │
│  Retrieved via semantic search                      │
└─────────────────────────────────────────────────────┘
```

### Memory Tools (via BLOCKS.yaml)

| Tool | Purpose |
|------|---------|
| `memory_replace` | Surgical edit within a block |
| `memory_append` | Add content to a block |
| `memory_rethink` | Replace entire block content |
| `compile_context` | Generate compiled context for LLM |

### MCP Integration (Planned)

- URI scheme: `memory://bank/{path}`
- Real-time subscriptions for file changes
- Standardized resource discovery

---

## 📞 Need Help?

1. **Can't find something?** → Check tables above or see `BLOCKS.yaml`
2. **Need operation instructions?** → See `OPERATIONS.md`
3. **Need team info?** → See `teamProtocols.md`
4. **Need phase details?** → See `PHASES/phase-n-*.md`
5. **Need background?** → See `projectbrief.md` and `productContext.md`
6. **Still stuck?** → Check `internal_docs/` for detailed docs

---

**Next Review**: 2026-02-27
**Last Reviewed**: 2026-02-20
**Maintained By**: Project Coordinator
**Version**: 2.0 (MemGPT Architecture)
