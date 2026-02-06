"""
Xoe-NovAi API Entrypoint
=======================
Initializes FastAPI app, includes routers, and manages service lifecycle.
"""

from fastapi import FastAPI
from XNAi_rag_app.api.routers import router as api_router
from XNAi_rag_app.core.services_init import ServiceOrchestrator
import logging

logger = logging.getLogger(__name__)

# Global LLM instance (lazy loading with circuit breaker)
llm = None

async def load_llm_with_circuit_breaker():
    """
    Load LLM with circuit breaker protection.
    This function should be called when LLM is needed.
    """
    global llm
    if llm is None:
        # Import here to avoid circular imports
        from XNAi_rag_app.core.services_init import ServiceOrchestrator
        orchestrator = ServiceOrchestrator()
        # Get services from the global orchestrator (already initialized during startup)
        services = orchestrator.services
        llm = services.get('llm')
        
        # If LLM is not in services, try to get it from dependencies directly
        if llm is None:
            try:
                from XNAi_rag_app.core.dependencies import get_llm_async
                llm = await get_llm_async()
            except Exception as e:
                raise RuntimeError(f"LLM not available - {str(e)}")
    return llm

# Instantiate orchestrator
orchestrator = ServiceOrchestrator()

# Create FastAPI app
app = FastAPI(
    title="Xoe-NovAi API",
    description="Foundation RAG API for Xoe-NovAi stack.",
    version="0.1.0-alpha"
)

# Include all API routers
app.include_router(api_router)

# Lifespan event handlers for service orchestration
@app.on_event("startup")
async def on_startup():
    logger.info("[Startup] Initializing all services via ServiceOrchestrator...")
    services = await orchestrator.initialize_all()
    app.state.services = services
    logger.info("[Startup] All services initialized.")

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("[Shutdown] Shutting down all services via ServiceOrchestrator...")
    await orchestrator.shutdown_all()
    logger.info("[Shutdown] All services shut down.")
