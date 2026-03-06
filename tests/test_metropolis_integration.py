#!/usr/bin/env python3
"""
XNAi Metropolis Integration Test
================================

Validates the full "Agent Metropolis" loop:
1. Summoning a new expert ("Nikola Tesla")
2. Background Knowledge Mining trigger
3. Entity Persistence
4. Feedback Loop Learning
"""

import sys
import os
import asyncio
import logging
import json
import time
from pathlib import Path
from redis.asyncio import Redis

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

from app.XNAi_rag_app.core.entities.registry import EntityRegistry
from app.XNAi_rag_app.services.feedback_loop import PerformanceFeedbackLoop

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_metropolis")

async def run_test():
    logger.info("🚀 Starting Metropolis Integration Test...")
    
    # 1. Setup Test Environment
    test_dir = PROJECT_ROOT / "entities_test"
    test_dir.mkdir(exist_ok=True)
    
    # Initialize Registry with local test dir
    # We use a mocked Redis client or just None for this integration unit test
    # (In a full e2e we'd use real Redis, but here we test the logic flow)
    registry = EntityRegistry(redis_client=None, base_dir=str(test_dir))
    
    # 2. Summon Expert
    expert_name = "Nikola Tesla"
    logger.info(f"Summoning {expert_name}...")
    
    entity = registry.get_entity(expert_name, role="inventor")
    assert entity is not None
    assert entity.entity_id == "nikola_tesla"
    logger.info("✅ Entity created in registry.")
    
    # 3. Simulate Knowledge Mining (Bootstrap)
    logger.info("Simulating Knowledge Mining...")
    entity.add_lesson(
        query="Who are you?", 
        advice="Bootstrap", 
        outcome="I am the inventor of AC electricity.", 
        rating=1.0
    )
    entity.is_initialized = True
    entity.save()
    
    # Verify file
    file_path = test_dir / "nikola_tesla.json"
    assert file_path.exists()
    logger.info("✅ Entity persisted to disk.")
    
    # 4. Simulate Feedback Loop
    logger.info("Simulating Feedback Loop...")
    dossier = {
        "involved_entities": ["nikola_tesla"],
        "query": "How does AC work?"
    }
    
    # Patch the global registry in feedback loop to use our test registry
    from app.XNAi_rag_app.services import feedback_loop
    feedback_loop.entity_registry = registry
    
    await PerformanceFeedbackLoop.record_session_outcome(
        "How does AC work?",
        dossier,
        0.95,
        "Great explanation of alternating current."
    )
    
    # 5. Verify Learning
    # Reload entity to check memory
    entity.load()
    last_lesson = entity.procedural_memory[-1]
    assert last_lesson["rating"] == 0.95
    assert "alternating current" in last_lesson["outcome"]
    logger.info("✅ Entity successfully learned from feedback.")
    
    logger.info("🎉 Metropolis Integration Test Passed!")

if __name__ == "__main__":
    asyncio.run(run_test())
