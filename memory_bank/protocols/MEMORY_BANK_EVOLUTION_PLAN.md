# 🧠 Memory Bank Evolution Plan: The Sovereign Gnosis

**Status**: Draft | **Phase**: 3.0 | **Author**: Gemini General

## 1. Executive Summary
This document outlines the strategic evolution of the XNAi Memory Bank from a passive storage system to an active, sovereign intelligence layer ("Gnosis"). The goal is to enable **True Agent Autonomy**, **Evolutionary Personality**, and **Semantic Hive Mind** capabilities while strictly adhering to offline-first sovereignty.

## 2. Core Architectural Pillars

### 2.1. The "Living Soul" (Dynamic Personality)
Current agents are static "snapshots" initialized at startup. We will transition to "Living Souls."
*   **Mechanism**: The `expert_soul.md` will become a template. The actual System Prompt will be constructed dynamically by the Memory Bank MCP at session start, injecting:
    *   **Base Personality**: The static core (Maat/Ethics).
    *   **Evolutionary Vector**: Summarized "lessons learned" from previous sessions (stored in Qdrant).
    *   **Current State**: Active project context and priorities.
*   **Implementation**: A `construct_soul(agent_id)` method in the MCP that aggregates these layers.

### 2.2. Fractal Vector Memory (The "Subconscious")
To ensure each Facet develops a unique perspective, we will implement **Namespaced Vector Storage**.
*   **Structure**: Single Qdrant Collection (`xnai_hive_mind`) with strict payload namespacing.
    *   `payload.agent_id`: "codebase_investigator", "general", etc.
    *   `payload.context_type`: "decision", "observation", "code_pattern".
*   **Benefit**: Allows for efficient "Cross-Pollination" (General can query *all* namespaces) while maintaining "Ego Integrity" (Facets primarily query their own namespace).

### 2.3. Agent-to-Agent (A2A) Telepathy
Direct semantic bridging between agents without user intermediation.
*   **Protocol**: `query_agent_memory(target, query)` (Implemented).
*   **Enhancement**: Add "Broadcast" capability. An agent can "shout" a finding to the Bus, and the Memory Bank records it for all relevant agents to "hear" (index) asynchronously.

### 2.4. Hardened Schema Validation
Moving from "JSON Soup" to strict Type Safety.
*   **Tool**: Pydantic Models for all Memory Bank entries.
*   **Validation**: The MCP will reject any `update_context` call that does not conform to the `ContextSchema`. This prevents garbage data from corrupting the Gnosis.

## 3. Token Optimization Strategy

### 3.1. "Gist" Compression
We cannot dump raw logs into the context window.
*   **Technique**: Use a lightweight local LLM (e.g., `specialist/summarizer` via Ollama/Llama.cpp) to compress "Hot" context into "Warm" summaries before storage.
*   **MCP Logic**: On `update_context`, if size > Threshold, trigger async summarization.

### 3.2. Pagination & Filtering
*   **API Update**: `get_context` will support `keys=["recent_errors", "active_file"]` to retrieve *slices* of memory rather than the full blob.

## 4. Implementation Roadmap

| Phase | Milestone | Deliverable | Status |
| :--- | :--- | :--- | :--- |
| **3.1** | **Harden** | Pydantic Schema Validation in MCP | ✅ Complete |
| **3.2** | **Isolate** | Qdrant Namespacing per Facet | ⏳ Pending |
| **3.3** | **Evolve** | Dynamic `construct_soul` endpoint | 🔮 Planned |
| **3.4** | **Compress** | Async Summarization Worker | 🔮 Planned |

## 5. Knowledge Gaps & Research
- **Rust Sentinel**: Need to prototype the `agent-bus` client in Rust for zero-cost monitoring.
- **GraphRAG**: Investigate `Neo4j` or `NetworkX` integration for "Dependency Awareness" (Task A blocks Task B).
