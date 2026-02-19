# OpenCode Fork Integration Research

## Executive Summary

OpenCode is MIT-licensed open source software, making it suitable for forking and deep integration with the XNAi Foundation stack. This document explores the feasibility and approach for creating a customized "XNAi Code" variant.

## License Analysis

### MIT License

OpenCode uses the MIT license, which permits:
- Commercial use
- Modification
- Distribution
- Private use

**Requirements**:
- Include copyright notice
- Include license copy

**No restrictions on**:
- Sublicensing
- Liability
- Warranty

### Implications for XNAi Foundation

We can:
1. Fork and modify OpenCode
2. Integrate deeply with Foundation stack
3. Distribute as "XNAi Code"
4. Keep modifications proprietary if desired

## Fork Strategy

### Option 1: Full Fork

Create a complete fork with custom branding and features.

**Pros**:
- Full control over features
- Custom branding
- Tailored UX

**Cons**:
- Maintenance burden
- Sync with upstream
- Fragmentation

**Estimated Effort**: High (ongoing)

### Option 2: Plugin Architecture (Recommended)

Extend OpenCode via plugins and MCP servers without forking.

**Pros**:
- Easy upstream updates
- Modular architecture
- Community compatibility

**Cons**:
- Limited to exposed APIs
- May hit extension limits

**Estimated Effort**: Medium (initial)

### Option 3: Hybrid Approach

Fork with plugin-first philosophy, contributing upstream where possible.

**Pros**:
- Balance of control and compatibility
- Can contribute useful changes upstream
- Custom core when needed

**Cons**:
- Complex maintenance
- Need to track upstream

**Estimated Effort**: Medium-High

## Deep Integration Points

### 1. Memory Bank Integration

**Current State**: Skills read memory bank via file system.

**Deep Integration**:
- Built-in memory bank awareness
- Automatic context loading
- Memory bank editing tools
- Conflict resolution

**Implementation**:
```typescript
// Core integration in OpenCode
class MemoryBankManager {
  async loadContext(): Promise<MemoryContext>
  async updateContext(changes: Changes): Promise<void>
  async resolveConflicts(): Promise<void>
}
```

### 2. Agent Bus Native Support

**Current State**: MCP server bridges to Redis.

**Deep Integration**:
- Native Redis Streams support
- Built-in agent discovery
- Circuit breaker integration
- Consul health checks

**Implementation**:
```typescript
class AgentBusClient {
  async registerAgent(role: string): Promise<AgentId>
  async publishTask(task: Task): Promise<void>
  async subscribeResults(handler: Handler): Promise<void>
}
```

### 3. RAG Integration

**Current State**: MCP server calls RAG API.

**Deep Integration**:
- Built-in semantic search
- Context-aware retrieval
- Hybrid search modes
- Result ranking

**Implementation**:
```typescript
class RAGClient {
  async semanticSearch(query: string): Promise<Results>
  async addToIndex(content: Content): Promise<void>
  async reindex(): Promise<void>
}
```

### 4. Vikunja Native Support

**Current State**: MCP server calls Vikunja API.

**Deep Integration**:
- Task panel in UI
- Progress tracking
- Sprint integration
- Burndown charts

### 5. Consul Integration

**Current State**: Not integrated.

**Deep Integration**:
- Service discovery
- Health monitoring
- Configuration distribution
- KV store access

## Proposed Architecture

### XNAi Code Core

```
xnai-code/
├── core/
│   ├── memory-bank/      # Built-in memory bank
│   ├── agent-bus/        # Native agent coordination
│   ├── rag/              # Semantic search
│   └── consul/           # Service discovery
├── mcp/                   # MCP server support
├── skills/                # Skill system
├── agents/                # Agent system
└── ui/                    # Custom UI (optional)
```

### Configuration Schema

```json
{
  "$schema": "https://xnai.ai/schema/xnai-code.json",
  "version": "1.0",
  "foundation": {
    "memory_bank": {
      "path": "memory_bank",
      "auto_load": true
    },
    "agent_bus": {
      "redis_url": "redis://localhost:6379",
      "streams": ["xnai:tasks", "xnai:results"]
    },
    "rag": {
      "api_url": "http://localhost:8000",
      "default_mode": "hybrid"
    },
    "consul": {
      "url": "http://localhost:8500",
      "service_name": "xnai-code"
    }
  }
}
```

## Implementation Roadmap

### Phase 1: MCP Servers (Current)
- xnai-rag MCP server
- xnai-agentbus MCP server
- xnai-vikunja MCP server

**Timeline**: Complete
**Effort**: 2 days

### Phase 2: Skills & Agents
- 7 core skills
- 2 specialized agents
- Custom commands

**Timeline**: Complete
**Effort**: 1 day

### Phase 3: Fork Evaluation
- Test plugin limits
- Identify missing APIs
- Evaluate fork necessity

**Timeline**: 1 week
**Effort**: 3 days

### Phase 4: Deep Integration (If Forked)
- Memory bank native support
- Agent bus integration
- RAG client built-in

**Timeline**: 2-4 weeks
**Effort**: 2-3 weeks

### Phase 5: XNAi Code Release
- Branding and packaging
- Documentation
- Distribution

**Timeline**: 1 week
**Effort**: 1 week

## Maintenance Considerations

### Upstream Sync

If forking, establish:
1. Regular upstream merge schedule
2. Feature parity tracking
3. Security update process

### Testing Strategy

1. Unit tests for core integrations
2. Integration tests with Foundation stack
3. E2E tests for workflows

### Documentation

1. Custom user guide
2. Integration documentation
3. API reference for extensions

## Recommendation

**Start with Option 2 (Plugin Architecture)**:
1. Implement via MCP servers (complete)
2. Create skills and agents (complete)
3. Test for 2-4 weeks
4. Evaluate fork necessity based on gaps

**Fork if needed**:
- Plugin APIs insufficient
- Performance limitations
- UX customization required

## Conclusion

OpenCode's MIT license enables deep integration with XNAi Foundation. The recommended approach is to start with plugins and MCP servers, then evaluate forking based on real-world needs. Current implementation via MCP servers and skills provides significant integration capability without modification.
