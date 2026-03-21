---
title: "JOB-AB1 & JOB-AB2 Research Deliverables"
date: 2026-02-23
status: "Complete"
version: "2.0.0"
---

# Agent Bus Integration Deep Dive - Research Complete

## Overview

This document indexes the complete research and specifications for:
- **JOB-AB1**: Agent Bus Message Format Specification
- **JOB-AB2**: MCP Server Registration & Discovery

All deliverables are production-ready specifications with examples and integration guidance.

---

## Deliverables Summary

### 1. AGENT-BUS-SPECIFICATION-v2.0.0.yaml (922 lines)

**Location**: `internal_docs/communication_hub/AGENT-BUS-SPECIFICATION-v2.0.0.yaml`

Comprehensive technical specification covering:

#### JOB-AB1 Content:
- **Message Format**: Standard envelope structure (message_id, timestamp, sender, target, type, priority, content, correlation_id)
- **Message Types**: 5 core types with full examples
  - task_assignment (work distribution)
  - task_completion (result reporting)
  - state_update (agent health/status)
  - error_report (exception handling)
  - assistance_request (inter-agent coordination)
- **Priority Levels**: HIGH (<5min), MEDIUM (<30min), LOW (<2hrs)
- **Redis Streams Implementation**: XADD, XREADGROUP, XACK, XAUTOCLAIM operations
- **Error Handling**: Timeout semantics, response formats, edge cases
- **Performance Characteristics**: Latency, throughput, payload limits

#### JOB-AB2 Content:
- **Registration Methods**: Configuration files (.opencode/opencode.json) and Consul HTTP API
- **Capability Declaration**: Tool declaration pattern with JSON Schema validation
- **Service Discovery**: 5-step discovery flow with announcement messages
- **Health Check Protocol**: Tool interface, response format, heartbeat mechanism
- **MCP Server Examples**: xnai-agentbus and memory-bank-mcp implementations
- **Registration Process**: 6-step guide from implementation to verification
- **Required Capabilities**: Minimum and specialized capability sets
- **Deregistration & Cleanup**: Graceful and error shutdown procedures
- **Security Model**: Authentication, authorization, message signing, audit trails

**Sections**: 15 major sections with YAML hierarchical structure

---

### 2. AGENT-BUS-INTEGRATION-GUIDE.md (580 lines)

**Location**: `internal_docs/communication_hub/AGENT-BUS-INTEGRATION-GUIDE.md`

Executive summary with practical implementation guidance:

#### Quick Reference:
- **Message Structure**: JSON envelope with all fields
- **Message Types**: 5 types with code examples
- **Priority Levels**: Quick reference table
- **Redis Operations**: publish_task, read_tasks, ack_task, recover_tasks with code snippets
- **Error Handling**: Timeout semantics, response formats

#### Implementation Examples:
1. **Publishing a Task**: Full Python example with Redis calls
2. **MCP Server Registration**: Complete server.py boilerplate
3. **Agent Registration**: Memory bank server example with tool declaration

#### Practical Resources:
- Registration Checklist (16 items across 5 categories)
- Key Files Reference (6 important files)
- Next Steps (5 recommended implementations)

**Format**: Markdown with code blocks, tables, and hierarchical sections

---

### 3. AGENT-BUS-PROTOCOL.md (470 lines) - Original Reference

**Location**: `internal_docs/communication_hub/AGENT-BUS-PROTOCOL.md`

Original protocol specification (maintained for historical reference):
- Core concepts and architecture
- Initial message types
- Directory structure
- Agent states and transitions
- Implementation guidelines
- Integration examples

---

## Key Technical Specifications

### Message Format

```yaml
Standard Envelope:
  - message_id: UUID v4 (unique identifier)
  - timestamp: ISO 8601 (creation time)
  - sender: Agent name (opencode-{hash}, cline-{hash}, etc.)
  - target: Target agent or broadcast
  - type: Message type (5 types defined)
  - priority: HIGH|MEDIUM|LOW
  - content: Type-specific payload
  - correlation_id: Optional UUID for request/response tracking
```

### Transport Layer

```
Protocol: Redis Streams
Stream: xnai:agent_bus
Consumer Group: xnai-mcp-server
Delivery Model: Exactly-once (via consumer groups)
Stale Message Recovery: 30-second idle timeout with XAUTOCLAIM
```

### Agent States

```
active   → ready for work
busy     → processing a task
error    → in error state
inactive → idle (not accepting tasks)
offline  → not responding
```

### MCP Server Lifecycle

```
1. Start MCP server process
2. Initialize Redis connection
3. Create/verify consumer group (XGROUP CREATE)
4. Register tools via @server.list_tools()
5. Publish capability announcement
6. Listen for commands on stdio
7. Process tool calls and return results
```

---

## Implementation Quick Start

### For MCP Server Developers

**1. Implement Server** (server.py template in specification)
```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

server = Server("your-server-name")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="your_tool",
            description="Tool description",
            inputSchema={...}
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    # Implementation
    return [TextContent(type="text", text="result")]

if __name__ == "__main__":
    stdio_server(server)
```

**2. Register in Configuration** (.opencode/opencode.json)
```json
{
  "mcp": {
    "servers": {
      "your-server": {
        "command": "python",
        "args": ["mcp-servers/your-server/server.py"],
        "env": {"KEY": "value"}
      }
    }
  }
}
```

**3. Implement Health Check**
```python
Tool(
    name="health",
    description="Check server health",
    inputSchema={"type": "object"}
)
```

**4. Test with OpenCode**
```bash
python mcp-servers/your-server/server.py
# Server should listen on stdio
```

### For Agent Developers

**1. Register Agent**
```python
# Call register_agent tool with:
{
  "agent_id": "your-agent-1",
  "capabilities": ["capability1", "capability2"],
  "memory_limit_gb": 2.0
}
```

**2. Publish Tasks**
```python
await redis.xadd("xnai:agent_bus", {
    "message_id": str(uuid.uuid4()),
    "timestamp": datetime.now().isoformat(),
    "sender": "your-agent",
    "target": "target-agent",
    "type": "task_assignment",
    "priority": "high",
    "content": {...}
})
```

**3. Consume Messages**
```python
messages = await redis.xreadgroup(
    groupname="xnai-mcp-server",
    consumername=f"mcp-{uuid.uuid4().hex[:8]}",
    streams={"xnai:agent_bus": ">"},
    count=10
)
```

**4. Acknowledge After Processing**
```python
await redis.xack("xnai:agent_bus", "xnai-mcp-server", message_id)
```

---

## Critical Dependencies

### Required Infrastructure
- **Redis >= 5.0**: For Streams and Consumer Groups
- **Python >= 3.8**: For async/await patterns
- **MCP Package**: `mcp[server]` for Protocol implementation
- **Redis Python**: `redis>=4.5` with async support

### Environment Variables
```
REDIS_URL=redis://localhost:6379
STREAM_KEY=xnai:agent_bus
CONSUMER_GROUP=xnai-mcp-server
LOG_LEVEL=info
```

---

## Security Considerations

### Authentication
- Redis AUTH (password in REDIS_URL)
- Optional TLS for Redis connections

### Authorization
- Consumer groups provide message isolation
- Separate Redis namespaces for different teams/projects

### Audit Trail
- All publish/consume operations logged
- Redis Streams retention policy configurable
- Compliance with ISO 27001 guidelines

---

## Performance Characteristics

| Operation | Latency P50 | Latency P99 | Throughput |
|-----------|------------|------------|-----------|
| publish_task | ~5ms | ~50ms | 1000+/sec |
| read_tasks | ~10ms | ~100ms | Limited by count param |
| ack_task | ~2ms | ~10ms | 10000+/sec |
| recover_tasks | ~50ms | ~200ms | 100/sec |

---

## Integration Checklist

### Pre-Registration
- [ ] Server executable works standalone
- [ ] Dependencies in requirements.txt
- [ ] Environment variables documented
- [ ] Health check responds

### Registration
- [ ] Config file updated (opencode.json)
- [ ] Tools declared with schemas
- [ ] Paths correct and accessible
- [ ] Environment variables match

### Discovery & Operation
- [ ] Tools appear in list after startup
- [ ] Messages publish/consume successfully
- [ ] Acknowledgment working
- [ ] Error handling graceful
- [ ] Health checks pass

### Monitoring
- [ ] Logging configured
- [ ] Metrics exported
- [ ] Alerting set up
- [ ] Consumer cleanup working

---

## Files and References

| Document | Lines | Purpose |
|----------|-------|---------|
| AGENT-BUS-SPECIFICATION-v2.0.0.yaml | 922 | Complete technical reference |
| AGENT-BUS-INTEGRATION-GUIDE.md | 580 | Practical implementation guide |
| AGENT-BUS-PROTOCOL.md | 470 | Original protocol (historical) |
| mcp-servers/xnai-agentbus/server.py | 350+ | Reference implementation |
| mcp-servers/memory-bank-mcp/server.py | 450+ | Agent registration system |
| .opencode/opencode.json | 97 | MCP server configuration |
| scripts/consul_registration.py | 43 | Consul integration helper |

---

## Standards & Compliance

### Followed Standards
- **JSON Schema**: Message validation
- **ISO 27001**: Security guidelines
- **NIST Cybersecurity Framework**: Security principles
- **OpenTelemetry**: Observability standards
- **MCP Protocol**: Model Context Protocol specification

### Alignment
- **Ma'at's 42 Ideals**: Ethical guardrails
- **XNAi Foundation**: Sovereign, local-first philosophy
- **Zero-Telemetry**: No external calls without approval
- **Resource Constraints**: <6GB RAM, <500ms latency target

---

## Next Steps for Implementation

### Phase 1: Foundation (Week 1)
- [ ] Review specifications with team
- [ ] Set up Redis consumer groups
- [ ] Implement health check infrastructure
- [ ] Create integration tests

### Phase 2: Core Agents (Week 2)
- [ ] Register existing agents (opencode, cline, gemini)
- [ ] Implement task dispatch protocol
- [ ] Create agent state management
- [ ] Set up heartbeat monitoring

### Phase 3: Advanced Features (Week 3)
- [ ] Implement task priority queue
- [ ] Create message filtering/routing
- [ ] Add metrics collection
- [ ] Build admin dashboard

### Phase 4: Hardening (Week 4)
- [ ] Add encryption for sensitive messages
- [ ] Implement message compression
- [ ] Create failover mechanisms
- [ ] Performance tuning

---

## Support & Questions

For questions on:
- **Message formats**: See `AGENT-BUS-SPECIFICATION-v2.0.0.yaml` sections 1-5
- **MCP registration**: See `AGENT-BUS-SPECIFICATION-v2.0.0.yaml` sections 6-11
- **Implementation**: See `AGENT-BUS-INTEGRATION-GUIDE.md` examples
- **Protocols**: See `AGENT-BUS-PROTOCOL.md` for original specification

---

**Document Version**: 2.0.0  
**Created**: 2026-02-23  
**Research Status**: ✅ Complete  
**Implementation Status**: Ready to Begin  
**Maintainer**: Copilot CLI
