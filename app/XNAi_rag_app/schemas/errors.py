"""
Xoe-NovAi Error Schemas
=======================
Standardized error models and categories.
"""

from typing import Optional
from pydantic import BaseModel, Field

class ErrorCategory:
    """Standardized error categories for consistent classification."""
    VALIDATION = "validation_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    NETWORK_ERROR = "network_error"
    CONFIGURATION_ERROR = "configuration_error"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    SECURITY_ERROR = "security_error"
    INTERNAL_ERROR = "internal_error"

class ErrorResponse(BaseModel):
    """Standardized error response model."""
    error_code: str
    message: str
    timestamp: float
    details: Optional[str] = None
    recovery_suggestion: Optional[str] = None
