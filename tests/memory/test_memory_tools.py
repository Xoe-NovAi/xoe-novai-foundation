"""
Memory Tools Tests
==================

Tests for memory_replace, memory_append, memory_rethink, compile_context.
"""

import pytest
from pathlib import Path


class TestMemoryTools:
    """Test memory tool operations."""

    @pytest.mark.asyncio
    async def test_memory_replace_surgical(self, block_manager):
        """Test surgical replacement in block content."""
        from XNAi_rag_app.core.memory.tools import memory_replace

        result = await memory_replace("test_block", "test content", "modified content")

        assert result["success"] is True
        assert result["chars_added"] == len("modified content")
        assert result["chars_removed"] == len("test content")

    @pytest.mark.asyncio
    async def test_memory_replace_not_found(self, block_manager):
        """Test replacement when old content not found."""
        from XNAi_rag_app.core.memory.tools import memory_replace

        result = await memory_replace("test_block", "nonexistent", "replacement")

        assert result["success"] is False
        assert "not found" in result["message"]

    @pytest.mark.asyncio
    async def test_memory_append_within_limit(self, block_manager):
        """Test append respects size limits."""
        from XNAi_rag_app.core.memory.tools import memory_append

        result = await memory_append("test_block", "Appended content.")

        assert result["success"] is True
        assert result["new_size"] > 0
        assert result["utilization"] < 1.0

    @pytest.mark.asyncio
    async def test_memory_append_exceeds_limit(self, block_manager):
        """Test append fails when exceeding limit."""
        from XNAi_rag_app.core.memory.tools import memory_append

        # Create content that exceeds the 1000 char limit
        large_content = "x" * 2000

        result = await memory_append("test_block", large_content)

        assert result["success"] is False
        assert "exceed" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_memory_rethink_preserves_frontmatter(self, block_manager):
        """Test rethink preserves YAML frontmatter."""
        from XNAi_rag_app.core.memory.tools import memory_rethink

        new_body = "# New Content\n\nThis is entirely new content."

        result = await memory_rethink("test_block", new_body)

        assert result["success"] is True

        # Verify frontmatter preserved
        content = await block_manager.read_block("test_block")
        assert content.startswith("---")

    @pytest.mark.asyncio
    async def test_compile_context_basic(self, block_manager):
        """Test basic context compilation."""
        from XNAi_rag_app.core.memory.tools import compile_context

        context = await compile_context(max_tokens=5000)

        assert "<memory_blocks>" in context
        assert "<block" in context

    @pytest.mark.asyncio
    async def test_compile_context_respects_token_budget(self, block_manager):
        """Test context compilation respects token budget."""
        from XNAi_rag_app.core.memory.tools import compile_context

        context = await compile_context(max_tokens=100)

        # Should be relatively short
        estimated_tokens = len(context) // 4
        assert estimated_tokens < 200  # Some overhead allowed


class TestBlockValidation:
    """Test block validation and size limits."""

    @pytest.mark.asyncio
    async def test_validate_block(self, block_manager):
        """Test block validation."""
        status = await block_manager.validate_block("test_block")

        assert status["valid"] is True
        assert status["chars"] > 0
        assert status["limit"] > 0
        assert 0 <= status["utilization"] <= 1

    @pytest.mark.asyncio
    async def test_validate_nonexistent_block(self, block_manager):
        """Test validation of nonexistent block."""
        status = await block_manager.validate_block("nonexistent")

        assert status["valid"] is False
        assert "error" in status

    @pytest.mark.asyncio
    async def test_get_all_block_status(self, block_manager):
        """Test getting all block status."""
        status = await block_manager.get_all_block_status()

        assert "blocks" in status
        assert "total_utilization" in status
        assert "warnings" in status


class TestBlockManager:
    """Test block manager operations."""

    def test_load_config(self, block_manager):
        """Test loading BLOCKS.yaml."""
        config = block_manager.load_config()

        assert "metadata" in config
        assert "core_blocks" in config

    def test_get_block_config(self, block_manager):
        """Test getting block configuration."""
        block_config = block_manager.get_block_config("test_block")

        assert block_config is not None
        assert block_config.get("label") == "test_block"

    def test_extract_frontmatter(self, block_manager, sample_content):
        """Test frontmatter extraction."""
        frontmatter, body = block_manager.extract_frontmatter(sample_content)

        assert "label: sample" in frontmatter
        assert "# Sample Content" in body

    def test_reconstruct_with_frontmatter(self, block_manager):
        """Test reconstruction with frontmatter."""
        frontmatter = "label: test\ndescription: Test"
        body = "# Content"

        result = block_manager.reconstruct_with_frontmatter(frontmatter, body)

        assert result.startswith("---")
        assert "---" in result
        assert "# Content" in result

    def test_reconstruct_without_frontmatter(self, block_manager):
        """Test reconstruction without frontmatter."""
        body = "# Content"

        result = block_manager.reconstruct_with_frontmatter("", body)

        assert result == "# Content"
