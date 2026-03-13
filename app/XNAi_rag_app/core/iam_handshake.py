#!/usr/bin/env python3
"""
Sovereign Handshake Protocol - Ed25519 Key Exchange
====================================================
File-based cryptographic handshake for inter-agent authentication.
Implements challenge-response protocol with Ed25519 signatures.

Pattern: Zero-Trust Agent Communication (Phase 4.2.6)
Version: 1.0.0
"""

import os
import json
import logging
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

from .iam_db import IAMDatabase, AgentIdentity, AgentType

logger = logging.getLogger(__name__)


class SovereignHandshakeConfig:
    """Configuration for handshake protocol"""
    
    # Timeouts (seconds)
    CHALLENGE_EXPIRY = 300  # 5 minutes
    HANDSHAKE_TIMEOUT = 600  # 10 minutes
    
    # File paths
    COMMUNICATION_HUB = os.getenv("COMMUNICATION_HUB_PATH", "communication_hub")
    STATE_DIR = os.path.join(COMMUNICATION_HUB, "state")
    CHALLENGES_DIR = os.path.join(STATE_DIR, "challenges")
    RESPONSES_DIR = os.path.join(STATE_DIR, "responses")
    VERIFIED_DIR = os.path.join(STATE_DIR, "verified")
    
    # Key serialization format
    KEY_ENCODING = "hex"  # Use hex for file storage


class KeyManager:
    """Manage Ed25519 key generation and serialization"""
    
    @staticmethod
    def generate_keypair() -> Tuple[str, str]:
        """
        Generate Ed25519 keypair.
        Returns: (private_key_hex, public_key_hex)
        """
        private_key = ed25519.Ed25519PrivateKey.generate()
        
        # Serialize keys to hex
        private_hex = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        ).hex()
        
        public_hex = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        ).hex()
        
        return private_hex, public_hex
    
    @staticmethod
    def load_private_key(private_key_hex: str) -> ed25519.Ed25519PrivateKey:
        """Load private key from hex"""
        private_bytes = bytes.fromhex(private_key_hex)
        return ed25519.Ed25519PrivateKey.from_private_bytes(private_bytes)
    
    @staticmethod
    def load_public_key(public_key_hex: str) -> ed25519.Ed25519PublicKey:
        """Load public key from hex"""
        public_bytes = bytes.fromhex(public_key_hex)
        return ed25519.Ed25519PublicKey.from_public_bytes(public_bytes)
    
    @staticmethod
    def sign_message(private_key_hex: str, message: bytes) -> str:
        """Sign message with private key, return signature as hex"""
        private_key = KeyManager.load_private_key(private_key_hex)
        signature = private_key.sign(message)
        return signature.hex()
    
    @staticmethod
    def verify_signature(public_key_hex: str, message: bytes, signature_hex: str) -> bool:
        """Verify message signature"""
        try:
            public_key = KeyManager.load_public_key(public_key_hex)
            signature = bytes.fromhex(signature_hex)
            public_key.verify(signature, message)
            return True
        except InvalidSignature:
            return False
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False


class ChallengeData:
    """Challenge message structure"""
    
    @staticmethod
    def create(
        challenger_did: str,
        challenge_nonce: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create challenge data"""
        if not challenge_nonce:
            challenge_nonce = secrets.token_hex(32)
        
        return {
            "type": "challenge",
            "challenger_did": challenger_did,
            "challenge_nonce": challenge_nonce,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(seconds=SovereignHandshakeConfig.CHALLENGE_EXPIRY)).isoformat()
        }
    
    @staticmethod
    def to_bytes(challenge: Dict[str, Any]) -> bytes:
        """Serialize challenge to bytes for signing"""
        return json.dumps(challenge, sort_keys=True).encode('utf-8')


class ResponseData:
    """Response message structure"""
    
    @staticmethod
    def create(
        responder_did: str,
        challenge_nonce: str,
        challenge_signature: str
    ) -> Dict[str, Any]:
        """Create response data"""
        return {
            "type": "response",
            "responder_did": responder_did,
            "challenge_nonce": challenge_nonce,
            "challenge_signature": challenge_signature,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    @staticmethod
    def to_bytes(response: Dict[str, Any]) -> bytes:
        """Serialize response to bytes for signing"""
        return json.dumps(response, sort_keys=True).encode('utf-8')


class SovereignHandshake:
    """
    File-based Ed25519 handshake protocol.
    
    Protocol Flow:
    1. Agent A creates challenge file: challenges/{challenge_id}.json
    2. Agent B signs challenge and creates response file: responses/{challenge_id}.json
    3. Agent A verifies response signature
    4. Both agents mark each other as verified in IAM DB
    """
    
    def __init__(self, iam_db: IAMDatabase):
        """Initialize handshake manager"""
        self.iam_db = iam_db
        self._setup_directories()
        logger.info("Sovereign handshake initialized")
    
    def _setup_directories(self):
        """Create communication hub directory structure"""
        for directory in [
            SovereignHandshakeConfig.STATE_DIR,
            SovereignHandshakeConfig.CHALLENGES_DIR,
            SovereignHandshakeConfig.RESPONSES_DIR,
            SovereignHandshakeConfig.VERIFIED_DIR
        ]:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"Directory ready: {directory}")
    
    def initiate_handshake(
        self,
        initiator_did: str,
        responder_did: str,
        initiator_private_key_hex: str
    ) -> Optional[str]:
        """
        Initiate handshake: Agent A → Agent B
        
        Args:
            initiator_did: DID of initiating agent
            responder_did: DID of responding agent
            initiator_private_key_hex: Initiator's private key for signing
            
        Returns:
            challenge_nonce on success, None on failure
        """
        try:
            # Verify both agents exist in IAM DB
            initiator = self.iam_db.get_agent(initiator_did)
            responder = self.iam_db.get_agent(responder_did)
            
            if not initiator:
                logger.error(f"Initiator not found: {initiator_did}")
                return None
            if not responder:
                logger.error(f"Responder not found: {responder_did}")
                return None
            
            # Create challenge
            challenge = ChallengeData.create(challenger_did=initiator_did)
            challenge_nonce = challenge["challenge_nonce"]
            challenge_bytes = ChallengeData.to_bytes(challenge)
            
            # Sign challenge with initiator's private key
            challenge_signature = KeyManager.sign_message(
                initiator_private_key_hex,
                challenge_bytes
            )
            
            # Add signature to challenge
            challenge["signature"] = challenge_signature
            
            # Write challenge file
            challenge_filename = f"{challenge_nonce}_{initiator_did.replace(':', '-')}.json"
            challenge_path = os.path.join(SovereignHandshakeConfig.CHALLENGES_DIR, challenge_filename)
            
            with open(challenge_path, 'w') as f:
                json.dump(challenge, f, indent=2)
            
            os.chmod(challenge_path, 0o644)
            logger.info(f"Challenge initiated: {challenge_nonce} → {initiator_did} to {responder_did}")
            
            return challenge_nonce
            
        except Exception as e:
            logger.error(f"Failed to initiate handshake: {e}")
            return None
    
    def respond_to_challenge(
        self,
        challenge_nonce: str,
        initiator_did: str,
        responder_did: str,
        responder_private_key_hex: str
    ) -> bool:
        """
        Respond to challenge: Agent B → Agent A
        
        Args:
            challenge_nonce: Challenge nonce from challenge file
            initiator_did: DID of initiating agent
            responder_did: DID of responding agent
            responder_private_key_hex: Responder's private key for signing
            
        Returns:
            True on success, False on failure
        """
        try:
            # Load challenge file
            challenge_filename = f"{challenge_nonce}_{initiator_did.replace(':', '-')}.json"
            challenge_path = os.path.join(SovereignHandshakeConfig.CHALLENGES_DIR, challenge_filename)
            
            if not os.path.exists(challenge_path):
                logger.error(f"Challenge not found: {challenge_path}")
                return False
            
            with open(challenge_path, 'r') as f:
                challenge = json.load(f)
            
            # Verify challenge hasn't expired
            expires_at = datetime.fromisoformat(challenge["expires_at"])
            if datetime.now(timezone.utc) > expires_at:
                logger.error(f"Challenge expired: {challenge_nonce}")
                return False
            
            # Verify challenge signature with initiator's public key
            initiator = self.iam_db.get_agent(initiator_did)
            if not initiator:
                logger.error(f"Initiator not found: {initiator_did}")
                return False
            
            # Reconstruct challenge for verification (without signature field)
            challenge_for_verification = {
                "type": challenge["type"],
                "challenger_did": challenge["challenger_did"],
                "challenge_nonce": challenge["challenge_nonce"],
                "timestamp": challenge["timestamp"],
                "expires_at": challenge["expires_at"]
            }
            challenge_bytes = ChallengeData.to_bytes(challenge_for_verification)
            
            if not KeyManager.verify_signature(
                initiator.public_key_ed25519,
                challenge_bytes,
                challenge["signature"]
            ):
                logger.error(f"Challenge signature verification failed: {challenge_nonce}")
                return False
            
            # Create response
            response = ResponseData.create(
                responder_did=responder_did,
                challenge_nonce=challenge_nonce,
                challenge_signature=challenge["signature"]
            )
            
            response_bytes = ResponseData.to_bytes(response)
            
            # Sign response with responder's private key
            response_signature = KeyManager.sign_message(
                responder_private_key_hex,
                response_bytes
            )
            
            response["signature"] = response_signature
            
            # Write response file
            response_filename = f"{challenge_nonce}_{responder_did.replace(':', '-')}.json"
            response_path = os.path.join(SovereignHandshakeConfig.RESPONSES_DIR, response_filename)
            
            with open(response_path, 'w') as f:
                json.dump(response, f, indent=2)
            
            os.chmod(response_path, 0o644)
            logger.info(f"Challenge response created: {challenge_nonce} from {responder_did}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to respond to challenge: {e}")
            return False
    
    def verify_response(
        self,
        challenge_nonce: str,
        initiator_did: str,
        responder_did: str
    ) -> bool:
        """
        Verify response and mark both agents as verified.
        
        Args:
            challenge_nonce: Challenge nonce
            initiator_did: DID of initiating agent
            responder_did: DID of responding agent
            
        Returns:
            True if verification successful
        """
        try:
            # Load response file
            response_filename = f"{challenge_nonce}_{responder_did.replace(':', '-')}.json"
            response_path = os.path.join(SovereignHandshakeConfig.RESPONSES_DIR, response_filename)
            
            if not os.path.exists(response_path):
                logger.error(f"Response not found: {response_path}")
                return False
            
            with open(response_path, 'r') as f:
                response = json.load(f)
            
            # Get responder's public key
            responder = self.iam_db.get_agent(responder_did)
            if not responder:
                logger.error(f"Responder not found: {responder_did}")
                return False
            
            # Reconstruct response for verification (without signature field)
            response_for_verification = {
                "type": response["type"],
                "responder_did": response["responder_did"],
                "challenge_nonce": response["challenge_nonce"],
                "challenge_signature": response["challenge_signature"],
                "timestamp": response["timestamp"]
            }
            response_bytes = ResponseData.to_bytes(response_for_verification)
            
            if not KeyManager.verify_signature(
                responder.public_key_ed25519,
                response_bytes,
                response["signature"]
            ):
                logger.error(f"Response signature verification failed: {challenge_nonce}")
                return False
            
            # Mark both agents as verified
            self.iam_db.update_agent_verification(initiator_did, True)
            self.iam_db.update_agent_verification(responder_did, True)
            self.iam_db.update_agent_last_seen(initiator_did)
            self.iam_db.update_agent_last_seen(responder_did)
            
            # Move verified files to verified directory
            challenge_filename = f"{challenge_nonce}_{initiator_did.replace(':', '-')}.json"
            challenge_path = os.path.join(SovereignHandshakeConfig.CHALLENGES_DIR, challenge_filename)
            verified_challenge_path = os.path.join(SovereignHandshakeConfig.VERIFIED_DIR, challenge_filename)
            
            if os.path.exists(challenge_path):
                os.rename(challenge_path, verified_challenge_path)
            
            verified_response_path = os.path.join(SovereignHandshakeConfig.VERIFIED_DIR, response_filename)
            if os.path.exists(response_path):
                os.rename(response_path, verified_response_path)
            
            logger.info(f"Handshake verified: {initiator_did} ↔ {responder_did}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to verify response: {e}")
            return False
    
    def get_handshake_status(self, initiator_did: str, responder_did: str) -> Dict[str, Any]:
        """Get status of handshake between two agents"""
        initiator = self.iam_db.get_agent(initiator_did)
        responder = self.iam_db.get_agent(responder_did)
        
        if not initiator or not responder:
            return {"status": "agents_not_found"}
        
        return {
            "status": "verified" if initiator.verified and responder.verified else "unverified",
            "initiator": {
                "did": initiator_did,
                "verified": initiator.verified,
                "last_seen": initiator.last_seen
            },
            "responder": {
                "did": responder_did,
                "verified": responder.verified,
                "last_seen": responder.last_seen
            }
        }


if __name__ == "__main__":
    # Demo usage - see test_handshake.py for complete example
    print("Sovereign Handshake Protocol - Ed25519 Key Exchange")
    print("Import this module to use: from iam_handshake import SovereignHandshake, KeyManager")
