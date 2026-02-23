"""
Quality Scoring Module
======================

Implements quality scoring for knowledge distillation.
"""

import logging
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================================================
# Quality Tiers
# ============================================================================


class QualityTier(Enum):
    """Quality tiers based on score ranges."""

    GOLD = "gold"  # 0.9 - 1.0
    HIGH = "high"  # 0.8 - 0.89
    GOOD = "good"  # 0.7 - 0.79
    ACCEPTABLE = "acceptable"  # 0.6 - 0.69
    REJECTED = "rejected"  # < 0.6


@dataclass
class QualityThreshold:
    """Quality threshold configuration."""

    min_score: float
    max_score: float
    storage_targets: List[str]
    expires: bool = False


class QualityThresholds:
    """Quality threshold configuration by tier."""

    THRESHOLDS = {
        QualityTier.GOLD: QualityThreshold(
            0.9, 1.0, ["qdrant", "memory_bank", "expert_knowledge"]
        ),
        QualityTier.HIGH: QualityThreshold(0.8, 0.89, ["qdrant", "memory_bank"]),
        QualityTier.GOOD: QualityThreshold(0.7, 0.79, ["qdrant"]),
        QualityTier.ACCEPTABLE: QualityThreshold(0.6, 0.69, ["qdrant"], expires=True),
        QualityTier.REJECTED: QualityThreshold(0.0, 0.59, []),
    }

    @classmethod
    def get_tier(cls, score: float) -> QualityTier:
        """Determine quality tier from score."""
        for tier, threshold in cls.THRESHOLDS.items():
            if threshold.min_score <= score <= threshold.max_score:
                return tier
        return QualityTier.REJECTED

    @classmethod
    def get_threshold(cls, content_type: str = "default") -> float:
        """Get minimum quality threshold."""
        return 0.6  # Universal threshold


# ============================================================================
# Quality Scorer
# ============================================================================


class QualityScorer:
    """
    Quality scorer for knowledge content.

    Scoring factors:
    - Relevance (30%): Semantic similarity to XNAi core topics
    - Novelty (25%): Duplicate detection
    - Actionability (20%): Presence of actionable items
    - Completeness (15%): Section coverage
    - Accuracy (10%): Cross-reference validation
    """

    # XNAi core topics for relevance
    CORE_TOPICS = [
        "chainlit",
        "redis",
        "qdrant",
        "langgraph",
        "fastapi",
        "agent",
        "knowledge",
        "distillation",
        "infrastructure",
        "voice",
        "session",
        "memory bank",
        "circuit breaker",
        "sovereign",
        "torch-free",
        "anyio",
    ]

    # Actionable patterns
    ACTION_PATTERNS = [
        r"\b(todo|task|action|implement|fix|create|add|update|remove)\b",
        r"\b(step \d|first|second|third|finally)\b",
        r"\b(must|should|need to|required)\b",
    ]

    def __init__(self):
        self._score_count = 0

    async def score(
        self,
        content: str,
        classification: Dict[str, Any],
        state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Calculate quality score for content.

        Args:
            content: Extracted content
            classification: Classification result
            state: Full knowledge state

        Returns:
            Dict with quality_score and quality_breakdown
        """
        self._score_count += 1

        # Calculate individual scores
        relevance = self._score_relevance(content)
        novelty = self._score_novelty(content, state)
        actionability = self._score_actionability(content)
        completeness = self._score_completeness(content, classification)
        accuracy = self._score_accuracy(content)

        # Weighted average
        quality_score = (
            relevance * 0.30
            + novelty * 0.25
            + actionability * 0.20
            + completeness * 0.15
            + accuracy * 0.10
        )

        # Clamp to 0-1 range
        quality_score = max(0.0, min(1.0, quality_score))

        quality_breakdown = {
            "relevance": relevance,
            "novelty": novelty,
            "actionability": actionability,
            "completeness": completeness,
            "accuracy": accuracy,
        }

        logger.info(
            f"Quality score: {quality_score:.2f} "
            f"(rel={relevance:.2f}, nov={novelty:.2f}, "
            f"act={actionability:.2f}, comp={completeness:.2f}, acc={accuracy:.2f})"
        )

        return {
            "quality_score": quality_score,
            "quality_breakdown": quality_breakdown,
        }

    def _score_relevance(self, content: str) -> float:
        """Score relevance to XNAi core topics."""
        content_lower = content.lower()

        # Count core topic matches
        matches = sum(1 for topic in self.CORE_TOPICS if topic in content_lower)

        # Normalize to 0-1 (expecting 3+ matches for high relevance)
        score = min(1.0, matches / 5.0)

        return score

    def _score_novelty(self, content: str, state: Dict[str, Any]) -> float:
        """Score novelty (new vs duplicate content)."""
        # For now, assume novelty based on length and structure
        # In production, would check against Qdrant

        # Novel content has substantial length
        if len(content) < 100:
            return 0.3
        elif len(content) < 500:
            return 0.6
        elif len(content) < 2000:
            return 0.8
        else:
            return 0.9

    def _score_actionability(self, content: str) -> float:
        """Score actionability of content."""
        content_lower = content.lower()

        # Count actionable pattern matches
        matches = 0
        for pattern in self.ACTION_PATTERNS:
            if re.search(pattern, content_lower):
                matches += 1

        # Normalize to 0-1
        score = min(1.0, matches / 3.0)

        return score

    def _score_completeness(
        self, content: str, classification: Dict[str, Any]
    ) -> float:
        """Score completeness of content."""
        # Check for common sections
        sections = [
            "summary" in content.lower(),
            "overview" in content.lower() or "introduction" in content.lower(),
            "conclusion" in content.lower() or "next steps" in content.lower(),
            "##" in content,  # Has sections
            len(content) > 500,
        ]

        # Score based on sections present
        score = sum(sections) / len(sections)

        return score

    def _score_accuracy(self, content: str) -> float:
        """Score accuracy (placeholder for future validation)."""
        # Check for code examples
        has_code = "```" in content or "def " in content or "async " in content

        # Check for links/references
        has_refs = "http" in content or "[" in content

        # Check for proper formatting
        has_formatting = "#" in content or "**" in content

        # Base score
        score = 0.6

        if has_code:
            score += 0.15
        if has_refs:
            score += 0.15
        if has_formatting:
            score += 0.10

        return min(1.0, score)

    def get_stats(self) -> Dict[str, Any]:
        """Get scorer statistics."""
        return {
            "score_count": self._score_count,
        }
