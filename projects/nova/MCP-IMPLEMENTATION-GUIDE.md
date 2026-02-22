# MCP Implementation & Architecture Guide

**Updated**: February 21, 2026  
**Status**: Production Ready

---

## Overview

**MCP** (Model Context Protocol) is a standard protocol that enables:
- AI assistants to discover and use tools
- IDEs to expose capabilities to AI systems
- Language models to interact with external systems

This document explains how MCP is implemented in the voice system.

---

## What is MCP?

### The Problem

Before MCP, integrating tools with AI assistants required:
- Custom protocols for each IDE
- Proprietary tool registration formats
- No standard way to expose capabilities
- Difficult IDE integration

### The Solution: MCP

MCP provides:
- **Standardized Protocol**: All tools follow same format
- **Tool Discovery**: AI assistants can find available tools
- **Tool Execution**: Consistent way to call tools
- **IDE Integration**: Works with Cline, Claude, OpenCode, etc.

### How It Works

```
AI Assistant (Cline, Claude, etc.)
    │
    ├─ Queries: "What tools are available?"
    │
    └─ MCP Server Endpoint: /tools/list
        │
        ├─ Returns: { tools: [{ name, description, schema }] }
        │
    ├─ Calls Tool: { tool: "voice_input", args: { text: "..." } }
    │
    └─ MCP Server Endpoint: /tools/call
        │
        └─ Returns: { status: "ok", data: {...} }
```

---

## Implementation Architecture

### System Components

```
┌─────────────────────────────────────────────────────┐
│              IDE Layer                              │
│  ┌──────────────────┐  ┌──────────────────┐        │
│  │  Cline (VS Code) │  │  Claude Desktop  │        │
│  └──────────────────┘  └──────────────────┘        │
└────────────────────┬────────────────────────────────┘
                     │ MCP Protocol (JSON)
                     │
┌────────────────────▼────────────────────────────────┐
│         MCP Server (mcp_server.py)                  │
│  ┌───────────────────────────────────────────────┐ │
│  │  Tool Registry:                               │ │
│  │  • voice_input                                │ │
│  │  • get_status                                 │ │
│  │  • list_memories                              │ │
│  └───────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────┐ │
│  │  Tool Handlers (async/sync)                   │ │
│  │  • Process requests                           │ │
│  │  • Return structured responses                │ │
│  └───────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────┘
                     │
         ┌───────────┴───────────┬──────────────┐
         │                       │              │
┌────────▼────────┐  ┌──────────▼──────┐  ┌───▼──────────┐
│ Voice           │  │ Memory Bank      │  │ Service      │
│ Orchestrator    │  │                  │  │ Manager      │
│                 │  │ • Semantic       │  │              │
│ • STT           │  │   search         │  │ • Ollama     │
│ • LLM (Ollama)  │  │ • Persistence    │  │ • Health     │
│ • TTS           │  │ • TTL            │  │   checks     │
└─────────────────┘  └──────────────────┘  └──────────────┘
```

---

## MCP Server Implementation

### Core Module: `mcp_server.py`

#### MCPTool Dataclass

```python
@dataclass
class MCPTool:
    name: str                    # "voice_input"
    description: str             # "Process voice input..."
    category: str               # "voice" or "system"
    input_schema: dict          # JSON schema for inputs
    examples: List[dict]        # Usage examples
```

**Example Tool Definition**:
```python
MCPTool(
    name="voice_input",
    description="Process text input through voice pipeline",
    category="voice",
    input_schema={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Text to process"
            }
        },
        "required": ["text"]
    },
    examples=[
        {
            "input": { "text": "tell me a joke" },
            "output": { "status": "ok", "data": {...} }
        }
    ]
)
```

#### MCPServer Class

```python
class MCPServer:
    def __init__(self):
        self.tools = {}          # Registered tools
        self.handlers = {}       # Handler functions
    
    def register_tool(self, tool, handler):
        """Register a tool with async/sync handler"""
        self.tools[tool.name] = tool
        self.handlers[tool.name] = handler
    
    def get_tools_list(self):
        """Return available tools for discovery"""
        return [tool for tool in self.tools.values()]
    
    async def call_tool(self, tool_name, args):
        """Execute a registered tool"""
        # Validate tool exists
        # Call handler with arguments
        # Return response
```

#### Singleton Pattern

```python
_mcp_server_instance = None

def get_mcp_server():
    """Get or create MCP server singleton"""
    global _mcp_server_instance
    if not _mcp_server_instance:
        _mcp_server_instance = MCPServer()
    return _mcp_server_instance
```

### CLI Integration: `cli_abstraction.py`

#### ClineCLI Registration

```python
class ClineCLI:
    def _register_mcp_tools(self):
        """Register 3 tools with MCP server"""
        server = get_mcp_server()
        
        # Tool 1: voice_input
        server.register_tool(
            MCPTool(...),
            handler=self._voice_input_handler
        )
        
        # Tool 2: get_status
        server.register_tool(
            MCPTool(...),
            handler=self._get_status_handler
        )
        
        # Tool 3: list_memories
        server.register_tool(
            MCPTool(...),
            handler=self._list_memories_handler
        )
```

#### Async Handler Example

```python
async def _voice_input_handler(self, text: str) -> dict:
    """Process text through voice pipeline"""
    try:
        response = await self.orchestrator.voice_turn(text)
        return {
            "status": "ok",
            "data": {
                "response": response,
                "memory_stored": True,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "code": "VOICE_PROCESSING_ERROR"
        }
```

---

## Tool Specifications

### Tool 1: `voice_input`

**Purpose**: Process text through the LLM voice pipeline

**Schema**:
```json
{
  "name": "voice_input",
  "description": "Process text input through voice pipeline (STT→LLM→TTS)",
  "category": "voice",
  "inputSchema": {
    "type": "object",
    "properties": {
      "text": {
        "type": "string",
        "description": "Input text to process",
        "examples": ["tell me a joke", "explain machine learning"]
      }
    },
    "required": ["text"]
  }
}
```

**Request**:
```json
{
  "tool": "voice_input",
  "arguments": {
    "text": "tell me a joke"
  }
}
```

**Response (Success)**:
```json
{
  "status": "ok",
  "data": {
    "response": "Why did the programmer quit? Because he didn't get arrays!",
    "memory_stored": true,
    "processing_time": 1.5,
    "model": "claude",
    "timestamp": "2026-02-21T12:34:56"
  }
}
```

**Response (Error)**:
```json
{
  "status": "error",
  "error": "Ollama service not responding",
  "code": "SERVICE_UNAVAILABLE",
  "suggestion": "Ensure Ollama is running with: ollama serve"
}
```

### Tool 2: `get_status`

**Purpose**: Return system health and status

**Schema**:
```json
{
  "name": "get_status",
  "description": "Get system status including services and health metrics",
  "category": "system",
  "inputSchema": {
    "type": "object",
    "properties": {}
  }
}
```

**Response**:
```json
{
  "status": "ok",
  "data": {
    "health": "healthy",
    "services": {
      "ollama": "running",
      "memory_bank": "initialized",
      "orchestrator": "ready"
    },
    "metrics": {
      "uptime": 3600,
      "requests": 42,
      "avg_response_time": 1.2
    }
  }
}
```

### Tool 3: `list_memories`

**Purpose**: Search stored memories

**Schema**:
```json
{
  "name": "list_memories",
  "description": "Search stored conversation memories",
  "category": "memory",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query (e.g., 'python functions')"
      },
      "limit": {
        "type": "integer",
        "description": "Max results (default: 10)"
      }
    }
  }
}
```

**Response**:
```json
{
  "status": "ok",
  "data": {
    "results": [
      {
        "id": 1,
        "timestamp": "2026-02-21T12:00:00",
        "type": "conversation",
        "summary": "Discussion about Python decorators",
        "relevance": 0.95
      }
    ],
    "total": 1
  }
}
```

---

## Response Format Specification

### Success Response

All successful tool calls return:

```json
{
  "status": "ok",
  "data": {
    // Tool-specific data
  }
}
```

### Error Response

All errors return:

```json
{
  "status": "error",
  "error": "Human-readable error message",
  "code": "UPPERCASE_ERROR_CODE",
  "suggestion": "How to fix (optional)",
  "details": {}  // Additional context
}
```

### Response Headers

Included with all responses:

```json
{
  "timestamp": "2026-02-21T12:34:56Z",
  "request_id": "req_abc123",
  "version": "1.0"
}
```

---

## Protocol Flow

### Tool Discovery Flow

```
1. IDE (Cline) connects to MCP server
2. IDE sends: GET /tools/list
3. Server returns:
   {
     "tools": [
       { "name": "voice_input", "description": "...", "schema": {...} },
       { "name": "get_status", "description": "...", "schema": {...} },
       { "name": "list_memories", "description": "...", "schema": {...} }
     ]
   }
4. IDE displays available tools to user
```

### Tool Call Flow

```
1. User in IDE: "Use voice_input to tell me a joke"
2. IDE recognizes tool request
3. IDE sends: POST /tools/call
   {
     "tool": "voice_input",
     "arguments": { "text": "tell me a joke" }
   }
4. Server receives request
5. Server calls registered handler
6. Handler processes (async if needed)
7. Handler returns response
8. Server sends response:
   {
     "status": "ok",
     "data": { "response": "..." }
   }
9. IDE receives and displays result
10. User sees response in chat
```

### Error Handling Flow

```
1. Tool call fails (e.g., Ollama down)
2. Handler catches exception
3. Handler returns error response:
   {
     "status": "error",
     "error": "Ollama service not responding",
     "code": "SERVICE_UNAVAILABLE",
     "suggestion": "Start Ollama with: ollama serve"
   }
4. IDE displays error with suggestion
5. User can take corrective action
```

---

## Integration Points

### How Cline Uses MCP Tools

```
Cline Interface
    │
    ├─ User asks: "Tell me a joke using voice_input"
    │
    ├─ Cline recognizes tool request
    │
    ├─ Cline queries: /tools/list
    │    └─ Server returns: [voice_input, get_status, list_memories]
    │
    ├─ Cline calls: /tools/call
    │    └─ Payload: { tool: "voice_input", arguments: { text: "tell me a joke" } }
    │
    ├─ Server processes through VoiceOrchestrator
    │
    └─ Response returned to Cline
        └─ User sees: "Why did the programmer quit?"
```

### How OpenCode Uses MCP Tools

OpenCode has a simpler integration - it's a full IDE, not an MCP client:

```
OpenCode Terminal
    │
    ├─ User types: > /voice tell me a joke
    │
    ├─ OpenCodeCLI parses command
    │
    ├─ OpenCodeCLI calls VoiceOrchestrator directly
    │    (No MCP protocol needed)
    │
    └─ Response printed to terminal
```

### How Standalone CLI Uses MCP Tools

Standalone doesn't use MCP - direct command processing:

```
Terminal Window
    │
    ├─ User types: > tell me a joke
    │
    ├─ StandaloneCLI parses input
    │
    ├─ StandaloneCLI calls VoiceOrchestrator directly
    │    (No MCP protocol needed)
    │
    └─ Response printed to terminal
```

---

## Adding New Tools

### Step 1: Define Tool Metadata

```python
new_tool = MCPTool(
    name="summarize_text",
    description="Summarize provided text using LLM",
    category="text_processing",
    input_schema={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Text to summarize"
            },
            "max_words": {
                "type": "integer",
                "description": "Max summary length"
            }
        },
        "required": ["text"]
    },
    examples=[
        {
            "input": { "text": "Long text here...", "max_words": 50 },
            "output": { "status": "ok", "data": { "summary": "..." } }
        }
    ]
)
```

### Step 2: Implement Handler

```python
async def summarize_handler(text: str, max_words: int = 100) -> dict:
    """Summarize text handler"""
    try:
        summary = await self.orchestrator.voice_turn(
            f"Summarize this in {max_words} words: {text}"
        )
        return {
            "status": "ok",
            "data": {
                "summary": summary,
                "words": len(summary.split())
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "code": "SUMMARIZATION_ERROR"
        }
```

### Step 3: Register Tool

```python
# In ClineCLI._register_mcp_tools()
server.register_tool(
    new_tool,
    handler=self.summarize_handler
)
```

### Step 4: Test Tool

```python
# Test directly
response = await server.call_tool(
    "summarize_text",
    { "text": "Long text...", "max_words": 50 }
)
assert response["status"] == "ok"
```

---

## Best Practices

### 1. Tool Design

✅ **Do**:
- Keep descriptions concise and clear
- Add multiple examples to schema
- Use meaningful error codes
- Return structured data

❌ **Don't**:
- Create ambiguous tool descriptions
- Skip input validation
- Return errors without codes
- Combine multiple operations in one tool

### 2. Handler Implementation

✅ **Do**:
- Use async for I/O operations
- Validate inputs
- Catch and handle exceptions
- Return consistent response format

❌ **Don't**:
- Block on network calls
- Trust user input directly
- Raise unhandled exceptions
- Return inconsistent formats

### 3. Performance

✅ **Do**:
- Cache service connections
- Use connection pooling
- Optimize database queries
- Monitor response times

❌ **Don't**:
- Create new connections per request
- Query unnecessarily
- Process large data synchronously
- Ignore performance metrics

### 4. Error Handling

✅ **Do**:
- Provide actionable error messages
- Include recovery suggestions
- Log errors for debugging
- Return appropriate status codes

❌ **Don't**:
- Hide error details
- Generic "unknown error" messages
- Swallow exceptions silently
- Return success for partial failures

### 5. Security

✅ **Do**:
- Validate all inputs
- Sanitize text content
- Limit resource usage
- Log access attempts

❌ **Don't**:
- Trust untrusted input
- Expose internal paths
- Allow unbounded requests
- Skip authentication checks

---

## Testing MCP Integration

### Unit Test Example

```python
import pytest
from mcp_server import get_mcp_server, MCPTool

@pytest.mark.asyncio
async def test_voice_input_tool():
    """Test voice_input tool execution"""
    server = get_mcp_server()
    
    # Call tool
    response = await server.call_tool(
        "voice_input",
        {"text": "tell me a joke"}
    )
    
    # Verify response
    assert response["status"] == "ok"
    assert "data" in response
    assert "response" in response["data"]
```

### Integration Test Example

```python
@pytest.mark.asyncio
async def test_cline_tool_discovery():
    """Test Cline can discover tools"""
    cli = ClineCLI()
    await cli.initialize()
    
    server = get_mcp_server()
    tools = server.get_tools_list()
    
    # Verify tools registered
    assert len(tools) == 3
    tool_names = [t.name for t in tools]
    assert "voice_input" in tool_names
    assert "get_status" in tool_names
    assert "list_memories" in tool_names
```

---

## Monitoring & Debugging

### MCP Server Logs

```
[2026-02-21 12:34:56] INFO - MCP Server initialized
[2026-02-21 12:34:57] INFO - Registered tool: voice_input
[2026-02-21 12:34:57] INFO - Registered tool: get_status
[2026-02-21 12:34:57] INFO - Registered tool: list_memories
[2026-02-21 12:35:00] INFO - Tool call: voice_input(text="tell me a joke")
[2026-02-21 12:35:02] INFO - Tool response: {"status": "ok", "data": {...}}
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Now see detailed tool execution
# [DEBUG] Tool input validation: OK
# [DEBUG] Handler called: _voice_input_handler
# [DEBUG] Handler response: {...}
```

### Health Check Endpoint

```bash
# Check MCP server health
curl http://localhost:8000/health

# Returns:
# {
#   "status": "healthy",
#   "tools": 3,
#   "uptime": 3600
# }
```

---

## Migration from Non-MCP

### Before (Basic CLI)

```bash
# Only command-line interface
python3 main.py --cli-mode standalone
# Commands limited to terminal
```

### After (With MCP)

```bash
# Same CLI works
python3 main.py --cli-mode cline
# Plus MCP tools available to Cline IDE
# Plus all other advanced features
```

**Key Benefits**:
- ✅ Backward compatible
- ✅ No breaking changes
- ✅ Works in more contexts
- ✅ Better IDE integration

---

## Reference

### Tools at a Glance

| Tool | Purpose | Handler Type |
|------|---------|--------------|
| `voice_input` | Process text | Async |
| `get_status` | System health | Sync |
| `list_memories` | Search memories | Async |

### Constants

| Setting | Value | Notes |
|---------|-------|-------|
| MCP Version | 1.0 | Protocol version |
| Tool Timeout | 30s | Max execution time |
| Response Size | 1MB | Max response data |
| Memory Limit | 512MB | Process limit |

### Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| `ok` | Success | Process complete |
| `error` | Failed | Check error message |
| `timeout` | Took too long | Retry or cancel |
| `invalid_input` | Bad parameters | Fix inputs |

---

## Glossary

- **MCP**: Model Context Protocol - Standard for tool integration
- **Tool**: A callable action exposed via MCP
- **Handler**: Function that executes a tool
- **Schema**: JSON definition of tool inputs
- **Registry**: Collection of registered tools
- **Tool Discovery**: Process of finding available tools
- **Tool Call**: Execution of a specific tool

---

## Next Steps

1. **Review** mcp_server.py implementation
2. **Test** tool discovery and execution
3. **Add** custom tools as needed
4. **Monitor** MCP server health
5. **Optimize** tool performance

---

**Document Version**: 1.0  
**Last Updated**: February 21, 2026  
**Status**: Production Ready
