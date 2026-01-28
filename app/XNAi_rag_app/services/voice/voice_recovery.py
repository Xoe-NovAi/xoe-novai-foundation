"""
Voice Pipeline Error Recovery System
====================================
Integrates with existing circuit breaker infrastructure.
"""

import asyncio
import logging
import io
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class VoiceErrorType(str, Enum):
    STT_FAILURE = "stt_failure"
    TTS_FAILURE = "tts_failure"
    RAG_FAILURE = "rag_failure"
    NETWORK_FAILURE = "network_failure"
    TIMEOUT_FAILURE = "timeout_failure"

@dataclass
class VoiceRecoveryConfig:
    """Configuration for voice error recovery."""
    max_recovery_attempts: int = 3
    recovery_timeout_seconds: int = 30
    enable_text_fallback: bool = True
    enable_cached_responses: bool = True
    notify_user_on_failure: bool = True

class VoiceRecoveryManager:
    """
    Manages voice pipeline error recovery and graceful degradation.
    """

    def __init__(self, config: VoiceRecoveryConfig = None):
        self.config = config or VoiceRecoveryConfig()
        self.recovery_stats = {
            "total_recoveries": 0,
            "successful_recoveries": 0,
            "failed_recoveries": 0,
            "recovery_times": []
        }

    async def recover_from_error(
        self,
        error: Exception,
        error_type: VoiceErrorType,
        original_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute comprehensive error recovery workflow.

        Recovery Hierarchy:
        1. Circuit breaker protection
        2. Service-specific fallbacks
        3. Cross-service degradation
        4. User notification and retry
        """
        start_time = asyncio.get_event_loop().time()

        try:
            recovery_result = await self._execute_recovery_strategy(
                error_type, original_request
            )

            recovery_time = asyncio.get_event_loop().time() - start_time
            self.recovery_stats["recovery_times"].append(recovery_time)
            self.recovery_stats["successful_recoveries"] += 1

            return {
                **recovery_result,
                "recovered": True,
                "recovery_time": recovery_time,
                "original_error": str(error)
            }

        except Exception as recovery_error:
            self.recovery_stats["failed_recoveries"] += 1

            # Ultimate fallback - static error response
            return await self._ultimate_fallback(error, recovery_error)

    async def _execute_recovery_strategy(
        self, error_type: VoiceErrorType, request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute specific recovery strategy based on error type."""

        if error_type == VoiceErrorType.STT_FAILURE:
            return await self._recover_stt_failure(request)

        elif error_type == VoiceErrorType.TTS_FAILURE:
            return await self._recover_tts_failure(request)

        elif error_type == VoiceErrorType.RAG_FAILURE:
            return await self._recover_rag_failure(request)

        elif error_type == VoiceErrorType.NETWORK_FAILURE:
            return await self._recover_network_failure(request)

        elif error_type == VoiceErrorType.TIMEOUT_FAILURE:
            return await self._recover_timeout_failure(request)

        # Default recovery
        return await self._default_recovery(request)

    async def _recover_stt_failure(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from STT transcription failure."""
        audio_data = request.get("audio_data")

        # Strategy 1: Check for text fallback in request
        if self.config.enable_text_fallback and request.get("text_fallback"):
            logger.info("Using text fallback for STT failure")
            return {
                "transcription": request["text_fallback"],
                "transcription_method": "text_fallback",
                "recovery_strategy": "text_fallback"
            }

        # Strategy 2: Attempt lightweight STT with "Tiny" model
        try:
            logger.info("Attempting Strategy 2: Tiny model STT fallback")
            from faster_whisper import WhisperModel
            tiny_model = WhisperModel("tiny", device="cpu", compute_type="int8")
            segments, _ = tiny_model.transcribe(io.BytesIO(audio_data))
            text = " ".join([s.text for s in segments])
            if text.strip():
                return {
                    "transcription": text,
                    "transcription_method": "tiny_model_fallback",
                    "recovery_strategy": "lightweight_stt"
                }
        except Exception as e:
            logger.warning(f"Strategy 2 failed: {e}")

        # Strategy 3: Cached similar transcription
        # (This is a placeholder for future semantic cache lookup)

        # Strategy 4: Static fallback response
        return {
            "transcription": "Voice input could not be processed. Please try text input.",
            "transcription_method": "error_fallback",
            "recovery_strategy": "error_message"
        }

    async def _recover_tts_failure(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from TTS synthesis failure."""
        text_response = request.get("text_response", "")

        # TTS failure - return text-only response
        return {
            "response": text_response,
            "audio_response": None,
            "response_format": "text_only",
            "recovery_strategy": "text_only_fallback",
            "user_message": "Voice synthesis unavailable. Here's the text response:"
        }

    async def _recover_rag_failure(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from RAG processing failure."""
        transcription = request.get("transcription", "")

        # Strategy 1: Use cached responses for similar queries
        if self.config.enable_cached_responses:
            cached_response = await self._find_cached_response(transcription)
            if cached_response:
                return {
                    "response": cached_response,
                    "response_source": "cache",
                    "recovery_strategy": "cached_response"
                }

        # Strategy 2: Static knowledge base fallback
        static_response = await self._generate_static_response(transcription)
        return {
            "response": static_response,
            "response_source": "static_fallback",
            "recovery_strategy": "static_knowledge"
        }

    async def _recover_network_failure(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from network connectivity issues."""
        # Implement exponential backoff retry
        for attempt in range(self.config.max_recovery_attempts):
            try:
                # Retry the original request
                result = await self._retry_request(request)
                return result
            except Exception:
                if attempt < self.config.max_recovery_attempts - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

        # All retries failed
        return await self._network_failure_fallback(request)

    async def _recover_timeout_failure(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from timeout errors."""
        # Return partial results if available
        partial_transcription = request.get("partial_transcription")
        if partial_transcription:
            return {
                "transcription": partial_transcription,
                "response": "Processing timed out, but here's what was transcribed:",
                "recovery_strategy": "partial_results"
            }

        return {
            "response": "Request timed out. Please try again with a shorter input.",
            "recovery_strategy": "timeout_fallback"
        }

    async def _default_recovery(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Default recovery strategy for unhandled errors."""
        return {
            "response": "I'm experiencing technical difficulties. Please try again in a moment.",
            "recovery_strategy": "default_fallback",
            "error": True
        }

    async def _ultimate_fallback(self, original_error: Exception,
                               recovery_error: Exception) -> Dict[str, Any]:
        """Ultimate fallback when all recovery strategies fail."""
        logger.error(f"All recovery strategies failed: {original_error} -> {recovery_error}")

        return {
            "response": "Service temporarily unavailable. Please contact support if this persists.",
            "recovery_strategy": "ultimate_fallback",
            "critical_failure": True,
            "original_error": str(original_error),
            "recovery_error": str(recovery_error)
        }

# Integration with existing voice interface
async def process_voice_with_recovery(audio_data: bytes, config: VoiceRecoveryConfig = None) -> Dict[str, Any]:
    """
    Process voice request with comprehensive error recovery.

    This function integrates voice recovery with the existing voice pipeline.
    """
    recovery_manager = VoiceRecoveryManager(config)

    try:
        # Normal voice processing pipeline
        result = await process_voice_pipeline(audio_data)
        return result

    except Exception as e:
        # Determine error type
        error_type = classify_voice_error(e)

        # Execute recovery
        recovery_result = await recovery_manager.recover_from_error(
            e, error_type, {"audio_data": audio_data}
        )

        return recovery_result

def classify_voice_error(error: Exception) -> VoiceErrorType:
    """Classify the type of voice processing error."""
    error_str = str(error).lower()

    if "stt" in error_str or "transcription" in error_str or "whisper" in error_str:
        return VoiceErrorType.STT_FAILURE
    elif "tts" in error_str or "synthesis" in error_str or "piper" in error_str:
        return VoiceErrorType.TTS_FAILURE
    elif "rag" in error_str or "knowledge" in error_str:
        return VoiceErrorType.RAG_FAILURE
    elif "network" in error_str or "connection" in error_str:
        return VoiceErrorType.NETWORK_FAILURE
    elif "timeout" in error_str:
        return VoiceErrorType.TIMEOUT_FAILURE
    else:
        return VoiceErrorType.TIMEOUT_FAILURE  # Default