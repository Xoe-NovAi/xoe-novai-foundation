# XNAi Foundation — Memory Bank Optimization Plan

## Current State Analysis

### Memory Bank Structure
```
memory_bank/
├── activeContext.md          # Current priorities (243 lines)
├── progress.md               # Phase status (60 lines)
├── systemPatterns.md         # Architecture (178 lines)
├── techContext.md            # Stack (141 lines)
├── productContext.md         # Product vision (4KB)
├── projectbrief.md           # Mission/values (3KB)
├── CONTEXT.md                # Index file
├── teamProtocols.md          # Team rules
└── OPERATIONS.md             # Operational procedures
```

### Context Window Analysis
- **Total memory bank content**: ~15KB compressed
- **Core files**: 6 files (8KB)
- **Recall tier**: ~7KB
- **Archival tier**: ~200+ files

## Optimization Strategy

### 1. Memory Bank Compression
```yaml
# BLOCKS.yaml - Memory Block Definitions
blocks:
  - label: core_context
    files: [projectbrief.md, productContext.md, systemPatterns.md, techContext.md, activeContext.md, progress.md]
    size_limit: 8000
    tier: core
    priority: 0
  
  - label: recall_tier
    directory: recall/
    size_limit: 15000
    tier: recall
    priority: 1
  
  - label: archival_tier
    directory: archival/
    size_limit: 50000
    tier: archival
    priority: 2
```

### 2. Context Loading Optimization
```python
# memory_bank_loader.py - Optimized context loading
class MemoryBankLoader:
    def __init__(self):
        self.core_blocks = self._load_core_blocks()
        self.recall_index = self._build_recall_index()
        self.archival_index = self._build_archival_index()
    
    def load_context(self, request):
        """Load only necessary context based on request type"""
        if request == "strategic":
            return self.core_blocks
        elif request == "research":
            return self.core_blocks + self._load_relevant_recall()
        elif request == "deep_dive":
            return self.core_blocks + self._load_archival_context()
```

### 3. Cross-Session Persistence
```yaml
# cross_session_memory.yaml
persistence:
  memory_bank:
    - activeContext.md
    - progress.md
    - recall/
  
  agent_bus:
    - agent_state.json
    - task_queue.json
  
  consul:
    - service_registry.json
```

## Implementation Plan

### Phase 1: Core Optimization (P0)
1. **Implement BLOCKS.yaml** - Define memory block structure
2. **Create MemoryBankLoader** - Optimized context loading
3. **Add cross_session_memory.yaml** - Persistence configuration

### Phase 2: Recall Tier Enhancement (P1)
1. **Build recall index** - Searchable session history
2. **Implement semantic search** - RAG for context retrieval
3. **Add freshness tracking** - Stale content detection

### Phase 3: Archival Tier (P2)
1. **Create archival index** - Content categorization
2. **Implement tagging system** - Quick retrieval
3. **Add compression** - Storage optimization

## Performance Targets

| Metric | Target | Current | Improvement |
|--------|--------|---------|-------------|
| Context Load Time | <50ms | ~200ms | 75% faster |
| Memory Usage | <2KB | ~8KB | 75% reduction |
| Search Response | <100ms | ~500ms | 80% faster |
| Cross-Session Sync | <100ms | ~500ms | 80% faster |

## Risk Mitigation

### Memory Fragmentation
- **Solution**: Regular garbage collection of old sessions
- **Frequency**: Weekly automated cleanup

### Context Drift
- **Solution**: Version-controlled memory blocks
- **Validation**: Automated consistency checks

### Performance Degradation
- **Solution**: Dynamic block loading based on priority
- **Monitoring**: Real-time performance metrics

---

**Status**: PENDING - Requires implementation via specialized agents
**Owner**: MC-Overseer → Coordination with memory-bank-loader agent
**Dependencies**: AnyIO TaskGroups, Redis persistence, Consul service discovery