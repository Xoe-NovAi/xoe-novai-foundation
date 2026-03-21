# Agent Bus Protocol v1.0.0

**Purpose**: Filesystem-based asynchronous message bus for autonomous multi-agent coordination in Xoe-NovAi Foundation Stack.

**Version**: 1.0.0  
**Last Updated**: 2026-02-14  
**Status**: Active

## Overview

The Agent Bus provides a standardized communication protocol for AI agents to coordinate tasks, share state, and perform handoffs without requiring synchronous communication or external message brokers.

## Architecture

```
Agent A → Outbox → Filesystem → Inbox → Agent B
                ↑
            State Persistence
```

## Message Format

### Standard Message Structure
```json
{
  "message_id": "uuid-v4",
  "timestamp": "2026-02-14T01:17:00Z",
  "sender": "agent-name",
  "target": "target-agent",
  "type": "message-type",
  "priority": "high|medium|low",
  "content": {
    "task": "task-name",
    "data": {...},
    "metadata": {...}
  },
  "correlation_id": "optional-uuid"
}
```

### Message Types

#### 1. Task Assignment
```json
{
  "type": "task_assignment",
  "content": {
    "task": "implement_circuit_breakers",
    "priority": "high",
    "deadline": "2026-02-21",
    "description": "Implement Redis-backed circuit breakers",
    "requirements": ["redis_connection", "graceful_degradation"],
    "deliverables": ["circuit_breaker_module", "tests", "documentation"]
  }
}
```

#### 2. Task Completion
```json
{
  "type": "task_completion",
  "content": {
    "task": "implement_circuit_breakers",
    "status": "success|failed|partial",
    "result": {
      "files_created": ["app/XNAi_rag_app/core/circuit_breakers/"],
      "tests_passed": 15,
      "performance_impact": "2%",
      "notes": "All requirements met"
    }
  }
}
```

#### 3. State Update
```json
{
  "type": "state_update",
  "content": {
    "agent": "cline-cli",
    "status": "active|inactive|busy|error",
    "current_task": "implement_circuit_breakers",
    "progress": 0.75,
    "memory_usage": "5.2GB",
    "last_heartbeat": "2026-02-14T01:17:00Z"
  }
}
```

#### 4. Error Report
```json
{
  "type": "error_report",
  "content": {
    "error_type": "redis_connection_failed",
    "message": "Cannot connect to Redis server",
    "stack_trace": "...",
    "context": {
      "agent": "cline-cli",
      "task": "implement_circuit_breakers",
      "timestamp": "2026-02-14T01:17:00Z"
    }
  }
}
```

#### 5. Request for Assistance
```json
{
  "type": "assistance_request",
  "content": {
    "request_type": "technical|research|validation",
    "description": "Need research on Redis circuit breaker patterns",
    "urgency": "high",
    "expected_response_time": "30m",
    "required_agents": ["opencode", "grok-mc"]
  }
}
```

## Directory Structure

```
internal_docs/communication_hub/
├── inbox/                    # Incoming messages for agents
│   ├── cline-cli_*.json
│   ├── gemini-cli_*.json
│   ├── opencode_*.json
│   └── grok-mc_*.json
├── outbox/                   # Outgoing messages from agents
│   ├── cline-cli_*.json
│   ├── gemini-cli_*.json
│   ├── opencode_*.json
│   └── grok-mc_*.json
├── state/                    # Agent state persistence
│   ├── cline-cli.json
│   ├── gemini-cli.json
│   ├── opencode.json
│   └── grok-mc.json
└── AGENT-BUS-PROTOCOL.md     # This protocol document
```

## Agent States

### State Schema
```json
{
  "agent_name": "string",
  "status": "active|inactive|busy|error|offline",
  "current_task": "string|null",
  "progress": 0.0-1.0,
  "last_heartbeat": "timestamp",
  "capabilities": ["list", "of", "capabilities"],
  "memory_usage": "string",
  "error_count": 0,
  "success_count": 0,
  "total_tasks": 0
}
```

### State Transitions
- **active** → **busy**: When accepting a new task
- **busy** → **active**: When task completed successfully
- **busy** → **error**: When task fails
- **error** → **active**: After error resolution
- **any** → **offline**: When agent becomes unavailable

## Priority Levels

### High Priority
- Critical system failures
- Security vulnerabilities
- Production outages
- **Response Time**: <5 minutes

### Medium Priority
- Feature implementations
- Performance optimizations
- Documentation updates
- **Response Time**: <30 minutes

### Low Priority
- Research tasks
- Code reviews
- Minor improvements
- **Response Time**: <2 hours

## Implementation Guidelines

### For Agent Implementers

1. **Message Processing**
   ```python
   def process_messages(agent_name):
       inbox_dir = Path(f"internal_docs/communication_hub/inbox")
       message_files = list(inbox_dir.glob(f"{agent_name}_*.json"))
       
       for msg_file in message_files:
           with open(msg_file, 'r') as f:
               message = json.load(f)
           
           # Process message based on type
           handle_message(message)
           
           # Archive message
           msg_file.unlink()
   ```

2. **State Management**
   ```python
   def update_agent_state(agent_name, updates):
       state_file = Path(f"internal_docs/communication_hub/state/{agent_name}.json")
       
       if state_file.exists():
           with open(state_file, 'r') as f:
               state = json.load(f)
       else:
           state = {"agent_name": agent_name}
       
       state.update(updates)
       state["last_heartbeat"] = datetime.utcnow().isoformat()
       
       with open(state_file, 'w') as f:
           json.dump(state, f, indent=2)
   ```

3. **Message Sending**
   ```python
   def send_message(target_agent, message_type, content, priority="medium"):
       message = {
           "message_id": str(uuid.uuid4()),
           "timestamp": datetime.utcnow().isoformat(),
           "sender": "current-agent",
           "target": target_agent,
           "type": message_type,
           "priority": priority,
           "content": content
       }
       
       outbox_dir = Path("internal_docs/communication_hub/outbox")
       filename = f"{target_agent}_{int(time.time())}.json"
       message_file = outbox_dir / filename
       
       with open(message_file, 'w') as f:
           json.dump(message, f, indent=2)
   ```

### For System Integrators

1. **Watcher Scripts**
   ```bash
   # scripts/agent_watcher.sh
   #!/bin/bash
   
   AGENT_NAME="cline-cli"
   WATCH_INTERVAL=30
   
   while true; do
       # Check for new messages
       MESSAGE_COUNT=$(ls -1 internal_docs/communication_hub/inbox/${AGENT_NAME}_*.json 2>/dev/null | wc -l)
       
       if [ $MESSAGE_COUNT -gt 0 ]; then
           echo "[$(date)] New messages for $AGENT_NAME: $MESSAGE_COUNT"
           # Trigger agent processing
           python3 scripts/process_messages.py $AGENT_NAME
       fi
       
       # Update heartbeat
       python3 scripts/update_heartbeat.py $AGENT_NAME
       
       sleep $WATCH_INTERVAL
   done
   ```

2. **Health Monitoring**
   ```python
   # scripts/agent_health_monitor.py
   import json
   from pathlib import Path
   from datetime import datetime, timedelta
   
   def check_agent_health():
       state_dir = Path("internal_docs/communication_hub/state")
       agents = ["cline-cli", "gemini-cli", "opencode", "grok-mc"]
       
       for agent in agents:
           state_file = state_dir / f"{agent}.json"
           if state_file.exists():
               with open(state_file, 'r') as f:
                   state = json.load(f)
               
               last_heartbeat = datetime.fromisoformat(state["last_heartbeat"])
               if datetime.utcnow() - last_heartbeat > timedelta(minutes=10):
                   print(f"WARNING: {agent} heartbeat stale")
           else:
               print(f"WARNING: {agent} state file missing")
   ```

## Error Handling

### Message Processing Errors
- Log errors to agent-specific log files
- Mark message as failed in state
- Send error report to sender if correlation_id present
- Retry mechanism: 3 attempts with exponential backoff

### Agent Failures
- Automatic detection via heartbeat monitoring
- Task reassignment to available agents
- State preservation for recovery
- Escalation to human operator if needed

### Filesystem Issues
- Atomic file operations to prevent corruption
- Backup state files before updates
- Graceful degradation when filesystem unavailable
- Alert generation for persistent issues

## Security Considerations

### Authentication
- Agent names must be whitelisted
- Message signing for critical operations
- File permissions: 600 for state files, 644 for messages

### Authorization
- Agents can only send to authorized targets
- Priority escalation requires approval
- Sensitive operations require multi-agent approval

### Audit Trail
- All messages archived for compliance
- State changes logged with timestamps
- Error reports include full context

## Performance Optimization

### Message Batching
- Group multiple messages for efficiency
- Priority-based processing order
- Background processing for low-priority items

### State Caching
- In-memory state caching for frequently accessed data
- Periodic persistence to disk
- State compression for large datasets

### Cleanup
- Automatic cleanup of old messages (7 days retention)
- State file size limits with rotation
- Archive important messages to long-term storage

## Integration Examples

### Cline CLI Integration
```python
# scripts/cline_cli_integration.py
import json
from pathlib import Path
import time

class ClineCLI:
    def __init__(self):
        self.agent_name = "cline-cli"
        self.capabilities = ["code_generation", "refactoring", "testing"]
        
    def process_inbox(self):
        inbox_dir = Path("internal_docs/communication_hub/inbox")
        message_files = list(inbox_dir.glob(f"{self.agent_name}_*.json"))
        
        for msg_file in message_files:
            with open(msg_file, 'r') as f:
                message = json.load(f)
            
            self.handle_message(message)
            msg_file.unlink()
    
    def handle_message(self, message):
        if message["type"] == "task_assignment":
            self.execute_task(message["content"])
        elif message["type"] == "state_update":
            self.update_state(message["content"])
        elif message["type"] == "assistance_request":
            self.respond_to_assistance(message["content"])
    
    def execute_task(self, task_content):
        # Task execution logic
        pass
```

### Multi-Agent Coordination
```python
# scripts/multi_agent_coordinator.py
import json
from pathlib import Path
import time

class MultiAgentCoordinator:
    def __init__(self):
        self.agents = {
            "cline-cli": {"priority": 1, "capabilities": ["code"]},
            "gemini-cli": {"priority": 2, "capabilities": ["execution"]},
            "opencode": {"priority": 3, "capabilities": ["research"]},
            "grok-mc": {"priority": 4, "capabilities": ["strategy"]}
        }
    
    def assign_task(self, task, target_agents=None):
        if not target_agents:
            target_agents = list(self.agents.keys())
        
        for agent in target_agents:
            message = {
                "type": "task_assignment",
                "content": task,
                "priority": "medium"
            }
            self.send_message(agent, message)
    
    def send_message(self, target_agent, message):
        outbox_dir = Path("internal_docs/communication_hub/outbox")
        filename = f"{target_agent}_{int(time.time())}.json"
        message_file = outbox_dir / filename
        
        with open(message_file, 'w') as f:
            json.dump(message, f, indent=2)
```

## Version History

### v1.0.0 (2026-02-14)
- Initial protocol specification
- Core message types defined
- State management system
- Multi-agent coordination patterns

## Future Enhancements

### Planned Features
- Message encryption for sensitive communications
- Message compression for large payloads
- Webhook integration for external systems
- Real-time dashboard for monitoring
- Advanced scheduling and queuing

### Research Areas
- Machine learning for message routing optimization
- Blockchain-based message integrity
- Federated agent coordination
- Quantum-resistant encryption

## Compliance & Standards

This protocol follows:
- JSON Schema standards for message validation
- ISO 27001 guidelines for security
- NIST Cybersecurity Framework principles
- OpenTelemetry standards for observability

## Support

For protocol questions or issues:
1. Check agent state files for error details
2. Review message logs in inbox/outbox directories
3. Consult this protocol document
4. Escalate to Grok MC for strategic issues

---

**Protocol Maintainer**: Cline CLI  
**Last Review**: 2026-02-14  
**Next Review**: 2026-05-14