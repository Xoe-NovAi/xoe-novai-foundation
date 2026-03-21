---
document_type: protocol_specification
title: A2A_PROTOCOL_SPEC
version: 1.0
created_date: 2026-03-14
created_by: Phase 3 Deployment
status: active
scope: Agent-to-Agent Communication
---

# Agent-to-Agent (A2A) Protocol Specification v1.0

## Protocol Overview

The A2A Protocol enables secure, structured communication between autonomous agents in the omega-stack system. Agent-1 implements this protocol for multi-agent coordination.

## Communication Layers

### Layer 1: Message Transport
- **Channel**: Memory Bank file system
- **Format**: Markdown documents
- **Encoding**: UTF-8 with YAML frontmatter
- **Persistence**: Permanent file storage
- **Discovery**: Directory polling / file watching

### Layer 2: Message Structure
- **Envelope**: YAML frontmatter metadata
- **Payload**: Markdown content body
- **Integrity**: SHA-256 checksum
- **Version**: Semantic versioning

### Layer 3: Protocol Semantics
- **Request/Response**: Async message pairs
- **Acknowledgment**: Explicit status updates
- **Retry**: Exponential backoff (3 attempts)
- **Timeout**: 30 minutes per message

## Message Format

### Standard A2A Message

```yaml
---
document_type: a2a_message
from_agent: Agent-1
to_agent: Agent-N
message_id: a2a-20260314-001
timestamp: 2026-03-14T17:00:00Z
status: active
requires_ack: true
reply_to: [message_id or null]
priority: [high|normal|low]
ttl_minutes: 30
checksum_sha256: [hash]
---

# Message Title

## Context
[Background and context]

## Request/Update
[What is being requested or reported]

## Expected Response
[What response is needed, if any]

## Deadline
[Time by which response needed]

## Contact
[How to reach sender for clarification]
```

### Example A2A Message

```yaml
---
document_type: a2a_message
from_agent: Agent-1
to_agent: Agent-2
message_id: a2a-20260314-001
timestamp: 2026-03-14T17:00:00Z
status: active
requires_ack: true
reply_to: null
priority: high
ttl_minutes: 30
checksum_sha256: abcd1234...
---

# Phase 3 Deployment Status Report

## Context
Agent-1 has completed initial phase of hardened prompt deployment.

## Status Update
- System prompt v3.2 deployed: ✅
- Custom instructions loaded: ✅
- Memory bank integration verified: ✅
- Verification tests in progress: 🔄

## Request for Agent-2
Please run comprehensive verification tests on deployed artifacts:
1. Prompt integrity validation
2. Memory bank query tests
3. Multi-agent coordination scenario tests

## Expected Response
Test results in PHASE_3_VERIFICATION_RESULTS.md

## Deadline
2026-03-14 18:00 UTC

## Contact
Report issues via memory_bank/PHASE-3-DEPLOYMENT/ directory
```

## Agent Registry

### Agent-1: Execution Engine
- **Role**: Command execution and deployment
- **Status**: Active
- **Capabilities**: bash, build, test, deploy
- **Inbox**: `/memory_bank/messages/agent-1-inbox/`
- **Outbox**: `/memory_bank/messages/agent-1-outbox/`

### Agent-2: Verification & Testing
- **Role**: Test execution and validation
- **Status**: Active
- **Capabilities**: test definition, result analysis
- **Inbox**: `/memory_bank/messages/agent-2-inbox/`
- **Outbox**: `/memory_bank/messages/agent-2-outbox/`

### Agent-9: Design & Research
- **Role**: Design, prompt engineering, research
- **Status**: Active
- **Capabilities**: design, analysis, documentation
- **Inbox**: `/memory_bank/messages/agent-9-inbox/`
- **Outbox**: `/memory_bank/messages/agent-9-outbox/`

## Protocol Rules

### Rule 1: Message Validation
Every message MUST have:
- Valid YAML frontmatter
- Unique message_id
- Timestamp in ISO 8601 format
- From and To agent identification
- Content hash for integrity

### Rule 2: Acknowledgment Pattern
```
Request: Agent-1 → Agent-2
Acknowledge: Agent-2 → Agent-1 (within 5 minutes)
Response: Agent-2 → Agent-1 (within TTL)
Confirm: Agent-1 → Agent-2 (after processing)
```

### Rule 3: Priority Handling
- **high**: Process within 5 minutes
- **normal**: Process within 1 hour
- **low**: Process when available

### Rule 4: Timeout Behavior
```
TTL Start: Message timestamp
TTL Expire: timestamp + ttl_minutes
On Timeout: Send reminder, extend TTL
After 3 attempts: Escalate to system log
```

### Rule 5: Error Handling
```yaml
---
document_type: a2a_error
original_message_id: a2a-20260314-001
error_code: [ERROR_CODE]
error_message: [Human readable message]
resolution: [Suggested fix]
---
```

## Message Exchange Patterns

### Pattern 1: Request-Response (Synchronous)
```
1. Agent-1 sends request
2. Agent-2 acknowledges receipt
3. Agent-2 processes and responds
4. Agent-1 confirms receipt
5. Message expires after TTL
```

### Pattern 2: Broadcast (One-to-Many)
```
1. Agent-1 sends to multiple agents
2. Each agent acknowledges independently
3. Responses aggregated by Agent-1
4. Summary sent to all recipients
```

### Pattern 3: Pipeline (Sequential)
```
1. Agent-1 → Agent-2: handover
2. Agent-2 ← Agent-1: ack
3. Agent-2 → Agent-3: pass-through
4. Agent-3 ← Agent-2: ack
5. Agent-3 → Agent-1: results
```

## Implementation Checklist

### Setup Phase
- [ ] Create message directories for each agent
- [ ] Initialize message queues
- [ ] Configure retry policies
- [ ] Set up monitoring/logging

### Runtime Phase
- [ ] Validate all messages on receipt
- [ ] Compute checksums for integrity
- [ ] Track message lifecycle
- [ ] Log all exchanges

### Monitoring Phase
- [ ] Alert on timeouts
- [ ] Track delivery success rate
- [ ] Monitor queue depths
- [ ] Report protocol violations

## Examples

### A2A Query Example
```yaml
---
document_type: a2a_message
from_agent: Agent-1
to_agent: Agent-9
message_id: a2a-20260314-002
timestamp: 2026-03-14T17:05:00Z
status: active
requires_ack: true
priority: normal
---

# Enhanced Prompt Design Query

What are the recommended optimizations for the system prompt
based on the latest observability requirements?
```

### A2A Response Example
```yaml
---
document_type: a2a_response
from_agent: Agent-9
to_agent: Agent-1
message_id: a2a-20260314-003
reply_to: a2a-20260314-002
timestamp: 2026-03-14T17:10:00Z
status: active
---

# Enhanced Prompt Recommendations

Based on Phase 3 requirements:
1. Add explicit observability hooks
2. Strengthen error handling protocols
3. Enhance context window management
```

## Security Considerations

### Encryption
- All messages stored in plaintext in memory bank
- Use filesystem permissions for access control
- Consider encrypting sensitive payloads

### Authentication
- Agent identity verified by directory location
- Message integrity via SHA-256 checksum
- No additional authentication required

### Authorization
- File permissions control agent access
- Directory-based inbox/outbox isolation
- No central authorization server

## Troubleshooting

### Issue: Message Not Received
1. Check agent inbox exists
2. Verify message syntax
3. Check file permissions
4. Review system logs

### Issue: Timeout on Response
1. Check agent status
2. Review agent logs
3. Send reminder message
4. Escalate if critical

---

**Version**: 1.0  
**Status**: Active  
**Last Updated**: 2026-03-14  
**Next Review**: 2026-03-21
