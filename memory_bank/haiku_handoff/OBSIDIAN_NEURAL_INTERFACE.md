# 🔮 OBSIDIAN NEURAL INTERFACE STRATEGY (The Crystal Brain)
**Status**: DRAFT | **Target**: Experimental Sandbox
**Role**: Visual Cortex & Associative Memory for Agents

---

## 1. The "Facet Sandbox" Experiment
**Objective**: Measure agent performance when using Obsidian as a primary RAG source vs. standard Vector Search.

### **The Protocol**
1.  **The Overseer**: Jem (Archon) presides.
2.  **The Subjects**: Facets 1-8 (Simulated or Parallel Threads).
3.  **The Task**: "Research X using only Graph Traversal" (following WikiLinks).
4.  **Metric**: "Epiphany Rate" (Useful insights found via serendipitous linking / Total links traversed).

### **Implementation**
*   **Interface**: `obsidian-rest-api` (Community Plugin) running on `localhost:27123`.
*   **Agent Tool**: `read_obsidian_note`, `follow_backlinks`, `graph_nearest_neighbors`.

---

## 2. The "Digital Garden" as Model Context
**Theory**: LLMs degrade when context is fragmented. Obsidian's "MOC" (Map of Content) structure provides pre-compacted context.
**Strategy**: Agents must prioritize reading `MOC` files before leaf nodes.

---

## 3. Future Integration
*   **Smart Canvas**: Agents draw Mermaid charts directly into Obsidian Canvas files.
*   **Daily Log Sync**: The `SESSION_LEDGER.md` is auto-appended to the User's "Daily Note".
