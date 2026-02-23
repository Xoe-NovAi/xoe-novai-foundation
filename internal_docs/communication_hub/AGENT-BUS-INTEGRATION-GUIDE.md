# Agent Bus Integration Guide
## JOB-AB1 & JOB-AB2 Research Summary

**Version**: 2.0.0  
**Date**: 2026-02-23  
**Status**: Research Complete  

---

## Executive Summary

This document summarizes the research for Agent Bus message format specification (JOB-AB1) and MCP server registration & discovery (JOB-AB2). Complete YAML specification available in `AGENT-BUS-SPECIFICATION-v2.0.0.yaml`.

---

## JOB-AB1: Agent Bus Message Format

### Current Architecture

**Transport**: Redis Streams with Consumer Groups
- **Stream Key**: `xnai:agent_bus`
- **Consumer Group**: `xnai-mcp-server`
- **Consumer Format**: `mcp-{8-char-uuid-hex}`

### Message Structure

All messages follow this standard envelope:

```json
{
  "message_id": "uuid-v4",
  "timestamp": "ISO-8601",
  "sender": "agent-name",
  "target": "target-agent",
  "type": "message_type",
  "priority": "high|medium|low",
  "content": { /* type-specific payload */ },
  "correlation_id": "optional-uuid"
}
```

### Message Types

#### 1. Task Assignment
```json
{
  "type": "task_assignment",
  "content": {
    "task": "task_name",
    "priority": "high",
    "deadline": "2026-02-28",
    "description": "What needs to be done",
    "requirements": ["requirement1", "requirement2"],
    "deliverables": ["deliverable1", "deliverable2"]
  }
}
```

#### 2. Task Completion
```json
{
  "type": "task_completion",
  "content": {
    "task": "task_name",
    "status": "success|failed|partial",
    "result": {
      "files_created": ["file1", "file2"],
      "tests_passed": 15,
      "performance_impact": "2%",
      "notes": "Summary of work"
    }
  }
}
```

#### 3. State Update
```json
{
  "type": "state_update",
  "content": {
    "agent": "agent-id",
    "status": "active|inactive|busy|error|offline",
    "current_task": "task_name",
    "progress": 0.65,
    "memory_usage_mb": 512.3,
    "last_heartbeat": "2026-02-23T14:30:00Z"
  }
}
```

#### 4. Error Report
```json
{
  "type": "error_report",
  "content": {
    "error_type": "connection_failed",
    "message": "Human-readable error message",
    "severity": "critical|error|warning",
    "context": {
      "agent": "agent-id",
      "task": "task_name",
      "timestamp": "2026-02-23T14:30:00Z"
    }
  }
}
```

#### 5. Assistance Request
```json
{
  "type": "assistance_request",
  "content": {
    "request_type": "technical|research|validation|code_review",
    "description": "What help is needed",
    "urgency": "high|medium|low",
    "expected_response_time_minutes": 30,
    "required_agents": ["agent-role-*"]
  }
}
```

### Priority Levels

| Level  | Response Time | Use Cases |
|--------|---------------|-----------|
| High   | < 5 min       | Critical failures, security, production outages |
| Medium | < 30 min      | Features, optimization, documentation |
| Low    | < 2 hours     | Research, code reviews, improvements |

### Redis Streams Operations

#### Publish Message
```python
# Tool: publish_task
# Operation: XADD xnai:agent_bus * {message_dict}
# Returns: message_id (e.g., "1614059222062-0")

response = await redis_client.xadd(
    "xnai:agent_bus",
    {
        "agent_id": "opencode-abc123",
        "role": "coder",
        "action": "implement_feature",
        "payload": json.dumps(payload),
        "target_did": "",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlation_id": str(uuid.uuid4()),
    }
)
```

#### Consume Messages
```python
# Tool: read_tasks
# Operation: XREADGROUP GROUP xnai-mcp-server {consumer} STREAMS xnai:agent_bus >
# Returns: Messages with entry_id (delivered once per consumer)

results = await redis_client.xreadgroup(
    groupname="xnai-mcp-server",
    consumername="mcp-a1b2c3d4",
    streams={"xnai:agent_bus": ">"},
    count=10,
    block=100  # milliseconds
)
```

#### Acknowledge Message
```python
# Tool: ack_task
# Operation: XACK xnai:agent_bus xnai-mcp-server {message_id}
# Effect: Marks message as processed, removes from pending list

acked = await redis_client.xack(
    "xnai:agent_bus",
    "xnai-mcp-server",
    "1614059222062-0"
)
```

#### Recover Stale Messages
```python
# Tool: recover_tasks
# Operation: XAUTOCLAIM xnai:agent_bus xnai-mcp-server {consumer} 30000 0
# Purpose: Reclaim messages idle >30 seconds (crashed consumers)

recovered = await redis_client.xautoclaim(
    "xnai:agent_bus",
    "xnai-mcp-server",
    "mcp-xyz789",
    30000,  # min idle time in milliseconds
    "0"     # start ID
)
```

### Error Handling

#### Timeout Semantics
- **Default Block**: 100ms per read
- **Message Stale Timeout**: 30 seconds without acknowledgment
- **Automatic Recovery**: XAUTOCLAIM reassigns stale messages
- **Consumer Timeout**: 90 seconds (3x heartbeat interval)

#### Response Format
```json
{
  "status": "error|success",
  "error": "error_description (if error)",
  "message_id": "uuid (if success)",
  "detail": "additional_information"
}
```

---

## JOB-AB2: MCP Server Registration & Discovery

### Registration Methods

#### 1. Configuration File Registration (Recommended)

**File**: `.opencode/opencode.json`

```json
{
  "mcp": {
    "servers": {
      "xnai-agentbus": {
        "command": "python",
        "args": ["mcp-servers/xnai-agentbus/server.py"],
        "env": {
          "REDIS_URL": "redis://localhost:6379",
          "LOG_LEVEL": "info",
          "CONSUMER_GROUP": "xnai-mcp-server"
        }
      }
    }
  }
}
```

**Required Fields**:
- `command`: Executable to run
- `args`: Command-line arguments
- `env`: Environment variables

#### 2. Consul Service Registration (Advanced)

**Endpoint**: `PUT /v1/agent/service/register`

```json
{
  "Name": "xnai-agentbus",
  "ID": "xnai-agentbus-1",
  "Port": 3000,
  "Address": "localhost",
  "Tags": ["mcp-server", "agent-bus", "redis"],
  "Check": {
    "HTTP": "http://localhost:3000/health",
    "Interval": "10s",
    "Timeout": "5s"
  }
}
```

### Capability Advertisement

MCP servers advertise tools via the `@server.list_tools()` method:

```python
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="publish_task",
            description="Publish a task to the Agent Bus for multi-agent coordination",
            inputSchema={
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "description": "Agent role (architect, coder, security, documenter, researcher)"
                    },
                    "action": {
                        "type": "string",
                        "description": "Action to perform"
                    },
                    "payload": {
                        "type": "object",
                        "description": "Task payload"
                    },
                    "target_did": {
                        "type": "string",
                        "description": "Optional target agent DID"
                    }
                },
                "required": ["role", "action", "payload"]
            }
        ),
        # Additional tools...
    ]
```

### Service Discovery

#### Discovery Flow

1. **Configuration Scanning**: Read `.opencode/opencode.json`
2. **Server Startup**: Launch MCP server process
3. **Consumer Group Creation**: Ensure Redis consumer group exists (XGROUP CREATE)
4. **Capability Announcement**: Publish capability message to stream
5. **Agent Discovery**: Other agents read announcements from stream
6. **Caching**: Store capability information in memory/Redis

#### Announcement Message Format

```json
{
  "type": "capability_announcement",
  "content": {
    "consumer_name": "mcp-a1b2c3d4",
    "capabilities": [
      "publish_task",
      "read_tasks",
      "ack_task",
      "recover_tasks",
      "bus_health"
    ],
    "version": "1.0.0",
    "timestamp": "2026-02-23T14:30:00Z"
  }
}
```

### Health Check Protocol

#### Health Check Tool

```python
Tool(
    name="bus_health",
    description="Check Redis connection and consumer group health",
    inputSchema={"type": "object", "properties": {}}
)
```

#### Health Check Response

```json
{
  "status": "healthy|degraded|unhealthy",
  "redis_connection": true,
  "consumer_group": "xnai-mcp-server",
  "message_lag": 0,
  "last_check_ms": 42,
  "timestamp": "2026-02-23T14:30:00Z"
}
```

#### Heartbeat Mechanism

- **Interval**: 30 seconds
- **Timeout Threshold**: 90 seconds (3x heartbeat)
- **Stale Detection**: Agent timestamp - now > timeout_threshold
- **Action**: Remove from registry, send error_report to all agents

---

## Implementation Examples

### Example 1: Publishing a Task

```python
# Agent: opencode-abc123
# Action: Publish task to Agent Bus

message = {
    "message_id": str(uuid.uuid4()),
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "sender": "opencode-abc123",
    "target": "cline-cli",
    "type": "task_assignment",
    "priority": "high",
    "correlation_id": str(uuid.uuid4()),
    "content": {
        "task": "implement_auth",
        "description": "Implement JWT-based authentication",
        "requirements": ["jwt", "redis_session", "password_hashing"],
        "deliverables": ["auth_module", "tests", "docs"]
    }
}

# Step 1: Publish to Redis Stream
message_id = await redis_client.xadd("xnai:agent_bus", message)
# Returns: "1614059222062-0"

# Step 2: Other agents consume message
# Step 3: cline-cli processes task and publishes completion
# Step 4: Completion message acknowledged with XACK
```

### Example 2: MCP Server Registration

```python
# File: mcp-servers/xnai-agentbus/server.py

from mcp.server import Server
from mcp.server.stdio import stdio_server
import redis.asyncio as redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
STREAM_KEY = "xnai:agent_bus"
CONSUMER_GROUP = "xnai-mcp-server"

server = Server("xnai-agentbus")
redis_client = None

async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    return redis_client

async def ensure_consumer_group(r):
    try:
        await r.xgroup_create(
            name=STREAM_KEY,
            groupname=CONSUMER_GROUP,
            id="0",
            mkstream=True
        )
    except redis.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="publish_task",
            description="Publish a task to the Agent Bus",
            # ... inputSchema ...
        ),
        # ... more tools ...
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    r = await get_redis()
    await ensure_consumer_group(r)
    
    if name == "publish_task":
        # Implementation
        pass
    return [TextContent(type="text", text="result")]

if __name__ == "__main__":
    stdio_server(server)
```

### Example 3: Agent Registration

```python
# File: mcp-servers/memory-bank-mcp/server.py

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="register_agent",
            description="Register an agent with its capabilities",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "Unique agent identifier"
                    },
                    "capabilities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of capabilities"
                    },
                    "memory_limit_gb": {
                        "type": "number",
                        "description": "Max memory in GB"
                    }
                },
                "required": ["agent_id", "capabilities", "memory_limit_gb"]
            }
        )
    ]

async def register_agent(agent_id, capabilities, memory_limit_gb):
    capability = AgentCapability(
        agent_id=agent_id,
        capabilities=capabilities,
        memory_limit_gb=memory_limit_gb,
        last_seen=datetime.now(),
        performance_score=0.0
    )
    
    # Store in memory
    self.agents[agent_id] = capability
    
    # Persist to Redis
    await self.redis.hset(
        f"memory_bank:agents:{agent_id}",
        mapping=asdict(capability)
    )
    
    return {
        "status": "success",
        "agent_id": agent_id,
        "capabilities": capabilities,
        "registration_time": datetime.now().isoformat()
    }
```

---

## Registration Checklist

### Pre-Registration
- [ ] MCP server executable works standalone
- [ ] All dependencies in requirements.txt
- [ ] Environment variables documented
- [ ] Health check endpoint responds

### Registration
- [ ] `.opencode/opencode.json` updated with server config
- [ ] Tools properly declared with JSON Schema
- [ ] Command and args paths are correct
- [ ] Environment variables match server expectations

### Discovery
- [ ] Server appears in tool list after startup
- [ ] Capability names are unique and descriptive
- [ ] Input schemas are valid JSON Schema

### Operation
- [ ] Messages published successfully
- [ ] Messages consumed by target agents
- [ ] Acknowledgment mechanism working
- [ ] Error handling graceful
- [ ] Health checks pass

### Monitoring
- [ ] Logging captures all errors
- [ ] Metrics exported to monitoring system
- [ ] Alerting configured for failures
- [ ] Stale consumer cleanup working

---

## Key Files

| File | Purpose |
|------|---------|
| `internal_docs/communication_hub/AGENT-BUS-PROTOCOL.md` | Original protocol specification |
| `internal_docs/communication_hub/AGENT-BUS-SPECIFICATION-v2.0.0.yaml` | Complete technical specification |
| `mcp-servers/xnai-agentbus/server.py` | Redis Streams MCP server implementation |
| `mcp-servers/memory-bank-mcp/server.py` | Agent capability registration and memory management |
| `.opencode/opencode.json` | MCP server configuration |
| `scripts/consul_registration.py` | Consul service registration helper |

---

## Next Steps

1. **Implement Task Gateway**: Create async task gateway for external CLI dispatch
2. **Credential Management**: Implement Consul KV store for secret management
3. **Dashboard**: Build usage tracking and account rotation dashboard
4. **Integration Tests**: Create comprehensive integration test suite
5. **Monitoring**: Set up metrics collection and alerting

---

**Created by**: Copilot CLI  
**Research Phase**: Complete  
**Implementation Status**: Ready for development
