"""
Unit tests for query endpoints.

Tests cover:
- QueryRequest schema validation
- Query endpoint behavior
- Streaming endpoint behavior
- RAG integration
- Metrics recording
- Circuit breaker handling
- Transaction logging

Task: W3-001-2
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from fastapi import Request, HTTPException
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
def mock_rag_service():
    """Mock RAG service."""
    mock = Mock()
    mock.retrieve_context = AsyncMock(return_value=("Test context content", ["source1.txt", "source2.txt"]))
    mock.generate_prompt = Mock(return_value="Test prompt with context")
    return mock


@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    mock = Mock()
    mock.invoke = Mock(return_value="This is a test response from the LLM.")
    mock.stream = Mock(return_value=iter(["This ", "is ", "a ", "test ", "response."]))
    return mock


@pytest.fixture
def query_request_data():
    """Sample query request data."""
    return {"query": "What is Xoe-NovAi?", "use_rag": True, "max_tokens": 512, "temperature": 0.7, "top_p": 0.95}


# ============================================================================
# QueryRequest Tests
# ============================================================================


class TestQueryRequestSchema:
    """Tests for QueryRequest Pydantic model."""

    def test_query_request_valid(self):
        """Test valid QueryRequest creation."""
        from app.XNAi_rag_app.schemas.requests import QueryRequest

        request = QueryRequest(query="Test query", use_rag=True, max_tokens=512, temperature=0.7, top_p=0.95)

        assert request.query == "Test query"
        assert request.use_rag is True
        assert request.max_tokens == 512
        assert request.temperature == 0.7
        assert request.top_p == 0.95

    def test_query_request_minimal(self):
        """Test QueryRequest with minimal required fields."""
        from app.XNAi_rag_app.schemas.requests import QueryRequest

        request = QueryRequest(query="Test")

        assert request.query == "Test"
        assert request.use_rag is True  # Default
        assert request.max_tokens == 512  # Default
        assert request.temperature == 0.7  # Default

    def test_query_request_validation_query_length(self):
        """Test query length validation."""
        from app.XNAi_rag_app.schemas.requests import QueryRequest
        from pydantic import ValidationError

        # Too short
        with pytest.raises(ValidationError):
            QueryRequest(query="")

        # Too long
        long_query = "a" * 2001
        with pytest.raises(ValidationError):
            QueryRequest(query=long_query)

    def test_query_request_validation_max_tokens(self):
        """Test max_tokens validation."""
        from app.XNAi_rag_app.schemas.requests import QueryRequest
        from pydantic import ValidationError

        # Too low
        with pytest.raises(ValidationError):
            QueryRequest(query="Test", max_tokens=0)

        # Too high
        with pytest.raises(ValidationError):
            QueryRequest(query="Test", max_tokens=3000)

    def test_query_request_validation_temperature(self):
        """Test temperature validation."""
        from app.XNAi_rag_app.schemas.requests import QueryRequest
        from pydantic import ValidationError

        # Below range
        with pytest.raises(ValidationError):
            QueryRequest(query="Test", temperature=-0.5)

        # Above range
        with pytest.raises(ValidationError):
            QueryRequest(query="Test", temperature=3.0)


# ============================================================================
# QueryResponse Tests
# ============================================================================


class TestQueryResponseSchema:
    """Tests for QueryResponse Pydantic model."""

    def test_query_response_valid(self):
        """Test valid QueryResponse creation."""
        from app.XNAi_rag_app.schemas.responses import QueryResponse

        response = QueryResponse(
            response="This is the answer.",
            sources=["doc1.txt", "doc2.txt"],
            tokens_generated=50,
            duration_ms=150.5,
            token_rate_tps=33.3,
        )

        assert response.response == "This is the answer."
        assert len(response.sources) == 2
        assert response.tokens_generated == 50
        assert response.duration_ms == 150.5
        assert response.token_rate_tps == 33.3

    def test_query_response_minimal(self):
        """Test QueryResponse with minimal fields."""
        from app.XNAi_rag_app.schemas.responses import QueryResponse

        response = QueryResponse(response="Answer")

        assert response.response == "Answer"
        assert response.sources == []  # Default empty list


# ============================================================================
# Query Endpoint Tests
# ============================================================================


class TestQueryEndpoint:
    """Tests for /query endpoint."""

    @pytest.mark.asyncio
    async def test_query_endpoint_basic(self, mock_request, mock_rag_service, mock_llm, query_request_data):
        """Test basic query endpoint functionality."""
        from app.XNAi_rag_app.schemas.requests import QueryRequest

        query_req = QueryRequest(**query_request_data)

        with (
            patch("app.XNAi_rag_app.api.routers.query.get_current_rag_config") as mock_rag_config,
            patch("app.XNAi_rag_app.api.routers.query.get_current_llm_config") as mock_llm_config,
            patch("app.XNAi_rag_app.api.routers.query.tier_config_factory") as mock_tier,
            patch("app.XNAi_rag_app.api.routers.query.transaction_logger") as mock_tx_logger,
        ):
            # Setup mock configs
            mock_rag_cfg = Mock()
            mock_rag_cfg.retrieval_enabled = True
            mock_rag_cfg.top_k = 5
            mock_rag_cfg.max_context_chars = 2048
            mock_rag_config.return_value = mock_rag_cfg

            mock_llm_cfg = Mock()
            mock_llm_cfg.max_tokens = 1024
            mock_llm_cfg.temperature = 0.7
            mock_llm_cfg.top_p = 0.95
            mock_llm_config.return_value = mock_llm_cfg

            mock_tier.get_current_tier.return_value = 1
            mock_tx_logger.log_transaction = AsyncMock()

            # Setup entrypoint mock
            mock_ep = Mock()
            mock_ep.llm = mock_llm

            with patch.dict("sys.modules", {"app.XNAi_rag_app.api.entrypoint": mock_ep}):
                # Set services
                mock_request.app.state.services = {"rag": mock_rag_service, "vectorstore": Mock(), "embeddings": Mock()}

                from app.XNAi_rag_app.api.routers.query import query_endpoint
                from app.XNAi_rag_app.schemas.responses import QueryResponse

                # Need to patch MetricsTimer context manager
                with patch("app.XNAi_rag_app.api.routers.query.MetricsTimer") as mock_timer:
                    mock_timer.return_value.__enter__ = Mock(return_value=None)
                    mock_timer.return_value.__exit__ = Mock(return_value=None)

                    result = await query_endpoint(mock_request, query_req)

                    assert isinstance(result, QueryResponse)
                    assert result.response is not None

    @pytest.mark.asyncio
    async def test_query_endpoint_without_rag(self, mock_request, mock_llm):
        """Test query endpoint without RAG retrieval."""
        from app.XNAi_rag_app.schemas.requests import QueryRequest

        query_req = QueryRequest(query="Test query", use_rag=False)

        with (
            patch("app.XNAi_rag_app.api.routers.query.get_current_rag_config") as mock_rag_config,
            patch("app.XNAi_rag_app.api.routers.query.get_current_llm_config") as mock_llm_config,
            patch("app.XNAi_rag_app.api.routers.query.tier_config_factory") as mock_tier,
            patch("app.XNAi_rag_app.api.routers.query.transaction_logger") as mock_tx_logger,
        ):
            mock_rag_cfg = Mock()
            mock_rag_cfg.retrieval_enabled = True
            mock_rag_config.return_value = mock_rag_cfg

            mock_llm_cfg = Mock()
            mock_llm_cfg.max_tokens = 1024
            mock_llm_cfg.temperature = 0.7
            mock_llm_cfg.top_p = 0.95
            mock_llm_config.return_value = mock_llm_cfg

            mock_tier.get_current_tier.return_value = 1
            mock_tx_logger.log_transaction = AsyncMock()

            mock_ep = Mock()
            mock_ep.llm = mock_llm

            mock_request.app.state.services = {"rag": Mock(), "vectorstore": None, "embeddings": Mock()}

            from app.XNAi_rag_app.api.routers.query import query_endpoint

            with patch("app.XNAi_rag_app.api.routers.query.MetricsTimer") as mock_timer:
                mock_timer.return_value.__enter__ = Mock(return_value=None)
                mock_timer.return_value.__exit__ = Mock(return_value=None)

                result = await query_endpoint(mock_request, query_req)

                # Should still return a valid response
                assert result.response is not None
                # Sources should be empty (no RAG)
                assert result.sources == []

    @pytest.mark.asyncio
    async def test_query_endpoint_circuit_breaker_open(self, mock_request, query_request_data):
        """Test query endpoint handles open circuit breaker."""
        from app.XNAi_rag_app.schemas.requests import QueryRequest
        from app.XNAi_rag_app.core.circuit_breakers import CircuitBreakerError

        query_req = QueryRequest(**query_request_data)

        with (
            patch("app.XNAi_rag_app.api.routers.query.get_current_rag_config") as mock_rag_config,
            patch("app.XNAi_rag_app.api.routers.query.get_current_llm_config") as mock_llm_config,
            patch("app.XNAi_rag_app.api.routers.query.tier_config_factory") as mock_tier,
            patch("app.XNAi_rag_app.api.routers.query.record_error") as mock_record_error,
        ):
            mock_rag_cfg = Mock()
            mock_rag_cfg.retrieval_enabled = False
            mock_rag_config.return_value = mock_rag_cfg

            mock_llm_cfg = Mock()
            mock_llm_cfg.max_tokens = 1024
            mock_llm_cfg.temperature = 0.7
            mock_llm_cfg.top_p = 0.95
            mock_llm_config.return_value = mock_llm_cfg

            mock_tier.get_current_tier.return_value = 1

            # Mock LLM that raises CircuitBreakerError
            mock_llm = Mock()
            mock_llm.invoke.side_effect = CircuitBreakerError("Circuit open")

            mock_ep = Mock()
            mock_ep.llm = mock_llm

            mock_request.app.state.services = {"rag": Mock(), "vectorstore": None, "embeddings": Mock()}

            from app.XNAi_rag_app.api.routers.query import query_endpoint
            from fastapi.responses import JSONResponse

            with patch("app.XNAi_rag_app.api.routers.query.MetricsTimer") as mock_timer:
                mock_timer.return_value.__enter__ = Mock(return_value=None)
                mock_timer.return_value.__exit__ = Mock(return_value=None)

                result = await query_endpoint(mock_request, query_req)

                # Should return 503 JSONResponse
                assert isinstance(result, JSONResponse)
                assert result.status_code == 503


# ============================================================================
# Stream Endpoint Tests
# ============================================================================


class TestStreamEndpoint:
    """Tests for /stream endpoint."""

    @pytest.mark.asyncio
    async def test_stream_endpoint_basic(self, mock_request, mock_rag_service, mock_llm):
        """Test basic streaming endpoint functionality."""
        from app.XNAi_rag_app.schemas.requests import QueryRequest

        query_req = QueryRequest(query="Test streaming")

        with (
            patch("app.XNAi_rag_app.api.routers.query.get_current_rag_config") as mock_rag_config,
            patch("app.XNAi_rag_app.api.routers.query.get_current_llm_config") as mock_llm_config,
            patch("app.XNAi_rag_app.api.routers.query.tier_config_factory") as mock_tier,
            patch("app.XNAi_rag_app.api.routers.query.transaction_logger") as mock_tx_logger,
        ):
            mock_rag_cfg = Mock()
            mock_rag_cfg.retrieval_enabled = True
            mock_rag_cfg.top_k = 5
            mock_rag_cfg.max_context_chars = 2048
            mock_rag_config.return_value = mock_rag_cfg

            mock_llm_cfg = Mock()
            mock_llm_cfg.max_tokens = 1024
            mock_llm_cfg.temperature = 0.7
            mock_llm_cfg.top_p = 0.95
            mock_llm_config.return_value = mock_llm_cfg

            mock_tier.get_current_tier.return_value = 1
            mock_tx_logger.log_transaction = AsyncMock()

            mock_ep = Mock()
            mock_ep.llm = mock_llm

            mock_request.app.state.services = {"rag": mock_rag_service, "vectorstore": Mock(), "embeddings": Mock()}

            from app.XNAi_rag_app.api.routers.query import stream_endpoint
            from fastapi.responses import StreamingResponse

            result = await stream_endpoint(mock_request, query_req)

            assert isinstance(result, StreamingResponse)
            assert result.media_type == "text/event-stream"

    @pytest.mark.asyncio
    async def test_stream_endpoint_generates_events(self, mock_request, mock_rag_service, mock_llm):
        """Test streaming endpoint generates SSE events."""
        from app.XNAi_rag_app.schemas.requests import QueryRequest
        import asyncio

        query_req = QueryRequest(query="Test", use_rag=False)

        with (
            patch("app.XNAi_rag_app.api.routers.query.get_current_rag_config") as mock_rag_config,
            patch("app.XNAi_rag_app.api.routers.query.get_current_llm_config") as mock_llm_config,
            patch("app.XNAi_rag_app.api.routers.query.tier_config_factory") as mock_tier,
            patch("app.XNAi_rag_app.api.routers.query.transaction_logger") as mock_tx_logger,
        ):
            mock_rag_cfg = Mock()
            mock_rag_cfg.retrieval_enabled = False
            mock_rag_config.return_value = mock_rag_cfg

            mock_llm_cfg = Mock()
            mock_llm_cfg.max_tokens = 1024
            mock_llm_cfg.temperature = 0.7
            mock_llm_cfg.top_p = 0.95
            mock_llm_config.return_value = mock_llm_cfg

            mock_tier.get_current_tier.return_value = 1
            mock_tx_logger.log_transaction = AsyncMock()

            mock_ep = Mock()
            mock_ep.llm = mock_llm

            mock_request.app.state.services = {"rag": mock_rag_service, "vectorstore": None, "embeddings": Mock()}

            from app.XNAi_rag_app.api.routers.query import stream_endpoint

            result = await stream_endpoint(mock_request, query_req)

            # Get the generator
            generator = result.body_iterator

            # Collect first few events
            events = []
            async for event in generator:
                events.append(event)
                if len(events) >= 3:
                    break

            # Should have generated events
            assert len(events) > 0


# ============================================================================
# Metrics Tests
# ============================================================================


class TestQueryMetrics:
    """Tests for metrics recording in query endpoints."""

    @pytest.mark.asyncio
    async def test_metrics_recorded(self, mock_request, mock_rag_service, mock_llm, query_request_data):
        """Test that metrics are recorded during query."""
        from app.XNAi_rag_app.schemas.requests import QueryRequest

        query_req = QueryRequest(**query_request_data)

        with (
            patch("app.XNAi_rag_app.api.routers.query.get_current_rag_config") as mock_rag_config,
            patch("app.XNAi_rag_app.api.routers.query.get_current_llm_config") as mock_llm_config,
            patch("app.XNAi_rag_app.api.routers.query.tier_config_factory") as mock_tier,
            patch("app.XNAi_rag_app.api.routers.query.transaction_logger") as mock_tx_logger,
            patch("app.XNAi_rag_app.api.routers.query.record_tokens_generated") as mock_tokens,
            patch("app.XNAi_rag_app.api.routers.query.record_query_processed") as mock_query,
            patch("app.XNAi_rag_app.api.routers.query.update_token_rate") as mock_rate,
        ):
            mock_rag_cfg = Mock()
            mock_rag_cfg.retrieval_enabled = False
            mock_rag_config.return_value = mock_rag_cfg

            mock_llm_cfg = Mock()
            mock_llm_cfg.max_tokens = 1024
            mock_llm_cfg.temperature = 0.7
            mock_llm_cfg.top_p = 0.95
            mock_llm_config.return_value = mock_llm_cfg

            mock_tier.get_current_tier.return_value = 1
            mock_tx_logger.log_transaction = AsyncMock()

            mock_ep = Mock()
            mock_ep.llm = mock_llm

            mock_request.app.state.services = {"rag": mock_rag_service, "vectorstore": None, "embeddings": Mock()}

            from app.XNAi_rag_app.api.routers.query import query_endpoint

            with patch("app.XNAi_rag_app.api.routers.query.MetricsTimer") as mock_timer:
                mock_timer.return_value.__enter__ = Mock(return_value=None)
                mock_timer.return_value.__exit__ = Mock(return_value=None)

                await query_endpoint(mock_request, query_req)

                # Verify metrics were called
                mock_tokens.assert_called_once()
                mock_query.assert_called_once()


# ============================================================================
# Transaction Logging Tests
# ============================================================================


class TestTransactionLogging:
    """Tests for transaction logging in query endpoints."""

    @pytest.mark.asyncio
    async def test_transaction_logged(self, mock_request, mock_rag_service, mock_llm, query_request_data):
        """Test that transactions are logged during query."""
        from app.XNAi_rag_app.schemas.requests import QueryRequest

        query_req = QueryRequest(**query_request_data)

        with (
            patch("app.XNAi_rag_app.api.routers.query.get_current_rag_config") as mock_rag_config,
            patch("app.XNAi_rag_app.api.routers.query.get_current_llm_config") as mock_llm_config,
            patch("app.XNAi_rag_app.api.routers.query.tier_config_factory") as mock_tier,
            patch("app.XNAi_rag_app.api.routers.query.transaction_logger") as mock_tx_logger,
        ):
            mock_rag_cfg = Mock()
            mock_rag_cfg.retrieval_enabled = False
            mock_rag_config.return_value = mock_rag_cfg

            mock_llm_cfg = Mock()
            mock_llm_cfg.max_tokens = 1024
            mock_llm_cfg.temperature = 0.7
            mock_llm_cfg.top_p = 0.95
            mock_llm_config.return_value = mock_llm_cfg

            mock_tier.get_current_tier.return_value = 1
            mock_tx_logger.log_transaction = AsyncMock()

            mock_ep = Mock()
            mock_ep.llm = mock_llm

            mock_request.app.state.services = {"rag": mock_rag_service, "vectorstore": None, "embeddings": Mock()}

            from app.XNAi_rag_app.api.routers.query import query_endpoint

            with patch("app.XNAi_rag_app.api.routers.query.MetricsTimer") as mock_timer:
                mock_timer.return_value.__enter__ = Mock(return_value=None)
                mock_timer.return_value.__exit__ = Mock(return_value=None)

                await query_endpoint(mock_request, query_req)

                # Verify transaction was logged
                mock_tx_logger.log_transaction.assert_called_once()
                call_args = mock_tx_logger.log_transaction.call_args
                assert call_args.kwargs["transaction_type"] == "query"


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestQueryErrorHandling:
    """Tests for error handling in query endpoints."""

    @pytest.mark.asyncio
    async def test_general_exception_handling(self, mock_request, query_request_data):
        """Test handling of general exceptions."""
        from app.XNAi_rag_app.schemas.requests import QueryRequest
        from fastapi import HTTPException

        query_req = QueryRequest(**query_request_data)

        with (
            patch("app.XNAi_rag_app.api.routers.query.get_current_rag_config") as mock_rag_config,
            patch("app.XNAi_rag_app.api.routers.query.get_current_llm_config") as mock_llm_config,
            patch("app.XNAi_rag_app.api.routers.query.tier_config_factory") as mock_tier,
        ):
            mock_rag_cfg = Mock()
            mock_rag_cfg.retrieval_enabled = False
            mock_rag_config.return_value = mock_rag_cfg

            mock_llm_cfg = Mock()
            mock_llm_cfg.max_tokens = 1024
            mock_llm_cfg.temperature = 0.7
            mock_llm_cfg.top_p = 0.95
            mock_llm_config.return_value = mock_llm_cfg

            mock_tier.get_current_tier.return_value = 1

            # Mock LLM that raises general exception
            mock_llm = Mock()
            mock_llm.invoke.side_effect = RuntimeError("LLM error")

            mock_ep = Mock()
            mock_ep.llm = mock_llm

            mock_request.app.state.services = {"rag": Mock(), "vectorstore": None, "embeddings": Mock()}

            from app.XNAi_rag_app.api.routers.query import query_endpoint

            with patch("app.XNAi_rag_app.api.routers.query.MetricsTimer") as mock_timer:
                mock_timer.return_value.__enter__ = Mock(return_value=None)
                mock_timer.return_value.__exit__ = Mock(return_value=None)

                # Should raise HTTPException
                with pytest.raises(HTTPException) as exc_info:
                    await query_endpoint(mock_request, query_req)

                assert exc_info.value.status_code == 500


# ============================================================================
# Tier Configuration Tests
# ============================================================================


class TestQueryTierConfiguration:
    """Tests for tier configuration in query endpoints."""

    @pytest.mark.asyncio
    async def test_tier_applies_max_tokens_limit(self, mock_request, mock_rag_service, mock_llm):
        """Test that tier configuration limits max tokens."""
        from app.XNAi_rag_app.schemas.requests import QueryRequest

        # Request more tokens than tier allows
        query_req = QueryRequest(
            query="Test",
            max_tokens=2000,  # Higher than tier limit
        )

        with (
            patch("app.XNAi_rag_app.api.routers.query.get_current_rag_config") as mock_rag_config,
            patch("app.XNAi_rag_app.api.routers.query.get_current_llm_config") as mock_llm_config,
            patch("app.XNAi_rag_app.api.routers.query.tier_config_factory") as mock_tier,
            patch("app.XNAi_rag_app.api.routers.query.transaction_logger") as mock_tx_logger,
        ):
            mock_rag_cfg = Mock()
            mock_rag_cfg.retrieval_enabled = False
            mock_rag_config.return_value = mock_rag_cfg

            # Tier limits max_tokens to 512
            mock_llm_cfg = Mock()
            mock_llm_cfg.max_tokens = 512
            mock_llm_cfg.temperature = 0.7
            mock_llm_cfg.top_p = 0.95
            mock_llm_config.return_value = mock_llm_cfg

            mock_tier.get_current_tier.return_value = 2
            mock_tx_logger.log_transaction = AsyncMock()

            mock_ep = Mock()
            mock_ep.llm = mock_llm

            mock_request.app.state.services = {"rag": mock_rag_service, "vectorstore": None, "embeddings": Mock()}

            from app.XNAi_rag_app.api.routers.query import query_endpoint

            with patch("app.XNAi_rag_app.api.routers.query.MetricsTimer") as mock_timer:
                mock_timer.return_value.__enter__ = Mock(return_value=None)
                mock_timer.return_value.__exit__ = Mock(return_value=None)

                await query_endpoint(mock_request, query_req)

                # Verify effective max_tokens was limited
                invoke_call = mock_llm.invoke.call_args
                effective_max = invoke_call.kwargs["max_tokens"]
                assert effective_max <= 512  # Tier limit applied
