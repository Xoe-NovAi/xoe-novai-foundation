#!/usr/bin/env python3
"""
Manual Cline Dispatch with Model Preference Tests
=================================================

Manual test for Cline dispatch functionality with model preference support.
This test manually verifies the functionality without complex imports.

Usage:
  python3 tests/test_cline_dispatch_manual.py
"""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from typing import Dict, Any


def test_imports():
    """Test that we can import the agent_watcher module."""
    print("Testing imports...")
    
    # Add the project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    try:
        # Try importing the module directly
        import scripts.agent_watcher as agent_watcher
        print("✓ Successfully imported scripts.agent_watcher")
        return True
    except ImportError as e:
        print(f"✗ Failed to import scripts.agent_watcher: {e}")
        return False


def test_execute_task_function():
    """Test the execute_task function directly."""
    print("\nTesting execute_task function...")
    
    # Add the project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    try:
        import scripts.agent_watcher as agent_watcher
        
        # Test with mock
        with patch('scripts.agent_watcher.stream_command') as mock_stream_command:
            mock_stream_command.return_value = ("Test output", 0)
            
            # Test with model preference
            output, code = agent_watcher.execute_task("cline", "Test task", "test-model")
            
            # Verify command was called correctly
            mock_stream_command.assert_called_once()
            call_args = mock_stream_command.call_args[0]
            cmd = call_args[0]
            
            # Verify command structure
            assert cmd[0] == "cline"
            assert "--yolo" in cmd
            assert "--json" in cmd
            assert "--model" in cmd
            assert "test-model" in cmd
            assert "Test task" in cmd
            
            # Verify return values
            assert output == "Test output"
            assert code == 0
            
            print("✓ execute_task with model preference works correctly")
            
            # Reset mock
            mock_stream_command.reset_mock()
            
            # Test without model preference
            output, code = agent_watcher.execute_task("cline", "Test task", None)
            
            # Verify command was called correctly
            mock_stream_command.assert_called_once()
            call_args = mock_stream_command.call_args[0]
            cmd = call_args[0]
            
            # Verify command structure (no --model flag)
            assert cmd[0] == "cline"
            assert "--yolo" in cmd
            assert "--json" in cmd
            assert "--model" not in cmd
            assert "Test task" in cmd
            
            # Verify return values
            assert output == "Test output"
            assert code == 0
            
            print("✓ execute_task without model preference works correctly")
            return True
            
    except Exception as e:
        print(f"✗ execute_task test failed: {e}")
        return False


def test_process_message_function():
    """Test the process_message function directly."""
    print("\nTesting process_message function...")
    
    # Add the project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    try:
        import scripts.agent_watcher as agent_watcher
        
        # Create test environment
        test_dir = Path(tempfile.mkdtemp())
        inbox_dir = test_dir / "inbox"
        outbox_dir = test_dir / "outbox"
        state_dir = test_dir / "state"
        
        inbox_dir.mkdir(parents=True, exist_ok=True)
        outbox_dir.mkdir(parents=True, exist_ok=True)
        state_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test message with model preference
        message = {
            "message_id": f"test-msg-{int(time.time())}",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "sender": "test_system",
            "target": "cline",
            "type": "task",
            "description": "Test task",
            "model_preference": "test-model-v3"
        }
        
        message_path = inbox_dir / "test_message.json"
        with open(message_path, 'w') as f:
            json.dump(message, f)
        
        # Mock execute_task to capture parameters
        with patch('scripts.agent_watcher.execute_task') as mock_execute:
            mock_execute.return_value = ("Test output", 0)
            
            # Process the message
            agent_watcher.process_message("cline", message_path)
            
            # Verify execute_task was called with correct parameters
            mock_execute.assert_called_once()
            call_args = mock_execute.call_args[0]
            assert call_args[0] == "cline"
            assert call_args[1] == "Test task"
            assert call_args[2] == "test-model-v3"
            
            print("✓ process_message with model preference works correctly")
            
            # Cleanup
            import shutil
            shutil.rmtree(test_dir, ignore_errors=True)
            return True
            
    except Exception as e:
        print(f"✗ process_message test failed: {e}")
        return False


def test_model_preference_extraction():
    """Test model preference extraction from messages."""
    print("\nTesting model preference extraction...")
    
    # Add the project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    try:
        import scripts.agent_watcher as agent_watcher
        
        # Test message with model preference at root
        message_with_preference = {
            "message_id": "test-msg-123",
            "sender": "test_system",
            "target": "cline",
            "type": "task",
            "description": "Test task",
            "model_preference": "test-model-v3"
        }
        
        # Test message without model preference
        message_without_preference = {
            "message_id": "test-msg-456",
            "sender": "test_system",
            "target": "cline",
            "type": "task",
            "description": "Test task without model preference"
        }
        
        # Test message with model preference in content
        message_with_content_preference = {
            "message_id": "test-msg-789",
            "sender": "test_system",
            "target": "cline",
            "type": "task",
            "content": {
                "description": "Test task",
                "model_preference": "test-model-v4"
            }
        }
        
        # Test each message type individually
        for i, (message, expected_model) in enumerate([
            (message_with_preference, "test-model-v3"),
            (message_without_preference, None),
            (message_with_content_preference, "test-model-v4")
        ]):
            # Create test environment for each message
            test_dir = Path(tempfile.mkdtemp())
            inbox_dir = test_dir / "inbox"
            outbox_dir = test_dir / "outbox"
            state_dir = test_dir / "state"
            
            inbox_dir.mkdir(parents=True, exist_ok=True)
            outbox_dir.mkdir(parents=True, exist_ok=True)
            state_dir.mkdir(parents=True, exist_ok=True)
            
            message_path = inbox_dir / f"test_message_{i}.json"
            with open(message_path, 'w') as f:
                json.dump(message, f)
            
            # Mock execute_task to capture parameters
            with patch('scripts.agent_watcher.execute_task') as mock_execute:
                mock_execute.return_value = ("Test output", 0)
                
                # Process the message
                agent_watcher.process_message("cline", message_path)
                
                # Verify execute_task was called with correct model preference
                mock_execute.assert_called_once()
                call_args = mock_execute.call_args[0]
                assert call_args[0] == "cline"
                assert call_args[1] == message.get("description") or message.get("content", {}).get("description")
                assert call_args[2] == expected_model
            
            # Cleanup
            import shutil
            shutil.rmtree(test_dir, ignore_errors=True)
        
        print("✓ Model preference extraction works correctly")
        return True
        
    except Exception as e:
        print(f"✗ Model preference extraction test failed: {e}")
        return False


def main():
    """Run all manual tests."""
    print("=== Manual Cline Dispatch with Model Preference Tests ===\n")
    
    tests = [
        test_imports,
        test_execute_task_function,
        test_process_message_function,
        test_model_preference_extraction
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())