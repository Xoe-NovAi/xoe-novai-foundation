# 🐒 CHAOS AGENT SPECIFICATION (The Entropy Engine)
**Status**: DRAFT | **Target**: Opus 4.6 Implementation
**Role**: System Resilience Auditor

## 1. Overview
The **Chaos Agent** is a specialized background worker that intentionally introduces faults into the system to verify the resilience of the **Circuit Breakers** and **Self-Healing** mechanisms.

## 2. Directives (Rules of Engagement)
1.  **Never Kill State**: Never touch `xnai_postgres` or `xnai_qdrant` volumes.
2.  **Dev/Test Only**: Default to `dev` namespace. Require explicit override for `prod`.
3.  **Log Everything**: All actions must be logged to `logs/chaos_audit.jsonl`.

## 3. Capabilities (The Toolkit)

### `inject_latency(service: str, duration: int)`
-   **Effect**: Adds artificial delay to network packets (using `tc`).
-   **Goal**: Test Timeout Circuit Breakers.

### `kill_pod(service: str)`
-   **Effect**: `podman kill <service>`.
-   **Goal**: Test Restart Policies and Health Checks.

### `saturate_cpu(service: str, duration: int)`
-   **Effect**: Spikes CPU usage.
-   **Goal**: Test Resource Gating and "Turn-Based Queue" logic.

## 4. Implementation
-   **Script**: `scripts/chaos_monkey.py`.
-   **Schedule**: Controlled via **Oikos Mastermind** (not cron), triggered during "War Games" sessions.


**Archon Signature**: `Jem-SESS27.7-Sovereign` 🔱
