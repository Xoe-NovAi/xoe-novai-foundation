"""
Xoe-NovAi API Exceptions
========================
Unified exception hierarchy for consistent error handling.
"""

from typing import Optional, Any, Dict
import time

class XNAiException(Exception):
    """Base exception for all Xoe-NovAi errors."""
    def __init__(
        self,
        message: str,
        error_code: str = "internal_error",
        http_status: int = 500,
        details: Optional[str] = None,
        recovery_suggestion: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.http_status = http_status
        self.details = details
        self.recovery_suggestion = recovery_suggestion
        self.timestamp = time.time()

class ModelNotFoundError(XNAiException):
    """Raised when an AI model file is missing or cannot be loaded."""
    def __init__(self, model_name: str, details: Optional[str] = None):
        super().__init__(
            message=f"Model not found: {model_name}",
            error_code="model_not_found",
            http_status=404,
            details=details,
            recovery_suggestion="Check model path configuration and ensure model files are downloaded."
        )

class TokenLimitError(XNAiException):
    """Raised when query exceeds token context limits."""
    def __init__(self, limit: int, current: int):
        super().__init__(
            message=f"Token limit exceeded: {current} > {limit}",
            error_code="token_limit_exceeded",
            http_status=400,
            recovery_suggestion="Try a shorter query or reduce context window size."
        )

class OfflineModeError(XNAiException):
    """Raised when an operation requiring internet is attempted in offline mode."""
    def __init__(self, operation: str):
        super().__init__(
            message=f"Operation '{operation}' not available in offline mode",
            error_code="offline_mode_restriction",
            http_status=503,
            recovery_suggestion="Enable online mode or use local alternative."
        )

class ResourceExhaustedError(XNAiException):
    """Raised when system is under critical memory pressure."""
    def __init__(self, resource: str = "memory"):
        super().__init__(
            message=f"System {resource} exhausted",
            error_code="resource_exhausted",
            http_status=503,
            recovery_suggestion="Please wait a few moments for resources to clear."
        )
