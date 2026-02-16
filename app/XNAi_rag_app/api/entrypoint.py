"""
Xoe-NovAi API Entrypoint
=======================
Initializes FastAPI app, includes routers, and manages service lifecycle.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from .routers import router as api_router
from .middleware import query_transaction_log_middleware
from ..core.services_init import ServiceOrchestrator
from ..core.degradation import degradation_manager
from .exceptions import XNAiException
from ..schemas.responses import ErrorResponse
from ..schemas.errors import ErrorCategory
import logging
import uuid
import time

try:
    from prometheus_fastapi_instrumentator import Instrumentator
    from prometheus_client import Counter, Histogram
    PROMETHEUS_AVAILABLE = True
    vector_lookup_latency = Histogram(
        'vector_lookup_latency_seconds',
        'Latency of vector search operations',
        ['source']
    )
except ImportError:
    PROMETHEUS_AVAILABLE = False
    vector_lookup_latency = None

logger = logging.getLogger(__name__)

# Global LLM instance (lazy loading with circuit breaker)
llm = None

async def load_llm_with_circuit_breaker():
    """
    Load LLM with circuit breaker protection.
    Uses the ServiceOrchestrator for thread-safe initialization.
    """
    global llm
    if llm is None:
        # Get LLM from orchestrator (handles locking and caching internally)
        llm = await orchestrator._initialize_llm()
        
    if llm is None:
        raise RuntimeError("LLM not available - initialization failed")
        
    return llm

# Instantiate orchestrator
orchestrator = ServiceOrchestrator()

# Create FastAPI app
app = FastAPI(
    title="Xoe-NovAi API",
    description="Foundation RAG API for Xoe-NovAi stack.",
    version="0.1.0-alpha"
)

# Initialize Prometheus instrumentation (optional)
if PROMETHEUS_AVAILABLE:
    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app, endpoint="/metrics")
else:
    logger.info("Prometheus not available - metrics disabled")

# Include all API routers
app.include_router(api_router)

# ============================================================================
# Global Exception Handlers
# ============================================================================

def _generate_request_id() -> str:
    """Generate a unique request ID for correlation."""
    return f"req_{uuid.uuid4()}"

def _build_error_response(
    request_id: str,
    error_code: str,
    message: str,
    category_str: str,
    http_status: int,
    details: dict = None,
    recovery_suggestion: str = None,
) -> dict:
    """Build standardized error response dict."""
    from datetime import datetime
    return {
        "error_code": error_code,
        "message": message,
        "category": category_str,
        "http_status": http_status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "details": details,
        "recovery_suggestion": recovery_suggestion,
        "request_id": request_id,
    }

@app.exception_handler(XNAiException)
async def xnai_exception_handler(request: Request, exc: XNAiException):
    """Handle all XNAiException instances with structured response."""
    request_id = request.state.request_id if hasattr(request.state, "request_id") else _generate_request_id()
    
    logger.warning(
        f"[{request_id}] XNAiException: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "category": exc.category.value,
            "http_status": exc.http_status,
            "details": exc.details,
        }
    )
    
    error_dict = _build_error_response(
        request_id=request_id,
        error_code=exc.error_code,
        message=exc.message,
        category_str=exc.category.value,
        http_status=exc.http_status,
        details=exc.details,
        recovery_suggestion=exc.recovery_suggestion,
    )
    
    return JSONResponse(
        status_code=exc.http_status,
        content=error_dict,
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert Pydantic validation errors to VALIDATION category errors."""
    request_id = request.state.request_id if hasattr(request.state, "request_id") else _generate_request_id()
    
    # Extract validation error details
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    field = ".".join(str(loc) for loc in first_error.get("loc", []))
    error_message = first_error.get("msg", "Validation error")
    
    logger.warning(
        f"[{request_id}] RequestValidationError: {field} - {error_message}",
        extra={
            "category": "validation",
            "http_status": 400,
            "errors": errors,
        }
    )
    
    error_dict = _build_error_response(
        request_id=request_id,
        error_code=f"{ErrorCategory.VALIDATION.value}_validation",
        message=f"Request validation failed: {error_message}" + (f" (field: {field})" if field else ""),
        category_str=ErrorCategory.VALIDATION.value,
        http_status=400,
        details={"validation_errors": [{"field": str(e["loc"]), "message": e["msg"]} for e in errors]},
        recovery_suggestion="Check your request format and ensure all required fields are present and valid.",
    )
    
    return JSONResponse(
        status_code=400,
        content=error_dict,
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions from Starlette."""
    request_id = request.state.request_id if hasattr(request.state, "request_id") else _generate_request_id()
    
    # Map HTTP status codes to error categories
    status_to_category = {
        401: ErrorCategory.AUTHENTICATION,
        403: ErrorCategory.AUTHORIZATION,
        404: ErrorCategory.NOT_FOUND,
        429: ErrorCategory.RATE_LIMITED,
        503: ErrorCategory.SERVICE_UNAVAILABLE,
        504: ErrorCategory.TIMEOUT,
    }
    
    category = status_to_category.get(exc.status_code, ErrorCategory.INTERNAL_ERROR)
    
    logger.warning(
        f"[{request_id}] HTTP {exc.status_code}: {exc.detail}",
        extra={
            "category": category.value,
            "http_status": exc.status_code,
        }
    )
    
    error_dict = _build_error_response(
        request_id=request_id,
        error_code=f"{category.value}_{exc.status_code}",
        message=str(exc.detail) if exc.detail else f"HTTP {exc.status_code} error",
        category_str=category.value,
        http_status=exc.status_code,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_dict,
    )

@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    """Middleware to add request ID to each request for correlation."""
    request_id = _generate_request_id()
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response

@app.middleware("http")
async def query_txn_middleware_wrapper(request: Request, call_next):
    return await query_transaction_log_middleware(request, call_next)


@app.on_event("startup")
async def on_startup():
    logger.info("[Startup] Initializing all services via ServiceOrchestrator...")
    services = await orchestrator.initialize_all()
    app.state.services = services
    
    # Start degradation monitor
    await degradation_manager.start_monitoring()
    
    logger.info("[Startup] All services initialized.")

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("[Shutdown] Shutting down all services via ServiceOrchestrator...")
    
    # Stop degradation monitor
    await degradation_manager.stop_monitoring()
    
    await orchestrator.shutdown_all()
    logger.info("[Shutdown] All services shut down.")