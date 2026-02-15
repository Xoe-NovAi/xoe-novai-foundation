# Memory Bank Navigation Index

**Last Updated**: 2026-02-14  
**Status**: Active  
**Purpose**: Single source of truth for Xoe-NovAi Foundation project status and coordination

---

## 📍 Where to Find What

### 🎯 IF YOU NEED TO...
| Need | File | Update Frequency | Purpose |
|------|------|------------------|---------|
| See overall project status | `progress.md` | After each phase | Phases 1-5+, milestones, metrics, roadmap |
| Understand project context | `CONTEXT.md` | Monthly | Mission, constraints, tech stack, team structure |
| Check what's currently being worked on | `activeContext.md` | Weekly | Active priorities, work streams, blockers |
| Learn project operations | `OPERATIONS.md` | As-needed | MkDocs, build system, common tasks |
| Review Phase N completion | `PHASES/phase-n-*.md` | Per phase | Objectives, deliverables, tests, handoff notes |
| Understand team coordination | `teamProtocols.md` | Monthly | Agent roles, workflows, communication protocols |

---

## 📚 CORE MEMORY BANK FILES

### 1. **progress.md** ⭐ PRIMARY
- **Type**: Status tracking (source of truth)
- **Update**: Every phase completion
- **Contains**: Phase status, milestones, metrics, health dashboard, recent achievements
- **Read if**: You want overall project status or completion metrics
- **Use for**: Team syncs, reporting, milestones

### 2. **CONTEXT.md** (Consolidated)
- **Type**: Strategic & technical reference
- **Update**: Monthly or on major architectural change
- **Contains**: 
  - Mission, vision, constraints
  - Technical stack and architecture decisions
  - System patterns and design patterns
  - Observability framework
  - Development environment setup
- **Read if**: You need background on project decisions
- **Use for**: New team member onboarding, architecture reviews

### 3. **activeContext.md**
- **Type**: Active work tracking
- **Update**: Weekly
- **Contains**: Current priorities (ranked P0-P8), active work streams, blockers, team roster
- **Read if**: You want to know current focus areas or what's blocking progress
- **Use for**: Daily standups, handoffs between team members

### 4. **OPERATIONS.md** (Consolidated)
- **Type**: How-to guide
- **Update**: As-needed
- **Contains**:
  - MkDocs build/serve commands
  - Common operations (test, build, deploy)
  - Troubleshooting procedures
  - Agent capabilities reference
- **Read if**: You need to run a command or do an operation
- **Use for**: Quick reference while developing

### 5. **teamProtocols.md**
- **Type**: Team coordination
- **Update**: When team changes or workflows change
- **Contains**: Agent roles, reporting structure, communication protocols, workflows
- **Read if**: You're new to the team or need to understand coordination
- **Use for**: Understanding who does what, handoff procedures

---

## 📂 PHASES DIRECTORY

Located in: `memory_bank/PHASES/`

| File | Purpose | Status |
|------|---------|--------|
| `phase-1-completion.md` | Circuit breakers & health monitoring | ✅ Complete |
| `phase-2-completion.md` | Service layer & infrastructure | ✅ Complete |
| `phase-3-status.md` | Error handling main status | 🟡 Partial |
| `phase-3-error-handling.md` | Error handling detailed progress | 🟡 Partial |
| `phase-4-status.md` | Integration testing & validation | 🟢 In Progress |
| `phase-5a-status.md` | zRAM optimization deployment | ✅ Complete |

**Use**: Reference specific phase completion details, test results, blockers

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

### 🤖 AI Agent / Team Member
1. Read: `teamProtocols.md` - understand your role
2. Check: `activeContext.md` - what are you assigned to?
3. Reference: `OPERATIONS.md` - how to run commands
4. Details: `PHASES/phase-n-*.md` - phase-specific docs

### 🆕 New Team Member
1. Read: `CONTEXT.md` - understand project (5 min)
2. Read: `teamProtocols.md` - understand team (5 min)
3. Read: `OPERATIONS.md` - learn procedures (5 min)
4. Read: `progress.md` - see current status (5 min)
5. Total onboarding: ~20 minutes

### 🔍 Researcher / Analyst
1. Check: `activeContext.md` - research requests and queue
2. Review: `expert-knowledge/research/` - research system
3. Reference: `internal_docs/02-research-lab/` - research templates

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

- **Latest Phase**: Phase 4 - Integration Testing & Stack Validation
- **Current Sub-Phase**: Phase 4.1 - Service Integration Testing (Commencing)
- **Overall Health**: 95% ✅
- **Latest Update**: 2026-02-14 10:20 UTC
- **Critical Blockers**: None
- **Active Work Streams**: 8 (See activeContext.md)

---

## 📞 Need Help?

1. **Can't find something?** → Check "Where to Find What" table above
2. **Need operation instructions?** → See `OPERATIONS.md`
3. **Need team info?** → See `teamProtocols.md`
4. **Need phase details?** → See `PHASES/phase-n-*.md`
5. **Need background?** → See `CONTEXT.md`
6. **Still stuck?** → Check `internal_docs/` for detailed docs

---

**Next Review**: 2026-02-21  
**Last Reviewed**: 2026-02-14  
**Maintained By**: Project Coordinator  
**Version**: 1.0 (2026-02-14)
