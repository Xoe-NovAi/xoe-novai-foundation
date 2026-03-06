#!/usr/bin/env python3
"""
XNAi Entity Registry (v2.0)
===========================

Manages dynamic creation and discovery of persistent intelligence entities.
Supports 'On-the-fly' expert summoning and background expertise mining.
"""

import logging
import json
import time
import asyncio
from typing import Dict, Any, List, Optional
from .persistent_entity import PersistentEntity

logger = logging.getLogger(__name__)

class EntityRegistry:
    def __init__(self, redis_client: Any = None, base_dir: str = "storage/data/entities"):
        self.entities: Dict[str, PersistentEntity] = {}
        self.base_dir = base_dir
        self._creation_lock = asyncio.Lock()

        # If no client provided, try to initialize one from environment
        if redis_client is None:
            try:
                from redis.asyncio import Redis
                import os
                host = os.getenv("REDIS_HOST", "localhost")
                port = int(os.getenv("REDIS_PORT", 6379))
                password = os.getenv("REDIS_PASSWORD")
                self.redis = Redis(host=host, port=port, password=password, decode_responses=True)
                logger.info(f"Connected EntityRegistry to Redis at {host}:{port}")
            except Exception as e:
                logger.warning(f"Could not initialize Redis for EntityRegistry: {e}")
                self.redis = None
        else:
            self.redis = redis_client

    async def get_entity(self, entity_id: str, role: str = "expert", auto_create: bool = True) -> Optional[PersistentEntity]:
        """
        Get an entity or create it on-the-fly if it doesn't exist.
        """
        eid = entity_id.lower().replace(" ", "_")
        
        async with self._creation_lock:
            if eid not in self.entities:
                # Check disk for existing entity not in memory
                entity = PersistentEntity(eid, role, self.base_dir)
                
                # If it's brand new and auto_create is True
                if not entity.is_initialized and auto_create:
                    logger.info(f"✨ New Expert Summoned: {entity_id}. Triggering expertise mining...")
                    entity.save() # Ensure file exists immediately
                    await self._trigger_expertise_mining(entity_id, role)
                
                self.entities[eid] = entity
                
        return self.entities[eid]

    async def _trigger_expertise_mining(self, name: str, role: str):
        """
        Dispatches a task to the Agent Bus to research this new entity.
        Uses AgentBusClient for standardized multi-agent communication.
        """
        await self._send_mining_task(name, role)

    async def _send_mining_task(self, name: str, role: str):
        """Standardized task dispatch via AgentBusClient."""
        from XNAi_rag_app.core.agent_bus import AgentBusClient
        try:
            async with AgentBusClient(agent_did="metropolis:registry:001") as bus:
                await bus.send_task(
                    target_did="worker:knowledge_miner:*",
                    task_type="expertise_mining",
                    payload={"name": name, "role": role}
                )
                logger.info(f"🚀 Dispatched expertise mining for '{name}' to Agent Bus.")
        except Exception as e:
            logger.error(f"❌ Failed to dispatch mining task for {name}: {e}")

    def record_feedback(self, entity_id: str, query: str, advice: str, outcome: str, rating: float):
        # Record feedback is now handled via the PerformanceFeedbackLoop service
        # but we keep this for direct entity updates if needed.
        pass


# Note: In production, the global registry will be initialized with a Redis client
registry = EntityRegistry()
