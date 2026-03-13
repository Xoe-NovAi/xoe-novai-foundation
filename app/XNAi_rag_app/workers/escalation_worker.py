#!/usr/bin/env python3
"""
Xoe-NovAi Escalation Research Worker
====================================

Listens for 'escalation_research' tasks on the Agent Bus and executes
the 4-level research chain. Posts results back to task_updates.
"""

import anyio
import json
import logging
import os
import time
from typing import Dict, Any
from XNAi_rag_app.core.agent_bus import AgentBusClient
from XNAi_rag_app.services.escalation_researcher import EscalationResearcher
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

class EscalationWorker(AgentBusClient):
    """
    Worker that processes research requests from other agents.
    """
    
    def __init__(self, agent_did: str = "worker:escalation_researcher:001"):
        super().__init__(agent_did)
        self.researcher = None
        self.update_stream = "xnai:task_updates"

    async def start(self):
        """Main loop to fetch and process research tasks."""
        # Initialize Redis and Researcher
        async with self as bus:
            self.researcher = EscalationResearcher(redis_client=bus.redis)
            logger.info(f"EscalationWorker {self.agent_did} started and listening...")
            
            while True:
                try:
                    tasks = await self.fetch_tasks(count=1)
                    for task in tasks:
                        if task["type"] == "escalation_research":
                            await self._process_research(task)
                        
                        await self.acknowledge_task(task["id"])
                    
                    await anyio.sleep(0.5)
                except Exception as e:
                    logger.error(f"EscalationWorker error: {e}")
                    await anyio.sleep(5)

    async def _process_research(self, task: Dict[str, Any]):
        """Execute research and post results."""
        task_id = task["id"]
        payload = task["payload"]
        query = payload.get("query")
        sender = task["sender"]
        
        if not query:
            logger.warning(f"Task {task_id} missing query payload")
            return

        logger.info(f"Processing research for {sender}: '{query}'")
        
        # We use the non-streaming version or collect the stream
        final_result = None
        async for result in self.researcher.research_stream(query):
            final_result = result
            # Optional: Post intermediate updates to task_updates as well
            await self._post_update(task_id, sender, "processing", result)

        # Post final result
        await self._post_update(task_id, sender, "completed", final_result)
        logger.info(f"Research complete for task {task_id}")

    async def _post_update(self, task_id: str, target: str, status: str, result: Dict[str, Any]):
        """Post result back to task_updates stream."""
        update = {
            "task_id": task_id,
            "target": target,
            "status": status,
            "level": str(result["level"]),
            "confidence": str(result["confidence"]),
            "answer": result["answer"],
            "dossier": json.dumps(result["dossier"]),
            "timestamp": str(time.time())
        }
        await self.redis.xadd(self.update_stream, update)

if __name__ == "__main__":
    # To run: python3 -m app.XNAi_rag_app.workers.escalation_worker
    logging.basicConfig(level=logging.INFO)
    worker = EscalationWorker()
    anyio.run(worker.start)
