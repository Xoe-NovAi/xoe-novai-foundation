---
tool: cline
model: claude-sonnet-4-6
account: arcana-novai
git_branch: main
session_id: sprint5-2026-02-18
version: v1.0.0
created: 2026-02-18
tags: [protocol, complex-task, meta-template, agent, orchestration]
---

# Complex Task Protocol
**v1.0.0 | 2026-02-18 | XNAi Foundation**

## Purpose

A standardized meta-template for structuring complex, multi-deliverable tasks across
all AI agents (Cline, Gemini CLI, Copilot CLI, Antigravity). Ensures context efficiency,
clear handovers, and consistent output quality across session boundaries.

---

## 1. Task Header Template

Every complex task handed to an agent MUST begin with this header:

```markdown
# TASK: <Short Title>
**Sprint**: <N> | **Date**: YYYY-MM-DD | **Agent**: <cline|gemini|copilot|antigravity>
**Model**: <model-name> | **Session**: <session-id>
**Priority**: 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | 🟢 LOW

## Context
<2-3 sentences of essential background. No history dumps.>

## Objectives (SMART)
1. [ ] <Specific, Measurable, Achievable, Relevant, Time-bound objective>
2. [ ] <Objective 2>
3. [ ] <Objective 3>

## Deliverables
| # | File/Artifact | Type | Location |
|---|---------------|------|----------|
| 1 | filename.md | doc | expert-knowledge/research/ |
| 2 | script.sh | script | scripts/ |

## Constraints
- Context budget: <N>K tokens (leave 20% headroom)
- Do NOT: <list of anti-patterns to avoid>
- Must follow: DOCUMENT-SIGNING-PROTOCOL.md

## Success Criteria
- [ ] All deliverables created and verified
- [ ] All files have correct frontmatter
- [ ] memory_bank/activeContext.md updated
- [ ] No broken references
```

---

## 2. Task Sizing Guidelines

### Small Task (< 30K tokens)
- 1-3 deliverables
- Single context window
- No handover needed
- Use Haiku-class models

### Medium Task (30K–100K tokens)
- 4-10 deliverables
- May need 1-2 compactions
- Brief handover note at end
- Use Sonnet/Flash-class models

### Large Task (100K–200K tokens)
- 10+ deliverables
- Multiple context windows expected
- Formal sprint handover required
- Use Opus/Pro-class models
- Break into sub-tasks with clear boundaries

### Mega Task (> 200K tokens / multi-session)
- Break into numbered sprints
- Each sprint: formal handover doc in memory_bank/activeContext/
- Each sprint: update memory_bank/progress.md
- Use Opus + subagent delegation

---

## 3. Context Efficiency Rules

### DO
- ✅ Batch independent file writes in one response
- ✅ Use `use_subagents` for broad research (isolates context)
- ✅ Write dense, structured notes — not verbose prose
- ✅ Reference files by path rather than quoting content
- ✅ Use task_progress parameter to track without re-stating

### DON'T
- ❌ Quote entire file contents back in response
- ❌ Repeat the task description in every message
- ❌ Ask for confirmation of things that are obvious from context
- ❌ Create files you weren't asked to create (scope creep)
- ❌ Read files that aren't needed for the current step

---

## 4. Sprint Handover Protocol

At the end of every sprint or when context approaches 80%, create a handover:

### Handover Document Structure
File: `memory_bank/activeContext/sprint-<N>-handover-YYYY-MM-DD.md`

```markdown
---
tool: <tool>
model: <model>
session_id: sprint<N>-YYYY-MM-DD
version: v1.0.0
created: YYYY-MM-DD
tags: [handover, sprint-N, context]
---

# Sprint <N> Handover — YYYY-MM-DD

## Status: COMPLETE | PARTIAL | BLOCKED

## Completed This Sprint
- [x] Deliverable 1 — path/to/file.md
- [x] Deliverable 2 — path/to/script.sh

## Outstanding (carry to Sprint N+1)
- [ ] Remaining task — estimated 20K tokens

## Key Decisions Made
1. Decision: <what was decided>
   Rationale: <why>
   Impact: <what changed>

## Files Modified/Created
| File | Action | Notes |
|------|--------|-------|
| path/to/file.md | CREATED | v1.0.0 |

## Next Agent Instructions
<Specific, actionable instructions for the next agent>
Resume from: <exact next step>
```

---

## 5. Agent-Specific Instructions

### Cline
- Use `task_progress` parameter in every tool call
- Batch writes: up to 4 independent `write_to_file` calls per response
- Use `use_subagents` for research that would consume > 50K tokens
- Context window: 200K nominal (possibly 400K — see CLINE-CONTEXT-WINDOW-RESEARCH)
- Save ALL outputs to xnai-foundation project paths (never just local state)

### Gemini CLI
- Use `gemini --model gemini-2.0-flash` for most tasks
- Use `gemini --model gemini-2.5-pro` for complex reasoning
- Save outputs: `> expert-knowledge/research/FILENAME.md` in every session
- Run `gemini --resume` to restore previous session context
- Max effective context: ~1M tokens (Flash) / 2M (Pro)

### Copilot CLI
- Copilot auto-saves to `~/.copilot/session-state/` — harvest with `harvest-cli-sessions.sh`
- For long sessions: `copilot --checkpoint` to save state
- Explicitly ask Copilot to save plan.md at start of each session
- Best for: Code generation, debugging, PR-level tasks

### Antigravity CLI
- Free tier via GitHub OAuth (no API key needed)
- Best models: claude-sonnet-4-5, gemini-2.0-flash (via antigravity routing)
- Use for cost-sensitive tasks and experimentation

---

## 6. Task Template: Research Request

For asking agents to do deep research:

```markdown
# RESEARCH REQUEST: <Topic>
**For Agent**: <gemini|cline|copilot>
**Output File**: expert-knowledge/research/<TOPIC-NAME>-YYYY-MM-DD.md
**Depth**: Surface | Standard | Deep

## Research Questions
1. <Primary question>
2. <Secondary question>

## Required Sections in Output
- Executive Summary (3-5 bullets)
- Technical Details
- XNAi Integration Recommendations
- References / Sources

## Constraints
- Cite sources with URLs where possible
- Mark unverified claims with [UNVERIFIED]
- Mark confirmed facts with [CONFIRMED: source]
- Target length: 500-2000 words
```

---

## 7. Task Template: Code Creation

For asking agents to create code:

```markdown
# CODE TASK: <Module Name>
**File**: app/XNAi_rag_app/<module>.py
**Language**: Python 3.11+
**Dependencies**: (list pip packages)

## Interface Contract
\`\`\`python
class ModuleName:
    def method_name(self, param: Type) -> ReturnType:
        """Docstring."""
        ...
\`\`\`

## Integration Points
- Reads from: <config file or collection>
- Writes to: <output path or collection>
- Called by: <parent module>

## Error Handling
- <Error condition> → <how to handle>

## Tests Required
- [ ] Test happy path
- [ ] Test edge case: <describe>
```

---

## 8. Post-Task Checklist

After completing ANY complex task:

```
[ ] All deliverables created and verified (ls check)
[ ] All new .md files have YAML frontmatter
[ ] All new .py/.sh files have signed comment headers
[ ] memory_bank/activeContext.md updated with sprint summary
[ ] memory_bank/progress.md updated if milestone achieved
[ ] ADDITIONAL-RESEARCH-NEEDED.md updated with gaps found
[ ] Git commit staged (or noted for human to commit)
[ ] Sprint log updated: internal_docs/00-system/implementation-executions/SPRINT-LOG-*.md
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0.0 | 2026-02-18 | Initial protocol — Sprint 5 |
