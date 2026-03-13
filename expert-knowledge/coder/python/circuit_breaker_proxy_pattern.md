# EKB Gem: Circuit Breaker Proxy Pattern for Import-Time Decorators
**Category:** Coder / Python / Architecture
**Date:** 2026-01-26
**Issue:** `ImportError` or `NoneType` exceptions when decorators (like `@rag_api_breaker`) are imported before the underlying service (Redis, Registry) is initialized.

## Root Cause
- **Decorator Initialization:** Python decorators are evaluated at *import time*. If a decorator depends on a global variable (e.g., `circuit_breaker_registry`) that is only initialized at *runtime* (e.g., in a FastAPI lifespan), the decorator will be initialized as `None` if it's imported too early.
- **Circular Imports:** UI modules often import breakers, which in turn might need UI config, creating a deadlock or a sequence error.

## Remediation: The Proxy Object
Implement a `CircuitBreakerProxy` that acts as a stable, callable interface at import time but delegates to the actual registry at runtime.

```python
class CircuitBreakerProxy:
    def __init__(self, name: str):
        self.name = name

    def _get_breaker(self):
        # Dynamically fetch from the global registry
        if circuit_breaker_registry is None:
            return None
        return circuit_breaker_registry.breakers.get(self.name)

    def __call__(self, func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            breaker = self._get_breaker()
            if breaker is None:
                return await func(*args, **kwargs) # Pass-through if not ready
            return await breaker.call(func, *args, **kwargs)
            
        def sync_wrapper(*args, **kwargs):
            breaker = self._get_breaker()
            if breaker is None:
                return func(*args, **kwargs)
            return breaker.call_sync(func, *args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

# Define stable globals
## Implementation Requirement
For the Proxy pattern to support both sync and async functions, the underlying `PersistentCircuitBreaker` (or equivalent) MUST implement both `call` (async) and `call_sync` (sync) methods.

In v0.1.5, `call_sync` was added to `PersistentCircuitBreaker` to prevent `AttributeError: 'PersistentCircuitBreaker' object has no attribute 'call_sync'` when wrapping synchronous session management methods in `chainlit_app_voice.py`.

## Benefits
1. **Import Safety:** Decorators are always valid, callable objects from the moment the module is loaded.
2. **Late Binding:** The actual circuit breaker logic is only attached once the registry and Redis are ready.
3. **Graceful Degradation:** If the registry fails to initialize, the proxy simply passes through the calls to the original function.

## Prevention
- **Avoid Global State:** Minimize reliance on global instances that require runtime setup.
- **Proxy Patterns:** Use proxies or factory functions for any decorator that depends on external services (DB, Redis, API).
