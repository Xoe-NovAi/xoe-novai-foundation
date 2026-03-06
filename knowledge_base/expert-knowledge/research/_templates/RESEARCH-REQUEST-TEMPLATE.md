---
version: 1.0.0
date: 2026-02-13
---

# Research Request Template

Use this template to submit research requests to the Xoe-NovAi research queue.

## Quick Submission (for rapid logging)

If you need to quickly log a research need without full details:

```markdown
<!-- Quick Request -->
**ID**: REQ-2026-02-13-XXX
**Type**: [model-research|technical|strategic|debug]
**Question**: [Single clear question]
**Priority**: [critical|high|medium|low]
**Submitted**: [Your name]
**Context**: [1-2 sentences of background]
```

Save to: `expert-knowledge/research/queue/pending/quick-req-YYYYMMDD-XXX.md`

## Full Template (for comprehensive requests)

Copy the YAML frontmatter and sections below into a new file:

```yaml
---
request_id: "REQ-2026-02-13-XXX"  # Will be assigned by system
date_submitted: "2026-02-13"
submitted_by: "Your Name"
status: "PENDING"
priority: "critical|high|medium|low"
request_type: "model-research|technical|strategic|debug|comparison"
assigned_to: ""  # To be filled by Grok MC
due_date: "2026-02-20"
ma_at_mappings: []
related_requests: []  # Link to related REQ-IDs
tags: []
---
```

# Research Request: [Clear, Descriptive Title]

## 1. Objective
**What do we need to know?**

One or two sentences clearly stating the research goal.

## 2. Background & Context
**Why do we need this?**

- Current situation
- Previous work or decisions
- What's blocking progress
- Strategic importance

## 3. Research Questions
**What specific questions need answers?**

1. Primary question
2. Secondary question
3. Tertiary question (if applicable)

## 4. Expected Deliverables
**What will the output look like?**

- [ ] Executive summary (1-2 paragraphs)
- [ ] Detailed findings document
- [ ] Comparison/analysis tables
- [ ] Code examples (if applicable)
- [ ] Action items with owners
- [ ] Confidence assessment

## 5. Success Criteria
**How will we know this is complete?**

Specific, measurable outcomes that indicate success.

## 6. Scope & Constraints
**What's in scope? What's out of scope?**

### In Scope:
- Item 1
- Item 2

### Out of Scope:
- Item 1
- Item 2

### Constraints:
- Time limit
- Resource limits
- Must work within XNAi stack constraints

## 7. Related Resources
**Where should the researcher start?**

### Internal Resources:
- `memory_bank/file.md` - Description
- `expert-knowledge/domain/file.md` - Description
- `docs/path/to/doc.md` - Description

### External Resources:
- [Link](url) - Description
- [Documentation](url) - Description

### Previous Research:
- REQ-YYYY-MM-DD-XXX - Summary of findings

## 8. Suggested Approach
**How might this be researched? (Optional)**

If you have ideas on methodology, include them here. Otherwise, leave for assigned agent to determine.

## 9. Urgency & Impact

### If Completed Successfully:
- **Immediate Impact**: What unblocks?
- **Strategic Impact**: How does this advance our goals?
- **Risk if Not Done**: What happens if we skip this?

### Timeline Sensitivity:
- [ ] Blocking critical path
- [ ] Needed for upcoming decision
- [ ] Nice to have, no immediate dependency
- [ ] Background research

## 10. Agent Assignment Preferences
**Who should work on this? (Optional)**

If you have a preference:
- **OpenCode**: For multi-model research, technical deep-dives
- **Grok MC**: For strategic, ecosystem questions
- **Gemini CLI**: For verification, ground truth
- **Cline**: For implementation-focused research
- **No Preference**: Grok MC will assign

---

## Submission Checklist

Before submitting, ensure:
- [ ] Objective is clear and answerable
- [ ] Background provides enough context
- [ ] Questions are specific
- [ ] Deliverables are defined
- [ ] Success criteria are measurable
- [ ] Related resources are linked

## After Submission

1. Save to: `expert-knowledge/research/queue/pending/REQ-YYYY-MM-DD-XXX.md`
2. Update `expert-knowledge/research/index.json`
3. Notify Grok MC (if urgent)
4. Continue with current work - research executes in parallel

---

**Template Version**: 1.0.0  
**Last Updated**: 2026-02-13
