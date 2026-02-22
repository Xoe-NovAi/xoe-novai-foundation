# XNAi Foundation — Cross-Session Memory Persistence

## Architecture Overview

### 1. Memory Persistence Layers
```
┌─────────────────────────────────────────────────────────────────┐
│                    CLI Environment Layer                        │
│  Cline CLI → ~/.config/cline/                                  │
│  Gemini CLI → ~/.gemini/                                        │
│  OpenCode CLI → ~/.opencode/                                    │
│  VS Codium → ~/.config/VSCodium/                                │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    Cross-Session Layer                          │
│  Redis Persistence → xnai:memory:* keys                         │
│  Consul Service → xnai-memory-service                           │
│  File System Cache → ~/.xnai/memory/                            │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    Memory Bank Layer                            │
│  memory_bank/core/ → Always loaded                              │
│  memory_bank/recall/ → Searchable sessions                      │
│  memory_bank/archival/ → On-demand research                     │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Persistence Strategy

| Data Type | Storage Location | TTL | Sync Method |
|-----------|------------------|-----|-------------|
| Core Context | Redis + File Cache | 24h | Real-time |
| Session State | Redis + Consul | 7d | Periodic |
| Strategic Decisions | Redis + File | Permanent | Manual |
| Agent Assignments | Redis + Consul | 24h | Real-time |

## Implementation Plan

### Phase 1: Redis Persistence Layer (P0)

```python
# persistence/redis_persistence.py
class RedisPersistence:
    def __init__(self):
        self.client = redis.asyncio.from_url(
            "redis://localhost:6379/0",
            encoding="utf-8",
            decode_responses=True
        )
        self.namespace = "xnai:memory"
    
    async def set_context(self, key, value, ttl=86400):
        """Set context with namespace and TTL"""
        full_key = f"{self.namespace}:{key}"
        await self.client.setex(full_key, ttl, value)
    
    async def get_context(self, key):
        """Get context from namespace"""
        full_key = f"{self.namespace}:{key}"
        return await self.client.get(full_key)
    
    async def delete_context(self, key):
        """Delete context from namespace"""
        full_key = f"{self.namespace}:{key}"
        await self.client.delete(full_key)
```

### Phase 2: CLI Agent Sync (P1)

```python
# persistence/cli_agent_sync.py
class CLIAgentSync:
    def __init__(self, persistence):
        self.persistence = persistence
        self.cli_paths = {
            "cline": os.path.expanduser("~/.config/cline/"),
            "gemini": os.path.expanduser("~/.gemini/"),
            "opencode": os.path.expanduser("~/.opencode/"),
            "vscode": os.path.expanduser("~/.config/VSCodium/")
        }
    
    async def sync_to_cli(self, cli_type, context_type, content):
        """Sync context to specific CLI environment"""
        cli_path = self.cli_paths[cli_type]
        cache_path = os.path.join(cli_path, "memory_cache.json")
        
        # Load or create cache
        cache = {}
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                cache = json.load(f)
        
        # Update cache
        cache[context_type] = {
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save cache
        with open(cache_path, 'w') as f:
            json.dump(cache, f, indent=2)
        
        # Sync to Redis
        await self.persistence.set_context(
            f"{cli_type}:{context_type}", 
            content
        )
```

### Phase 3: Session Recovery (P2)

```python
# persistence/session_recovery.py
class SessionRecoveryManager:
    def __init__(self, persistence, file_cache):
        self.persistence = persistence
        self.file_cache = file_cache
        self.context_order = ["core", "session", "strategic", "agent"]
    
    async def recover_session(self):
        """Recover session context from all sources"""
        recovered_context = {}
        
        # Try Redis first
        for context_type in self.context_order:
            content = await self.persistence.get_context(context_type)
            if content:
                recovered_context[context_type] = content
        
        # Try file cache if Redis fails
        if not recovered_context:
            for context_type in self.context_order:
                content = self.file_cache.load_from_cache(context_type)
                if content:
                    recovered_context[context_type] = content
        
        return recovered_context
    
    async def save_session(self, context_data):
        """Save session context to all sources"""
        for context_type, content in context_data.items():
            await self.persistence.set_context(context_type, content)
            self.file_cache.save_to_cache(context_type, content)
```

## Context Types

```yaml
# persistence/context_types.yaml
core:
  ttl: 86400  # 24 hours
  priority: high
  description: Core project context

session:
  ttl: 604800  # 7 days
  priority: medium
  description: Session state and decisions

strategic:
  ttl: null     # Permanent
  priority: high
  description: Strategic decisions and plans

agent:
  ttl: 86400    # 24 hours
  priority: high
  description: Agent assignments and states
```

## Performance Targets

| Metric | Target | Current | Improvement |
|--------|--------|---------|-------------|
| Context Load Time | <50ms | ~200ms | 75% faster |
| Memory Usage | <2KB | ~8KB | 75% reduction |
| Cross-CLI Sync | <100ms | ~500ms | 80% faster |
| Session Recovery | <200ms | ~1s | 80% faster |

## Error Handling

```python
# persistence/error_handling.py
class PersistenceErrorHandler:
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 1.0
    
    async def handle_redis_error(self, operation, *args, **kwargs):
        """Handle Redis operation errors with retry"""
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                return await operation(*args, **kwargs)
            except redis.exceptions.RedisError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                continue
        
        raise PersistenceError(f"Redis operation failed: {last_exception}")
```

---

**Status**: PENDING - Requires implementation via specialized agents
**Owner**: MC-Overseer
**Dependencies**: Redis service, Consul service, File system access
**Last Updated**: 2026-02-22