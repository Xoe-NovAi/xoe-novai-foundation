# 🎯 CLI Routing Decision Framework (XNAi Standard)
**Date**: Wednesday, March 18, 2026
**Context**: SESS-26 Hardened | **Hardware**: Ryzen 7 5700U (8C/16T)

---

## 1. The Multi-CLI Taxonomy
To preserve the 16GB RAM budget and optimize for token ROI, tasks must be routed to the appropriate tool.

| Tool | Strength | Cost (Context/RAM) | Use Case |
| :--- | :--- | :--- | :--- |
| **Gemini CLI** | Strategic Planning, Codebase Investigation | High Context (1M+), Low Local RAM | Project discovery, architectural mapping, complex refactoring plans. |
| **OpenCode** | Targeted Implementation, Bug Fixing | Moderate RAM, Free Tier (Antigravity) | Writing feature code, fixing identified bugs, running local tests. |
| **Cline (IDE)** | Interactive UI/UX, Local File Edits | High Local RAM (VSCodium) | Immediate IDE-based edits, UI styling, real-time feedback loop. |
| **Copilot CLI** | Tactical Search, Rapid Reads | Low | Finding specific strings, quick documentation lookups. |
| **Antigravity IDE** | Deep Reasoning (Opus/Gemini 3) | Zero Local RAM (Cloud) | Solving "impossible" logic puzzles, high-level brainstorming. |

---

## 2. Decision Logic (The Routing Matrix)

### **A. Research & Discovery (The "Mind")**
- **Trigger**: "How does X work?" or "Map the dependencies of Y."
- **Primary**: `Gemini CLI /agent infrastructure`
- **Secondary**: `Copilot CLI` (for narrow, file-specific grep).

### **B. Strategic Planning (The "Will")**
- **Trigger**: "Plan the migration to Python 3.12" or "Design a new microservice."
- **Primary**: `Gemini CLI` (Facet-7/8 Speculative agents).
- **Secondary**: `Antigravity IDE` (Claude 3.7 Sonnet/Opus) for cross-validation.

### **C. Execution & Implementation (The "Body")**
- **Trigger**: "Implement the Redis Stream consumer" or "Fix the permission error."
- **Primary**: `OpenCode` (using Antigravity plugin for free models).
- **Secondary**: `Cline` if the task requires visual verification in the IDE.

---

## 3. Handoff Protocols (The "Bridge")

### **Rule 1: The Summary Mandate**
No tool may end a session without writing a `HANDOVER_*.md` to the `artifacts/` directory if the task is incomplete.

### **Rule 2: Context Passing**
When moving from **Gemini CLI** (Local) → **Antigravity IDE** (Cloud):
1. Run `/agent infrastructure "Extract context for Claude"`.
2. Paste the resulting `SYSTEM_INFRASTRUCTURE_CONTEXT.md` as the first message in the IDE.

### **Rule 3: Conflict Resolution**
If two tools provide conflicting advice:
1. Default to **Gemini CLI's** `codebase_investigator` output for file paths.
2. Default to **Antigravity IDE** (Opus 4.6) for high-level logic/math.

---

## 4. Degraded Mode & Failover Logic (Enterprise Resilience)
To ensure zero downtime, the system implements automated fallback strategies.

### **Failover Tier Matrix**
| Active Target | Primary Fallback | Status | Trigger |
| :--- | :--- | :--- | :--- |
| **Antigravity (Cloud)** | **Oikos (Local)** | Degraded | Quota Exceeded (429) |
| **OpenCode (CLI)** | **Gemini (CLI)** | Operational| Auth Plugin Failure |
| **Caddy Gateway** | **Direct Port (8002)**| Critical | Proxy Crash |

### **Automated Recovery (Rainbow Rotation)**
- **Trigger**: `healthcheck.py` returns `CRITICAL` for an external provider.
- **Action**: The `cli-service-bridge` rotates to the next available account in `config_cline-accounts_prod.yaml`.
- **Notification**: Broadcast to `xnai:alerts` Redis stream for user awareness.

---
**Registry Rigidity**: SESS-26.V1
