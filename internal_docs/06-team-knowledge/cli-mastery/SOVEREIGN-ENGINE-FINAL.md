---
last_updated: 2026-02-14
status: finalized
persona_focus: All Agents
agent_impact: critical
related_phases: Phase-4.1
---

# Sovereign Engine Mastery: Conclusive Automation Framework

This research concludes the setup of the Xoe-NovAi multi-agent automation loop.

## 1. Conclusive Strategy: Reactive Autonomy
The Sovereign Engine is **Reactive**. It does not perform work unless a signal is detected in the `communication_hub/inbox`.
- **Gemini 3 Flash** is the "Thinker" that generates these signals.
- **Kimi K2.5 (Cline)** and **Haiku 4.5 (Copilot)** are the "Executors" that wait for them.

## 2. Advanced Tool Protocols (Non-Interactive)
All agents must adhere to the following command signatures to ensure the loop never stalls:

### 🤖 Cline CLI (The Engineer)
- **Flag**: `--yolo` (Auto-approves all tool calls).
- **Flag**: `--json` (Outputs structured messages for the watcher).
- **Flag**: `--taskId <id>` (Resumes interrupted implementation tracks).

### 🚀 Copilot CLI (The Scout)
- **Flag**: `--yolo` (Allows all permissions automatically).
- **Flag**: `--silent` (Clean stdout for redirection).
- **Binary**: Use `/home/arcana-novai/.local/bin/copilot` (Standalone).

### ♊ Gemini CLI (The Orchestrator)
- **Flag**: `--prompt` (Headless mode).
- **Flag**: `--yolo` (Auto-approves auditing/file management).

## 3. Centralized MCP Hub (The Command Center)
We have implemented a custom MCP server (`scripts/xnai_mcp_server.py`) using **FastMCP**. This server allows agents to:
- **`send_agent_message`**: Assign tasks to peers programmatically.
- **`get_system_load`**: Monitor Ryzen host resources (NPU/iGPU load).
- **`read_agent_outbox`**: Audit cross-agent results.

## 4. Operational Instructions for Human Director
To keep the engine running:
1.  **Maintain the Pulse**: Keep `python3 scripts/agent_watcher.py` running in a dedicated terminal.
2.  **Dispatch the Vision**: Use Gemini CLI to assign the high-level roadmap.
3.  **Review the Logs**: Check `internal_docs/communication_hub/state/` for real-time agent heartbeats.
