#!/usr/bin/env python3
# ============================================================================
# Xoe-NovAi Phase 6 - Semantic Search REST API
# ============================================================================
# Purpose: FastAPI endpoints for semantic search on technical manuals
# Guide Reference: Phase 6 (Testing & Production Hardening)
# Last Updated: 2026-02-16
# Features:
#   - /search endpoint for semantic search queries
#   - /health endpoint for service health checks
#   - Pydantic request/response models
#   - XNAiException error handling
#   - Structured logging with trace_id/span_id
# ============================================================================

import logging
import time
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

try:
    from fastapi import FastAPI, HTTPException, Request, Depends
    from fastapi.responses import JSONResponse
    import numpy as np
    from langchain_core.documents import Document
except ImportError:
    # Graceful degradation for non-FastAPI environments
    FastAPI = None
    HTTPException = None
    Request = None
    Depends = None
    np = None

# Import XNAi conventions
try:
    from XNAi_rag_app.api.exceptions import XNAiException
    from XNAi_rag_app.schemas.errors import ErrorCategory, ErrorResponse
except ImportError:
    # Fallback exception class
    class XNAiException(Exception):
        def __init__(
            self,
            message: str,
            category: str = "internal_error",
            error_code: Optional[str] = None,
            http_status: int = 500,
            details: Optional[Dict[str, Any]] = None
        ):
            self.message = message
            self.category = category
            self.error_code = error_code or f"{category}_error"
            self.http_status = http_status
            self.details = details or {}
            self.timestamp = time.time()
            super().__init__(message)
    
    class ErrorResponse(BaseModel):
        error_code: str
        message: str
        category: str
        timestamp: float
        details: Optional[Dict[str, Any]] = None
        recovery_suggestion: Optional[str] = None
        request_id: Optional[str] = None


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class SemanticSearchRequest(BaseModel):
    """Request model for semantic search"""
    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Search query text"
    )
    top_k: int = Field(
        5,
        ge=1,
        le=100,
        description="Number of top results to return"
    )
    min_score: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score threshold"
    )
    alpha: float = Field(
        0.5,
        ge=0.0,
        le=1.0,
        description="Blend factor: 0=pure semantic, 1=pure lexical"
    )
    filters: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional metadata filters"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "query": "How to configure Python for machine learning?",
                "top_k": 5,
                "min_score": 0.5,
                "alpha": 0.5,
                "filters": {"source": "official_docs"}
            }
        }


class SearchResultItem(BaseModel):
    """Individual search result"""
    id: str = Field(..., description="Document ID")
    rank: int = Field(..., description="Result rank (1-based)")
    score: float = Field(..., description="Similarity score [0-1]")
    content: str = Field(..., description="Document content (truncated)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")


class SemanticSearchResponse(BaseModel):
    """Response model for semantic search"""
    request_id: str = Field(..., description="Unique request ID for tracing")
    query: str = Field(..., description="The search query")
    result_count: int = Field(..., description="Number of results returned")
    results: List[SearchResultItem] = Field(..., description="Search results")
    execution_time_ms: float = Field(..., description="Query execution time in milliseconds")
    timestamp: str = Field(..., description="Response timestamp (ISO 8601)")
    
    class Config:
        schema_extra = {
            "example": {
                "request_id": "req_123456",
                "query": "Python configuration",
                "result_count": 3,
                "results": [
                    {
                        "id": "doc1",
                        "rank": 1,
                        "score": 0.95,
                        "content": "How to set up Python...",
                        "metadata": {"source": "docs"}
                    }
                ],
                "execution_time_ms": 125.5,
                "timestamp": "2026-02-16T10:30:45.123456Z"
            }
        }


class HealthCheckResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status: 'healthy', 'degraded', 'unhealthy'")
    timestamp: str = Field(..., description="Check timestamp (ISO 8601)")
    version: str = Field(..., description="API version")
    dependencies: Dict[str, str] = Field(default_factory=dict, description="Dependency statuses")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2026-02-16T10:30:45.123456Z",
                "version": "0.1.0-phase6",
                "dependencies": {
                    "embeddings": "ready",
                    "index": "ready"
                }
            }
        }


# ============================================================================
# LOGGING & TRACING
# ============================================================================

class RequestContext:
    """Context for request tracing"""
    def __init__(self, request_id: Optional[str] = None):
        self.request_id = request_id or f"req_{uuid.uuid4().hex[:12]}"
        self.span_id = f"span_{uuid.uuid4().hex[:12]}"
        self.timestamp = datetime.utcnow().isoformat()
        self.start_time = time.time()
    
    def get_elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds"""
        return (time.time() - self.start_time) * 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "request_id": self.request_id,
            "span_id": self.span_id,
            "timestamp": self.timestamp,
            "elapsed_ms": self.get_elapsed_ms()
        }


def create_logger(name: str) -> logging.Logger:
    """Create a logger with XNAi conventions"""
    logger = logging.getLogger(name)
    
    # Add default handlers if not present
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger


logger = create_logger(__name__)


# ============================================================================
# API IMPLEMENTATION
# ============================================================================

class SemanticSearchAPI:
    """Semantic search API implementation"""
    
    def __init__(self):
        """Initialize the API"""
        self.app = None
        self.embeddings = None
        self.documents = None
        self.logger = logger
        
        if FastAPI is not None:
            self._setup_fastapi()
    
    def _setup_fastapi(self):
        """Setup FastAPI application"""
        self.app = FastAPI(
            title="Xoe-NovAi Semantic Search API",
            description="Phase 6 - Testing & Production Hardening",
            version="0.1.0-phase6"
        )
        
        # Add routes
        self.app.get("/health")(self.health_check)
        self.app.post("/search")(self.search)
        
        # Add exception handler
        self.app.add_exception_handler(
            XNAiException,
            self._xnai_exception_handler
        )
        
        # Add middleware for request context
        @self.app.middleware("http")
        async def add_request_context(request: Request, call_next):
            request_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:12]}"
            request.state.request_id = request_id
            request.state.span_id = f"span_{uuid.uuid4().hex[:12]}"
            
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
    
    async def _xnai_exception_handler(self, request: Request, exc: XNAiException):
        """Handle XNAiException with proper formatting"""
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        error_response = ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            category=exc.category if isinstance(exc.category, str) else exc.category.value,
            timestamp=exc.timestamp,
            details=exc.details,
            recovery_suggestion=getattr(exc, 'recovery_suggestion', None),
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=exc.http_status,
            content=error_response.dict(),
            headers={"X-Request-ID": request_id}
        )
    
    async def health_check(self) -> HealthCheckResponse:
        """Health check endpoint"""
        dependencies = {
            "embeddings": "ready" if self.embeddings is not None else "not_initialized",
            "index": "ready" if self.documents is not None else "not_initialized"
        }
        
        # Determine overall status
        if all(v == "ready" for v in dependencies.values()):
            status = "healthy"
        elif any(v == "ready" for v in dependencies.values()):
            status = "degraded"
        else:
            status = "unhealthy"
        
        return HealthCheckResponse(
            status=status,
            timestamp=datetime.utcnow().isoformat() + "Z",
            version="0.1.0-phase6",
            dependencies=dependencies
        )
    
    async def search(self, request: SemanticSearchRequest) -> SemanticSearchResponse:
        """Semantic search endpoint"""
        try:
            # Create request context
            context = RequestContext()
            
            # Log request
            self.logger.info(
                f"Search request: query={request.query[:50]}, top_k={request.top_k}",
                extra=context.to_dict()
            )
            
            # Validate request
            if not request.query.strip():
                raise XNAiException(
                    message="Query cannot be empty",
                    category="validation_error",
                    http_status=400,
                    details={"field": "query"}
                )
            
            # Validate dependencies
            if self.embeddings is None or self.documents is None:
                raise XNAiException(
                    message="Search service not initialized",
                    category="service_unavailable",
                    http_status=503,
                    recovery_suggestion="Please try again in a few moments"
                )
            
            # Perform search (simplified implementation)
            results = self._perform_search(
                query=request.query,
                top_k=request.top_k,
                min_score=request.min_score,
                alpha=request.alpha,
                filters=request.filters
            )
            
            # Format results
            formatted_results = []
            for rank, (doc, score) in enumerate(results, 1):
                formatted_results.append(
                    SearchResultItem(
                        id=doc.metadata.get('id', f'doc_{rank}'),
                        rank=rank,
                        score=round(float(score), 4),
                        content=doc.page_content[:200],
                        metadata={k: v for k, v in (doc.metadata or {}).items()
                                 if k != 'id'}
                    )
                )
            
            # Log success
            self.logger.info(
                f"Search completed: returned {len(formatted_results)} results",
                extra=context.to_dict()
            )
            
            # Return response
            return SemanticSearchResponse(
                request_id=context.request_id,
                query=request.query,
                result_count=len(formatted_results),
                results=formatted_results,
                execution_time_ms=round(context.get_elapsed_ms(), 2),
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
        
        except XNAiException:
            # Re-raise XNAi exceptions
            raise
        except Exception as e:
            # Wrap unexpected exceptions
            self.logger.error(f"Unexpected error during search: {str(e)}")
            raise XNAiException(
                message="An unexpected error occurred during search",
                category="internal_error",
                http_status=500,
                details={"error_type": type(e).__name__}
            )
    
    def _perform_search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0,
        alpha: float = 0.5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[tuple]:
        """
        Perform actual search (simplified implementation)
        
        In production, this would use embeddings and vector similarity
        """
        if not self.documents:
            return []
        
        # Simulate search by returning documents in order
        results = []
        for i, doc in enumerate(self.documents[:top_k]):
            # Simulate similarity score
            score = 0.95 - (i * 0.1)
            if score >= min_score:
                results.append((doc, score))
        
        return results
    
    def initialize(
        self,
        documents: Optional[List[Document]] = None,
        embeddings: Optional[np.ndarray] = None
    ):
        """Initialize the API with documents and embeddings"""
        self.documents = documents or []
        self.embeddings = embeddings
        self.logger.info(
            f"API initialized with {len(self.documents)} documents"
        )
    
    def get_app(self):
        """Get FastAPI application instance"""
        return self.app


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_semantic_search_api() -> SemanticSearchAPI:
    """Factory function to create and configure API"""
    api = SemanticSearchAPI()
    return api


# ============================================================================
# STANDALONE USAGE
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Create API
    api = create_semantic_search_api()
    
    # Check if FastAPI is available
    if api.get_app() is None:
        print("FastAPI not available. Install with: pip install fastapi uvicorn")
        sys.exit(1)
    
    # Run server
    import uvicorn
    
    print("Starting Xoe-NovAi Semantic Search API on http://localhost:8000")
    print("API docs: http://localhost:8000/docs")
    print("ReDoc: http://localhost:8000/redoc")
    
    uvicorn.run(
        api.get_app(),
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
