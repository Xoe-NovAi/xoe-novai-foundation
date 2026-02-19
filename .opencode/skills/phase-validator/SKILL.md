# Phase Validator Skill

## Purpose
Verify phase completion criteria and validate readiness for phase transitions.

## Trigger
- Phase completion claimed
- Milestone reached
- Phase transition requested

## Phase Definitions

| Phase | Name | Key Deliverables |
|-------|------|------------------|
| 1 | Foundation | Project structure, memory bank |
| 2 | Core Services | RAG API, Agent Bus |
| 3 | Voice Interface | TTS/STT integration |
| 4 | Multi-Agent | Agent orchestration |
| 5 | Production | Deployment, monitoring |
| 6 | Optimization | Performance tuning |
| 7 | Documentation | Complete docs |

## Validation Workflow

### Step 1: Read Phase Status
Load current phase from `memory_bank/progress.md`:
```markdown
## Current Phase: 4
Status: In Progress
Started: 2026-02-01
```

### Step 2: Check Completion Criteria
Validate each criterion:
- [ ] Required files exist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Memory bank reflects changes

### Step 3: Run Validation Tests
```bash
# Example validation commands
pytest tests/phase_4/ -v
mkdocs build --strict
podman ps --filter "name=xnai"
```

### Step 4: Generate Report
```
## Phase Validation Report
Phase: 4
Status: [READY/BLOCKED/INCOMPLETE]

### Completed
- [x] Agent Bus implementation
- [x] Consul integration

### Remaining
- [ ] Circuit breaker persistence
- [ ] Ed25519 handshakes

### Blockers
- [Issue description]

### Recommendation
[Proceed/Wait/Fix]
```

## Completion Criteria Template
Each phase must have:
1. **Files**: Required files created
2. **Tests**: Unit and integration tests passing
3. **Docs**: Documentation updated
4. **Memory Bank**: Progress recorded
5. **Security**: Audit passed (if applicable)

## Phase Transition Protocol
1. Validator confirms completion
2. Update `progress.md`
3. Notify via Agent Bus
4. Create Vikunja tasks for next phase

## Integration
- Triggers `memory-bank-loader` to update context
- Works with `sovereign-security-auditor` for security phases
- Notifies `vikunja-task-manager` of phase changes
