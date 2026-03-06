"""Agent bus for inter-agent communication and coordination."""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis

from app.XNAi_rag_app.services.agent_management import AgentRegistry, ResearchJobManager
from app.XNAi_rag_app.services.database import get_db_session


class MessageType(Enum):
    """Types of messages in the agent bus."""
    REGISTRATION = "registration"
    HEARTBEAT = "heartbeat"
    TASK_ASSIGNMENT = "task_assignment"
    COLLABORATION_REQUEST = "collaboration_request"
    COLLABORATION_RESPONSE = "collaboration_response"
    STATUS_UPDATE = "status_update"
    METRIC_REPORT = "metric_report"
    SHUTDOWN = "shutdown"
    ERROR = "error"


@dataclass
class AgentMessage:
    """Standard message format for agent communication."""
    message_id: str
    message_type: MessageType
    sender_id: str
    timestamp: str
    payload: Dict[str, Any]
    recipient_id: Optional[str] = None
    correlation_id: Optional[str] = None


class AgentBus:
    """Redis-based message bus for agent communication."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.registry = AgentRegistry()
        self.jobs = ResearchJobManager()
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        self.running = False
        self.logger = logging.getLogger(__name__)
        
        # Channel names
        self.control_channel = "agent-bus:control"
        self.heartbeat_channel = "agent-bus:heartbeat"
        
    async def connect(self):
        """Connect to Redis and initialize the bus."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            self.logger.info("Agent bus connected to Redis")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            self.logger.info("Agent bus disconnected from Redis")
    
    def register_handler(self, message_type: MessageType, handler: Callable):
        """Register a handler for a specific message type."""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
        self.logger.info(f"Registered handler for {message_type}")
    
    async def send_message(self, message: AgentMessage):
        """Send a message to the appropriate channel."""
        if not self.redis_client:
            raise RuntimeError("Agent bus not connected")
        
        # Route message based on type
        channel = self._get_channel_for_message(message)
        
        # Convert message to JSON
        message_data = {
            "message_id": message.message_id,
            "message_type": message.message_type.value,
            "sender_id": message.sender_id,
            "timestamp": message.timestamp,
            "payload": message.payload,
            "recipient_id": message.recipient_id,
            "correlation_id": message.correlation_id
        }
        
        await self.redis_client.publish(channel, json.dumps(message_data))
        self.logger.debug(f"Sent {message.message_type} message from {message.sender_id}")
    
    async def broadcast_message(self, message: AgentMessage):
        """Broadcast a message to all agents."""
        if not self.redis_client:
            raise RuntimeError("Agent bus not connected")
        
        # Send to control channel for broadcast
        message_data = {
            "message_id": message.message_id,
            "message_type": message.message_type.value,
            "sender_id": message.sender_id,
            "timestamp": message.timestamp,
            "payload": message.payload,
            "recipient_id": None,  # Broadcast
            "correlation_id": message.correlation_id
        }
        
        await self.redis_client.publish(self.control_channel, json.dumps(message_data))
        self.logger.debug(f"Broadcast {message.message_type} message from {message.sender_id}")
    
    async def listen_for_messages(self) -> AsyncGenerator[AgentMessage, None]:
        """Listen for incoming messages."""
        if not self.redis_client:
            raise RuntimeError("Agent bus not connected")
        
        pubsub = self.redis_client.pubsub()
        
        # Subscribe to relevant channels
        channels = [
            self.control_channel,
            self.heartbeat_channel,
            "agent:*:in"  # All agent input channels
        ]
        
        for channel in channels:
            await pubsub.subscribe(channel)
        
        self.logger.info("Agent bus listening for messages")
        
        try:
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        agent_message = self._parse_message(data)
                        yield agent_message
                    except json.JSONDecodeError:
                        self.logger.warning(f"Invalid JSON message: {message['data']}")
                    except Exception as e:
                        self.logger.error(f"Error parsing message: {e}")
        finally:
            await pubsub.unsubscribe(*channels)
    
    def _get_channel_for_message(self, message: AgentMessage) -> str:
        """Determine the appropriate channel for a message."""
        if message.recipient_id:
            # Direct message to specific agent
            return f"agent:{message.recipient_id}:in"
        else:
            # Broadcast message
            return self.control_channel
    
    def _parse_message(self, data: Dict[str, Any]) -> AgentMessage:
        """Parse a dictionary into an AgentMessage."""
        return AgentMessage(
            message_id=data["message_id"],
            message_type=MessageType(data["message_type"]),
            sender_id=data["sender_id"],
            timestamp=data["timestamp"],
            payload=data["payload"],
            recipient_id=data.get("recipient_id"),
            correlation_id=data.get("correlation_id")
        )
    
    async def register_agent(self, agent_id: str, agent_info: Dict[str, Any]):
        """Register an agent with the bus."""
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.REGISTRATION,
            sender_id=agent_id,
            timestamp=datetime.utcnow().isoformat(),
            payload={
                "agent_info": agent_info,
                "status": "online"
            }
        )
        await self.send_message(message)
        self.logger.info(f"Agent {agent_id} registered")
    
    async def send_heartbeat(self, agent_id: str, status: str = "active"):
        """Send a heartbeat message from an agent."""
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.HEARTBEAT,
            sender_id=agent_id,
            timestamp=datetime.utcnow().isoformat(),
            payload={
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        await self.send_message(message)
    
    async def request_collaboration(self, job_id: str, requesting_agent: str, target_agents: List[str]):
        """Request collaboration on a job."""
        for target_agent in target_agents:
            message = AgentMessage(
                message_id=str(uuid.uuid4()),
                message_type=MessageType.COLLABORATION_REQUEST,
                sender_id=requesting_agent,
                timestamp=datetime.utcnow().isoformat(),
                recipient_id=target_agent,
                payload={
                    "job_id": job_id,
                    "requesting_agent": requesting_agent,
                    "collaboration_type": "research"
                }
            )
            await self.send_message(message)
    
    async def respond_to_collaboration(self, job_id: str, responding_agent: str, target_agent: str, accepted: bool):
        """Respond to a collaboration request."""
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.COLLABORATION_RESPONSE,
            sender_id=responding_agent,
            timestamp=datetime.utcnow().isoformat(),
            recipient_id=target_agent,
            payload={
                "job_id": job_id,
                "responding_agent": responding_agent,
                "accepted": accepted
            }
        )
        await self.send_message(message)
    
    async def assign_task(self, job_id: str, agent_id: str, task_details: Dict[str, Any]):
        """Assign a task to an agent."""
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.TASK_ASSIGNMENT,
            sender_id="system",
            timestamp=datetime.utcnow().isoformat(),
            recipient_id=agent_id,
            payload={
                "job_id": job_id,
                "task_details": task_details
            }
        )
        await self.send_message(message)
    
    async def report_metric(self, agent_id: str, metric_name: str, value: float):
        """Report a metric from an agent."""
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.METRIC_REPORT,
            sender_id=agent_id,
            timestamp=datetime.utcnow().isoformat(),
            payload={
                "metric_name": metric_name,
                "value": value
            }
        )
        await self.send_message(message)
    
    async def shutdown_agent(self, agent_id: str, reason: str = "shutdown"):
        """Send shutdown message to an agent."""
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.SHUTDOWN,
            sender_id="system",
            timestamp=datetime.utcnow().isoformat(),
            recipient_id=agent_id,
            payload={
                "reason": reason
            }
        )
        await self.send_message(message)


class AgentBusManager:
    """Manager for the agent bus with automatic message handling."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.bus = AgentBus(redis_url)
        self.running = False
        self.handlers = {}
        
    async def start(self):
        """Start the agent bus manager."""
        await self.bus.connect()
        self.running = True
        
        # Register default handlers
        self._register_default_handlers()
        
        # Start message processing loop
        asyncio.create_task(self._message_processing_loop())
        
        self.bus.logger.info("Agent bus manager started")
    
    async def stop(self):
        """Stop the agent bus manager."""
        self.running = False
        await self.bus.disconnect()
        self.bus.logger.info("Agent bus manager stopped")
    
    def _register_default_handlers(self):
        """Register default message handlers."""
        self.bus.register_handler(MessageType.REGISTRATION, self._handle_registration)
        self.bus.register_handler(MessageType.HEARTBEAT, self._handle_heartbeat)
        self.bus.register_handler(MessageType.COLLABORATION_REQUEST, self._handle_collaboration_request)
        self.bus.register_handler(MessageType.COLLABORATION_RESPONSE, self._handle_collaboration_response)
        self.bus.register_handler(MessageType.METRIC_REPORT, self._handle_metric_report)
        self.bus.register_handler(MessageType.SHUTDOWN, self._handle_shutdown)
    
    async def _message_processing_loop(self):
        """Main message processing loop."""
        async for message in self.bus.listen_for_messages():
            if message.message_type in self.bus.message_handlers:
                for handler in self.bus.message_handlers[message.message_type]:
                    try:
                        await handler(message)
                    except Exception as e:
                        self.bus.logger.error(f"Error in handler {handler.__name__}: {e}")
    
    async def _handle_registration(self, message: AgentMessage):
        """Handle agent registration."""
        agent_info = message.payload.get("agent_info", {})
        self.bus.logger.info(f"Agent {message.sender_id} registered: {agent_info}")
    
    async def _handle_heartbeat(self, message: AgentMessage):
        """Handle agent heartbeat."""
        status = message.payload.get("status", "unknown")
        self.bus.logger.debug(f"Heartbeat from {message.sender_id}: {status}")
    
    async def _handle_collaboration_request(self, message: AgentMessage):
        """Handle collaboration request."""
        job_id = message.payload.get("job_id")
        requesting_agent = message.payload.get("requesting_agent")
        self.bus.logger.info(f"Collaboration request for job {job_id} from {requesting_agent}")
    
    async def _handle_collaboration_response(self, message: AgentMessage):
        """Handle collaboration response."""
        job_id = message.payload.get("job_id")
        accepted = message.payload.get("accepted", False)
        self.bus.logger.info(f"Collaboration response for job {job_id}: {'accepted' if accepted else 'rejected'}")
    
    async def _handle_metric_report(self, message: AgentMessage):
        """Handle metric report."""
        metric_name = message.payload.get("metric_name")
        value = message.payload.get("value")
        self.bus.logger.debug(f"Metric report from {message.sender_id}: {metric_name} = {value}")
    
    async def _handle_shutdown(self, message: AgentMessage):
        """Handle agent shutdown."""
        reason = message.payload.get("reason", "unknown")
        self.bus.logger.info(f"Agent {message.sender_id} shutting down: {reason}")


# Global agent bus instance
agent_bus_manager = AgentBusManager()


async def get_agent_bus() -> AgentBusManager:
    """Get the global agent bus manager instance."""
    return agent_bus_manager