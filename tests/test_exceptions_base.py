"""
Base Exception Hierarchy Tests
==============================
Verifies core XNAiException functionality and category mapping.
"""

import pytest
import time
import sys
import os
from pathlib import Path

# Add app root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

# Now we can import directly
from XNAi_rag_app.api.exceptions import (
    XNAiException,
    ModelNotFoundError,
    TokenLimitError,
    OfflineModeError,
    ResourceExhaustedError
)
from XNAi_rag_app.schemas.errors import ErrorCategory


class TestXNAiExceptionBase:
    """Test XNAiException base class."""
    
    def test_xnai_exception_category_mapping(self):
        """Verify all categories map to correct HTTP status."""
        test_cases = [
            (ErrorCategory.VALIDATION, 400),
            (ErrorCategory.INPUT_SANITIZATION, 400),
            (ErrorCategory.AUTHENTICATION, 401),
            (ErrorCategory.AUTHORIZATION, 403),
            (ErrorCategory.NOT_FOUND, 404),
            (ErrorCategory.RATE_LIMITED, 429),
            (ErrorCategory.INTERNAL_ERROR, 500),
            (ErrorCategory.MODEL_ERROR, 500),
            (ErrorCategory.CIRCUIT_OPEN, 503),
            (ErrorCategory.SERVICE_UNAVAILABLE, 503),
            (ErrorCategory.VOICE_SERVICE, 503),
            (ErrorCategory.TIMEOUT, 504),
            (ErrorCategory.MEMORY_LIMIT, 507),
        ]
        
        for category, expected_status in test_cases:
            exc = XNAiException(
                message="Test error",
                category=category
            )
            assert exc.http_status == expected_status, \
                f"{category} should map to {expected_status}, got {exc.http_status}"
    
    def test_error_code_determinism(self):
        """Verify same message generates same error code."""
        exc1 = XNAiException(
            message="Model not found",
            category=ErrorCategory.NOT_FOUND
        )
        exc2 = XNAiException(
            message="Model not found",
            category=ErrorCategory.NOT_FOUND
        )
        assert exc1.error_code == exc2.error_code, \
            "Same message should generate same error code"
    
    def test_error_code_determinism_different_categories(self):
        """Verify different categories generate different error codes."""
        exc1 = XNAiException(
            message="Test",
            category=ErrorCategory.VALIDATION
        )
        exc2 = XNAiException(
            message="Test",
            category=ErrorCategory.SERVICE_UNAVAILABLE
        )
        assert exc1.error_code != exc2.error_code, \
            "Different categories should generate different codes"
    
    def test_error_serialization(self):
        """Verify exception serializes correctly."""
        exc = XNAiException(
            message="Test error",
            category=ErrorCategory.VALIDATION,
            details={"field": "query"},
            recovery_suggestion="Fix input"
        )
        
        data = exc.to_dict()
        assert data["message"] == "Test error"
        assert data["category"] == "validation"
        assert data["details"]["field"] == "query"
        assert data["recovery_suggestion"] == "Fix input"
        assert "error_code" in data
        assert "timestamp" in data
    
    def test_custom_error_code(self):
        """Verify custom error code is preserved."""
        exc = XNAiException(
            message="Test",
            category=ErrorCategory.VALIDATION,
            error_code="custom_error_xyz"
        )
        assert exc.error_code == "custom_error_xyz"
    
    def test_custom_http_status(self):
        """Verify custom HTTP status overrides category default."""
        exc = XNAiException(
            message="Test",
            category=ErrorCategory.VALIDATION,
            http_status=418  # I'm a teapot
        )
        assert exc.http_status == 418
    
    def test_timestamp_precision(self):
        """Verify timestamp is set accurately."""
        before = time.time()
        exc = XNAiException(
            message="Test",
            category=ErrorCategory.INTERNAL_ERROR
        )
        after = time.time()
        
        assert before <= exc.timestamp <= after
    
    def test_exception_cause_chain(self):
        """Verify cause exception is stored."""
        original_error = ValueError("Original error")
        exc = XNAiException(
            message="Wrapped error",
            category=ErrorCategory.INTERNAL_ERROR,
            cause=original_error
        )
        assert exc.cause is original_error


class TestModelNotFoundError:
    """Test ModelNotFoundError subclass."""
    
    def test_model_not_found_creation(self):
        """Verify ModelNotFoundError creates correctly."""
        exc = ModelNotFoundError(model_name="llama-3.2-1b")
        
        assert isinstance(exc, XNAiException)
        assert exc.category == ErrorCategory.NOT_FOUND
        assert exc.http_status == 404
        assert "llama-3.2-1b" in exc.message
    
    def test_model_not_found_recovery_suggestion(self):
        """Verify recovery suggestion is set."""
        exc = ModelNotFoundError(model_name="test-model")
        assert exc.recovery_suggestion is not None
        assert "Check model path" in exc.recovery_suggestion


class TestTokenLimitError:
    """Test TokenLimitError subclass."""
    
    def test_token_limit_error_creation(self):
        """Verify TokenLimitError creates correctly."""
        exc = TokenLimitError(limit=2048, current=3000)
        
        assert isinstance(exc, XNAiException)
        assert exc.category == ErrorCategory.VALIDATION
        assert exc.http_status == 400
        assert "3000" in exc.message
        assert "2048" in exc.message
    
    def test_token_limit_details(self):
        """Verify token limit details are included."""
        exc = TokenLimitError(limit=512, current=1024)
        assert exc.details["limit"] == 512
        assert exc.details["current"] == 1024


class TestOfflineModeError:
    """Test OfflineModeError subclass."""
    
    def test_offline_mode_error_creation(self):
        """Verify OfflineModeError creates correctly."""
        exc = OfflineModeError(operation="fetch_updates")
        
        assert isinstance(exc, XNAiException)
        assert exc.category == ErrorCategory.SERVICE_UNAVAILABLE
        assert exc.http_status == 503
        assert "fetch_updates" in exc.message


class TestResourceExhaustedError:
    """Test ResourceExhaustedError subclass."""
    
    def test_resource_exhausted_error_creation(self):
        """Verify ResourceExhaustedError creates correctly."""
        exc = ResourceExhaustedError(resource="memory")
        
        assert isinstance(exc, XNAiException)
        assert exc.category == ErrorCategory.MEMORY_LIMIT
        assert exc.http_status == 507
        assert "memory" in exc.message
