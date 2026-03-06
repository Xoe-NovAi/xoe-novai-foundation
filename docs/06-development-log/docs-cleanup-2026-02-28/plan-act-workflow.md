# Deep Dive: The Plan/Act Workflow in Cline (2026 Edition)

The **Plan/Act workflow** is Cline's signature feature and one of its most powerful differentiators from other AI coding assistants (e.g., Cursor, GitHub Copilot, or Continue.dev). Introduced in mid-2024 and refined through 2025-2026 updates (v3.20+), it enforces a structured, safe approach to code changes: **Plan mode** for deep reasoning and outlining, **Act mode** for execution. This prevents reckless file edits, reduces errors by 70-90% (per community benchmarks), and enables reliable handling of complex refactors in large codebases.

This deep dive covers:
- Core mechanics
- Why it's cutting-edge
- Step-by-step tutorial
- Integration with rules, memory banks, roles, and skills
- Advanced patterns
- Best practices and troubleshooting

Based on official docs (cline.bot/features/plan-act), GitHub issues (#3809, #4389), and 2026 community guides.

## Core Mechanics: How Plan/Act Works
Cline operates in two explicit modes (toggled via slash commands or rules):

1. **Plan Mode** (default for safety):
   - Cline **thinks aloud**: Outlines steps, risks, dependencies, verification.
   - Produces diagrams (Mermaid), pseudocode, file lists.
   - **No execution**: Does not edit files, run terminal commands, or commit changes.
   - Goal: Build consensus before action.

2. **Act Mode**:
   - Executes the approved plan: Edits files, runs commands, tests.
   - Step-by-step confirmation (configurable).
   - Post-action: Reports outcomes, suggests next steps.

**Toggling**:
- `/plan`: Enter/exit Plan.
- `/act`: Switch to Act (requires explicit approval).
- Rules can auto-enforce: "Default to Plan for >3 files."

**Why Dual Modes?** LLMs excel at reasoning but can hallucinate actions. Plan/Act separates "think" from "do"—like a human senior dev reviewing junior code.

## Why It's Cutting-Edge
- **Safety First**: Prevents "cowboy coding" disasters (e.g., breaking production in one shot).
- **Scalability**: Handles 100k+ LOC projects—Plan reviews context without immediate edits.
- **2026 Refinements**: v3.48+ adds "hybrid" (auto-suggest Act after Plan approval), token-aware planning (summarizes if nearing limits), and integration with Skills (load testing skill in Plan phase).
- **Community Impact**: Users report 80% fewer rollbacks; essential for enterprise (e.g., PR-like reviews inside VS Code).
- **Comparison**: Cursor has "apply" but no enforced planning; Aider is execution-heavy. Plan/Act is the gold standard for reliability.

## Step-by-Step Tutorial
### 1. Basic Usage
Prompt a task: "Refactor authentication module to use OAuth2."

Cline (Plan mode):
- Outlines: Files to touch, risks (breaking login), steps (backup, test suite, deploy).
- Mermaid diagram of flow.
- Asks: "Approve plan? (/act to proceed)"

You: `/act`

Cline (Act):
- Edits files one-by-one.
- Runs tests.
- Reports: "Success—login preserved."

### 2. Setup for Automatic Enforcement
Add to `.clinerules/01-workflow.md`:
```markdown
# Plan/Act Enforcement
- Default to Plan mode for any task involving >3 files, architecture changes, or migrations.
- In Plan: Provide numbered steps, risks, verification commands, Mermaid if relevant.
- Reference MEMORY_BANK.md for history.
- Do not switch to Act without explicit user approval (/act).
- Post-Act: Update MEMORY_BANK.md and suggest verification.
```

### 3. Advanced Session Flow
1. **Start**: Prompt complex task.
2. **Plan Phase**:
   - Cline queries memory bank/rules.
   - Outputs detailed plan.
   - You review/edit plan (Cline can iterate: "Revise step 3").
3. **Approval**: `/act` or "Proceed".
4. **Act Phase**:
   - Executes incrementally.
   - Pauses for confirmation if risky.
5. **Wrap-Up**: Updates memory bank, suggests tests.

## Integration with Other Features
Plan/Act shines when combined:

- **Memory Bank**: Plans query bank for context; Act updates it. Rule: "Always reference MEMORY_BANK.md in plans."
- **Roles/Skills**: Plan in architect role → Act in coder role. Load testing skill during Plan verification.
- **Token Efficiency**: Long plans compress history into bank.
- **Rules**: Enforce thresholds (e.g., Plan mandatory for security changes).

**Combined Example** (OAuth refactor):
- Plan (architect role): Queries bank → Diagrams new flow.
- Skills: Loads security skill → Flags vulnerabilities.
- Approval → Act (coder + tester skills) → Implements/tests → Updates bank.

## Advanced Patterns
- **Iterative Planning**: "/revise plan" multiple times.
- **Branching Plans**: "Option A (safe) vs B (optimized)".
- **Verification Gates**: "Run tests before final commit."
- **Hybrid Auto-Act**: Rules: "If plan <5 steps and low-risk, suggest auto-act."
- **Rollback Integration**: "Include git branch/backup in every plan."

## Best Practices
- **Always Plan Complex Tasks**: >3 files, unknowns, migrations.
- **Explicit Approvals**: Never auto-act on critical code.
- **Rich Outputs**: Demand Mermaid, tables, checklists in plans.
- **Combine Modes**: Use Plan for 80% of time—saves rework.
- **Token Awareness**: "If nearing limit, summarize plan."
- **Troubleshooting**:
  - Stuck in Plan: Explicit `/act`.
  - Vague Plans: Rules "Be specific—number steps, include commands."
  - Over-Execution: Reinforce "Step-by-step confirmation."

Plan/Act is the foundation of reliable AI coding—turning Cline into a thoughtful partner. For your Xoe-NovAi (Podman/MkDocs), enforce it for migrations: "Plan Diátaxis changes fully before Act."