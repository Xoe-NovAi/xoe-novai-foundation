import pytest
import anyio
import json
import os
from datetime import datetime, timezone
from app.XNAi_rag_app.core.iam_db import IAMDatabase, AgentIdentity, AgentType
from app.XNAi_rag_app.core.agent_bus import AgentBusClient
from app.XNAi_rag_app.core.iam_handshake import KeyManager
from app.XNAi_rag_app.core.context_sync import ContextSyncEngine

async def test_phase5_integrated_flow():
    """Test the integrated Phase 5 flow: IAM -> Bus -> Context Sync."""
    # Force reset redis dependencies
    from app.XNAi_rag_app.core import dependencies
    dependencies._redis_client = None
    os.environ["REDIS_HOST"] = "localhost"

    db_path = "data/test_iam_v2.db"
    if os.path.exists(db_path): os.remove(db_path)
    
    db = IAMDatabase(db_path)
    
    # 1. Register a Human-Controlled Agent
    priv_gem, pub_gem = KeyManager.generate_keypair()
    gemini = AgentIdentity(
        did="did:xnai:agent:gemini:test",
        agent_name="gemini_test",
        agent_type=AgentType.GEMINI,
        public_key_ed25519=pub_gem,
        metadata={"version": "2.0"},
        created_at=datetime.now(timezone.utc).isoformat(),
        controller_did="did:xnai:human:arcana",
        relationship_type="owner"
    )
    db.register_agent(gemini)
    
    # 2. Test Agent Bus
    async with AgentBusClient(gemini.did) as bus:
        task_payload = {"cmd": "research", "topic": "anyio"}
        task_id = await bus.send_task("did:xnai:agent:cline:test", "research_task", task_payload)
        
        # Fetch tasks as Cline (mock)
        async with AgentBusClient("did:xnai:agent:cline:test") as cline_bus:
            tasks = await cline_bus.fetch_tasks()
            assert len(tasks) > 0
            assert tasks[0]["sender"] == gemini.did
            await cline_bus.acknowledge_task(tasks[0]["id"])

    # 3. Test Context Sync
    sync = ContextSyncEngine(gemini.did, context_dir="communication_hub/state/test_contexts")
    session_id = "sess_001"
    context_data = {"active_task": "bus_scaling", "history": ["msg1", "msg2"]}
    
    await sync.save_context(session_id, context_data, priv_gem)
    
    # Load and verify as another agent
    loaded_context = await sync.load_context(session_id, pub_gem)
    assert loaded_context == context_data
    assert loaded_context["active_task"] == "bus_scaling"

    db.close()
    if os.path.exists(db_path): os.remove(db_path)
    print("\n✓ Phase 5 Integrated Flow: SUCCESSFUL")

if __name__ == "__main__":
    anyio.run(test_phase5_integrated_flow)
