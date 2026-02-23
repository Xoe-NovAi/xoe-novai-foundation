# CLI Dispatch Templates and Protocols

**Version**: 1.0.0
**Created**: 2026-02-23
**Owner**: MC-Overseer Agent

---

## 1. Dispatch Protocol

### 1.1 Pre-Dispatch Checklist

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Read target agent's context file | `memory_bank/strategies/ACTIVE-TASK-DISPATCH-*.md` |
| 2 | Verify task is not blocked | Check dependencies |
| 3 | Assign unique task ID | Format: `CLI-YYYYMMDD-HHMMSS-NN` |
| 4 | Create dispatch prompt | Use template below |
| 5 | Publish to Agent Bus | `xnai:agent_bus` stream |
| 6 | Execute dispatch command | Via bash tool |
| 7 | Monitor output | Capture results |
| 8 | Update memory bank | Record completion |

### 1.2 Agent Bus Publication

Before dispatching, publish to Agent Bus:

```bash
redis-cli -a "$REDIS_PASS" --no-auth-warning XADD xnai:agent_bus '*' \
    sender 'did:xnai:mc-overseer-v1' \
    action 'dispatch' \
    target_agent 'did:xnai:cline-1' \
    task_id 'CLI-20260223-123456-01' \
    task_type 'implementation' \
    timestamp "$(date -Iseconds)" \
    status 'dispatched'
```

---

## 2. Cline CLI Dispatch Template

### 2.1 Standard Dispatch Command

```bash
timeout 600 cline --yolo --json --timeout 300 --model z-ai/glm-5 "PROMPT_HERE" 2>&1 | tee /tmp/cline-dispatch-TASK_ID.log
```

### 2.2 Full Prompt Template

```
You are CLINE-N (where N is your instance number).

## Identity
- Agent ID: did:xnai:cline-N
- CLI: Cline CLI
- Model: z-ai/glm-5
- Session: TASK_ID

## Coordination Key
Search for: ACTIVE-TASK-DISPATCH-WAVE-3-2026-02-23

## Your Assigned Tasks
[TASK LIST FROM DISPATCH DOCUMENT]

## Critical Instructions

1. **Read Context First**: Read memory_bank/activeContext.md and memory_bank/strategies/ACTIVE-TASK-DISPATCH-WAVE-3-2026-02-23.md before starting.

2. **Use Subagents**: For complex tasks, use your subagent feature by calling the Task tool with appropriate subagent_type:
   - `general` for complex multi-step tasks
   - `explore` for codebase exploration
   - `review` for code review
   - `security` for security audits

3. **Update Memory Bank**: After completing tasks, update:
   - memory_bank/progress.md
   - memory_bank/WAVE-3-PROGRESS.md (create if needed)
   - memory_bank/activeContext.md

4. **Report Issues**: If you encounter blockers, document them and publish to xnai:agent_bus:
   ```bash
   redis-cli -a "changeme123" --no-auth-warning XADD xnai:agent_bus '*' \
       sender 'did:xnai:cline-N' \
       action 'blocked' \
       task_id 'TASK_ID' \
       issue 'DESCRIPTION'
   ```

5. **Research Gaps**: If you find knowledge gaps outside your task scope, create research jobs in:
   - expert-knowledge/research/NEW-RESEARCH-TOPIC-YYYY-MM-DD.md

6. **Complete Thoroughly**: Do not partially complete tasks. Either complete fully or document why you cannot.

## Deliverables Location
[EXPECTED OUTPUT FILES]

## Success Criteria
[MEASURABLE OUTCOMES]

## Timeout
You have 10 minutes to complete this dispatch. Work efficiently.
```

---

## 3. MC-Overseer Self-Dispatch Protocol

### 3.1 Own Task Assignment

As MC-Overseer, I maintain these responsibilities during multi-agent dispatch:

| Responsibility | Method |
|----------------|--------|
| **Coordination** | Monitor Agent Bus for status updates |
| **Research** | Fill knowledge gaps discovered by agents |
| **Documentation** | Update dispatch history and lessons learned |
| **Quality Gate** | Verify agent outputs meet standards |
| **Memory Bank** | Keep all files synchronized |

### 3.2 Parallel Work Strategy

```
Timeline:
T+0:00  - Dispatch Cline-1
T+0:30  - Dispatch Cline-2 (offset to prevent resource contention)
T+1:00  - Begin MC-Overseer tasks (research, documentation)
T+5:00  - Check agent progress
T+10:00 - Collect results, update memory bank
```

---

## 4. Agent Communication Protocol

### 4.1 Status Messages

| Status | Agent Bus Field | Description |
|--------|-----------------|-------------|
| `dispatched` | action | Task assigned |
| `started` | action | Work begun |
| `progress` | action | Checkpoint update |
| `blocked` | action | Cannot proceed |
| `complete` | action | Task finished |
| `failed` | action | Task failed |

### 4.2 Redis Stream Structure

```
Stream: xnai:agent_bus
Fields:
  - sender: DID of sending agent
  - action: Status/action type
  - target_agent: DID of recipient (if applicable)
  - task_id: Unique task identifier
  - task_type: Category of task
  - timestamp: ISO 8601 timestamp
  - status: Current status
  - details: JSON-encoded details
  - memory_bank_update: Boolean (if memory bank was updated)
```

---

## 5. Output Capture Protocol

### 5.1 Log Files

Each dispatch creates a log file:

```
/tmp/cline-dispatch-TASK_ID.log
```

### 5.2 Output Parsing

For JSON output mode (`--json`), parse with:

```python
import json

def parse_cline_output(log_file):
    results = []
    with open(log_file) as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                results.append(data)
            except json.JSONDecodeError:
                continue
    return results
```

---

## 6. Error Handling

### 6.1 Common Errors

| Error | Cause | Resolution |
|-------|-------|------------|
| `Timeout` | Task exceeded time limit | Increase timeout or simplify task |
| `SIGTERM` | Process killed | Check system resources |
| `Connection refused` | Redis unavailable | Verify Redis is running |
| `ImportError` | Missing dependency | Install required packages |

### 6.2 Recovery Procedure

1. Check log file for error details
2. Publish failure to Agent Bus
3. Document in dispatch history
4. Assign to next available agent or self

---

## 7. Success Metrics

| Metric | Target |
|--------|--------|
| Dispatch Success Rate | >95% |
| Average Task Completion | <10 min |
| Memory Bank Update Rate | 100% |
| Agent Bus Publication | 100% |

---

## 8. Template Quick Reference

### Minimal Dispatch
```bash
cline --yolo --timeout 300 "Read memory_bank/activeContext.md. [TASK]. Update memory_bank on completion."
```

### Full Dispatch with Subagents
```bash
timeout 600 cline --yolo --json --timeout 300 --model z-ai/glm-5 "
You are CLINE-1 (did:xnai:cline-1).

## Coordination Key: ACTIVE-TASK-DISPATCH-WAVE-3-2026-02-23

## Tasks:
1. [TASK 1]
2. [TASK 2]

## Instructions:
- Use Task tool with subagent_type for complex work
- Update memory_bank after completion
- Publish status to xnai:agent_bus

Timeout: 10 minutes.
" 2>&1 | tee /tmp/cline-dispatch-CLI-$(date +%Y%m%d-%H%M%S).log
```

---

**Last Updated**: 2026-02-23
**Next Review**: After first multi-agent dispatch
