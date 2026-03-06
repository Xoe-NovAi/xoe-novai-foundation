import anyio
import httpx
import logging
import os
import json
from typing import Dict, Any, List
from app.XNAi_rag_app.core.agent_bus import AgentBusClient
from app.XNAi_rag_app.core.iam_db import get_iam_database, AgentType

logger = logging.getLogger("xnai.curation_bridge")

class VikunjaCurationBridge:
    """Watches Vikunja for 'curate' tasks and triggers the Agent Bus."""
    
    def __init__(self, agent_did: str, vikunja_url: str, api_token: str):
        self.agent_did = agent_did
        self.vikunja_url = vikunja_url.rstrip('/')
        self.headers = {"Authorization": f"Bearer {api_token}"}
        self.bus = AgentBusClient(agent_did)

    async def __aenter__(self):
        await self.bus.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.bus.__aexit__(exc_type, exc_val, exc_tb)

    async def poll_curation_tasks(self):
        """Fetch tasks labeled with 'curate' from Vikunja."""
        async with httpx.AsyncClient() as client:
            try:
                # Query tasks with label 'curate' (assuming label ID 1 for PoC or name-based filter)
                # For now, we list all open tasks and filter locally for instruction 'curate:'
                response = await client.get(f"{self.vikunja_url}/api/v1/tasks/all", headers=self.headers)
                if response.status_code != 200:
                    logger.error(f"Vikunja API error: {response.status_code}")
                    return []
                
                tasks = response.json()
                curation_requests = []
                for task in tasks:
                    title = task.get("title", "")
                    if title.lower().startswith("curate:"):
                        curation_requests.append({
                            "vikunja_id": task["id"],
                            "path": title.split("curate:", 1)[1].strip(),
                            "description": task.get("description", "")
                        })
                return curation_requests
            except Exception as e:
                logger.error(f"Failed to poll Vikunja: {e}")
                return []

    async def trigger_bus_curation(self, curation_req: Dict[str, Any]):
        """Send CURATE_BOOK task to the Agent Bus."""
        payload = {
            "source_path": curation_req["path"],
            "vikunja_task_id": curation_req["vikunja_id"],
            "priority": "manual",
            "metadata": {"triggered_by": self.agent_did}
        }
        # Target the CRAWLER or a specialized CURATOR agent
        # We'll use AgentType.SERVICE for the worker
        task_id = await self.bus.send_task("*", "CURATE_BOOK", payload)
        logger.info(f"Curation task {task_id} sent for {curation_req['path']}")
        return task_id

async def run_bridge_cycle():
    # Load config from env
    token = os.getenv("VIKUNJA_API_TOKEN", "dummy_token")
    url = os.getenv("VIKUNJA_URL", "http://localhost:8000/vikunja")
    did = "did:xnai:agent:curation_bridge"
    
    async with VikunjaCurationBridge(did, url, token) as bridge:
        logger.info("Curation bridge active. Polling...")
        tasks = await bridge.poll_curation_tasks()
        for t in tasks:
            await bridge.trigger_bus_curation(t)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    anyio.run(run_bridge_cycle)
