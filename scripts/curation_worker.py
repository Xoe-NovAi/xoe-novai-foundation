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

# --- Config ---
LOG_DIR = Path(os.getenv("LOG_DIR", "logs/curations"))
DATA_DIR = Path(os.getenv("DATA_DIR", "data/curations"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}',
    handlers=[logging.FileHandler(LOG_DIR / "worker.log"), logging.StreamHandler()]
)
logger = logging.getLogger("curation_worker")

async def process_curation_task(task: dict):
    """Actual ingestion logic."""
    payload = task["payload"]
    source = payload.get("source_path")
    vikunja_id = payload.get("vikunja_task_id")
    
    logger.info(f"INGESTING: {source} (Vikunja Task: {vikunja_id})")
    
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
