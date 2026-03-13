# EKB Gem: Circuit Breaker Dependency Resolution (LlamaCpp)

## Issue
RAG API crashes at startup with `NameError: name 'LlamaCpp' is not defined` even though `llama-cpp-python` is installed.

## Root Cause
In complex FastAPI applications with lazy loading, dependencies imported within localized scopes or conditional blocks (like Pattern 5 Circuit Breakers) may not be available in the global namespace if the initialization path skips the primary import. In this specific case, the circuit breaker logic attempted to reference `LlamaCpp` as a class for type-checking or instantiation without an explicit import in the `main.py` scope.

## Circuit Breaker Library Choice: PyBreaker vs PyCircuitBreaker

**Recommendation**: Use **PyBreaker** for Xoe-NovAi implementation

**Rationale**:
- **Simplicity**: PyBreaker is lightweight and straightforward
- **Async Support**: Better async/await integration for FastAPI applications
- **Maintenance**: More actively maintained than PyCircuitBreaker
- **Performance**: Lower overhead for high-frequency AI service calls

**Implementation Pattern**:
```python
from pybreaker import CircuitBreaker

# Async-compatible circuit breaker
class AsyncCircuitBreaker:
    def __init__(self, name: str, failure_threshold: int = 3):
        self.breaker = CircuitBreaker(fail_max=failure_threshold)
        self.name = name
    
    async def call(self, func, *args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Circuit breaker handles the failure logic
            raise e
```

## Remediation
Ensure all dependencies used by circuit breakers or lazy loaders are explicitly imported at the top of the module or within the scope of the factory function.

```python
# app/XNAi_rag_app/main.py
try:
    from langchain_community.llms import LlamaCpp
except ImportError:
    LlamaCpp = None
```

## Prevention
1. **Startup Smoke Test**: Always run a local `uvicorn main:app --port 8000` test before building the container to catch NameErrors.
2. **Explicit Imports**: Avoid relying on transitive imports for core architectural components (LLMs, Vectorstores).