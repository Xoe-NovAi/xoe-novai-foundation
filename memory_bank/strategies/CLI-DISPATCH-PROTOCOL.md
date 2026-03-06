---
tool: cline
model: claude-sonnet-4-6
account: arcana-novai
git_branch: main
session_id: sprint9-2026-02-21
version: v1.0.0
created: 2026-02-21
tags: [protocol, cli-dispatch, multi-agent, orchestration]
---

# CLI Dispatch Protocol v1.0

## Purpose

Enable the Sovereign MC Agent to dispatch tasks to external AI CLIs (Cline, Gemini, Copilot) via bash commands, aggregating results into a unified workflow.

## Available CLIs

| CLI | Binary Path | Auth Method | Best For |
|-----|-------------|-------------|----------|
| **Cline** | `~/.nvm/versions/node/v25.3.0/bin/cline` | VS Code extension | IDE-integrated coding |
| **Gemini** | `~/.nvm/versions/node/v25.3.0/bin/gemini` | Google OAuth | Research, 1M context |
| **Copilot** | `~/.local/bin/copilot` | GitHub OAuth | GitHub integration |

## Dispatch Patterns

### Pattern 1: Research Task → Gemini CLI

```bash
# Dispatch research task to Gemini
gemini --model gemini-2.5-pro "Research topic: [TOPIC]. Output as markdown."

# With file context
cat context.md | gemini --model gemini-2.5-pro "Analyze this and provide recommendations."
```

### Pattern 2: GitHub Task → Copilot CLI

```bash
# PR review
copilot review --pr https://github.com/org/repo/pull/123

# Issue analysis
copilot explain "What does this codebase do?"
```

### Pattern 3: Coding Task → Cline (via file-based dispatch)

```bash
# Cline runs as VS Code extension - dispatch via task file
echo "Task: Implement X feature" > /tmp/cline-task.md
# User manually triggers Cline in IDE
```

## Integration with Sovereign MC Agent

The `cli-dispatch` skill/subagent is invoked via `@cli-dispatch` in OpenCode CLI.

### Dispatch Decision Tree

```
Task Type?
├── Research/Web Search → Gemini CLI (gemini-2.5-pro)
├── GitHub Operations → Copilot CLI
├── Code Implementation → Cline (IDE) or Sonnet (Antigravity)
├── Architecture Review → Opus 4.6 (Antigravity)
└── Fast Prototyping → Gemini Flash or Groq
```

## Output Aggregation

All CLI outputs should be captured and stored:

```bash
# Capture output to session state
gemini --model gemini-2.5-pro "Research X" 2>&1 | tee session-state-archives/gemini-output-$(date +%Y%m%d-%H%M%S).md
```

## Rate Limit Awareness

| CLI | Rate Limit | Fallback |
|-----|------------|----------|
| Gemini CLI | 25 req/day (Pro) | Gemini Flash (higher) |
| Copilot | ~50 chat/day | N/A |
| Cline | Unlimited (local) | N/A |

## Error Handling

1. **CLI not found**: Check binary path, suggest installation
2. **Auth expired**: Re-run auth flow for the CLI
3. **Rate limited**: Fall back to next CLI in waterfall
4. **Timeout**: Kill process after 5 minutes, log error

## Session State Persistence

Store dispatch results in:
- `session-state-archives/cline-sessions/` - Cline outputs
- `session-state-archives/gemini-sessions/` - Gemini outputs
- `session-state-archives/copilot-sessions/` - Copilot outputs

---

**Version**: 1.0.0
**Status**: Active
**Next Review**: 2026-03-21