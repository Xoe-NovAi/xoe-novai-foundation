# 🧠 Xoe-NovAi Elite Agent Infrastructure (Complementary Tooling)

> **⚠️ NOTE: COMPLEMENTARY TOOLING**
> This documentation covers the advanced agentic orchestration layer. While these tools are included in the repository to enhance the developer experience and build performance, they are **OPTIONAL** and complementary to the core Xoe-NovAi Foundation stack services (RAG, UI, Voice).

---

## 🤵 1. The Butler System (`scripts/infra/butler.sh`)
The Butler is a high-level infrastructure orchestrator designed for Ryzen-based systems.
- **Ryzen Core Steering**: Automatically pins AI workloads to cores 0-11 and background tasks to 12-15.
- **Build Bridge**: Manages rootless Podman BuildKit cache mounts and temporary build logs.
- **Resource Guard**: Monitors ZRAM and enforces the 400MB soft-stop rule.

## 🤖 2. Master-Class Agents
Defined in `.gemini/agents/`, these specialized LLM personas handle complex project tasks:
- **`stack-researcher`**: Expert in Podman 5.x, BuildKit, and RAG architecture.
- **`qa-specialist`**: Specialized in log analysis, test execution, and build stabilization.
- **`turn-auditor`**: Meta-agent that identifies "Turn-Wasting" blockers (like .gitignore issues) to optimize AI performance.

## 📂 3. Model Context Protocol (MCP) Integration
Xoe-NovAi utilizes the **Model Context Protocol** to give agents direct, safe access to the local environment.
- **Configuration**: Located in `.gemini/settings.json`.
- **Primary Server**: A local filesystem server powered by `uvx` and `@modelcontextprotocol/server-filesystem`.
- **Benefit**: Allows agents to use high-performance, standardized tools for file manipulation and analysis.

## 🛠️ 4. The Agent Manager (`scripts/dev/run_agent.sh`)
Since some internal agent delegation tools are restricted, Xoe-NovAi includes a host-side wrapper to invoke custom agents reliably.
```bash
./scripts/dev/run_agent.sh qa-specialist "Analyze the last build log for errors"
```

## 📈 5. Why Use These?
cloning the Xoe-NovAi repo provides more than just a stack; it provides a **Self-Healing Development Environment**. These agents are designed to "teach" themselves about the project by reading the `memory_bank/` and `expert-knowledge/` bases, allowing them to assist in complex refactors and infrastructure hardening autonomously.
