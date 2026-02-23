#!/usr/bin/env python3
"""
Content Sanitizer for XNAi Foundation
======================================

Comprehensive content sanitization for security and privacy compliance.
Implements zero-trust security principles with GDPR/SOC2 alignment.

CLAUDE STANDARD: Uses AnyIO for structured concurrency where applicable.
Pattern: Zero-Trust Security (Phase 4.2.6)
Version: 1.0.0

Features:
- API key detection and removal (multiple formats)
- Credential redaction (passwords, tokens, secrets)
- PII detection with SHA256 correlation hashes
- Configurable redaction levels
- Comprehensive audit logging
"""

import re
import hashlib
import logging
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMERATIONS
# ============================================================================

class RedactionType(str, Enum):
    """Types of sensitive content that can be redacted."""
    API_KEY = "api_key"
    PASSWORD = "password"
    SECRET = "secret"
    TOKEN = "token"
    EMAIL = "email"
    IP_ADDRESS = "ip_address"
    CREDIT_CARD = "credit_card"
    SSN = "ssn"
    PHONE = "phone"
    PRIVATE_KEY = "private_key"
    CONNECTION_STRING = "connection_string"
    AWS_KEY = "aws_key"
    JWT = "jwt"
    URL_CREDENTIALS = "url_credentials"


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class SanitizationConfig:
    """Configuration for content sanitization."""
    
    # Enable/disable specific redactions
    redact_api_keys: bool = True
    redact_passwords: bool = True
    redact_secrets: bool = True
    redact_tokens: bool = True
    redact_emails: bool = True
    redact_ip_addresses: bool = False  # Often needed for logs
    redact_credit_cards: bool = True
    redact_ssn: bool = True
    redact_phones: bool = False  # Optional, may be needed
    redact_private_keys: bool = True
    redact_connection_strings: bool = True
    redact_aws_keys: bool = True
    redact_jwt: bool = True
    redact_url_credentials: bool = True
    
    # Redaction behavior
    use_hash_correlation: bool = True  # Use SHA256 hash prefix for correlation
    hash_prefix_length: int = 8  # Number of hash chars to show
    replacement_template: str = "[REDACTED_{type}:{hash}]"
    
    # Logging
    log_redactions: bool = True
    log_content_preview: bool = False  # Security risk if True
    preview_length: int = 20
    
    # Risk scoring thresholds
    high_risk_threshold: int = 70
    medium_risk_threshold: int = 40


# ============================================================================
# RESULT DATA CLASS
# ============================================================================

@dataclass
class RedactionRecord:
    """Record of a single redaction."""
    type: RedactionType
    original_preview: str
    position: Tuple[int, int]  # Start, end
    replacement: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class SanitizationResult:
    """Result of content sanitization."""
    
    # The sanitized content
    sanitized: str
    
    # List of redactions performed
    redactions: List[RedactionRecord] = field(default_factory=list)
    
    # Risk assessment (0-100)
    risk_score: int = 0
    
    # Risk level
    risk_level: str = "low"
    
    # Metadata
    original_length: int = 0
    sanitized_length: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Counts by type
    redaction_counts: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "sanitized": self.sanitized,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "original_length": self.original_length,
            "sanitized_length": self.sanitized_length,
            "redaction_count": len(self.redactions),
            "redaction_counts": self.redaction_counts,
            "timestamp": self.timestamp,
        }


# ============================================================================
# DETECTION PATTERNS
# ============================================================================

class SanitizationPatterns:
    """Regex patterns for sensitive content detection."""
    
    # API Keys - Various formats
    API_KEY_PATTERNS = [
        # Generic API keys (common prefixes)
        (r'(?i)(api[_-]?key|apikey)["\s:=]+["\']?([a-zA-Z0-9_\-]{20,64})["\']?', 'api_key'),
        (r'(?i)(bearer)\s+([a-zA-Z0-9_\-\.]{20,64})', 'token'),
        
        # OpenAI API key
        (r'sk-[a-zA-Z0-9]{20,}', 'api_key'),
        
        # Anthropic API key
        (r'sk-ant-[a-zA-Z0-9\-]{20,}', 'api_key'),
        
        # Google API key
        (r'AIza[a-zA-Z0-9_\-]{35,}', 'api_key'),
        
        # GitHub token
        (r'ghp_[a-zA-Z0-9]{36,}', 'token'),
        (r'github_pat_[a-zA-Z0-9_]{22,}', 'token'),
        
        # GitLab token
        (r'glpat-[a-zA-Z0-9_\-]{20,}', 'token'),
        
        # Slack token
        (r'xox[baprs]-[a-zA-Z0-9\-]{10,}', 'token'),
        
        # Stripe key
        (r'sk_live_[a-zA-Z0-9]{24,}', 'api_key'),
        (r'rk_live_[a-zA-Z0-9]{24,}', 'api_key'),
        
        # Generic secret patterns
        (r'(?i)(secret[_-]?key|secretkey)["\s:=]+["\']?([a-zA-Z0-9_\-]{16,64})["\']?', 'secret'),
    ]
    
    # AWS Keys
    AWS_PATTERNS = [
        # Access Key ID
        (r'AKIA[0-9A-Z]{16}', 'aws_key'),
        # Secret Access Key (40 char base64-like)
        (r'(?i)(aws[_-]?secret[_-]?access[_-]?key)["\s:=]+["\']?([A-Za-z0-9/+=]{40})["\']?', 'aws_key'),
    ]
    
    # Password patterns
    PASSWORD_PATTERNS = [
        # URL credentials
        (r'(?i)://([^:]+):([^@]+)@', 'url_credentials'),
        # Password in config
        (r'(?i)(password|passwd|pwd)["\s:=]+["\']?([^\s"\']{4,})["\']?', 'password'),
    ]
    
    # Private keys
    PRIVATE_KEY_PATTERN = r'-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----[\s\S]+?-----END (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----'
    
    # JWT tokens
    JWT_PATTERN = r'eyJ[a-zA-Z0-9_\-]*\.eyJ[a-zA-Z0-9_\-]*\.[a-zA-Z0-9_\-]*'
    
    # Connection strings
    CONNECTION_STRING_PATTERNS = [
        # PostgreSQL
        (r'postgres(?:ql)?://[^:]+:[^@]+@[^\s]+', 'connection_string'),
        # MySQL
        (r'mysql://[^:]+:[^@]+@[^\s]+', 'connection_string'),
        # MongoDB
        (r'mongodb(?:\+srv)?://[^:]+:[^@]+@[^\s]+', 'connection_string'),
        # Redis
        (r'redis://[^:]*:[^@]+@[^\s]+', 'connection_string'),
        # Generic DB
        (r'(?i)(connection[_-]?string|connstring)["\s:=]+["\']?([^\s"\']+)["\']?', 'connection_string'),
    ]
    
    # PII Patterns
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    IP_PATTERN = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    CREDIT_CARD_PATTERN = r'\b(?:\d{4}[\s-]?){3}\d{4}\b'
    SSN_PATTERN = r'\b\d{3}[\s-]?\d{2}[\s-]?\d{4}\b'
    PHONE_PATTERN = r'\b(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'


# ============================================================================
# MAIN SANITIZER CLASS
# ============================================================================

class ContentSanitizer:
    """
    Comprehensive content sanitizer for security and privacy compliance.
    
    Usage:
        sanitizer = ContentSanitizer()
        result = sanitizer.sanitize("content with sk-1234567890 api key")
        
        print(result.sanitized)  # "content with [REDACTED_api_key:abc12345] api key"
        print(result.risk_score)  # 85 (high risk detected)
    
    Features:
    - Multiple API key format detection
    - Password and credential redaction
    - PII detection with correlation hashes
    - Configurable redaction levels
    - Audit logging support
    """
    
    def __init__(self, config: Optional[SanitizationConfig] = None):
        """Initialize sanitizer with optional configuration."""
        self.config = config or SanitizationConfig()
        self._compile_patterns()
        
    def _compile_patterns(self):
        """Pre-compile regex patterns for performance."""
        self._compiled_patterns: List[Tuple[re.Pattern, RedactionType]] = []
        
        # API Key patterns
        if self.config.redact_api_keys:
            for pattern, rtype in SanitizationPatterns.API_KEY_PATTERNS:
                try:
                    self._compiled_patterns.append(
                        (re.compile(pattern), RedactionType(rtype))
                    )
                except Exception as e:
                    logger.warning(f"Failed to compile pattern {pattern}: {e}")
        
        # AWS patterns
        if self.config.redact_aws_keys:
            for pattern, rtype in SanitizationPatterns.AWS_PATTERNS:
                try:
                    self._compiled_patterns.append(
                        (re.compile(pattern), RedactionType(rtype))
                    )
                except Exception as e:
                    logger.warning(f"Failed to compile AWS pattern {pattern}: {e}")
        
        # Password patterns
        if self.config.redact_passwords:
            for pattern, rtype in SanitizationPatterns.PASSWORD_PATTERNS:
                try:
                    self._compiled_patterns.append(
                        (re.compile(pattern), RedactionType(rtype))
                    )
                except Exception as e:
                    logger.warning(f"Failed to compile password pattern {pattern}: {e}")
        
        # Connection strings
        if self.config.redact_connection_strings:
            for pattern, rtype in SanitizationPatterns.CONNECTION_STRING_PATTERNS:
                try:
                    self._compiled_patterns.append(
                        (re.compile(pattern), RedactionType(rtype))
                    )
                except Exception as e:
                    logger.warning(f"Failed to compile connection string pattern: {e}")
    
    def sanitize(self, content: str) -> SanitizationResult:
        """
        Sanitize content by detecting and redacting sensitive information.
        
        Args:
            content: The content to sanitize
            
        Returns:
            SanitizationResult with sanitized content and metadata
        """
        result = SanitizationResult(
            sanitized=content,
            original_length=len(content)
        )
        
        # Apply each pattern type
        self._apply_patterns(result)
        self._apply_pii_patterns(result)
        self._apply_private_key_pattern(result)
        self._apply_jwt_pattern(result)
        
        # Calculate final metrics
        result.sanitized_length = len(result.sanitized)
        result.redaction_counts = self._count_by_type(result.redactions)
        result.risk_score = self._calculate_risk_score(result)
        result.risk_level = self._determine_risk_level(result.risk_score)
        
        # Log if enabled
        if self.config.log_redactions and result.redactions:
            self._log_redactions(result)
        
        return result
    
    def _apply_patterns(self, result: SanitizationResult) -> None:
        """Apply compiled patterns to content."""
        for pattern, rtype in self._compiled_patterns:
            matches = list(pattern.finditer(result.sanitized))
            
            for match in reversed(matches):  # Reverse to preserve positions
                # Get the matched groups
                if match.groups():
                    # Use the last group as the sensitive part
                    sensitive_start = match.start(match.lastindex or 0)
                    sensitive_end = match.end(match.lastindex or 0)
                    sensitive_value = match.group(match.lastindex or 0)
                else:
                    sensitive_start = match.start()
                    sensitive_end = match.end()
                    sensitive_value = match.group(0)
                
                # Create redaction record
                replacement = self._create_replacement(rtype, sensitive_value)
                record = RedactionRecord(
                    type=rtype,
                    original_preview=self._get_preview(sensitive_value),
                    position=(sensitive_start, sensitive_end),
                    replacement=replacement
                )
                result.redactions.append(record)
                
                # Apply redaction
                result.sanitized = (
                    result.sanitized[:sensitive_start] +
                    replacement +
                    result.sanitized[sensitive_end:]
                )
    
    def _apply_pii_patterns(self, result: SanitizationResult) -> None:
        """Apply PII detection patterns."""
        
        # Email addresses
        if self.config.redact_emails:
            self._apply_single_pattern(
                result,
                SanitizationPatterns.EMAIL_PATTERN,
                RedactionType.EMAIL
            )
        
        # IP addresses
        if self.config.redact_ip_addresses:
            self._apply_single_pattern(
                result,
                SanitizationPatterns.IP_PATTERN,
                RedactionType.IP_ADDRESS
            )
        
        # Credit cards
        if self.config.redact_credit_cards:
            self._apply_single_pattern(
                result,
                SanitizationPatterns.CREDIT_CARD_PATTERN,
                RedactionType.CREDIT_CARD
            )
        
        # SSN
        if self.config.redact_ssn:
            self._apply_single_pattern(
                result,
                SanitizationPatterns.SSN_PATTERN,
                RedactionType.SSN
            )
        
        # Phone numbers
        if self.config.redact_phones:
            self._apply_single_pattern(
                result,
                SanitizationPatterns.PHONE_PATTERN,
                RedactionType.PHONE
            )
    
    def _apply_single_pattern(
        self,
        result: SanitizationResult,
        pattern: str,
        rtype: RedactionType
    ) -> None:
        """Apply a single pattern to content."""
        try:
            regex = re.compile(pattern)
            matches = list(regex.finditer(result.sanitized))
            
            for match in reversed(matches):
                sensitive_value = match.group(0)
                replacement = self._create_replacement(rtype, sensitive_value)
                
                record = RedactionRecord(
                    type=rtype,
                    original_preview=self._get_preview(sensitive_value),
                    position=(match.start(), match.end()),
                    replacement=replacement
                )
                result.redactions.append(record)
                
                result.sanitized = (
                    result.sanitized[:match.start()] +
                    replacement +
                    result.sanitized[match.end():]
                )
        except Exception as e:
            logger.warning(f"Failed to apply PII pattern {rtype}: {e}")
    
    def _apply_private_key_pattern(self, result: SanitizationResult) -> None:
        """Detect and redact private keys."""
        if not self.config.redact_private_keys:
            return
            
        try:
            pattern = re.compile(SanitizationPatterns.PRIVATE_KEY_PATTERN, re.DOTALL)
            matches = list(pattern.finditer(result.sanitized))
            
            for match in reversed(matches):
                replacement = self._create_replacement(RedactionType.PRIVATE_KEY, "[PRIVATE_KEY]")
                
                record = RedactionRecord(
                    type=RedactionType.PRIVATE_KEY,
                    original_preview="[PRIVATE_KEY_BLOCK]",
                    position=(match.start(), match.end()),
                    replacement=replacement
                )
                result.redactions.append(record)
                
                result.sanitized = (
                    result.sanitized[:match.start()] +
                    replacement +
                    result.sanitized[match.end():]
                )
        except Exception as e:
            logger.warning(f"Failed to apply private key pattern: {e}")
    
    def _apply_jwt_pattern(self, result: SanitizationResult) -> None:
        """Detect and redact JWT tokens."""
        if not self.config.redact_jwt:
            return
            
        try:
            pattern = re.compile(SanitizationPatterns.JWT_PATTERN)
            matches = list(pattern.finditer(result.sanitized))
            
            for match in reversed(matches):
                replacement = self._create_replacement(RedactionType.JWT, match.group(0))
                
                record = RedactionRecord(
                    type=RedactionType.JWT,
                    original_preview=self._get_preview(match.group(0)),
                    position=(match.start(), match.end()),
                    replacement=replacement
                )
                result.redactions.append(record)
                
                result.sanitized = (
                    result.sanitized[:match.start()] +
                    replacement +
                    result.sanitized[match.end():]
                )
        except Exception as e:
            logger.warning(f"Failed to apply JWT pattern: {e}")
    
    def _create_replacement(self, rtype: RedactionType, value: str) -> str:
        """Create replacement string for redacted content."""
        if self.config.use_hash_correlation:
            hash_prefix = self._hash_value(value)[:self.config.hash_prefix_length]
            return self.config.replacement_template.format(
                type=rtype.value.upper(),
                hash=hash_prefix
            )
        else:
            return f"[REDACTED_{rtype.value.upper()}]"
    
    @staticmethod
    def _hash_value(value: str) -> str:
        """Generate SHA256 hash for correlation."""
        return hashlib.sha256(value.encode('utf-8')).hexdigest()
    
    def _get_preview(self, value: str) -> str:
        """Get preview of original value (if enabled)."""
        if self.config.log_content_preview:
            return value[:self.config.preview_length] + "..." if len(value) > self.config.preview_length else value
        return "[REDACTED]"
    
    def _count_by_type(self, redactions: List[RedactionRecord]) -> Dict[str, int]:
        """Count redactions by type."""
        counts: Dict[str, int] = {}
        for record in redactions:
            rtype = record.type.value
            counts[rtype] = counts.get(rtype, 0) + 1
        return counts
    
    def _calculate_risk_score(self, result: SanitizationResult) -> int:
        """
        Calculate risk score based on types and counts of redactions.
        
        Score weights:
        - Private keys, AWS keys: 30 points each (critical)
        - API keys, passwords, tokens: 20 points each (high)
        - Connection strings, secrets: 15 points each (medium-high)
        - SSN, credit cards: 15 points each (medium-high)
        - Email, IP, phone: 5 points each (low)
        """
        score = 0
        
        weight_map = {
            RedactionType.PRIVATE_KEY: 30,
            RedactionType.AWS_KEY: 30,
            RedactionType.API_KEY: 20,
            RedactionType.PASSWORD: 20,
            RedactionType.TOKEN: 20,
            RedactionType.SECRET: 15,
            RedactionType.CONNECTION_STRING: 15,
            RedactionType.SSN: 15,
            RedactionType.CREDIT_CARD: 15,
            RedactionType.JWT: 15,
            RedactionType.URL_CREDENTIALS: 10,
            RedactionType.EMAIL: 5,
            RedactionType.IP_ADDRESS: 5,
            RedactionType.PHONE: 5,
        }
        
        for record in result.redactions:
            score += weight_map.get(record.type, 5)
        
        # Cap at 100
        return min(score, 100)
    
    def _determine_risk_level(self, score: int) -> str:
        """Determine risk level from score."""
        if score >= self.config.high_risk_threshold:
            return "high"
        elif score >= self.config.medium_risk_threshold:
            return "medium"
        return "low"
    
    def _log_redactions(self, result: SanitizationResult) -> None:
        """Log redaction summary for audit."""
        logger.info(
            "Content sanitized",
            extra={
                "operation": "sanitization",
                "redaction_count": len(result.redactions),
                "risk_score": result.risk_score,
                "risk_level": result.risk_level,
                "redaction_types": list(result.redaction_counts.keys()),
                "original_length": result.original_length,
                "sanitized_length": result.sanitized_length,
            }
        )


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def sanitize_content(content: str, config: Optional[SanitizationConfig] = None) -> str:
    """
    Quick sanitization function that returns just the sanitized string.
    
    Args:
        content: Content to sanitize
        config: Optional sanitization configuration
        
    Returns:
        Sanitized content string
    """
    sanitizer = ContentSanitizer(config)
    result = sanitizer.sanitize(content)
    return result.sanitized


def check_content_risk(content: str) -> int:
    """
    Check risk score of content without returning sanitized version.
    
    Args:
        content: Content to check
        
    Returns:
        Risk score (0-100)
    """
    sanitizer = ContentSanitizer()
    result = sanitizer.sanitize(content)
    return result.risk_score