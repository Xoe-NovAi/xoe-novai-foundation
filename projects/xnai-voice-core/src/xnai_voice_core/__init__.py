"""
xnai-voice-core

Standalone, plug-and-play voice module for the XNAi Foundation Stack.
"""

__version__ = "0.1.0"

from .audio.audio_processor import AudioProcessor, AudioConfig, AudioChunk
from .stt.stt_manager import STTManager, STTConfig, TranscriptResult
from .tts.tts_manager import TTSManager, TTSConfig
from .core.voice_interface import VoiceSessionManager, VoiceFAISSClient, WakeWordDetector

__all__ = [
    "AudioProcessor",
    "AudioConfig",
    "AudioChunk",
    "STTManager",
    "STTConfig",
    "TranscriptResult",
    "TTSManager",
    "TTSConfig",
    "VoiceSessionManager",
    "VoiceFAISSClient",
    "WakeWordDetector"
]
