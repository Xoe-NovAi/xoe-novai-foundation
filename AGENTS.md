## CLI Environment Architecture

### CLI Environment Distinctions

#### 1. Cline CLI vs Cline Extension

**Cline CLI**
- **Binary**: `~/.nvm/versions/node/v25.3.0/bin/cline`
- **Environment**: Standalone terminal application
- **Session Management**: File-based session storage in `~/.config/VSCodium/User/globalStorage/saoudrizwan.claude-dev/tasks`
- **Integration**: MCP server support via `mcp-servers/` directory
- **Architecture**: Node.js-based with VS Code extension integration

**Cline Extension**
- **Location**: VS Codium extension marketplace
- **Environment**: VS Codium IDE integration
- **Session Management**: Workspace-based sessions with inline diffs
- **Integration**: Direct IDE integration with file operations
- **Architecture**: VS Code extension API with Node.js backend

#### 2. Copilot CLI vs Copilot Extension

**Copilot CLI**
- **Binary**: `~/.local/bin/copilot`
- **Environment**: Standalone terminal application
- **Session Management**: Auto-save with `--resume` and `--continue` flags
- **Integration**: GitHub OAuth, MCP support, Raycast integration
- **Architecture**: Python-based with CLI-first design

**Copilot Extension**
- **Location**: VS Codium extension marketplace
- **Environment**: VS Codium IDE integration
- **Session Management**: Workspace-based sessions with inline suggestions
- **Integration**: Direct code completion and file operations
- **Architecture**: VS Code extension API with remote processing

#### 3. OpenCode CLI

**Standalone Environment**
- **Binary**: Built-in binary (no separate installation path)
- **Session Storage**: `~/.local/share/opencode/storage/session/{hash}/ses_{id}.json`
- **Context Management**: Automatic compaction with 10,000 token buffer
- **Working Memory**: Community plugin (`opencode-working-memory`) for long-term memory
- **Architecture**: Node.js-based with file system storage

#### 4. Gemini CLI

**Standalone Environment**
- **Binary**: `~/.nvm/versions/node/v25.3.0/bin/gemini`
- **Session Storage**: `~/.gemini/tmp/chats/` with complete conversation history
- **Context Window**: 1M token context with AI compression
- **Memory System**: Hierarchical memory (global/project/subdirectory)
- **Architecture**: Node.js-based with Google OAuth integration

## Integration Architecture

### 1. VS Codium Integration Patterns

#### Extension Integration
```yaml
# Extension Integration Architecture
extensions:
  - cline:
    - Type: VS Code Extension
    - Session: Workspace-based
    - Integration: Direct IDE integration
    - Storage: VS Codium workspace files
    
  - copilot:
    - Type: VS Code Extension
    - Session: Workspace-based
    - Integration: Inline code completion
    - Storage: VS Codium workspace files
```

#### Terminal Integration
```yaml
# Terminal Integration Architecture
terminals:
  - cline-cli:
    - Type: Standalone CLI
    - Session: File-based
    - Integration: MCP server support
    - Storage: ~/.config/VSCodium/User/globalStorage/
    
  - copilot-cli:
    - Type: Standalone CLI
    - Session: File-based
    - Integration: GitHub OAuth, MCP support
    - Storage: ~/.local/bin/
```

### 2. Cross-Environment Coordination

#### Agent Bus Architecture
```python
# Agent Bus Coordination
class AgentBusCoordinator:
    def __init__(self):
        self.stream_name = "xnai:agent_bus"
        self.group_name = "agent_wavefront"
        self.session_tracking = {
            "cline-cli": "file-based",
            "cline-extension": "workspace-based",
            "copilot-cli": "file-based",
            "copilot-extension": "workspace-based",
            "opencode": "file-based",
            "gemini": "project-specific"
        }
```

#### Session Synchronization
```python
# Session Synchronization Logic
async def sync_sessions(session_type: str, session_data: Dict):
    if session_type == "cline-cli":
        # File-based session sync
        await sync_file_based_session(session_data)
    elif session_type == "cline-extension":
        # Workspace-based session sync
        await sync_workspace_session(session_data)
    elif session_type == "copilot-cli":
        # File-based session sync with GitHub integration
        await sync_copilot_cli_session(session_data)
    elif session_type == "copilot-extension":
        # Workspace-based session sync
        await sync_copilot_extension_session(session_data)
    elif session_type == "opencode":
        # File-based session with compaction
        await sync_opencode_session(session_data)
    elif session_type == "gemini":
        # Project-specific session with AI compression
        await sync_gemini_session(session_data)
```

## Session Management Comparison

| Feature | Cline CLI | Cline Extension | Copilot CLI | Copilot Extension | OpenCode | Gemini CLI |
|---------|-----------|-----------------|-------------|-------------------|----------|------------|
| **Session Type** | File-based | Workspace-based | File-based | Workspace-based | File-based | Project-specific |
| **Context Window** | 200K tokens | 200K tokens | 128K-264K* | 128K-264K* | 200K-262K** | 1M tokens |
| **Memory Management** | Manual | Manual | Auto-save | Auto-save | Compaction | AI Compression |
| **MCP Support** | Yes | Limited | Yes | Limited | No | No |
| **IDE Integration** | VS Code only | Full IDE | VS Code only | Full IDE | Terminal only | Terminal only |
| **Cross-session Sync** | File-based | Workspace-based | File-based | Workspace-based | File-based | Project-based |

**\* Copilot context depends on model:**
- Raptor mini: 264K tokens
- Claude Haiku 4.5: 200K tokens
- GPT-4.1/GPT-4o/GPT-5 mini: 128K tokens

**\*\* OpenCode context depends on model:**
- Kimi K2.5 Free: 262K tokens
- GLM-5 Free: 200K tokens
- MiniMax M2.5 Free: 196K-1M tokens

## Technical Implementation Details

### 1. Session Storage Locations

```python
# Session Storage Paths
SESSION_PATHS = {
    "cline-cli": Path.home() / ".config" / "VSCodium" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "tasks",
    "cline-extension": Path.home() / ".config" / "VSCodium" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "tasks",
    "copilot-cli": Path.home() / ".local" / "bin" / "copilot",
    "copilot-extension": Path.home() / ".config" / "VSCodium" / "User" / "globalStorage" / "github.copilot-chat" / "sessions",
    "opencode": Path.home() / ".local" / "share" / "opencode" / "storage" / "session",
    "gemini": Path.home() / ".gemini" / "tmp" / "chats"
}
```

### 2. Session Format Specifications

```json
// Cline CLI Session Format
{
  "session_id": "string",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "messages": [
    {
      "role": "string",
      "content": "string",
      "timestamp": "timestamp",
      "tool_calls": [{"name": "string", "arguments": "string"}]
    }
  ],
  "context": {
    "files": ["string"],
    "variables": {"string": "string"},
    "state": {"string": "any"}
  }
}

// Gemini CLI Session Format
{
  "session_id": "string",
  "project_path": "string",
  "created_at": "timestamp",
  "messages": [
    {
      "role": "string",
      "content": "string",
      "timestamp": "timestamp",
      "assistant_thoughts": "string",
      "token_usage": {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}
    }
  ],
  "memory": {
    "global": "string",
    "project": "string",
    "subdirectory": "string"
  }
}
```

## Agent Coordination Patterns

### 1. Cross-Environment Agent Communication

```python
# Agent Communication Protocol
class AgentCommunication:
    def __init__(self):
        self.agent_bus = AgentBusClient()
        self.session_tracker = SessionTracker()
    
    async def coordinate_agents(self, agent_type: str, session_data: Dict):
        # Route based on environment
        if agent_type.startswith("cline-"):
            await self._coordinate_cline_agents(session_data)
        elif agent_type.startswith("copilot-"):
            await self._coordinate_copilot_agents(session_data)
        elif agent_type == "opencode":
            await self._coordinate_opencode_agents(session_data)
        elif agent_type == "gemini":
            await self._coordinate_gemini_agents(session_data)
```

### 2. Session State Management

```python
# Session State Management
class SessionStateManager:
    def __init__(self):
        self.session_store = {
            "cline-cli": FileBasedSessionStore(),
            "cline-extension": WorkspaceBasedSessionStore(),
            "copilot-cli": FileBasedSessionStore(),
            "copilot-extension": WorkspaceBasedSessionStore(),
            "opencode": FileBasedSessionStore(),
            "gemini": ProjectBasedSessionStore()
        }
    
    async def get_session(self, agent_type: str, session_id: str):
        return await self.session_store[agent_type].get(session_id)
    
    async def save_session(self, agent_type: str, session_data: Dict):
        return await self.session_store[agent_type].save(session_data)
```

## Integration with XNAi Foundation

### 1. Memory Bank Integration

```python
# Memory Bank Integration
class MemoryBankIntegration:
    def __init__(self):
        self.memory_bank = MemoryBankLoader()
        self.session_manager = SessionStateManager()
    
    async def integrate_session_memory(self, agent_type: str, session_data: Dict):
        # Extract relevant context from session
        context = self._extract_context(session_data)
        
        # Store in appropriate memory tier
        if agent_type == "gemini":
            # Store in recall tier for Gemini sessions
            await self.memory_bank.save_to_recall("gemini_session", context)
        else:
            # Store in archival tier for other sessions
            await self.memory_bank.save_to_archival(f"{agent_type}_session", context)
```

### 2. Agent Bus Coordination

```python
# Agent Bus Integration
class AgentBusIntegration:
    def __init__(self):
        self.agent_bus = AgentBusClient()
        self.session_manager = SessionStateManager()
    
    async def route_agent_tasks(self, agent_type: str, task_data: Dict):
        # Route tasks based on environment capabilities
        if agent_type == "gemini":
            # Route to Gemini-specific handlers
            await self._route_gemini_tasks(task_data)
        else:
            # Route to generic handlers
            await self._route_generic_tasks(task_data)
```

## Security Considerations

### 1. Session Data Protection

```python
# Session Security
class SessionSecurity:
    def __init__(self):
        self.encryption_key = self._load_encryption_key()
    
    async def encrypt_session(self, session_data: Dict) -> Dict:
        # Encrypt sensitive session data
        encrypted = {}
        for key, value in session_data.items():
            if key in ["content", "variables", "state"]:
                encrypted[key] = self._encrypt(value)
            else:
                encrypted[key] = value
        return encrypted
    
    async def decrypt_session(self, encrypted_data: Dict) -> Dict:
        # Decrypt session data
        decrypted = {}
        for key, value in encrypted_data.items():
            if key in ["content", "variables", "state"]:
                decrypted[key] = self._decrypt(value)
            else:
                decrypted[key] = value
        return decrypted
```

### 2. Cross-Environment Security

```python
# Cross-Environment Security
class CrossEnvironmentSecurity:
    def __init__(self):
        self.session_manager = SessionStateManager()
        self.agent_bus = AgentBusClient()
    
    async def secure_cross_environment_communication(self, agent_type: str, data: Dict):
        # Validate agent type
        if agent_type not in VALID_AGENT_TYPES:
            raise ValueError(f"Invalid agent type: {agent_type}")
        
        # Encrypt data for cross-environment transmission
        encrypted_data = await self._encrypt_data_for_environment(agent_type, data)
        
        # Route through secure agent bus
        await self.agent_bus.send_secure_message(agent_type, encrypted_data)
```

## Performance Considerations

### 1. Session Loading Performance

```python
# Session Loading Optimization
class SessionLoadingOptimizer:
    def __init__(self):
        self.cache = {}
        self.lru_cache = {}
    
    async def load_session(self, agent_type: str, session_id: str):
        # Check cache first
        cache_key = f"{agent_type}:{session_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Load from session store
        session_data = await self.session_manager.get_session(agent_type, session_id)
        
        # Cache result
        self.cache[cache_key] = session_data
        self._update_lru_cache(cache_key)
        
        return session_data
    
    def _update_lru_cache(self, cache_key: str):
        # Update LRU cache
        if cache_key in self.lru_cache:
            del self.lru_cache[cache_key]
        self.lru_cache[cache_key] = time.time()
        
        # Evict oldest if cache is full
        if len(self.lru_cache) > MAX_CACHE_SIZE:
            oldest = min(self.lru_cache, key=self.lru_cache.get)
            del self.cache[oldest]
            del self.lru_cache[oldest]
```

### 2. Cross-Environment Latency

```python
# Latency Management
class LatencyManager:
    def __init__(self):
        self.latency_metrics = {}
    
    async def measure_cross_environment_latency(self, agent_type: str):
        # Measure round-trip latency
        start_time = time.time()
        
        # Simulate cross-environment communication
        await self.agent_bus.send_message(agent_type, {"ping": True})
        response = await self.agent_bus.wait_for_response(agent_type)
        
        end_time = time.time()
        latency = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Store metrics
        self.latency_metrics[agent_type] = latency
        
        return latency
```

## Best Practices

### 1. Session Management

```python
# Session Management Best Practices
class SessionManager:
    @staticmethod
    async def best_practices():
        # Use appropriate session type for environment
        # - Use workspace-based for IDE extensions
        # - Use file-based for standalone CLIs
        # - Use project-specific for directory-based work
        
        # Implement proper session cleanup
        # - Auto-save sessions regularly
        # - Implement session expiration policies
        # - Clean up old session data
        
        # Use appropriate context management
        # - Leverage AI compression for large contexts
        # - Implement context window management
        # - Use hierarchical memory for organization
```

### 2. Cross-Environment Communication

```python
# Cross-Environment Communication Best Practices
class CrossEnvironmentCommunication:
    @staticmethod
    async def best_practices():
        # Use secure communication channels
        # - Encrypt sensitive data
        # - Validate agent types and permissions
        # - Implement authentication and authorization
        
        # Implement proper error handling
        # - Handle network failures gracefully
        # - Implement retry logic with exponential backoff
        # - Provide meaningful error messages
        
        # Optimize for performance
        # - Use connection pooling
        # - Implement caching strategies
        # - Minimize cross-environment communication
```

---

**Last Updated**: 2026-02-22
**Owner**: MC-Overseer Agent
**Dependencies**: Agent Bus, Session Manager, Memory Bank System
