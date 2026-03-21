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

## 2. INFRASTRUCTURE HARDENING (16GB CONSTRAINT)
**Hardware Reality**: AMD Ryzen 7 5700U (Zen 2) | 16GB RAM | 8GB zRAM (lz4/zstd).
**Mandates**:
1.  **Turn-Based Queue**: Concurrent services must be gated to stay under 10GB RAM.
2.  **Vulkan Acceleration**: `llama-cpp-python` must use iGPU (Vega 8) for inference (2x speedup).
3.  **Port Isolation**:
    -   `RAG API`: **8012** (Resolved conflict with Prometheus on 8002).
    -   `Oikos`: **8006**.
    -   `Memory Bank`: **8005**.
    -   `Gateway`: **8000** (Caddy Proxy).
4.  **Dependencies**: `psutil` mandated in `Dockerfile.base` for memory awareness.

---

## 3. THE UNIFIED TOOLING STRATEGY (The 5-CLI Ecosystem)
**Problem**: Tool fragmentation.
**Solution**: **Symbiotic Orchestration**.
-   **Gemini CLI (Archon)**: The Orchestrator, Researcher, and "Glue".
-   **OpenCode (Workbench)**: The TUI Core, hosting the **Antigravity** plugin (OAuth unlocker).
-   **Cline (Surgeon)**: The VSCodium IDE extension for deep coding.
-   **Copilot (Assistant)**: The GitHub CLI wrapper for PRs and quick tasks.
-   **Antigravity (Unlocker)**: The OAuth plugin providing access to frontier models.

### **GitHub Strategy (Free-Tier Optimized)**
-   **Goal**: Optimize CI/CD for GitHub Free Tier (2,000 mins/month).
-   **Reference**: `docs/strategies/GITHUB_STRATEGY.md` (Version 2.0).

---

## 4. THE HAIKU PROTOCOL (v4.5 Integration)
**Source**: `artifacts/haiku_sync/`
**Mandate**: Align tactical execution with Haiku's research.
1.  **Session Management**: Adopt the **Hybrid Model** (Redis Hot + Disk Persistent).
2.  **Startup**: Enforce **Tiered Startup** (Core -> App -> Full) to respect 16GB RAM.
3.  **Handoff**: Use "Smart Handoff" protocol (Archon suggests, User confirms).
4.  **Knowledge Map**: The `XNA_OMEGA_SYSTEM_KNOWLEDGE_MAP_v1.1.md` is the shared Source of Truth.

---

## 5. AUTOMATED CURATION (GMC WORKER)
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
