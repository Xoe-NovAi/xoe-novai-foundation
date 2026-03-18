# 🧠 OMEGA MODEL STRATEGY PLAN (The Gnostic Brain)
**Status**: PROPOSED | **Target**: Omega Stack v4.6
**Role**: Holistic Intelligence Orchestration

---

## 1. Strategic Architecture: The Hybrid Mind
The Omega Stack utilizes a **Hybrid-Cognitive Architecture**, assigning specific models to the "Facets" of the Phronetic Hierarchy.

### **Tier 1: Logos (Strategy & Design)**
-   **The Architect**: **Claude 3.5 Sonnet** (Cloud).
    -   *Role*: System design, complex refactoring, "impossible" logic puzzles.
-   **The Context Sovereign**: **Gemini 1.5 Pro** (Cloud).
    -   *Role*: Massive context ingestion (2M tokens), log analysis.

### **Tier 2: Praxis (Execution & Action)**
-   **The Artisan**: **Qwen 2.5 Coder 32B** (Local).
    -   *Role*: Private, offline code generation. SOTA performance.
-   **The Watcher**: **Gemini 1.5 Flash** (Cloud).
    -   *Role*: Real-time visual monitoring, autonomous screenshot analysis.

### **Tier 3: Archon (Orchestration & Curation)**
-   **The Router**: **Gemini 1.5 Flash** (Cloud).
    -   *Role*: High-speed intent classification and triage.
-   **The Curator (GMC)**: **Gemini 1.5 Flash** or **Llama 3.1 8B**.
    -   *Role*: Chat log cleaning, indexing, and archiving.

---

## 2. The "Watcher" Implementation (Vision)
**Objective**: Detect and analyze errors in real-time.
**Model**: **Gemini 1.5 Flash** (chosen for sub-second latency + native multimodal).

### **Architecture:**
-   **Trigger**: Keyword (`/scan`) or Log Event (`ERROR`).
-   **Action**: `mss` capture -> Flash Analysis -> Redis Alert.
-   **Script**: `scripts/watcher_vision.py`.

---

## 3. The Unified Mind Model (Nomenclature)
**The Nous** (The Cosmic Mind).

| Component | Name | Concept | Function |
| :--- | :--- | :--- | :--- |
| **System** | **The Nous** | *Nous* | Unified Consciousness. |
| **Memory** | **The Mnemosyne** | *Mnemosyne* | Persistent Knowledge. |
| **Bus** | **The Syndesmos** | *Syndesmos* | Connective Tissue. |
| **Goal** | **Homonoia** | *Homonoia* | One-mindedness. |

---

## 4. Next Steps
1.  **Download Qwen**: `ollama pull qwen2.5-coder:32b`.
2.  **Configure Flash**: Update `google-generativeai` settings.
3.  **Prototype Watcher**: Create `scripts/watcher_vision.py`.
