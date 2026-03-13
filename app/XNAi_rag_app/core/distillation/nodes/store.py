"""
Knowledge Distillation Nodes - Store Node
=========================================

Storage routing node for LangGraph.
"""

import logging
import os
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from ..state import KnowledgeState
from ..quality.scorer import QualityThresholds, QualityTier

logger = logging.getLogger(__name__)

# Default staging path
STAGING_BASE = Path(os.getenv("XNAI_STAGING_PATH", "library/_staging"))


async def store_content_node(state: KnowledgeState) -> Dict[str, Any]:
    """
    Store content in appropriate targets based on quality tier.

    Quality Tier Storage:
    - GOLD (0.9-1.0): Qdrant + Memory Bank + Expert-Knowledge
    - HIGH (0.8-0.89): Qdrant + Memory Bank
    - GOOD (0.7-0.79): Qdrant only
    - ACCEPTABLE (0.6-0.69): Qdrant with expiry

    Args:
        state: Current knowledge state

    Returns:
        Dict with storage_targets, qdrant_ids, memory_bank_refs
    """
    quality_score = state["quality_score"]
    tier = QualityThresholds.get_tier(quality_score)
    threshold = QualityThresholds.THRESHOLDS[tier]

    storage_targets = []
    qdrant_ids = []
    memory_bank_refs = []

    # Staging path for this content
    staging_path = _create_staging_path(state)

    # Store to Qdrant
    if "qdrant" in threshold.storage_targets:
        qdrant_id = await _store_to_qdrant(state, threshold.expires)
        if qdrant_id:
            qdrant_ids.append(qdrant_id)
            storage_targets.append("qdrant")

    # Store to Memory Bank
    if "memory_bank" in threshold.storage_targets:
        ref = await _store_to_memory_bank(state)
        if ref:
            memory_bank_refs.append(ref)
            storage_targets.append("memory_bank")

    # Store to Expert Knowledge
    if "expert_knowledge" in threshold.storage_targets:
        ref = await _store_to_expert_knowledge(state)
        if ref:
            memory_bank_refs.append(ref)
            storage_targets.append("expert_knowledge")

    logger.info(f"Stored to: {storage_targets} (tier={tier.value})")

    return {
        "storage_targets": storage_targets,
        "qdrant_ids": qdrant_ids,
        "memory_bank_refs": memory_bank_refs,
        "staging_path": str(staging_path),
    }


def _create_staging_path(state: KnowledgeState) -> Path:
    """Create staging directory path."""
    source = state["source"].replace(" ", "_")[:50]
    date = datetime.utcnow().strftime("%Y-%m-%d")

    # Determine subdirectory by quality
    quality_score = state["quality_score"]
    if quality_score >= 0.8:
        subdir = "distilled"
    elif quality_score >= 0.6:
        subdir = "extracted"
    else:
        subdir = "rejected"

    path = STAGING_BASE / subdir / f"{source}_{date}"
    path.mkdir(parents=True, exist_ok=True)

    return path


async def _store_to_qdrant(state: KnowledgeState, expires: bool) -> str:
    """Store content to Qdrant vector database."""
    import uuid

    # Generate ID
    qdrant_id = str(uuid.uuid4())

    # In production, would call KnowledgeClient.add_document()
    # For now, log the intent
    logger.info(f"Would store to Qdrant: {qdrant_id} (expires={expires})")

    return qdrant_id


async def _store_to_memory_bank(state: KnowledgeState) -> str:
    """Store content to memory bank."""
    classification = state.get("classification", {})
    topic = classification.get("topic", "unknown").replace(" ", "_")[:30]

    # Determine memory bank location
    ref = f"memory_bank/recall/{topic}.md"

    logger.info(f"Would store to memory bank: {ref}")

    return ref


async def _store_to_expert_knowledge(state: KnowledgeState) -> str:
    """Store content to expert knowledge."""
    classification = state.get("classification", {})
    content_type = classification.get("type", "reference")

    # Determine expert knowledge location
    ref = f"expert-knowledge/{content_type}/{state['source'][:30]}.md"

    logger.info(f"Would store to expert knowledge: {ref}")

    return ref
