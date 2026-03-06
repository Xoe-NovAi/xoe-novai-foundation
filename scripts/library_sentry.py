#!/usr/bin/env python3
"""
Xoe-NovAi Library Sentry
========================

Background service that monitors 'library/bookdrop' for new documents
and triggers the ingestion pipeline via the Agent Bus.

Hardware Optimized: Ryzen 5700U (Zen 2)
Integration: Agent Bus (Redis Streams)
"""

import os
import time
import logging
from pathlib import Path
import subprocess
from app.XNAi_rag_app.core.agent_bus import AgentBusClient

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("library_sentry")

# Configuration
BOOKDROP_DIR = Path("library/bookdrop")
CHECK_INTERVAL = 10  # Seconds
AGENT_DID = "service:library_sentry:001"

async def monitor_bookdrop():
    """Monitor the bookdrop directory and trigger ingestion."""
    if not BOOKDROP_DIR.exists():
        BOOKDROP_DIR.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"LibrarySentry active. Monitoring {BOOKDROP_DIR}...")
    
    async with AgentBusClient(AGENT_DID) as bus:
        while True:
            files = list(BOOKDROP_DIR.glob("*"))
            if files:
                logger.info(f"Detected {len(files)} new files in bookdrop.")
                
                # 1. Trigger ingestion via subprocess (to avoid venv issues if needed)
                # Or call the module directly if environment is safe
                try:
                    logger.info("Triggering ingestion pipeline...")
                    # Using --mode from_library for the bookdrop specifically
                    result = subprocess.run(
                        ["python3", "-m", "app.XNAi_rag_app.ingest_library", "--mode", "from_library", "--library-path", str(BOOKDROP_DIR)],
                        capture_output=True, text=True
                    )
                    
                    if result.returncode == 0:
                        logger.info("Ingestion successful.")
                        # 2. Notify Agent Bus
                        await bus.send_task(
                            target_did="agent:gnosis_extractor:*",
                            task_type="graph_extraction_request",
                            payload={"files": [str(f.name) for f in files]}
                        )
                        
                        # 3. Clean up bookdrop (move to sorted or delete)
                        # For now, we'll assume the ingestion script handles movement or we delete
                        for f in files:
                            f.unlink()
                            logger.info(f"Cleaned up {f.name}")
                    else:
                        logger.error(f"Ingestion failed: {result.stderr}")
                        
                except Exception as e:
                    logger.error(f"Error during ingestion trigger: {e}")
            
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(monitor_bookdrop())
    except KeyboardInterrupt:
        logger.info("LibrarySentry stopping...")
