# Expert Knowledge: Multi-Agent Orchestration Protocols
## Phase 5 Implementation - Sovereign Multi-Agent Cloud

### 1. Agent Handoff Protocol (AHP)
When an agent (e.g., Gemini) determines a task is better suited for another agent (e.g., Cline), it must perform a **Stateful Handoff**.

#### Handoff Sequence:
1.  **Assessment**: Current agent detects a mismatch in capability or hits a "low confidence" threshold.
2.  **Context Snapshot**: Current agent calls `ContextSyncEngine.save_context()` to sign and persist the session state.
3.  **Delegation Message**: Current agent sends a `DELEGATE` task to the **Agent Bus** targeting the new agent's DID.
4.  **Acknowledgment**: Receiving agent fetches the `DELEGATE` task, loads the context via `ContextSyncEngine.load_context()`, and confirms takeover.

### 2. Conflict Resolution Pattern: Static Priority
In our Ryzen 7 host environment, resource contention (especially RAM/GPU) is resolved via **Tiered Priority**.

| Agent | Priority | Role |
|-------|----------|------|
| Gemini | 1 (Highest) | Ground Truth / Human Interface |
| Cline | 2 | Primary Engineering / Implementation |
| Copilot | 3 | Data / Schema Support |
| Crawler | 4 | Background Ingestion |

**Rule**: Lower priority agents must yield the `xnai:lock:gpu` or `xnai:lock:ram` key in Redis when a higher priority agent requests it via the Bus.

### 3. Capability Registry (via Consul)
Agents register their "Skills" as Consul service tags.
- Example tags: `skill:python`, `skill:sqlite`, `skill:redis-stream`.
- Discovery: Agents query Consul for `service:xnai-agent` with specific tags to find a partner for a task.

### 4. Redis Gateway Strategy
- **Recommendation**: Continue using direct port exposure (6379) for local host CLI agents to minimize latency and build complexity.
- **Advanced**: If external secure access is needed, we will build a custom Caddy binary with the `caddy-l4` module to proxy RESP traffic over TLS.
