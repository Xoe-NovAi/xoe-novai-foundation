---
document_type: integration_guide
title: MEMORY_BANK_INTEGRATION_GUIDE
version: 1.0
created_date: 2026-03-14
created_by: Phase 3 Deployment
status: active
scope: Agent-1 Memory Integration
---

# Memory Bank Integration Guide for Agent-1 v1.0

## Overview

Agent-1 integrates with the omega-stack memory banking system to provide:
- Persistent state across sessions
- Multi-agent communication
- Task tracking and dependencies
- Historical context and recall

## Architecture

### Three-Layer Memory System

#### Layer 1: Ephemeral Session Memory
- Current execution context
- Recent command outputs
- Active task state
- **Duration**: Current session only
- **Scope**: Agent-1 local

#### Layer 2: Persistent Database (SQLite)
- Task tracking (todos table)
- Test case results
- Session state
- **Duration**: Across sessions
- **Scope**: Per-session isolation
- **Location**: `~/.copilot/session.db`

#### Layer 3: File-Based Memory Bank
- Strategic documents
- Handover protocols
- Research findings
- Agent communications
- **Duration**: Permanent
- **Scope**: Shared across agents
- **Location**: `/memory_bank/` directory tree

## Operational Patterns

### Pattern 1: Task Tracking

```sql
-- Create task
INSERT INTO todos (id, title, description, status)
VALUES ('phase3-agent1-deployment', 'Deploy Agent-1 hardened prompt', '...', 'in_progress');

-- Update task
UPDATE todos SET status = 'done', updated_at = datetime('now')
WHERE id = 'phase3-agent1-deployment';

-- Check dependencies
SELECT t.* FROM todos t
WHERE t.status = 'pending'
AND NOT EXISTS (
    SELECT 1 FROM todo_deps td
    JOIN todos dep ON td.depends_on = dep.id
    WHERE td.todo_id = t.id AND dep.status != 'done'
);
```

### Pattern 2: Document Storage

```
/memory_bank/PHASE-3-DEPLOYMENT/
├── SYSTEM_PROMPT_v3_2_ENHANCED.md          # System instructions
├── CUSTOM_INSTRUCTIONS_v1_2_FINAL.md       # Custom directives
├── MEMORY_BANK_INTEGRATION_GUIDE.md        # This document
├── A2A_PROTOCOL_SPEC.md                    # Agent-to-agent protocol
├── OBSERVABILITY_REQUIREMENTS.md           # Monitoring/logging
├── ISS_AUTOMATION_PROCEDURES.md            # Issue automation
└── PHASE_3_DEPLOYMENT_REPORT.md            # Results summary
```

### Pattern 3: Inter-Agent Communication

When passing context to other agents:

```markdown
## Handover to Agent-N

**From**: Agent-1 (Execution)
**To**: Agent-N (Next Phase)
**Date**: 2026-03-14 17:00 UTC

### Completed Tasks
- [x] System prompt deployed
- [x] Tests passed
- [x] Documentation updated

### Context for Next Phase
[Details about what was accomplished]

### Open Issues
[Items requiring follow-up]

### Recommendations
[Suggestions for next steps]
```

## API Reference

### SQL Queries

#### Get Pending Todos
```sql
SELECT * FROM todos WHERE status = 'pending' ORDER BY created_at;
```

#### Get In-Progress Tasks
```sql
SELECT * FROM todos WHERE status = 'in_progress' ORDER BY updated_at DESC;
```

#### Track Phase Completion
```sql
SELECT 
  SUBSTR(id, 1, 6) as phase,
  COUNT(*) as total,
  SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as completed,
  ROUND(100.0 * SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) / COUNT(*), 1) as percent
FROM todos
GROUP BY phase
ORDER BY phase;
```

#### Query with Dependencies
```sql
SELECT t.id, t.title, t.status,
  COUNT(DISTINCT td.depends_on) as blocked_by,
  GROUP_CONCAT(td.depends_on, ', ') as blocking_tasks
FROM todos t
LEFT JOIN todo_deps td ON t.id = td.todo_id
WHERE t.status = 'pending'
GROUP BY t.id
ORDER BY blocked_by DESC;
```

### File Operations

#### Reading Context Documents
```bash
# View system prompt
view /home/arcana-novai/Documents/Xoe-NovAi/omega-stack/memory_bank/PHASE-3-DEPLOYMENT/SYSTEM_PROMPT_v3_2_ENHANCED.md

# Search for specific content
grep -r "Memory Bank" /memory_bank/PHASE-3-DEPLOYMENT/ --include="*.md"

# List all Phase 3 documents
glob /home/arcana-novai/Documents/Xoe-NovAi/omega-stack/memory_bank/PHASE-3-DEPLOYMENT/*.md
```

#### Updating Status Documents
```bash
# Create progress report
create /memory_bank/PHASE-3-DEPLOYMENT/PHASE_3_DEPLOYMENT_REPORT.md

# Archive old reports
edit /memory_bank/PHASE-3-DEPLOYMENT/PHASE_3_DEPLOYMENT_REPORT.md
```

## Best Practices

### 1. Always Verify Integrity
- Check file permissions before access
- Validate JSON/YAML formatting
- Verify hash checksums for critical docs

### 2. Maintain Clean State
- Archive old sessions regularly
- Update progress in real-time
- Clear ephemeral cache weekly

### 3. Document Everything
- Log all major decisions
- Record deployment timestamps
- Keep audit trail of changes

### 4. Respect Isolation
- Use session-specific database
- Don't share credentials
- Isolate per-agent context

### 5. Enable Discoverability
- Use consistent naming
- Maintain index documents
- Link related documents

## Troubleshooting

### Issue: Database Not Found
```bash
# Check location
ls -la ~/.copilot/session.db

# Verify permissions
chmod 600 ~/.copilot/session.db

# Check schema
sqlite3 ~/.copilot/session.db ".schema"
```

### Issue: Memory Bank Access Denied
```bash
# Check directory permissions
ls -la /memory_bank/

# Verify file permissions
ls -la /memory_bank/PHASE-3-DEPLOYMENT/

# Fix if needed
chmod 755 /memory_bank/
chmod 644 /memory_bank/PHASE-3-DEPLOYMENT/*.md
```

### Issue: Context Too Large
- Archive command output to database
- Summarize long documents
- Request session context reset
- Split work into smaller chunks

## Maintenance Schedule

| Task | Frequency | Owner |
|------|-----------|-------|
| Archive old sessions | Weekly | Agent-1 |
| Update progress docs | Daily | Agent-1 |
| Validate database integrity | Daily | Agent-1 |
| Clean ephemeral cache | Weekly | Agent-1 |
| Review memory usage | Weekly | Agent-1 |
| Backup critical docs | Daily | Agent-1 |

---

**Version**: 1.0  
**Last Updated**: 2026-03-14  
**Status**: Active  
**Review Date**: 2026-03-21
