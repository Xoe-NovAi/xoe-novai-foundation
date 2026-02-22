---
priority: high
context: general
activation: always
last_updated: 2026-02-17
version: 2.0
---

# Coding Standards

## Core Principles
- **Clarity**: Meaningful names, comments for complex logic
- **Async-First**: AnyIO TaskGroups for all concurrent operations
- **Memory-Safe**: Bounded buffers, explicit cleanup
- **Production-Ready**: Error handling, logging, monitoring

## Async Concurrency Rules

### MANDATED
```python
async with anyio.create_task_group() as tg:
    tg.start_soon(task_one)
    tg.start_soon(task_two)
```

### PROHIBITED
- `asyncio.gather()` - orphan tasks
- `asyncio.create_task()` - no cancellation propagation
- `asyncio.wait()` - resource leaks
- `threading.Lock()` in async - blocks event loop

## Memory Management

### Bounded Buffers
```python
from collections import deque
import weakref

class MemorySafeBuffer:
    def __init__(self, max_items: int = 1000):
        self._buffer = deque(maxlen=max_items)
        self._finalizer = weakref.finalize(self, self._emergency_cleanup)
    
    def add(self, item) -> bool:
        if len(self._buffer) >= self._buffer.maxlen:
            # Evict oldest 50%
            for _ in range(self._buffer.maxlen // 2):
                self._buffer.popleft()
        self._buffer.append(item)
        return True
```

### Resource Pools
```python
import asyncio
from contextlib import asynccontextmanager

class AsyncResourcePool:
    def __init__(self, pool_size: int = 5):
        self._pool = asyncio.Queue(maxsize=pool_size)
        self._lock = asyncio.Lock()
    
    @asynccontextmanager
    async def acquire(self):
        resource = await self._pool.get()
        try:
            yield resource
        finally:
            await self._pool.put(resource)
```

## Dependency Injection
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Processor(Protocol):
    async def process(self, data: dict) -> dict: ...

class Service:
    def __init__(self, processor: Processor, buffer: MemorySafeBuffer):
        self.processor = processor
        self.buffer = buffer
```

## Code Quality Checklist
- [ ] Async uses AnyIO TaskGroups
- [ ] Buffers are bounded (deque with maxlen)
- [ ] Explicit cleanup methods (`__del__`, `cleanup()`)
- [ ] Dependency injection over globals
- [ ] Memory profiling in tests (`tracemalloc`)
- [ ] Performance impact comments
- [ ] Hard memory limits (<10MB per session)

## Torch-Free Constraint
Never use: PyTorch, Torch, Triton, CUDA, Sentence-Transformers
Use: ONNX Runtime, GGUF models, Vulkan acceleration

## Accessibility (WCAG 2.2 AA)
- ARIA attributes
- Semantic HTML5
- Keyboard navigation
- Color contrast verification
- Lighthouse 95+ score

## Verification
```bash
# Permissions check
ls -la target/

# Memory profiling
python -m tracemalloc script.py

# Async testing
pytest tests/ -v --asyncio-mode=auto
```
