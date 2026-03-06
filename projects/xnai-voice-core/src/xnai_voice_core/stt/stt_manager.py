"""
STTManager — Speech-to-text with fallback chain.

Backend priority:
  1. Local Whisper (port 2022) — default, private, fast
  2. OpenAI Whisper API — cloud fallback, higher accuracy
  3. macOS SpeechRecognizer (AVFoundation) — emergency fallback

All backends share the same async interface.
Circuit breaker prevents repeated calls to a failing backend.
"""

from __future__ import annotations

import asyncio
import io
import os
import struct
import time
from dataclasses import dataclass, field
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


@dataclass
class TranscriptResult:
    """Result from a transcription request."""
    text: str
    confidence: float = 1.0       # 0.0–1.0; 1.0 if backend doesn't report it
    language: str = "en"
    duration_ms: float = 0.0
    backend: str = "unknown"
    is_empty: bool = False         # True if audio was silence


class STTError(Exception):
    """Base error for STT failures."""
    def __init__(self, message: str, voice_message: str, recoverable: bool = True):
        super().__init__(message)
        self.voice_message = voice_message
        self.recoverable = recoverable


class STTConnectionError(STTError):
    pass


class STTTimeoutError(STTError):
    pass


import json
from pathlib import Path

CB_STATE_FILE = Path.home() / ".voiceos" / "memory" / "circuit_breaker.json"

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """
    Circuit breaker for external service calls with persistent state across restarts.
    """

    def __init__(
        self,
        name: str = "default",
        failure_threshold: int = 3,
        success_threshold: int = 2,
        timeout_sec: float = 30.0,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_sec = timeout_sec
        self.state = CircuitState.CLOSED
        self._failures = 0
        self._successes = 0
        self._last_failure_time = 0.0
        self._load_state()

    def _load_state(self) -> None:
        if not CB_STATE_FILE.exists():
            return
        try:
            data = json.loads(CB_STATE_FILE.read_text(encoding="utf-8"))
            if self.name in data:
                state_data = data[self.name]
                self._failures = state_data.get("failures", 0)
                self._successes = state_data.get("successes", 0)
                state_str = state_data.get("state", "closed")
                try:
                    self.state = CircuitState(state_str)
                except ValueError:
                    self.state = CircuitState.CLOSED
                self._last_failure_time = state_data.get("last_failure", 0.0)
        except Exception as e:
            logger.debug(f"Failed to load circuit breaker state: {e}")

    def _save_state(self) -> None:
        try:
            CB_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            data = {}
            if CB_STATE_FILE.exists():
                try:
                    data = json.loads(CB_STATE_FILE.read_text(encoding="utf-8"))
                except Exception:
                    pass
            data[self.name] = {
                "failures": self._failures,
                "successes": self._successes,
                "state": self.state.value,
                "last_failure": self._last_failure_time
            }
            CB_STATE_FILE.write_text(json.dumps(data), encoding="utf-8")
        except Exception as e:
            logger.debug(f"Failed to save circuit breaker state: {e}")

    def is_available(self) -> bool:
        if self.state == CircuitState.OPEN:
            if time.time() - self._last_failure_time > self.timeout_sec:
                self.state = CircuitState.HALF_OPEN
                self._successes = 0
                self._save_state()
                return True
            return False
        return True

    def record_success(self) -> None:
        self._failures = 0
        if self.state == CircuitState.HALF_OPEN:
            self._successes += 1
            if self._successes >= self.success_threshold:
                self.state = CircuitState.CLOSED
                logger.info("circuit_breaker_closed")
        self._save_state()

    def record_failure(self) -> None:
        self._failures += 1
        self._successes = 0
        self._last_failure_time = time.time()
        if self._failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(
                "circuit_breaker_opened",
                failures=self._failures,
            )
        self._save_state()


@dataclass
class STTConfig:
    """Configuration for the STTManager."""
    whisper_url: str = "http://127.0.0.1:2022"
    openai_api_key: str = ""
    language: str = "en"
    timeout_sec: float = 20.0   # large-v3 needs more time than base for longer utterances
    vocabulary_bias: list[str] = field(default_factory=lambda: [
        # Python / general dev
        "async", "await", "pytest", "def", "class", "import", "return",
        "function", "variable", "argument", "decorator", "iterator",
        # AI / project-specific
        "Claude", "Anthropic", "VoiceOS", "voiceos", "Ollama", "llama",
        "Whisper", "Kokoro", "qwen", "phi", "LLM", "MCP",
        # Infrastructure
        "AudioProcessor", "STTManager", "TTSManager", "LLMRouter",
        "LaunchAgent", "plist", "launchd", "homebrew", "uv", "pip",
        # Git / tools
        "git", "GitHub", "commit", "branch", "pull request", "merge",
        "pytest", "mypy", "ruff", "linter",
        # macOS
        "macOS", "Sonoma", "Sequoia", "Xcode", "AppleScript", "osascript",
    ])

    @classmethod
    def from_env(cls) -> "STTConfig":
        return cls(
            whisper_url=os.getenv("VOICEOS_STT_URL", "http://127.0.0.1:2022"),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            language=os.getenv("VOICEOS_STT_LANGUAGE", "en"),
            timeout_sec=float(os.getenv("VOICEOS_STT_TIMEOUT", "20.0")),
        )


def _pcm_to_wav(pcm_bytes: bytes, sample_rate: int = 16000) -> bytes:
    """Convert raw int16 PCM bytes to WAV format (in-memory)."""
    num_samples = len(pcm_bytes) // 2
    num_channels = 1
    bits_per_sample = 16
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = len(pcm_bytes)
    chunk_size = 36 + data_size

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", chunk_size, b"WAVE",
        b"fmt ", 16, 1, num_channels, sample_rate,
        byte_rate, block_align, bits_per_sample,
        b"data", data_size,
    )
    return header + pcm_bytes


class WhisperLocalBackend:
    """Whisper STT backend using faster-whisper natively via CTranslate2."""

    def __init__(self, config: STTConfig) -> None:
        self.config = config
        self.breaker = CircuitBreaker(name="stt_faster_whisper")
        
        try:
            from faster_whisper import WhisperModel
            model_dir = os.path.expanduser("~/.voiceos/models")
            os.makedirs(model_dir, exist_ok=True)
            self.model = WhisperModel(
                "distil-large-v3", 
                device="cpu", 
                compute_type="int8",
                download_root=model_dir
            )
            self._available = True
        except ImportError:
            logger.warning("faster-whisper not installed")
            self._available = False
            self.model = None
            
    def _do_transcribe(self, audio_data: np.ndarray) -> str:
        if not self.model:
            return ""
        segments, _ = self.model.transcribe(
            audio_data, 
            language=self.config.language,
            initial_prompt=" ".join(self.config.vocabulary_bias)
        )
        return "".join(s.text for s in segments).strip()

    async def transcribe(self, audio_pcm: bytes) -> TranscriptResult:
        """Transcribe PCM audio via local faster-whisper."""
        if not self._available or not self.model:
            raise STTConnectionError(
                "faster-whisper is not available",
                voice_message="Local speech recognition engine is not installed.",
            )
            
        if not self.breaker.is_available():
            raise STTConnectionError(
                "Whisper circuit breaker is open",
                voice_message="Local speech recognition is temporarily unavailable.",
            )

        start = time.monotonic()

        try:
            import numpy as np
            # Convert 16-bit PCM to float32 normalized
            audio_data = np.frombuffer(audio_pcm, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Run in executor to prevent blocking the async loop
            text = await asyncio.get_running_loop().run_in_executor(
                None, self._do_transcribe, audio_data
            )
            
        except Exception as e:
            self.breaker.record_failure()
            raise STTConnectionError(
                f"faster-whisper transcription failed: {e}",
                voice_message="Cannot process speech audio.",
            ) from e

        duration_ms = (time.monotonic() - start) * 1000
        self.breaker.record_success()

        logger.info(
            "whisper_transcription",
            text=text[:80],
            duration_ms=round(duration_ms),
        )

        return TranscriptResult(
            text=text,
            duration_ms=duration_ms,
            backend="faster_whisper_native",
            is_empty=len(text) == 0,
        )

    async def health_check(self) -> bool:
        """Return True if Whisper model is loaded."""
        return self._available and self.model is not None


class MacOSSpeechBackend:
    """
    Emergency fallback: macOS native Speech Recognition via AVFoundation.
    Requires PyObjC. If not available, silently skips.
    """

    def __init__(self) -> None:
        self._available: bool | None = None

    def _check_available(self) -> bool:
        if self._available is None:
            try:
                import Speech  # noqa: F401 — PyObjC
                self._available = True
            except ImportError:
                self._available = False
        return self._available

    async def transcribe(self, audio_pcm: bytes) -> TranscriptResult:
        """Transcribe using macOS Speech Recognition (blocking subprocess)."""
        if not self._check_available():
            raise STTConnectionError(
                "PyObjC Speech framework not available",
                voice_message="Native speech recognition not available.",
            )

        # Use macOS dictation via osascript as last resort
        result = await asyncio.get_running_loop().run_in_executor(
            None, self._run_macos_stt, audio_pcm
        )
        return result

    def _run_macos_stt(self, audio_pcm: bytes) -> TranscriptResult:
        """Run macOS STT synchronously in executor thread."""
        import tempfile, subprocess, os
        wav = _pcm_to_wav(audio_pcm)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(wav)
            tmp_path = f.name
        try:
            # Use Whisper CLI if available, otherwise fail gracefully
            result = subprocess.run(
                ["whisper", tmp_path, "--language", "en", "--output_format", "txt"],
                capture_output=True, text=True, timeout=30
            )
            text = result.stdout.strip()
            return TranscriptResult(
                text=text,
                backend="macos_speech",
                is_empty=len(text) == 0,
            )
        except Exception as e:
            raise STTConnectionError(
                f"macOS STT failed: {e}",
                voice_message="All speech recognition methods failed.",
            ) from e
        finally:
            os.unlink(tmp_path)


class STTManager:
    """
    Main speech-to-text manager with fallback chain.

    Tries backends in order:
      1. WhisperLocalBackend (port 2022)
      2. MacOSSpeechBackend (emergency fallback)

    Usage:
        config = STTConfig.from_env()
        stt = STTManager(config)
        result = await stt.transcribe(audio_bytes)
        print(result.text)
    """

    def __init__(self, config: STTConfig | None = None) -> None:
        self.config = config or STTConfig.from_env()
        self._whisper = WhisperLocalBackend(self.config)
        self._macos = MacOSSpeechBackend()

    async def transcribe(self, audio_pcm: bytes) -> TranscriptResult:
        """
        Transcribe PCM audio to text using the best available backend.

        Args:
            audio_pcm: Raw PCM audio bytes (16kHz mono int16)

        Returns:
            TranscriptResult with .text and metadata

        Raises:
            STTError: If all backends fail (with voice_message for user)
        """
        if len(audio_pcm) < 1600:  # Less than 50ms of audio
            return TranscriptResult(
                text="",
                backend="skipped",
                is_empty=True,
            )

        # Try Whisper first
        try:
            return await self._whisper.transcribe(audio_pcm)
        except STTError as primary_error:
            logger.warning(
                "whisper_failed_trying_fallback",
                error=str(primary_error),
            )

        # Emergency fallback
        try:
            return await self._macos.transcribe(audio_pcm)
        except STTError:
            pass

        # All failed
        raise STTConnectionError(
            "All STT backends failed",
            voice_message=(
                "Sorry, speech recognition is unavailable. "
                "Please check that the Whisper service is running."
            ),
            recoverable=True,
        )

    async def health_check(self) -> dict[str, bool]:
        """Check health of all backends."""
        whisper_ok = await self._whisper.health_check()
        return {
            "whisper_local": whisper_ok,
            "macos_speech": self._macos._check_available(),
        }
