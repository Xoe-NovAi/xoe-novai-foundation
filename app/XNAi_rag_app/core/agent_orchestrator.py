import anyio
import logging
import json
from typing import Optional, Dict, Any, List
from app.XNAi_rag_app.core.agent_bus import AgentBusClient
from app.XNAi_rag_app.core.context_sync import ContextSyncEngine
from app.XNAi_rag_app.core.iam_db import get_iam_database, AgentType, IAMDatabase

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Orchestrates multi-agent handoffs, capability discovery, and resource locking."""
    
    def __init__(self, agent_did: str, private_key_hex: str, iam_db: Optional[IAMDatabase] = None):
        self.agent_did = agent_did
        self.private_key_hex = private_key_hex
        self.bus = AgentBusClient(agent_did)
        self.sync = ContextSyncEngine(agent_did)
        self.iam = iam_db or get_iam_database()

    async def __aenter__(self):
        await self.bus.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.bus.__aexit__(exc_type, exc_val, exc_tb)

    async def delegate_task(self, target_agent_type: AgentType, session_id: str, context_data: Dict[str, Any]):
        """Perform a stateful handoff to another agent type."""
        # 1. Discover target agent
        target_agents = self.iam.list_agents(agent_type=target_agent_type)
        if not target_agents:
            logger.error(f"No agents found for type: {target_agent_type}")
            return False
        
        target_did = target_agents[0].did  # Take the first available
        
        # 2. Save and Sign Context
        await self.sync.save_context(session_id, context_data, self.private_key_hex)
        
        # 3. Send DELEGATE task via Bus
        task_payload = {
            "session_id": session_id,
            "instruction": "Continue task from shared context."
        }
        await self.bus.send_task(target_did, "DELEGATE", task_payload)
        logger.info(f"Handoff initiated: {self.agent_did} -> {target_did} (Session: {session_id})")
        return True

    async def acquire_resource_lock(self, resource_name: str, timeout: int = 10) -> bool:
        """Acquire a global resource lock in Redis (Conflict Resolution)."""
        lock_key = f"xnai:lock:{resource_name}"
        # Set lock with TTL to prevent deadlocks
        success = await self.bus.redis.set(lock_key, self.agent_did, ex=timeout, nx=True)
        if success:
            logger.info(f"Resource lock acquired: {resource_name} by {self.agent_did}")
        else:
            current_owner = await self.bus.redis.get(lock_key)
            logger.warning(f"Resource contention: {resource_name} owned by {current_owner.decode() if current_owner else 'unknown'}")
        return bool(success)

    async def release_resource_lock(self, resource_name: str):
        """Release a global resource lock."""
        lock_key = f"xnai:lock:{resource_name}"
        await self.bus.redis.delete(lock_key)
        logger.info(f"Resource lock released: {resource_name}")
