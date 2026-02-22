# Phase Status Command

## Purpose
Check and report current phase status from memory bank.

## Usage
```
/phase-status
```

## Workflow
1. Read `memory_bank/progress.md`
2. Parse current phase and status
3. List completed milestones
4. Identify remaining tasks
5. Report blockers

## Output
```
## Phase Status Report

### Current Phase: 4
Status: In Progress
Started: 2026-02-01

### Completed
- [x] Agent Bus implementation
- [x] Consul service discovery
- [x] Redis Streams setup

### In Progress
- [ ] Circuit breaker persistence
- [ ] Ed25519 agent handshakes

### Blocked
- [Issue] Waiting for [dependency]

### Next Phase Preview
Phase 5: Production
- Deployment automation
- Monitoring setup
- Performance optimization
```

## Integration
- Uses `memory-bank-loader` skill
- Triggers `phase-validator` on demand
