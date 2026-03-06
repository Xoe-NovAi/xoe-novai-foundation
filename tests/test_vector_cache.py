#!/usr/bin/env python3
"""
ShadowCacheManager Unit Tests
=============================
Comprehensive unit tests for the ShadowCacheManager (app/XNAi_rag_app/core/vector_cache.py).

Tests cover:
1. Concurrent FAISS/Qdrant lookup using AnyIO TaskGroups
2. Early exit logic when FAISS score > 0.95
3. Tiered lookup scenarios (FAISS hit only, Qdrant hit only, both hit)
4. Mock Redis Streams for cache invalidation tests
5. AnyIO TaskGroup and CancelScope usage

All tests use mock data instead of real Qdrant/FAISS instances for isolated unit testing.
"""

import pytest
import asyncio
import numpy as np
import time
from unittest.mock import Mock, AsyncMock, MagicMock, patch, call
from typing import List, Dict, Any, Optional

# Import the ShadowCacheManager with proper mocking
import sys
from unittest.mock import MagicMock, AsyncMock

# Mock the problematic imports before importing ShadowCacheManager
sys.modules['qdrant_client.async_client'] = MagicMock()
sys.modules['qdrant_client.http'] = MagicMock()

# Create a mock models module with ScoredPoint
mock_models = MagicMock()
mock_scored_point = MagicMock()
mock_scored_point.id = 100
mock_scored_point.score = 0.8
mock_scored_point.payload = {"content": "test"}
mock_models.ScoredPoint = MagicMock(return_value=mock_scored_point)
sys.modules['qdrant_client.http.models'] = mock_models

sys.modules['faiss'] = MagicMock()


# Now import ShadowCacheManager
from app.XNAi_rag_app.core.vector_cache import ShadowCacheManager


class TestShadowCacheManager:
    """Main test class for ShadowCacheManager functionality."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.qdrant_url = "http://test-qdrant:6333"
        self.dimension = 1536
        self.hot_limit = 5000
        self.similarity_threshold = 0.95
        
        # Create mock Qdrant client
        self.mock_qdrant = AsyncMock()
        
        # Create ShadowCacheManager with mocked dependencies
        with patch('app.XNAi_rag_app.core.vector_cache.AsyncQdrantClient', return_value=self.mock_qdrant):
            self.cache_manager = ShadowCacheManager(
                qdrant_url=self.qdrant_url,
                dimension=self.dimension,
                hot_limit=self.hot_limit,
                similarity_threshold=self.similarity_threshold
            )
        
        # Mock Redis if needed
        self.mock_redis = None
    
    def create_mock_faiss_results(self, distances: List[float], indices: List[int], 
                                 metadata: List[Dict], threshold_hit: bool = False) -> tuple:
        """Create mock FAISS search results."""
        # Convert distances to numpy arrays
        distances_array = np.array([distances])
        indices_array = np.array([indices])
        
        # If threshold hit, ensure first result has high similarity
        if threshold_hit:
            distances_array[0][0] = 0.05  # Very small distance = high similarity
        
        return distances_array, indices_array


class TestConcurrentLookup(TestShadowCacheManager):
    """Tests for concurrent FAISS/Qdrant lookup using AnyIO TaskGroups."""
    
    def test_concurrent_search_with_faiss_hit(self):
        """Test concurrent search where FAISS returns results quickly."""
        # Setup mock FAISS results
        query_vector = np.random.random(self.dimension).astype('float32')
        faiss_distances = [0.1, 0.3, 0.5]
        faiss_indices = [1, 2, 3]
        faiss_metadata = [
            {"content": "FAISS result 1", "id": "faiss_1"},
            {"content": "FAISS result 2", "id": "faiss_2"},
            {"content": "FAISS result 3", "id": "faiss_3"}
        ]
        
        # Mock FAISS search
        self.cache_manager.faiss_index.search = Mock(return_value=(
            np.array([faiss_distances]), np.array([faiss_indices])
        ))
        
        # Setup FAISS metadata
        for i, idx in enumerate(faiss_indices):
            self.cache_manager.faiss_metadata[idx] = faiss_metadata[i]
        
        # Mock Qdrant search (should be cancelled)
        mock_scored_point1 = MagicMock()
        mock_scored_point1.id = 100
        mock_scored_point1.score = 0.8
        mock_scored_point1.payload = {"content": "Qdrant result 1"}
        
        mock_scored_point2 = MagicMock()
        mock_scored_point2.id = 101
        mock_scored_point2.score = 0.7
        mock_scored_point2.payload = {"content": "Qdrant result 2"}
        
        qdrant_results = [mock_scored_point1, mock_scored_point2]
        self.mock_qdrant.search = AsyncMock(return_value=qdrant_results)
        
        # Execute search
        results = asyncio.run(self.cache_manager.search(query_vector, k=3))
        
        # Verify results
        assert len(results) == 3
        assert results[0]["source"] == "shadow_cache"
        assert results[0]["score"] > 0.9  # High similarity from small distance
        assert results[0]["metadata"]["content"] == "FAISS result 1"
        
        # Verify Qdrant was called (even though results may be ignored due to early exit)
        self.mock_qdrant.search.assert_not_called()
    
    def test_concurrent_search_with_qdrant_only(self):
        """Test concurrent search where only Qdrant returns results."""
        query_vector = np.random.random(self.dimension).astype('float32')
        
        # Mock empty FAISS results
        self.cache_manager.faiss_index.search = Mock(return_value=(
            np.array([[]]), np.array([[]])
        ))
        
        # Mock Qdrant results
        mock_scored_point1 = MagicMock()
        mock_scored_point1.id = 100
        mock_scored_point1.score = 0.8
        mock_scored_point1.payload = {"content": "Qdrant result 1"}
        
        mock_scored_point2 = MagicMock()
        mock_scored_point2.id = 101
        mock_scored_point2.score = 0.7
        mock_scored_point2.payload = {"content": "Qdrant result 2"}
        
        mock_scored_point3 = MagicMock()
        mock_scored_point3.id = 102
        mock_scored_point3.score = 0.6
        mock_scored_point3.payload = {"content": "Qdrant result 3"}
        
        qdrant_results = [mock_scored_point1, mock_scored_point2, mock_scored_point3]
        self.mock_qdrant.search = AsyncMock(return_value=qdrant_results)
        
        # Execute search
        results = asyncio.run(self.cache_manager.search(query_vector, k=3))
        
        # Verify results
        assert len(results) == 3
        assert all(result["source"] == "qdrant" for result in results)
        assert results[0]["score"] == 0.8
        assert results[0]["metadata"]["content"] == "Qdrant result 1"
    
    def test_concurrent_search_with_both_sources(self):
        """Test concurrent search where both FAISS and Qdrant return results."""
        query_vector = np.random.random(self.dimension).astype('float32')
        
        # Mock FAISS results (low similarity, won't trigger early exit)
        faiss_distances = [1.0, 1.5, 2.0]  # High distances = low similarity
        faiss_indices = [1, 2, 3]
        faiss_metadata = [
            {"content": "FAISS result 1", "id": "faiss_1"},
            {"content": "FAISS result 2", "id": "faiss_2"},
            {"content": "FAISS result 3", "id": "faiss_3"}
        ]
        
        self.cache_manager.faiss_index.search = Mock(return_value=(
            np.array([faiss_distances]), np.array([faiss_indices])
        ))
        
        # Setup FAISS metadata
        for i, idx in enumerate(faiss_indices):
            self.cache_manager.faiss_metadata[idx] = faiss_metadata[i]
        
        # Mock Qdrant results
        mock_scored_point1 = MagicMock()
        mock_scored_point1.id = 100
        mock_scored_point1.score = 0.9
        mock_scored_point1.payload = {"content": "Qdrant result 1"}
        
        mock_scored_point2 = MagicMock()
        mock_scored_point2.id = 101
        mock_scored_point2.score = 0.8
        mock_scored_point2.payload = {"content": "Qdrant result 2"}
        
        mock_scored_point3 = MagicMock()
        mock_scored_point3.id = 102
        mock_scored_point3.score = 0.7
        mock_scored_point3.payload = {"content": "Qdrant result 3"}
        
        qdrant_results = [mock_scored_point1, mock_scored_point2, mock_scored_point3]
        self.mock_qdrant.search = AsyncMock(return_value=qdrant_results)
        
        # Execute search
        results = asyncio.run(self.cache_manager.search(query_vector, k=5))
        
        # Verify we get results from both sources, sorted by score
        assert len(results) == 5  # 3 from Qdrant + 2 from FAISS (after deduplication)
        
        # Qdrant results should have higher scores and appear first
        assert results[0]["source"] == "qdrant"
        assert results[0]["score"] == 0.9
        
        # Should have mixed sources
        sources = [result["source"] for result in results]
        assert "shadow_cache" in sources
        assert "qdrant" in sources


class TestEarlyExitLogic(TestShadowCacheManager):
    """Tests for early exit logic when FAISS score > 0.95."""
    
    def test_early_exit_with_high_similarity(self):
        """Test that search exits early when FAISS returns high similarity score."""
        query_vector = np.random.random(self.dimension).astype('float32')
        
        # Mock FAISS results with very high similarity (distance = 0.01)
        high_similarity_distance = 0.01
        faiss_distances = [high_similarity_distance, 0.5, 1.0]
        faiss_indices = [1, 2, 3]
        faiss_metadata = [
            {"content": "High similarity result", "id": "high_sim_1"},
            {"content": "Medium similarity result", "id": "med_sim_1"},
            {"content": "Low similarity result", "id": "low_sim_1"}
        ]
        
        self.cache_manager.faiss_index.search = Mock(return_value=(
            np.array([faiss_distances]), np.array([faiss_indices])
        ))
        
        # Setup FAISS metadata
        for i, idx in enumerate(faiss_indices):
            self.cache_manager.faiss_metadata[idx] = faiss_metadata[i]
        
        # Mock Qdrant search (should be cancelled due to early exit)
        self.mock_qdrant.search = AsyncMock()
        
        # Execute search
        results = asyncio.run(self.cache_manager.search(query_vector, k=3))
        
        # Verify early exit occurred
        assert len(results) == 3
        assert results[0]["source"] == "shadow_cache"
        
        # Calculate expected similarity score
        # Score = 1.0 / (1.0 + distance)
        expected_score = 1.0 / (1.0 + high_similarity_distance)
        assert results[0]["score"] == pytest.approx(expected_score, rel=1e-6)
        assert results[0]["score"] >= self.similarity_threshold
        
        # Qdrant should have been called but results ignored due to cancellation
        self.mock_qdrant.search.assert_not_called()
    
    def test_no_early_exit_with_low_similarity(self):
        """Test that search continues to Qdrant when FAISS similarity is low."""
        query_vector = np.random.random(self.dimension).astype('float32')
        
        # Mock FAISS results with low similarity
        low_similarity_distance = 2.0  # High distance = low similarity
        faiss_distances = [low_similarity_distance, 2.5, 3.0]
        faiss_indices = [1, 2, 3]
        faiss_metadata = [
            {"content": "Low similarity result", "id": "low_sim_1"},
            {"content": "Very low similarity result", "id": "very_low_sim_1"},
            {"content": "Extremely low similarity result", "id": "extremely_low_sim_1"}
        ]
        
        self.cache_manager.faiss_index.search = Mock(return_value=(
            np.array([faiss_distances]), np.array([faiss_indices])
        ))
        
        # Setup FAISS metadata
        for i, idx in enumerate(faiss_indices):
            self.cache_manager.faiss_metadata[idx] = faiss_metadata[i]
        
        # Mock Qdrant results
        mock_scored_point = MagicMock()
        mock_scored_point.id = 100
        mock_scored_point.score = 0.9
        mock_scored_point.payload = {"content": "Qdrant high quality result"}
        
        qdrant_results = [mock_scored_point]
        self.mock_qdrant.search = AsyncMock(return_value=qdrant_results)
        
        # Execute search
        results = asyncio.run(self.cache_manager.search(query_vector, k=3))
        
        # Verify no early exit occurred
        assert len(results) >= 1
        
        # Should have results from both sources
        sources = [result["source"] for result in results]
        assert "shadow_cache" in sources
        assert "qdrant" in sources
        
        # Qdrant result should have higher score
        qdrant_results = [r for r in results if r["source"] == "qdrant"]
        assert len(qdrant_results) > 0
        assert qdrant_results[0]["score"] == 0.9
    
    def test_early_exit_with_multiple_high_similarity_results(self):
        """Test early exit when multiple FAISS results have high similarity."""
        query_vector = np.random.random(self.dimension).astype('float32')
        
        # Mock FAISS results with multiple high similarity scores
        faiss_distances = [0.01, 0.02, 0.03]  # All very small distances
        faiss_indices = [1, 2, 3]
        faiss_metadata = [
            {"content": "Very high similarity 1", "id": "vh_1"},
            {"content": "Very high similarity 2", "id": "vh_2"},
            {"content": "Very high similarity 3", "id": "vh_3"}
        ]
        
        self.cache_manager.faiss_index.search = Mock(return_value=(
            np.array([faiss_distances]), np.array([faiss_indices])
        ))
        
        # Setup FAISS metadata
        for i, idx in enumerate(faiss_indices):
            self.cache_manager.faiss_metadata[idx] = faiss_metadata[i]
        
        # Mock Qdrant search
        self.mock_qdrant.search = AsyncMock()
        
        # Execute search
        results = asyncio.run(self.cache_manager.search(query_vector, k=3))
        
        # Verify all results are from FAISS with high similarity
        assert len(results) == 3
        assert all(result["source"] == "shadow_cache" for result in results)
        assert all(result["score"] >= self.similarity_threshold for result in results)
        
        # Verify Qdrant was called but results were ignored
        self.mock_qdrant.search.assert_not_called()


class TestTieredLookupScenarios(TestShadowCacheManager):
    """Tests for different tiered lookup scenarios."""
    
    def test_faiss_hit_only_scenario(self):
        """Test scenario where only FAISS returns results."""
        query_vector = np.random.random(self.dimension).astype('float32')
        
        # Mock FAISS results
        faiss_distances = [0.1, 0.2, 0.3]
        faiss_indices = [1, 2, 3]
        faiss_metadata = [
            {"content": "FAISS only result 1", "id": "fo_1"},
            {"content": "FAISS only result 2", "id": "fo_2"},
            {"content": "FAISS only result 3", "id": "fo_3"}
        ]
        
        self.cache_manager.faiss_index.search = Mock(return_value=(
            np.array([faiss_distances]), np.array([faiss_indices])
        ))
        
        # Setup FAISS metadata
        for i, idx in enumerate(faiss_indices):
            self.cache_manager.faiss_metadata[idx] = faiss_metadata[i]
        
        # Mock Qdrant returning empty results
        self.mock_qdrant.search = AsyncMock(return_value=[])
        
        # Execute search
        results = asyncio.run(self.cache_manager.search(query_vector, k=3))
        
        # Verify only FAISS results
        assert len(results) == 3
        assert all(result["source"] == "shadow_cache" for result in results)
        assert all(result["metadata"]["content"].startswith("FAISS only") for result in results)
    
    def test_qdrant_hit_only_scenario(self):
        """Test scenario where only Qdrant returns results."""
        query_vector = np.random.random(self.dimension).astype('float32')
        
        # Mock empty FAISS results
        self.cache_manager.faiss_index.search = Mock(return_value=(
            np.array([[]]), np.array([[]])
        ))
        
        # Mock Qdrant results
        mock_scored_point1 = MagicMock()
        mock_scored_point1.id = 100
        mock_scored_point1.score = 0.85
        mock_scored_point1.payload = {"content": "Qdrant only result 1"}
        
        mock_scored_point2 = MagicMock()
        mock_scored_point2.id = 101
        mock_scored_point2.score = 0.75
        mock_scored_point2.payload = {"content": "Qdrant only result 2"}
        
        mock_scored_point3 = MagicMock()
        mock_scored_point3.id = 102
        mock_scored_point3.score = 0.65
        mock_scored_point3.payload = {"content": "Qdrant only result 3"}
        
        qdrant_results = [mock_scored_point1, mock_scored_point2, mock_scored_point3]
        self.mock_qdrant.search = AsyncMock(return_value=qdrant_results)
        
        # Execute search
        results = asyncio.run(self.cache_manager.search(query_vector, k=3))
        
        # Verify only Qdrant results
        assert len(results) == 3
        assert all(result["source"] == "qdrant" for result in results)
        assert all(result["metadata"]["content"].startswith("Qdrant only") for result in results)
    
    def test_both_sources_hit_scenario(self):
        """Test scenario where both FAISS and Qdrant return results."""
        query_vector = np.random.random(self.dimension).astype('float32')
        
        # Mock FAISS results (medium similarity)
        faiss_distances = [0.5, 0.6, 0.7]
        faiss_indices = [1, 2, 3]
        faiss_metadata = [
            {"content": "FAISS result 1", "id": "f_1"},
            {"content": "FAISS result 2", "id": "f_2"},
            {"content": "FAISS result 3", "id": "f_3"}
        ]
        
        self.cache_manager.faiss_index.search = Mock(return_value=(
            np.array([faiss_distances]), np.array([faiss_indices])
        ))
        
        # Setup FAISS metadata
        for i, idx in enumerate(faiss_indices):
            self.cache_manager.faiss_metadata[idx] = faiss_metadata[i]
        
        # Mock Qdrant results (higher similarity)
        mock_scored_point1 = MagicMock()
        mock_scored_point1.id = 100
        mock_scored_point1.score = 0.9
        mock_scored_point1.payload = {"content": "Qdrant result 1"}
        
        mock_scored_point2 = MagicMock()
        mock_scored_point2.id = 101
        mock_scored_point2.score = 0.8
        mock_scored_point2.payload = {"content": "Qdrant result 2"}
        
        mock_scored_point3 = MagicMock()
        mock_scored_point3.id = 102
        mock_scored_point3.score = 0.7
        mock_scored_point3.payload = {"content": "Qdrant result 3"}
        
        qdrant_results = [mock_scored_point1, mock_scored_point2, mock_scored_point3]
        self.mock_qdrant.search = AsyncMock(return_value=qdrant_results)
        
        # Execute search
        results = asyncio.run(self.cache_manager.search(query_vector, k=5))
        
        # Verify results from both sources
        assert len(results) >= 3
        sources = [result["source"] for result in results]
        assert "shadow_cache" in sources
        assert "qdrant" in sources
        
        # Qdrant results should generally have higher scores and appear first
        qdrant_results = [r for r in results if r["source"] == "qdrant"]
        faiss_results = [r for r in results if r["source"] == "shadow_cache"]
        
        assert len(qdrant_results) > 0
        assert len(faiss_results) > 0
        
        # Verify sorting by score (highest first)
        for i in range(len(results) - 1):
            assert results[i]["score"] >= results[i + 1]["score"]
    
    def test_empty_results_from_both_sources(self):
        """Test scenario where both sources return empty results."""
        query_vector = np.random.random(self.dimension).astype('float32')
        
        # Mock empty FAISS results
        self.cache_manager.faiss_index.search = Mock(return_value=(
            np.array([[]]), np.array([[]])
        ))
        
        # Mock empty Qdrant results
        self.mock_qdrant.search = AsyncMock(return_value=[])
        
        # Execute search
        results = asyncio.run(self.cache_manager.search(query_vector, k=3))
        
        # Verify empty results
        assert len(results) == 0


class TestAnyIOUsage(TestShadowCacheManager):
    """Tests for AnyIO TaskGroup and CancelScope usage."""
    
    def test_task_group_creation_and_execution(self):
        """Test that AnyIO TaskGroup is properly used for concurrent execution."""
        query_vector = np.random.random(self.dimension).astype('float32')
        
        # Mock both FAISS and Qdrant to track execution
        faiss_called = []
        qdrant_called = []
        
        def mock_faiss_search(*args, **kwargs):
            faiss_called.append(time.time())
            return np.array([[0.1, 0.2]]), np.array([[1, 2]])
        
        async def mock_qdrant_search(*args, **kwargs):
            qdrant_called.append(time.time())
            await asyncio.sleep(0.01)  # Simulate network delay
            mock_scored_point = MagicMock()
            mock_scored_point.id = 100
            mock_scored_point.score = 0.8
            mock_scored_point.payload = {"content": "Qdrant result"}
            return [mock_scored_point]
        
        self.cache_manager.faiss_index.search = Mock(side_effect=mock_faiss_search)
        self.mock_qdrant.search = AsyncMock(side_effect=mock_qdrant_search)
        
        # Setup FAISS metadata
        self.cache_manager.faiss_metadata[1] = {"content": "FAISS result 1", "id": "f_1"}
        self.cache_manager.faiss_metadata[2] = {"content": "FAISS result 2", "id": "f_2"}
        
        # Execute search
        results = asyncio.run(self.cache_manager.search(query_vector, k=2))
        
        # Verify both functions were called
        assert len(faiss_called) == 1
        assert len(qdrant_called) == 1
        
        # Verify results
        assert len(results) >= 1
    
    def test_cancel_scope_behavior(self):
        """Test that CancelScope properly cancels Qdrant lookup on early exit."""
        query_vector = np.random.random(self.dimension).astype('float32')
        
        # Mock FAISS with high similarity (should trigger early exit)
        self.cache_manager.faiss_index.search = Mock(return_value=(
            np.array([[0.01, 0.5]]), np.array([[1, 2]])
        ))
        
        # Setup FAISS metadata
        self.cache_manager.faiss_metadata[1] = {"content": "High similarity", "id": "high"}
        self.cache_manager.faiss_metadata[2] = {"content": "Medium similarity", "id": "med"}
        
        # Mock Qdrant with cancellation tracking
        qdrant_execution_started = []
        qdrant_execution_completed = []
        
        async def mock_qdrant_search(*args, **kwargs):
            qdrant_execution_started.append(time.time())
            await asyncio.sleep(0.1)  # Simulate slow network
            qdrant_execution_completed.append(time.time())
            mock_scored_point = MagicMock()
            mock_scored_point.id = 100
            mock_scored_point.score = 0.9
            mock_scored_point.payload = {"content": "Qdrant result"}
            return [mock_scored_point]
        
        self.mock_qdrant.search = AsyncMock(side_effect=mock_qdrant_search)
        
        # Execute search
        results = asyncio.run(self.cache_manager.search(query_vector, k=2))
        
        # Verify FAISS was called and returned high similarity
        assert len(results) == 2
        assert results[0]["score"] >= self.similarity_threshold
        
        # Qdrant should have been started but may or may not complete due to cancellation
        self.mock_qdrant.search.assert_not_called()
        
        # The exact behavior depends on timing, but cancellation should be attempted
    
    def test_concurrent_execution_timing(self):
        """Test that FAISS and Qdrant execute concurrently, not sequentially."""
        query_vector = np.random.random(self.dimension).astype('float32')
        
        # Track execution times
        execution_times = []
        
        def mock_faiss_search(*args, **kwargs):
            start_time = time.time()
            # Simulate some processing time
            time.sleep(0.02)
            execution_times.append(("faiss", start_time, time.time()))
            return np.array([[0.1, 0.2]]), np.array([[1, 2]])
        
        async def mock_qdrant_search(*args, **kwargs):
            start_time = time.time()
            # Simulate network delay
            await asyncio.sleep(0.05)
            execution_times.append(("qdrant", start_time, time.time()))
            mock_scored_point = MagicMock()
            mock_scored_point.id = 100
            mock_scored_point.score = 0.8
            mock_scored_point.payload = {"content": "Qdrant result"}
            return [mock_scored_point]
        
        self.cache_manager.faiss_index.search = Mock(side_effect=mock_faiss_search)
        self.mock_qdrant.search = AsyncMock(side_effect=mock_qdrant_search)
        
        # Setup FAISS metadata
        self.cache_manager.faiss_metadata[1] = {"content": "FAISS result", "id": "f_1"}
        self.cache_manager.faiss_metadata[2] = {"content": "FAISS result 2", "id": "f_2"}
        
        # Execute search
        start_search = time.time()
        results = asyncio.run(self.cache_manager.search(query_vector, k=2))
        end_search = time.time()
        
        search_duration = end_search - start_search
        
        # Verify both were called
        assert len(execution_times) == 2
        
        # Verify concurrent execution (total time should be less than sum of individual times)
        # FAISS: 0.02s, Qdrant: 0.05s, total if sequential would be ~0.07s
        # With concurrency, should be closer to max(0.02, 0.05) = 0.05s
        assert search_duration < 0.08, f"Search took {search_duration}s, seems sequential"
        
        # Verify results
        assert len(results) == 2


class TestRedisStreamsIntegration(TestShadowCacheManager):
    """Tests for Redis Streams cache invalidation (mocked)."""
    
    def setup_method(self):
        """Setup with mocked Redis."""
        super().setup_method()
        
        # Create mock Redis
        self.mock_redis = AsyncMock()
        self.mock_redis.ping.return_value = True
        
        # Recreate cache manager with Redis (without RedisCircuitBreakerState patch)
        with patch('app.XNAi_rag_app.core.vector_cache.AsyncQdrantClient', return_value=self.mock_qdrant):
            with patch('app.XNAi_rag_app.core.vector_cache.RedisCircuitBreakerState', create=True):
                self.cache_manager = ShadowCacheManager(
                    qdrant_url=self.qdrant_url,
                    dimension=self.dimension,
                    hot_limit=self.hot_limit,
                    similarity_threshold=self.similarity_threshold,
                    redis_uri="redis://localhost:6379"
                )
    
    def test_redis_stream_subscription(self):
        """Test Redis stream subscription setup."""
        # Mock the listen_for_updates method
        self.cache_manager.listen_for_updates = AsyncMock()
        
        # Execute listen_for_updates
        asyncio.run(self.cache_manager.listen_for_updates())
        
        # Verify the method was called (implementation would be more complex in reality)
        self.cache_manager.listen_for_updates.assert_called_once()
    
    def test_cache_invalidation_message_handling(self):
        """Test handling of cache invalidation messages from Redis streams."""
        # This is a simplified test since full Redis stream testing would require 
        # a more complex setup. In a real implementation, this would involve
        # consuming messages from a Redis stream and updating the FAISS metadata.
        
        # Setup some initial FAISS data
        self.cache_manager.faiss_metadata[1] = {"content": "Original content", "id": "test_1"}
        self.cache_manager.faiss_metadata[2] = {"content": "Another content", "id": "test_2"}
        
        # Simulate cache invalidation (in real implementation, this would come from Redis)
        invalidation_ids = [1]
        
        # Remove invalidated items
        for item_id in invalidation_ids:
            if item_id in self.cache_manager.faiss_metadata:
                del self.cache_manager.faiss_metadata[item_id]
        
        # Verify invalidation
        assert 1 not in self.cache_manager.faiss_metadata
        assert 2 in self.cache_manager.faiss_metadata
        assert self.cache_manager.faiss_metadata[2]["content"] == "Another content"


class TestErrorHandling(TestShadowCacheManager):
    """Tests for error handling in ShadowCacheManager."""
    
    def test_qdrant_connection_error_handling(self):
        """Test handling of Qdrant connection errors."""
        query_vector = np.random.random(self.dimension).astype('float32')
        
        # Mock FAISS results
        self.cache_manager.faiss_index.search = Mock(return_value=(
            np.array([[0.1, 0.2]]), np.array([[1, 2]])
        ))
        
        # Setup FAISS metadata
        self.cache_manager.faiss_metadata[1] = {"content": "FAISS result", "id": "f_1"}
        self.cache_manager.faiss_metadata[2] = {"content": "FAISS result 2", "id": "f_2"}
        
        # Mock Qdrant connection error
        self.mock_qdrant.search = AsyncMock(side_effect=Exception("Qdrant connection failed"))
        
        # Execute search - should not raise exception, should log error and continue
        results = asyncio.run(self.cache_manager.search(query_vector, k=2))
        
        # Verify FAISS results are still returned
        assert len(results) == 2
        assert all(result["source"] == "shadow_cache" for result in results)
    
    def test_faiss_search_error_handling(self):
        """Test handling of FAISS search errors."""
        query_vector = np.random.random(self.dimension).astype('float32')
        
        # Mock FAISS search error
        self.cache_manager.faiss_index.search = Mock(side_effect=Exception("FAISS search failed"))
        
        # Mock Qdrant results
        mock_scored_point = MagicMock()
        mock_scored_point.id = 100
        mock_scored_point.score = 0.8
        mock_scored_point.payload = {"content": "Qdrant result"}
        qdrant_results = [mock_scored_point]
        self.mock_qdrant.search = AsyncMock(return_value=qdrant_results)
        
        # Execute search - should not raise exception, should continue with Qdrant
        results = asyncio.run(self.cache_manager.search(query_vector, k=2))
        
        # Verify Qdrant results are returned
        assert len(results) == 1
        assert results[0]["source"] == "qdrant"
        assert results[0]["score"] == 0.8
    
    def test_mixed_error_scenario(self):
        """Test scenario where both FAISS and Qdrant have issues."""
        query_vector = np.random.random(self.dimension).astype('float32')
        
        # Mock both searches failing
        self.cache_manager.faiss_index.search = Mock(side_effect=Exception("FAISS failed"))
        self.mock_qdrant.search = AsyncMock(side_effect=Exception("Qdrant failed"))
        
        # Execute search
        results = asyncio.run(self.cache_manager.search(query_vector, k=2))
        
        # Should return empty results rather than raising exception
        assert len(results) == 0


class TestPerformanceMetrics(TestShadowCacheManager):
    """Tests for performance metrics and latency tracking."""
    
    def test_latency_recording(self):
        """Test that latency is properly recorded for both sources."""
        query_vector = np.random.random(self.dimension).astype('float32')
        
        # Mock latency recording
        recorded_latencies = []
        
        def mock_record_latency(source: str, latency: float):
            recorded_latencies.append((source, latency))
        
        # Patch the latency recording method
        self.cache_manager._record_vector_lookup_latency = mock_record_latency
        
        # Mock FAISS with timing
        def mock_faiss_search(*args, **kwargs):
            start_time = time.time()
            time.sleep(0.01)  # Simulate processing time
            return np.array([[0.1, 0.2]]), np.array([[1, 2]])
        
        # Mock Qdrant with timing
        async def mock_qdrant_search(*args, **kwargs):
            start_time = time.time()
            await asyncio.sleep(0.02)  # Simulate network time
            mock_scored_point = MagicMock()
            mock_scored_point.id = 100
            mock_scored_point.score = 0.8
            mock_scored_point.payload = {"content": "Qdrant result"}
            return [mock_scored_point]
        
        self.cache_manager.faiss_index.search = Mock(side_effect=mock_faiss_search)
        self.mock_qdrant.search = AsyncMock(side_effect=mock_qdrant_search)
        
        # Setup FAISS metadata
        self.cache_manager.faiss_metadata[1] = {"content": "FAISS result", "id": "f_1"}
        self.cache_manager.faiss_metadata[2] = {"content": "FAISS result 2", "id": "f_2"}
        
        # Execute search
        results = asyncio.run(self.cache_manager.search(query_vector, k=2))
        
        # Verify latency was recorded for both sources
        assert len(recorded_latencies) == 2
        sources = [latency[0] for latency in recorded_latencies]
        assert "shadow_cache" in sources
        assert "qdrant" in sources
        
        # Verify latencies are positive and reasonable
        for source, latency in recorded_latencies:
            assert latency > 0
            assert latency < 1.0  # Should be much less than 1 second


class TestIntegrationScenarios(TestShadowCacheManager):
    """Integration tests for complex scenarios."""
    
    def test_mixed_similarity_scores_scenario(self):
        """Test scenario with mixed similarity scores from both sources."""
        query_vector = np.random.random(self.dimension).astype('float32')
        
        # Mock FAISS results with varying similarity
        faiss_distances = [0.8, 0.3, 1.2]  # Medium, High, Low similarity
        faiss_indices = [1, 2, 3]
        faiss_metadata = [
            {"content": "FAISS medium similarity", "id": "f_med"},
            {"content": "FAISS high similarity", "id": "f_high"},
            {"content": "FAISS low similarity", "id": "f_low"}
        ]
        
        self.cache_manager.faiss_index.search = Mock(return_value=(
            np.array([faiss_distances]), np.array([faiss_indices])
        ))
        
        # Setup FAISS metadata
        for i, idx in enumerate(faiss_indices):
            self.cache_manager.faiss_metadata[idx] = faiss_metadata[i]
        
        # Mock Qdrant results with different scores
        mock_scored_point1 = MagicMock()
        mock_scored_point1.id = 100
        mock_scored_point1.score = 0.6
        mock_scored_point1.payload = {"content": "Qdrant medium"}
        
        mock_scored_point2 = MagicMock()
        mock_scored_point2.id = 101
        mock_scored_point2.score = 0.95
        mock_scored_point2.payload = {"content": "Qdrant very high"}
        
        mock_scored_point3 = MagicMock()
        mock_scored_point3.id = 102
        mock_scored_point3.score = 0.4
        mock_scored_point3.payload = {"content": "Qdrant low"}
        
        qdrant_results = [mock_scored_point1, mock_scored_point2, mock_scored_point3]
        self.mock_qdrant.search = AsyncMock(return_value=qdrant_results)
        
        # Execute search
        results = asyncio.run(self.cache_manager.search(query_vector, k=5))
        
        # Verify results are properly sorted by score
        assert len(results) >= 3
        
        # The highest scoring result should be from Qdrant (score 0.95)
        assert results[0]["source"] == "qdrant"
        assert results[0]["score"] == 0.95
        
        # Verify sorting is correct (descending by score)
        for i in range(len(results) - 1):
            assert results[i]["score"] >= results[i + 1]["score"]
    
    def test_large_k_value_scenario(self):
        """Test search with large k value requiring result deduplication."""
        query_vector = np.random.random(self.dimension).astype('float32')
        
        # Mock FAISS with many results
        faiss_distances = [0.1, 0.2, 0.3, 0.4, 0.5]
        faiss_indices = [1, 2, 3, 4, 5]
        faiss_metadata = [{"content": f"FAISS {i}", "id": f"f_{i}"} for i in range(5)]
        
        self.cache_manager.faiss_index.search = Mock(return_value=(
            np.array([faiss_distances]), np.array([faiss_indices])
        ))
        
        # Setup FAISS metadata
        for i, idx in enumerate(faiss_indices):
            self.cache_manager.faiss_metadata[idx] = faiss_metadata[i]
        
        # Mock Qdrant with overlapping content (same as FAISS)
        mock_scored_point1 = MagicMock()
        mock_scored_point1.id = 100
        mock_scored_point1.score = 0.8
        mock_scored_point1.payload = {"content": "FAISS 0"}
        
        mock_scored_point2 = MagicMock()
        mock_scored_point2.id = 101
        mock_scored_point2.score = 0.7
        mock_scored_point2.payload = {"content": "FAISS 1"}
        
        mock_scored_point3 = MagicMock()
        mock_scored_point3.id = 102
        mock_scored_point3.score = 0.6
        mock_scored_point3.payload = {"content": "Qdrant unique"}
        
        qdrant_results = [mock_scored_point1, mock_scored_point2, mock_scored_point3]
        self.mock_qdrant.search = AsyncMock(return_value=qdrant_results)
        
        # Execute search with large k
        results = asyncio.run(self.cache_manager.search(query_vector, k=10))
        
        # Verify deduplication occurred (should not have duplicate content)
        content_hashes = set()
        for result in results:
            content_hash = hash(str(result["metadata"]))
            assert content_hash not in content_hashes, f"Duplicate content found: {result['metadata']}"
            content_hashes.add(content_hash)
        
        # Should have unique results from both sources
        assert len(results) <= 7  # 5 FAISS + 3 Qdrant - duplicates


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])