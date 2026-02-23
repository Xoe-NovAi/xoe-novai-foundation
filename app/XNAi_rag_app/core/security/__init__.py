"""
XNAi Security Module - Zero-Trust Access Control & Content Sanitization
========================================================================

This module provides comprehensive security for knowledge operations:
- Agent DID validation and verification
- Task type authorization with ABAC policies
- Qdrant write permission management
- Content sanitization (API keys, credentials, PII)

Pattern: Zero-Trust Security (Phase 4.2.6)
Version: 1.0.0
"""

from .knowledge_access import (
    KnowledgeAccessController,
    KnowledgeOperation,
    KnowledgePermission,
    AccessDeniedError,
)
from .sanitization import (
    ContentSanitizer,
    SanitizationResult,
    SanitizationLevel,
)

__all__ = [
    # Knowledge Access Control
    "KnowledgeAccessController",
    "KnowledgeOperation",
    "KnowledgePermission",
    "AccessDeniedError",
    # Content Sanitization
    "ContentSanitizer",
    "SanitizationResult",
    "SanitizationLevel",
]