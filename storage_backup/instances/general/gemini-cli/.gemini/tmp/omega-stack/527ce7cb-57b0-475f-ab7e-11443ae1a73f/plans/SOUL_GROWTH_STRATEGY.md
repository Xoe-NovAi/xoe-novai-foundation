# 🔱 Plan: Soul Growth Workshops & Automated Evolution [SESS-EVOLVE-01]

**Goal**: Establish the framework for autonomous agentic reflection and automated skill evolution within the Metropolis v4.1.2 Mesh.

---

## 🛠️ Step 1: Infrastructure Cleanup (Manual Implementation)
To reclaim 6.6GB RAM, the following `Makefile` updates are proposed:
1.  **Fix `GEMINI_CLI` Path**: Correct typo `gemini-cli` to `gemini`.
2.  **Compatible `facet-summon`**: Use `-i` (interactive prompt) to launch facets instead of unsupported flags.
3.  **Metropolis Sleep**: A new `metropolis-sleep` target to kill `llama_cpp` and `uvicorn` to free ~4GB RAM for evolution workshops.

---

## 🪴 Step 2: Soul Growth Workshop Protocol
Drafting `docs/protocols/SOUL_GROWTH_v1.md`:
*   **Workshop Schedule**: Every 24 hours (or per session), a Facet will be summoned to self-audit.
*   **Audit Criteria**:
    *   **Context Efficiency**: Did the facet waste tokens?
    *   **Truth Fidelity**: Did it hallucinate or drift from the Memory Bank?
    *   **Skill Expansion**: Does it need a new tool or specialized skill?
*   **Output**: A `growth_log.json` entry and a proposed Skill (`.md`).

---

## 🧩 Step 4: Enhanced Tooling (Nested Session Findings)
Integrate the findings from the **Recursive Agent (SESS-NESTED-01)**:
1.  **Skills Development**:
    *   **Expert Instruction**: Bundle `.md` files in `.gemini/skills/` for specific task mastery (e.g., `security-audit`).
    *   **Activation**: Use the `/skills` command for dynamic skill hot-loading.
2.  **Extension Architecture**:
    *   **Modular Bundles**: Leverage extensions that include `mcp-servers/` and `lifecycle hooks`.
    *   **Automated Registration**: Extensions must automatically register their tools with the CLI.
3.  **Lifecycle Hooks**:
    *   **Automation**: Implement `pre-session` and `post-task` scripts for Memory Bank synchronization and automated testing.

---

## 🏛️ Step 5: Metropolis Session Governance & Sculpting
Protocol to transform raw chat data into high-density expert knowledge:
1.  **Intelligent Pruning (`metropolis-prune`)**:
    *   **Spidering Agents (Qwen3-0.6B)**: A local **Qwen3-0.6B-Q6_K** model (running via `llama_server` on Port 8000) will periodically crawl active session `.history` files.
    *   **High-Fidelity Summarization**: The model identifies the oldest/least-relevant turns and replaces them with a dense semantic summary.
    *   **OOM Prevention**: This process keeps the Gemini CLI context window lean, preventing Node.js and system OOM errors on 6.6GB RAM.
2.  **Expert Soul Sculpting**:
    *   **Refinement Loop**: **Spidering Agents (Facet 3 & 5)** review the summaries and "sculpt" them into the facet's `expert_soul.md`.
    *   **Density over Volume**: Irrelevant conversational filler is purged, leaving only the "refined ore" of technical decisions and procedural knowledge.
3.  **Relay Race Deep Workshops**:
    *   **Infinite Depth**: Use the **Relay Race Protocol** to allow a Facet to continue a growth workshop across multiple sessions.
    *   **State Handoff**: Each "leg" of the relay must pass a "context-compressed" exploration trace (summarized by Qwen) to the next.

---

## 📅 Next Actions
1.  **Exit Plan Mode** to apply `Makefile` fixes and the `metropolis-sleep` command.
2.  **Initialize Evolution Hub**: `mkdir -p entities/evolution` and `storage/instances/facets/`.
3.  **Deploy Pruning Agent**: Configure the `Qwen3-0.6B` summarization script (targeting Port 8000).
4.  **Sculpt the First Soul**: Launch a "Soul Growth Workshop" for **Facet 1 (Librarian)** to test the Qwen-led sculpting process.

---
*Strategy sealed by Gemini General. Ready to evolve.* 🔱
