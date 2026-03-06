# Voice Assistant Multi-CLI Guide

## Overview

This is a production-ready **multi-CLI voice orchestrator** that supports four distinct execution environments:

1. **Standalone Python CLI** - Pure Python REPL with no external dependencies
2. **Cline CLI** - Model Context Protocol (MCP) integration for Cline IDE extension
3. **GitHub Copilot CLI** - GitHub-native integration via `gh` CLI commands
4. **Claude API Custom CLI** - Direct Anthropic SDK integration with conversation history

All modes support:
- **Ollama LLM backend** with auto-start and health monitoring
- **Persistent memory system** with semantic search and TTL
- **Speech-to-text** and **text-to-speech** pipelines
- **Service health monitoring** with circuit breaker patterns
- **Dynamic configuration** without restart

---

## Quick Start

### 1. Prerequisites

```bash
# Ensure Python 3.12+ is installed
python3 --version

# Activate virtual environment (if not already active)
source voice_venv/bin/activate

# Ensure Ollama is installed on macOS
open -a Ollama  # Starts Ollama application
# Or on Linux/Windows: ollama serve
```

### 2. Interactive Session (Standalone)

```bash
python3 main.py --interactive
```

**Available commands:**
- `voice <text>` - Process text through voice pipeline
- `status` - Show service and health status
- `config` - Display current configuration
- `help` - Show all available commands

### 3. Single Command Execution

```bash
python3 main.py --command "voice Hello, what's the weather?"
```

### 4. View System Status

```bash
python3 main.py --status
```

### 5. View Configuration

```bash
python3 main.py --config
```

---

## CLI Mode Selection

### Auto-Detection (Default)

The system automatically detects available environments in this order:
1. **Cline**: Checks for `CLINE_AVAILABLE` environment variable or `~/.cline` directory
2. **GitHub Copilot**: Checks for `GITHUB_COPILOT_ENABLED` environment variable
3. **Claude API**: Checks for `ANTHROPIC_API_KEY` environment variable
4. **Standalone**: Default if none above are detected

### Manual Mode Selection

```bash
# Use specific CLI mode
python3 main.py --cli-mode standalone --interactive
python3 main.py --cli-mode cline --headless
python3 main.py --cli-mode copilot --interactive
python3 main.py --cli-mode claude --api-key YOUR_KEY --interactive
```

---

## CLI Mode Details

### Standalone Python CLI

**Best for:** Local development, testing, quick scripts

**Features:**
- Pure Python REPL with command history
- No external tool dependencies
- Full access to all voice orchestrator functions
- Displays formatted status and help

**Example:**
```bash
python3 main.py --interactive
# >>> voice Tell me a joke
# Claude response to: Tell me a joke ...
# >>> status
# Application Status: Running | CLI Mode: standalone
```

### Cline CLI (MCP Integration)

**Best for:** Using with Cline IDE extension

**Features:**
- MCP (Model Context Protocol) server interface
- Exposes tools: `voice_input`, `get_status`, `list_memories`
- Headless operation (no interactive REPL)
- Cline controls the interface directly

**Setup:**
```bash
# Check Cline is available
echo $CLINE_AVAILABLE  # Should be "true"

# Or create .cline directory
mkdir -p ~/.cline

# Run in MCP server mode
python3 main.py --cli-mode cline --headless
```

**MCP Tools Exposed:**
```json
{
  "name": "voice_input",
  "description": "Send text through voice processing pipeline",
  "inputSchema": {
    "type": "object",
    "properties": {
      "text": {"type": "string", "description": "Text to process"}
    }
  }
}
```

### GitHub Copilot CLI

**Best for:** GitHub CLI integration and automation

**Features:**
- Native `gh` CLI integration
- Uses GitHub authentication context
- Subprocess-based command execution
- Integration with GitHub workflows

**Setup:**
```bash
# Authenticate with GitHub
gh auth login

# Enable Copilot CLI
export GITHUB_COPILOT_ENABLED=true

# Run
python3 main.py --cli-mode copilot --interactive
```

### Claude API Custom CLI

**Best for:** Direct Anthropic SDK usage with custom configuration

**Features:**
- Full Anthropic SDK integration
- Multi-turn conversation history tracking
- Custom system prompts and parameters
- API key-based authentication

**Setup:**
```bash
# Set API key
export ANTHROPIC_API_KEY=sk-ant-xxxxx

# Or pass via CLI
python3 main.py --cli-mode claude --api-key sk-ant-xxxxx --interactive
```

**Multi-turn Example:**
```python
# Conversation history persists across turns
>>> voice Tell me a story
Claude: Once upon a time...
>>> voice Make it shorter
Claude: Once there was...
>>> voice Now add a twist
Claude: Suddenly the protagonist was...
```

---

## Configuration

### Config File Location

```
/Users/buck/Documents/voice-setup-project/voice_config.json
```

### Config Structure

```json
{
  "memory": {
    "enabled": true,
    "max_memories": 1000,
    "ttl_default": 86400,
    "embedding_model": "all-MiniLM-L6-v2"
  },
  "stt": {
    "model": "whisper_large_v3_turbo",
    "confidence_threshold": 0.8,
    "max_audio_duration": 30.0
  },
  "tts": {
    "model": "kokoro",
    "voice": "af_sky",
    "speed": 1.0,
    "pitch": 1.0
  },
  "ollama": {
    "host": "localhost",
    "port": 11434,
    "timeout": 120,
    "max_tokens": 2000,
    "temperature": 0.7
  },
  "voice": {
    "llm_mode": "auto",
    "quality_mode": "balanced"
  }
}
```

### Dynamic Configuration

Update configuration without restarting:

```bash
python3 main.py --provider claude --interactive
```

**Available Providers:**
- `claude` - Anthropic Claude
- `openai` - OpenAI GPT
- `openrouter` - OpenRouter API
- `ollama` - Local Ollama instance

---

## Memory System

### Persistent Storage

Voice conversations are automatically stored in SQLite database at:
```
config/memory.db
```

### Memory Types

- `conversation` - User/assistant dialogue turns
- `knowledge` - Learned facts and information
- `context` - Ephemeral context for current session
- `custom` - User-defined memory types

### Search Memory

```python
from src.memory.memory_bank import search_memory

# Search across all types
results = search_memory("weather forecast")

# Search specific types
results = search_memory("weather", memory_types=["knowledge"])

# Results include confidence scores and metadata
for item in results:
    print(f"{item.content} ({item.memory_type})")
```

### Context Management

```python
from src.memory.memory_bank import get_memory_bank

mb = get_memory_bank()

# Get conversation context
history = mb.get_conversation_history(limit=5)

# Get ephemeral context
context = mb.context_manager.get_context()

# Update ephemeral context
mb.context_manager.update_context({
    "user_location": "San Francisco",
    "time_of_day": "morning"
})
```

### TTL (Time-to-Live)

Memories automatically expire after configured TTL:

```json
{
  "memory": {
    "ttl_default": 86400  // 1 day in seconds
  }
}
```

Expired memories are cleaned up by background daemon thread.

---

## Service Management

### Ollama Service

The system automatically manages Ollama via `ServiceManager`:

#### macOS
```bash
# Auto-starts Ollama application
open -a Ollama
```

#### Linux/Windows
```bash
# Auto-starts Ollama service
ollama serve
```

### Service Status

```bash
python3 main.py --status
```

Shows:
- Ollama: `running` / `stopped` / `error`
- STT Service: health status
- TTS Service: health status
- Memory System: enabled/disabled
- Latest error messages

### Health Monitoring

- **Frequency**: Every 30 seconds
- **Timeout**: 5 seconds per service
- **Auto-restart**: Yes (configurable with `--no-auto-start`)

### Service Startup Options

```bash
# Auto-start all required services
python3 main.py --interactive

# Skip service startup (for testing)
python3 main.py --skip-services --interactive

# Require services or fail
python3 main.py --fail-on-service-error --interactive

# Don't require Ollama
python3 main.py --no-ollama --interactive

# Manual mode - no Ollama
python3 main.py --headless --no-auto-start --command "voice test"
```

---

## Architecture

### Component Hierarchy

```
main.py (CLI Entry Point)
├── VoiceApp (orchestrator)
├── ServiceManager
│   └── Ollama
│       ├── Health Monitor
│       └── Auto-start Handler
├── CLIInterface (abstract base)
│   ├── StandaloneCLI
│   ├── ClineCLI
│   ├── CopilotCLI
│   └── ClaudeCLI
└── VoiceOrchestrator
    ├── STTManager (Speech-to-Text)
    ├── TTSManager (Text-to-Speech)
    ├── OllamaClient (LLM)
    ├── HealthMonitor
    └── MemoryBank
        ├── SQLite DB
        ├── ContextManager
        └── SemanticSearch
```

### Module Details

#### `main.py`
- Entry point with argparse configuration
- VoiceApp orchestration
- Service setup and lifecycle
- Mode determination (interactive/headless/single-command)

#### `cli_abstraction.py`
- CLIInterface abstract base class
- 4 CLI implementations with factory pattern
- Environment detection
- Command routing and processing

#### `service_manager.py`
- Async service lifecycle management
- Platform-aware startup commands
- Health monitoring with circuit breaker
- Singleton access via `get_service_manager()`

#### `voice_orchestrator.py`
- Core voice pipeline: STT → LLM → TTS
- Memory integration for context
- Configuration management
- Status and metrics tracking

#### `src/memory/memory_bank.py`
- Persistent SQLite storage
- Semantic search (optional: requires sentence-transformers)
- TTL-based expiration
- Thread-safe operations
- Singleton via `get_memory_bank()`

---

## Advanced Usage

### Verbose Logging

```bash
python3 main.py --verbose --interactive
```

Shows:
- All service startup events
- Memory operations
- LLM response details
- Health check results

### Quiet Mode

```bash
python3 main.py --quiet --command "voice hello"
```

Suppresses non-essential output.

### Custom API Keys

```bash
python3 main.py --cli-mode claude \
  --api-key sk-ant-xxxxx \
  --provider claude \
  --interactive
```

### Headless Server Mode

Useful for MCP servers and background services:

```bash
python3 main.py --cli-mode cline --headless
```

Runs without interactive prompt, awaits external commands.

---

## Troubleshooting

### "Cannot operate on a closed database"

**Cause**: Memory bank connection was closed by prior cleanup

**Solution**: Fixed in v1.0+ - Memory bank is never closed automatically. If you see this error in tests, ensure each test properly initializes a new VoiceOrchestrator instance.

### Ollama not found

**macOS:**
```bash
brew install ollama
open -a Ollama
```

**Linux:**
```bash
curl https://ollama.ai/install.sh | sh
ollama serve
```

**Windows:**
- Download from https://ollama.ai
- Install and run executable

### API Key Errors

```bash
# Claude API
export ANTHROPIC_API_KEY=sk-ant-xxxxx

# GitHub
gh auth login

# OpenAI
export OPENAI_API_KEY=sk-xxxxx
```

### Memory Disabled

If memories aren't being stored:

1. Check config:
```bash
python3 main.py --config | grep -A5 memory
```

2. Enable memory:
```json
{
  "memory": {
    "enabled": true
  }
}
```

3. Restart application

---

## Development

### Testing

```bash
# Run integration tests
python3 test_integration.py

# Test specific CLI
python3 -c "
from cli_abstraction import CLIFactory
import asyncio

async def test():
    cli = CLIFactory.create('standalone')
    await cli.initialize()
    resp = await cli.process_command('voice hello')
    print(resp)
    await cli.shutdown()

asyncio.run(test())
"
```

### Adding New CLI Modes

1. Create subclass of `CLIInterface`:

```python
class MyCustomCLI(CLIInterface):
    async def initialize(self) -> bool:
        # Your init logic
        return True
    
    async def process_command(self, command: str) -> str:
        # Your command processing
        return result
    
    async def shutdown(self) -> None:
        # Cleanup
        pass
```

2. Add to CLIMode enum and factory detection

### Adding Memory Stores

```python
from src.memory.memory_bank import get_memory_bank

mb = get_memory_bank()

# Store interaction
mb.store_interaction(
    user_input="Tell me about Python",
    assistant_response="Python is a programming language...",
    memory_type="conversation"
)

# Search with filters
results = mb.search("Python", memory_types=["conversation"])
```

---

## Performance

### Benchmarks (on macOS M1)

- **Voice Input**: 50-200ms (depends on STT model)
- **LLM Response**: 1-5s (depends on model and token count)
- **Voice Output**: 100-500ms (depends on TTS model)
- **Memory Search**: 10-50ms (with semantic search)
- **Service Health Check**: 100-500ms

### Optimization Tips

1. **Use faster models** for real-time interaction:
   - STT: `fast-whisper` instead of `whisper_large_v3_turbo`
   - LLM: `mistral` instead of `llama3.2`
   - TTS: `kokoro` is already optimized

2. **Reduce memory search scope**:
   ```python
   mb.search("query", memory_types=["conversation"], limit=5)
   ```

3. **Increase Ollama context size**:
   ```json
   {
     "ollama": {
       "max_tokens": 4000
     }
   }
   ```

---

## License

See LICENSE file in project root

---

## Support

For issues and feature requests, see:
- [GitHub Issues](https://github.com/your-org/voice-setup-project/issues)
- Memory bank: Search for "decision" or "architecture" in persistent memory

---

## Changelog

### v1.0 (Current)
- Multi-CLI abstraction layer
- Service manager with auto-restart
- Fixed memory bank singleton issues
- All 4 CLI implementations
- Comprehensive health monitoring
- Dynamic configuration support
