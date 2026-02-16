#!/usr/bin/env python3
"""
Copilot-to-Gemini Sovereign Handshake Demonstration
====================================================
End-to-end proof of concept for IAM DB persistence and Ed25519 handshake.

Demonstrates:
1. Agent identity registration in SQLite DB
2. Ed25519 keypair generation
3. File-based challenge-response handshake
4. Signature verification
5. Agent verification status in DB

Execution: python3 app/XNAi_rag_app/core/test_iam_handshake.py
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.XNAi_rag_app.core.iam_db import IAMDatabase, AgentIdentity, AgentType
from app.XNAi_rag_app.core.iam_handshake import (
    SovereignHandshake,
    KeyManager,
    SovereignHandshakeConfig
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def demo_iam_db_persistence():
    """Demonstrate IAM DB persistence with agent identities"""
    print_section("1. IAM DB PERSISTENCE - Agent Identity Registration")
    
    # Create temporary database
    db_path = "data/iam_agents_demo.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    db = IAMDatabase(db_path)
    
    # Generate keypairs for Copilot and Gemini
    print("Generating Ed25519 keypairs...")
    copilot_private, copilot_public = KeyManager.generate_keypair()
    gemini_private, gemini_public = KeyManager.generate_keypair()
    
    print(f"✓ Copilot keys generated (public: {copilot_public[:16]}...)")
    print(f"✓ Gemini keys generated (public: {gemini_public[:16]}...)")
    
    # Create agent identities
    copilot_identity = AgentIdentity(
        did="did:xnai:copilot-001",
        agent_name="copilot",
        agent_type=AgentType.COPILOT,
        public_key_ed25519=copilot_public,
        metadata={
            "version": "1.0.0",
            "region": "local",
            "capabilities": ["speech-to-text", "nlp", "reasoning"]
        },
        created_at=datetime.now(timezone.utc).isoformat()
    )
    
    gemini_identity = AgentIdentity(
        did="did:xnai:gemini-001",
        agent_name="gemini",
        agent_type=AgentType.GEMINI,
        public_key_ed25519=gemini_public,
        metadata={
            "version": "1.0.0",
            "region": "local",
            "capabilities": ["text-generation", "reasoning", "multimodal"]
        },
        created_at=datetime.now(timezone.utc).isoformat()
    )
    
    # Register agents
    print("\nRegistering agents in IAM DB...")
    success_copilot = db.register_agent(copilot_identity)
    success_gemini = db.register_agent(gemini_identity)
    
    if success_copilot and success_gemini:
        print("✓ Copilot registered")
        print("✓ Gemini registered")
    else:
        print("✗ Registration failed")
        return False, db, None, None, None, None
    
    # Retrieve agents and verify
    print("\nRetrieving agents from database...")
    copilot_db = db.get_agent(copilot_identity.did)
    gemini_db = db.get_agent(gemini_identity.did)
    
    if copilot_db and gemini_db:
        print(f"✓ Copilot retrieved: {copilot_db.agent_name} ({copilot_db.did})")
        print(f"✓ Gemini retrieved: {gemini_db.agent_name} ({gemini_db.did})")
        print(f"  Copilot verified: {copilot_db.verified}")
        print(f"  Gemini verified: {gemini_db.verified}")
    else:
        print("✗ Retrieval failed")
        return False, db, None, None, None, None
    
    # List all agents
    print("\nListing all registered agents...")
    all_agents = db.list_agents()
    for agent in all_agents:
        print(f"  - {agent.agent_name} ({agent.agent_type.value}): {agent.did}")
    
    return True, db, copilot_private, gemini_private, copilot_identity, gemini_identity


def demo_sovereign_handshake(
    db: IAMDatabase,
    copilot_private: str,
    gemini_private: str,
    copilot_identity: AgentIdentity,
    gemini_identity: AgentIdentity
):
    """Demonstrate Ed25519 sovereign handshake protocol"""
    print_section("2. SOVEREIGN HANDSHAKE - Ed25519 Key Exchange")
    
    # Initialize handshake manager
    handshake = SovereignHandshake(db)
    
    print(f"Communication hub: {SovereignHandshakeConfig.COMMUNICATION_HUB}")
    print(f"State directory: {SovereignHandshakeConfig.STATE_DIR}")
    
    # Step 1: Copilot initiates handshake to Gemini
    print("\n[STEP 1] Copilot initiates challenge...")
    challenge_nonce = handshake.initiate_handshake(
        initiator_did=copilot_identity.did,
        responder_did=gemini_identity.did,
        initiator_private_key_hex=copilot_private
    )
    
    if not challenge_nonce:
        print("✗ Challenge initiation failed")
        return False
    
    print(f"✓ Challenge created with nonce: {challenge_nonce[:16]}...")
    
    # Show challenge file
    challenge_file = os.path.join(
        SovereignHandshakeConfig.CHALLENGES_DIR,
        f"{challenge_nonce}_{copilot_identity.did.replace(':', '-')}.json"
    )
    
    if os.path.exists(challenge_file):
        with open(challenge_file, 'r') as f:
            challenge_data = json.load(f)
        print(f"✓ Challenge file created: {os.path.basename(challenge_file)}")
        print(f"  - Type: {challenge_data['type']}")
        print(f"  - Challenger: {challenge_data['challenger_did']}")
        print(f"  - Signature: {challenge_data['signature'][:16]}...")
    
    # Step 2: Gemini responds to challenge
    print("\n[STEP 2] Gemini responds to challenge...")
    response_ok = handshake.respond_to_challenge(
        challenge_nonce=challenge_nonce,
        initiator_did=copilot_identity.did,
        responder_did=gemini_identity.did,
        responder_private_key_hex=gemini_private
    )
    
    if not response_ok:
        print("✗ Challenge response failed")
        return False
    
    print("✓ Response created")
    
    # Show response file
    response_file = os.path.join(
        SovereignHandshakeConfig.RESPONSES_DIR,
        f"{challenge_nonce}_{gemini_identity.did.replace(':', '-')}.json"
    )
    
    if os.path.exists(response_file):
        with open(response_file, 'r') as f:
            response_data = json.load(f)
        print(f"✓ Response file created: {os.path.basename(response_file)}")
        print(f"  - Type: {response_data['type']}")
        print(f"  - Responder: {response_data['responder_did']}")
        print(f"  - Signature: {response_data['signature'][:16]}...")
    
    # Step 3: Copilot verifies response
    print("\n[STEP 3] Copilot verifies response and marks agents as verified...")
    verify_ok = handshake.verify_response(
        challenge_nonce=challenge_nonce,
        initiator_did=copilot_identity.did,
        responder_did=gemini_identity.did
    )
    
    if not verify_ok:
        print("✗ Response verification failed")
        return False
    
    print("✓ Response verified successfully")
    
    # Check verified status in DB
    print("\nVerifying agent status in database...")
    copilot_updated = db.get_agent(copilot_identity.did)
    gemini_updated = db.get_agent(gemini_identity.did)
    
    print(f"  Copilot verified: {copilot_updated.verified} (was: {copilot_identity.verified})")
    print(f"  Gemini verified: {gemini_updated.verified} (was: {gemini_identity.verified})")
    print(f"  Copilot last_seen: {copilot_updated.last_seen}")
    print(f"  Gemini last_seen: {gemini_updated.last_seen}")
    
    if copilot_updated.verified and gemini_updated.verified:
        print("\n✓ HANDSHAKE SUCCESSFUL - Both agents verified")
        return True
    else:
        print("\n✗ Agents not marked as verified")
        return False


def demo_file_structure():
    """Display the communication hub file structure"""
    print_section("3. COMMUNICATION HUB FILE STRUCTURE")
    
    def print_tree(directory, prefix="", is_last=True):
        """Recursively print directory tree"""
        if not os.path.exists(directory):
            return
        
        items = sorted(os.listdir(directory))
        if not items:
            return
        
        for i, item in enumerate(items):
            is_last_item = (i == len(items) - 1)
            current_prefix = "└── " if is_last_item else "├── "
            print(f"{prefix}{current_prefix}{item}")
            
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                next_prefix = prefix + ("    " if is_last_item else "│   ")
                print_tree(item_path, next_prefix, is_last_item)
    
    hub_path = SovereignHandshakeConfig.COMMUNICATION_HUB
    if os.path.exists(hub_path):
        print(f"{hub_path}/")
        print_tree(hub_path)
    else:
        print(f"Communication hub not found: {hub_path}")


def cleanup_demo(db_path: str):
    """Clean up demo files"""
    if os.path.exists(db_path):
        os.remove(db_path)
        logger.info(f"Cleaned up demo database: {db_path}")


def main():
    """Run complete demonstration"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  COPILOT-TO-GEMINI SOVEREIGN HANDSHAKE DEMONSTRATION".center(68) + "║")
    print("║" + "  Phase 4.2.6: IAM DB Persistence & Key Exchange PoC".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝\n")
    
    try:
        # Phase 1: IAM DB Persistence
        db_ok, db, copilot_priv, gemini_priv, copilot_id, gemini_id = demo_iam_db_persistence()
        
        if not db_ok:
            print("\n✗ IAM DB demonstration failed")
            return 1
        
        # Phase 2: Sovereign Handshake
        handshake_ok = demo_sovereign_handshake(db, copilot_priv, gemini_priv, copilot_id, gemini_id)
        
        if not handshake_ok:
            print("\n✗ Handshake demonstration failed")
            return 1
        
        # Phase 3: File structure
        demo_file_structure()
        
        # Summary
        print_section("SUMMARY")
        print("✓ IAM Database created and populated")
        print("✓ Agent identities registered with Ed25519 public keys")
        print("✓ Sovereign handshake protocol completed")
        print("✓ Challenge-response files exchanged via file system")
        print("✓ Agent verification confirmed in database")
        print("✓ Communication hub structure created")
        
        print("\nNext Steps:")
        print("  1. Integrate IAM DB and Handshake into main application")
        print("  2. Deploy to Consul service registry")
        print("  3. Implement health checks for verified agents")
        print("  4. Add audit logging for all handshakes")
        
        # Cleanup
        print("\nCleaning up demo database...")
        cleanup_demo("data/iam_agents_demo.db")
        
        return 0
        
    except Exception as e:
        logger.error(f"Demonstration failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
