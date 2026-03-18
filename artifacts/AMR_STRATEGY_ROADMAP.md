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

## 7. GEMINI CLI CONFIGURATION
**Goal**: Optimize Gemini CLI for persistence and security.
-   **Strategy**: [GEMINI_CLI_STRATEGY.md](../docs/strategies/GEMINI_CLI_STRATEGY.md)
-   **Action**:
    1.  redirect 'plans' from `/tmp` to `.gemini/plans`.
    2.  Review `.gemini/settings.json` for masking and agent limits.
