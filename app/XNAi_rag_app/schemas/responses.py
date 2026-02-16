"""
Xoe-NovAi Response Schemas
==========================
Pydantic models for API responses.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ErrorResponse(BaseModel):
    """
    Standardized error response for all API errors.
    
    All XNAiException instances are serialized to this format.
    """
    error_code: str = Field(..., description="Unique error identifier (category_hash)")
    message: str = Field(..., description="Human-readable error message")
    category: str = Field(..., description="Error category value (e.g., 'voice_service', 'validation')")
    http_status: int = Field(..., description="HTTP status code")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When error occurred (ISO 8601)")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Subsystem-specific context")
    recovery_suggestion: Optional[str] = Field(None, description="User-facing recovery guidance")
    request_id: Optional[str] = Field(None, description="Request correlation ID for logging")

    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "voice_service_a123",
                "message": "Failed to process audio stream",
                "category": "voice_service",
                "http_status": 503,
                "timestamp": "2026-02-11T10:30:45.123456Z",
                "details": {"cause_code": "stt_circuit_open", "component": "whisper"},
                "recovery_suggestion": "The speech-to-text service is temporarily unavailable. Please retry in 5 seconds.",
                "request_id": "req_550e8400-e29b-41d4-a716-446655440000"
            }
        }

class SSEErrorMessage(BaseModel):
    """
    Error message for Server-Sent Events (streaming) responses.
    
    Used when errors occur during streaming operations.
    """
    event: str = Field("error", description="Always 'error' for error messages")
    error_code: str = Field(..., description="Unique error identifier")
    message: str = Field(..., description="Error message")
    recovery_suggestion: Optional[str] = Field(None, description="Recovery guidance")
    request_id: Optional[str] = Field(None, description="Request correlation ID")

    class Config:
        json_schema_extra = {
            "example": {
                "event": "error",
                "error_code": "timeout_b456",
                "message": "Request exceeded time limit",
                "recovery_suggestion": "Try with a simpler query or shorter context window",
                "request_id": "req_550e8400-e29b-41d4-a716-446655440000"
            }
        }

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]

class QueryResponse(BaseModel):
    """
    Query response model.
    """
    response: str = Field(..., description="Generated response")
    sources: List[str] = Field(default_factory=list, description="RAG sources used")
    tokens_generated: Optional[int] = Field(None, description="Number of tokens generated")
    duration_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    token_rate_tps: Optional[float] = Field(None, description="Tokens per second")

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Health status: healthy, degraded, or partial")
    version: str = Field(..., description="Stack version")
    memory_gb: float = Field(..., description="Current memory usage in GB")
    vectorstore_loaded: bool = Field(..., description="Whether vectorstore is available")
    components: Dict[str, Any] = Field(..., description="Component status map")
