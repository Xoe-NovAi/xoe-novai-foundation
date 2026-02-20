---
name: cli-dispatch
description: 'Enables agents to trigger external AI CLIs (Cline, Gemini, Copilot, OpenCode) directly via bash.'
license: MIT
compatibility: opencode
metadata:
  workflow: multi-agent-orchestration
---

## Purpose
This skill provides standardized instructions for an agent to delegate tasks to external command-line AI interfaces.

## Available CLIs & Patterns

| CLI | Target Model | Pattern |
|-----|--------------|---------|
| **Cline** | `kat-coder-pro` | `cline --yolo --timeout 600 "task"` |
| **Gemini** | `gemini-2.5-flash` | `gemini -p "task"` |
| **Copilot** | `github-copilot` | `copilot -p "task"` |
| **OpenCode** | `various` | `opencode run -m [model] -p "task"` |

## When to Use
- When a task requires the 1M context window of the Gemini CLI.
- When a task requires the specialized agentic coding of kat-coder-pro (via Cline).
- When parallel execution in another process is desired to avoid context bloat in the current session.

## Implementation Instructions
1. Analyze the user request to determine if an external CLI is more appropriate.
2. Select the CLI based on the `Selection Logic` defined in the agent profile.
3. Formulate a precise, standalone prompt for the target CLI.
4. Execute the command using the `bash` tool.
5. Capture and summarize the output for the user.
