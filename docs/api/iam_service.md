# IAM Service API Reference

> **Generated**: 2026-02-21  
> **Source**: `app/XNAi_rag_app/core/iam_service.py`  
> **Version**: 1.1.0

---

## Overview

The IAM (Identity & Access Management) service provides enterprise-grade authentication and authorization for the XNAi Foundation Stack. It implements a Zero-Trust security model with JWT-based authentication, RBAC/ABAC policies, and MFA support.

> **Note**: The IAM service is implemented but not currently exposed as FastAPI routes. For now, it provides authentication dependency injection for internal use.

---

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| JWT Authentication | ✅ | RS256-signed tokens |
| RBAC | ✅ | Role-based access control |
| ABAC | ✅ | Attribute-based policies |
| MFA Support | ✅ | TOTP-based 2FA |
| Refresh Tokens | ✅ | Long-lived refresh tokens |
| Audit Logging | ✅ | Compliance tracking |
| Rate Limiting | ✅ | Login attempt tracking |
| Password Policy | ✅ | Strength enforcement |

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MFA_ENABLED` | `true` | Enable multi-factor authentication |
| `IAM_DB_PATH` | `data/iam.db` | SQLite database path |
| `IAM_CREATE_DEFAULT_ADMIN` | `false` | Create default admin on startup |

### JWT Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Algorithm | `RS256` | Asymmetric signing |
| Access Token Expiry | 15 minutes | Short-lived access |
| Refresh Token Expiry | 7 days | Long-lived refresh |

### Password Policy

| Rule | Default |
|------|---------|
| Minimum Length | 8 characters |
| Require Uppercase | Yes |
| Require Lowercase | Yes |
| Require Numbers | Yes |
| Require Special Chars | No |

### Session Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Max Concurrent Sessions | 5 | Per user |
| Session Timeout | 480 minutes | 8 hours |
| Max Login Attempts | 5 | Before lockout |
| Lockout Duration | 30 minutes | After max attempts |

---

## User Roles

| Role | Description | Default Permissions |
|------|-------------|-------------------|
| `admin` | Full system access | All permissions |
| `user` | Standard user | Basic RAG, voice |
| `service` | Service-to-service | API access |
| `auditor` | Read-only access | Monitoring only |

---

## Permissions

### Voice Permissions
| Permission | Description |
|------------|-------------|
| `voice:use` | Use voice interface |
| `voice:admin` | Manage voice settings |

### RAG Permissions
| Permission | Description |
|------------|-------------|
| `rag:query` | Query RAG system |
| `rag:ingest` | Ingest documents |
| `rag:admin` | Manage RAG configuration |

### LLM Permissions
| Permission | Description |
|------------|-------------|
| `llm:inference` | Run inference |
| `llm:train` | Fine-tune models |
| `llm:admin` | Manage LLM settings |

### System Permissions
| Permission | Description |
|------------|-------------|
| `system:monitor` | View monitoring |
| `system:admin` | Full system access |

---

## Data Models

### User

```python
@dataclass
class User:
    username: str              # Unique identifier
    email: str                # User email
    full_name: str            # Display name
    password_hash: str        # bcrypt hash
    roles: List[UserRole]    # Assigned roles
    permissions: List[Permission]  # Direct permissions
    disabled: bool            # Account disabled flag
    mfa_enabled: bool        # MFA enabled
    mfa_secret: Optional[str]  # TOTP secret
    created_at: str          # ISO 8601 timestamp
    last_login: Optional[str] # Last login timestamp
    login_attempts: int      # Failed attempt count
    locked_until: Optional[str]  # Lockout expiry
```

### Login Request

```python
class LoginRequest(BaseModel):
    username: str
    password: str
    mfa_code: Optional[str] = None  # TOTP code if MFA enabled
```

### Login Response

```python
class LoginResponse(BaseModel):
    access_token: str      # JWT access token (15 min)
    refresh_token: str     # Refresh token (7 days)
    token_type: str       # "bearer"
    expires_in: int       # Seconds
    user: Dict[str, Any] # User profile
```

---

## Authentication Flow

### Standard Login

```
1. Client sends POST /login with username/password
2. Server validates credentials against IAM database
3. If MFA enabled, validate TOTP code
4. On success, generate JWT access + refresh tokens
5. Return tokens with user profile
```

### Token Refresh

```
1. Client sends POST /auth/refresh with refresh_token
2. Server validates refresh token signature and expiry
3. Generate new access token
4. Return new access token
```

### JWT Token Structure

**Access Token Payload:**
```json
{
  "sub": "username",
  "email": "user@example.com",
  "roles": ["user"],
  "permissions": ["rag:query", "voice:use"],
  "iat": 1700000000,
  "exp": 1700000900
}
```

---

## Security Features

### Rate Limiting

The service implements automatic account lockout:

1. Track failed login attempts per user
2. After 5 failed attempts, lock for 30 minutes
3. Log all authentication events

### Password Storage

- Uses `bcrypt` for password hashing
- Automatic salt generation
- Cost factor: 12 (work factor)

### JWT Security

- RS256 asymmetric signing
- Short-lived access tokens (15 min)
- Separate refresh tokens (7 days)
- Token revocation on logout

### Audit Logging

All authentication events are logged:

| Event | Logged |
|-------|--------|
| Login success | ✅ |
| Login failure | ✅ |
| MFA validation | ✅ |
| Token refresh | ✅ |
| Account lockout | ✅ |
| Password change | ✅ |

---

## Integration with Main API

### FastAPI Dependency

The IAM service provides a FastAPI dependency for route protection:

```python
from XNAi_rag_app.core.iam_service import get_current_user

@app.get("/protected")
async def protected_route(user: User = Depends(get_current_user)):
    return {"username": user.username, "roles": user.roles}
```

### Permission Decorators

```python
from XNAi_rag_app.core.iam_service import require_permission

@app.post("/admin/rag")
@require_permission("rag:admin")
async def admin_rag():
    return {"status": "admin access granted"}
```

---

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    roles TEXT NOT NULL DEFAULT '[]',
    permissions TEXT NOT NULL DEFAULT '[]',
    disabled INTEGER NOT NULL DEFAULT 0,
    mfa_enabled INTEGER NOT NULL DEFAULT 0,
    mfa_secret TEXT,
    created_at TEXT NOT NULL,
    last_login TEXT,
    login_attempts INTEGER DEFAULT 0,
    locked_until TEXT
);
```

### Sessions Table

```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    FOREIGN KEY (username) REFERENCES users(username)
);
```

---

## Environment Setup

### Generate JWT Keys

```bash
# Generate RSA private key
openssl genrsa -out jwt-private-key.pem 2048

# Extract public key
openssl rsa -in jwt-private-key.pem -pubout -out jwt-public-key.pem
```

### Configure Environment

```bash
# .env
IAM_DB_PATH=/app/data/iam.db
MFA_ENABLED=true
JWT_PRIVATE_KEY_PATH=/app/data/jwt-private-key.pem
JWT_PUBLIC_KEY_PATH=/app/data/jwt-public-key.pem
```

---

## Error Handling

### Authentication Errors

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `INVALID_CREDENTIALS` | 401 | Wrong username/password |
| `ACCOUNT_LOCKED` | 403 | Too many failed attempts |
| `MFA_REQUIRED` | 401 | MFA code needed |
| `MFA_INVALID` | 401 | Invalid MFA code |
| `TOKEN_EXPIRED` | 401 | JWT expired |
| `TOKEN_INVALID` | 401 | Malformed JWT |
| `INSUFFICIENT_PERMISSIONS` | 403 | Missing required permission |

### Error Response Format

```json
{
  "error_code": "INVALID_CREDENTIALS",
  "message": "Invalid username or password",
  "category": "authentication",
  "http_status": 401,
  "recovery_suggestion": "Please check your credentials and try again"
}
```

---

## Related Documentation

- [Main API](main.md)
- [Security Model](../04-explanation/security.md)
- [Zero-Trust Architecture](../04-explanation/sovereign-entity-architecture.md)
