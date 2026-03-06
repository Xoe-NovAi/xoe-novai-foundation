"""
Knowledge Distillation Nodes
============================

Node functions for LangGraph StateGraph.
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..state import KnowledgeState

logger = logging.getLogger(__name__)


# ============================================================================
# Extract Node
# ============================================================================


async def extract_content_node(state: KnowledgeState) -> Dict[str, Any]:
    """
    Extract and clean content from raw input.

    Tasks:
    - Strip markdown code fences if present
    - Remove navigation elements
    - Extract main content sections
    - Create content chunks

    Args:
        state: Current knowledge state

    Returns:
        Dict with extracted_content and chunks
    """
    raw = state["raw_content"]

    # Strip code fences
    extracted = _strip_code_fences(raw)

    # Remove common navigation patterns
    extracted = _remove_navigation(extracted)

    # Normalize whitespace
    extracted = _normalize_whitespace(extracted)

    # Create chunks for processing
    chunks = _create_chunks(extracted, chunk_size=2000)

    logger.info(f"Extracted {len(extracted)} chars, {len(chunks)} chunks")

    return {
        "extracted_content": extracted,
        "chunks": chunks,
    }


def _strip_code_fences(content: str) -> str:
    """Remove markdown code fences while preserving content."""
    # Remove ```language fences but keep content
    pattern = r"```\w*\n(.*?)```"
    result = re.sub(pattern, r"\1", content, flags=re.DOTALL)
    return result.strip()


def _remove_navigation(content: str) -> str:
    """Remove common navigation elements."""
    patterns = [
        r"\[Home\].*?\n",
        r"\[Back\].*?\n",
        r"\[Next\].*?\n",
        r"Previous:.*?\n",
        r"Next:.*?\n",
        r"Navigation.*?\n",
        r"Table of Contents.*?\n---\n",
    ]

    result = content
    for pattern in patterns:
        result = re.sub(pattern, "", result, flags=re.IGNORECASE)

    return result


def _normalize_whitespace(content: str) -> str:
    """Normalize whitespace and line endings."""
    # Normalize line endings
    result = content.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse multiple blank lines
    result = re.sub(r"\n{3,}", "\n\n", result)

    # Strip trailing whitespace from lines
    result = "\n".join(line.rstrip() for line in result.split("\n"))

    return result.strip()


def _create_chunks(content: str, chunk_size: int = 2000) -> List[Dict[str, Any]]:
    """
    Create content chunks for processing.

    Respects section boundaries where possible.
    """
    chunks = []

    # Split by sections (## headers)
    sections = re.split(r"\n(?=## )", content)

    current_chunk = ""
    chunk_index = 0

    for section in sections:
        if len(current_chunk) + len(section) <= chunk_size:
            current_chunk += "\n" + section if current_chunk else section
        else:
            if current_chunk:
                chunks.append(
                    {
                        "index": chunk_index,
                        "content": current_chunk.strip(),
                        "char_count": len(current_chunk),
                    }
                )
                chunk_index += 1
            current_chunk = section

    # Add final chunk
    if current_chunk:
        chunks.append(
            {
                "index": chunk_index,
                "content": current_chunk.strip(),
                "char_count": len(current_chunk),
            }
        )

    return chunks


# ============================================================================
# Classify Node
# ============================================================================


async def classify_content_node(state: KnowledgeState) -> Dict[str, Any]:
    """
    Classify content type and assign tags.

    Uses keyword matching and structure analysis for classification.
    Maps to Diátaxis framework: tutorial, how-to, reference, explanation.

    Args:
        state: Current knowledge state

    Returns:
        Dict with classification
    """
    content = state.get("extracted_content", "")
    source_type = state["source_type"]

    # Determine content type
    content_type = _classify_type(content, source_type)

    # Extract topic
    topic = _extract_topic(content)

    # Generate tags
    tags = _generate_tags(content, content_type)

    # Determine priority
    priority = _determine_priority(content, source_type)

    classification = {
        "type": content_type,
        "topic": topic,
        "tags": tags,
        "priority": priority,
    }

    logger.info(f"Classified as: {content_type}, topic: {topic}, priority: {priority}")

    return {"classification": classification}


def _classify_type(content: str, source_type: str) -> str:
    """Determine content type based on content and source."""
    content_lower = content.lower()

    # Check for tutorial patterns
    if any(
        p in content_lower for p in ["step 1", "first,", "getting started", "beginner"]
    ):
        return "tutorial"

    # Check for how-to patterns
    if any(p in content_lower for p in ["how to", "steps:", "1.", "follow these"]):
        return "how_to"

    # Check for reference patterns
    if any(
        p in content_lower for p in ["api reference", "parameters:", "configuration"]
    ):
        return "reference"

    # Check for explanation patterns
    if any(p in content_lower for p in ["why", "understanding", "concept", "overview"]):
        return "explanation"

    # Check for research patterns
    if any(
        p in content_lower for p in ["research", "findings", "analysis", "conclusion"]
    ):
        return "research"

    # Default based on source type
    if source_type == "agent_research":
        return "research"
    elif source_type == "cli_session":
        return "how_to"

    return "reference"


def _extract_topic(content: str) -> str:
    """Extract main topic from content."""
    # Try to find from first heading
    heading_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if heading_match:
        return heading_match.group(1).strip()

    # Try to find from first significant line
    lines = [l.strip() for l in content.split("\n") if l.strip()]
    if lines:
        first_line = lines[0]
        # Truncate to reasonable length
        if len(first_line) > 50:
            return first_line[:50] + "..."
        return first_line

    return "unknown"


def _generate_tags(content: str, content_type: str) -> List[str]:
    """Generate tags based on content analysis."""
    tags = [content_type]

    content_lower = content.lower()

    # Technology tags
    tech_patterns = {
        "python": ["python", "pip", "pyproject"],
        "docker": ["docker", "container", "podman"],
        "redis": ["redis", "cache"],
        "qdrant": ["qdrant", "vector", "embedding"],
        "chainlit": ["chainlit", "chat interface"],
        "langgraph": ["langgraph", "state graph"],
        "fastapi": ["fastapi", "api", "endpoint"],
    }

    for tag, patterns in tech_patterns.items():
        if any(p in content_lower for p in patterns):
            tags.append(tag)

    # Action tags
    if "fix" in content_lower or "bug" in content_lower:
        tags.append("bugfix")
    if "implement" in content_lower or "create" in content_lower:
        tags.append("implementation")
    if "research" in content_lower:
        tags.append("research")

    return list(set(tags))[:10]  # Limit to 10 unique tags


def _determine_priority(content: str, source_type: str) -> str:
    """Determine priority based on content analysis."""
    content_lower = content.lower()

    # P0: Critical
    if any(p in content_lower for p in ["critical", "urgent", "blocking", "security"]):
        return "p0"

    # P0: Source type based
    if source_type in ["error_log", "benchmark"]:
        return "p0"

    # P1: High
    if any(
        p in content_lower for p in ["important", "high priority", "action required"]
    ):
        return "p1"

    # P1: Source type based
    if source_type == "agent_research":
        return "p1"

    # P2: Medium
    if source_type == "cli_session":
        return "p2"

    # Default
    return "p3"
