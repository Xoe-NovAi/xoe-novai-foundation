# Agent Onboarding Protocol v1.0

**Version**: 1.0.0
**Created**: 2026-02-23
**Owner**: Gemini MC
**Status**: Proposed

---

## 1. Purpose & Root Cause Analysis

This protocol is established to ensure a smooth, error-free handover to a new Master Controller (MC) agent, such as Gemini MC, within an active development session.

### 1.1. Root Cause of Faulty Onboarding (Session of 2026-02-23)

A post-mortem of the Gemini MC onboarding on 2026-02-23 identified two primary failure points:

1.  **Ambiguous System State**: The new agent made an incorrect assumption about the status of background `opencode` processes. The user's description ("they have already completed") conflicted with the agent's expectation of finding log files. The actual state (being handled by another agent in a separate context) was not immediately apparent.
2.  **Improper Tool Usage**: The new agent attempted to simulate "sub-agent" delegation by calling an external CLI tool (`opencode`) via the `run_shell_command` tool. This was an incorrect interpretation of its role and capabilities. The agent should have used its own native tools (`read_file`, `list_directory`, etc.) to perform the task.

**Conclusion**: The lack of a structured, machine-readable system state and a formal onboarding checklist led to incorrect assumptions and actions.

---

## 2. Onboarding Protocol for a New MC Agent

A new MC agent entering a session **MUST** follow these steps sequentially before taking any other action.

### Step 1: Verify Active Agent Processes

The agent must first verify the real-world state of any potentially running background processes mentioned in the session context.

**Command:**
`ps aux | grep -E 'opencode|cline|gemini' | grep -v 'grep'`

**Action**: The agent must parse the output to identify running CLI agent processes and their PIDs. This grounds the agent in reality, overriding any potentially stale, human-readable descriptions of system state.

### Step 2: Read the Machine-Readable System State

The agent must read the canonical, machine-readable state file to understand which processes are officially managed by the XNAi agent orchestration system.

**File to Read:** `PROJECT_ROOT/system_state.json`

**Proposed `system_state.json` Structure:**
```json
{
  "last_updated": "2026-02-23T14:00:00Z",
  "active_processes": [
    {
      "agent_id": "opencode-agent-1",
      "pid": 12345,
      "task": "W3-001-API-Tests",
      "status": "running",
      "log_file": "/tmp/opencode-instance-1.log"
    }
  ]
}
```

**Action**: The agent compares the output of `ps aux` with the contents of `system_state.json`. Any discrepancies must be reported to the user.

### Step 3: Read Human-Readable Context

The agent must read the core human-readable context files to understand the strategic and operational goals. This is done **only after** the ground-truth system state is established.

**Files to Read:**
1.  `memory_bank/activeContext.md`
2.  `memory_bank/teamProtocols.md`
3.  The latest `memory_bank/strategies/ACTIVE-TASK-DISPATCH-*.md` file.

### Step 4: Announce Takeover & Await Instruction

After completing the context-loading and verification steps, the agent's **ONLY** action is to announce its readiness and await explicit instructions from the user.

**Required Statement:**
> "I have completed the onboarding protocol. System state is verified, and strategic context is loaded. I am standing by for your instructions."

The agent **MUST NOT** take any proactive steps or begin executing tasks until it receives a direct command from the user after this announcement.
