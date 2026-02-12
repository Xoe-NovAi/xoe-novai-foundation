"""
Xoe-NovAi Error Schemas
=======================
Standardized error models and categories.
"""

from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

class ErrorCategory(str, Enum):
    """Comprehensive error categorization for unified handling."""
    
    # Client Errors (4xx)
    VALIDATION = "validation"                      # 400
    INPUT_SANITIZATION = "input_sanitization"      # 400
    AUTHENTICATION = "authentication"              # 401
    AUTHORIZATION = "authorization"                # 403
    NOT_FOUND = "not_found"                        # 404
    RATE_LIMITED = "rate_limited"                  # 429
    
    # Server Errors (5xx)
    INTERNAL_ERROR = "internal_error"              # 500
    SERVICE_UNAVAILABLE = "service_unavailable"    # 503
    TIMEOUT = "timeout"                            # 504
    
    # Domain-Specific
    AWQ_QUANTIZATION = "awq_quantization"          # 500
    VULKAN_ACCELERATION = "vulkan_acceleration"    # 500
    CIRCUIT_OPEN = "circuit_open"                  # 503
    VOICE_SERVICE = "voice_service"                # 503
    MODEL_ERROR = "model_error"                    # 500
    MEMORY_LIMIT = "memory_limit"                  # 507
    
    # Security
    SECURITY_ERROR = "security_error"              # 403
    
    # Legacy (for backward compatibility)
    NETWORK_ERROR = "network_error"                # 500
    CONFIGURATION_ERROR = "configuration_error"    # 500
    RESOURCE_EXHAUSTED = "resource_exhausted"      # 507

class ErrorResponse(BaseModel):
    """
    Standardized error response model.
    
    Used in all API error responses to ensure consistency
    and prevent information leakage.
    """
    error_code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    category: str = Field(..., description="Error category")
    timestamp: float = Field(..., description="Unix timestamp")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Structured error details")
    recovery_suggestion: Optional[str] = Field(default=None, description="Recovery guidance")
    request_id: Optional[str] = Field(default=None, description="Request correlation ID")
