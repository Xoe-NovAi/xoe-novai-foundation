"""
AudioProcessor — Microphone capture, VAD, noise reduction, audio output.

All audio I/O in VoiceOS goes through this module. sounddevice callbacks
are synchronous (C thread), bridged to asyncio via thread-safe queues.

Audio format throughout: 16kHz, mono, int16 (Whisper requirement).
"""

from __future__ import annotations

import asyncio
import subprocess
import threading
import time
from dataclasses import dataclass
from typing import AsyncIterator

import numpy as np
import structlog

logger = structlog.get_logger(__name__)

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    logger.warning("sounddevice_not_installed", hint="pip install sounddevice")


SAMPLE_RATE = 16_000          # Hz — Whisper requirement
CHANNELS = 1                  # Mono
DTYPE = "int16"               # 16-bit signed
CHUNK_FRAMES = 1_600          # 100ms chunks at 16kHz
SILENCE_DURATION_SEC = 2.5    # Seconds of silence before cutoff
SILENCE_THRESHOLD = 500       # RMS energy below this = silence (int16 scale)


@dataclass
class AudioChunk:
    """A chunk of raw audio from the microphone."""
    data: bytes          # Raw PCM int16
    timestamp: float     # Unix timestamp of capture
    is_silent: bool      # True if this chunk contains no speech
    rms: float           # Root-mean-square energy of chunk


@dataclass
class AudioConfig:
    """Configuration for audio capture and playback."""
    input_device: str | int | None = None   # None = system default
    output_device: str | int | None = None  # None = system default
    preferred_output: str = "Mac mini Speakers"
    sample_rate: int = SAMPLE_RATE
    silence_threshold: int = SILENCE_THRESHOLD
    silence_duration_sec: float = SILENCE_DURATION_SEC
    vad_aggressiveness: int = 2             # 0-3

    @classmethod
    def from_env(cls) -> "AudioConfig":
        import os
        return cls(
            preferred_output=os.getenv(
                "VOICEOS_OUTPUT_DEVICE", "Mac mini Speakers"
            ),
            silence_duration_sec=float(
                os.getenv("VOICEOS_SILENCE_DURATION", "2.5")
            ),
        )


class AudioOutputWatcher:
    """
    Background daemon that monitors macOS audio output device and
    restores it to the preferred device if it gets hijacked (e.g., by AirPods).

    Runs in a separate thread. Checks every 2 seconds.
    Requires `SwitchAudioSource` CLI tool (brew install switchaudio-osx).
    """

    def __init__(
        self,
        preferred_device: str = "Mac mini Speakers",
        check_interval_sec: float = 2.0,
    ) -> None:
        self.preferred_device = preferred_device
        self.check_interval_sec = check_interval_sec
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        """Start the watcher thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._watch_loop,
            daemon=True,
            name="AudioOutputWatcher",
        )
        self._thread.start()
        logger.info(
            "audio_watcher_started",
            preferred_device=self.preferred_device,
        )

    def stop(self) -> None:
        """Stop the watcher thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5.0)

    def _watch_loop(self) -> None:
        """Main watcher loop — runs in background thread."""
        while not self._stop_event.is_set():
            try:
                current = self._get_current_output()
                if current and current != self.preferred_device:
                    self._restore_output()
                    logger.info(
                        "audio_output_restored",
                        from_device=current,
                        to_device=self.preferred_device,
                    )
            except Exception as e:
                logger.debug("audio_watcher_check_failed", error=str(e))
            self._stop_event.wait(self.check_interval_sec)

    def _get_current_output(self) -> str | None:
        """Get current audio output device name via SwitchAudioSource."""
        try:
            result = subprocess.run(
                ["SwitchAudioSource", "-c", "-t", "output"],
                capture_output=True,
                text=True,
                timeout=2.0,
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None

    def _restore_output(self) -> None:
        """Restore output to preferred device via SwitchAudioSource."""
        try:
            subprocess.run(
                ["SwitchAudioSource", "-s", self.preferred_device, "-t", "output"],
                capture_output=True,
                timeout=2.0,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass


class VADDetector:
    """
    Simple energy-based Voice Activity Detector.

    Detects whether audio chunks contain speech based on RMS energy.
    Marks speech_active=True when energy exceeds threshold.
    Marks speech_active=False after silence_duration_sec of quiet.
    """

    def __init__(
        self,
        threshold: int = SILENCE_THRESHOLD,
        silence_duration_sec: float = SILENCE_DURATION_SEC,
    ) -> None:
        self.threshold = threshold
        self.silence_duration_sec = silence_duration_sec
        self._speech_active = False
        self._last_speech_time = 0.0

    def process(self, chunk: np.ndarray) -> bool:
        """
        Process an audio chunk and return True if speech is active.

        Args:
            chunk: numpy array of int16 audio samples

        Returns:
            True if speech has been detected and not yet timed out
        """
        rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))
        now = time.monotonic()

        if rms > self.threshold:
            self._speech_active = True
            self._last_speech_time = now
        elif self._speech_active:
            silence_elapsed = now - self._last_speech_time
            if silence_elapsed >= self.silence_duration_sec:
                self._speech_active = False

        return self._speech_active

    def reset(self) -> None:
        """Reset VAD state (call between utterances)."""
        self._speech_active = False
        self._last_speech_time = 0.0

    @staticmethod
    def compute_rms(chunk: np.ndarray) -> float:
        """Compute RMS energy of audio chunk."""
        return float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))


class AudioProcessor:
    """
    Main audio I/O controller for VoiceOS.

    Handles:
    - Microphone capture with VAD
    - Audio playback to speakers
    - Output device watching (anti-hijack)
    - Async interface for the voice pipeline

    Usage:
        config = AudioConfig.from_env()
        processor = AudioProcessor(config)

        # Start output device watcher
        processor.start_watcher()

        # Capture one utterance (blocks until speech + silence)
        audio_bytes = await processor.capture_utterance()

        # Play audio
        await processor.play(tts_audio_bytes)
    """

    def __init__(self, config: AudioConfig | None = None) -> None:
        self.config = config or AudioConfig.from_env()
        self.vad = VADDetector(
            threshold=self.config.silence_threshold,
            silence_duration_sec=self.config.silence_duration_sec,
        )
        self.watcher = AudioOutputWatcher(
            preferred_device=self.config.preferred_output
        )
        self._loop: asyncio.AbstractEventLoop | None = None
        self._capture_queue: asyncio.Queue[np.ndarray] | None = None
        self._playing = False
        self._play_stop_event = threading.Event()

    def start_watcher(self) -> None:
        """Start the audio output device watcher."""
        self.watcher.start()

    def stop_watcher(self) -> None:
        """Stop the audio output device watcher."""
        self.watcher.stop()

    async def capture_utterance(self) -> bytes:
        """
        Record one complete utterance (speech + trailing silence).

        Waits for speech to begin, then records until silence_duration_sec
        of silence is detected.

        Returns:
            Raw PCM audio bytes (16kHz mono int16) of the utterance

        Raises:
            RuntimeError: If sounddevice is not available
        """
        if not SOUNDDEVICE_AVAILABLE:
            raise RuntimeError(
                "sounddevice is not installed. Run: pip install sounddevice"
            )

        self._loop = asyncio.get_running_loop()
        self._capture_queue = asyncio.Queue()
        self.vad.reset()

        chunks: list[np.ndarray] = []
        speech_started = False

        def callback(
            indata: np.ndarray,
            frames: int,
            time_info: object,
            status: sd.CallbackFlags,
        ) -> None:
            if status:
                logger.debug("sounddevice_status", status=str(status))
            # Bridge sync callback to async queue
            chunk = indata[:, 0].copy()  # Take first channel (mono)
            assert self._loop is not None
            assert self._capture_queue is not None
            self._loop.call_soon_threadsafe(
                self._capture_queue.put_nowait, chunk
            )

        with sd.InputStream(
            samplerate=self.config.sample_rate,
            channels=CHANNELS,
            dtype=DTYPE,
            blocksize=CHUNK_FRAMES,
            device=self.config.input_device,
            callback=callback,
        ):
            logger.debug("capture_started")
            while True:
                chunk = await self._capture_queue.get()
                is_speech = self.vad.process(chunk)

                if is_speech:
                    if not speech_started:
                        speech_started = True
                        logger.debug("speech_detected")
                    chunks.append(chunk)
                    # Prevent unbounded memory usage (max 30 seconds = 300 chunks)
                    if len(chunks) > 300:
                        logger.warning("audio_capture_max_duration_reached")
                        break
                elif speech_started:
                    # Still collecting trailing silence
                    chunks.append(chunk)
                    if len(chunks) > 300:
                        logger.warning("audio_capture_max_duration_reached")
                        break
                    # Check if we've had enough silence
                    if not self.vad._speech_active:
                        logger.debug(
                            "utterance_complete",
                            chunks=len(chunks),
                            duration_ms=len(chunks) * 100,
                        )
                        break

        audio_array = np.concatenate(chunks)
        return audio_array.tobytes()

    async def capture_stream(self) -> AsyncIterator[AudioChunk]:
        """
        Stream audio chunks continuously. Yields AudioChunk objects.

        Use for real-time processing or streaming STT.
        Call `.aclose()` on the generator to stop.
        """
        if not SOUNDDEVICE_AVAILABLE:
            raise RuntimeError("sounddevice is not installed")

        self._loop = asyncio.get_running_loop()
        self._capture_queue = asyncio.Queue()

        def callback(
            indata: np.ndarray,
            frames: int,
            time_info: object,
            status: sd.CallbackFlags,
        ) -> None:
            chunk = indata[:, 0].copy()
            assert self._loop is not None
            assert self._capture_queue is not None
            self._loop.call_soon_threadsafe(
                self._capture_queue.put_nowait,
                (chunk, time.time()),
            )

        with sd.InputStream(
            samplerate=self.config.sample_rate,
            channels=CHANNELS,
            dtype=DTYPE,
            blocksize=CHUNK_FRAMES,
            device=self.config.input_device,
            callback=callback,
        ):
            while True:
                chunk, ts = await self._capture_queue.get()
                rms = VADDetector.compute_rms(chunk)
                is_silent = rms < self.config.silence_threshold
                yield AudioChunk(
                    data=chunk.tobytes(),
                    timestamp=ts,
                    is_silent=is_silent,
                    rms=rms,
                )

    async def play(self, audio: bytes) -> None:
        """
        Play raw PCM audio bytes through the configured output device.

        Args:
            audio: Raw PCM bytes (16kHz mono int16)
        """
        if not SOUNDDEVICE_AVAILABLE:
            logger.warning("sounddevice_unavailable_skipping_playback")
            return

        self._play_stop_event.clear()
        self._playing = True

        try:
            array = np.frombuffer(audio, dtype=np.int16)
            await asyncio.get_running_loop().run_in_executor(
                None,
                lambda: sd.play(
                    array,
                    samplerate=self.config.sample_rate,
                    device=self.config.output_device,
                    blocking=True,
                ),
            )
        finally:
            self._playing = False

        logger.debug("playback_complete", bytes=len(audio))

    def interrupt_playback(self) -> None:
        """Stop any currently playing audio immediately."""
        if self._playing and SOUNDDEVICE_AVAILABLE:
            sd.stop()
            self._play_stop_event.set()
            logger.debug("playback_interrupted")
