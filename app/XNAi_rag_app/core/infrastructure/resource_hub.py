"""
Resource Hub for Hellenic Ingestion (SESS-26)
==============================================
Provides singleton model loading and resource gating using AnyIO CapacityLimiter.
Ensures models are shared across workers and prevents OOM during ingestion.

Mandate: XNA Frontier (Resource Hardening)
"""

import anyio
import logging
import os
from typing import Dict, Any, Optional
from app.XNAi_rag_app.core.dependencies import get_llm, get_embeddings

logger = logging.getLogger(__name__)

class ResourceHub:
    """
    Singleton hub for managed model loading and resource gating.
    """
    _instance: Optional['ResourceHub'] = None
    _models: Dict[str, Any] = {}
    _limiter: Optional[anyio.CapacityLimiter] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResourceHub, cls).__new__(cls)
            # Limit concurrent model usage to 2 (e.g., 1 LLM + 1 Embedding)
            # This is a safe baseline for 16GB RAM
            cls._limiter = anyio.CapacityLimiter(2)
        return cls._instance
    
    async def get_model(self, model_type: str, **kwargs) -> Any:
        """
        Get or load a model with managed access.
        
        Args:
            model_type: 'llm' or 'embeddings'
            **kwargs: Loading parameters
            
        Returns:
            The loaded model instance
        """
        if model_type not in self._models:
            async with self._limiter:
                if model_type == 'llm':
                    # Use get_llm from dependencies (already optimized for stack)
                    self._models['llm'] = await anyio.to_thread.run_sync(
                        lambda: get_llm(**kwargs)
                    )
                elif model_type == 'embeddings':
                    self._models['embeddings'] = await anyio.to_thread.run_sync(
                        lambda: get_embeddings(**kwargs)
                    )
                else:
                    raise ValueError(f"Unknown model type: {model_type}")
                    
        return self._models[model_type]

    async def release_model(self, model_type: str):
        """Unload a model to free RAM (optional manual control)"""
        if model_type in self._models:
            # We don't actually 'unload' in Python easily, but we can delete reference
            del self._models[model_type]
            logger.info(f"Model reference {model_type} released")

    @property
    def limiter(self) -> anyio.CapacityLimiter:
        return self._limiter

# Global accessor
_hub = ResourceHub()

async def get_resource_hub() -> ResourceHub:
    return _hub
