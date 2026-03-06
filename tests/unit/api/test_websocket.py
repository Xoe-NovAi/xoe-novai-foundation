"""
Unit tests for WebSocket endpoints.

Tests cover:
- ConnectionManager class
- WebSocket connection handling
- Message routing
- Room-based broadcasting
- Agent Bus integration
- Error handling

Task: W3-001-3
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from fastapi import WebSocket, WebSocketDisconnect


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection."""
    mock = Mock(spec=WebSocket)
    mock.accept = AsyncMock()
    mock.send_json = AsyncMock()
    mock.receive_json = AsyncMock()
    mock.close = AsyncMock()
    mock.iter_text = Mock()
    return mock


@pytest.fixture
def connection_manager():
    """Create ConnectionManager instance."""
    from app.XNAi_rag_app.api.routers.websocket import ConnectionManager

    return ConnectionManager()


# ============================================================================
# WebSocketMessage Tests
# ============================================================================


class TestWebSocketMessage:
    """Tests for WebSocketMessage Pydantic model."""

    def test_websocket_message_valid(self):
        """Test valid WebSocketMessage creation."""
        from app.XNAi_rag_app.api.routers.websocket import WebSocketMessage

        message = WebSocketMessage(
            type="task",
            sender="did:xoe:agent:test-agent",
            target="did:xoe:agent:target-agent",
            payload={"task": "test"},
            correlation_id="corr-123",
        )

        assert message.type == "task"
        assert message.sender == "did:xoe:agent:test-agent"
        assert message.target == "did:xoe:agent:target-agent"
        assert message.payload == {"task": "test"}
        assert message.correlation_id == "corr-123"

    def test_websocket_message_minimal(self):
        """Test WebSocketMessage with minimal required fields."""
        from app.XNAi_rag_app.api.routers.websocket import WebSocketMessage

        message = WebSocketMessage(type="ping", sender="did:xoe:agent:test")

        assert message.type == "ping"
        assert message.sender == "did:xoe:agent:test"
        assert message.target is None
        assert message.payload == {}
        assert message.timestamp is not None

    def test_websocket_message_timestamp_auto(self):
        """Test that timestamp is auto-generated."""
        from app.XNAi_rag_app.api.routers.websocket import WebSocketMessage

        before = datetime.now(timezone.utc)
        message = WebSocketMessage(type="test", sender="test")
        after = datetime.now(timezone.utc)

        # Parse timestamp
        msg_time = datetime.fromisoformat(message.timestamp.replace("Z", "+00:00"))

        assert before <= msg_time <= after


# ============================================================================
# TaskMessage Tests
# ============================================================================


class TestTaskMessage:
    """Tests for TaskMessage Pydantic model."""

    def test_task_message_valid(self):
        """Test valid TaskMessage creation."""
        from app.XNAi_rag_app.api.routers.websocket import TaskMessage

        task = TaskMessage(
            task_id="task-123",
            task_type="rag",
            priority="high",
            payload={"query": "test"},
            sender_did="did:xoe:agent:test",
            created_at="2026-02-23T10:00:00Z",
        )

        assert task.task_id == "task-123"
        assert task.task_type == "rag"
        assert task.priority == "high"
        assert task.payload == {"query": "test"}

    def test_task_message_default_priority(self):
        """Test TaskMessage default priority."""
        from app.XNAi_rag_app.api.routers.websocket import TaskMessage

        task = TaskMessage(
            task_id="task-123", task_type="test", payload={}, sender_did="test", created_at="2026-02-23T10:00:00Z"
        )

        assert task.priority == "normal"


# ============================================================================
# ConnectionManager Tests
# ============================================================================


class TestConnectionManager:
    """Tests for ConnectionManager class."""

    @pytest.mark.asyncio
    async def test_connect_success(self, connection_manager, mock_websocket):
        """Test successful WebSocket connection."""
        result = await connection_manager.connect(room="test-room", websocket=mock_websocket, agent_did="did:xoe:agent:test")

        assert result is True
        assert "test-room" in connection_manager.rooms
        assert mock_websocket in connection_manager.rooms["test-room"]
        assert mock_websocket in connection_manager.connection_data
        assert "did:xoe:agent:test" in connection_manager.agent_connections

    @pytest.mark.asyncio
    async def test_connect_with_roles(self, connection_manager, mock_websocket):
        """Test WebSocket connection with roles."""
        result = await connection_manager.connect(
            room="test-room", websocket=mock_websocket, agent_did="did:xoe:agent:test", agent_roles=["admin", "researcher"]
        )

        assert result is True
        assert connection_manager.connection_data[mock_websocket]["roles"] == ["admin", "researcher"]

    @pytest.mark.asyncio
    async def test_connect_failure(self, connection_manager, mock_websocket):
        """Test handling of connection failure."""
        mock_websocket.accept.side_effect = Exception("Connection failed")

        result = await connection_manager.connect(room="test-room", websocket=mock_websocket, agent_did="did:xoe:agent:test")

        assert result is False

    @pytest.mark.asyncio
    async def test_disconnect(self, connection_manager, mock_websocket):
        """Test WebSocket disconnection."""
        # First connect
        await connection_manager.connect(room="test-room", websocket=mock_websocket, agent_did="did:xoe:agent:test")

        # Then disconnect
        await connection_manager.disconnect(mock_websocket)

        assert mock_websocket not in connection_manager.connection_data
        assert "did:xoe:agent:test" not in connection_manager.agent_connections

    @pytest.mark.asyncio
    async def test_disconnect_removes_empty_room(self, connection_manager, mock_websocket):
        """Test that empty rooms are removed on disconnect."""
        # Connect single client
        await connection_manager.connect(room="test-room", websocket=mock_websocket, agent_did="did:xoe:agent:test")

        # Disconnect should remove room
        await connection_manager.disconnect(mock_websocket)

        assert "test-room" not in connection_manager.rooms

    @pytest.mark.asyncio
    async def test_send_personal(self, connection_manager, mock_websocket):
        """Test sending personal message."""
        message = {"type": "test", "data": "value"}

        result = await connection_manager.send_personal(mock_websocket, message)

        assert result is True
        mock_websocket.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_send_personal_failure(self, connection_manager, mock_websocket):
        """Test handling of personal message failure."""
        mock_websocket.send_json.side_effect = Exception("Send failed")

        message = {"type": "test", "data": "value"}

        result = await connection_manager.send_personal(mock_websocket, message)

        assert result is False

    @pytest.mark.asyncio
    async def test_send_to_agent(self, connection_manager, mock_websocket):
        """Test sending message to specific agent."""
        # Connect the agent
        await connection_manager.connect(room="test-room", websocket=mock_websocket, agent_did="did:xoe:agent:target")

        message = {"type": "test", "data": "value"}

        result = await connection_manager.send_to_agent("did:xoe:agent:target", message)

        assert result is True
        mock_websocket.send_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_to_unknown_agent(self, connection_manager):
        """Test sending message to unknown agent."""
        message = {"type": "test", "data": "value"}

        result = await connection_manager.send_to_agent("did:xoe:agent:unknown", message)

        assert result is False

    @pytest.mark.asyncio
    async def test_broadcast(self, connection_manager):
        """Test broadcasting to room."""
        # Create multiple mock websockets
        ws1 = Mock(spec=WebSocket)
        ws1.send_json = AsyncMock()
        ws2 = Mock(spec=WebSocket)
        ws2.send_json = AsyncMock()
        ws3 = Mock(spec=WebSocket)
        ws3.send_json = AsyncMock()

        # Connect all to same room
        await connection_manager.connect("test-room", ws1, "agent1")
        await connection_manager.connect("test-room", ws2, "agent2")
        await connection_manager.connect("test-room", ws3, "agent3")

        message = {"type": "broadcast", "data": "test"}

        result = await connection_manager.broadcast("test-room", message)

        assert result == 3
        ws1.send_json.assert_called_once_with(message)
        ws2.send_json.assert_called_once_with(message)
        ws3.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_broadcast_with_exclude(self, connection_manager):
        """Test broadcasting with exclusion."""
        ws1 = Mock(spec=WebSocket)
        ws1.send_json = AsyncMock()
        ws2 = Mock(spec=WebSocket)
        ws2.send_json = AsyncMock()

        await connection_manager.connect("test-room", ws1, "agent1")
        await connection_manager.connect("test-room", ws2, "agent2")

        message = {"type": "broadcast", "data": "test"}

        result = await connection_manager.broadcast("test-room", message, exclude=ws1)

        assert result == 1
        ws1.send_json.assert_not_called()
        ws2.send_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_to_empty_room(self, connection_manager):
        """Test broadcasting to non-existent room."""
        message = {"type": "broadcast", "data": "test"}

        result = await connection_manager.broadcast("nonexistent", message)

        assert result == 0

    @pytest.mark.asyncio
    async def test_broadcast_to_all(self, connection_manager):
        """Test broadcasting to all connections."""
        ws1 = Mock(spec=WebSocket)
        ws1.send_json = AsyncMock()
        ws2 = Mock(spec=WebSocket)
        ws2.send_json = AsyncMock()

        await connection_manager.connect("room1", ws1, "agent1")
        await connection_manager.connect("room2", ws2, "agent2")

        message = {"type": "global", "data": "test"}

        result = await connection_manager.broadcast_to_all(message)

        assert result == 2

    def test_get_room_connections(self, connection_manager):
        """Test getting room connections."""
        ws1 = Mock(spec=WebSocket)
        ws2 = Mock(spec=WebSocket)

        connection_manager.rooms["test-room"] = {ws1, ws2}

        connections = connection_manager.get_room_connections("test-room")

        assert len(connections) == 2
        assert ws1 in connections
        assert ws2 in connections

    def test_get_room_connections_empty(self, connection_manager):
        """Test getting connections for non-existent room."""
        connections = connection_manager.get_room_connections("nonexistent")

        assert len(connections) == 0

    def test_get_agent_did(self, connection_manager, mock_websocket):
        """Test getting agent DID for connection."""
        connection_manager.connection_data[mock_websocket] = {"agent_did": "did:xoe:agent:test"}

        did = connection_manager.get_agent_did(mock_websocket)

        assert did == "did:xoe:agent:test"

    def test_get_agent_did_unknown(self, connection_manager, mock_websocket):
        """Test getting agent DID for unknown connection."""
        did = connection_manager.get_agent_did(mock_websocket)

        assert did is None

    def test_get_stats(self, connection_manager):
        """Test getting connection statistics."""
        ws1 = Mock(spec=WebSocket)
        ws2 = Mock(spec=WebSocket)

        connection_manager.rooms = {"room1": {ws1}, "room2": {ws2}}
        connection_manager.connection_data = {ws1: {"agent_did": "agent1"}, ws2: {"agent_did": "agent2"}}
        connection_manager.agent_connections = {"agent1": ws1, "agent2": ws2}

        stats = connection_manager.get_stats()

        assert stats["total_connections"] == 2
        assert stats["total_rooms"] == 2
        assert len(stats["agents_connected"]) == 2


# ============================================================================
# WebSocket Endpoint Tests
# ============================================================================


class TestWebSocketEndpoint:
    """Tests for WebSocket endpoint behavior."""

    @pytest.mark.asyncio
    async def test_websocket_endpoint_connect(self, mock_websocket):
        """Test WebSocket endpoint connection."""
        # Setup message iterator
        mock_websocket.iter_text.return_value = iter([])

        from app.XNAi_rag_app.api.routers.websocket import websocket_endpoint, manager

        await websocket_endpoint(websocket=mock_websocket, room="test-room", agent_did="did:xoe:agent:test")

        # Verify welcome message sent
        mock_websocket.send_json.assert_called()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "connected"
        assert call_args["room"] == "test-room"

    @pytest.mark.asyncio
    async def test_websocket_endpoint_ping_pong(self, mock_websocket):
        """Test ping/pong message handling."""
        ping_message = json.dumps({"type": "ping", "sender": "did:xoe:agent:test"})

        mock_websocket.iter_text.return_value = iter([ping_message])

        from app.XNAi_rag_app.api.routers.websocket import websocket_endpoint

        await websocket_endpoint(websocket=mock_websocket, room="test-room", agent_did="did:xoe:agent:test")

        # Find pong message
        calls = [call[0][0] for call in mock_websocket.send_json.call_args_list]
        pong_found = any(c.get("type") == "pong" for c in calls)
        assert pong_found

    @pytest.mark.asyncio
    async def test_websocket_endpoint_status_request(self, mock_websocket):
        """Test status request handling."""
        status_message = json.dumps({"type": "status", "sender": "did:xoe:agent:test"})

        mock_websocket.iter_text.return_value = iter([status_message])

        from app.XNAi_rag_app.api.routers.websocket import websocket_endpoint

        await websocket_endpoint(websocket=mock_websocket, room="test-room", agent_did="did:xoe:agent:test")

        # Find status_response message
        calls = [call[0][0] for call in mock_websocket.send_json.call_args_list]
        status_found = any(c.get("type") == "status_response" for c in calls)
        assert status_found

    @pytest.mark.asyncio
    async def test_websocket_endpoint_broadcast(self, mock_websocket):
        """Test broadcast message handling."""
        broadcast_message = json.dumps({"type": "broadcast", "sender": "did:xoe:agent:test", "payload": {"data": "test"}})

        mock_websocket.iter_text.return_value = iter([broadcast_message])

        from app.XNAi_rag_app.api.routers.websocket import websocket_endpoint

        await websocket_endpoint(websocket=mock_websocket, room="test-room", agent_did="did:xoe:agent:test")

        # Find broadcast_ack message
        calls = [call[0][0] for call in mock_websocket.send_json.call_args_list]
        ack_found = any(c.get("type") == "broadcast_ack" for c in calls)
        assert ack_found

    @pytest.mark.asyncio
    async def test_websocket_endpoint_task_routing(self, mock_websocket):
        """Test task message routing to Agent Bus."""
        task_message = json.dumps(
            {
                "type": "task",
                "sender": "did:xoe:agent:test",
                "target": "did:xoe:agent:target",
                "payload": {"task": "test"},
                "correlation_id": "corr-123",
            }
        )

        mock_websocket.iter_text.return_value = iter([task_message])

        with patch("app.XNAi_rag_app.api.routers.websocket.route_task_to_agent_bus") as mock_route:
            mock_route.return_value = True

            from app.XNAi_rag_app.api.routers.websocket import websocket_endpoint

            await websocket_endpoint(websocket=mock_websocket, room="test-room", agent_did="did:xoe:agent:test")

            # Find task_ack message
            calls = [call[0][0] for call in mock_websocket.send_json.call_args_list]
            ack_found = any(c.get("type") == "task_ack" for c in calls)
            assert ack_found

    @pytest.mark.asyncio
    async def test_websocket_endpoint_invalid_json(self, mock_websocket):
        """Test handling of invalid JSON."""
        mock_websocket.iter_text.return_value = iter(["not valid json"])

        from app.XNAi_rag_app.api.routers.websocket import websocket_endpoint

        await websocket_endpoint(websocket=mock_websocket, room="test-room", agent_did="did:xoe:agent:test")

        # Should send error message
        calls = [call[0][0] for call in mock_websocket.send_json.call_args_list]
        error_found = any(c.get("type") == "error" for c in calls)
        assert error_found

    @pytest.mark.asyncio
    async def test_websocket_endpoint_unknown_type(self, mock_websocket):
        """Test handling of unknown message type."""
        unknown_message = json.dumps({"type": "unknown_type", "sender": "did:xoe:agent:test"})

        mock_websocket.iter_text.return_value = iter([unknown_message])

        from app.XNAi_rag_app.api.routers.websocket import websocket_endpoint

        await websocket_endpoint(websocket=mock_websocket, room="test-room", agent_did="did:xoe:agent:test")

        # Should send warning message
        calls = [call[0][0] for call in mock_websocket.send_json.call_args_list]
        warning_found = any(c.get("type") == "warning" for c in calls)
        assert warning_found


# ============================================================================
# Agent Bus Integration Tests
# ============================================================================


class TestAgentBusIntegration:
    """Tests for Agent Bus integration."""

    @pytest.mark.asyncio
    async def test_route_task_to_agent_bus_success(self, mock_websocket):
        """Test successful task routing to Agent Bus."""
        from app.XNAi_rag_app.api.routers.websocket import WebSocketMessage, route_task_to_agent_bus, manager

        # Register connection
        manager.connection_data[mock_websocket] = {"agent_did": "did:xoe:agent:test"}

        message = WebSocketMessage(
            type="task", sender="did:xoe:agent:test", target="did:xoe:agent:target", payload={"task": "test"}
        )

        with patch("app.XNAi_rag_app.api.routers.websocket.AgentBusClient") as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.send_task = AsyncMock(return_value="task-123")

            result = await route_task_to_agent_bus(message, mock_websocket)

            assert result is True
            mock_instance.send_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_route_task_to_agent_bus_failure(self, mock_websocket):
        """Test handling of Agent Bus routing failure."""
        from app.XNAi_rag_app.api.routers.websocket import WebSocketMessage, route_task_to_agent_bus, manager

        manager.connection_data[mock_websocket] = {"agent_did": "did:xoe:agent:test"}

        message = WebSocketMessage(
            type="task", sender="did:xoe:agent:test", target="did:xoe:agent:target", payload={"task": "test"}
        )

        with patch("app.XNAi_rag_app.api.routers.websocket.AgentBusClient") as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.send_task.side_effect = Exception("Bus error")

            result = await route_task_to_agent_bus(message, mock_websocket)

            assert result is False


# ============================================================================
# WebSocket Stats Endpoint Tests
# ============================================================================


class TestWebSocketStats:
    """Tests for WebSocket stats endpoint."""

    @pytest.mark.asyncio
    async def test_get_websocket_stats(self):
        """Test getting WebSocket statistics."""
        from app.XNAi_rag_app.api.routers.websocket import get_websocket_stats, manager

        # Add some test data
        manager.rooms = {"room1": set()}
        manager.connection_data = {}
        manager.agent_connections = {}

        result = await get_websocket_stats()

        assert "total_connections" in result
        assert "total_rooms" in result
        assert "rooms" in result
        assert "agents_connected" in result


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestWebSocketErrorHandling:
    """Tests for WebSocket error handling."""

    @pytest.mark.asyncio
    async def test_disconnect_during_message_handling(self, mock_websocket):
        """Test handling of disconnect during message processing."""
        message = json.dumps({"type": "ping", "sender": "test"})

        mock_websocket.iter_text.return_value = iter([message])
        mock_websocket.send_json.side_effect = WebSocketDisconnect()

        from app.XNAi_rag_app.api.routers.websocket import websocket_endpoint

        # Should handle WebSocketDisconnect gracefully
        await websocket_endpoint(websocket=mock_websocket, room="test-room", agent_did="did:xoe:agent:test")

    @pytest.mark.asyncio
    async def test_cleanup_on_exception(self, mock_websocket):
        """Test cleanup happens even on exception."""
        mock_websocket.iter_text.side_effect = Exception("Test error")

        from app.XNAi_rag_app.api.routers.websocket import websocket_endpoint, manager

        await websocket_endpoint(websocket=mock_websocket, room="test-room", agent_did="did:xoe:agent:test")

        # Verify cleanup happened
        assert mock_websocket not in manager.connection_data


# ============================================================================
# Concurrency Tests
# ============================================================================


class TestWebSocketConcurrency:
    """Tests for concurrent WebSocket handling."""

    @pytest.mark.asyncio
    async def test_concurrent_connections_same_room(self):
        """Test multiple concurrent connections to same room."""
        from app.XNAi_rag_app.api.routers.websocket import ConnectionManager

        manager = ConnectionManager()

        async def connect_agent(agent_id):
            ws = Mock(spec=WebSocket)
            ws.accept = AsyncMock()
            ws.send_json = AsyncMock()
            ws.iter_text.return_value = iter([])

            await manager.connect(room="shared-room", websocket=ws, agent_did=f"did:xoe:agent:{agent_id}")
            return ws

        # Connect multiple agents concurrently
        import asyncio

        websockets = await asyncio.gather(*[connect_agent(i) for i in range(5)])

        # All should be in the same room
        assert len(manager.rooms["shared-room"]) == 5
        assert len(manager.agent_connections) == 5
