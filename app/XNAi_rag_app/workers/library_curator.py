#!/usr/bin/env python3
"""
XNAi Library Curator Worker
===========================

Autonomous worker that processes library curation tasks from the Agent Bus.
Uses the EnterpriseIngestionEngine for multi-source ingestion and scholarly curation.

Workflow:
1.  Listen for 'curation_task' on Agent Bus.
2.  Initialize EnterpriseIngestionEngine.
3.  Ingest from specified source (API, RSS, or local).
4.  Apply scholarly enhancements and deduplication.
5.  Index into Vectorstore (Qdrant/FAISS).
"""

import anyio
import json
import logging
import os
import time
from typing import Dict, Any, List, Optional
from XNAi_rag_app.core.agent_bus import AgentBusClient
from XNAi_rag_app.services.ingest_library import EnterpriseIngestionEngine, IngestionStats
from prometheus_client import Counter, Histogram, start_http_server

logger = logging.getLogger("library_curator")

# SI1: Library Curation Metrics
CURATOR_INGESTED = Counter("xnai_curator_ingested_total", "Total items successfully ingested into library", ["source"])
CURATOR_ERRORS = Counter("xnai_curator_errors_total", "Total errors during ingestion", ["source", "error_type"])
CURATOR_LATENCY = Histogram("xnai_curator_processing_seconds", "Time taken to process a single item")
SUMMARIZATION_TIME = Histogram("xnai_curator_summarization_seconds", "Local LLM summarization latency")

class LibraryCuratorWorker(AgentBusClient):
    """
    Autonomous worker for library curation and scholarly indexing.
    """
    
    def __init__(self, agent_did: str = "worker:library_curator:001"):
        super().__init__(agent_did)
        self.engine = None
        self.update_stream = "xnai:task_updates"

    async def start(self):
        """Main loop to fetch and process curation tasks."""
        # SI1: Start metrics exporter
        metrics_port = int(os.getenv("METRICS_PORT", 8004))
        try:
            start_http_server(metrics_port)
            logger.info(f"📊 Curation metrics exporter started on port {metrics_port}")
        except Exception as me:
            logger.warning(f"Metrics exporter failed to start: {me}")

        # Initialize Redis and Ingestion Engine
        async with self as bus:
            # Note: EnterpriseIngestionEngine needs a config dict
            from XNAi_rag_app.core.config_loader import load_config
            config = load_config()
            self.engine = EnterpriseIngestionEngine(config=config)
            logger.info(f"LibraryCuratorWorker {self.agent_did} started and listening...")
            
            while True:
                try:
                    # Check for kill switch
                    if await self.check_kill_switch():
                        logger.critical("🛑 Kill switch detected. Shutting down worker.")
                        break

                    tasks = await self.fetch_tasks(count=1)
                    for task in tasks:
                        if task["type"] == "curation_task":
                            await self._process_curation(task)
                        
                        await self.acknowledge_task(task["id"])
                    
                    await anyio.sleep(1.0)
                except Exception as e:
                    logger.error(f"LibraryCuratorWorker error: {e}")
                    await anyio.sleep(5)

    async def _process_curation(self, task: Dict[str, Any]):
        """Execute curation and post results."""
        task_id = task["id"]
        payload = task["payload"]
        sender = task["sender"]
        
        source_type = payload.get("source_type", "api") # api, rss, local
        api_name = payload.get("api_name", "gutenberg")
        query = payload.get("query")
        category = payload.get("category", "general")
        rss_urls = payload.get("rss_urls", [])
        directory = payload.get("directory")
        max_items = payload.get("max_items", 50)

        if not query and source_type == "api":
            logger.warning(f"Task {task_id} missing query for API source")
            return

        logger.info(f"Processing curation for {sender}: {source_type} (Query: '{query}', Category: '{category}')")
        
        start_process = time.time()
        try:
            stats = None
            if source_type == "api":
                stats = await self.engine.ingest_from_api(api_name, query, max_items=max_items)
            elif source_type == "local":
                stats = await self.engine.ingest_from_directory(directory)
            # RSS currently not implemented in the minimal engine restore

            # Post final result
            if stats:
                CURATOR_INGESTED.labels(source=source_type).inc(stats.total_ingested)
                CURATOR_LATENCY.observe(time.time() - start_process)
                
                await self._post_update(task_id, sender, "completed", stats)
                logger.info(f"Curation complete for task {task_id}: {stats.total_ingested} items")
            else:
                CURATOR_ERRORS.labels(source=source_type, error_type="invalid_source").inc()
                await self._post_update(task_id, sender, "failed", {"error": "Invalid source type"})

        except Exception as e:
            CURATOR_ERRORS.labels(source=source_type, error_type=type(e).__name__).inc()
            logger.error(f"Failed to process curation task {task_id}: {e}")
            await self._post_update(task_id, sender, "failed", {"error": str(e)})

    async def _post_update(self, task_id: str, target: str, status: str, result: Any):
        """Post result back to task_updates stream."""
        update = {
            "task_id": task_id,
            "target": target,
            "status": status,
            "timestamp": str(time.time())
        }
        
        if isinstance(result, IngestionStats):
            update["stats"] = json.dumps(result.to_dict())
        else:
            update["result"] = json.dumps(result)
            
        await self.redis.xadd(self.update_stream, update)

if __name__ == "__main__":
    # To run: python3 -m app.XNAi_rag_app.workers.library_curator
    import sys
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )
    worker = LibraryCuratorWorker()
    anyio.run(worker.start)
