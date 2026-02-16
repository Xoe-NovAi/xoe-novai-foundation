# UNIFIED MASTER STRATEGY: The "Sovereign Engine" (v3.5 Final)

This is the definitive blueprint for the fully automated, hardware-optimized, multi-agent development engine.

## 1. The Triple-CLI Master loop: "Thinking-Scout-Engineer" (Non-Interactive)
To prevent the engine from stalling on user confirmation, all agents MUST use **YOLO (Auto-Approve)** modes.

| Step | Agent | Model | Mandatory Flags |
| :--- | :--- | :--- | :--- |
| **1. Spec** | Gemini | **Flash 3** | `--prompt "..." --yolo --output-format json` |
| **2. Review** | Copilot | **Haiku 4.5** | `copilot --prompt "..." --yolo --silent` |
| **3. Finalize**| Gemini | **Flash 3** | `--prompt "..." --yolo` |
| **4. Execute** | Cline | **Kimi K2.5** | `cline --yolo "prompt"` |
| **5. Audit** | Gemini | **Flash 3** | `--prompt "..." --yolo` |

### 🚨 Critical Automation Rules
1.  **Binary Pathing**: Use the standalone `copilot` binary (not `gh copilot`) for automated reviews.
2.  **Streaming**: Always stream `stdout` in watcher scripts to monitor agent thought processes.
3.  **Timeout**: Use `--timeout 600` for Cline to prevent infinite loops in complex refactors.

## 2. Advanced Tool Mastery

### ♊ Gemini 3 Flash (The Orchestrator)
- **Explicit Context Caching**: 1M token cache for the 00-07 taxonomy (12h TTL).
- **Thinking Levels**: High for strategy, Medium for audits.

### 🚀 GitHub Copilot (The Scout)
- **Agent Skills**: Using `.github/skills/` to teach Copilot specialized XNAi workflows.
- **Path-Specific Context**: Using `.github/instructions/` for hyper-local guidance.

### 🤖 Cline (The Engineer)
- **Track-Isolated Sessions**: `--config` isolation for concurrent task tracks.
- **Active Listener**: Triggers automatically on `spec_finalized` message.

## 3. Hardware Sovereignty (Ryzen 7 5700U)
- **Architecture**: Zen 2 / Lucienne with Vega 8 iGPU.
- **Vulkan Performance**:
  - Wavefront Size: **64-wide** (Vega Standard).
  - Environment: `RADV_PERFTEST=gpl` (for shader efficiency).
- **Memory**: Aggressive **Multi-Tiered zRAM** (lz4 + zstd) with `swappiness=180`.
- **Experimental**: **AWQ** remains **DISABLED** (GGUF is the production standard).

## 4. Maintenance
The `scripts/agent_watcher.py` is the pulse of this engine. It must be updated as new Model Context Protocol (MCP) servers or CLI features are released.
