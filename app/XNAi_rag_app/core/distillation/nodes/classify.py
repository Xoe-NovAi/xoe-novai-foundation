"""
Knowledge Distillation Nodes - Classify Node
============================================

Classifies content into domains and types for optimized distillation.
"""

import logging
from typing import Any, Dict
from ..state import KnowledgeState

logger = logging.getLogger(__name__)

async def classify_content_node(state: KnowledgeState) -> KnowledgeState:
    """
    Classify the extracted content.
    [AP:docs/protocols/RCF_MASTER_PROTOCOL.md]
    """
    logger.info(f"Classifying content from source: {state.get('source')}")
    
    # Simple heuristic classification
    raw = state.get("raw_content", "").lower()
    
    if "def " in raw or "import " in raw or "class " in raw:
        content_type = "source_code"
    elif "## " in raw or "# " in raw:
        content_type = "documentation"
    else:
        content_type = "general_text"
        
    state["content_type"] = content_type
    
    # Initialize metadata if not present
    if "metadata" not in state:
        state["metadata"] = {}
        
    state["metadata"]["classification_engine"] = "Heuristic-v1"
    
    return state
