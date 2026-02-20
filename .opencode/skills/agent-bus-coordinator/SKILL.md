# Agent Bus Coordinator Skill

## Purpose
Coordinate multiple agents via Redis Streams for parallel work execution.

## Trigger
- Multi-agent tasks initiated
- Parallel execution needed
- Agent handoff required

## Redis Streams Channels

| Stream | Purpose |
|--------|---------|
| `xnai:agent_bus` | Task assignments and results |
| `xnai:alerts` | Error/issue broadcasts |
| `xnai:heartbeat` | Agent health |

## Message Format
```json
{
  "agent_id": "agent-001",
  "role": "coder",
  "action": "implement_feature",
  "payload": {
    "task": "...",
    "context": "..."
  },
  "timestamp": "2026-02-17T12:00:00Z",
  "correlation_id": "uuid-v4"
}
```

## Workflow

### Step 1: Task Analysis
Determine if task requires:
- Single agent (direct execution)
- Multiple agents (coordination needed)
- Sequential handoff (pipeline)

### Step 2: Agent Selection
Match task requirements to agent roles:
- **Architect**: System design, patterns
- **Coder**: Implementation, testing
- **Security**: Hardening, audits
- **Documenter**: MkDocs, API docs
- **Researcher**: Gap analysis

### Step 3: Task Distribution
1. Publish task to `xnai:agent_bus`
2. Wait for agent acknowledgment
3. Monitor execution via heartbeat
4. Collect results from `xnai:agent_bus`

### Step 4: Coordination
- Handle conflicts (priority-based resolution)
- Manage circuit breakers
- Track failure rates

## Handoff Protocol
```
[Agent A] -> xnai:agent_bus (completion + context)
[Agent B] <- xnai:agent_bus (next task + context)
[Agent B] -> xnai:agent_bus (acknowledgment)
```

## Error Handling
| Error | Action |
|-------|--------|
| Agent timeout | Retry with new agent |
| Circuit open | Fallback to single agent |
| Message loss | Replay from persistence |

## Consul Integration
Register agents with Consul for:
- Health checks
- Configuration distribution
- Service discovery

## Output
Report coordination status:
```
## Coordination Status
- Active agents: [count]
- Pending tasks: [count]
- Completed: [count]
- Circuit breakers: [status]
```
