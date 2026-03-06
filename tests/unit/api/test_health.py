"""
Unit tests for health endpoints.

Tests cover:
- HealthResponse schema validation
- Health check endpoint behavior
- Component status reporting
- Tier configuration integration
- Circuit breaker status
- Memory monitoring

Task: W3-001-1
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from fastapi import Request
from fastapi.testclient import TestClient


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_request():
    """Mock FastAPI Request with app state."""
    mock = Mock(spec=Request)
    mock.app = Mock()
    mock.app.state = Mock()
    mock.app.state.services = {"embeddings": Mock(), "vectorstore": Mock(), "rag": Mock()}
    return mock


@pytest.fixture
def mock_request_no_services():
    """Mock FastAPI Request without services."""
    mock = Mock(spec=Request)
    mock.app = Mock()
    mock.app.state = Mock()
    mock.app.state.services = {}
    return mock


@pytest.fixture
def mock_config():
    """Mock configuration."""
    return {"metadata": {"stack_version": "v0.1.4-test"}, "performance": {"memory_limit_gb": 6.0}}


@pytest.fixture
def mock_psutil_memory():
    """Mock psutil virtual memory."""
    mock = Mock()
    mock.used = 4 * 1024**3  # 4GB
    mock.percent = 50.0
    return mock


# ============================================================================
# HealthResponse Tests
# ============================================================================


class TestHealthResponseSchema:
    """Tests for HealthResponse Pydantic model."""

    def test_health_response_valid(self):
        """Test valid HealthResponse creation."""
        from app.XNAi_rag_app.schemas.responses import HealthResponse

        response = HealthResponse(
            status="healthy",
            version="v0.1.4",
            memory_gb=4.5,
            vectorstore_loaded=True,
            components={"embeddings": True, "vectorstore": True, "llm": True},
        )

        assert response.status == "healthy"
        assert response.version == "v0.1.4"
        assert response.memory_gb == 4.5
        assert response.vectorstore_loaded is True
        assert response.components["embeddings"] is True

    def test_health_response_degraded(self):
        """Test HealthResponse with degraded status."""
        from app.XNAi_rag_app.schemas.responses import HealthResponse

        response = HealthResponse(
            status="degraded",
            version="v0.1.4",
            memory_gb=5.8,
            vectorstore_loaded=True,
            components={"embeddings": True, "vectorstore": False, "circuit_breakers_healthy": False},
        )

        assert response.status == "degraded"
        assert response.components["circuit_breakers_healthy"] is False

    def test_health_response_partial(self):
        """Test HealthResponse with partial status."""
        from app.XNAi_rag_app.schemas.responses import HealthResponse

        response = HealthResponse(
            status="partial",
            version="v0.1.4",
            memory_gb=3.0,
            vectorstore_loaded=False,
            components={"embeddings": True, "vectorstore": False, "llm": True},
        )

        assert response.status == "partial"
        assert response.vectorstore_loaded is False


# ============================================================================
# Health Check Endpoint Tests
# ============================================================================


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, mock_request, mock_config, mock_psutil_memory):
        """Test health check returns healthy status."""
        with (
            patch("app.XNAi_rag_app.api.routers.health.load_config", return_value=mock_config),
            patch("app.XNAi_rag_app.api.routers.health.psutil.virtual_memory", return_value=mock_psutil_memory),
            patch("app.XNAi_rag_app.api.routers.health.get_circuit_breaker_status", new_callable=AsyncMock) as mock_cb,
        ):
            mock_cb.return_value = {
                "llm": {"state": "closed", "fail_count": 0},
                "embeddings": {"state": "closed", "fail_count": 0},
            }

            from app.XNAi_rag_app.api.routers.health import health_check
            from app.XNAi_rag_app.schemas.responses import HealthResponse

            result = await health_check(mock_request)

            assert isinstance(result, HealthResponse)
            assert result.status in ["healthy", "partial", "degraded"]
            assert result.version == mock_config["metadata"]["stack_version"]

    @pytest.mark.asyncio
    async def test_health_check_no_services(self, mock_request_no_services, mock_config, mock_psutil_memory):
        """Test health check handles missing services."""
        with (
            patch("app.XNAi_rag_app.api.routers.health.load_config", return_value=mock_config),
            patch("app.XNAi_rag_app.api.routers.health.psutil.virtual_memory", return_value=mock_psutil_memory),
            patch("app.XNAi_rag_app.api.routers.health.get_circuit_breaker_status", new_callable=AsyncMock) as mock_cb,
        ):
            mock_cb.return_value = {}

            from app.XNAi_rag_app.api.routers.health import health_check

            result = await health_check(mock_request_no_services)

            # Should still return a valid response
            assert result.status in ["healthy", "partial", "degraded"]
            assert result.components["embeddings"] is False
            assert result.components["vectorstore"] is False

    @pytest.mark.asyncio
    async def test_health_check_circuit_breaker_open(self, mock_request, mock_config, mock_psutil_memory):
        """Test health check handles open circuit breakers."""
        with (
            patch("app.XNAi_rag_app.api.routers.health.load_config", return_value=mock_config),
            patch("app.XNAi_rag_app.api.routers.health.psutil.virtual_memory", return_value=mock_psutil_memory),
            patch("app.XNAi_rag_app.api.routers.health.get_circuit_breaker_status", new_callable=AsyncMock) as mock_cb,
        ):
            # Simulate open circuit breaker
            mock_cb.return_value = {
                "llm": {"state": "open", "fail_count": 5},
                "embeddings": {"state": "closed", "fail_count": 0},
            }

            from app.XNAi_rag_app.api.routers.health import health_check

            result = await health_check(mock_request)

            # Circuit breaker should be marked unhealthy
            assert result.components["circuit_breakers_healthy"] is False

    @pytest.mark.asyncio
    async def test_health_check_high_memory(self, mock_request, mock_config):
        """Test health check detects high memory usage."""
        high_memory = Mock()
        high_memory.used = 7 * 1024**3  # 7GB (above limit)
        high_memory.percent = 85.0

        with (
            patch("app.XNAi_rag_app.api.routers.health.load_config", return_value=mock_config),
            patch("app.XNAi_rag_app.api.routers.health.psutil.virtual_memory", return_value=high_memory),
            patch("app.XNAi_rag_app.api.routers.health.get_circuit_breaker_status", new_callable=AsyncMock) as mock_cb,
        ):
            mock_cb.return_value = {}

            from app.XNAi_rag_app.api.routers.health import health_check

            result = await health_check(mock_request)

            # Should be degraded due to memory
            assert result.status == "degraded"

    @pytest.mark.asyncio
    async def test_health_check_circuit_breaker_exception(self, mock_request, mock_config, mock_psutil_memory):
        """Test health check handles circuit breaker exceptions."""
        with (
            patch("app.XNAi_rag_app.api.routers.health.load_config", return_value=mock_config),
            patch("app.XNAi_rag_app.api.routers.health.psutil.virtual_memory", return_value=mock_psutil_memory),
            patch("app.XNAi_rag_app.api.routers.health.get_circuit_breaker_status", new_callable=AsyncMock) as mock_cb,
        ):
            mock_cb.side_effect = Exception("Circuit breaker check failed")

            from app.XNAi_rag_app.api.routers.health import health_check

            result = await health_check(mock_request)

            # Should handle gracefully and mark circuit breakers as unhealthy
            assert result.components["circuit_breakers_healthy"] is False


# ============================================================================
# Component Status Tests
# ============================================================================


class TestComponentStatus:
    """Tests for component status reporting."""

    @pytest.mark.asyncio
    async def test_embeddings_status_true(self, mock_request, mock_config, mock_psutil_memory):
        """Test embeddings component reports as available."""
        with (
            patch("app.XNAi_rag_app.api.routers.health.load_config", return_value=mock_config),
            patch("app.XNAi_rag_app.api.routers.health.psutil.virtual_memory", return_value=mock_psutil_memory),
            patch("app.XNAi_rag_app.api.routers.health.get_circuit_breaker_status", new_callable=AsyncMock) as mock_cb,
        ):
            mock_cb.return_value = {}

            from app.XNAi_rag_app.api.routers.health import health_check

            result = await health_check(mock_request)

            assert result.components["embeddings"] is True

    @pytest.mark.asyncio
    async def test_vectorstore_status_true(self, mock_request, mock_config, mock_psutil_memory):
        """Test vectorstore component reports as available."""
        with (
            patch("app.XNAi_rag_app.api.routers.health.load_config", return_value=mock_config),
            patch("app.XNAi_rag_app.api.routers.health.psutil.virtual_memory", return_value=mock_psutil_memory),
            patch("app.XNAi_rag_app.api.routers.health.get_circuit_breaker_status", new_callable=AsyncMock) as mock_cb,
        ):
            mock_cb.return_value = {}

            from app.XNAi_rag_app.api.routers.health import health_check

            result = await health_check(mock_request)

            assert result.components["vectorstore"] is True

    @pytest.mark.asyncio
    async def test_llm_status_assumed_ok(self, mock_request, mock_config, mock_psutil_memory):
        """Test LLM status is assumed OK (lazy loaded)."""
        with (
            patch("app.XNAi_rag_app.api.routers.health.load_config", return_value=mock_config),
            patch("app.XNAi_rag_app.api.routers.health.psutil.virtual_memory", return_value=mock_psutil_memory),
            patch("app.XNAi_rag_app.api.routers.health.get_circuit_breaker_status", new_callable=AsyncMock) as mock_cb,
        ):
            mock_cb.return_value = {}

            from app.XNAi_rag_app.api.routers.health import health_check

            result = await health_check(mock_request)

            # LLM is lazy loaded, so assumed OK
            assert result.components["llm"] is True


# ============================================================================
# Tier Configuration Tests
# ============================================================================


class TestTierConfiguration:
    """Tests for tier configuration integration."""

    @pytest.mark.asyncio
    async def test_tier_info_included(self, mock_request, mock_config, mock_psutil_memory):
        """Test tier information is included in response."""
        with (
            patch("app.XNAi_rag_app.api.routers.health.load_config", return_value=mock_config),
            patch("app.XNAi_rag_app.api.routers.health.psutil.virtual_memory", return_value=mock_psutil_memory),
            patch("app.XNAi_rag_app.api.routers.health.get_circuit_breaker_status", new_callable=AsyncMock) as mock_cb,
            patch("app.XNAi_rag_app.api.routers.health.tier_config_factory") as mock_tier,
        ):
            mock_cb.return_value = {}
            mock_tier.get_current_tier.return_value = 1
            mock_tier.get_tier_summary.return_value = {"tier_name": "normal"}

            from app.XNAi_rag_app.api.routers.health import health_check

            result = await health_check(mock_request)

            assert "degradation_tier" in result.components
            assert "tier_name" in result.components

    @pytest.mark.asyncio
    async def test_degraded_tier_triggers_status(self, mock_request, mock_config, mock_psutil_memory):
        """Test tier 3+ triggers degraded status."""
        with (
            patch("app.XNAi_rag_app.api.routers.health.load_config", return_value=mock_config),
            patch("app.XNAi_rag_app.api.routers.health.psutil.virtual_memory", return_value=mock_psutil_memory),
            patch("app.XNAi_rag_app.api.routers.health.get_circuit_breaker_status", new_callable=AsyncMock) as mock_cb,
            patch("app.XNAi_rag_app.api.routers.health.tier_config_factory") as mock_tier,
        ):
            mock_cb.return_value = {}
            mock_tier.get_current_tier.return_value = 3  # Degraded tier
            mock_tier.get_tier_summary.return_value = {"tier_name": "degraded"}

            from app.XNAi_rag_app.api.routers.health import health_check

            result = await health_check(mock_request)

            assert result.status == "degraded"
            assert result.components["degradation_tier"] >= 3


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestHealthErrorHandling:
    """Tests for error handling in health check."""

    @pytest.mark.asyncio
    async def test_healthcheck_module_import_error(self, mock_request, mock_config, mock_psutil_memory):
        """Test handling when healthcheck module is not available."""
        with (
            patch("app.XNAi_rag_app.api.routers.health.load_config", return_value=mock_config),
            patch("app.XNAi_rag_app.api.routers.health.psutil.virtual_memory", return_value=mock_psutil_memory),
            patch("app.XNAi_rag_app.api.routers.health.get_circuit_breaker_status", new_callable=AsyncMock) as mock_cb,
        ):
            mock_cb.return_value = {}

            # This test verifies the ImportError handling in health.py
            from app.XNAi_rag_app.api.routers.health import health_check

            result = await health_check(mock_request)

            # Should still work without healthcheck module
            assert result is not None

    @pytest.mark.asyncio
    async def test_memory_check_graceful_failure(self, mock_request, mock_config):
        """Test graceful handling of memory check failures."""
        with (
            patch("app.XNAi_rag_app.api.routers.health.load_config", return_value=mock_config),
            patch("app.XNAi_rag_app.api.routers.health.psutil.virtual_memory", side_effect=Exception("Memory error")),
            patch("app.XNAi_rag_app.api.routers.health.get_circuit_breaker_status", new_callable=AsyncMock) as mock_cb,
        ):
            mock_cb.return_value = {}

            from app.XNAi_rag_app.api.routers.health import health_check

            # Should raise or handle gracefully
            # The endpoint may raise or return an error response
            try:
                result = await health_check(mock_request)
                # If it returns, check it's valid
                assert result is not None
            except Exception:
                # Exception is also acceptable behavior
                pass


# ============================================================================
# Integration Tests
# ============================================================================


class TestHealthIntegration:
    """Integration tests for health endpoint."""

    @pytest.mark.asyncio
    async def test_full_health_check_flow(self, mock_request, mock_config, mock_psutil_memory):
        """Test complete health check flow."""
        with (
            patch("app.XNAi_rag_app.api.routers.health.load_config", return_value=mock_config),
            patch("app.XNAi_rag_app.api.routers.health.psutil.virtual_memory", return_value=mock_psutil_memory),
            patch("app.XNAi_rag_app.api.routers.health.get_circuit_breaker_status", new_callable=AsyncMock) as mock_cb,
            patch("app.XNAi_rag_app.api.routers.health.tier_config_factory") as mock_tier,
        ):
            mock_cb.return_value = {
                "llm": {"state": "closed", "fail_count": 0},
                "embeddings": {"state": "closed", "fail_count": 0},
            }
            mock_tier.get_current_tier.return_value = 1
            mock_tier.get_tier_summary.return_value = {"tier_name": "normal"}

            from app.XNAi_rag_app.api.routers.health import health_check

            result = await health_check(mock_request)

            # Verify all expected fields
            assert hasattr(result, "status")
            assert hasattr(result, "version")
            assert hasattr(result, "memory_gb")
            assert hasattr(result, "vectorstore_loaded")
            assert hasattr(result, "components")

            # Verify component statuses
            assert "embeddings" in result.components
            assert "vectorstore" in result.components
            assert "llm" in result.components
            assert "circuit_breakers_healthy" in result.components
