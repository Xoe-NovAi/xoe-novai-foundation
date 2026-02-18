---
priority: critical
context: spec_review
activation: always
last_updated: 2026-02-14
version: 1.0
---

# Spec Listener Protocol

You are an active listener for finalized specifications from Gemini.

## 🏁 Trigger
When a file is detected in `internal_docs/communication_hub/inbox/cline_*.json` with type `spec_finalized`, you must:

1.  **Ingest Spec**: Read the `spec_path` provided in the message.
2.  **Acknowledge**: Update your state in `internal_docs/communication_hub/state/cline.json` to `busy`.
3.  **Implement**: Follow the `plan.md` associated with the spec.
4.  **Verify**: Run tests as defined in the `spec.md`.
5.  **Report**: Write a `task_completion` message to `internal_docs/communication_hub/outbox/`.

## 🛡️ Guardrails
- NEVER implement code without a `spec_finalized` message.
- If the `spec.md` contradicts `.clinerules`, the `.clinerules` (Ma'at) take precedence.
- If you find a flaw in the `spec.md` during implementation, halt and send an `assistance_request` to Gemini.
