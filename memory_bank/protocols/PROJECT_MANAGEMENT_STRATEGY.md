# 🛡️ Project Management Strategy: The Sentinel & The Ledger

**Status**: Draft | **Phase**: 3.0 | **Author**: Gemini General

## 1. The Sentinel (Local Inference Guardian)
To relieve the "Gemini General" from low-level monitoring, we will deploy a sovereign, low-resource Sentinel.

### 1.1. Architecture
*   **Language**: Rust (or lightweight Python `asyncio`).
*   **Interface**: Connects to the **Agent Bus** (Redis Streams).
*   **Role**: Passive Monitor & Active Alerter.
*   **Resource Budget**: <50MB RAM, <1% CPU.

### 1.2. Core Duties
1.  **Health Watch**: Polls `/health` endpoints of all MCPs and Containers every 30s.
2.  **Resource Guard**: Monitors `podman stats`. If RAM usage > 85%, broadcasts a `SystemAlert:ResourceCritical` event to the Bus.
    *   *Action*: Agents receiving this MUST pause non-essential inference.
3.  **Log Sentry**: Tails `syslog` for "OOM", "Segfault", or "Permission Denied" patterns and injects them as "Observation" events into the Memory Bank.

## 2. The Ledger (Vikunja Integration)
Vikunja is our "Source of Truth" for tasks. Integration must be seamless via MCP.

### 2.1. Deployment Strategy
*   **Wait Condition**: Deployed only when Free Storage > 20GB (to accommodate DB + Attachments).
*   **Alternative (Interim)**: Use `memory_bank/tasks/` as a flat-file Ledger, managed by the General.

### 2.2. The "Project Manager" MCP
A dedicated MCP Server (`vikunja-mcp`) that exposes high-level tools to agents:
*   `create_task(title, priority, context_id)`
*   `list_blocking_tasks()`
*   `mark_task_complete(id, proof_summary)`

### 2.3. Context Linking
Every Vikunja Task will have a custom field `xnai_context_id` linking it back to the Memory Bank.
*   **Flow**: Agent solves a bug -> Updates Memory -> Marks Vikunja Task Done -> Sentinel verifies -> Ledger updated.

## 3. Implementation Plan

### Phase 1: The "Hollow" Sentinel (Python Prototype)
*   **Goal**: Prove the Agent Bus alert concept.
*   **Tech**: Python script using `redis-py` and `psutil`.
*   **Deliverable**: `scripts/sentinel_prototype.py`.

### Phase 2: The Interim Ledger (Markdown)
*   **Goal**: Immediate task tracking without Vikunja overhead.
*   **Structure**: `memory_bank/tasks/active_sprint.md`.
*   **Automation**: General updates this file via `write_file`.

### Phase 3: The Rust Sentinel
*   **Goal**: Zero-cost monitoring.
*   **Tech**: Rust binary compiled against `musl` for portability.

## 4. Strengthening PM Capability
To immediately strengthen PM:
1.  **Daily Standup Protocol**: General starts every session by reading `active_sprint.md`.
2.  **Definition of Done (DoD)**: Enforced by the Memory Bank Schema. A task isn't "Done" until it has a linked Test Result in the Memory Bank.
