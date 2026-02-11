# Systematic Error Code & Handling Audit - 2026-02-11

## 📋 Executive Summary
This audit evaluates the current state of error handling, exception hierarchies, and error code standardization across the Xoe-NovAi Foundation codebase. While a unified exception base exists, its adoption is inconsistent across core modules, leading to fragmented error reporting and potential information leakage in API responses.

## 🔍 Key Findings

### 1. Exception Hierarchy Fragmentation
**Status**: 🟠 MODERATE RISK
- **Issue**: A base `XNAiException` is defined in `app/XNAi_rag_app/api/exceptions.py`, but several core modules define their own independent exception hierarchies.
- **Affected Files**:
    - `app/XNAi_rag_app/core/awq_quantizer.py` (`AWQQuantizationError`)
    - `app/XNAi_rag_app/core/vulkan_acceleration.py` (`VulkanAccelerationError`)
    - `app/XNAi_rag_app/core/circuit_breakers.py` (`CircuitBreakerError`)
    - `app/XNAi_rag_app/core/dynamic_precision.py` (`PrecisionSwitchError`)
- **Impact**: Inconsistent catch-all blocks and difficulty in implementing global error handlers that provide standardized responses.

### 2. Error Code & Category Inconsistency
**Status**: 🟠 MODERATE RISK
- **Issue**: `ErrorCategory` constants in `app/XNAi_rag_app/schemas/errors.py` are not consistently used. `XNAiException` and its subclasses use hardcoded strings for `error_code` (e.g., `"model_not_found"`) instead of referencing the central category enum.
- **Impact**: Risk of "magic string" drift where different parts of the system use slightly different codes for the same error type.

### 3. Leaky API Error Responses
**Status**: 🔴 HIGH RISK
- **Issue**: FastAPI routers (e.g., `query.py`) catch generic `Exception` and raise `HTTPException(status_code=500, detail=str(e))`.
- **Impact**: 
    - Leaks internal implementation details/stack traces to clients.
    - Bypasses the standardized `ErrorResponse` Pydantic model.
    - Inconsistent status codes for similar failure modes.

### 4. Inconsistent Voice Subsystem Error Protocol
**Status**: 🟡 LOW RISK
- **Issue**: `voice_interface.py` often returns magic strings like `"[STT temporarily unavailable]"` or `None` instead of raising structured exceptions.
- **Impact**: Calling code (like the Chainlit UI) has to perform string matching or null checks instead of standard exception handling.

### 5. Fragmented Circuit Breaker Handling
**Status**: 🟡 LOW RISK
- **Issue**: `CircuitBreakerError` is caught manually in multiple endpoints and converted to `JSONResponse(503, ...)` with hardcoded schemas.
- **Impact**: Redundant code in routers and inconsistent error formats between sync and streaming endpoints.

---

## 🛠️ Recommendations

### R1: Unify Exception Hierarchy
- **Action**: Update all core exception classes (`AWQQuantizationError`, `VulkanAccelerationError`, `CircuitBreakerError`, etc.) to inherit from `XNAiException`.
- **Goal**: Enable a single `except XNAiException` block to catch all domain-specific errors.

### R2: Enforce `ErrorCategory` Usage
- **Action**: Refactor `app/XNAi_rag_app/api/exceptions.py` to use `ErrorCategory` constants for the `error_code` parameter.
- **Goal**: Centralize error code definitions and eliminate magic strings.

### R3: Implement Global Exception Handlers
- **Action**: Add a global exception handler in `app/XNAi_rag_app/api/entrypoint.py` for `XNAiException`.
- **Implementation**:
  ```python
  @app.exception_handler(XNAiException)
  async def xnai_exception_handler(request: Request, exc: XNAiException):
      return JSONResponse(
          status_code=exc.http_status,
          content=ErrorResponse(
              error_code=exc.error_code,
              message=exc.message,
              timestamp=exc.timestamp,
              details=exc.details,
              recovery_suggestion=exc.recovery_suggestion
          ).dict()
      )
  ```
- **Goal**: Standardize all API error responses and reduce boilerplate in routers.

### R4: Standardize Streaming Error Format
- **Action**: Define a standard JSON schema for errors within the Server-Sent Events (SSE) stream.
- **Goal**: Ensure the UI can consistently parse and display errors regardless of which background process failed.

### R5: Refactor Voice Interface to Raise Exceptions
- **Action**: Replace error strings/None returns in `VoiceInterface` with specialized `XNAiException` subclasses (e.g., `VoiceServiceError`).
- **Goal**: Improve programmatic error handling and observability.

---

## 📅 Implementation Plan (Proposed)

1. **Phase 1 (Immediate)**: Implement global exception handler and refactor `XNAiException` to use `ErrorCategory`.
2. **Phase 2 (Short-term)**: Refactor core modules to inherit from `XNAiException`.
3. **Phase 3 (Medium-term)**: Clean up routers to remove redundant try/except blocks and manual `HTTPException` raises.
4. **Phase 4 (Long-term)**: Standardize voice interface and streaming error protocols.

---
**Audit Performed By**: Gemini CLI Agent
**Date**: 2026-02-11
**Status**: Findings Ready for Review/Implementation
