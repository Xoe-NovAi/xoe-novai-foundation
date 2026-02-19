# Vikunja Task Manager Skill

## Purpose
Create, update, and track tasks in Vikunja for project management.

## Trigger
- New task identified
- Task status change
- Planning session
- Phase transition

## Vikunja API Endpoints
Base URL: `http://localhost:3456/api/v1`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/projects` | GET | List projects |
| `/projects/{id}/tasks` | GET | List tasks |
| `/projects/{id}/tasks` | POST | Create task |
| `/tasks/{id}` | POST | Update task |
| `/tasks/{id}` | DELETE | Delete task |

## Task Structure
```json
{
  "title": "Implement feature X",
  "description": "Details...",
  "project_id": 1,
  "priority": 3,
  "labels": ["backend", "phase-4"],
  "due_date": "2026-02-20T00:00:00Z",
  "related_tasks": [123, 456]
}
```

## Priority Levels
| Level | Name | Response Time |
|-------|------|---------------|
| 1 | Critical | Immediate |
| 2 | High | Same day |
| 3 | Medium | This week |
| 4 | Low | Backlog |
| 5 | Someday | Future |

## Workflow

### Step 1: Identify Task
Parse user request or memory bank for task:
- Feature request
- Bug fix
- Documentation
- Refactoring

### Step 2: Create Task
```bash
curl -X POST http://localhost:3456/api/v1/projects/1/tasks \
  -H "Authorization: Bearer $VIKUNJA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "...",
    "description": "...",
    "priority": 3
  }'
```

### Step 3: Link Context
Connect task to:
- Memory bank reference
- Related Agent Bus tasks
- Phase in progress

### Step 4: Track Progress
Update task status:
- `todo` -> `in_progress` -> `done`
- Add comments for blockers
- Update due dates as needed

## Task Categories

| Label | Purpose |
|-------|---------|
| phase-1..7 | Phase tracking |
| backend | Core services |
| frontend | UI/UX |
| docs | Documentation |
| security | Security tasks |
| bug | Bug fixes |
| enhancement | Improvements |

## Output Format
```
## Task Created
ID: [task_id]
Title: [title]
Priority: [level]
Project: [project_name]
Labels: [labels]

### Next Steps
1. [step 1]
2. [step 2]
```

## Integration
- Syncs with `memory_bank/activeContext.md`
- Notifies `agent-bus-coordinator` of task assignments
- Triggers `phase-validator` on task completion

## Status Sync
Keep Vikunja and memory bank aligned:
```
Vikunja Task Status <-> activeContext.md priorities
Task completion -> progress.md update
```
