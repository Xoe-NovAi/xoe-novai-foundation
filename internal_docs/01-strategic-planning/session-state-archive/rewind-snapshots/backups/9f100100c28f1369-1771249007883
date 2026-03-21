# Documentation Standards & Organization Procedures

**Purpose**: Define documentation standards maintained throughout all 15 phases  
**Scope**: When/where to create docs, naming, organization, archiving  
**Status**: ✅ ACTIVE  
**Date**: 2026-02-16 10:20 UTC  

---

## 📂 DOCUMENT LOCATION MATRIX

### ALWAYS In Project Structure
```
/home/arcana-novai/Documents/xnai-foundation/

internal_docs/00-project-standards/
├── Reusable templates
├── Standards documents  
├── Procedures (this folder)
├── EXECUTION-FRAMEWORK-AND-ORGANIZATION.md
└── COPILOT-CLINE-COORDINATION-PROCEDURES.md

internal_docs/01-strategic-planning/
├── sessions/02_16_2026_phase5_operationalization/
│   ├── MASTER-PLAN-v3.1.md ⭐ PRIMARY REFERENCE
│   ├── EXPANDED-PLAN.md (detailed tasks)
│   ├── PHASE-BY-PHASE-COORDINATION.md
│   ├── 00-15-PHASE-COMPLETE-INVENTORY.md
│   ├── T5-ANCIENT-GREEK-RESEARCH-REQUEST-FOR-CLAUDE.md
│   ├── [Phase completion reports during execution]
│   └── [Handoff documents between phases]
│
├── session-state-archive/
│   └── [Old session-state documents, archived]
│
└── research/
    └── [Supporting research documents]

internal_docs/03-claude-ai-context/
├── [All Claude-related materials]
├── CLAUDE-AI-DELIVERY-CHECKLIST.md
└── [6 other Claude context guides]

internal_docs/04-research-and-development/
├── Ancient-Greek-Models/ (Phase 10 deliverables)
├── Memory-Optimization/ (Phase 10 findings)
├── Security-Hardening/ (Phase 13 findings)
├── Agent-Performance/ (Phase 11 findings)
└── Knowledge-Integration/ (Phase 12 findings)

internal_docs/02-archived-phases/
└── [Previous phase archives - organized by category]
```

### NEVER In Session-State (Except plan.md)
```
❌ Planning documents
❌ Phase deliverables
❌ Execution guides
❌ Research materials
❌ Claude context materials
❌ Phase reports
❌ Handoff documents

✅ ONLY in session-state:
├── plan.md (session tracking)
├── checkpoints/ (session history)
└── rewind-snapshots/ (recovery data)
```

---

## 📝 DOCUMENT NAMING CONVENTIONS

### Phase Completion Reports
```
Format: PHASE-[N]-COMPLETION-REPORT-[DATE].md
Example: PHASE-1-COMPLETION-REPORT-2026-02-16.md
Location: /internal_docs/01-strategic-planning/sessions/02_16_2026_phase5_operationalization/
```

### Handoff Documents
```
Format: PHASE-[N]-TO-[N+1]-HANDOFF-[DATE].md
Example: PHASE-5-TO-6-HANDOFF-2026-02-16.md
Location: /internal_docs/01-strategic-planning/sessions/02_16_2026_phase5_operationalization/
```

### Phase Findings/Research
```
Format: PHASE-[N]-[CATEGORY]-FINDINGS-[DATE].md
Example: PHASE-10-MODEL-SELECTION-FINDINGS-2026-02-16.md
Location: /internal_docs/04-research-and-development/[Category]/
```

### Checkpoint Reports
```
Format: CHECKPOINT-[N]-[NAME]-[DATE].md
Example: CHECKPOINT-1-OPERATIONS-VERIFIED-2026-02-16.md
Location: /home/arcana-novai/.copilot/session-state/.../checkpoints/
```

### Integration Notes
```
Format: PHASE-12-INTEGRATION-[CATEGORY]-[DATE].md
Example: PHASE-12-INTEGRATION-RESEARCH-FINDINGS-2026-02-16.md
Location: /internal_docs/04-research-and-development/Knowledge-Integration/
```

---

## 📋 DOCUMENT CREATION CHECKLIST

### Before Creating Any Document

**Verify It Should Be Created**:
- [ ] Is this a deliverable from the phase plan? (YES = create)
- [ ] Is this a findings/research document? (YES = create)
- [ ] Is this supporting documentation? (Evaluate → create if necessary)
- [ ] Is this a session-state only item? (NO = create in project structure)

**Determine Correct Location**:
- [ ] Is this a planning/coordination doc? → `/01-strategic-planning/sessions/.../`
- [ ] Is this a phase deliverable? → `/04-research-and-development/[Phase]/`
- [ ] Is this a standards/procedures doc? → `/00-project-standards/`
- [ ] Is this an archived doc? → `/02-archived-phases/[Category]/`
- [ ] Is this Claude-related? → `/03-claude-ai-context/`

**Apply Naming Convention**:
- [ ] Use format: `PHASE-[N]-[PURPOSE]-[DATE].md`
- [ ] Include date in format: YYYY-MM-DD
- [ ] Make name descriptive and searchable
- [ ] No spaces in filenames (use hyphens)

**Include Required Elements**:
- [ ] Title (matching filename)
- [ ] Purpose statement
- [ ] Date created
- [ ] Status (ACTIVE, COMPLETE, ARCHIVED)
- [ ] Cross-reference to MASTER-PLAN-v3.1.md
- [ ] Success criteria (if applicable)

**Link to Broader Context**:
- [ ] Reference phase number(s)
- [ ] Reference section in MASTER-PLAN-v3.1.md
- [ ] Reference section in EXPANDED-PLAN.md
- [ ] Link to related documents

---

## 🗂️ ORGANIZATION DURING EXECUTION

### Daily (While Phase Running)
```
✅ DO:
  - Create deliverables in correct project folder
  - Update plan.md with daily progress
  - Maintain cross-references to MASTER-PLAN
  - Keep session-state clean (plan.md only)

❌ DON'T:
  - Create documents in session-state
  - Leave documents scattered/unorganized
  - Forget to update plan.md
  - Create ambiguous filenames
```

### Phase Completion (End of Each Phase)
```
✅ DO:
  - Create phase completion report
  - Organize all deliverables in project structure
  - Update plan.md with completion status
  - Create handoff document (if applicable)
  - Verify all cross-references

❌ DON'T:
  - Leave deliverables scattered
  - Forget to document findings
  - Leave plan.md out of date
  - Create phase docs in session-state
```

### Checkpoint Gates (Hours 5.6, 9, 14, 18.5)
```
✅ DO:
  - Review all documents created so far
  - Verify organization standards met
  - Archive superseded documents if any
  - Update master inventory
  - Create checkpoint report

❌ DON'T:
  - Allow organization to slide
  - Leave old versions around
  - Forget to update inventories
  - Create session-state clutter
```

---

## 📊 EXAMPLE: PROPER PHASE ORGANIZATION

### Phase 1 Complete Example
```
/home/arcana-novai/Documents/xnai-foundation/

Project Structure Shows:

internal_docs/01-strategic-planning/sessions/02_16_2026_phase5_operationalization/
├── PHASE-1-COMPLETION-REPORT-2026-02-16.md
├── PHASE-1-TO-2-HANDOFF-2026-02-16.md
├── PHASE-1-DIAGNOSTICS-FINDINGS-2026-02-16.md

internal_docs/04-research-and-development/
└── Agent-Performance/
    ├── PHASE-1-SERVICE-BASELINE-METRICS-2026-02-16.md

Session-State Shows:

/home/arcana-novai/.copilot/session-state/392fed92-9f81-4db6-afe4-8729d6f28e1b/
├── plan.md [UPDATED: Phase 1 complete, Phase 2 starting]
└── checkpoints/
    └── CHECKPOINT-1-OPERATIONS-PHASE-1-2026-02-16.md

✅ RESULT: Clear, organized, discoverable
```

---

## 🔄 ARCHIVING PROCEDURES

### When to Archive
- Old planning documents (superseded by newer versions)
- Completed phase reports (after Phase 12 integration)
- Superseded research documents (if new research replaces old)
- Test/draft documents (not final deliverables)

### Where to Archive
```
/internal_docs/02-archived-phases/
├── phase-4.2-completion/ (old phases)
├── phase-4.2.6-tasks/ (old phase tasks)
├── test-and-research/ (test documents)
├── legacy-planning/ (old planning)
└── [Future: phase-5-sessions/ for old sessions]
```

### Archiving Process
1. Create `/02-archived-phases/[category]/` if needed
2. Move document with original name + `-ARCHIVED-DATE.md` suffix
3. Create `.index.md` listing all archived items
4. Update master inventory
5. Verify no broken references

### Archive Index Template
```
# Archive Index - [Category]

**Purpose**: Documents archived from [phase/category]  
**Archive Date**: [Date]  
**Count**: [N] documents

## Contents
| Document | Date | Status |
|----------|------|--------|
| [Name] | [Date] | [Original Status] |
```

---

## ✅ COMPLIANCE CHECKLIST

### Documentation Standards
- [ ] All deliverables in project structure (NOT session-state)
- [ ] All documents named per convention
- [ ] All documents dated
- [ ] All documents linked to MASTER-PLAN
- [ ] All documents organized in proper folders
- [ ] All cross-references verified

### Organization Excellence
- [ ] Session-state contains ONLY plan.md + checkpoints/ + rewind-snapshots/
- [ ] No scattered/orphaned documents
- [ ] All old versions archived
- [ ] Master inventory current
- [ ] All folder structures as specified

### Phase Completion
- [ ] Phase deliverables created
- [ ] Phase completion report created
- [ ] Handoff document created (if applicable)
- [ ] plan.md updated
- [ ] Checkpoint created in checkpoints/
- [ ] All documents in correct locations
- [ ] All cross-references verified
- [ ] Ready for next phase

---

## 🎯 SUCCESS CRITERIA

### Documentation Excellence
- ✅ All documents in correct locations
- ✅ Clear, discoverable naming conventions
- ✅ All cross-references working
- ✅ No session-state pollution
- ✅ Organized by phase/category/type

### Maintained Through All 15 Phases
- ✅ Each phase documents deliverables properly
- ✅ Each handoff clear and complete
- ✅ Each checkpoint verified organization
- ✅ Final state clean and organized
- ✅ Templates documented for reuse

---

**Status**: ✅ STANDARDS ACTIVE  
**For**: Copilot CLI & Cline Advanced Development  
**Applies To**: All 15 phases of execution  
**Reference**: PHASE-BY-PHASE-COORDINATION.md (procedures), MASTER-PLAN-v3.1.md (structure)  

---

*Standards ensure documentation excellence and organization maintained through all 15 phases of execution.*
