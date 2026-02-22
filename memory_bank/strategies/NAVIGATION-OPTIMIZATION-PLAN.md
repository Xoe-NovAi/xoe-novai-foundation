# XNAi Foundation — Unified Navigation System

## Navigation Architecture

### 1. Master Project Index
```yaml
# master_index.yaml
projects:
  xnai-foundation:
    path: "/home/arcana-novai/Documents/xnai-foundation"
    description: "Sovereign AI platform with RAG, voice interfaces, multi-agent orchestration"
    status: "Production-Ready"
    last_updated: "2026-02-22"
    
  arcana-nova-stack:
    path: "/home/arcana-novai/Documents/arcana-nova"
    description: "Esoteric consciousness layer with 10 Pillars, Dual Flame, Pantheon Model"
    status: "In Development"
    last_updated: "2026-02-15"
    
  xoe-novai-sync:
    path: "/home/arcana-novai/Documents/xoe-novai-sync"
    description: "External AI context hub for Grok/Claude/Gemini integration"
    status: "Planning"
    last_updated: "2026-02-10"
```

### 2. Directory Structure Optimization
```
/home/arcana-novai/Documents/
├── xnai-foundation/                    # Core platform
│   ├── memory_bank/                   # Strategic context
│   │   ├── core/                     # Always loaded (6 files)
│   │   ├── recall/                    # Searchable sessions
│   │   ├── archival/                  # On-demand research
│   │   └── strategies/               # Strategic planning
│   ├── mc-oversight/                 # Strategic guidance
│   ├── expert-knowledge/             # Research repository
│   ├── plans/                       # Implementation plans
│   ├── benchmarks/                   # Performance testing
│   └── configs/                     # Service configurations
├── arcana-nova/                      # Consciousness layer
│   ├── pillars/                     # 10 Pillars documentation
│   ├── pantheon/                    # Pantheon Model
│   ├── dual-flame/                  # Dual Flame system
│   └── implementations/             # Code implementations
├── xoe-novai-sync/                   # Context synchronization
│   ├── grok-context/                # Grok context packs
│   ├── claude-context/              # Claude context packs
│   ├── gemini-context/              # Gemini context packs
│   └── ekb-exports/                 # External knowledge base
└── projects-index.yaml              # Unified navigation
```

### 3. Navigation CLI Tool
```python
# navigation_cli.py
class XNAINavigation:
    def __init__(self):
        self.project_index = self._load_project_index()
        self.context_cache = {}
    
    def navigate(self, project, target):
        """Navigate to any project or context"""
        if project not in self.project_index:
            raise ValueError(f"Project {project} not found")
        
        project_path = self.project_index[project]['path']
        
        if target == "memory_bank":
            return self._navigate_memory_bank(project_path)
        elif target == "strategies":
            return self._navigate_strategies(project_path)
        elif target == "active_context":
            return self._navigate_active_context(project_path)
        else:
            return f"{project_path}/{target}"
    
    def search_context(self, query):
        """Search across all projects and contexts"""
        results = []
        for project, info in self.project_index.items():
            results.extend(self._search_project(project, info['path'], query))
        return sorted(results, key=lambda x: x['relevance'], reverse=True)
```

## Implementation Plan

### Phase 1: Master Index Creation (P0)
1. **Create projects-index.yaml** - Unified project registry
2. **Implement XNAINavigation** - Navigation CLI tool
3. **Add cross-project search** - Semantic search across all projects

### Phase 2: Directory Structure (P1)
1. **Standardize project layouts** - Consistent directory patterns
2. **Create navigation aliases** - Quick access shortcuts
3. **Implement context caching** - Performance optimization

### Phase 3: Integration (P2)
1. **Agent Bus integration** - Navigation via agent coordination
2. **CLI tool integration** - Direct navigation from all CLI environments
3. **Documentation generation** - Auto-generated navigation docs

## Performance Targets

| Metric | Target | Current | Improvement |
|--------|--------|---------|-------------|
| Navigation Response | <50ms | ~200ms | 75% faster |
| Context Search | <100ms | ~500ms | 80% faster |
| Cross-Project Sync | <500ms | ~2s | 75% faster |
| Memory Usage | <2MB | ~8MB | 75% reduction |

## Cross-Environment Integration

### CLI Agent Integration
```yaml
# cli_integration.yaml
agents:
  cline:
    navigation: "/home/arcana-novai/.config/cline/navigation.json"
    context: "/home/arcana-novai/.config/cline/context_cache.json"
  
  gemini:
    navigation: "/home/arcana-novai/.gemini/navigation.json"
    context: "/home/arcana-novai/.gemini/context_cache.json"
  
  opencode:
    navigation: "/home/arcana-novai/.opencode/navigation.json"
    context: "/home/arcana-novai/.opencode/context_cache.json"
```

### Memory Persistence
```python
# cross_session_memory.py
class CrossSessionMemory:
    def __init__(self):
        self.persistence_engine = RedisPersistence()
        self.context_cache = self._load_context_cache()
    
    def save_context(self, context_type, content):
        """Save context across sessions"""
        key = f"xnai:context:{context_type}"
        self.persistence_engine.set(key, content, ttl=86400)
        
    def load_context(self, context_type):
        """Load context from previous sessions"""
        key = f"xnai:context:{context_type}"
        return self.persistence_engine.get(key)
```

---

**Status**: PENDING - Requires implementation via specialized agents
**Owner**: MC-Overseer → Coordination with navigation-cli agent
**Dependencies**: Redis persistence, Consul service discovery, Agent Bus coordination