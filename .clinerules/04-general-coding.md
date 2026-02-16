
---
priority: medium
context: general
activation: always
last_updated: 2026-01-27
version: 1.0
---

# General Coding Standards

**Enhanced with Claude-Level Production Excellence (26 Learning Patterns)**

## CLAUDE-INSPIRED CODING EXCELLENCE FRAMEWORK

### =4 CLAUDE PERMANENT LEARNING: 26 Production Patterns

#### 1-3. Import Path Management (Environment-Based Resolution)
-  **DO**: Use environment variables for project root paths
-  **DO**: Implement package-relative imports with proper `__init__.py`
-  **DO**: Set PYTHONPATH in Docker/container environments
- L **DON'T**: Hardcode `sys.path.insert()` with relative depths like `parents[1]`
- L **DON'T**: Assume all files are at the same directory depth
- L **DON'T**: Use different import patterns across files in the same project

#### 4-8. Memory Management Excellence
-  **DO**: Use `deque(maxlen=N)` for bounded FIFO buffers
-  **DO**: Implement explicit `cleanup()` methods
-  **DO**: Add `__del__()` for resource cleanup guarantees
-  **DO**: Set maximum sizes on all caches and collections
-  **DO**: Profile memory with `tracemalloc` in tests
- L **DON'T**: Use unbounded `list`, `bytearray`, or `dict` for accumulation
- L **DON'T**: Assume Python's GC will clean up resources promptly
- L **DON'T**: Forget to clear buffers after processing

#### 9-13. Async State Management
-  **DO**: Use `asyncio.Lock()` for async-safe synchronization
-  **DO**: Implement dependency injection instead of globals
-  **DO**: Create resource pools for expensive initialization
-  **DO**: Use FastAPI `Depends()` for managed dependencies
- L **DON'T**: Use `threading.Lock()` in async functions (blocks event loop!)
- L **DON'T**: Mutate globals without synchronization
- L **DON'T**: Initialize expensive resources in endpoint handlers

#### 14-18. Testing Excellence Patterns
-  **DO**: Include memory profiling tests with `tracemalloc`
-  **DO**: Test concurrent access patterns for thread safety
-  **DO**: Use dependency injection for isolated unit testing
-  **DO**: Validate performance targets in automated test suites
- L **DON'T**: Skip memory leak detection in long-running services
- L **DON'T**: Test async code without concurrency validation
- L **DON'T**: Ignore resource pool behavior under load

#### 19-23. Architecture & Design Patterns
-  **DO**: Use factory methods for complex async initialization
-  **DO**: Implement context managers for guaranteed cleanup
-  **DO**: Add weakref finalizers as safety nets
-  **DO**: Follow protocol-based dependency injection
- L **DON'T**: Mix sync/async patterns without clear boundaries
- L **DON'T**: Skip resource lifecycle management in services

#### 24-26. Performance & Reliability Standards
-  **DO**: Set hard memory limits (<10MB per session)
-  **DO**: Implement overflow protection with graceful degradation
-  **DO**: Use structured logging with monitoring context
- L **DON'T**: Allow unbounded resource consumption
- L **DON'T**: Skip performance benchmarking in production code

## ORIGINAL CODING STANDARDS (Enhanced)

- **Clarity**: Meaningful file, function, and folder names, comments for complex logic (e.g., ethical guardrails, checksum verification). **CLAUDE ENHANCEMENT**: Include performance impact comments and memory usage estimates.
- **Async Concurrency**: Use **AnyIO TaskGroups** for all concurrent operations. 
  - **PROHIBITED**: `asyncio.gather()`, `asyncio.create_task()`, and `asyncio.wait()`. These patterns lead to orphan tasks and resource leaks.
  - **MANDATED**: Use `async with anyio.create_task_group() as tg:` for all spawning. Ensure proper cancellation propagation and exception handling within the group.
  - **Blocking I/O**: Use `await anyio.to_thread.run_sync()` for synchronous file/network operations to prevent event loop stalls.
- **Output**: Complete, copy-pasteable code blocks with verification steps (e.g., `ls -la` for permissions). **CLAUDE ENHANCEMENT**: Include memory profiling commands and performance validation.
- **Best Practices**: Follow official docs. Prioritize torch-free optimization, performance (<300ms latency), security, maintainability, accessibility (WCAG 2.2 AA compliance, ARIA attributes, semantic HTML, keyboard navigation). **CLAUDE ENHANCEMENT**: Add 2024-2025 research citations and production validation metrics.
- **Reversibility**: Atomic operations, backups, auditable logs. Include --rollback flags in scripts. **CLAUDE ENHANCEMENT**: Add memory state rollback and async operation cancellation.

## CLAUDE STANDARD CODE PATTERNS

### Memory-Safe Buffer Implementation
```python
# CLAUDE STANDARD: Bounded buffer with overflow protection
from collections import deque
import weakref

class MemorySafeBuffer:
    def __init__(self, max_items: int = 1000):
        self._buffer = deque(maxlen=max_items)  # Automatic eviction
        self._overflow_count = 0
        self._finalizer = weakref.finalize(self, self._emergency_cleanup, max_items)

    def add_item(self, item) -> bool:
        if len(self._buffer) >= self._buffer.maxlen:
            # Evict oldest 50% on overflow
            evict_count = self._buffer.maxlen // 2
            for _ in range(evict_count):
                self._buffer.popleft()
            self._overflow_count += 1
        self._buffer.append(item)
        return True

    def cleanup(self):
        self._buffer.clear()
        return len(self._buffer)
```

### Async-Safe Resource Pool
```python
# CLAUDE STANDARD: Async resource pooling
import asyncio
from contextlib import asynccontextmanager

class AsyncResourcePool:
    def __init__(self, pool_size: int = 5):
        self.pool_size = pool_size
        self._pool = asyncio.Queue(maxsize=pool_size)
        self._lock = asyncio.Lock()  # Never threading.Lock!

    async def initialize_pool(self):
        async with self._lock:
            for _ in range(self.pool_size):
                resource = await self._create_resource()
                await self._pool.put(resource)

    @asynccontextmanager
    async def acquire(self):
        resource = await self._pool.get()
        try:
            yield resource
        finally:
            await self._pool.put(resource)
```

### Dependency Injection Service
```python
# CLAUDE STANDARD: Protocol-based dependency injection
from typing import Protocol, runtime_checkable

@runtime_checkable
class DataProcessor(Protocol):
    async def process(self, data: dict) -> dict: ...

class ProcessingService:
    def __init__(self, processor: DataProcessor, buffer: MemorySafeBuffer, pool: AsyncResourcePool):
        self.processor = processor
        self.buffer = buffer
        self.pool = pool

    @classmethod
    async def create(cls) -> 'ProcessingService':
        processor = await DefaultDataProcessor.create()
        buffer = MemorySafeBuffer(max_items=1000)
        pool = AsyncResourcePool(pool_size=5)
        await pool.initialize_pool()
        return cls(processor, buffer, pool)
```

Focus on local-first, CPU/Vulkan-optimized, sovereign changes aligned with Ma'at ideals. **CLAUDE ENHANCEMENT**: Apply 26 production patterns to ensure memory safety, async correctness, and enterprise reliability. Avoid vague code; include examples and anti-patterns. Test iteratively with memory profiling; use expert mode for Claude-level validation.