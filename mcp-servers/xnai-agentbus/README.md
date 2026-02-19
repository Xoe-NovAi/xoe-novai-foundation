# XNAi Agent Bus MCP Server

MCP server providing Redis Streams integration for multi-agent coordination.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Add to `.opencode/opencode.json`:

```json
{
  "mcp": {
    "servers": {
      "xnai-agentbus": {
        "command": "python",
        "args": ["mcp-servers/xnai-agentbus/server.py"],
        "env": {
          "REDIS_URL": "redis://localhost:6379"
        }
      }
    }
  }
}
```

## Tools

### publish_task

Publish a task to the Agent Bus.

**Parameters:**
- `role` (string, required): Agent role (architect, coder, security, documenter, researcher)
- `action` (string, required): Action to perform
- `payload` (object, required): Task payload

**Example:**
```json
{
  "role": "coder",
  "action": "implement_feature",
  "payload": {
    "feature": "authentication",
    "priority": "high"
  }
}
```

### read_results

Read results from the Agent Bus.

**Parameters:**
- `count` (integer): Number of results to read (default: 10)

### bus_health

Check Redis connection health.

## Streams

| Stream | Purpose |
|--------|---------|
| xnai:tasks | Task assignments |
| xnai:results | Completion notifications |
| xnai:alerts | Error/issue broadcasts |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| REDIS_URL | redis://localhost:6379 | Redis connection URL |
