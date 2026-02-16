import pytest
import anyio
import os
from datetime import datetime, timezone
from app.XNAi_rag_app.core.iam_db import IAMDatabase, AgentIdentity, AgentType
from app.XNAi_rag_app.core.agent_orchestrator import AgentOrchestrator
from app.XNAi_rag_app.core.iam_handshake import KeyManager

async def test_orchestrator_handoff():
    """Test full delegation/handoff flow via Orchestrator."""
    os.environ["REDIS_HOST"] = "localhost"
    os.environ["REDIS_PASSWORD"] = "changeme123"
    
    db_path = "data/test_orchestrator.db"
    if os.path.exists(db_path): os.remove(db_path)
    db = IAMDatabase(db_path)
    
    # Register Gemini and Cline
    priv_gem, pub_gem = KeyManager.generate_keypair()
    priv_cli, pub_cli = KeyManager.generate_keypair()
    
    gemini = AgentIdentity(
        did="did:xnai:agent:gemini:orch", agent_name="gemini_orch",
        agent_type=AgentType.GEMINI, public_key_ed25519=pub_gem,
        metadata={}, created_at=datetime.now(timezone.utc).isoformat()
    )
    cline = AgentIdentity(
        did="did:xnai:agent:cline:orch", agent_name="cline_orch",
        agent_type=AgentType.CLINE, public_key_ed25519=pub_cli,
        metadata={}, created_at=datetime.now(timezone.utc).isoformat()
    )
    db.register_agent(gemini)
    db.register_agent(cline)
    
    # Initialize Orchestrator for Gemini
    async with AgentOrchestrator(gemini.did, priv_gem, iam_db=db) as orch:
        # 1. Test Resource Locking
        locked = await orch.acquire_resource_lock("gpu_cluster", timeout=5)
        assert locked is True
        
        # 2. Test Delegation (Handoff)
        session_id = "sess_orch_001"
        context_data = {"step": "research_complete", "next_step": "implementation"}
        
        success = await orch.delegate_task(AgentType.CLINE, session_id, context_data)
        assert success is True
        
        # 3. Verify as Cline
        async with AgentOrchestrator(cline.did, priv_cli, iam_db=db) as cline_orch:
            # Fetch delegation task
            tasks = await cline_orch.bus.fetch_tasks()
            assert len(tasks) > 0
            assert tasks[0]["type"] == "DELEGATE"
            
            # Load shared context
            loaded_context = await cline_orch.sync.load_context(session_id, pub_gem)
            assert loaded_context == context_data
            
            await cline_orch.bus.acknowledge_task(tasks[0]["id"])

    db.close()
    if os.path.exists(db_path): os.remove(db_path)
    print("\n✓ Orchestrator Handoff: SUCCESSFUL")

if __name__ == "__main__":
    anyio.run(test_orchestrator_handoff)
