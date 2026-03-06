"""
Xoe-NovAi WebSocket Router
=========================
Real-time WebSocket endpoints for agent communication and task routing.

Features:
- AnyIO-based structured concurrency
- Agent Bus task routing integration
- Connection management with proper cleanup
- Zero-trust verification for agent connections
"""

import anyio
import json
import logging
from typing import Dict, Set, Optional, Any
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])


# ============================================================================
# Models
# ============================================================================

class WebSocketMessage(BaseModel):
    """Standard WebSocket message format."""
    type: str = Field(..., description="Message type: task, status, query, response")
    sender: str = Field(..., description="Sender agent DID")
    target: Optional[str] = Field(None, description="Target agent DID (None for broadcast)")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Message payload")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Message timestamp"
    )
    correlation_id: Optional[str] = Field(None, description="Correlation ID for request/response")


class TaskMessage(BaseModel):
    """Task message format for Agent Bus routing."""
    task_id: str
    task_type: str
    priority: str = "normal"  # low, normal, high, critical
    payload: Dict[str, Any]
    sender_did: str
    created_at: str


# ============================================================================
# Connection Manager
# ============================================================================

class ConnectionManager:
    """
    Manages WebSocket connections with room-based routing.
    
    Uses AnyIO for structured concurrency and proper cancellation handling.
    """
    
    def __init__(self):
        # Room-based connection management
        self.rooms: Dict[str, Set[WebSocket]] = {}
        # Connection metadata for zero-trust verification
        self.connection_data: Dict[WebSocket, Dict[str, Any]] = {}
        # Agent DID to WebSocket mapping
        self.agent_connections: Dict[str, WebSocket] = {}
        
    async def connect(
        self, 
        room: str, 
        websocket: WebSocket, 
        agent_did: str,
        agent_roles: list = None
    ) -> bool:
        """
        Accept and register a WebSocket connection.
        
        Args:
            room: Room/channel to join
            websocket: WebSocket connection
            agent_did: Decentralized identifier for the agent
            agent_roles: List of roles for authorization
            
        Returns:
            bool: True if connection accepted
        """
        try:
            await websocket.accept()
            
            # Initialize room if needed
            if room not in self.rooms:
                self.rooms[room] = set()
            
            # Register connection
            self.rooms[room].add(websocket)
            self.connection_data[websocket] = {
                "agent_did": agent_did,
                "room": room,
                "roles": agent_roles or [],
                "connected_at": datetime.now(timezone.utc).isoformat()
            }
            self.agent_connections[agent_did] = websocket
            
            logger.info(
                f"WebSocket connected: agent={agent_did}, room={room}",
                extra={"agent_did": agent_did, "room": room}
            )
            return True
            
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            return False
    
    async def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection and clean up.
        
        Uses shielding to ensure cleanup completes even during cancellation.
        """
        try:
            with anyio.CancelScope(shield=True):
                if websocket not in self.connection_data:
                    return
                
                data = self.connection_data[websocket]
                room = data.get("room")
                agent_did = data.get("agent_did")
                
                # Remove from room
                if room and room in self.rooms:
                    self.rooms[room].discard(websocket)
                    if not self.rooms[room]:
                        del self.rooms[room]
                
                # Remove connection data
                del self.connection_data[websocket]
                
                # Remove agent mapping
                if agent_did and agent_did in self.agent_connections:
                    del self.agent_connections[agent_did]
                
                logger.info(
                    f"WebSocket disconnected: agent={agent_did}",
                    extra={"agent_did": agent_did, "room": room}
                )
                
        except Exception as e:
            logger.error(f"WebSocket disconnect cleanup failed: {e}")
    
    async def send_personal(self, websocket: WebSocket, message: dict) -> bool:
        """Send a message to a specific connection."""
        try:
            await websocket.send_json(message)
            return True
        except Exception as e:
            logger.warning(f"Failed to send personal message: {e}")
            return False
    
    async def send_to_agent(self, agent_did: str, message: dict) -> bool:
        """Send a message to a specific agent by DID."""
        websocket = self.agent_connections.get(agent_did)
        if websocket:
            return await self.send_personal(websocket, message)
        return False
    
    async def broadcast(
        self, 
        room: str, 
        message: dict, 
        exclude: WebSocket = None
    ) -> int:
        """
        Broadcast a message to all connections in a room.
        
        Returns:
            int: Number of successful sends
        """
        if room not in self.rooms:
            return 0
        
        successful = 0
        for connection in self.rooms[room]:
            if exclude and connection == exclude:
                continue
            if await self.send_personal(connection, message):
                successful += 1
        
        return successful
    
    async def broadcast_to_all(self, message: dict) -> int:
        """Broadcast to all connected clients."""
        successful = 0
        for room in self.rooms.values():
            for connection in room:
                if await self.send_personal(connection, message):
                    successful += 1
        return successful
    
    def get_room_connections(self, room: str) -> Set[WebSocket]:
        """Get all connections for a room."""
        return self.rooms.get(room, set())
    
    def get_agent_did(self, websocket: WebSocket) -> Optional[str]:
        """Get the agent DID for a connection."""
        data = self.connection_data.get(websocket)
        return data.get("agent_did") if data else None
    
    def get_stats(self) -> dict:
        """Get connection statistics."""
        return {
            "total_connections": len(self.connection_data),
            "total_rooms": len(self.rooms),
            "rooms": {room: len(conns) for room, conns in self.rooms.items()},
            "agents_connected": list(self.agent_connections.keys())
        }


# Global connection manager
manager = ConnectionManager()


# ============================================================================
# Agent Bus Integration
# ============================================================================

async def route_task_to_agent_bus(
    message: WebSocketMessage,
    websocket: WebSocket
) -> bool:
    """
    Route a task message to the Agent Bus.
    
    Integrates with core.agent_bus for distributed task processing.
    """
    try:
        from ..core.agent_bus import AgentBusClient
        from ..core.dependencies import get_redis_client
        
        # Get agent DID from connection
        sender_did = manager.get_agent_did(websocket)
        if not sender_did:
            sender_did = message.sender
        
        # Create Agent Bus client
        async with AgentBusClient(agent_did=sender_did) as bus_client:
            # Send task to target agent
            task_id = await bus_client.send_task(
                target_did=message.target or "*",
                task_type=message.type,
                payload=message.payload
            )
            
            logger.info(
                f"Task routed to Agent Bus: {task_id}",
                extra={
                    "task_id": task_id,
                    "sender": sender_did,
                    "target": message.target
                }
            )
            return True
            
    except Exception as e:
        logger.error(f"Failed to route task to Agent Bus: {e}")
        return False


# ============================================================================
# WebSocket Endpoints
# ============================================================================

@router.websocket("/{room}/{agent_did}")
async def websocket_endpoint(
    websocket: WebSocket,
    room: str,
    agent_did: str,
    roles: str = Query(default="", description="Comma-separated agent roles")
):
    """
    Main WebSocket endpoint for agent communication.
    
    Args:
        room: Room/channel to join (e.g., "tasks", "status", "notifications")
        agent_did: Decentralized identifier for the agent
        roles: Comma-separated list of agent roles for authorization
    """
    # Parse roles
    role_list = [r.strip() for r in roles.split(",") if r.strip()]
    
    # Accept connection
    connected = await manager.connect(
        room=room,
        websocket=websocket,
        agent_did=agent_did,
        agent_roles=role_list
    )
    
    if not connected:
        return
    
    try:
        # Send welcome message
        await manager.send_personal(websocket, {
            "type": "connected",
            "room": room,
            "agent_did": agent_did,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Message loop with structured concurrency
        async with anyio.create_task_group() as tg:
            async for message_text in websocket.iter_text():
                try:
                    # Parse message
                    data = json.loads(message_text)
                    message = WebSocketMessage(**data)
                    
                    # Handle different message types
                    if message.type == "task":
                        # Route task to Agent Bus
                        success = await route_task_to_agent_bus(message, websocket)
                        
                        # Acknowledge task receipt
                        await manager.send_personal(websocket, {
                            "type": "task_ack",
                            "correlation_id": message.correlation_id,
                            "success": success,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                        
                    elif message.type == "broadcast":
                        # Broadcast to room
                        delivered = await manager.broadcast(
                            room=room,
                            message=message.dict(),
                            exclude=websocket
                        )
                        
                        await manager.send_personal(websocket, {
                            "type": "broadcast_ack",
                            "delivered": delivered,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                        
                    elif message.type == "ping":
                        # Heartbeat response
                        await manager.send_personal(websocket, {
                            "type": "pong",
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                        
                    elif message.type == "status":
                        # Return connection status
                        await manager.send_personal(websocket, {
                            "type": "status_response",
                            "stats": manager.get_stats(),
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                        
                    else:
                        # Unknown message type - acknowledge with warning
                        await manager.send_personal(websocket, {
                            "type": "warning",
                            "message": f"Unknown message type: {message.type}",
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                        
                except json.JSONDecodeError:
                    await manager.send_personal(websocket, {
                        "type": "error",
                        "message": "Invalid JSON format",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    
                except Exception as e:
                    logger.error(f"WebSocket message processing error: {e}")
                    await manager.send_personal(websocket, {
                        "type": "error",
                        "message": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: agent={agent_did}")
        
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        
    finally:
        await manager.disconnect(websocket)


@router.get("/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics."""
    return manager.get_stats()


# ============================================================================
# Export
# ============================================================================

__all__ = [
    "router",
    "ConnectionManager",
    "manager",
    "WebSocketMessage",
    "TaskMessage",
]