"""
Xoe-NovAi Service Orchestrator
===============================
Handles ordered initialization of all stack services.
Ensures dependencies are resolved before dependent services start.

CLAUDE STANDARD: Uses AnyIO for structured concurrency.
- TaskGroups for managed background tasks
- CancelScope for clean shutdown
- anyio.sleep for cancellation-safe delays
"""

import logging
import time
import anyio
import asyncio  # Kept for Lock compatibility
import socket
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

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

# OpenPipe integration (optional)
try:
    from .openpipe_integration import openpipe_manager
    OPENPIPE_AVAILABLE = True
except ImportError:
    openpipe_manager = None
    OPENPIPE_AVAILABLE = False

logger = get_logger(__name__)


class ServiceOrchestrator:
    """
    Orchestrates the lifecycle of all services in the Xoe-NovAi stack.
    
    CLAUDE STANDARD: Uses AnyIO for structured concurrency.
    Background tasks run in TaskGroups with proper cancellation.
    
    Attributes:
        enable_openpipe: Enable OpenPipe LLM optimization integration
    """
    
    def __init__(self, enable_openpipe: bool = True):
        self.config = None
        self.services: Dict[str, Any] = {}
        self._initialized = False
        self._ready = False
        self._enable_openpipe = enable_openpipe and OPENPIPE_AVAILABLE
        self._openpipe_initialized = False
        
        # CLAUDE: Use CancelScope for lifecycle management
        self._cancel_scope: Optional[anyio.CancelScope] = None
        self._running = False
        
        self._service_id = f"rag-api-{socket.gethostname()}" if hasattr(socket, 'gethostname') else "rag-api-unknown"
        
        # Lock for LLM initialization (asyncio.Lock for compatibility)
        self._llm_init_lock = asyncio.Lock()
        self._llm_cache = None
        
        # Start time for uptime tracking
        self._start_time: Optional[float] = None

    async def _register_with_consul(self):
        """Register the RAG API with Consul."""
        try:
            port = self.config.get('api', {}).get('port', 8000)
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
        
        CLAUDE STANDARD: Uses TaskGroup for background model initialization.
        """
        if self._initialized:
            logger.warning("Services already initialized")
            return self.services

        self._start_time = time.time()
        logger.info("=" * 70)
        logger.info("Initializing Xoe-NovAi Foundation Stack")
        if self._enable_openpipe:
            logger.info("OpenPipe Integration: ENABLED")
        logger.info("=" * 70)

        try:
            # 1. Configuration & Logging
            self.config = load_config()
            setup_logging()
            logger.info("✓ Configuration and logging initialized")

            # 2. Metrics & Observability
            start_metrics_server()
            
            # 2.1 Consul Registration
            await self._register_with_consul()
            logger.info("✓ Consul registration initiated")
            
            # 2.2 Circuit Breakers
            redis_url = f"redis://:{self.config.get('redis', {}).get('password', '')}@{self.config.get('redis', {}).get('host', 'redis')}:{self.config.get('redis', {}).get('port', 6379)}/0"
            try:
                await initialize_circuit_breakers(redis_url)
                await initialize_voice_circuit_breakers(redis_url)
                logger.info("✓ Circuit breakers initialized")
            except Exception as e:
                logger.warning(f"⚠ Failed to initialize circuit breakers: {e}")

            # 2.3 OpenPipe Integration (optional)
            if self._enable_openpipe and openpipe_manager:
                try:
                    self._openpipe_initialized = await openpipe_manager.initialize()
                    if self._openpipe_initialized:
                        logger.info("✓ OpenPipe integration initialized")
                    else:
                        logger.warning("⚠ OpenPipe initialization failed, continuing without")
                except Exception as e:
                    logger.warning(f"⚠ OpenPipe initialization error: {e}")
                    self._openpipe_initialized = False

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

            # 4. Models - placeholders, initialized in background
            self.services['embeddings'] = None
            self.services['vectorstore'] = None
            self.services['llm'] = None

            # CLAUDE STANDARD: Use TaskGroup for background initialization
            # This provides structured concurrency with guaranteed cleanup
            self._running = True
            async with anyio.create_task_group() as tg:
                self._cancel_scope = tg.cancel_scope
                tg.start_soon(self._background_init_models)
                # TaskGroup waits here until background task completes or is cancelled

            # 5. Business Services
            self.services['rag'] = RAGService(self.services.get('vectorstore'))
            
            # Wrap RAG service with OpenPipe if available
            if self._openpipe_initialized and openpipe_manager:
                self.services['rag'] = openpipe_manager.create_llm_wrapper(
                    self.services['rag'], "rag_service"
                )
                logger.info("✓ RAG Service initialized with OpenPipe")
            else:
                logger.info("✓ RAG Service initialized")

            self.services['voice'] = setup_voice_interface()
            logger.info("✓ Voice Interface initialized")

            self.services['research'] = get_research_agent()
            logger.info("✓ Research Agent initialized")

            self._initialized = True
            duration = time.time() - self._start_time
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
        
        CLAUDE STANDARD: Cancel via CancelScope for clean shutdown.
        """
        logger.info("Shutting down Xoe-NovAi services...")
        
        # Cancel background tasks
        self._running = False
        if self._cancel_scope:
            self._cancel_scope.cancel()
            self._cancel_scope = None

        # Deregister from Consul
        try:
            await consul_client.deregister_service(self._service_id)
        except Exception as e:
            logger.warning(f"⚠ Failed to deregister from Consul: {e}")

        # Stop research agent
        if 'research' in self.services:
            self.services['research'].stop_monitoring()
        
        # Shutdown OpenPipe
        if self._openpipe_initialized and openpipe_manager:
            await openpipe_manager.shutdown()
        
        # Shutdown observability
        if hasattr(observability, 'shutdown'):
            observability.shutdown()
            
        # Shutdown infrastructure
        await shutdown_dependencies()

        logger.info("Stack shutdown complete")

    def is_ready(self) -> bool:
        """Return True when background initialization has completed."""
        return self._ready

    async def _initialize_llm(self) -> Any:
        """
        Thread-safe lazy initialization of the LLM.
        
        CLAUDE STANDARD: Uses asyncio.Lock for thread safety.
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
                llm = await get_llm_async()
                
                # Wrap with OpenPipe if available
                if self._openpipe_initialized and openpipe_manager:
                    llm = openpipe_manager.create_llm_wrapper(llm, "llm_service")
                    logger.info("✓ LLM wrapped with OpenPipe")
                
                self._llm_cache = llm
                self.services['llm'] = self._llm_cache
                return self._llm_cache
            except Exception as e:
                logger.error(f"Failed to initialize LLM: {e}")
                raise

    async def _background_init_models(self):
        """
        Background task to initialize embeddings, vectorstore, and LLM.
        
        CLAUDE STANDARD: Runs in TaskGroup with cancellation support.
        """
        try:
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
                self.services['llm'] = self._llm_cache
                logger.info("Background: LLM primed and cached")
            except Exception as e:
                logger.warning(f"Background: LLM init failed: {e}")

        except anyio.get_cancelled_exc_class():
            logger.info("Background model initialization cancelled")
            raise
        finally:
            self._ready = True

    async def get_performance_report(self) -> Dict[str, Any]:
        """
        Get comprehensive performance report including OpenPipe metrics.
        """
        try:
            # Get OpenPipe performance report
            openpipe_report = {}
            if self._openpipe_initialized and openpipe_manager:
                openpipe_report = await openpipe_manager.get_performance_report()
            
            # Get system metrics
            system_metrics = {
                "memory_usage": self._get_memory_usage(),
                "active_sessions": self._get_active_sessions(),
                "cache_stats": self._get_cache_stats(),
                "uptime_seconds": time.time() - self._start_time if self._start_time else 0
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
        try:
            import psutil
            memory = psutil.virtual_memory()
            return {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_percent": memory.percent,
                "free_gb": round(memory.free / (1024**3), 2)
            }
        except ImportError:
            return {"status": "psutil_unavailable"}
    
    def _get_active_sessions(self) -> int:
        """Get number of active sessions."""
        return 0  # Placeholder
    
    def _get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics from Redis."""
        if not self.services.get('redis'):
            return {"status": "redis_unavailable"}
        
        try:
            redis = self.services['redis']
            info = redis.info('memory')
            return {
                "used_memory_human": info.get('used_memory_human', 'N/A'),
                "maxmemory_human": info.get('maxmemory_human', 'N/A'),
                "cache_hits": info.get('keyspace_hits', 0),
                "cache_misses": info.get('keyspace_misses', 0)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _assess_overall_health(
        self, 
        openpipe_report: Dict[str, Any], 
        system_metrics: Dict[str, Any]
    ) -> str:
        """Assess overall system health."""
        health_score = 100
        
        # Check OpenPipe integration status
        if openpipe_report.get("integration_status") == "active":
            pass  # Good
        elif self._enable_openpipe:
            health_score -= 10
        
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
        
        if health_score >= 90:
            return "excellent"
        elif health_score >= 75:
            return "good"
        elif health_score >= 60:
            return "fair"
        else:
            return "poor"


# Global orchestrator instance
orchestrator = ServiceOrchestrator()