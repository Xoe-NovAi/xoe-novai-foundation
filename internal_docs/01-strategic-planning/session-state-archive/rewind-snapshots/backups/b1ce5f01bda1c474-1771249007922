# Cline Dispatch with Model Preference Test Plan

## Overview
Test the Cline dispatch functionality with model preference support as implemented in `scripts/agent_watcher.py`.

## Test Scenarios

### 1. Basic Model Preference Functionality
- [ ] Test Cline dispatch with explicit model preference
- [ ] Test Cline dispatch without model preference (default behavior)
- [ ] Test Kat agent dispatch with model preference
- [ ] Test Kat agent dispatch without model preference (default model)

### 2. Message Processing
- [ ] Test model preference extraction from root level of message
- [ ] Test model preference extraction from content section
- [ ] Test fallback to description when no model preference specified
- [ ] Test unknown agent handling

### 3. Integration Tests
- [ ] Test full message processing flow
- [ ] Test multiple agent types with different model preferences
- [ ] Test response file creation in outbox
- [ ] Test state file updates
- [ ] Test message deletion after successful processing

### 4. Error Handling
- [ ] Test error handling during execution
- [ ] Test error state updates
- [ ] Test graceful handling of malformed messages

## Test Execution Commands

```bash
# Run all Cline dispatch tests
pytest tests/test_cline_dispatch_model_preference.py -v

# Run with coverage
pytest tests/test_cline_dispatch_model_preference.py -v --cov

# Run specific test class
pytest tests/test_cline_dispatch_model_preference.py::TestClineDispatchModelPreference -v

# Run specific test method
pytest tests/test_cline_dispatch_model_preference.py::TestClineDispatchModelPreference::test_cline_dispatch_with_model_preference -v
```

## Expected Results

### Success Criteria
- All model preference extraction tests pass
- Command construction includes correct model parameters
- Agent dispatch works for all supported agent types
- Error handling is robust and graceful
- State management works correctly

### Key Validation Points
1. **Model Preference Extraction**: Correctly extracts from both root and content sections
2. **Command Construction**: Properly builds Cline commands with --model flag
3. **Agent Dispatch**: Supports cline, kat, copilot, gemini, and cline-like agents
4. **Fallback Behavior**: Uses appropriate defaults when no model preference specified
5. **Error Handling**: Graceful handling of unknown agents and execution failures

## Test Data

### Sample Messages for Testing

**Message with model preference at root:**
```json
{
  "message_id": "test-msg-123",
  "timestamp": "2026-01-15T19:40:00Z",
  "sender": "test_system",
  "target": "cline",
  "type": "task",
  "description": "Test task description",
  "model_preference": "test-model-v2"
}
```

**Message with model preference in content:**
```json
{
  "message_id": "test-msg-456",
  "timestamp": "2026-01-15T19:40:00Z",
  "sender": "test_system",
  "target": "cline",
  "type": "task",
  "content": {
    "description": "Test task description",
    "model_preference": "test-model-v3"
  }
}
```

**Message without model preference:**
```json
{
  "message_id": "test-msg-789",
  "timestamp": "2026-01-15T19:40:00Z",
  "sender": "test_system",
  "target": "cline",
  "type": "task",
  "description": "Test task without model preference"
}
```

## Implementation Notes

### Key Files
- **Main Implementation**: `scripts/agent_watcher.py`
- **Test File**: `tests/test_cline_dispatch_model_preference.py`
- **Core Dispatch Logic**: `execute_task()` function

### Model Preference Flow
1. Message received in inbox
2. `process_message()` extracts model preference from root or content
3. `execute_task()` constructs appropriate command with model parameter
4. Command executed via `stream_command()`
5. Response written to outbox with results

### Agent Type Support
- **cline**: Uses `--yolo --json --model <model>`
- **kat-like**: Uses `--yolo --silent --model <model>`
- **copilot**: Forces `claude-haiku-4.5` model
- **gemini**: Uses `--yolo --prompt --output-format json`
- **unknown**: Returns error message

## Success Metrics
- 100% test pass rate
- All model preference scenarios covered
- Robust error handling
- Proper state management
- Clean command construction