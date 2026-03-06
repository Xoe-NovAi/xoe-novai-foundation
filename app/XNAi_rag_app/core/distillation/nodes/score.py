"""
Knowledge Distillation Nodes - Score Node
=========================================

Quality scoring wrapper node for LangGraph.
"""

import logging
from typing import Dict, Any

from ..state import KnowledgeState
from ..quality.scorer import QualityScorer

logger = logging.getLogger(__name__)

_scorer: QualityScorer = None


def _get_scorer() -> QualityScorer:
    """Get or create quality scorer instance."""
    global _scorer
    if _scorer is None:
        _scorer = QualityScorer()
    return _scorer


async def score_content_node(state: KnowledgeState) -> Dict[str, Any]:
    """
    Score content quality.

    Args:
        state: Current knowledge state

    Returns:
        Dict with quality_score and quality_breakdown
    """
    scorer = _get_scorer()

    result = await scorer.score(
        content=state.get("extracted_content", ""),
        classification=state.get("classification", {}),
        state=state,
    )

    return result
