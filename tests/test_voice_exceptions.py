"""
Voice Service Exception Tests
============================
Verifies voice service exception hierarchy and functionality.
"""

import pytest
import sys
import os
from pathlib import Path

# Add app root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from XNAi_rag_app.services.voice.exceptions import (
    VoiceServiceError,
    STTError,
    TTSError,
    VADError,
)
from XNAi_rag_app.schemas.errors import ErrorCategory


class TestVoiceServiceError:
    """Test VoiceServiceError base class."""
    
    def test_voice_service_error_creation(self):
        """Test creating a VoiceServiceError."""
        exc = VoiceServiceError(
            message="Voice service failed",
            cause_code="stt_timeout"
        )
        assert exc.message == "Voice service failed"
        assert exc.cause_code == "stt_timeout"
        assert exc.category == ErrorCategory.VOICE_SERVICE
        assert exc.http_status == 503  # Service unavailable
    
    def test_voice_service_error_with_component(self):
        """Test VoiceServiceError with component."""
        exc = VoiceServiceError(
            message="STT failed",
            cause_code="stt_unavailable",
            component="stt"
        )
        assert exc.component == "stt"
        assert exc.details["component"] == "stt"
        assert exc.details["cause_code"] == "stt_unavailable"
    
    def test_voice_service_error_with_audio_format(self):
        """Test VoiceServiceError with audio format."""
        exc = VoiceServiceError(
            message="Unsupported format",
            cause_code="audio_format_unsupported",
            audio_format="OGG"
        )
        assert exc.details["audio_format"] == "OGG"
    
    def test_voice_service_error_cause_codes(self):
        """Verify voice error cause codes map to suggestions."""
        test_cases = [
            ("stt_circuit_open", "30 seconds"),
            ("tts_timeout", "speech synthesis"),
            ("vad_failed", "Voice activity detection"),
            ("rate_limited", "Too many requests"),
        ]
        
        for cause_code, expected_text in test_cases:
            exc = VoiceServiceError(
                message="Test",
                cause_code=cause_code
            )
            assert expected_text.lower() in exc.recovery_suggestion.lower(), \
                f"Expected '{expected_text}' in recovery suggestion for '{cause_code}'"
    
    def test_voice_service_error_with_cause(self):
        """Test VoiceServiceError with underlying cause."""
        original_error = RuntimeError("Underlying issue")
        exc = VoiceServiceError(
            message="Voice failed",
            cause_code="stt_unavailable",
            cause=original_error
        )
        assert exc.__cause__ is original_error
    
    def test_voice_service_error_serialization(self):
        """Test VoiceServiceError serialization."""
        exc = VoiceServiceError(
            message="STT failed",
            cause_code="stt_circuit_open",
            component="stt"
        )
        error_dict = exc.to_dict()
        
        assert error_dict["message"] == "STT failed"
        assert error_dict["category"] == "voice_service"
        assert error_dict["details"]["cause_code"] == "stt_circuit_open"
        assert error_dict["details"]["component"] == "stt"
        assert "recovery_suggestion" in error_dict


class TestSTTError:
    """Test STT-specific error."""
    
    def test_stt_error_creation(self):
        """Test creating an STTError."""
        exc = STTError(
            message="Speech recognition failed",
            cause_code="stt_timeout"
        )
        assert exc.component == "stt"
        assert exc.details["component"] == "stt"
    
    def test_stt_error_priority(self):
        """Test that STTError automatically sets component."""
        exc = STTError(
            message="Test",
            cause_code="timeout",
            component="different"  # Should be overridden
        )
        assert exc.component == "stt"  # STT sets it to "stt"


class TestTTSError:
    """Test TTS-specific error."""
    
    def test_tts_error_creation(self):
        """Test creating a TTSError."""
        exc = TTSError(
            message="Text-to-speech failed",
            cause_code="tts_timeout"
        )
        assert exc.component == "tts"
        assert exc.details["component"] == "tts"
    
    def test_tts_error_priority(self):
        """Test that TTSError automatically sets component."""
        exc = TTSError(
            message="Test",
            cause_code="timeout",
            component="different"  # Should be overridden
        )
        assert exc.component == "tts"  # TTS sets it to "tts"


class TestVADError:
    """Test VAD-specific error."""
    
    def test_vad_error_creation(self):
        """Test creating a VADError."""
        exc = VADError(
            message="Voice activity detection failed",
            cause_code="vad_failed"
        )
        assert exc.component == "vad"
        assert exc.details["component"] == "vad"
    
    def test_vad_error_priority(self):
        """Test that VADError automatically sets component."""
        exc = VADError(
            message="Test",
            cause_code="failed",
            component="different"  # Should be overridden
        )
        assert exc.component == "vad"  # VAD sets it to "vad"


class TestVoiceErrorInheritance:
    """Test voice error inheritance chain."""
    
    def test_stt_is_voice_service_error(self):
        """Test STTError is a VoiceServiceError."""
        exc = STTError(message="Test", cause_code="test")
        assert isinstance(exc, VoiceServiceError)
    
    def test_tts_is_voice_service_error(self):
        """Test TTSError is a VoiceServiceError."""
        exc = TTSError(message="Test", cause_code="test")
        assert isinstance(exc, VoiceServiceError)
    
    def test_vad_is_voice_service_error(self):
        """Test VADError is a VoiceServiceError."""
        exc = VADError(message="Test", cause_code="test")
        assert isinstance(exc, VoiceServiceError)
    
    def test_voice_service_is_xnai_exception(self):
        """Test VoiceServiceError is an XNAiException."""
        from XNAi_rag_app.api.exceptions import XNAiException
        exc = VoiceServiceError(message="Test", cause_code="test")
        assert isinstance(exc, XNAiException)
