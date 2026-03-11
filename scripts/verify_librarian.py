import asyncio
import json
import logging
from app.XNAi_rag_app.core.agent_bus import AgentBusClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("librarian_verifier")

async def verify_librarian():
    session_id = "test-session-marathon-001"
    agent_did = "tester:verifier:001"
    
    async with AgentBusClient(agent_did) as bus:
        logger.info(f"🚀 Sending session_bloat event for {session_id}...")
        task_id = await bus.emit_session_bloat(session_id, token_count=25000)
        logger.info(f"✅ Event sent. Task ID: {task_id}")
        
        logger.info("⏳ Waiting for Librarian to process (check logs)...")
        # In a real test, we would subscribe to a 'summary_completed' event
        # For this PoC, we verify via log output and filesystem check.

if __name__ == "__main__":
    asyncio.run(verify_librarian())
