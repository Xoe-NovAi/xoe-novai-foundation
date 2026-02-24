"""
LLMRouter — Route requests to the best available LLM provider.

Default mode: CLAUDE_ONLY (Anthropic API, same account as Claude Code CLI).
Configure with:  voiceos set-key <sk-ant-...>   (once, persists to ~/.voiceos/config)

Three modes:
  - CLAUDE_ONLY (default): Anthropic API. Auto-falls back to Ollama if rate-limited,
      auto-recovers to Claude after the rate-limit window resets.
  - HYBRID: Try Ollama first; fall back to Claude if Ollama fails or times out.
  - OLLAMA_ONLY: Local Ollama only. Fully offline, no API costs.

Rate-limit handling (CLAUDE_ONLY / HYBRID):
  - On HTTP 429, parses retry-after / anthropic-ratelimit-*-reset headers.
  - Automatically falls back to local Ollama for the duration.
  - Schedules silent recovery: switches back to Claude when the window resets.
  - Voice-announces fallback and recovery so you always know which AI is active.
"""

from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import AsyncIterator

import structlog

logger = structlog.get_logger(__name__)

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class LLMMode(Enum):
    OLLAMA_ONLY = "ollama_only"
    HYBRID = "hybrid"
    CLAUDE_ONLY = "claude_only"


class RequestType(Enum):
    CODE = "code"           # Write/debug/explain code
    QUERY = "query"         # General question, fast response needed
    NAVIGATION = "nav"      # Navigate apps, what should I click?
    SYSTEM = "system"       # System status, configuration
    ACCESSIBILITY = "a11y"  # Accessibility-specific guidance


@dataclass
class Message:
    """A single conversation message."""
    role: str   # "system", "user", "assistant"
    content: str


@dataclass
class RequestContext:
    """Context that guides LLM routing decisions."""
    request_type: RequestType = RequestType.QUERY
    latency_budget_ms: int = 5000    # Maximum acceptable response time
    max_tokens: int = 150            # Keep short for voice
    temperature: float = 0.7
    require_quality: bool = False    # True = use best model regardless of latency


@dataclass
class LLMResponse:
    """Response from an LLM provider."""
    content: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    finish_reason: str = "stop"

    @property
    def is_empty(self) -> bool:
        return not self.content.strip()


class LLMError(Exception):
    """Base LLM error."""
    def __init__(
        self,
        message: str,
        voice_message: str = "",
        recoverable: bool = True,
        rate_limited_until: float = 0.0,   # time.time() epoch; non-zero = rate limited
    ):
        super().__init__(message)
        self.voice_message = voice_message or "AI service unavailable."
        self.recoverable = recoverable
        self.rate_limited_until = rate_limited_until


def _format_duration(seconds: float) -> str:
    """Return a human-friendly duration string ('5 minutes', '1 hour 20 minutes')."""
    seconds = int(seconds)
    if seconds < 90:
        return f"{seconds} seconds"
    minutes = seconds // 60
    if minutes < 90:
        return f"{minutes} minutes"
    hours = minutes // 60
    rem_min = minutes % 60
    if rem_min == 0:
        return f"{hours} hour{'s' if hours != 1 else ''}"
    return f"{hours} hour{'s' if hours != 1 else ''} {rem_min} minutes"


class RateLimitState:
    """
    Tracks Anthropic API rate-limit windows.

    When a 429 is received, records the reset time from response headers.
    LLMRouter polls is_rate_limited() before each cloud call and falls back
    to Ollama automatically. A background task calls schedule_recovery() to
    restore Claude at the exact reset moment.
    """

    def __init__(self) -> None:
        self._limited_until: float = 0.0   # monotonic clock

    def set_limited(self, retry_after_sec: float) -> None:
        self._limited_until = time.monotonic() + retry_after_sec
        logger.warning(
            "anthropic_rate_limited",
            retry_after_sec=round(retry_after_sec),
            resets_at=datetime.now(timezone.utc).isoformat(),
        )

    def clear(self) -> None:
        self._limited_until = 0.0

    @property
    def is_limited(self) -> bool:
        return time.monotonic() < self._limited_until

    @property
    def seconds_remaining(self) -> float:
        return max(0.0, self._limited_until - time.monotonic())


def _parse_retry_after(exc: Exception) -> float:
    """
    Extract retry-after seconds from an Anthropic 429 exception.

    Checks (in order):
      1. exc.response.headers['retry-after']            (seconds)
      2. exc.response.headers['anthropic-ratelimit-requests-reset']  (ISO-8601 timestamp)
      3. exc.response.headers['anthropic-ratelimit-tokens-reset']    (ISO-8601 timestamp)
      4. Default: 3600 seconds (1 hour conservative fallback)
    """
    default_sec = 3600.0
    try:
        headers = exc.response.headers  # type: ignore[union-attr]
    except AttributeError:
        return default_sec

    # retry-after: integer seconds
    if ra := headers.get("retry-after"):
        try:
            return float(ra)
        except ValueError:
            pass

    # anthropic-ratelimit-*-reset: ISO-8601 UTC timestamp
    for header in ("anthropic-ratelimit-requests-reset", "anthropic-ratelimit-tokens-reset"):
        if ts := headers.get(header):
            try:
                reset_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                delta = (reset_dt - datetime.now(timezone.utc)).total_seconds()
                if delta > 0:
                    return delta
            except ValueError:
                pass

    return default_sec


class CircuitBreaker:
    """Per-provider circuit breaker (see stt_manager.py for full docs)."""

    def __init__(
        self,
        failure_threshold: int = 3,
        success_threshold: int = 2,
        timeout_sec: float = 60.0,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_sec = timeout_sec
        self._failures = 0
        self._successes = 0
        self._state = "closed"
        self._last_failure = 0.0

    def is_available(self) -> bool:
        if self._state == "open":
            if time.monotonic() - self._last_failure > self.timeout_sec:
                self._state = "half_open"
                self._successes = 0
                return True
            return False
        return True

    def record_success(self) -> None:
        self._failures = 0
        if self._state == "half_open":
            self._successes += 1
            if self._successes >= self.success_threshold:
                self._state = "closed"

    def record_failure(self) -> None:
        self._failures += 1
        self._successes = 0
        self._last_failure = time.monotonic()
        if self._failures >= self.failure_threshold:
            self._state = "open"


@dataclass
class OllamaConfig:
    """Ollama provider configuration."""
    base_url: str = "http://127.0.0.1:11434"
    default_model: str = "qwen2.5:32b"      # General chat (high quality, ~20GB — fits 64GB RAM)
    code_model: str = "qwen2.5-coder:7b"    # Code tasks (specialized, 4.7GB)
    fast_model: str = "phi4-mini"           # Ultra-fast queries (2.5GB)
    timeout_sec: float = 90.0               # 32B needs more time than 3B

    # Fallback order when preferred model unavailable:
    # code:    qwen2.5-coder:7b → starcoder2:3b
    # general: qwen2.5:32b → llama3.2:3b → phi4-mini
    # fast:    phi4-mini → llama3.2:3b

    @classmethod
    def from_env(cls) -> "OllamaConfig":
        return cls(
            base_url=os.getenv("VOICEOS_LLM_URL", "http://127.0.0.1:11434"),
            default_model=os.getenv("VOICEOS_OLLAMA_MODEL", "qwen2.5:32b"),
            code_model=os.getenv("VOICEOS_OLLAMA_CODE_MODEL", "qwen2.5-coder:7b"),
            fast_model=os.getenv("VOICEOS_OLLAMA_FAST_MODEL", "phi4-mini"),
        )


@dataclass
class AnthropicConfig:
    """Anthropic Claude provider configuration."""
    api_key: str = ""
    fast_model: str = "claude-haiku-4-5-20251001"   # Fast responses
    quality_model: str = "claude-opus-4-6"            # Best quality
    timeout_sec: float = 30.0

    @classmethod
    def from_env(cls) -> "AnthropicConfig":
        return cls(
            api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        )


VOICE_SYSTEM_PROMPT = """You are VoiceOS, a voice assistant for developers.
Keep responses brief and spoken-friendly:
- Maximum 2 sentences unless asked for detail
- No markdown, no bullet lists, no code blocks in your response
- Speak naturally as if in conversation
- For code changes: describe what you'll do in 1 sentence, then do it
- If uncertain, say so briefly"""

CODE_SYSTEM_PROMPT = """You are VoiceOS, an expert coding assistant.
Provide working, correct code. Keep explanations to 1-2 sentences.
After code: briefly state what it does."""


class OllamaProvider:
    """Ollama local LLM provider."""

    def __init__(self, config: OllamaConfig) -> None:
        self.config = config
        self.breaker = CircuitBreaker()

    def _select_model(self, request_type: RequestType) -> str:
        if request_type == RequestType.CODE:
            return self.config.code_model
        if request_type == RequestType.SYSTEM:
            return self.config.fast_model
        return self.config.default_model

    async def complete(
        self,
        messages: list[Message],
        context: RequestContext,
    ) -> LLMResponse:
        """Complete via Ollama API."""
        if not self.breaker.is_available():
            raise LLMError(
                "Ollama circuit breaker open",
                voice_message="Local AI is temporarily unavailable.",
            )
        if not HTTPX_AVAILABLE:
            raise LLMError("httpx not installed", recoverable=False)

        model = self._select_model(context.request_type)
        ollama_messages = [{"role": m.role, "content": m.content} for m in messages]
        start = time.monotonic()

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_sec) as client:
                response = await client.post(
                    f"{self.config.base_url}/api/chat",
                    json={
                        "model": model,
                        "messages": ollama_messages,
                        "stream": False,
                        "options": {
                            "temperature": context.temperature,
                            "num_predict": context.max_tokens,
                        },
                    },
                )
                response.raise_for_status()
                data = response.json()

        except httpx.TimeoutException as e:
            self.breaker.record_failure()
            raise LLMError(
                f"Ollama timeout after {self.config.timeout_sec}s",
                voice_message="Local AI took too long. Trying cloud.",
            ) from e
        except (httpx.ConnectError, httpx.HTTPStatusError) as e:
            self.breaker.record_failure()
            raise LLMError(
                f"Ollama unavailable: {e}",
                voice_message="Local AI is not running.",
            ) from e

        latency_ms = (time.monotonic() - start) * 1000
        self.breaker.record_success()

        content = data.get("message", {}).get("content", "")
        logger.info(
            "ollama_response",
            model=model,
            latency_ms=round(latency_ms),
            tokens=data.get("eval_count", 0),
        )

        return LLMResponse(
            content=content,
            provider="ollama",
            model=model,
            output_tokens=data.get("eval_count", 0),
            latency_ms=latency_ms,
        )


class AnthropicProvider:
    """Anthropic Claude provider."""

    def __init__(self, config: AnthropicConfig) -> None:
        self.config = config
        self.breaker = CircuitBreaker()
        self.rate_limit = RateLimitState()
        self._client: "anthropic.Anthropic | None" = None

    def reload_api_key(self) -> bool:
        """
        Re-read ANTHROPIC_API_KEY from environment (picks up changes since startup).

        Returns True if a valid key is now present.
        """
        key = os.getenv("ANTHROPIC_API_KEY", "")
        if key and key != self.config.api_key:
            self.config.api_key = key
            self._client = None  # Force new client with updated key
            logger.info("anthropic_api_key_reloaded")
        return bool(self.config.api_key)

    @property
    def has_api_key(self) -> bool:
        """Return True if an API key is currently configured."""
        return bool(self.config.api_key)

    @property
    def is_rate_limited(self) -> bool:
        return self.rate_limit.is_limited

    def _get_client(self) -> "anthropic.Anthropic":
        if not ANTHROPIC_AVAILABLE:
            raise LLMError("anthropic package not installed", recoverable=False)
        if not self.config.api_key:
            raise LLMError(
                "ANTHROPIC_API_KEY not set",
                voice_message="Claude API key is not configured.",
                recoverable=False,
            )
        if self._client is None:
            self._client = anthropic.Anthropic(api_key=self.config.api_key)
        return self._client

    def _select_model(self, context: RequestContext) -> str:
        if context.require_quality or context.request_type == RequestType.CODE:
            return self.config.quality_model
        return self.config.fast_model

    async def complete(
        self,
        messages: list[Message],
        context: RequestContext,
    ) -> LLMResponse:
        """Complete via Anthropic API."""
        if not self.breaker.is_available():
            raise LLMError(
                "Anthropic circuit breaker open",
                voice_message="Claude is temporarily unavailable.",
            )

        client = self._get_client()
        model = self._select_model(context)

        # Separate system message from conversation
        system_parts = [m.content for m in messages if m.role == "system"]
        conversation = [
            {"role": m.role, "content": m.content}
            for m in messages if m.role != "system"
        ]

        system = "\n\n".join(system_parts) if system_parts else VOICE_SYSTEM_PROMPT
        start = time.monotonic()

        try:
            response = await asyncio.get_running_loop().run_in_executor(
                None,
                lambda: client.messages.create(
                    model=model,
                    max_tokens=context.max_tokens,
                    system=system,
                    messages=conversation,
                    temperature=context.temperature,
                ),
            )
        except Exception as e:
            # Detect rate limit (HTTP 429) — parse reset window from headers
            is_rate_limit = (
                ANTHROPIC_AVAILABLE
                and isinstance(e, anthropic.RateLimitError)
            ) or "429" in str(e) or "rate_limit" in str(e).lower()

            if is_rate_limit:
                retry_after = _parse_retry_after(e)
                self.rate_limit.set_limited(retry_after)
                duration_str = _format_duration(retry_after)
                raise LLMError(
                    f"Anthropic rate limited for {duration_str}",
                    voice_message=(
                        f"Claude rate limit reached. Switching to local AI for {duration_str}. "
                        "I'll switch back automatically."
                    ),
                    recoverable=True,
                    rate_limited_until=time.time() + retry_after,
                ) from e

            self.breaker.record_failure()
            raise LLMError(
                f"Anthropic API error: {e}",
                voice_message="Claude is unavailable right now.",
            ) from e

        latency_ms = (time.monotonic() - start) * 1000
        self.breaker.record_success()

        content = response.content[0].text
        logger.info(
            "anthropic_response",
            model=model,
            latency_ms=round(latency_ms),
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

        return LLMResponse(
            content=content,
            provider="anthropic",
            model=model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            latency_ms=latency_ms,
            finish_reason=response.stop_reason or "stop",
        )


class LLMRouter:
    """
    Routes LLM requests to the best available provider.

    Usage:
        config_ollama = OllamaConfig.from_env()
        config_anthropic = AnthropicConfig.from_env()
        router = LLMRouter(mode=LLMMode.HYBRID)

        response = await router.complete(
            messages=[
                Message(role="system", content=VOICE_SYSTEM_PROMPT),
                Message(role="user", content="How do I open Terminal?"),
            ],
            context=RequestContext(request_type=RequestType.NAVIGATION),
        )
        print(response.content)
    """

    def __init__(
        self,
        mode: LLMMode = LLMMode.CLAUDE_ONLY,   # Default: use Anthropic API
        ollama_config: OllamaConfig | None = None,
        anthropic_config: AnthropicConfig | None = None,
        on_rate_limit_fallback: "callable | None" = None,
        on_rate_limit_recovered: "callable | None" = None,
    ) -> None:
        self.mode = mode
        self._ollama = OllamaProvider(ollama_config or OllamaConfig.from_env())
        self._anthropic = AnthropicProvider(
            anthropic_config or AnthropicConfig.from_env()
        )
        # Callbacks for the orchestrator to announce fallback/recovery via TTS
        self._on_fallback = on_rate_limit_fallback
        self._on_recovered = on_rate_limit_recovered
        self._recovery_task: asyncio.Task | None = None

    def set_mode(self, mode: LLMMode) -> None:
        """Change routing mode at runtime."""
        self.mode = mode
        logger.info("llm_mode_changed", mode=mode.value)

    def reload_api_key(self) -> bool:
        """
        Re-read ANTHROPIC_API_KEY from environment (e.g. after voiceos set-key).

        Returns True if a valid key is now loaded.
        """
        return self._anthropic.reload_api_key()

    @property
    def cloud_available(self) -> bool:
        """True if API key configured, package installed, and not currently rate-limited."""
        return (
            ANTHROPIC_AVAILABLE
            and self._anthropic.has_api_key
            and not self._anthropic.is_rate_limited
        )

    @property
    def rate_limited(self) -> bool:
        """True if currently in a rate-limit window."""
        return self._anthropic.is_rate_limited

    @property
    def rate_limit_seconds_remaining(self) -> float:
        return self._anthropic.rate_limit.seconds_remaining

    def _schedule_recovery(self, retry_after_sec: float) -> None:
        """
        Schedule a background task to flip back to Claude after the rate-limit window.
        Cancels any existing recovery task first.
        """
        if self._recovery_task and not self._recovery_task.done():
            self._recovery_task.cancel()

        async def _recover() -> None:
            await asyncio.sleep(retry_after_sec + 2)  # +2s buffer
            if self._anthropic.is_rate_limited:
                self._anthropic.rate_limit.clear()
            logger.info("anthropic_rate_limit_recovered")
            if self._on_recovered:
                try:
                    await self._on_recovered()  # type: ignore[misc]
                except Exception:
                    pass

        try:
            loop = asyncio.get_running_loop()
            self._recovery_task = loop.create_task(_recover())
        except RuntimeError:
            pass  # No running loop (e.g. in tests)

    async def _try_cloud(
        self,
        messages: list[Message],
        context: RequestContext,
    ) -> LLMResponse | None:
        """
        Attempt a cloud call. Returns None (with side effects) if unavailable/rate-limited.
        Schedules auto-recovery if rate-limited.
        """
        if not self._anthropic.has_api_key:
            self._anthropic.reload_api_key()
        if not self._anthropic.has_api_key:
            logger.warning("no_anthropic_api_key", hint="voiceos set-key <sk-ant-...>")
            return None
        if self._anthropic.is_rate_limited:
            secs = self._anthropic.rate_limit.seconds_remaining
            logger.info("anthropic_still_rate_limited", seconds_remaining=round(secs))
            return None

        try:
            return await self._anthropic.complete(messages, context)
        except LLMError as e:
            if e.rate_limited_until:
                retry_after = e.rate_limited_until - time.time()
                self._schedule_recovery(retry_after)
            if not e.recoverable:
                raise
            return None

    async def complete(
        self,
        messages: list[Message],
        context: RequestContext | None = None,
    ) -> LLMResponse:
        """
        Complete a conversation using the best available provider.

        Mode behavior:
          CLAUDE_ONLY (default):
            - Uses Anthropic API for every request.
            - On 429 rate limit: announces via voice, falls back to Ollama,
              schedules silent auto-recovery (restores Claude at reset time).
            - On missing key: falls back to Ollama with a setup hint.
          HYBRID:
            - Tries Ollama first within latency budget, Claude as fallback.
            - Respects rate-limit windows.
          OLLAMA_ONLY:
            - Local only, no cloud calls ever.

        Raises:
            LLMError: If all available providers fail.
        """
        context = context or RequestContext()

        if self.mode == LLMMode.OLLAMA_ONLY:
            return await self._ollama.complete(messages, context)

        if self.mode == LLMMode.CLAUDE_ONLY:
            result = await self._try_cloud(messages, context)
            if result is not None:
                return result
            # Fallback to local — avoids silence when rate-limited or key missing
            try:
                return await self._ollama.complete(messages, context)
            except LLMError:
                pass
            raise LLMError(
                "CLAUDE_ONLY: cloud unavailable and Ollama not running",
                voice_message=(
                    "Both cloud and local AI are unavailable. "
                    "Check Ollama is running, or run voiceos set-key."
                ),
            )

        # HYBRID: Try Ollama first within latency budget, then Claude
        try:
            result = await asyncio.wait_for(
                self._ollama.complete(messages, context),
                timeout=context.latency_budget_ms / 1000,
            )
            if not result.is_empty:
                return result
        except (asyncio.TimeoutError, LLMError) as e:
            logger.warning("ollama_failed_in_hybrid", error=str(e))

        result = await self._try_cloud(messages, context)
        if result is not None:
            return result

        raise LLMError(
            "All LLM providers failed in HYBRID mode",
            voice_message=(
                "AI is unavailable. Check that Ollama is running, "
                "or run voiceos set-key to enable cloud fallback."
            ),
        )

    def build_voice_messages(
        self,
        user_input: str,
        history: list[Message] | None = None,
        request_type: RequestType = RequestType.QUERY,
    ) -> list[Message]:
        """
        Build a properly formatted message list for voice interaction.

        Args:
            user_input: The user's spoken text
            history: Previous conversation turns (optional)
            request_type: Type of request (affects system prompt)

        Returns:
            List of Message objects ready for complete()
        """
        system = CODE_SYSTEM_PROMPT if request_type == RequestType.CODE else VOICE_SYSTEM_PROMPT
        messages: list[Message] = [Message(role="system", content=system)]
        if history:
            messages.extend(history[-6:])  # Keep last 6 turns
        messages.append(Message(role="user", content=user_input))
        return messages
