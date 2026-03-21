---
last_updated: 2026-02-14
status: active
persona_focus: Gemini
agent_impact: critical
related_phases: Phase-4.1
---

# CLI Orchestration & Audit Protocol

This protocol defines how Gemini CLI audits the work of other autonomous agents (Cline, Copilot).

## 1. The Audit Loop
Any implementation triggered by a non-Gemini agent must undergo a Gemini Audit before it is considered "Ground Truth."

1.  **Submission**: Agent (e.g., Cline) writes a `task_completion` message to `internal_docs/communication_hub/outbox/`.
2.  **Ingestion**: Gemini CLI reads the message and the diff of modified files.
3.  **Synthesis**: Gemini loads the original `spec.md` from `01-strategic-planning/`.
4.  **Verification**: Gemini runs `pytest` or `ruff` via `run_shell_command`.
5.  **Truth Scoring**: Gemini assigns a score (0-100) based on spec alignment.

## 2. Automated Monitoring
The `scripts/monitor-cli-implementations.sh` script provides real-time oversight of the orchestration:

```bash
# Start real-time monitoring of integration tests
./scripts/monitor-cli-implementations.sh --watch
```

This ensures that as Cline (Kimi) or Copilot (Haiku) generates code, Gemini (Flash 3) has an immediate "Tactical Snippet" to review against the Ground Truth.

## 3. Success Metrics
- **Zero Drift**: Implementation exactly matches the Spec.
- **Pass/Fail**: Automated tests must pass 100%.
- **Review Coverage**: 100% of new test files must have a log entry in `logs/tactical-reviews.log`.
- **Doc Sync**: All changed code must have matching doc updates in `internal_docs/`.
