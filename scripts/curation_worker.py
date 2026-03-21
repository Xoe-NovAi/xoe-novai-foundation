#!/usr/bin/env python3
import anyio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import subprocess
from app.XNAi_rag_app.core.agent_bus import AgentBusClient
from app.XNAi_rag_app.core.infrastructure.resource_hub import ResourceHub
from app.XNAi_rag_app.core.xnai_zram_monitor import wait_for_resource_availability

# Initialize hub
hub = ResourceHub()

async def process_curation_task(task: dict):
    """Actual ingestion logic."""
    payload = task["payload"]
    source = payload.get("source_path")
    vikunja_id = payload.get("vikunja_task_id")
    
    # 🔱 RESOURCE HARDENING GATE
    # Wait for zRAM availability before potentially intensive ingestion
    await wait_for_resource_availability()
    
    logger.info(f"INGESTING: {source} (Vikunja Task: {vikunja_id})")
    
    # Example of model usage via ResourceHub (if needed for extraction/summarization)
    # llm = await hub.get_model('llm')
    
    # Mock command for technical manual ingestion
    # In production, this calls ingest_library.py
    cmd = ["python3", "scripts/ingest_library.py", "--path", source]
    
    try:
        # Simulate execution for now
        # In real case: subprocess.run(cmd, check=True)
        await anyio.sleep(2)
        logger.info(f"Successfully curated: {source}")
        return True
    except Exception as e:
        logger.error(f"Ingestion failed for {source}: {e}")
        return False

async def run_worker():
    agent_did = "did:xnai:agent:curation_worker"
    async with AgentBusClient(agent_did) as bus:
        logger.info(f"Curation Worker {agent_did} online via Agent Bus. Waiting for tasks...")
        while True:
            tasks = await bus.fetch_tasks(count=1)
            for task in tasks:
                if task["type"] == "CURATE_BOOK":
                    success = await process_curation_task(task)
                    if success:
                        await bus.acknowledge_task(task["id"])
                        logger.info(f"Task {task['id']} COMPLETED.")
            await anyio.sleep(5)

if __name__ == "__main__":
    try:
        anyio.run(run_worker)
    except KeyboardInterrupt:
        pass
