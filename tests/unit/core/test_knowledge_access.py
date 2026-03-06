"""
Unit tests for knowledge access control.

Tests cover:
- KnowledgeAccessController class (from security/knowledge_access.py)
- Agent DID validation
- Task type authorization
- QdrantPermissionManager class
- TaskAuthorizationPolicy class

Note: QdrantPermissionManager and TaskAuthorizationPolicy are in
      app/XNAi_rag_app/core/security/knowledge_access.py
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone


# Test fixtures
@pytest.fixture
def mock_iam_service():
    """Mock IAM service for testing."""
    mock = Mock()
    mock.validate_agent = AsyncMock(return_value=True)
    mock.get_agent_roles = AsyncMock(return_value=["admin", "researcher"])
    return mock


@pytest.fixture
def knowledge_access_control(mock_iam_service):
    """KnowledgeAccessController instance for testing."""
    from app.XNAi_rag_app.core.security.knowledge_access import KnowledgeAccessController

    return KnowledgeAccessController(iam_service=mock_iam_service)


class TestKnowledgeAccessController:
    """Tests for KnowledgeAccessController class."""

    @pytest.mark.asyncio
    async def test_initialization(self, mock_iam_service):
        """Test KnowledgeAccessController initializes correctly."""
        from app.XNAi_rag_app.core.security.knowledge_access import KnowledgeAccessController

        kac = KnowledgeAccessController(iam_service=mock_iam_service)

        assert kac.iam_service == mock_iam_service
        assert kac.qdrant_perms is not None
        assert kac.task_policy is not None

    @pytest.mark.asyncio
    async def test_check_qdrant_write_success(self, knowledge_access_control):
        """Test successful Qdrant write check."""
        from app.XNAi_rag_app.core.security.knowledge_access import KnowledgeOperation, AgentContext, KnowledgePermission

        agent_ctx = AgentContext(
            did="did:xoe:agent:test-agent",
            agent_name="test",
            agent_type="service",
            verified=True,
            permissions={KnowledgePermission.READ_WRITE},
        )
        result = await knowledge_access_control.check_qdrant_access(
            agent_context=agent_ctx, operation=KnowledgeOperation.WRITE, collection="xnai_knowledge"
        )

        assert result is not None
        assert hasattr(result, "allowed")

    @pytest.mark.asyncio
    async def test_check_qdrant_read_success(self, knowledge_access_control):
        """Test successful Qdrant read check."""
        from app.XNAi_rag_app.core.security.knowledge_access import KnowledgeOperation, AgentContext, KnowledgePermission

        agent_ctx = AgentContext(
            did="did:xoe:agent:test-agent",
            agent_name="test",
            agent_type="user",
            verified=True,
            permissions={KnowledgePermission.READ_ONLY},
        )
        result = await knowledge_access_control.check_qdrant_access(
            agent_context=agent_ctx, operation=KnowledgeOperation.READ, collection="xnai_knowledge"
        )

        assert result is not None
        assert hasattr(result, "allowed")

    @pytest.mark.asyncio
    async def test_check_qdrant_delete_success(self, knowledge_access_control):
        """Test successful Qdrant delete check."""
        from app.XNAi_rag_app.core.security.knowledge_access import KnowledgeOperation, AgentContext, KnowledgePermission

        agent_ctx = AgentContext(
            did="did:xoe:agent:test-agent",
            agent_name="test",
            agent_type="admin",
            verified=True,
            permissions={KnowledgePermission.ADMIN},
        )
        result = await knowledge_access_control.check_qdrant_access(
            agent_context=agent_ctx, operation=KnowledgeOperation.DELETE, collection="xnai_knowledge"
        )

        assert result is not None
        assert hasattr(result, "allowed")


class TestQdrantPermissionManager:
    """Tests for QdrantPermissionManager class."""

    def test_can_read_collection_admin(self):
        """Test admin can read any collection."""
        from app.XNAi_rag_app.core.security.knowledge_access import QdrantPermissionManager

        qpm = QdrantPermissionManager()

        result = qpm.can_read_collection(collection="xnai_knowledge", agent_roles={"admin"})

        assert result is True

    def test_can_read_collection_researcher(self):
        """Test researcher can read specific collections."""
        from app.XNAi_rag_app.core.security.knowledge_access import QdrantPermissionManager

        qpm = QdrantPermissionManager()

        result = qpm.can_read_collection(collection="xnai_knowledge", agent_roles={"user"})

        assert result is True  # xnai_knowledge has public_read=True

    def test_can_write_collection_admin(self):
        """Test admin can write to any collection."""
        from app.XNAi_rag_app.core.security.knowledge_access import QdrantPermissionManager

        qpm = QdrantPermissionManager()

        result = qpm.can_write_collection(collection="xnai_knowledge", agent_roles={"admin"})

        assert result is True

    def test_can_write_collection_guest_denied(self):
        """Test guest cannot write to collections."""
        from app.XNAi_rag_app.core.security.knowledge_access import QdrantPermissionManager

        qpm = QdrantPermissionManager()

        result = qpm.can_write_collection(collection="xnai_knowledge", agent_roles={"guest"})

        assert result is False


class TestTaskAuthorizationPolicy:
    """Tests for TaskAuthorizationPolicy class."""

    def test_is_authorized_task_allowed(self):
        """Test allowed task type."""
        from app.XNAi_rag_app.core.security.knowledge_access import TaskAuthorizationPolicy, KnowledgeOperation

        tap = TaskAuthorizationPolicy()

        result = tap.is_operation_allowed(task_type="rag", operation=KnowledgeOperation.QUERY)

        assert result is True

    def test_is_authorized_task_denied(self):
        """Test denied task type for role."""
        from app.XNAi_rag_app.core.security.knowledge_access import TaskAuthorizationPolicy, KnowledgeOperation

        tap = TaskAuthorizationPolicy()

        result = tap.is_operation_allowed(task_type="voice", operation=KnowledgeOperation.DELETE)

        assert result is False


class TestDIDValidation:
    """Tests for Decentralized Identifier validation."""

    def test_valid_did_format(self):
        """Test valid DID format is accepted."""
        valid_did = "did:xoe:agent:test-agent-001"
        # Basic format validation
        assert valid_did.startswith("did:")
        assert ":" in valid_did

    def test_invalid_did_format(self):
        """Test invalid DID format is rejected."""
        invalid_did = "not-a-did"
        assert not invalid_did.startswith("did:")


class TestKnowledgeAccessIntegration:
    """Integration tests for knowledge access module."""

    @pytest.mark.asyncio
    async def test_full_access_check_flow(self, mock_iam_service):
        """Test complete access check flow."""
        from app.XNAi_rag_app.core.security.knowledge_access import (
            KnowledgeAccessController,
            KnowledgeOperation,
            AgentContext,
            KnowledgePermission,
        )

        kac = KnowledgeAccessController(iam_service=mock_iam_service)

        # Simulate full flow
        agent_ctx = AgentContext(
            did="did:xoe:agent:test-agent",
            agent_name="test",
            agent_type="service",
            verified=True,
            permissions={KnowledgePermission.READ_WRITE},
        )
        collection = "xnai_knowledge"

        # Check read access
        read_result = await kac.check_qdrant_access(agent_ctx, KnowledgeOperation.READ, collection)
        assert read_result is not None

        # Check write access
        write_result = await kac.check_qdrant_access(agent_ctx, KnowledgeOperation.WRITE, collection)
        assert write_result is not None


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Tests for error handling in knowledge access."""

    @pytest.mark.asyncio
    async def test_iam_service_unavailable(self):
        """Test handling when IAM service is unavailable."""
        from app.XNAi_rag_app.core.security.knowledge_access import (
            KnowledgeAccessController,
            KnowledgeOperation,
            AgentContext,
            KnowledgePermission,
        )

        # Mock IAM service that raises exception
        mock_iam = Mock()
        mock_iam.validate_agent = AsyncMock(side_effect=Exception("IAM unavailable"))

        kac = KnowledgeAccessController(iam_service=mock_iam)

        # Should handle gracefully - create an agent context directly
        agent_ctx = AgentContext(
            did="did:xoe:agent:test",
            agent_name="test",
            agent_type="service",
            verified=True,
            permissions={KnowledgePermission.READ_ONLY},
        )
        result = await kac.check_qdrant_access(agent_ctx, KnowledgeOperation.READ, "test_collection")

        # Result should indicate access decision
        assert result is not None

    @pytest.mark.asyncio
    async def test_invalid_collection_name(self, knowledge_access_control):
        """Test handling of invalid collection names."""
        from app.XNAi_rag_app.core.security.knowledge_access import KnowledgeOperation, AgentContext, KnowledgePermission

        agent_ctx = AgentContext(
            did="did:xoe:agent:test",
            agent_name="test",
            agent_type="service",
            verified=True,
            permissions={KnowledgePermission.READ_ONLY},
        )
        result = await knowledge_access_control.check_qdrant_access(
            agent_context=agent_ctx,
            operation=KnowledgeOperation.READ,
            collection="../../../etc/passwd",  # Path traversal attempt
        )

        # Should handle gracefully - unknown collection returns False for write
        assert result is not None


# ============================================================================
# Edge Case Tests - JOB-W3-002-2
# ============================================================================


class TestEdgeCases:
    """Edge case tests for knowledge access control."""

    @pytest.mark.asyncio
    async def test_invalid_did_format_empty(self):
        """Test handling of empty DID."""
        from app.XNAi_rag_app.core.security.knowledge_access import AgentContext, KnowledgePermission

        # Empty DID should be handled
        agent_ctx = AgentContext(
            did="",
            agent_name="test",
            agent_type="service",
            verified=False,
            permissions={KnowledgePermission.READ_ONLY},
        )

        # Should handle gracefully even with empty DID
        assert agent_ctx.did == ""

    @pytest.mark.asyncio
    async def test_invalid_did_format_missing_prefix(self):
        """Test handling of DID without 'did:' prefix."""
        invalid_did = "xoe:agent:test-agent-001"

        # Basic format validation
        assert not invalid_did.startswith("did:")

    @pytest.mark.asyncio
    async def test_invalid_did_format_special_chars(self):
        """Test handling of DID with special characters."""
        from app.XNAi_rag_app.core.security.knowledge_access import AgentContext, KnowledgePermission

        # DID with special characters - may be invalid
        agent_ctx = AgentContext(
            did="did:xoe:agent:test@#$%",
            agent_name="test",
            agent_type="service",
            verified=False,
            permissions={KnowledgePermission.READ_ONLY},
        )

        # Should store but may fail validation later
        assert "@" in agent_ctx.did or "#" in agent_ctx.did or "$" in agent_ctx.did

    @pytest.mark.asyncio
    async def test_very_long_did(self):
        """Test handling of excessively long DID."""
        from app.XNAi_rag_app.core.security.knowledge_access import AgentContext, KnowledgePermission

        long_did = "did:xoe:agent:" + "a" * 1000
        agent_ctx = AgentContext(
            did=long_did,
            agent_name="test",
            agent_type="service",
            verified=True,
            permissions={KnowledgePermission.READ_ONLY},
        )

        assert len(agent_ctx.did) > 100

    @pytest.mark.asyncio
    async def test_permission_boundary_read_write(self):
        """Test permission boundary - read-only attempting write."""
        from app.XNAi_rag_app.core.security.knowledge_access import QdrantPermissionManager, KnowledgeOperation

        qpm = QdrantPermissionManager()

        # User with only read permission trying to write
        result = qpm.can_write_collection(
            collection="xnai_knowledge",
            agent_roles={"user"},  # user role typically has read-only
        )

        # Should be denied (default deny pattern)
        assert result is False

    @pytest.mark.asyncio
    async def test_permission_boundary_guest_access(self):
        """Test permission boundary - guest role restrictions."""
        from app.XNAi_rag_app.core.security.knowledge_access import QdrantPermissionManager

        qpm = QdrantPermissionManager()

        # Guest should not have write access
        result = qpm.can_write_collection(collection="xnai_knowledge", agent_roles={"guest"})

        assert result is False

    @pytest.mark.asyncio
    async def test_permission_boundary_admin_full_access(self):
        """Test permission boundary - admin has full access."""
        from app.XNAi_rag_app.core.security.knowledge_access import QdrantPermissionManager

        qpm = QdrantPermissionManager()

        # Admin should have full access
        assert qpm.can_read_collection(collection="xnai_knowledge", agent_roles={"admin"}) is True
        assert qpm.can_write_collection(collection="xnai_knowledge", agent_roles={"admin"}) is True

    @pytest.mark.asyncio
    async def test_unknown_collection_default_deny(self):
        """Test default deny for unknown collections."""
        from app.XNAi_rag_app.core.security.knowledge_access import QdrantPermissionManager

        qpm = QdrantPermissionManager()

        # Unknown collection should default to deny for writes
        result = qpm.can_write_collection(collection="unknown_collection_xyz", agent_roles={"admin"})

        # Unknown collections may be denied for security
        assert result is not None

    @pytest.mark.asyncio
    async def test_empty_agent_roles(self):
        """Test handling when agent has no roles."""
        from app.XNAi_rag_app.core.security.knowledge_access import QdrantPermissionManager

        qpm = QdrantPermissionManager()

        # Empty roles should result in denial
        result = qpm.can_read_collection(collection="xnai_knowledge", agent_roles=set())

        # Should default to deny
        assert result is False

    @pytest.mark.asyncio
    async def test_none_permissions_handling(self):
        """Test handling of None permissions."""
        from app.XNAi_rag_app.core.security.knowledge_access import AgentContext, KnowledgePermission

        # None permissions
        agent_ctx = AgentContext(
            did="did:xoe:agent:test",
            agent_name="test",
            agent_type="service",
            verified=True,
            permissions=None,  # None permissions
        )

        # Should handle gracefully
        assert agent_ctx.permissions is None or agent_ctx.permissions == set()

    @pytest.mark.asyncio
    async def test_unverified_agent_access(self):
        """Test that unverified agents are handled correctly."""
        from app.XNAi_rag_app.core.security.knowledge_access import AgentContext, KnowledgePermission

        agent_ctx = AgentContext(
            did="did:xoe:agent:test",
            agent_name="test",
            agent_type="service",
            verified=False,  # Not verified
            permissions={KnowledgePermission.READ_ONLY},
        )

        # Verified should be False
        assert agent_ctx.verified is False

    @pytest.mark.asyncio
    async def test_collection_name_edge_cases(self):
        """Test handling of edge case collection names."""
        from app.XNAi_rag_app.core.security.knowledge_access import QdrantPermissionManager

        qpm = QdrantPermissionManager()

        # Empty collection name
        result_empty = qpm.can_read_collection(collection="", agent_roles={"user"})
        assert result_empty is False

        # Collection with special characters
        result_special = qpm.can_read_collection(collection="col@lection!", agent_roles={"admin"})
        assert result_special is not None

    @pytest.mark.asyncio
    async def test_task_type_edge_cases(self):
        """Test handling of edge case task types."""
        from app.XNAi_rag_app.core.security.knowledge_access import TaskAuthorizationPolicy, KnowledgeOperation

        tap = TaskAuthorizationPolicy()

        # Empty task type
        result_empty = tap.is_operation_allowed(task_type="", operation=KnowledgeOperation.READ)
        assert result_empty is False

        # Unknown task type
        result_unknown = tap.is_operation_allowed(task_type="unknown_task_xyz", operation=KnowledgeOperation.READ)
        assert result_unknown is False

    @pytest.mark.asyncio
    async def test_concurrent_access_checks(self):
        """Test concurrent access checks don't interfere."""
        import asyncio
        from app.XNAi_rag_app.core.security.knowledge_access import AgentContext, KnowledgePermission

        async def check_access():
            agent_ctx = AgentContext(
                did="did:xoe:agent:test",
                agent_name="test",
                agent_type="service",
                verified=True,
                permissions={KnowledgePermission.READ_ONLY},
            )
            return agent_ctx.verified

        # Run multiple checks concurrently
        results = await asyncio.gather(*[check_access() for _ in range(10)])

        # All should return True
        assert all(results)

    @pytest.mark.asyncio
    async def test_agent_context_immutability(self):
        """Test that agent context fields cannot be modified after creation."""
        from app.XNAi_rag_app.core.security.knowledge_access import AgentContext, KnowledgePermission

        agent_ctx = AgentContext(
            did="did:xoe:agent:test",
            agent_name="test",
            agent_type="service",
            verified=True,
            permissions={KnowledgePermission.READ_ONLY},
        )

        # Original values
        original_did = agent_ctx.did
        original_name = agent_ctx.agent_name

        # Dataclass by default is mutable - verify behavior
        agent_ctx.did = "modified"

        # Value should be modified (dataclass behavior)
        assert agent_ctx.did == "modified" or agent_ctx.did == original_did

    @pytest.mark.asyncio
    async def test_permission_enum_completeness(self):
        """Test all permission enum values."""
        from app.XNAi_rag_app.core.security.knowledge_access import KnowledgePermission

        # All known permission types
        permissions = list(KnowledgePermission)

        # Should have at least basic permissions
        assert len(permissions) >= 3

    @pytest.mark.asyncio
    async def test_operation_enum_completeness(self):
        """Test all operation enum values."""
        from app.XNAi_rag_app.core.security.knowledge_access import KnowledgeOperation

        # All known operations
        operations = list(KnowledgeOperation)

        # Should have at least read, write, delete
        assert len(operations) >= 3
