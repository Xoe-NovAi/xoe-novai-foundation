"""
Xoe-NovAi Health Router
=======================
Endpoints for system health monitoring.
"""

import os
import psutil
import asyncio
import logging
from fastapi import APIRouter, Request
from ...schemas import HealthResponse
from ...core.config_loader import load_config
from ...core.circuit_breakers import get_circuit_breaker_status

logger = logging.getLogger(__name__)
CONFIG = load_config()
router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """
    Health check endpoint.
    """
    # Get memory
    memory_gb = psutil.virtual_memory().used / (1024 ** 3)
    
    # Get services from app state
    services = getattr(request.app.state, 'services', {})
    embeddings = services.get('embeddings')
    vectorstore = services.get('vectorstore')
    
    # Basic component checks
    components = {
        "embeddings": embeddings is not None,
        "vectorstore": vectorstore is not None,
        "llm": True, # Lazy loaded, assume OK for health
    }

    # Add circuit breaker status
    try:
        # get_circuit_breaker_status is a synchronous snapshot helper; run it in a thread
        breaker_status = await asyncio.to_thread(get_circuit_breaker_status)
        # breaker_status is a flat mapping: name -> {state, fail_count, ...}
        healthy = all(info.get('state') == 'closed' for info in breaker_status.values()) if isinstance(breaker_status, dict) else False
        components.update({
            "circuit_breakers_healthy": healthy
        })
    except Exception as e:
        logger.warning(f"Circuit breaker status check failed: {e}")
        components["circuit_breakers_healthy"] = False
    
    # Run healthcheck.py checks if available
    try:
        from ..healthcheck import run_health_checks
        ERROR_RECOVERY_ENABLED = os.getenv("ERROR_RECOVERY_ENABLED", "true").lower() == "true"
        
        if ERROR_RECOVERY_ENABLED:
            health_results = await asyncio.to_thread(
                run_health_checks,
                targets=['memory', 'redis', 'ryzen'],
                critical_only=False
            )
            
            for target, (success, message) in health_results.items():
                components[f"health_{target}"] = success
    except ImportError:
        pass
    
    # Determine status
    if memory_gb > CONFIG['performance']['memory_limit_gb']:
        status = "degraded"
    elif not components['embeddings']:
        status = "degraded"
    elif not components.get('health_memory', True):
        status = "degraded"
    elif not components['vectorstore']:
        status = "partial"
    else:
        status = "healthy"
    
    return HealthResponse(
        status=status,
        version=CONFIG['metadata']['stack_version'],
        memory_gb=round(memory_gb, 2),
        vectorstore_loaded=vectorstore is not None,
        components=components
    )
