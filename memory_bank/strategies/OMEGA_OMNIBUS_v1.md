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

### **GitHub Strategy (Free-Tier Optimized)**
-   **Goal**: Optimize CI/CD for GitHub Free Tier (2,000 mins/month).
-   **Reference**: `docs/strategies/GITHUB_STRATEGY.md` (Version 2.0).
-   **Key Tactics**: Fail-Fast CI, Layered CI, Smart Caching, Selective Job Execution, Artifact Cleanup, Workflow Event Filtering.

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
