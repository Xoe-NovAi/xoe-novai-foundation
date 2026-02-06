"""
Xoe-NovAi Services Module
=========================
Core business logic and service implementations.
"""

from .rag.rag_service import RAGService
from .voice.voice_interface import VoiceInterface, get_voice_interface
from .research_agent import ResearchBestPracticeAgent

__all__ = [
    'RAGService',
    'VoiceInterface',
    'get_voice_interface',
    'ResearchBestPracticeAgent'
]