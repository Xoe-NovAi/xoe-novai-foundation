---
last_updated: 2026-02-14
status: active
persona_focus: Gemini
agent_impact: critical
related_phases: Phase-4.1
---

# CLI Automation Flags Reference

Use this reference when writing automation scripts or multi-agent handoff routines.

## ♊ Gemini CLI
| Feature | Flag/Command | Description |
| :--- | :--- | :--- |
| Non-interactive | `--prompt "..."` / `-p "..."` | Execute a prompt and exit. |
| Pipe Input | `cat file.txt | gemini` | Ingest context via stdin. |
| JSON Output | `--output-format json` | Machine-readable response + metadata. |
| Model Override | `--model [name]` | Select specific model for task. |

## 🤖 Cline CLI
| Feature | Flag/Command | Description |
| :--- | :--- | :--- |
| Direct Prompt | `cline -p "..."` | Assign a coding task directly. |
| Mode Select | `cline --mode [code|architect]` | Choose the agent persona. |
| Continuous | `cline --headless` | Run without interactive prompts (if supported). |

## 🚀 GitHub Copilot CLI
| Feature | Flag/Command | Description |
| :--- | :--- | :--- |
| Programmatic | `gh copilot -p "..."` | Single-shot prompt. |
| Silent | `--silent` | Clean output for piping. |
| Auto-Tool | `--allow-all-tools` | Grants permission to execute shell. |
| Shell Assist | `gh copilot suggest` | Tactical shell command generation. |

## 🛠️ Shell Orchestration Example
```bash
# Gemini creates the plan, Cline implements it
PLAN=$(gemini -p "Create an atomic implementation plan for Redis circuit breakers" --output-format json | jq -r '.response')
cline -p "Implement the following plan: $PLAN"
```
