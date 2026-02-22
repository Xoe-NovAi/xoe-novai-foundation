"""
Phase 7: Agent Bus Integration Tests

Tests for semantic search service integration with XNAi Agent Bus.
"""

import pytest
import json
import asyncio
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

# Import service
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.XNAi_rag_app.api.semantic_search_agent_bus import (
    SemanticSearchAgentBusService,
    Message,
    SemanticSearchRequest,
    SemanticSearchResponse
)


class TestAgentBusIntegration:
    """Integration tests for Agent Bus semantic search service"""
    
    @pytest.fixture
    def service(self):
        """Create service instance"""
        return SemanticSearchAgentBusService()
    
    @pytest.fixture
    def sample_message(self):
        """Sample task assignment message"""
        return Message(
            message_id="test-001",
            timestamp=datetime.utcnow().isoformat(),
            sender="agent_coordinator",
            target="semantic-search-service",
            type="task_assignment",
            priority="high",
            content={
                "query": "Redis cluster configuration",
                "top_k": 5,
                "min_score": 0.3
            }
        )
    
    def test_service_initialization(self, service):
        """Test service initializes correctly"""
        assert service.agent_name == "semantic-search-service"
        assert "semantic_search" in service.capabilities
        assert service.status == "initializing"
        assert service.task_count == 0
    
    def test_message_serialization(self, sample_message):
        """Test message can be serialized to JSON"""
        json_str = sample_message.to_json()
        assert isinstance(json_str, str)
        
        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed["message_id"] == "test-001"
        assert parsed["target"] == "semantic-search-service"
    
    def test_message_deserialization(self, sample_message):
        """Test message can be deserialized from JSON"""
        json_str = sample_message.to_json()
        restored = Message.from_json(json_str)
        
        assert restored.message_id == sample_message.message_id
        assert restored.sender == sample_message.sender
        assert restored.content == sample_message.content
    
    @pytest.mark.asyncio
    async def test_startup_creates_directories(self, service, tmp_path):
        """Test startup creates communication directories"""
        # Mock the index to avoid loading actual knowledge base
        service.index = Mock()
        service.index.add_chunks = Mock(return_value=100)
        
        # Mock the doc directory
        with patch('app.XNAi_rag_app.api.semantic_search_agent_bus.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            
            # This should complete without error
            result = await service.startup()
            # Note: Would need actual directory setup to test fully
    
    @pytest.mark.asyncio
    async def test_handle_task_success(self, service, sample_message):
        """Test successful task handling"""
        # Mock the search index
        service.index = Mock()
        service.index.search = Mock(return_value=[
            {
                "score": 0.75,
                "service": "redis",
                "text": "Redis configuration documentation...",
                "file": "configuration.md"
            },
            {
                "score": 0.68,
                "service": "redis",
                "text": "Redis cluster setup guide...",
                "file": "cluster.md"
            }
        ])
        
        # Mock message writing
        service._write_message = AsyncMock()
        
        # Handle task
        await service.handle_task(sample_message)
        
        # Verify task was processed
        assert service.task_count == 1
        assert service.success_count == 1
        
        # Verify response was sent
        service._write_message.assert_called_once()
        response_msg = service._write_message.call_args[0][0]
        assert response_msg.type == "task_completion"
        assert response_msg.content["status"] == "success"
        assert response_msg.content["result_count"] == 2
    
    @pytest.mark.asyncio
    async def test_handle_task_missing_query(self, service):
        """Test error handling when query is missing"""
        # Create message without query
        message = Message(
            message_id="test-002",
            timestamp=datetime.utcnow().isoformat(),
            sender="agent_coordinator",
            target="semantic-search-service",
            type="task_assignment",
            priority="high",
            content={}  # Missing query
        )
        
        # Mock message writing
        service._write_message = AsyncMock()
        
        # Handle task
        await service.handle_task(message)
        
        # Should report error
        assert service.error_count == 1
        service._write_message.assert_called_once()
        error_msg = service._write_message.call_args[0][0]
        assert error_msg.type == "error_report"
    
    @pytest.mark.asyncio
    async def test_heartbeat_message(self, service):
        """Test heartbeat message generation"""
        service._write_message = AsyncMock()
        
        await service.send_heartbeat()
        
        # Verify heartbeat was sent
        service._write_message.assert_called_once()
        heartbeat = service._write_message.call_args[0][0]
        
        assert heartbeat.type == "heartbeat"
        assert heartbeat.target == "agent_coordinator"
        assert "capabilities" in heartbeat.content
        assert "task_count" in heartbeat.content
    
    def test_get_status(self, service):
        """Test status reporting"""
        service.task_count = 10
        service.success_count = 8
        service.error_count = 2
        
        status = service.get_status()
        
        assert status["agent_name"] == "semantic-search-service"
        assert status["task_count"] == 10
        assert status["success_count"] == 8
        assert status["error_count"] == 2
        assert status["capabilities"] == service.capabilities
    
    def test_semantic_search_request_validation(self):
        """Test request validation"""
        # Valid request
        valid_req = SemanticSearchRequest(
            query="test query",
            top_k=5,
            min_score=0.3
        )
        assert valid_req.query == "test query"
        assert valid_req.top_k == 5
        
        # Invalid request (missing query)
        with pytest.raises(ValueError):
            SemanticSearchRequest(top_k=5)
    
    def test_semantic_search_response_format(self):
        """Test response format"""
        response = SemanticSearchResponse(
            query="test",
            results=[
                {"score": 0.9, "service": "redis", "text": "doc"}
            ],
            execution_time_ms=42.5,
            total_results=1
        )
        
        assert response.status == "success"
        assert response.total_results == 1
        assert response.execution_time_ms == 42.5


class TestAgentBusProtocols:
    """Test compliance with Agent Bus protocols"""
    
    def test_message_has_all_required_fields(self):
        """Test message includes all required Agent Bus fields"""
        required_fields = [
            "message_id", "timestamp", "sender", "target",
            "type", "priority", "content"
        ]
        
        message = Message(
            message_id="test",
            timestamp="2026-02-17T01:58:00Z",
            sender="service",
            target="coordinator",
            type="task_completion",
            priority="high",
            content={}
        )
        
        for field in required_fields:
            assert hasattr(message, field)
            assert getattr(message, field) is not None
    
    def test_valid_message_types(self):
        """Test message type compliance"""
        valid_types = [
            "task_assignment",
            "task_completion",
            "error_report",
            "heartbeat"
        ]
        
        for msg_type in valid_types:
            message = Message(
                message_id="test",
                timestamp="2026-02-17T01:58:00Z",
                sender="test",
                target="test",
                type=msg_type,
                priority="high",
                content={}
            )
            assert message.type == msg_type
    
    def test_valid_priorities(self):
        """Test priority compliance"""
        valid_priorities = ["high", "medium", "low"]
        
        for priority in valid_priorities:
            message = Message(
                message_id="test",
                timestamp="2026-02-17T01:58:00Z",
                sender="test",
                target="test",
                type="task_completion",
                priority=priority,
                content={}
            )
            assert message.priority == priority
    
    def test_correlation_id_optional(self):
        """Test correlation_id is optional"""
        # Without correlation_id
        msg1 = Message(
            message_id="test1",
            timestamp="2026-02-17T01:58:00Z",
            sender="test",
            target="test",
            type="heartbeat",
            priority="low",
            content={}
        )
        assert msg1.correlation_id is None
        
        # With correlation_id
        msg2 = Message(
            message_id="test2",
            timestamp="2026-02-17T01:58:00Z",
            sender="test",
            target="test",
            type="task_completion",
            priority="high",
            content={},
            correlation_id="original-task-id"
        )
        assert msg2.correlation_id == "original-task-id"


class TestSemanticSearchIntegration:
    """Integration tests with actual semantic search"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_search_flow(self):
        """Test complete search request/response flow"""
        service = SemanticSearchAgentBusService()
        
        # Mock the knowledge base loading
        service.index.chunks = [
            {"service": "redis", "text": "Redis configuration guide", "file": "redis.md"},
            {"service": "docker", "text": "Docker containerization", "file": "docker.md"}
        ]
        service.status = "ready"
        
        # Create task
        task = Message(
            message_id="e2e-test",
            timestamp=datetime.utcnow().isoformat(),
            sender="coordinator",
            target="semantic-search-service",
            type="task_assignment",
            priority="high",
            content={
                "query": "container",
                "top_k": 2,
                "min_score": 0.0
            }
        )
        
        # Mock output
        service._write_message = AsyncMock()
        
        # Execute
        await service.handle_task(task)
        
        # Verify response
        assert service._write_message.called
        response = service._write_message.call_args[0][0]
        assert response.type == "task_completion"
        assert response.correlation_id == "e2e-test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

