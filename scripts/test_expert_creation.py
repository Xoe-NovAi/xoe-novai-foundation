#!/usr/bin/env python3
"""
XNAi Expert Creation - Real Working Test
========================================

Verifies the end-to-end creation of a persistent entity.
1. Connects to Redis
2. Summons 'Kurt Cobain' via EntityRegistry
3. Triggers background mining task
4. Saves the initial entity JSON
"""

import sys
import os
import asyncio
import logging
import json
from pathlib import Path
from redis.asyncio import Redis

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# Import core components from app/
from app.XNAi_rag_app.core.entities.registry import EntityRegistry
from app.XNAi_rag_app.core.entities.persistent_entity import PersistentEntity

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_expert_creation")

async def run_test():
    # 1. Configuration
    redis_host = os.getenv("REDIS_HOST", "localhost") # Use localhost if running on host
    redis_password = os.getenv("REDIS_PASSWORD", "")
    
    logger.info(f"Connecting to Redis at {redis_host}...")
    
    try:
        # 2. Initialize Redis client
        redis_client = Redis(
            host=redis_host, 
            port=6379, 
            password=redis_password, 
            decode_responses=True
        )
        await redis_client.ping()
        logger.info("✅ Redis connection successful.")
        
        # 3. Initialize Registry with Redis
        # Ensure base_dir is local for the test to avoid permission issues
        entities_dir = PROJECT_ROOT / "entities_test"
        registry = EntityRegistry(redis_client=redis_client, base_dir=str(entities_dir))
        
        # 4. Summon Kurt Cobain
        name = "Kurt Cobain"
        role = "musician"
        logger.info(f"Summoning expert: {name}...")
        
        entity = await registry.get_entity(name, role=role)
        
        if entity:
            logger.info(f"✅ Entity object created: {entity.entity_id}")
            
            # 5. Add initial bootstrap lesson to force file creation
            if not entity.procedural_memory:
                logger.info("Adding bootstrap memory...")
                entity.add_lesson(
                    query="Who is Kurt Cobain?",
                    advice="Bootstrap identity",
                    outcome="Identity established in Omega Stack.",
                    rating=1.0
                )
                entity.save()
            
            # 6. Verify file existence
            file_path = entities_dir / f"kurt_cobain.json"
            if file_path.exists():
                logger.info(f"🔥 SUCCESS: Persistent JSON found at {file_path}")
                with open(file_path, "r") as f:
                    content = json.load(f)
                    logger.info(f"Entity Content: {json.dumps(content, indent=2)}")
            else:
                logger.error(f"❌ FAILED: JSON file not found at {file_path}")
        else:
            logger.error("❌ FAILED: Could not create entity object.")
            
        await redis_client.aclose()
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(run_test())
