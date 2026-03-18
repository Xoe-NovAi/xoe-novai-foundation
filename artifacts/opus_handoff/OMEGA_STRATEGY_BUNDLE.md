# 🧠 OMEGA BUNDLE 1: STRATEGIC VISION (The Mind)
**Target**: Opus 4.6 (Antigravity)
**Contents**:
1.  `OMEGA_OMNIBUS_v1.md` (The Vision)
2.  `AMR_STRATEGY_ROADMAP.md` (The Plan)
3.  `CLI_ROLES_AND_INTEGRATIONS.md` (The Roles)
4.  `CLI_ROUTING_DECISION_FRAMEWORK.md` (The Logic)

---
# FILE 1: OMEGA_OMNIBUS_v1.md
# 🦅 OMEGA OMNIBUS: THE UNIFIED STRATEGIC VISION (v1.0)
**Date**: March 18, 2026
**Target**: Global Omega Stack (v4.6)
**Status**: SEEDED (Active Strategy)

---

## 1. THE VISION: GNOSTIC ORCHESTRATION
We are transitioning from a fragmented "Xoe-NovAi Foundation" to a unified "Omega Stack."
**Core Principle**: "Seeded Cognitive Compression" (SCC).
-   We compress knowledge into high-density "seeds" (Gnosis) rather than storing raw data.
-   We execute via a clear hierarchy: **Logos** (Strategy) → **Praxis** (Execution) → **Archon** (Orchestration).

---

## 2. INFRASTRUCTURE HARDENING (12GB CONSTRAINT)
**Hardware Reality**: AMD Ryzen 7 5700U (Zen 2) | 12GB RAM | 8GB zRAM (lz4/zstd).
**Mandates**:
1.  **Turn-Based Queue**: Concurrent services must be gated to stay under 6.5GB RAM.
2.  **Vulkan Acceleration**: `llama-cpp-python` must use iGPU (Vega 8) for inference (2x speedup).
3.  **Port Isolation**:
    -   `RAG API`: **8012** (Resolved conflict with Prometheus on 8002).
    -   `Oikos`: **8006**.
    -   `Memory Bank`: **8005**.
    -   `Gateway`: **8000** (Caddy Proxy).
4.  **Dependencies**: `psutil` mandated in `Dockerfile.base` for memory awareness.

---

## 3. THE UNIFIED TOOLING STRATEGY
**Problem**: Tool fragmentation (Cline, Gemini, Copilot, OpenCode).
**Solution**: **The Unified Omega CLI**.
-   **Strategy**: Fork **OpenCode** (or similar lightweight CLI) to serve as the central hub.
-   **Integration**: Direct connection to the **Agent Bus** (Redis Streams) for cross-agent coordination.

---

## 4. AUTOMATED CURATION (GMC WORKER)
**Spec**: "Gnostic Memory Curator" (GMC).
-   **Role**: The "Cleaner" and "Librarian" of the stack.
-   **Function 1 (Hygiene)**: Strip backslash bloat (`re.sub(r'\\+', r'\', content)`) before writing.
-   **Function 2 (Indexing)**: Create a searchable registry of all chat sessions.
-   **Function 3 (Pruning)**: Archive stale data to `_archive/`.

---

## 5. RESEARCH & RESILIENCE
-   **Chaos Monkey**: Expand `tests/test_circuit_breaker_chaos.py` to randomly test service resilience in production.
-   **Panda Browser**: Develop a lightweight browser tool for autonomous agent research.
-   **Media MCP**: Implement `mpv` control for local media management.

---

## 6. HANDOVER TO OPUS 4.6 (ANTIGRAVITY)
**Objective**: Full architectural review and enhancement.
**Artifacts**:
1.  `artifacts/AMR_STRATEGY_ROADMAP.md` (The Execution Plan).
2.  `artifacts/SYSTEM_INFRASTRUCTURE_CONTEXT.md` (The State).
3.  `memory_bank/strategies/OMEGA_OMNIBUS_v1.md` (This Vision).

**Directives**:
-   **Validate**: The "Seeded" approach.
-   **Refactor**: Begin the "Unified CLI" migration.
-   **Optimize**: Implement the "Turn-Based Queue."

---
# FILE 2: AMR_STRATEGY_ROADMAP.md
# 🦅 OMEGA OMNIBUS: AUTOMATED MARATHON RUN (AMR) STRATEGY & ROADMAP
**Target**: Antigravity (Opus 4.6) | **Status**: SEEDED (Ready for Execution)
**Date**: March 18, 2026
**Version**: v1.0 (The Gnostic Seed)

---

## 1. THE PRIME DIRECTIVE: "GNOSTIC SYNTHESIS"
**Goal**: Transition from "Xoe-NovAi Foundation" to "Omega Stack" (v4.6).
**Core Philosophy**:
-   **Gnostic Compression (SCC)**: "Seeded Cognitive Compression." We do not "remember" everything; we "seed" high-density concepts that unfold into full context when triggered.
-   **Phronetic Hierarchy**:
    -   **Logos** (Reasoning/Strategy) → **Opus/Gemini**
    -   **Praxis** (Action/Execution) → **Haiku/Flash** (formerly "Krikri")
    -   **Archon** (Orchestration) → **Gemini CLI/Manager**

---

## 2. INFRASTRUCTURE HARDENING (The 12GB Mandate)
**Constraint**: 12GB Physical RAM + 8GB zRAM (Dual-Tier lz4/zstd).
**Strategy**:
1.  **zRAM Hardening**: Enforce persistent 8GB swap.
2.  **Vulkan Inference**: Deploy `llama-cpp-python` with Vulkan support for AMD iGPU (Vega 8) acceleration (2x speedup).
3.  **Turn-Based Queue**: Implement a resource-gated queue system to keep RAM <6.5GB during concurrent operations.
4.  **Service Isolation**:
    -   **RAG API**: Moved to Port `8012` to resolve `8002` conflict with Prometheus.
    -   **Oikos**: Port `8006`.
    -   **Memory Bank**: Port `8005`.
    -   **Gateway**: Caddy proxies all via Port `8000`.

---

## 3. THE UNIFIED OMEGA CLI
**Problem**: Fragmentation (Cline, Gemini, Copilot, OpenCode).
**Solution**: **The Unified Omega CLI**.
-   **Base**: Fork **OpenCode** (or similar lightweight CLI).
-   **Role**: Central Hub for all providers.
-   **Integration**: Direct hook into the **Agent Bus** (Redis Streams).

---

## 4. THE CHAT CRAWLER (GMC Worker)
**Spec**: "Gnostic Memory Curator" (GMC).
-   **Function**:
    1.  **Strip Backslashes**: `re.sub(r'\\+', r'\', content)` pre-write.
    2.  **Index**: Create a searchable registry of all chat sessions (`1747349798183.conversation.json`, etc.).
    3.  **Prune**: Move stale data to `_archive/`.

---

## 5. RESEARCH INITIATIVES
1.  **Chaos Monkey**: Expand `tests/test_circuit_breaker_chaos.py` to a full stack auditor.
2.  **Panda Browser**: Integrate lightweight browser for agent research.
3.  **Media MCP**: `mpv`-based local media control.

---

## 6. HANDOVER PROTOCOLS (To Opus 4.6)
**The Pack**:
1.  `artifacts/AMR_STRATEGY_ROADMAP.md` (This file).
2.  `artifacts/SYSTEM_INFRASTRUCTURE_CONTEXT.md` (Infrastructure State).
3.  `docs/CLI_ROLES_AND_INTEGRATIONS.md` (Role Definition).
4.  `memory_bank/strategies/OMEGA_OMNIBUS_v1.md` (Strategic Vision).

**Directives for Opus**:
-   **Review**: Validate the "Seeded" approach.
-   **Enhance**: Optimize the "Turn-Based Queue" logic.
-   **Execute**: Begin the "Unified CLI" refactor.

---
# FILE 3: CLI_ROLES_AND_INTEGRATIONS.md
# 🎭 CLI Roles & Integration Matrix

## 1. The Cast (Personas)
-   **Gemini CLI (Archon)**: The Orchestrator. Wide context, tool-rich, manages the session.
-   **Cline (Praxis)**: The Coder. Deep file access, precise edits, test runner.
-   **Copilot (Logos)**: The Advisor. Code explanation, rapid query, inline suggestion.
-   **OpenCode (Hub)**: The Target for Unified CLI.

## 2. Integration Matrix
| CLI | Role | Access Level | Ideal Task |
| :--- | :--- | :--- | :--- |
| Gemini | Orchestrator | System-Wide | Planning, Research, Multi-file Refactor |
| Cline | Engineer | File-System | Implementation, Debugging, Testing |
| Copilot | Consultant | Editor-Context | Q&A, snippets, inline docs |

---
# FILE 4: CLI_ROUTING_DECISION_FRAMEWORK.md
# 🚦 CLI Routing Decision Framework

## 1. Decision Logic
-   **IF** task is "Create a Plan" -> **Gemini** (Archon).
-   **IF** task is "Fix this Bug" -> **Cline** (Praxis).
-   **IF** task is "Explain this Code" -> **Copilot** (Logos).
-   **IF** task is "Research the Web" -> **Gemini** (with Tavily).

## 2. Handoff Protocol
1.  **Gemini** creates the Plan (`artifacts/plan.md`).
2.  **Gemini** creates the Context Pack (`artifacts/context.md`).
3.  User invokes **Cline** with: "Execute the plan in `artifacts/plan.md` using context `artifacts/context.md`."
