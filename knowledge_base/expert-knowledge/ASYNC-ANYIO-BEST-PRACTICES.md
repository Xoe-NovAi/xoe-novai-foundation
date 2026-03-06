---
title: AnyIO Best Practices & Patterns
type: reference
audience: developer
last_updated: 2026-02-20
source: research_session_2026-02-20
related: [AGENTS.md, techContext.md]
---

# AnyIO Best Practices for XNAi Foundation

## Why AnyIO Over asyncio

AnyIO provides safer cancellation semantics, cross-backend compatibility (asyncio + Trio), and structured concurrency patterns. Per AGENTS.md constraint, XNAi uses AnyIO TaskGroups instead of asyncio.gather.

## Critical Patterns

### 1. Entry Point Migration

```python
# OLD (asyncio)
import asyncio
if __name__ == "__main__":
    asyncio.run(main())

# NEW (AnyIO)
import anyio
if __name__ == "__main__":
    anyio.run(main)
```

**Note**: `anyio.run()` takes the function reference, not a call result.

### 2. Cancellation Handling

```python
# OLD (asyncio)
except asyncio.CancelledError:
    await cleanup()
    raise

# NEW (AnyIO) - Backend-agnostic
from anyio import get_cancelled_exc_class

except get_cancelled_exc_class():
    with anyio.CancelScope(shield=True):
        await cleanup()
    raise  # MUST re-raise!
```

**Critical**: Always re-raise cancellation exceptions. Failing to do so causes undefined behavior.

### 3. Sleep Operations

```python
# OLD
await asyncio.sleep(1.0)

# NEW
await anyio.sleep(1.0)
```

AnyIO sleep respects cancellation semantics properly.

### 4. TaskGroups vs create_task

```python
# OLD - Unmanaged task (DANGEROUS)
task = asyncio.create_task(background_worker())

# NEW - Structured concurrency
async with anyio.create_task_group() as tg:
    tg.start_soon(background_worker)
    # Guaranteed cleanup on exit
```

### 5. asyncio.gather → TaskGroup

```python
# OLD
results = await asyncio.gather(*tasks, return_exceptions=True)

# NEW
results = []
async def run_and_collect(coro):
    try:
        results.append(await coro)
    except Exception as e:
        results.append(e)

async with anyio.create_task_group() as tg:
    for task in tasks:
        tg.start_soon(run_and_collect, task)
```

### 6. Threading Operations

```python
# OLD
result = await asyncio.to_thread(blocking_func)

# NEW - With capacity limiting
from anyio import CapacityLimiter, to_thread

limiter = CapacityLimiter(10)  # Max 10 concurrent threads
result = await to_thread.run_sync(blocking_func, limiter=limiter)
```

## Anti-Patterns to Avoid

### ❌ Mixing asyncio and AnyIO Primitives

```python
# BAD - asyncio primitive doesn't respect AnyIO cancellation
await asyncio.sleep(10)  # Won't cancel properly
```

### ❌ Yielding Inside TaskGroup

```python
# BAD - Corrupts cancel scope stack
async def bad_generator():
    async with create_task_group() as tg:
        tg.start_soon(worker)
        yield  # Task group state corrupted
```

### ❌ Not Re-Raising Cancellation

```python
# BAD - Undefined behavior
except get_cancelled_exc_class():
    await cleanup()
    # Missing raise!
```

## Deferred Migrations

The following patterns remain in codebase for managed background services:

- `asyncio.create_task()` in service managers with explicit lifecycle control
- These require structural refactoring with TaskGroups + cancellation scopes

## Sources

1. AnyIO Official Documentation: https://anyio.readthedocs.io/
2. "Why you should use AnyIO APIs instead of asyncio"
3. Prefect Engineering Blog on AnyIO
4. Research session: 2026-02-20
