"""
XNAi Voice Services
===================

Torch-free voice interface with Piper ONNX TTS and faster-whisper STT.

Features:
- Speech-to-Text (STT) with faster-whisper
- Text-to-Speech (TTS) with Piper ONNX
- Wake word detection ("Hey Nova")
- Circuit breaker protection
- Graceful degradation

Usage:
    from XNAi_rag_app.services.voice import VoiceModule, VoiceModuleConfig

    voice = VoiceModule(VoiceModuleConfig(enabled=True))
    await voice.initialize()

    # Transcribe
    text, confidence = await voice.transcribe(audio_bytes)

    # Synthesize
    audio = await voice.synthesize("Hello!")
"""

# Voice Module (Chainlit integration adapter) - Always available
from .voice_module import (
    VoiceModule,
    VoiceModuleConfig,
    VoiceNotEnabledError,
    VoiceNotInitializedError,
    create_voice_module,
)

# Try to import core voice interface components
# These may not be available if dependencies are missing
VoiceInterface = None
VoiceConfig = None
STTProvider = None
TTSProvider = None
VADProvider = None
WhisperModel_ = None
WakeWordDetector = None
AudioStreamProcessor = None
VoiceRateLimiter = None
VoiceSessionManager = None
VoiceFAISSClient = None
VoiceMetrics = None
voice_degradation = None
process_voice_with_recovery = None
VoiceRecoveryConfig = None
VoiceServiceError = None
STTError = None
TTSError = None
VADError = None

try:
    from .voice_interface import (
        VoiceInterface,
        VoiceConfig,
        STTProvider,
        TTSProvider,
        VADProvider,
        WhisperModel_,
        WakeWordDetector,
        AudioStreamProcessor,
        VoiceRateLimiter,
        VoiceSessionManager,
        VoiceFAISSClient,
        VoiceMetrics,
    )
except ImportError:
    pass  # Core interface not available

try:
    from .voice_degradation import voice_degradation
except ImportError:
    pass

try:
    from .voice_recovery import (
        process_voice_with_recovery,
        VoiceRecoveryConfig,
    )
except ImportError:
    pass

try:
    from .exceptions import (
        VoiceServiceError,
        STTError,
        TTSError,
        VADError,
    )
except ImportError:
    pass

__all__ = [
    # Voice Module (Chainlit integration) - Always available
    "VoiceModule",
    "VoiceModuleConfig",
    "VoiceNotEnabledError",
    "VoiceNotInitializedError",
    "create_voice_module",
    # Core Interface - Optional
    "VoiceInterface",
    "VoiceConfig",
    "STTProvider",
    "TTSProvider",
    "VADProvider",
    "WhisperModel_",
    # Components - Optional
    "WakeWordDetector",
    "AudioStreamProcessor",
    "VoiceRateLimiter",
    "VoiceSessionManager",
    "VoiceFAISSClient",
    "VoiceMetrics",
    # Degradation & Recovery - Optional
    "voice_degradation",
    "process_voice_with_recovery",
    "VoiceRecoveryConfig",
    # Exceptions - Optional
    "VoiceServiceError",
    "STTError",
    "TTSError",
    "VADError",
]

__version__ = "0.1.0"
