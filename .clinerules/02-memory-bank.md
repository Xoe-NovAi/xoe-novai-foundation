---
priority: critical
context: general
activation: always
last_updated: 2026-02-17
version: 2.0
---

# Memory Bank Protocol

**Core Instruction**: You have no built-in memory. Rely ENTIRELY on `memory_bank/` files for context persistence.

## Session Workflow

### Session Start
1. Read ALL `memory_bank/*.md` files before any task
2. Establish complete project context
3. Note current priorities and blockers

### During Work
- Reference relevant memory bank files for consistency
- Check architectural decisions in `systemPatterns.md`

### Session End
1. Update `activeContext.md` with session outcomes
2. Update `progress.md` with completed work
3. Commit changes to git for team synchronization

## File Reference Guide

| File | Purpose | When to Use |
|------|---------|-------------|
| `projectbrief.md` | Goals, constraints, success metrics | Fundamental decisions |
| `productContext.md` | UX, user requirements | UX decisions |
| `systemPatterns.md` | Architecture, patterns, diagrams | Architectural decisions |
| `techContext.md` | Tech stack, performance targets | Implementation constraints |
| `activeContext.md` | Current priorities, blockers | Daily reference |
| `progress.md` | Completed work, new priorities | Status updates |

## Update Triggers
Update memory bank after:
- Changes affecting >3 files
- Architectural decisions
- New patterns discovered
- Major implementation milestones

## Quality Standards
- **Accuracy**: Only document verified, implemented changes
- **Completeness**: Document decisions, implementations, outcomes
- **Consistency**: Align recommendations with system patterns

## Multi-Agent Integration
Each agent role references relevant memory bank sections:
- **Architect**: `systemPatterns.md`, `techContext.md`
- **Coder**: `activeContext.md`, `progress.md`
- **Security**: `projectbrief.md` (constraints)
- **Documenter**: All files for comprehensive updates

## Emergency Procedures
| Issue | Resolution |
|-------|------------|
| Corruption | Rebuild from git history |
| Missing context | Escalate to human |
| Conflicting info | Prioritize most recent |
| Incomplete docs | Flag for human review |

## Success Metrics
- 70-90% faster work continuation
- 95% architectural pattern alignment
- Zero context loss between sessions
