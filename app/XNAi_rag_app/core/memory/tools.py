"""
Memory Tools
============

Core memory operations: replace, append, rethink, compile_context.
Implements MemGPT-style memory management for XNAi Foundation.
"""

from typing import Optional
from .block_manager import BlockManager

# Global block manager instance
_manager: Optional[BlockManager] = None


def get_manager() -> BlockManager:
    """Get or create the block manager instance."""
    global _manager
    if _manager is None:
        _manager = BlockManager()
    return _manager


async def memory_replace(block_label: str, old_content: str, new_content: str) -> dict:
    """
    Surgical edit within a memory block.

    Args:
        block_label: The block label (e.g., "active_context", "progress")
        old_content: Text to find and replace
        new_content: Replacement text

    Returns:
        {"success": bool, "chars_added": int, "chars_removed": int, "message": str}
    """
    manager = get_manager()

    try:
        content = await manager.read_block(block_label)

        if old_content not in content:
            return {
                "success": False,
                "chars_added": 0,
                "chars_removed": 0,
                "message": f"Old content not found in block '{block_label}'",
            }

        new_body = content.replace(old_content, new_content, 1)
        chars_added = len(new_content)
        chars_removed = len(old_content)

        # Validate size limit
        status = await manager.validate_block(block_label)
        if status and len(new_body) > status.get("limit", 10000):
            return {
                "success": False,
                "chars_added": 0,
                "chars_removed": 0,
                "message": f"Result would exceed block limit ({status['limit']} chars)",
            }

        await manager.write_block(block_label, new_body)

        return {
            "success": True,
            "chars_added": chars_added,
            "chars_removed": chars_removed,
            "message": f"Replaced {chars_removed} chars with {chars_added} chars in '{block_label}'",
        }

    except Exception as e:
        return {
            "success": False,
            "chars_added": 0,
            "chars_removed": 0,
            "message": str(e),
        }


async def memory_append(block_label: str, content: str) -> dict:
    """
    Add content to a memory block.

    Args:
        block_label: The block label
        content: Content to append

    Returns:
        {"success": bool, "new_size": int, "limit": int, "utilization": float, "message": str}
    """
    manager = get_manager()

    try:
        current = await manager.read_block(block_label)
        new_body = current + "\n" + content

        status = await manager.validate_block(block_label)
        limit = status.get("limit", 10000) if status else 10000
        new_size = len(new_body)
        utilization = new_size / limit if limit > 0 else 0.0

        if new_size > limit:
            return {
                "success": False,
                "new_size": new_size,
                "limit": limit,
                "utilization": utilization,
                "message": f"Content would exceed limit ({new_size} > {limit} chars)",
            }

        await manager.write_block(block_label, new_body)

        return {
            "success": True,
            "new_size": new_size,
            "limit": limit,
            "utilization": utilization,
            "message": f"Appended {len(content)} chars to '{block_label}'",
        }

    except Exception as e:
        return {
            "success": False,
            "new_size": 0,
            "limit": 0,
            "utilization": 0.0,
            "message": str(e),
        }


async def memory_rethink(block_label: str, new_value: str) -> dict:
    """
    Replace entire block content, preserving frontmatter.

    Args:
        block_label: The block label
        new_value: Complete new content (body only; frontmatter preserved)

    Returns:
        {"success": bool, "old_size": int, "new_size": int, "message": str}
    """
    manager = get_manager()

    try:
        current = await manager.read_block(block_label)
        old_size = len(current)

        # Extract and preserve frontmatter
        frontmatter, _ = manager.extract_frontmatter(current)

        # Reconstruct with new body
        new_content = manager.reconstruct_with_frontmatter(frontmatter, new_value)
        new_size = len(new_content)

        # Validate
        status = await manager.validate_block(block_label)
        if status and new_size > status.get("limit", 10000):
            return {
                "success": False,
                "old_size": old_size,
                "new_size": new_size,
                "message": f"Content exceeds limit ({new_size} > {status['limit']} chars)",
            }

        await manager.write_block(block_label, new_content)

        return {
            "success": True,
            "old_size": old_size,
            "new_size": new_size,
            "message": f"Replaced block '{block_label}' ({old_size} → {new_size} chars)",
        }

    except Exception as e:
        return {
            "success": False,
            "old_size": 0,
            "new_size": 0,
            "message": str(e),
        }


async def compile_context(
    include_recall: bool = False,
    recall_query: Optional[str] = None,
    include_archival: bool = False,
    archival_query: Optional[str] = None,
    max_tokens: int = 25000,
) -> str:
    """
    Compile memory blocks into LLM context format.

    Args:
        include_recall: Whether to include recall tier (searchable history)
        recall_query: Semantic search query for recall tier
        include_archival: Whether to include archival tier
        archival_query: Semantic search query for archival tier
        max_tokens: Maximum tokens for compiled context

    Returns:
        XML-formatted context string
    """
    manager = get_manager()
    config = manager.load_config()

    parts = []
    estimated_tokens = 0

    # Add core blocks
    parts.append("<memory_blocks>")

    core_blocks = config.get("core_blocks", {})
    for block_name, block_config in core_blocks.items():
        label = block_config.get("label", block_name)
        description = block_config.get("description", "")

        try:
            content = await manager.read_block(label)

            # Estimate tokens (~4 chars per token)
            tokens = len(content) // 4

            if estimated_tokens + tokens > max_tokens:
                continue  # Skip to stay within budget

            estimated_tokens += tokens
            parts.append(f'\n<block label="{label}">')
            parts.append(f"<description>{description.strip()}</description>")
            parts.append(f"<content>\n{content}\n</content>")
            parts.append("</block>")

        except Exception:
            pass  # Skip blocks that can't be read

    parts.append("\n</memory_blocks>")

    # TODO: Add recall tier search when implemented
    # TODO: Add archival tier search when implemented

    return "".join(parts)


async def get_block_status() -> dict:
    """
    Get size and limit status for all blocks.

    Returns:
        {"blocks": [...], "total_utilization": float, "warnings": [...]}
    """
    manager = get_manager()
    return await manager.get_all_block_status()
