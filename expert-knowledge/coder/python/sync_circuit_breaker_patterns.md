# 🧠 Sync Circuit Breaker Patterns in Async Applications

## Context
When building highly async applications (like Chainlit or FastAPI), some legacy or third-party components might still require synchronous execution. Using an async circuit breaker in these contexts can lead to `AttributeError` or `RuntimeError: no running event loop`.

## The Challenge
Async circuit breakers (like `PersistentCircuitBreaker`) rely on `await` for Redis operations. If called from a synchronous function, they fail.

## The Solution: Proxy Pattern with Sync Fallback
Implemented in `circuit_breakers.py`, the `CircuitBreakerProxy` detects the calling context and routes to either `call` (async) or `call_sync` (sync).

### Implementation Pattern

```python
class CircuitBreakerProxy:
    def __init__(self, name: str):
        self.name = name

    def __call__(self, func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Normal async logic with await
            breaker = self._get_breaker()
            return await breaker.call(func, *args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            # Sync fallback logic
            breaker = self._get_breaker()
            return breaker.call_sync(func, *args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
```

### Sync Method Safety
The `call_sync` method must be non-blocking to avoid stalling the event loop if called from a thread, or it must be a "fail-safe" pass-through if the complexity of sync Redis operations is too high for the current context.

```python
def call_sync(self, func: Callable, *args, **kwargs):
    # Pass-through implementation to prevent crashes
    # Logic can be expanded with a sync Redis client if needed
    return func(*args, **kwargs)
```

## Impact
- **Stability**: Prevents `AttributeError: 'CircuitBreakerProxy' object has no attribute 'call_sync'`
- **Resilience**: Maintains a consistent interface across the entire stack regardless of function type.
- **Performance**: Zero overhead for sync pass-throughs.
