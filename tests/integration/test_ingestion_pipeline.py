"""
Comprehensive Ingestion Pipeline Tests
=======================================

End-to-end, performance, and stress testing for the XNAi RAG ingestion pipeline.

Coverage:
- Document discovery and ingestion
- Content chunking and metadata extraction
- Embedding generation and validation
- Vector storage and retrieval
- Query correctness and performance
- Stress testing under concurrent load
"""

import pytest
import asyncio
import json
import logging
import time
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field, asdict
import statistics

logger = logging.getLogger(__name__)


# ============================================================================
# Data Models for Testing
# ============================================================================


@dataclass
class TestDocument:
    """Test document with metadata."""

    doc_id: str
    title: str
    content: str
    source: str
    source_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create_test_doc(
        cls, index: int, content_size: str = "medium"
    ) -> "TestDocument":
        """Create test document with varying content sizes."""
        sizes = {
            "small": 500,
            "medium": 2000,
            "large": 5000,
        }
        size = sizes.get(content_size, 2000)

        content = " ".join(
            [f"Test content chunk {i}" for i in range(size // 20)]
        )

        return cls(
            doc_id=f"test_doc_{index:04d}",
            title=f"Test Document {index}",
            content=content,
            source=f"test_source_{index // 10}",
            source_type="test",
            metadata={"index": index, "created_at": datetime.now().isoformat()},
        )


@dataclass
class ChunkMetrics:
    """Metrics for a chunk."""

    chunk_id: str
    chunk_index: int
    char_count: int
    token_estimate: int
    embedding_vector: Optional[List[float]] = None
    embedding_dim: int = 384
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IngestionMetrics:
    """Metrics for ingestion operation."""

    operation: str
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0
    document_count: int = 0
    chunk_count: int = 0
    throughput_docs_per_sec: float = 0.0
    throughput_chunks_per_sec: float = 0.0
    memory_peak_mb: float = 0.0
    memory_delta_mb: float = 0.0
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        return d


@dataclass
class QueryPerformance:
    """Query performance metrics."""

    query_type: str  # vector, keyword, hybrid
    query_text: str
    top_k: int
    duration_ms: float
    result_count: int
    scores: List[float] = field(default_factory=list)
    relevance_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StressTestMetrics:
    """Metrics from stress test."""

    concurrent_queries: int
    total_queries: int
    duration_sec: float
    throughput_qps: float
    latencies_ms: List[float] = field(default_factory=list)
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    error_count: int = 0
    error_rate: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================================
# Mock Ingestion Pipeline Components
# ============================================================================


class MockChunker:
    """Mock document chunker."""

    def __init__(self, chunk_size: int = 2000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(self, doc: TestDocument) -> List[ChunkMetrics]:
        """Chunk document into smaller pieces."""
        chunks = []
        content = doc.content
        offset = 0
        chunk_index = 0

        while offset < len(content):
            end = min(offset + self.chunk_size, len(content))
            chunk_text = content[offset : end]

            # Estimate tokens (rough: 1 token per 4 chars)
            token_estimate = len(chunk_text) // 4

            chunk = ChunkMetrics(
                chunk_id=f"{doc.doc_id}_chunk_{chunk_index}",
                chunk_index=chunk_index,
                char_count=len(chunk_text),
                token_estimate=token_estimate,
                metadata={"parent_doc": doc.doc_id, "source": doc.source},
            )

            chunks.append(chunk)
            chunk_index += 1

            # Move offset with overlap
            offset = end - self.overlap

        return chunks


class MockEmbeddingGenerator:
    """Mock embedding generator."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self._embedding_cache = {}

    def embed(self, text: str) -> List[float]:
        """Generate mock embedding."""
        if text in self._embedding_cache:
            return self._embedding_cache[text]

        # Create deterministic embedding based on text hash
        seed = hash(text) % 10000
        import random

        random.seed(seed)
        embedding = [random.gauss(0, 1) for _ in range(self.dimension)]

        # Normalize
        norm = (sum(x**2 for x in embedding)) ** 0.5
        embedding = [x / norm for x in embedding]

        self._embedding_cache[text] = embedding
        return embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts."""
        return [self.embed(text) for text in texts]


class MockVectorStore:
    """Mock vector database."""

    def __init__(self):
        self.documents = {}  # id -> document data
        self.vectors = {}  # id -> embedding
        self.metadata = {}  # id -> metadata

    async def store_document(self, chunk: ChunkMetrics, embedding: List[float]):
        """Store document with embedding."""
        self.documents[chunk.chunk_id] = {
            "index": chunk.chunk_index,
            "char_count": chunk.char_count,
        }
        self.vectors[chunk.chunk_id] = embedding
        self.metadata[chunk.chunk_id] = chunk.metadata

    async def vector_search(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """Search by vector similarity."""
        if not self.vectors:
            return []

        # Calculate cosine similarity for all vectors
        similarities = []

        for doc_id, vector in self.vectors.items():
            # Cosine similarity
            dot = sum(a * b for a, b in zip(query_embedding, vector))
            similarities.append((doc_id, dot))

        # Sort by score descending, return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    async def keyword_search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Simple keyword search."""
        results = []

        for doc_id, metadata in self.metadata.items():
            # Simple keyword matching
            parent = metadata.get("parent_doc", "")
            score = 0.5 if query.lower() in parent.lower() else 0.1
            results.append((doc_id, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve document."""
        return self.documents.get(doc_id)

    def document_count(self) -> int:
        """Total documents stored."""
        return len(self.documents)

    def vector_count(self) -> int:
        """Total vectors stored."""
        return len(self.vectors)


# ============================================================================
# Integration Test Fixtures
# ============================================================================


@pytest.fixture
def test_documents():
    """Generate test documents."""
    return [
        TestDocument.create_test_doc(i, "medium") for i in range(100)
    ]


@pytest.fixture
def chunker():
    """Create mock chunker."""
    return MockChunker(chunk_size=2000, overlap=200)


@pytest.fixture
def embedding_generator():
    """Create mock embedding generator."""
    return MockEmbeddingGenerator(dimension=384)


@pytest.fixture
def vector_store():
    """Create mock vector store."""
    return MockVectorStore()


@pytest.fixture
def ingestion_metrics():
    """List to collect metrics."""
    return []


# ============================================================================
# End-to-End Integration Tests
# ============================================================================


class TestIngestionPipeline:
    """End-to-end ingestion pipeline tests."""

    @pytest.mark.asyncio
    async def test_document_discovery(self, test_documents):
        """Test document discovery phase."""
        assert len(test_documents) == 100
        assert all(isinstance(doc, TestDocument) for doc in test_documents)
        assert all(doc.doc_id for doc in test_documents)

    @pytest.mark.asyncio
    async def test_chunking(self, test_documents, chunker):
        """Test document chunking."""
        doc = test_documents[0]
        chunks = chunker.chunk_document(doc)

        assert len(chunks) > 0
        assert all(isinstance(c, ChunkMetrics) for c in chunks)
        assert all(c.chunk_index >= 0 for c in chunks)
        assert all(c.char_count > 0 for c in chunks)

        logger.info(f"Document chunked into {len(chunks)} chunks")

    @pytest.mark.asyncio
    async def test_metadata_extraction(self, test_documents, chunker):
        """Test metadata extraction from chunks."""
        doc = test_documents[0]
        chunks = chunker.chunk_document(doc)

        for chunk in chunks:
            assert chunk.metadata["parent_doc"] == doc.doc_id
            assert chunk.metadata["source"] == doc.source
            assert chunk.token_estimate > 0

    @pytest.mark.asyncio
    async def test_embedding_generation(self, embedding_generator):
        """Test embedding generation."""
        texts = [
            "Test document one",
            "Test document two",
            "Another test document",
        ]

        embeddings = embedding_generator.embed_batch(texts)

        assert len(embeddings) == 3
        assert all(len(e) == 384 for e in embeddings)

        # Verify normalization (magnitude ~1.0)
        for embedding in embeddings:
            mag = (sum(x**2 for x in embedding)) ** 0.5
            assert 0.99 <= mag <= 1.01

    @pytest.mark.asyncio
    async def test_vector_storage(self, vector_store, chunker, embedding_generator, test_documents):
        """Test vector storage."""
        doc = test_documents[0]
        chunks = chunker.chunk_document(doc)

        for chunk in chunks:
            embedding = embedding_generator.embed(chunk.metadata.get("parent_doc", ""))
            await vector_store.store_document(chunk, embedding)

        assert vector_store.document_count() == len(chunks)
        assert vector_store.vector_count() == len(chunks)

    @pytest.mark.asyncio
    async def test_query_validation_vector_search(
        self, vector_store, chunker, embedding_generator, test_documents
    ):
        """Test vector query returns all stored chunks."""
        # Store documents
        stored_chunks = []
        for doc in test_documents[:10]:
            chunks = chunker.chunk_document(doc)
            for chunk in chunks:
                embedding = embedding_generator.embed(chunk.metadata.get("parent_doc", ""))
                await vector_store.store_document(chunk, embedding)
                stored_chunks.append(chunk)

        # Query
        query_text = test_documents[0].title
        query_embedding = embedding_generator.embed(query_text)
        results = await vector_store.vector_search(query_embedding, top_k=10)

        assert len(results) > 0
        assert all(chunk_id in vector_store.vectors for chunk_id, _ in results)

        logger.info(f"Vector query returned {len(results)} results from {len(stored_chunks)} stored")

    @pytest.mark.asyncio
    async def test_query_validation_keyword_search(
        self, vector_store, chunker, embedding_generator, test_documents
    ):
        """Test keyword query functionality."""
        # Store documents
        for doc in test_documents[:10]:
            chunks = chunker.chunk_document(doc)
            for chunk in chunks:
                embedding = embedding_generator.embed(chunk.metadata.get("parent_doc", ""))
                await vector_store.store_document(chunk, embedding)

        # Query
        results = await vector_store.keyword_search("test_source", top_k=10)

        assert len(results) > 0
        logger.info(f"Keyword query returned {len(results)} results")

    @pytest.mark.asyncio
    async def test_embedding_correctness(self, embedding_generator):
        """Test embedding correctness - same text produces same embedding."""
        text = "This is a test document for embedding"

        emb1 = embedding_generator.embed(text)
        emb2 = embedding_generator.embed(text)

        # Should be identical
        assert emb1 == emb2

        # Different text should produce different embedding
        emb3 = embedding_generator.embed("Different text entirely")
        assert emb3 != emb1


# ============================================================================
# Performance Testing
# ============================================================================


class TestPerformance:
    """Performance testing for ingestion pipeline."""

    @pytest.mark.asyncio
    async def test_ingestion_throughput(
        self, test_documents, chunker, embedding_generator, vector_store
    ):
        """Test ingestion throughput: docs/sec, chunks/sec."""
        start_time = time.time()

        total_chunks = 0
        for doc in test_documents:
            chunks = chunker.chunk_document(doc)
            total_chunks += len(chunks)

            for chunk in chunks:
                embedding = embedding_generator.embed(chunk.metadata.get("parent_doc", ""))

        end_time = time.time()
        duration = end_time - start_time

        docs_per_sec = len(test_documents) / duration
        chunks_per_sec = total_chunks / duration

        logger.info(f"Throughput: {docs_per_sec:.2f} docs/sec, {chunks_per_sec:.2f} chunks/sec")

        assert docs_per_sec > 100, f"Throughput too low: {docs_per_sec:.2f} docs/sec"
        assert chunks_per_sec > 100, f"Throughput too low: {chunks_per_sec:.2f} chunks/sec"

    @pytest.mark.asyncio
    async def test_vector_query_latency(
        self, vector_store, chunker, embedding_generator, test_documents
    ):
        """Test vector query latency distribution."""
        # Store documents
        for doc in test_documents[:50]:
            chunks = chunker.chunk_document(doc)
            for chunk in chunks:
                embedding = embedding_generator.embed(chunk.metadata.get("parent_doc", ""))
                await vector_store.store_document(chunk, embedding)

        # Perform queries and measure latency
        latencies = []
        for i in range(100):
            query_embedding = embedding_generator.embed(f"query_{i}")

            start = time.time()
            results = await vector_store.vector_search(query_embedding, top_k=5)
            duration_ms = (time.time() - start) * 1000

            latencies.append(duration_ms)

        p95 = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
        p99 = statistics.quantiles(latencies, n=100)[98]  # 99th percentile

        logger.info(f"Vector query latency - p95: {p95:.2f}ms, p99: {p99:.2f}ms")

        assert p95 < 100, f"p95 latency too high: {p95:.2f}ms"

    @pytest.mark.asyncio
    async def test_keyword_query_latency(
        self, vector_store, chunker, embedding_generator, test_documents
    ):
        """Test keyword query latency."""
        # Store documents
        for doc in test_documents[:50]:
            chunks = chunker.chunk_document(doc)
            for chunk in chunks:
                embedding = embedding_generator.embed(chunk.metadata.get("parent_doc", ""))
                await vector_store.store_document(chunk, embedding)

        # Perform queries
        latencies = []
        for i in range(50):
            start = time.time()
            results = await vector_store.keyword_search(f"test_source_{i % 5}", top_k=5)
            duration_ms = (time.time() - start) * 1000

            latencies.append(duration_ms)

        p95 = statistics.quantiles(latencies, n=20)[18]

        logger.info(f"Keyword query latency - p95: {p95:.2f}ms")

        assert p95 < 50, f"p95 latency too high: {p95:.2f}ms"

    @pytest.mark.asyncio
    async def test_memory_usage_during_ingestion(
        self, test_documents, chunker, embedding_generator
    ):
        """Test memory usage during ingestion."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        mem_start = process.memory_info().rss / 1024 / 1024  # MB

        for doc in test_documents[:50]:
            chunks = chunker.chunk_document(doc)
            for chunk in chunks:
                embedding = embedding_generator.embed(chunk.metadata.get("parent_doc", ""))

        mem_end = process.memory_info().rss / 1024 / 1024  # MB
        mem_delta = mem_end - mem_start

        logger.info(f"Memory delta: {mem_delta:.2f} MB")

        # Should not consume excessive memory
        assert mem_delta < 500, f"Memory usage too high: {mem_delta:.2f} MB"


# ============================================================================
# Stress Testing
# ============================================================================


class TestStress:
    """Stress testing for concurrent operations."""

    @pytest.mark.asyncio
    async def test_concurrent_vector_queries(
        self, vector_store, embedding_generator, test_documents, chunker
    ):
        """Test 1000+ concurrent vector queries."""
        # Store documents
        for doc in test_documents[:100]:
            chunks = chunker.chunk_document(doc)
            for chunk in chunks:
                embedding = embedding_generator.embed(chunk.metadata.get("parent_doc", ""))
                await vector_store.store_document(chunk, embedding)

        logger.info(f"Stored {vector_store.vector_count()} vectors")

        # Concurrent queries
        concurrent = 100
        total_queries = 1000

        async def query_task(i):
            query_embedding = embedding_generator.embed(f"query_{i}")
            start = time.time()
            results = await vector_store.vector_search(query_embedding, top_k=5)
            return (time.time() - start) * 1000

        start_time = time.time()
        latencies = []

        # Run queries in batches
        for batch_start in range(0, total_queries, concurrent):
            batch_size = min(concurrent, total_queries - batch_start)
            tasks = [query_task(i) for i in range(batch_start, batch_start + batch_size)]
            batch_latencies = await asyncio.gather(*tasks)
            latencies.extend(batch_latencies)

        total_duration = time.time() - start_time

        p50 = statistics.median(latencies)
        p95 = statistics.quantiles(latencies, n=20)[18]
        p99 = statistics.quantiles(latencies, n=100)[98]
        qps = total_queries / total_duration

        logger.info(
            f"Stress test: {total_queries} queries in {total_duration:.2f}s "
            f"({qps:.2f} qps) - p50: {p50:.2f}ms, p95: {p95:.2f}ms, p99: {p99:.2f}ms"
        )

        assert p95 < 200, f"p95 latency too high under stress: {p95:.2f}ms"

    @pytest.mark.asyncio
    async def test_incremental_updates_under_load(
        self, vector_store, embedding_generator, test_documents, chunker
    ):
        """Test incremental updates while querying."""
        # Initial load
        for doc in test_documents[:50]:
            chunks = chunker.chunk_document(doc)
            for chunk in chunks:
                embedding = embedding_generator.embed(chunk.metadata.get("parent_doc", ""))
                await vector_store.store_document(chunk, embedding)

        initial_count = vector_store.vector_count()

        async def query_task():
            query_embedding = embedding_generator.embed("test_query")
            return await vector_store.vector_search(query_embedding, top_k=5)

        async def update_task():
            for doc in test_documents[50:75]:
                chunks = chunker.chunk_document(doc)
                for chunk in chunks:
                    embedding = embedding_generator.embed(chunk.metadata.get("parent_doc", ""))
                    await vector_store.store_document(chunk, embedding)
                await asyncio.sleep(0.01)

        # Run queries and updates concurrently
        tasks = [query_task() for _ in range(100)] + [update_task()]

        start = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start

        final_count = vector_store.vector_count()

        logger.info(
            f"Incremental update test: {initial_count} -> {final_count} vectors in {duration:.2f}s"
        )

        assert final_count > initial_count
        assert len(results) > 0


# ============================================================================
# Test Report Generation
# ============================================================================


class TestReporter:
    """Generate test reports."""

    def __init__(self):
        self.ingestion_metrics: List[IngestionMetrics] = []
        self.query_metrics: List[QueryPerformance] = []
        self.stress_metrics: List[StressTestMetrics] = []

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "test_suite": "Ingestion Pipeline Validation",
            "summary": self._generate_summary(),
            "ingestion_metrics": [m.to_dict() for m in self.ingestion_metrics],
            "query_performance": [q.to_dict() for q in self.query_metrics],
            "stress_test_results": [s.to_dict() for s in self.stress_metrics],
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        return {
            "total_tests": len(self.ingestion_metrics) + len(self.query_metrics) + len(self.stress_metrics),
            "ingestion_tests": len(self.ingestion_metrics),
            "query_tests": len(self.query_metrics),
            "stress_tests": len(self.stress_metrics),
        }

    def save_report(self, path: Path):
        """Save report to JSON file."""
        report = self.generate_report()
        with open(path, "w") as f:
            json.dump(report, f, indent=2)


# ============================================================================
# Performance Baseline Comparison
# ============================================================================


class PerformanceBaseline:
    """Performance baseline tracking."""

    TARGET_INGESTION_THROUGHPUT = 100  # docs/sec
    TARGET_VECTOR_QUERY_P95 = 100  # ms
    TARGET_KEYWORD_QUERY_P95 = 50  # ms

    def __init__(self):
        self.baselines = {
            "ingestion_throughput": self.TARGET_INGESTION_THROUGHPUT,
            "vector_query_p95": self.TARGET_VECTOR_QUERY_P95,
            "keyword_query_p95": self.TARGET_KEYWORD_QUERY_P95,
        }

    def validate(self, metrics: Dict[str, float]) -> Dict[str, bool]:
        """Validate metrics against baselines."""
        results = {}

        for key, target in self.baselines.items():
            if key in metrics:
                if key.endswith("_throughput"):
                    results[key] = metrics[key] >= target
                else:
                    results[key] = metrics[key] <= target

        return results

    def to_dict(self) -> Dict[str, float]:
        """Export baselines."""
        return self.baselines.copy()
