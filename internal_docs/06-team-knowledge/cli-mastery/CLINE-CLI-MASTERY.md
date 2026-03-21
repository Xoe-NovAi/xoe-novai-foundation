---
last_updated: 2026-02-14
status: active
persona_focus: Cline
agent_impact: critical
related_phases: All
---

# Cline CLI Mastery

The Cline CLI is the autonomous engineer of the Xoe-NovAi Foundation.

## ⚙️ Advanced Configuration
Cline CLI loads instructions from the workspace root by default.

### 1. The `.clinerules` Protocol
- **Discovery**: Cline CLI automatically loads `.clinerules` (file) or `.clinerules/` (directory) in the current working directory.
- **Priority**: Workspace rules always override global rules.
- **Modularity**: Use a directory (`.clinerules/*.md`) for cleaner management of coding standards, security, and workflow.

### 2. Isolated Instances
Use the `--config` flag to run isolated automation sessions.
```bash
# Point to a specific configuration directory for a dedicated task
cline --config .gemini/tmp/task_123 -p "Implement Redis circuit breakers"
```

### 3. Environment Variables
- `CLINE_DIR`: Override the default data directory (`~/.cline/data/`). Useful for CI/CD or containerized execution.

## 🤖 Automation Patterns
- **Handoffs**: Gemini writes a task to the `inbox/` -> Watcher triggers `cline -p "..."`.
- **Self-Correction**: Cline is instructed via `.clinerules/10-spec-listener.md` to halt and request assistance if a spec is flawed.
- **Result Capturing**: Always capture Cline's output to the `outbox/` for Gemini's audit.

### 4. Non-Interactive Automation (YOLO)
For autonomous handoffs, use the `-y` or `--yolo` flag. This automatically approves all tool actions (reads, writes, commands).
```bash
cline --yolo "Task prompt"
```
**Warning**: Only use YOLO mode in isolated environments or when the agent is grounded in a finalized `spec.md`.
