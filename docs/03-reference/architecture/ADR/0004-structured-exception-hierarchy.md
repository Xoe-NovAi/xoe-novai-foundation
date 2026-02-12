# ADR 0004: Structured Exception Hierarchy with Category-Based Error Handling

**Status**: Accepted

**Date**: 2026-02-11

**Participants**: Claude (AI), Code Architecture Team

## Context

The Xoe-NovAi system was experiencing inconsistent error handling across API endpoints, with manual try/except blocks scattered throughout routers, varying error response formats, and difficulty tracking error types across subsystems. Error responses lacked context information (timestamps, error codes, recovery suggestions), making debugging and user communication difficult. Additionally, different subsystems (voice service, AWQ quantization, Vulkan acceleration, circuit breakers) had incompatible exception hierarchies that didn't integrate with the main API error handling.

### Constraints
- Must support integration with FastAPI and Pydantic validation
- Must provide deterministic error codes for logging and tracking
- Must map to HTTP status codes (400, 401, 403, 404, 429, 500, 503, 504, 507)
- Must support multiple subsystems with varying error semantics
- Must maintain backward compatibility with existing error responses during transition

## Decision

We will implement a **category-driven exception hierarchy** with the following principles:

### 1. Centralized ErrorCategory Enum
- **File**: `app/XNAi_rag_app/schemas/errors.py`
- **19 Error Categories**: VALIDATION, AUTH, PERMISSION_DENIED, NOT_FOUND, RATE_LIMIT, SERVICE_UNAVAILABLE, VOICE_SERVICE, AWQ_QUANTIZATION, VULKAN_ACCELERATION, CIRCUIT_OPEN, TIMEOUT, RESOURCE_LIMIT, MEMORY_LIMIT, GPU_UNAVAILABLE, DATABASE_ERROR, EXTERNAL_SERVICE_ERROR, INTERNAL_ERROR, MODEL_INIT_ERROR, STREAMING_ERROR
- **Deterministic Mapping**: Each category maps to exactly one HTTP status code
- **Values**: Use short string values (e.g., "validation", "voice_service") for serialization

### 2. Unified XNAiException Base Class
- **File**: `app/XNAi_rag_app/api/exceptions.py`
- **Constructor Parameters**:
  - `message`: Human-readable error description
  - `category`: ErrorCategory enum value
  - `error_code`: Unique identifier (auto-generated if not provided)
  - `http_status`: HTTP status code (auto-derived from category if not provided)
  - `details`: Dict for additional context (service_name, retry_after, etc.)
  - `recovery_suggestion`: User-facing guidance for error resolution
  - `cause`: Python exception for chaining
- **Error Code Generation**: Deterministic format `{category}_{message_hash[:4]}` using SHA256
- **Serialization**: `to_dict()` method returns structured error data for API responses

### 3. Subsystem-Specific Exception Hierarchies
- **Circuit Breaker**: `CircuitBreakerError(XNAiException)` with failure_count, retry_after_seconds
- **AWQ Quantization** (experimental/optional):
  - `AWQQuantizationError` (base)
  - `CalibrationError`, `QuantizationError`, `PrecisionSwitchError` (specialized)
- **Vulkan Acceleration** (optional):
  - `VulkanAccelerationError` (base)
  - `VulkanInitializationError`, `VulkanOperationError` (specialized)
- **Voice Service**:
  - `VoiceServiceError` (base, with cause_code parameter)
  - `STTError`, `TTSError`, `VADError` (specialized)
  - Cause codes map to recovery suggestions: stt_timeout, tts_circuit_open, vad_failed, etc.

### 4. Global Exception Handler
- **File**: `app/XNAi_rag_app/api/entrypoint.py`
- **Handlers**:
  - `@app.exception_handler(XNAiException)`: Serializes to ErrorResponse with correlation ID
  - `@app.exception_handler(RequestValidationError)`: Converts Pydantic errors to VALIDATION category
  - `@app.exception_handler(StarletteHTTPException)`: Wraps HTTP exceptions
- **Request Correlation**: Adds request_id to all error responses for tracing
- **Logging**: Logs all exceptions with full context for monitoring

### 5. Standardized Error Response Schema
- **ErrorResponse Model** (in `schemas/responses.py`):
  ```python
  {
    "error_code": "voice_service_a123",
    "message": "Failed to process audio stream",
    "category": "voice_service",
    "http_status": 503,
    "timestamp": "2026-02-11T10:30:45.123Z",
    "details": {"cause_code": "stt_circuit_open", "component": "whisper"},
    "recovery_suggestion": "The speech-to-text service is temporarily unavailable (circuit breaker open). Please retry in 5 seconds.",
    "request_id": "req_12345"
  }
  ```
- **For Streaming** (SSEErrorMessage):
  ```python
  {
    "event": "error",
    "error_code": "service_unavailable_b456",
    "message": "...",
    "recovery_suggestion": "..."
  }
  ```

## Consequences

### Positive
1. **Consistency**: All API errors follow the same structure and categorization
2. **Debuggability**: Error codes, timestamps, and request IDs enable efficient log analysis
3. **User Experience**: Recovery suggestions guide users toward resolution
4. **Maintainability**: Subsystems have localized exception hierarchies while integrating with global handler
5. **Testability**: Exception hierarchy allows fine-grained error path testing (100% coverage achievable)
6. **Determinism**: Error codes are deterministic and reproducible (same message → same code)
7. **Extensibility**: New subsystems can define specialized exceptions inheriting from XNAiException
8. **Experimental Features**: AWQ and Vulkan marked as optional/experimental throughout recovery suggestions

### Negative
1. **Migration Overhead**: Requires updating all routers to remove manual error handling (mitigated by global handler)
2. **Type Safety**: Manual error_code or http_status overrides could contradict category (mitigated by tests)
3. **Learning Curve**: New developers must learn category system and exception hierarchy

### Neutral
1. **Performance**: Negligible impact of error code generation via SHA256 (cold path, < 1ms)
2. **Backward Compatibility**: Phase 1 implementation doesn't break existing error handling yet (Phase 2 will unify)

## Implementation Phases

### Phase 1: Exception Infrastructure (COMPLETED - 62 tests passing)
- ✅ Create ErrorCategory enum (19 categories)
- ✅ Implement XNAiException base class
- ✅ Migrate subsystem exceptions (circuit breaker, AWQ, Vulkan, voice)
- ✅ Add comprehensive test coverage

### Phase 2: API Standardization (NEXT)
- [ ] Implement global exception handler in api/entrypoint.py
- [ ] Add ErrorResponse and SSEErrorMessage schemas
- [ ] Standardize input validation with Pydantic
- [ ] Migrate routers to rely on global handler

### Phase 3-5: Rollout and Observability
- [ ] Request correlation and tracing
- [ ] Error metrics and dashboards
- [ ] Client SDK updates for new responses

## References
- Exception hierarchy implementation: `app/XNAi_rag_app/api/exceptions.py`
- Test coverage: `tests/test_exceptions_*.py` (62 tests)
- Error schemas: `app/XNAi_rag_app/schemas/errors.py`
- Implementation manual: `_meta/xnai-code-audit-implementation-manual.md`
- Progress tracking: `memory_bank/error-handling-refactoring-progress.md`
