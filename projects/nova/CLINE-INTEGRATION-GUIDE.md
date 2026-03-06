# Cline IDE Integration Guide

**Updated**: February 21, 2026  
**Status**: Full MCP Integration Ready

---

## Quick Start

### 1. Ensure Cline is Installed
```bash
# Cline is already installed in VS Code
# Verify: Look for "Cline" in VS Code extensions
```

### 2. Start the MCP Voice Server

```bash
cd /Users/buck/Documents/voice-setup-project
source voice_venv/bin/activate
python3 main.py --cli-mode cline --headless
```

The MCP server starts with these tools registered:
- `voice_input` - Process voice text
- `get_status` - Get system status  
- `list_memories` - Search memories

### 3. Use in Cline

In VS Code:
1. Open Cline (Ctrl+K or click Cline icon)
2. In Cline's message input, type naturally:
   ```
   Tell me a joke using the voice tool
   ```

3. Or use the tool directly:
   ```
   @voice_input Please tell me a joke
   ```

---

## Understanding the Integration

### What's the MCP Server?

**MCP** = Model Context Protocol - a standard way for AI assistants to discover and use tools.

**The Voice MCP Server**:
- Runs in the background on your machine
- Cline auto-discovers the available tools
- Cline can call tools like `voice_input`, `get_status`, etc.
- Responses come back with structured data

### Why This Works

1. **Tool Discovery**: Cline queries the MCP server for available tools
2. **Tool Calling**: When you ask Cline to use a tool, it sends the request
3. **Auto-Execution**: The voice server processes it and returns results
4. **Native Integration**: Feels like Cline's built-in capability

---

## Available Tools

### Tool 1: `voice_input`

**What it does**: Processes text through the voice pipeline (Claude LLM)

**Usage**:
```
"Use voice_input to tell me a joke"
```

**Returns**:
- The processed response from the LLM
- Success status
- Memory updated with the interaction

**Example**:
```
User: "Use voice_input to ask what 2+2 is"
Cline: "Calls voice_input with 'what is 2+2'"
Server: "Returns 'The answer is 4'"
```

### Tool 2: `get_status`

**What it does**: Returns current system status

**Usage**:
```
"What's the status of the voice system?"
```

**Returns**:
- Service status (Ollama, STT, TTS)
- Memory system status
- Configuration
- Health metrics

**Example**:
```
User: "Check system status"
Cline: "Calls get_status"
Server: "Returns { services: {...}, health: {...} }"
```

### Tool 3: `list_memories`

**What it does**: Search stored conversation memories

**Usage**:
```
"Search memories for conversations about Python"
```

**Returns**:
- Array of matching memories
- Metadata (id, type, timestamp)
- Total count

**Example**:
```
User: "Find all memories about weather"
Cline: "Calls list_memories with query='weather'"
Server: "Returns [{ id: 1, content: 'Weather was sunny', type: 'conversation' }]"
```

---

## Troubleshooting

### Issue 1: "Tool not found" or tool doesn't appear

**Solution**:
1. Restart Cline (Ctrl+Shift+P → "Reload Window")
2. Ensure MCP server is running: Check terminal for "Registered 3 tools"
3. Restart the whole VS Code window

### Issue 2: Tool returns error

**Debug**:
1. Check MCP server terminal for error logs
2. Ensure voice_venv is activated
3. Check that Ollama is running

### Issue 3: Response is slow

**Reasons**:
- First call loads models (~5-10s normal)
- Ollama model loading
- Network latency

**Solution**: Give it time, subsequent calls are faster

### Issue 4: Can't find the voice tools in Cline

**Steps**:
1. Make sure MCP server is running
2. Open Cline chat
3. Look for "Cline Tools" or "@" symbol  
4. Start typing "@voice" to see available tools
5. Or ask naturally: "use the voice tool to..."

### Issue 5: MCP server won't start

**Debug**:
```bash
# Test if imports work
source voice_venv/bin/activate
python3 -c "from mcp_server import get_mcp_server; print('✅ MCP OK')"

# Test CLI directly
python3 cli_abstraction.py
```

---

## Advanced Usage

### Using Multiple Tools Together

```
"Get the status, then use voice_input to describe the system, then search memories for similar conversations"
```

Cline will:
1. Get status data
2. Pass it to voice_input for explanation
3. Search memories for related conversations
4. Combine results into a coherent response

### Creating Memory Context

```
"Use voice_input to ask about Python, then save this as a memory"
```

Results are automatically saved to memory for future reference.

### Filtering Memory Searches

```
"Search memories for 'python' but only show me the last 5 results"
```

The list_memories tool supports:
- `query`: search term
- `max_results`: limit (default 10)

---

## Architecture

```
VS Code Window
    │
    ├─ Cline Extension
    │   └─ Detects MCP server
    │
    └─ MCP Server (background Python process)
        ├─ voice_input tool
        ├─ get_status tool
        └─ list_memories tool
        
When you ask Cline to use a tool:
1. Cline sends request to MCP server
2. MCP server calls VoiceOrchestrator  
3. VoiceOrchestrator processes via LLM/Memory
4. Response returned to Cline
5. Cline displays it to you
```

---

## Performance

### Response Times
- **First call**: 3-8 seconds (model loading)
- **Subsequent calls**: 1-3 seconds
- **Status check**: <500ms
- **Memory search**: <1 second

### Memory Usage
- **MCP Server**: ~150-200MB
- **Voice Orchestrator**: ~200-300MB  
- **Total**: ~400-500MB

### Optimization Tips
1. Keep MCP server running between uses
2. Use simpler queries for faster responses
3. Memory searches are faster than voice processing
4. Batch multiple questions when possible

---

## Best Practices

### 1. Natural Language is Best

❌ Bad: `@voice_input tell me joke`  
✅ Good: "Tell me a joke using the voice tool"

The MCP server understands context better.

### 2. Ask for Specific Tools When Needed

❌ Bad: "what's happening?"  
✅ Good: "Use get_status to show me the system status"

Makes it explicit which tool to use.

### 3. Combine Tools for Richer Results

```
"First get the status, then use voice_input to summarize it"
```

Leverages multiple tools for better responses.

### 4. Check Memories Regularly

```
"Search memories for our previous conversations about voice setup"
```

Memory system learns from past interactions.

---

## Common Workflows

### Workflow 1: Voice-Driven Development

```
1. Ask Cline: "Use voice_input to explain how this code works"
2. Cline: Calls voice_input with code explanation request
3. Result: Voice explanation of the code
```

### Workflow 2: System Monitoring

```
1. Ask: "Get system status and let me know if everything is healthy"
2. Cline: Calls get_status, analyzes results
3. Result: Health summary with any issues
```

### Workflow 3: Memory-Based Context

```
1. Ask: "Based on past memories, suggest improvements to this code"
2. Cline: Searches memories, retrieves context
3. Result: Suggestions informed by past conversations
```

---

## Reference

### Tool Response Format

All tools return JSON:

```json
{
  "status": "ok",
  "data": {
    // tool-specific data
  }
}
```

Or on error:
```json
{
  "status": "error",
  "error": "error message",
  "code": "ERROR_CODE"
}
```

### MCP Server Terminal Output

When running, you'll see:
```
INFO - ClineCLI - Initializing Cline CLI
INFO - ClineCLI - Registered 3 tools with MCP server
  - voice_input: Process voice input text...
  - get_status: Get system status...
  - list_memories: List memories...
```

This means it's ready!

---

## Next Steps

1. **Start the server** (if not running)
2. **Open Cline** in VS Code
3. **Ask naturally**: "Tell me a joke using the voice tool"
4. **Explore**: Try different questions and tool combinations

---

## Support

**Issue**: Tool doesn't work  
**Solution**: Check terminal for error logs, restart server

**Issue**: Server won't start  
**Solution**: Verify venv activated, check mcp_server.py exists

**Issue**: Response takes too long  
**Solution**: This is normal for first call, LLM models are loading

---

**Document Version**: 1.0  
**Last Updated**: February 21, 2026  
**Status**: Ready for Use
