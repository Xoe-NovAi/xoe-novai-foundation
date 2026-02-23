"""
Knowledge State Schema
======================

Defines the state schema for the LangGraph-based knowledge distillation workflow.

CLAUDE STANDARD: Uses TypedDict for type safety.
TORCH-FREE: No PyTorch dependencies.

Based on: memory_bank/strategies/KNOWLEDGE-ABSORPTION-SYSTEM-DESIGN.md
"""

from typing import TypedDict, Annotated, Optional, List, Dict, Any
from datetime import datetime
import operator


class KnowledgeState(TypedDict):
    """
    State schema for knowledge distillation workflow.

    This TypedDict defines all fields that flow through the LangGraph
    StateGraph for knowledge processing.

    Fields are organized by workflow stage:
    - Input: source, source_type, raw_content
    - Processing: extracted_content, chunks, classification
    - Quality: quality_score, rejection_reason
    - Output: distilled_content, summary, key_insights
    - Storage: storage_targets, qdrant_ids, memory_bank_refs
    """

    # ========================================================================
    # INPUT FIELDS
    # ========================================================================

    source: str
    """Source identifier (e.g., 'agent_research_2026-02-22')"""

    source_type: str
    """Type of source: 'agent_research' | 'cli_session' | 'web_content' | 'code_analysis'"""

    raw_content: str
    """Original raw content to be processed"""

    # ========================================================================
    # PROCESSING FIELDS
    # ========================================================================

    extracted_content: Optional[str]
    """Cleaned and extracted content after processing"""

    chunks: Optional[List[Dict[str, Any]]]
    """List of content chunks with metadata"""

    classification: Optional[Dict[str, Any]]
    """
    Classification result with structure:
    {
        "type": "tutorial" | "reference" | "explanation" | "how_to" | "research",
        "topic": str,
        "tags": List[str],
        "priority": "p0" | "p1" | "p2" | "p3"
    }
    """

    # ========================================================================
    # QUALITY FIELDS
    # ========================================================================

    quality_score: float
    """Quality score from 0.0 to 1.0 (threshold: 0.6)"""

    quality_breakdown: Optional[Dict[str, float]]
    """
    Quality score breakdown:
    {
        "relevance": float,      # 30% weight
        "novelty": float,        # 25% weight
        "actionability": float,  # 20% weight
        "completeness": float,   # 15% weight
        "accuracy": float        # 10% weight
    }
    """

    rejection_reason: Optional[str]
    """Reason for rejection if quality_score < 0.6"""

    # ========================================================================
    # DISTILLATION FIELDS
    # ========================================================================

    distilled_content: Optional[str]
    """Refined and optimized content for storage"""

    summary: Optional[str]
    """Brief summary of the content (1-2 sentences)"""

    key_insights: Optional[List[str]]
    """List of extracted key insights"""

    action_items: Optional[List[str]]
    """List of actionable items extracted from content"""

    # ========================================================================
    # METADATA FIELDS
    # ========================================================================

    provenance: Optional[Dict[str, Any]]
    """
    Source tracking metadata:
    {
        "agent": str,           # Agent that created the content
        "cli": str,             # CLI used
        "model": str,           # Model used
        "session_id": str,      # Session identifier
        "timestamp": str        # Original creation time
    }
    """

    created_at: str
    """ISO timestamp when content was submitted"""

    processed_at: Optional[str]
    """ISO timestamp when processing completed"""

    processing_time_ms: Optional[int]
    """Total processing time in milliseconds"""

    # ========================================================================
    # STORAGE FIELDS (Accumulated via operator.add)
    # ========================================================================

    storage_targets: Annotated[List[str], operator.add]
    """
    List of storage targets written to:
    - "qdrant": Vector database
    - "memory_bank": Context files
    - "expert_knowledge": Gold-standard docs
    """

    qdrant_ids: Annotated[List[str], operator.add]
    """List of Qdrant point IDs created"""

    memory_bank_refs: Annotated[List[str], operator.add]
    """List of memory bank file paths created"""

    staging_path: Optional[str]
    """Path to staging directory for this content"""


# ============================================================================
# Source Types
# ============================================================================

SOURCE_TYPES = [
    "agent_research",  # Research from AI agents
    "cli_session",  # CLI conversation logs
    "web_content",  # Scraped web content
    "code_analysis",  # Code analysis results
    "documentation",  # Generated documentation
    "benchmark",  # Performance benchmarks
    "error_log",  # Error analysis
]


# ============================================================================
# Content Types (Diátaxis-aligned)
# ============================================================================

CONTENT_TYPES = [
    "tutorial",  # Learning-oriented
    "how_to",  # Problem-oriented
    "reference",  # Information-oriented
    "explanation",  # Understanding-oriented
    "research",  # Research findings
    "code",  # Code snippets
    "config",  # Configuration
]


# ============================================================================
# Priority Levels
# ============================================================================

PRIORITY_LEVELS = [
    "p0",  # Critical - immediate action required
    "p1",  # High - action within 1 week
    "p2",  # Medium - action within 1 month
    "p3",  # Low - backlog
]


# ============================================================================
# Helper Functions
# ============================================================================


def create_initial_state(
    source: str,
    source_type: str,
    raw_content: str,
    provenance: Optional[Dict[str, Any]] = None,
) -> KnowledgeState:
    """
    Create an initial KnowledgeState for processing.

    Args:
        source: Source identifier
        source_type: Type of source (see SOURCE_TYPES)
        raw_content: Raw content to process
        provenance: Optional source tracking metadata

    Returns:
        Initialized KnowledgeState dict
    """
    return KnowledgeState(
        source=source,
        source_type=source_type,
        raw_content=raw_content,
        extracted_content=None,
        chunks=None,
        classification=None,
        quality_score=0.0,
        quality_breakdown=None,
        rejection_reason=None,
        distilled_content=None,
        summary=None,
        key_insights=None,
        action_items=None,
        provenance=provenance or {},
        created_at=datetime.utcnow().isoformat(),
        processed_at=None,
        processing_time_ms=None,
        storage_targets=[],
        qdrant_ids=[],
        memory_bank_refs=[],
        staging_path=None,
    )
