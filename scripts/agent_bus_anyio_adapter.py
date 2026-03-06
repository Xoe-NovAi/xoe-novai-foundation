"""
AnyIO adapter for the XNAi Agent Bus watchers (skeleton).

Provides an AnyIO-based watcher implementation to replace threaded watchers and a compatibility shim to run existing threaded handlers.
"""

from pathlib import Path
import anyio
import json


async def anyio_watcher(inbox_dir: str, process_message_cb, poll_interval: int = 5):
    inbox = Path(inbox_dir)
    inbox.mkdir(parents=True, exist_ok=True)
    while True:
        for msg in inbox.glob("*.json"):
            try:
                # process_message_cb may be async or sync; support both
                if anyio.is_async_callable(process_message_cb):
                    await process_message_cb(msg)
                else:
                    # run in thread
                    await anyio.to_thread.run_sync(process_message_cb, msg)
            except Exception:
                # swallow errors in watcher loop; handler should report back
                pass
        await anyio.sleep(poll_interval)


async def start_watchers(watch_map: dict, poll_interval: int = 5):
    """Start multiple watchers concurrently. watch_map: {inbox_dir: callback}"""
    async with anyio.create_task_group() as tg:
        for inbox, cb in watch_map.items():
            tg.start_soon(anyio_watcher, inbox, cb, poll_interval)
