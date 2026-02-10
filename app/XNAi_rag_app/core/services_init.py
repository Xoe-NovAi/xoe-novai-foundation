"""
Xoe-NovAi Service Orchestrator
===============================
Handles ordered initialization of all stack services.
Ensures dependencies are resolved before dependent services start.
"""

import logging
import time
import asyncio
from typing import Dict, Any, Optional, List

# Core imports
from XNAi_rag_app.core.config_loader import load_config
from XNAi_rag_app.core.logging_config import setup_logging, get_logger
from XNAi_rag_app.core.observability import observability
from XNAi_rag_app.core.metrics import start_metrics_server
from XNAi_rag_app.core.circuit_breakers import initialize_circuit_breakers, initialize_voice_circuit_breakers
from XNAi_rag_app.core.dependencies import (
    get_redis_client,
    get_http_client,
    get_embeddings,
    get_vectorstore,
    shutdown_dependencies
)

# Service imports
from XNAi_rag_app.services.rag.rag_service import RAGService
from XNAi_rag_app.services.voice.voice_interface import setup_voice_interface
from XNAi_rag_app.services.research_agent import get_research_agent

logger = get_logger(__name__)

class ServiceOrchestrator:
    """
    Orchestrates the lifecycle of all services in the Xoe-NovAi stack.
    """
    
    def __init__(self):
        self.config = None
        self.services: Dict[str, Any] = {}
        self._initialized = False
        self._ready = False
        self._background_tasks: List[asyncio.Task] = []
        # Lock and cache for LLM initialization to prevent race conditions
        self._llm_init_lock = asyncio.Lock()
        self._llm_cache = None

    async def _initialize_llm(self):
        """Thread-safe LLM initialization with double-check pattern."""
        # Fast path
        if self._llm_cache is not None:
            return self._llm_cache

        async with self._llm_init_lock:
            if self._llm_cache is not None:
                return self._llm_cache

            # Lazy import to avoid circular deps at module import time
            from XNAi_rag_app.core.dependencies import get_llm_async

            logger.info("[LLM Init] Priming LLM (this may take a few seconds)...")
            try:
                self._llm_cache = await get_llm_async()
                logger.info("[LLM Init] LLM primed successfully")
                return self._llm_cache
            except Exception as e:
                logger.warning(f"[LLM Init] Failed to prime LLM: {e}")
                self._llm_cache = None
                raise

    async def initialize_all(self) -> Dict[str, Any]:
        """
        Initialize all services in strict order.
        """
        if self._initialized:
            logger.warning("Services already initialized")
            return self.services

        start_time = time.time()
        logger.info("=" * 70)
        logger.info("Initializing Xoe-NovAi Foundation Stack")
        logger.info("=" * 70)

        try:
            # 1. Configuration & Logging
            self.config = load_config()
            setup_logging()
            logger.info("✓ Configuration and logging initialized")

            # 2. Metrics & Observability
            start_metrics_server()
            
            # 2.1 Circuit Breakers (Redis needed)
            redis_url = f"redis://:{self.config.get('redis', {}).get('password', '')}@{self.config.get('redis', {}).get('host', 'redis')}:{self.config.get('redis', {}).get('port', 6379)}/0"
            try:
                await initialize_voice_circuit_breakers(redis_url)
                logger.info("✓ Circuit breakers initialized")
            except Exception as e:
                logger.warning(f"⚠ Failed to initialize circuit breakers: {e}")

            # Observability is initialized on import, but we can log its status
            logger.info("✓ Metrics and observability initialized")

            # 3. Core Infrastructure (Redis, HTTP)
            try:
                self.services['redis'] = get_redis_client()
                logger.info("✓ Redis connection established")
            except Exception as e:
                logger.warning(f"⚠ Redis not available: {e}")
                self.services['redis'] = None

            self.services['http_client'] = get_http_client()
            logger.info("✓ HTTP client initialized")

            # 4. Models (Embeddings, Vectorstore, LLM) - initialize in background to keep startup fast
            # Placeholders so other services can inspect presence
            self.services['embeddings'] = None
            self.services['vectorstore'] = None
            self.services['llm'] = None

            # Schedule background initialization of heavy models (non-blocking)
            try:
                task = asyncio.create_task(self._background_init_models())
                self._background_tasks.append(task)
                logger.info("✓ Background model initialization scheduled")
            except Exception as e:
                logger.warning(f"Failed to schedule background model init: {e}")

            # 5. Business Services
            self.services['rag'] = RAGService(self.services.get('vectorstore'))
            logger.info("✓ RAG Service initialized")

            self.services['voice'] = setup_voice_interface()
            logger.info("✓ Voice Interface initialized")

            self.services['research'] = get_research_agent()
            # We don't start the monitor loop automatically, let the app decide
            logger.info("✓ Research Agent initialized")

            self._initialized = True
            # readiness will be true when background init completes
            duration = time.time() - start_time
            logger.info("=" * 70)
            logger.info(f"Stack initialized successfully in {duration:.2f}s")
            logger.info("=" * 70)

            return self.services

        except Exception as e:
            logger.critical(f"FAILED to initialize stack: {e}", exc_info=True)
            raise

    async def shutdown_all(self):
        """
        Gracefully shutdown all services.
        """
        logger.info("Shutting down Xoe-NovAi services...")
        
        # Stop research agent if it was running
        if 'research' in self.services:
            self.services['research'].stop_monitoring()
        
        # Shutdown observability
        if hasattr(observability, 'shutdown'):
            observability.shutdown()
            
        # Shutdown infrastructure
        await shutdown_dependencies()

        # Cancel any background init tasks
        for t in self._background_tasks:
            try:
                t.cancel()
            except Exception:
                pass
        self._background_tasks = []
        
        logger.info("Stack shutdown complete")

    def is_ready(self) -> bool:
        """Return True when background initialization has completed."""
        return self._ready

    async def _background_init_models(self):
        """Background task to initialize embeddings, vectorstore, and LLM."""
        try:
            # Import dependency helpers lazily
            from XNAi_rag_app.core.dependencies import (
                get_embeddings_async,
                get_vectorstore_async,
                get_llm_async,
            )

            try:
                embeddings = await get_embeddings_async()
                self.services['embeddings'] = embeddings
                logger.info("Background: embeddings initialized")
            except Exception as e:
                logger.warning(f"Background: embeddings init failed: {e}")

            try:
                vectorstore = await get_vectorstore_async(self.services.get('embeddings'))
                self.services['vectorstore'] = vectorstore
                logger.info("Background: vectorstore initialized")
            except Exception as e:
                logger.warning(f"Background: vectorstore init failed: {e}")

            try:
                await self._initialize_llm()
                # _initialize_llm caches LLM in _llm_cache
                self.services['llm'] = self._llm_cache
                logger.info("Background: LLM primed and cached")
            except Exception as e:
                logger.warning(f"Background: LLM init failed: {e}")

        finally:
            self._ready = True

# Global orchestrator instance
orchestrator = ServiceOrchestrator()

    
    
async def _noop():
    return None