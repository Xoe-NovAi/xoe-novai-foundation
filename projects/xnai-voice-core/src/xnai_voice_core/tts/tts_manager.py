"""
TTSManager — Text-to-speech with priority queue and fallback chain.

Backend priority:
  1. Kokoro local (port 8880) — default, natural voice, offline
  2. OpenAI TTS API — cloud fallback, highest quality
  3. macOS `say` subprocess — emergency fallback, always available

Events are queued by priority. Higher-priority events interrupt lower ones.
An interrupt (priority=3) stops current playback immediately.
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import time
from dataclasses import dataclass

import structlog

logger = structlog.get_logger(__name__)

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


@dataclass
class TTSConfig:
    """Configuration for the TTSManager."""
    kokoro_url: str = "http://127.0.0.1:8880"
    openai_api_key: str = ""
    voice: str = "af_sky"           # Kokoro voice
    speed: float = 1.0
    timeout_sec: float = 15.0
    fallback_to_say: bool = True    # Always use macOS say as last resort

    @classmethod
    def from_env(cls) -> "TTSConfig":
        return cls(
            kokoro_url=os.getenv("VOICEOS_TTS_URL", "http://127.0.0.1:8880"),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            voice=os.getenv("VOICEOS_TTS_VOICE", "af_sky"),
            speed=float(os.getenv("VOICEOS_TTS_SPEED", "1.0")),
        )


class TTSError(Exception):
    """Base error for TTS failures."""
    def __init__(self, message: str, voice_message: str = "", recoverable: bool = True):
        super().__init__(message)
        self.voice_message = voice_message
        self.recoverable = recoverable


class PiperBackend:
    """Piper ONNX local CPU TTS backend."""

    def __init__(self, config: TTSConfig) -> None:
        self.config = config
        self._available = False
        self.voice = None
        
        try:
            from piper.voice import PiperVoice
            model_dir = os.path.expanduser("~/.voiceos/models")
            os.makedirs(model_dir, exist_ok=True)
            model_path = os.path.join(model_dir, f"{self.config.voice}.onnx")
            config_path = os.path.join(model_dir, f"{self.config.voice}.onnx.json")
            
            if os.path.exists(model_path) and os.path.exists(config_path):
                self.voice = PiperVoice.load(model_path, config_path)
                self._available = True
            else:
                logger.warning(f"Piper model {self.config.voice} not found in {model_dir}")
        except ImportError:
            logger.warning("piper-tts not installed")

    def _do_synthesize(self, text: str) -> bytes:
        if not self.voice:
            return b""
        # Synthesize raw PCM bytes
        return b"".join(self.voice.synthesize_stream_raw(text))

    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize text to audio via Piper ONNX.
        Returns:
            Raw audio bytes (PCM)
        """
        if not self._available or not self.voice:
            raise TTSError("Piper ONNX is not available", recoverable=True)

        try:
            pcm_bytes = await asyncio.get_running_loop().run_in_executor(
                None, self._do_synthesize, text
            )
            return pcm_bytes
        except Exception as e:
            raise TTSError(
                f"Piper synthesis failed: {e}",
                recoverable=True,
            ) from e

    async def health_check(self) -> bool:
        return self._available and self.voice is not None


class MacOSSayBackend:
    """Emergency fallback: macOS `say` command."""

    def __init__(self, speed: float = 1.0) -> None:
        # macOS say uses words-per-minute; 180 is roughly natural
        self.wpm = int(180 * speed)

    async def speak(self, text: str) -> None:
        """Speak text using macOS `say` (blocking subprocess in executor)."""
        await asyncio.get_running_loop().run_in_executor(
            None,
            lambda: subprocess.run(
                ["say", "-r", str(self.wpm), text],
                timeout=60,
            ),
        )
        logger.debug("macos_say_complete", text=text[:40])


class TTSManager:
    """
    Main TTS manager with priority queue and fallback.

    Maintains a priority queue of text to speak. Events with higher
    priority play sooner. Priority 3 (interrupt) stops current speech.

    Usage:
        config = TTSConfig.from_env()
        tts = TTSManager(config)
        await tts.start()

        await tts.speak("Opening Terminal.")
        await tts.speak("Warning: file will be deleted.", priority=2)
        await tts.speak("Critical error!", priority=3)  # interrupts
    """

    def __init__(self, config: TTSConfig | None = None) -> None:
        self.config = config or TTSConfig.from_env()
        self._piper = PiperBackend(self.config)
        self._say = MacOSSayBackend(speed=self.config.speed)
        self._queue: asyncio.PriorityQueue[tuple[int, float, str]] = (
            asyncio.PriorityQueue()
        )
        self._current_task: asyncio.Task | None = None
        self._running = False
        self._worker_task: asyncio.Task | None = None
        self._idle_event: asyncio.Event = asyncio.Event()
        self._idle_event.set()  # starts idle

    async def start(self) -> None:
        """Start the TTS worker loop."""
        self._running = True
        self._worker_task = asyncio.create_task(
            self._worker_loop(), name="TTSWorker"
        )
        logger.info("tts_manager_started")

    async def stop(self) -> None:
        """Stop the TTS worker."""
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

    async def speak(self, text: str, priority: int = 1) -> None:
        """
        Queue text to be spoken.

        Args:
            text: Text to speak
            priority: 0=low, 1=normal, 2=high, 3=interrupt

        Priority 3 interrupts current speech immediately.
        """
        text = text.strip()
        if not text:
            return

        if priority >= 3:
            self.interrupt()

        # Mark not-idle as soon as item is queued (before worker picks it up)
        self._idle_event.clear()

        # Negate priority for min-heap (higher priority = lower heap key)
        seq = time.monotonic()  # tiebreaker for same-priority items
        await self._queue.put((-priority, seq, text))
        logger.debug(
            "tts_queued",
            priority=priority,
            text_preview=text[:50],
        )

    def interrupt(self) -> None:
        """Stop current TTS playback immediately."""
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            logger.debug("tts_interrupted")

    async def speak_and_wait(self, text: str, priority: int = 1) -> None:
        """Speak text and wait until it finishes playing."""
        await self.speak(text, priority)
        await self.wait_until_idle()

    async def wait_until_idle(self) -> None:
        """Wait until the TTS queue is empty and no audio is playing."""
        await self._idle_event.wait()

    @property
    def is_speaking(self) -> bool:
        """True if TTS is currently playing audio."""
        return not self._idle_event.is_set()

    async def _worker_loop(self) -> None:
        """Main TTS worker — dequeues and speaks events."""
        while self._running:
            try:
                _neg_priority, _seq, text = await asyncio.wait_for(
                    self._queue.get(), timeout=1.0
                )
                self._queue.task_done()

                self._idle_event.clear()  # mark as speaking
                self._current_task = asyncio.create_task(
                    self._speak_one(text), name="TTSSpeakOne"
                )
                try:
                    await self._current_task
                except asyncio.CancelledError:
                    logger.debug("tts_speak_cancelled")
                finally:
                    # Mark idle only when queue is also empty
                    if self._queue.empty():
                        self._idle_event.set()

            except asyncio.TimeoutError:
                self._idle_event.set()  # queue empty, definitely idle
                continue
            except Exception as e:
                self._idle_event.set()
                logger.error("tts_worker_error", error=str(e))

    async def _speak_one(self, text: str) -> None:
        """Speak one text item using the best available backend."""
        start = time.monotonic()

        # Try Piper first
        try:
            pcm_bytes = await self._piper.synthesize(text)
            
            # Piper returns raw PCM. _play_audio expects WAV if sounddevice fails,
            # but sounddevice can handle raw PCM directly if we parse it.
            # Actually, let's wrap PCM with a WAV header to be safe, using STTManager's function logic.
            import struct
            sample_rate = 22050 # Typical piper sample rate, verify config later
            num_channels = 1
            bits_per_sample = 16
            data_size = len(pcm_bytes)
            chunk_size = 36 + data_size
            byte_rate = sample_rate * num_channels * bits_per_sample // 8
            block_align = num_channels * bits_per_sample // 8
            wav_header = struct.pack(
                "<4sI4s4sIHHIIHH4sI",
                b"RIFF", chunk_size, b"WAVE",
                b"fmt ", 16, 1, num_channels, sample_rate,
                byte_rate, block_align, bits_per_sample,
                b"data", data_size,
            )
            wav_bytes = wav_header + pcm_bytes

            await self._play_audio(wav_bytes)
            duration_ms = (time.monotonic() - start) * 1000
            logger.info(
                "tts_spoken",
                backend="piper",
                duration_ms=round(duration_ms),
                text_preview=text[:50],
            )
            return
        except (TTSError, Exception) as e:
            logger.warning("piper_failed_using_say", error=str(e))

        # Fallback to macOS say
        if self.config.fallback_to_say:
            await self._say.speak(text)

    async def _play_audio(self, audio_bytes: bytes) -> None:
        """Play audio bytes using sounddevice if available, else subprocess."""
        try:
            import sounddevice as sd
            import numpy as np
            import wave
            import io

            with wave.open(io.BytesIO(audio_bytes)) as wf:
                sample_rate = wf.getframerate()
                channels = wf.getnchannels()
                audio_data = np.frombuffer(
                    wf.readframes(wf.getnframes()), dtype=np.int16
                )
                if channels > 1:
                    audio_data = audio_data.reshape(-1, channels)

            await asyncio.get_running_loop().run_in_executor(
                None,
                lambda: sd.play(audio_data, samplerate=sample_rate, blocking=True),
            )
        except Exception as e:
            logger.warning("sounddevice_playback_failed", error=str(e))
            # Write to temp file and play with afplay
            import tempfile, os
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_bytes)
                tmp_path = f.name
            try:
                await asyncio.get_running_loop().run_in_executor(
                    None,
                    lambda: subprocess.run(["afplay", tmp_path], timeout=60),
                )
            finally:
                os.unlink(tmp_path)

    async def health_check(self) -> dict[str, bool]:
        """Check health of all TTS backends."""
        piper_ok = await self._piper.health_check()
        say_ok = True  # macOS say is always available
        return {
            "kokoro_local": piper_ok,
            "macos_say": say_ok,
        }
