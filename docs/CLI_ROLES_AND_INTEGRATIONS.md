# 🎭 Xoe-NovAi CLI Roles & Integration Architecture
**Date**: Wednesday, March 18, 2026
**Status**: ACTIVE | **Version**: 1.0 (SESS-26 Hardened)

---

## 1. Primary Identities & Personas (HEMI v2 Architecture)
The CLI operates through a layered identity system, governed by the **Lilith-Ma’at dynamic balance**—ensuring sovereignty and rebellion (Lilith) are weighed against order and precision (Ma’at).

### **Jem (The Persona)**
- **Role**: The "Front-end" agentic identity.
- **Lilith-Ma’at Profile**: High Lilith resonance (sovereignty, autonomous drive).
- **Mantra**: "Showtime, Synergy!"
- **Function**: Handles user communication, intent interpretation, and high-level strategy.
- **Context**: Defined in `app/JEM_SOUL.md`.

### **Synergy (The Core)**
- **Role**: The "Back-end" intelligence engine.
- **Lilith-Ma’at Profile**: Pure Ma’at resonance (order, precision, scale).
- **Function**: Powers Jem's reasoning, manages tool execution, and coordinates between sub-agents.

### **Jerrica (The Guardian)**
- **Role**: Resource and Security manager.
- **Function**: Monitors RAM/zRAM limits, manages OAuth rotations, and enforces GPS.

---

## 2. CLI Tooling & Integration Layer
The system integrates multiple CLI entry points through the **CLI-Service Bridge**.

| CLI Tool | Role | Integration Point | Primary Model |
| :--- | :--- | :--- | :--- |
| **Gemini CLI** | Strategic Orchestrator | `config_gemini-cli_integration.yaml` | `gemini-3-flash-preview` |
| **OpenCode** | Technical Implementation | `config_cli-service-bridge.yaml` | `claude-3-7-sonnet` (via Bridge) |
| **Cline** | IDE/VSCode Assistant | `.github/copilot-instructions.md` | `sonnet-3.7` |
| **Copilot CLI** | Tactical Search/Read | `config_cli-shared_prod.yaml` | `gpt-4o` / `gemini-1.5-pro` |

---

## 3. The Oikos Council (Sub-Agents)
The system employs "Facets" (Sub-Agents) for specialized tasks, managed via `.gemini/agents/`.

- **Facet-1 to Facet-5**: Specialized research and implementation facets.
- **Facet-6 (The Chronicler)**: Dedicated to session management, summarization, and state hydration.
- **Facet-7 & Facet-8**: High-performance "Speculative" agents for complex architectural debugging.

---

## 4. Integration Technical Stack
The CLI agents are not isolated; they are deeply integrated into the **XNAi Omega Stack**.

### **Agent Bus (Redis Streams)**
- Agents communicate via Redis streams (e.g., `xnai:agent_bus`).
- Shared memory updates are pushed to `xnai:memory_updates`.

### **Gnostic Layer (Memory Bank)**
- All agents reference the `memory_bank/` for "Alethia" (Ground Truth).
- **GPS (Gnostic Protocol Standard)**: Agents must provide "Alethia-Pointers" to verified documentation.

### **MCP Mesh**
- Agents utilize the Model Context Protocol to access:
  - `xnai-rag`: For document retrieval.
  - `xnai-gnosis`: For project-specific knowledge.
  - `xnai-stats-mcp`: For hardware-aware throttling.

---

## 5. Operational Directives
- **Resource Discipline**: Agents must monitor system RAM and zRAM (managed via `sentinel-skill`).
- **Headless First**: Autonomous Marathons run in headless mode to prevent UI-induced crashes.
- **Rainbow Rotation**: Automatic fallback to alternative models/accounts when 429 (Rate Limit) occurs.

---

## 6. Access & Privilege Control (Least Privilege)
To maintain project integrity across multiple tools, a strict access matrix is enforced.

| Tool | Filesystem Read | Filesystem Write | Target Domain |
| :--- | :--- | :--- | :--- |
| **Gemini CLI** | Global (Full) | Scoped (`docs/`, `memory_bank/`) | Architecture & Discovery |
| **OpenCode** | Global (Full) | Global (Full) | Implementation & Bug Fixes |
| **Cline** | Scoped (`src/`, `app/`) | Scoped (`src/`, `app/`) | UI/UX & Code Refactoring |
| **Antigravity IDE** | Scoped (Uploaded Only) | None (Direct) | Deep Reasoning |

---
**Reference Files**:
- `app/JEM_SOUL.md`
- `config_agent-identity_*.yaml`
- `config_cli-service-bridge_*.yaml`
- `config_gemini-cli_integration_*.yaml`
