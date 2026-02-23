#!/usr/bin/env python3
"""
Knowledge Distillation Pipeline - LangGraph StateGraph Implementation
======================================================================

Implements the Knowledge Absorption System using LangGraph.

CLAUDE STANDARD: Uses AnyIO for structured concurrency.
TORCH-FREE: No PyTorch dependencies.

Pipeline:
    Extract → Classify → Score → Distill → Store

Quality Gate: Content with score < 0.6 is rejected.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

# LangGraph imports
from langgraph.graph import StateGraph, END

# Import state definition
from .state import (
    KnowledgeState,
    create_initial_state,
    CONTENT_TYPES,
    PRIORITY_LEVELS,
)

# Import quality scoring
from .quality.scorer import QualityScorer, QualityThresholds

# Import node functions
from .nodes.extract import extract_content_node
from .nodes.classify import classify_content_node
from .nodes.score import score_content_node
from .nodes.distill import distill_content_node
from .nodes.store import store_content_node

logger = logging.getLogger(__name__)


# ============================================================================
# Quality Gate Function
# ============================================================================


def quality_gate(state: KnowledgeState) -> str:
    """
    Determine if content passes quality threshold.

    Args:
        state: Current knowledge state

    Returns:
        "accept" if quality_score >= threshold, else "reject"
    """
    threshold = QualityThresholds.get_threshold(state.get("content_type", "default"))

    if state["quality_score"] >= threshold:
        logger.info(
            f"Content passed quality gate: {state['quality_score']:.2f} >= {threshold}"
        )
        return "accept"
    else:
        logger.info(
            f"Content rejected by quality gate: {state['quality_score']:.2f} < {threshold}"
        )
        return "reject"


# ============================================================================
# Build LangGraph StateGraph
# ============================================================================


def build_distillation_graph() -> StateGraph:
    """
    Build the knowledge distillation LangGraph StateGraph.

    Graph Structure:
        START → extract → classify → score → [quality_gate]
                                            ↓
                                    ┌───────┴───────┐
                                    ↓               ↓
                                "accept"         "reject"
                                    ↓               ↓
                                distill           END
                                    ↓
                                store
                                    ↓
                                    END

    Returns:
        Compiled StateGraph
    """
    # Create the graph
    graph = StateGraph(KnowledgeState)

    # Add nodes
    graph.add_node("extract", extract_content_node)
    graph.add_node("classify", classify_content_node)
    graph.add_node("score", score_content_node)
    graph.add_node("distill", distill_content_node)
    graph.add_node("store", store_content_node)

    # Set entry point
    graph.set_entry_point("extract")

    # Add linear edges
    graph.add_edge("extract", "classify")
    graph.add_edge("classify", "score")

    # Add conditional edge for quality gate
    graph.add_conditional_edges(
        "score",
        quality_gate,
        {
            "accept": "distill",
            "reject": END,
        },
    )

    # Add remaining edges
    graph.add_edge("distill", "store")
    graph.add_edge("store", END)

    return graph.compile()


# ============================================================================
# Pipeline Class
# ============================================================================


class KnowledgeDistillationPipeline:
    """
    Main interface for knowledge distillation.

    Usage:
        pipeline = KnowledgeDistillationPipeline()

        result = await pipeline.process(
            source="session_123",
            source_type="cli_session",
            raw_content="Long content to process..."
        )

        if result["quality_score"] >= 0.6:
            print(f"Stored to: {result['storage_targets']}")
        else:
            print(f"Rejected: {result['rejection_reason']}")
    """

    def __init__(self):
        self.graph = build_distillation_graph()
        self._processed_count = 0
        self._rejected_count = 0

    async def process(
        self,
        source: str,
        source_type: str,
        raw_content: str,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeState:
        """
        Process content through the distillation pipeline.

        Args:
            source: Source identifier
            source_type: Type of source (cli_session, agent_research, etc.)
            raw_content: Raw content to process
            provenance: Optional source tracking metadata

        Returns:
            Final KnowledgeState with processing results
        """
        start_time = datetime.utcnow()

        # Create initial state
        initial_state = create_initial_state(
            source=source,
            source_type=source_type,
            raw_content=raw_content,
            provenance=provenance,
        )

        try:
            # Run the graph
            result = await self.graph.ainvoke(initial_state)

            # Update timing
            end_time = datetime.utcnow()
            result["processed_at"] = end_time.isoformat()
            result["processing_time_ms"] = int(
                (end_time - start_time).total_seconds() * 1000
            )

            # Update counts
            self._processed_count += 1
            if result.get("rejection_reason"):
                self._rejected_count += 1

            logger.info(
                f"Distillation complete: quality={result['quality_score']:.2f}, "
                f"time={result['processing_time_ms']}ms"
            )

            return result

        except Exception as e:
            logger.error(f"Distillation pipeline failed: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return {
            "processed_count": self._processed_count,
            "rejected_count": self._rejected_count,
            "acceptance_rate": (
                (self._processed_count - self._rejected_count) / self._processed_count
                if self._processed_count > 0
                else 0.0
            ),
        }


# ============================================================================
# Convenience Functions
# ============================================================================

# Global pipeline instance
_pipeline: Optional[KnowledgeDistillationPipeline] = None


def get_pipeline() -> KnowledgeDistillationPipeline:
    """Get or create the global pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = KnowledgeDistillationPipeline()
    return _pipeline


async def distill_content(
    source: str,
    source_type: str,
    raw_content: str,
    provenance: Optional[Dict[str, Any]] = None,
) -> KnowledgeState:
    """
    Convenience function to distill content.

    Args:
        source: Source identifier
        source_type: Type of source
        raw_content: Raw content to process
        provenance: Optional source tracking metadata

    Returns:
        Final KnowledgeState with processing results
    """
    pipeline = get_pipeline()
    return await pipeline.process(source, source_type, raw_content, provenance)


# ============================================================================
# CLI Entry Point
# ============================================================================


async def main():
    """CLI entry point for testing."""
    import argparse

    parser = argparse.ArgumentParser(description="Knowledge Distillation Pipeline")
    parser.add_argument("--source", required=True, help="Source identifier")
    parser.add_argument("--type", default="cli_session", help="Source type")
    parser.add_argument("--content", required=True, help="Content to process")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    result = await distill_content(
        source=args.source,
        source_type=args.type,
        raw_content=args.content,
    )

    print(f"\n{'=' * 60}")
    print(f"QUALITY SCORE: {result['quality_score']:.2f}")
    print(f"STATUS: {'ACCEPTED' if not result.get('rejection_reason') else 'REJECTED'}")

    if result.get("rejection_reason"):
        print(f"REASON: {result['rejection_reason']}")
    else:
        print(f"\nSUMMARY: {result.get('summary', 'N/A')}")
        print(f"KEY INSIGHTS: {result.get('key_insights', [])}")
        print(f"STORAGE TARGETS: {result.get('storage_targets', [])}")

    print(f"PROCESSING TIME: {result.get('processing_time_ms', 0)}ms")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
