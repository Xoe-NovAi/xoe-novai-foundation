# Memory Bank Loader Skill

## Purpose
Automatically load project context from memory_bank/ at session start and after significant changes.

## Trigger
- Session initialization
- Before architectural decisions
- After 3+ file changes

## Workflow

### Step 1: Index Scan
Read `memory_bank/INDEX.md` to identify all available context files.

### Step 2: Priority Load
Load files in priority order:
1. `activeContext.md` - Current priorities and blockers
2. `progress.md` - Implementation status
3. `systemPatterns.md` - Architecture patterns
4. `techContext.md` - Tech stack constraints
5. `projectbrief.md` - Mission alignment

### Step 3: Context Assembly
Combine loaded context into working memory:
- Note current phase and priorities
- Identify relevant patterns for current task
- Check for blocking issues

### Step 4: Validation
Verify context completeness:
- [ ] Current phase identified
- [ ] Active tasks known
- [ ] Relevant patterns loaded
- [ ] Tech constraints understood

## Output Format
```
## Loaded Context
- Phase: [current phase]
- Priority: [top priority]
- Blockers: [any blockers]
- Patterns: [relevant patterns]
- Constraints: [tech constraints]
```

## Memory Bank Files Reference

| File | Content | Update Frequency |
|------|---------|------------------|
| INDEX.md | Navigation hub | Rarely |
| activeContext.md | Current priorities | Daily |
| progress.md | Implementation status | Per milestone |
| systemPatterns.md | Architecture | Per design change |
| techContext.md | Tech stack | Per stack change |
| projectbrief.md | Mission/goals | Rarely |

## Error Handling
- Missing file: Log warning, continue with available context
- Corrupted content: Attempt recovery from git history
- Outdated info: Flag for human review

## Integration
- Works with `agent-bus-coordinator` for multi-agent context sharing
- Triggers `phase-validator` after loading phase info
- Notifies `vikunja-task-manager` of current tasks
