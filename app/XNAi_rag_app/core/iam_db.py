"""Identity and Access Management Database for Omega-Stack Agent-Bus.

This module provides comprehensive IAM functionality including:
- Agent authentication and authorization
- Capability-based permissions
- JWT token management
- Audit logging
- Resource access control

Follows the security requirements identified in the gap analysis.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import secrets
from passlib.context import CryptContext
from sqlalchemy import Column, String, DateTime, JSON, Boolean, UUID, ForeignKey, Table, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, declarative_base, Session
from sqlalchemy.sql import func
import jwt

from app.XNAi_rag_app.services.database import get_db_session

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AgentType(str, Enum):
    """Types of agents in the system."""
    RESEARCHER = "researcher"
    CURATOR = "curator"
    ESCALATION = "escalation"
    ADMIN = "admin"
    SYSTEM = "system"


class PermissionLevel(str, Enum):
    """Permission levels for resource access."""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"


@dataclass
class AgentCapabilities:
    """Agent capabilities and permissions."""
    agent_id: str
    capabilities: List[str]
    permissions: Dict[str, PermissionLevel]
    resource_access: List[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class AuthToken:
    """Authentication token structure."""
    token: str
    agent_id: str
    expires_at: datetime
    permissions: List[str]
    issued_at: datetime


class Agent(Base):
    """Agent identity and basic information."""
    
    __tablename__ = 'agents_iam'
    
    id = Column(PGUUID(as_uuid=True), primary_key=True)
    did = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    agent_type = Column(String(50), nullable=False)
    model = Column(String(255), nullable=True)
    runtime = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default='active')
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    
    # Authentication
    password_hash = Column(String(255), nullable=True)
    public_key = Column(String, nullable=True)
    
    # Relationships
    capabilities = relationship("AgentCapability", back_populates="agent", cascade="all, delete-orphan")
    permissions = relationship("AgentPermission", back_populates="agent", cascade="all, delete-orphan")
    sessions = relationship("AgentSession", back_populates="agent", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="agent", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_agents_did', 'did'),
        Index('idx_agents_type', 'agent_type'),
        Index('idx_agents_status', 'status'),
    )


class AgentCapability(Base):
    """Agent capabilities and skills."""
    
    __tablename__ = 'agent_capabilities'
    
    agent_id = Column(PGUUID(as_uuid=True), ForeignKey('agents_iam.id', ondelete='CASCADE'), primary_key=True)
    capability = Column(String(255), primary_key=True)
    level = Column(String(50), nullable=False, default='basic')
    confidence = Column(String(50), nullable=False, default='medium')
    
    # Relationships
    agent = relationship("Agent", back_populates="capabilities")
    
    __table_args__ = (
        Index('idx_agent_capabilities_agent', 'agent_id'),
        Index('idx_agent_capabilities_capability', 'capability'),
    )


class AgentPermission(Base):
    """Agent resource permissions."""
    
    __tablename__ = 'agent_permissions'
    
    agent_id = Column(PGUUID(as_uuid=True), ForeignKey('agents_iam.id', ondelete='CASCADE'), primary_key=True)
    resource_type = Column(String(50), primary_key=True)
    resource_id = Column(PGUUID(as_uuid=True), primary_key=True)
    permission_level = Column(String(20), nullable=False)
    
    # Relationships
    agent = relationship("Agent", back_populates="permissions")
    
    __table_args__ = (
        Index('idx_agent_permissions_agent', 'agent_id'),
        Index('idx_agent_permissions_resource', 'resource_type', 'resource_id'),
    )


class AgentSession(Base):
    """Agent session management."""
    
    __tablename__ = 'agent_sessions'
    
    session_id = Column(PGUUID(as_uuid=True), primary_key=True)
    agent_id = Column(PGUUID(as_uuid=True), ForeignKey('agents_iam.id', ondelete='CASCADE'), nullable=False)
    context_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_activity = Column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    
    # Relationships
    agent = relationship("Agent", back_populates="sessions")
    
    __table_args__ = (
        Index('idx_agent_sessions_agent', 'agent_id'),
        Index('idx_agent_sessions_expires', 'expires_at'),
    )


class AuditLog(Base):
    """Audit trail for agent actions."""
    
    __tablename__ = 'audit_logs'
    
    id = Column(PGUUID(as_uuid=True), primary_key=True)
    agent_id = Column(PGUUID(as_uuid=True), ForeignKey('agents_iam.id', ondelete='CASCADE'), nullable=False)
    action = Column(String(255), nullable=False)
    resource = Column(String(255), nullable=True)
    result = Column(String(50), nullable=False)  # success, failed, denied
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    
    # Relationships
    agent = relationship("Agent", back_populates="audit_logs")
    
    __table_args__ = (
        Index('idx_audit_logs_agent', 'agent_id'),
        Index('idx_audit_logs_timestamp', 'timestamp'),
        Index('idx_audit_logs_action', 'action'),
    )


class IAMDatabase:
    """Main IAM database interface."""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session or get_db_session()
        self.logger = logging.getLogger(__name__)
        
        # JWT Configuration
        self.jwt_secret = self._get_jwt_secret()
        self.jwt_algorithm = "HS256"
        self.token_expiry = timedelta(hours=24)
    
    def _get_jwt_secret(self) -> str:
        """Get or generate JWT secret."""
        secret = self.db.execute(
            "SELECT value FROM config WHERE key = 'jwt_secret'"
        ).scalar()
        
        if not secret:
            secret = secrets.token_urlsafe(64)
            self.db.execute(
                "INSERT INTO config (key, value) VALUES ('jwt_secret', :secret)",
                {"secret": secret}
            )
            self.db.commit()
        
        return secret
    
    def register_agent(
        self,
        did: str,
        name: str,
        agent_type: AgentType,
        model: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        public_key: Optional[str] = None
    ) -> Agent:
        """Register a new agent."""
        try:
            # Check if agent already exists
            existing = self.db.query(Agent).filter(Agent.did == did).first()
            if existing:
                raise ValueError(f"Agent with DID {did} already exists")
            
            # Create agent
            agent = Agent(
                did=did,
                name=name,
                email=email,
                agent_type=agent_type.value,
                model=model,
                runtime="unknown",
                status="active",
                password_hash=self._hash_password(password) if password else None,
                public_key=public_key
            )
            
            self.db.add(agent)
            self.db.commit()
            self.db.refresh(agent)
            
            self._log_audit(agent.id, "agent_registered", "success", {"did": did, "type": agent_type.value})
            
            return agent
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error registering agent {did}: {e}")
            raise
    
    def authenticate_agent(self, did: str, credentials: Dict[str, Any]) -> Optional[AuthToken]:
        """Authenticate an agent and return JWT token."""
        try:
            agent = self.db.query(Agent).filter(Agent.did == did).first()
            if not agent:
                self._log_audit(None, "authentication_failed", "failed", {"did": did, "reason": "agent_not_found"})
                return None
            
            # Check agent status
            if agent.status != "active":
                self._log_audit(agent.id, "authentication_failed", "failed", {"reason": f"agent_inactive_{agent.status}"})
                return None
            
            # Authenticate based on credentials type
            auth_method = credentials.get("method", "password")
            
            if auth_method == "password":
                password = credentials.get("password")
                if not password or not self._verify_password(password, agent.password_hash):
                    self._log_audit(agent.id, "authentication_failed", "failed", {"reason": "invalid_password"})
                    return None
            
            elif auth_method == "public_key":
                signature = credentials.get("signature")
                message = credentials.get("message")
                if not self._verify_signature(agent.public_key, message, signature):
                    self._log_audit(agent.id, "authentication_failed", "failed", {"reason": "invalid_signature"})
                    return None
            
            else:
                self._log_audit(agent.id, "authentication_failed", "failed", {"reason": f"unsupported_auth_method_{auth_method}"})
                return None
            
            # Generate JWT token
            token = self._generate_jwt_token(agent)
            
            # Create session
            session = AgentSession(
                session_id=token,
                agent_id=agent.id,
                expires_at=datetime.utcnow() + self.token_expiry
            )
            
            self.db.add(session)
            self.db.commit()
            
            self._log_audit(agent.id, "authentication_success", "success", {"session_id": str(session.session_id)})
            
            return AuthToken(
                token=token,
                agent_id=str(agent.id),
                expires_at=datetime.utcnow() + self.token_expiry,
                permissions=self._get_agent_permissions(agent.id),
                issued_at=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Error authenticating agent {did}: {e}")
            return None
    
    def authorize_action(
        self,
        agent_id: str,
        action: str,
        resource: str,
        resource_type: Optional[str] = None
    ) -> bool:
        """Check if agent is authorized to perform an action on a resource."""
        try:
            # Get agent
            agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
            if not agent or agent.status != "active":
                self._log_audit(agent_id, "authorization_denied", "denied", {
                    "action": action,
                    "resource": resource,
                    "reason": "agent_inactive"
                })
                return False
            
            # Check capability
            if not self._has_capability(agent.id, action):
                self._log_audit(agent_id, "authorization_denied", "denied", {
                    "action": action,
                    "resource": resource,
                    "reason": "missing_capability"
                })
                return False
            
            # Check resource permission
            if resource_type and not self._has_resource_permission(agent.id, resource_type, resource, action):
                self._log_audit(agent_id, "authorization_denied", "denied", {
                    "action": action,
                    "resource": resource,
                    "reason": "insufficient_permissions"
                })
                return False
            
            self._log_audit(agent_id, "authorization_granted", "success", {
                "action": action,
                "resource": resource
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error authorizing action for agent {agent_id}: {e}")
            return False
    
    def get_agent_capabilities(self, agent_id: str) -> List[str]:
        """Get agent capabilities."""
        try:
            capabilities = self.db.query(AgentCapability.capability).filter(
                AgentCapability.agent_id == agent_id
            ).all()
            
            return [cap[0] for cap in capabilities]
            
        except Exception as e:
            self.logger.error(f"Error getting capabilities for agent {agent_id}: {e}")
            return []
    
    def add_agent_capability(self, agent_id: str, capability: str, level: str = "basic", confidence: str = "medium"):
        """Add capability to agent."""
        try:
            # Check if capability already exists
            existing = self.db.query(AgentCapability).filter(
                AgentCapability.agent_id == agent_id,
                AgentCapability.capability == capability
            ).first()
            
            if existing:
                existing.level = level
                existing.confidence = confidence
            else:
                capability_obj = AgentCapability(
                    agent_id=agent_id,
                    capability=capability,
                    level=level,
                    confidence=confidence
                )
                self.db.add(capability_obj)
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error adding capability {capability} to agent {agent_id}: {e}")
    
    def set_agent_permission(
        self,
        agent_id: str,
        resource_type: str,
        resource_id: str,
        permission_level: PermissionLevel
    ):
        """Set agent permission for a resource."""
        try:
            # Check if permission already exists
            existing = self.db.query(AgentPermission).filter(
                AgentPermission.agent_id == agent_id,
                AgentPermission.resource_type == resource_type,
                AgentPermission.resource_id == resource_id
            ).first()
            
            if existing:
                existing.permission_level = permission_level.value
            else:
                permission = AgentPermission(
                    agent_id=agent_id,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    permission_level=permission_level.value
                )
                self.db.add(permission)
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error setting permission for agent {agent_id}: {e}")
    
    def list_agents(self, agent_type: Optional[AgentType] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List agents with optional filtering."""
        try:
            query = self.db.query(Agent)
            
            if agent_type:
                query = query.filter(Agent.agent_type == agent_type.value)
            
            if status:
                query = query.filter(Agent.status == status)
            
            agents = query.all()
            
            return [
                {
                    "id": str(agent.id),
                    "did": agent.did,
                    "name": agent.name,
                    "agent_type": agent.agent_type,
                    "model": agent.model,
                    "status": agent.status,
                    "capabilities": self.get_agent_capabilities(str(agent.id)),
                    "created_at": agent.created_at.isoformat()
                }
                for agent in agents
            ]
            
        except Exception as e:
            self.logger.error(f"Error listing agents: {e}")
            return []
    
    def _hash_password(self, password: Optional[str]) -> Optional[str]:
        """Hash password using bcrypt."""
        if not password:
            return None
        return pwd_context.hash(password)
    
    def _verify_password(self, password: str, hash: str) -> bool:
        """Verify password against hash."""
        if not password or not hash:
            return False
        return pwd_context.verify(password, hash)
    
    def _verify_signature(self, public_key: str, message: str, signature: str) -> bool:
        """Verify digital signature."""
        # This is a placeholder - in production, use proper crypto library
        # For now, we'll use a simple hash comparison
        expected = hashlib.sha256(f"{public_key}:{message}".encode()).hexdigest()
        return signature == expected
    
    def _generate_jwt_token(self, agent: Agent) -> str:
        """Generate JWT token for agent."""
        payload = {
            "agent_id": str(agent.id),
            "did": agent.did,
            "name": agent.name,
            "agent_type": agent.agent_type,
            "exp": datetime.utcnow() + self.token_expiry,
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def _get_agent_permissions(self, agent_id: str) -> List[str]:
        """Get agent permissions."""
        try:
            permissions = self.db.query(AgentPermission.permission_level).filter(
                AgentPermission.agent_id == agent_id
            ).all()
            
            return [perm[0] for perm in permissions]
            
        except Exception as e:
            self.logger.error(f"Error getting permissions for agent {agent_id}: {e}")
            return []
    
    def _has_capability(self, agent_id: str, action: str) -> bool:
        """Check if agent has required capability."""
        capabilities = self.get_agent_capabilities(agent_id)
        return action in capabilities
    
    def _has_resource_permission(
        self,
        agent_id: str,
        resource_type: str,
        resource_id: str,
        action: str
    ) -> bool:
        """Check if agent has permission for resource."""
        try:
            permission = self.db.query(AgentPermission).filter(
                AgentPermission.agent_id == agent_id,
                AgentPermission.resource_type == resource_type,
                AgentPermission.resource_id == resource_id
            ).first()
            
            if not permission:
                return False
            
            # Map actions to permission levels
            action_levels = {
                "read": ["read", "write", "execute", "admin"],
                "write": ["write", "execute", "admin"],
                "execute": ["execute", "admin"],
                "admin": ["admin"]
            }
            
            required_levels = action_levels.get(action, [])
            return permission.permission_level in required_levels
            
        except Exception as e:
            self.logger.error(f"Error checking resource permission: {e}")
            return False
    
    def _log_audit(self, agent_id: Optional[str], action: str, result: str, details: Dict[str, Any]):
        """Log audit event."""
        try:
            audit_log = AuditLog(
                agent_id=agent_id,
                action=action,
                result=result,
                details=details
            )
            
            self.db.add(audit_log)
            self.db.commit()
            
        except Exception as e:
            self.logger.error(f"Error logging audit event: {e}")
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        try:
            cutoff = datetime.utcnow()
            expired_sessions = self.db.query(AgentSession).filter(
                AgentSession.expires_at < cutoff
            ).all()
            
            for session in expired_sessions:
                self.db.delete(session)
            
            self.db.commit()
            
            self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up expired sessions: {e}")


# Global IAM instance
iam_database = IAMDatabase()


def get_iam_database() -> IAMDatabase:
    """Get global IAM database instance."""
    return iam_database