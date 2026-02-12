"""
Xoe-NovAi API Exceptions
========================
Unified exception hierarchy for consistent error handling.
"""

from typing import Optional, Any, Dict
import time
import hashlib

from ..schemas.errors import ErrorCategory

class XNAiException(Exception):
    """
    Unified base exception for all Xoe-NovAi errors.
    
    Design Principles:
    - Category-driven HTTP status mapping
    - Deterministic error codes for client parsing
    - Recovery suggestions for user guidance
    - Structured metadata for observability
    """
    
    # Category-to-HTTP status code mapping
    CATEGORY_TO_STATUS = {
        ErrorCategory.VALIDATION: 400,
        ErrorCategory.INPUT_SANITIZATION: 400,
        ErrorCategory.AUTHENTICATION: 401,
        ErrorCategory.AUTHORIZATION: 403,
        ErrorCategory.SECURITY_ERROR: 403,
        ErrorCategory.NOT_FOUND: 404,
        ErrorCategory.RATE_LIMITED: 429,
        ErrorCategory.INTERNAL_ERROR: 500,
        ErrorCategory.MODEL_ERROR: 500,
        ErrorCategory.AWQ_QUANTIZATION: 500,
        ErrorCategory.VULKAN_ACCELERATION: 500,
        ErrorCategory.NETWORK_ERROR: 500,
        ErrorCategory.CONFIGURATION_ERROR: 500,
        ErrorCategory.CIRCUIT_OPEN: 503,
        ErrorCategory.SERVICE_UNAVAILABLE: 503,
        ErrorCategory.VOICE_SERVICE: 503,
        ErrorCategory.TIMEOUT: 504,
        ErrorCategory.MEMORY_LIMIT: 507,
        ErrorCategory.RESOURCE_EXHAUSTED: 507,
    }
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        error_code: Optional[str] = None,
        http_status: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        recovery_suggestion: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize XNAiException with category-based structure.
        
        Args:
            message: Human-readable error message
            category: ErrorCategory enum value
            error_code: Custom error code (auto-generated if None)
            http_status: Override HTTP status code
            details: Structured error metadata (sanitized)
            recovery_suggestion: User-friendly recovery guidance
            cause: Original exception if exists
        """
        super().__init__(message)
        self.message = message
        self.category = category
        
        # Auto-derive HTTP status from category unless overridden
        self.http_status = http_status or self.CATEGORY_TO_STATUS.get(
            category, 500
        )
        
        # Generate deterministic error code if not provided
        self.error_code = error_code or self._generate_error_code(
            category, message
        )
        
        self.details = details or {}
        self.recovery_suggestion = recovery_suggestion
        self.cause = cause
        self.timestamp = time.time()
        
        # Set Python exception chaining if cause provided
        if cause is not None:
            self.__cause__ = cause
    
    def _generate_error_code(self, category: ErrorCategory, message: str) -> str:
        """
        Generate version-stable error code from category and message.
        
        Format: {category}_{short_hash}
        Example: validation_a3f2, circuit_open_b8c1
        
        This ensures consistency across versions - same error generates same code.
        """
        message_hash = hashlib.sha256(message.encode()).hexdigest()[:4]
        return f"{category.value}_{message_hash}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize exception for API responses."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "category": self.category.value,
            "timestamp": self.timestamp,
            "details": self.details,
            "recovery_suggestion": self.recovery_suggestion,
        }

# Standard exception subclasses for common scenarios

class ModelNotFoundError(XNAiException):
    """Raised when an AI model file is missing or cannot be loaded."""
    def __init__(self, model_name: str, details: Optional[str] = None):
        super().__init__(
            message=f"Model not found: {model_name}",
            category=ErrorCategory.NOT_FOUND,
            details={"model_name": model_name} if model_name else {},
            recovery_suggestion="Check model path configuration and ensure model files are downloaded."
        )

class TokenLimitError(XNAiException):
    """Raised when query exceeds token context limits."""
    def __init__(self, limit: int, current: int):
        super().__init__(
            message=f"Token limit exceeded: {current} > {limit}",
            category=ErrorCategory.VALIDATION,
            details={"limit": limit, "current": current},
            recovery_suggestion="Try a shorter query or reduce context window size."
        )

class OfflineModeError(XNAiException):
    """Raised when an operation requiring internet is attempted in offline mode."""
    def __init__(self, operation: str):
        super().__init__(
            message=f"Operation '{operation}' not available in offline mode",
            category=ErrorCategory.SERVICE_UNAVAILABLE,
            recovery_suggestion="Enable online mode or use local alternative."
        )

class ResourceExhaustedError(XNAiException):
    """Raised when system is under critical memory pressure."""
    def __init__(self, resource: str = "memory"):
        super().__init__(
            message=f"System {resource} exhausted",
            category=ErrorCategory.MEMORY_LIMIT,
            recovery_suggestion="Please wait a few moments for resources to clear."
        )
