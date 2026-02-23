# Best Practices: Error Handling and Edge Cases

> **Date**: 2026-02-23
> **Context**: JOB-W2-008 - Edge Cases & Error Handling Research
> **Status**: INITIAL DRAFT

---

## 1. Core Error Handling Patterns

Robust error handling is critical for a multi-agent, distributed system like the XNAi Foundation. These patterns ensure consistency and observability across all specialized agents.

### 1.1 The Result Object Pattern
Instead of raising exceptions for common "failure" states (e.g., Access Denied, No Results Found), return a structured `Result` object.
- **Example**: `AccessResult` in `knowledge_access.py`.
- **Benefit**: Easier control flow in asynchronous pipelines; no need for nested `try/except` blocks.

### 1.2 The Dead Letter Queue (DLQ)
For background tasks processed via **Redis Streams**, do not retry indefinitely on failure.
- **Pattern**: 
  1. Attempt task with exponential backoff.
  2. If still failing, move the task to the `xnai:agent_bus:dlq` stream.
  3. Log the failure with full context for manual inspection.

### 1.3 The Default Deny Pattern
In any security or access control logic, the final state must always be `DENIED`.
- **Example**: `_evaluate_abac` in `knowledge_access.py` returns `False, "No matching policy found (default deny)"`.

---

## 2. Handling Critical Edge Cases

| Component | Edge Case | Mitigation Strategy |
|-----------|-----------|---------------------|
| **Sanitizer** | Extremely Large Payload | Check `len(content) > MAX_PAYLOAD_SIZE` before processing. |
| **IAM** | Unverified DID | Use `if not agent.verified: return None` in the validation layer. |
| **Qdrant** | Resource Collision | Use unique UUIDs for document IDs and clear collection naming. |
| **Agent Bus** | Duplicate Task IDs | Implement idempotency checks in the task processing logic. |

---

## 3. Developer Best Practices

1. **Structured Logging**: Always include the `audit_id` or `trace_id` in logs to correlate actions across multiple agents.
2. **Context Preservation**: When catching an exception to re-raise it, use `raise XNAiError(...) from e`.
3. **Fail Fast**: Validate all inputs (Pydantic, Regex) at the very beginning of a function.
4. **AnyIO Timeouts**: Wrap all network calls (Redis, Qdrant, LLM) in `anyio.fail_after(timeout)`.

---

## 4. Next Steps

1. **Testing**: Add unit tests in `tests/unit/` specifically for the edge cases identified in this document.
2. **Implementation**: Integrate the DLQ pattern into the `core/redis_streams.py` implementation.
3. **Documentation**: Update the [User FAQ](../03-reference/USER-FAQ.md) with common error codes and their meanings.
