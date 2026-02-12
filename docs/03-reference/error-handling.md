# Error Handling Reference

**Version**: 1.0.0  
**Last Updated**: 2026-02-11  
**Status**: Active (Phase 1 Complete, Phase 2 In Progress)

## Overview

The Xoe-NovAi API uses a **category-driven exception hierarchy** to provide consistent, contextual error information to clients. This document explains how to understand, use, and extend the error handling system.

## Error Categories

All API errors are classified into one of 19 categories. Each category maps to a specific HTTP status code:

| Category | HTTP Status | Description | Use Cases |
|----------|-------------|-------------|-----------|
| VALIDATION | 400 | Request data invalid | Malformed requests, missing fields, constraint violations |
| AUTH | 401 | Authentication required | Missing/invalid API keys, expired tokens |
| PERMISSION_DENIED | 403 | Access forbidden | User lacks permission for resource/action |
| NOT_FOUND | 404 | Resource not found | Query returns empty, model doesn't exist |
| RATE_LIMIT | 429 | Rate limit exceeded | Too many requests within time window |
| SERVICE_UNAVAILABLE | 503 | Service temporarily down | Scheduled maintenance, temporary outage |
| VOICE_SERVICE | 503 | Voice processing failed | STT, TTS, or VAD errors (circuit open, timeout) |
| AWQ_QUANTIZATION | 500 | AWQ processing failed | GPU calibration/quantization error (experimental) |
| VULKAN_ACCELERATION | 500 | Vulkan processing failed | GPU acceleration error (optional) |
| CIRCUIT_OPEN | 503 | Circuit breaker open | Too many failures, retry after cooldown |
| TIMEOUT | 504 | Operation exceeded time limit | Query timeout, streaming timeout |
| RESOURCE_LIMIT | 429 | Max concurrent operations reached | Resource exhaustion limit |
| MEMORY_LIMIT | 507 | Out of memory | RAM/VRAM exhaustion |
| GPU_UNAVAILABLE | 500 | GPU not available | GPU offline, insufficient VRAM |
| DATABASE_ERROR | 500 | Database operation failed | Connection error, query failure |
| EXTERNAL_SERVICE_ERROR | 503 | Third-party service failed | LLM API timeout, embedding service down |
| INTERNAL_ERROR | 500 | Unexpected internal error | Unhandled exception, invariant violation |
| MODEL_INIT_ERROR | 500 | Model initialization failed | Model load timeout, corrupted weights |
| STREAMING_ERROR | 500 | Streaming response interrupted | Stream closed, transmission error |

## Error Response Format

All error responses follow this structure:

```json
{
  "error_code": "voice_service_a123",
  "message": "Failed to process audio stream",
  "category": "voice_service",
  "http_status": 503,
  "timestamp": "2026-02-11T10:30:45.123456Z",
  "details": {
    "cause_code": "stt_circuit_open",
    "component": "whisper",
    "retry_after_seconds": 5
  },
  "recovery_suggestion": "The speech-to-text service is temporarily unavailable (circuit breaker open). Please retry in 5 seconds.",
  "request_id": "req_550e8400-e29b-41d4-a716-446655440000"
}
```

### Field Descriptions

- **error_code**: Unique, deterministic identifier for this error type. Format: `{category}_{hash[:4]}` where hash is SHA256 of the message
- **message**: Human-readable description of what went wrong
- **category**: Error classification (see table above)
- **http_status**: HTTP status code for this error
- **timestamp**: ISO 8601 timestamp of when the error occurred (UTC)
- **details**: Subsystem-specific metadata (optional, not present on all errors)
- **recovery_suggestion**: User-facing guidance for resolving the error
- **request_id**: Unique identifier for correlating logs and debugging

## Using Error Responses

### Client-Side Error Handling

**By HTTP Status Code** (simple approach):
```python
import requests
try:
    response = requests.post("/api/v1/query", json={"query": "..."})
    response.raise_for_status()
    data = response.json()
except requests.HTTPError as e:
    status = e.response.status_code
    if status == 400:
        print("Invalid request format")
    elif status == 401:
        print("API key invalid or expired")
    elif status == 503:
        print("Service temporarily unavailable, trying again...")
    elif status == 504:
        print("Request timed out, try with shorter context")
```

**By Error Category** (recommended approach):
```python
try:
    response = requests.post("/api/v1/query", json={"query": "..."})
    response.raise_for_status()
    data = response.json()
except requests.HTTPError as e:
    error = e.response.json()
    category = error["category"]
    
    if category == "validation":
        # Show error to user, they need to fix input
        print(f"Error: {error['message']}")
        print(f"Suggestion: {error['recovery_suggestion']}")
    elif category == "rate_limit":
        # Implement exponential backoff
        wait_time = error["details"].get("retry_after_seconds", 60)
        print(f"Rate limited. Retrying in {wait_time}s...")
    elif category == "voice_service":
        # Voice-specific handling
        cause = error["details"].get("cause_code")
        if cause == "stt_circuit_open":
            print("STT service temporarily down, try again later")
        elif cause == "tts_failed":
            print("TTS synthesis failed, try simpler text")
    elif category == "service_unavailable":
        # Generic retry logic
        print("Service temporarily down, please try again")
```

**By Error Code** (debugging approach):
```python
try:
    response = requests.post("/api/v1/query", json={"query": "..."})
    response.raise_for_status()
except requests.HTTPError as e:
    error = e.response.json()
    error_code = error["error_code"]
    request_id = error["request_id"]
    
    # Send to logging/monitoring
    log_error(error_code, request_id, error)
    
    # Support team can search logs by error_code
    print(f"Error occurred. Please report code {error_code} to support.")
    print(f"Tracking ID: {request_id}")
```

## Server-Side: Raising Errors

### Basic Exception Usage

```python
from app.XNAi_rag_app.api.exceptions import XNAiException
from app.XNAi_rag_app.schemas.errors import ErrorCategory

# Raise a basic error
raise XNAiException(
    message="User quota exceeded",
    category=ErrorCategory.RATE_LIMIT,
    details={"quota_type": "monthly_requests", "limit": 10000},
    recovery_suggestion="Upgrade your plan or wait until next month"
)
```

### Subsystem-Specific Exceptions

#### Voice Service Errors

```python
from app.XNAi_rag_app.services.voice.exceptions import (
    VoiceServiceError, STTError, TTSError, VADError
)

# STT Error
if not audio_data:
    raise STTError(
        message="No audio data received",
        cause_code="no_audio_input",
        component="whisper"
    )

# TTS with circuit breaker context
try:
    synthesize_speech(text)
except CircuitBreakerOpenError:
    raise TTSError(
        message="TTS service circuit breaker open",
        cause_code="tts_circuit_open",
        component="piper"
    )

# VAD Error
if confidence < 0.3:
    raise VADError(
        message="Voice activity detection uncertain",
        cause_code="vad_confidence_low",
        component="silero_vad",
        audio_format="wav_16kHz"
    )
```

Available `cause_code` values for voice errors:
- `stt_timeout`: Speech recognition took too long
- `stt_no_match`: No speech recognized
- `stt_failed`: Recognition engine error
- `tts_circuit_open`: TTS service unavailable
- `tts_timeout`: Synthesis took too long
- `tts_failed`: Synthesis engine error
- `vad_failed`: Voice detection engine error
- `vad_timeout`: Detection took too long
- `vad_confidence_low`: Uncertain detection result

#### AWQ Quantization Errors (Experimental/Optional)

```python
from app.XNAi_rag_app.core.awq_quantizer import (
    CalibrationError, QuantizationError, PrecisionSwitchError
)

# Calibration error (GPU calibration dataset issue)
if not calibration_samples:
    raise CalibrationError(
        message="Insufficient calibration samples",
        details={"samples_count": 0, "min_required": 128}
    )

# Quantization error (layer processing failed)
if quant_layer_index >= len(model.layers):
    raise QuantizationError(
        message=f"Invalid layer for quantization",
        details={"layer_index": 5, "total_layers": 4}
    )

# Precision switch error (mixed precision conversion failed)
raise PrecisionSwitchError(
    message="Cannot convert fp16 to int8",
    details={
        "from_precision": "float16",
        "to_precision": "int8"
    }
)
```

**Note**: AWQ quantization is marked as **experimental** in all recovery suggestions.

#### Vulkan Acceleration Errors (Optional)

```python
from app.XNAi_rag_app.core.vulkan_acceleration import (
    VulkanInitializationError, VulkanOperationError
)

# Initialization error (device setup failed)
if not vulkan_device:
    raise VulkanInitializationError(
        message="Vulkan device initialization failed",
        details={"device_info": "No compatible GPU"}
    )

# Operation error (runtime processing failed)
if operation_result is None:
    raise VulkanOperationError(
        message="Vulkan shader execution failed",
        details={"operation_name": "matrix_multiply"}
    )
```

#### Chaining Exceptions

```python
try:
    result = process_request()
except RuntimeError as original_error:
    raise XNAiException(
        message="Request processing failed",
        category=ErrorCategory.INTERNAL_ERROR,
        recovery_suggestion="Retry the request",
        cause=original_error  # Preserves stack trace
    )
```

### Circuit Breaker Errors

```python
from app.XNAi_rag_app.core.circuit_breakers import CircuitBreakerError

# Automatically raised when circuit opens
raise CircuitBreakerError(
    message="Voice service circuit breaker open",
    details={
        "service_name": "whisper_stt",
        "failure_count": 5,
        "retry_after_seconds": 30,
        "breaker_state": "open"
    }
)
```

## Error Context (`details` Dict)

The `details` dictionary provides subsystem-specific context. Common fields:

| Field | Type | Used By | Description |
|-------|------|---------|-------------|
| service_name | str | Circuit Breaker | Which service failed |
| failure_count | int | Circuit Breaker | Number of consecutive failures |
| retry_after_seconds | int | Circuit Breaker, Rate Limit | How long to wait before retry |
| breaker_state | str | Circuit Breaker | Current state (open, closed, half_open) |
| cause_code | str | Voice Service | Specific fault code |
| component | str | Voice Service | Which subsystem (whisper, piper, silero_vad) |
| audio_format | str | Voice Service | Audio format encountered (wav_16kHz, mp3_44.1kHz) |
| layer_index | int | AWQ | Model layer index (for quantization) |
| samples_count | int | AWQ | Number of calibration samples |
| from_precision, to_precision | str | AWQ | Precision conversion (float16, int8) |
| device_info | str | Vulkan | GPU device information |
| operation_name | str | Vulkan | Name of operation that failed |

## Testing Error Paths

```python
import pytest
from app.XNAi_rag_app.api.exceptions import XNAiException
from app.XNAi_rag_app.schemas.errors import ErrorCategory

def test_circuit_breaker_error():
    with pytest.raises(XNAiException) as exc_info:
        raise XNAiException(
            message="Circuit open",
            category=ErrorCategory.CIRCUIT_OPEN
        )
    
    error = exc_info.value
    assert error.category == ErrorCategory.CIRCUIT_OPEN
    assert error.http_status == 503
    assert error.error_code.startswith("circuit_open_")
    
    # Verify serialization
    error_dict = error.to_dict()
    assert error_dict["category"] == "circuit_open"
    assert error_dict["http_status"] == 503
```

## Best Practices

1. **Use Specific Categories**: Always choose the most specific category for your error. Use `INTERNAL_ERROR` only for truly unexpected exceptions.

2. **Provide Context via Details**: Include relevant metadata in the `details` dict to help debugging (service name, layer index, audio format, etc.).

3. **Meaningful Recovery Suggestions**: Recovery suggestions should be actionable. Bad: "Something went wrong". Good: "The voice service is temporarily unavailable due to high load. Please retry in 30 seconds."

4. **Preserve Cause Chains**: When catching and re-raising, use the `cause` parameter to preserve the original exception for debugging.

5. **Don't Expose Internal Details**: Recovery suggestions are user-facing; avoid implementation details like Python stack traces.

6. **Mark Experimental Features**: When using AWQ or Vulkan, always include "(experimental)" or "(GPU-only)" in recovery suggestions.

7. **Log with Request ID**: When logging errors, include the request_id for cross-referencing with API logs.

## Phase 2-5 Roadmap

**Current State (Phase 1 Complete)**:
- ✅ Exception hierarchy implemented
- ✅ 62 tests passing
- ✅ Error codes deterministic and trackable

**Phase 2 (API Standardization - In Progress)**:
- [ ] Global exception handler standardizes all API responses
- [ ] Pydantic validation mapped to VALIDATION category
- [ ] Request correlation IDs added to all responses

**Phase 3 (Observability)**:
- [ ] Error metrics dashboard
- [ ] Error rate alerting
- [ ] Error code trending

**Phase 4 (Client SDKs)**:
- [ ] SDK updates to parse new error format
- [ ] Language-specific retry logic (exponential backoff)

**Phase 5 (Advanced Features)**:
- [ ] Machine learning-based error prediction
- [ ] Automatic recovery suggestions based on context
- [ ] Error pattern analysis

## References

- **ADR 0004**: [Structured Exception Hierarchy](architecture/ADR/0004-structured-exception-hierarchy.md)
- **Implementation Manual**: `_meta/xnai-code-audit-implementation-manual.md`
- **Progress Tracking**: `memory_bank/error-handling-refactoring-progress.md`
- **Source Code**:
  - Exception Base: `app/XNAi_rag_app/api/exceptions.py`
  - Error Schemas: `app/XNAi_rag_app/schemas/errors.py`
  - Voice Exceptions: `app/XNAi_rag_app/services/voice/exceptions.py`
  - Handler (Phase 2): `app/XNAi_rag_app/api/entrypoint.py`
