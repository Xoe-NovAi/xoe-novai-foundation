# Rate Limit Handling and Context Preservation Solution

## Problem Statement

The user experienced a critical issue with the multi-account system:

1. **No Automatic Rate Limit Rotation**: When hitting "too many requests" limits with DeepSeek v3.1 in OpenCode, the system didn't automatically rotate to alternative accounts
2. **Context Loss**: When switching from DeepSeek to Minimax, the ~60K tokens in the context window were lost, appearing as a brand new session
3. **Manual Intervention Required**: User had to manually switch models and lost all conversation history

## Root Cause Analysis

### 1. Missing Rate Limit Detection
- The existing system only checked quotas pre-dispatch but didn't detect HTTP 429 errors during execution
- No real-time monitoring of CLI responses for rate limit indicators
- No automatic fallback when providers returned rate limit errors

### 2. Context Isolation Issues
- OpenCode CLI uses XDG_DATA_HOME for session isolation, but this wasn't being managed properly
- No context preservation mechanism across account switches
- Session data was being lost when switching between different CLI instances

### 3. Account Rotation Logic Gaps
- Account rotation only happened on quota exhaustion, not rate limits
- No exponential backoff for rate-limited accounts
- No retry-after time handling

## Solution Implementation

### 1. Rate Limit Detection System (`rate_limit_handler.py`)

**Components:**
- `RateLimitDetector`: Detects rate limits from CLI responses using regex patterns
- `AccountRotator`: Manages account state and rotation with rate limit awareness
- `ContextManager`: Preserves conversation context across account switches
- `SmartDispatcher`: Orchestrates dispatch with automatic fallback

**Key Features:**
- **Multi-Provider Rate Limit Detection**: Detects rate limits for DeepSeek, Minimax, OpenCode, and other providers
- **Context Loss Detection**: Identifies when sessions are lost and triggers recovery
- **Retry-After Extraction**: Automatically extracts retry timing from error messages
- **Exponential Backoff**: Implements smart backoff for rate-limited accounts

### 2. Enhanced Multi-Provider Dispatcher (`enhanced_multi_provider_dispatcher.py`)

**Integration Points:**
- Wraps existing multi-provider dispatcher with rate limit handling
- Maintains backward compatibility with original API
- Adds session management and context preservation
- Provides enhanced error reporting with rate limit and context info

**Key Improvements:**
- **Automatic Account Rotation**: Rotates accounts on HTTP 429 errors
- **Context Preservation**: Maintains conversation history across switches
- **Smart Fallback**: Uses multiple accounts in rotation order
- **Session Management**: Tracks and preserves session state

### 3. Context Preservation System

**Mechanisms:**
- **Session Context Storage**: Saves conversation history to disk
- **Context Window Management**: Maintains last 10 messages for context
- **Session Recovery**: Attempts to recover lost context from file system
- **XDG_DATA_HOME Isolation**: Properly manages OpenCode session isolation

**Context Flow:**
```
User Task → Load Session Context → Enhance Task with Context → Dispatch → 
Save Response to Context → Rotate on Rate Limit → Recover Context → Continue
```

## Usage Examples

### Basic Usage with Rate Limit Handling

```python
from app.XNAi_rag_app.core.enhanced_multi_provider_dispatcher import EnhancedMultiProviderDispatcher

# Initialize with rate limit handling enabled
dispatcher = EnhancedMultiProviderDispatcher(
    enable_rate_limit_handling=True,
    enable_context_preservation=True
)

# Dispatch with session management
result = await dispatcher.dispatch(
    task="Analyze the codebase architecture",
    task_spec=TaskSpecialization.REASONING,
    session_id="user_session_123",
    timeout_sec=60.0
)

print(f"Success: {result.success}")
print(f"Account used: {result.account}")
print(f"Rate limit triggered: {result.rate_limit_triggered}")
print(f"Context preserved: {result.context_preserved}")
```

### CLI Integration

The enhanced dispatcher integrates seamlessly with existing CLI commands:

```bash
# The system now automatically handles rate limits
xnai account dispatch "Analyze this code" --session my_session

# Context is preserved across account switches
xnai account dispatch "Continue analysis" --session my_session
```

### Agent Integration

Agents can use the enhanced dispatcher for automatic rate limit handling:

```python
from app.XNAi_rag_app.core.agent_account_integration import AccountAwareAgent

agent = AccountAwareAgent("my_agent")
await agent.initialize()

# Agent automatically handles rate limits and preserves context
result = await agent.perform_task(
    my_task_function,
    task_type="reasoning",
    session_id="agent_session_456"
)
```

## Configuration

### Account Registry Updates

Add rate limit handling configuration to your account registry:

```yaml
accounts:
  - id: "deepseek_user_01"
    name: "DeepSeek User Account"
    provider: "deepseek"
    quota_remaining: 1000000
    quota_limit: 1000000
    models_preferred: ["deepseek-v3"]
    priority: 1
    api_key: "your_deepseek_api_key"
    rate_limit_config:
      max_retries: 3
      backoff_factor: 2
      max_backoff: 3600

  - id: "minimax_user_01"
    name: "Minimax User Account"
    provider: "minimax"
    quota_remaining: 800000
    quota_limit: 1000000
    models_preferred: ["minimax-v2"]
    priority: 2
    api_key: "your_minimax_api_key"
    rate_limit_config:
      max_retries: 3
      backoff_factor: 2
      max_backoff: 3600
```

### Environment Variables

Set up environment variables for context management:

```bash
export XNAI_CONTEXT_DIR="~/.xnai/context"
export XNAI_RATE_LIMIT_ENABLED="true"
export XNAI_CONTEXT_PRESERVATION_ENABLED="true"
```

## Monitoring and Debugging

### Dispatch Statistics

Get comprehensive statistics about rate limit handling:

```python
stats = dispatcher.get_dispatch_stats()
print(f"Total calls: {stats['total_calls']}")
print(f"Rate limits triggered: {stats['rate_limit_triggered']}")
print(f"Context preserved: {stats['context_preserved']}")
print(f"Fallback used: {stats['fallback_used']}")
```

### Session Context Debugging

Debug session context issues:

```python
# Get session context for debugging
context = dispatcher.get_session_context("user_session_123")
print(f"Session messages: {len(context['messages'])}")
print(f"Context window: {len(context['context_window'])}")

# Clear corrupted context
dispatcher.clear_session_context("user_session_123")
```

### Rate Limit Statistics

Monitor account rotation and rate limits:

```python
rate_limit_stats = dispatcher.smart_dispatcher.get_rotation_stats()
print(f"Account stats: {rate_limit_stats['account_stats']}")
print(f"Healthy accounts: {rate_limit_stats['account_stats']['healthy']}")
print(f"Rate limited accounts: {rate_limit_stats['account_stats']['rate_limited']}")
```

## Testing

### Run Rate Limit Tests

```bash
python test_rate_limit_handling.py
```

This comprehensive test suite validates:
- Rate limit detection accuracy
- Context preservation across switches
- Account rotation logic
- End-to-end scenarios
- Recovery from context loss

### Manual Testing Scenarios

Test the system with real rate limit scenarios:

```python
# Simulate rate limit scenario
async def test_rate_limit_scenario():
    dispatcher = EnhancedMultiProviderDispatcher()
    
    # This will trigger rate limits and test fallback
    for i in range(5):
        result = await dispatcher.dispatch(
            task=f"Test task {i}",
            session_id="rate_limit_test",
            timeout_sec=10.0
        )
        print(f"Attempt {i+1}: Success={result.success}, Account={result.account}")
```

## Benefits

### 1. Automatic Rate Limit Handling
- **Zero Manual Intervention**: System automatically rotates accounts on rate limits
- **Smart Fallback**: Uses optimal alternative accounts
- **Retry Logic**: Implements exponential backoff for rate-limited accounts

### 2. Context Preservation
- **Session Continuity**: Maintains conversation history across account switches
- **Context Recovery**: Automatically recovers lost context when possible
- **Seamless Experience**: Users don't notice account switches

### 3. Enhanced Reliability
- **Multi-Account Resilience**: Redundant accounts prevent single points of failure
- **Intelligent Routing**: Routes tasks to optimal providers based on current status
- **Real-time Monitoring**: Tracks account health and performance

### 4. Improved User Experience
- **No Context Loss**: Users maintain their conversation flow
- **Automatic Recovery**: System handles errors transparently
- **Better Performance**: Optimal provider selection improves response times

## Migration Guide

### Existing Code Migration

Replace existing dispatcher usage:

```python
# Before (original dispatcher)
from app.XNAi_rag_app.core.multi_provider_dispatcher import MultiProviderDispatcher
dispatcher = MultiProviderDispatcher()

# After (enhanced dispatcher)
from app.XNAi_rag_app.core.enhanced_multi_provider_dispatcher import EnhancedMultiProviderDispatcher
dispatcher = EnhancedMultiProviderDispatcher(
    enable_rate_limit_handling=True,
    enable_context_preservation=True
)
```

### CLI Migration

No changes needed - enhanced dispatcher maintains backward compatibility with existing CLI commands.

### Agent Migration

Update agent initialization:

```python
# Before
agent = AccountAwareAgent("my_agent")

# After
agent = AccountAwareAgent("my_agent")
agent.dispatcher = EnhancedMultiProviderDispatcher(
    enable_rate_limit_handling=True,
    enable_context_preservation=True
)
```

## Troubleshooting

### Common Issues

#### 1. Context Still Being Lost
**Symptoms**: Session history disappears after account switches
**Solutions**:
- Check that `enable_context_preservation=True`
- Verify context directory permissions
- Ensure session IDs are consistent across calls

#### 2. Rate Limits Not Detected
**Symptoms**: System doesn't rotate on rate limits
**Solutions**:
- Check rate limit detection patterns match your provider's error messages
- Verify `enable_rate_limit_handling=True`
- Check account rotation configuration

#### 3. Slow Fallback Performance
**Symptoms**: Long delays when hitting rate limits
**Solutions**:
- Adjust backoff configuration
- Increase timeout values
- Add more accounts to rotation pool

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging
logging.getLogger("RateLimitHandler").setLevel(logging.DEBUG)
logging.getLogger("EnhancedMultiProviderDispatcher").setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features

1. **Machine Learning Rate Limit Prediction**: Use ML to predict rate limits before they occur
2. **Dynamic Account Pool Management**: Automatically add/remove accounts based on usage patterns
3. **Advanced Context Compression**: Compress large context windows to fit smaller providers
4. **Real-time Provider Health Monitoring**: Monitor provider uptime and performance
5. **Smart Session Merging**: Merge context from multiple sessions intelligently

### Integration Opportunities

- **Monitoring Systems**: Integrate with Prometheus/Grafana for real-time monitoring
- **Alerting Systems**: Set up alerts for rate limit patterns and account health
- **Load Balancers**: Integrate with external load balancing systems
- **Cloud Providers**: Native integration with cloud provider rate limiting APIs

## Conclusion

The enhanced multi-account system now provides:

✅ **Automatic Rate Limit Detection and Rotation**
✅ **Context Preservation Across Account Switches**  
✅ **Intelligent Fallback and Recovery**
✅ **Seamless User Experience**
✅ **Comprehensive Monitoring and Debugging**

This solution addresses the user's specific issue where DeepSeek rate limits caused context loss and manual intervention. The system now automatically handles these scenarios transparently, maintaining conversation continuity and improving overall reliability.

---

For support and questions, see the [Multi-Account System Documentation](./MULTI_ACCOUNT_SYSTEM.md).