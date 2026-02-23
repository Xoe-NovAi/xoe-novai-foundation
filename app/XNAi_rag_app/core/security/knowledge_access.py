#!/usr/bin/env python3
"""
Knowledge Access Controller - Zero-Trust Access Control
========================================================
Implements fine-grained access control for knowledge operations.

Features:
- Agent DID validation and verification
- Task type authorization with ABAC policies
- Qdrant write permission management
- Audit logging for compliance

Pattern: Zero-Trust Security (Phase 4.2.6)
Version: 1.0.0
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)


# ============================================================================
# Exceptions
# ============================================================================


class AccessDeniedError(Exception):
    """Raised when access is denied to a resource"""

    def __init__(
        self,
        message: str,
        agent_did: Optional[str] = None,
        operation: Optional[str] = None,
        resource: Optional[str] = None,
    ):
        self.agent_did = agent_did
        self.operation = operation
        self.resource = resource
        super().__init__(message)


class AgentNotVerifiedError(AccessDeniedError):
    """Raised when agent DID is not verified"""

    pass


class InsufficientPermissionsError(AccessDeniedError):
    """Raised when agent lacks required permissions"""

    pass


# ============================================================================
# Enums & Data Models
# ============================================================================


class KnowledgeOperation(str, Enum):
    """Knowledge operation types"""

    # Read operations
    READ = "knowledge:read"
    QUERY = "knowledge:query"
    SEARCH = "knowledge:search"

    # Write operations
    WRITE = "knowledge:write"
    INGEST = "knowledge:ingest"
    UPDATE = "knowledge:update"
    DELETE = "knowledge:delete"

    # Admin operations
    ADMIN = "knowledge:admin"
    COLLECTION_CREATE = "knowledge:collection:create"
    COLLECTION_DELETE = "knowledge:collection:delete"


class KnowledgePermission(str, Enum):
    """Permission levels for knowledge access"""

    NONE = "none"
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"


@dataclass
class AgentContext:
    """Context for an agent making a request"""

    did: str
    agent_name: str
    agent_type: str
    verified: bool = False
    permissions: Set[KnowledgePermission] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_seen: Optional[str] = None

    def has_permission(self, permission: KnowledgePermission) -> bool:
        """Check if agent has a specific permission"""
        return permission in self.permissions or KnowledgePermission.ADMIN in self.permissions


@dataclass
class AccessDecision:
    """Result of an access control decision"""

    allowed: bool
    agent_did: str
    operation: KnowledgeOperation
    resource: str
    reason: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    audit_id: Optional[str] = None


@dataclass
class AuditLogEntry:
    """Audit log entry for access control"""

    audit_id: str
    agent_did: str
    operation: str
    resource: str
    allowed: bool
    reason: str
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Task Type Authorization Policies
# ============================================================================


class TaskAuthorizationPolicy:
    """
    ABAC policies for task type authorization.

    Maps task types to required permissions and allowed operations.
    """

    # Task type definitions with required permissions
    TASK_POLICIES: Dict[str, Dict[str, Any]] = {
        # Research tasks - read only
        "research": {
            "required_permissions": [KnowledgePermission.READ_ONLY],
            "allowed_operations": [
                KnowledgeOperation.READ,
                KnowledgeOperation.QUERY,
                KnowledgeOperation.SEARCH,
            ],
            "description": "Research tasks require read-only access",
        },
        # Curation tasks - read/write
        "curation": {
            "required_permissions": [KnowledgePermission.READ_WRITE],
            "allowed_operations": [
                KnowledgeOperation.READ,
                KnowledgeOperation.QUERY,
                KnowledgeOperation.SEARCH,
                KnowledgeOperation.WRITE,
                KnowledgeOperation.INGEST,
                KnowledgeOperation.UPDATE,
            ],
            "description": "Curation tasks require read-write access",
        },
        # Ingestion tasks - write focused
        "ingestion": {
            "required_permissions": [KnowledgePermission.READ_WRITE],
            "allowed_operations": [
                KnowledgeOperation.READ,
                KnowledgeOperation.WRITE,
                KnowledgeOperation.INGEST,
            ],
            "description": "Ingestion tasks require write access",
        },
        # Admin tasks - full access
        "admin": {
            "required_permissions": [KnowledgePermission.ADMIN],
            "allowed_operations": list(KnowledgeOperation),
            "description": "Admin tasks require full access",
        },
        # Voice tasks - read only for queries
        "voice": {
            "required_permissions": [KnowledgePermission.READ_ONLY],
            "allowed_operations": [
                KnowledgeOperation.QUERY,
                KnowledgeOperation.SEARCH,
            ],
            "description": "Voice tasks require read access for queries",
        },
        # RAG tasks - standard read/write
        "rag": {
            "required_permissions": [KnowledgePermission.READ_WRITE],
            "allowed_operations": [
                KnowledgeOperation.READ,
                KnowledgeOperation.QUERY,
                KnowledgeOperation.SEARCH,
                KnowledgeOperation.WRITE,
                KnowledgeOperation.INGEST,
            ],
            "description": "RAG tasks require standard read-write access",
        },
        # MC Agent tasks - full access for coordination
        "mc_agent": {
            "required_permissions": [KnowledgePermission.ADMIN],
            "allowed_operations": list(KnowledgeOperation),
            "description": "MC Agent tasks require full access for coordination",
        },
    }

    @classmethod
    def get_policy(cls, task_type: str) -> Optional[Dict[str, Any]]:
        """Get policy for a task type"""
        return cls.TASK_POLICIES.get(task_type)

    @classmethod
    def is_operation_allowed(cls, task_type: str, operation: KnowledgeOperation) -> bool:
        """Check if an operation is allowed for a task type"""
        policy = cls.get_policy(task_type)
        if not policy:
            return False
        return operation in policy["allowed_operations"]

    @classmethod
    def get_required_permissions(cls, task_type: str) -> List[KnowledgePermission]:
        """Get required permissions for a task type"""
        policy = cls.get_policy(task_type)
        if not policy:
            return []
        return policy["required_permissions"]


# ============================================================================
# Qdrant Permission Manager
# ============================================================================


class QdrantPermissionManager:
    """
    Manages Qdrant collection-level permissions.

    Implements collection-level access control for write operations.
    """

    # Default collection permissions
    DEFAULT_COLLECTION_PERMISSIONS: Dict[str, Dict[str, Any]] = {
        "xnai_knowledge": {
            "read_roles": {"user", "service", "admin"},
            "write_roles": {"service", "admin"},
            "admin_roles": {"admin"},
            "public_read": True,
        },
        "xnai_staging": {
            "read_roles": {"service", "admin"},
            "write_roles": {"service", "admin"},
            "admin_roles": {"admin"},
            "public_read": False,
        },
        "xnai_archive": {
            "read_roles": {"admin"},
            "write_roles": {"admin"},
            "admin_roles": {"admin"},
            "public_read": False,
        },
    }

    def __init__(self):
        self._collection_permissions = self.DEFAULT_COLLECTION_PERMISSIONS.copy()

    def get_collection_permissions(self, collection: str) -> Dict[str, Any]:
        """Get permissions for a collection"""
        return self._collection_permissions.get(
            collection,
            {
                "read_roles": {"admin"},
                "write_roles": {"admin"},
                "admin_roles": {"admin"},
                "public_read": False,
            },
        )

    def can_read_collection(self, collection: str, agent_roles: Set[str]) -> bool:
        """Check if agent roles can read from collection"""
        perms = self.get_collection_permissions(collection)
        if perms.get("public_read", False):
            return True
        return bool(agent_roles & perms["read_roles"])

    def can_write_collection(self, collection: str, agent_roles: Set[str]) -> bool:
        """Check if agent roles can write to collection"""
        perms = self.get_collection_permissions(collection)
        return bool(agent_roles & perms["write_roles"])

    def can_admin_collection(self, collection: str, agent_roles: Set[str]) -> bool:
        """Check if agent roles can admin collection"""
        perms = self.get_collection_permissions(collection)
        return bool(agent_roles & perms["admin_roles"])

    def register_collection(
        self,
        collection: str,
        read_roles: Set[str],
        write_roles: Set[str],
        admin_roles: Set[str],
        public_read: bool = False,
    ) -> None:
        """Register a new collection with permissions"""
        self._collection_permissions[collection] = {
            "read_roles": read_roles,
            "write_roles": write_roles,
            "admin_roles": admin_roles,
            "public_read": public_read,
        }
        logger.info(f"Registered collection permissions: {collection}")


# ============================================================================
# Knowledge Access Controller
# ============================================================================


class KnowledgeAccessController:
    """
    Zero-Trust Access Controller for Knowledge Operations.

    Integrates IAM service with knowledge operations, providing:
    - Agent DID validation (R004-2)
    - Task type authorization (R004-3)
    - Qdrant write permissions (R004-4)

    Usage:
        from core.security import KnowledgeAccessController, KnowledgeOperation

        controller = KnowledgeAccessController(iam_db, iam_service)

        # Check access
        decision = await controller.check_access(
            agent_did="did:xnai:cline:cline-1",
            operation=KnowledgeOperation.QUERY,
            resource="xnai_knowledge",
            task_type="rag"
        )

        if decision.allowed:
            # Proceed with operation
            results = await knowledge_client.search(query)
        else:
            raise AccessDeniedError(decision.reason)
    """

    def __init__(
        self,
        iam_db: Any = None,
        iam_service: Any = None,
        audit_log_path: Optional[str] = None,
    ):
        """
        Initialize the access controller.

        Args:
            iam_db: IAM database for agent identity lookup
            iam_service: IAM service for ABAC policy evaluation
            audit_log_path: Path to audit log file
        """
        self.iam_db = iam_db
        self.iam_service = iam_service
        self.qdrant_perms = QdrantPermissionManager()
        self.task_policy = TaskAuthorizationPolicy()

        # Audit log
        self._audit_log_path = audit_log_path or os.getenv(
            "KNOWLEDGE_AUDIT_LOG", "logs/knowledge_access_audit.jsonl"
        )
        self._audit_counter = 0

        # Cache for verified agents
        self._verified_agents: Dict[str, AgentContext] = {}

        logger.info("KnowledgeAccessController initialized")

    # ========================================================================
    # Agent DID Validation (R004-2)
    # ========================================================================

    async def validate_agent_did(self, agent_did: str) -> AgentContext:
        """
        Validate agent DID and return agent context.

        This implements DID validation by:
        1. Looking up the agent in IAM database
        2. Verifying the agent's Ed25519 key is registered
        3. Checking verification status

        Args:
            agent_did: The DID to validate (e.g., "did:xnai:cline:cline-1")

        Returns:
            AgentContext with agent details

        Raises:
            AgentNotVerifiedError: If agent is not verified
            AccessDeniedError: If agent not found
        """
        # Check cache first
        if agent_did in self._verified_agents:
            cached = self._verified_agents[agent_did]
            return cached

        # Look up agent in IAM database
        if self.iam_db:
            agent = self.iam_db.get_agent(agent_did)
            if not agent:
                raise AccessDeniedError(
                    f"Agent not found: {agent_did}",
                    agent_did=agent_did,
                )

            # Build agent context
            context = AgentContext(
                did=agent.did,
                agent_name=agent.agent_name,
                agent_type=agent.agent_type.value,
                verified=agent.verified,
                metadata=agent.metadata,
                last_seen=agent.last_seen,
            )

            # Determine permissions based on agent type
            context.permissions = self._get_agent_permissions(agent)

            # Cache verified agent
            if agent.verified:
                self._verified_agents[agent_did] = context

            return context

        # Fallback for testing without IAM DB
        logger.warning("IAM database not available, using fallback validation")
        return AgentContext(
            did=agent_did,
            agent_name="unknown",
            agent_type="unknown",
            verified=False,
        )

    def _get_agent_permissions(self, agent: Any) -> Set[KnowledgePermission]:
        """Determine permissions based on agent type and metadata"""
        permissions: Set[KnowledgePermission] = set()

        # Map agent types to default permissions
        type_permissions = {
            "cline": {KnowledgePermission.READ_WRITE},
            "copilot": {KnowledgePermission.READ_WRITE},
            "gemini": {KnowledgePermission.READ_WRITE},
            "claude": {KnowledgePermission.READ_WRITE},
            "service": {KnowledgePermission.READ_WRITE},
            "admin": {KnowledgePermission.ADMIN},
        }

        # Get default permissions for agent type
        agent_type = agent.agent_type.value if hasattr(agent.agent_type, "value") else str(agent.agent_type)
        permissions = type_permissions.get(agent_type, {KnowledgePermission.READ_ONLY})

        # Check metadata for additional permissions
        if hasattr(agent, "metadata") and agent.metadata:
            meta_perms = agent.metadata.get("permissions", [])
            for perm in meta_perms:
                try:
                    permissions.add(KnowledgePermission(perm))
                except ValueError:
                    pass

        return permissions

    async def require_verified_agent(self, agent_did: str) -> AgentContext:
        """
        Require that an agent is verified.

        Raises:
            AgentNotVerifiedError: If agent is not verified
        """
        context = await self.validate_agent_did(agent_did)

        if not context.verified:
            raise AgentNotVerifiedError(
                f"Agent not verified: {agent_did}. Complete handshake verification first.",
                agent_did=agent_did,
            )

        return context

    # ========================================================================
    # Task Type Authorization (R004-3)
    # ========================================================================

    async def authorize_task(
        self,
        agent_context: AgentContext,
        task_type: str,
        operation: KnowledgeOperation,
    ) -> AccessDecision:
        """
        Authorize a task type for an agent.

        Checks:
        1. Task type is valid
        2. Operation is allowed for task type
        3. Agent has required permissions

        Args:
            agent_context: The agent's context
            task_type: The type of task (research, curation, etc.)
            operation: The operation being performed

        Returns:
            AccessDecision with authorization result
        """
        # Get task policy
        policy = self.task_policy.get_policy(task_type)

        if not policy:
            return AccessDecision(
                allowed=False,
                agent_did=agent_context.did,
                operation=operation,
                resource="task",
                reason=f"Unknown task type: {task_type}",
            )

        # Check if operation is allowed for task type
        if operation not in policy["allowed_operations"]:
            return AccessDecision(
                allowed=False,
                agent_did=agent_context.did,
                operation=operation,
                resource="task",
                reason=f"Operation {operation.value} not allowed for task type {task_type}",
            )

        # Check if agent has required permissions
        required = policy["required_permissions"]
        has_permission = any(
            perm in agent_context.permissions or KnowledgePermission.ADMIN in agent_context.permissions
            for perm in required
        )

        if not has_permission:
            return AccessDecision(
                allowed=False,
                agent_did=agent_context.did,
                operation=operation,
                resource="task",
                reason=f"Agent lacks required permissions: {[p.value for p in required]}",
            )

        return AccessDecision(
            allowed=True,
            agent_did=agent_context.did,
            operation=operation,
            resource="task",
            reason=f"Authorized for {task_type} task",
        )

    # ========================================================================
    # Qdrant Write Permissions (R004-4)
    # ========================================================================

    async def check_qdrant_access(
        self,
        agent_context: AgentContext,
        operation: KnowledgeOperation,
        collection: str,
    ) -> AccessDecision:
        """
        Check access to Qdrant collection.

        Args:
            agent_context: The agent's context
            operation: The operation being performed
            collection: The Qdrant collection name

        Returns:
            AccessDecision with access result
        """
        # Determine roles from agent type and permissions
        agent_roles: Set[str] = set()
        agent_roles.add(agent_context.agent_type)

        if KnowledgePermission.ADMIN in agent_context.permissions:
            agent_roles.add("admin")
        if KnowledgePermission.READ_WRITE in agent_context.permissions:
            agent_roles.add("service")
        if KnowledgePermission.READ_ONLY in agent_context.permissions:
            agent_roles.add("user")

        # Check based on operation type
        if operation in [KnowledgeOperation.READ, KnowledgeOperation.QUERY, KnowledgeOperation.SEARCH]:
            allowed = self.qdrant_perms.can_read_collection(collection, agent_roles)
            reason = f"Read access {'granted' if allowed else 'denied'} for collection {collection}"

        elif operation in [
            KnowledgeOperation.WRITE,
            KnowledgeOperation.INGEST,
            KnowledgeOperation.UPDATE,
            KnowledgeOperation.DELETE,
        ]:
            allowed = self.qdrant_perms.can_write_collection(collection, agent_roles)
            reason = f"Write access {'granted' if allowed else 'denied'} for collection {collection}"

        elif operation in [KnowledgeOperation.COLLECTION_CREATE, KnowledgeOperation.COLLECTION_DELETE]:
            allowed = self.qdrant_perms.can_admin_collection(collection, agent_roles)
            reason = f"Admin access {'granted' if allowed else 'denied'} for collection {collection}"

        else:
            allowed = False
            reason = f"Unknown operation: {operation.value}"

        return AccessDecision(
            allowed=allowed,
            agent_did=agent_context.did,
            operation=operation,
            resource=f"qdrant:{collection}",
            reason=reason,
        )

    # ========================================================================
    # Unified Access Check
    # ========================================================================

    async def check_access(
        self,
        agent_did: str,
        operation: KnowledgeOperation,
        resource: str,
        task_type: Optional[str] = None,
        require_verified: bool = True,
    ) -> AccessDecision:
        """
        Unified access check for knowledge operations.

        Performs all access checks in sequence:
        1. Agent DID validation
        2. Task type authorization (if task_type provided)
        3. Qdrant collection access (if resource is a collection)

        Args:
            agent_did: The agent's DID
            operation: The operation being performed
            resource: The resource being accessed (collection name)
            task_type: Optional task type for authorization
            require_verified: Whether to require verified agent

        Returns:
            AccessDecision with final access result
        """
        try:
            # Step 1: Validate agent DID
            if require_verified:
                agent_context = await self.require_verified_agent(agent_did)
            else:
                agent_context = await self.validate_agent_did(agent_did)

            # Step 2: Check task type authorization
            if task_type:
                task_decision = await self.authorize_task(
                    agent_context, task_type, operation
                )
                if not task_decision.allowed:
                    await self._log_audit(task_decision)
                    return task_decision

            # Step 3: Check Qdrant access
            qdrant_decision = await self.check_qdrant_access(
                agent_context, operation, resource
            )

            # Log audit
            await self._log_audit(qdrant_decision)

            return qdrant_decision

        except AgentNotVerifiedError as e:
            decision = AccessDecision(
                allowed=False,
                agent_did=agent_did,
                operation=operation,
                resource=resource,
                reason=str(e),
            )
            await self._log_audit(decision)
            return decision

        except AccessDeniedError as e:
            decision = AccessDecision(
                allowed=False,
                agent_did=agent_did,
                operation=operation,
                resource=resource,
                reason=str(e),
            )
            await self._log_audit(decision)
            return decision

    # ========================================================================
    # Audit Logging
    # ========================================================================

    async def _log_audit(self, decision: AccessDecision) -> None:
        """Log access decision to audit log"""
        try:
            self._audit_counter += 1
            audit_id = f"AUDIT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{self._audit_counter:06d}"

            entry = AuditLogEntry(
                audit_id=audit_id,
                agent_did=decision.agent_did,
                operation=decision.operation.value,
                resource=decision.resource,
                allowed=decision.allowed,
                reason=decision.reason,
                timestamp=decision.timestamp,
            )

            # Ensure log directory exists
            log_dir = os.path.dirname(self._audit_log_path)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)

            # Write to file synchronously (simple approach for audit logs)
            with open(self._audit_log_path, "a") as f:
                f.write(json.dumps(entry.__dict__) + "\n")

            decision.audit_id = audit_id

        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def clear_cache(self) -> None:
        """Clear the verified agent cache"""
        self._verified_agents.clear()
        logger.info("Agent cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get access controller statistics"""
        return {
            "cached_agents": len(self._verified_agents),
            "audit_counter": self._audit_counter,
            "collections_registered": len(self.qdrant_perms._collection_permissions),
            "task_types_supported": list(self.task_policy.TASK_POLICIES.keys()),
        }


# ============================================================================
# Decorator for Access Control
# ============================================================================


def require_knowledge_access(
    operation: KnowledgeOperation,
    resource: str,
    task_type: Optional[str] = None,
):
    """
    Decorator for knowledge access control.

    Usage:
        @require_knowledge_access(KnowledgeOperation.QUERY, "xnai_knowledge", "rag")
        async def search_knowledge(agent_did: str, query: str):
            # Access already verified
            return await knowledge_client.search(query)
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract agent_did from kwargs or first argument
            agent_did = kwargs.get("agent_did")
            if not agent_did and args:
                # Assume first string argument might be agent_did
                for arg in args:
                    if isinstance(arg, str) and arg.startswith("did:"):
                        agent_did = arg
                        break

            if not agent_did:
                raise AccessDeniedError("agent_did required for access control")

            # Get global controller
            controller = get_global_controller()
            decision = await controller.check_access(
                agent_did, operation, resource, task_type
            )

            if not decision.allowed:
                raise AccessDeniedError(
                    decision.reason,
                    agent_did=agent_did,
                    operation=operation.value,
                    resource=resource,
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# ============================================================================
# Global Controller Instance
# ============================================================================

_global_controller: Optional[KnowledgeAccessController] = None


def get_global_controller() -> KnowledgeAccessController:
    """Get or create global access controller"""
    global _global_controller
    if _global_controller is None:
        _global_controller = KnowledgeAccessController()
    return _global_controller


def set_global_controller(controller: KnowledgeAccessController) -> None:
    """Set the global access controller"""
    global _global_controller
    _global_controller = controller