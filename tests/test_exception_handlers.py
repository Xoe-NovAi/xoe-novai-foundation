"""
Tests for global exception handlers in api/entrypoint.py

Tests validate that:
1. XNAiException instances are serialized to ErrorResponse format
2. Pydantic validation errors are converted to VALIDATION category
3. HTTP exceptions are wrapped with proper categories
4. Request IDs are generated and tracked correctly
5. All responses contain required fields: error_code, message, category, http_status, timestamp, request_id
"""

import pytest
import json
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel, Field, validator

# Mock the imports to avoid circular dependencies
import sys
from unittest.mock import MagicMock

# Import from the API module
from app.XNAi_rag_app.api.exceptions import XNAiException
from app.XNAi_rag_app.schemas.errors import ErrorCategory
from app.XNAi_rag_app.schemas.responses import ErrorResponse, SSEErrorMessage
from app.XNAi_rag_app.core.circuit_breakers import CircuitBreakerError
from app.XNAi_rag_app.services.voice.exceptions import STTError, TTSError


# Test request models
class TestQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    max_tokens: int = Field(512, ge=1, le=2048)


# Create a minimal test app with exception handlers
test_app = FastAPI()

# Copy the exception handler registration logic from entrypoint
import uuid
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)



def _generate_request_id_test() -> str:
    """Generate a unique request ID for correlation."""
    return f"req_{uuid.uuid4()}"


def _build_error_response_test(
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


@test_app.exception_handler(XNAiException)
async def xnai_exception_handler(request: Request, exc: XNAiException):
    """Handle all XNAiException instances with structured response."""
    request_id = request.state.request_id if hasattr(request.state, "request_id") else _generate_request_id_test()
    
    error_dict = _build_error_response_test(
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


@test_app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert Pydantic validation errors to VALIDATION category errors."""
    request_id = request.state.request_id if hasattr(request.state, "request_id") else _generate_request_id_test()
    
    # Extract validation error details
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    field = ".".join(str(loc) for loc in first_error.get("loc", []))
    error_message = first_error.get("msg", "Validation error")
    
    error_dict = _build_error_response_test(
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


@test_app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions from Starlette."""
    request_id = request.state.request_id if hasattr(request.state, "request_id") else _generate_request_id_test()
    
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
    
    error_dict = _build_error_response_test(
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


@test_app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    """Middleware to add request ID to each request for correlation."""
    request_id = _generate_request_id_test()
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response


# Test endpoints
@test_app.post("/test/voice-error")
async def voice_error_endpoint():
    """Endpoint that raises a voice service error."""
    raise STTError(
        message="Failed to process audio",
        cause_code="stt_circuit_open",
        component="whisper"
    )


@test_app.post("/test/circuit-breaker-error")
async def circuit_breaker_error_endpoint():
    """Endpoint that raises a circuit breaker error."""
    raise CircuitBreakerError(
        service_name="test_service",
        failure_count=5,
        retry_after=30
    )


@test_app.post("/test/validation-error", response_model=TestQueryRequest)
async def validation_error_endpoint(request: TestQueryRequest):
    """Endpoint with Pydantic validation."""
    return request


@test_app.post("/test/xnai-error")
async def xnai_error_endpoint():
    """Endpoint that raises a generic XNAiException."""
    raise XNAiException(
        message="Something went wrong",
        category=ErrorCategory.INTERNAL_ERROR,
        recovery_suggestion="Please try again later"
    )


@test_app.get("/test/not-found")
async def not_found_endpoint():
    """Endpoint that raises HTTP 404."""
    raise StarletteHTTPException(status_code=404, detail="Resource not found")


@test_app.get("/test/unauthorized")
async def unauthorized_endpoint():
    """Endpoint that raises HTTP 401."""
    raise StarletteHTTPException(status_code=401, detail="Authentication required")


# Tests
class TestXNAiExceptionHandler:
    """Tests for XNAiException handler."""
    
    def test_xnai_exception_serialization(self):
        """XNAiException should be serialized to structured error response."""
        client = TestClient(test_app)
        response = client.post("/test/xnai-error")
        
        assert response.status_code == 500
        data = response.json()
        
        # Verify all required fields
        assert "error_code" in data
        assert "message" in data
        assert data["message"] == "Something went wrong"
        assert "category" in data
        assert data["category"] == "internal_error"
        assert "http_status" in data
        assert data["http_status"] == 500
        assert "timestamp" in data
        assert "recovery_suggestion" in data
        assert data["recovery_suggestion"] == "Please try again later"
        assert "request_id" in data
        assert data["request_id"].startswith("req_")
    
    def test_voice_error_serialization(self):
        """Voice service error should be serialized with cause_code details."""
        client = TestClient(test_app)
        response = client.post("/test/voice-error")
        
        assert response.status_code == 503
        data = response.json()
        
        assert data["category"] == "voice_service"
        assert data["http_status"] == 503
        assert data["message"] == "Failed to process audio"
        assert "details" in data
        assert data["details"]["cause_code"] == "stt_circuit_open"
        assert data["details"]["component"] == "stt"  # STTError sets component to "stt"
        assert "recovery_suggestion" in data
    
    def test_circuit_breaker_error_serialization(self):
        """Circuit breaker error should include failure context."""
        client = TestClient(test_app)
        response = client.post("/test/circuit-breaker-error")
        
        assert response.status_code == 503
        data = response.json()
        
        assert data["category"] == "circuit_open"
        assert "details" in data
        assert data["details"]["service_name"] == "test_service"
        assert data["details"]["failure_count"] == 5
        assert data["details"]["retry_after_seconds"] == 30


class TestValidationErrorHandler:
    """Tests for Pydantic RequestValidationError handler."""
    
    def test_missing_required_field(self):
        """Missing required field should return 400 with VALIDATION category."""
        client = TestClient(test_app)
        response = client.post("/test/validation-error", json={})
        
        assert response.status_code == 400
        data = response.json()
        
        assert data["category"] == "validation"
        assert data["http_status"] == 400
        assert "validation_errors" in data["details"]
        assert len(data["details"]["validation_errors"]) > 0
        assert "query" in data["details"]["validation_errors"][0]["field"]
    
    def test_invalid_field_type(self):
        """Invalid field type should return validation error."""
        client = TestClient(test_app)
        response = client.post(
            "/test/validation-error",
            json={"query": "test", "max_tokens": "invalid"}
        )
        
        assert response.status_code == 400
        data = response.json()
        
        assert data["category"] == "validation"
        assert "max_tokens" in data["details"]["validation_errors"][0]["field"]
    
    def test_field_too_long(self):
        """Field exceeding max length should return validation error."""
        client = TestClient(test_app)
        response = client.post(
            "/test/validation-error",
            json={"query": "x" * 2001, "max_tokens": 512}
        )
        
        assert response.status_code == 400
        data = response.json()
        
        assert data["category"] == "validation"
        assert "validation_errors" in data["details"]


class TestHTTPExceptionHandler:
    """Tests for HTTP exception handler."""
    
    def test_unauthorized_exception(self):
        """HTTP 401 should map to AUTHENTICATION category."""
        client = TestClient(test_app)
        response = client.get("/test/unauthorized")
        
        assert response.status_code == 401
        data = response.json()
        
        assert data["category"] == "authentication"
        assert data["http_status"] == 401
        assert data["message"] == "Authentication required"
    
    def test_not_found_exception(self):
        """HTTP 404 should map to NOT_FOUND category."""
        client = TestClient(test_app)
        response = client.get("/test/not-found")
        
        assert response.status_code == 404
        data = response.json()
        
        assert data["category"] == "not_found"
        assert data["http_status"] == 404
        assert data["message"] == "Resource not found"


class TestRequestIDCorrelation:
    """Tests for request ID generation and correlation."""
    
    def test_request_id_in_response(self):
        """All error responses should include request_id."""
        client = TestClient(test_app)
        response = client.post("/test/xnai-error")
        
        assert response.status_code == 500
        data = response.json()
        
        assert "request_id" in data
        assert data["request_id"].startswith("req_")
    
    def test_request_id_in_headers(self):
        """Request ID should be present in response headers."""
        client = TestClient(test_app)
        response = client.post("/test/xnai-error")
        
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Request-ID"].startswith("req_")
    
    def test_request_id_matches_in_body_and_headers(self):
        """Request ID in body should match header."""
        client = TestClient(test_app)
        response = client.post("/test/xnai-error")
        
        data = response.json()
        header_id = response.headers["X-Request-ID"]
        
        assert data["request_id"] == header_id


class TestTimestampFormat:
    """Tests for error timestamp format."""
    
    def test_timestamp_iso_8601_format(self):
        """Timestamp should be in ISO 8601 format."""
        client = TestClient(test_app)
        response = client.post("/test/xnai-error")
        
        data = response.json()
        timestamp_str = data["timestamp"]
        
        # Should end with 'Z' for UTC
        assert timestamp_str.endswith("Z")
        
        # Should be parseable as ISO 8601
        # Remove trailing Z and parse
        dt = datetime.fromisoformat(timestamp_str.rstrip("Z"))
        assert isinstance(dt, datetime)
    
    def test_all_requests_have_timestamp(self):
        """All error responses should have timestamp."""
        client = TestClient(test_app)
        
        test_endpoints = [
            ("POST", "/test/xnai-error"),
            ("POST", "/test/voice-error"),
            ("POST", "/test/circuit-breaker-error"),
            ("GET", "/test/unauthorized"),
        ]
        
        for method, endpoint in test_endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint)
            
            data = response.json()
            assert "timestamp" in data
            assert data["timestamp"].endswith("Z")


class TestErrorResponseSchema:
    """Tests for ErrorResponse schema compliance."""
    
    def test_error_response_schema_validation(self):
        """ErrorResponse should be valid Pydantic model."""
        error_data = {
            "error_code": "test_error_1234",
            "message": "Test error",
            "category": "internal_error",
            "http_status": 500,
            "timestamp": datetime.utcnow(),
            "details": {"key": "value"},
            "recovery_suggestion": "Try again",
            "request_id": "req_test"
        }
        
        error = ErrorResponse(**error_data)
        assert error.error_code == "test_error_1234"
        assert error.category == "internal_error"
    
    def test_error_response_optional_fields(self):
        """ErrorResponse optional fields should work."""
        error_data = {
            "error_code": "test_error",
            "message": "Test",
            "category": "validation",
            "http_status": 400,
            "timestamp": datetime.utcnow(),
        }
        
        error = ErrorResponse(**error_data)
        assert error.details is None
        assert error.recovery_suggestion is None
        assert error.request_id is None


class TestSSEErrorMessage:
    """Tests for SSEErrorMessage schema."""
    
    def test_sse_error_message_creation(self):
        """SSEErrorMessage should be creatable with required fields."""
        sse_error = SSEErrorMessage(
            error_code="test_error_1234",
            message="Test error in stream"
        )
        
        assert sse_error.event == "error"
        assert sse_error.error_code == "test_error_1234"
        assert sse_error.message == "Test error in stream"
    
    def test_sse_error_message_with_recovery(self):
        """SSEErrorMessage with recovery suggestion."""
        sse_error = SSEErrorMessage(
            error_code="timeout_b456",
            message="Stream timeout",
            recovery_suggestion="Try with less context",
            request_id="req_123"
        )
        
        assert sse_error.recovery_suggestion == "Try with less context"
        assert sse_error.request_id == "req_123"


class TestErrorCodeDeterminism:
    """Tests for deterministic error code generation."""
    
    def test_same_message_generates_same_error_code(self):
        """Same exception message should generate same error code."""
        exc1 = XNAiException(
            message="Test error",
            category=ErrorCategory.INTERNAL_ERROR
        )
        
        exc2 = XNAiException(
            message="Test error",
            category=ErrorCategory.INTERNAL_ERROR
        )
        
        assert exc1.error_code == exc2.error_code
    
    def test_different_message_different_error_code(self):
        """Different exception messages should generate different error codes."""
        exc1 = XNAiException(
            message="Error one",
            category=ErrorCategory.INTERNAL_ERROR
        )
        
        exc2 = XNAiException(
            message="Error two",
            category=ErrorCategory.INTERNAL_ERROR
        )
        
        assert exc1.error_code != exc2.error_code


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
