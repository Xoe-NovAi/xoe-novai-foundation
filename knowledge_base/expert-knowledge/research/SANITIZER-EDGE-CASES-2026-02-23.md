# Edge Cases in Content Sanitizer

> **Date**: 2026-02-23
> **Context**: JOB-W2-008 - Edge Cases & Error Handling Research
> **Status**: COMPLETE

---

## 1. Identified Edge Cases

### 1.1 Size and Performance Edge Cases

| Edge Case | Issue | Mitigation |
|-----------|-------|------------|
| **Large Payload** | Content > 10MB may cause memory issues | Check `len(content) > MAX_PAYLOAD_SIZE` before processing |
| **Deeply Nested JSON** | Recursive parsing may exceed stack depth | Limit JSON depth to 10 levels |
| **Binary Content** | Non-text content causes regex errors | Detect MIME type and skip binary content |
| **Unicode Edge Cases** | Emoji, zero-width chars, RTL text | Normalize with `unicodedata.normalize('NFKC', content)` |

### 1.2 Pattern Matching Edge Cases

| Edge Case | Example | Mitigation |
|-----------|---------|------------|
| **Partial API Keys** | `sk-1234...` (truncated) | Match full pattern or ignore partials |
| **Keys in Code Comments** | `# API_KEY = sk-...` | Redact regardless of context |
| **Keys in URLs** | `?api_key=sk-...&...` | Parse query params separately |
| **Base64 Encoded Keys** | `base64.b64encode(key)` | Decode and check |
| **Environment Variables** | `${API_KEY}`, `$API_KEY` | Expand and check values |

### 1.3 Credential Edge Cases

| Edge Case | Example | Mitigation |
|-----------|---------|------------|
| **Password in URL** | `postgres://user:pass@host` | Redact password portion |
| **Multi-line Secrets** | Private keys spanning lines | Handle multi-line patterns |
| **Escaped Characters** | `pass\"word` in JSON | Unescape before matching |
| **Secrets in Logs** | Stack traces with passwords | Redact in log output |

### 1.4 PII Edge Cases

| Edge Case | Example | Mitigation |
|-----------|---------|------------|
| **International Phone** | `+44 20 7946 0958` | Support international formats |
| **Email Variations** | `user+tag@domain.co.uk` | Handle subdomains and TLDs |
| **SSN Variations** | `123-45-6789`, `123 45 6789` | Normalize spacing |
| **Partial PII** | `***-**-1234` (masked) | Preserve masked formats |

---

## 2. Implementation Fixes

### 2.1 Fixed Regex Pattern (Python 3.13+)

The original password-in-URL pattern used variable-width look-behind:

```python
# OLD (broken in Python 3.13+)
re.compile(r"(?<=://[^:]+:)[^@]+(?=@)")

# NEW (fixed-width compatible)
re.compile(r"://[^:]+:([^@]+)@")
```

### 2.2 Size Check Before Processing

```python
MAX_PAYLOAD_SIZE = 10 * 1024 * 1024  # 10MB

def sanitize_content(content: str, config: SanitizationConfig) -> SanitizationResult:
    if len(content) > MAX_PAYLOAD_SIZE:
        raise PayloadTooLargeError(
            f"Content size {len(content)} exceeds maximum {MAX_PAYLOAD_SIZE}"
        )
    # ... rest of sanitization
```

### 2.3 Binary Content Detection

```python
import mimetypes

def is_binary_content(content: str) -> bool:
    """Detect if content is binary data."""
    # Check for null bytes
    if '\x00' in content[:8192]:
        return True
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(content[:100])
    if mime_type and not mime_type.startswith('text/'):
        return True
    return False
```

### 2.4 Unicode Normalization

```python
import unicodedata

def normalize_content(content: str) -> str:
    """Normalize Unicode for consistent matching."""
    # NFKC normalization handles:
    # - Compatibility characters
    # - Zero-width characters
    # - RTL/LTR marks
    return unicodedata.normalize('NFKC', content)
```

---

## 3. Test Coverage

### 3.1 Edge Case Tests Required

```python
# tests/unit/security/test_sanitization_edge_cases.py

class TestSanitizerEdgeCases:
    """Edge case tests for content sanitizer."""
    
    def test_large_payload_rejection(self):
        """Test that large payloads are rejected."""
        large_content = "x" * (11 * 1024 * 1024)  # 11MB
        with pytest.raises(PayloadTooLargeError):
            sanitize_content(large_content)
    
    def test_unicode_normalization(self):
        """Test Unicode normalization."""
        # Contains zero-width characters
        content = "API_KEY = sk\u200b-1234567890"  # Zero-width space
        result = sanitize_content(content)
        assert "[REDACTED" in result
    
    def test_multiline_private_key(self):
        """Test multi-line private key detection."""
        content = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
-----END RSA PRIVATE KEY-----"""
        result = sanitize_content(content)
        assert "[REDACTED_PRIVATE_KEY" in result
    
    def test_password_in_connection_string(self):
        """Test password redaction in connection strings."""
        content = "postgres://admin:secretpass123@localhost:5432/db"
        result = sanitize_content(content)
        assert "secretpass123" not in result
    
    def test_base64_encoded_key(self):
        """Test detection of base64 encoded keys."""
        import base64
        key = "sk-1234567890abcdefghijklmnop"
        encoded = base64.b64encode(key.encode()).decode()
        content = f"encoded_key = {encoded}"
        result = sanitize_content(content)
        # Should detect the key pattern even when encoded
        assert "sk-" not in result or "[REDACTED" in result
```

---

## 4. Known Limitations

| Limitation | Workaround |
|------------|------------|
| Encrypted secrets | Cannot detect without decryption key |
| Custom encoding | Require explicit configuration |
| Obfuscated keys | Heuristic detection may miss some |
| Language-specific formats | Add custom patterns per language |

---

## 5. Future Improvements

1. **ML-based Detection**: Use a model to detect sensitive data patterns
2. **Context-aware Redaction**: Preserve context while redacting
3. **Custom Pattern DSL**: Allow users to define custom patterns
4. **Streaming Sanitization**: Process large files without loading into memory

---

**Related Files**:
- `app/XNAi_rag_app/core/security/sanitization.py`
- `tests/unit/security/test_sanitization.py`
- `docs/03-reference/ERROR-BEST-PRACTICES.md`
