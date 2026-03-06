# Error Handling Patterns for Multi-Agent Systems

> **Date**: 2026-02-23
> **Context**: JOB-W2-008 - Edge Cases & Error Handling Research
> **Status**: COMPLETE

---

## 1. Core Patterns

### 1.1 Result Object Pattern

Instead of raising exceptions for expected failure states, return a structured Result object:

```python
from dataclasses import dataclass
from typing import Generic, TypeVar, Optional
from enum import Enum

T = TypeVar('T')

class ResultStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"

@dataclass
class Result(Generic[T]):
    """A result object that encapsulates success or failure."""
    status: ResultStatus
    value: Optional[T] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    
    def is_success(self) -> bool:
        return self.status == ResultStatus.SUCCESS
    
    def is_failure(self) -> bool:
        return self.status == ResultStatus.FAILURE
    
    def unwrap(self) -> T:
        """Get value or raise exception."""
        if self.is_failure():
            raise ValueError(f"Result is failure: {self.error}")
        return self.value
```

**Usage**:
```python
async def check_access(agent_did: str, resource: str) -> Result[bool]:
    if not agent_did.startswith("did:"):
        return Result(
            status=ResultStatus.FAILURE,
            error="Invalid DID format",
            error_code="INVALID_DID"
        )
    
    # ... access check logic ...
    return Result(
        status=ResultStatus.SUCCESS,
        value=True
    )
```

### 1.2 Dead Letter Queue (DLQ) Pattern

For async tasks that fail repeatedly:

```python
class DLQManager:
    """Manages failed tasks for later inspection."""
    
    MAX_RETRIES = 3
    DLQ_STREAM = "xnai:dlq"
    
    async def handle_failure(
        self,
        task: Task,
        error: Exception,
        retry_count: int
    ) -> None:
        if retry_count >= self.MAX_RETRIES:
            await self.send_to_dlq(task, error)
        else:
            await self.schedule_retry(task, error, retry_count)
    
    async def send_to_dlq(self, task: Task, error: Exception) -> None:
        entry = {
            "task_id": task.id,
            "task_type": task.type,
            "payload": json.dumps(task.payload),
            "error": str(error),
            "failed_at": datetime.utcnow().isoformat(),
            "retry_count": task.retry_count
        }
        await self.redis.xadd(self.DLQ_STREAM, entry)
        logger.error(f"Task {task.id} sent to DLQ: {error}")
```

### 1.3 Default Deny Pattern

Security-sensitive operations should default to denial:

```python
async def check_permission(agent: Agent, action: Action) -> bool:
    """Check if agent has permission for action. Default: DENY."""
    
    # Explicit allow list
    if action in agent.permissions:
        return True
    
    # Check role-based permissions
    for role in agent.roles:
        if action in ROLE_PERMISSIONS.get(role, set()):
            return True
    
    # Default: DENY
    logger.warning(f"Access denied for {agent.did} to {action}")
    return False  # <-- Always default to False
```

### 1.4 Circuit Breaker Pattern

Protect external services from cascading failures:

```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(str, Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """Circuit breaker for external service calls."""
    
    FAILURE_THRESHOLD = 5
    RECOVERY_TIMEOUT = timedelta(seconds=30)
    
    def __init__(self):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure: Optional[datetime] = None
    
    async def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if self._should_attempt_recovery():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitOpenError("Circuit is open")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_recovery(self) -> bool:
        return (
            self.last_failure and
            datetime.utcnow() - self.last_failure > self.RECOVERY_TIMEOUT
        )
    
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure = datetime.utcnow()
        if self.failure_count >= self.FAILURE_THRESHOLD:
            self.state = CircuitState.OPEN
```

---

## 2. Error Classification

### 2.1 Error Categories

| Category | Examples | Handling |
|----------|----------|----------|
| **Transient** | Network timeout, rate limit | Retry with backoff |
| **Permanent** | Invalid input, not found | Return error, no retry |
| **Systemic** | Out of memory, disk full | Alert, graceful degradation |
| **Security** | Auth failure, access denied | Log, deny, audit |

### 2.2 Custom Exception Hierarchy

```python
class XNAiError(Exception):
    """Base exception for XNAi Foundation."""
    def __init__(self, message: str, code: str = None, details: dict = None):
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(message)

class TransientError(XNAiError):
    """Error that may resolve on retry."""
    pass

class PermanentError(XNAiError):
    """Error that will not resolve on retry."""
    pass

class SecurityError(XNAiError):
    """Security-related error."""
    def __init__(self, message: str, agent_did: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.agent_did = agent_did

class AccessDeniedError(SecurityError):
    """Access was denied to a resource."""
    pass

class AuthenticationError(SecurityError):
    """Authentication failed."""
    pass
```

---

## 3. Observability

### 3.1 Structured Logging

```python
import structlog

logger = structlog.get_logger()

async def process_task(task: Task):
    log = logger.bind(
        task_id=task.id,
        task_type=task.type,
        agent_did=task.agent_did,
        trace_id=task.trace_id
    )
    
    try:
        result = await execute_task(task)
        log.info("task_completed", result=result)
    except TransientError as e:
        log.warning("task_transient_error", error=str(e), code=e.code)
        await retry_task(task)
    except PermanentError as e:
        log.error("task_permanent_error", error=str(e), code=e.code)
        await send_to_dlq(task, e)
    except Exception as e:
        log.exception("task_unexpected_error", error=str(e))
        raise
```

### 3.2 Metrics

```python
from prometheus_client import Counter, Histogram

task_total = Counter(
    'xnai_task_total',
    'Total tasks processed',
    ['task_type', 'status']
)

task_duration = Histogram(
    'xnai_task_duration_seconds',
    'Task processing duration',
    ['task_type']
)

async def process_task(task: Task):
    with task_duration.labels(task_type=task.type).time():
        try:
            result = await execute_task(task)
            task_total.labels(task_type=task.type, status='success').inc()
            return result
        except Exception as e:
            task_total.labels(task_type=task.type, status='error').inc()
            raise
```

---

## 4. Timeout Handling

### 4.1 AnyIO Timeouts

```python
import anyio

DEFAULT_TIMEOUT = 30.0

async def call_with_timeout(
    func,
    *args,
    timeout: float = DEFAULT_TIMEOUT,
    **kwargs
):
    """Call async function with timeout."""
    try:
        async with anyio.fail_after(timeout):
            return await func(*args, **kwargs)
    except TimeoutError:
        raise TransientError(
            f"Operation timed out after {timeout}s",
            code="TIMEOUT"
        )
```

### 4.2 Cascading Timeouts

```python
async def multi_service_call():
    """Call multiple services with appropriate timeouts."""
    async with anyio.create_task_group() as tg:
        # Fast service - short timeout
        tg.start_soon(call_with_timeout, fast_service, timeout=5.0)
        
        # Slow service - longer timeout
        tg.start_soon(call_with_timeout, slow_service, timeout=60.0)
```

---

## 5. Graceful Degradation

### 5.1 Fallback Patterns

```python
async def get_knowledge(query: str) -> Result:
    """Get knowledge with fallback to cache."""
    try:
        # Try primary source
        return await qdrant_search(query)
    except ConnectionError:
        # Fallback to cache
        logger.warning("Qdrant unavailable, using cache")
        return await cache_search(query)
    except Exception as e:
        # Final fallback
        logger.error(f"Knowledge retrieval failed: {e}")
        return Result(
            status=ResultStatus.FAILURE,
            error="Knowledge service unavailable",
            error_code="SERVICE_UNAVAILABLE"
        )
```

### 5.2 Feature Flags

```python
class FeatureFlags:
    """Feature flags for graceful degradation."""
    
    ENABLE_QDRANT = True
    ENABLE_CACHE = True
    MAX_RESULTS = 100
    
    @classmethod
    def is_enabled(cls, feature: str) -> bool:
        return getattr(cls, f"ENABLE_{feature.upper()}", False)

async def search(query: str):
    if FeatureFlags.is_enabled("QDRANT"):
        return await qdrant_search(query)
    elif FeatureFlags.is_enabled("CACHE"):
        return await cache_search(query)
    else:
        raise ServiceUnavailableError("Search not available")
```

---

## 6. Testing Error Handling

### 6.1 Error Injection

```python
import pytest

class TestErrorHandling:
    """Test error handling patterns."""
    
    @pytest.fixture
    def failing_qdrant(self, monkeypatch):
        """Fixture that makes Qdrant fail."""
        async def failing_search(*args, **kwargs):
            raise ConnectionError("Qdrant unavailable")
        monkeypatch.setattr("qdrant_search", failing_search)
    
    @pytest.mark.asyncio
    async def test_fallback_on_connection_error(self, failing_qdrant):
        """Test that cache fallback works when Qdrant fails."""
        result = await get_knowledge("test query")
        assert result.is_success()
        assert result.source == "cache"
    
    @pytest.mark.asyncio
    async def test_timeout_propagates(self):
        """Test that timeouts are properly raised."""
        async def slow_function():
            await anyio.sleep(10)
        
        with pytest.raises(TransientError) as exc:
            await call_with_timeout(slow_function, timeout=0.1)
        assert exc.value.code == "TIMEOUT"
```

---

**Related Files**:
- `app/XNAi_rag_app/core/redis_streams.py` - DLQ implementation
- `app/XNAi_rag_app/core/security/knowledge_access.py` - Access control patterns
- `docs/03-reference/ERROR-BEST-PRACTICES.md` - Best practices summary
