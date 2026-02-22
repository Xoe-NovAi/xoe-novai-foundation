"""
Enhanced Service Orchestrator with OpenPipe Integration
=======================================================
Extends the existing services_init.py with comprehensive OpenPipe integration
while maintaining sovereignty and offline-first capabilities.
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
from .openpipe_integration import openpipe_manager

# Service imports
from ..services.rag.rag_service import RAGService
from ..services.voice.voice_interface import setup_voice_interface
from ..services.research_agent import get_research_agent

from .consul_client import consul_client

logger = get_logger(__name__)

class EnhancedServiceOrchestrator:
    """
    Enhanced orchestrator with OpenPipe integration for the Xoe-NovAi stack.
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
        Initialize all services with OpenPipe integration in strict order.
        """
        if self._initialized:
            logger.warning("Services already initialized")
            return self.services

        start_time = time.time()
        logger.info("=" * 70)
        logger.info("Initializing Xoe-NovAi Foundation Stack with OpenPipe")
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

            # 2.3 OpenPipe Integration
            openpipe_success = await openpipe_manager.initialize()
            if openpipe_success:
                logger.info("✓ OpenPipe integration initialized")
            else:
                logger.warning("⚠ OpenPipe integration failed, continuing without OpenPipe")

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

            # 5. Business Services with OpenPipe Integration
            self.services['rag'] = RAGService(self.services.get('vectorstore'))
            
            # Wrap RAG service with OpenPipe if available
            if openpipe_success:
                self.services['rag'] = openpipe_manager.create_llm_wrapper(
                    self.services['rag'], "rag_service"
                )
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
        Gracefully shutdown all services including OpenPipe.
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
        
        # Shutdown OpenPipe integration
        await openpipe_manager.shutdown()
        
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
        Thread-safe lazy initialization of the LLM with OpenPipe integration.
        """
        if self._llm_cache is not None:
            return self._llm_cache

        async with self._llm_init_lock:
            # Double-checked locking pattern
            if self._llm_cache is not None:
                return self._llm_cache

            try:
                from .dependencies import get_llm_async
                logger.info("Initializing LLM (lazy loading with OpenPipe)...")
                llm = await get_llm_async()
                
                # Wrap with OpenPipe if available
                if openpipe_manager.openpipe_client:
                    llm = openpipe_manager.create_llm_wrapper(llm, "llm_service")
                    logger.info("✓ LLM wrapped with OpenPipe integration")
                
                self._llm_cache = llm
                self.services['llm'] = self._llm_cache
                return self._llm_cache
            except Exception as e:
                logger.error(f"Failed to initialize LLM: {e}")
                raise

    async def _background_init_models(self):
        """Background task to initialize embeddings, vectorstore, and LLM with OpenPipe."""
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
                logger.info("Background: LLM primed and cached with OpenPipe")
            except Exception as e:
                logger.warning(f"Background: LLM init failed: {e}")

        finally:
            self._ready = True

    async def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report including OpenPipe metrics."""
        try:
            # Get OpenPipe performance report
            openpipe_report = await openpipe_manager.get_performance_report()
            
            # Get existing system metrics
            system_metrics = {
                "memory_usage": self._get_memory_usage(),
                "active_sessions": self._get_active_sessions(),
                "cache_stats": self._get_cache_stats(),
                "uptime_seconds": time.time() - self._start_time if hasattr(self, '_start_time') else 0
            }
            
            return {
                "openpipe_integration": openpipe_report,
                "system_metrics": system_metrics,
                "overall_health": self._assess_overall_health(openpipe_report, system_metrics)
            }
            
        except Exception as e:
            logger.error(f"Performance report generation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics."""
        import psutil
        memory = psutil.virtual_memory()
        return {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_percent": memory.percent,
            "free_gb": round(memory.free / (1024**3), 2)
        }
    
    def _get_active_sessions(self) -> int:
        """Get number of active sessions."""
        # This would integrate with your session management
        return 0  # Placeholder
    
    def _get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics from Redis."""
        if not self.services.get('redis'):
            return {"status": "redis_unavailable"}
        
        try:
            # Get Redis cache statistics
            redis = self.services['redis']
            info = redis.info('memory')
            return {
                "used_memory_human": info.get('used_memory_human', 'N/A'),
                "maxmemory_human": info.get('maxmemory_human', 'N/A'),
                "cache_hits": info.get('keyspace_hits', 0),
                "cache_misses": info.get('keyspace_misses', 0)
            }
        except Exception as e:
            logger.warning(f"Cache stats retrieval failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _assess_overall_health(self, openpipe_report: Dict[str, Any], system_metrics: Dict[str, Any]) -> str:
        """Assess overall system health."""
        health_score = 100
        
        # Check OpenPipe integration status
        if openpipe_report.get("integration_status") != "active":
            health_score -= 20
        
        # Check memory usage
        memory_usage = system_metrics.get("memory_usage", {}).get("used_percent", 0)
        if memory_usage > 80:
            health_score -= 20
        elif memory_usage > 60:
            health_score -= 10
        
        # Check cache performance
        cache_stats = system_metrics.get("cache_stats", {})
        if cache_stats.get("status") == "error":
            health_score -= 10
        
        # Determine health status
        if health_score >= 90:
            return "excellent"
        elif health_score >= 75:
            return "good"
        elif health_score >= 60:
            return "fair"
        else:
            return "poor"

# Global enhanced orchestrator instance
enhanced_orchestrator = EnhancedServiceOrchestrator()