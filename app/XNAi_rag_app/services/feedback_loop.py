#!/usr/bin/env python3
"""
XNAi Performance Feedback Loop
==============================

Closes the loop between user/agent feedback and entity learning.
Distributes ratings and outcomes to the persistent entities involved
in a research session.
"""

import logging
from typing import List, Dict, Any
from XNAi_rag_app.core.entities.registry import registry as entity_registry
from XNAi_rag_app.core.training.fine_tuning_logger import ft_logger

logger = logging.getLogger(__name__)

class PerformanceFeedbackLoop:
    """
    Manages the 'Digest' phase where entities learn from their work.
    """

    @staticmethod
    async def record_session_outcome(
        query: str, 
        dossier: Dict[str, Any], 
        rating: float, 
        outcome_note: str = "Self-evaluated success"
    ):
        """
        Distribute feedback to all involved models and personas.
        """
        # 1. Gather all entities involved in the chain
        involved_roles = dossier.get("involved_entities", [])
        model_id = dossier.get("model_id", "unknown_model")
        answer = dossier.get("final_answer", "")
        
        logger.info(f"Closing feedback loop for query: '{query[:50]}...' (Rating: {rating})")
        logger.info(f"Entities receiving feedback: {involved_roles}")
        
        success_count = 0
        
        for entity_id in involved_roles:
            try:
                # Ensure entity exists and get it
                await entity_registry.get_entity(entity_id)
                
                # Record the lesson
                entity_registry.record_feedback(
                    entity_id=entity_id,
                    query=query,
                    advice="N/A (Automated research turn)",
                    outcome=outcome_note,
                    rating=rating
                )
                
                # Log for Fine-Tuning if high quality
                if rating >= 0.85:
                    await ft_logger.log_interaction(
                        query=query,
                        response=answer,
                        expert_id=entity_id,
                        model_id=model_id,
                        rating=rating,
                        metadata={"outcome": outcome_note}
                    )
                
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to record feedback for {entity_id}: {e}")

        logger.info(f"Feedback loop closed. {success_count}/{len(involved_roles)} entities updated.")
        return success_count

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    
    # Self-test with mock data
    async def test():
        # Ensure at least one entity exists for test
        entity_registry.get_entity("test_expert", "tester")
        
        mock_dossier = {
            "involved_entities": ["test_expert"],
            "query": "Unit Test Query"
        }
        await PerformanceFeedbackLoop.record_session_outcome(
            "Test Query", 
            mock_dossier, 
            0.9, 
            "Excellent tech detail"
        )
        
    asyncio.run(test())
