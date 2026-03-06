# XNAi Foundation Memory Bank System Analysis

## Executive Summary

This research analyzes the current memory bank system architecture, session management, and performance characteristics to inform optimization strategies for the MC agent implementation.

## Research Date
2026-02-22

## Research Type
System Analysis

## Key Findings

### 1. Memory Bank Architecture

#### MemGPT-Style Hierarchical Memory

```
┌─────────────────────────────────────┐
│       CORE MEMORY (Always Loaded)   │
│  projectbrief • productContext      │
│  systemPatterns • techContext       │
│  activeContext • progress           │
│  Budget: ~25K tokens (~100KB chars) │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│      RECALL TIER (Searchable)       │
│  Session logs • Decisions           │
│  recall/ directory                  │
│  Retention: 90 days                 │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│     ARCHIVAL TIER (On-Demand)       │
│  Research • Benchmarks • Strategies │
│  archival/ directory                │
│  Retention: Permanent               │
└─────────────────────────────────────┘
```

#### Memory Block Configuration

| Block | Size Limit (chars) | Token Budget | Purpose |
|-------|-------------------|--------------|---------|
| projectbrief | 3,000 | ~750 | Mission, values, constraints |
| productContext | 4,000 | ~1,000 | Why XNAi, problems solved |
| activeContext | 5,000 | ~1,250 | Current priorities |
| systemPatterns | 8,000 | ~2,000 | Architecture patterns |
| techContext | 5,000 | ~1,250 | Stack, dependencies |
| progress | 3,000 | ~750 | Phase status, milestones |
| **Total Core** | **28,000** | **~7,000** | |

---

### 2. Session State Management

#### Multi-Environment Session Tracking

```python
SESSION_PATHS = {
    "cline-cli": Path.home() / ".config" / "VSCodium" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "tasks",
    "cline-extension": Path.home() / ".config" / "VSCodium" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "tasks",
    "copilot-cli": Path.home() / ".copilot" / "session-state",
    "opencode": Path.home() / ".local" / "share" / "opencode" / "storage" / "session",
    "gemini": Path.home() / ".gemini" / "tmp" / "chats"
}
```

#### Session Storage Patterns

| CLI Type | Session Type | Storage | Context Window |
|----------|--------------|---------|----------------|
| Cline CLI | File-based | JSON in tasks/ | 200K tokens |
| Cline Extension | Workspace-based | VS Code storage | 200K tokens |
| Copilot CLI | Auto-save | session-state/ | 100K tokens |
| OpenCode | File-based | storage/session/ | 10K tokens |
| Gemini | Project-specific | tmp/chats/ | 1M tokens |

---

### 3. Context Window Management

#### AnyIO-Based Async Patterns

```python
# Non-blocking I/O via anyio.to_thread.run_sync
async def read_memory_block(self, block_label: str) -> str:
    return await anyio.to_thread.run_sync(_read)

# TaskGroup-based concurrency
async with anyio.create_task_group() as tg:
    tg.start_soon(anyio_watcher, inbox, cb, poll_interval)
```

#### Context Limits & Enforcement

- **Core Memory**: Fixed 25K token limit
- **Overflow Handling**: Warning at 80%, compression at 90%
- **Compression Strategies**: 
  - Summarize old entries
  - Extract to recall tier
  - Prune duplicates

---

### 4. Agent Bus Coordination

#### Implementation

**Core Client**: `app/XNAi_rag_app/core/agent_bus.py`

```python
class AgentBusClient:
    """AnyIO-wrapped Redis Stream Client for multi-agent task distribution."""
    
    def __init__(self, agent_did: str, stream_name: str = "xnai:agent_bus"):
        self.stream_name = stream_name
        self.group_name = "agent_wavefront"
```

#### Task Routing Mechanism

```
Stream: xnai:agent_bus
Group:  agent_wavefront

Tools:
├── publish_task    → Publish task with role, action, payload
├── read_tasks      → XREADGROUP for reliable delivery
├── ack_task        → XACK for message acknowledgment
├── recover_tasks   → XAUTOCLAIM for stale message recovery
└── bus_health      → Connection health check
```

#### Agent Roles
- `architect` - Architecture decisions
- `coder` - Code implementation
- `security` - Security audits
- `documenter` - Documentation
- `researcher` - Research tasks

---

### 5. Performance Analysis

#### Current Performance Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Build Repeatability | 100% | 100% | ✅ |
| Service Startup | <120s | 60s | ✅ |
| LLM Initialization | <10s | 4s | ✅ |
| Voice Latency | <300ms | 250ms | ✅ |
| RAM Footprint | <6GB | 5.6GB | ✅ |
| API Response | <500ms | <100ms | ✅ |
| Test Pass Rate | >90% | 94%+ | ✅ |

#### Identified Bottlenecks

| Bottleneck | Impact | Solution |
|------------|--------|----------|
| Fixed Context Limits | Limits growth | Dynamic scaling |
| Manual Overflow | Requires intervention | Automatic compression |
| Redis Coordination | Latency overhead | Edge caching |
| Memory Fragmentation | No cleanup | Garbage collection |

---

### 6. Qdrant Integration

#### Collections

| Collection | Purpose | Dimension | Embedding Model |
|------------|---------|-----------|-----------------|
| `sovereign_mc_decisions` | Past decisions | 384 | BAAI/bge-small-en-v1.5 |
| `xnai_conversations` | CLI session history | 768 | nomic-ai/nomic-embed-text-v1.5 |

#### QdrantMemory Implementation

```python
class QdrantMemory:
    """Semantic memory layer using AsyncQdrantClient."""
    
    async def store_decision(self, decision_id: str, title: str, content: str, tags: list[str])
    async def search_decisions(self, query: str, limit: int = 5) -> list[dict]
    async def ensure_collection(self) -> bool  # 3-retry backoff
```

---

### 7. Conversation Ingestion

#### Implementation: `conversation_ingestion.py`

```python
class ConversationIngestion:
    """Harvest CLI session data and ingest into Qdrant xnai_conversations."""
    
    # Sources: Copilot CLI, Gemini CLI, OpenCode CLI, Cline
    # Process: Parse → Embed (fastembed) → Upsert to Qdrant
```

#### Ingestion Process

1. **Discovery**: `discover_sessions()` finds session directories
2. **Parsing**: Source-specific parsers extract content
3. **Classification**: Auto-tagging (architectural-decision, code, research, debugging)
4. **Embedding**: `fastembed.TextEmbedding` → 768-dim vectors
5. **Upsert**: Batch 100 records at a time with UUID5 IDs

---

### 8. OpenPipe Integration

#### Current State

**Implementation**: `app/XNAi_rag_app/core/openpipe_integration.py`

```python
class SovereignOpenPipeClient:
    """Sovereign OpenPipe client with caching, deduplication, and circuit breaker."""
    
    # Features:
    # - Intelligent caching (40-60% performance improvement)
    # - Request deduplication (50% cost reduction)
    # - Circuit breaker integration
    # - Zero telemetry (sovereign mode)
```

#### Task-Specific TTLs

| Task Type | TTL | Description |
|-----------|-----|-------------|
| code_generation | 600s | Code generation responses |
| research | 300s | Research findings |
| documentation | 900s | Documentation content |
| default | 300s | Default caching |

---

### 9. Security Architecture

#### Zero-Telemetry Design

- No external data transmission
- No phone-home mechanisms
- No usage tracking
- Air-gap capable (works offline)

#### Container Security

| Aspect | Implementation |
|--------|----------------|
| Rootless Execution | UID 1001 |
| Read-Only Filesystems | Immutable runtime |
| No New Privileges | CAP_DROP all |
| Resource Limits | Memory, CPU, FD limits |
| Network Isolation | Private bridge |

---

### 10. Recommendations

#### Immediate Improvements

1. **Dynamic Context Scaling**
   - Implement token budget management
   - Add automatic compression triggers
   - Support variable context windows

2. **Memory Management**
   - Add garbage collection for old sessions
   - Implement LRU eviction for embeddings
   - Create memory pooling for common contexts

3. **Performance Optimization**
   - Edge caching to reduce Redis overhead
   - Lazy loading for archival content
   - Connection pooling for Qdrant

#### Long-term Enhancements

1. **LangGraph Integration**
   - Multi-step context management workflows
   - Automated distillation pipelines
   - Quality-gated knowledge absorption

2. **Multi-Model Support**
   - Route based on context size
   - Fallback for large contexts
   - Cost optimization strategies

---

## Technical Implementation Details

### Memory Bank Tools

```python
# memory_append tool
async def memory_append(block_label: str, content: str):
    """Append content to memory block with overflow handling."""
    block = await read_memory_block(block_label)
    if len(block) + len(content) > BLOCK_LIMITS[block_label]:
        await trigger_compression(block_label)
    await write_memory_block(block_label, block + content)

# memory_replace tool
async def memory_replace(block_label: str, old: str, new: str):
    """Surgical edit to memory block."""
    block = await read_memory_block(block_label)
    updated = block.replace(old, new)
    await write_memory_block(block_label, updated)
```

### Session State Manager

```python
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
```

---

## Sources

1. XNAi Foundation Codebase Analysis
2. memory_bank/BLOCKS.yaml
3. app/XNAi_rag_app/core/agent_bus.py
4. app/XNAi_rag_app/conversation_ingestion.py
5. sovereign_mc_agent.py

---

**Research Completed**: 2026-02-22
**Quality Score**: 0.95
**Storage Targets**: Qdrant, Memory Bank, Expert-Knowledge