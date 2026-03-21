# Pre-Execution Template: Strategic Planning with Copilot & Claude.ai

**Purpose**: Reusable template for large, complex projects requiring deep research and architectural validation.

**Recommended For**: Projects with:
- 10+ phases / 15+ hours effort
- Multiple technical constraints  
- Architectural decisions with security/performance implications
- Need for cross-functional team coordination
- Requirement for continuous validation

**This Template Covers**: The complete workflow from requirements → planning → research → execution

---

## OVERVIEW: The XNAi Foundation Workflow

This template was developed and validated through the XNAi Foundation Phase 5+ operationalization project (Feb 16, 2026).

**What This Template Provides**:
1. ✅ Requirements gathering methodology
2. ✅ Codebase analysis framework  
3. ✅ Initial plan creation process
4. ✅ Architectural review with Claude.ai
5. ✅ Research integration methodology
6. ✅ Execution authorization gates
7. ✅ Multi-track parallel execution
8. ✅ Checkpoint validation framework
9. ✅ Lessons learned capture
10. ✅ Reusable components for next projects

**Key Benefit**: 40-50% faster execution through upfront planning and research integration.

---

## PART 1: INITIAL REQUIREMENTS GATHERING

### Step 1.1: Define High-Level Goals
**User provides**: 2-3 sentence problem statement

**Copilot asks clarifying questions**:
```
Using ask_user tool, clarify:
1. What's the primary success metric?
2. What are the hard constraints (memory, time, security, compliance)?
3. Who are the stakeholders?
4. What's the timeline for completion?
5. Are there existing systems to integrate with?
```

**Document**: Create REQUIREMENTS.md with user responses

### Step 1.2: Identify Assumptions
**Copilot documents**:
```
- Technical assumptions (architecture, frameworks, deployment)
- Business assumptions (budget, resources, priorities)
- Constraint assumptions (hardware, licensing, compliance)
- Risk assumptions (what might go wrong?)
```

**Validation**: Ask user to confirm assumptions or correct misunderstandings

---

## PART 2: CODEBASE ANALYSIS & DEEP EXPLORATION

### Step 2.1: Automated Code Structure Analysis
**Copilot performs** (30-60 minutes):
```
Deliverables from this step:
- Service architecture mapping
- Dependency graph visualization  
- Data flow documentation
- Technology stack inventory
- Configuration audit
- Constraint verification (memory, security, APIs)
```

**Tools Used**:
- `grep` for code search (patterns, imports, function definitions)
- `glob` for file discovery (by extension, naming patterns)
- `task explore` for multi-file analysis
- `view` for critical files

**Output**: CODEBASE-ANALYSIS.md (500-1000 lines)

### Step 2.2: Online Research (if needed)
**Copilot researches** (30-90 minutes):
```
Research topics:
- Best practices for chosen frameworks
- Deployment patterns for target environment  
- Security hardening for use case
- Performance optimization techniques
- Compatibility matrices (libraries, versions)
```

**Output**: RESEARCH-FINDINGS.md with sources and relevance

### Step 2.3: Gap Analysis
**Copilot identifies**:
```
- Knowledge gaps requiring external research
- Dependency challenges
- Technical risks
- Open architectural questions
```

**Output**: KNOWLEDGE-GAPS.md (for Claude.ai research)

---

## PART 3: INITIAL PLAN CREATION

### Step 3.1: Phase Definition
**Copilot creates** (90-120 minutes):
```yaml
For each phase:
  - Name: Clear, actionable name
  - Duration: Estimated hours  
  - Dependencies: [other phases]
  - Blockers: [known risks]
  - Owner: Agent (Copilot, Cline, Gemini, Grok)

Organize into:
  - Tracks: Parallel execution groups
  - Sequences: Dependencies between tracks
  - Critical path: Blocking tasks first
```

**Approach**:
1. Identify critical path (blocking tasks)
2. Find parallelizable work
3. Sequence for dependency management
4. Estimate realistically (add 20% buffer)

**Output**: PHASE-BREAKDOWN.md with all phases, tasks, estimates

### Step 3.2: Task Breakdown
**Copilot details**:
```
For each phase:
- 3-8 specific tasks
- Technical commands/code samples
- Success criteria (how do we know it's done?)
- Estimated duration (30-120 minutes)
- Risk mitigation (what if it fails?)
```

**Output**: TASK-BREAKDOWN.md (detailed execution checklist)

### Step 3.3: Create Draft Plan Document
**Copilot compiles comprehensive plan**:
```
DRAFT-PLAN.md should contain:
├─ Executive Summary
├─ Phase Overview (table)
├─ Track Definitions  
├─ Detailed Phase Specifications
├─ Task Breakdown
├─ Risk Mitigation
├─ Success Criteria
└─ Timeline Estimate
```

**Target Length**: 40-80 pages of technical detail

---

## PART 4: ARCHITECTURAL REVIEW (Claude.ai)

### Step 4.1: Submit Plan for Review
**Copilot sends to Claude.ai**:
```
Materials provided:
- DRAFT-PLAN.md (primary document)
- CODEBASE-ANALYSIS.md (context)
- KNOWLEDGE-GAPS.md (research needed)
- REQUIREMENTS.md (user goals)
- Any relevant code/config files
```

**Format**: Upload files directly (Claude.ai is not code-aware from URLs)

### Step 4.2: Claude.ai Performs Architectural Review
**Claude reviews** (45-90 minutes):
```
Evaluation criteria:
1. Constraint Alignment
   - Does plan respect all constraints?
   - Are hardware limits considered?
   - Is security architecture sound?

2. Technical Feasibility
   - Are implementation approaches correct?
   - Are estimates realistic?
   - Are dependencies properly sequenced?

3. Gap Identification
   - What critical knowledge is missing?
   - What research must happen before implementation?
   - Are there architectural risks?

4. Enhancement Opportunities
   - Can this be done better?
   - Are there cost/time/quality tradeoffs?
   - What's the optimal approach?

5. Security & Compliance
   - Does plan maintain sovereignty?
   - Are security best practices followed?
   - Is compliance strategy clear?
```

**Deliverable**: CLAUDE-REVIEW.md with:
- Executive assessment
- Gap analysis (3-5 critical items)
- Enhancement recommendations
- New phases to add/modify
- Research guides (if needed)

### Step 4.3: Claude Provides Research Guides
**If knowledge gaps identified, Claude creates** (0-4 hours):
```
Research Guides format (3-10 pages each):
1. Tactical implementation guides
2. Architecture decision frameworks
3. Benchmark/comparison matrices
4. Best practices for specific technologies
5. Risk mitigation strategies

Example topics from XNAi:
- "mmap() for Large Model Loading"
- "Zero-Trust Redis ACL Design"
- "Disaster Recovery Architecture"
- "Compliance Framework for Sovereign Systems"
```

**These become**: Expert knowledge to integrate into plan

---

## PART 5: RESEARCH INTEGRATION

### Step 5.1: Incorporate Claude Feedback
**Copilot updates plan**:
```
For each gap Claude identified:
1. Add new phases (if needed)
2. Enhance existing phases with Claude's research
3. Update task breakdown with refined approaches
4. Adjust timeline estimate (+5-15% typical)
5. Document decision rationale
```

**Deliverable**: INTEGRATED-PLAN.md (updated version of draft)

### Step 5.2: Update Knowledge Management
**Copilot creates**:
```
expert-knowledge/
├─ [topic-1]/
│  ├─ summary.md (Claude's research)
│  └─ implementation-guide.md
├─ [topic-2]/
│  └─ ...
└─ INDEX.md (cross-references)
```

**Link to**: memory_bank/RESEARCH_INDEX.md

### Step 5.3: Validate Technical Soundness
**Copilot confirms**:
```
✓ All constraints satisfied
✓ Dependencies properly sequenced
✓ Task estimates verified
✓ Success criteria measurable
✓ Risk mitigation strategies identified
✓ Artifact storage standards met
✓ Documentation templates ready
```

---

## PART 6: EXECUTION AUTHORIZATION

### Step 6.1: Present Final Plan to User
**Copilot provides**:
```
Documents to review:
- INTEGRATED-PLAN.md (main document)
- QUICK-START.md (5-minute overview)
- EXECUTION-SUMMARY.md (timeline, metrics)
- README.md (file navigation)
```

### Step 6.2: Clarify Checkpoint Gates
**Confirm with user**:
```
Define pause-and-review points:

Example gates:
- After Phase 5: Is operational foundation stable?
- After Phase 8: Is documentation complete?
- After Phase 11: Are security & research complete?
- After Phase 15: Is everything production-ready?

At each gate:
- Claude.ai provides checkpoint review
- User approves proceeding or requests changes
- Copilot documents decisions
```

### Step 6.3: Confirm Agent Delegation
**Define roles**:
```
Copilot:      Orchestration, critical operations, validation
Cline:        Heavy lifting (documentation, research, complex coding)
Gemini/Grok:  Specialized research (if needed)
Claude.ai:    Architectural review, decision validation, optimization

Process:
1. Copilot identifies task
2. Assigns to appropriate agent
3. Agent executes independently
4. Reports back to Copilot
5. Copilot validates and integrates
```

### Step 6.4: Authorize Artifact Storage
**Confirm policy**:
```
✓ All artifacts in project folders (NOT /tmp)
✓ Session-state for planning docs (valid)
✓ Project root for operational outputs
✓ memory_bank/ for knowledge
✓ expert-knowledge/ for research
✓ internal_docs/ for strategic planning

Example final structure:
project_root/
├─ internal_docs/
│  ├─ 00-project-standards/
│  │  └─ PRE-EXECUTION-TEMPLATE-v1.0.md (THIS DOCUMENT)
│  └─ 01-strategic-planning/
│     └─ sessions/[date]_[project]/
│        ├─ INTEGRATED-PLAN.md
│        ├─ claude-research-[topic]/
│        └─ execution-artifacts/
├─ memory_bank/ ← Updated with research
├─ expert-knowledge/ ← Linked to research
└─ logs/ ← Execution outputs
```

---

## PART 7: EXECUTION FRAMEWORK

### Step 7.1: Define Execution Tracks
**Organize as**:
```
Track A: Critical path (sequential, must complete first)
         └─ Phases that block all other work

Track B: Documentation (parallel with A, independent)
         └─ Can start immediately, independent of operations

Track C: Research (after A complete, can start early)
         └─ Depends on operational foundation from Track A

Track D: Knowledge sync (continuous, all phases)
         └─ Updates memory_bank as each track completes

Track E: Cleanup/standardization (concurrent with A/B)
         └─ Project organization, best practices
```

**Benefits**:
- Maximize parallelization
- Minimize blocking
- Enable independent agent assignment
- Improve overall timeline (40-50% time savings)

### Step 7.2: Create Execution Checklist
**For each phase, document**:
```
Phase: [Name]
├─ Start Condition: [what must be complete before]
├─ Tasks
│  ├─ Task 1: [specific action]
│  ├─ Task 2: [specific action]
│  └─ Task N: [specific action]
├─ Success Criteria: [how do we validate completion?]
├─ Artifacts: [outputs, where stored]
├─ Rollback: [what to do if phase fails]
└─ Checkpoint: [validation before proceeding]
```

### Step 7.3: Establish Monitoring & Checkpoints
**Define**:
```
Checkpoint Gates (pause-and-review points):
├─ After Track A: Operational status check (Claude.ai review)
├─ After Track B: Documentation quality check (Claude.ai review)
├─ After Track C: Research & security check (Claude.ai review)
└─ Final: Production readiness check (Claude.ai sign-off)

Monitoring (continuous):
- Phase progress tracking
- Task completion status
- Blocker identification
- Timeline drift detection
- Quality metric tracking
```

---

## PART 8: EXECUTION DETAILS

### Step 8.1: Execute Track A (Critical Operations)
**Copilot leads**:
```
Sequential execution of blocking phases:
1. Phase 1-5 executed in order
2. Each phase dependent on previous success
3. Test after each phase
4. Fix issues immediately

Status reporting:
- After each phase: Copilot → User
- Every 2 hours: Copilot → Claude.ai
- Blockers immediately escalated
```

### Step 8.2: Execute Track B (Documentation, Parallel)
**Cline leads**:
```
Parallel with Track A Phase 1:
1. Start Phase 6 immediately
2. Independent of operations track
3. Reference architecture from Phase 1 as it completes
4. Deliver complete docs by end of Track A

Coordination:
- Weekly sync with Copilot
- Access to Phase 1-5 outputs
- Update docs based on actual implementation
```

### Step 8.3: Execute Track C (Research, After A Complete)
**Cline + Claude leads**:
```
After Phase 5 operational validation:
1. Phase 9-11 research tasks
2. Cline execution, Claude.ai guidance
3. Integrate findings into expert-knowledge
4. Update memory_bank with discoveries
```

### Step 8.4: Execute Track D (Knowledge Sync, Continuous)
**Copilot + Cline**:
```
Ongoing throughout execution:
1. After each track completes: Update memory_bank
2. Link expert-knowledge to implementations
3. Update OPERATIONS.md with new procedures
4. Archive old/deprecated knowledge
```

---

## PART 9: CHECKPOINT REVIEWS

### Checkpoint 1: After Track A (Operational Phase)
**Deliverables to Claude.ai**:
```
- Service health report
- Performance baselines
- Security audit summary
- Memory profiling data
```

**Claude.ai validates**:
```
✓ All services operational?
✓ Performance targets met?
✓ Security baseline established?
✓ Safe to proceed to Track C?
```

**Possible Outcomes**:
- ✅ Approved: Proceed to research phase
- ⚠️ Conditional: Fix specific items first
- ❌ Blocked: Major issues require redesign

### Checkpoint 2-4: Similar Validation Gates
(See full plan for details on each checkpoint)

---

## PART 10: DOCUMENTATION & LESSONS LEARNED

### Step 10.1: Create Project Archive
**Organize**:
```
internal_docs/strategic-planning/sessions/
└─ [date]_[project-name]/
   ├─ 00-INTEGRATED-PLAN.md (primary reference)
   ├─ 01-INITIAL-PLAN.md (draft)
   ├─ 02-CLAUDE-FEEDBACK.md (review results)
   ├─ 03-RESEARCH-GUIDES/ (Claude's research)
   ├─ 04-EXECUTION-LOGS/ (phase completion records)
   ├─ 05-CHECKPOINT-REVIEWS/ (Claude.ai review notes)
   └─ 06-LESSONS-LEARNED.md (post-mortem)
```

### Step 10.2: Capture Lessons Learned
**Document**:
```
For Each Phase:
- What went well?
- What could have been better?
- Were estimates accurate?
- Did dependencies work as planned?
- What surprised us?
- What would we do differently?

Overall Project:
- Was the planning approach effective?
- Did Claude.ai feedback significantly improve the plan?
- Were agent assignments optimal?
- How accurate was the timeline?
- Should we repeat this process for future projects?
```

### Step 10.3: Update Template
**Based on this project's lessons**:
```
1. What worked well → Keep in template
2. What needs improvement → Update template
3. New insights → Add to template
4. Better estimates → Update durations
5. New decision frameworks → Add to template
```

---

## QUICK REFERENCE: WHEN TO USE THIS TEMPLATE

### ✅ GOOD USE CASES
- Projects with 10+ phases / 15+ hours
- Architectural decisions with long-term impact
- Systems with security or compliance requirements
- Complex technical integrations
- Multi-agent team coordination needed
- Continuous research/learning needed

### ❌ POOR USE CASES
- Simple bug fixes (<2 hours)
- Routine maintenance
- Well-defined problems (no research needed)
- Single-agent work (no coordination)
- No architectural decisions needed

### 🔄 HYBRID APPROACH
For projects 5-10 hours:
1. Skip full Checkpoint Reviews
2. Single end-of-project validation from Claude.ai
3. Simplified phase breakdown (3-4 phases vs. 15)
4. Still use track-based parallelization

---

## TEMPLATE USAGE CHECKLIST

Before starting a new large project:
```
Planning Phase Setup:
- [ ] Read this entire template (30 min)
- [ ] Gather high-level requirements (1 hour)
- [ ] Perform codebase analysis (2-4 hours)
- [ ] Create draft plan (2-3 hours)
- [ ] Submit to Claude.ai review (0.5 hours)
- [ ] Integrate feedback (1-2 hours)
- [ ] Finalize execution plan (1 hour)
- [ ] Obtain user approval (0.5 hour)
- [ ] Begin execution

Total Planning Time: 8-14 hours
(Typically 10-20% of total project)

Expected Benefits:
- 40-50% faster execution
- Fewer blocking surprises
- Better team coordination
- Documented decision rationale
- Reusable templates for next project
```

---

**Version**: 1.0  
**Created**: 2026-02-16  
**Validated On**: XNAi Foundation Phase 5+ operationalization  
**Recommended For**: Projects 15-40 hours, complex architecture, security/research focus

**For Next Project**: Copy this template, follow Parts 1-10 sequentially, adapt components as needed.
