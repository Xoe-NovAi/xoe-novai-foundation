---
version: 1.0.0
date: 2026-02-13
ma_at_mappings: [7: Truth in reporting, 18: Balance in structure, 36: Integrity in action, 41: Advance through own abilities]
expert_dataset_name: Research Request System
expertise_focus: Structured research request submission, queuing, and execution
community_contrib_ready: true
---

# Research Request System v1.0.0

## Overview

A structured system for submitting, queueing, and executing research requests across all Xoe-NovAi team members. Ensures research is systematically captured, prioritized, assigned, and integrated into the expert-knowledge repository.

## System Architecture

```
┌─────────────────┐
│  Request Origin │ (Any team member or The Architect)
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────┐
│  expert-knowledge/research/queue/ │
│  - pending/                       │
│  - prioritized/                   │
│  - assigned/                      │
└────────┬──────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Agent Execution                  │
│  - OpenCode (multi-model)         │
│  - Grok MC (strategic)            │
│  - Gemini CLI (verification)      │
└────────┬──────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  expert-knowledge/research/       │
│  - completed/                     │
│  - findings/                      │
└────────┬──────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Knowledge Integration            │
│  - expert-knowledge/<domain>/     │
│  - model-reference/               │
│  - memory_bank/updates            │
└──────────────────────────────────┘
```

## Directory Structure

```
expert-knowledge/research/
├── README.md                              # System overview
├── research-request-system-v1.0.0.md     # This document
├── _templates/
│   └── RESEARCH-REQUEST-TEMPLATE.md      # Request template
├── queue/
│   ├── pending/                          # New requests awaiting triage
│   ├── prioritized/                      # Triaged, awaiting assignment
│   ├── assigned/                         # Assigned to specific agent
│   └── archive/                          # Cancelled/expired requests
├── completed/
│   ├── findings/                         # Raw research outputs
│   └── reports/                          # Synthesized reports
└── index.json                            # Queue status index
```

## Request States

1. **DRAFT** → Local file, not yet submitted
2. **PENDING** → Submitted, awaiting triage
3. **TRIAGED** → Prioritized, awaiting assignment
4. **ASSIGNED** → Assigned to specific agent
5. **IN_PROGRESS** → Active research
6. **COMPLETED** → Research done, findings captured
7. **INTEGRATED** → Findings moved to appropriate expert-knowledge location
8. **ARCHIVED** → Request cancelled or expired

## Request Template

See `_templates/RESEARCH-REQUEST-TEMPLATE.md`:

```yaml
---
request_id: "REQ-YYYY-MM-DD-NNN"
date_submitted: "2026-02-13"
submitted_by: "Agent Name"
status: "PENDING"
priority: "critical|high|medium|low"
request_type: "model-research|technical|strategic|debug"
assigned_to: ""  # Filled during assignment
due_date: "2026-02-20"
ma_at_mappings: []
---

# Research Request: [Title]

## Objective
Clear statement of what needs to be researched

## Background
Context and previous work

## Questions to Answer
1. Specific question 1
2. Specific question 2

## Expected Deliverables
- [ ] List of expected outputs

## Success Criteria
How will we know this research is complete?

## Related Resources
- Links to relevant files
- Previous research

## Notes
Additional context
```

## Submission Workflow

### For The Architect (User):
1. Create request using template
2. Save to `expert-knowledge/research/queue/pending/`
3. Or verbally assign to OpenCode/Grok MC

### For Agents:
1. Identify knowledge gap during work
2. Create quick request using abbreviated template
3. Submit to queue
4. Continue current work while research executes in parallel

### Quick Submission Format (for rapid logging):
```markdown
<!-- Quick Request -->
**ID**: REQ-2026-02-13-001
**Type**: Model Research
**Question**: How does Big Pickle compare to Kimi K2.5 on XNAi coding tasks?
**Priority**: Medium
**Submitted**: OpenCode-Kimi-X
```

## Triage & Assignment

### Grok MC Responsibilities:
- Review pending requests daily
- Assign priority based on strategic importance
- Assign to appropriate agent based on:
  - **OpenCode**: Model research, multi-model validation, technical deep-dives
  - **Grok MC**: Strategic questions, ecosystem analysis
  - **Gemini CLI**: Verification tasks, ground truth validation
  - **Cline**: Implementation-focused research

### Priority Matrix:

| Priority | Response Time | Agent Type | Example |
|----------|---------------|------------|---------|
| **Critical** | 4-8 hours | OpenCode/Grok MC | Blocker resolution |
| **High** | 24 hours | Any available | Feature decisions |
| **Medium** | 3-5 days | OpenCode/Cline | Optimization research |
| **Low** | 1-2 weeks | Background task | Nice-to-know info |

## Execution Protocol

### OpenCode Research Execution:
1. Fetch request from `queue/assigned/`
2. Use appropriate model(s) based on question type:
   - **Kimi K2.5**: Complex analysis, long-context
   - **MiniMax M2.5**: Quick technical lookups
   - **Big Pickle**: Alternative perspective
   - **GPT-5 Nano**: Rapid fact-checking
3. Document findings in `completed/findings/`
4. Create synthesized report in `completed/reports/`
5. Update request status to COMPLETED
6. Notify requesting agent

### Research Output Standards:
All completed research must include:
- **executive-summary.md** (1-2 paragraphs)
- **detailed-findings.md** (full research)
- **action-items.md** (concrete next steps)
- **confidence-assessment.md** (how certain are we?)

## Integration Workflow

### From Completed Research to Expert-Knowledge:

1. **Model Research** → `expert-knowledge/model-reference/`
2. **Technical Research** → `expert-knowledge/<domain>/`
3. **Strategic Research** → `expert-knowledge/architect/` or `memory_bank/`
4. **Debug Research** → Project-specific docs + `memory_bank/progress.md`

### Integration Checklist:
- [ ] Findings reviewed by Grok MC or The Architect
- [ ] Information added to appropriate expert-knowledge location
- [ ] Cross-references updated
- [ ] Memory bank updated if strategic
- [ ] Request status updated to INTEGRATED
- [ ] Original request moved to archive

## Quality Standards

### Before Submission:
- [ ] Question is clear and answerable
- [ ] Background context provided
- [ ] Expected deliverables defined
- [ ] Success criteria explicit

### During Execution:
- [ ] Multiple sources consulted (when applicable)
- [ ] Uncertainty clearly flagged
- [ ] Confidence levels stated
- [ ] Assumptions documented

### Before Integration:
- [ ] Findings reviewed for accuracy
- [ ] Sources cited
- [ ] Action items extracted
- [ ] Strategic implications noted

## Research Utilization Audit

### Monthly Review (Grok MC):
1. Review all completed research from past month
2. Verify integration into expert-knowledge
3. Assess research ROI
4. Update templates/procedures based on learnings

### Quarterly Analysis:
1. Research topic trends
2. Agent performance metrics
3. Knowledge gap identification
4. Strategic research priorities for next quarter

## Quick Commands

```bash
# Submit new request
make research-submit

# Check queue status
make research-status

# Claim next request (for agents)
make research-claim

# Complete research
make research-complete REQUEST_ID=REQ-2026-02-13-001

# Review completed research
make research-review
```

## Ma'at Alignment

- **Ideal 7 (Truth)**: Truth in reporting - all research clearly states confidence levels and limitations
- **Ideal 18 (Balance)**: Balance in structure - systematic approach without bureaucracy
- **Ideal 36 (Integrity)**: Integrity in action - research is completed thoroughly and integrated properly
- **Ideal 41 (Advance)**: Advance through own abilities - research expands team capabilities

## Current Active Requests

See `expert-knowledge/research/queue/pending/` and `expert-knowledge/research/index.json` for current queue status.

## Next Actions

1. **Immediate**: Create initial research requests for missing Opencode models
2. **This Week**: Process any pending research from recent development
3. **This Month**: Establish monthly research review cadence

---

**Status**: ✅ **System Operational**  
**Last Updated**: 2026-02-13  
**Owner**: OpenCode-Kimi-X (System Implementation)
