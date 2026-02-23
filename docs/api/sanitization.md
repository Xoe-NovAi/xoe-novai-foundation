# Content Sanitization API

> **Module**: `XNAi_rag_app.core.sanitization`
> **Version**: 1.0.0
> **Last Updated**: 2026-02-22

---

## Overview

Comprehensive content sanitization for security and privacy compliance. Detects and redacts sensitive information including API keys, credentials, PII, and private keys.

---

## Classes

### ContentSanitizer

Main class for content sanitization.

```python
from XNAi_rag_app.core.sanitization import ContentSanitizer, SanitizationConfig

# Initialize with defaults
sanitizer = ContentSanitizer()

# Or with custom configuration
config = SanitizationConfig(
    redact_api_keys=True,
    redact_passwords=True,
    redact_emails=True,
    use_hash_correlation=True
)
sanitizer = ContentSanitizer(config)
```

#### Methods

##### `sanitize()`

Sanitize content by detecting and redacting sensitive information.

```python
result = sanitizer.sanitize("""
Content with sk-1234567890 api key and
password: secretpassword123
Email: user@example.com
""")

print(result.sanitized)
# Content with [REDACTED_API_KEY:a1b2c3d4] api key and
# password: [REDACTED_PASSWORD:e5f6g7h8]
# Email: [REDACTED_EMAIL:i9j0k1l2]

print(result.risk_score)  # 45 (medium risk)
print(result.risk_level)  # "medium"
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `content` | str | Yes | The content to sanitize |

**Returns:** `SanitizationResult`

---

## Configuration

### SanitizationConfig

```python
from XNAi_rag_app.core.sanitization import SanitizationConfig

config = SanitizationConfig(
    # Enable/disable specific redactions
    redact_api_keys=True,
    redact_passwords=True,
    redact_secrets=True,
    redact_tokens=True,
    redact_emails=True,
    redact_ip_addresses=False,    # Often needed for logs
    redact_credit_cards=True,
    redact_ssn=True,
    redact_phones=False,          # Optional, may be needed
    redact_private_keys=True,
    redact_connection_strings=True,
    redact_aws_keys=True,
    redact_jwt=True,
    redact_url_credentials=True,
    
    # Redaction behavior
    use_hash_correlation=True,    # Use SHA256 hash prefix
    hash_prefix_length=8,         # Number of hash chars
    replacement_template="[REDACTED_{type}:{hash}]",
    
    # Logging
    log_redactions=True,
    log_content_preview=False,    # Security risk if True
    
    # Risk thresholds
    high_risk_threshold=70,
    medium_risk_threshold=40
)
```

---

## Data Classes

### SanitizationResult

```python
@dataclass
class SanitizationResult:
    sanitized: str              # The sanitized content
    redactions: List[RedactionRecord]  # What was redacted
    risk_score: int             # Risk assessment (0-100)
    risk_level: str             # "low", "medium", or "high"
    original_length: int
    sanitized_length: int
    timestamp: str
    redaction_counts: Dict[str, int]  # Count by type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        ...
```

### RedactionRecord

```python
@dataclass
class RedactionRecord:
    type: RedactionType         # Type of sensitive content
    original_preview: str       # Preview (if enabled)
    position: Tuple[int, int]   # Start, end position
    replacement: str            # What replaced it
    timestamp: str
```

---

## Enums

### RedactionType

```python
from XNAi_rag_app.core.sanitization import RedactionType

class RedactionType(str, Enum):
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
```

---

## Detected Patterns

### API Keys (15+ patterns)

| Service | Pattern |
|---------|---------|
| OpenAI | `sk-...` |
| Anthropic | `sk-ant-...` |
| Google | `AIza...` |
| GitHub | `ghp_...`, `github_pat_...` |
| GitLab | `glpat-...` |
| Slack | `xox[baprs]-...` |
| Stripe | `sk_live_...`, `rk_live_...` |
| AWS | `AKIA...` |
| Generic | `api_key=...`, `bearer ...` |

### Credentials

- Passwords in config files
- URL credentials (`user:pass@host`)
- Connection strings (PostgreSQL, MySQL, MongoDB, Redis)

### PII

- Email addresses
- IP addresses (optional)
- Credit card numbers
- Social Security Numbers
- Phone numbers (optional)

### Security

- RSA/EC/DSA/OpenSSH private keys
- JWT tokens

---

## Risk Scoring

| Content Type | Points |
|--------------|--------|
| Private keys, AWS keys | 30 (critical) |
| API keys, passwords, tokens | 20 (high) |
| Connection strings, SSN, credit cards | 15 (medium-high) |
| JWT, URL credentials | 10-15 |
| Email, IP, phone | 5 (low) |

**Risk Levels:**
- **High**: Score ≥ 70
- **Medium**: Score ≥ 40
- **Low**: Score < 40

---

## Convenience Functions

### `sanitize_content()`

Quick function that returns just the sanitized string.

```python
from XNAi_rag_app.core.sanitization import sanitize_content

sanitized = sanitize_content("content with sk-1234567890")
# "content with [REDACTED_API_KEY:a1b2c3d4]"
```

### `check_content_risk()`

Check risk score without returning sanitized version.

```python
from XNAi_rag_app.core.sanitization import check_content_risk

risk = check_content_risk("content with api_key=secret123")
# Returns risk score (0-100)
```

---

## Integration Example

```python
from XNAi_rag_app.core.sanitization import ContentSanitizer, SanitizationConfig

async def process_user_input(content: str) -> dict:
    """Process user input with sanitization."""
    config = SanitizationConfig(
        redact_api_keys=True,
        redact_passwords=True,
        log_redactions=True
    )
    
    sanitizer = ContentSanitizer(config)
    result = sanitizer.sanitize(content)
    
    # Check risk level
    if result.risk_level == "high":
        logger.warning(
            f"High risk content detected",
            extra={
                "risk_score": result.risk_score,
                "redaction_types": list(result.redaction_counts.keys())
            }
        )
    
    return {
        "sanitized_content": result.sanitized,
        "risk_score": result.risk_score,
        "risk_level": result.risk_level,
        "redaction_count": len(result.redactions)
    }
```

---

## Best Practices

1. **Always sanitize before logging**: Prevent accidental credential exposure
2. **Check risk scores**: High scores may indicate compromised content
3. **Use hash correlation**: Enables tracking without exposing originals
4. **Configure appropriately**: Disable redactions you don't need
5. **Log redactions**: Audit trail for security compliance

---

## Related Modules

- [`knowledge_access`](./knowledge_access.md) - Knowledge access control
- [`redis_streams`](./redis_streams.md) - Redis stream management

---

**Source**: `app/XNAi_rag_app/core/sanitization/sanitizer.py`
