"""
Voice Service Exception Hierarchy
=================================
Unified error handling for TTS/STT/VAD subsystems.
"""

from typing import Optional, Dict, Any
from ...api.exceptions import XNAiException
from ...schemas.errors import ErrorCategory


class VoiceServiceError(XNAiException):
    """Base exception for voice subsystem failures."""
    
    def __init__(
        self,
        message: str,
        cause_code: str,
        component: Optional[str] = None,
        audio_format: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        """
        Args:
            message: Human-readable error description
            cause_code: Machine-readable cause identifier
                (e.g., 'stt_unavailable', 'tts_timeout', 'vad_failed')
            component: Which voice component failed ('stt', 'tts', 'vad')
            audio_format: Audio format if relevant
            cause: Original exception if available
        """
        details = {
            "cause_code": cause_code,
        }
        if component:
            details["component"] = component
        if audio_format:
            details["audio_format"] = audio_format
        
        recovery = self._get_recovery_suggestion(cause_code)
        
        super().__init__(
            message=message,
            category=ErrorCategory.VOICE_SERVICE,
            details=details,
            recovery_suggestion=recovery,
            cause=cause
        )
        
        self.cause_code = cause_code
        self.component = component
    
    @staticmethod
    def _get_recovery_suggestion(cause_code: str) -> str:
        """Map cause codes to user-friendly recovery suggestions."""
        suggestions = {
            "stt_unavailable": "Speech-to-text service is temporarily unavailable. Try again in a moment.",
            "tts_unavailable": "Text-to-speech service is temporarily unavailable. Try again in a moment.",
            "stt_circuit_open": "STT circuit breaker is open. Wait 30 seconds before retry.",
            "tts_circuit_open": "TTS circuit breaker is open. Wait 30 seconds before retry.",
            "stt_timeout": "Speech recognition timed out. Speak more clearly or check microphone.",
            "tts_timeout": "Speech synthesis timed out. Try shorter text input.",
            "vad_failed": "Voice activity detection failed. Check audio input.",
            "audio_format_unsupported": "Audio format not supported. Use WAV/MP3/FLAC.",
            "rate_limited": "Too many requests. Wait before retrying.",
        }
        return suggestions.get(
            cause_code,
            "Voice service error occurred. Check logs and retry."
        )


# Specialized subclasses
class STTError(VoiceServiceError):
    """Speech-to-text specific error."""
    
    def __init__(self, message: str, cause_code: str, **kwargs):
        kwargs["component"] = "stt"
        super().__init__(message, cause_code, **kwargs)


class TTSError(VoiceServiceError):
    """Text-to-speech specific error."""
    
    def __init__(self, message: str, cause_code: str, **kwargs):
        kwargs["component"] = "tts"
        super().__init__(message, cause_code, **kwargs)


class VADError(VoiceServiceError):
    """Voice activity detection specific error."""
    
    def __init__(self, message: str, cause_code: str, **kwargs):
        kwargs["component"] = "vad"
        super().__init__(message, cause_code, **kwargs)
