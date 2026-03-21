#!/usr/bin/env python3
"""
Queue Local Manuals for Hellenic Ingestion
==========================================
Surgical script to dispatch ingestion tasks for local technical manuals.
"""

import anyio
import logging
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

from app.XNAi_rag_app.core.agent_bus import AgentBusClient

async def queue_manuals():
    """Dispatch curation tasks for library/manuals."""
    agent_id = "scripts:queue_local_manuals"
    
    async with AgentBusClient(agent_id) as bus:
        print(f"🚀 Connected to Agent Bus as {agent_id}")
        
        # Task 1: Redis Manuals
        task_redis = {
            "type": "curation_task",
            "payload": {
                "source_type": "local",
                "directory": "library/manuals"
            },
            "sender": agent_id
        }
        
        task_id = await bus.send_task(task_redis)
        print(f"✅ Queued task for library/manuals: {task_id}")
        
        # Task 2: Qdrant Manuals (already in manuals dir but for testing)
        task_qdrant = {
            "type": "curation_task",
            "payload": {
                "source_type": "local",
                "directory": "library/manuals"
            },
            "sender": agent_id
        }
        
        # Actually, let's just queue the whole manuals dir once
        print("🎉 Ingestion wave dispatched.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    anyio.run(queue_manuals)
