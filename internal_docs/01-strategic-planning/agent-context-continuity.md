# Internal Doc: Agent Context Continuity Design
## Phase 5 Discovery - Sovereign Multi-Agent Cloud

### 1. The Challenge
When a human user switches from Gemini CLI to Cline CLI, the "Shared Brain" state must persist. Currently, each CLI is an isolated process.

### 2. Hybrid Continuity Pattern
We will implement a **Hybrid Redis-File State Sync**.

#### A. Redis State (Fast/Volatile)
- **Key**: `xnai:context:active_session`
- **Data**: JSON object containing:
    - `current_task_id`
    - `active_agent_did`
    - `last_interaction_timestamp`
    - `resource_claims` (e.g., "Cline has claimed the GPU")

#### B. File State (Sovereign/Persistent)
- **Path**: `communication_hub/state/contexts/{session_id}.json`
- **Data**: Full message history and tool execution results.
- **Verification**: Files are signed using the **Sovereign Handshake** protocol (Ed25519) to prevent tampering between agent process handoffs.

### 3. Handover Protocol
1.  **Gemini** (Active) receives a request better suited for **Cline**.
2.  **Gemini** writes the current context to `contexts/{session_id}.json` and signs it.
3.  **Gemini** sets `xnai:context:pending_handover = cline_did` in Redis.
4.  **Cline** (Watcher) detects the handover, verifies the signature, and loads the context.
