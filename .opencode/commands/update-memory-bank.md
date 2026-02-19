# Update Memory Bank Command

## Purpose
Manually trigger memory bank update after significant changes.

## Usage
```
/update-memory-bank [section]
```

## Sections
- `all` - Update all sections
- `activeContext` - Current priorities
- `progress` - Implementation status
- `systemPatterns` - Architecture patterns

## Workflow
1. Read current memory bank state
2. Analyze recent changes (git diff)
3. Identify updates needed
4. Update specified sections
5. Validate consistency

## Update Triggers
- Architectural decisions
- 3+ file changes
- Phase transitions
- New integrations

## Output
```
## Memory Bank Update

### Updated Sections
- activeContext.md
  - Added: New priority item
  - Modified: Current task status
  
- progress.md
  - Completed: Task X
  - Added: Task Y to in-progress

### Files Analyzed
- app/core/agent_bus.py
- app/services/rag_service.py
- docs/api/SEMANTIC_SEARCH_API.md

### Validation
✅ All sections consistent
✅ No orphaned references
✅ Timestamps updated
```

## Validation Checks
- [ ] No broken internal links
- [ ] Consistent phase references
- [ ] Updated timestamps
- [ ] Removed obsolete entries
