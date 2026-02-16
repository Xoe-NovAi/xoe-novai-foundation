import anyio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from app.XNAi_rag_app.core.dependencies import get_redis_client
from app.XNAi_rag_app.core.iam_handshake import KeyManager

logger = logging.getLogger(__name__)

class ContextSyncEngine:
    """Hybrid Redis-File sync engine for multi-agent context continuity."""
    
    def __init__(self, agent_did: str, context_dir: str = "communication_hub/state/contexts"):
        self.agent_did = agent_did
        self.context_dir = context_dir
        os.makedirs(self.context_dir, exist_ok=True)

    async def save_context(self, session_id: str, context_data: Dict[str, Any], private_key_hex: str):
        """Save context to Redis and signed File."""
        # 1. Update Redis (Volatile/Fast)
        host = os.getenv("REDIS_HOST", "localhost")
        password = os.getenv("REDIS_PASSWORD")
        from redis.asyncio import Redis
        redis = Redis(host=host, password=password, decode_responses=False)
        
        redis_key = f"xnai:context:{session_id}"
        await redis.set(redis_key, json.dumps({
            "last_agent": self.agent_did,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "active_task": context_data.get("active_task")
        }))
        await redis.aclose()

        # 2. Write to File (Persistent/Sovereign)
        context_file = os.path.join(self.context_dir, f"{session_id}.json")
        
        # Prepare for signing
        payload = {
            "session_id": session_id,
            "agent_did": self.agent_did,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": context_data
        }
        
        # Sign the payload
        message_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        signature = KeyManager.sign_message(private_key_hex, message_bytes)
        payload["signature"] = signature

        async with await anyio.open_file(context_file, 'w') as f:
            await f.write(json.dumps(payload, indent=2))
        
        logger.info(f"Context saved and signed: {session_id} by {self.agent_did}")

    async def load_context(self, session_id: str, expected_agent_public_key_hex: str) -> Optional[Dict[str, Any]]:
        """Load context from File and verify signature."""
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

        logger.info(f"Context loaded and verified: {session_id}")
        return payload["data"]
