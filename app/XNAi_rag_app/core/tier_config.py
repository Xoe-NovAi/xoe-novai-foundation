#!/usr/bin/env python3
# ============================================================================
# Xoe-NovAi Phase 4.2.3 - Tiered Degradation Configuration
# ============================================================================
# Purpose: Centralize resource limits and configuration per degradation tier
# Features:
#   - Tier-specific resource limits (context window, top_k, max_tokens)
#   - Dynamic Whisper model selection per tier
#   - Factory methods for creating tier-aware service configurations
#   - Integration with DegradationTierManager
# ============================================================================

import logging
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
from enum import Enum

from .degradation import degradation_manager

logger = logging.getLogger(__name__)

class WhisperModel(str, Enum):
    """Available Whisper models for different degradation tiers."""
    DISTIL_LARGE = "distil-large-v3"
    BASE = "base"
    TINY = "tiny"

class TTSProvider(str, Enum):
    """Available TTS providers for different degradation tiers."""
    PIPER_ONNX = "piper_onnx"
    PYTTSX3 = "pyttsx3"

@dataclass
class RAGTierConfig:
    """Configuration for RAG service per degradation tier."""
    top_k: int = 5
    max_context_chars: int = 2048
    retrieval_enabled: bool = True
    cache_only: bool = False
    embedding_cache_ttl_seconds: int = 300  # 5 minutes for Tier 3
    vector_search_enabled: bool = True

@dataclass
class LLMTierConfig:
    """Configuration for LLM service per degradation tier."""
    max_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.95
    use_cache_only: bool = False
    response_timeout_seconds: int = 30

@dataclass
class VoiceTierConfig:
    """Configuration for voice services per degradation tier."""
    stt_model: WhisperModel = WhisperModel.DISTIL_LARGE
    tts_provider: TTSProvider = TTSProvider.PIPER_ONNX
    stt_timeout_seconds: int = 60
    tts_timeout_seconds: int = 30
    voice_enabled: bool = True
    wake_word_enabled: bool = True

@dataclass
class SystemTierConfig:
    """Complete system configuration for a degradation tier."""
    tier: int
    name: str
    description: str
    rag: RAGTierConfig
    llm: LLMTierConfig
    voice: VoiceTierConfig
    memory_threshold_percent: float
    cpu_threshold_percent: float

class DegradationConfigFactory:
    """
    Factory for creating tier-specific configurations.
    
    Provides centralized configuration management for all services
    based on the current degradation tier.
    """
    
    # Default configurations per tier
    TIER_CONFIGS = {
        1: SystemTierConfig(
            tier=1,
            name="Normal",
            description="Full performance - All features enabled",
            rag=RAGTierConfig(
                top_k=5,
                max_context_chars=2048,
                retrieval_enabled=True,
                cache_only=False,
                vector_search_enabled=True
            ),
            llm=LLMTierConfig(
                max_tokens=256,
                temperature=0.7,
                top_p=0.95,
                use_cache_only=False,
                response_timeout_seconds=30
            ),
            voice=VoiceTierConfig(
                stt_model=WhisperModel.DISTIL_LARGE,
                tts_provider=TTSProvider.PIPER_ONNX,
                stt_timeout_seconds=60,
                tts_timeout_seconds=30,
                voice_enabled=True,
                wake_word_enabled=True
            ),
            memory_threshold_percent=85.0,
            cpu_threshold_percent=80.0
        ),
        2: SystemTierConfig(
            tier=2,
            name="Constrained",
            description="Reduced context - Performance optimization",
            rag=RAGTierConfig(
                top_k=3,
                max_context_chars=1200,  # ~40% reduction
                retrieval_enabled=True,
                cache_only=False,
                vector_search_enabled=True
            ),
            llm=LLMTierConfig(
                max_tokens=150,  # ~40% reduction
                temperature=0.7,
                top_p=0.95,
                use_cache_only=False,
                response_timeout_seconds=25
            ),
            voice=VoiceTierConfig(
                stt_model=WhisperModel.BASE,
                tts_provider=TTSProvider.PIPER_ONNX,
                stt_timeout_seconds=45,
                tts_timeout_seconds=25,
                voice_enabled=True,
                wake_word_enabled=True
            ),
            memory_threshold_percent=92.0,
            cpu_threshold_percent=85.0
        ),
        3: SystemTierConfig(
            tier=3,
            name="Critical",
            description="Minimal context - Cache priority",
            rag=RAGTierConfig(
                top_k=1,  # Single best match only
                max_context_chars=500,  # ~75% reduction
                retrieval_enabled=True,
                cache_only=False,
                embedding_cache_ttl_seconds=300,  # 5 minutes
                vector_search_enabled=True
            ),
            llm=LLMTierConfig(
                max_tokens=100,  # ~60% reduction
                temperature=0.7,
                top_p=0.95,
                use_cache_only=False,
                response_timeout_seconds=20
            ),
            voice=VoiceTierConfig(
                stt_model=WhisperModel.TINY,
                tts_provider=TTSProvider.PIPER_ONNX,
                stt_timeout_seconds=30,
                tts_timeout_seconds=20,
                voice_enabled=True,
                wake_word_enabled=False  # Disable wake word to reduce CPU
            ),
            memory_threshold_percent=97.0,
            cpu_threshold_percent=90.0
        ),
        4: SystemTierConfig(
            tier=4,
            name="Failover",
            description="Read-only mode - Cache only",
            rag=RAGTierConfig(
                top_k=0,  # No fresh retrieval
                max_context_chars=0,  # No context
                retrieval_enabled=False,
                cache_only=True,
                vector_search_enabled=False
            ),
            llm=LLMTierConfig(
                max_tokens=50,  # Minimal response
                temperature=0.7,
                top_p=0.95,
                use_cache_only=True,
                response_timeout_seconds=15
            ),
            voice=VoiceTierConfig(
                stt_model=WhisperModel.TINY,
                tts_provider=TTSProvider.PYTTSX3,  # Fallback to CPU-only
                stt_timeout_seconds=15,
                tts_timeout_seconds=15,
                voice_enabled=False,  # Disable voice processing
                wake_word_enabled=False
            ),
            memory_threshold_percent=99.0,
            cpu_threshold_percent=95.0
        )
    }
    
    @classmethod
    def get_current_tier(cls) -> int:
        """Get the current degradation tier from the manager."""
        return degradation_manager.current_tier
    
    @classmethod
    def get_rag_config(cls, tier: Optional[int] = None) -> RAGTierConfig:
        """
        Get RAG configuration for the specified tier.
        
        Args:
            tier: Target tier (defaults to current tier)
            
        Returns:
            RAGTierConfig for the specified tier
        """
        if tier is None:
            tier = cls.get_current_tier()
        
        config = cls.TIER_CONFIGS.get(tier, cls.TIER_CONFIGS[1])
        logger.debug(f"RAG config for tier {tier}: {asdict(config.rag)}")
        return config.rag
    
    @classmethod
    def get_llm_config(cls, tier: Optional[int] = None) -> LLMTierConfig:
        """
        Get LLM configuration for the specified tier.
        
        Args:
            tier: Target tier (defaults to current tier)
            
        Returns:
            LLMTierConfig for the specified tier
        """
        if tier is None:
            tier = cls.get_current_tier()
        
        config = cls.TIER_CONFIGS.get(tier, cls.TIER_CONFIGS[1])
        logger.debug(f"LLM config for tier {tier}: {asdict(config.llm)}")
        return config.llm
    
    @classmethod
    def get_voice_config(cls, tier: Optional[int] = None) -> VoiceTierConfig:
        """
        Get voice configuration for the specified tier.
        
        Args:
            tier: Target tier (defaults to current tier)
            
        Returns:
            VoiceTierConfig for the specified tier
        """
        if tier is None:
            tier = cls.get_current_tier()
        
        config = cls.TIER_CONFIGS.get(tier, cls.TIER_CONFIGS[1])
        logger.debug(f"Voice config for tier {tier}: {asdict(config.voice)}")
        return config.voice
    
    @classmethod
    def get_system_config(cls, tier: Optional[int] = None) -> SystemTierConfig:
        """
        Get complete system configuration for the specified tier.
        
        Args:
            tier: Target tier (defaults to current tier)
            
        Returns:
            SystemTierConfig for the specified tier
        """
        if tier is None:
            tier = cls.get_current_tier()
        
        config = cls.TIER_CONFIGS.get(tier, cls.TIER_CONFIGS[1])
        logger.info(f"System config for tier {tier}: {config.name} - {config.description}")
        return config
    
    @classmethod
    def get_all_configs(cls) -> Dict[int, SystemTierConfig]:
        """Get all tier configurations."""
        return cls.TIER_CONFIGS.copy()
    
    @classmethod
    def get_tier_summary(cls, tier: Optional[int] = None) -> Dict[str, Any]:
        """
        Get a summary of the current tier configuration.
        
        Args:
            tier: Target tier (defaults to current tier)
            
        Returns:
            Summary dictionary with key configuration values
        """
        if tier is None:
            tier = cls.get_current_tier()
        
        config = cls.get_system_config(tier)
        
        return {
            "current_tier": tier,
            "tier_name": config.name,
            "description": config.description,
            "memory_threshold": config.memory_threshold_percent,
            "cpu_threshold": config.cpu_threshold_percent,
            "rag_config": {
                "top_k": config.rag.top_k,
                "max_context_chars": config.rag.max_context_chars,
                "retrieval_enabled": config.rag.retrieval_enabled,
                "cache_only": config.rag.cache_only,
                "vector_search_enabled": config.rag.vector_search_enabled
            },
            "llm_config": {
                "max_tokens": config.llm.max_tokens,
                "temperature": config.llm.temperature,
                "top_p": config.llm.top_p,
                "use_cache_only": config.llm.use_cache_only,
                "response_timeout_seconds": config.llm.response_timeout_seconds
            },
            "voice_config": {
                "stt_model": config.voice.stt_model.value,
                "tts_provider": config.voice.tts_provider.value,
                "stt_timeout_seconds": config.voice.stt_timeout_seconds,
                "tts_timeout_seconds": config.voice.tts_timeout_seconds,
                "voice_enabled": config.voice.voice_enabled,
                "wake_word_enabled": config.voice.wake_word_enabled
            }
        }
    
    @classmethod
    def log_tier_transition(cls, old_tier: int, new_tier: int):
        """Log tier transition with configuration changes."""
        old_config = cls.get_tier_summary(old_tier)
        new_config = cls.get_tier_summary(new_tier)
        
        logger.warning(
            f"⚠️ DEGRADATION TIER TRANSITION: {old_tier} → {new_tier}",
            extra={
                "old_tier": old_config,
                "new_tier": new_config,
                "transition_reason": "Resource threshold exceeded",
                "impact": {
                    "context_reduction": f"{old_config['rag_config']['max_context_chars']} → {new_config['rag_config']['max_context_chars']} chars",
                    "token_reduction": f"{old_config['llm_config']['max_tokens']} → {new_config['llm_config']['max_tokens']} tokens",
                    "stt_model_change": f"{old_config['voice_config']['stt_model']} → {new_config['voice_config']['stt_model']}",
                    "voice_enabled": new_config['voice_config']['voice_enabled']
                }
            }
        )

# Global configuration factory instance
tier_config_factory = DegradationConfigFactory()

# Convenience functions for direct access
def get_current_rag_config() -> RAGTierConfig:
    """Get RAG configuration for current tier."""
    return tier_config_factory.get_rag_config()

def get_current_llm_config() -> LLMTierConfig:
    """Get LLM configuration for current tier."""
    return tier_config_factory.get_llm_config()

def get_current_voice_config() -> VoiceTierConfig:
    """Get voice configuration for current tier."""
    return tier_config_factory.get_voice_config()

def get_current_system_config() -> SystemTierConfig:
    """Get complete system configuration for current tier."""
    return tier_config_factory.get_system_config()

def get_tier_summary() -> Dict[str, Any]:
    """Get summary of current tier configuration."""
    return tier_config_factory.get_tier_summary()