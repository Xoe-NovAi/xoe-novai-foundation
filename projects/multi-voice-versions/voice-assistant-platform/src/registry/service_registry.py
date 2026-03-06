"""
ServiceRegistry — Discover and track health of VoiceOS services.

Services:
  - stt: Speech-to-text (Whisper, port 2022)
  - tts: Text-to-speech (Kokoro, port 8880)
  - llm: Language model (Ollama, port 11434)

Discovery priority:
  1. Environment variables (VOICEOS_STT_URL, etc.)
  2. ~/.voiceos/config.yaml
  3. Hardcoded local defaults

Remote registration: add services by URL for distributed setups.
Health polling: background task checks all services every 30 seconds.
"""

from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Awaitable

import structlog

logger = structlog.get_logger(__name__)

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class ServiceStatus(Enum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass
class ServiceConfig:
    """Configuration and health state for one service."""
    name: str
    url: str
    health_endpoint: str = "/health"
    timeout_sec: float = 3.0
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_check: float = 0.0
    last_error: str = ""
    consecutive_failures: int = 0
    consecutive_successes: int = 0

    @property
    def is_healthy(self) -> bool:
        return self.status == ServiceStatus.HEALTHY

    @property
    def health_url(self) -> str:
        return self.url.rstrip("/") + self.health_endpoint


# Default local service configurations
DEFAULT_SERVICES: dict[str, ServiceConfig] = {
    "stt": ServiceConfig(
        name="stt",
        url=os.getenv("VOICEOS_STT_URL", "http://127.0.0.1:2022"),
        health_endpoint="/health",
    ),
    "tts": ServiceConfig(
        name="tts",
        url=os.getenv("VOICEOS_TTS_URL", "http://127.0.0.1:8880"),
        health_endpoint="/health",
    ),
    "llm": ServiceConfig(
        name="llm",
        url=os.getenv("VOICEOS_LLM_URL", "http://127.0.0.1:11434"),
        health_endpoint="/api/tags",  # Ollama uses this
    ),
}


class ServiceRegistry:
    """
    Registry of all VoiceOS external services.

    Maintains health state for each service. Provides health-aware
    URL resolution. Runs background health polling.

    Usage:
        registry = ServiceRegistry()
        await registry.start()

        stt_config = await registry.get_service("stt")
        if stt_config.is_healthy:
            await stt_client.transcribe(audio, url=stt_config.url)

        health = await registry.health_check_all()
        print(health)  # {"stt": True, "tts": True, "llm": False}
    """

    def __init__(
        self,
        poll_interval_sec: float = 30.0,
        on_status_change: Callable[[str, ServiceStatus], Awaitable[None]] | None = None,
    ) -> None:
        self._services: dict[str, ServiceConfig] = {
            k: ServiceConfig(**{**vars(v)}) for k, v in DEFAULT_SERVICES.items()
        }
        self.poll_interval_sec = poll_interval_sec
        self.on_status_change = on_status_change
        self._poll_task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        """Start background health polling and do initial check."""
        self._running = True
        # Initial check
        await self.health_check_all()
        # Start poller
        self._poll_task = asyncio.create_task(
            self._poll_loop(), name="ServiceRegistryPoller"
        )
        logger.info("service_registry_started", services=list(self._services.keys()))

    async def stop(self) -> None:
        """Stop background polling."""
        self._running = False
        if self._poll_task:
            self._poll_task.cancel()
            try:
                await self._poll_task
            except asyncio.CancelledError:
                pass

    def register_remote(self, name: str, url: str, health_endpoint: str = "/health") -> None:
        """
        Register a remote service by URL.

        Useful for distributed setups where services run on different machines.
        Example: registry.register_remote("stt", "http://192.168.1.50:2022")
        """
        self._services[name] = ServiceConfig(
            name=name,
            url=url,
            health_endpoint=health_endpoint,
        )
        logger.info("service_registered", name=name, url=url)

    async def get_service(self, name: str) -> ServiceConfig:
        """
        Get service config, with latest health status.

        Args:
            name: Service name ("stt", "tts", "llm")

        Returns:
            ServiceConfig with current status

        Raises:
            KeyError: If service name is not registered
        """
        if name not in self._services:
            raise KeyError(f"Unknown service: {name!r}. Registered: {list(self._services)}")
        return self._services[name]

    async def health_check_all(self) -> dict[str, bool]:
        """
        Check health of all registered services concurrently.

        Returns:
            Dict mapping service name to health status (True=healthy)
        """
        tasks = {
            name: asyncio.create_task(self._check_one(config))
            for name, config in self._services.items()
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        return {
            name: isinstance(result, bool) and result
            for name, result in zip(tasks.keys(), results)
        }

    async def _check_one(self, config: ServiceConfig) -> bool:
        """Check health of a single service."""
        if not HTTPX_AVAILABLE:
            return False

        old_status = config.status
        try:
            async with httpx.AsyncClient(timeout=config.timeout_sec) as client:
                response = await client.get(config.health_url)
                is_healthy = response.status_code < 500

        except Exception as e:
            is_healthy = False
            config.last_error = str(e)

        config.last_check = time.monotonic()

        if is_healthy:
            config.consecutive_failures = 0
            config.consecutive_successes += 1
            new_status = ServiceStatus.HEALTHY
        else:
            config.consecutive_successes = 0
            config.consecutive_failures += 1
            if config.consecutive_failures >= 3:
                new_status = ServiceStatus.UNAVAILABLE
            else:
                new_status = ServiceStatus.DEGRADED

        config.status = new_status

        if new_status != old_status:
            logger.info(
                "service_status_changed",
                service=config.name,
                old=old_status.value,
                new=new_status.value,
            )
            if self.on_status_change:
                await self.on_status_change(config.name, new_status)

        return is_healthy

    async def _poll_loop(self) -> None:
        """Background loop that checks all services periodically."""
        while self._running:
            await asyncio.sleep(self.poll_interval_sec)
            try:
                await self.health_check_all()
            except Exception as e:
                logger.error("health_poll_failed", error=str(e))

    def get_status_summary(self) -> dict[str, str]:
        """Return a human-readable status summary for all services."""
        return {
            name: config.status.value
            for name, config in self._services.items()
        }

    def all_healthy(self) -> bool:
        """Return True if all registered services are healthy."""
        return all(c.is_healthy for c in self._services.values())

    def get_voice_status_message(self) -> str:
        """Return a spoken status message for the user."""
        summary = self.get_status_summary()
        issues = [
            name for name, status in summary.items()
            if status != "healthy"
        ]
        if not issues:
            return "All services are running normally."
        service_names = ", ".join(issues)
        return f"Warning: {service_names} {'is' if len(issues) == 1 else 'are'} unavailable."
