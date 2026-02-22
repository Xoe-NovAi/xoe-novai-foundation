# Voice Assistant - Quick Reference Guide

## Command Cheat Sheet

### Starting the App

```bash
# Interactive mode (auto-detect CLI)
python3 main.py --interactive

# Specific CLI mode
python3 main.py --cli-mode standalone --interactive
python3 main.py --cli-mode cline --headless
python3 main.py --cli-mode copilot --interactive
python3 main.py --cli-mode claude --api-key sk-ant-xxxxx --interactive

# Single command
python3 main.py --command "voice hello world"

# Show status
python3 main.py --status

# Show config
python3 main.py --config
```

## Interactive Commands

Inside interactive session:

```
voice <text>         - Process text through voice pipeline
status               - Show system status
config               - Show configuration
help                 - Show available commands
```

## Memory Operations

### Store Memory

```python
from src.memory.memory_bank import get_memory_bank

mb = get_memory_bank()
mb.store_interaction(
    user_input="Hello",
    assistant_response="Hi there!"
)
```

### Search Memory

```python
from src.memory.memory_bank import search_memory

# Search all types
results = search_memory("vacation")

# Search specific type
results = search_memory("python", memory_types=["knowledge"])

# Get results
for item in results:
    print(f"Type: {item.memory_type}, Content: {item.content}")
```

### Get Conversation History

```python
from src.memory.memory_bank import get_memory_bank

mb = get_memory_bank()
history = mb.get_conversation_history(limit=5)

for item in history:
    print(f"{item.memory_type}: {item.content}")
```

### Clear Memory

```python
from src.memory.memory_bank import get_memory_bank

mb = get_memory_bank()
deleted = mb.cleanup_expired()
print(f"Cleaned up {deleted} expired memories")
```

## Service Management

### Check Service Status

```bash
python3 main.py --status
```

### Restart Services

```bash
# Standard restart (auto-management)
python3 main.py --interactive

# Skip services (offline mode)
python3 main.py --skip-services --interactive

# Require services (fail if unavailable)
python3 main.py --fail-on-service-error --interactive
```

### Manual Ollama Operations

```bash
# macOS
open -a Ollama

# Linux
ollama serve

# Windows
ollama.exe serve
```

## Configuration

### View Current Config

```bash
python3 main.py --config
```

### Common Config Paths

- Main config: `voice_config.json`
- Memory config: `config/memory_config.json`
- Memory DB: `config/memory.db`
- Ollama: `~/.ollama/`

### Config Sections

```json
{
  "memory": {"enabled": true, "max_memories": 1000},
  "stt": {"model": "whisper_large_v3_turbo"},
  "tts": {"model": "kokoro"},
  "ollama": {"host": "localhost", "port": 11434},
  "voice": {"llm_mode": "auto", "quality_mode": "balanced"},
  "monitoring": {"enabled": true, "check_interval": 30}
}
```

## CLI Mode Selection

### Standalone (Default)

```bash
python3 main.py --cli-mode standalone --interactive
```

✅ Best for: Local testing, development  
⚙️ Requirements: None (pure Python)  
🔧 Setup: None

### Cline

```bash
export CLINE_AVAILABLE=true
python3 main.py --cli-mode cline --headless
```

✅ Best for: IDE extension integration  
⚙️ Requirements: Cline IDE extension installed  
🔧 Setup: `mkdir -p ~/.cline`

### GitHub Copilot

```bash
gh auth login
export GITHUB_COPILOT_ENABLED=true
python3 main.py --cli-mode copilot --interactive
```

✅ Best for: GitHub CLI workflows  
⚙️ Requirements: GitHub CLI (`gh`) installed  
🔧 Setup: `gh auth login`

### Claude API

```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxx
python3 main.py --cli-mode claude --interactive
```

✅ Best for: Direct Anthropic integration  
⚙️ Requirements: Anthropic API key  
🔧 Setup: Get API key from https://console.anthropic.com

## Debugging

### Enable Verbose Logging

```bash
python3 main.py --verbose --interactive
```

Shows:
- Service startup details
- Memory operations
- LLM request/response
- Health check results

### Test Memory

```bash
python3 -c "
from src.memory.memory_bank import get_memory_bank
mb = get_memory_bank()
print('Memory enabled:', mb is not None)
print('Connection valid:', mb.conn)
searched = mb.search('test')
print('Search works:', len(searched) >= 0)
"
```

### Test CLI Factory

```bash
python3 -c "
from cli_abstraction import CLIFactory, CLIMode
cli = CLIFactory.create(CLIMode.STANDALONE)
print('CLI created:', cli.__class__.__name__)
"
```

### Test Service Manager

```bash
python3 -c "
import asyncio
from service_manager import get_service_manager

async def test():
    sm = get_service_manager()
    status = await sm.get_all_services_status()
    for name, info in status.items():
        print(f'{name}: {info[\"status\"]}')

asyncio.run(test())
"
```

## Troubleshooting

### Memory Operations Fail

**Error**: `Cannot operate on a closed database`

**Fix**:
1. Update to latest version (v1.0+)
2. Ensure memory bank isn't explicitly closed in cleanup
3. Check memory config is enabled

### Ollama Not Responding

**Check**:
```bash
curl http://localhost:11434/api/tags
```

**Fix**:
```bash
# Start Ollama
open -a Ollama  # macOS
ollama serve    # Linux/Windows

# Wait 5-10 seconds for startup
sleep 10
python3 main.py --status
```

### API Key Not Working

**Verify**:
```bash
echo $ANTHROPIC_API_KEY  # Should show key (first 7 chars)
```

**Fix**:
```bash
export ANTHROPIC_API_KEY=sk-ant-YOUR_ACTUAL_KEY
python3 main.py --cli-mode claude --interactive
```

### CLI Mode Not Detected

**Check**:
```bash
python3 -c "
from cli_abstraction import CLIFactory
detected = CLIFactory.detect_environment()
print('Detected mode:', detected.value)
"
```

**Force Mode**:
```bash
python3 main.py --cli-mode standalone --interactive
```

## Performance Tips

### Faster Response

1. **Use smaller LLM models**:
   ```bash
   python3 main.py --provider ollama  # Uses faster local model
   ```

2. **Reduce memory search**:
   ```python
   mb.search("query", limit=3)  # Only get top 3
   ```

3. **Disable memory if not needed**:
   ```json
   {"memory": {"enabled": false}}
   ```

4. **Increase Ollama context**:
   ```json
   {"ollama": {"max_tokens": 4000}}
   ```

### Memory Optimization

1. **Clean expired memories**:
   ```python
   deleted = mb.cleanup_expired()
   ```

2. **Reduce TTL for faster expiration**:
   ```json
   {"memory": {"ttl_default": 3600}}  # 1 hour instead of 1 day
   ```

3. **Limit max memories**:
   ```json
   {"memory": {"max_memories": 500}}  # Default: 1000
   ```

## File Locations

```
/Users/buck/Documents/voice-setup-project/
├── main.py                          # Entry point
├── cli_abstraction.py               # CLI implementations
├── service_manager.py               # Service lifecycle
├── voice_orchestrator.py            # Core pipeline
├── voice_config.json                # Configuration
├── config/
│   ├── memory_config.json
│   └── memory.db
├── src/memory/
│   ├── memory_bank.py              # Persistent store
│   └── memory_integration.py
├── MULTI-CLI-GUIDE.md              # User guide
├── ARCHITECTURE-DETAILS.md         # Technical details
└── README-QUICK-REFERENCE.md       # This file
```

## Import Examples

### Use Voice Orchestrator

```python
from voice_orchestrator import VoiceOrchestrator
import asyncio

async def main():
    orch = VoiceOrchestrator()
    response = await orch.generate_response("Hello!")
    print(response)

asyncio.run(main())
```

### Use CLI Directly

```python
from cli_abstraction import CLIFactory, CLIMode
import asyncio

async def main():
    cli = CLIFactory.create(CLIMode.STANDALONE)
    await cli.initialize()
    response = await cli.process_command("voice hello")
    print(response)
    await cli.shutdown()

asyncio.run(main())
```

### Use Memory Bank

```python
from src.memory.memory_bank import get_memory_bank

mb = get_memory_bank()

# Store
mb.store_interaction("user input", "assistant response", memory_type="conversation")

# Search
results = mb.search("topic", limit=5)

# Get history
history = mb.get_conversation_history(limit=10)

# Get context
context = mb.context_manager.get_context()
```

### Use Service Manager

```python
from service_manager import get_service_manager
import asyncio

async def main():
    sm = get_service_manager()
    
    # Start service
    await sm.start_service('ollama')
    
    # Check status
    status = await sm.get_all_services_status()
    print(status)
    
    # Start monitoring
    await sm.start_monitoring()

asyncio.run(main())
```

## Environment Variables

```bash
# CLI Mode Detection
export CLINE_AVAILABLE=true                    # Force Cline mode
export GITHUB_COPILOT_ENABLED=true            # Force Copilot mode
export ANTHROPIC_API_KEY=sk-ant-xxxxx         # Force Claude mode

# API Keys
export ANTHROPIC_API_KEY=sk-ant-xxxxx
export OPENAI_API_KEY=sk-xxxxx
export GITHUB_TOKEN=ghp_xxxxx

# Service Configuration
export OLLAMA_HOST=localhost:11434
export USER_DATA_DIR=~/.voice-assistant

# Logging
export LOG_LEVEL=DEBUG
export VERBOSE=true
```

## Common Patterns

### Multi-turn Conversation

```python
from cli_abstraction import CLIFactory
import asyncio

async def chat_session():
    cli = CLIFactory.create('standalone')
    await cli.initialize()
    
    # Multiple turns - memory persists
    await cli.process_command('voice What is Python?')
    await cli.process_command('voice How does it compare to JavaScript?')
    await cli.process_command('voice Which is faster?')
    
    await cli.shutdown()

asyncio.run(chat_session())
```

### Batch Processing

```python
import asyncio
from voice_orchestrator import VoiceOrchestrator

async def process_batch(texts):
    orch = VoiceOrchestrator()
    results = []
    
    for text in texts:
        response = await orch.generate_response(text)
        results.append(response)
    
    return results

# Usage
batch = ["Hello", "How are you?", "Tell me a joke"]
responses = asyncio.run(process_batch(batch))
```

### Conditional Service Startup

```bash
# Only start if Ollama not already running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    open -a Ollama
    sleep 5
fi

python3 main.py --interactive
```

## Version Info

```bash
# Check Python version
python3 --version  # Should be 3.12+

# Check package versions
python3 -c "
import sys; print(f'Python: {sys.version}')
try:
    import anthropic; print(f'Anthropic SDK: {anthropic.__version__}')
except ImportError:
    print('Anthropic SDK: not installed')
"
```
