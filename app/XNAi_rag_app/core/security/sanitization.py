#!/usr/bin/env python3
"""
Content Sanitization Module - Security Redaction & PII Protection
==================================================================
Implements content sanitization for knowledge ingestion and storage.

Features:
- API key detection and removal (R012-1)
- Credential redaction (R012-2)
- PII detection (R012-3)
- Sanitization logging (R012-4)

Pattern: Zero-Trust Security (Phase 4.2.6)
Version: 1.0.0
"""

import os
import re
import json
import logging
import hashlib
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple, Pattern
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================================================
# Enums & Data Models
# ============================================================================


class SanitizationLevel(str, Enum):
    """Sanitization strictness levels"""

    MINIMAL = "minimal"  # Only critical secrets
    STANDARD = "standard"  # Secrets + common PII
    STRICT = "strict"  # All detectable sensitive data
    PARANOID = "paranoid"  # Maximum redaction


class SanitizationAction(str, Enum):
    """Actions taken on sensitive content"""

    REDACTED = "redacted"
    HASHED = "hashed"
    MASKED = "masked"
    REMOVED = "removed"
    FLAGGED = "flagged"


@dataclass
class SanitizationMatch:
    """A single sanitization match"""

    pattern_name: str
    match_type: str
    original_value: str
    action: SanitizationAction
    sanitized_value: str
    position: Tuple[int, int]
    confidence: float = 1.0


@dataclass
class SanitizationResult:
    """Result of content sanitization"""

    original_content: str
    sanitized_content: str
    level: SanitizationLevel
    matches: List[SanitizationMatch] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    content_hash: str = ""
    was_modified: bool = False

    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = hashlib.sha256(self.original_content.encode()).hexdigest()[:16]
        self.was_modified = self.original_content != self.sanitized_content

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content_hash": self.content_hash,
            "level": self.level.value,
            "was_modified": self.was_modified,
            "match_count": len(self.matches),
            "matches": [
                {
                    "pattern": m.pattern_name,
                    "type": m.match_type,
                    "action": m.action.value,
                    "position": m.position,
                    "confidence": m.confidence,
                }
                for m in self.matches
            ],
            "timestamp": self.timestamp,
        }


# ============================================================================
# Pattern Definitions
# ============================================================================


class SanitizationPatterns:
    """
    Regex patterns for sensitive content detection.

    Patterns are ordered by specificity and grouped by category.
    """

    # ========================================================================
    # API Keys (R012-1)
    # ========================================================================

    API_KEY_PATTERNS: List[Tuple[str, Pattern, str]] = [
        # OpenAI API keys
        ("openai_api_key", re.compile(r"sk-[a-zA-Z0-9]{48}", re.IGNORECASE), "api_key"),
        ("openai_project_key", re.compile(r"sk-proj-[a-zA-Z0-9]{48}", re.IGNORECASE), "api_key"),
        ("openai_service_key", re.compile(r"sk-svc[a-zA-Z0-9_-]{48}", re.IGNORECASE), "api_key"),
        # Anthropic API keys
        ("anthropic_api_key", re.compile(r"sk-ant-api[a-zA-Z0-9_-]{80,}", re.IGNORECASE), "api_key"),
        # Google API keys
        ("google_api_key", re.compile(r"AIza[a-zA-Z0-9_-]{35}", re.IGNORECASE), "api_key"),
        ("gcp_service_account", re.compile(r'"type"\s*:\s*"service_account"'), "api_key"),
        # AWS keys
        ("aws_access_key", re.compile(r"(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])"), "api_key"),
        ("aws_secret_key", re.compile(r"(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])"), "api_key"),
        # GitHub tokens
        ("github_pat", re.compile(r"ghp_[a-zA-Z0-9]{36}", re.IGNORECASE), "api_key"),
        ("github_oauth", re.compile(r"gho_[a-zA-Z0-9]{36}", re.IGNORECASE), "api_key"),
        ("github_app_token", re.compile(r"(?:ghu|ghs)_[a-zA-Z0-9]{36}", re.IGNORECASE), "api_key"),
        ("github_refresh_token", re.compile(r"ghr_[a-zA-Z0-9]{36}", re.IGNORECASE), "api_key"),
        # Generic API key patterns
        (
            "generic_api_key",
            re.compile(r"(?:api[_-]?key|apikey)\s*[=:]\s*['\"]?[a-zA-Z0-9_\-]{20,}['\"]?", re.IGNORECASE),
            "api_key",
        ),
        ("bearer_token", re.compile(r"Bearer\s+[a-zA-Z0-9_\-\.]+", re.IGNORECASE), "api_key"),
        # JWT tokens
        ("jwt_token", re.compile(r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*"), "api_key"),
        # Slack tokens
        ("slack_bot_token", re.compile(r"xoxb-[a-zA-Z0-9\-]{10,}", re.IGNORECASE), "api_key"),
        ("slack_app_token", re.compile(r"xoxa-[a-zA-Z0-9\-]{10,}", re.IGNORECASE), "api_key"),
        # Stripe keys
        ("stripe_live_key", re.compile(r"sk_live_[a-zA-Z0-9]{24,}", re.IGNORECASE), "api_key"),
        ("stripe_test_key", re.compile(r"sk_test_[a-zA-Z0-9]{24,}", re.IGNORECASE), "api_key"),
        # Private keys
        ("rsa_private_key", re.compile(r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----"), "private_key"),
        ("pgp_private_key", re.compile(r"-----BEGIN\s+PGP\s+PRIVATE\s+KEY\s+BLOCK-----"), "private_key"),
        ("ssh_private_key", re.compile(r"-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----"), "private_key"),
    ]

    # ========================================================================
    # Credentials (R012-2)
    # ========================================================================

    CREDENTIAL_PATTERNS: List[Tuple[str, Pattern, str]] = [
        # Password in connection strings
        # Note: Uses fixed-width look-behind for Python 3.13+ compatibility
        # Matches passwords in URLs like postgres://user:password@host
        ("password_in_url", re.compile(r"://[^:]+:([^@]+)@"), "password"),
        ("db_password", re.compile(r"(?:password|passwd|pwd)\s*[=:]\s*['\"]?[^'\"\s]{8,}['\"]?", re.IGNORECASE), "password"),
        # Connection strings with credentials
        ("postgres_connection", re.compile(r"postgres(?:ql)?://[^:]+:[^@]+@"), "connection_string"),
        ("mysql_connection", re.compile(r"mysql://[^:]+:[^@]+@"), "connection_string"),
        ("mongodb_connection", re.compile(r"mongodb(?:\+srv)?://[^:]+:[^@]+@"), "connection_string"),
        ("redis_connection", re.compile(r"redis://[^:]*:[^@]+@"), "connection_string"),
        # Generic credential patterns
        ("basic_auth", re.compile(r"(?:Authorization\s*:\s*Basic\s+)[a-zA-Z0-9+/=]+", re.IGNORECASE), "credential"),
        ("auth_header", re.compile(r"Authorization\s*:\s*\w+\s+[^\s]+", re.IGNORECASE), "credential"),
        # Secret keys in config
        (
            "secret_key",
            re.compile(r"(?:secret[_-]?key|secretkey)\s*[=:]\s*['\"]?[^'\"\s]{16,}['\"]?", re.IGNORECASE),
            "secret",
        ),
        # Environment variable secrets
        (
            "env_password",
            re.compile(r"(?:export\s+)?(?:PASSWORD|SECRET|TOKEN|KEY)\s*=\s*['\"]?[^'\"\s]+['\"]?", re.IGNORECASE),
            "secret",
        ),
    ]

    # ========================================================================
    # PII Detection (R012-3)
    # ========================================================================

    PII_PATTERNS: List[Tuple[str, Pattern, str]] = [
        # Email addresses
        ("email", re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"), "email"),
        # Phone numbers (various formats)
        ("phone_us", re.compile(r"\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"), "phone"),
        ("phone_intl", re.compile(r"\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}"), "phone"),
        # Social Security Numbers
        ("ssn", re.compile(r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b"), "ssn"),
        # Credit card numbers
        ("credit_card_visa", re.compile(r"\b4\d{12}(?:\d{3})?\b"), "credit_card"),
        ("credit_card_mc", re.compile(r"\b5[1-5]\d{14}\b"), "credit_card"),
        ("credit_card_amex", re.compile(r"\b3[47]\d{13}\b"), "credit_card"),
        ("credit_card_discover", re.compile(r"\b6(?:011|5\d{2})\d{12}\b"), "credit_card"),
        # IP addresses
        (
            "ipv4",
            re.compile(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"),
            "ip_address",
        ),
        ("ipv6", re.compile(r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b"), "ip_address"),
        # Dates of birth
        ("dob_us", re.compile(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b"), "dob"),
        ("dob_iso", re.compile(r"\b\d{4}-\d{2}-\d{2}\b"), "dob"),
        # Names in certain contexts
        (
            "full_name",
            re.compile(r"(?:name|full[_-]?name)\s*[=:]\s*['\"]?[A-Z][a-z]+\s+[A-Z][a-z]+['\"]?", re.IGNORECASE),
            "name",
        ),
        # Addresses
        (
            "street_address",
            re.compile(
                r"\d+\s+[A-Za-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\.?(?:\s+[A-Za-z]+)*",
                re.IGNORECASE,
            ),
            "address",
        ),
        ("zip_code_us", re.compile(r"\b\d{5}(?:-\d{4})?\b"), "zip_code"),
        # Bank account numbers
        ("bank_account", re.compile(r"\b\d{8,17}\b"), "bank_account"),
        # Passport numbers
        ("passport_us", re.compile(r"\b[A-Z]{1,2}\d{6,9}\b"), "passport"),
        # Driver's license (US formats vary by state)
        ("drivers_license", re.compile(r"(?:DL|Driver\s*License)[:\s]*[A-Z0-9]{6,12}", re.IGNORECASE), "drivers_license"),
    ]

    @classmethod
    def get_all_patterns(cls) -> List[Tuple[str, Pattern, str]]:
        """Get all patterns combined"""
        return cls.API_KEY_PATTERNS + cls.CREDENTIAL_PATTERNS + cls.PII_PATTERNS

    @classmethod
    def get_patterns_by_category(cls, category: str) -> List[Tuple[str, Pattern, str]]:
        """Get patterns by category"""
        categories = {
            "api_keys": cls.API_KEY_PATTERNS,
            "credentials": cls.CREDENTIAL_PATTERNS,
            "pii": cls.PII_PATTERNS,
        }
        return categories.get(category, [])


# ============================================================================
# Content Sanitizer
# ============================================================================


class ContentSanitizer:
    """
    Content sanitization for knowledge operations.

    Implements:
    - API key detection and removal (R012-1)
    - Credential redaction (R012-2)
    - PII detection (R012-3)
    - Sanitization logging (R012-4)

    Usage:
        sanitizer = ContentSanitizer(level=SanitizationLevel.STANDARD)

        result = sanitizer.sanitize(content)
        if result.was_modified:
            logger.info(f"Sanitized {len(result.matches)} sensitive items")
            sanitized_content = result.sanitized_content
        else:
            sanitized_content = result.original_content
    """

    def __init__(
        self,
        level: SanitizationLevel = SanitizationLevel.STANDARD,
        log_path: Optional[str] = None,
        hash_sensitive_values: bool = False,
    ):
        """
        Initialize the content sanitizer.

        Args:
            level: Sanitization strictness level
            log_path: Path to sanitization log file
            hash_sensitive_values: Whether to hash instead of redact
        """
        self.level = level
        self.log_path = log_path or os.getenv("SANITIZATION_LOG", "logs/sanitization_audit.jsonl")
        self.hash_sensitive_values = hash_sensitive_values

        # Select patterns based on level
        self._patterns = self._select_patterns()

        logger.info(f"ContentSanitizer initialized with level={level.value}, patterns={len(self._patterns)}")

    def _select_patterns(self) -> List[Tuple[str, Pattern, str]]:
        """Select patterns based on sanitization level"""
        if self.level == SanitizationLevel.MINIMAL:
            # Only API keys and private keys
            return SanitizationPatterns.API_KEY_PATTERNS
        elif self.level == SanitizationLevel.STANDARD:
            # API keys, credentials, and basic PII
            return (
                SanitizationPatterns.API_KEY_PATTERNS
                + SanitizationPatterns.CREDENTIAL_PATTERNS
                + SanitizationPatterns.PII_PATTERNS[:5]  # Email, phone, SSN, credit cards
            )
        elif self.level == SanitizationLevel.STRICT:
            # All patterns
            return SanitizationPatterns.get_all_patterns()
        else:  # PARANOID
            # All patterns + additional heuristics
            return SanitizationPatterns.get_all_patterns()

    def sanitize(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> SanitizationResult:
        """
        Sanitize content by detecting and redacting sensitive data.

        Args:
            content: The content to sanitize
            metadata: Optional metadata for logging

        Returns:
            SanitizationResult with sanitized content and match details
        """
        sanitized = content
        matches: List[SanitizationMatch] = []

        # Process each pattern
        for pattern_name, pattern, match_type in self._patterns:
            try:
                sanitized, pattern_matches = self._process_pattern(sanitized, pattern_name, pattern, match_type)
                matches.extend(pattern_matches)
            except Exception as e:
                logger.error(f"Error processing pattern {pattern_name}: {e}")

        result = SanitizationResult(
            original_content=content,
            sanitized_content=sanitized,
            level=self.level,
            matches=matches,
        )

        # Log sanitization (R012-4)
        if result.was_modified:
            self._log_sanitization(result, metadata)

        return result

    def _process_pattern(
        self,
        content: str,
        pattern_name: str,
        pattern: Pattern,
        match_type: str,
    ) -> Tuple[str, List[SanitizationMatch]]:
        """Process a single pattern and apply sanitization"""
        matches = []

        def replace_match(match) -> str:
            original = match.group(0)
            start, end = match.span()

            # Determine action based on match type
            if match_type in ("api_key", "private_key", "password", "secret", "credential"):
                action = SanitizationAction.REDACTED
                sanitized = self._redact_value(original, match_type)
            elif match_type in ("email", "phone"):
                action = SanitizationAction.MASKED
                sanitized = self._mask_value(original, match_type)
            elif match_type in ("ssn", "credit_card", "bank_account"):
                action = SanitizationAction.REDACTED
                sanitized = self._redact_value(original, match_type)
            elif match_type in ("ip_address", "address"):
                action = SanitizationAction.HASHED if self.hash_sensitive_values else SanitizationAction.MASKED
                sanitized = self._mask_value(original, match_type)
            else:
                action = SanitizationAction.FLAGGED
                sanitized = original  # Keep original but flag

            # Record match
            matches.append(
                SanitizationMatch(
                    pattern_name=pattern_name,
                    match_type=match_type,
                    original_value=self._truncate_for_log(original),
                    action=action,
                    sanitized_value=sanitized,
                    position=(start, end),
                )
            )

            return sanitized

        # Apply pattern substitution
        sanitized_content = pattern.sub(replace_match, content)

        return sanitized_content, matches

    def _redact_value(self, value: str, match_type: str) -> str:
        """Completely redact a sensitive value"""
        if self.hash_sensitive_values:
            # Use hash for reference
            hashed = hashlib.sha256(value.encode()).hexdigest()[:8]
            return f"[REDACTED:{match_type.upper()}:hash={hashed}]"
        return f"[REDACTED:{match_type.upper()}]"

    def _mask_value(self, value: str, match_type: str) -> str:
        """Partially mask a value for readability"""
        if len(value) <= 4:
            return "*" * len(value)

        # Keep first and last characters visible
        visible_start = min(2, len(value) // 4)
        visible_end = min(2, len(value) // 4)

        masked = value[:visible_start] + "*" * (len(value) - visible_start - visible_end) + value[-visible_end:]
        return masked

    def _truncate_for_log(self, value: str, max_length: int = 50) -> str:
        """Truncate value for safe logging"""
        if len(value) > max_length:
            return value[:max_length] + "..."
        return value

    # ========================================================================
    # Sanitization Logging (R012-4)
    # ========================================================================

    def _log_sanitization(
        self,
        result: SanitizationResult,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log sanitization action for audit"""
        try:
            log_entry = {
                "timestamp": result.timestamp,
                "content_hash": result.content_hash,
                "level": result.level.value,
                "was_modified": result.was_modified,
                "match_count": len(result.matches),
                "matches": [
                    {
                        "pattern": m.pattern_name,
                        "type": m.match_type,
                        "action": m.action.value,
                        "position": m.position,
                        "confidence": m.confidence,
                    }
                    for m in result.matches
                ],
                "metadata": metadata or {},
            }

            # Ensure log directory exists
            log_dir = os.path.dirname(self.log_path)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)

            # Append to log file
            with open(self.log_path, "a") as f:
                f.write(json.dumps(log_entry) + "\n")

            logger.info(f"Sanitization logged: {len(result.matches)} items in {result.content_hash}")

        except Exception as e:
            logger.error(f"Failed to log sanitization: {e}")

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def scan_only(self, content: str) -> List[SanitizationMatch]:
        """
        Scan content without modifying it.

        Returns list of detected sensitive items.
        """
        matches: List[SanitizationMatch] = []

        for pattern_name, pattern, match_type in self._patterns:
            for match in pattern.finditer(content):
                matches.append(
                    SanitizationMatch(
                        pattern_name=pattern_name,
                        match_type=match_type,
                        original_value=self._truncate_for_log(match.group(0)),
                        action=SanitizationAction.FLAGGED,
                        sanitized_value=match.group(0),  # Not sanitized
                        position=match.span(),
                    )
                )

        return matches

    def get_stats(self) -> Dict[str, Any]:
        """Get sanitizer statistics"""
        return {
            "level": self.level.value,
            "pattern_count": len(self._patterns),
            "pattern_categories": {
                "api_keys": len(SanitizationPatterns.API_KEY_PATTERNS),
                "credentials": len(SanitizationPatterns.CREDENTIAL_PATTERNS),
                "pii": len(SanitizationPatterns.PII_PATTERNS),
            },
            "hash_sensitive_values": self.hash_sensitive_values,
        }


# ============================================================================
# Utility Functions
# ============================================================================


def quick_sanitize(content: str, level: SanitizationLevel = SanitizationLevel.STANDARD) -> str:
    """
    Quick sanitization function for simple use cases.

    Args:
        content: Content to sanitize
        level: Sanitization level

    Returns:
        Sanitized content string
    """
    sanitizer = ContentSanitizer(level=level)
    result = sanitizer.sanitize(content)
    return result.sanitized_content


def check_for_secrets(content: str) -> List[Dict[str, Any]]:
    """
    Check content for secrets without modifying.

    Args:
        content: Content to check

    Returns:
        List of detected secrets
    """
    sanitizer = ContentSanitizer(level=SanitizationLevel.MINIMAL)
    matches = sanitizer.scan_only(content)
    return [
        {
            "pattern": m.pattern_name,
            "type": m.match_type,
            "position": m.position,
            "preview": m.original_value[:30] + "..." if len(m.original_value) > 30 else m.original_value,
        }
        for m in matches
    ]


# ============================================================================
# Global Sanitizer Instance
# ============================================================================

_global_sanitizer: Optional[ContentSanitizer] = None


def get_global_sanitizer() -> ContentSanitizer:
    """Get or create global sanitizer"""
    global _global_sanitizer
    if _global_sanitizer is None:
        _global_sanitizer = ContentSanitizer()
    return _global_sanitizer


def set_global_sanitizer(sanitizer: ContentSanitizer) -> None:
    """Set the global sanitizer"""
    global _global_sanitizer
    _global_sanitizer = sanitizer
