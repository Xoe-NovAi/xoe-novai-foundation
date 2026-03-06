"""
Content Sanitization Module for XNAi Foundation
================================================

Provides comprehensive content sanitization for security and privacy:
- API key detection and removal
- Credential redaction
- PII detection and hashing
- Sanitization logging

CLAUDE STANDARD: Uses AnyIO for structured concurrency where applicable.
Pattern: Zero-Trust Security (Phase 4.2.6)
Version: 1.0.0

Usage:
    from XNAi_rag_app.core.sanitization import ContentSanitizer
    
    sanitizer = ContentSanitizer()
    result = sanitizer.sanitize(content)
    # result.sanitized - sanitized content
    # result.redactions - list of what was redacted
    # result.risk_score - risk assessment (0-100)
"""

from .sanitizer import (
    ContentSanitizer,
    SanitizationResult,
    SanitizationConfig,
    RedactionType,
)

__all__ = [
    "ContentSanitizer",
    "SanitizationResult",
    "SanitizationConfig",
    "RedactionType",
]