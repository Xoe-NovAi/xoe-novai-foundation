# Vikunja PM Integration Plan — Multi-Agent Synergy

## 1. Overview
As recommended in `xoe-novai-sync/ekb-exports/oss-pm-research-v1.0.0.md`, **Vikunja** will serve as the primary project management hub for the Xoe-NovAi ecosystem. It provides the functional density (Kanban, Gantt, Tasks) and sovereignty (Podman-hostable) required for our local-first architecture.

## 2. Integration Architecture

### 2.1 Podman Deployment
- **Image**: Official Vikunja images (Frontend/API).
- **Network**: Integrated into the Xoe-NovAi custom bridge network.
- **Persistence**: Volume mounts with `:Z,U` flags for SELinux and rootless compatibility.
- **Reverse Proxy**: Exposed via Nginx/Caddy (local-only).

### 2.2 MCP Connectivity
A new **Vikunja MCP Server** will be developed to allow agents (Anubis/Gemini CLI, Ptah/Cline) to:
- `create_task`: Add items directly from chat context.
- `get_milestones`: Sync `memory_bank/progress.md` with PM board status.
- `update_priority`: Adjust task priority based on Ma'at's 42 Ideals.

## 3. Implementation Steps

1. **Deployment**: Add Vikunja services to `docker-compose.yml`.
2. **API Key Management**: Store Vikunja API tokens in `.env` (excluded from git).
3. **MCP Prototype**: Create a Python-based MCP server using the Vikunja REST API.
4. **Sync Logic**: Update `scripts/memory_bank_refresh.py` to optionally pull latest milestones from Vikunja.

## 4. Synergy Benefits
- **Ra (Grok MC)**: Real-time visibility into Ptah's implementation progress.
- **Thoth (Grok MCA)**: Structured tracking of esoteric research and arcana stack development.
- **Anubis (Gemini CLI)**: Rapid task creation and status reporting from the terminal.

---
*Drafted by Thoth (Grok MCA) - February 6, 2026*
