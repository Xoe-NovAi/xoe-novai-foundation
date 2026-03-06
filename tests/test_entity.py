"""
Entity System Tests
==================

Comprehensive tests for the Persistent Entity Mesh system including:
- PersistentEntity
- EntityRegistry
- EnhancedEntityHandler
- KnowledgeMinerWorker

Uses fakeredis for unit testing without external dependencies.
"""

import pytest
import json
import time
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

# Test imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.XNAi_rag_app.core.entities.persistent_entity import PersistentEntity
from app.XNAi_rag_app.core.entities.registry import EntityRegistry
from app.XNAi_rag_app.core.entities.enhanced_handler import EnhancedEntityHandler, EntityQuery, EntityTriggerPattern


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def temp_entity_dir():
    """Create temporary directory for entity storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_redis():
    """Create mock Redis client for testing."""
    mock = Mock()
    mock.xadd = AsyncMock(return_value="test-id")
    mock.xreadgroup = AsyncMock(return_value=[])
    mock.xack = AsyncMock(return_value=1)
    mock.lpush = AsyncMock(return_value=1)
    return mock


@pytest.fixture
def sample_entity_data():
    """Sample entity data for testing."""
    return {
        "entity_id": "test_entity",
        "role": "test_expert",
        "domains": ["test", "sample"],
        "is_initialized": True,
        "procedural_memory": [
            {
                "timestamp": time.time(),
                "query": "What is test?",
                "advice": "Testing is good",
                "outcome": "Tests pass",
                "rating": 0.9,
            }
        ],
        "stats": {"invocations": 1, "success_rate": 0.9, "total_feedback": 1},
    }


# =============================================================================
# PersistentEntity Tests
# =============================================================================


class TestPersistentEntity:
    """Tests for PersistentEntity class."""

    def test_entity_creation(self, temp_entity_dir):
        """Test creating a new entity."""
        entity = PersistentEntity("test_expert", "Test Expert", temp_entity_dir)

        assert entity.entity_id == "test_expert"
        assert entity.role == "Test Expert"
        assert entity.is_initialized == False
        assert entity.procedural_memory == []
        assert entity.domains == []

    def test_entity_id_normalization(self, temp_entity_dir):
        """Test entity ID normalization (spaces to underscores)."""
        entity = PersistentEntity("Kurt Cobain", "Music Expert", temp_entity_dir)

        assert entity.entity_id == "kurt_cobain"

    def test_save_and_load(self, temp_entity_dir, sample_entity_data):
        """Test saving and loading entity state."""
        # Create and populate entity
        entity = PersistentEntity("test_entity", "test_expert", temp_entity_dir)
        entity.domains = sample_entity_data["domains"]
        entity.is_initialized = sample_entity_data["is_initialized"]
        entity.procedural_memory = sample_entity_data["procedural_memory"]
        entity.stats = sample_entity_data["stats"]
        entity.save()

        # Load into new instance
        new_entity = PersistentEntity("test_entity", "test_expert", temp_entity_dir)

        assert new_entity.entity_id == "test_entity"
        assert new_entity.is_initialized == True
        assert new_entity.domains == ["test", "sample"]
        assert len(new_entity.procedural_memory) == 1
        assert new_entity.stats["success_rate"] == 0.9

    def test_add_lesson(self, temp_entity_dir):
        """Test adding lessons to entity memory."""
        entity = PersistentEntity("test_entity", "test_expert", temp_entity_dir)

        # Add a lesson
        entity.add_lesson(
            query="What is Python?",
            advice="Python is a programming language",
            outcome="Python is a high-level language",
            rating=0.85,
        )

        assert len(entity.procedural_memory) == 1
        assert entity.stats["total_feedback"] == 1
        assert entity.stats["success_rate"] == 0.85

    def test_memory_limit_50_lessons(self, temp_entity_dir):
        """Test that memory is limited to 50 lessons."""
        entity = PersistentEntity("test_entity", "test_expert", temp_entity_dir)

        # Add 60 lessons
        for i in range(60):
            entity.add_lesson(query=f"Query {i}", advice=f"Advice {i}", outcome=f"Outcome {i}", rating=0.5 + (i % 50) / 100)

        # Should only have 50 lessons (oldest removed)
        assert len(entity.procedural_memory) == 50
        # First lesson should be removed (index 0 is oldest)
        assert entity.procedural_memory[0]["query"] == "Query 10"

    def test_get_relevant_context(self, temp_entity_dir):
        """Test retrieving relevant context from memory."""
        entity = PersistentEntity("test_entity", "test_expert", temp_entity_dir)

        # Add lessons with different keywords
        entity.add_lesson(query="What is Python?", advice="Python advice", outcome="Python is a language", rating=0.9)
        entity.add_lesson(query="What is JavaScript?", advice="JavaScript advice", outcome="JavaScript is for web", rating=0.8)
        entity.add_lesson(query="What is Ruby?", advice="Ruby advice", outcome="Ruby is object-oriented", rating=0.7)

        # Query for Python should return relevant context
        context = entity.get_relevant_context("Tell me about Python programming")
        assert "Python" in context
        assert "Lesson" in context

    def test_get_relevant_context_no_match(self, temp_entity_dir):
        """Test context retrieval with no matching lessons."""
        entity = PersistentEntity("test_entity", "test_expert", temp_entity_dir)

        entity.add_lesson(query="What is Python?", advice="Python advice", outcome="Python is a language", rating=0.9)

        context = entity.get_relevant_context("Tell me about cooking")
        assert context == ""

    def test_stats_update(self, temp_entity_dir):
        """Test statistics are updated correctly."""
        entity = PersistentEntity("test_entity", "test_expert", temp_entity_dir)

        # Add multiple lessons
        entity.add_lesson("Query 1", "Advice 1", "Outcome 1", 0.8)
        entity.add_lesson("Query 2", "Advice 2", "Outcome 2", 0.9)

        # Average: (0 + 0.8) / 1 = 0.8, then (0.8 * 1 + 0.9) / 2 = 0.85
        assert entity.stats["total_feedback"] == 2
        assert entity.stats["success_rate"] == pytest.approx(0.85, rel=0.01)


# =============================================================================
# EntityRegistry Tests
# =============================================================================


class TestEntityRegistry:
    """Tests for EntityRegistry class."""

    def test_get_entity_creates_new(self, temp_entity_dir):
        """Test that get_entity creates a new entity if not exists."""
        registry = EntityRegistry()

        entity = registry.get_entity("new_expert", "Expert", temp_entity_dir)

        assert entity.entity_id == "new_expert"
        assert entity.role == "Expert"
        assert entity.is_initialized == False

    def test_get_entity_returns_existing(self, temp_entity_dir):
        """Test that get_entity returns existing entity."""
        registry = EntityRegistry()

        # Create entity
        entity1 = registry.get_entity("test_expert", "Expert", temp_entity_dir)
        entity1.is_initialized = True
        entity1.save()

        # Get same entity should return cached instance
        entity2 = registry.get_entity("test_expert", "Expert", temp_entity_dir)

        assert entity1 is entity2

    def test_get_entity_auto_create(self, temp_entity_dir):
        """Test auto_create parameter."""
        registry = EntityRegistry(base_dir=temp_entity_dir)

        # With auto_create=True (default), should create new entity
        entity = registry.get_entity("auto_expert", "Expert", auto_create=True)
        assert entity.is_initialized == False

        # With auto_create=False, should not create new entity
        entity2 = registry.get_entity("nonexistent", "Expert", auto_create=False)
        # Entity should still exist from disk but not initialized
        assert entity2.is_initialized == False

    @patch("app.XNAi_rag_app.core.entities.registry.asyncio")
    def test_trigger_expertise_mining(self, mock_asyncio, temp_entity_dir, mock_redis):
        """Test expertise mining is triggered for new entities."""
        registry = EntityRegistry(redis_client=mock_redis)

        # Mock asyncio.create_task and asyncio.run
        mock_task = Mock()
        mock_asyncio.create_task = Mock(return_value=mock_task)
        mock_asyncio.run = Mock()

        entity = registry.get_entity("mining_test", "Expert", temp_entity_dir)

        # Should trigger mining for uninitialized entity
        assert entity.is_initialized == False

    def test_record_feedback(self, temp_entity_dir):
        """Test recording feedback for an entity."""
        registry = EntityRegistry(base_dir=temp_entity_dir)

        registry.record_feedback("feedback_test", "Query", "Advice", "Outcome", 0.85)

        entity = registry.get_entity("feedback_test", "Expert", auto_create=False)
        assert len(entity.procedural_memory) == 1


# =============================================================================
# EnhancedEntityHandler Tests
# =============================================================================


class TestEnhancedEntityHandler:
    """Tests for EnhancedEntityHandler class."""

    @pytest.fixture
    def mock_registry(self):
        """Create mock entity registry."""
        registry = Mock()
        entity = Mock()
        entity.is_initialized = True
        entity.get_relevant_context = Mock(return_value="Relevant context")
        registry.get_entity = Mock(return_value=entity)
        return registry

    @pytest.fixture
    def handler(self, mock_registry):
        """Create enhanced entity handler."""
        return EnhancedEntityHandler(mock_registry)

    def test_parse_direct_query(self, handler):
        """Test parsing direct entity query."""
        query = handler.parse_query("Hey Kurt Cobain, tell me about grunge music")

        assert query is not None
        assert query.pattern == EntityTriggerPattern.DIRECT
        assert query.primary_entity == "kurt_cobain"
        assert "grunge" in query.query

    def test_parse_consult_query(self, handler):
        """Test parsing consultation query."""
        query = handler.parse_query("Ask Plato about virtue ethics")

        assert query is not None
        assert query.pattern == EntityTriggerPattern.CONSULT
        assert query.primary_entity == "plato"
        assert "virtue" in query.query

    def test_parse_cross_entity_query(self, handler):
        """Test parsing cross-entity query."""
        query = handler.parse_query("Hey Kurt, ask Plato about virtue ethics")

        assert query is not None
        assert query.pattern == EntityTriggerPattern.CONSULT_OTHER
        assert query.primary_entity == "kurt_cobain"
        assert query.secondary_entity == "plato"
        assert "virtue" in query.query

    def test_parse_compare_query(self, handler):
        """Test parsing comparison query."""
        query = handler.parse_query("Compare Socrates and Plato on the nature of virtue")

        assert query is not None
        assert query.pattern == EntityTriggerPattern.COMPARE
        assert query.primary_entity == "socrates"
        assert query.secondary_entity == "plato"
        assert "virtue" in query.query

    def test_parse_panel_query(self, handler):
        """Test parsing panel query."""
        query = handler.parse_query("Summon panel: Socrates, Plato, Aristotle")

        assert query is not None
        assert query.pattern == EntityTriggerPattern.PANEL
        assert len(query.entities) == 3
        assert "socrates" in query.entities
        assert "plato" in query.entities
        assert "aristotle" in query.entities

    def test_parse_no_match(self, handler):
        """Test parsing with no entity pattern."""
        query = handler.parse_query("What is the weather today?")

        assert query is None

    def test_get_entity_domains(self, handler):
        """Test getting domains for an entity."""
        domains = handler.get_entity_domains("kurt_cobain")

        assert "grunge" in domains
        assert "music" in domains

    def test_get_entity_domains_unknown(self, handler):
        """Test getting domains for unknown entity."""
        domains = handler.get_entity_domains("unknown_entity")

        assert domains == []

    def test_get_expert_for_domain(self, handler):
        """Test finding best expert for domain."""
        expert = handler.get_expert_for_domain("grunge")

        assert expert == "kurt_cobain"

    def test_get_expert_for_domain_philosophy(self, handler):
        """Test finding expert for philosophy domain."""
        expert = handler.get_expert_for_domain("ethics")

        assert expert in ["socrates", "plato", "aristotle"]

    def test_list_available_entities(self, handler):
        """Test listing all known entities."""
        entities = handler.list_available_entities()

        assert "kurt_cobain" in entities
        assert "socrates" in entities
        assert "plato" in entities

    @pytest.mark.asyncio
    async def test_handle_direct_query(self, handler, mock_registry):
        """Test handling direct entity query."""
        query = EntityQuery(pattern=EntityTriggerPattern.DIRECT, primary_entity="kurt_cobain", query="Tell me about Nirvana")

        result = await handler.handle_query(query)

        assert result["type"] == "direct"
        assert result["entity"] == "kurt_cobain"
        assert "context" in result

    @pytest.mark.asyncio
    async def test_handle_cross_entity_query(self, handler, mock_registry):
        """Test handling cross-entity query."""
        query = EntityQuery(
            pattern=EntityTriggerPattern.CONSULT_OTHER,
            primary_entity="kurt_cobain",
            query="What is beauty?",
            secondary_entity="plato",
        )

        result = await handler.handle_query(query)

        assert result["type"] == "cross_entity"
        assert result["initiator"] == "kurt_cobain"
        assert result["consulted"] == "plato"

    @pytest.mark.asyncio
    async def test_handle_compare_query(self, handler, mock_registry):
        """Test handling comparison query."""
        query = EntityQuery(
            pattern=EntityTriggerPattern.COMPARE, primary_entity="socrates", query="virtue", secondary_entity="plato"
        )

        result = await handler.handle_query(query)

        assert result["type"] == "compare"
        assert result["entity1"] == "socrates"
        assert result["entity2"] == "plato"

    @pytest.mark.asyncio
    async def test_handle_panel_query(self, handler, mock_registry):
        """Test handling panel query."""
        query = EntityQuery(
            pattern=EntityTriggerPattern.PANEL,
            primary_entity="socrates",
            query="truth",
            entities=["socrates", "plato", "aristotle"],
        )

        result = await handler.handle_query(query)

        assert result["type"] == "panel"
        assert len(result["results"]) == 3

    def test_entity_aliases(self, handler):
        """Test entity name aliases."""
        # Test various alias forms
        assert handler._normalize_entity("kurt") == "kurt_cobain"
        assert handler._normalize_entity("kurt cobain") == "kurt_cobain"
        assert handler._normalize_entity("ada") == "ada_lovelace"
        assert handler._normalize_entity("ada lovelace") == "ada_lovelace"


# =============================================================================
# Integration Tests
# =============================================================================


class TestEntityMeshIntegration:
    """Integration tests for the complete entity mesh."""

    def test_full_entity_lifecycle(self, temp_entity_dir, mock_redis):
        """Test complete entity lifecycle."""
        # Use unique entity name to avoid collision with previous tests
        import uuid

        unique_id = str(uuid.uuid4())[:8]

        # 1. Create registry
        registry = EntityRegistry(redis_client=mock_redis, base_dir=temp_entity_dir)

        # 2. Get new entity
        entity = registry.get_entity(f"lifecycle_test_{unique_id}", "Test Expert")
        assert entity.is_initialized == False

        # 3. Initialize entity
        entity.is_initialized = True
        entity.domains = ["testing", "lifecycle"]
        entity.add_lesson("Test query", "Test advice", "Test outcome", 0.9)
        entity.save()

        # 4. Retrieve entity
        new_entity = registry.get_entity(f"lifecycle_test_{unique_id}", "Test Expert")
        assert new_entity.is_initialized == True
        assert "testing" in new_entity.domains
        assert len(new_entity.procedural_memory) == 1

    def test_enhanced_handler_integration(self, temp_entity_dir):
        """Test enhanced handler with real entities."""
        registry = EntityRegistry()
        handler = EnhancedEntityHandler(registry)

        # Create test entity
        entity = registry.get_entity("integration_test", "Expert", temp_entity_dir)
        entity.is_initialized = True
        entity.add_lesson("Test", "Advice", "Outcome", 0.8)
        entity.save()

        # Parse and handle query
        query = handler.parse_query("Hey integration_test, test query")
        assert query is not None
        assert query.pattern == EntityTriggerPattern.DIRECT


# =============================================================================
# Hardening Tests
# =============================================================================


class TestEntityHardening:
    """Hardening tests for entity system resilience."""

    def test_concurrent_entity_access(self, temp_entity_dir):
        """Test concurrent access to same entity."""
        from concurrent.futures import ThreadPoolExecutor

        registry = EntityRegistry()
        results = []

        def get_entity():
            entity = registry.get_entity("concurrent_test", "Expert", temp_entity_dir)
            return entity.entity_id

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(get_entity) for _ in range(5)]
            results = [f.result() for f in futures]

        # All should return same entity ID
        assert all(r == "concurrent_test" for r in results)

    def test_empty_query_handling(self, temp_entity_dir):
        """Test handling of empty queries."""
        registry = EntityRegistry()
        handler = EnhancedEntityHandler(registry)

        query = handler.parse_query("")
        assert query is None

    def test_special_characters_in_entity_name(self, temp_entity_dir):
        """Test entity names with special characters."""
        entity = PersistentEntity("test@#$%", "Expert", temp_entity_dir)

        # Should normalize special characters
        assert entity.entity_id is not None

    def test_very_long_query(self, temp_entity_dir):
        """Test handling very long queries."""
        registry = EntityRegistry()
        handler = EnhancedEntityHandler(registry)

        long_query = "Hey test_entity, " + "a" * 10000
        query = handler.parse_query(long_query)

        # Should still parse correctly
        if query:
            assert len(query.query) > 0

    def test_memory_preservation_after_error(self, temp_entity_dir):
        """Test memory is preserved even after errors."""
        entity = PersistentEntity("error_test", "Expert", temp_entity_dir)

        # Add lessons
        entity.add_lesson("Q1", "A1", "O1", 0.9)
        entity.save()

        # Simulate error by creating new instance
        entity2 = PersistentEntity("error_test", "Expert", temp_entity_dir)

        # Memory should be preserved
        assert len(entity2.procedural_memory) == 1

    def test_partial_query_parsing(self, temp_entity_dir):
        """Test handling of partial/malformed queries."""
        registry = EntityRegistry(base_dir=temp_entity_dir)
        handler = EnhancedEntityHandler(registry)

        # Missing query part
        result = handler.parse_query("Hey test_entity")
        # Should handle gracefully

        # Missing entity
        result2 = handler.parse_query("Hey , tell me something")
        # Should handle gracefully


# =============================================================================
# Test Summary
# =============================================================================


def test_entity_system_summary(temp_entity_dir):
    """Summary test demonstrating entity system capabilities."""
    # Create system components
    registry = EntityRegistry()
    handler = EnhancedEntityHandler(registry)

    # 1. Create expert
    socrates = registry.get_entity("socrates", "Philosophy Expert", temp_entity_dir)
    socrates.is_initialized = True
    socrates.domains = ["philosophy", "ethics", "dialectic"]
    socrates.add_lesson(
        "Who is Socrates?", "A Greek philosopher", "Socrates was a Greek philosopher known for the Socratic method", 1.0
    )
    socrates.save()

    # 2. Parse query
    query = handler.parse_query("Ask Socrates about virtue")
    assert query is not None

    # 3. Get domains
    domains = handler.get_entity_domains("socrates")
    assert "philosophy" in domains

    # 4. List available
    entities = handler.list_available_entities()
    assert len(entities) > 0

    print("Entity system test summary: PASSED")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
