#!/usr/bin/env python3
"""
XNAi Entity Registry
===================

Global registry for all persistent entities (Models and Personas).
Provides identity management, feedback collection, and cross-session learning.
Now AnyIO/Async compliant.
"""

import os
import logging
import anyio
import json as _json
from typing import Dict, Any, Optional, List
from pathlib import Path

from .persistent_entity import PersistentEntity

logger = logging.getLogger(__name__)

class EntityRegistry:
    """
    Global registry for persistent entities.
    Ensures each Model/Persona has a unique identity and persistent memory.
    """

    def __init__(self, base_dir: str = "storage/data/entities"):
        self.base_dir = Path(base_dir)
        
        # Registry of all entities
        self.entities: Dict[str, PersistentEntity] = {}
        
        # Entity metadata
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self._initialized = False

    async def initialize(self):
        """Async initialization of the registry."""
        if self._initialized:
            return
            
        storage_parent = anyio.Path(self.base_dir)
        if not await storage_parent.exists():
            await storage_parent.mkdir(parents=True, exist_ok=True)
            
        await self.load_registry()
        self._initialized = True

    async def register_entity(self, entity_id: str, role: str) -> PersistentEntity:
        """
        Register or retrieve a persistent entity (Async).
        Creates the entity if it doesn't exist.
        """
        if not self._initialized:
            await self.initialize()

        key = entity_id.lower().replace(" ", "_")
        
        if key not in self.entities:
            # Create new entity via async factory
            entity = await PersistentEntity.create(entity_id, role, str(self.base_dir))
            self.entities[key] = entity
            
            # Store metadata
            self.metadata[key] = {
                "entity_id": entity_id,
                "role": role,
                "created_at": entity.stats.get("invocations", 0),
                "type": "persona" if "persona" in role.lower() else "model"
            }
            
            logger.info(f"Registered new entity: {entity_id} ({role})")
        
        return self.entities[key]

    def get_entity(self, entity_id: str) -> Optional[PersistentEntity]:
        """Get an entity by ID (Sync - assumes already loaded)."""
        key = entity_id.lower().replace(" ", "_")
        return self.entities.get(key)

    async def record_feedback(self, entity_id: str, query: str, advice: str, 
                       outcome: str, rating: float) -> bool:
        """
        Record feedback for an entity (Async).
        This is the core learning mechanism.
        """
        entity = self.get_entity(entity_id)
        if not entity:
            logger.warning(f"Entity not found for feedback: {entity_id}")
            return False
        
        try:
            await entity.add_lesson(query, advice, outcome, rating)
            logger.info(f"Recorded feedback for {entity_id} (rating: {rating})")
            return True
        except Exception as e:
            logger.error(f"Failed to record feedback for {entity_id}: {e}")
            return False

    def get_entity_stats(self, entity_id: str) -> Dict[str, Any]:
        """Get statistics for an entity (Sync)."""
        entity = self.get_entity(entity_id)
        if not entity:
            return {}
        
        return {
            "entity_id": entity.entity_id,
            "role": entity.role,
            "invocations": entity.stats["invocations"],
            "success_rate": entity.stats["success_rate"],
            "total_feedback": entity.stats["total_feedback"],
            "memory_size": len(entity.procedural_memory)
        }

    def get_all_entities(self) -> List[Dict[str, Any]]:
        """Get all registered entities (Sync)."""
        return [
            {
                "entity_id": entity.entity_id,
                "role": entity.role,
                "type": self.metadata.get(key, {}).get("type", "unknown"),
                "stats": self.get_entity_stats(entity.entity_id)
            }
            for key, entity in self.entities.items()
        ]

    async def load_registry(self):
        """Load all existing entities from disk using Async I/O."""
        path = anyio.Path(self.base_dir)
        if not await path.exists():
            return
        
        # Since anyio.Path.glob is not always available or behaves differently, 
        # we use to_thread for the listing if needed, but Path(base_dir).glob is usually fine for metadata.
        # However, for consistency with 'AnyIO first', we'll use a safer approach.
        
        import os
        for filename in os.listdir(self.base_dir):
            if filename.endswith(".json"):
                json_path = self.base_dir / filename
                try:
                    # Extract entity_id from filename
                    entity_id = json_path.stem.replace("_", " ")
                    
                    # Determine role from metadata if available
                    role = "unknown"
                    async with await anyio.open_file(json_path, "r") as f:
                        content = await f.read()
                        data = _json.loads(content)
                        role = data.get("role", "unknown")
                    
                    # Load entity via async factory
                    entity = await PersistentEntity.create(entity_id, role, str(self.base_dir))
                    
                    # Register entity
                    key = entity_id.lower().replace(" ", "_")
                    self.entities[key] = entity
                    self.metadata[key] = {
                        "entity_id": entity_id,
                        "role": role,
                        "type": "persona" if "persona" in role.lower() else "model"
                    }
                    
                except Exception as e:
                    logger.warning(f"Failed to load entity from {json_path}: {e}")

    def get_top_performers(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing entities by success rate (Sync)."""
        performers = []
        for entity in self.entities.values():
            if entity.stats["total_feedback"] > 0:
                performers.append({
                    "entity_id": entity.entity_id,
                    "role": entity.role,
                    "success_rate": entity.stats["success_rate"],
                    "total_feedback": entity.stats["total_feedback"]
                })
        
        # Sort by success rate and feedback count
        performers.sort(key=lambda x: (x["success_rate"], x["total_feedback"]), reverse=True)
        return performers[:limit]

    def get_entity_context(self, entity_id: str, query: str) -> str:
        """Get relevant context from an entity's memory (Sync)."""
        entity = self.get_entity(entity_id)
        if not entity:
            return ""
        
        return entity.get_relevant_context(query)

# Global registry instance
_entity_registry: Optional[EntityRegistry] = None

async def get_entity_registry() -> EntityRegistry:
    """Get the global entity registry (Async)."""
    global _entity_registry
    if _entity_registry is None:
        _entity_registry = EntityRegistry()
        await _entity_registry.initialize()
    return _entity_registry

async def register_persistent_entity(entity_id: str, role: str) -> PersistentEntity:
    """Register a persistent entity (Async)."""
    registry = await get_entity_registry()
    return await registry.register_entity(entity_id, role)

async def record_entity_feedback(entity_id: str, query: str, advice: str, 
                          outcome: str, rating: float) -> bool:
    """Record feedback for an entity (Async)."""
    registry = await get_entity_registry()
    return await registry.record_feedback(entity_id, query, advice, outcome, rating)

async def get_entity_context(entity_id: str, query: str) -> str:
    """Get context from an entity's memory (Async)."""
    registry = await get_entity_registry()
    return registry.get_entity_context(entity_id, query)
