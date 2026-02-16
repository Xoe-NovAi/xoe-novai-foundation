import anyio
import json
import logging
import os
from typing import Optional, Dict, Any, List
from redis.asyncio import Redis
from app.XNAi_rag_app.core.dependencies import get_redis_client

logger = logging.getLogger(__name__)

class AgentBusClient:
    """AnyIO-wrapped Redis Stream Client for multi-agent task distribution."""
    
    def __init__(self, agent_did: str, stream_name: str = "xnai:agent_bus"):
        self.agent_did = agent_did
        self.stream_name = stream_name
        self.group_name = "agent_wavefront"
        self.redis: Optional[Redis] = None

    async def __aenter__(self):
        host = os.getenv("REDIS_HOST", "localhost")
        password = os.getenv("REDIS_PASSWORD")
        self.redis = Redis(host=host, password=password, decode_responses=False)
        # Initialize Group
        try:
            await self.redis.xgroup_create(self.stream_name, self.group_name, id="0", mkstream=True)
        except Exception:
            # Group likely already exists
            pass
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.redis:
            await self.redis.aclose()

    async def send_task(self, target_did: str, task_type: str, payload: Dict[str, Any]) -> str:
        """Add a task to the stream."""
        message = {
            "sender": self.agent_did,
            "target": target_did,
            "type": task_type,
            "payload": json.dumps(payload),
            "status": "pending"
        }
        task_id = await self.redis.xadd(self.stream_name, message)
        logger.info(f"Task sent: {task_id} from {self.agent_did} to {target_did}")
        return task_id

    async def fetch_tasks(self, count: int = 1) -> List[Dict[str, Any]]:
        """Fetch tasks assigned to this agent or global tasks (target='*')."""
        # 1. Recover from PEL (Pending Entries List)
        # 2. Fetch new messages ('>')
        tasks = []
        
        # Pattern: Read from PEL first, then new
        for read_id in ["0", ">"]:
            response = await self.redis.xreadgroup(
                groupname=self.group_name,
                consumername=self.agent_did,
                streams={self.stream_name: read_id},
                count=count,
                block=1000 if read_id == ">" else None
            )
            
            if response:
                for _, messages in response:
                    for msg_id, data in messages:
                        # Filter for this agent or broadcast
                        target = data.get(b"target", b"*").decode()
                        if target == self.agent_did or target == "*":
                            tasks.append({
                                "id": msg_id.decode(),
                                "sender": data.get(b"sender").decode(),
                                "type": data.get(b"type").decode(),
                                "payload": json.loads(data.get(b"payload").decode())
                            })
        return tasks

    async def acknowledge_task(self, task_id: str):
        """Acknowledge task completion."""
        await self.redis.xack(self.stream_name, self.group_name, task_id)
        logger.debug(f"Task acknowledged: {task_id}")
