# Research: Edge Cases & Error Handling Patterns

> **Date**: 2026-02-23
> **Author**: GEMINI-MC
> **Status**: INITIAL DRAFT
> **Context**: JOB-W2-008 - Edge Cases & Error Handling Research

---

## 1. Edge Cases in Core Services (W2-008-1/2)

### 1.1 `knowledge_access.py` (Identity & Access)
- **Edge Case: Partial Identity**: Agent DID exists in the database but `verified` flag is false.
  - *Risk*: Unauthorized access.
  - *Handling*: `_validate_agent` correctly returns `None`, resulting in `INVALID_IDENTITY`.
- **Edge Case: Wildcard Abuse**: Permission `*` or `all` granted to a service account.
  - *Risk*: Violation of least privilege.
  - *Handling*: `_check_service_permission` handles this, but requires audit logging.
- **Edge Case: Resource Name Collisions**: Multiple collections with similar names (e.g., `knowledge` and `knowledge_test`).
  - *Risk*: Misrouting of access checks.
  - *Handling*: Use exact string matching for resources in ABAC policies.

### 1.2 `sanitizer.py` (Content Security)
- **Edge Case: Large Payload DoS**: Extremely large input (10MB+) sent to the regex engine.
  - *Risk*: ReDoS (Regular Expression Denial of Service).
  - *Handling*: Implement a `max_length` check *before* calling `sanitize()`.
- **Edge Case: Overlapping Secrets**: Multiple patterns match the same string (e.g., a URL with credentials and an API key).
  - *Risk*: Incomplete redaction or corrupted output.
  - *Handling*: `reversed(matches)` approach in `sanitizer.py` handles this correctly by preserving positions.
- **Edge Case: Obfuscated Secrets**: Base64 or split-string secrets (e.g., `"sk-" + "ant-..."`).
  - *Risk*: Sanitization bypass.
  - *Handling*: Requires semantic (LLM-based) sanitization beyond regex.

---

## 2. Error Handling Patterns (W2-008-3/4)

### 2.1 Pattern: Result Data Classes
Using `AccessResult` and `SanitizationResult` allows for structured error communication without raising exceptions for expected failure modes (e.g., "Access Denied").

### 2.2 Pattern: Fail-Safe (Zero-Trust)
- **Default Deny**: `KnowledgeAccessControl` defaults to `AccessDecision.DENIED` if no matching policy is found.
- **Strict Validation**: Metadata is validated against Pydantic models (where applicable) to prevent injection.

### 2.3 Pattern: Circuit Breakers (AnyIO)
When calling external services (e.g., Redis, Qdrant), use a circuit breaker to prevent cascading failures.

### 2.4 Pattern: Dead Letter Queue (DLQ)
For asynchronous tasks (Redis streams), move failed tasks to a DLQ for manual inspection rather than retrying indefinitely.

---

## 3. Best Practices for Developers

1. **Avoid Generic Exceptions**: Use `ValueError`, `KeyError`, or custom `XNAiError` types.
2. **Atomic Operations**: Ensure shared state (Memory Bank) is updated using lock files.
3. **Log Contextually**: Include `agent_did`, `task_id`, and `audit_id` in all error logs.
4. **Graceful Degradation**: If a non-critical service (e.g., monitoring) is down, the core pipeline should continue.

---

## 4. Next Steps
- Update `docs/03-reference/ERROR-BEST-PRACTICES.md` with these patterns.
- Design unit tests for the identified edge cases in `tests/unit/`.
