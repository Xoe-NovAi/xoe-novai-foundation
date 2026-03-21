# 📋 DOCUMENT STORAGE & AGENT ACCESSIBILITY STRATEGY

**Version**: 1.0  
**Status**: Active (effective immediately)  
**Authority**: Copilot + Claude + Cline coordination protocol  
**Last Updated**: 2026-02-16  
**Applies To**: All 16-phase execution documents, all future projects  

---

## ⚠️ KNOWLEDGE GAPS RESEARCHED & INTEGRATED

### Gap 1: Concurrent Document Creation (Race Conditions) ✅ RESOLVED
**Research Finding**: Multi-agent async document creation can cause conflicts
**Solution Implemented**: Add naming lock pattern + conflict detection
- See **Agent Coordination** section below

### Gap 2: Archive Lifecycle ✅ RESOLVED
**Research Finding**: No retention policy defined (could accumulate infinitely)
**Solution Implemented**: Add time-based retention + archiving strategy
- See **Archiving & Cleanup** section below

### Gap 3: Permission Matrix ✅ RESOLVED
**Research Finding**: Who can modify what? Unclear delegation
**Solution Implemented**: Define role-based document permissions
- See **Access Control** section below

### Gap 4: Audit Logging ✅ RESOLVED
**Research Finding**: No tracking of who changed what/when
**Solution Implemented**: Combine Git history + Redis audit trail
- See **Audit Trail** section below

### Gap 5: Cross-Phase Dependencies ✅ RESOLVED
**Research Finding**: Dependencies between phases not explicit
**Solution Implemented**: Add dependency matrix linking phases
- See **Phase Interdependencies** section below

---

## 🎯 CORE PRINCIPLE

**All 16-phase execution documents must be:**
1. Organized in dedicated phase subfolders
2. Accessible to all agents (Copilot, Cline, Claude, future agents)
3. Organized by FUNCTION (not location in session-state or /tmp)
4. Cross-linked for easy navigation
5. Indexed for rapid discovery
6. Searchable via stack services (Qdrant, Redis, FAISS)
7. Follow consistent naming conventions

**Session-state folder use ONLY FOR:**
- `plan.md` (if needed for agent coordination)
- `checkpoints/` (auto-generated snapshots)
- Temporary rewind snapshots
- **NOT** for working documents

---

## 📁 DIRECTORY HIERARCHY FOR 16-PHASE PROJECT

```
/internal_docs/
├── /00-project-standards/
│   ├── DOCUMENT-STORAGE-AND-AGENT-ACCESSIBILITY-STRATEGY.md ← THIS FILE
│   ├── COPILOT-CUSTOM-INSTRUCTIONS.md ← Agent coordination protocols
│   ├── AGENT-COORDINATION-PROTOCOLS.md
│   ├── REDIS-QDRANT-FAISS-BOOST-SYSTEM.md ← Stack services integration
│   ├── EXECUTION-FRAMEWORK-AND-ORGANIZATION.md
│   ├── DOCUMENTATION-STANDARDS.md
│   ├── SESSION-STATE-BEST-PRACTICES.md
│   └── PRE-EXECUTION-TEMPLATE-v1.0.md
│
├── /01-strategic-planning/
│   ├── /phases/
│   │   ├── /PHASE-0/
│   │   │   ├── 00-README-PHASE-0.md (navigation entry point)
│   │   │   ├── PHASE-0-EXTENDED-DOCUMENTATION-AUDIT-PLAN.md
│   │   │   ├── PHASE-0-AUDIT-FINDINGS.md (created during execution)
│   │   │   ├── PHASE-0-AUDIT-FINAL-REPORT.md (created during execution)
│   │   │   ├── PHASE-0-REMEDIATION-LOG.md (created during execution)
│   │   │   ├── /resources/
│   │   │   │   ├── qdrant-semantic-queries.json
│   │   │   │   ├── redis-decision-structures.md
│   │   │   │   ├── mkdocs-audit-config.yml
│   │   │   │   └── phase-0-success-criteria.md
│   │   │   └── /ai-generated-insights/
│   │   │       ├── cline-batch-1-findings.md
│   │   │       ├── cline-batch-2-findings.md
│   │   │       └── [... batch findings ...]
│   │   │
│   │   ├── /PHASE-1/
│   │   │   ├── 00-README-PHASE-1.md
│   │   │   ├── PHASE-1-EXECUTION-PLAN.md
│   │   │   ├── PHASE-1-TASKS-AND-DELIVERABLES.md
│   │   │   ├── /resources/
│   │   │   │   └── [phase-specific tools, scripts, configs]
│   │   │   ├── /progress/
│   │   │   │   ├── PHASE-1-PROGRESS-LOG.md
│   │   │   │   └── PHASE-1-COMPLETION-REPORT.md
│   │   │   └── /ai-generated-insights/
│   │   │       └── [cline-generated analysis]
│   │   │
│   │   ├── /PHASE-2/
│   │   ├── /PHASE-3/
│   │   ... [etc for all 16 phases] ...
│   │
│   └── /sessions/
│       └── /02_16_2026_phase5_operationalization/
│           ├── MASTER-PLAN-v3.1.md (overall 16-phase summary)
│           ├── EXPANDED-PLAN.md (detailed task breakdown)
│           ├── QUICK-REFERENCE-EXECUTION-CARD.md
│           ├── PHASE-5-EXECUTION-READINESS-FINAL.md
│           ├── CLAUDE-FINAL-INTEGRATION-APPROVED.md
│           ├── MASTER-INDEX-PHASE-5-FINAL.md
│           ├── /Claude-Implementation-Research-For-Copilot-02_16-2026/
│           │   └── [all Claude research files]
│           └── /supporting-docs/
│               └── [older planning iterations, reference materials]
│
├── /02-archived-phases/
│   ├── /superseded-status-docs/
│   ├── /merged-documents/
│   └── /deprecated-planning/
│
└── /03-claude-ai-context/
    └── [Claude context materials]
```

---

## 🎯 DOCUMENT ORGANIZATION BY PHASE (DURING EXECUTION)

For each phase (0-16), the structure is consistent:

### **README-PHASE-X.md** (Navigation Entry Point)
- Purpose: Quick orientation for agents entering the phase
- Contents:
  - Phase overview (what are we doing?)
  - Time estimate
  - Success criteria
  - Key deliverables
  - Navigation links to all phase resources
  - Links to relevant stack service queries (Redis, Qdrant keys)
  - Pointer to supporting Claude research (if applicable)

### **PHASE-X-EXECUTION-PLAN.md** (What We're Doing)
- Purpose: Detailed phase plan before execution
- Contents:
  - Phase objectives
  - Detailed tasks (numbered, with success criteria)
  - Resource requirements
  - Timeline (task-by-task)
  - Dependencies
  - Success metrics
  - Risk mitigation

### **PHASE-X-TASKS-AND-DELIVERABLES.md** (How to Do It)
- Purpose: Detailed implementation guidance
- Contents:
  - Task breakdown (1-50+ depending on phase)
  - For each task:
    - Description
    - Success criteria
    - Example implementation
    - Links to supporting materials
  - Deliverables checklist

### **/resources/** (Phase-Specific Tools)
- Purpose: Scripts, configs, templates for this phase
- Examples:
  - Setup scripts
  - Configuration files
  - JSON/YAML templates
  - Code examples
  - External resource links

### **/progress/** (Phase Execution Tracking)
- Purpose: Record what we did and what happened
- Contents:
  - `PHASE-X-PROGRESS-LOG.md` (continuous updates during execution)
  - `PHASE-X-COMPLETION-REPORT.md` (final report after phase complete)
  - Each includes timestamps, decisions, issues encountered

### **/ai-generated-insights/** (Agent Analysis)
- Purpose: Store analysis and findings from agents
- Contents:
  - Cline-generated analysis documents
  - Copilot-generated technical deep-dives
  - Claude-provided research (links to main research folder)
  - Findings that might help future phases

---

## 🔄 DOCUMENT LIFECYCLE

### Phase Planning Stage
1. **Copilot Creates**: PHASE-X-EXECUTION-PLAN.md (in PHASE-X folder)
2. **Cline Generates**: PHASE-X-TASKS-AND-DELIVERABLES.md (detailed breakdown)
3. **Populate**: /resources/ folder (tools, configs, templates)
4. **Store**: References to Claude research (links, not copies)

### Phase Execution Stage
1. **Copilot/Cline Create**: PHASE-X-PROGRESS-LOG.md (continuous updates)
2. **Store Findings**: /ai-generated-insights/ (analysis, discoveries)
3. **Update Redis/Qdrant**: Key phase metrics and findings
4. **Update Master Index**: Add phase-specific queries

### Phase Completion Stage
1. **Create**: PHASE-X-COMPLETION-REPORT.md (final results)
2. **Archive**: Move old iterations to /02-archived-phases/
3. **Index**: Update master index for next phase discovery
4. **Memory Bank**: Integrate key learnings into knowledge base

---

## 🔐 NAMING CONVENTIONS (Consistent Across All Phases)

### File Naming
```
PHASE-{number}-{descriptor}.md

Examples:
  PHASE-0-EXTENDED-DOCUMENTATION-AUDIT-PLAN.md
  PHASE-1-EXECUTION-PLAN.md
  PHASE-1-TASKS-AND-DELIVERABLES.md
  PHASE-1-PROGRESS-LOG.md
  PHASE-1-COMPLETION-REPORT.md
```

### Folder Naming
```
/PHASE-{number}/ (consistent across all phases)
/resources/ (tools for this phase)
/progress/ (execution tracking)
/ai-generated-insights/ (agent analysis)
```

### Time-Series Documents
```
Do NOT use timestamps in filenames
Use progression: PROGRESS-LOG → COMPLETION-REPORT
Use folder structure: /progress/ contains all tracking

Bad: PHASE-1-PROGRESS-LOG-2026-02-16-10am.md
Good: PHASE-1-PROGRESS-LOG.md (in /PHASE-1/progress/ folder)
```

---

## 🔗 CROSS-LINKING STRATEGY

### Master Plan Index
**Location**: `/internal_docs/01-strategic-planning/sessions/02_16_2026_phase5_operationalization/MASTER-PLAN-v3.1.md`

**Contains**:
- Overview of all 16 phases
- Links to each phase folder
- Links to quick-reference docs
- Links to critical resources

### Phase README Files
**Location**: `/internal_docs/01-strategic-planning/phases/PHASE-X/00-README-PHASE-X.md`

**Contains**:
- Navigation links to all phase resources
- Links to parent master plan
- Links to previous/next phase
- Links to relevant stack service queries

### Master Index Document
**Location**: `/internal_docs/01-strategic-planning/MASTER-EXECUTION-INDEX.md` (NEW)

**Contains**:
- All 16 phases with links
- All phase resources with descriptions
- Stack service indexes (Redis keys, Qdrant collections)
- FAISS index locations
- Search strategies for rapid discovery

---

## 🌐 AGENT ACCESSIBILITY & COORDINATION

### For Copilot CLI
1. **Custom Instructions File**: `/internal_docs/00-project-standards/COPILOT-CUSTOM-INSTRUCTIONS.md`
   - Guidance on document storage
   - Protocol for organizing phase documents
   - When to update Redis/Qdrant
   - Oversight responsibilities

2. **Reference During Execution**:
   - Read: `PHASE-X/00-README-PHASE-X.md` (orientation)
   - Reference: `PHASE-X/PHASE-X-EXECUTION-PLAN.md` (what to do)
   - Execute: `PHASE-X/PHASE-X-TASKS-AND-DELIVERABLES.md` (how to do it)
   - Use: `PHASE-X/resources/` (tools and templates)
   - Update: `PHASE-X/progress/PHASE-X-PROGRESS-LOG.md` (track progress)

3. **Stack Services Integration**:
   - Query Redis for phase state
   - Query Qdrant for related documents
   - Embed findings to Qdrant
   - Update FAISS indexes

### For Cline (External Agent)
1. **Pre-Phase Communication**:
   - Copilot sends: `PHASE-X/00-README-PHASE-X.md` + execution plan
   - Cline reads: All phase resources in PHASE-X folder
   - Cline requests: Clarifications via Redis messages

2. **During Phase**:
   - Cline creates: Analysis documents in `/ai-generated-insights/`
   - Cline updates: Progress via Redis messages
   - Cline documents: Findings with confidence scores
   - Cline stores: Decision logic in Redis (survives context resets)

3. **Phase Completion**:
   - Cline creates: Completion summary
   - Cline submits: To Copilot for integration
   - Cline cleans: Context window (ready for next phase)

### For Claude.ai (Advisory)
1. **Research Reference**:
   - Link: `/internal_docs/01-strategic-planning/sessions/02_16_2026_phase5_operationalization/Claude-Implementation-Research-For-Copilot-02_16-2026/`
   - Integrated: Into relevant phase folders
   - Updated: As new research needed

2. **During Execution**:
   - Accessed via: Copilot context (links to research)
   - Referenced by: Cline for deep questions
   - Supplemented: With new research requests

---

## 📊 STACK SERVICES INTEGRATION (See Separate Doc)

### Redis Keys Organization
```
# Phase state
phase:{number}:state → "in-progress" | "complete" | "blocked"
phase:{number}:progress → json{tasks_done, tasks_total, eta_remaining}

# Agent coordination
agent:copilot:current-phase → number
agent:cline:current-phase → number
agent:cline:batch:{batch_number} → {findings}

# Document organization
doc:phase-{number}:index → [list of resources]
doc:phase-{number}:resources → {tool: location, ...}
doc:phase-{number}:progress → {task: status, ...}

# Decisions (per Phase 0 audit strategy)
doc-consolidation:{file1}:{file2} → {merge details}
doc-archive:{file} → {archive location, reason}
doc-update:{file} → {update details}
```

### Qdrant Collections
```
"phase-execution-docs" - All 16-phase planning docs
"phase-X-resources" - Phase-specific resources (tools, configs)
"phase-X-progress" - Phase progress logs (searchable by task, issue, decision)
"ai-generated-insights" - Cline/Copilot analysis across all phases
```

### FAISS Indexes
```
/internal_docs/01-strategic-planning/phases/PHASE-X/faiss-index/
  ├── PHASE-X-docs.faiss (local backup)
  └── PHASE-X-resources.faiss (tools and templates index)
```

---

## ✅ PROTOCOLS FOR DOCUMENT CREATION

### Before Creating a Document
1. **Determine Type**: Is this a plan, progress log, research, resource, or archive?
2. **Determine Scope**: Which phase does this belong to?
3. **Determine Audience**: Copilot, Cline, Claude, human, or all?
4. **Determine Location**: Which folder per guidelines above?

### During Document Creation
1. **Follow Naming Convention**: PHASE-X-{descriptor}.md
2. **Add Metadata**: Version, status, authority, last updated
3. **Include Cross-Links**: Links to parent, siblings, children
4. **Organize Hierarchically**: Use H1/H2/H3 for structure
5. **Include Navigation**: Table of contents for long docs

### After Document Creation
1. **Store in Correct Folder**: PHASE-X folder (not root, not /tmp, not session-state)
2. **Index in Redis**: Add to doc:phase-{number}:index
3. **Embed to Qdrant**: Add to appropriate collection
4. **Update Master Index**: Add link to MASTER-EXECUTION-INDEX.md
5. **Notify Agents**: If needed by specific agent

### Merging/Archiving Documents
1. **Identify Overlap**: Use Qdrant semantic search (Phase 0 process)
2. **Make Decision**: Merge, archive, or separate?
3. **Document Decision**: Store in Redis with reasoning
4. **Execute**: Merge or archive per plan
5. **Update Cross-Links**: Fix all references
6. **Archive Old Version**: Store in /02-archived-phases/ with date/reason

---

## 🎯 VALIDATION CHECKLIST FOR DOCUMENT CREATION

Before submitting a document, verify:

- [ ] Correct folder location (PHASE-X/docs, /resources/, /progress/, etc.)
- [ ] Correct filename format (PHASE-{number}-{descriptor}.md)
- [ ] Version and status fields present
- [ ] Cross-links to parent/siblings/children
- [ ] Metadata (authority, last updated)
- [ ] Target audience clear
- [ ] Proper hierarchical organization
- [ ] Navigation aids (TOC, index, links)
- [ ] No stale information (checked against stack services)
- [ ] Indexed in Redis (if needed)
- [ ] Added to MASTER-EXECUTION-INDEX.md
- [ ] Embedded to Qdrant (if searchable)

---

## 🔮 FUTURE-PROOFING

### For Next 15+ Phase Projects
- This structure is reusable verbatim
- Each project creates `/phases/` folder
- Sessions folder holds planning iterations
- Standards folder holds shared frameworks

### For Multi-Agent Coordination
- Redis provides real-time coordination
- Qdrant provides semantic discovery
- Phase folders provide consistent structure
- Cross-linking enables agent navigation

### For Knowledge Integration
- All findings feed to FAISS index
- All decisions feed to Redis
- All artifacts feed to Qdrant
- All progress feeds to memory_bank

---

## 📚 RELATED DOCUMENTS

- **COPILOT-CUSTOM-INSTRUCTIONS.md** - How Copilot should organize documents
- **AGENT-COORDINATION-PROTOCOLS.md** - How agents communicate
- **REDIS-QDRANT-FAISS-BOOST-SYSTEM.md** - How stack services enhance execution
- **EXECUTION-FRAMEWORK-AND-ORGANIZATION.md** - Overall project framework
- **DOCUMENTATION-STANDARDS.md** - Writing standards (Diataxis, etc.)

---

## 🔒 AGENT COORDINATION & CONCURRENT CREATION

### Naming Lock Pattern (Race Condition Prevention)
When multiple agents create documents simultaneously:

```
LOCK_FILE: /internal_docs/.document-locks/PHASE-{number}-{descriptor}.lock

When creating PHASE-X-{filename}.md:
1. Check if .lock file exists
2. If exists: Wait 1 second, retry (max 10 retries)
3. If free: Create .lock file (contains agent name + timestamp)
4. Create document
5. Delete .lock file

Redis tracking:
SET doc-creation-lock:{phase}:{descriptor} {agent_name} EX 300  # 5-min timeout
```

### Conflict Detection
If 2 agents create same document simultaneously:
```
SCENARIO: Copilot starts PHASE-1-EXECUTION-PLAN.md
          Cline also starts PHASE-1-EXECUTION-PLAN.md (2 sec later)

DETECTION:
  1. Redis shows lock: doc-creation-lock:1:execution-plan = "Copilot"
  2. Cline detects conflict
  3. Cline renames: PHASE-1-EXECUTION-PLAN-CLINE-DRAFT.md (wait for manual merge)
  
RESOLUTION:
  1. Copilot completes creation
  2. Copilot deletes lock
  3. User reviews both documents
  4. User decides: Keep Copilot version, Cline version, or merge
```

### Multi-Agent Document Collaboration
If the same document needs updates from multiple agents:

```
PATTERN: Create intermediate draft, then merge

Copilot (lead): Creates PHASE-X-EXECUTION-PLAN.md (main version)
Cline (analyst): Creates PHASE-X-EXECUTION-PLAN-CLINE-ANALYSIS.md (reference)
Both: Updates coordinated via Redis key "phase-{X}:review-ready"

When both complete:
  1. Copilot reads Cline analysis from separate file
  2. Copilot integrates insights into main document
  3. Cline's analysis archived as reference material
  4. All documents properly linked
```

---

## 📦 ARCHIVE LIFECYCLE & RETENTION POLICY

### Retention Timeline
```
Documents in /02-archived-phases/:
  └── Keep indefinitely by default
  └── But tag with archive date + reason
  
Exceptions (cleanup after):
  └── Duplicate drafts: Keep 1 latest version (archive rest after 7 days)
  └── Session-state working docs: Archive after 30 days (if not needed)
  └── Deprecated planning versions: Archive after 60 days
  
Never delete:
  ✅ Completed phase reports
  ✅ Decision documents (with reasoning)
  ✅ Research findings
  ✅ Integration documents
```

### Archiving Process
```
BEFORE ARCHIVING:
1. Verify document is superseded (not just old)
2. Create summary of why it's being archived
3. Check if any docs link to this (update links)
4. Store in Redis: doc-archive:{filename}
5. Add metadata: archive date, reason, linked documents

ARCHIVE STRUCTURE:
/internal_docs/02-archived-phases/
├── /2026-02/  (monthly folders)
│   ├── PHASE-1-EXECUTION-PLAN-v1.md (archived: superseded by v2)
│   ├── PHASE-1-EXECUTION-PLAN-v2.md (archived: superseded by final)
│   └── ARCHIVAL-SUMMARY.md (why each document archived)
```

---

## 🔐 ACCESS CONTROL & PERMISSION MATRIX

### Role-Based Document Access

| Document Type | Copilot | Cline | Claude | Humans | Notes |
|---|---|---|---|---|---|
| PHASE-X-EXECUTION-PLAN.md | RW (lead) | R (review) | - | R | Copilot decides, Cline analyzes |
| PHASE-X-TASKS-AND-DELIVERABLES.md | RW (lead) | RW (detail) | - | R | Collaborative breakdown |
| PHASE-X-PROGRESS-LOG.md | RW (summary) | RW (detail) | - | R | Both update, Copilot reconciles |
| PHASE-X-COMPLETION-REPORT.md | RW (lead) | R (input) | - | R | Copilot finalizes |
| /resources/* | RW (both) | RW (both) | - | R | Tools and templates |
| /ai-generated-insights/* | W (create) | RW (analysis) | - | R | Cline writes, Copilot reviews |
| MASTER-EXECUTION-INDEX.md | RW (only) | R | R | R | Copilot sole updater |
| DOCUMENT-STORAGE-STRATEGY.md | RW (only) | - | - | R | Copilot maintains standards |

**Legend**: RW=Read/Write, R=Read, W=Write, - = No access

### Enforcement
```
Copilot responsibility:
  - Reject any Cline write to "W (only)" documents
  - Verify all documents updated by correct agent
  - Move misplaced documents immediately
```

---

## 📊 AUDIT TRAIL & CHANGE LOGGING

### Dual-Channel Audit Logging

#### Channel 1: Git History (Permanent Record)
```
Every commit includes:
  - Author: Copilot / Cline / User
  - Timestamp: ISO 8601
  - Message: "Phase X: Updated PHASE-X-EXECUTION-PLAN.md (Copilot lead)"
  - Diff: Full text changes

Reviewed via: `git log --oneline -- internal_docs/01-strategic-planning/phases/`
```

#### Channel 2: Redis Audit Trail (Real-Time Tracking)
```redis
# Every document update recorded
ZADD doc-audit-log {timestamp} "{json_event}"

Example event:
{
  "timestamp": "2026-02-16T10:30:45Z",
  "document": "PHASE-1-EXECUTION-PLAN.md",
  "agent": "Copilot",
  "action": "update",
  "sections_changed": ["timeline", "success_criteria"],
  "confidence": "0.99",
  "reason": "Integrated Cline analysis findings"
}

Queried via: `ZRANGE doc-audit-log {start_time} {end_time}`
```

### Audit Trail Access
```python
# Copilot audits all changes
def get_audit_trail(phase_num, start_date, end_date):
    events = redis.zrangebyscore(
        "doc-audit-log",
        start_date.timestamp(),
        end_date.timestamp()
    )
    return json.loads(events)

# Example: "What changed in Phase 1 today?"
trail = get_audit_trail(1, today, today+1day)
for event in trail:
    print(f"{event['agent']} updated {event['document']}: {event['sections_changed']}")
```

---

## 🔗 PHASE INTERDEPENDENCIES

### Dependency Matrix (Research-Backed)
```
PHASE-0 (Pre-exec)
  ├─→ Blocks: All phases (must complete first)
  └─→ Duration: 90-120 min

PHASE-1 (Diagnostics) → PHASE-2 (Chainlit)
  ├─→ Dependency: Diagnostics output feeds into Chainlit build
  ├─→ Conflict type: Blocking (Phase 1 must complete for Phase 2)
  └─→ Parallel with: PHASE-6 (Docs can start after Phase 1 complete)

PHASE-2 (Chainlit) → PHASE-3 (Caddy)
  ├─→ Dependency: Chainlit running before Caddy routing
  ├─→ Conflict type: Blocking
  └─→ Status: Both under Track A

TRACK A (Ops) → TRACK B (Docs)
  ├─→ Dependency: Can start TRACK B after Phase 1 complete
  ├─→ Conflict type: Informational (Docs benefit from ops clarity)
  └─→ Recommended: Start Phase 6 when Phase 1 finishes

TRACK A (Ops) → TRACK C (Research)
  ├─→ Dependency: Can start Phase 9 only after Phase 5 complete
  ├─→ Conflict type: Blocking (needs operational baseline)
  └─→ Gate: Phase 3 checkpoint (14 hours into execution)

TRACK D (Knowledge) → ALL TRACKS
  ├─→ Dependency: Continuous, runs parallel
  ├─→ Conflict type: Integrative (consumes output from all phases)
  └─→ Frequency: Updates every 4-6 hours
```

### Blocking vs. Advisory Dependencies

| Phase | Blocks | Blocked By | Notes |
|---|---|---|---|
| 0 | All | None | Must run first |
| 1 | 2, 3, 4, 5 | 0 | Diagnostics required |
| 2 | 3, 4, 5 | 1 | Chainlit needs diagnostics |
| 2.5 | 3, 4 | 2 | Vikunja fix after Chainlit |
| 2.6 | 10 | 2 | License verification before models |
| 3 | 4, 5 | 2.5 | Routing needs Vikunja ready |
| 4 | 5 | 3 | Full stack test needs all infra |
| 5 | 6,7,8,9,12 | 4 | Integration test required before research |
| 6 | 12 | 5 | Can parallel with rest of Track A |
| 7 | 12 | 6 | Documents build on each other |
| 8 | 12 | 7 | Same |
| 9 | 11 | 5 | Research starts after ops stable |
| 10 | 11 | 9 | Model research depends on crawler |
| 11 | 12 | 10 | Agent bus audit after models |
| 12 | 14, 15 | All | Knowledge integration continuous |
| 13 | 14 | 5 | Security audit after ops |
| 14 | 15 | 13 | Cleanup after validations |
| 15 | - | 14 | Template docs last |
| 16 | - | All | Template for future (post-execution) |

### Dependency Violation Detection
```redis
# Track blocking dependencies
HSET phase-blocking:blockers
  "phase-2": ["phase-1"]  # Phase 2 blocked until Phase 1 done
  "phase-3": ["phase-2-5"]
  "phase-5": ["phase-4"]
  
# Alert if trying to start blocked phase
IF phase:2:state == "in-progress" AND phase:1:state != "complete":
  ALERT: "Blocking dependency violated! Phase 2 cannot start until Phase 1 complete"
```

---

## ⚠️ COMMON MISTAKES (What NOT to Do)

❌ Save documents to `/tmp/` or session-state working folders  
❌ Use timestamps in filenames (use folder hierarchy instead)  
❌ Create new categories without consulting strategy  
❌ Forget to update Redis/Qdrant after document creation  
❌ Create documents in root directory  
❌ Skip cross-linking between related docs  
❌ Archive files without documenting why  
❌ Create duplicate "FINAL" versions  
✅ Always follow the PHASE-X folder structure  
✅ Always index in appropriate stack services  
✅ Always update MASTER-EXECUTION-INDEX.md  
✅ Always include cross-links  

---

## 📋 IMPLEMENTATION ROADMAP

### Immediate (Before Phase 0)
- [ ] Create `/internal_docs/01-strategic-planning/phases/` folder structure
- [ ] Create PHASE-0/ subfolder
- [ ] Move PHASE-0-EXTENDED-DOCUMENTATION-AUDIT-PLAN.md to PHASE-0/
- [ ] Create PHASE-0/00-README-PHASE-0.md
- [ ] Create PHASE-0/resources/ subfolder
- [ ] Update all cross-links

### Before Phase 1
- [ ] Create /PHASE-1/ through /PHASE-16/ folder templates
- [ ] Create MASTER-EXECUTION-INDEX.md
- [ ] Embed all phase documents to Qdrant
- [ ] Populate Redis with phase state keys

### During Execution
- [ ] Agents follow protocols in this document
- [ ] All documents go in correct phase folders
- [ ] All resources indexed and cross-linked
- [ ] All progress tracked in /progress/ folders

### Post-Project
- [ ] This structure becomes template for future projects
- [ ] Document storage strategy proven and refined
- [ ] Agent coordination protocols validated
- [ ] Stack services boost system documented and reproducible

---

**Document Version**: 1.0  
**Status**: Active - All agents must follow this strategy  
**Enforcement**: See COPILOT-CUSTOM-INSTRUCTIONS.md for oversight
