# XNAi Foundation — AI Implementation Framework
## Master Template & Execution Standard

**Version**: 1.1.0  
**Created**: 2026-02-18  
**Updated**: 2026-02-18 (Sprint 2) — Added CLI verification pre-sprint step; added context exhaustion protocol
**Created By**: Claude Opus 4.6 (Cline) + research synthesis from GLM-5 session  
**Purpose**: Reusable framework for all future autonomous AI implementation executions  
**Status**: AUTHORITATIVE — all agents follow this framework

---

## FRAMEWORK PHILOSOPHY

This framework captures the XNAi Foundation's methodology for autonomous AI-driven development. Every implementation session should produce:

1. **Historic Record** — A session log capturing decisions, findings, and rationale
2. **Knowledge Integration** — Research findings absorbed into `expert-knowledge/`
3. **Implementation Artifacts** — Code, config, docs, tests
4. **Forward Planning** — Updated task queue and next-session briefing

The XNAi Foundation operates as a **sovereign AI development platform** where AI agents are primary implementers under human strategic direction. This framework ensures continuity across sessions and agents.

---

## FRAMEWORK STRUCTURE

```
internal_docs/
├── 00-system/
│   ├── IMPLEMENTATION-FRAMEWORK-v1.0.0.md    ← This file
│   ├── MASTER-PROJECT-INDEX-v1.0.0.md         ← Project state index
│   ├── STRATEGIC-REVIEW-CLINE-2026-02-18.md   ← Strategic review (Feb 18)
│   └── implementation-executions/             ← Per-session sprint logs
│       ├── SPRINT-LOG-TEMPLATE.md             ← Template for new sessions
│       └── SPRINT-LOG-2026-02-18-OPUS.md      ← This session's log
│
├── 01-strategic-planning/
│   ├── SOVEREIGN-MC-AGENT-SPEC-v1.0.0.md      ← MC Agent design spec
│   └── PHASE-8-EXECUTION-PLAN.md              ← Phase 8 implementation plan
│
├── 02-research-lab/                            ← Research request outputs
│   └── [REQ-*.md files]
│
└── 03-infrastructure-ops/
    └── SERVICE-HEALTH-*.md

expert-knowledge/
├── AGENT-CLI-MODEL-MATRIX-v2.0.0.md           ← Agent/model assignments
├── OPENCODE-CLI-COMPREHENSIVE-GUIDE-v1.0.0.md ← OpenCode setup guide
└── research/
    ├── ANTIGRAVITY-AUTH-DISCOVERY-2026-02-18.md ← This session's discovery
    └── [REQ-*.md research results]

mc-oversight/
├── OPUS-ONBOARDING-*.md                        ← Agent onboarding briefs
├── MESSAGE-FOR-OPUS-*.md                       ← Inter-agent messages
├── initiative-status-dashboard.md              ← Live project status
├── priority-matrix.md                          ← Task priorities
├── risk-assessment.md                          ← Current risks
└── strategic-recommendations.md               ← MC recommendations
```

---

## SPRINT EXECUTION PROTOCOL

### Pre-Sprint Checklist (Every Session)
1. **Read**: `memory_bank/activeContext.md` — current priorities
2. **Read**: `memory_bank/progress.md` — phase completion status
3. **Read**: Latest `mc-oversight/OPUS-ONBOARDING-*.md` — agent briefing
4. **Check**: Service health (`make up`, `docker ps`)
5. **Check**: Git status (`git status --short | wc -l`)
6. **Create**: New sprint log from `SPRINT-LOG-TEMPLATE.md`
7. **Verify CLI tools** ← NEW — see section below before using any external CLI

### CLI Tool Verification Protocol (⚠️ MANDATORY before first use)

> **Why this exists**: The `opencode-ai/opencode` repo was archived Sep 18, 2025 with no warning.  
> Documents written before that date contain wrong flags (`--print` instead of `-p`).  
> Always verify a CLI tool's current repository and flags before writing integration code.

For **any** CLI tool used in agent code:

```
1. Verify the active GitHub repository (check for archive/redirect notices)
2. Check the current --help output or CHANGELOG for flag changes
3. Check if npm package name changed (opencode-ai/opencode → charmbracelet/crush)
4. Document findings in expert-knowledge/research/ before writing code
5. Cross-reference existing docs — they may be outdated
```

**Known CLI audit status (as of 2026-02-18):**

| Tool | Active Repo | Non-interactive flag | Guide |
|------|-------------|---------------------|-------|
| `opencode` | `charmbracelet/crush` | `-p` / `-q` | `OPENCODE-CLI-COMPREHENSIVE-GUIDE-v1.0.0.md` |
| `gemini` | `google-gemini/gemini-cli` | `--prompt` or `-p` | `GEMINI-CLI-MODELS-v1.0.0.md` |
| `ollama` | `ollama/ollama` | `run <model>` | — |

Research doc pattern for CLI verification:
```
expert-knowledge/research/[TOOL]-ARCHIVED-DISCOVERY-YYYY-MM-DD.md
```

### During Sprint
- Update sprint log in real-time with decisions and findings
- Capture any new knowledge to `expert-knowledge/`
- Flag blockers immediately in sprint log
- Use AnyIO TaskGroups for all async operations (never `asyncio.gather`)

### Post-Sprint Checklist
1. **Update**: `memory_bank/activeContext.md` with current state
2. **Update**: `memory_bank/progress.md` with completed items
3. **Commit**: All changes with semantic commit messages
4. **Write**: Next session onboarding brief to `mc-oversight/`
5. **Update**: `mc-oversight/initiative-status-dashboard.md`

---

## AGENT ROLE PROTOCOL

### Role Hierarchy
```
Human Director (ultimate authority)
  ↓
Sovereign MC Agent (LOCAL — app/XNAi_rag_app/core/sovereign_mc_agent.py)
  ├─ Cline/Claude Opus 4.6    → Multi-file implementation, complex code
  ├─ OpenCode/GLM-5           → Research, structured analysis, gap reports
  ├─ OpenCode/Antigravity     → Free Claude Opus 4.5, Gemini 3 Pro (1M ctx)
  ├─ OpenCode/Kimi-K2.5       → Large context (262k) synthesis
  └─ Gemini CLI               → Whole-codebase audit (1M context)
Claude.ai Project → High-level org strategy only (not daily operations)
```

### Task Assignment Rules
| Complexity | Context Needed | Assign To |
|------------|---------------|-----------|
| 5/5 — Architecture | >50k tokens | Cline/Opus 4.6 |
| 4-5/5 — Implementation | IDE + file tree | Cline/Opus 4.6 |
| 3/5 — Research | Deep analysis | OpenCode/GLM-5 |
| 3/5 — Large context | >100k tokens | OpenCode/Kimi K2.5 |
| 2/5 — Quick code | Terminal | OpenCode/any model |
| 1-2/5 — Validation | Second opinion | OpenCode/Big Pickle |
| Any — Codebase audit | Full repo scan | Gemini CLI |

### Delegation via Agent Bus
```python
# Example: Delegating a research task to OpenCode via Agent Bus
async with AgentBusClient("did:xnai:sovereign-mc") as bus:
    await bus.send_task(
        target_did="did:xnai:opencode-glm5",
        task_type="research",
        payload={
            "request": "REQ-DOC-001",
            "model": "opencode/glm-5-free",
            "output_path": "internal_docs/02-research-lab/REQ-DOC-001-RESULTS.md"
        }
    )
```

---

## CODING STANDARDS (XNAi Specific)

### Mandatory Constraints
- ❌ **NEVER**: `asyncio.gather()` — use AnyIO TaskGroups
- ❌ **NEVER**: PyTorch, CUDA, Triton, sentence-transformers
- ✅ **ALWAYS**: AnyIO TaskGroups for concurrency
- ✅ **ALWAYS**: ONNX + GGUF + Vulkan for model inference
- ✅ **ALWAYS**: Zero external telemetry
- ✅ **ALWAYS**: UID 1001 for container file ownership

### AnyIO Pattern (Required)
```python
import anyio

async def parallel_ops():
    async with anyio.create_task_group() as tg:
        tg.start_soon(operation_a)
        tg.start_soon(operation_b)
        tg.start_soon(operation_c)
```

### Error Handling Pattern
```python
from app.XNAi_rag_app.core.circuit_breakers.circuit_breaker import CircuitBreaker

async def resilient_operation():
    try:
        result = await service_call()
        return result
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        # Circuit breaker handles retry/fallback
        raise
```

---

## RESEARCH DOCUMENTATION PROTOCOL

### When to Create Research Docs
- Any external library version confirmed (PyPI, GitHub)
- Any provider/API capability discovered
- Any constraint or limitation verified
- Any architectural pattern validated

### Research Doc Format
```markdown
# [DISCOVERY-NAME] — Research Record
**Date**: YYYY-MM-DD
**Researcher**: [Agent name]
**Method**: [How discovered — web search, live CLI, PyPI, etc.]
**Confidence**: [High/Medium/Low]

## Finding
[Specific, verifiable facts]

## Impact on XNAi
[How this changes our approach]

## Source URLs
[Where to verify]

## Implementation Notes
[Code snippets, config examples]
```

---

## HISTORIC RECORD FORMAT

Every implementation session creates a sprint log in `internal_docs/00-system/implementation-executions/`. These logs are the **institutional memory** of the project — they capture not just what was done, but why, what was discovered, and what was abandoned.

Future AI agents reading these logs can:
1. Understand design decisions and their rationale
2. Avoid repeating research already done
3. Pick up exactly where a previous session left off
4. See the evolution of architectural thinking

---

## TEMPLATE VARIABLES FOR FUTURE AGENTS

When starting a new session, fill these in:

```
SESSION_DATE: YYYY-MM-DD
SESSION_AGENT: [Claude Opus 4.6 | Claude Sonnet 4.x | GLM-5 | ...]
SESSION_TYPE: [Implementation | Research | Review | Architecture]
PHASE_CURRENT: [Phase X]
BRANCH_CURRENT: [git branch]
SERVICES_RUNNING: [list]
BLOCKERS: [list or "none"]
PRIORITIES_TODAY: [ordered list]
```

---

## DOCUMENT VERSIONING

| File | Version Pattern | Example |
|------|----------------|---------|
| Framework files | `vMAJOR.MINOR.PATCH` | `v1.0.0` |
| Sprint logs | `YYYY-MM-DD-AGENT` | `2026-02-18-OPUS` |
| Research records | `YYYY-MM-DD` in filename | `ANTIGRAVITY-2026-02-18.md` |
| Agent matrices | `vMAJOR.0.0` | `v2.0.0` |

---

## AUTONOMOUS SESSION CONTINUITY PROTOCOL

> **Why this exists**: Long autonomous sessions exhaust context windows. When this happens mid-task,  
> the next agent session has no knowledge of what was done, what's pending, or why.  
> This protocol ensures the work survives context exhaustion without human intervention.

### Context Exhaustion Warning Signs
- Context window usage exceeds **75%**
- Response generation starts noticeably slowing
- You are about to start a complex multi-file operation

### When Approaching Context Limit (>75% used)

**Do immediately, before context runs out:**

1. **Write a handover block** to `memory_bank/activeContext.md`:
   ```markdown
   ## [AGENT] Session Handover — [TIMESTAMP]
   
   ### Work Completed This Session
   - [list of completed items with file paths]
   
   ### Work In Progress (INCOMPLETE — pick up here)
   - [ ] [specific next action]
   - [ ] [second action]
   
   ### Critical Context for Next Session
   - [key decisions made, bugs found, discoveries]
   
   ### Files Modified This Session
   - [file path] — [what changed]
   ```

2. **Commit all completed work** with descriptive message:
   ```bash
   git add -A && git commit -m "feat(sprint-2): partial session — [what's done] | CONTINUE: [what's next]"
   ```

3. **Write a session summary** to the sprint log in `internal_docs/00-system/implementation-executions/`

4. **Stop gracefully** — do not attempt work that will be cut off mid-execution

### When Resuming After Context Exhaustion

1. Read `memory_bank/activeContext.md` — find the most recent "Session Handover" block
2. Read the sprint log from the previous session
3. Check `git log --oneline -10` to see what was committed
4. Continue from the "Work In Progress" checklist
5. Do NOT re-do work that was committed — verify first

### Sprint Log Minimum Required Fields

Every sprint log MUST capture before context exhaustion:

```markdown
## Session Status at Close
- **Context exhausted**: [yes/no]
- **Completed items**: [list]
- **Pending items**: [list with priority]
- **Next agent should start with**: [specific instruction]
- **Files modified**: [list]
- **Bugs found but not fixed**: [list]
```

---

*This framework is a living document. Update it when new patterns emerge, new agents join the team, or new constraints are discovered.*

**Maintained By**: Cline/Opus (implementation changes), GLM-5 (research additions)  
**Review Cycle**: After each major phase completion
