# CLI Nomenclature Guide v1.0.0

**Last Updated**: 2026-02-17  
**Status**: ACTIVE - Zero-Hallucination Protocol  
**Scope**: XNAi Foundation terminal CLIs and IDE plugins

---

## Purpose

This guide establishes **strict nomenclature standards** to eliminate confusion between terminal-based CLI tools and their IDE plugin counterparts. All team members and agents must use these conventions consistently.

---

## Core Rule

> **CLI references (bare names) refer ONLY to terminal CLI variants.**  
> **IDE plugins MUST use explicit naming to denote they are NOT CLI variants.**

---

## Nomenclature Standards

### Terminal CLIs (Bare Names)

Use these names ONLY when referring to terminal-based tools:

| CLI Name | Full Name | Version | Purpose |
|----------|-----------|---------|---------|
| **Copilot** | GitHub Copilot CLI | v0.0.410 | GitHub-native AI assistant |
| **Cline** | Cline CLI | v2.2.3 | Multi-provider AI coding assistant |
| **OpenCode** | OpenCode CLI | v1.2.6 | Advanced code reasoning & generation |
| **Gemini** | Gemini CLI | v0.28.2 | Google Gemini model access |

**Example usage:**
- ✅ "Run `copilot --help` to see models"
- ✅ "Cline CLI supports OpenRouter free tier"
- ✅ "OpenCode has 5 built-in free models"
- ✅ "Gemini CLI uses Google AI Studio API"

### IDE Plugins (Explicit Names)

Always include IDE context and plugin type:

| IDE Plugin | Full Name | Provider |
|------------|-----------|----------|
| **Cline VS Code Extension** | Cline plugin for VS Code | Cline |
| **Copilot VS Code Extension** | GitHub Copilot plugin for VS Code | GitHub |
| **OpenCode IDE** | OpenCode integrated development environment | OpenCode |
| **Cline with kat-coder-pro** | Cline enhanced with kat-coder-pro plugin | VS Code ecosystem |

**Example usage:**
- ✅ "The Cline VS Code Extension can use local models"
- ✅ "Copilot VS Code Extension has real-time code completion"
- ✅ "OpenCode IDE integrates project-wide context"
- ✅ "Cline with kat-coder-pro provides advanced code editing"

---

## Special Cases

### Agent Roles vs Tools

When referring to agents/orchestrators, use clear role labels:

| Role | Type | Primary Tool | Notes |
|------|------|--------------|-------|
| **Agent: Copilot** | CLI Agent | Copilot CLI | XNAi orchestration & planning |
| **Agent: Cline** | CLI Agent | Cline CLI | Code implementation & review |
| **Agent: Gemini** | CLI Agent | Gemini CLI | Synthesis & complex reasoning |
| **Agent: OpenCode** | CLI Agent | OpenCode CLI | Research & codebase exploration |
| **Mission Control (MC)** | Project Agent | Claude.ai Project | Strategic oversight (GitHub-synced) |

**Example usage:**
- ✅ "Agent: Copilot orchestrates the workflow"
- ✅ "Agent: Cline implements the changes"
- ✅ "Agent: Gemini provides synthesis"
- ✅ "Mission Control monitors all initiatives"

---

## Workspace Locations

### Terminal CLI Configurations

```
/home/arcana-novai/Documents/xnai-foundation/
├── .opencode/
│   └── opencode.json          # OpenCode CLI config
├── .clinerules/
│   ├── 00-core-context.md     # Cline CLI context
│   └── ...
└── .copilot/
    └── config.json             # Copilot CLI config (if exists)
```

### IDE Plugin Configurations

```
/home/arcana-novai/.config/Code/
├── extensions/                 # VS Code extension data
└── settings.json              # VS Code settings

~/.anthropic/
├── claude-ai-config.json      # Claude.ai project refs

~/.opencode-ide/
└── ...                        # OpenCode IDE settings
```

---

## Communication Examples

### ✅ CORRECT Usage

"I'll use the Cline CLI with OpenRouter free tier to implement the feature. The OpenCode CLI can then audit the code, and Copilot CLI will orchestrate the workflow."

"The Cline VS Code Extension provides real-time feedback, while the Cline CLI handles batch operations in CI/CD pipelines."

"Mission Control reviews progress from the Claude.ai Project's GitHub sync."

"Agent: Cline implements via CLI, Agent: OpenCode reviews via CLI, Copilot CLI orchestrates both."

### ❌ INCORRECT Usage

"I'll use Cline to implement the feature." ← Ambiguous (CLI or VS Code Extension?)

"OpenCode will handle this." ← Unclear (CLI or IDE?)

"Copilot is running slow." ← Which Copilot? (CLI or VS Code Extension?)

"Grok MC runs Claude Opus." ← Wrong (Grok runs Grok models, not Claude)

"Gemini CLI uses GPT models." ← Wrong (Gemini CLI uses Gemini models only)

---

## Enforcement Rules

### For Documentation
- All docs MUST use CLI-explicit naming
- Any ambiguous naming gets flagged as error
- IDE plugin features must include "(IDE)" suffix

### For Code Comments
- Use full agent role names: "Agent: Copilot does X"
- Never shorten to bare names in ambiguous contexts
- Prefix with CLI type: "Cline CLI config at X"

### For Team Communication
- Slack/email: Always specify terminal vs IDE
- GitHub issues: Use this guide's terminology
- Agent outputs: Always use correct nomenclature

### For Configuration Files
- `.clinerules/` = Cline CLI config (terminal)
- `.opencode/` = OpenCode CLI config (terminal)
- `.vscode/settings.json` = VS Code settings (IDE)
- `claude-ai-project/` = Claude.ai Project config (web/cloud)

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-02-17 | Initial release - CLI/IDE distinction rules |

---

## Questions?

Refer to:
- Agent assignments: `AGENT-CLI-MODEL-MATRIX-v1.0.0.md`
- CLI models: `expert-knowledge/` model card files
- Agent roles: `memory_bank/activeContext.md`
