---
priority: high
context: general
activation: always
last_updated: 2026-02-17
version: 1.0
---

# Multi-Agent Coordination

## Agent Roles
| Role | Focus | Memory Bank Reference |
|------|-------|----------------------|
| Architect | System design, patterns | `systemPatterns.md` |
| Coder | Implementation, testing | `activeContext.md`, `progress.md` |
| Security | Hardening, audits | `projectbrief.md` (constraints) |
| Documenter | MkDocs, API docs | All files |
| Researcher | Gap analysis, integration | `techContext.md` |

## Agent Bus Protocol
Redis Streams at `localhost:6379` for inter-agent communication.

### Message Format
```json
{
  "agent_id": "architect-001",
  "role": "architect",
  "action": "design_review",
  "payload": {...},
  "timestamp": "2026-02-17T12:00:00Z",
  "correlation_id": "uuid"
}
```

### Stream Channels
- `xnai:tasks` - Task assignments
- `xnai:results` - Completion notifications
- `xnai:alerts` - Error/issue broadcasts
- `xnai:heartbeat` - Agent health

## Coordination Patterns

### Handoff Protocol
1. Agent publishes task completion to `xnai:results`
2. Includes context summary for next agent
3. Next agent acknowledges via `xnai:tasks`

### Conflict Resolution
1. Multiple agents claim same task
2. Compare timestamps and agent priority
3. Lower priority agent yields
4. Log resolution to memory bank

### Circuit Breaker
Redis-backed persistent circuit breakers:
- Track failure rates per agent
- Open circuit after threshold
- Half-open for recovery testing
- Close on success

## Consul Integration
Service discovery at `localhost:8500`:
- Agent registration
- Health checks
- Configuration distribution

## Ed25519 Agent Handshakes
Cryptographic identity verification:
1. Agent generates Ed25519 keypair
2. Registers public key with IAM
3. Signs all messages
4. Recipients verify signature

## Task Management (Vikunja)
- Task creation: `POST /api/v1/tasks`
- Status updates via Agent Bus
- Priority alignment with `activeContext.md`

## Session Protocol
1. Agent reads memory bank
2. Checks Agent Bus for pending tasks
3. Executes assigned work
4. Publishes results
5. Updates memory bank
6. Heartbeat to Consul

## Monitoring
| Metric | Source | Threshold |
|--------|--------|-----------|
| Agent latency | Agent Bus | <500ms |
| Task queue depth | Redis | <100 |
| Heartbeat interval | Consul | 30s |
| Circuit breaker state | Redis | Monitor |

## Escalation
1. Agent fails 3 consecutive tasks
2. Circuit breaker opens
3. Alert broadcast to `xnai:alerts`
4. Human intervention flagged
5. Memory bank updated with incident
