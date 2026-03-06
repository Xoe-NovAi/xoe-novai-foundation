# Gnosis Engine Synthesis Templates

**Purpose**: Standardized templates for synthesizing research into documentation and expert knowledge

---

## Template 1: Research to Official Docs

```markdown
---
title: [Document Title]
description: [Brief description]
category: [api|guide|reference|protocol]
status: [stable|experimental|deprecated]
created: 2026-02-27
last_updated: 2026-02-27
owner: [team/agent]
review_cycle: [quarterly|annually]
---

# [Document Title]

## Overview
[Brief 2-3 sentence overview]

## Background
[Context from research]

## Details
[Technical content]

## Usage
[How to use]

## Examples
```[language]
[code examples]
```

## Related
- [Link to related docs]
- [Link to research source]

## Changelog
| Date | Change | Author |
|------|--------|--------|
| 2026-02-27 | Initial synthesis | [Agent] |
```

---

## Template 2: Research to Expert Knowledge

```markdown
---
title: [Expert Knowledge Title]
domain: [model-reference|security|protocols|coder|infrastructure]
expert: [Expert Agent Name]
status: [active|review_needed|stale]
created: 2026-02-27
last_verified: 2026-02-27
---

# [Expert Knowledge Title]

## Domain Context
[How this fits into the domain]

## Key Findings

### [Finding 1]
- **Source**: [Research document]
- **Verified**: [Yes/No]
- **Relevance**: [High/Medium/Low]

### [Finding 2]
- **Source**: [Research document]
- **Verified**: [Yes/No]
- **Relevance**: [High/Medium/Low]

## Best Practices
1. [Practice 1]
2. [Practice 2]

## Common Pitfalls
1. [Pitfall 1]
2. [Pitfall 2]

## References
- [Research source 1]
- [Research source 2]

## See Also
- [Related expert knowledge]
- [Related documentation]
```

---

## Template 3: Domain Expert Creation

```markdown
---
title: [Expert Name]
domain: [domain name]
status: [draft|active|deprecated]
created: 2026-02-27
owner: [owner]
---

# [Expert Name]

## Expert Overview
[Brief description of the expert's purpose]

## Knowledge Domains

### [Domain 1]
- **Source**: [expert-knowledge/domain/]
- **Coverage**: [percentage or description]
- **Last Updated**: [date]

### [Domain 2]
- **Source**: [expert-knowledge/domain/]
- **Coverage**: [percentage or description]
- **Last Updated**: [date]

## Capabilities

### Core Functions
1. [Function 1]
2. [Function 2]

### Specialized Knowledge
- [Knowledge area 1]
- [Knowledge area 2]

## Loading Protocol

```markdown
## Load Order

1. Core: activeContext.md
2. Domain: expert-knowledge/[domain]/
3. Docs: docs/[relevant-section]/
4. Research: memory_bank/research/
5. Status: Research queue + Vikunja tasks
```

## Directives

### Primary Directive
[Main directive for the expert]

### Behavior Rules
1. [Rule 1]
2. [Rule 2]

### Output Formats
- [Format 1]
- [Format 2]

## Knowledge References

| Source | Type | Update Frequency |
|--------|------|------------------|
| [Doc 1] | Official Docs | [Frequency] |
| [KB 1] | Expert Knowledge | [Frequency] |
| [Research] | Memory Bank | [Frequency] |

## Audit Trail

| Date | Action | Trigger |
|------|--------|---------|
| 2026-02-27 | Created | Gnosis Engine |
| [Date] | [Action] | [Trigger] |

---

## Template 4: Knowledge Audit Entry

```yaml
# expert-knowledge/_meta/audit/[domain]-YYYY-Q[Q].yaml

domain: [domain-name]
quarter: YYYY-Q#
audit_date: 2026-02-27
auditor: [agent/name]

coverage:
  total_files: [count]
  current: [count]
  needs_review: [count]
  stale: [count]

findings:
  - file: [filename]
    status: [current|needs_update|stale]
    last_verified: [date]
    notes: [notes]

actions:
  - type: [update|archive|create]
    target: [file/path]
    priority: [high|medium|low]
    owner: [assignee]
```

---

## Template 5: Synthesis Job

```markdown
---
title: RJ-Synth-[NUMBER]-[DOMAIN]
description: [Description]
status: [pending|in_progress|complete]
priority: [P0|P1|P2|P3]
created: 2026-02-27
---

# Synthesis Job: [Job Name]

## Source Research
- [Research document 1]
- [Research document 2]

## Destination
- [docs/ path]
- [expert-knowledge/ path]
- [multi_expert/ path]

## Tasks

### Task 1: [Task Name]
- [ ] [Subtask]
- [ ] [Subtask]

### Task 2: [Task Name]
- [ ] [Subtask]
- [ ] [Subtask]

## Verification Checklist
- [ ] Cross-references valid
- [ ] No conflicts with existing docs
- [ ] Formatting consistent
- [ ] Indexes updated

## Completion Notes
[Notes on what was synthesized]
```

---

**Last Updated**: 2026-02-27
**Owner**: MC-Overseer
