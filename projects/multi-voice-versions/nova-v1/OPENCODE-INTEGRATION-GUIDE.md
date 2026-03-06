# OpenCode IDE Integration Guide

**Updated**: February 21, 2026  
**Status**: Full CLI Integration Ready

---

## Quick Start

### 1. Verify OpenCode is Installed

```bash
# Check if OpenCode is available
which opencode

# Or verify installation
opencode --version
```

### 2. Start the Voice CLI Server

```bash
cd /Users/buck/Documents/voice-setup-project
source voice_venv/bin/activate
python3 main.py --cli-mode opencode
```

You should see output like:
```
OpenCodeCLI - Ready for voice input
Type 'help' for commands, 'quit' to exit
>
```

### 3. Use in OpenCode

Open OpenCode and use the terminal:

```bash
# Input a voice request
> tell me a joke

# The system responds
✓ Response: I'd like to tell you a funny one...

# Use slash commands for more control
> /voice summarize this code
> /status
> /memory search python
> /help
```

---

## Understanding the Integration

### What is the OpenCode CLI?

**OpenCode** is a full-featured code editor/IDE that runs in your terminal.

**The Voice CLI Interface**:
- Simple command-line input/output
- Natural language voice requests
- Slash commands for specific operations
- JSON output option for automation
- Memory integration for context

### Why This Works

1. **Native Terminal Integration**: No special protocols needed
2. **Native IDE Support**: Works with any terminal OpenCode opens
3. **Simple API**: Type commands, get responses
4. **Real-time Feedback**: Immediate status indicators

---

## Commands

### Basic Voice Input

```bash
> tell me what this code does
> explain how memory search works
> write a bash function for that
```

**Response Format**:
```
✓ Response: [Answer from voice system]
├─ Status: Processing complete
├─ Tokens used: 124
└─ Memory stored: Yes
```

### Slash Commands

#### `/help`
Show all available commands

```bash
> /help

Available Commands:
  tell me...          Natural voice input
  /voice <text>       Explicit voice request
  /status             Show system health
  /memory <query>     Search memories
  /info               Show current config
  /clear              Clear screen
  /quit               Exit
  
Voice Input Examples:
  tell me a joke
  /voice explain this function
  /memory search "python functions"
```

#### `/voice`
Process explicit voice request

```bash
> /voice explain how the voice pipeline works
✓ Response: The voice pipeline consists of...
```

#### `/status`
Show system health and configuration

```bash
> /status

System Status:
  Services:
    ✓ Ollama: Running (active)
    ✓ TTS: Initialized
    ✓ STT: Available
    ✗ Optimizations: Not loaded
  
  Memory:
    - Total memories: 42
    - Memories last 7 days: 12
    - Average response time: 1.2s
  
  Configuration:
    - Model: claude
    - Memory enabled: true
    - Auto-save: enabled
```

#### `/memory`
Search stored memories

```bash
> /memory search python
Found 5 memories:
  1. [2026-02-21] Conversation about Python functions
  2. [2026-02-20] Discussion of Python best practices
  3. [2026-02-19] Python memory bank implementation
  4. [2026-02-18] Python list comprehensions explained
  5. [2026-02-17] Python async/await overview

To view full content: /memory show <id>
```

#### `/info`
Show configuration details

```bash
> /info

Configuration:
  CLI Mode: opencode
  Project: voice-setup-project
  Python: 3.12
  Memory DB: voice_config.json
  Ollama: localhost:11434
  LLM Model: claude
  
Paths:
  Project: /Users/buck/Documents/voice-setup-project
  Memory: voice_config.json
  Config: config/memory_config.json
```

#### `/clear`
Clear the terminal screen

```bash
> /clear
[Screen cleared]
>
```

#### `/quit` or `/exit`
Exit the CLI

```bash
> /quit
Goodbye! Memory saved.
```

---

## Usage Examples

### Example 1: Get Code Explanation

```bash
> explain what the voice_orchestrator.py file does

✓ Response: The voice_orchestrator is the core component that...
├─ Context: 3 related memories found
├─ Similar topics: voice pipeline, STT, TTS
└─ Suggestion: Try "tell me about the memory system"
```

### Example 2: System Status Check

```bash
> /status

System Status:
  Services: ✓ All running
  Memory: ✓ 42 items stored
  Health: ✓ Excellent (avg response 1.2s)
```

### Example 3: Search Memories

```bash
> /memory search memory bank

Found 3 memories:
  1. Memory bank implementation details
  2. How memory search works
  3. Memory TTL configuration

Recent similar queries:
  - "How does memory integration work?"
  - "What memories do we have?"
  - "Memory system architecture"
```

### Example 4: Multiple Commands

```bash
> /status
System Status: All good ✓

> tell me what changed since the last update
✓ Response: Based on memories, here's what changed...

> /memory search "recent updates"
Found 2 memories about updates

> /quit
Goodbye!
```

---

## Output Formats

### Standard Response

```bash
✓ Response: [Main answer]
├─ Status: [Operation status]
├─ Time: [Processing time]
├─ Context: [Related items]
└─ Suggestions: [Follow-up options]
```

### Error Response

```bash
✗ Error: [What went wrong]
├─ Code: [Error code]
├─ Suggestion: [How to fix]
└─ Retry: /voice [command]
```

### Status Response

```bash
Status: [Overall health]
  - Service 1: [Status]
  - Service 2: [Status]
  - Memory: [Status]
  - Health: [Rating]
```

---

## Troubleshooting

### Issue 1: "Command not found: opencode"

**Solution**:
1. Install OpenCode (if not installed)
2. Add OpenCode to PATH
3. Restart terminal

```bash
# Verify installation
which opencode
```

### Issue 2: CLI starts but voice doesn't respond

**Debug**:
```bash
# Test individual services
> /status

# Check if Ollama is running
# Check if voice_venv is activated
# Try a simple command: > help
```

### Issue 3: Memory search returns no results

**Expected behavior** - This can happen if:
- Memory database is empty (first run)
- Search query doesn't match stored memories
- Memory TTL expired

**Solution**:
```bash
> tell me something interesting  # Creates a memory
> /memory search [topic]         # Now search
```

### Issue 4: "Cannot connect to Ollama"

**Solution**:
```bash
# Check if Ollama is running
ps aux | grep ollama

# If not running, start it
ollama serve

# Then restart the CLI
```

### Issue 5: Response times are slow

**Reasons**:
- First calls load models (5-10s normal)
- Ollama startup time
- System resources

**Solution**: Be patient on first use, subsequent calls are faster

---

## Advanced Usage

### Using JSON Output

Add `--json` flag for structured output:

```bash
> /status --json

{
  "status": "ok",
  "services": {
    "ollama": "running",
    "tts": "ready",
    "stt": "ready"
  },
  "memory": {
    "total": 42,
    "recent": 12
  }
}
```

### Piping Commands

```bash
# Get memory search as JSON and pipe to other tools
/memory search python --json | jq '.memories | length'

# Extract specific data
/status --json | jq '.services'
```

### Batch Processing

```bash
# Create a script file
cat > voice_commands.txt << EOF
/status
tell me a joke
/memory search recent
/quit
EOF

# Run interactively or pipe
cat voice_commands.txt | python3 main.py --cli-mode opencode
```

---

## Keyboard Shortcuts

### Navigation
- `Ctrl+C`: Cancel current input
- `Ctrl+D`: Exit (like /quit)
- `Ctrl+L`: Clear screen (like /clear)
- `↑/↓`: Scroll through command history
- `Tab`: Command/argument completion

### Editing
- `Ctrl+A`: Move to start of line
- `Ctrl+E`: Move to end of line
- `Ctrl+U`: Clear from cursor to start
- `Ctrl+K`: Clear from cursor to end
- `Alt+D`: Delete next word

---

## Best Practices

### 1. Use Natural Language

❌ Bad: `tell me joke`  
✅ Good: `tell me a funny joke`

### 2. Be Specific with Queries

❌ Bad: `search memory`  
✅ Good: `/memory search python functions`

### 3. Check Status When Debugging

```bash
> /status  # Check everything is running
> tell me [your request]  # Then try your request
```

### 4. Use Slash Commands for Operations

✅ `/status` for health check  
✅ `/memory search` for finding info  
✅ `/voice` for explicit requests

### 5. Monitor Response Times

- First response: Give it time (models loading)
- Subsequent responses: Should be fast (<3s)
- If slower: Check `/status` for issues

---

## Architecture

```
Terminal Window
    │
    └─ OpenCode CLI (Python process)
        │
        ├– Command Parser
        │   ├─ Natural language ("tell me...")
        │   └─ Slash commands ("/voice", "/status", etc.)
        │
        ├─ Voice Orchestrator
        │   ├─ STT (input processing)
        │   ├─ LLM (Claude via Ollama)
        │   └─ TTS (response generation)
        │
        ├─ Memory System
        │   ├─ SQLite database
        │   └─ Semantic search
        │
        └─ Service Manager
            ├─ Ollama health check
            └─ Auto-start if needed
```

---

## Performance

### Response Times
- **First response**: 3-5 seconds (model loading)
- **Regular response**: 1-2 seconds
- **Status check**: <100ms
- **Memory search**: <500ms

### Memory Usage
- **CLI Process**: ~100-150MB
- **LLM Models**: ~200-400MB
- **Memory DB**: <10MB

### Optimization
1. Keep CLI running between requests
2. Use memory search for existing info
3. Batch similar requests
4. Close when not in use to free memory

---

## Common Workflows

### Workflow 1: Learning
```bash
> explain how the voice system works
✓ Response: The voice system consists of...

> /memory search "voice system"
Found 1 memory about voice system

> tell me more about the memory part
✓ Response: The memory system uses...
```

### Workflow 2: Debugging
```bash
> /status
System Status: Some issues detected

> tell me which services are having problems
✓ Response: Ollama service is slow

> /restart-ollama
✓ Ollama restarted

> /status
System Status: All good ✓
```

### Workflow 3: Development
```bash
> explain this Python function
✓ Response: This function...

> what would improve this?
✓ Response: Consider these improvements...

> /memory search "Python best practices"
Found 3 related memories

> show me examples
✓ Response: Here are examples from past conversations...
```

---

## Command Reference

| Command | Purpose | Example |
|---------|---------|---------|
| (natural text) | Voice input | `tell me a joke` |
| `/voice <text>` | Explicit voice | `/voice explain this` |
| `/status` | System health | `/status` |
| `/info` | Configuration | `/info` |
| `/memory <query>` | Search memories | `/memory search python` |
| `/clear` | Clear screen | `/clear` |
| `/help` | Show help | `/help` |
| `/quit` | Exit | `/quit` |

---

## Integration with OpenCode IDE

### From OpenCode Terminal

1. Open OpenCode
2. Open terminal (Ctrl+`)
3. Start voice CLI:
   ```bash
   cd ~/Documents/voice-setup-project
   source voice_venv/bin/activate
   python3 main.py --cli-mode opencode
   ```
4. Use voice commands while editing code

### Running in Background

```bash
# Start in background
nohup python3 main.py --cli-mode opencode > voice.log 2>&1 &

# Commands sent via other terminal window
/status
tell me about this file
```

---

## Next Steps

1. **Start the CLI**: Run main.py with --cli-mode opencode
2. **Try /help**: See all available commands
3. **Ask naturally**: Start with "tell me a joke"
4. **Explore**: Try different commands and workflows
5. **Save memories**: They grow over time

---

## Support

**CLI won't start**: Check that voice_venv is active and all packages installed  
**Memory not working**: Ensure config/memory_config.json exists  
**Ollama connection fails**: Make sure ollama serve is running  
**Slow responses**: First call loads models; subsequent calls are faster

---

**Document Version**: 1.0  
**Last Updated**: February 21, 2026  
**Status**: Ready for Use
