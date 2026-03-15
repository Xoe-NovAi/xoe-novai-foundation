#!/usr/bin/env python3
"""
XNAi Persistent Entity System
=============================

Implements long-term memory and identity for personas and models.
Allows each 'Expert' to learn from past interactions and feedback.
"""

import os
import json
import logging
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PersistentEntity:
    """
    A persistent intelligence entity (Model or Persona).
    """

    def __init__(self, entity_id: str, role: str, base_dir: str = "storage/data/entities"):
        self.entity_id = entity_id.lower().replace(" ", "_")
        self.role = role
        self.storage_path = Path(base_dir) / f"{self.entity_id}.json"
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Memory tiers
        self.procedural_memory: List[Dict[str, Any]] = []
        self.domains: List[str] = []  # Attached domains (e.g., ['grunge', 'nirvana'])
        self.is_initialized = False  # Flag for expertise mining
        self.stats = {"invocations": 0, "success_rate": 0.0, "total_feedback": 0}

        self.load()

    def load(self):
        """Load entity state from disk."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    self.procedural_memory = data.get("procedural_memory", [])
                    self.domains = data.get("domains", [])
                    self.is_initialized = data.get("is_initialized", False)
                    self.stats = data.get("stats", self.stats)
                    logger.debug(f"Loaded entity {self.entity_id}")
            except Exception as e:
                logger.error(f"Failed to load entity {self.entity_id}: {e}")

    def save(self):
        """Persist entity state."""
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
            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save entity {self.entity_id}: {e}")

    def add_lesson(self, query: str, advice: str, outcome: str, rating: float):
        """Add a 'Lesson Learned' to procedural memory."""
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

        self.save()

    def get_relevant_context(self, query: str) -> str:
        """Retrieves past lessons relevant to the current query."""
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
