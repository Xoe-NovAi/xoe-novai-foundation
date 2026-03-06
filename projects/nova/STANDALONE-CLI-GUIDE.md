# Standalone CLI Usage Guide

**Updated**: February 21, 2026  
**Status**: Full Terminal Integration Ready

---

## Quick Start

### 1. Activate Virtual Environment

```bash
cd /Users/buck/Documents/voice-setup-project
source voice_venv/bin/activate
```

### 2. Run the Standalone CLI

```bash
python3 main.py --cli-mode standalone
```

Or simply:
```bash
python3 main.py  # Defaults to standalone
```

### 3. Start Using It

```
Voice Assistant > tell me a joke
Response: Here's one for you...

Voice Assistant > /help
Available commands:
  • Natural voice input
  • /status - Show system status
  • /memory - Manage memories
  • /quit - Exit

Voice Assistant >
```

---

## Understanding Standalone Mode

### What is Standalone?

**Standalone Mode** is the pure Python CLI interface:
- Direct command-line interaction
- No IDE integration needed
- Simple REPL (Read-Eval-Print Loop)
- Real-time feedback
- Persistent memory across sessions

### When to Use

✅ **Use Standalone when**:
- Running on a headless/terminal-only machine
- You want the simplest setup
- Developing/debugging voice features
- Automating voice requests in scripts
- Learning how the system works

---

## Commands

### Natural Voice Input

Simply type what you want to say:

```bash
Voice Assistant > tell me a joke
Response: Why did the programmer quit his job? Because he didn't get arrays!

Voice Assistant > explain how quantum computing works
Response: Quantum computing uses quantum bits (qubits)...

Voice Assistant > what is 2+2
Response: 2+2 equals 4
```

### Explicit Voice Command

Use `/voice` for explicit requests:

```bash
Voice Assistant > /voice tell me about the weather
Response: Weather information...
```

### Status Command

Check system health:

```bash
Voice Assistant > /status

System Status:
  Services:
    ✓ Ollama: Running (active)
    ✓ STT: Ready
    ✓ TTS: Configured
  
  Memory:
    - Total memories: 42
    - Last 7 days: 12
    - Database size: 156 KB
  
  Performance:
    - Avg response time: 1.2s
    - Longest response: 3.4s
    - Total processed: 147 requests
```

### Memory Commands

#### List All Memories

```bash
Voice Assistant > /memory list
Stored Memories:
  [1] 2026-02-21 12:34 - Tell me a joke
  [2] 2026-02-21 12:33 - Explain quantum computing
  [3] 2026-02-20 15:22 - Python best practices
  ...
  Showing 1-10 of 42 total
```

#### Search Memories

```bash
Voice Assistant > /memory search python

Search Results for 'python':
  [3] Python best practices
  [8] Python async/await explained
  [15] Python memory bank implementation
  
Found 3 results. Use /memory show <id> to view full content
```

#### Show Memory Details

```bash
Voice Assistant > /memory show 3

Memory #3:
  Date: 2026-02-20
  Type: conversation
  Duration: 2.3s
  Tokens: 156
  
  Content:
  User: "Explain Python best practices"
  Response: "Python best practices include..."
```

#### Delete Memory

```bash
Voice Assistant > /memory delete 3
Memory #3 deleted successfully
```

#### Statistics

```bash
Voice Assistant > /memory stats

Memory Statistics:
  Total memories: 42
  Total size: 2.1 MB
  Average size: 50 KB
  
  By type:
    - conversation: 38
    - feedback: 2
    - system: 2
  
  Time range:
    - Oldest: 2026-02-01
    - Newest: 2026-02-21
    - Average age: 12 days
```

### System Commands

#### Show Configuration

```bash
Voice Assistant > /info

Configuration:
  Mode: standalone
  Project: voice-setup-project
  Python: 3.12
  Ollama: localhost:11434
  
  Paths:
    Project: /Users/buck/Documents/voice-setup-project
    Memory: voice_config.json
    Config: config/memory_config.json
```

#### Restart Services

```bash
Voice Assistant > /restart

Restarting services...
  ✓ Ollama: Restarted
  ✓ Memory system: Reloaded
  ✓ Configuration: Refreshed

All services ready!
```

#### Clear Screen

```bash
Voice Assistant > /clear
[Screen cleared, history preserved]
```

#### Help

```bash
Voice Assistant > /help

Help - Voice Assistant Commands
================================

Natural Input:
  tell me a joke              Natural voice request
  explain how...              Ask about something
  what is...                  Ask questions

Voice Commands:
  /voice <text>               Explicit voice request

Memory Commands:
  /memory list                Show all memories
  /memory search <query>      Search stored memories
  /memory show <id>           Show memory details
  /memory delete <id>         Delete memory
  /memory stats               Show memory statistics

System Commands:
  /status                     Show system status
  /info                        Show configuration
  /restart                    Restart services
  /clear                      Clear screen
  /history                    Show command history
  /quit                       Exit

Examples:
  tell me about vector databases
  /memory search "Python functions"
  /status
  /quit
```

#### Command History

```bash
Voice Assistant > /history

Command History (last 10):
  1. tell me a joke
  2. explain quantum computing
  3. /status
  4. /memory search python
  5. /memory show 3
  6. /memory stats
  7. what is machine learning
  8. /info
  9. /restart
  10. /history

Use ↑/↓ arrow keys to navigate
```

#### Exit

```bash
Voice Assistant > /quit
Saving memory bank...
Goodbye! 42 memories saved.
```

---

## Interactive Features

### Arrow Key Navigation

Navigate command history:
```bash
Voice Assistant > tell me a joke
# ↑ Arrow up - previous command
# ↓ Arrow down - next command
```

### Tab Completion

Start typing and press Tab:
```bash
Voice Assistant > /mem  [TAB]
# Completes to: /memory
```

Available completions:
- `/voice`, `/status`, `/memory`, `/info`, `/clear`, `/history`, `/quit`
- Memory search suggestions

### Auto-Suggestions

```bash
Voice Assistant > tell me
                        → Did you mean: tell me a joke
                        → Suggestion: explain how memory works

Voice Assistant > /mem
                      → Did you mean: /memory
                      → Recent: /memory search python
```

### Command History Search

```bash
Voice Assistant > [Ctrl+R]
(reverse-i-search): 'memory'_
# Shows previous 'memory' command
```

---

## Output Formats

### Standard Response

```bash
Voice Assistant > tell me a joke

Response: Why did the programmer quit his job?
Because he didn't get arrays!

[Processing time: 1.2s | Tokens: 45 | Memory saved: Yes]
```

### Error Response

```bash
Voice Assistant > /memory show 999

Error: Memory #999 not found
Available IDs: 1-42
Use /memory list to see all memories
```

### Status Response

```bash
Voice Assistant > /status

✓ Ollama: Running
✓ STT: Ready
✓ TTS: Configured
```

### Data Response (List)

```bash
Voice Assistant > /memory list | head -5

Memory List:
  [1] 2026-02-21 12:34 - Tell me a joke
  [2] 2026-02-21 12:33 - Explain quantum computing
  [3] 2026-02-20 15:22 - Python best practices
  [4] 2026-02-20 14:11 - Memory bank implementation
  [5] 2026-02-19 10:05 - Voice pipeline architecture
```

---

## Advanced Usage

### Piping Commands

```bash
# Count memories
/memory list | wc -l
Output: 42

# Search and count results
/memory search python | grep "Found" | cut -d' ' -f2
Output: 3
```

### Batch Processing

#### File Input

Create a script file:
```bash
cat > voice_commands.txt << 'EOF'
tell me a joke
explain how memory works
/memory stats
/quit
EOF

# Run commands from file
python3 main.py --cli-mode standalone < voice_commands.txt
```

#### Output Capture

```bash
# Capture all output
python3 main.py --cli-mode standalone > voice_output.log 2>&1

# Or run background
nohup python3 main.py --cli-mode standalone > voice.log &
```

### Debugging Mode

```bash
# Enable verbose logging
VOICE_DEBUG=1 python3 main.py --cli-mode standalone

# Output includes:
# [DEBUG] Loading memory bank...
# [DEBUG] Initializing STT service...
# [DEBUG] Calling Ollama at localhost:11434
```

---

## Keyboard Shortcuts

### Navigation
| Key | Action |
|-----|--------|
| `↑` | Previous command |
| `↓` | Next command |
| `Ctrl+C` | Cancel input |
| `Ctrl+D` | Exit gracefully |
| `Ctrl+L` | Clear screen |
| `Ctrl+R` | Search history |

### Editing
| Key | Action |
|-----|--------|
| `Ctrl+A` | Move to start |
| `Ctrl+E` | Move to end |
| `Ctrl+U` | Clear from start to cursor |
| `Ctrl+K` | Clear from cursor to end |
| `Alt+D` | Delete next word |
| `Tab` | Complete command |

---

## Troubleshooting

### Issue 1: "Command not found: python3"

**Solution**:
```bash
# Check Python is installed
which python3

# Or use active venv
source voice_venv/bin/activate
which python3
```

### Issue 2: CLI starts but doesn't respond to commands

**Debug**:
```bash
# Check if it's waiting for input
# Press Enter
# Try: /help

# Check terminal mode
stty -a
```

### Issue 3: Memory commands fail

**Debug**:
```bash
# Check memory file exists
ls -la voice_config.json

# Check permissions
ls -la config/memory_config.json

# Initialize if missing
python3 -c "from memory_bank import init_memory_bank; init_memory_bank()"
```

### Issue 4: Very slow responses

**Reasons**:
- First run loads LLM models (normal: 5-10s)
- System low on memory
- Ollama needs optimization

**Solution**:
```bash
# Check status
/status

# Monitor resources
# top -l 1 | grep python

# Restart services
/restart
```

### Issue 5: "Ollama not found"

**Solution**:
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama manually
ollama serve

# Or use service manager to auto-start
# Service manager runs automatically
```

---

## Best Practices

### 1. Clear Previous Context Sometimes

```bash
# After many commands, clear history
/clear

# Restart for fresh state
/restart
```

### 2. Use Natural Language

❌ Bad: `joke`  
✅ Good: `tell me a funny joke`

❌ Bad: `python stuff`  
✅ Good: `explain Python decorators`

### 3. Review Memory Periodically

```bash
/memory list    # See what's been saved
/memory stats   # Check memory growth
/memory search  # Find relevant past conversations
```

### 4. Monitor System Health

```bash
/status         # Check everything
/memory stats   # Verify database health
/info           # Confirm configuration
```

### 5. Use /voice for Complex Requests

```bash
# For multi-part questions, be explicit
/voice "considering the voice orchestrator architecture, how would you optimize memory search?"
```

---

## Common Workflows

### Workflow 1: Learning Mode

```bash
Voice Assistant > explain how the voice system works
Response: The voice system consists of...

Voice Assistant > tell me more about the memory part
Response: The memory system uses semantic search...

Voice Assistant > /memory search "voice system"
Found 2 memories about voice system

Voice Assistant > what improvements would you suggest?
Response: Based on the architecture, here are improvements...

Voice Assistant > /memory stats
Total memories: 45 (3 new from this session)
```

### Workflow 2: Development Session

```bash
Voice Assistant > /status
All services: ✓ Running

Voice Assistant > explain this function [paste code]
Response: This function does X...

Voice Assistant > what would improve it?
Response: Consider these improvements...

Voice Assistant > /memory search "function optimization"
Found relevant memories

Voice Assistant > show me an example
Response: Here's an example from past conversations...
```

### Workflow 3: Q&A Session

```bash
Voice Assistant > what is machine learning?
Response: Machine learning is...

Voice Assistant > how does it differ from AI?
Response: Machine learning is a subset of AI...

Voice Assistant > give me practical examples
Response: Here are practical examples...

Voice Assistant > /memory stats
New memories: 3
Session duration: 5 minutes
```

---

## Performance Characteristics

### Response Times

| Operation | Time | Notes |
|-----------|------|-------|
| First response | 3-8s | LLM loading |
| Regular response | 1-3s | Typical |
| Status check | <100ms | Local only |
| Memory search | <500ms | Database query |
| Memory list | <1s | All 42 items |

### Memory Usage

| Component | RAM |
|-----------|-----|
| Python process | ~100MB |
| LLM models | ~200-400MB |
| Memory database | ~10MB |
| Total | ~350-500MB |

### Optimization Tips

1. **Reuse session**: Don't restart CLI between requests
2. **Use memory search**: Faster than re-processing
3. **Batch similar requests**: Better context retention
4. **Close when done**: Releases memory back to system

---

## Session Management

### Automatic Saving

```bash
# Memory is automatically saved after each command
Voice Assistant > tell me a joke
# ← Automatically saved to memory

# On exit, full summary is shown
Voice Assistant > /quit
Saving memory bank...
Session Summary:
  - Commands: 15
  - New memories: 3
  - Processing time: 20.3s
  - Model requests: 12
Goodbye! 45 total memories saved.
```

### Resuming Sessions

```bash
# Start new session - memory is loaded
python3 main.py --cli-mode standalone

# Previous memories are available
Voice Assistant > /memory list
# Shows all 45 previous memories
```

### Exporting Sessions

```bash
# Capture output to file
python3 main.py > session_log.txt 2>&1

# Or in standalone, run then save:
# /memory stats > memory_report.txt
```

---

## Reference

### Command Categories

**Voice Input**:
- Natural language: `tell me...`, `explain...`, `what is...`, `how to...`
- Explicit: `/voice <text>`

**Memory Management**:
- `/memory list` - Show all
- `/memory search <q>` - Find
- `/memory show <id>` - View
- `/memory delete <id>` - Remove
- `/memory stats` - Statistics

**System**:
- `/status` - Health check
- `/info` - Configuration
- `/restart` - Restart services
- `/clear` - Clear screen
- `/history` - Command history
- `/help` - Help
- `/quit` - Exit

---

## Next Steps

1. **Start the CLI**: `python3 main.py --cli-mode standalone`
2. **Say hello**: `tell me a joke`
3. **Try `/help`** to see all commands
4. **Explore memory**: `/memory list`
5. **Check status**: `/status`
6. **Build workflows**: Combine commands for your use case

---

## Support

**CLI won't start**: Ensure voice_venv is activated  
**Memory not working**: Check config/memory_config.json exists  
**Commands not recognized**: Type `/help` to see available commands  
**Slow responses**: Normal on first use; patience needed  
**Service errors**: Run `/status` to diagnose

---

**Document Version**: 1.0  
**Last Updated**: February 21, 2026  
**Status**: Ready for Use
