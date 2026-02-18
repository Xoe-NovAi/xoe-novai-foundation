# OpenCode CLI Best Practices

## Overview

OpenCode is an open-source CLI tool for AI-assisted software engineering. It supports 75+ LLM providers, local models via Ollama, and MCP (Model Context Protocol) servers for extensibility.

## Installation

```bash
# Via npm
npm install -g @opencode/cli

# Via Homebrew
brew install opencode
```

## Configuration

### opencode.json

Configuration file at project root or `~/.opencode/`:

```json
{
  "model": {
    "provider": "ollama",
    "model": "devstral:latest",
    "options": {
      "temperature": 0.7,
      "num_ctx": 32768
    }
  },
  "mcp": {
    "servers": {}
  },
  "skills": {
    "auto_load": true
  }
}
```

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `OPENCODE_MODEL` | Default model |
| `OPENCODE_PROVIDER` | Default provider |
| `OPENCODE_API_KEY` | API key for cloud providers |

## CLI Commands

### Core Commands

```bash
# Start interactive session
opencode

# Run with specific model
opencode --model llama3.2

# Execute single command
opencode -p "Explain this codebase"

# Run with specific skill
opencode --skill memory-bank-loader

# Run agent
opencode --agent xnai-researcher "Research RAG patterns"
```

### File Operations

```bash
# Read and analyze files
opencode -p "Analyze src/main.py"

# Generate code
opencode -p "Create a FastAPI endpoint for /health"

# Refactor
opencode -p "Refactor this function to use AnyIO"
```

### Git Integration

```bash
# Commit with AI-generated message
opencode commit

# Create PR
opencode pr --title "Feature: Add RAG API"

# Review changes
opencode review
```

## Project Structure

```
project/
├── AGENTS.md              # Project rules (like CLAUDE.md)
├── .opencode/
│   ├── opencode.json      # Configuration
│   ├── skills/
│   │   └── skill-name/
│   │       └── SKILL.md
│   ├── agents/
│   │   └── agent-name.md
│   ├── commands/
│   │   └── command-name.md
│   └── tools/
│       └── tool-name.ts
└── mcp-servers/
    └── server-name/
        ├── server.py
        ├── requirements.txt
        └── README.md
```

## AGENTS.md Format

Similar to CLAUDE.md, provides project context:

```markdown
# Project Name

## Overview
Brief description

## Core Principles
1. Principle one
2. Principle two

## Tech Stack
- Technology 1
- Technology 2

## Development Workflow
1. Step one
2. Step two
```

## Skills

Skills define reusable workflows. Create in `.opencode/skills/name/SKILL.md`:

```markdown
# Skill Name

## Purpose
What this skill does

## Trigger
When to activate

## Workflow
### Step 1: ...
### Step 2: ...
```

## Agents

Agents are specialized personas. Create in `.opencode/agents/name.md`:

```markdown
# Agent Name

## Role
Description

## Capabilities
- Capability 1
- Capability 2

## Tools Used
- tool-name
```

## Commands

Custom slash commands. Create in `.opencode/commands/name.md`:

```markdown
# Command Name

## Purpose
What this command does

## Usage
/command-name [options]

## Workflow
1. Step one
2. Step two
```

## MCP Integration

MCP servers extend OpenCode capabilities:

```json
{
  "mcp": {
    "servers": {
      "server-name": {
        "command": "python",
        "args": ["mcp-servers/server-name/server.py"],
        "env": {
          "API_URL": "http://localhost:8000"
        }
      }
    }
  }
}
```

## Best Practices

### 1. Use AGENTS.md for Project Context
- Define core principles
- Document tech stack
- Specify workflow patterns

### 2. Create Skills for Repeated Tasks
- Memory bank loading
- Test running
- Documentation updates

### 3. Use Agents for Specialized Work
- Research agent
- Security auditor
- Code reviewer

### 4. Leverage MCP for External Tools
- RAG integration
- Task management
- Database queries

### 5. Configure Local Models
- Use Ollama for offline capability
- Match model to task complexity
- Set appropriate context windows

## Performance Tips

| Task | Recommended Model | Context |
|------|-------------------|---------|
| Quick fixes | llama3.2:latest | 8K |
| Code review | devstral:latest | 32K |
| Research | mistral:latest | 32K |
| Architecture | deepseek-coder:latest | 64K |

## Error Handling

```bash
# Verbose mode for debugging
opencode --verbose

# Check logs
cat ~/.opencode/logs/latest.log

# Reset configuration
opencode --reset
```

## Integration with XNAi Foundation

OpenCode integrates with the Foundation stack via:
- MCP servers for RAG, Agent Bus, Vikunja
- Skills for memory bank, phase validation
- Agents for specialized research and architecture
- AGENTS.md for project rules
