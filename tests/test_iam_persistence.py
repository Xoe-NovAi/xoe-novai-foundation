import pytest
import sqlite3
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from XNAi_rag_app.core.iam_db import IAMDatabase, AgentIdentity, AgentType

@pytest.fixture
def temp_db_path():
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test_iam.db"

def test_iam_db_persistence(temp_db_path):
    # Pass 1: Initialize DB and write a record
    db1 = IAMDatabase(db_path=str(temp_db_path))
    
    test_did = "did:xnai:test-persistence-agent"
    test_pubkey = "test-pubkey-abc123"
    
    agent = AgentIdentity(
        did=test_did,
        agent_name="persistence-tester",
        agent_type=AgentType.SERVICE,
        public_key_ed25519=test_pubkey,
        metadata={"capabilities": ["persistence_test"]},
        created_at=datetime.utcnow().isoformat(),
        last_seen=datetime.utcnow().isoformat(),
        verified=False
    )
    
    # Register the agent
    success = db1.register_agent(agent)
    assert success is True
    
    # Update verification status
    updated = db1.update_agent_verification(test_did, True)
    assert updated is True
    
    # Close the connection to simulate restart
    db1.conn.close()
    
    # Pass 2: Reopen DB and verify data
    db2 = IAMDatabase(db_path=str(temp_db_path))
    
    retrieved_agent = db2.get_agent(test_did)
    assert retrieved_agent is not None
    assert retrieved_agent.did == test_did
    assert retrieved_agent.public_key_ed25519 == test_pubkey
    assert retrieved_agent.verified is True
    assert "persistence_test" in retrieved_agent.metadata.get("capabilities", [])
    
    db2.conn.close()
