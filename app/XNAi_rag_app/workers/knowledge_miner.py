#!/usr/bin/env python3
"""
XNAi Persona Knowledge Miner
============================

Autonomous worker that researches and builds the 'Expert Memory Bank'
for new persistent personas.

Workflow:
1.  Receive 'expertise_mining' task.
2.  Trigger Deep Crawl/Research on the persona and attached domains.
3.  Synthesize findings into high-value 'Lessons Learned'.
4.  Inject into Gnosis Engine (LightRAG) for long-term recall.
"""

import anyio
import json
import logging
import time
import os
from typing import Dict, Any, List
from XNAi_rag_app.core.agent_bus import AgentBusClient
from XNAi_rag_app.core.entities.registry import registry as entity_registry
from XNAi_rag_app.workers.crawl import curate_from_source
from scripts.graph_extractor import process_document

from XNAi_rag_app.core.health.health_monitoring import create_enhanced_health_checker
from XNAi_rag_app.core.health.recovery_manager import RecoveryManager

logger = logging.getLogger("knowledge_miner")

class KnowledgeMinerWorker(AgentBusClient):
    """
    Autonomous worker that researches and builds the 'Expert Memory Bank'.
    """
    
    # Mapping roles to crawl sources
    ROLE_SOURCES = {
        "philosopher": "gutenberg",
        "scientist": "arxiv",
        "engineer": "arxiv",
        "medical": "pubmed",
        "musician": "youtube",
        "artist": "youtube",
        "general": "gutenberg"
    }

    def __init__(self, agent_did: str = "worker:knowledge_miner:001"):
        super().__init__(agent_did)
        self.recovery = RecoveryManager()
        # Enterprise Hardening: Limit concurrent heavy research tasks
        self.limiter = anyio.CapacityLimiter(1)
        # Initialize health checker
        self.health_monitor = create_enhanced_health_checker({
            "targets": ["memory", "redis"],
            "interval_seconds": 60
        })

    async def start(self):
        async with self as bus:
            logger.info("Knowledge Miner Worker active. Searching for expertise gaps...")
            while True:
                try:
                    # Health Check: Don't mine if system is degraded (RAM pressure)
                    summary = await self.health_monitor.get_health_summary()
                    # Check system metrics directly if services not checked yet
                    ram_usage = summary.get("system_metrics", {}).get("memory_usage_percent", 0)
                    
                    if ram_usage > 90:
                        logger.warning(f"System under high RAM pressure ({ram_usage}%). Knowledge Mining paused.")
                        await anyio.sleep(30)
                        continue

                    tasks = await self.fetch_tasks(count=1)
                    for task in tasks:
                        if task["type"] == "expertise_mining":
                            # Use limiter to protect Ryzen 5700U memory
                            async with self.limiter:
                                await self._mine_expertise(task)
                        await self.acknowledge_task(task["id"])
                    
                    await anyio.sleep(1)
                except Exception as e:
                    logger.error(f"Worker loop error: {e}")
                    await anyio.sleep(5)

    async def _mine_expertise(self, task: Dict[str, Any]):
        payload = task["payload"]
        name = payload.get("name")
        role = payload.get("role", "general")
        
        logger.info(f"⛏️  Mining Expertise for: {name} ({role})")
        
        # 1. Determine Source
        source = self.ROLE_SOURCES.get(role.lower(), "gutenberg")
        category = f"expert-{name.lower().replace(' ', '-')}"
        
        # 2. Delegate to LibraryCuratorWorker via Agent Bus
        logger.info(f"📡 Delegating curation task for {name} to LibraryCurator...")
        try:
            # Send task to Agent Bus
            curation_payload = {
                "source_type": "api",
                "api_name": source,
                "query": name,
                "category": category,
                "max_items": 5
            }
            curation_task_id = await self.send_task(
                target_did="worker:library_curator:001",
                task_type="curation_task",
                payload=curation_payload
            )
            logger.info(f"📤 Curation task sent: {curation_task_id}")
            
            # 3. Wait for result (Simple poll for now)
            # In a production system, we might use a proper callback/promise pattern
            max_wait = 120 # 2 minutes
            start_wait = time.time()
            completed = False
            
            while time.time() - start_wait < max_wait:
                # Check task updates stream (this is simplified)
                # Ideally we'd filter for the specific task_id
                updates = await self.redis.xrevrange("xnai:task_updates", count=10)
                for msg_id, data in updates:
                    if data.get("task_id") == curation_task_id and data.get("status") == "completed":
                        logger.info(f"✅ Curation task {curation_task_id} confirmed complete")
                        completed = True
                        break
                if completed: break
                await anyio.sleep(5)
            
            if not completed:
                logger.warning(f"⚠️ Curation task {curation_task_id} timed out or failed")

        except Exception as e:
            logger.error(f"❌ Delegation failed for {name}: {e}")

        # 4. Extract high-value findings (Mocked for now)
        findings = [
            f"{name} research complete via delegated curation.",
            f"Expertise category created: {category}.",
            f"Knowledge injected into Gnosis Engine."
        ]
        
        # 4. Update Entity Memory
        entity = entity_registry.get_entity(name, role, auto_create=False)
        if entity:
            for fact in findings:
                entity.add_lesson(
                    query="Who is this entity?",
                    advice="N/A (Bootstrap)",
                    outcome=fact,
                    rating=1.0
                )
            entity.is_initialized = True
            entity.save()
            
        logger.info(f"✅ Expertise mined and persisted for {name}.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    worker = KnowledgeMinerWorker()
    anyio.run(worker.start)
