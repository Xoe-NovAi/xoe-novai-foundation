# Xoe-NovAi Code Audit Implementation Manual
## Comprehensive Enhancement Guide for Claude Haiku 4.5 Agentic Mode

**Document Version:** 1.0  
**Created:** 2026-02-11  
**Target:** Claude Haiku 4.5 in VS Code (Agentic Mode)  
**Audit Source:** `_meta/systematic-error-code-audit-20260211.md`  
**Priority:** Critical - Production Hardening

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Pre-Implementation Checklist](#pre-implementation-checklist)
3. [Phase 1: Error Architecture Foundation (Days 1-3)](#phase-1-error-architecture-foundation)
4. [Phase 2: API Standardization & Security (Days 4-7)](#phase-2-api-standardization--security)
5. [Phase 3: Subsystem Hardening (Days 8-12)](#phase-3-subsystem-hardening)
6. [Phase 4: Testing & Validation (Days 13-17)](#phase-4-testing--validation)
7. [Phase 5: Documentation & Observability (Days 18-21)](#phase-5-documentation--observability)
8. [Rollback Procedures](#rollback-procedures)
9. [Success Metrics](#success-metrics)
10. [Emergency Protocols](#emergency-protocols)

---

## 🎯 Executive Summary

### Audit Overview
The systematic audit identified **10 critical risk areas** across the Xoe-NovAi Foundation codebase:

| Risk Category | Severity | Files Affected | Priority |
|--------------|----------|----------------|----------|
| Exception Hierarchy Fragmentation | 🔴 HIGH | 15+ | CRITICAL |
| API Information Leakage | 🔴 HIGH | 8+ | CRITICAL |
| Error Code Inconsistency | 🟠 MODERATE | 50+ | HIGH |
| Voice Error Protocol | 🟡 MEDIUM | 5+ | HIGH |
| Async Race Conditions | 🟡 MEDIUM | 10+ | MEDIUM |
| Testing Coverage Gaps | 🟡 MEDIUM | All | MEDIUM |
| Security Boundaries | 🟡 MEDIUM | 12+ | MEDIUM |
| Documentation Gaps | 🟡 MEDIUM | 30+ | MEDIUM |
| Performance Monitoring | 🟡 MEDIUM | All | LOW |
| Circuit Breaker Format | 🟢 LOW | 3+ | LOW |

### Implementation Goals
- **Eliminate information leakage** in API responses
- **Unify exception hierarchies** under single base class
- **Standardize error response contracts** across all endpoints
- **Harden voice subsystem** error handling
- **Achieve 95%+ test coverage** for error paths
- **Zero security vulnerabilities** in production

### Time Estimate
**Total:** 21 days (3 weeks)  
**Phases:** 5 sequential phases with validation gates

---

## ✅ Pre-Implementation Checklist

### Environment Preparation

```bash
# 1. Verify development environment
cd /home/arcana-novai/Documents/Xoe-NovAi
python --version  # Should be 3.11+
uv --version      # Should be latest

# 2. Create implementation branch
git checkout -b audit-implementation-2026-02
git pull origin main

# 3. Backup current state
tar -czf ~/xnai-backup-$(date +%Y%m%d).tar.gz \
  app/ tests/ memory_bank/ config.toml

# 4. Set up test environment
cd tests
pytest --version
pytest --collect-only  # Verify test discovery

# 5. Create tracking directory
mkdir -p _meta/implementation-logs
touch _meta/implementation-logs/phase-tracker.md
```

### Required Tools & Dependencies

```python
# requirements-dev.txt additions
pytest==8.0.0
pytest-asyncio==0.23.0
pytest-cov==4.1.0
pytest-mock==3.12.0
httpx==0.27.0
fakeredis==2.21.0
black==24.2.0
ruff==0.2.2
mypy==1.8.0
```

### Safety Protocols

1. **Never modify production files directly** - Always work in `/app/XNAi_rag_app/`
2. **Test before commit** - All changes require passing tests
3. **Incremental commits** - Commit after each sub-phase completion
4. **Document decisions** - Update `_meta/implementation-logs/` with rationale
5. **Pair review** - Tag Taylor for critical architectural changes

---

## 🏗️ Phase 1: Error Architecture Foundation (Days 1-3)

### Objective
Establish unified exception hierarchy and error categorization system.

### 🎯 Success Criteria
- [ ] All custom exceptions inherit from `XNAiException`
- [ ] `ErrorCategory` enum used consistently
- [ ] Error codes are deterministic and version-stable
- [ ] All exceptions have `http_status`, `error_code`, `recovery_suggestion`

---

### Task 1.1: Create Unified Exception Base (Day 1, AM)

**File:** `app/XNAi_rag_app/api/exceptions.py`

#### Current State Analysis
```python
# EXISTING CODE (KEEP AS REFERENCE)
class XNAiException(Exception):
    """Base exception for Xoe-NovAi errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "internal_error",
        http_status: int = 500,
        details: Optional[Dict[str, Any]] = None,
        recovery_suggestion: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.http_status = http_status
        self.details = details or {}
        self.recovery_suggestion = recovery_suggestion
        self.timestamp = time.time()
```

#### Implementation Steps

**Step 1.1.1:** Enhance `ErrorCategory` enum

```python
# Location: app/XNAi_rag_app/schemas/errors.py
from enum import Enum

class ErrorCategory(str, Enum):
    """Comprehensive error categorization for unified handling."""
    
    # Client Errors (4xx)
    VALIDATION = "validation"              # 400
    AUTHENTICATION = "authentication"      # 401
    AUTHORIZATION = "authorization"        # 403
    NOT_FOUND = "not_found"               # 404
    RATE_LIMITED = "rate_limited"         # 429
    
    # Server Errors (5xx)
    INTERNAL_ERROR = "internal_error"     # 500
    SERVICE_UNAVAILABLE = "service_unavailable"  # 503
    TIMEOUT = "timeout"                   # 504
    
    # Domain-Specific
    AWQ_QUANTIZATION = "awq_quantization" # 500
    VULKAN_ACCELERATION = "vulkan_acceleration"  # 500
    CIRCUIT_OPEN = "circuit_open"         # 503
    VOICE_SERVICE = "voice_service"       # 503
    MODEL_ERROR = "model_error"           # 500
    MEMORY_LIMIT = "memory_limit"         # 507
    
    # Security
    SECURITY_ERROR = "security_error"     # 403
    INPUT_SANITIZATION = "input_sanitization"  # 400
```

**Step 1.1.2:** Update `XNAiException` with category mapping

```python
# Location: app/XNAi_rag_app/api/exceptions.py
from typing import Optional, Dict, Any
import time
from XNAi_rag_app.schemas.errors import ErrorCategory

class XNAiException(Exception):
    """
    Unified base exception for all Xoe-NovAi errors.
    
    Design Principles:
    - Category-driven HTTP status mapping
    - Deterministic error codes for client parsing
    - Recovery suggestions for user guidance
    - Structured metadata for observability
    
    Usage:
        raise XNAiException(
            message="Model not found",
            category=ErrorCategory.NOT_FOUND,
            details={"model_id": "llama-3.2-1b"},
            recovery_suggestion="Check model name and try again"
        )
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
        ErrorCategory.CIRCUIT_OPEN: 503,
        ErrorCategory.SERVICE_UNAVAILABLE: 503,
        ErrorCategory.VOICE_SERVICE: 503,
        ErrorCategory.TIMEOUT: 504,
        ErrorCategory.MEMORY_LIMIT: 507,
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
    
    def _generate_error_code(self, category: ErrorCategory, message: str) -> str:
        """
        Generate version-stable error code from category and message.
        
        Format: {category}_{short_hash}
        Example: validation_a3f2, circuit_open_b8c1
        """
        import hashlib
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
```

**Step 1.1.3:** Validation Script

```python
# Location: tests/test_exceptions_base.py
import pytest
from XNAi_rag_app.api.exceptions import XNAiException
from XNAi_rag_app.schemas.errors import ErrorCategory

def test_xnai_exception_category_mapping():
    """Verify all categories map to correct HTTP status."""
    test_cases = [
        (ErrorCategory.VALIDATION, 400),
        (ErrorCategory.NOT_FOUND, 404),
        (ErrorCategory.CIRCUIT_OPEN, 503),
        (ErrorCategory.INTERNAL_ERROR, 500),
    ]
    
    for category, expected_status in test_cases:
        exc = XNAiException(
            message="Test error",
            category=category
        )
        assert exc.http_status == expected_status, \
            f"{category} should map to {expected_status}"

def test_error_code_determinism():
    """Verify same message generates same error code."""
    exc1 = XNAiException(
        message="Model not found",
        category=ErrorCategory.NOT_FOUND
    )
    exc2 = XNAiException(
        message="Model not found",
        category=ErrorCategory.NOT_FOUND
    )
    assert exc1.error_code == exc2.error_code

def test_error_serialization():
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
```

**Validation Command:**
```bash
pytest tests/test_exceptions_base.py -v --tb=short
```

---

### Task 1.2: Migrate Existing Exceptions (Day 1, PM - Day 2)

**Objective:** Update all custom exception classes to inherit from `XNAiException`.

#### Files to Update (Priority Order)

1. **Circuit Breakers** (`app/XNAi_rag_app/core/circuit_breakers.py`)
2. **AWQ Quantizer** (`app/XNAi_rag_app/core/awq_quantizer.py`)
3. **Vulkan Acceleration** (`app/XNAi_rag_app/core/vulkan_acceleration.py`)
4. **Voice Services** (`app/XNAi_rag_app/services/voice/`)

---

#### Migration Pattern Template

```python
# BEFORE (Example: CircuitBreakerError)
class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""
    pass

# AFTER
from XNAi_rag_app.api.exceptions import XNAiException
from XNAi_rag_app.schemas.errors import ErrorCategory

class CircuitBreakerError(XNAiException):
    """
    Raised when circuit breaker is open.
    
    Attributes:
        service_name: Name of the protected service
        failure_count: Number of consecutive failures
        retry_after: Seconds until circuit half-opens
    """
    
    def __init__(
        self,
        service_name: str,
        failure_count: int,
        retry_after: Optional[int] = None,
        message: Optional[str] = None
    ):
        msg = message or f"Service '{service_name}' circuit is open"
        details = {
            "service_name": service_name,
            "failure_count": failure_count,
            "retry_after": retry_after,
        }
        recovery = f"Wait {retry_after}s before retry" if retry_after else \
                   "Check service health and retry"
        
        super().__init__(
            message=msg,
            category=ErrorCategory.CIRCUIT_OPEN,
            details=details,
            recovery_suggestion=recovery
        )
        
        # Store domain-specific attributes
        self.service_name = service_name
        self.failure_count = failure_count
        self.retry_after = retry_after
```

---

#### Step 1.2.1: Update `CircuitBreakerError`

**File:** `app/XNAi_rag_app/core/circuit_breakers.py`

```python
# Add import at top of file
from XNAi_rag_app.api.exceptions import XNAiException
from XNAi_rag_app.schemas.errors import ErrorCategory

# Replace existing CircuitBreakerError class
class CircuitBreakerError(XNAiException):
    """Raised when circuit breaker is open."""
    
    def __init__(
        self,
        service_name: str,
        failure_count: int,
        retry_after: Optional[int] = None,
        message: Optional[str] = None
    ):
        msg = message or f"Circuit breaker open for service: {service_name}"
        details = {
            "service_name": service_name,
            "failure_count": failure_count,
            "retry_after_seconds": retry_after,
            "breaker_state": "OPEN"
        }
        recovery = (
            f"Service is temporarily unavailable. "
            f"Retry after {retry_after} seconds." if retry_after else
            "Service is temporarily unavailable. Check health and retry."
        )
        
        super().__init__(
            message=msg,
            category=ErrorCategory.CIRCUIT_OPEN,
            details=details,
            recovery_suggestion=recovery
        )
        
        self.service_name = service_name
        self.failure_count = failure_count
        self.retry_after = retry_after

# Update all raise statements in the file
# BEFORE: raise CircuitBreakerError("LLM service unavailable")
# AFTER: raise CircuitBreakerError(
#     service_name="llm",
#     failure_count=breaker.failure_count,
#     retry_after=breaker.timeout
# )
```

**Test:** `tests/test_circuit_breakers.py`

```python
def test_circuit_breaker_error_inheritance():
    """Verify CircuitBreakerError inherits from XNAiException."""
    from XNAi_rag_app.core.circuit_breakers import CircuitBreakerError
    from XNAi_rag_app.api.exceptions import XNAiException
    
    exc = CircuitBreakerError(
        service_name="test_service",
        failure_count=5,
        retry_after=30
    )
    
    assert isinstance(exc, XNAiException)
    assert exc.http_status == 503
    assert exc.category.value == "circuit_open"
    assert "test_service" in exc.message
    assert exc.details["failure_count"] == 5
```

---

#### Step 1.2.2: Update AWQ Quantization Exceptions

**File:** `app/XNAi_rag_app/core/awq_quantizer.py`

```python
# Add imports
from XNAi_rag_app.api.exceptions import XNAiException
from XNAi_rag_app.schemas.errors import ErrorCategory

# Update exception classes
class AWQQuantizationError(XNAiException):
    """Base exception for AWQ quantization failures."""
    
    def __init__(
        self,
        message: str,
        model_path: Optional[str] = None,
        precision: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        details = {}
        if model_path:
            details["model_path"] = model_path
        if precision:
            details["target_precision"] = precision
        
        super().__init__(
            message=message,
            category=ErrorCategory.AWQ_QUANTIZATION,
            details=details,
            recovery_suggestion="Check model compatibility and try lower precision",
            cause=cause
        )

class CalibrationError(AWQQuantizationError):
    """Raised during model calibration phase."""
    
    def __init__(
        self,
        message: str,
        calibration_samples: Optional[int] = None,
        **kwargs
    ):
        if calibration_samples:
            kwargs.setdefault("details", {})["calibration_samples"] = calibration_samples
        super().__init__(message, **kwargs)

class QuantizationError(AWQQuantizationError):
    """Raised during weight quantization phase."""
    pass

class PrecisionSwitchError(AWQQuantizationError):
    """Raised when precision switching fails."""
    
    def __init__(
        self,
        message: str,
        from_precision: str,
        to_precision: str,
        **kwargs
    ):
        kwargs.setdefault("details", {}).update({
            "from_precision": from_precision,
            "to_precision": to_precision
        })
        super().__init__(message, **kwargs)
```

**Test:** `tests/test_awq_quantizer_exceptions.py`

```python
def test_awq_exception_hierarchy():
    """Verify AWQ exceptions inherit correctly."""
    from XNAi_rag_app.core.awq_quantizer import (
        AWQQuantizationError,
        CalibrationError,
        QuantizationError,
        PrecisionSwitchError
    )
    from XNAi_rag_app.api.exceptions import XNAiException
    
    # Test base AWQ exception
    exc = AWQQuantizationError(
        message="Quantization failed",
        model_path="/models/llama-3.2-1b",
        precision="int4"
    )
    
    assert isinstance(exc, XNAiException)
    assert exc.category.value == "awq_quantization"
    assert exc.details["model_path"] == "/models/llama-3.2-1b"
    
    # Test subclass inheritance
    calib_exc = CalibrationError(
        message="Calibration failed",
        calibration_samples=512
    )
    assert isinstance(calib_exc, AWQQuantizationError)
    assert isinstance(calib_exc, XNAiException)
```

---

#### Step 1.2.3: Update Vulkan Exceptions

**File:** `app/XNAi_rag_app/core/vulkan_acceleration.py`

```python
from XNAi_rag_app.api.exceptions import XNAiException
from XNAi_rag_app.schemas.errors import ErrorCategory

class VulkanAccelerationError(XNAiException):
    """Base exception for Vulkan acceleration failures."""
    
    def __init__(
        self,
        message: str,
        gpu_device: Optional[str] = None,
        vulkan_version: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        details = {}
        if gpu_device:
            details["gpu_device"] = gpu_device
        if vulkan_version:
            details["vulkan_version"] = vulkan_version
        
        super().__init__(
            message=message,
            category=ErrorCategory.VULKAN_ACCELERATION,
            details=details,
            recovery_suggestion="Check GPU drivers and Vulkan runtime",
            cause=cause
        )

class VulkanInitializationError(VulkanAccelerationError):
    """Raised when Vulkan initialization fails."""
    pass

class VulkanOperationError(VulkanAccelerationError):
    """Raised during Vulkan compute operations."""
    pass
```

---

#### Step 1.2.4: Create Voice Service Exception

**New File:** `app/XNAi_rag_app/services/voice/exceptions.py`

```python
"""
Voice Service Exception Hierarchy
=================================
Unified error handling for TTS/STT/VAD subsystems.
"""

from typing import Optional, Dict, Any
from XNAi_rag_app.api.exceptions import XNAiException
from XNAi_rag_app.schemas.errors import ErrorCategory

class VoiceServiceError(XNAiException):
    """Base exception for voice subsystem failures."""
    
    def __init__(
        self,
        message: str,
        cause_code: str,
        component: Optional[str] = None,
        audio_format: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        """
        Args:
            message: Human-readable error description
            cause_code: Machine-readable cause identifier
                (e.g., 'stt_unavailable', 'tts_timeout', 'vad_failed')
            component: Which voice component failed ('stt', 'tts', 'vad')
            audio_format: Audio format if relevant
            cause: Original exception if available
        """
        details = {
            "cause_code": cause_code,
        }
        if component:
            details["component"] = component
        if audio_format:
            details["audio_format"] = audio_format
        
        recovery = self._get_recovery_suggestion(cause_code)
        
        super().__init__(
            message=message,
            category=ErrorCategory.VOICE_SERVICE,
            details=details,
            recovery_suggestion=recovery,
            cause=cause
        )
        
        self.cause_code = cause_code
        self.component = component
    
    @staticmethod
    def _get_recovery_suggestion(cause_code: str) -> str:
        """Map cause codes to user-friendly recovery suggestions."""
        suggestions = {
            "stt_unavailable": "Speech-to-text service is temporarily unavailable. Try again in a moment.",
            "tts_unavailable": "Text-to-speech service is temporarily unavailable. Try again in a moment.",
            "stt_circuit_open": "STT circuit breaker is open. Wait 30 seconds before retry.",
            "tts_circuit_open": "TTS circuit breaker is open. Wait 30 seconds before retry.",
            "stt_timeout": "Speech recognition timed out. Speak more clearly or check microphone.",
            "tts_timeout": "Speech synthesis timed out. Try shorter text input.",
            "vad_failed": "Voice activity detection failed. Check audio input.",
            "audio_format_unsupported": "Audio format not supported. Use WAV/MP3/FLAC.",
            "rate_limited": "Too many requests. Wait before retrying.",
        }
        return suggestions.get(
            cause_code,
            "Voice service error occurred. Check logs and retry."
        )

# Specialized subclasses
class STTError(VoiceServiceError):
    """Speech-to-text specific error."""
    
    def __init__(self, message: str, cause_code: str, **kwargs):
        kwargs["component"] = "stt"
        super().__init__(message, cause_code, **kwargs)

class TTSError(VoiceServiceError):
    """Text-to-speech specific error."""
    
    def __init__(self, message: str, cause_code: str, **kwargs):
        kwargs["component"] = "tts"
        super().__init__(message, cause_code, **kwargs)

class VADError(VoiceServiceError):
    """Voice activity detection specific error."""
    
    def __init__(self, message: str, cause_code: str, **kwargs):
        kwargs["component"] = "vad"
        super().__init__(message, cause_code, **kwargs)
```

**Test:** `tests/test_voice_exceptions.py`

```python
def test_voice_service_error_cause_codes():
    """Verify voice error cause codes map to suggestions."""
    from XNAi_rag_app.services.voice.exceptions import VoiceServiceError
    
    exc = VoiceServiceError(
        message="STT unavailable",
        cause_code="stt_circuit_open",
        component="stt"
    )
    
    assert exc.cause_code == "stt_circuit_open"
    assert "30 seconds" in exc.recovery_suggestion
    assert exc.details["component"] == "stt"
    assert exc.http_status == 503

def test_voice_subclass_components():
    """Verify voice subclasses set component correctly."""
    from XNAi_rag_app.services.voice.exceptions import STTError, TTSError
    
    stt_exc = STTError(message="Test", cause_code="stt_timeout")
    assert stt_exc.component == "stt"
    
    tts_exc = TTSError(message="Test", cause_code="tts_timeout")
    assert tts_exc.component == "tts"
```

---

### Task 1.3: Exception Migration Checklist

**Validation Script:** `scripts/validate_exception_migration.py`

```python
#!/usr/bin/env python3
"""
Exception Migration Validation Script
=====================================
Verifies all exceptions inherit from XNAiException.
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple

def find_exception_classes(file_path: Path) -> List[Tuple[str, str]]:
    """Find all exception class definitions in a file."""
    try:
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
    except SyntaxError:
        return []
    
    exceptions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check if class ends with 'Error' or 'Exception'
            if node.name.endswith(('Error', 'Exception')):
                bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
                exceptions.append((node.name, ', '.join(bases) if bases else 'None'))
    
    return exceptions

def validate_migration():
    """Validate all custom exceptions inherit from XNAiException."""
    project_root = Path(__file__).parent.parent
    app_root = project_root / "app" / "XNAi_rag_app"
    
    # Files to check
    files_to_check = [
        app_root / "api" / "exceptions.py",
        app_root / "core" / "circuit_breakers.py",
        app_root / "core" / "awq_quantizer.py",
        app_root / "core" / "vulkan_acceleration.py",
        app_root / "services" / "voice" / "exceptions.py",
    ]
    
    issues = []
    valid = []
    
    for file_path in files_to_check:
        if not file_path.exists():
            issues.append(f"❌ Missing file: {file_path}")
            continue
        
        exceptions = find_exception_classes(file_path)
        for exc_name, bases in exceptions:
            if exc_name == "XNAiException":
                # Base class itself
                valid.append(f"✅ {file_path.name}: {exc_name} (base class)")
            elif "XNAiException" in bases or any(
                base.endswith("Error") and base != "Exception" for base in bases.split(", ")
            ):
                # Inherits from XNAiException or another custom exception
                valid.append(f"✅ {file_path.name}: {exc_name} extends {bases}")
            else:
                issues.append(
                    f"❌ {file_path.name}: {exc_name} does NOT inherit from XNAiException (bases: {bases})"
                )
    
    # Print results
    print("\n" + "="*80)
    print("EXCEPTION MIGRATION VALIDATION REPORT")
    print("="*80 + "\n")
    
    if valid:
        print("✅ VALID EXCEPTIONS:")
        for item in valid:
            print(f"  {item}")
    
    if issues:
        print("\n❌ ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
        print(f"\nTotal issues: {len(issues)}")
        return False
    else:
        print(f"\n✅ All {len(valid)} custom exceptions properly inherit from XNAiException")
        return True

if __name__ == "__main__":
    success = validate_migration()
    sys.exit(0 if success else 1)
```

**Run Validation:**
```bash
python scripts/validate_exception_migration.py
```

---

### Task 1.4: Phase 1 Completion Checklist

- [ ] `ErrorCategory` enum expanded with all categories
- [ ] `XNAiException` base class enhanced with category mapping
- [ ] `CircuitBreakerError` migrated and tested
- [ ] AWQ exceptions migrated and tested
- [ ] Vulkan exceptions migrated and tested
- [ ] Voice exceptions created and tested
- [ ] Exception migration validation script passes
- [ ] All Phase 1 tests pass: `pytest tests/test_exceptions*.py -v`
- [ ] Git commit: `git commit -m "Phase 1: Unified exception hierarchy"`

**Validation Command:**
```bash
pytest tests/test_exceptions*.py -v --cov=app/XNAi_rag_app/api/exceptions --cov-report=term-missing
```

**Expected Output:**
```
tests/test_exceptions_base.py::test_xnai_exception_category_mapping PASSED
tests/test_exceptions_base.py::test_error_code_determinism PASSED
tests/test_exceptions_base.py::test_error_serialization PASSED
tests/test_circuit_breakers.py::test_circuit_breaker_error_inheritance PASSED
tests/test_awq_quantizer_exceptions.py::test_awq_exception_hierarchy PASSED
tests/test_voice_exceptions.py::test_voice_service_error_cause_codes PASSED
tests/test_voice_exceptions.py::test_voice_subclass_components PASSED

Coverage: 95%+ on exceptions.py
```

---

## 🛡️ Phase 2: API Standardization & Security (Days 4-7)

### Objective
Eliminate information leakage, standardize error responses, implement global exception handler.

### 🎯 Success Criteria
- [ ] Global exception handler catches all `XNAiException` instances
- [ ] No `detail=str(e)` patterns in API responses
- [ ] All error responses use `ErrorResponse` Pydantic model
- [ ] SSE error format standardized
- [ ] Input validation boundaries enforced

---

### Task 2.1: Create Global Exception Handler (Day 4)

**File:** `app/XNAi_rag_app/api/entrypoint.py`

#### Step 2.1.1: Define Error Response Schema

**File:** `app/XNAi_rag_app/schemas/responses.py`

```python
"""
API Response Schemas
===================
Pydantic models for standardized API responses.
"""

from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

class ErrorResponse(BaseModel):
    """
    Standardized error response for all API endpoints.
    
    This schema ensures consistent error structure across
    the API surface and prevents information leakage.
    """
    
    error_code: str = Field(
        ...,
        description="Machine-readable error code (e.g., 'validation_a3f2')",
        example="circuit_open_b8c1"
    )
    
    message: str = Field(
        ...,
        description="Human-readable error message",
        example="Service temporarily unavailable"
    )
    
    category: str = Field(
        ...,
        description="Error category for client handling",
        example="circuit_open"
    )
    
    timestamp: float = Field(
        ...,
        description="Unix timestamp when error occurred",
        example=1707667200.0
    )
    
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Structured error details (sanitized)",
        example={"service_name": "llm", "retry_after": 30}
    )
    
    recovery_suggestion: Optional[str] = Field(
        default=None,
        description="User-friendly recovery guidance",
        example="Wait 30 seconds before retrying"
    )
    
    request_id: Optional[str] = Field(
        default=None,
        description="Correlation ID for request tracing"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "circuit_open_b8c1",
                "message": "LLM service temporarily unavailable",
                "category": "circuit_open",
                "timestamp": 1707667200.0,
                "details": {
                    "service_name": "llm",
                    "failure_count": 5,
                    "retry_after_seconds": 30
                },
                "recovery_suggestion": "Service is temporarily unavailable. Retry after 30 seconds.",
                "request_id": "req_abc123xyz"
            }
        }

class SSEErrorMessage(BaseModel):
    """
    Standardized error message for Server-Sent Events streams.
    
    Usage in SSE generators:
        error_data = SSEErrorMessage(
            error_code=exc.error_code,
            message=exc.message,
            ...
        ).model_dump()
        yield f"data: {json.dumps(error_data)}\n\n"
    """
    
    type: Literal["error"] = "error"
    error_code: str
    message: str
    category: str
    timestamp: float
    details: Optional[Dict[str, Any]] = None
    recovery_suggestion: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "error",
                "error_code": "timeout_c4d3",
                "message": "Query processing timed out",
                "category": "timeout",
                "timestamp": 1707667200.0,
                "recovery_suggestion": "Try a simpler query or increase timeout"
            }
        }
```

---

#### Step 2.1.2: Implement Global Exception Handlers

**File:** `app/XNAi_rag_app/api/entrypoint.py`

```python
"""
Xoe-NovAi API Entrypoint
=======================
ENHANCED: Global exception handling and standardized error responses.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import time
import uuid

from XNAi_rag_app.api.routers import router as api_router
from XNAi_rag_app.core.services_init import ServiceOrchestrator
from XNAi_rag_app.api.exceptions import XNAiException
from XNAi_rag_app.schemas.responses import ErrorResponse

logger = logging.getLogger(__name__)

# Global LLM instance (lazy loading with circuit breaker)
llm = None

async def load_llm_with_circuit_breaker():
    """Load LLM with circuit breaker protection."""
    global llm
    if llm is None:
        llm = await orchestrator._initialize_llm()
    if llm is None:
        raise RuntimeError("LLM not available - initialization failed")
    return llm

# Instantiate orchestrator
orchestrator = ServiceOrchestrator()

# Create FastAPI app
app = FastAPI(
    title="Xoe-NovAi API",
    description="Foundation RAG API for Xoe-NovAi stack.",
    version="0.1.0-alpha"
)

# ============================================================================
# GLOBAL EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(XNAiException)
async def xnai_exception_handler(request: Request, exc: XNAiException):
    """
    Global handler for all XNAiException instances.
    
    This ensures consistent error responses and prevents
    information leakage by using the structured ErrorResponse model.
    """
    request_id = str(uuid.uuid4())
    
    # Log error with context (sanitized)
    logger.error(
        f"XNAiException in {request.method} {request.url.path}",
        extra={
            "request_id": request_id,
            "error_code": exc.error_code,
            "category": exc.category.value,
            "status_code": exc.http_status,
            "user_agent": request.headers.get("user-agent"),
        },
        exc_info=True  # Include stack trace in logs, not response
    )
    
    # Build sanitized error response
    error_response = ErrorResponse(
        error_code=exc.error_code,
        message=exc.message,
        category=exc.category.value,
        timestamp=exc.timestamp,
        details=exc.details,  # Already sanitized in exception
        recovery_suggestion=exc.recovery_suggestion,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=exc.http_status,
        content=error_response.model_dump()
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors with standardized format.
    
    Converts Pydantic validation errors to ErrorResponse format.
    """
    request_id = str(uuid.uuid4())
    
    # Extract validation errors
    validation_errors = []
    for error in exc.errors():
        validation_errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation error in {request.method} {request.url.path}",
        extra={
            "request_id": request_id,
            "validation_errors": validation_errors
        }
    )
    
    error_response = ErrorResponse(
        error_code="validation_input",
        message="Request validation failed",
        category="validation",
        timestamp=time.time(),
        details={"validation_errors": validation_errors},
        recovery_suggestion="Fix the invalid fields and retry",
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=400,
        content=error_response.model_dump()
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle FastAPI/Starlette HTTP exceptions.
    
    Wraps HTTPException in ErrorResponse format.
    """
    request_id = str(uuid.uuid4())
    
    logger.warning(
        f"HTTP exception in {request.method} {request.url.path}",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "detail": exc.detail
        }
    )
    
    # Map status code to category
    category_map = {
        400: "validation",
        401: "authentication",
        403: "authorization",
        404: "not_found",
        429: "rate_limited",
        500: "internal_error",
        503: "service_unavailable",
        504: "timeout"
    }
    category = category_map.get(exc.status_code, "internal_error")
    
    error_response = ErrorResponse(
        error_code=f"http_{exc.status_code}",
        message=str(exc.detail),
        category=category,
        timestamp=time.time(),
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Last-resort handler for unexpected exceptions.
    
    This catches any exceptions not handled by specific handlers.
    IMPORTANT: Never exposes exception details to client.
    """
    request_id = str(uuid.uuid4())
    
    # Log full error details internally
    logger.error(
        f"Unhandled exception in {request.method} {request.url.path}",
        extra={
            "request_id": request_id,
            "exception_type": type(exc).__name__,
        },
        exc_info=True  # Full stack trace in logs only
    )
    
    # Return generic error to client (no leak)
    error_response = ErrorResponse(
        error_code="internal_error_unknown",
        message="An unexpected error occurred",
        category="internal_error",
        timestamp=time.time(),
        recovery_suggestion="Please contact support with the request ID",
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )

# ============================================================================
# APPLICATION SETUP
# ============================================================================

# Include all API routers
app.include_router(api_router)

# Lifespan event handlers for service orchestration
@app.on_event("startup")
async def on_startup():
    logger.info("[Startup] Initializing all services via ServiceOrchestrator...")
    services = await orchestrator.initialize_all()
    app.state.services = services
    logger.info("[Startup] All services initialized.")

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("[Shutdown] Shutting down all services via ServiceOrchestrator...")
    await orchestrator.shutdown_all()
    logger.info("[Shutdown] All services shut down.")
```

---

#### Step 2.1.3: Remove Try/Except from Routers

**File:** `app/XNAi_rag_app/api/routers/query.py`

```python
"""
Xoe-NovAi Query Router
======================
ENHANCED: Removed manual exception handling - relies on global handlers.
"""

import json
import logging
import asyncio
from typing import AsyncGenerator
from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse

from XNAi_rag_app.schemas import QueryRequest, QueryResponse
from XNAi_rag_app.schemas.responses import SSEErrorMessage
from XNAi_rag_app.core.metrics import (
    record_tokens_generated,
    record_query_processed,
    update_token_rate,
    MetricsTimer,
    response_latency_ms,
    record_error
)
from XNAi_rag_app.core.logging_config import PerformanceLogger, get_logger
from XNAi_rag_app.core.circuit_breakers import CircuitBreakerError
from XNAi_rag_app.api.exceptions import XNAiException

logger = get_logger(__name__)
perf_logger = PerformanceLogger(logger)
router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: Request, query_req: QueryRequest):
    """
    Synchronous query endpoint.
    
    REMOVED: Manual try/except blocks - global handler catches all exceptions.
    """
    start_time = asyncio.get_event_loop().time()
    
    # Business logic - exceptions propagate to global handler
    llm = await load_llm_with_circuit_breaker()
    
    # Process query
    response = await process_query(llm, query_req)
    
    # Record metrics
    elapsed = asyncio.get_event_loop().time() - start_time
    response_latency_ms.observe(elapsed * 1000)
    record_query_processed()
    
    return response

@router.post("/query/stream")
async def stream_endpoint(request: Request, query_req: QueryRequest):
    """
    Streaming query endpoint with SSE.
    
    ENHANCED: Standardized SSE error format.
    """
    
    async def generate_stream() -> AsyncGenerator[str, None]:
        """Generate SSE stream with standardized error handling."""
        try:
            llm = await load_llm_with_circuit_breaker()
            
            # Stream tokens
            async for token in llm.stream(query_req.query):
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
            
            # Stream complete
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except XNAiException as e:
            # Use standardized SSE error format
            error_data = SSEErrorMessage(
                error_code=e.error_code,
                message=e.message,
                category=e.category.value,
                timestamp=e.timestamp,
                details=e.details,
                recovery_suggestion=e.recovery_suggestion
            ).model_dump()
            
            yield f"data: {json.dumps(error_data)}\n\n"
            
            # Log error
            logger.error(
                f"Stream error: {e.error_code}",
                extra={"error_category": e.category.value}
            )
            record_error(e.category.value)
            
        except Exception as e:
            # Generic error in stream (last resort)
            error_data = SSEErrorMessage(
                error_code="stream_error_unknown",
                message="Stream processing failed",
                category="internal_error",
                timestamp=asyncio.get_event_loop().time()
            ).model_dump()
            
            yield f"data: {json.dumps(error_data)}\n\n"
            
            logger.error("Unhandled stream error", exc_info=True)
            record_error("internal_error")
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"
    )
```

---

### Task 2.2: Add Input Validation Boundaries (Day 5)

**File:** `app/XNAi_rag_app/schemas/__init__.py`

```python
"""
Enhanced Request Schemas with Validation Boundaries
===================================================
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List

class QueryRequest(BaseModel):
    """
    Query request with strict validation boundaries.
    
    Prevents:
    - Excessively long queries (DoS)
    - Invalid token limits
    - Malformed input
    """
    
    query: str = Field(
        ...,
        min_length=1,
        max_length=4096,
        description="User query text (1-4096 chars)",
        example="What is the capital of France?"
    )
    
    max_tokens: int = Field(
        default=512,
        gt=0,
        le=4096,
        description="Maximum tokens to generate (1-4096)",
        example=512
    )
    
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (0.0-2.0)",
        example=0.7
    )
    
    top_p: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling threshold (0.0-1.0)",
        example=0.9
    )
    
    context_window: Optional[int] = Field(
        default=None,
        gt=0,
        le=128000,
        description="Context window size (optional, max 128k)"
    )
    
    @validator("query")
    def sanitize_query(cls, v):
        """Sanitize query input."""
        # Strip excessive whitespace
        v = " ".join(v.split())
        
        # Check for injection patterns (basic)
        forbidden_patterns = ["<script>", "javascript:", "onerror="]
        for pattern in forbidden_patterns:
            if pattern.lower() in v.lower():
                raise ValueError(f"Query contains forbidden pattern: {pattern}")
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the key principles of sovereign AI?",
                "max_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.9
            }
        }

class QueryResponse(BaseModel):
    """Query response model."""
    
    answer: str = Field(..., description="Generated response")
    sources: List[str] = Field(default=[], description="Retrieved sources")
    tokens_generated: int = Field(..., description="Number of tokens generated")
    latency_ms: float = Field(..., description="Response latency in milliseconds")
```

---

### Task 2.3: Update Voice Interface Error Protocol (Day 6-7)

**File:** `app/XNAi_rag_app/services/voice/voice_interface.py`

#### Current State (Lines 1389-1391)
```python
# BEFORE - String sentinel return
return "[STT temporarily unavailable]", 0.0
```

#### Updated Implementation
```python
# AFTER - Raise structured exception
from XNAi_rag_app.services.voice.exceptions import STTError

# Replace all string sentinels
# Line 1389-1391
if stt_circuit_breaker.is_open():
    raise STTError(
        message="Speech-to-text service is temporarily unavailable",
        cause_code="stt_circuit_open"
    )

# Other voice error patterns
try:
    result = await whisper_stt.transcribe(audio_data)
except TimeoutError as e:
    raise STTError(
        message="Speech recognition timed out",
        cause_code="stt_timeout",
        audio_format=audio_format,
        cause=e
    )
except Exception as e:
    raise STTError(
        message="Speech recognition failed",
        cause_code="stt_unavailable",
        cause=e
    )
```

**Find and Replace Pattern:**

```bash
# Search for all string sentinel returns in voice module
grep -rn "return \"\[.*unavailable.*\]\""  app/XNAi_rag_app/services/voice/

# Common patterns to replace:
# 1. "[STT temporarily unavailable]" → raise STTError(...)
# 2. "[TTS temporarily unavailable]" → raise TTSError(...)
# 3. "[VAD failed]" → raise VADError(...)
```

---

### Task 2.4: Update Chainlit Voice Handlers (Day 7)

**File:** `app/XNAi_rag_app/ui/chainlit_app.py`

```python
"""
Chainlit UI - Voice Handler Updates
===================================
Replace string matching with structured exception handling.
"""

from XNAi_rag_app.services.voice.exceptions import (
    VoiceServiceError,
    STTError,
    TTSError,
    VADError
)

# BEFORE - String matching
@cl.on_audio_chunk
async def handle_audio_chunk(chunk):
    result = await voice_interface.process_audio(chunk)
    
    # OLD: Brittle string matching
    if isinstance(result, str) and "unavailable" in result:
        await cl.Message(content=result).send()
        return

# AFTER - Structured exception handling
@cl.on_audio_chunk
async def handle_audio_chunk(chunk):
    """Process audio chunk with structured error handling."""
    try:
        result = await voice_interface.process_audio(chunk)
        # Normal processing
        await process_voice_result(result)
        
    except STTError as e:
        # Speech-to-text specific error
        await cl.Message(
            content=f"🎤 {e.message}",
            metadata={"error_code": e.error_code}
        ).send()
        logger.warning(f"STT error: {e.cause_code}", exc_info=True)
        
    except TTSError as e:
        # Text-to-speech specific error
        await cl.Message(
            content=f"🔊 {e.message}"
        ).send()
        logger.warning(f"TTS error: {e.cause_code}", exc_info=True)
        
    except VoiceServiceError as e:
        # Generic voice service error
        await cl.Message(
            content=f"🚨 Voice service error: {e.recovery_suggestion}"
        ).send()
        logger.error(f"Voice error: {e.cause_code}", exc_info=True)
```

---

### Task 2.5: Phase 2 Testing

**Test File:** `tests/test_global_exception_handler.py`

```python
"""
Global Exception Handler Tests
==============================
Verifies global exception handling and error response standardization.
"""

import pytest
import json
from httpx import AsyncClient
from fastapi import FastAPI
from unittest.mock import patch, AsyncMock

from app.XNAi_rag_app.api.entrypoint import app
from app.XNAi_rag_app.api.exceptions import XNAiException
from app.XNAi_rag_app.schemas.errors import ErrorCategory

@pytest.mark.asyncio
async def test_xnai_exception_handler():
    """Verify XNAiException is caught and formatted correctly."""
    
    # Mock endpoint that raises XNAiException
    @app.get("/test/xnai-error")
    async def test_xnai_error():
        raise XNAiException(
            message="Test error",
            category=ErrorCategory.VALIDATION,
            details={"field": "test"}
        )
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/test/xnai-error")
    
    assert response.status_code == 400
    data = response.json()
    
    # Verify ErrorResponse structure
    assert "error_code" in data
    assert "message" in data
    assert "category" in data
    assert "timestamp" in data
    assert data["message"] == "Test error"
    assert data["category"] == "validation"
    assert data["details"]["field"] == "test"
    assert "request_id" in data

@pytest.mark.asyncio
async def test_no_information_leakage():
    """Verify generic Exception does NOT leak details."""
    
    @app.get("/test/generic-error")
    async def test_generic_error():
        raise Exception("Internal implementation detail that should not leak")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/test/generic-error")
    
    assert response.status_code == 500
    data = response.json()
    
    # Should NOT contain exception message
    assert "Internal implementation detail" not in data["message"]
    # Should have generic message
    assert data["message"] == "An unexpected error occurred"
    assert data["category"] == "internal_error"
    # Should have recovery suggestion
    assert "contact support" in data["recovery_suggestion"].lower()

@pytest.mark.asyncio
async def test_validation_error_standardization():
    """Verify Pydantic validation errors are standardized."""
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Send invalid request (query too long)
        response = await client.post(
            "/query",
            json={
                "query": "x" * 5000,  # Exceeds 4096 limit
                "max_tokens": 512
            }
        )
    
    assert response.status_code == 400
    data = response.json()
    
    assert data["error_code"] == "validation_input"
    assert data["category"] == "validation"
    assert "validation_errors" in data["details"]
    assert data["recovery_suggestion"] is not None

@pytest.mark.asyncio
async def test_sse_error_format():
    """Verify SSE errors use standardized format."""
    
    with patch("app.XNAi_rag_app.api.routers.query.load_llm_with_circuit_breaker") as mock_llm:
        # Mock LLM to raise CircuitBreakerError
        mock_llm.side_effect = CircuitBreakerError(
            service_name="llm",
            failure_count=5,
            retry_after=30
        )
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            async with client.stream(
                "POST",
                "/query/stream",
                json={"query": "test"}
            ) as response:
                # Read first SSE message
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        data = json.loads(line[5:])  # Remove "data: " prefix
                        break
        
        # Verify SSE error structure
        assert data["type"] == "error"
        assert data["error_code"].startswith("circuit_open")
        assert data["category"] == "circuit_open"
        assert "retry" in data["recovery_suggestion"].lower()
```

**Run Tests:**
```bash
pytest tests/test_global_exception_handler.py -v --tb=short
```

---

### Task 2.6: Phase 2 Completion Checklist

- [ ] `ErrorResponse` Pydantic model created
- [ ] `SSEErrorMessage` model created
- [ ] Global exception handlers implemented in entrypoint.py
- [ ] Manual try/except blocks removed from routers
- [ ] Voice interface updated to raise exceptions
- [ ] Chainlit handlers updated for structured exceptions
- [ ] Input validation boundaries added to schemas
- [ ] All Phase 2 tests pass
- [ ] Git commit: `git commit -m "Phase 2: Global exception handling & API standardization"`

**Validation:**
```bash
# Run full test suite
pytest tests/test_global_exception_handler.py -v
pytest tests/test_voice_exceptions.py -v

# Verify no information leakage
grep -r "detail=str(e)" app/XNAi_rag_app/api/
# Should return NO results

# Verify no string sentinels in voice
grep -rn "return \"\[.*unavailable.*\]\""  app/XNAi_rag_app/services/voice/
# Should return NO results
```

---

## 🔧 Phase 3: Subsystem Hardening (Days 8-12)

### Objective
Harden async patterns, fix race conditions, enhance circuit breaker handling.

### 🎯 Success Criteria
- [ ] No race conditions in LLM initialization
- [ ] Proper async resource cleanup in streaming endpoints
- [ ] Circuit breaker state transitions tested
- [ ] Metrics properly record error categories

---

### Task 3.1: Fix LLM Initialization Race Condition (Day 8)

**Current Issue:**
```python
# VULNERABLE: Race condition window
if ep.llm is None:
    ep.llm = await initialize_llm()  # Two requests could both initialize
```

**File:** `app/XNAi_rag_app/api/entrypoint.py` and `app/XNAi_rag_app/core/services_init.py`

#### Solution: Use AsyncLock

```python
"""
Service Orchestrator - Race Condition Fix
=========================================
"""

import asyncio
from typing import Optional

class ServiceOrchestrator:
    """Service initialization and lifecycle management."""
    
    def __init__(self):
        self._llm: Optional[Any] = None
        self._llm_lock = asyncio.Lock()  # ADD THIS
        self._services = {}
        self._initialized = False
    
    async def _initialize_llm(self):
        """
        Initialize LLM with race condition protection.
        
        Uses AsyncLock to ensure only one initialization occurs
        even if multiple requests arrive simultaneously.
        """
        async with self._llm_lock:  # CRITICAL: Lock acquisition
            # Double-check pattern
            if self._llm is not None:
                return self._llm
            
            logger.info("Initializing LLM (thread-safe)...")
            
            try:
                # Actual initialization
                self._llm = await self._do_llm_init()
                logger.info("LLM initialized successfully")
                return self._llm
                
            except Exception as e:
                logger.error("LLM initialization failed", exc_info=True)
                raise XNAiException(
                    message="Failed to initialize LLM",
                    category=ErrorCategory.INTERNAL_ERROR,
                    cause=e
                )
    
    async def _do_llm_init(self):
        """Actual LLM initialization logic (called within lock)."""
        # Existing initialization code here
        from langchain_community.llms import LlamaCpp
        
        llm = LlamaCpp(
            model_path="/models/llama-3.2-1b-q4_K_M.gguf",
            n_ctx=2048,
            n_gpu_layers=-1,
            verbose=False
        )
        
        return llm
```

**Test:** `tests/test_race_conditions.py`

```python
import pytest
import asyncio
from app.XNAi_rag_app.core.services_init import ServiceOrchestrator

@pytest.mark.asyncio
async def test_concurrent_llm_initialization():
    """Verify no race condition in concurrent LLM init."""
    
    orchestrator = ServiceOrchestrator()
    
    # Simulate 10 concurrent requests
    tasks = [
        orchestrator._initialize_llm()
        for _ in range(10)
    ]
    
    results = await asyncio.gather(*tasks)
    
    # All should return the SAME instance
    assert all(r is results[0] for r in results)
    
    # Should only initialize once (verify via logs or counter)
```

---

### Task 3.2: Add Streaming Resource Cleanup (Day 9)

**File:** `app/XNAi_rag_app/api/routers/query.py`

```python
@router.post("/query/stream")
async def stream_endpoint(request: Request, query_req: QueryRequest):
    """Streaming endpoint with proper resource cleanup."""
    
    async def generate_stream() -> AsyncGenerator[str, None]:
        """Generate SSE stream with resource cleanup."""
        llm = None
        stream = None
        
        try:
            llm = await load_llm_with_circuit_breaker()
            stream = llm.stream(query_req.query)
            
            async for token in stream:
                # Check if client disconnected
                if await request.is_disconnected():
                    logger.info("Client disconnected, stopping stream")
                    break
                
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except XNAiException as e:
            error_data = SSEErrorMessage(
                error_code=e.error_code,
                message=e.message,
                category=e.category.value,
                timestamp=e.timestamp,
                recovery_suggestion=e.recovery_suggestion
            ).model_dump()
            
            yield f"data: {json.dumps(error_data)}\n\n"
            record_error(e.category.value)
            
        finally:
            # CRITICAL: Cleanup resources
            if stream is not None:
                try:
                    await stream.aclose()  # Close async generator
                except Exception as e:
                    logger.warning(f"Error closing stream: {e}")
            
            logger.debug("Stream resources cleaned up")
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
```

---

### Task 3.3: Circuit Breaker State Transition Tests (Day 10)

**File:** `tests/test_circuit_breaker_transitions.py`

```python
"""
Circuit Breaker State Transition Tests
======================================
Comprehensive testing of circuit breaker state machine.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from app.XNAi_rag_app.core.circuit_breakers import (
    CircuitBreaker,
    CircuitBreakerError
)

@pytest.fixture
def circuit_breaker():
    """Create circuit breaker with short timeouts for testing."""
    return CircuitBreaker(
        name="test_service",
        failure_threshold=3,
        timeout=1,  # 1 second for fast tests
        expected_exception=Exception
    )

@pytest.mark.asyncio
async def test_circuit_breaker_opens_after_threshold(circuit_breaker):
    """Verify circuit opens after failure threshold."""
    
    async def failing_operation():
        raise Exception("Simulated failure")
    
    # Trigger failures
    for i in range(3):
        with pytest.raises(Exception):
            await circuit_breaker.call(failing_operation)
    
    # Circuit should now be OPEN
    assert circuit_breaker.state == "OPEN"
    
    # Next call should raise CircuitBreakerError immediately
    with pytest.raises(CircuitBreakerError) as exc_info:
        await circuit_breaker.call(failing_operation)
    
    assert exc_info.value.service_name == "test_service"
    assert exc_info.value.failure_count == 3

@pytest.mark.asyncio
async def test_circuit_breaker_half_open_transition(circuit_breaker):
    """Verify circuit transitions to HALF_OPEN after timeout."""
    
    async def failing_operation():
        raise Exception("Failure")
    
    # Open the circuit
    for _ in range(3):
        with pytest.raises(Exception):
            await circuit_breaker.call(failing_operation)
    
    assert circuit_breaker.state == "OPEN"
    
    # Wait for timeout
    await asyncio.sleep(1.1)
    
    # Next call should transition to HALF_OPEN
    async def successful_operation():
        return "success"
    
    result = await circuit_breaker.call(successful_operation)
    
    # Should succeed and close circuit
    assert result == "success"
    assert circuit_breaker.state == "CLOSED"
    assert circuit_breaker.failure_count == 0

@pytest.mark.asyncio
async def test_circuit_breaker_resets_on_success(circuit_breaker):
    """Verify failure count resets after successful call."""
    
    call_count = 0
    
    async def intermittent_operation():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("Fail")
        return "success"
    
    # Two failures
    for _ in range(2):
        with pytest.raises(Exception):
            await circuit_breaker.call(intermittent_operation)
    
    assert circuit_breaker.failure_count == 2
    
    # Success resets counter
    result = await circuit_breaker.call(intermittent_operation)
    assert result == "success"
    assert circuit_breaker.failure_count == 0
    assert circuit_breaker.state == "CLOSED"
```

---

### Task 3.4: Metrics Category Recording (Day 11-12)

**File:** `app/XNAi_rag_app/core/metrics.py`

```python
"""
Enhanced Metrics with Error Category Tracking
=============================================
"""

from prometheus_client import Counter, Histogram, Gauge
from typing import Optional

# Error counters by category
errors_by_category = Counter(
    "xnai_errors_total",
    "Total errors by category",
    ["category", "error_code"]
)

# Error rate by endpoint
errors_by_endpoint = Counter(
    "xnai_endpoint_errors_total",
    "Errors by API endpoint",
    ["endpoint", "method", "category"]
)

# Circuit breaker state gauge
circuit_breaker_state = Gauge(
    "xnai_circuit_breaker_state",
    "Circuit breaker state (0=closed, 1=open, 0.5=half_open)",
    ["service_name"]
)

def record_error(
    category: str,
    error_code: Optional[str] = None,
    endpoint: Optional[str] = None,
    method: Optional[str] = None
):
    """
    Record error with category classification.
    
    Args:
        category: ErrorCategory value (e.g., 'circuit_open')
        error_code: Specific error code (e.g., 'circuit_open_b8c1')
        endpoint: API endpoint path (e.g., '/query')
        method: HTTP method (e.g., 'POST')
    """
    # Increment category counter
    errors_by_category.labels(
        category=category,
        error_code=error_code or "unknown"
    ).inc()
    
    # Increment endpoint counter if provided
    if endpoint and method:
        errors_by_endpoint.labels(
            endpoint=endpoint,
            method=method,
            category=category
        ).inc()

def update_circuit_breaker_state(service_name: str, state: str):
    """
    Update circuit breaker state metric.
    
    Args:
        service_name: Name of service (e.g., 'llm', 'stt', 'tts')
        state: State string ('CLOSED', 'OPEN', 'HALF_OPEN')
    """
    state_map = {
        "CLOSED": 0.0,
        "OPEN": 1.0,
        "HALF_OPEN": 0.5
    }
    
    circuit_breaker_state.labels(
        service_name=service_name
    ).set(state_map.get(state, 0.0))
```

**Integration:**

```python
# In circuit_breakers.py, add metric updates
class CircuitBreaker:
    def _update_state(self, new_state: str):
        """Update circuit breaker state with metrics."""
        old_state = self.state
        self.state = new_state
        
        logger.info(
            f"Circuit breaker '{self.name}' state transition: {old_state} → {new_state}"
        )
        
        # Update Prometheus metric
        from XNAi_rag_app.core.metrics import update_circuit_breaker_state
        update_circuit_breaker_state(self.name, new_state)
```

---

### Task 3.5: Phase 3 Completion Checklist

- [ ] LLM initialization race condition fixed with AsyncLock
- [ ] Streaming endpoints have proper resource cleanup
- [ ] Circuit breaker state transitions fully tested
- [ ] Metrics track error categories
- [ ] Circuit breaker state exposed to Prometheus
- [ ] All Phase 3 tests pass
- [ ] Git commit: `git commit -m "Phase 3: Async hardening & circuit breaker enhancements"`

---

## 🧪 Phase 4: Testing & Validation (Days 13-17)

### Objective
Achieve 95%+ test coverage for error paths and validate all refactorings.

---

### Task 4.1: Error Path Test Coverage (Day 13-15)

**Create:** `tests/test_error_paths_comprehensive.py`

```python
"""
Comprehensive Error Path Testing
================================
Validates all error scenarios across the codebase.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from app.XNAi_rag_app.api.entrypoint import app

# Test matrix: All error categories × All endpoints
ERROR_TEST_MATRIX = [
    # (category, endpoint, method, mock_side_effect, expected_status)
    ("CIRCUIT_OPEN", "/query", "POST", CircuitBreakerError("llm", 5, 30), 503),
    ("VALIDATION", "/query", "POST", None, 400),  # Invalid input
    ("TIMEOUT", "/query/stream", "POST", asyncio.TimeoutError(), 504),
    ("AWQ_QUANTIZATION", "/query", "POST", AWQQuantizationError("test"), 500),
    ("VULKAN_ACCELERATION", "/query", "POST", VulkanAccelerationError("test"), 500),
    ("VOICE_SERVICE", "/voice/transcribe", "POST", STTError("test", "stt_timeout"), 503),
]

@pytest.mark.parametrize("category,endpoint,method,side_effect,expected_status", ERROR_TEST_MATRIX)
@pytest.mark.asyncio
async def test_error_path_coverage(category, endpoint, method, side_effect, expected_status):
    """Test all error paths return correct status and format."""
    
    with patch("app.XNAi_rag_app.api.routers.query.load_llm_with_circuit_breaker") as mock_llm:
        if side_effect:
            mock_llm.side_effect = side_effect
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            if method == "POST":
                response = await client.post(endpoint, json={"query": "test"})
            else:
                response = await client.get(endpoint)
        
        assert response.status_code == expected_status
        data = response.json()
        
        # Verify ErrorResponse structure
        assert "error_code" in data
        assert "category" in data
        assert "message" in data
        assert "timestamp" in data
```

---

### Task 4.2: Integration Test Suite (Day 16)

**File:** `tests/test_integration_full_stack.py`

```python
"""
Full Stack Integration Tests
============================
End-to-end testing of complete request flows.
"""

@pytest.mark.integration
@pytest.mark.asyncio
async def test_query_success_path():
    """Test successful query flow end-to-end."""
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/query",
            json={
                "query": "What is sovereign AI?",
                "max_tokens": 256
            }
        )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "answer" in data
    assert "tokens_generated" in data
    assert data["tokens_generated"] > 0

@pytest.mark.integration
@pytest.mark.asyncio
async def test_circuit_breaker_recovery():
    """Test circuit breaker opens, then recovers."""
    
    # Trigger circuit breaker
    # ... test implementation
    pass
```

---

### Task 4.3: Phase 4 Completion Checklist

- [ ] 95%+ code coverage on error paths
- [ ] All error categories tested
- [ ] Integration tests pass
- [ ] Coverage report generated
- [ ] Git commit: `git commit -m "Phase 4: Comprehensive testing"`

**Validation:**
```bash
pytest --cov=app/XNAi_rag_app --cov-report=html --cov-report=term
open htmlcov/index.html  # Review coverage
```

---

## 📚 Phase 5: Documentation & Observability (Days 18-21)

### Objective
Document all changes, update API contracts, enhance observability.

---

### Task 5.1: API Error Documentation (Day 18-19)

**Create:** `docs/api/error-codes-reference.md`

```markdown
# Xoe-NovAi API Error Code Reference

## Error Response Format

All API errors return a standardized `ErrorResponse`:

\`\`\`json
{
  "error_code": "circuit_open_b8c1",
  "message": "LLM service temporarily unavailable",
  "category": "circuit_open",
  "timestamp": 1707667200.0,
  "details": {
    "service_name": "llm",
    "retry_after_seconds": 30
  },
  "recovery_suggestion": "Wait 30 seconds before retrying",
  "request_id": "req_abc123"
}
\`\`\`

## Error Categories

### Client Errors (4xx)

| Category | HTTP Status | Description | Recovery |
|----------|------------|-------------|----------|
| `validation` | 400 | Invalid input | Fix request params |
| `authentication` | 401 | Missing/invalid auth | Provide valid credentials |
| `authorization` | 403 | Insufficient permissions | Contact admin |
| `not_found` | 404 | Resource not found | Check resource ID |
| `rate_limited` | 429 | Too many requests | Implement backoff |

### Server Errors (5xx)

| Category | HTTP Status | Description | Recovery |
|----------|------------|-------------|----------|
| `circuit_open` | 503 | Service degraded | Retry after specified time |
| `timeout` | 504 | Request timed out | Simplify request |
| `internal_error` | 500 | Unexpected error | Contact support |

## Common Error Codes

### Circuit Breaker Errors

**Code:** `circuit_open_*`  
**Status:** 503  
**Cause:** Service has failed too many times

Example:
\`\`\`json
{
  "error_code": "circuit_open_b8c1",
  "details": {
    "service_name": "llm",
    "failure_count": 5,
    "retry_after_seconds": 30
  }
}
\`\`\`

### Voice Service Errors

**Code:** `voice_service_*`  
**Status:** 503  
**Cause:** STT/TTS/VAD failure

Example:
\`\`\`json
{
  "error_code": "voice_service_a4f2",
  "details": {
    "component": "stt",
    "cause_code": "stt_circuit_open"
  }
}
\`\`\`

```

---

### Task 5.2: Update OpenAPI Documentation (Day 20)

**File:** `app/XNAi_rag_app/api/routers/query.py`

```python
@router.post(
    "/query",
    response_model=QueryResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid request parameters"
        },
        503: {
            "model": ErrorResponse,
            "description": "Service temporarily unavailable (circuit breaker open)"
        },
        500: {
            "model": ErrorResponse,
            "description": "Internal server error"
        }
    },
    summary="Submit a RAG query",
    description="""
    Submit a natural language query to the RAG system.
    
    **Error Handling:**
    - Returns standardized ErrorResponse on all failures
    - Circuit breaker protection prevents cascade failures
    - All errors include recovery suggestions
    
    **Rate Limits:** 100 requests/minute per IP
    """
)
async def query_endpoint(request: Request, query_req: QueryRequest):
    """Synchronous query endpoint."""
    ...
```

---

### Task 5.3: Observability Enhancement (Day 21)

**File:** `app/XNAi_rag_app/core/observability.py`

```python
"""
Enhanced Observability
=====================
Structured logging with error context.
"""

import structlog
from typing import Dict, Any

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

def log_error_with_context(
    logger,
    error: Exception,
    request_id: str,
    endpoint: str,
    user_id: Optional[str] = None,
    **extra_context
):
    """
    Log error with full context for debugging.
    
    Args:
        logger: Logger instance
        error: Exception object
        request_id: Request correlation ID
        endpoint: API endpoint path
        user_id: User identifier (if available)
        **extra_context: Additional context fields
    """
    context = {
        "request_id": request_id,
        "endpoint": endpoint,
        "error_type": type(error).__name__,
    }
    
    if hasattr(error, "error_code"):
        context["error_code"] = error.error_code
        context["error_category"] = error.category.value
    
    if user_id:
        context["user_id"] = user_id
    
    context.update(extra_context)
    
    logger.error(
        f"Error in {endpoint}",
        extra=context,
        exc_info=True
    )
```

---

### Task 5.4: Phase 5 Completion Checklist

- [ ] Error code reference documentation created
- [ ] OpenAPI documentation updated with error responses
- [ ] Structured logging enhanced
- [ ] Observability dashboard configured (Grafana)
- [ ] All documentation reviewed
- [ ] Git commit: `git commit -m "Phase 5: Documentation & observability"`

---

## 🔄 Rollback Procedures

### Emergency Rollback

If critical issues are discovered:

```bash
# 1. Revert to pre-implementation state
git checkout main
git branch -D audit-implementation-2026-02

# 2. Restore backup
cd ~
tar -xzf xnai-backup-YYYYMMDD.tar.gz -C /home/arcana-novai/Documents/Xoe-NovAi/

# 3. Restart services
cd /home/arcana-novai/Documents/Xoe-NovAi
podman-compose -f docker-compose.yml down
podman-compose -f docker-compose.yml up -d
```

### Phased Rollback

To rollback specific phases:

```bash
# Rollback Phase 5 only
git revert <phase5-commit-hash>

# Rollback Phases 4-5
git revert <phase4-commit-hash>^..<phase5-commit-hash>
```

---

## 📊 Success Metrics

### Code Quality Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Test Coverage | ≥95% | `pytest --cov` |
| Exception Hierarchy Compliance | 100% | `validate_exception_migration.py` |
| Zero Information Leakage | 100% | Manual audit + grep |
| API Response Consistency | 100% | Integration tests |
| Documentation Completeness | 100% | Review checklist |

### Performance Metrics

| Metric | Target | Monitoring |
|--------|--------|------------|
| Error Handling Overhead | <5ms | Prometheus latency |
| Memory Impact | <10MB | Process monitoring |
| Circuit Breaker Recovery Time | <30s | Metrics dashboard |

### Operational Metrics

| Metric | Target | Tool |
|--------|--------|------|
| Production Errors | <0.1% | Grafana alerts |
| Mean Time to Recovery | <5min | Incident logs |
| Error Categorization Accuracy | 100% | Manual validation |

---

## 🚨 Emergency Protocols

### Critical Error During Implementation

1. **Stop immediately** - Don't continue if tests fail
2. **Document the issue** in `_meta/implementation-logs/issues.md`
3. **Notify Taylor** via Vikunja task
4. **Rollback to last known good state**
5. **Analyze root cause** before resuming

### Production Incident

If audit changes cause production issues:

1. **Immediate rollback** using emergency procedure
2. **Activate incident response** team
3. **Collect logs** and metrics
4. **Root cause analysis** before re-implementation

---

## 📝 Implementation Log Template

**File:** `_meta/implementation-logs/phase-{N}-log.md`

```markdown
# Phase {N} Implementation Log

## Date: YYYY-MM-DD
## Implementer: Claude Haiku 4.5

### Tasks Completed
- [ ] Task 1: Description
- [ ] Task 2: Description

### Issues Encountered
1. **Issue:** Description
   **Resolution:** How it was fixed
   **Time Lost:** X hours

### Test Results
\`\`\`bash
pytest output here
\`\`\`

### Code Review Notes
- Finding 1
- Finding 2

### Commit Hash
\`abc123def456\`

### Next Steps
1. Step 1
2. Step 2
```

---

## ✅ Final Checklist

### Pre-Merge Requirements

- [ ] All 5 phases completed
- [ ] 95%+ test coverage achieved
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Code review by Taylor
- [ ] Performance benchmarks met
- [ ] Security audit passed
- [ ] Rollback procedure tested
- [ ] Production deployment plan approved

### Post-Merge Monitoring

- [ ] Monitor error rates for 48 hours
- [ ] Review Grafana dashboards
- [ ] Check for anomalies in logs
- [ ] Validate circuit breaker behavior
- [ ] Collect user feedback

---

## 📚 Additional Resources

### Reference Documentation
- Audit Report: `_meta/systematic-error-code-audit-20260211.md`
- Architecture Docs: `memory_bank/architectureContext.md`
- API Contracts: `docs/api/`

### Support Contacts
- **Project Director:** Taylor (Vikunja: @taylor)
- **Research Specialist:** Grok (Slack: #xoe-research)
- **DevOps:** Gemini CLI (Terminal)

---

**End of Implementation Manual**

**Version:** 1.0  
**Last Updated:** 2026-02-11  
**Next Review:** Post-Phase 5 completion
