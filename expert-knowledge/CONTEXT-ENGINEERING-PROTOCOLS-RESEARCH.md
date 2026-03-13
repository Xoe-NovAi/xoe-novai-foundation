---
title: Context Engineering & Agent Protocols Research
type: research
audience: architect
last_updated: 2026-02-20
source: multi_agent_research_session
related: [MEMORY-BANK-OPTIMIZATION-RESEARCH.md, ASYNC-ANYIO-BEST-PRACTICES.md]
---

# Context Engineering & Agent Protocol Research

## Executive Summary

Context engineering is the discipline of designing the entire informational environment LLMs operate within—system prompts, memory blocks, tool schemas, conversation history, and dynamic context evolution. This research covers MCP (Model Context Protocol), A2A (Agent-to-Agent Protocol), and LangGraph patterns for state management.

---

## 1. Context Engineering vs Prompt Engineering

| Aspect | Prompt Engineering | Context Engineering |
|--------|-------------------|---------------------|
| Scope | Single request/response | Entire informational environment |
| Focus | Phrasing & format | Architecture & state management |
| Duration | Stateless | Stateful, long-running |
| Complexity | Linear | Hierarchical, multi-layered |

> "If prompt engineering is writing a good question, context engineering is setting up the entire classroom."

---

## 2. MCP (Model Context Protocol) - Anthropic

### Architecture
- **Client-Server** using JSON-RPC 2.0
- **"USB-C for AI applications"** - develop once, use everywhere
- Supports both local (stdio) and remote (HTTP/SSE) transports

### Three Core Primitives

| Primitive | Purpose | Control Model | Side Effects |
|-----------|---------|---------------|--------------|
| **Resources** | Contextual data (files, schemas, logs) | Application-driven | Read-only |
| **Tools** | Actions/operations (API calls, DB queries) | Model-controlled | Side effects allowed |
| **Prompts** | Templated messages/workflows | User-controlled | Structured input |

### Resource Discovery
1. **Direct resources**: `resources/list` endpoint
2. **Resource templates**: Parameterized URIs for dynamic content
3. **Subscriptions**: `resources/subscribe` for real-time updates

### Protocol Messages
```json
// List resources
{ "method": "resources/list" }

// Read resource
{ "method": "resources/read", "params": { "uri": "file:///path/to/file" } }

// Subscribe to changes
{ "method": "resources/subscribe", "params": { "uri": "resource://..." } }
```

---

## 3. A2A (Agent-to-Agent Protocol) - Google/Linux Foundation

### Overview
Standardizes communication between AI agents. Solves the **"MxN problem"** - the combinatorial difficulty of integrating M agents with N other agents.

### Key Components

| Component | Description |
|-----------|-------------|
| **Agent Card** | JSON metadata at `/.well-known/agent.json` |
| **Task** | Work unit with lifecycle states |
| **Message** | Communication turn with Parts |
| **Part** | Content: TextPart, FilePart, DataPart |
| **Artifact** | Output generated during task execution |

### Task Lifecycle
```
submitted → working → input-required → completed/failed/canceled
```

### A2A vs MCP Complementarity

| Aspect | MCP | A2A |
|--------|-----|-----|
| **Focus** | Agent-to-Tool communication | Agent-to-Agent communication |
| **Pattern** | Tool calling, function execution | Task delegation, collaboration |
| **State** | Request-response | Long-running tasks with lifecycle |

**Best Practice**: Use MCP for tools/data within an agent, A2A for inter-agent collaboration.

---

## 4. LangGraph State Management

### Checkpointing
- State snapshots at every super-step
- Stored to `thread_id` for session continuity
- Backends: SQLite, Redis, Postgres, S3

### State Schema
```python
class AgentState(TypedDict):
    messages: list[BaseMessage]
    context: dict[str, Any]
    artifacts: dict[str, str]
```

### Context Engineering Strategies

| Strategy | Description |
|----------|-------------|
| **Write** | Save context outside window (checkpoints, memory) |
| **Select** | Pull relevant context into window |
| **Compress** | Retain only essential tokens |
| **Isolate** | Split context across sub-agents/sandboxes |

---

## 5. Practical Applications for XNAi

### MCP for Memory Bank Integration

**Proposed URI Scheme**: `memory://bank/{path}`

```python
@mcp.resource("memory://bank/{path}")
async def get_memory_resource(path: str) -> Resource:
    return Resource(
        uri=f"memory://bank/{path}",
        mimeType="text/markdown",
        text=await read_memory_file(path)
    )

@mcp.tool()
async def update_active_context(priority: str, status: str) -> str:
    # Update activeContext.md programmatically
    pass
```

### A2A for Agent Bus

**Replace file-based agent bus with A2A protocol**:
- Create Agent Cards for each role (Grok MC, Cline, Claude, etc.)
- Implement task lifecycle for cross-agent work
- Standardized Message/Part structure for handoffs

### Benefits for XNAi

| Enhancement | Current | With Protocols |
|-------------|---------|----------------|
| Discovery | Manual file reading | `resources/list` |
| Updates | Poll file system | `resources/subscribe` |
| Handoffs | Ad-hoc documents | A2A task lifecycle |
| Recovery | Manual | LangGraph checkpointing |
| Coordination | File-based bus | A2A delegation |

---

## 6. Sovereignty Requirements

All protocol implementations must:
- ✅ Support air-gap operation
- ✅ No external telemetry
- ✅ No cloud dependencies
- ✅ Local-first implementations only

---

## Research Sources

### Protocol Specifications
1. [MCP Specification](https://modelcontextprotocol.io/specification/2025-11-25) - Anthropic
2. [MCP Resources](https://modelcontextprotocol.io/specification/2025-06-18/server/resources)
3. [A2A Protocol Guide](https://a2a.how/protocol)
4. [A2A GitHub](https://github.com/google/A2A)
5. [Linux Foundation A2A Announcement](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project)

### Framework Documentation
6. [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
7. [LangGraph Handoffs](https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs)
8. [LangChain Context Engineering](https://blog.langchain.com/context-engineering-for-agents/)

### Industry Announcements
9. [Google A2A Blog](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)
10. [AWS A2A Integration](https://aws.amazon.com/blogs/opensource/open-protocols-for-agent-interoperability-part-4-inter-agent-communication-on-a2a/)
11. [Google Cloud MCP Guide](https://cloud.google.com/discover/what-is-model-context-protocol)

### Courses
12. [DeepLearning.AI A2A Course](https://www.deeplearning.ai/short-courses/a2a-the-agent2agent-protocol/)

---

**Research Session**: 2026-02-20
**Status**: Ready for user review
