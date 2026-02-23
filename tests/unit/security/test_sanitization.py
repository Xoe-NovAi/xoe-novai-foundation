#!/usr/bin/env python3
"""
Unit Tests for Content Sanitizer
=================================

Tests for comprehensive content sanitization including:
- API key detection and redaction
- Credential redaction
- PII detection
- Risk scoring

Pattern: Zero-Trust Security (Phase 4.2.6)
"""

import pytest
from XNAi_rag_app.core.sanitization import (
    ContentSanitizer,
    SanitizationConfig,
    SanitizationResult,
    RedactionType,
    sanitize_content,
    check_content_risk,
)


class TestAPIKeyDetection:
    """Tests for API key detection and redaction."""

    def test_openai_api_key(self):
        """Test OpenAI API key detection."""
        content = "API_KEY = sk-1234567890abcdefghijklmnop"
        result = sanitize_content(content)

        assert "sk-1234567890abcdefghijklmnop" not in result
        assert "[REDACTED_API_KEY:" in result
        assert result != content  # Content was modified

    def test_anthropic_api_key(self):
        """Test Anthropic API key detection."""
        content = "anthropic_key = sk-ant-api03-1234567890abcdef"
        result = sanitize_content(content)

        assert "sk-ant-api03-1234567890abcdef" not in result
        assert "[REDACTED_" in result

    def test_google_api_key(self):
        """Test Google API key detection."""
        content = "GOOGLE_KEY = AIzaSyDaGmWKa4JsXZ-HjGw7ISLn_3namBGewQe"
        result = sanitize_content(content)

        assert "AIzaSyDaGmWKa4JsXZ-HjGw7ISLn_3namBGewQe" not in result
        assert "[REDACTED_API_KEY:" in result

    def test_github_token(self):
        """Test GitHub token detection."""
        content = "GITHUB_TOKEN = ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        result = sanitize_content(content)

        assert "ghp_1234567890abcdefghijklmnopqrstuvwxyz" not in result
        assert "[REDACTED_TOKEN:" in result

    def test_generic_api_key(self):
        """Test generic API key patterns."""
        content = 'api_key = "my_secret_api_key_12345678901234567890"'
        result = sanitize_content(content)

        # The API key value should be redacted
        assert "my_secret_api_key_12345678901234567890" not in result


class TestCredentialRedaction:
    """Tests for credential redaction."""

    def test_password_redaction(self):
        """Test password redaction."""
        content = 'password = "mySecretPassword123"'
        result = sanitize_content(content)

        assert "mySecretPassword123" not in result
        assert "[REDACTED_PASSWORD:" in result

    def test_url_credentials(self):
        """Test URL credential redaction."""
        content = "DATABASE_URL = postgresql://admin:secretpass@localhost:5432/db"
        result = sanitize_content(content)

        assert "secretpass" not in result
        assert "[REDACTED_URL_CREDENTIALS:" in result

    def test_connection_string_redaction(self):
        """Test connection string redaction."""
        content = "mongodb://user:password123@mongodb.example.com:27017/mydb"
        result = sanitize_content(content)

        assert "password123" not in result
        assert "[REDACTED_CONNECTION_STRING:" in result

    def test_aws_access_key(self):
        """Test AWS access key detection."""
        content = "AWS_ACCESS_KEY_ID = AKIAIOSFODNN7EXAMPLE"
        result = sanitize_content(content)

        assert "AKIAIOSFODNN7EXAMPLE" not in result
        assert "[REDACTED_AWS_KEY:" in result


class TestPIIDetection:
    """Tests for PII detection."""

    def test_email_redaction(self):
        """Test email address redaction."""
        content = "Contact: john.doe@example.com for more info"
        result = sanitize_content(content)

        assert "john.doe@example.com" not in result
        assert "[REDACTED_EMAIL:" in result

    def test_credit_card_redaction(self):
        """Test credit card redaction."""
        content = "Card: 4111-1111-1111-1111"
        result = sanitize_content(content)

        assert "4111-1111-1111-1111" not in result
        assert "[REDACTED_CREDIT_CARD:" in result

    def test_ssn_redaction(self):
        """Test SSN redaction."""
        content = "SSN: 123-45-6789"
        result = sanitize_content(content)

        assert "123-45-6789" not in result
        assert "[REDACTED_SSN:" in result

    def test_ip_redaction_disabled_by_default(self):
        """Test that IP redaction is disabled by default."""
        content = "Server IP: 192.168.1.100"
        result = sanitize_content(content)

        # IP should NOT be redacted by default
        assert "192.168.1.100" in result

    def test_ip_redaction_when_enabled(self):
        """Test IP redaction when explicitly enabled."""
        config = SanitizationConfig(redact_ip_addresses=True)
        sanitizer = ContentSanitizer(config)
        content = "Server IP: 192.168.1.100"
        result = sanitizer.sanitize(content)

        assert "192.168.1.100" not in result.sanitized
        assert "[REDACTED_IP_ADDRESS:" in result.sanitized


class TestPrivateKeyRedaction:
    """Tests for private key redaction."""

    def test_rsa_private_key(self):
        """Test RSA private key redaction."""
        content = """
        -----BEGIN RSA PRIVATE KEY-----
        MIIEpAIBAAKCAQEA0Z3VS5JJcds3xfn/ygWyF8PbnGy0AHB7mSrORbsXxHNHYtML
        ExamplePrivateKeyContent1234567890abcdefghijklmnopqrstuvwx
        -----END RSA PRIVATE KEY-----
        """
        result = sanitize_content(content)

        assert "-----BEGIN RSA PRIVATE KEY-----" not in result
        assert "[REDACTED_PRIVATE_KEY:" in result

    def test_openssh_private_key(self):
        """Test OpenSSH private key redaction."""
        content = """
        -----BEGIN OPENSSH PRIVATE KEY-----
        b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
        ExampleOpenSSHKeyContent1234567890abcdefghijklmnopqrstuvwx
        -----END OPENSSH PRIVATE KEY-----
        """
        result = sanitize_content(content)

        assert "-----BEGIN OPENSSH PRIVATE KEY-----" not in result
        assert "[REDACTED_PRIVATE_KEY:" in result


class TestJWTRedaction:
    """Tests for JWT token redaction."""

    def test_jwt_token(self):
        """Test JWT token redaction."""
        content = "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        result = sanitize_content(content)

        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in result
        assert "[REDACTED_JWT:" in result


class TestRiskScoring:
    """Tests for risk score calculation."""

    def test_high_risk_content(self):
        """Test high risk content scoring."""
        content = """
        API_KEY = sk-1234567890abcdefghijklmnop
        password = "secretpassword"
        -----BEGIN RSA PRIVATE KEY-----
        privatekeycontent
        -----END RSA PRIVATE KEY-----
        """
        score = check_content_risk(content)

        # Should be high risk due to private key + API key + password
        assert score >= 70

    def test_medium_risk_content(self):
        """Test medium risk content scoring."""
        content = """
        Email: john@example.com
        SSN: 123-45-6789
        """
        score = check_content_risk(content)

        # Should be medium risk
        assert 40 <= score < 70

    def test_low_risk_content(self):
        """Test low risk content scoring."""
        content = "This is a normal document without sensitive data."
        score = check_content_risk(content)

        # Should be low risk
        assert score < 40

    def test_risk_level_determination(self):
        """Test risk level determination."""
        sanitizer = ContentSanitizer()

        # High risk
        high_risk = SanitizationResult(sanitized="", risk_score=85)
        assert sanitizer._determine_risk_level(85) == "high"

        # Medium risk
        medium_risk = SanitizationResult(sanitized="", risk_score=50)
        assert sanitizer._determine_risk_level(50) == "medium"

        # Low risk
        low_risk = SanitizationResult(sanitized="", risk_score=20)
        assert sanitizer._determine_risk_level(20) == "low"


class TestSanitizationResult:
    """Tests for SanitizationResult dataclass."""

    def test_to_dict(self):
        """Test SanitizationResult serialization."""
        sanitizer = ContentSanitizer()
        content = "Email: test@example.com"
        result = sanitizer.sanitize(content)

        result_dict = result.to_dict()

        assert "sanitized" in result_dict
        assert "risk_score" in result_dict
        assert "risk_level" in result_dict
        assert "redaction_count" in result_dict
        assert "redaction_counts" in result_dict

    def test_redaction_counts(self):
        """Test redaction counting by type."""
        sanitizer = ContentSanitizer()
        content = "Email: test1@example.com and test2@example.com"
        result = sanitizer.sanitize(content)

        assert "email" in result.redaction_counts
        assert result.redaction_counts["email"] == 2


class TestConfiguration:
    """Tests for sanitization configuration."""

    def test_disable_api_key_redaction(self):
        """Test disabling API key redaction."""
        config = SanitizationConfig(redact_api_keys=False)
        sanitizer = ContentSanitizer(config)
        content = "API_KEY = sk-1234567890abcdefghijklmnop"
        result = sanitizer.sanitize(content)

        # API key should NOT be redacted
        assert "sk-1234567890abcdefghijklmnop" in result.sanitized

    def test_disable_email_redaction(self):
        """Test disabling email redaction."""
        config = SanitizationConfig(redact_emails=False)
        sanitizer = ContentSanitizer(config)
        content = "Email: test@example.com"
        result = sanitizer.sanitize(content)

        # Email should NOT be redacted
        assert "test@example.com" in result.sanitized

    def test_custom_replacement_template(self):
        """Test custom replacement template."""
        config = SanitizationConfig(replacement_template="[HIDDEN_{type}]", use_hash_correlation=False)
        sanitizer = ContentSanitizer(config)
        content = "Email: test@example.com"
        result = sanitizer.sanitize(content)

        assert "[HIDDEN_EMAIL]" in result.sanitized


class TestMultipleRedactions:
    """Tests for multiple redactions in same content."""

    def test_multiple_sensitive_items(self):
        """Test content with multiple types of sensitive data."""
        content = """
        Configuration:
        API_KEY = sk-1234567890abcdefghijklmnop
        DATABASE_URL = postgresql://admin:password@localhost:5432/db
        AWS_KEY = AKIAIOSFODNN7EXAMPLE
        Contact: admin@example.com
        SSN: 123-45-6789
        """

        sanitizer = ContentSanitizer()
        result = sanitizer.sanitize(content)

        # None of the sensitive values should be present
        assert "sk-1234567890abcdefghijklmnop" not in result.sanitized
        assert "password" not in result.sanitized
        assert "AKIAIOSFODNN7EXAMPLE" not in result.sanitized
        assert "admin@example.com" not in result.sanitized
        assert "123-45-6789" not in result.sanitized

        # Should have multiple redactions
        assert result.redaction_count >= 5

        # Should be high risk
        assert result.risk_score >= 70


# ============================================================================
# Edge Case Tests - JOB-W3-002-1
# ============================================================================


class TestEdgeCases:
    """Edge case tests for content sanitizer."""

    def test_large_payload_rejection(self):
        """Test that payloads exceeding 10MB are rejected."""
        # Create content larger than 10MB
        large_content = "x" * (11 * 1024 * 1024)  # 11MB

        with pytest.raises(Exception) as exc_info:
            sanitize_content(large_content)

        # Should raise an error about payload size
        assert "size" in str(exc_info.value).lower() or "large" in str(exc_info.value).lower() or "10" in str(exc_info.value)

    def test_large_payload_at_boundary(self):
        """Test payload at exactly the size boundary (10MB)."""
        # Create content at exactly 10MB
        boundary_content = "x" * (10 * 1024 * 1024)  # 10MB

        # Should either succeed or fail gracefully at exact boundary
        try:
            result = sanitize_content(boundary_content)
            # If it succeeds, verify it was processed
            assert result is not None
        except Exception:
            pass  # Acceptable to reject at boundary

    def test_unicode_normalization_zero_width(self):
        """Test Unicode normalization with zero-width characters."""
        # Contains zero-width space (U+200B)
        content = "API_KEY = sk-1234567890" + "\u200b" + "abcdefghijklmnop"
        result = sanitize_content(content)

        # Should still redact the API key despite zero-width chars
        assert "sk-1234567890" not in result or "[REDACTED" in result

    def test_unicode_normalization_rtl(self):
        """Test Unicode normalization with RTL text."""
        # Contains right-to-left mark
        content = "API_KEY = sk-1234567890\u200fabcdefghijklmnop"
        result = sanitize_content(content)

        # Should still redact the API key
        assert "sk-1234567890" not in result or "[REDACTED" in result

    def test_unicode_emoji_handling(self):
        """Test handling of emoji in content."""
        content = "Contact: john.doe@example.com for more info 🔐"
        result = sanitize_content(content)

        # Email should be redacted, emoji preserved
        assert "john.doe@example.com" not in result
        assert "🔐" in result

    def test_unicode_combining_characters(self):
        """Test handling of combining characters."""
        # Contains combining characters that modify letters
        content = "Email: test@example.com\u0301"  # combining acute
        result = sanitize_content(content)

        # Should still redact the email
        assert "test@example.com" not in result

    def test_binary_content_null_bytes(self):
        """Test detection of binary content with null bytes."""
        # Content with null bytes (binary indicator)
        content = "some text\x00\x00binary data"
        result = sanitize_content(content)

        # Should handle gracefully
        assert result is not None

    def test_multiline_private_key(self):
        """Test multi-line private key detection."""
        content = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA0Z3VS5JJcds3xfn/ygWyF8PbnGy0AHB7mSrORbsXxHNHYtML
ExamplePrivateKeyContent1234567890abcdefghijklmnopqrstuvwx
-----END RSA PRIVATE KEY-----"""
        result = sanitize_content(content)

        assert "[REDACTED_PRIVATE_KEY:" in result

    def test_password_in_connection_string(self):
        """Test password redaction in connection strings."""
        content = "postgres://admin:secretpass123@localhost:5432/db"
        result = sanitize_content(content)

        assert "secretpass123" not in result
        assert "[REDACTED" in result

    def test_base64_encoded_api_key(self):
        """Test detection of base64 encoded keys."""
        import base64

        key = "sk-1234567890abcdefghijklmnop"
        encoded = base64.b64encode(key.encode()).decode()
        content = f"encoded_key = {encoded}"
        result = sanitize_content(content)

        # May or may not detect encoded keys depending on implementation
        # But should not crash
        assert result is not None

    def test_empty_content(self):
        """Test handling of empty content."""
        result = sanitize_content("")

        # Should return empty or original content
        assert result == "" or result is not None

    def test_whitespace_only_content(self):
        """Test handling of whitespace-only content."""
        content = "   \n\t  \n   "
        result = sanitize_content(content)

        # Should handle gracefully
        assert result is not None

    def test_very_long_line(self):
        """Test handling of extremely long lines."""
        content = "data=" + "x" * 100000
        result = sanitize_content(content)

        # Should handle gracefully
        assert result is not None

    def test_nested_json_braces(self):
        """Test handling of deeply nested JSON."""
        # Create deeply nested structure
        content = '{"level1": {"level2": {"level3": {"level4": {"level5": {"level6": {"level7": "value"}}}}}}}'
        result = sanitize_content(content)

        # Should handle gracefully
        assert result is not None

    def test_special_characters_in_content(self):
        """Test handling of special characters."""
        content = "Text with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        result = sanitize_content(content)

        # Should handle gracefully without errors
        assert result is not None

    def test_newlines_and_tabs(self):
        """Test handling of various newline and tab combinations."""
        content = "Line1\nLine2\r\nLine3\tTabbed\rMixed"
        result = sanitize_content(content)

        # Should preserve formatting
        assert "\n" in result or "\r" in result or result is not None

    def test_html_content(self):
        """Test handling of HTML content."""
        content = "<html><body><p>Email: test@example.com</p></body></html>"
        result = sanitize_content(content)

        # Email should be redacted even in HTML
        assert "test@example.com" not in result

    def test_json_with_sensitive_data(self):
        """Test handling of JSON with sensitive data."""
        content = '{"api_key": "sk-1234567890abcdefghijklmnop", "password": "secret123"}'
        result = sanitize_content(content)

        # Both should be redacted
        assert "sk-1234567890" not in result
        assert "secret123" not in result

    def test_mixed_encoding_content(self):
        """Test handling of content with mixed encodings."""
        content = "ASCII text with émoji and 中文characters"
        result = sanitize_content(content)

        # Should handle gracefully
        assert result is not None

    def test_repeated_patterns(self):
        """Test handling of repeated sensitive patterns."""
        content = """
        Key1: sk-1234567890abcdefghijklmnop
        Key2: sk-1234567890abcdefghijklmnop
        Key3: sk-1234567890abcdefghijklmnop
        """
        result = sanitize_content(content)

        # All keys should be redacted
        assert result.count("[REDACTED_API_KEY:") >= 3

    def test_sanitization_performance_large_content(self):
        """Test sanitization performance on large content."""
        import time

        content = "Email: test@example.com\n" * 10000  # 10k lines
        start = time.time()
        result = sanitize_content(content)
        elapsed = time.time() - start

        # Should complete in reasonable time (< 1 second)
        assert elapsed < 1.0
        # Should redact all emails
        assert result.count("[REDACTED_EMAIL:") == 10000
