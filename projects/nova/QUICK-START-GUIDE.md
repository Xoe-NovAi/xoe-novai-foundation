# Quick Start: Choose Your Integration

**Updated**: February 21, 2026  
**Status**: All Modes Ready

---

## Overview

The voice system supports **3 integration modes**. Choose the best one for your workflow:

| Mode | Use Case | Setup Time | Features |
|------|----------|-----------|----------|
| **Standalone CLI** | Terminal + Scripts | 2 min | Simple, lightweight, powerful |
| **OpenCode IDE** | Full code editing | 3 min | IDE + voice in one window |
| **Cline MCP** | VS Code + Copilot | 5 min | Cloud AI + local voice |

---

## Mode 1: Standalone CLI

### When to Use
✅ Command-line development  
✅ Server/headless machines  
✅ Script automation  
✅ Learning the system  

### Setup (2 minutes)

```bash
# 1. Activate environment
cd /Users/buck/Documents/voice-setup-project
source voice_venv/bin/activate

# 2. Start CLI
python3 main.py

# 3. Start using
Voice Assistant > tell me a joke
```

### Quick Commands
```bash
tell me a joke                 # Natural input
/voice explain this function   # Explicit request
/memory search python          # Find memories
/status                       # Check health
/help                         # See all commands
/quit                         # Exit
```

### Best For
- Rapid iteration
- Debugging voice pipeline
- Automation scripts
- Pure Python workflows

**See**: [STANDALONE-CLI-GUIDE.md](STANDALONE-CLI-GUIDE.md)

---

## Mode 2: OpenCode IDE

### When to Use
✅ Code editing with voice  
✅ Full IDE integrated terminal  
✅ Multi-file development  
✅ Visual + voice workflows  

### Setup (3 minutes)

```bash
# 1. Install OpenCode (if needed)
# brew install opencode
# OR download from https://opencode.ai

# 2. Start OpenCode
opencode /Users/buck/Documents/voice-setup-project

# 3. Open terminal in OpenCode (Ctrl+`)

# 4. Start voice CLI
source voice_venv/bin/activate
python3 main.py --cli-mode opencode

# 5. Use voice while editing code
```

### Quick Commands
```bash
tell me how this works         # Explain code
/voice write a function for X  # Generate code
/memory search similar         # Find past examples
/status                       # Check services
/help                         # See all options
```

### Best For
- Code editing sessions
- Integrated development
- Multi-file refactoring
- Teaching/learning workflows

**See**: [OPENCODE-INTEGRATION-GUIDE.md](OPENCODE-INTEGRATION-GUIDE.md)

---

## Mode 3: Cline MCP (VS Code)

### When to Use
✅ VS Code with Copilot/Claude  
✅ AI-assisted development  
✅ Multi-tool workflows  
✅ Cloud + local hybrid  

### Setup (5 minutes)

```bash
# 1. Install Cline in VS Code
# Open Extensions (Ctrl+Shift+X)
# Search "Cline"
# Install "Cline - Autonomous Coding Agent"

# 2. Start MCP server (in terminal)
cd /Users/buck/Documents/voice-setup-project
source voice_venv/bin/activate
python3 main.py --cli-mode cline --headless

# 3. In VS Code, open Cline (Ctrl+K)

# 4. Ask naturally
"Tell me a joke using the voice tool"
"Use voice_input to summarize this code"
```

### Available in Cline
```
@voice_input Tell me a joke       # Process voice
@get_status Show system health    # Check status
@list_memories Search for Python  # Find memories
```

### Best For
- Cloud + local hybrid workflows
- AI-assisted coding with voice
- Complex problem solving
- Professional development

**See**: [CLINE-INTEGRATION-GUIDE.md](CLINE-INTEGRATION-GUIDE.md)

---

## Comparison Matrix

### Capabilities per Mode

| Capability | Standalone | OpenCode | Cline MCP |
|------------|-----------|----------|-----------|
| Natural language | ✅ | ✅ | ✅ |
| Memory search | ✅ | ✅ | ✅ |
| System status | ✅ | ✅ | ✅ |
| Code editing | ❌ | ✅ | ✅ |
| IDE integration | ❌ | ✅ | ✅ |
| AI-assisted | ❌ | ❌ | ✅ |
| Cloud AI (Claude) | ❌ | ❌ | ✅ |
| Local only | ✅ | ✅ | ✅* |
| Automation | ✅ | ✅ | ❌ |
| Scripting | ✅ | ✅ | ❌ |

*Cline MCP can work with local LLMs only or cloud AI

### Performance

| Metric | Standalone | OpenCode | Cline MCP |
|--------|-----------|----------|-----------|
| First response | 3-5s | 3-5s | 3-5s |
| Subsequent | 1-2s | 1-2s | 1-2s |
| Memory search | <500ms | <500ms | <500ms |
| Status check | <100ms | <100ms | <100ms |

### System Requirements

| Requirement | Standalone | OpenCode | Cline MCP |
|-------------|-----------|----------|-----------|
| Python 3.12 | ✅ | ❌* | ✅ |
| Virtual env | ✅ | ❌* | ✅ |
| Terminal access | ✅ | ✅ | ✅ |
| IDE | ❌ | ✅ | ✅ |
| Network | ❌ | ❌ | Optional |
| Dependencies | Minimal | Minimal | Minimal |

*OpenCode IDE includes Python environment

---

## Getting Started Flowchart

```
Want to use voice?
│
├─ Only terminal access?
│  └─ Use: Standalone CLI
│     Setup: 2 min
│     Guide: STANDALONE-CLI-GUIDE.md
│
├─ Want to edit code?
│  │
│  ├─ Prefer OpenCode IDE?
│  │  └─ Use: OpenCode CLI
│  │     Setup: 3 min
│  │     Guide: OPENCODE-INTEGRATION-GUIDE.md
│  │
│  └─ Using VS Code?
│     └─ Use: Cline MCP
│        Setup: 5 min
│        Guide: CLINE-INTEGRATION-GUIDE.md
```

---

## First Time Setup

### Option 1: Standalone (Quickest)

```bash
# Step 1: Activate
cd /Users/buck/Documents/voice-setup-project
source voice_venv/bin/activate

# Step 2: Run
python3 main.py

# Step 3: Try it
Voice Assistant > tell me a joke
Voice Assistant > /help
```

**Time**: 2 minutes  
**Complexity**: Minimal

### Option 2: OpenCode (Recommended for coders)

```bash
# Step 1: Open OpenCode
opencode /Users/buck/Documents/voice-setup-project

# Step 2: Terminal (Ctrl+`)
# Step 3: Activate
source voice_venv/bin/activate

# Step 4: Run
python3 main.py --cli-mode opencode

# Step 5: Start coding with voice!
```

**Time**: 3 minutes  
**Complexity**: Low

### Option 3: Cline (Most powerful)

```bash
# Step 1: Install Cline in VS Code
# Ctrl+Shift+X → Search "Cline" → Install

# Step 2: Terminal
cd /Users/buck/Documents/voice-setup-project
source voice_venv/bin/activate

# Step 3: Start MCP server
python3 main.py --cli-mode cline --headless

# Step 4: Open Cline in VS Code (Ctrl+K)

# Step 5: Ask naturally
"Use voice_input to tell me a joke"
```

**Time**: 5 minutes  
**Complexity**: Medium

---

## Common Workflows

### Workflow 1: Quick Question

```
Fastest: Standalone
> tell me how JWT works
Response: [Answer]
> /quit
```

### Workflow 2: Code Writing Session

```
Best: OpenCode
1. Open OpenCode
2. Tell voice: "create a function that..."
3. Voice generates code
4. Edit in IDE
5. Ask voice: "how can I improve this?"
```

### Workflow 3: Complex Problem + AI

```
Best: Cline MCP
1. Open VS Code + Cline extension
2. Ask Cline to analyze code
3. Cline uses voice_input tool for perspective
4. Get cloud AI + local voice hybrid response
```

---

## Troubleshooting Quick Reference

### Issue: Can't start CLI
```bash
# Check environment
which python3
source voice_venv/bin/activate
python3 --version  # Should be 3.12

# Try again
python3 main.py
```

### Issue: No response from voice
```bash
# Check Ollama
ps aux | grep ollama
# If not running:
ollama serve

# Check status
/status
```

### Issue: Memory not working
```bash
# Verify file exists
ls -la voice_config.json
ls -la config/memory_config.json

# Reinitialize if needed
python3 -c "from memory import init; init()"
```

### Issue: Cline tools not appearing
```bash
# Restart Cline extension
Ctrl+Shift+P → "Reload Window"

# Or start fresh:
python3 main.py --cli-mode cline --headless
# Then in Cline: type "@" and look for tools
```

---

## Advanced: Running Multiple Modes

### Side-by-Side Development

```
Terminal 1:
source voice_venv/bin/activate
python3 main.py --cli-mode standalone
# Use for quick questions

Terminal 2:
opencode project/
# Edit code, can also use voice

Terminal 3:
python3 main.py --cli-mode cline --headless
# Available to VS Code/Cline extension
```

### Shared Memory

All three modes share the same memory database:
```bash
# In Standalone
/memory search python
# Found 3 memories

# Later in OpenCode
/memory search python
# Shows same 3 memories from earlier session
```

---

## Documentation Map

```
📚 GET STARTED
├─ This file (Quick Start)
├─ README.md (Overview)
└─ SETUP-COMPLETE.md (Installation history)

📖 INTEGRATION GUIDES
├─ STANDALONE-CLI-GUIDE.md (Mode 1)
├─ OPENCODE-INTEGRATION-GUIDE.md (Mode 2)
├─ CLINE-INTEGRATION-GUIDE.md (Mode 3)
└─ MCP-IMPLEMENTATION-GUIDE.md (Technical)

🔍 RESEARCH & REFERENCE
├─ RESEARCH-AND-STRATEGY.md (Why this design)
├─ accessibility-*.md (Accessibility research)
├─ macOS-*.md (Platform specific)
└─ FUTURE-WORK.md (Next steps)

⚙️ CONFIGURATION
├─ voice_config.json (Settings)
├─ config/memory_config.json (Memory config)
└─ main.py --help (CLI options)
```

---

## Decision Tree: Which Mode?

```
What's your primary use case?

1. I'm working in terminal only
   → Use STANDALONE
   → Time: 2 min
   → Guide: STANDALONE-CLI-GUIDE.md

2. I'm coding and want IDE + voice
   → Do you have OpenCode?
      YES → Use OPENCODE
           → Time: 3 min
           → Guide: OPENCODE-INTEGRATION-GUIDE.md
      NO  → Do you have VS Code?
           YES → Use CLINE MCP
                → Time: 5 min
                → Guide: CLINE-INTEGRATION-GUIDE.md
           NO  → Install either IDE first

3. I want cloud AI + local voice
   → Use CLINE MCP with Claude
   → Time: 5 min
   → Guide: CLINE-INTEGRATION-GUIDE.md

4. I want to integrate into my own app
   → Use the Python API directly
   → See: voice_orchestrator.py
   → See: MCP-IMPLEMENTATION-GUIDE.md
```

---

## Next Steps

### Immediate (Pick One)

**Option A - Explore Standalone (5 min)**
```bash
source voice_venv/bin/activate
python3 main.py
tell me about the voice system
/memory list
/quit
```

**Option B - Start with OpenCode (10 min)**
```bash
opencode /Users/buck/Documents/voice-setup-project
# (open terminal in IDE)
source voice_venv/bin/activate
python3 main.py --cli-mode opencode
```

**Option C - Try Cline MCP (15 min)**
```bash
# Install Cline extension first
# Then in terminal:
cd /Users/buck/Documents/voice-setup-project
source voice_venv/bin/activate
python3 main.py --cli-mode cline --headless
```

### Then

1. **Read** the appropriate guide for your mode
2. **Explore** available commands
3. **Build** your first workflow
4. **Create** custom memories
5. **Optimize** for your needs

---

## Support Resources

**For Standalone CLI**: [STANDALONE-CLI-GUIDE.md](STANDALONE-CLI-GUIDE.md)  
**For OpenCode IDE**: [OPENCODE-INTEGRATION-GUIDE.md](OPENCODE-INTEGRATION-GUIDE.md)  
**For Cline MCP**: [CLINE-INTEGRATION-GUIDE.md](CLINE-INTEGRATION-GUIDE.md)  
**For Technical Details**: [MCP-IMPLEMENTATION-GUIDE.md](MCP-IMPLEMENTATION-GUIDE.md)  
**For Architecture**: [RESEARCH-AND-STRATEGY.md](RESEARCH-AND-STRATEGY.md)

---

## Quick Command Reference

### Standalone Mode
```bash
tell me a joke              # Natural input
/voice [command]            # Explicit request
/status                     # System health
/memory search [query]      # Find memories
/help                       # All commands
/quit                       # Exit
```

### OpenCode Mode
```bash
tell me a joke              # Natural input
/voice [command]            # Explicit request
/status                     # System health
/memory search [query]      # Find memories
/help                       # All commands
/quit                       # Exit
```

### Cline MCP Mode
```
In Cline chat:
@voice_input tell me a joke             # Use tool
@get_status                             # Get status
@list_memories search python            # Find memories
"Use the voice tools to help with this" # Natural request
```

---

## Success Checklist

- ✅ Chosen a mode (Standalone, OpenCode, or Cline)
- ✅ Environment activated (`source voice_venv/bin/activate`)
- ✅ System started properly
- ✅ Made first voice request
- ✅ Verified memory was saved
- ✅ Read the full guide for your mode
- ✅ Ready to build workflows!

---

**Document Version**: 1.0  
**Last Updated**: February 21, 2026  
**Status**: Ready to Use

💡 **Tip**: Start with Standalone if unsure - fastest way to learn the system!
