# Recall - Handovers

Agent handoff documents for session continuity.

## Naming Convention

```
YYYY-MM-DD_from-agent-to-agent.handover.md
```

## Content Template

```markdown
---
type: episodic
from_agent: [source agent]
to_agent: [target agent]
date: YYYY-MM-DD
session_id: ses_xxx
priority: high | medium | low
status: pending | acknowledged | completed
---

# Handover: [Title]

## Current State
[What's been done]

## In Progress
[What's being worked on]

## Blockers
[What's blocking progress]

## Next Steps
1. [Step 1]
2. [Step 2]

## Context Files
- [File 1]: [Why relevant]
- [File 2]: [Why relevant]

## Decisions Made
- [Decision 1]
```

## Workflow

1. Agent creates handover document
2. Target agent acknowledges
3. Target agent updates status as work progresses
4. Document archived after completion
