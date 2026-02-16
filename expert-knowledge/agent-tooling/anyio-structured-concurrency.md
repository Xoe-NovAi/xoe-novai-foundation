# Expert Knowledge: AnyIO Structured Concurrency Patterns
## Xoe-NovAi Production Standard

### 1. Why AnyIO?
We use AnyIO to enforce **Structured Concurrency**. Unlike raw `asyncio`, AnyIO prevents:
- **Orphan Tasks**: Tasks that keep running after their parent has finished.
- **Resource Leaks**: Unclosed connections/files due to failed gathers.
- **Silent Failures**: Exceptions in background tasks that never bubble up.

### 2. The TaskGroup Pattern
```python
import anyio

async def parent_service():
    async with anyio.create_task_group() as tg:
        tg.start_soon(fetch_data_from_redis)
        tg.start_soon(process_llm_request)
        # If either fails, BOTH are cancelled.
```

### 3. Blocking I/O (Thread Offloading)
Never use `os.path.exists` or `open()` directly in an async loop.
```python
# CORRECT
await anyio.to_thread.run_sync(os.makedirs, directory_path)
```

### 4. Cancellation & Timeouts
```python
with anyio.move_on_after(10): # 10s timeout
    await service.heavy_task()
```

### 5. Integration with XNAi Circuit Breakers
Always wrap `tg.start_soon` calls in a circuit breaker decorator if they involve network calls.
