"""
Memory Integration for Voice Orchestrator
Adds memory awareness to the voice orchestrator system
"""

import os
import sys
import logging

# Note: memory_bank is imported using package path to ensure singleton usage
from src.memory.memory_bank import get_memory_bank, store_interaction, get_relevant_context
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

class MemoryAwareVoiceOrchestrator:
    """Helper class to keep memory-related helpers.

    The main voice orchestrator will directly use the memory bank; this
    wrapper remains for backward compatibility and for code that prefers a
    separate helper object.
    """
    
    def __init__(self, orchestrator: 'VoiceOrchestrator'):
        """Keep a reference to the orchestrator and global memory bank."""
        self.orchestrator = orchestrator
        self.memory_bank = get_memory_bank()
    
    async def process_voice_input(self, audio_data: bytes) -> bool:
        """High‑level convenience method that performs a full cycle of
        transcription, context lookup, response generation, memory storage and
        speech playback.

        Returns True on success, False otherwise.  This method is provided
        mainly for scripts that want a single-call API; the orchestrator
        itself handles memory when the feature is enabled.
        """
        try:
            transcription = await self.orchestrator.stt_manager.transcribe(audio_data)
            context = get_relevant_context(transcription)

            # delegate to orchestrator (it will also record the interaction)
            response = await self.orchestrator.generate_response(transcription, context)
            if response is None:
                return False

            success = await self.orchestrator.tts_manager.speak(response)
            return success
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            await self.orchestrator.tts_manager.speak(f"Error: {str(e)}")
            return False
    
    async def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Forward to orchestrator; this helper only adds formatting if a
        context dict is provided.  The orchestrator itself will handle any
        memory configuration and storage.
        """
        try:
            if context:
                context_prompt = "\n".join([f"{k}: {v}" for k, v in context.items()])
                prompt = f"{prompt}\nContext:\n{context_prompt}"
            return await self.orchestrator.generate_response(prompt)
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return None
