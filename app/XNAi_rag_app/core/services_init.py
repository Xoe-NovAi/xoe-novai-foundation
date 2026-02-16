"""
Xoe-NovAi Service Orchestrator
===============================
Handles ordered initialization of all stack services.
Ensures dependencies are resolved before dependent services start.
"""

import logging
import time
import asyncio
import socket
from typing import Dict, Any, Optional, List

# Core imports
from .config_loader import load_config
from .logging_config import setup_logging, get_logger
from .observability import observability
from .metrics import start_metrics_server
from .circuit_breakers import initialize_circuit_breakers, initialize_voice_circuit_breakers
from .dependencies import (
    get_redis_client,
    get_http_client,
    get_embeddings,
    get_vectorstore,
    shutdown_dependencies
)

# Service imports
from ..services.rag.rag_service import RAGService
from ..services.voice.voice_interface import setup_voice_interface
from ..services.research_agent import get_research_agent

from .consul_client import consul_client

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
        self._service_id = f"rag-api-{socket.gethostname()}" if hasattr(socket, 'gethostname') else "rag-api-unknown"
        # Lock and cache for LLM initialization to prevent race conditions
        self._llm_init_lock = asyncio.Lock()
        self._llm_cache = None

    async def _register_with_consul(self):
        """Register the RAG API with Consul."""
        try:
            # Get port from config or default to 8000
            port = self.config.get('api', {}).get('port', 8000)
            # Use container name 'rag' or hostname as address
            import socket
            hostname = socket.gethostname()
            
            await consul_client.register_service(
                name="rag-api",
                service_id=self._service_id,
                address=hostname,
                port=port,
                check_url=f"http://{hostname}:{port}/health"
            )
        except Exception as e:
            logger.warning(f"⚠ Consul registration failed: {e}")

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
            
            # 2.1 Consul Registration (Optional foundation)
            await self._register_with_consul()
            logger.info("✓ Consul registration initiated")
            
            # 2.2 Circuit Breakers (Redis needed)
            redis_url = f"redis://:{self.config.get('redis', {}).get('password', '')}@{self.config.get('redis', {}).get('host', 'redis')}:{self.config.get('redis', {}).get('port', 6379)}/0"
            try:
                await initialize_circuit_breakers(redis_url)
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
        
        # Deregister from Consul
        try:
            await consul_client.deregister_service(self._service_id)
        except Exception as e:
            logger.warning(f"⚠ Failed to deregister from Consul: {e}")

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

    async def _initialize_llm(self) -> Any:
        """
        Thread-safe lazy initialization of the LLM.
        """
        if self._llm_cache is not None:
            return self._llm_cache

        async with self._llm_init_lock:
            # Double-checked locking pattern
            if self._llm_cache is not None:
                return self._llm_cache

            try:
                from .dependencies import get_llm_async
                logger.info("Initializing LLM (lazy loading)...")
                self._llm_cache = await get_llm_async()
                self.services['llm'] = self._llm_cache
                return self._llm_cache
            except Exception as e:
                logger.error(f"Failed to initialize LLM: {e}")
                raise

    async def _background_init_models(self):
        """Background task to initialize embeddings, vectorstore, and LLM."""
        try:
            # Import dependency helpers lazily
            from .dependencies import (
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