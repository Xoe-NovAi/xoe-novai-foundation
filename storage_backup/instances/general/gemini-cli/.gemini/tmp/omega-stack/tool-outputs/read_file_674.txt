#!/usr/bin/env python3
"""
XNAi Persistent Entity System
=============================

Implements long-term memory and identity for personas and models.
Allows each 'Expert' to learn from past interactions and feedback.
Now AnyIO/Async compliant.
"""

import os
import json
import logging
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
import anyio

logger = logging.getLogger(__name__)


class PersistentEntity:
    """
    A persistent intelligence entity (Model or Persona).
    """

    def __init__(self, entity_id: str, role: str, base_dir: str = "storage/data/entities"):
        self.entity_id = entity_id.lower().replace(" ", "_")
        self.role = role
        self.storage_path = Path(base_dir) / f"{self.entity_id}.json"
        
        # Memory tiers
        self.procedural_memory: List[Dict[str, Any]] = []
        self.domains: List[str] = []  # Attached domains (e.g., ['grunge', 'nirvana'])
        self.is_initialized = False  # Flag for expertise mining
        self.stats = {"invocations": 0, "success_rate": 0.0, "total_feedback": 0}

    @classmethod
    async def create(cls, entity_id: str, role: str, base_dir: str = "storage/data/entities") -> 'PersistentEntity':
        """
        Async factory method to create and load an entity.
        """
        instance = cls(entity_id, role, base_dir)
        # Ensure directory exists
        storage_parent = anyio.Path(instance.storage_path.parent)
        if not await storage_parent.exists():
            await storage_parent.mkdir(parents=True, exist_ok=True)
            
        await instance.load()
        return instance

    async def load(self):
        """Load entity state from disk using Async I/O."""
        path = anyio.Path(self.storage_path)
        if await path.exists():
            try:
                async with await anyio.open_file(self.storage_path, "r") as f:
                    content = await f.read()
                    data = json.loads(content)
                    self.procedural_memory = data.get("procedural_memory", [])
                    self.domains = data.get("domains", [])
                    self.is_initialized = data.get("is_initialized", False)
                    self.stats = data.get("stats", self.stats)
                    logger.debug(f"Loaded entity {self.entity_id}")
            except FileNotFoundError:
                logger.debug(f"Entity file not found for {self.entity_id}, creating new")
            except json.JSONDecodeError as e:
                logger.warning(f"Corrupted entity data for {self.entity_id}: {e}")
                await self._handle_corrupted_data()
            except PermissionError as e:
                logger.error(f"Permission denied loading entity {self.entity_id}: {e}")
                await self._handle_permission_error(e)
            except Exception as e:
                logger.error(f"Unexpected error loading entity {self.entity_id}: {e}")
                await self._handle_unexpected_error(e, "load")

    async def save(self):
        """Persist entity state using Async I/O."""
        data = {
            "entity_id": self.entity_id,
            "role": self.role,
            "domains": self.domains,
            "is_initialized": self.is_initialized,
            "procedural_memory": self.procedural_memory,
            "stats": self.stats,
            "last_updated": time.time(),
        }
        try:
            # Ensure parent exists
            storage_parent = anyio.Path(self.storage_path.parent)
            if not await storage_parent.exists():
                await storage_parent.mkdir(parents=True, exist_ok=True)

            async with await anyio.open_file(self.storage_path, "w") as f:
                content = json.dumps(data, indent=2)
                await f.write(content)
        except PermissionError as e:
            logger.error(f"Permission denied saving entity {self.entity_id}: {e}")
            await self._handle_permission_error(e)
        except Exception as e:
            logger.error(f"Unexpected error saving entity {self.entity_id}: {e}")
            await self._handle_unexpected_error(e, "save")

    async def _handle_corrupted_data(self):
        """Recover from corrupted entity data."""
        backup_path = self.storage_path.with_suffix(".corrupted")
        try:
            if os.path.exists(self.storage_path):
                os.rename(self.storage_path, backup_path)
                logger.info(f"Moved corrupted data to {backup_path}")
        except:
            pass
        # Reset to default state
        self.procedural_memory = []
        self.is_initialized = False

    async def _handle_permission_error(self, e: Exception):
        """Handle permission errors (e.g. log to observability)."""
        # Placeholder for observability integration
        logger.error(f"Critical Permission Error: {e}")

    async def _handle_unexpected_error(self, e: Exception, operation: str):
        """Handle unexpected errors."""
        logger.critical(f"Unexpected error during {operation} for {self.entity_id}: {e}")

    async def add_lesson(self, query: str, advice: str, outcome: str, rating: float):
        """Add a 'Lesson Learned' to procedural memory (Async)."""
        lesson = {"timestamp": time.time(), "query": query, "advice": advice, "outcome": outcome, "rating": rating}
        self.procedural_memory.append(lesson)

        # Update stats
        n = self.stats["total_feedback"]
        current_sr = self.stats["success_rate"]
        self.stats["success_rate"] = ((current_sr * n) + rating) / (n + 1)
        self.stats["total_feedback"] += 1

        # Keep memory concise (last 50 lessons)
        if len(self.procedural_memory) > 50:
            self.procedural_memory.pop(0)

        await self.save()

    def get_relevant_context(self, query: str) -> str:
        """Retrieves past lessons relevant to the current query (Sync)."""
        if not self.procedural_memory:
            return ""

        query_words = set(w.strip("?!.,") for w in query.lower().split())
        relevant = [
            l
            for l in self.procedural_memory
            if any(word in query_words for w in l["query"].lower().split() for word in [w.strip("?!.,")])
        ]
        if not relevant:
            return ""

        context = "\nPAST LESSONS LEARNED:\n"
        for l in relevant[-3:]:  # Top 3
            status = "SUCCESS" if l["rating"] > 0.8 else "FAILURE"
            context += f"- Task: {l['query']} | Result: {status} | Lesson: {l['outcome']}\n"
        return context
