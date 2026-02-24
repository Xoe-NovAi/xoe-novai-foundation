"""
VoiceEventBus — Central pub/sub bus for all voice events.

All speech output in VoiceOS goes through this bus.
Subscribers (TTSManager, VoiceOverBridge) listen for events and speak them
in priority order.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Callable, Awaitable
import structlog

logger = structlog.get_logger(__name__)


@dataclass(order=True)
class VoiceEvent:
    """
    A voice event to be spoken to the user.

    Priority determines speaking order:
      0 — Low: queued, plays when all higher-priority events are done
      1 — Normal: default for most responses
      2 — High: warnings, important status changes
      3 — Interrupt: immediately interrupts any current speech
    """
    priority: int
    event_type: str = field(compare=False)
    message: str = field(compare=False)
    ssml: str | None = field(default=None, compare=False)
    interrupt_current: bool = field(default=False, compare=False)

    def __post_init__(self) -> None:
        if not self.message:
            raise ValueError("VoiceEvent message must not be empty")
        if len(self.message) > 500:
            logger.warning(
                "voice_event_message_too_long",
                length=len(self.message),
                event_type=self.event_type,
            )
        # Negate priority for max-heap behavior in asyncio.PriorityQueue
        object.__setattr__(self, "priority", -self.priority)


class VoiceEventBus:
    """
    Async pub/sub bus for VoiceEvents.

    Modules emit events via `publish()`. Subscribers receive them in
    priority order via `subscribe()`.

    Usage:
        bus = VoiceEventBus()

        # Publisher (any module)
        await bus.publish(VoiceEvent(
            event_type="response_ready",
            message="Opening Terminal.",
            priority=1,
        ))

        # Subscriber (TTSManager, VoiceOverBridge)
        async for event in bus.subscribe():
            await tts.speak(event.message)
    """

    def __init__(self) -> None:
        self._queue: asyncio.PriorityQueue[VoiceEvent] = asyncio.PriorityQueue()
        self._subscribers: list[asyncio.Queue[VoiceEvent]] = []
        self._running = False

    async def publish(self, event: VoiceEvent) -> None:
        """Publish a VoiceEvent to all subscribers."""
        logger.debug(
            "voice_event_published",
            event_type=event.event_type,
            priority=-event.priority,  # un-negate for logging
            message_preview=event.message[:50],
        )
        await self._queue.put(event)

    async def publish_simple(
        self,
        message: str,
        event_type: str = "response",
        priority: int = 1,
    ) -> None:
        """Convenience method to publish a plain text event."""
        await self.publish(VoiceEvent(
            event_type=event_type,
            message=message,
            priority=priority,
        ))

    async def subscribe(self) -> asyncio.AsyncIterator[VoiceEvent]:
        """
        Async generator that yields VoiceEvents in priority order.

        This is a consuming subscriber — only one consumer should read
        from the main bus. Use fan_out() for multiple subscribers.
        """
        while True:
            event = await self._queue.get()
            self._queue.task_done()
            yield event

    def subscribe_queue(self) -> asyncio.Queue[VoiceEvent]:
        """
        Register a new subscriber queue (fan-out pattern).
        Returns a queue that receives copies of all events.
        """
        q: asyncio.Queue[VoiceEvent] = asyncio.Queue()
        self._subscribers.append(q)
        return q

    async def _fan_out_loop(self) -> None:
        """Background task that fans out events to all subscriber queues."""
        async for event in self.subscribe():
            for q in self._subscribers:
                await q.put(event)

    async def drain(self) -> None:
        """Wait until all queued events have been consumed."""
        await self._queue.join()


# Module-level singleton
_bus: VoiceEventBus | None = None


def get_bus() -> VoiceEventBus:
    """Get or create the global VoiceEventBus instance."""
    global _bus
    if _bus is None:
        _bus = VoiceEventBus()
    return _bus
