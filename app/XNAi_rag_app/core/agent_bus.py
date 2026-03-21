import anyio
import json
import logging
import os
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from redis.asyncio import Redis
from app.XNAi_rag_app.core.dependencies import get_redis_client, get_redis_client_async
from app.XNAi_rag_app.core.iam_handshake import KeyManager
from prometheus_client import Counter, Histogram

logger = logging.getLogger(__name__)

# Prometheus Metrics
BUS_SENT_TASKS = Counter("xnai_agent_bus_sent_tasks_total", "Total tasks sent via Agent Bus", ["sender", "target", "task_type"])
BUS_RECEIVED_TASKS = Counter("xnai_agent_bus_received_tasks_total", "Total tasks received via Agent Bus", ["receiver", "sender", "task_type"])
BUS_SIG_VERIFICATION = Counter("xnai_agent_bus_signature_verification_total", "Task signature verification results", ["status"])
BUS_PROCESSING_TIME = Histogram("xnai_agent_bus_task_processing_duration_seconds", "Time taken to process a task")


class AgentBusClient:
    """AnyIO-wrapped Redis Stream Client for multi-agent task distribution with IA2 signatures."""

    def __init__(self, agent_did: str, stream_name: str = "xnai:agent_bus"):
        self.agent_did = agent_did
        self.stream_name = stream_name
        self.group_name = "agent_wavefront"
        self.redis: Optional[Redis] = None
        
        # IA2: Load cryptographic keys from environment
        self.private_key = os.getenv(f"AGENT_KEY_PRIVATE_{agent_did.upper().replace(':', '_')}")
        self.public_keys = self._load_public_keys()

    def _load_public_keys(self) -> Dict[str, str]:
        """IA2: Load all known agent public keys from environment."""
        keys = {}
        # Pattern: AGENT_KEY_PUBLIC_GEMINI, etc.
        for env_var, value in os.environ.items():
            if env_var.startswith("AGENT_KEY_PUBLIC_"):
                agent_name = env_var.replace("AGENT_KEY_PUBLIC_", "").lower()
                keys[agent_name] = value
        return keys

    async def __aenter__(self):
        # ST4/NS1: Use centralized async redis client with TLS support
        self.redis = await get_redis_client_async()
        # Initialize Group
        try:
            await self.redis.xgroup_create(self.stream_name, self.group_name, id="0", mkstream=True)
        except Exception:
            # Group likely already exists
            pass
        
        # 🔱 Archon Mandate: Auto-Connect (HEARTBEAT & IDENTITY)
        await self._publish_identity()
        return self

    async def _publish_identity(self):
        """Publish HEARTBEAT and IDENTITY upon initialization."""
        payload = {
            "agent_did": self.agent_did,
            "capabilities": ["generic"], # Default
            "status": "online",
            "timestamp": datetime.utcnow().isoformat()
        }
        try:
            await self.send_task(target_did="*", task_type="IDENTITY", payload=payload)
            await self.send_task(target_did="*", task_type="HEARTBEAT", payload=payload)
            logger.info(f"🔱 Agent {self.agent_did} registered with Agent Bus.")
        except Exception as e:
            logger.error(f"Failed to publish identity for {self.agent_did}: {e}")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the asynchronous context manager."""
        if self.redis:
            await self.redis.aclose()

    async def check_kill_switch(self) -> bool:
        """S3: Red-Phone Kill Switch. Returns True if emergency_stop is active."""
        try:
            # Check for most recent emergency_stop message in the stream
            # We use xrevread to get the latest without needing a group
            messages = await self.redis.xrevrange(self.stream_name, count=10)
            for msg_id, data in messages:
                if data.get("type") == "emergency_stop":
                    logger.critical(f"🛑 KILL SWITCH DETECTED: {msg_id} from {data.get('sender')}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to check kill switch: {e}")
            return False

    async def send_emergency_stop(self, reason: str = "Manual Trigger"):
        """S3: Broadcast emergency_stop to all agents."""
        message = {
            "sender": self.agent_did,
            "target": "*",
            "type": "emergency_stop",
            "payload": json.dumps({"reason": reason, "timestamp": datetime.utcnow().isoformat()}),
            "status": "critical",
        }
        task_id = await self.redis.xadd(self.stream_name, message)
        logger.critical(f"🚨 EMERGENCY STOP SENT: {task_id} - Reason: {reason}")
        return task_id

    async def send_task(self, target_did: str, task_type: str, payload: Dict[str, Any]) -> str:

        if self.redis:
            await self.redis.aclose()

    async def send_task(self, target_did: str, task_type: str, payload: Dict[str, Any]) -> str:
        """Add a signed task to the stream."""
        timestamp = datetime.utcnow().isoformat()
        message = {
            "sender": self.agent_did,
            "target": target_did,
            "type": task_type,
            "payload": json.dumps(payload),
            "status": "pending",
            "timestamp": timestamp,
        }
        
        # IA2: Generate signature if private key available
        if self.private_key:
            try:
                # Sign essential fields
                sign_payload = f"{self.agent_did}|{target_did}|{task_type}|{json.dumps(payload)}|{timestamp}".encode()
                message["signature"] = KeyManager.sign_message(self.private_key, sign_payload)
            except Exception as e:
                logger.error(f"Failed to sign message: {e}")

        task_id = await self.redis.xadd(self.stream_name, message)
        
        # Instrument
        BUS_SENT_TASKS.labels(sender=self.agent_did, target=target_did, task_type=task_type).inc()
        
        logger.info(f"Task sent: {task_id} from {self.agent_did} to {target_did} (Signed: {'signature' in message})")
        return task_id

    async def fetch_tasks(self, count: int = 1) -> List[Dict[str, Any]]:
        """Fetch tasks assigned to this agent or global tasks (target='*')."""
        # 1. Recover from PEL (Pending Entries List)
        # 2. Fetch new messages ('>')
        tasks = []

        # Pattern: Read from PEL first, then new
        for read_id in ["0", ">"]:
            response = await self.redis.xreadgroup(
                groupname=self.group_name,
                consumername=self.agent_did,
                streams={self.stream_name: read_id},
                count=count,
                block=1000 if read_id == ">" else None,
            )

            if response:
                for _, messages in response:
                    for msg_id, data in messages:
                        # Filter for this agent or broadcast
                        target = data.get("target", "*")
                        if target == self.agent_did or target == "*":
                            # IA2: Verify signature if possible
                            sender = data.get("sender", "unknown")
                            sig = data.get("signature")
                            verified = False
                            
                            if sig and sender in self.public_keys:
                                try:
                                    sign_payload = f"{sender}|{target}|{data.get('type')}|{data.get('payload')}|{data.get('timestamp')}".encode()
                                    verified = KeyManager.verify_signature(self.public_keys[sender], sign_payload, sig)
                                except Exception as e:
                                    logger.warning(f"Signature verification failed for message {msg_id} from {sender}: {e}")
                            elif not sig:
                                logger.debug(f"Message {msg_id} from {sender} is unsigned")
                            else:
                                logger.debug(f"No public key for sender {sender}, cannot verify signature")

                            # Instrument
                            BUS_RECEIVED_TASKS.labels(receiver=self.agent_did, sender=sender, task_type=data.get("type")).inc()
                            sig_status = "verified" if verified else ("unsigned" if not sig else "failed")
                            BUS_SIG_VERIFICATION.labels(status=sig_status).inc()

                            # SI1: Robust payload parsing
                            raw_payload = data.get("payload")
                            try:
                                payload = json.loads(raw_payload) if raw_payload else {}
                            except (json.JSONDecodeError, TypeError):
                                logger.warning(f"Malformed payload in message {msg_id}")
                                payload = {}

                            tasks.append(
                                {
                                    "id": msg_id,
                                    "sender": sender,
                                    "type": data.get("type"),
                                    "payload": payload,
                                    "verified": verified,
                                }
                            )
        return tasks

    async def acknowledge_task(self, task_id: str):
        """Acknowledge task completion."""
        await self.redis.xack(self.stream_name, self.group_name, task_id)
        logger.debug(f"Task acknowledged: {task_id}")

    async def emit_session_bloat(self, session_id: str, token_count: int):
        """Broadcast a session bloat event for the Librarian to handle."""
        payload = {
            "session_id": session_id,
            "token_count": token_count,
            "threshold_pct": 75,
            "timestamp": datetime.utcnow().isoformat()
        }
        return await self.send_task(target_did="worker:librarian:*", task_type="session_bloat", payload=payload)


class GapListener(AgentBusClient):
    """Specialized listener for Knowledge Gaps."""

    def __init__(self, agent_did: str = "listener:gap_detector:001"):
        super().__init__(agent_did)
        self.group_name = "gap_detection_group"

    async def start_listening(self):
        """Monitor stream for gap events."""
        logger.info("GapListener started...")
        while True:
            try:
                tasks = await self.fetch_tasks(count=5)
                for task in tasks:
                    event_type = task["type"]
                    payload = task["payload"]

                    if event_type in ["retrieval_failed", "low_confidence"]:
                        await self._handle_gap(payload)

                    await self.acknowledge_task(task["id"])

                await anyio.sleep(1)
            except Exception as e:
                logger.error(f"GapListener error: {e}")
                await anyio.sleep(5)  # Backoff

    async def _handle_gap(self, payload: Dict[str, Any]):
        """Trigger a research job for the detected gap."""
        query = payload.get("query", "unknown query")
        score = payload.get("score", 0.0)

        logger.warning(f"Knowledge Gap Detected! Query: '{query}' (Score: {score})")

        # Enqueue job to Redis (using raw redis client for simplicity here)
        job = {"type": "gap_fill", "criteria": {"topic": query}, "priority": 1, "created_at": datetime.utcnow().isoformat()}
        await self.redis.lpush("xnai:jobs:crawler:pending", json.dumps(job))
