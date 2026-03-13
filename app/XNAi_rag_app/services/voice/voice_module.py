"""
Voice Module for Chainlit Integration
======================================

Provides modular voice integration for Chainlit UI.
Wraps the existing voice services with a clean interface.

CLAUDE STANDARD: Uses AnyIO for structured concurrency.
TORCH-FREE: No PyTorch dependencies.

Features:
- Wake word detection ("Hey Nova")
- STT (Speech-to-Text) with faster-whisper
- TTS (Text-to-Speech) with Piper ONNX
- Audio streaming support
- Circuit breaker protection
- Feature flag for enable/disable

Usage:
    from XNAi_rag_app.services.voice.voice_module import VoiceModule, VoiceConfig

    # Initialize voice module
    config = VoiceConfig(wake_word_enabled=True)
    voice = VoiceModule(config)
    await voice.initialize()

    # In Chainlit handler:
    if voice.is_enabled():
        transcription, confidence = await voice.transcribe(audio_data)
        audio = await voice.synthesize("Hello, how can I help?")
"""

import os
import logging
import anyio
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Import feature flag
FEATURE_VOICE = os.getenv("FEATURE_VOICE", "false").lower() == "true"

# Try to import voice interface components
try:
    from .voice_interface import (
        VoiceInterface,
        VoiceConfig as VoiceInterfaceConfig,
        STTProvider,
        TTSProvider,
        WhisperModel_,
        WakeWordDetector,
        AudioStreamProcessor,
        VoiceRateLimiter,
        VoiceSessionManager,
        VoiceFAISSClient,
    )

    VOICE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Voice interface not available: {e}")
    VoiceInterface = None
    VoiceInterfaceConfig = None
    STTProvider = None
    TTSProvider = None
    WhisperModel_ = None
    WakeWordDetector = None
    AudioStreamProcessor = None
    VoiceRateLimiter = None
    VoiceSessionManager = None
    VoiceFAISSClient = None
    VOICE_AVAILABLE = False

# Import circuit breakers
try:
    from ...core.circuit_breakers import (
        voice_stt_breaker,
        voice_tts_breaker,
        CircuitBreakerError,
    )

    CIRCUIT_BREAKERS_AVAILABLE = True
except ImportError:
    voice_stt_breaker = None
    voice_tts_breaker = None
    CircuitBreakerError = Exception
    CIRCUIT_BREAKERS_AVAILABLE = False


# ============================================================================
# Configuration
# ============================================================================


@dataclass
class VoiceModuleConfig:
    """Configuration for VoiceModule."""

    # Feature flags
    enabled: bool = False
    wake_word_enabled: bool = True
    offline_mode: bool = True

    # Wake word settings
    wake_word: str = "hey nova"
    wake_word_sensitivity: float = 0.5

    # STT settings
    stt_provider: str = "faster_whisper"
    whisper_model: str = "tiny"
    whisper_device: str = "cpu"

    # TTS settings
    tts_provider: str = "piper"
    piper_model_path: Optional[str] = None

    # Audio settings
    sample_rate: int = 16000
    channels: int = 1

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    def to_voice_interface_config(self) -> Optional["VoiceInterfaceConfig"]:
        """Convert to VoiceInterface config."""
        if not VoiceInterfaceConfig:
            return None

        return VoiceInterfaceConfig(
            stt_provider=STTProvider(self.stt_provider) if STTProvider else None,
            tts_provider=TTSProvider(self.tts_provider) if TTSProvider else None,
            whisper_model=WhisperModel_(self.whisper_model) if WhisperModel_ else None,
            whisper_device=self.whisper_device,
            piper_model_path=self.piper_model_path,
            wake_word_enabled=self.wake_word_enabled,
            wake_word=self.wake_word,
            wake_word_sensitivity=self.wake_word_sensitivity,
            sample_rate=self.sample_rate,
            channels=self.channels,
            offline_mode=self.offline_mode,
        )


# ============================================================================
# Voice Module Exception
# ============================================================================


class VoiceNotEnabledError(Exception):
    """Raised when voice operations are attempted while disabled."""

    pass


class VoiceNotInitializedError(Exception):
    """Raised when voice operations are attempted before initialization."""

    pass


# ============================================================================
# Voice Module
# ============================================================================


class VoiceModule:
    """
    Modular voice integration for Chainlit.

    Provides a clean interface for voice operations with:
    - Wake word detection
    - STT (Speech-to-Text)
    - TTS (Text-to-Speech)
    - Circuit breaker protection
    - Graceful degradation

    Usage:
        voice = VoiceModule(config)
        await voice.initialize()

        # Check if enabled
        if voice.is_enabled():
            # Transcribe audio
            text, confidence = await voice.transcribe(audio_bytes)

            # Check wake word
            detected, confidence = voice.check_wake_word(text)

            # Synthesize speech
            audio = await voice.synthesize("Hello!")
    """

    def __init__(self, config: Optional[VoiceModuleConfig] = None):
        self.config = config or VoiceModuleConfig()

        # Core components
        self._voice_interface: Optional[VoiceInterface] = None
        self._wake_word_detector: Optional[WakeWordDetector] = None
        self._rate_limiter: Optional[VoiceRateLimiter] = None

        # State
        self._enabled = self.config.enabled
        self._initialized = False
        self._initialization_error: Optional[str] = None

        # Metrics
        self._transcription_count = 0
        self._synthesis_count = 0
        self._wake_word_count = 0

    # ========================================================================
    # Lifecycle
    # ========================================================================

    async def initialize(self) -> bool:
        """
        Initialize voice components.

        Returns:
            True if initialized successfully
        """
        if self._initialized:
            return True

        if not VOICE_AVAILABLE:
            self._initialization_error = "Voice interface not available"
            logger.warning(self._initialization_error)
            return False

        if not FEATURE_VOICE and not self.config.enabled:
            logger.info("Voice module disabled by feature flag")
            return False

        try:
            # Initialize rate limiter
            if VoiceRateLimiter:
                self._rate_limiter = VoiceRateLimiter(
                    max_requests=self.config.rate_limit_requests,
                    window_seconds=self.config.rate_limit_window,
                )

            # Initialize voice interface
            if VoiceInterface:
                interface_config = self.config.to_voice_interface_config()
                self._voice_interface = VoiceInterface(interface_config)

                # Initialize the interface
                init_success = await anyio.to_thread.run_sync(
                    self._voice_interface.initialize
                )

                if not init_success:
                    self._initialization_error = "Voice interface initialization failed"
                    logger.warning(self._initialization_error)
                    return False

            # Initialize wake word detector
            if self.config.wake_word_enabled and WakeWordDetector:
                self._wake_word_detector = WakeWordDetector(
                    wake_word=self.config.wake_word,
                    sensitivity=self.config.wake_word_sensitivity,
                )

            self._initialized = True
            self._enabled = True

            logger.info("Voice module initialized successfully")
            return True

        except Exception as e:
            self._initialization_error = str(e)
            logger.error(f"Voice module initialization failed: {e}")
            return False

    async def close(self) -> None:
        """Close voice components."""
        if self._voice_interface:
            try:
                await anyio.to_thread.run_sync(self._voice_interface.close)
            except Exception as e:
                logger.warning(f"Error closing voice interface: {e}")

        self._voice_interface = None
        self._wake_word_detector = None
        self._rate_limiter = None
        self._initialized = False
        self._enabled = False

        logger.info("Voice module closed")

    # ========================================================================
    # State Management
    # ========================================================================

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def is_enabled(self) -> bool:
        return self._enabled and self._initialized

    def enable(self) -> None:
        """Enable voice responses."""
        if self._initialized:
            self._enabled = True
            logger.info("Voice module enabled")

    def disable(self) -> None:
        """Disable voice responses."""
        self._enabled = False
        logger.info("Voice module disabled")

    def get_status(self) -> Dict[str, Any]:
        """Get voice module status."""
        return {
            "enabled": self._enabled,
            "initialized": self._initialized,
            "feature_flag": FEATURE_VOICE,
            "voice_available": VOICE_AVAILABLE,
            "initialization_error": self._initialization_error,
            "wake_word_enabled": self.config.wake_word_enabled,
            "stt_provider": self.config.stt_provider,
            "tts_provider": self.config.tts_provider,
            "metrics": {
                "transcription_count": self._transcription_count,
                "synthesis_count": self._synthesis_count,
                "wake_word_count": self._wake_word_count,
            },
        }

    # ========================================================================
    # STT (Speech-to-Text)
    # ========================================================================

    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
    ) -> Tuple[str, float]:
        """
        Transcribe audio to text.

        Args:
            audio_data: Raw audio bytes
            language: Optional language code (e.g., "en")

        Returns:
            Tuple of (transcription_text, confidence_score)

        Raises:
            VoiceNotEnabledError: If voice is disabled
            VoiceNotInitializedError: If not initialized
        """
        if not self.is_enabled:
            raise VoiceNotEnabledError("Voice module is not enabled")

        if not self._voice_interface:
            raise VoiceNotInitializedError("Voice interface not initialized")

        # Check rate limit
        if self._rate_limiter and not self._rate_limiter.is_allowed("default"):
            raise VoiceNotEnabledError("Rate limit exceeded")

        # Use circuit breaker if available
        if CIRCUIT_BREAKERS_AVAILABLE and voice_stt_breaker:
            try:
                result = await voice_stt_breaker.call(
                    lambda: self._do_transcribe(audio_data, language)
                )
                self._transcription_count += 1
                return result
            except CircuitBreakerError as e:
                logger.warning(f"STT circuit breaker open: {e}")
                raise VoiceNotEnabledError("STT service temporarily unavailable")
        else:
            result = await self._do_transcribe(audio_data, language)
            self._transcription_count += 1
            return result

    async def _do_transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
    ) -> Tuple[str, float]:
        """Perform transcription (internal)."""
        # Run transcription in thread pool
        result = await anyio.to_thread.run_sync(
            lambda: self._voice_interface.transcribe_audio(
                audio_data, language=language
            )
        )
        return result

    # ========================================================================
    # TTS (Text-to-Speech)
    # ========================================================================

    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
    ) -> Optional[bytes]:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize
            voice_id: Optional voice ID (provider-specific)

        Returns:
            Audio bytes or None if synthesis failed

        Raises:
            VoiceNotEnabledError: If voice is disabled
            VoiceNotInitializedError: If not initialized
        """
        if not self.is_enabled:
            raise VoiceNotEnabledError("Voice module is not enabled")

        if not self._voice_interface:
            raise VoiceNotInitializedError("Voice interface not initialized")

        # Check rate limit
        if self._rate_limiter and not self._rate_limiter.is_allowed("default"):
            logger.warning("TTS rate limit exceeded")
            return None

        # Use circuit breaker if available
        if CIRCUIT_BREAKERS_AVAILABLE and voice_tts_breaker:
            try:
                result = await voice_tts_breaker.call(
                    lambda: self._do_synthesize(text, voice_id)
                )
                self._synthesis_count += 1
                return result
            except CircuitBreakerError as e:
                logger.warning(f"TTS circuit breaker open: {e}")
                return None
        else:
            result = await self._do_synthesize(text, voice_id)
            self._synthesis_count += 1
            return result

    async def _do_synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
    ) -> Optional[bytes]:
        """Perform synthesis (internal)."""
        try:
            result = await anyio.to_thread.run_sync(
                lambda: self._voice_interface.synthesize_speech(text, voice_id)
            )
            return result
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            return None

    # ========================================================================
    # Wake Word Detection
    # ========================================================================

    def check_wake_word(self, text: str) -> Tuple[bool, float]:
        """
        Check for wake word in text.

        Args:
            text: Text to check for wake word

        Returns:
            Tuple of (detected, confidence)
        """
        if not self._wake_word_detector:
            return True, 1.0  # No detector means always detect

        detected, confidence = self._wake_word_detector.detect(text)

        if detected:
            self._wake_word_count += 1
            logger.info(
                f"Wake word detected: '{self.config.wake_word}' (confidence: {confidence:.2f})"
            )

        return detected, confidence

    def add_wake_word(self, phrase: str) -> None:
        """Add a new wake word phrase."""
        if self._wake_word_detector:
            self._wake_word_detector.add_phrase(phrase)
            logger.info(f"Added wake word phrase: '{phrase}'")

    def remove_wake_word(self, phrase: str) -> None:
        """Remove a wake word phrase."""
        if self._wake_word_detector:
            self._wake_word_detector.remove_phrase(phrase)
            logger.info(f"Removed wake word phrase: '{phrase}'")

    # ========================================================================
    # Streaming Support
    # ========================================================================

    async def start_streaming(self) -> bool:
        """Start streaming audio mode."""
        if not self.is_enabled:
            return False

        if self._voice_interface:
            try:
                return await anyio.to_thread.run_sync(
                    self._voice_interface.start_streaming
                )
            except Exception as e:
                logger.error(f"Failed to start streaming: {e}")
                return False

        return False

    async def stop_streaming(self) -> Optional[bytes]:
        """Stop streaming and get buffered audio."""
        if not self.is_enabled:
            return None

        if self._voice_interface:
            try:
                return await anyio.to_thread.run_sync(
                    self._voice_interface.stop_streaming
                )
            except Exception as e:
                logger.error(f"Failed to stop streaming: {e}")
                return None

        return None

    async def process_audio_chunk(self, chunk: bytes) -> Optional[str]:
        """
        Process an audio chunk for streaming STT.

        Args:
            chunk: Audio chunk bytes

        Returns:
            Partial transcription or None
        """
        if not self.is_enabled:
            return None

        if self._voice_interface:
            try:
                return await anyio.to_thread.run_sync(
                    lambda: self._voice_interface.process_audio_chunk(chunk)
                )
            except Exception as e:
                logger.error(f"Failed to process audio chunk: {e}")
                return None

        return None


# ============================================================================
# Factory Functions
# ============================================================================


async def create_voice_module(
    enabled: bool = True,
    wake_word_enabled: bool = True,
    offline_mode: bool = True,
    **kwargs,
) -> VoiceModule:
    """
    Create and initialize a voice module.

    Args:
        enabled: Whether to enable voice
        wake_word_enabled: Whether to enable wake word detection
        offline_mode: Whether to use offline-only providers
        **kwargs: Additional configuration options

    Returns:
        Initialized VoiceModule instance
    """
    config = VoiceModuleConfig(
        enabled=enabled,
        wake_word_enabled=wake_word_enabled,
        offline_mode=offline_mode,
        **kwargs,
    )

    module = VoiceModule(config)
    await module.initialize()

    return module
