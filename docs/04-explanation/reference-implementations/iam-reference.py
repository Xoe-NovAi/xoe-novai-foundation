# ============================================================================
# INTEGRATION STATUS: CLAUDE IMPLEMENTATION DELIVERABLE
# ============================================================================
# Status: NOT INTEGRATED - Requires implementation into Xoe-NovAi codebase
# Source: Claude Week 3 Session Deliverable - Enterprise Security & Compliance Hardening
# Date Received: January 27, 2026 (Week 3)
# Implementation Priority: CRITICAL (Zero-trust IAM with MFA and ABAC)
# Estimated Integration Effort: 4-5 days
# Dependencies: Redis Sentinel, OAuth2/JWT, Multi-factor authentication
# Integration Checklist:
# - [ ] Implement OAuth2/JWT authentication with RS256
# - [ ] Deploy multi-factor authentication (TOTP)
# - [ ] Configure role-based and permission-based access control
# - [ ] Set up token refresh and revocation
# - [ ] Add password complexity validation
# - [ ] Implement MFA setup with QR codes and backup codes
# - [ ] Create admin user management endpoints
# - [ ] Integrate with Redis for session management
# - [ ] Test authentication flows
# - [ ] Validate security compliance
# Integration Complete: [ ] Date: ___________ By: ___________
# ============================================================================

# app/security/iam_service_complete.py
"""
Xoe-NovAi Complete IAM Service
Enterprise-grade Identity & Access Management with MFA, JWT, and ABAC integration
"""

from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import jwt
import bcrypt
import pyotp
import qrcode
from io import BytesIO
import base64
import os
import logging
from dataclasses import dataclass
import redis.asyncio as redis
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
MFA_ISSUER = "Xoe-NovAi"

app = FastAPI(
    title="Xoe-NovAi IAM Service",
    description="Enterprise Identity & Access Management",
    version="1.0.0"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security = HTTPBearer()

# Redis for session management and rate limiting
redis_client = None

# ============================================================================
# MODELS
# ============================================================================

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    
class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 16:
            raise ValueError('Password must be at least 16 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letters')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letters')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digits')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain special characters')
        return v

class User(UserBase):
    id: str
    disabled: bool = False
    roles: List[str] = []
    permissions: List[str] = []
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    
class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []
    
class MFASetupResponse(BaseModel):
    secret: str
    qr_code: str
    backup_codes: List[str]
    
class MFAVerifyRequest(BaseModel):
    token: str
    
class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

# ============================================================================
# DATABASE (In-memory for demo - replace with actual database)
# ============================================================================

users_db: Dict[str, Dict] = {
    "admin": {
        "id": "user-admin-001",
        "username": "admin",
        "full_name": "System Administrator",
        "email": "admin@xoenovai.local",
        "hashed_password": bcrypt.hashpw(b"Admin123!@#$SecurePass", bcrypt.gensalt()),
        "disabled": False,
        "roles": ["admin"],
        "permissions": ["*"],
        "mfa_enabled": False,
        "mfa_secret": None,
        "created_at": datetime.utcnow().isoformat(),
        "last_login": None
    }
}

# ============================================================================
# CRYPTOGRAPHIC OPERATIONS
# ============================================================================

class CryptoManager:
    """Manage cryptographic operations for JWT"""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self._load_keys()
    
    def _load_keys(self):
        """Load RSA keys for JWT signing"""
        private_key_path = os.getenv("JWT_PRIVATE_KEY_PATH", "/etc/xoenovai/certs/jwt-private-key.pem")
        public_key_path = os.getenv("JWT_PUBLIC_KEY_PATH", "/etc/xoenovai/certs/jwt-public-key.pem")
        
        try:
            # Load private key
            with open(private_key_path, "rb") as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            
            # Load public key
            with open(public_key_path, "rb") as f:
                self.public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
            
            logger.info("RSA keys loaded successfully")
            
        except FileNotFoundError:
            logger.warning("RSA keys not found, generating new keys")
            self._generate_keys()
    
    def _generate_keys(self):
        """Generate new RSA key pair (development only)"""
        from cryptography.hazmat.primitives.asymmetric import rsa
        
        # Generate private key
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        
        # Generate public key
        self.public_key = self.private_key.public_key()
        
        # Save keys (in production, use secure key management)
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        logger.info("Generated new RSA keys (DEVELOPMENT MODE)")

crypto_manager = CryptoManager()

# ============================================================================
# SECURITY UTILITIES
# ============================================================================

def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode(), hashed_password)

def get_password_hash(password: str) -> bytes:
    """Hash password with bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
        "jti": os.urandom(16).hex()  # JWT ID for revocation
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        crypto_manager.private_key,
        algorithm=ALGORITHM
    )
    
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
        "jti": os.urandom(16).hex()
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        crypto_manager.private_key,
        algorithm=ALGORITHM
    )
    
    return encoded_jwt

def generate_mfa_secret() -> str:
    """Generate MFA secret"""
    return pyotp.random_base32()

def generate_mfa_qr_code(username: str, secret: str) -> str:
    """Generate MFA QR code"""
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=username,
        issuer_name=MFA_ISSUER
    )
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def generate_backup_codes(count: int = 10) -> List[str]:
    """Generate backup codes for MFA"""
    return [os.urandom(8).hex() for _ in range(count)]

def verify_mfa_token(secret: str, token: str) -> bool:
    """Verify MFA token"""
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> User:
    """Get current authenticated user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        
        payload = jwt.decode(
            token,
            crypto_manager.public_key,
            algorithms=[ALGORITHM]
        )
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # Check token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Check if token is revoked (check Redis)
        jti = payload.get("jti")
        if redis_client and await redis_client.exists(f"revoked:{jti}"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )
        
        token_data = TokenData(username=username, scopes=payload.get("scopes", []))
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise credentials_exception
    
    user_dict = users_db.get(username)
    if user_dict is None:
        raise credentials_exception
    
    return User(**user_dict)

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure user is active"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_role(required_role: str):
    """Decorator to require specific role"""
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        if required_role not in current_user.roles and "admin" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return current_user
    return role_checker

def require_permission(required_permission: str):
    """Decorator to require specific permission"""
    async def permission_checker(current_user: User = Depends(get_current_active_user)):
        if "*" not in current_user.permissions and required_permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{required_permission}' required"
            )
        return current_user
    return permission_checker

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.on_event("startup")
async def startup():
    """Initialize Redis connection"""
    global redis_client
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_client = await redis.from_url(redis_url, decode_responses=True)
    logger.info("IAM Service started, Redis connected")

@app.on_event("shutdown")
async def shutdown():
    """Close Redis connection"""
    if redis_client:
        await redis_client.close()
    logger.info("IAM Service shutdown")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "iam",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/auth/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_create: UserCreate):
    """Register new user"""
    
    # Check if username exists
    if user_create.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email exists
    for user in users_db.values():
        if user["email"] == user_create.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Hash password
    hashed_password = get_password_hash(user_create.password)
    
    # Create user
    user_id = f"user-{os.urandom(8).hex()}"
    user_dict = {
        "id": user_id,
        "username": user_create.username,
        "full_name": user_create.full_name,
        "email": user_create.email,
        "hashed_password": hashed_password,
        "disabled": False,
        "roles": ["user"],
        "permissions": ["voice:use", "rag:query", "llm:inference"],
        "mfa_enabled": False,
        "mfa_secret": None,
        "created_at": datetime.utcnow().isoformat(),
        "last_login": None
    }
    
    users_db[user_create.username] = user_dict
    
    logger.info(f"User registered: {user_create.username}")
    
    return User(**user_dict)

@app.post("/auth/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    mfa_token: Optional[str] = None
):
    """Authenticate user and return tokens"""
    
    user = users_db.get(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if user["disabled"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Check MFA if enabled
    if user["mfa_enabled"]:
        if not mfa_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="MFA token required",
                headers={"X-MFA-Required": "true"}
            )
        
        if not verify_mfa_token(user["mfa_secret"], mfa_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA token"
            )
    
    # Update last login
    user["last_login"] = datetime.utcnow().isoformat()
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user["username"], "scopes": user["permissions"]}
    )
    refresh_token = create_refresh_token(
        data={"sub": user["username"]}
    )
    
    logger.info(f"User logged in: {user['username']}")
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@app.post("/auth/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str):
    """Refresh access token using refresh token"""
    
    try:
        payload = jwt.decode(
            refresh_token,
            crypto_manager.public_key,
            algorithms=[ALGORITHM]
        )
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type"
            )
        
        username = payload.get("sub")
        user = users_db.get(username)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create new access token
        new_access_token = create_access_token(
            data={"sub": username, "scopes": user["permissions"]}
        )
        
        return Token(
            access_token=new_access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@app.post("/auth/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Logout user and revoke token"""
    
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            crypto_manager.public_key,
            algorithms=[ALGORITHM]
        )
        
        jti = payload.get("jti")
        exp = payload.get("exp")
        
        # Add token to revocation list in Redis
        if redis_client and jti:
            ttl = exp - datetime.utcnow().timestamp()
            if ttl > 0:
                await redis_client.setex(
                    f"revoked:{jti}",
                    int(ttl),
                    "1"
                )
        
        logger.info(f"User logged out: {current_user.username}")
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@app.post("/users/me/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(current_user: User = Depends(get_current_active_user)):
    """Setup MFA for user"""
    
    # Generate MFA secret
    secret = generate_mfa_secret()
    
    # Generate QR code
    qr_code = generate_mfa_qr_code(current_user.username, secret)
    
    # Generate backup codes
    backup_codes = generate_backup_codes()
    
    # Store secret (temporarily, will be confirmed on verification)
    user_dict = users_db[current_user.username]
    user_dict["mfa_secret_pending"] = secret
    user_dict["backup_codes"] = [
        get_password_hash(code) for code in backup_codes
    ]
    
    logger.info(f"MFA setup initiated for user: {current_user.username}")
    
    return MFASetupResponse(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes
    )

@app.post("/users/me/mfa/verify")
async def verify_mfa_setup(
    request: MFAVerifyRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Verify and enable MFA"""
    
    user_dict = users_db[current_user.username]
    pending_secret = user_dict.get("mfa_secret_pending")
    
    if not pending_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending MFA setup"
        )
    
    if not verify_mfa_token(pending_secret, request.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA token"
        )
    
    # Enable MFA
    user_dict["mfa_enabled"] = True
    user_dict["mfa_secret"] = pending_secret
    del user_dict["mfa_secret_pending"]
    
    logger.info(f"MFA enabled for user: {current_user.username}")
    
    return {"message": "MFA enabled successfully"}

@app.post("/users/me/mfa/disable")
async def disable_mfa(
    password: str,
    current_user: User = Depends(get_current_active_user)
):
    """Disable MFA (requires password)"""
    
    user_dict = users_db[current_user.username]
    
    if not verify_password(password, user_dict["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    user_dict["mfa_enabled"] = False
    user_dict["mfa_secret"] = None
    user_dict["backup_codes"] = []
    
    logger.info(f"MFA disabled for user: {current_user.username}")
    
    return {"message": "MFA disabled successfully"}

@app.post("/users/me/password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Change user password"""
    
    user_dict = users_db[current_user.username]
    
    if not verify_password(request.current_password, user_dict["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password"
        )
    
    # Validate new password
    try:
        UserCreate.validate_password(request.new_password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Update password
    user_dict["hashed_password"] = get_password_hash(request.new_password)
    
    logger.info(f"Password changed for user: {current_user.username}")
    
    return {"message": "Password changed successfully"}

@app.get("/admin/users", dependencies=[Depends(require_role("admin"))])
async def list_users():
    """List all users (admin only)"""
    return [
        {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "disabled": user["disabled"],
            "roles": user["roles"],
            "mfa_enabled": user["mfa_enabled"],
            "created_at": user["created_at"],
            "last_login": user["last_login"]
        }
        for user in users_db.values()
    ]

@app.put("/admin/users/{username}/roles", dependencies=[Depends(require_role("admin"))])
async def update_user_roles(username: str, roles: List[str]):
    """Update user roles (admin only)"""
    
    user = users_db.get(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user["roles"] = roles
    
    logger.info(f"Roles updated for user {username}: {roles}")
    
    return {"message": "Roles updated successfully"}

@app.put("/admin/users/{username}/permissions", dependencies=[Depends(require_role("admin"))])
async def update_user_permissions(username: str, permissions: List[str]):
    """Update user permissions (admin only)"""
    
    user = users_db.get(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user["permissions"] = permissions
    
    logger.info(f"Permissions updated for user {username}: {permissions}")
    
    return {"message": "Permissions updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_keyfile=os.getenv("SSL_KEYFILE", "/etc/xoenovai/certs/server-key.pem"),
        ssl_certfile=os.getenv("SSL_CERTFILE", "/etc/xoenovai/certs/server-cert.pem")
    )
