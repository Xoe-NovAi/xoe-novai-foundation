#!/usr/bin/env python3
"""
Simple Cline Dispatch with Model Preference Tests
=================================================

Simplified test for Cline dispatch functionality with model preference support.
This test directly imports and tests the agent_watcher module.

Usage:
  pytest tests/test_cline_dispatch_simple.py -v
"""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
import sys
import os
from typing import Dict, Any


# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestClineDispatchSimple:
    """Simple test for Cline dispatch with model preference functionality."""

    def setup_method(self):
        """Setup test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.inbox_dir = self.test_dir / "inbox"
        self.outbox_dir = self.test_dir / "outbox"
        self.state_dir = self.test_dir / "state"
        
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        self.outbox_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_test_message(self, agent_name: str, task_desc: str, model_preference: str = None) -> Dict[str, Any]:
        """Create a test message with optional model preference."""
        message = {
            "message_id": f"test-msg-{int(time.time())}",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "sender": "test_system",
            "target": agent_name,
            "type": "task",
            "description": task_desc
        }
        
        if model_preference:
            message["model_preference"] = model_preference
        
        return message

    @patch('scripts.agent_watcher.stream_command')
    def test_cline_dispatch_with_model_preference(self, mock_stream_command):
        """Test Cline dispatch with explicit model preference."""
        # Setup mock response
        mock_stream_command.return_value = ("Test output", 0)
        
        # Import the module
        from scripts.agent_watcher import execute_task
        
        # Test with model preference
        task_desc = "Test task description"
        model_name = "test-model-v2"
        
        output, code = execute_task("cline", task_desc, model_name)
        
        # Verify command was called correctly
        mock_stream_command.assert_called_once()
        call_args = mock_stream_command.call_args[0]
        cmd = call_args[0]
        
        # Verify command structure
        assert cmd[0] == "cline"
        assert "--yolo" in cmd
        assert "--json" in cmd
        assert "--model" in cmd
        assert model_name in cmd
        assert task_desc in cmd
        
        # Verify return values
        assert output == "Test output"
        assert code == 0

    @patch('scripts.agent_watcher.stream_command')
    def test_cline_dispatch_without_model_preference(self, mock_stream_command):
        """Test Cline dispatch without model preference (should use defaults)."""
        # Setup mock response
        mock_stream_command.return_value = ("Test output", 0)
        
        # Import the module
        from scripts.agent_watcher import execute_task
        
        # Test without model preference
        task_desc = "Test task description"
        
        output, code = execute_task("cline", task_desc, None)
        
        # Verify command was called correctly
        mock_stream_command.assert_called_once()
        call_args = mock_stream_command.call_args[0]
        cmd = call_args[0]
        
        # Verify command structure (no --model flag)
        assert cmd[0] == "cline"
        assert "--yolo" in cmd
        assert "--json" in cmd
        assert "--model" not in cmd
        assert task_desc in cmd
        
        # Verify return values
        assert output == "Test output"
        assert code == 0

    @patch('scripts.agent_watcher.stream_command')
    def test_kat_agent_dispatch_with_model_preference(self, mock_stream_command):
        """Test Kat agent dispatch with model preference."""
        # Setup mock response
        mock_stream_command.return_value = ("Test output", 0)
        
        # Import the module
        from scripts.agent_watcher import execute_task
        
        # Test with Kat agent and model preference
        task_desc = "Test Kat task"
        model_name = "kwaipilot/kat-coder-pro-v2"
        
        output, code = execute_task("kat-agent", task_desc, model_name)
        
        # Verify command was called correctly
        mock_stream_command.assert_called_once()
        call_args = mock_stream_command.call_args[0]
        cmd = call_args[0]
        
        # Verify command structure
        assert cmd[0] == "cline"
        assert "--yolo" in cmd
        assert "--silent" in cmd
        assert "--model" in cmd
        assert model_name in cmd
        assert task_desc in cmd
        
        # Verify log prefix
        call_kwargs = mock_stream_command.call_args[1]
        assert call_kwargs.get('log_prefix') == '[KAT-AGENT]'

    @patch('scripts.agent_watcher.stream_command')
    def test_kat_agent_dispatch_without_model_preference(self, mock_stream_command):
        """Test Kat agent dispatch without model preference (should use default)."""
        # Setup mock response
        mock_stream_command.return_value = ("Test output", 0)
        
        # Import the module
        from scripts.agent_watcher import execute_task
        
        # Test with Kat agent without model preference
        task_desc = "Test Kat task"
        
        output, code = execute_task("kat-agent", task_desc, None)
        
        # Verify command was called correctly
        mock_stream_command.assert_called_once()
        call_args = mock_stream_command.call_args[0]
        cmd = call_args[0]
        
        # Verify command structure (should use default model)
        assert cmd[0] == "cline"
        assert "--yolo" in cmd
        assert "--silent" in cmd
        assert "--model" in cmd
        assert "kwaipilot/kat-coder-pro" in cmd  # Default model
        assert task_desc in cmd
        
        # Verify log prefix
        call_kwargs = mock_stream_command.call_args[1]
        assert call_kwargs.get('log_prefix') == '[KAT-AGENT]'

    @patch('scripts.agent_watcher.stream_command')
    def test_cline_like_agent_dispatch(self, mock_stream_command):
        """Test dispatch for agents with 'cline' in name."""
        # Setup mock response
        mock_stream_command.return_value = ("Test output", 0)
        
        # Import the module
        from scripts.agent_watcher import execute_task
        
        # Test with agent name containing 'cline'
        task_desc = "Test cline-like agent task"
        model_name = "custom-cline-model"
        
        output, code = execute_task("my-cline-agent", task_desc, model_name)
        
        # Verify command was called correctly
        mock_stream_command.assert_called_once()
        call_args = mock_stream_command.call_args[0]
        cmd = call_args[0]
        
        # Verify command structure
        assert cmd[0] == "cline"
        assert "--yolo" in cmd
        assert "--silent" in cmd
        assert "--model" in cmd
        assert model_name in cmd
        assert task_desc in cmd
        
        # Verify log prefix
        call_kwargs = mock_stream_command.call_args[1]
        assert call_kwargs.get('log_prefix') == '[MY-CLINE-AGENT]'

    @patch('scripts.agent_watcher.stream_command')
    def test_unknown_agent_handling(self, mock_stream_command):
        """Test handling of unknown agent types."""
        # Import the module
        from scripts.agent_watcher import execute_task
        
        # Test with unknown agent
        output, code = execute_task("unknown-agent", "Test task", None)
        
        # Should return error message and code 1
        assert output == "Unknown agent"
        assert code == 1
        
        # stream_command should not be called for unknown agents
        mock_stream_command.assert_not_called()

    def test_model_preference_extraction_from_root(self):
        """Test model preference extraction from root level of message."""
        # Import the module
        from scripts.agent_watcher import process_message
        
        # Create test message with model preference at root
        message = self.create_test_message(
            agent_name="cline",
            task_desc="Test task",
            model_preference="test-model-v3"
        )
        
        message_path = self.inbox_dir / "test_message.json"
        with open(message_path, 'w') as f:
            json.dump(message, f)
        
        # Mock execute_task to capture parameters
        with patch('scripts.agent_watcher.execute_task') as mock_execute:
            mock_execute.return_value = ("Test output", 0)
            
            # Process the message
            process_message("cline", message_path)
            
            # Verify execute_task was called with correct parameters
            mock_execute.assert_called_once()
            call_args = mock_execute.call_args[0]
            assert call_args[0] == "cline"
            assert call_args[1] == "Test task"
            assert call_args[2] == "test-model-v3"

    def test_model_preference_fallback_to_description(self):
        """Test fallback to description when model preference is not specified."""
        # Import the module
        from scripts.agent_watcher import process_message
        
        # Create test message without model preference
        message = self.create_test_message(
            agent_name="cline",
            task_desc="Test task without model preference"
        )
        
        message_path = self.inbox_dir / "test_message.json"
        with open(message_path, 'w') as f:
            json.dump(message, f)
        
        # Mock execute_task to capture parameters
        with patch('scripts.agent_watcher.execute_task') as mock_execute:
            mock_execute.return_value = ("Test output", 0)
            
            # Process the message
            process_message("cline", message_path)
            
            # Verify execute_task was called with correct parameters
            mock_execute.assert_called_once()
            call_args = mock_execute.call_args[0]
            assert call_args[0] == "cline"
            assert call_args[1] == "Test task without model preference"
            assert call_args[2] is None  # No model preference

    def test_response_file_creation(self):
        """Test that response files are created in outbox directory."""
        # Import the module
        from scripts.agent_watcher import process_message
        
        # Create test message
        message = self.create_test_message(
            agent_name="cline",
            task_desc="Test task for response creation"
        )
        
        message_path = self.inbox_dir / "test_message.json"
        with open(message_path, 'w') as f:
            json.dump(message, f)
        
        # Mock execute_task to return success
        with patch('scripts.agent_watcher.execute_task') as mock_execute:
            mock_execute.return_value = ("Test output", 0)
            
            # Process the message
            process_message("cline", message_path)
            
            # Verify response file was created
            response_files = list(self.outbox_dir.glob("*.json"))
            assert len(response_files) == 1
            
            # Verify response content
            with open(response_files[0], 'r') as f:
                response = json.load(f)
            
            assert response['sender'] == "cline"
            assert response['target'] == "test_system"
            assert response['type'] == "task_completion"
            assert response['content']['status'] == "success"
            assert response['content']['exit_code'] == 0

    def test_message_deletion_after_success(self):
        """Test that message files are deleted after successful processing."""
        # Import the module
        from scripts.agent_watcher import process_message
        
        # Create test message
        message = self.create_test_message(
            agent_name="cline",
            task_desc="Test task for deletion"
        )
        
        message_path = self.inbox_dir / "test_message.json"
        with open(message_path, 'w') as f:
            json.dump(message, f)
        
        # Verify message exists before processing
        assert message_path.exists()
        
        # Mock execute_task to return success
        with patch('scripts.agent_watcher.execute_task') as mock_execute:
            mock_execute.return_value = ("Test output", 0)
            
            # Process the message
            process_message("cline", message_path)
            
            # Verify message was deleted after successful processing
            assert not message_path.exists()

    @patch('scripts.agent_watcher.stream_command')
    def test_error_handling_in_execution(self, mock_stream_command):
        """Test error handling when execution fails."""
        # Setup mock to raise exception
        mock_stream_command.side_effect = Exception("Test execution error")
        
        # Import the module
        from scripts.agent_watcher import process_message
        
        # Create test message
        message = self.create_test_message(
            agent_name="cline",
            task_desc="Test task that will fail"
        )
        
        message_path = self.inbox_dir / "test_message.json"
        with open(message_path, 'w') as f:
            json.dump(message, f)
        
        # Process the message (should handle the exception)
        process_message("cline", message_path)
        
        # Verify state file shows error status
        state_files = list(self.state_dir.glob("*.json"))
        assert len(state_files) == 1
        
        with open(state_files[0], 'r') as f:
            state = json.load(f)
        
        assert state['status'] == "error"
        assert 'error' in state


class TestClineDispatchIntegration:
    """Integration tests for Cline dispatch functionality."""

    def setup_method(self):
        """Setup test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.inbox_dir = self.test_dir / "inbox"
        self.outbox_dir = self.test_dir / "outbox"
        self.state_dir = self.test_dir / "state"
        
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        self.outbox_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('scripts.agent_watcher.stream_command')
    def test_full_message_processing_flow(self, mock_stream_command):
        """Test the complete message processing flow."""
        # Setup mock response
        mock_stream_command.return_value = ("Test output", 0)
        
        # Import the module
        from scripts.agent_watcher import process_message
        
        # Create comprehensive test message
        message = {
            "message_id": "test-full-flow-123",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "sender": "test_system",
            "target": "cline",
            "type": "task",
            "description": "Comprehensive test task",
            "model_preference": "test-model-integration",
            "priority": "high",
            "metadata": {
                "test_type": "integration",
                "created_by": "test_framework"
            }
        }
        
        message_path = self.inbox_dir / "test_full_flow.json"
        with open(message_path, 'w') as f:
            json.dump(message, f, indent=2)
        
        # Process the message
        process_message("cline", message_path)
        
        # Verify response file was created
        response_files = list(self.outbox_dir.glob("*.json"))
        assert len(response_files) == 1
        
        with open(response_files[0], 'r') as f:
            response = json.load(f)
        
        # Verify response structure
        assert response['message_id'].startswith('resp-test-full-flow-123')
        assert response['sender'] == "cline"
        assert response['target'] == "test_system"
        assert response['type'] == "task_completion"
        assert response['content']['status'] == "success"
        assert response['content']['exit_code'] == 0
        assert "output_summary" in response['content']
        
        # Verify state file was updated
        state_files = list(self.state_dir.glob("*.json"))
        assert len(state_files) == 1
        
        with open(state_files[0], 'r') as f:
            state = json.load(f)
        
        assert state['agent_id'] == "cline"
        assert state['status'] == "idle"
        assert state['last_task_id'] == "test-full-flow-123"
        
        # Verify message was deleted
        assert not message_path.exists()

    @patch('scripts.agent_watcher.stream_command')
    def test_multiple_agent_types(self, mock_stream_command):
        """Test dispatch for multiple agent types with different model preferences."""
        # Setup mock response
        mock_stream_command.return_value = ("Test output", 0)
        
        # Import the module
        from scripts.agent_watcher import execute_task
        
        test_cases = [
            ("cline", "Test cline task", "custom-cline-model", ["--yolo", "--json", "--model", "custom-cline-model"]),
            ("kat-agent", "Test kat task", "custom-kat-model", ["--yolo", "--silent", "--model", "custom-kat-model"]),
            ("my-cline-bot", "Test cline-like task", "custom-cline-bot-model", ["--yolo", "--silent", "--model", "custom-cline-bot-model"]),
        ]
        
        for agent_name, task_desc, model_preference, expected_flags in test_cases:
            with self.subTest(agent_name=agent_name):
                # Reset mock
                mock_stream_command.reset_mock()
                
                # Execute task
                output, code = execute_task(agent_name, task_desc, model_preference)
                
                # Verify command was called
                mock_stream_command.assert_called_once()
                call_args = mock_stream_command.call_args[0]
                cmd = call_args[0]
                
                # Verify expected flags are present
                for flag in expected_flags:
                    assert flag in cmd, f"Flag '{flag}' not found in command for {agent_name}: {cmd}"
                
                # Verify task description is in command
                assert task_desc in cmd


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "--tb=short"])