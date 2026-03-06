# XNAi Memory Bank MCP Server

MCP server exposing XNAi's MemGPT-style hierarchical memory architecture.

## Features

- **Resources**: Access memory bank files via `memory://bank/{path}` URIs
- **Tools**: Load context, search memory, check block status
- **Prompts**: Templates for common memory operations

## Installation

```bash
uv pip install -e .
```

## Usage

### With Claude Desktop

Add to Claude config:
```json
{
  "mcpServers": {
    "xnai-memory": {
      "command": "uv",
      "args": ["run", "server.py"],
      "cwd": "/path/to/xnai-foundation/mcp-servers/xnai-memory"
    }
  }
}
```

### With Cline

Add to Cline settings:
```json
{
  "mcpServers": {
    "xnai-memory": {
      "command": "uv",
      "args": ["run", "server.py"],
      "cwd": "/path/to/xnai-foundation/mcp-servers/xnai-memory",
      "alwaysAllow": ["get_core_context", "search_memory_bank"]
    }
  }
}
```

### Testing with MCP Inspector

```bash
fastmcp dev server.py
```

## Resources

| URI | Description |
|-----|-------------|
| `memory://bank/{path}` | Any memory bank file |
| `memory://bank/core/activeContext.md` | Current priorities |
| `memory://bank/core/progress.md` | Project status |

## Tools

| Tool | Description |
|------|-------------|
| `get_core_context` | Compile all core memory blocks |
| `get_block_status` | Check block utilization |
| `search_memory_bank` | Full-text search |
| `list_memory_files` | List files by tier |

## Prompts

| Prompt | Description |
|--------|-------------|
| `load_context_prompt` | Load and summarize context |
| `search_and_summarize` | Search and summarize findings |
