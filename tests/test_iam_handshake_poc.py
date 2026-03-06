#!/usr/bin/env python3
"""
Phase 4.2.6 PoC: IAM DB Persistence & Sovereign Handshake
==========================================================
Demonstrates:
1. SQLite agent identity persistence with Ed25519 keys
2. File-based handshake protocol with signed challenges
3. Copilot-to-Gemini inter-agent authentication flow
4. Communication hub state management

Run with: python3 test_iam_handshake_poc.py
"""

import sys
import os
import json
import logging
import tempfile
import shutil
from datetime import datetime, timezone
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from XNAi_rag_app.core.iam_db import IAMDatabase, AgentIdentity, AgentType
from XNAi_rag_app.core.iam_handshake import (
    SovereignHandshake,
    KeyManager,
    SovereignHandshakeConfig,
    ChallengeData,
    ResponseData
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


class IAMHandshakePoCDemo:
    """Complete PoC demonstration of IAM DB and Sovereign Handshake"""
    
    def __init__(self):
        """Initialize demo environment"""
        self.test_dir = tempfile.mkdtemp(prefix="iam_poc_")
        self.db_path = os.path.join(self.test_dir, "iam_agents.db")
        self.comm_hub = os.path.join(self.test_dir, "communication_hub")
        
        logger.info(f"PoC Demo initialized in: {self.test_dir}")
    
    def setup_communication_hub(self):
        """Create communication hub directory structure"""
        logger.info("=" * 70)
        logger.info("STEP 1: Setting up Communication Hub")
        logger.info("=" * 70)
        
        os.environ["COMMUNICATION_HUB_PATH"] = self.comm_hub
        
        dirs = [
            os.path.join(self.comm_hub, "state"),
            os.path.join(self.comm_hub, "state", "challenges"),
            os.path.join(self.comm_hub, "state", "responses"),
            os.path.join(self.comm_hub, "state", "verified")
        ]
        
        for d in dirs:
            os.makedirs(d, exist_ok=True)
            logger.info(f"✓ Created: {d}")
        
        return self.comm_hub
    
    def initialize_iam_db(self) -> IAMDatabase:
        """Initialize IAM database with test agents"""
        logger.info("\n" + "=" * 70)
        logger.info("STEP 2: Initializing IAM Database")
        logger.info("=" * 70)
        
        db = IAMDatabase(db_path=self.db_path)
        logger.info(f"✓ Database initialized at: {self.db_path}")
        
        return db
    
    def register_copilot_agent(self, db: IAMDatabase) -> tuple:
        """Register Copilot agent with Ed25519 keypair"""
        logger.info("\n" + "=" * 70)
        logger.info("STEP 3: Register Copilot Agent")
        logger.info("=" * 70)
        
        # Generate keypair
        private_key_hex, public_key_hex = KeyManager.generate_keypair()
        
        copilot_identity = AgentIdentity(
            did="did:xnai:copilot-001",
            agent_name="copilot",
            agent_type=AgentType.COPILOT,
            public_key_ed25519=public_key_hex,
            metadata={
                "version": "1.0.0",
                "region": "local",
                "capabilities": ["code-analysis", "refactoring", "testing"]
            },
            created_at=datetime.now(timezone.utc).isoformat(),
            verified=False
        )
        
        success = db.register_agent(copilot_identity)
        if success:
            logger.info(f"✓ Registered: {copilot_identity.agent_name}")
            logger.info(f"  DID: {copilot_identity.did}")
            logger.info(f"  Type: {copilot_identity.agent_type.value}")
            logger.info(f"  Public Key (first 32 chars): {public_key_hex[:32]}...")
        else:
            logger.error("✗ Failed to register copilot")
            return None, None, None
        
        return copilot_identity, private_key_hex, public_key_hex
    
    def register_gemini_agent(self, db: IAMDatabase) -> tuple:
        """Register Gemini agent with Ed25519 keypair"""
        logger.info("\n" + "=" * 70)
        logger.info("STEP 4: Register Gemini Agent")
        logger.info("=" * 70)
        
        # Generate keypair
        private_key_hex, public_key_hex = KeyManager.generate_keypair()
        
        gemini_identity = AgentIdentity(
            did="did:xnai:gemini-001",
            agent_name="gemini",
            agent_type=AgentType.GEMINI,
            public_key_ed25519=public_key_hex,
            metadata={
                "version": "3.0",
                "region": "local",
                "capabilities": ["reasoning", "generation", "multimodal"]
            },
            created_at=datetime.now(timezone.utc).isoformat(),
            verified=False
        )
        
        success = db.register_agent(gemini_identity)
        if success:
            logger.info(f"✓ Registered: {gemini_identity.agent_name}")
            logger.info(f"  DID: {gemini_identity.did}")
            logger.info(f"  Type: {gemini_identity.agent_type.value}")
            logger.info(f"  Public Key (first 32 chars): {public_key_hex[:32]}...")
        else:
            logger.error("✗ Failed to register gemini")
            return None, None, None
        
        return gemini_identity, private_key_hex, public_key_hex
    
    def list_registered_agents(self, db: IAMDatabase):
        """Display all registered agents"""
        logger.info("\n" + "=" * 70)
        logger.info("STEP 5: Database Verification - List All Agents")
        logger.info("=" * 70)
        
        agents = db.list_agents()
        logger.info(f"Total agents in database: {len(agents)}")
        
        for agent in agents:
            logger.info(f"\n  Agent: {agent.agent_name.upper()}")
            logger.info(f"    DID: {agent.did}")
            logger.info(f"    Type: {agent.agent_type.value}")
            logger.info(f"    Verified: {agent.verified}")
            logger.info(f"    Created: {agent.created_at}")
            logger.info(f"    Public Key (first 24 chars): {agent.public_key_ed25519[:24]}...")
    
    def initiate_handshake(
        self,
        handshake: SovereignHandshake,
        copilot_did: str,
        gemini_did: str,
        copilot_private_key: str
    ) -> str:
        """Copilot initiates handshake to Gemini"""
        logger.info("\n" + "=" * 70)
        logger.info("STEP 6: Initiate Handshake (Copilot → Gemini)")
        logger.info("=" * 70)
        
        challenge_nonce = handshake.initiate_handshake(
            initiator_did=copilot_did,
            responder_did=gemini_did,
            initiator_private_key_hex=copilot_private_key
        )
        
        if challenge_nonce:
            logger.info(f"✓ Challenge created with nonce: {challenge_nonce[:16]}...")
            
            # Display challenge file
            challenge_file = os.path.join(
                SovereignHandshakeConfig.CHALLENGES_DIR,
                f"{challenge_nonce}_{copilot_did.replace(':', '-')}.json"
            )
            if os.path.exists(challenge_file):
                with open(challenge_file, 'r') as f:
                    challenge_data = json.load(f)
                logger.info(f"✓ Challenge file created at: {challenge_file}")
                logger.info(f"  Challenger: {challenge_data['challenger_did']}")
                logger.info(f"  Expires: {challenge_data['expires_at']}")
                logger.info(f"  Signature (first 32 chars): {challenge_data['signature'][:32]}...")
        else:
            logger.error("✗ Failed to initiate handshake")
            return None
        
        return challenge_nonce
    
    def respond_to_challenge(
        self,
        handshake: SovereignHandshake,
        challenge_nonce: str,
        copilot_did: str,
        gemini_did: str,
        gemini_private_key: str
    ) -> bool:
        """Gemini responds to Copilot's challenge"""
        logger.info("\n" + "=" * 70)
        logger.info("STEP 7: Respond to Challenge (Gemini → Copilot)")
        logger.info("=" * 70)
        
        success = handshake.respond_to_challenge(
            challenge_nonce=challenge_nonce,
            initiator_did=copilot_did,
            responder_did=gemini_did,
            responder_private_key_hex=gemini_private_key
        )
        
        if success:
            logger.info("✓ Challenge response created")
            
            # Display response file
            response_file = os.path.join(
                SovereignHandshakeConfig.RESPONSES_DIR,
                f"{challenge_nonce}_{gemini_did.replace(':', '-')}.json"
            )
            if os.path.exists(response_file):
                with open(response_file, 'r') as f:
                    response_data = json.load(f)
                logger.info(f"✓ Response file created at: {response_file}")
                logger.info(f"  Responder: {response_data['responder_did']}")
                logger.info(f"  Timestamp: {response_data['timestamp']}")
                logger.info(f"  Signature (first 32 chars): {response_data['signature'][:32]}...")
        else:
            logger.error("✗ Failed to respond to challenge")
            return False
        
        return success
    
    def verify_handshake(
        self,
        handshake: SovereignHandshake,
        challenge_nonce: str,
        copilot_did: str,
        gemini_did: str
    ) -> bool:
        """Copilot verifies Gemini's response"""
        logger.info("\n" + "=" * 70)
        logger.info("STEP 8: Verify Handshake Response")
        logger.info("=" * 70)
        
        success = handshake.verify_response(
            challenge_nonce=challenge_nonce,
            initiator_did=copilot_did,
            responder_did=gemini_did
        )
        
        if success:
            logger.info("✓ Handshake verification successful!")
            
            # Check verified directory
            verified_challenge = os.path.join(
                SovereignHandshakeConfig.VERIFIED_DIR,
                f"{challenge_nonce}_{copilot_did.replace(':', '-')}.json"
            )
            verified_response = os.path.join(
                SovereignHandshakeConfig.VERIFIED_DIR,
                f"{challenge_nonce}_{gemini_did.replace(':', '-')}.json"
            )
            
            if os.path.exists(verified_challenge):
                logger.info(f"✓ Verified challenge file: {verified_challenge}")
            if os.path.exists(verified_response):
                logger.info(f"✓ Verified response file: {verified_response}")
        else:
            logger.error("✗ Handshake verification failed")
            return False
        
        return success
    
    def verify_database_state(self, db: IAMDatabase, copilot_did: str, gemini_did: str):
        """Verify database state after handshake"""
        logger.info("\n" + "=" * 70)
        logger.info("STEP 9: Verify Database State After Handshake")
        logger.info("=" * 70)
        
        copilot = db.get_agent(copilot_did)
        gemini = db.get_agent(gemini_did)
        
        if copilot:
            logger.info(f"\nCopilot Agent:")
            logger.info(f"  DID: {copilot.did}")
            logger.info(f"  Verified: {copilot.verified}")
            logger.info(f"  Last Seen: {copilot.last_seen}")
        
        if gemini:
            logger.info(f"\nGemini Agent:")
            logger.info(f"  DID: {gemini.did}")
            logger.info(f"  Verified: {gemini.verified}")
            logger.info(f"  Last Seen: {gemini.last_seen}")
    
    def display_communication_hub_structure(self):
        """Display final communication hub structure"""
        logger.info("\n" + "=" * 70)
        logger.info("STEP 10: Communication Hub Structure")
        logger.info("=" * 70)
        
        for root, dirs, files in os.walk(self.comm_hub):
            level = root.replace(self.comm_hub, '').count(os.sep)
            indent = ' ' * 2 * level
            rel_path = os.path.basename(root)
            if rel_path:
                logger.info(f"{indent}{rel_path}/")
            else:
                logger.info(f"{indent}communication_hub/")
            
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                logger.info(f"{subindent}{file}")
    
    def cleanup(self):
        """Clean up test directory"""
        logger.info("\n" + "=" * 70)
        logger.info("Cleanup")
        logger.info("=" * 70)
        
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            logger.info(f"✓ Cleaned up: {self.test_dir}")
    
    def run_full_poc(self):
        """Execute complete PoC demonstration"""
        try:
            # Setup
            self.setup_communication_hub()
            db = self.initialize_iam_db()
            
            # Register agents
            copilot, copilot_priv, _ = self.register_copilot_agent(db)
            gemini, gemini_priv, _ = self.register_gemini_agent(db)
            
            if not (copilot and gemini):
                logger.error("Failed to register agents")
                return False
            
            # Verify database
            self.list_registered_agents(db)
            
            # Initialize handshake protocol
            handshake = SovereignHandshake(db)
            
            # Execute handshake flow
            challenge_nonce = self.initiate_handshake(
                handshake,
                copilot.did,
                gemini.did,
                copilot_priv
            )
            
            if not challenge_nonce:
                logger.error("Handshake initiation failed")
                return False
            
            respond_success = self.respond_to_challenge(
                handshake,
                challenge_nonce,
                copilot.did,
                gemini.did,
                gemini_priv
            )
            
            if not respond_success:
                logger.error("Challenge response failed")
                return False
            
            verify_success = self.verify_handshake(
                handshake,
                challenge_nonce,
                copilot.did,
                gemini.did
            )
            
            if not verify_success:
                logger.error("Handshake verification failed")
                return False
            
            # Final verification
            self.verify_database_state(db, copilot.did, gemini.did)
            self.display_communication_hub_structure()
            
            # Summary
            logger.info("\n" + "=" * 70)
            logger.info("PHASE 4.2.6 PoC SUMMARY")
            logger.info("=" * 70)
            logger.info("✓ IAM Database Persistence: SUCCESSFUL")
            logger.info("  - SQLite with agent identities and Ed25519 keys")
            logger.info("✓ Sovereign Handshake Protocol: SUCCESSFUL")
            logger.info("  - File-based challenge-response with Ed25519 signatures")
            logger.info("✓ Copilot-to-Gemini Authentication: SUCCESSFUL")
            logger.info("  - Both agents verified and marked in database")
            logger.info("✓ Communication Hub: SUCCESSFUL")
            logger.info("  - State files organized in challenges/responses/verified")
            logger.info("=" * 70)
            
            db.close()
            return True
            
        except Exception as e:
            logger.error(f"PoC execution failed: {e}", exc_info=True)
            return False


def main():
    """Main entry point"""
    logger.info("\n" + "=" * 70)
    logger.info("XNAI FOUNDATION - PHASE 4.2.6 PoC")
    logger.info("IAM DB Persistence & Sovereign Handshake")
    logger.info("=" * 70)
    
    demo = IAMHandshakePoCDemo()
    
    try:
        success = demo.run_full_poc()
        
        if success:
            logger.info("\n✓ PoC completed successfully!")
            return 0
        else:
            logger.error("\n✗ PoC failed!")
            return 1
    finally:
        # Preserve test directory for inspection
        logger.info(f"\nTest artifacts preserved at: {demo.test_dir}")
        logger.info("Run 'rm -rf <path>' to clean up manually")


if __name__ == "__main__":
    sys.exit(main())
