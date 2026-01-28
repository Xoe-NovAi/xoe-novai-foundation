"""
Xoe-NovAi Services Module
=========================
Core business logic and service implementations.
"""

from XNAi_rag_app.services.rag.rag_service import RAGService
from XNAi_rag_app.services.voice.voice_interface import VoiceInterface, get_voice_interface
from XNAi_rag_app.services.research_agent import ResearchBestPracticeAgent

__all__ = [
    'RAGService',
    'VoiceInterface',
    'get_voice_interface',
    'ResearchBestPracticeAgent'
]