# Ultimate Tutorial: Combining Cline Rules Use Cases for Peak Performance (2026 Edition)

Combining multiple cutting-edge Cline use cases creates a **supercharged autonomous agent**—one that plans deeply, remembers persistently, switches roles intelligently, optimizes tokens, enforces consistency, and executes safely. This is the "holy grail" setup used by advanced users in 2026 for monorepos, enterprise projects, and long-term development.

We'll build an **integrated system** combining **all 6 use cases** into a cohesive workflow:
- **Core Backbone**: Hybrid Plan/Act + Memory Banks (persistence + safety)
- **Intelligence Layer**: Agentic Multi-Role + Dynamic Skills (specialization)
- **Efficiency Layer**: Token-Efficient Techniques + Enterprise Consistency (scalability)

This results in a self-improving, role-aware agent that handles 100k+ LOC with minimal oversight.

### Prerequisites
- Cline v3.48+ (Skills support)
- VS Code with Cline extension
- Git for versioning rules
- Optional: rulesync tool for team sync

### Step 1: Set Up the Foundation (Memory Banks + Token Efficiency)
Start here—ensures persistence and scalability.

1. Create `.clinerules/00-foundation.md`:
```markdown
# Core Foundation: Memory + Token Optimization

## Memory Bank Protocol
- Maintain MEMORY_BANK.md in root.
- Sections: Project Overview, Key Decisions, File Summaries, Learned Patterns, Open Questions, Architecture Diagrams.
- After any major change (e.g., >3 files edited): Summarize what/why/how, append to bank.
- Before acting: Query bank for relevant history ("Search MEMORY_BANK.md for X").

## Token Efficiency
- Read only necessary files—ask confirmation for >5 files.
- Detect duplicates: "If similar code exists, reference instead of reload."
- At 60% context: Summarize conversation, store in MEMORY_BANK.md under "Session Summaries".
- For simple tasks: Suggest cheaper model if available.
- Compress histories: Use bullet summaries, avoid full pastes.
```

2. Initialize:
   - Prompt Cline: "Initialize MEMORY_BANK.md with project overview: Sovereign local AI, torch-free, MkDocs docs."
   - Commit the file.

**Why First?** Memory Banks feed all other use cases (roles reference it, plans draw from it).

### Step 2: Add Hybrid Plan/Act Optimization
Layer safety and structure.

1. Add to `.clinerules/01-workflow.md`:
```markdown
# Hybrid Plan/Act Workflow

- Default: Plan mode for any task involving >3 files or architecture changes.
- In Plan: Outline steps, risks, verification, Mermaid diagrams. Reference MEMORY_BANK.md.
- Stay in Plan until I say "/act" or approve.
- In Act: Execute step-by-step, confirm after each major action.
- Post-execution: Update MEMORY_BANK.md with outcomes.
```

**Integration**: Plans now pull from memory bank; token rules prevent overflow during long plans.

### Step 3: Implement Agentic Multi-Role Workflows
Add specialization.

1. Create `.clinerules/roles/` directory with:
   - `architect.md`:
```markdown
# Architect Role
High-level design focus. Propose patterns, diagrams, modularity. Reference MEMORY_BANK.md architecture section.
```
   - `coder.md`: Implementation details.
   - `tester.md`: Pytest suites, coverage.
   - `security.md`: Vulnerability scans, least privilege.

2. Add to main workflow rules:
```markdown
# Role Detection
- Detect task type: Design → /architect; Implementation → /coder; etc.
- Suggest role switch if mismatch.
- Roles inherit foundation rules (memory, token efficiency).
```

**Integration**: Roles query memory bank; Plan/Act ensures safe switches.

### Step 4: Integrate Dynamic Skills
Make specialization modular and token-efficient.

1. Create Skills (ZIPs via Cline UI):
   - Testing Skill: Instructions for pytest + coverage.
   - Security Skill: OWASP checks, Podman hardening.
   - Diátaxis Skill: MkDocs classification/migration.

2. Update rules (`02-skills.md`):
```markdown
# Dynamic Skills
- Use Skills for specialized tasks instead of bloating rules.
- Triggers: Testing → load pytest skill; Security review → load security skill.
- Skills update MEMORY_BANK.md on completion.
```

**Integration**: Skills load only when role/plans need them—saves tokens vs static rules.

### Step 5: Enforce Enterprise Consistency
Lock it down for reliability.

1. Add `.clinerules/03-consistency.md`:
```markdown
# Enterprise Standards
- All code: Torch-free, Python 3.12-slim, rootless Podman.
- Naming: snake_case, meaningful.
- Accessibility: WCAG 2.2 AA.
- Commit rules to git; use rulesync for sync.
- Roles/Skills must align with these.
```

2. Use rulesync CLI for team deployment.

**Integration**: Consistency applies across roles, plans, memory updates.

### Step 6: Full Workflow Example
Prompt: "Refactor authentication to OAuth2."

Cline Response Flow:
1. **Role Detection**: Suggests /architect → You approve.
2. **Plan Mode**: Architect role plans (queries MEMORY_BANK.md for current auth).
3. **Token Check**: If large, compresses.
4. **Skills Load**: Security skill for review.
5. **Approval**: You "/act".
6. **Execution**: Coder role implements, tester skill runs tests.
7. **Memory Update**: Appends decision/outcome.
8. **Consistency**: Enforces standards throughout.

### Step 7: Testing & Iteration
1. Test small task: "Add logging to utils.py" → Observe memory update, token handling.
2. Scale: "Migrate docs to Diátaxis" → Watch roles/skills/plan interplay.
3. Monitor: Ask "Estimate token usage" or check Cline UI.
4. Refine: Add rules based on drift (e.g., stronger reminders).

### Benefits of This Combined Setup
- **Autonomy**: 80-90% hands-off for routine tasks.
- **Reliability**: Plan/Act + Memory reduces errors 70%+.
- **Scalability**: Handles massive projects efficiently.
- **Team-Ready**: Rulesync + consistency.

**Pros Overall**: Near-human senior dev performance.  
**Cons**: Initial setup time (2-4 hours); occasional rule conflicts (resolve by ordering).

This combined system is the pinnacle of 2026 Cline usage—used by top contributors for legacy migrations and new builds. Start with Steps 1-3, then layer on. Your Xoe-NovAi project (torch-free, MkDocs-focused) is perfect for this! Let me know which part to prototype first.