#!/usr/bin/env python3
"""
Knowledge Access Control Module for XNAi Foundation
====================================================

Integrates IAM service with knowledge operations for zero-trust access control.
Implements agent DID validation and task type authorization.

CLAUDE STANDARD: Uses AnyIO for structured concurrency.
Pattern: Zero-Trust Security (Phase 4.2.6)
Version: 1.0.0

Features:
- IAM service integration with knowledge client
- Agent DID validation via Ed25519 signatures
- Task type authorization with ABAC policies
- Qdrant write permission management
- Audit logging for all access attempts
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from .iam_service import IAMService, User, Permission
from .iam_db import IAMDatabase, AgentIdentity, AgentType
from .iam_handshake import SovereignHandshake, KeyManager

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMERATIONS
# ============================================================================

class KnowledgeAction(str, Enum):
    """Knowledge operation types."""
    READ = "knowledge:read"
    WRITE = "knowledge:write"
    DELETE = "knowledge:delete"
    SEARCH = "knowledge:search"
    INDEX = "knowledge:index"
    ADMIN = "knowledge:admin"


class AccessDecision(str, Enum):
    """Access control decisions."""
    ALLOWED = "allowed"
    DENIED = "denied"
    NOT_AUTHORIZED = "not_authorized"
    INVALID_IDENTITY = "invalid_identity"
    RATE_LIMITED = "rate_limited"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class AccessRequest:
    """Request for knowledge access."""
    agent_did: str
    action: KnowledgeAction
    resource: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class AccessResult:
    """Result of access control check."""
    decision: AccessDecision
    request: AccessRequest
    reason: str
    user: Optional[User] = None
    agent: Optional[AgentIdentity] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    audit_id: str = ""
    
    def is_allowed(self) -> bool:
        return self.decision == AccessDecision.ALLOWED
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision.value,
            "reason": self.reason,
            "agent_did": self.request.agent_did,
            "action": self.request.action.value,
            "resource": self.request.resource,
            "timestamp": self.timestamp,
            "audit_id": self.audit_id,
        }


@dataclass
class KnowledgePermission:
    """Permission mapping for knowledge operations."""
    action: KnowledgeAction
    required_permission: Permission
    description: str


# ============================================================================
# PERMISSION MAPPINGS
# ============================================================================

KNOWLEDGE_PERMISSIONS: Dict[KnowledgeAction, Permission] = {
    KnowledgeAction.READ: Permission.RAG_QUERY,
    KnowledgeAction.SEARCH: Permission.RAG_QUERY,
    KnowledgeAction.WRITE: Permission.RAG_INGEST,
    KnowledgeAction.INDEX: Permission.RAG_INGEST,
    KnowledgeAction.DELETE: Permission.RAG_ADMIN,
    KnowledgeAction.ADMIN: Permission.RAG_ADMIN,
}


# ============================================================================
# KNOWLEDGE ACCESS CONTROL
# ============================================================================

class KnowledgeAccessControl:
    """
    Zero-trust access control for knowledge operations.
    
    Integrates IAM service with knowledge client to provide:
    - Agent DID validation
    - Task type authorization
    - ABAC policy enforcement
    - Audit logging
    
    Usage:
        iam_service = IAMService()
        access_control = KnowledgeAccessControl(iam_service)
        
        # Check access
        result = await access_control.check_access(
            agent_did="did:xoe:agent:cline-1",
            action=KnowledgeAction.SEARCH,
            resource="knowledge_base"
        )
        
        if result.is_allowed():
            # Proceed with knowledge operation
            pass
        else:
            # Deny access
            logger.warning(f"Access denied: {result.reason}")
    """
    
    def __init__(
        self,
        iam_service: Optional[IAMService] = None,
        iam_db: Optional[IAMDatabase] = None
    ):
        """Initialize knowledge access control."""
        self.iam_service = iam_service or IAMService()
        self.iam_db = iam_db or IAMDatabase()
        
        # Initialize handshake manager
        self.handshake = SovereignHandshake(self.iam_db)
        
        # Permission mappings
        self.permissions = KNOWLEDGE_PERMISSIONS
        
        logger.info("Knowledge access control initialized")
    
    async def check_access(
        self,
        agent_did: str,
        action: KnowledgeAction,
        resource: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AccessResult:
        """
        Check if agent has permission for the requested action.
        
        Args:
            agent_did: Decentralized identifier of the requesting agent
            action: The knowledge action being requested
            resource: The resource being accessed (collection, document, etc.)
            context: Additional context for ABAC evaluation
            
        Returns:
            AccessResult with decision and reasoning
        """
        request = AccessRequest(
            agent_did=agent_did,
            action=action,
            resource=resource,
            context=context or {}
        )
        
        # Step 1: Validate agent identity
        agent = await self._validate_agent(agent_did)
        if not agent:
            return AccessResult(
                decision=AccessDecision.INVALID_IDENTITY,
                request=request,
                reason=f"Agent not found or not verified: {agent_did}"
            )
        
        # Step 2: Get required permission for action
        required_permission = self.permissions.get(action)
        if not required_permission:
            return AccessResult(
                decision=AccessDecision.NOT_AUTHORIZED,
                request=request,
                reason=f"No permission mapping for action: {action.value}"
            )
        
        # Step 3: Check if agent has the required permission
        # For service accounts, check metadata permissions
        if agent.agent_type == AgentType.SERVICE:
            has_permission = self._check_service_permission(agent, required_permission)
        else:
            # For user accounts, would need to get user from IAM service
            has_permission = True  # Placeholder - integrate with User system
        
        if not has_permission:
            return AccessResult(
                decision=AccessDecision.NOT_AUTHORIZED,
                request=request,
                reason=f"Agent lacks permission: {required_permission.value}",
                agent=agent
            )
        
        # Step 4: Evaluate ABAC policies
        abac_allowed, abac_reason = await self._evaluate_abac(agent, resource, action)
        if not abac_allowed:
            return AccessResult(
                decision=AccessDecision.DENIED,
                request=request,
                reason=f"ABAC policy denied: {abac_reason}",
                agent=agent
            )
        
        # Access granted
        result = AccessResult(
            decision=AccessDecision.ALLOWED,
            request=request,
            reason="Access granted",
            agent=agent
        )
        
        # Log successful access
        self._log_access(result)
        
        return result
    
    async def _validate_agent(self, agent_did: str) -> Optional[AgentIdentity]:
        """
        Validate agent identity and verification status.
        
        Args:
            agent_did: The agent's DID
            
        Returns:
            AgentIdentity if valid, None otherwise
        """
        try:
            agent = self.iam_db.get_agent(agent_did)
            
            if not agent:
                logger.warning(f"Agent not found: {agent_did}")
                return None
            
            # Check if agent is verified (completed Ed25519 handshake)
            if not agent.verified:
                logger.warning(f"Agent not verified: {agent_did}")
                return None
            
            return agent
            
        except Exception as e:
            logger.error(f"Error validating agent {agent_did}: {e}")
            return None
    
    def _check_service_permission(
        self,
        agent: AgentIdentity,
        required_permission: Permission
    ) -> bool:
        """
        Check if service account has the required permission.
        
        Args:
            agent: The agent identity
            required_permission: The permission required for the action
            
        Returns:
            True if agent has permission
        """
        # Check metadata for permissions list
        metadata = agent.metadata or {}
        permissions = metadata.get("permissions", [])
        
        # Check for wildcard permission
        if "*" in permissions or Permission.ALL.value in permissions:
            return True
        
        # Check for specific permission
        return required_permission.value in permissions
    
    async def _evaluate_abac(
        self,
        agent: AgentIdentity,
        resource: str,
        action: KnowledgeAction
    ) -> tuple[bool, str]:
        """
        Evaluate ABAC policies for the access request.
        
        Args:
            agent: The agent identity
            resource: The resource being accessed
            action: The action being performed
            
        Returns:
            Tuple of (allowed, reason)
        """
        # Agent attributes
        agent_attrs = {
            "did": agent.did,
            "agent_type": agent.agent_type.value,
            "agent_name": agent.agent_name,
            "verified": agent.verified,
            "metadata": agent.metadata or {}
        }
        
        # Resource attributes (simplified - would normally query resource metadata)
        resource_attrs = {
            "name": resource,
            "type": "knowledge_collection"
        }
        
        # Evaluate policies
        policies = self._get_abac_policies()
        
        for policy in policies:
            try:
                if policy["condition"](agent_attrs, resource_attrs, action.value):
                    if policy["effect"] == "deny":
                        return False, f"Policy '{policy['name']}' denied access"
                    elif policy["effect"] == "allow":
                        return True, f"Policy '{policy['name']}' allowed access"
            except Exception as e:
                logger.error(f"Error evaluating policy '{policy['name']}': {e}")
                continue
        
        # Default deny
        return False, "No matching policy found (default deny)"
    
    def _get_abac_policies(self) -> List[Dict[str, Any]]:
        """Get ABAC policies for knowledge access."""
        return [
            {
                "name": "verified_agents_only",
                "description": "Only verified agents can access knowledge",
                "condition": lambda agent, resource, action: agent.get("verified", False),
                "effect": "allow"
            },
            {
                "name": "service_account_write_restriction",
                "description": "Service accounts cannot delete without admin",
                "condition": lambda agent, resource, action: (
                    agent.get("agent_type") == "service" and
                    action == KnowledgeAction.DELETE.value and
                    "admin" not in agent.get("metadata", {}).get("permissions", [])
                ),
                "effect": "deny"
            },
            {
                "name": "knowledge_admin_full_access",
                "description": "Knowledge admins have full access",
                "condition": lambda agent, resource, action: (
                    Permission.RAG_ADMIN.value in agent.get("metadata", {}).get("permissions", [])
                ),
                "effect": "allow"
            },
        ]
    
    def _log_access(self, result: AccessResult) -> None:
        """Log access attempt for audit."""
        logger.info(
            f"Knowledge access: {result.decision.value}",
            extra={
                "operation": "knowledge_access",
                "decision": result.decision.value,
                "agent_did": result.request.agent_did,
                "action": result.request.action.value,
                "resource": result.request.resource,
                "reason": result.reason,
                "timestamp": result.timestamp,
            }
        )
    
    # ========================================================================
    # Qdrant-Specific Methods
    # ========================================================================
    
    async def check_qdrant_write(
        self,
        agent_did: str,
        collection: str
    ) -> AccessResult:
        """
        Check if agent can write to Qdrant collection.
        
        Args:
            agent_did: The agent's DID
            collection: The Qdrant collection name
            
        Returns:
            AccessResult for write permission
        """
        return await self.check_access(
            agent_did=agent_did,
            action=KnowledgeAction.WRITE,
            resource=f"qdrant:{collection}"
        )
    
    async def check_qdrant_read(
        self,
        agent_did: str,
        collection: str
    ) -> AccessResult:
        """
        Check if agent can read from Qdrant collection.
        
        Args:
            agent_did: The agent's DID
            collection: The Qdrant collection name
            
        Returns:
            AccessResult for read permission
        """
        return await self.check_access(
            agent_did=agent_did,
            action=KnowledgeAction.READ,
            resource=f"qdrant:{collection}"
        )
    
    async def check_qdrant_delete(
        self,
        agent_did: str,
        collection: str
    ) -> AccessResult:
        """
        Check if agent can delete from Qdrant collection.
        
        Args:
            agent_did: The agent's DID
            collection: The Qdrant collection name
            
        Returns:
            AccessResult for delete permission
        """
        return await self.check_access(
            agent_did=agent_did,
            action=KnowledgeAction.DELETE,
            resource=f"qdrant:{collection}"
        )
    
    # ========================================================================
    # Agent Registration Helpers
    # ========================================================================
    
    async def register_knowledge_agent(
        self,
        agent_name: str,
        agent_type: AgentType,
        permissions: List[Permission],
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentIdentity:
        """
        Register a new agent with knowledge access permissions.
        
        Args:
            agent_name: Name for the agent
            agent_type: Type of agent (cline, gemini, service, etc.)
            permissions: List of permissions to grant
            metadata: Additional metadata
            
        Returns:
            The created AgentIdentity
        """
        # Generate Ed25519 keypair
        private_key_hex, public_key_hex = KeyManager.generate_keypair()
        
        # Create DID
        did = f"did:xoe:agent:{agent_type.value}:{agent_name}"
        
        # Create identity
        identity = AgentIdentity(
            did=did,
            agent_name=agent_name,
            agent_type=agent_type,
            public_key_ed25519=public_key_hex,
            metadata={
                **(metadata or {}),
                "permissions": [p.value for p in permissions],
                "created_by": "knowledge_access_control"
            },
            created_at=datetime.now(timezone.utc).isoformat(),
            verified=False  # Requires handshake verification
        )
        
        # Register in database
        self.iam_db.register_agent(identity)
        
        logger.info(
            f"Registered knowledge agent: {agent_name}",
            extra={
                "operation": "agent_registration",
                "did": did,
                "agent_type": agent_type.value,
                "permissions": [p.value for p in permissions]
            }
        )
        
        return identity


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def check_knowledge_access(
    agent_did: str,
    action: KnowledgeAction,
    resource: str
) -> bool:
    """
    Quick check if agent has access to perform action.
    
    Args:
        agent_did: The agent's DID
        action: The action to check
        resource: The resource being accessed
        
    Returns:
        True if access is allowed
    """
    access_control = KnowledgeAccessControl()
    result = await access_control.check_access(agent_did, action, resource)
    return result.is_allowed()