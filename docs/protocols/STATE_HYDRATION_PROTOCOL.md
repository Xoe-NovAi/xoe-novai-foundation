# 🌊 Protocol: State Hydration (Metropolis v4.1.2)

**Status**: AUTHORITATIVE  
**Role**: Mandatory for all agents (Main Orchestrator & Sub-Agents)  
**Objective**: Ensure the Memory Bank remains a consistent "Single Source of Truth" during multi-step session transitions.

---

## 🏛️ 1. The Atomic Beat
When a session objective is met, or a major architectural change is applied, the agent MUST perform a **State Hydration** beat. This beat updates three core files simultaneously:

1.  **`memory_bank/activeContext.md`**: Current session status, next steps, and handoff points.
2.  **`memory_bank/progress.md`**: Phase status, milestone updates, and completed tasks.
3.  **`memory_bank/INDEX.md`**: Master status update and "Recent Additions" log.

---

## 🏗️ 2. The Hydration Workflow

### Step 1: Preparation
Identify the new **Coordination Key**.  
*Format*: `METROPOLIS-[STATE]-[YYYYMMDD]` (e.g., `METROPOLIS-STABLE-20260312`).

### Step 2: Atomic Update
Execute file writes to all three files in a single turn.

### Step 3: Verification
The agent MUST verify the update by searching for the new Coordination Key:
```bash
grep -r "METROPOLIS-STABLE-20260312" memory_bank/
```

### Step 4: Event Logging
Write a hydration event log to `memory_bank/recall/handovers/HYDRATION_[TIMESTAMP].md`.

---

## 📜 3. Mandatory Metadata Template
Every hydration event must include this YAML block at the top of `activeContext.md`:

```yaml
hydration:
  event_id: "HYD-xxxx"
  session_id: "SESS-xx"
  coordination_key: "METROPOLIS-xxxx"
  timestamp: "2026-03-12T00:00:00Z"
  status: "STABLE"
```

---
*Protocol Sealed by Gemini General 2. Compliance is non-negotiable. 🔱*
