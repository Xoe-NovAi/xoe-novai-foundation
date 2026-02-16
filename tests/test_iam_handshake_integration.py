import pytest
import os
import shutil
from datetime import datetime, timezone
from app.XNAi_rag_app.core.iam_db import IAMDatabase, AgentIdentity, AgentType
from app.XNAi_rag_app.core.iam_handshake import SovereignHandshake, KeyManager, SovereignHandshakeConfig

@pytest.fixture
def clean_comm_hub():
    """Ensure a clean communication hub for tests."""
    hub_path = SovereignHandshakeConfig.COMMUNICATION_HUB
    if os.path.exists(hub_path):
        shutil.rmtree(hub_path)
    os.makedirs(hub_path, exist_ok=True)
    yield
    # Cleanup after test
    # shutil.rmtree(hub_path)

@pytest.mark.asyncio
async def test_agent_handshake_end_to_end(clean_comm_hub):
    """Test full Ed25519 handshake between two agents."""
    # 1. Setup in-memory IAM DB
    db = IAMDatabase(":memory:")
    handshake = SovereignHandshake(db)
    
    # 2. Create Agent A (Gemini)
    priv_a, pub_a = KeyManager.generate_keypair()
    agent_a = AgentIdentity(
        did="did:xnai:gemini-test",
        agent_name="gemini",
        agent_type=AgentType.GEMINI,
        public_key_ed25519=pub_a,
        metadata={"version": "1.0"},
        created_at=datetime.now(timezone.utc).isoformat()
    )
    db.register_agent(agent_a)
    
    # 3. Create Agent B (Cline)
    priv_b, pub_b = KeyManager.generate_keypair()
    agent_b = AgentIdentity(
        did="did:xnai:cline-test",
        agent_name="cline",
        agent_type=AgentType.CLINE,
        public_key_ed25519=pub_b,
        metadata={"version": "1.0"},
        created_at=datetime.now(timezone.utc).isoformat()
    )
    db.register_agent(agent_b)
    
    # 4. Initiate Handshake (A -> B)
    nonce = handshake.initiate_handshake(
        initiator_did=agent_a.did,
        responder_did=agent_b.did,
        initiator_private_key_hex=priv_a
    )
    assert nonce is not None
    
    # 5. Respond to Challenge (B -> A)
    success = handshake.respond_to_challenge(
        challenge_nonce=nonce,
        initiator_did=agent_a.did,
        responder_did=agent_b.did,
        responder_private_key_hex=priv_b
    )
    assert success is True
    
    # 6. Verify Response (A verifies B)
    verified = handshake.verify_response(
        challenge_nonce=nonce,
        initiator_did=agent_a.did,
        responder_did=agent_b.did
    )
    assert verified is True
    
    # 7. Check final status in DB
    status = handshake.get_handshake_status(agent_a.did, agent_b.did)
    assert status["status"] == "verified"
    assert status["initiator"]["verified"] is True
    assert status["responder"]["verified"] is True
