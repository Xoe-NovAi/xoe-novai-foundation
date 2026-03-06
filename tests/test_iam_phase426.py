#!/usr/bin/env python3
"""
Unit tests for Phase 4.2.6: IAM DB Persistence & Sovereign Handshake

Test Coverage:
- IAM Database CRUD operations
- Ed25519 key generation and serialization
- Challenge-response handshake protocol
- Signature verification
- Agent verification status
"""

import os
import json
import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timezone

from app.XNAi_rag_app.core.iam_db import (
    IAMDatabase,
    AgentIdentity,
    AgentType,
    get_iam_database
)
from app.XNAi_rag_app.core.iam_handshake import (
    KeyManager,
    ChallengeData,
    ResponseData,
    SovereignHandshake,
    SovereignHandshakeConfig
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    db = IAMDatabase(db_path)
    yield db
    
    # Close database connection
    db.close()
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)
    if os.path.exists(f"{db_path}-wal"):
        os.remove(f"{db_path}-wal")
    if os.path.exists(f"{db_path}-shm"):
        os.remove(f"{db_path}-shm")


@pytest.fixture
def temp_comm_hub(monkeypatch):
    """Create temporary communication hub for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("COMMUNICATION_HUB_PATH", tmpdir)
        # Reload config to pick up environment variable
        import importlib
        import app.XNAi_rag_app.core.iam_handshake as hs_module
        original_hub = SovereignHandshakeConfig.COMMUNICATION_HUB
        original_state = SovereignHandshakeConfig.STATE_DIR
        
        SovereignHandshakeConfig.COMMUNICATION_HUB = tmpdir
        SovereignHandshakeConfig.STATE_DIR = os.path.join(tmpdir, "state")
        SovereignHandshakeConfig.CHALLENGES_DIR = os.path.join(tmpdir, "state", "challenges")
        SovereignHandshakeConfig.RESPONSES_DIR = os.path.join(tmpdir, "state", "responses")
        SovereignHandshakeConfig.VERIFIED_DIR = os.path.join(tmpdir, "state", "verified")
        
        yield tmpdir
        
        # Restore original config
        SovereignHandshakeConfig.COMMUNICATION_HUB = original_hub
        SovereignHandshakeConfig.STATE_DIR = original_state


@pytest.fixture
def sample_agents(temp_db):
    """Create sample agents for testing"""
    copilot_priv, copilot_pub = KeyManager.generate_keypair()
    gemini_priv, gemini_pub = KeyManager.generate_keypair()
    
    copilot = AgentIdentity(
        did="did:xnai:copilot-test",
        agent_name="copilot-test",
        agent_type=AgentType.COPILOT,
        public_key_ed25519=copilot_pub,
        metadata={"test": True},
        created_at=datetime.now(timezone.utc).isoformat()
    )
    
    gemini = AgentIdentity(
        did="did:xnai:gemini-test",
        agent_name="gemini-test",
        agent_type=AgentType.GEMINI,
        public_key_ed25519=gemini_pub,
        metadata={"test": True},
        created_at=datetime.now(timezone.utc).isoformat()
    )
    
    temp_db.register_agent(copilot)
    temp_db.register_agent(gemini)
    
    return {
        "copilot": {"identity": copilot, "private_key": copilot_priv},
        "gemini": {"identity": gemini, "private_key": gemini_priv}
    }


# ============================================================================
# Tests: IAM Database
# ============================================================================

class TestIAMDatabase:
    """Test IAM database operations"""
    
    def test_database_initialization(self, temp_db):
        """Test database is properly initialized"""
        assert os.path.exists(temp_db.db_path)
    
    def test_register_agent(self, temp_db):
        """Test agent registration"""
        _, pub_key = KeyManager.generate_keypair()
        agent = AgentIdentity(
            did="did:test:agent-001",
            agent_name="test-agent",
            agent_type=AgentType.SERVICE,
            public_key_ed25519=pub_key,
            metadata={"test": True},
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        success = temp_db.register_agent(agent)
        assert success is True
    
    def test_get_agent_by_did(self, temp_db, sample_agents):
        """Test retrieval by DID"""
        copilot_did = sample_agents["copilot"]["identity"].did
        agent = temp_db.get_agent(copilot_did)
        
        assert agent is not None
        assert agent.did == copilot_did
        assert agent.agent_name == "copilot-test"
        assert agent.agent_type == AgentType.COPILOT
    
    def test_get_agent_by_name(self, temp_db, sample_agents):
        """Test retrieval by name and type"""
        agent = temp_db.get_agent_by_name("copilot-test", AgentType.COPILOT)
        
        assert agent is not None
        assert agent.agent_name == "copilot-test"
    
    def test_list_agents(self, temp_db, sample_agents):
        """Test listing all agents"""
        all_agents = temp_db.list_agents()
        assert len(all_agents) == 2
    
    def test_list_agents_by_type(self, temp_db, sample_agents):
        """Test listing agents filtered by type"""
        copilot_agents = temp_db.list_agents(AgentType.COPILOT)
        assert len(copilot_agents) == 1
        assert copilot_agents[0].agent_type == AgentType.COPILOT
    
    def test_update_agent_verification(self, temp_db, sample_agents):
        """Test marking agent as verified"""
        copilot_did = sample_agents["copilot"]["identity"].did
        
        # Initially not verified
        agent = temp_db.get_agent(copilot_did)
        assert agent.verified is False
        
        # Mark as verified
        success = temp_db.update_agent_verification(copilot_did, True)
        assert success is True
        
        # Verify status changed
        agent = temp_db.get_agent(copilot_did)
        assert agent.verified is True
    
    def test_update_agent_last_seen(self, temp_db, sample_agents):
        """Test updating last seen timestamp"""
        copilot_did = sample_agents["copilot"]["identity"].did
        
        agent = temp_db.get_agent(copilot_did)
        assert agent.last_seen is None
        
        success = temp_db.update_agent_last_seen(copilot_did)
        assert success is True
        
        agent = temp_db.get_agent(copilot_did)
        assert agent.last_seen is not None
    
    def test_delete_agent(self, temp_db, sample_agents):
        """Test agent deletion"""
        copilot_did = sample_agents["copilot"]["identity"].did
        
        # Verify agent exists
        agent = temp_db.get_agent(copilot_did)
        assert agent is not None
        
        # Delete
        success = temp_db.delete_agent(copilot_did)
        assert success is True
        
        # Verify deleted
        agent = temp_db.get_agent(copilot_did)
        assert agent is None


# ============================================================================
# Tests: Key Management
# ============================================================================

class TestKeyManager:
    """Test Ed25519 key operations"""
    
    def test_generate_keypair(self):
        """Test keypair generation"""
        private_key, public_key = KeyManager.generate_keypair()
        
        assert isinstance(private_key, str)
        assert isinstance(public_key, str)
        assert len(private_key) == 64  # 32 bytes * 2 (hex)
        assert len(public_key) == 64   # 32 bytes * 2 (hex)
    
    def test_load_private_key(self):
        """Test loading private key"""
        private_hex, _ = KeyManager.generate_keypair()
        
        key = KeyManager.load_private_key(private_hex)
        assert key is not None
    
    def test_load_public_key(self):
        """Test loading public key"""
        _, public_hex = KeyManager.generate_keypair()
        
        key = KeyManager.load_public_key(public_hex)
        assert key is not None
    
    def test_sign_message(self):
        """Test message signing"""
        private_hex, _ = KeyManager.generate_keypair()
        message = b"test message"
        
        signature = KeyManager.sign_message(private_hex, message)
        
        assert isinstance(signature, str)
        assert len(signature) > 0
    
    def test_verify_signature_valid(self):
        """Test valid signature verification"""
        private_hex, public_hex = KeyManager.generate_keypair()
        message = b"test message"
        
        signature = KeyManager.sign_message(private_hex, message)
        is_valid = KeyManager.verify_signature(public_hex, message, signature)
        
        assert is_valid is True
    
    def test_verify_signature_invalid(self):
        """Test invalid signature rejection"""
        private_hex, public_hex = KeyManager.generate_keypair()
        message = b"test message"
        
        signature = KeyManager.sign_message(private_hex, message)
        
        # Verify with different message
        is_valid = KeyManager.verify_signature(public_hex, b"different message", signature)
        assert is_valid is False
    
    def test_verify_signature_wrong_key(self):
        """Test signature verification with wrong key"""
        private_hex1, public_hex1 = KeyManager.generate_keypair()
        _, public_hex2 = KeyManager.generate_keypair()
        message = b"test message"
        
        signature = KeyManager.sign_message(private_hex1, message)
        
        # Verify with different public key
        is_valid = KeyManager.verify_signature(public_hex2, message, signature)
        assert is_valid is False


# ============================================================================
# Tests: Challenge and Response Data
# ============================================================================

class TestChallengeAndResponseData:
    """Test challenge and response message structures"""
    
    def test_create_challenge(self):
        """Test challenge creation"""
        did = "did:test:agent"
        challenge = ChallengeData.create(did)
        
        assert challenge["type"] == "challenge"
        assert challenge["challenger_did"] == did
        assert "challenge_nonce" in challenge
        assert "timestamp" in challenge
        assert "expires_at" in challenge
    
    def test_challenge_to_bytes(self):
        """Test challenge serialization"""
        challenge = ChallengeData.create("did:test:agent")
        data_bytes = ChallengeData.to_bytes(challenge)
        
        assert isinstance(data_bytes, bytes)
        assert len(data_bytes) > 0
    
    def test_challenge_bytes_consistency(self):
        """Test challenge serialization is consistent"""
        challenge = ChallengeData.create("did:test:agent", challenge_nonce="fixed-nonce")
        
        bytes1 = ChallengeData.to_bytes(challenge)
        bytes2 = ChallengeData.to_bytes(challenge)
        
        assert bytes1 == bytes2
    
    def test_create_response(self):
        """Test response creation"""
        response = ResponseData.create(
            responder_did="did:test:responder",
            challenge_nonce="test-nonce",
            challenge_signature="test-sig"
        )
        
        assert response["type"] == "response"
        assert response["responder_did"] == "did:test:responder"
        assert response["challenge_nonce"] == "test-nonce"
        assert "timestamp" in response
    
    def test_response_to_bytes(self):
        """Test response serialization"""
        response = ResponseData.create(
            responder_did="did:test:responder",
            challenge_nonce="test-nonce",
            challenge_signature="test-sig"
        )
        data_bytes = ResponseData.to_bytes(response)
        
        assert isinstance(data_bytes, bytes)
        assert len(data_bytes) > 0


# ============================================================================
# Tests: Sovereign Handshake
# ============================================================================

class TestSovereignHandshake:
    """Test handshake protocol"""
    
    def test_handshake_initialization(self, temp_db, temp_comm_hub):
        """Test handshake initialization"""
        handshake = SovereignHandshake(temp_db)
        assert handshake is not None
        assert os.path.exists(SovereignHandshakeConfig.CHALLENGES_DIR)
        assert os.path.exists(SovereignHandshakeConfig.RESPONSES_DIR)
        assert os.path.exists(SovereignHandshakeConfig.VERIFIED_DIR)
    
    def test_initiate_handshake(self, temp_db, temp_comm_hub, sample_agents):
        """Test initiating handshake"""
        handshake = SovereignHandshake(temp_db)
        
        copilot = sample_agents["copilot"]
        gemini = sample_agents["gemini"]
        
        challenge_nonce = handshake.initiate_handshake(
            initiator_did=copilot["identity"].did,
            responder_did=gemini["identity"].did,
            initiator_private_key_hex=copilot["private_key"]
        )
        
        assert challenge_nonce is not None
        
        # Verify challenge file exists
        challenge_filename = f"{challenge_nonce}_{copilot['identity'].did.replace(':', '-')}.json"
        challenge_path = os.path.join(SovereignHandshakeConfig.CHALLENGES_DIR, challenge_filename)
        assert os.path.exists(challenge_path)
    
    def test_respond_to_challenge(self, temp_db, temp_comm_hub, sample_agents):
        """Test responding to challenge"""
        handshake = SovereignHandshake(temp_db)
        
        copilot = sample_agents["copilot"]
        gemini = sample_agents["gemini"]
        
        # Initiate
        challenge_nonce = handshake.initiate_handshake(
            initiator_did=copilot["identity"].did,
            responder_did=gemini["identity"].did,
            initiator_private_key_hex=copilot["private_key"]
        )
        
        # Respond
        success = handshake.respond_to_challenge(
            challenge_nonce=challenge_nonce,
            initiator_did=copilot["identity"].did,
            responder_did=gemini["identity"].did,
            responder_private_key_hex=gemini["private_key"]
        )
        
        assert success is True
        
        # Verify response file exists
        response_filename = f"{challenge_nonce}_{gemini['identity'].did.replace(':', '-')}.json"
        response_path = os.path.join(SovereignHandshakeConfig.RESPONSES_DIR, response_filename)
        assert os.path.exists(response_path)
    
    def test_verify_response(self, temp_db, temp_comm_hub, sample_agents):
        """Test verifying response"""
        handshake = SovereignHandshake(temp_db)
        
        copilot = sample_agents["copilot"]
        gemini = sample_agents["gemini"]
        
        # Initiate
        challenge_nonce = handshake.initiate_handshake(
            initiator_did=copilot["identity"].did,
            responder_did=gemini["identity"].did,
            initiator_private_key_hex=copilot["private_key"]
        )
        
        # Respond
        handshake.respond_to_challenge(
            challenge_nonce=challenge_nonce,
            initiator_did=copilot["identity"].did,
            responder_did=gemini["identity"].did,
            responder_private_key_hex=gemini["private_key"]
        )
        
        # Verify
        success = handshake.verify_response(
            challenge_nonce=challenge_nonce,
            initiator_did=copilot["identity"].did,
            responder_did=gemini["identity"].did
        )
        
        assert success is True
    
    def test_agents_marked_verified(self, temp_db, temp_comm_hub, sample_agents):
        """Test agents are marked as verified after handshake"""
        handshake = SovereignHandshake(temp_db)
        
        copilot = sample_agents["copilot"]
        gemini = sample_agents["gemini"]
        
        # Verify not verified initially
        copilot_agent = temp_db.get_agent(copilot["identity"].did)
        gemini_agent = temp_db.get_agent(gemini["identity"].did)
        assert copilot_agent.verified is False
        assert gemini_agent.verified is False
        
        # Complete handshake
        challenge_nonce = handshake.initiate_handshake(
            initiator_did=copilot["identity"].did,
            responder_did=gemini["identity"].did,
            initiator_private_key_hex=copilot["private_key"]
        )
        
        handshake.respond_to_challenge(
            challenge_nonce=challenge_nonce,
            initiator_did=copilot["identity"].did,
            responder_did=gemini["identity"].did,
            responder_private_key_hex=gemini["private_key"]
        )
        
        handshake.verify_response(
            challenge_nonce=challenge_nonce,
            initiator_did=copilot["identity"].did,
            responder_did=gemini["identity"].did
        )
        
        # Verify both are marked verified
        copilot_agent = temp_db.get_agent(copilot["identity"].did)
        gemini_agent = temp_db.get_agent(gemini["identity"].did)
        assert copilot_agent.verified is True
        assert gemini_agent.verified is True
    
    def test_get_handshake_status(self, temp_db, temp_comm_hub, sample_agents):
        """Test getting handshake status"""
        handshake = SovereignHandshake(temp_db)
        
        copilot = sample_agents["copilot"]
        gemini = sample_agents["gemini"]
        
        # Before handshake
        status = handshake.get_handshake_status(
            copilot["identity"].did,
            gemini["identity"].did
        )
        assert status["status"] == "unverified"
        
        # Complete handshake
        challenge_nonce = handshake.initiate_handshake(
            initiator_did=copilot["identity"].did,
            responder_did=gemini["identity"].did,
            initiator_private_key_hex=copilot["private_key"]
        )
        
        handshake.respond_to_challenge(
            challenge_nonce=challenge_nonce,
            initiator_did=copilot["identity"].did,
            responder_did=gemini["identity"].did,
            responder_private_key_hex=gemini["private_key"]
        )
        
        handshake.verify_response(
            challenge_nonce=challenge_nonce,
            initiator_did=copilot["identity"].did,
            responder_did=gemini["identity"].did
        )
        
        # After handshake
        status = handshake.get_handshake_status(
            copilot["identity"].did,
            gemini["identity"].did
        )
        assert status["status"] == "verified"


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for full workflow"""
    
    def test_end_to_end_handshake(self, temp_db, temp_comm_hub):
        """Test complete end-to-end handshake workflow"""
        # Generate keypairs
        copilot_priv, copilot_pub = KeyManager.generate_keypair()
        gemini_priv, gemini_pub = KeyManager.generate_keypair()
        
        # Register agents
        copilot = AgentIdentity(
            did="did:xnai:copilot-e2e",
            agent_name="copilot-e2e",
            agent_type=AgentType.COPILOT,
            public_key_ed25519=copilot_pub,
            metadata={},
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        gemini = AgentIdentity(
            did="did:xnai:gemini-e2e",
            agent_name="gemini-e2e",
            agent_type=AgentType.GEMINI,
            public_key_ed25519=gemini_pub,
            metadata={},
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        temp_db.register_agent(copilot)
        temp_db.register_agent(gemini)
        
        # Execute handshake
        handshake = SovereignHandshake(temp_db)
        
        challenge_nonce = handshake.initiate_handshake(
            initiator_did=copilot.did,
            responder_did=gemini.did,
            initiator_private_key_hex=copilot_priv
        )
        
        assert challenge_nonce is not None
        
        response_ok = handshake.respond_to_challenge(
            challenge_nonce=challenge_nonce,
            initiator_did=copilot.did,
            responder_did=gemini.did,
            responder_private_key_hex=gemini_priv
        )
        
        assert response_ok is True
        
        verify_ok = handshake.verify_response(
            challenge_nonce=challenge_nonce,
            initiator_did=copilot.did,
            responder_did=gemini.did
        )
        
        assert verify_ok is True
        
        # Verify final state
        copilot_final = temp_db.get_agent(copilot.did)
        gemini_final = temp_db.get_agent(gemini.did)
        
        assert copilot_final.verified is True
        assert gemini_final.verified is True
        assert copilot_final.last_seen is not None
        assert gemini_final.last_seen is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
