# Voice Assistant Architecture - Technical Deep Dive

## System Design Principles

1. **Modular CLI Abstraction**: Support multiple execution environments with single codebase
2. **Global Singleton Resources**: Memory bank, service manager shared across CLI instances
3. **Async-First**: All I/O operations are async-compatible
4. **Configuration-Driven**: Behavior controlled via `voice_config.json`
5. **Health-Aware**: Continuous monitoring with automatic recovery

---

## CLI Abstraction Layer

### Abstract Base Class Pattern

```python
class CLIInterface(ABC):
    """Base interface all CLI modes must implement"""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Setup resources, return success status"""
    
    @abstractmethod
    async def process_command(self, command: str) -> str:
        """Process user command, return response"""
    
    @abstractmethod
    async def start_interactive_session(self):
        """Run interactive REPL loop"""
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Cleanup resources gracefully"""
```

### Factory Pattern Implementation

```python
class CLIFactory:
    @staticmethod
    def detect_environment() -> CLIMode:
        """Auto-detect best CLI mode in order:
        1. CLINE_AVAILABLE env var or ~/.cline exists → CLINE
        2. GITHUB_COPILOT_ENABLED env var → COPILOT
        3. ANTHROPIC_API_KEY env var → CLAUDE
        4. Default → STANDALONE
        """
        # Implementation details...
    
    @staticmethod
    def create(mode: CLIMode | str) -> CLIInterface:
        """Factory constructor - returns correct CLI implementation"""
        if isinstance(mode, str):
            mode = CLIMode(mode)
        
        if mode == CLIMode.STANDALONE:
            return StandaloneCLI()
        elif mode == CLIMode.CLINE:
            return ClineCLI()
        # ... etc
```

### Implementation Details

#### StandaloneCLI
- **Use Case**: Local development, testing
- **Input**: Command-line REPL
- **Output**: Formatted text to stdout
- **State**: In-memory during session

#### ClineCLI
- **Use Case**: IDE extension integration
- **Protocol**: MCP (Model Context Protocol)
- **Tools Exposed**: 3 JSON-defined tools
- **State**: Per-tool invocation

#### CopilotCLI
- **Use Case**: GitHub CLI integration
- **Protocol**: Subprocess + GitHub context
- **Input**: `gh` CLI commands
- **State**: GitHub authentication context

#### ClaudeCLI
- **Use Case**: Direct Anthropic SDK usage
- **Protocol**: REST API + conversation history
- **Input**: Multi-turn text prompts
- **State**: Conversation history in memory

---

## Service Manager Architecture

### Service Definition

```python
@dataclass
class ServiceConfig:
    name: str
    type: ServiceType  # INFERENCE, STT, TTS, ORCHESTRATOR
    host: str
    port: int
    health_url: str
    startup_command: str
    max_startup_time: float = 30.0
    health_check_timeout: float = 5.0
```

### Async Service Management

```python
class ServiceManager:
    async def start_service(self, name: str, wait_for_ready: bool = True):
        """
        1. Execute startup_command (platform-aware)
        2. Poll health_url until responsive or timeout
        3. Return immediately if service already running
        """
    
    async def _check_service_health(self, name: str) -> bool:
        """GET health_url with 5s timeout, handle connection errors gracefully"""
    
    async def start_monitoring(self):
        """Background task: check all services every 30s, auto-restart if needed"""
    
    async def ensure_service_running(self, service_name: str):
        """Idempotent: only starts if not already running"""
```

### Platform-Specific Startup

**macOS:**
```python
# Use Ollama.app GUI
startup_command = "open -a Ollama"

# Non-blocking launch, app starts asynchronously
subprocess.run(cmd, shell=True)
```

**Linux/Windows:**
```python
# Direct subprocess for ollama serve
startup_command = "ollama serve"

# Managed subprocess with PID tracking
process = subprocess.Popen(cmd, shell=True)
```

### Health Check Circuit Breaker

```python
if service.failure_count > FAILURE_THRESHOLD:
    service.circuit_open = True
    # Stop checking health temporarily (prevents hammering failing service)
    # Reset after CIRCUIT_RESET_TIME
```

---

## Memory Bank Architecture

### Singleton Pattern

```python
_memory_bank: Optional[MemoryBank] = None

def get_memory_bank() -> MemoryBank:
    """Lazy initialization - returns same instance across app lifetime"""
    global _memory_bank
    if _memory_bank is None:
        _memory_bank = MemoryBank()  # Reads config on init
    return _memory_bank
```

### Critical Design Decision: Never Close on Cleanup

**Problem**: Multiple CLI instances use shared global `_memory_bank`. If one CLI closes the database connection, all subsequent instances fail.

**Solution**: Memory bank stays open for entire application lifetime. Closing is only for app shutdown/testing:

```python
def cleanup(self):
    """Voice Orchestrator cleanup"""
    # ❌ WRONG: self.memory_bank.close()
    # ✅ RIGHT: Don't close - it's a global resource
    pass
```

### Storage: SQLite with Thread Safety

```python
class MemoryBank:
    def __init__(self):
        self.db_lock = threading.Lock()  # Protect concurrent access
        self.conn = sqlite3.connect(':memory:')  # Or persistent file
        self._init_schema()
    
    def store_interaction(self, user_input: str, assistant_response: str):
        with self.db_lock:
            # All DB operations protected
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO memories (content, type, created_at, expires_at)
                VALUES (?, ?, datetime('now'), datetime('now', '+1 day'))
            """, ...)
            self.conn.commit()
```

### Semantic Search (Optional)

```python
# If sentence-transformers available:
from sentence_transformers import SentenceTransformer

class MemoryBank:
    def __init__(self):
        try:
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            self.semantic_enabled = True
        except ImportError:
            self.semantic_enabled = False
    
    def search(self, query: str, use_semantic: bool = True):
        if use_semantic and self.semantic_enabled:
            # Vector-based search using embeddings
            query_vec = self.encoder.encode(query)
            # Compare with stored embeddings
        else:
            # Fallback to exact text matching
```

### TTL-Based Expiration

```python
class MemoryBank:
    def cleanup_expired(self) -> int:
        """Background daemon: runs every 60s"""
        with self.db_lock:
            cursor = self.conn.cursor()
            cursor.execute("""
                DELETE FROM memories
                WHERE expires_at < datetime('now')
            """)
            deleted = cursor.rowcount
            self.conn.commit()
        return deleted
    
    def _start_cleanup_thread(self):
        """Daemon thread for automatic cleanup"""
        def cleanup_loop():
            while True:
                time.sleep(60)
                self.cleanup_expired()
        
        thread = threading.Thread(target=cleanup_loop, daemon=True)
        thread.start()
```

---

## Voice Orchestrator Integration

### Memory-Aware Response Generation

```python
async def generate_response(self, user_input: str, context: Optional[Dict] = None) -> str:
    """
    1. If memory enabled and no context passed:
       - Search memory for relevant past interactions
       - Prepend to prompt as "previous context"
    2. Generate response via LLM
    3. Store interaction and update ephemeral context
    """
    
    # Step 1: Get context
    if self.memory_enabled and context is None and self.memory_bank:
        context = self.memory_bank.get_relevant_context(user_input)
        
        # Get conversation history
        history = self.memory_bank.get_conversation_history(limit=5)
        history_prompt = self._format_history(history)
        
        # Prepend to actual prompt
        full_prompt = history_prompt + user_input
    else:
        full_prompt = user_input
    
    # Step 2-3: Generate and store
    response = await self.ollama_client.generate(full_prompt)
    
    if self.memory_enabled and response:
        self.memory_bank.store_interaction(user_input, response)
        self.memory_bank.context_manager.update_context({
            'last_interaction': response,
            'timestamp': datetime.now().isoformat()
        })
    
    return response
```

### Ephemeral Context Manager

```python
class ContextManager:
    """In-memory context for current session"""
    
    def __init__(self):
        self.context = {
            'role': 'system',
            'session_start': datetime.now(),
            'turn_count': 0
        }
    
    def update_context(self, updates: Dict[str, Any]):
        """Merge new values (thread-safe)"""
        with self.lock:
            self.context.update(updates)
    
    def get_context(self) -> Dict[str, Any]:
        """Get current context snapshot"""
        with self.lock:
            return self.context.copy()
```

---

## Configuration Hierarchy

### Loading Strategy

```python
class ConfigManager:
    def __init__(self, config_path: Optional[str] = None):
        # 1. Load from file (default: voice_config.json)
        self.config = self._load_from_file(config_path)
        
        # 2. Override with environment variables
        self.config = self._merge_env_overrides(self.config)
```

### Section-Based Distribution

```python
# In VoiceOrchestrator.__init__:
config_dict = self.config_manager.config

# Each manager gets its section
self.stt_manager = STTManager(config_dict.get('stt', {}))
self.tts_manager = TTSManager(config_dict.get('tts', {}))
self.ollama_client = OllamaClient(config_dict.get('ollama', {}))

# Memory reads its own config for TTL defaults
mem_config = config_dict.get('memory', {})
self.memory_enabled = mem_config.get('enabled', False)
```

### Dynamic Updates

```python
def update_config(self, updates: Dict[str, Any]):
    """Update config sections without restart"""
    # Merge at top level
    for section, values in updates.items():
        if section in self.config:
            self.config[section].update(values)
    
    # Propagate to affected managers
    self.ollama_client.update_config(self.config['ollama'])
    self.memory_bank.reload_config()
```

---

## Data Flow Diagrams

### Voice Command Processing

```
User Input
    ↓
[CLI Interface]
    ↓
VoiceOrchestrator.generate_response()
    ├─→ MemoryBank.get_relevant_context() [optional]
    ├─→ MemoryBank.get_conversation_history() [optional]
    ├─→ Format Full Prompt
    ├─→ OllamaClient.generate()
    └─→ MemoryBank.store_interaction() [if enabled]
    ↓
Response + Update EphemeralContext
    ↓
CLI Output
```

### Service Startup Sequence

```
VoiceApp.run()
    ↓
setup_services()
    ├─→ ServiceManager.start_monitoring() [background]
    ├─→ ServiceManager.start_service('ollama')
    │   ├─→ Platform-specific startup command
    │   ├─→ Poll health_url
    │   └─→ Return when healthy or timeout
    └─→ show_status()
    ↓
[App Ready]
```

### CLI Selection Flow

```
main.py executed
    ↓
determine_cli_mode()
    ├─→ Check --cli-mode flag
    └─→ or CLIFactory.detect_environment()
    ↓
CLIFactory.create(mode)
    └─→ Return appropriate CLI instance
    ↓
cli.initialize()
    └─→ Setup VoiceOrchestrator + ServiceManager
    ↓
[Running in Selected Mode]
    ├─→ interactive: Start REPL loop
    ├─→ headless: Await external commands
    └─→ single-command: Execute and exit
```

---

## Thread Safety

### Protected Resources

1. **Memory Bank Database**
   - Protected by `threading.Lock` in `MemoryBank.__init__`
   - All DB operations use context manager

2. **Memory Configuration**
   - Config read-only after initialization
   - Config updates merged carefully

3. **Ephemeral Context**
   - Protected by `threading.Lock` in `ContextManager`
   - Snapshots on read

### Async Compatibility

- All I/O using `asyncio` (service checks, LLM calls)
- Thread safety for background daemon (cleanup thread)
- No blocking operations in async contexts

---

## Error Handling Strategies

### Service Health Failures

```python
async def _check_service_health(self, name: str) -> bool:
    try:
        async with timeout(5):  # 5s timeout
            response = requests.get(service.health_url)
            return response.status_code == 200
    except (ConnectionError, TimeoutError):
        return False
    except Exception as e:
        logger.warning(f"Health check error: {e}")
        return False
```

### Fallback LLM Selection

```python
async def generate_response(self, prompt: str):
    # Try primary LLM
    try:
        return await self.ollama_client.generate(prompt)
    except Exception as e:
        logger.warning(f"Ollama failed: {e}, trying fallback...")
        # Try Claude fallback
        try:
            return await self.claude_fallback.generate(prompt)
        except Exception as e2:
            logger.error(f"All LLMs failed: {e2}")
            return "Sorry, I'm unable to respond right now."
```

### Memory Operation Resilience

```python
if self.memory_enabled and self.memory_bank:
    try:
        context = self.memory_bank.get_relevant_context(user_input)
    except Exception as e:
        self.logger.warning(f"Memory retrieval error: {e}")
        context = None  # Continue without context
```

---

## Performance Optimizations

### Lazy Initialization

```python
# Expensive imports only when needed
if mode == CLIMode.CLAUDE:
    from anthropic import Anthropic  # Import only for Claude mode
```

### Connection Pooling

```python
# SQLite connection reused for memory bank
self.conn = sqlite3.connect(':memory:', check_same_thread=False)

# Ollama client uses httpx.AsyncClient for connection reuse
self.client = httpx.AsyncClient(timeout=httpx.Timeout(120.0))
```

### Memory Search Optimization

```python
# Limit results with keyword argument
results = self.memory_bank.search("query", limit=5, memory_types=["conversation"])
```

---

## Testing Strategy

### Unit Testing

```python
# test_cli_abstraction.py
async def test_cli_factory():
    cli = CLIFactory.create(CLIMode.STANDALONE)
    success = await cli.initialize()
    assert success
    await cli.shutdown()
```

### Integration Testing

```python
# test_integration.py
async def test_voice_with_memory():
    cli = CLIFactory.create(CLIMode.STANDALONE)
    await cli.initialize()
    
    # First interaction
    resp1 = await cli.process_command("voice hello")
    assert len(resp1) > 0
    
    # Verify stored in memory
    mb = get_memory_bank()
    results = mb.search("hello")
    assert len(results) > 0
    
    await cli.shutdown()
```

---

## Future Extensions

1. **Additional CLI Modes**
   - VS Code Extension Integration
   - Obsidian Plugin
   - Slack Bot

2. **Advanced Memory**
   - Vector database (FAISS) for semantic search
   - Long-term memory with summarization
   - Multi-user memory stores

3. **Enhanced Services**
   - Multiple LLM provider support
   - Speech recognition confidence feedback
   - Voice emotion detection

4. **Developer Tools**
   - CLI mode simulator for testing
   - Memory browser UI
   - Service health dashboard
