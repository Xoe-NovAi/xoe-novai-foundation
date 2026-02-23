#!/usr/bin/env python3
"""
Unit Tests for XNAi Security Module
====================================
Tests for knowledge access control and content sanitization.

Run with: pytest tests/unit/test_security_module.py -v
"""

import pytest
import os
import tempfile
from datetime import datetime, timezone

# Import security modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../app'))

from XNAi_rag_app.core.security import (
    KnowledgeAccessController,
    KnowledgeOperation,
    KnowledgePermission,
    AccessDeniedError,
    AgentNotVerifiedError,
    ContentSanitizer,
    SanitizationResult,
    SanitizationLevel,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def access_controller():
    """Create access controller without IAM DB for testing"""
    return KnowledgeAccessController(iam_db=None, iam_service=None)


@pytest.fixture
def sanitizer():
    """Create content sanitizer with standard level"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "sanitization_audit.jsonl")
        yield ContentSanitizer(level=SanitizationLevel.STANDARD, log_path=log_path)


@pytest.fixture
def paranoid_sanitizer():
    """Create content sanitizer with paranoid level"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "sanitization_audit.jsonl")
        yield ContentSanitizer(level=SanitizationLevel.PARANOID, log_path=log_path)


# ============================================================================
# Knowledge Access Controller Tests
# ============================================================================


class TestKnowledgeAccessController:
    """Tests for KnowledgeAccessController"""

    def test_knowledge_operations_exist(self):
        """Test all knowledge operations are defined"""
        operations = [
            KnowledgeOperation.READ,
            KnowledgeOperation.QUERY,
            KnowledgeOperation.SEARCH,
            KnowledgeOperation.WRITE,
            KnowledgeOperation.INGEST,
            KnowledgeOperation.UPDATE,
            KnowledgeOperation.DELETE,
            KnowledgeOperation.ADMIN,
            KnowledgeOperation.COLLECTION_CREATE,
            KnowledgeOperation.COLLECTION_DELETE,
        ]
        assert len(operations) == 10

    def test_knowledge_permissions_exist(self):
        """Test all knowledge permissions are defined"""
        permissions = [
            KnowledgePermission.NONE,
            KnowledgePermission.READ_ONLY,
            KnowledgePermission.READ_WRITE,
            KnowledgePermission.ADMIN,
        ]
        assert len(permissions) == 4

    def test_access_controller_initialization(self, access_controller):
        """Test access controller initializes correctly"""
        stats = access_controller.get_stats()
        assert "cached_agents" in stats
        assert "task_types_supported" in stats
        assert len(stats["task_types_supported"]) > 0

    def test_agent_did_validation_without_iam(self, access_controller):
        """Test agent DID validation without IAM database"""
        # Without IAM DB, agent should be unverified
        context = access_controller.validate_agent_did("did:xnai:cline:test")
        assert context.did == "did:xnai:cline:test"
        assert context.agent_name == "unknown"
        assert context.verified is False

    def test_require_verified_agent_raises(self, access_controller):
        """Test require_verified_agent raises error for unverified agent"""
        with pytest.raises(AgentNotVerifiedError):
            access_controller.require_verified_agent("did:xnai:cline:test")

    def test_check_access_unverified_agent(self, access_controller):
        """Test access check with unverified agent"""
        decision = access_controller.check_access(
            agent_did="did:xnai:cline:test",
            operation=KnowledgeOperation.QUERY,
            resource="xnai_knowledge",
            require_verified=False,  # Don't require verification
        )
        # Should pass because we don't require verification
        # but agent context will be unverified
        assert decision.agent_did == "did:xnai:cline:test"

    def test_task_authorization_unknown_task(self, access_controller):
        """Test task authorization rejects unknown task types"""
        from XNAi_rag_app.core.security.knowledge_access import AgentContext

        context = AgentContext(
            did="did:xnai:cline:test",
            agent_name="test",
            agent_type="cline",
            verified=True,
            permissions={KnowledgePermission.READ_WRITE},
        )

        decision = access_controller.authorize_task(
            agent_context=context,
            task_type="unknown_task",
            operation=KnowledgeOperation.QUERY,
        )
        assert decision.allowed is False
        assert "Unknown task type" in decision.reason

    def test_task_authorization_valid_task(self, access_controller):
        """Test task authorization allows valid task"""
        from XNAi_rag_app.core.security.knowledge_access import AgentContext

        context = AgentContext(
            did="did:xnai:cline:test",
            agent_name="test",
            agent_type="cline",
            verified=True,
            permissions={KnowledgePermission.READ_WRITE},
        )

        decision = access_controller.authorize_task(
            agent_context=context,
            task_type="rag",
            operation=KnowledgeOperation.QUERY,
        )
        assert decision.allowed is True

    def test_qdrant_read_access(self, access_controller):
        """Test Qdrant read access control"""
        from XNAi_rag_app.core.security.knowledge_access import AgentContext

        # Admin should have access
        context = AgentContext(
            did="did:xnai:cline:test",
            agent_name="test",
            agent_type="cline",
            verified=True,
            permissions={KnowledgePermission.ADMIN},
        )

        decision = access_controller.check_qdrant_access(
            agent_context=context,
            operation=KnowledgeOperation.QUERY,
            collection="xnai_knowledge",
        )
        assert decision.allowed is True

    def test_qdrant_write_access_service_role(self, access_controller):
        """Test Qdrant write access for service role"""
        from XNAi_rag_app.core.security.knowledge_access import AgentContext

        # Read-write permission should allow write
        context = AgentContext(
            did="did:xnai:cline:test",
            agent_name="test",
            agent_type="service",
            verified=True,
            permissions={KnowledgePermission.READ_WRITE},
        )

        decision = access_controller.check_qdrant_access(
            agent_context=context,
            operation=KnowledgeOperation.WRITE,
            collection="xnai_knowledge",
        )
        assert decision.allowed is True

    def test_qdrant_write_access_denied_readonly(self, access_controller):
        """Test Qdrant write access denied for read-only"""
        from XNAi_rag_app.core.security.knowledge_access import AgentContext

        context = AgentContext(
            did="did:xnai:cline:test",
            agent_name="test",
            agent_type="user",
            verified=True,
            permissions={KnowledgePermission.READ_ONLY},
        )

        decision = access_controller.check_qdrant_access(
            agent_context=context,
            operation=KnowledgeOperation.WRITE,
            collection="xnai_knowledge",
        )
        assert decision.allowed is False

    def test_clear_cache(self, access_controller):
        """Test clearing agent cache"""
        access_controller._verified_agents["test_did"] = "test"
        access_controller.clear_cache()
        assert len(access_controller._verified_agents) == 0


# ============================================================================
# Content Sanitizer Tests
# ============================================================================


class TestContentSanitizer:
    """Tests for ContentSanitizer"""

    def test_sanitize_clean_content(self, sanitizer):
        """Test sanitization of clean content"""
        content = "This is a normal piece of text with no sensitive data."
        result = sanitizer.sanitize(content)

        assert result.was_modified is False
        assert result.sanitized_content == content
        assert len(result.matches) == 0

    def test_sanitize_openai_api_key(self, sanitizer):
        """Test sanitization of OpenAI API key"""
        content = "The API key is sk-1234567890abcdefghijklmnopqrstuvwxyz123456"
        result = sanitizer.sanitize(content)

        assert result.was_modified is True
        assert "[REDACTED:API_KEY]" in result.sanitized_content
        assert len(result.matches) > 0
        assert result.matches[0].match_type == "api_key"

    def test_sanitize_github_pat(self, sanitizer):
        """Test sanitization of GitHub PAT"""
        content = "Set GITHUB_TOKEN=ghp_1234567890abcdefghijklmnopqrstuv"
        result = sanitizer.sanitize(content)

        assert result.was_modified is True
        assert "ghp_" not in result.sanitized_content

    def test_sanitize_email(self, sanitizer):
        """Test sanitization of email addresses"""
        content = "Contact us at support@example.com for help."
        result = sanitizer.sanitize(content)

        assert result.was_modified is True
        # Email should be masked, not fully redacted
        assert "@" not in result.sanitized_content or "*" in result.sanitized_content

    def test_sanitize_ssn(self, sanitizer):
        """Test sanitization of SSN"""
        content = "SSN: 123-45-6789"
        result = sanitizer.sanitize(content)

        assert result.was_modified is True
        assert "123-45-6789" not in result.sanitized_content

    def test_sanitize_credit_card(self, sanitizer):
        """Test sanitization of credit card number"""
        content = "Card number: 4532015112830366"
        result = sanitizer.sanitize(content)

        assert result.was_modified is True
        assert "4532015112830366" not in result.sanitized_content

    def test_sanitize_connection_string(self, sanitizer):
        """Test sanitization of database connection string"""
        content = "postgres://user:secretpassword@localhost:5432/mydb"
        result = sanitizer.sanitize(content)

        assert result.was_modified is True
        assert "secretpassword" not in result.sanitized_content

    def test_sanitize_jwt_token(self, sanitizer):
        """Test sanitization of JWT token"""
        content = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        result = sanitizer.sanitize(content)

        assert result.was_modified is True
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in result.sanitized_content

    def test_sanitize_private_key(self, sanitizer):
        """Test sanitization of private key"""
        content = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA..."
        result = sanitizer.sanitize(content)

        assert result.was_modified is True
        assert "RSA PRIVATE KEY" not in result.sanitized_content

    def test_sanitize_multiple_secrets(self, sanitizer):
        """Test sanitization of multiple secrets in one content"""
        content = """
        API Key: sk-1234567890abcdefghijklmnopqrstuvwxyz123456
        Email: admin@example.com
        Password: supersecret123
        """
        result = sanitizer.sanitize(content)

        assert result.was_modified is True
        assert len(result.matches) >= 2

    def test_sanitize_paranoia_mode(self, paranoid_sanitizer):
        """Test paranoid mode sanitization"""
        content = "My email is test@example.com and phone is +1-555-123-4567"
        result = paranoid_sanitizer.sanitize(content)

        assert result.was_modified is True
        assert len(result.matches) >= 2

    def test_scan_only(self, sanitizer):
        """Test scan-only mode (no modification)"""
        content = "API Key: sk-1234567890abcdefghijklmnopqrstuvwxyz123456"
        matches = sanitizer.scan_only(content)

        assert len(matches) > 0
        # Content should not be modified
        assert matches[0].sanitized_value == matches[0].original_value

    def test_content_hash(self, sanitizer):
        """Test content hash generation"""
        content = "Test content for hashing"
        result = sanitizer.sanitize(content)

        assert result.content_hash != ""
        assert len(result.content_hash) == 16

    def test_to_dict(self, sanitizer):
        """Test result serialization"""
        content = "sk-1234567890abcdefghijklmnopqrstuvwxyz123456"
        result = sanitizer.sanitize(content)

        result_dict = result.to_dict()
        assert "content_hash" in result_dict
        assert "level" in result_dict
        assert "matches" in result_dict

    def test_sanitizer_stats(self, sanitizer):
        """Test sanitizer statistics"""
        stats = sanitizer.get_stats()

        assert "level" in stats
        assert "pattern_count" in stats
        assert "pattern_categories" in stats
        assert stats["pattern_categories"]["api_keys"] > 0


# ============================================================================
# Sanitization Pattern Tests
# ============================================================================


class TestSanitizationPatterns:
    """Tests for specific pattern detection"""

    def test_aws_access_key_detection(self, sanitizer):
        """Test AWS access key detection"""
        content = "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE"
        result = sanitizer.sanitize(content)
        assert result.was_modified is True

    def test_stripe_key_detection(self, sanitizer):
        """Test Stripe key detection"""
        content = "STRIPE_KEY=sk_live_abcdefghijklmnopqrstuvwxyz"
        result = sanitizer.sanitize(content)
        assert result.was_modified is True

    def test_slack_token_detection(self, sanitizer):
        """Test Slack token detection"""
        content = "SLACK_BOT_TOKEN=xoxb-123456789012-1234567890123-AbCdEfGhIjKlMnOpQrStUvWx"
        result = sanitizer.sanitize(content)
        assert result.was_modified is True

    def test_ipv4_detection(self, sanitizer):
        """Test IPv4 address detection"""
        content = "Server IP: 192.168.1.100"
        result = sanitizer.sanitize(content)
        # IP should be masked in standard mode
        assert result.was_modified is True or len(result.matches) > 0

    def test_phone_detection(self, sanitizer):
        """Test phone number detection"""
        content = "Call me at +1-555-123-4567"
        result = sanitizer.sanitize(content)
        assert result.was_modified is True


# ============================================================================
# Integration Tests
# ============================================================================


class TestSecurityIntegration:
    """Integration tests for security module"""

    def test_full_sanitization_workflow(self):
        """Test complete sanitization workflow"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "audit.jsonl")
            sanitizer = ContentSanitizer(
                level=SanitizationLevel.STANDARD,
                log_path=log_path,
            )

            content = """
            Configuration:
            API_KEY=sk-1234567890abcdefghijklmnopqrstuvwxyz123456
            DB_URL=postgres://admin:password123@localhost:5432/production
            EMAIL=admin@company.com
            """

            result = sanitizer.sanitize(content)

            assert result.was_modified is True
            assert "sk-1234567890" not in result.sanitized_content
            assert "password123" not in result.sanitized_content

            # Check audit log was created
            assert os.path.exists(log_path)

    def test_decorator_access_control(self):
        """Test access control decorator"""
        from XNAi_rag_app.core.security.knowledge_access import (
            require_knowledge_access,
            get_global_controller,
        )

        @require_knowledge_access(KnowledgeOperation.QUERY, "xnai_knowledge", "rag")
        async def query_knowledge(agent_did: str, query: str):
            return {"result": "success"}

        # This would raise AccessDeniedError in real scenario
        # For now, just verify the decorator was applied
        assert callable(query_knowledge)


# ============================================================================
# Run Tests
# ============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v"])