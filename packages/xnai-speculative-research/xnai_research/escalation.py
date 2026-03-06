#!/usr/bin/env python3
"""
Xoe-NovAi Escalation Researcher
===============================

Hierarchical research agent that escalates based on confidence and depth.
Implements the 3x researched escalation chain (Revised).

Levels:
1. Tiny (150M) - 3x Local RAG
2. Hybrid (1B) - 1x Web -> 1x Local -> 1x Web
3. Deep (Intermediate) - 2x Web -> 1x Local
4. Authority (8B) - Flexible combination, Achievement of >95% confidence.
"""

import logging
import asyncio
import time
from typing import List, Dict, Any, Optional
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class EscalationLevel:
    TINY = 1
    HYBRID = 2
    DEEP = 3
    AUTHORITY = 4

class EscalationResearcher:
    """
    Coordinates hierarchical research across multiple model levels.
    Each level produces a structured 'Research Dossier'.
    """

    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        stream_key: str = "xnai:speculative_updates"
    ):
        self.redis = redis_client
        self.stream_key = stream_key
        self.interrupt_event = asyncio.Event()
        self.force_cli_event = asyncio.Event()
        logger.info("EscalationResearcher initialized")

    def interrupt(self, next_level: bool = True):
        """Interrupt current research to escalate."""
        if next_level:
            self.interrupt_event.set()
        else:
            self.force_cli_event.set()
            self.interrupt_event.set()

    async def research_stream(self, query: str):
        """
        Execute the escalation research chain and yield intermediate results.
        Each yielded result is a 'Research Dossier'.
        """
        dossier = {
            "query": query,
            "raw_findings": [],
            "verified_facts": [],
            "cited_sources": [],
            "knowledge_map": {},
            "confidence": 0.0
        }
        
        # Reset events
        self.interrupt_event.clear()
        self.force_cli_event.clear()
        
        # Level 1: Tiny Researcher
        result = await self._level1_tiny(query, dossier)
        dossier.update(result["dossier"])
        yield result
        await self._broadcast_update(EscalationLevel.TINY, result)
        
        if self._should_stop(result["confidence"]):
            return

        # Level 2: Hybrid Researcher
        result = await self._level2_hybrid(query, dossier)
        dossier.update(result["dossier"])
        yield result
        await self._broadcast_update(EscalationLevel.HYBRID, result)

        if self._should_stop(result["confidence"]):
            return

        # Level 3: Deep Researcher
        result = await self._level3_deep(query, dossier)
        dossier.update(result["dossier"])
        yield result
        await self._broadcast_update(EscalationLevel.DEEP, result)

        if self._should_stop(result["confidence"]):
            return

        # Level 4: Authority Researcher (Krikri-8B)
        result = await self._level4_authority(query, dossier)
        yield result
        await self._broadcast_update(EscalationLevel.AUTHORITY, result)

    def _should_stop(self, confidence: float) -> bool:
        """Check if we should stop research based on confidence or interrupt."""
        if self.force_cli_event.is_set():
            logger.info("Force CLI escalation requested")
            return True
        if self.interrupt_event.is_set():
            logger.info("Manual next-level escalation requested")
            self.interrupt_event.clear()
            return False
        return confidence >= 0.9 # Default threshold

    async def _level1_tiny(self, query: str, prev_dossier: Dict[str, Any]) -> Dict[str, Any]:
        """Level 1: 3x Local RAG Research."""
        logger.info("Level 1 Research: 3x Local RAG")
        # Simulate work
        new_dossier = prev_dossier.copy()
        new_dossier["raw_findings"].extend(["Local RAG result A", "Local RAG result B"])
        new_dossier["verified_facts"].append("Fact 1 discovered via local RAG")
        
        return {
            "level": 1,
            "answer": "Draft answer from Tiny Model",
            "dossier": new_dossier,
            "confidence": 0.75,
            "latency_ms": 150
        }

    async def _level2_hybrid(self, query: str, prev_dossier: Dict[str, Any]) -> Dict[str, Any]:
        """Level 2: 1x Web -> 1x Local -> 1x Web."""
        logger.info("Level 2 Research: 1x Web -> 1x Local -> 1x Web")
        new_dossier = prev_dossier.copy()
        new_dossier["cited_sources"].append({"url": "https://example.com/source", "score": 0.9})
        new_dossier["verified_facts"].append("Fact 2 discovered via web search")
        new_dossier["knowledge_map"]["concept_A"] = ["entity_1", "entity_2"]
        
        return {
            "level": 2,
            "answer": "Refined answer from Hybrid Model",
            "dossier": new_dossier,
            "confidence": 0.82,
            "latency_ms": 450
        }

    async def _level3_deep(self, query: str, prev_dossier: Dict[str, Any]) -> Dict[str, Any]:
        """Level 3: 2x Web -> 1x Local."""
        logger.info("Level 3 Research: 2x Web -> 1x Local")
        new_dossier = prev_dossier.copy()
        new_dossier["verified_facts"].append("Fact 3: Complex relationship confirmed")
        new_dossier["knowledge_map"]["concept_B"] = ["entity_3", "entity_4"]
        
        return {
            "level": 3,
            "answer": "Advanced answer from Deep Model",
            "dossier": new_dossier,
            "confidence": 0.88,
            "latency_ms": 1200
        }

    async def _level4_authority(self, query: str, prev_dossier: Dict[str, Any]) -> Dict[str, Any]:
        """Level 4: Krikri-8B-Instruct Flexible Research."""
        logger.info("Level 4 Research: Authority (Krikri-8B)")
        new_dossier = prev_dossier.copy()
        new_dossier["verified_facts"].append("Final authoritative conclusion reached")
        
        return {
            "level": 4,
            "answer": "Final authoritative answer from Krikri-8B-Instruct using deep dossier",
            "dossier": new_dossier,
            "confidence": 0.98,
            "latency_ms": 2500
        }

    async def _broadcast_update(self, level: int, result: Dict[str, Any]):
        """Broadcast update to Redis for real-time UI."""
        if self.redis:
            message = {
                "type": "speculative_update",
                "level": str(level),
                "answer": result["answer"],
                "confidence": str(result["confidence"]),
                "dossier_size": str(len(result["dossier"]["verified_facts"])),
                "timestamp": str(time.time())
            }
            await self.redis.xadd(self.stream_key, message)
            logger.debug(f"Broadcasted update for Level {level}")

if __name__ == "__main__":
    # Test script
    logging.basicConfig(level=logging.INFO)
    researcher = EscalationResearcher()
    import asyncio
    
    async def run_test():
        print("Starting Escalation Research Test with Dossiers...")
        async for result in researcher.research_stream("Tell me about the Xoe-NovAi Foundation"):
             print(f"\n[Level {result['level']}] Facts: {len(result['dossier']['verified_facts'])}")

    asyncio.run(run_test())
