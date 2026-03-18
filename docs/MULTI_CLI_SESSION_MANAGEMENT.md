# 🔄 Multi-CLI Session Management & Persistence Strategy
**Date**: Wednesday, March 18, 2026
**Status**: DRAFT | **Context**: SESS-26 Hardened

---

## 1. The Challenge: Context Fragmentation
With 5+ CLIs (Gemini, OpenCode, Cline, Copilot, etc.) and the Antigravity IDE (Claude.ai) operating on the same codebase, context fragmentation is the primary risk. Each tool maintains its own local session history, leading to "split-brain" scenarios where one tool is unaware of another's changes.

---

## 2. The Solution: Gnostic State Hydration
We implement a **Unified Memory Bank** as the single source of truth (Alethia).

### **Session Store Architecture**
| Component | Location | Role |
| :--- | :--- | :--- |
| **Gnostic Root** | `memory_bank/` | Persistent "Ground Truth" (Architecture, Roadmap, Active Context). |
| **CLI Sessions** | `.gemini/sessions/`, `.opencode/history/` | Tool-specific execution logs and local state. |
| **Sync Layer** | `xnai-memory-mcp` | Real-time synchronization via Redis Streams. |
| **Bridge** | `xnai-agentbus` | Cross-CLI event notification. |

---

## 3. The Protocol: Sync-On-Handoff (SOH)
Whenever switching between tools (e.g., from Gemini CLI to Antigravity IDE), the following protocol MUST be observed:

### **Step 1: Summarize (The Producer)**
The active CLI must generate a session summary before concluding its task.
- **Tool**: Gemini CLI Facet-6 (The Chronicler).
- **Action**: `write_file` to `memory_bank/activeContext.md` or a session-specific markdown file in `artifacts/`.

### **Step 2: Hydrate (The Consumer)**
The new tool (e.g., Claude.ai in Antigravity IDE) must read the latest state.
- **Action**: Claude.ai should be prompted to "Read `memory_bank/activeContext.md` and the latest `artifacts/HANDOVER_*.md` before acting."

---

## 4. Persistence Layer Specification
- **Format**: Markdown (LLM-friendly) + JSON (Machine-readable).
- **Location**: `storage/instances/general/gemini-cli/.gemini/sessions/` (Symlinked to bulk storage).
- **Cleanup**: `sentinel-skill` triggers an archive of sessions older than 7 days to `_archive/session-handoffs/`.

---

## 5. Antigravity IDE Integration
Since the Antigravity IDE is cloud-hosted, it lacks direct filesystem access. 
- **Bridge Strategy**: Use the Gemini CLI to "Extract Context for Claude" (as done in this session).
- **Input**: `artifacts/SYSTEM_INFRASTRUCTURE_CONTEXT.md`
- **Output**: Paste the content into the Antigravity IDE at the start of every new Claude.ai session.

---

## 6. The Redis Sync Layer (Technical Schema)
To ensure all CLIs can parse the `xnai:memory_updates` stream uniformly.

### **JSON Message Schema**
```json
{
  "event_id": "uuid-v4",
  "source_tool": "gemini-cli",
  "target_context": "memory_bank/activeContext.md",
  "operation": "update",
  "sequence_id": 125,
  "payload_hash": "sha256-...",
  "timestamp": "2026-03-18T12:00:00Z"
}
```

### **Race Condition Protection (CAS)**
To prevent "split-brain" updates when multiple tools are active:
- **Compare-And-Swap (CAS)**: Every update must include the `sequence_id` of the last known state.
- **Verification**: If the `sequence_id` in Redis is higher than the tool's last seen ID, the tool MUST perform a "Merge & Re-Hydrate" before writing.
- **DLQ Handling**: Failed sync operations are moved to `xnai:dlq` for manual resolution or automated retry with backoff.

---
**Registry Rigidity Hash**: (Pending SESS-27 Validation)
