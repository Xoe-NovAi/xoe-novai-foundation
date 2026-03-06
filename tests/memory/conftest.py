"""
Memory Bank Test Fixtures
=========================

Pytest fixtures for memory bank testing.
"""

import os
import sys
import pytest
from pathlib import Path

# Add app to path
app_path = Path(__file__).parent.parent.parent / "app"
sys.path.insert(0, str(app_path))


@pytest.fixture
def memory_bank_path(tmp_path: Path) -> Path:
    """Create a temporary memory bank for testing."""
    mb_path = tmp_path / "memory_bank"
    mb_path.mkdir()

    # Create BLOCKS.yaml
    blocks_yaml = """
metadata:
  version: "1.0.0"
  
core_blocks:
  test_block:
    label: "test_block"
    file: "test_block.md"
    description: "Test block for testing"
    limit_chars: 1000
    limit_tokens: 250
    read_only: false
    tier: core
    priority: 1
"""
    (mb_path / "BLOCKS.yaml").write_text(blocks_yaml)

    # Create test block file
    test_block = """---
block:
  label: test_block
  description: Test block
---

# Test Block

This is test content for testing memory tools.
"""
    (mb_path / "test_block.md").write_text(test_block)

    return mb_path


@pytest.fixture
def block_manager(memory_bank_path: Path):
    """Create a BlockManager with test memory bank."""
    from XNAi_rag_app.core.memory.block_manager import BlockManager

    return BlockManager(str(memory_bank_path))


@pytest.fixture
def sample_content() -> str:
    """Sample content for testing."""
    return """---
block:
  label: sample
  description: Sample block
---

# Sample Content

This is sample content with:
- Item 1
- Item 2
- Item 3

## Section

More content here.
"""
