# RESEARCH-S2: The Xoe-NovAi Central Nervous System (CNS) Framework
**Version**: 1.0.0 | **Status**: ACTIVE RESEARCH | **Topic**: Advanced Multi-Agent Coordination & Memory

## Executive Summary
This report defines the transition from a passive filesystem-based "Agent Bus" to an active **Central Nervous System (CNS)**. The CNS integrates Vikunja PM, the local filesystem, and advanced context engineering to create a self-correcting, multi-agent ecosystem that resists "context drift" and maximizes agent autonomy.

---

## 🔬 Advanced Best Practices & Pitfalls

### 1. Context Engineering vs. Context Bloat
*   **Best Practice: Context Compaction**: Agents should summarize their work into "Compact State Fragments" before handoff.
*   **Pitfall: The "Telephone Game"**: Repeatedly passing full logs between agents leads to information decay and hallucination.
*   **Xoe-NovAi Solution**: Use `internal_docs/02-research-lab/RESEARCH-SESSIONS/` for deep logs, but pass only the `SESSION-WORK-SUMMARY.md` into the Agent Bus/Vikunja.

### 2. Concurrency & Locking in Sovereign Stacks
*   **Best Practice: Single-Writer Principle**: Only one agent should have "Write" access to a specific sub-directory in the `communication_hub/` at any time.
*   **Pitfall: Race Conditions**: Multiple agents writing to `activeContext.md` simultaneously.
*   **Xoe-NovAi Solution**: Implement a "Token" system in `internal_docs/communication_hub/state/` where an agent must "check out" a file before modifying it.

---

## 🏛️ Vikunja as the Central Nervous System (CNS)

Vikunja is no longer just a PM tool; it is the **API-First State Machine** of the foundation.

### 1. State Persistence via Task Metadata
*   **Current Objective**: The `Task Title` is the agent's primary directive.
*   **Detailed Context**: The `Task Description` stores the current "Knowledge Snapshot."
*   **Audit Trail**: `Task Comments` serve as the multi-agent dialogue log (The "Round Table").
*   **Artifacts**: `Task Attachments` link specific dabs of data (JSON state, diffs) to the task.

### 2. Enhancing Agent Abilities with Vikunja API
*   **Dynamic Re-prioritization**: Gemini CLI can use the Vikunja API to move tasks to the "High Priority" bucket based on audit findings, instantly redirecting Cline's focus.
*   **Context Injection**: Agents can "Fetch" only the tasks relevant to their role (e.g., Cline fetches only `agent:cline` labels), reducing context window noise.

---

## 🛠️ Actionable Enhancements

### 1. The "Agent Heartbeat" (Observed Strategy)
*   Agents will write a JSON heartbeat to `internal_docs/communication_hub/state/[agent].json`.
*   This file includes: `current_task_id`, `last_active_timestamp`, `health_status`, and `current_resource_usage`.

### 2. Vikunja-to-Bus Bridge
*   We will develop a simple script (or use `stack-cat`) to sync Vikunja tasks to the local `internal_docs/communication_hub/bus/pending/` directory.
*   This ensures that even if an agent is offline (sovereign), it can pick up tasks once it syncs with the local filesystem.

### 3. "Anti-Drift" Protocols
*   **Periodic Reconciliation**: Every 5 sessions, Gemini CLI will perform a "Full State Reconciliation," comparing the Memory Bank, Vikunja, and the Filesystem to identify and fix inconsistencies.

---

## 📈 Implementation Roadmap: CNS v1.0

1.  **Phase 1 (JSON Heartbeats)**: Implement the state JSON files for all active agents.
2.  **Phase 2 (Vikunja API Integration)**: Expand `stack-cat` to include `pm-sync` capabilities.
3.  **Phase 3 (Watcher Scripts)**: Create the automated listeners that trigger agents based on filesystem/Vikunja changes.

---

**Next Steps**: I will now create the "AI Agent State Schema" to standardize the JSON heartbeats.
