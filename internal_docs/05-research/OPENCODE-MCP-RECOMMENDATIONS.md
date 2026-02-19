# OpenCode MCP Server Recommendations

## Overview

MCP (Model Context Protocol) servers extend OpenCode with external capabilities. This document covers recommended MCP servers for the XNAi Foundation stack.

## Foundation Stack MCP Servers

### 1. xnai-rag (Semantic Search)

Connects OpenCode to the Foundation RAG API.

**Purpose**: Enable semantic/lexical search across project knowledge.

**Tools**:
- `semantic_search`: Query the knowledge base
- `rag_health`: Check API health

**Configuration**:
```json
{
  "xnai-rag": {
    "command": "python",
    "args": ["mcp-servers/xnai-rag/server.py"],
    "env": {
      "RAG_API_URL": "http://localhost:8000"
    }
  }
}
```

**Use Cases**:
- Finding relevant code patterns
- Researching implementation approaches
- Context loading for tasks

### 2. xnai-agentbus (Multi-Agent Coordination)

Connects OpenCode to Redis Streams Agent Bus.

**Purpose**: Enable multi-agent task coordination.

**Tools**:
- `publish_task`: Send task to agent bus
- `read_results`: Read completed tasks
- `bus_health`: Check Redis connection

**Configuration**:
```json
{
  "xnai-agentbus": {
    "command": "python",
    "args": ["mcp-servers/xnai-agentbus/server.py"],
    "env": {
      "REDIS_URL": "redis://localhost:6379"
    }
  }
}
```

**Use Cases**:
- Parallel task execution
- Agent handoffs
- Result collection

### 3. xnai-vikunja (Task Management)

Connects OpenCode to Vikunja for task tracking.

**Purpose**: Create, update, and track tasks.

**Tools**:
- `list_projects`: List all projects
- `list_tasks`: List project tasks
- `create_task`: Create new task
- `update_task`: Update existing task
- `vikunja_health`: Check API health

**Configuration**:
```json
{
  "xnai-vikunja": {
    "command": "python",
    "args": ["mcp-servers/xnai-vikunja/server.py"],
    "env": {
      "VIKUNJA_URL": "http://localhost:3456",
      "VIKUNJA_TOKEN": "your-token"
    }
  }
}
```

**Use Cases**:
- Task creation from code analysis
- Progress tracking
- Sprint planning

## External MCP Servers

### Filesystem Access

```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"]
  }
}
```

### Git Operations

```json
{
  "git": {
    "command": "python",
    "args": ["-m", "mcp_server_git", "--repository", "."]
  }
}
```

### PostgreSQL Database

```json
{
  "postgres": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-postgres"],
    "env": {
      "POSTGRES_URL": "postgresql://user:pass@localhost/db"
    }
  }
}
```

## MCP Server Development

### Python Template

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("server-name")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="tool_name",
            description="Tool description",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {"type": "string"}
                },
                "required": ["param"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "tool_name":
        # Implementation
        return [TextContent(type="text", text="result")]
    return [TextContent(type="text", text="Unknown tool")]

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Requirements

```
mcp>=1.0.0
```

## Security Considerations

1. **Validate Inputs**: Sanitize all tool inputs
2. **Limit Scope**: Restrict file/database access
3. **Use Environment Variables**: Never hardcode secrets
4. **Audit Logging**: Log all tool invocations
5. **Rate Limiting**: Prevent abuse

## Performance Tuning

| Setting | Recommendation |
|---------|----------------|
| Timeout | 30s default |
| Max results | 100 items |
| Cache TTL | 5 minutes |
| Connection pool | 5 connections |

## Troubleshooting

### Server Not Starting
```bash
# Check Python path
which python

# Verify dependencies
pip install -r mcp-servers/server-name/requirements.txt

# Test directly
python mcp-servers/server-name/server.py
```

### Connection Refused
```bash
# Verify service is running
curl http://localhost:8000/health

# Check environment variables
env | grep API_URL
```

### Permission Denied
```bash
# Check file permissions
ls -la mcp-servers/

# Fix ownership
chown -R $(id -u):$(id -g) mcp-servers/
```
