#!/usr/bin/env python3
"""
Tests for Memory Bank Fallback System
======================================

Comprehensive test suite for SQLite fallback and circuit breaker patterns.
Tests cover:
- Basic SQLite operations
- Circuit breaker state transitions
- Fallback activation and recovery
- Cache hit/miss patterns
- Full-text search functionality
"""

import pytest
import asyncio
from pathlib import Path
from datetime import datetime
import json
import tempfile
import shutil

# These would be imported from the actual modules
# from memory_bank_store import MemoryBankStore, ContextTier, ContextType
# from memory_bank_fallback import MemoryBankFallbackWrapper, FallbackCircuitBreaker

class TestMemoryBankStore:
    """Test SQLite store functionality."""

    @pytest.fixture
    async def store(self):
        """Create temporary store for testing."""
        tmpdir = tempfile.mkdtemp()
        db_path = Path(tmpdir) / "test.db"
        
        store = MemoryBankStore(db_path=db_path)
        await store.initialize()
        
        yield store
        
        await store.close()
        shutil.rmtree(tmpdir)

    @pytest.mark.asyncio
    async def test_initialize_creates_schema(self, store):
        """Test that initialize creates proper schema."""
        assert store._initialized
        assert store.db_path.exists()

    @pytest.mark.asyncio
    async def test_register_agent(self, store):
        """Test agent registration."""
        result = await store.register_agent(
            "test_agent_1",
            ["capability_a", "capability_b"],
            memory_limit_gb=4.0
        )
        
        assert result["status"] == "success"
        assert result["agent_id"] == "test_agent_1"
        assert store.metrics["agent_registrations"] == 1

    @pytest.mark.asyncio
    async def test_set_and_get_context_hot(self, store):
        """Test storing and retrieving hot tier context."""
        await store.register_agent("agent1", ["test"], 1.0)
        
        context = {
            "project_name": "XNAi Foundation",
            "version": "1.0.0"
        }
        
        # Set context
        set_result = await store.set_context(
            "agent1",
            "project",
            "hot",
            context
        )
        
        assert set_result["status"] == "success"
        assert set_result["version"] == 1
        assert store.metrics["context_writes"] == 1

        # Get context
        get_result = await store.get_context("agent1", "project", "hot")
        
        assert get_result["status"] == "success"
        assert get_result["content"] == context
        assert get_result["source"] == "hot_cache" or get_result["source"] == "database"
        assert store.metrics["context_reads"] == 1

    @pytest.mark.asyncio
    async def test_cache_hit_rate(self, store):
        """Test that cache hits are tracked correctly."""
        await store.register_agent("agent2", ["test"], 1.0)
        
        context = {"test": "data"}
        
        # Initial store and read
        await store.set_context("agent2", "technical", "hot", context)
        
        # First read (from hot cache)
        result1 = await store.get_context("agent2", "technical", "hot")
        assert result1["status"] == "success"
        
        # Second read (should be cache hit)
        result2 = await store.get_context("agent2", "technical", "hot")
        assert result2["status"] == "success"
        
        # Check metrics
        assert store.metrics["cache_hits"] >= 1

    @pytest.mark.asyncio
    async def test_full_text_search(self, store):
        """Test FTS functionality."""
        await store.register_agent("agent3", ["test"], 1.0)
        
        # Store multiple contexts with different content
        await store.set_context("agent3", "project", "warm", {
            "name": "Project Alpha",
            "description": "A foundational system for autonomous agents"
        })
        
        await store.set_context("agent3", "technical", "warm", {
            "stack": "Python AsyncIO",
            "framework": "MCP and XNAI Foundation"
        })
        
        # Search
        search_result = await store.search_context(
            "autonomous agents",
            agent_id="agent3"
        )
        
        assert search_result["status"] == "success"
        assert len(search_result["results"]) >= 1
        assert store.metrics["fts_searches"] == 1

    @pytest.mark.asyncio
    async def test_context_versioning(self, store):
        """Test version tracking for contexts."""
        await store.register_agent("agent4", ["test"], 1.0)
        
        context_v1 = {"version": 1, "data": "first"}
        context_v2 = {"version": 2, "data": "second"}
        
        # Store v1
        await store.set_context("agent4", "project", "warm", context_v1, version=1)
        
        # Store v2 of same context
        await store.set_context("agent4", "project", "warm", context_v2, version=2)
        
        # Retrieve - should get latest
        result = await store.get_context("agent4", "project", "warm")
        
        assert result["version"] == 2
        assert result["content"]["version"] == 2

    @pytest.mark.asyncio
    async def test_access_logging(self, store):
        """Test that access is logged."""
        await store.register_agent("agent5", ["test"], 1.0)
        
        context = {"test": "data"}
        await store.set_context("agent5", "operational", "hot", context)
        
        # Multiple reads
        for _ in range(3):
            await store.get_context("agent5", "operational", "hot")
        
        # Verify metrics track reads
        assert store.metrics["context_reads"] >= 3

class TestFallbackCircuitBreaker:
    """Test circuit breaker state transitions."""

    def test_circuit_starts_closed(self):
        """Test that circuit starts in closed state."""
        breaker = FallbackCircuitBreaker()
        assert breaker.state == "closed"
        assert breaker.check_can_attempt() is True

    def test_circuit_opens_after_failures(self):
        """Test that circuit opens after threshold failures."""
        breaker = FallbackCircuitBreaker(failure_threshold=3)
        
        # Record failures
        for _ in range(3):
            breaker.record_failure()
        
        assert breaker.state == "open"
        assert breaker.check_can_attempt() is False

    def test_circuit_enters_half_open_after_timeout(self):
        """Test half-open state after recovery timeout."""
        breaker = FallbackCircuitBreaker(
            failure_threshold=2,
            recovery_timeout=1  # 1 second for testing
        )
        
        # Open circuit
        for _ in range(2):
            breaker.record_failure()
        assert breaker.state == "open"
        
        # Wait for recovery timeout
        import time
        time.sleep(1.1)
        
        # Should attempt to recover
        assert breaker.check_can_attempt() is True
        assert breaker.state == "half_open"

    def test_circuit_closes_on_success(self):
        """Test that circuit closes on successful call."""
        breaker = FallbackCircuitBreaker(failure_threshold=1)
        
        # Trigger open state
        breaker.record_failure()
        assert breaker.state == "open"
        
        # Wait for recovery
        import time
        time.sleep(1.1)
        
        breaker.check_can_attempt()
        assert breaker.state == "half_open"
        
        # Record success
        breaker.record_success()
        assert breaker.state == "closed"

class TestMemoryBankFallbackWrapper:
    """Test fallback wrapper integration."""

    @pytest.fixture
    async def wrapper(self):
        """Create wrapper with temporary store."""
        tmpdir = tempfile.mkdtemp()
        db_path = Path(tmpdir) / "test.db"
        
        fallback_store = MemoryBankStore(db_path=db_path)
        wrapper = MemoryBankFallbackWrapper(fallback_store=fallback_store)
        
        await wrapper.initialize()
        
        yield wrapper
        
        await wrapper.close()
        shutil.rmtree(tmpdir)

    @pytest.mark.asyncio
    async def test_fallback_wrapper_initializes(self, wrapper):
        """Test that wrapper initializes successfully."""
        assert wrapper.fallback_store._initialized
        assert wrapper.circuit_breaker.state == "closed"

    @pytest.mark.asyncio
    async def test_register_agent_with_fallback(self, wrapper):
        """Test agent registration through wrapper."""
        result = await wrapper.register_agent(
            "test_agent",
            ["capability1"],
            memory_limit_gb=2.0
        )
        
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_context_storage_with_fallback(self, wrapper):
        """Test context storage through fallback wrapper."""
        await wrapper.register_agent("agent1", ["test"], 1.0)
        
        context = {"data": "test_content"}
        
        # Set context
        set_result = await wrapper.set_context(
            "agent1",
            "project",
            "hot",
            context
        )
        
        assert set_result["status"] == "success"
        
        # Get context
        get_result = await wrapper.get_context("agent1", "project", "hot")
        
        assert get_result["status"] == "success"
        assert get_result["content"] == context

    @pytest.mark.asyncio
    async def test_get_fallback_status(self, wrapper):
        """Test fallback status reporting."""
        status = await wrapper.get_fallback_status()
        
        assert "timestamp" in status
        assert "fallback_mode_active" in status
        assert "circuit_breaker_state" in status
        assert status["circuit_breaker_state"] == "closed"

class TestIntegrationScenarios:
    """Test realistic integration scenarios."""

    @pytest.mark.asyncio
    async def test_scenario_primary_failure_fallback_recovery(self):
        """Test full scenario: primary fails, fallback takes over, primary recovers."""
        # This would test a real scenario with mock MCP server
        pass

    @pytest.mark.asyncio
    async def test_scenario_cache_coherence(self):
        """Test that cache stays coherent across tiers."""
        # Verify that hot cache, warm, and cold tiers are consistent
        pass

    @pytest.mark.asyncio
    async def test_scenario_concurrent_access(self):
        """Test concurrent access patterns."""
        # Test multiple agents accessing contexts simultaneously
        pass

if __name__ == "__main__":
    # Run tests with: pytest test_memory_bank_fallback.py -v
    pytest.main([__file__, "-v", "-s"])
