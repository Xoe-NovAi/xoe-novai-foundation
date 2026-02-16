#!/usr/bin/env python3
"""
Phase 4.2.6: Practical Integration Example
===========================================
Demonstrates how to integrate IAM DB and Sovereign Handshake into applications.

Usage:
  python3 iam_integration_example.py --register-agents
  python3 iam_integration_example.py --handshake
  python3 iam_integration_example.py --status
"""

import sys
import os
import argparse
import logging
from datetime import datetime, timezone

# Configure path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, os.path.join(project_root, "app"))

from XNAi_rag_app.core.iam_db import (
    IAMDatabase,
    AgentIdentity,
    AgentType,
    get_iam_database
)
from XNAi_rag_app.core.iam_handshake import (
    SovereignHandshake,
    KeyManager
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def setup_agents():
    """Example 1: Setup and register agents"""
    logger.info("=" * 70)
    logger.info("EXAMPLE 1: Agent Registration")
    logger.info("=" * 70)
    
    db = get_iam_database()
    
    # Define agents
    agents_config = [
        {
            "did": "did:xnai:copilot-prod-001",
            "name": "copilot-prod",
            "type": AgentType.COPILOT,
            "capabilities": ["code-analysis", "refactoring", "testing"]
        },
        {
            "did": "did:xnai:gemini-prod-001",
            "name": "gemini-prod",
            "type": AgentType.GEMINI,
            "capabilities": ["reasoning", "generation", "multimodal"]
        }
    ]
    
    for agent_config in agents_config:
        # Check if already registered
        existing = db.get_agent(agent_config["did"])
        if existing:
            logger.info(f"✓ Agent already registered: {agent_config['name']}")
            continue
        
        # Generate keypair
        private_key, public_key = KeyManager.generate_keypair()
        
        # Create identity
        agent = AgentIdentity(
            did=agent_config["did"],
            agent_name=agent_config["name"],
            agent_type=agent_config["type"],
            public_key_ed25519=public_key,
            metadata={
                "version": "1.0.0",
                "region": "production",
                "capabilities": agent_config["capabilities"]
            },
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        # Register
        success = db.register_agent(agent)
        
        if success:
            logger.info(f"✓ Registered: {agent.agent_name}")
            logger.info(f"  DID: {agent.did}")
            
            # In production, store private key securely
            env_var = f"{agent_config['name'].upper()}_PRIVATE_KEY"
            logger.info(f"  Private Key (store as env var {env_var}):")
            logger.info(f"    {private_key}")
        else:
            logger.error(f"✗ Failed to register: {agent_config['name']}")
    
    db.close()


def perform_handshake():
    """Example 2: Perform handshake between agents"""
    logger.info("=" * 70)
    logger.info("EXAMPLE 2: Sovereign Handshake")
    logger.info("=" * 70)
    
    db = get_iam_database()
    handshake = SovereignHandshake(db)
    
    initiator_did = "did:xnai:copilot-prod-001"
    responder_did = "did:xnai:gemini-prod-001"
    
    # In production, load from secure environment
    # For this example, we'll need to regenerate (not ideal for production)
    
    # Get agents from database
    initiator = db.get_agent(initiator_did)
    responder = db.get_agent(responder_did)
    
    if not initiator or not responder:
        logger.error("One or both agents not found in database")
        logger.error("Run with --register-agents first")
        db.close()
        return
    
    if initiator.verified and responder.verified:
        logger.info("✓ Agents already verified")
        db.close()
        return
    
    logger.info(f"Initiator: {initiator.agent_name}")
    logger.info(f"Responder: {responder.agent_name}")
    logger.info("\nNote: In production, private keys should be loaded from secure storage")
    
    db.close()


def check_status():
    """Example 3: Check agent verification status"""
    logger.info("=" * 70)
    logger.info("EXAMPLE 3: Agent Status")
    logger.info("=" * 70)
    
    db = get_iam_database()
    
    agents = db.list_agents()
    
    if not agents:
        logger.info("No agents registered")
        db.close()
        return
    
    logger.info(f"Total agents: {len(agents)}\n")
    
    for agent in agents:
        status = "✓ VERIFIED" if agent.verified else "✗ UNVERIFIED"
        logger.info(f"{status} | {agent.agent_name}")
        logger.info(f"       DID: {agent.did}")
        logger.info(f"       Type: {agent.agent_type.value}")
        logger.info(f"       Created: {agent.created_at}")
        if agent.last_seen:
            logger.info(f"       Last Seen: {agent.last_seen}")
        logger.info("")
    
    db.close()


def security_best_practices():
    """Print security best practices"""
    logger.info("=" * 70)
    logger.info("SECURITY BEST PRACTICES FOR PRODUCTION")
    logger.info("=" * 70)
    
    practices = [
        ("Private Key Storage", [
            "Use environment variables for development",
            "Use HashiCorp Vault in production",
            "Use AWS Secrets Manager or Azure Key Vault",
            "Never commit keys to version control"
        ]),
        ("Database Security", [
            "Use file system permissions: chmod 600 iam_agents.db",
            "Enable SQLite encryption (e.g., SQLCipher)",
            "Implement regular backups with encryption",
            "Monitor database access logs"
        ]),
        ("Communication Hub", [
            "Use restrictive file permissions: chmod 700",
            "Implement automatic cleanup of expired challenges",
            "Monitor for unauthorized file access",
            "Use separate directories for staging/verified"
        ]),
        ("Handshake Protocol", [
            "Verify challenge signatures before processing",
            "Enforce challenge expiration (default 5 minutes)",
            "Log all handshake attempts",
            "Implement rate limiting on failed attempts"
        ]),
        ("Monitoring & Auditing", [
            "Log all agent registrations",
            "Log all handshake attempts and results",
            "Monitor for repeated verification failures",
            "Implement alerting for security events"
        ])
    ]
    
    for category, items in practices:
        logger.info(f"\n{category}:")
        for item in items:
            logger.info(f"  • {item}")


def example_api_integration():
    """Example 4: How to integrate with FastAPI"""
    logger.info("=" * 70)
    logger.info("EXAMPLE 4: FastAPI Integration Code")
    logger.info("=" * 70)
    
    code = '''
from fastapi import FastAPI, HTTPException
from app.XNAi_rag_app.core.iam_db import get_iam_database
from app.XNAi_rag_app.core.iam_handshake import SovereignHandshake

app = FastAPI()
db = get_iam_database()
handshake = SovereignHandshake(db)

@app.post("/api/v1/agents")
async def register_agent(agent_id: str, agent_type: str):
    """Register new agent"""
    from app.XNAi_rag_app.core.iam_handshake import KeyManager
    
    private_key, public_key = KeyManager.generate_keypair()
    
    # Store and return
    return {
        "agent_id": agent_id,
        "did": f"did:xnai:{agent_id}",
        "public_key": public_key,
        # IMPORTANT: Store private_key securely, not in response!
    }

@app.post("/api/v1/handshake/initiate")
async def initiate_handshake(initiator_did: str, responder_did: str):
    """Initiate handshake between agents"""
    
    # Load private key from secure storage
    private_key = os.getenv(f"{initiator_did}_PRIVATE_KEY")
    if not private_key:
        raise HTTPException(status_code=400, detail="Private key not available")
    
    challenge_nonce = handshake.initiate_handshake(
        initiator_did=initiator_did,
        responder_did=responder_did,
        initiator_private_key_hex=private_key
    )
    
    if not challenge_nonce:
        raise HTTPException(status_code=400, detail="Handshake initiation failed")
    
    return {"challenge_nonce": challenge_nonce}

@app.post("/api/v1/handshake/respond")
async def respond_to_challenge(
    challenge_nonce: str,
    initiator_did: str,
    responder_did: str
):
    """Respond to handshake challenge"""
    
    private_key = os.getenv(f"{responder_did}_PRIVATE_KEY")
    if not private_key:
        raise HTTPException(status_code=400, detail="Private key not available")
    
    success = handshake.respond_to_challenge(
        challenge_nonce=challenge_nonce,
        initiator_did=initiator_did,
        responder_did=responder_did,
        responder_private_key_hex=private_key
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Challenge response failed")
    
    return {"status": "responded"}

@app.post("/api/v1/handshake/verify")
async def verify_handshake(
    challenge_nonce: str,
    initiator_did: str,
    responder_did: str
):
    """Verify handshake response"""
    
    success = handshake.verify_response(
        challenge_nonce=challenge_nonce,
        initiator_did=initiator_did,
        responder_did=responder_did
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Verification failed")
    
    return {"status": "verified"}

@app.get("/api/v1/handshake/status")
async def get_handshake_status(initiator_did: str, responder_did: str):
    """Get handshake status between agents"""
    
    return handshake.get_handshake_status(
        initiator_did=initiator_did,
        responder_did=responder_did
    )
    '''
    
    logger.info(code)


def main():
    parser = argparse.ArgumentParser(
        description="Phase 4.2.6 IAM & Handshake Integration Examples"
    )
    parser.add_argument(
        "--register-agents",
        action="store_true",
        help="Register sample agents"
    )
    parser.add_argument(
        "--handshake",
        action="store_true",
        help="Perform handshake between agents"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Check agent verification status"
    )
    parser.add_argument(
        "--best-practices",
        action="store_true",
        help="Show security best practices"
    )
    parser.add_argument(
        "--api-example",
        action="store_true",
        help="Show FastAPI integration example"
    )
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return 1
    
    try:
        if args.register_agents:
            setup_agents()
        
        if args.handshake:
            perform_handshake()
        
        if args.status:
            check_status()
        
        if args.best_practices:
            security_best_practices()
        
        if args.api_example:
            example_api_integration()
        
        return 0
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
