---
last_updated: 2026-02-14
status: active
persona_focus: Copilot
agent_impact: high
related_phases: All
---

# Copilot CLI Mastery

GitHub Copilot CLI serves as our **Tactical Scout** (Haiku 4.5+).

## ⚙️ Advanced Configuration

### 1. Custom Instructions
- **Global**: `~/.github/copilot-instructions.md` (Not recommended for our multi-agent stack).
- **Workspace**: `.github/copilot-instructions.md` (Primary Ground Truth for Copilot).
- **Path-Specific**: Use `.github/instructions/NAME.instructions.md` to provide hyper-local context (e.g., `api.instructions.md` for FastAPI routes).

### 2. Aliases for Speed
Configure your shell to use unified aliases:
```bash
alias ghcs='gh copilot suggest'
alias ghce='gh copilot explain'
alias ghcr='gh copilot -p "Review this file" --silent'
```

### 3. Programmatic Reviews
Use the `--silent` flag and redirection for automated audits.
```bash
gh copilot -p "Review internal_docs/00-system/MASTER-STRATEGY.md for inconsistencies." --silent > logs/scout_report.txt
```

## 🤖 Automation Strategy: The "Scout" Role
1.  **Auditor**: Reviews `spec.md` before implementation.
2.  **Snippet Generator**: Generates boilerplate code for Cline to integrate.
3.  **Shell Assist**: Explains complex terminal errors during Phase 4.1 testing.

## 🛡️ Best Practices
- **JSON Delivery**: When used programmatically, always append "Deliver response as raw JSON" to the prompt.
- **Context Loading**: Use the `gh copilot -p "Based on [file]..."` pattern to ensure Copilot is grounded in specific project artifacts.
- **Safety**: Never use `--allow-all-tools` in production; whitelist specific tools if needed.
