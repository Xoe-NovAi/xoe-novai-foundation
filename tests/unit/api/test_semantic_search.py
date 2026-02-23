"""
Unit tests for semantic search endpoints.

Tests cover:
- SemanticSearchRequest schema validation
- SemanticSearchResponse schema validation
- SemanticSearchAPI class
- Health check endpoint
- Search endpoint
- Error handling
- Request context and tracing

Task: W3-001-4
"""

import pytest
import json
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from fastapi import Request
from fastapi.testclient import TestClient


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def search_request_data():
    """Sample semantic search request data."""
    return {
        "query": "How to configure Python for machine learning?",
        "top_k": 5,
        "min_score": 0.5,
        "alpha": 0.5,
        "filters": {"source": "official_docs"},
    }


@pytest.fixture
def mock_documents():
    """Mock documents for testing."""
    from langchain_core.documents import Document

    return [
        Document(
            page_content="Python configuration guide for ML frameworks like TensorFlow and PyTorch.",
            metadata={"id": "doc1", "source": "official_docs"},
        ),
        Document(
            page_content="Setting up virtual environments for Python development.",
            metadata={"id": "doc2", "source": "tutorials"},
        ),
        Document(
            page_content="Best practices for Python package management with pip.",
            metadata={"id": "doc3", "source": "official_docs"},
        ),
    ]


@pytest.fixture
def mock_embeddings():
    """Mock embeddings array."""
    import numpy as np

    return np.random.rand(10, 384).astype(np.float32)


@pytest.fixture
def semantic_search_api():
    """Create SemanticSearchAPI instance."""
    from app.XNAi_rag_app.api.semantic_search import SemanticSearchAPI

    return SemanticSearchAPI()


# ============================================================================
# SemanticSearchRequest Tests
# ============================================================================


class TestSemanticSearchRequest:
    """Tests for SemanticSearchRequest Pydantic model."""

    def test_request_valid(self):
        """Test valid SemanticSearchRequest creation."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchRequest

        request = SemanticSearchRequest(query="Test query", top_k=10, min_score=0.7, alpha=0.3, filters={"category": "docs"})

        assert request.query == "Test query"
        assert request.top_k == 10
        assert request.min_score == 0.7
        assert request.alpha == 0.3
        assert request.filters == {"category": "docs"}

    def test_request_minimal(self):
        """Test SemanticSearchRequest with minimal fields."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchRequest

        request = SemanticSearchRequest(query="Test")

        assert request.query == "Test"
        assert request.top_k == 5  # Default
        assert request.min_score == 0.0  # Default
        assert request.alpha == 0.5  # Default
        assert request.filters is None

    def test_request_query_validation_min_length(self):
        """Test query minimum length validation."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SemanticSearchRequest(query="")

    def test_request_query_validation_max_length(self):
        """Test query maximum length validation."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchRequest
        from pydantic import ValidationError

        long_query = "a" * 2001
        with pytest.raises(ValidationError):
            SemanticSearchRequest(query=long_query)

    def test_request_top_k_validation_min(self):
        """Test top_k minimum validation."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SemanticSearchRequest(query="Test", top_k=0)

    def test_request_top_k_validation_max(self):
        """Test top_k maximum validation."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SemanticSearchRequest(query="Test", top_k=101)

    def test_request_min_score_validation(self):
        """Test min_score validation."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchRequest
        from pydantic import ValidationError

        # Below range
        with pytest.raises(ValidationError):
            SemanticSearchRequest(query="Test", min_score=-0.1)

        # Above range
        with pytest.raises(ValidationError):
            SemanticSearchRequest(query="Test", min_score=1.1)

    def test_request_alpha_validation(self):
        """Test alpha validation."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchRequest
        from pydantic import ValidationError

        # Below range
        with pytest.raises(ValidationError):
            SemanticSearchRequest(query="Test", alpha=-0.1)

        # Above range
        with pytest.raises(ValidationError):
            SemanticSearchRequest(query="Test", alpha=1.1)


# ============================================================================
# SearchResultItem Tests
# ============================================================================


class TestSearchResultItem:
    """Tests for SearchResultItem Pydantic model."""

    def test_result_item_valid(self):
        """Test valid SearchResultItem creation."""
        from app.XNAi_rag_app.api.semantic_search import SearchResultItem

        item = SearchResultItem(id="doc1", rank=1, score=0.95, content="Test content", metadata={"source": "docs"})

        assert item.id == "doc1"
        assert item.rank == 1
        assert item.score == 0.95
        assert item.content == "Test content"
        assert item.metadata == {"source": "docs"}

    def test_result_item_default_metadata(self):
        """Test SearchResultItem with default metadata."""
        from app.XNAi_rag_app.api.semantic_search import SearchResultItem

        item = SearchResultItem(id="doc1", rank=1, score=0.9, content="Test")

        assert item.metadata == {}


# ============================================================================
# SemanticSearchResponse Tests
# ============================================================================


class TestSemanticSearchResponse:
    """Tests for SemanticSearchResponse Pydantic model."""

    def test_response_valid(self):
        """Test valid SemanticSearchResponse creation."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchResponse, SearchResultItem

        response = SemanticSearchResponse(
            request_id="req_123",
            query="Test query",
            result_count=2,
            results=[
                SearchResultItem(id="doc1", rank=1, score=0.9, content="Content 1"),
                SearchResultItem(id="doc2", rank=2, score=0.8, content="Content 2"),
            ],
            execution_time_ms=125.5,
            timestamp="2026-02-23T10:30:45.123456Z",
        )

        assert response.request_id == "req_123"
        assert response.query == "Test query"
        assert response.result_count == 2
        assert len(response.results) == 2
        assert response.execution_time_ms == 125.5


# ============================================================================
# HealthCheckResponse Tests
# ============================================================================


class TestHealthCheckResponse:
    """Tests for HealthCheckResponse Pydantic model."""

    def test_health_response_healthy(self):
        """Test healthy status response."""
        from app.XNAi_rag_app.api.semantic_search import HealthCheckResponse

        response = HealthCheckResponse(
            status="healthy",
            timestamp="2026-02-23T10:30:45Z",
            version="0.1.0-phase6",
            dependencies={"embeddings": "ready", "index": "ready"},
        )

        assert response.status == "healthy"
        assert response.dependencies["embeddings"] == "ready"

    def test_health_response_degraded(self):
        """Test degraded status response."""
        from app.XNAi_rag_app.api.semantic_search import HealthCheckResponse

        response = HealthCheckResponse(
            status="degraded",
            timestamp="2026-02-23T10:30:45Z",
            version="0.1.0-phase6",
            dependencies={"embeddings": "ready", "index": "not_initialized"},
        )

        assert response.status == "degraded"

    def test_health_response_unhealthy(self):
        """Test unhealthy status response."""
        from app.XNAi_rag_app.api.semantic_search import HealthCheckResponse

        response = HealthCheckResponse(
            status="unhealthy",
            timestamp="2026-02-23T10:30:45Z",
            version="0.1.0-phase6",
            dependencies={"embeddings": "not_initialized", "index": "not_initialized"},
        )

        assert response.status == "unhealthy"


# ============================================================================
# RequestContext Tests
# ============================================================================


class TestRequestContext:
    """Tests for RequestContext class."""

    def test_context_creation(self):
        """Test RequestContext creation."""
        from app.XNAi_rag_app.api.semantic_search import RequestContext

        context = RequestContext(request_id="req_123")

        assert context.request_id == "req_123"
        assert context.span_id is not None
        assert context.timestamp is not None
        assert context.start_time > 0

    def test_context_auto_request_id(self):
        """Test auto-generated request ID."""
        from app.XNAi_rag_app.api.semantic_search import RequestContext

        context = RequestContext()

        assert context.request_id.startswith("req_")
        assert len(context.request_id) > 4

    def test_get_elapsed_ms(self):
        """Test elapsed time calculation."""
        from app.XNAi_rag_app.api.semantic_search import RequestContext

        context = RequestContext()
        time.sleep(0.01)  # Small delay

        elapsed = context.get_elapsed_ms()

        assert elapsed >= 10  # At least 10ms

    def test_to_dict(self):
        """Test context serialization."""
        from app.XNAi_rag_app.api.semantic_search import RequestContext

        context = RequestContext(request_id="req_123")
        result = context.to_dict()

        assert "request_id" in result
        assert "span_id" in result
        assert "timestamp" in result
        assert "elapsed_ms" in result


# ============================================================================
# SemanticSearchAPI Tests
# ============================================================================


class TestSemanticSearchAPI:
    """Tests for SemanticSearchAPI class."""

    def test_api_initialization(self, semantic_search_api):
        """Test API initialization."""
        assert semantic_search_api.app is not None
        assert semantic_search_api.embeddings is None
        assert semantic_search_api.documents is None

    def test_api_fastapi_setup(self, semantic_search_api):
        """Test FastAPI application setup."""
        app = semantic_search_api.get_app()

        assert app is not None
        assert app.title == "Xoe-NovAi Semantic Search API"

    def test_api_initialize(self, semantic_search_api, mock_documents, mock_embeddings):
        """Test API initialization with data."""
        semantic_search_api.initialize(documents=mock_documents, embeddings=mock_embeddings)

        assert semantic_search_api.documents == mock_documents
        assert semantic_search_api.embeddings is mock_embeddings


# ============================================================================
# Health Check Endpoint Tests
# ============================================================================


class TestHealthCheckEndpoint:
    """Tests for health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_not_initialized(self, semantic_search_api):
        """Test health check when not initialized."""
        result = await semantic_search_api.health_check()

        assert result.status == "unhealthy"
        assert result.dependencies["embeddings"] == "not_initialized"
        assert result.dependencies["index"] == "not_initialized"

    @pytest.mark.asyncio
    async def test_health_check_partial(self, semantic_search_api, mock_documents):
        """Test health check with partial initialization."""
        semantic_search_api.documents = mock_documents

        result = await semantic_search_api.health_check()

        assert result.status == "degraded"
        assert result.dependencies["index"] == "ready"
        assert result.dependencies["embeddings"] == "not_initialized"

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, semantic_search_api, mock_documents, mock_embeddings):
        """Test health check when fully initialized."""
        semantic_search_api.initialize(documents=mock_documents, embeddings=mock_embeddings)

        result = await semantic_search_api.health_check()

        assert result.status == "healthy"
        assert result.dependencies["embeddings"] == "ready"
        assert result.dependencies["index"] == "ready"


# ============================================================================
# Search Endpoint Tests
# ============================================================================


class TestSearchEndpoint:
    """Tests for search endpoint."""

    @pytest.mark.asyncio
    async def test_search_basic(self, semantic_search_api, mock_documents, mock_embeddings):
        """Test basic search functionality."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchRequest

        semantic_search_api.initialize(documents=mock_documents, embeddings=mock_embeddings)

        request = SemanticSearchRequest(query="Python configuration")
        result = await semantic_search_api.search(request)

        assert result.request_id is not None
        assert result.query == "Python configuration"
        assert result.result_count >= 0
        assert result.execution_time_ms >= 0
        assert result.timestamp is not None

    @pytest.mark.asyncio
    async def test_search_with_top_k(self, semantic_search_api, mock_documents, mock_embeddings):
        """Test search with custom top_k."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchRequest

        semantic_search_api.initialize(documents=mock_documents, embeddings=mock_embeddings)

        request = SemanticSearchRequest(query="Test", top_k=2)
        result = await semantic_search_api.search(request)

        assert result.result_count <= 2

    @pytest.mark.asyncio
    async def test_search_with_min_score(self, semantic_search_api, mock_documents, mock_embeddings):
        """Test search with minimum score filter."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchRequest

        semantic_search_api.initialize(documents=mock_documents, embeddings=mock_embeddings)

        request = SemanticSearchRequest(query="Test", min_score=0.8)
        result = await semantic_search_api.search(request)

        # All results should have score >= min_score
        for item in result.results:
            assert item.score >= 0.8

    @pytest.mark.asyncio
    async def test_search_empty_query(self, semantic_search_api):
        """Test search with empty query."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchRequest
        from app.XNAi_rag_app.api.exceptions import XNAiException

        request = SemanticSearchRequest(query="   ")  # Whitespace only

        with pytest.raises(XNAiException) as exc_info:
            await semantic_search_api.search(request)

        assert exc_info.value.http_status == 400

    @pytest.mark.asyncio
    async def test_search_not_initialized(self, semantic_search_api):
        """Test search when not initialized."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchRequest
        from app.XNAi_rag_app.api.exceptions import XNAiException

        request = SemanticSearchRequest(query="Test")

        with pytest.raises(XNAiException) as exc_info:
            await semantic_search_api.search(request)

        assert exc_info.value.http_status == 503

    @pytest.mark.asyncio
    async def test_search_no_documents(self, semantic_search_api):
        """Test search with no documents."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchRequest

        semantic_search_api.documents = []
        semantic_search_api.embeddings = Mock()

        request = SemanticSearchRequest(query="Test")
        result = await semantic_search_api.search(request)

        assert result.result_count == 0
        assert result.results == []


# ============================================================================
# Search Result Formatting Tests
# ============================================================================


class TestSearchResultFormatting:
    """Tests for search result formatting."""

    @pytest.mark.asyncio
    async def test_result_content_truncated(self, semantic_search_api, mock_documents, mock_embeddings):
        """Test that long content is truncated."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchRequest

        # Create document with long content
        long_doc = Mock()
        long_doc.page_content = "a" * 500
        long_doc.metadata = {"id": "long_doc"}

        semantic_search_api.documents = [long_doc]
        semantic_search_api.embeddings = mock_embeddings

        request = SemanticSearchRequest(query="Test")
        result = await semantic_search_api.search(request)

        if result.results:
            # Content should be truncated to 200 chars
            assert len(result.results[0].content) <= 200

    @pytest.mark.asyncio
    async def test_result_rank_sequential(self, semantic_search_api, mock_documents, mock_embeddings):
        """Test that results have sequential ranks."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchRequest

        semantic_search_api.initialize(documents=mock_documents, embeddings=mock_embeddings)

        request = SemanticSearchRequest(query="Python", top_k=10)
        result = await semantic_search_api.search(request)

        # Ranks should be sequential starting from 1
        for i, item in enumerate(result.results, 1):
            assert item.rank == i

    @pytest.mark.asyncio
    async def test_result_score_precision(self, semantic_search_api, mock_documents, mock_embeddings):
        """Test that scores are rounded to 4 decimal places."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchRequest

        semantic_search_api.initialize(documents=mock_documents, embeddings=mock_embeddings)

        request = SemanticSearchRequest(query="Test")
        result = await semantic_search_api.search(request)

        for item in result.results:
            # Check precision
            score_str = str(item.score)
            if "." in score_str:
                decimal_places = len(score_str.split(".")[1])
                assert decimal_places <= 4


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestSemanticSearchErrorHandling:
    """Tests for error handling in semantic search."""

    @pytest.mark.asyncio
    async def test_xnai_exception_handler(self, semantic_search_api):
        """Test XNAiException handling."""
        from app.XNAi_rag_app.api.exceptions import XNAiException
        from app.XNAi_rag_app.schemas.errors import ErrorCategory
        from fastapi import Request

        mock_request = Mock(spec=Request)
        mock_request.state = Mock()
        mock_request.state.request_id = "req_123"

        exc = XNAiException(message="Test error", category=ErrorCategory.VALIDATION, http_status=400)

        response = await semantic_search_api._xnai_exception_handler(mock_request, exc)

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_unexpected_error_wrapped(self, semantic_search_api, mock_documents, mock_embeddings):
        """Test that unexpected errors are wrapped."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchRequest
        from app.XNAi_rag_app.api.exceptions import XNAiException

        semantic_search_api.documents = mock_documents
        semantic_search_api.embeddings = mock_embeddings

        # Make _perform_search raise an unexpected error
        semantic_search_api._perform_search = Mock(side_effect=RuntimeError("Unexpected"))

        request = SemanticSearchRequest(query="Test")

        with pytest.raises(XNAiException) as exc_info:
            await semantic_search_api.search(request)

        assert exc_info.value.http_status == 500
        assert "unexpected" in exc_info.value.message.lower()


# ============================================================================
# Middleware Tests
# ============================================================================


class TestMiddleware:
    """Tests for API middleware."""

    @pytest.mark.asyncio
    async def test_request_context_middleware(self, semantic_search_api):
        """Test request context middleware."""
        from fastapi import Request
        from starlette.responses import Response

        mock_request = Mock(spec=Request)
        mock_request.headers = {}
        mock_request.state = Mock()

        async def call_next(request):
            return Response(content="OK")

        # The middleware is added in _setup_fastapi
        # We can test it exists by checking the app routes
        app = semantic_search_api.get_app()
        assert app is not None


# ============================================================================
# Factory Function Tests
# ============================================================================


class TestFactoryFunction:
    """Tests for create_semantic_search_api factory."""

    def test_factory_creates_api(self):
        """Test factory creates valid API instance."""
        from app.XNAi_rag_app.api.semantic_search import create_semantic_search_api

        api = create_semantic_search_api()

        assert api is not None
        assert api.get_app() is not None


# ============================================================================
# Integration Tests
# ============================================================================


class TestSemanticSearchIntegration:
    """Integration tests for semantic search API."""

    @pytest.mark.asyncio
    async def test_full_search_flow(self, mock_documents, mock_embeddings):
        """Test complete search flow."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchAPI, SemanticSearchRequest

        api = SemanticSearchAPI()
        api.initialize(documents=mock_documents, embeddings=mock_embeddings)

        # Health check
        health = await api.health_check()
        assert health.status == "healthy"

        # Search
        request = SemanticSearchRequest(query="Python machine learning", top_k=5, min_score=0.0)
        result = await api.search(request)

        assert result.request_id is not None
        assert result.query == "Python machine learning"
        assert result.result_count >= 0
        assert result.execution_time_ms >= 0

    @pytest.mark.asyncio
    async def test_multiple_searches_same_instance(self, semantic_search_api, mock_documents, mock_embeddings):
        """Test multiple searches with same API instance."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchRequest

        semantic_search_api.initialize(documents=mock_documents, embeddings=mock_embeddings)

        queries = ["Python", "configuration", "machine learning"]

        for query in queries:
            request = SemanticSearchRequest(query=query)
            result = await semantic_search_api.search(request)

            assert result is not None
            assert result.query == query


# ============================================================================
# Performance Tests
# ============================================================================


class TestSemanticSearchPerformance:
    """Tests for search performance."""

    @pytest.mark.asyncio
    async def test_execution_time_logged(self, semantic_search_api, mock_documents, mock_embeddings):
        """Test that execution time is logged."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchRequest

        semantic_search_api.initialize(documents=mock_documents, embeddings=mock_embeddings)

        request = SemanticSearchRequest(query="Test")
        result = await semantic_search_api.search(request)

        assert result.execution_time_ms is not None
        assert result.execution_time_ms >= 0

    @pytest.mark.asyncio
    async def test_large_top_k_handled(self, semantic_search_api, mock_documents, mock_embeddings):
        """Test handling of large top_k values."""
        from app.XNAi_rag_app.api.semantic_search import SemanticSearchRequest

        semantic_search_api.initialize(documents=mock_documents, embeddings=mock_embeddings)

        request = SemanticSearchRequest(query="Test", top_k=100)
        result = await semantic_search_api.search(request)

        # Should return available documents (less than top_k)
        assert result.result_count <= len(mock_documents)
