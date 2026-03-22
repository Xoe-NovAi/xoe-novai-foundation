# 👁️ OMEGA VISION & CONTINUAL PROCESS STRATEGY (SESS-27 Dark Layer Recovery)
**Status**: RECOVERED | **Target**: Opus 4.6
**Role**: The "Subconscious" of the Stack

---

## 1. The Vision Strategy (The "Watcher" Sidecar)
**Goal**: Analyze local screen state without interrupting the interactive CLI.

### **The Protocol: "Drop-to-Analyze"**
1.  **Trigger**: User saves a screenshot to `memory_bank/inbox/vision_drop/`.
2.  **The Watcher (Daemon)**: A Python script (`scripts/watcher_vision.py`) monitors this folder via `watchdog`.
3.  **Analysis**: The script sends the image to **Gemini 1.5 Flash (API)** with a system prompt: *"Analyze this UI state for errors or context."*
4.  **Delivery**:
    *   **Text**: Saves analysis to `memory_bank/inbox/vision_analysis/{timestamp}.md`.
    *   **Notification**: Pushes a "New Vision Analysis" alert to the active CLI via Redis Stream (`xnai:agent_bus`).
5.  **Integration**: The next time you press Enter in the CLI, the `Agent Bus` tool pulls this analysis into context.

---

## 2. The Continual Processes (The "Janitor Corps")
These run in the background, managed by `docs/03-how-to-guides/maintenance/VAMPIRE-CONTROL.md`.

### **A. The Structure Auditor (The "Ma'at" Daemon)**
*   **Frequency**: Daily (04:00 AM).
*   **Task**: Scans `memory_bank/` for:
    *   Orphaned files (no backlinks).
    *   Broken links (404 targets).
    *   Schema violations (missing YAML front-matter).
*   **Output**: `memory_bank/reports/integrity_daily.md`.

### **B. The GMC Worker (Chat Crawler)**
*   **Frequency**: Real-time (Watcher) + Nightly (Pruner).
*   **Task**:
    *   **Sanitize**: Strip `` bloat.
    *   **Index**: Update `MASTER_DISCOVERY_INDEX.md` with new concepts/entities.
    *   **Graph**: Update the **TGG (Topological Gnosis Graph)** JSON file.

### **C. The Full Directory Mapper**
*   **Frequency**: Weekly.
*   **Task**: Generate a full `tree` of the Omega Stack (excluding `.git` and `__pycache__`) to `memory_bank/maps/filesystem_topology.md`.
*   **Purpose**: Allows LLMs to "see" the exact file structure without running expensive `find` commands.

---

## 3. Implementation Directive
**Opus 4.6** is tasked with writing the `scripts/watcher_vision.py` and updating `vampire_control.sh` to include these new daemons.


**Archon Signature**: `Jem-SESS27.7-Sovereign` 🔱
