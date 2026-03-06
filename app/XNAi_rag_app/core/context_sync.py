import anyio
import json
import logging
import os
import hashlib
import time
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from app.XNAi_rag_app.core.dependencies import get_redis_client
from app.XNAi_rag_app.core.iam_handshake import KeyManager
from app.XNAi_rag_app.core.iam_db import get_iam_database, AgentType

logger = logging.getLogger(__name__)

@dataclass
class ContextMetadata:
    """Metadata for context synchronization."""
    session_id: str
    agent_did: str
    timestamp: datetime
    context_hash: str
    version: str = "1.0"
    expires_at: Optional[datetime] = None

class ContextSyncEngine:
    """Enhanced hybrid Redis-File sync engine for multi-agent context continuity."""
    
    def __init__(self, agent_did: str, context_dir: str = "communication_hub/state/contexts"):
        self.agent_did = agent_did
        self.context_dir = context_dir
        self.iam = get_iam_database()
        os.makedirs(self.context_dir, exist_ok=True)
        
        # Configuration
        self.context_ttl = timedelta(hours=24)  # Context expiration
        self.max_context_size = 1024 * 1024  # 1MB limit

    async def save_context(self, session_id: str, context_data: Dict[str, Any], private_key_hex: str):
        """Save context to Redis and signed File with enhanced validation."""
        try:
            # Validate context data size
            context_json = json.dumps(context_data)
            if len(context_json.encode('utf-8')) > self.max_context_size:
                logger.error(f"Context size exceeds limit: {len(context_json)} bytes")
                raise ValueError("Context size too large")
            
            # Calculate context hash for integrity
            context_hash = hashlib.sha256(context_json.encode('utf-8')).hexdigest()
            
            # Create metadata
            metadata = ContextMetadata(
                session_id=session_id,
                agent_did=self.agent_did,
                timestamp=datetime.now(timezone.utc),
                context_hash=context_hash,
                expires_at=datetime.now(timezone.utc) + self.context_ttl
            )
            
            # 1. Update Redis (Volatile/Fast)
            host = os.getenv("REDIS_HOST", "localhost")
            password = os.getenv("REDIS_PASSWORD")
            from redis.asyncio import Redis
            redis = Redis(host=host, password=password, decode_responses=False)
            
            redis_key = f"xnai:context:{session_id}"
            redis_data = {
                "last_agent": self.agent_did,
                "timestamp": metadata.timestamp.isoformat(),
                "active_task": context_data.get("active_task"),
                "context_hash": context_hash,
                "expires_at": metadata.expires_at.isoformat() if metadata.expires_at else None
            }
            
            await redis.setex(redis_key, int(self.context_ttl.total_seconds()), json.dumps(redis_data))
            await redis.aclose()

            # 2. Write to File (Persistent/Sovereign)
            context_file = os.path.join(self.context_dir, f"{session_id}.json")
            
            # Prepare for signing with metadata
            payload = {
                "metadata": asdict(metadata),
                "data": context_data
            }
            
            # Sign the payload
            message_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
            signature = KeyManager.sign_message(private_key_hex, message_bytes)
            payload["signature"] = signature

            async with await anyio.open_file(context_file, 'w') as f:
                await f.write(json.dumps(payload, indent=2))
            
            logger.info(f"Context saved and signed: {session_id} by {self.agent_did}")
            
        except Exception as e:
            logger.error(f"Error saving context for session {session_id}: {e}")
            raise

    async def load_context(self, session_id: str, expected_agent_public_key_hex: str) -> Optional[Dict[str, Any]]:
        """Load context from File and verify signature with enhanced validation."""
        try:
            context_file = os.path.join(self.context_dir, f"{session_id}.json")
            
            if not os.path.exists(context_file):
                logger.warning(f"Context file not found: {context_file}")
                return None

            async with await anyio.open_file(context_file, 'r') as f:
                content = await f.read()
                payload = json.loads(content)

            # Verify signature
            signature = payload.pop("signature")
            message_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
            is_valid = KeyManager.verify_signature(
                expected_agent_public_key_hex,
                message_bytes,
                signature
            )

            if not is_valid:
                logger.error(f"Context signature verification failed for session {session_id}!")
                return None

            # Validate metadata
            metadata = payload.get("metadata", {})
            if not metadata:
                logger.warning(f"Missing metadata in context for session {session_id}")
                return None

            # Check expiration
            expires_at = metadata.get("expires_at")
            if expires_at:
                expires_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                if datetime.now(timezone.utc) > expires_dt:
                    logger.warning(f"Context expired for session {session_id}")
                    return None

            # Verify context hash
            context_data = payload.get("data", {})
            if context_data:
                context_json = json.dumps(context_data)
                expected_hash = metadata.get("context_hash")
                actual_hash = hashlib.sha256(context_json.encode('utf-8')).hexdigest()
                
                if expected_hash and expected_hash != actual_hash:
                    logger.error(f"Context hash mismatch for session {session_id}")
                    return None

            logger.info(f"Context loaded and verified: {session_id}")
            return context_data
            
        except Exception as e:
            logger.error(f"Error loading context for session {session_id}: {e}")
            return None

    async def cleanup_expired_contexts(self):
        """Clean up expired contexts from both Redis and filesystem."""
        try:
            # Clean up Redis
            host = os.getenv("REDIS_HOST", "localhost")
            password = os.getenv("REDIS_PASSWORD")
            from redis.asyncio import Redis
            redis = Redis(host=host, password=password, decode_responses=False)
            
            # Get all context keys
            keys = await redis.keys("xnai:context:*")
            
            for key in keys:
                try:
                    data = await redis.get(key)
                    if data:
                        context_data = json.loads(data.decode('utf-8'))
                        expires_at = context_data.get("expires_at")
                        
                        if expires_at:
                            expires_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                            if datetime.now(timezone.utc) > expires_dt:
                                await redis.delete(key)
                                logger.info(f"Removed expired context from Redis: {key}")
                except Exception as e:
                    logger.error(f"Error checking Redis context {key}: {e}")
            
            await redis.aclose()
            
            # Clean up filesystem
            import glob
            context_files = glob.glob(os.path.join(self.context_dir, "*.json"))
            
            for context_file in context_files:
                try:
                    async with await anyio.open_file(context_file, 'r') as f:
                        content = await f.read()
                        payload = json.loads(content)
                    
                    metadata = payload.get("metadata", {})
                    expires_at = metadata.get("expires_at")
                    
                    if expires_at:
                        expires_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                        if datetime.now(timezone.utc) > expires_dt:
                            os.remove(context_file)
                            logger.info(f"Removed expired context file: {context_file}")
                            
                except Exception as e:
                    logger.error(f"Error checking context file {context_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Error during context cleanup: {e}")

    async def get_context_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status information about a context."""
        try:
            # Check Redis
            host = os.getenv("REDIS_HOST", "localhost")
            password = os.getenv("REDIS_PASSWORD")
            from redis.asyncio import Redis
            redis = Redis(host=host, password=password, decode_responses=False)
            
            redis_key = f"xnai:context:{session_id}"
            redis_data = await redis.get(redis_key)
            await redis.aclose()
            
            status = {
                "session_id": session_id,
                "redis_exists": bool(redis_data),
                "file_exists": False,
                "is_valid": False,
                "expires_at": None,
                "last_agent": None
            }
            
            # Check file
            context_file = os.path.join(self.context_dir, f"{session_id}.json")
            if os.path.exists(context_file):
                status["file_exists"] = True
                
                try:
                    async with await anyio.open_file(context_file, 'r') as f:
                        content = await f.read()
                        payload = json.loads(content)
                    
                    metadata = payload.get("metadata", {})
                    status["expires_at"] = metadata.get("expires_at")
                    status["last_agent"] = metadata.get("agent_did")
                    
                    # Check if expired
                    if status["expires_at"]:
                        expires_dt = datetime.fromisoformat(status["expires_at"].replace('Z', '+00:00'))
                        status["is_valid"] = datetime.now(timezone.utc) < expires_dt
                    else:
                        status["is_valid"] = True
                        
                except Exception as e:
                    logger.error(f"Error reading context file {context_file}: {e}")
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting context status for {session_id}: {e}")
            return None
