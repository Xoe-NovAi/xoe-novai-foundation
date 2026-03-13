#!/usr/bin/env python3
"""
XNAi Agent Tools: Expert Summoning
==================================

Allows agents to autonomously summon and consult persistent expert entities.
Enables the "Metropolis" vision of cross-expert communication.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from XNAi_rag_app.core.entities.registry import registry as entity_registry
from XNAi_rag_app.core.entities.enhanced_handler import create_entity_handler

logger = logging.getLogger(__name__)

# Initialize enhanced handler
handler = create_entity_handler(entity_registry)

async def summon_expert(entity_name: str, query: str) -> Dict[str, Any]:
    """
    Summon a persistent expert entity to consult on a specific query.
    
    Args:
        entity_name: Name of the expert (e.g., "Socrates", "Kurt Cobain")
        query: The specific question or task for the expert.
        
    Returns:
        Expert's response including context and procedural memory.
    """
    logger.info(f"🤖 Agent summoning expert: {entity_name}")
    
    # Use enhanced handler to parse and route
    # We simulate a "hey {entity}, {query}" pattern for the agent
    parsed = handler.parse_query(f"hey {entity_name}, {query}")
    
    if not parsed:
        # Fallback to direct lookup if parsing fails
        entity = await entity_registry.get_entity(entity_name)
        context = entity.get_relevant_context(query)
        return {
            "entity": entity_name,
            "response": f"Expert {entity_name} summoned directly.",
            "context": context
        }
        
    result = await handler.handle_query(parsed)
    return result

async def get_available_experts() -> List[str]:
    """List all known persistent experts in the metropolis."""
    return handler.list_available_entities()

async def compare_experts(entity1: str, entity2: str, topic: str) -> Dict[str, Any]:
    """Compare perspectives of two experts on a given topic."""
    parsed = handler.parse_query(f"compare {entity1} and {entity2} on {topic}")
    if parsed:
        return await handler.handle_query(parsed)
    return {"error": "Invalid comparison pattern"}
