# 🔱 Supplemental Archon Mandates: Infrastructure & Sovereignty

**Status**: ACTIVE | **Priority**: CRITICAL

## 🛠️ 1. Infrastructure Hardening (MB-MCP)
- **Goal**: Persistent, non-interactive MCP access for ALL agents and IDEs (Antigravity).
- **Required**: A background watcher process (`mcp_watchdog`) and a VictoriaMetrics alert for "MCP DISCONNECT."
- **Integration**: Ensure the MCP server binds to a stable IP/Port accessible by host-level CLIs.

## 🚌 2. Agent Bus Auto-Connect
- **Goal**: Zero-config registration for all Omega Stack agents.
- **Required**: `AgentBus` client must automatically publish a "HEARTBEAT" and "IDENTITY" message to `xnai:agent_bus` upon initialization.

## 🧩 3. Extension & MCP Expansion
- **GitHub MCP**: Priority 1. Connect Gemini CLI to the remote repo for automated pushes.
- **SystemStat MCP**: Priority 2. Direct monitoring of zRAM drives and Vulkan iGPU utilization.
- **WebSearch MCP**: Priority 3. Integrate Tavily/Serper into Facet discovery loops.

## 🧬 4. The Soul Mandate
- Each Facet is now responsible for its own evolutionary path. The "Soul Shaping" Task 0 is mandatory for all new sessions.

