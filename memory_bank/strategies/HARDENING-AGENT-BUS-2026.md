# 🏙️ Omega Metropolis: Agent Bus Hardening (2026)
**Strategy**: WAVE 5 (Hardening) | **Coordination Key**: `HARDENING-AGENT-BUS-2026`
**Status**: ACTIVE | **Owner**: MC-Overseer

---

## 📜 The Genesis: Origin Story & Vision
The Omega Stack was born from a singular mission: **Sovereignty**. It was created by a non-programmer who saw a gap in the local AI community—the lack of an advanced, local-first RAG system that could rival cloud solutions on mid-grade hardware (Ryzen 5700U). 

Built entirely using free AI tools (OpenCode, Copilot, Gemini, Grok), this project is a testament to the power of human-AI collaboration. The "Metropolis" vision is to give this sovereign power back to the community, proving that you don't need a massive compute budget or deep coding knowledge to build the "ultimate expert" system.

---

## 🏗️ Architectural Scaffolding: The 8-Domain Expert Network

### 1. Isolated Expertise (Instance 1-8)
We have deployed 8 distinct, persistent domain experts, each with its own isolated memory and state:
*   **Domain 1: Architect** (System Blueprinting, Mermaid diagrams)
*   **Domain 2: API / Backend** (FastAPI, Redis Streams, AnyIO)
*   **Domain 3: UI / Frontend** (Chainlit, Open WebUI, Dashboard)
*   **Domain 4: Voice / Audio** (Speech-to-text integration)
*   **Domain 5: Data / RAG** (Qdrant, PostgreSQL, Gnosis Engine)
*   **Domain 6: Ops / Infra** (Podman, Caddy, CI/CD)
*   **Domain 7: Research** (Scholarly ingestion, metadata extraction)
*   **Domain 8: Test / QA** (Pytest, Coverage, Integration testing)

### 2. Multi-Account Rotation (The "8-Account Pulse")
To maximize free tier limits (Gemini Pro/Flash, Copilot Raptor), we utilize:
*   **Sticky Domains**: Each expert is mapped to a specific Google account (1-8).
*   **Dynamic Rotation**: The `xnai-gemini-dispatcher.sh` switches accounts when quota limits are reached.
*   **Observability**: The **Omega Dashboard** (dashboard/index.html) provides a real-time view of tokens, messages, and quota health for all 8 experts.

---

## 🧩 MCP & Tool Hardening Roadmap

### 1. Unified Configuration (The `/settings` Sync)
*   **Sync Logic**: All 8 experts share a Master `settings.json` and `mcp_config.json` via the `xnai-sync-gemini-configs.sh` script.
*   **UX Consistency**: Ensure "Context Usage" and "Percentage" displays are unified across all 8 experts.

### 2. Community MCP Integration
We are integrating the following MCP servers to enhance Gemini CLI performance:
*   **Memory Bank MCP**: Direct read/write access to project history and context.
*   **Gnosis MCP**: Local search across the vector database (Qdrant).
*   **System Explorer MCP**: Real-time monitoring of host resources (CPU, Memory, ZRAM).
*   **Search MCP**: Targeted web search (Serper) to bypass regional knowledge cutoffs.

---

## 🔒 Security & System Hardening
*   **ProxyChains**: Route only API key collection through proxy to bypass regional availability blocks.
*   **Rootless Podman**: All services isolated in rootless containers with `:Z,U` volumes.
*   **Credential Masking**: Automated scrubbing of API keys and secrets from logs.

---

## 📋 Future Scenario Planning
1.  **Phase 5.1**: Complete the Antigravity OAuth restoration for Opus 4.6 Thinking access.
2.  **Phase 5.2**: Deploy the "4-Level Escalation Chain" for deep research tasks.
3.  **Phase 5.3**: Community Release of the "Omega Metropolis" setup guide for non-programmers.

---
**Custodian**: Gemini CLI (MC-Overseer)
**Verification Key**: `OMEGA-METROPOLIS-HARDENING-2026-03-04`
