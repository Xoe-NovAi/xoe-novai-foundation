"""
Knowledge Distillation Module
=============================

LangGraph-based knowledge absorption system for XNAi Foundation.

Usage:
    from XNAi_rag_app.core.distillation import distill_content

    result = await distill_content(
        source="session_123",
        source_type="cli_session",
        raw_content="Content to process..."
    )

    if result["quality_score"] >= 0.6:
        print(f"Stored to: {result['storage_targets']}")

Pipeline:
    Extract → Classify → Score → Distill → Store

Quality Gate:
    Content with score < 0.6 is rejected.
"""

from .state import (
    KnowledgeState,
    create_initial_state,
    SOURCE_TYPES,
    CONTENT_TYPES,
    PRIORITY_LEVELS,
)

from .knowledge_distillation import (
    KnowledgeDistillationPipeline,
    build_distillation_graph,
    distill_content,
    get_pipeline,
)

__all__ = [
    # State
    "KnowledgeState",
    "create_initial_state",
    "SOURCE_TYPES",
    "CONTENT_TYPES",
    "PRIORITY_LEVELS",
    # Pipeline
    "KnowledgeDistillationPipeline",
    "build_distillation_graph",
    "distill_content",
    "get_pipeline",
]

__version__ = "0.1.0"
