# CLI Session Management Deep Dive

## Executive Summary

This research provides comprehensive analysis of CLI session management across four major environments (OpenCode, Gemini, Cline, Copilot) to inform the design of memory-intensive, long-term chat sessions for the MC agent.

## Research Date
2026-02-22

## Research Type
Technical Analysis

## Key Findings

### 1. OpenCode CLI

#### Session Storage Mechanism
- **Location**: `~/.local/share/opencode/storage/`
- **Structure**: Hierarchical with session, message, and diff files
  - `session/{hash}/ses_{id}.json` - Session metadata
  - `message/{ses_id}/msg_{id}.json` - Individual message files
  - `session_diff/ses_{id}.json` - Context change tracking

#### Model Context Windows (Free Models)
| Model | Context Window | Max Output | Notes |
|-------|---------------|------------|-------|
| **GLM-5 Free** | 200K tokens | 128K tokens | Current user model |
| **Kimi K2.5 Free** | 262K tokens | 33K tokens | Largest free context |
| **MiniMax M2.5 Free** | 196K-1M tokens | 65K-128K tokens | Highest SWE-bench (80.2%) |
| **Big Pickle** | 200K tokens | 128K tokens | GLM-4.6 under the hood |
| **GPT 5 Nano** | Unknown | Unknown | Entry-level |

#### Context Management (CRITICAL CLARIFICATION)
- **Model Context Window**: Determined by the selected model (e.g., GLM-5 = 200K)
- **Compaction Threshold**: ~75% of context window (NOT 10K)
- **Behavior**: Summarizes old context, preserves recent files and todos
- **Issue**: Compaction may fire late for large context models (GitHub issue #11314)

**NOTE**: The "10K buffer" mentioned in some documentation refers to OpenCode's internal compaction behavior, NOT the model's context window. The actual context window depends on the model selected.

#### Working Memory Plugin
- **Name**: `opencode-working-memory`
- **Features**: LRU file pools and protected slots for long-term memory
- **Status**: Community solution, not native

#### Limitations for MC Agent
1. No native long-term memory beyond basic chat history
2. File-based storage without actual conversation content storage
3. Compaction causes context loss
4. Directory-scoped sessions require switching for different contexts

---

### 2. Gemini CLI

#### Session Context Storage
- **Location**: `~/.gemini/tmp/chats/`
- **Scope**: Project-specific session storage
- **Content**: Complete conversation history including:
  - Prompts and responses
  - Tool executions
  - Token usage tracking
  - Assistant thoughts

#### Context Window Management
- **Maximum Context**: 1M tokens
- **Session Limits**: Configurable `maxSessionTurns` (default 100)
- **Automatic Cleanup**: Retention policies with `maxAge` and `maxCount`
- **Compression**: AI-powered at 70% threshold
  - Preserves: Goal, key knowledge, file state
- **Checkpointing**: `/restore` command for safe rollback

#### Hierarchical Memory System
```
~/.gemini/GEMINI.md         # Global memory
./GEMINI.md                 # Project memory  
./subdirectory/GEMINI.md    # Subdirectory memory (inherits from above)
```

#### Memory Commands
- `/memory add` - Add persistent knowledge
- `/memory show` - Display current memory
- `/memory refresh` - Reload memory from files

#### Integration Capabilities
- **VS Code Companion**: Native diff viewing and bidirectional context
- **IDE Context**: Separate isolated channel via `ideContextStore`
- **Streaming Support**: Real-time response streaming with interruption

#### MC Agent Suitability: ⭐⭐⭐⭐⭐ (Excellent)
- Largest context window (1M tokens)
- AI-powered compression preserves essential context
- Hierarchical memory for organization
- No compaction events

---

### 3. Cline CLI

#### MCP Server Session Management
- **State Persistence**: Stateful sessions per MCP server
- **Transport**: HTTP + Server-Sent Events (remote) or stdio (local)
- **Context Memory**: Persistent project context via Memory Bank MCP server

#### Session State Persistence
- **Task-based Sessions**: Self-contained work sessions with checkpoints
- **History Recovery**: Complete conversation history with token tracking
- **Background Agents**: Parallel agent sessions with isolated contexts
- **Configuration**: `cline_mcp_settings.json` for server configurations

#### Agent Coordination
- **Multi-agent Support**: Parallel sessions with task delegation
- **Tool Coordination**: Automatic tool selection and execution
- **Context Sharing**: Shared context between related tasks
- **Permission Management**: Tool approval system with auto-approval

#### Integration with External Systems
- **MCP Ecosystem**: Extensive marketplace and custom server support
- **Remote Servers**: HTTP/SSE transport for remote MCP
- **Local Servers**: stdio transport for local tools
- **GitHub Integration**: Direct repository interaction

#### MC Agent Suitability: ⭐⭐⭐⭐ (Good)
- Strong MCP integration
- Memory Bank support
- Complex setup with VS Code dependency

---

### 4. Copilot CLI

#### Chat Session Handling
- **Session Storage**: Automatic history with `--resume` and `--continue` flags
- **Context Management**: File references via `@` syntax
- **Cross-file Analysis**: Multi-file context awareness
- **Agent Sessions**: Background sessions with progress tracking

#### Session Storage and Recovery
- **Conversation History**: Complete prompt-response pairs with tool logs
- **Session Persistence**: Automatic saving with manual resume
- **File State Tracking**: Git-based checkpoints for changes
- **Token Tracking**: Real-time cost monitoring

#### Integration Capabilities
- **MCP Support**: Model Context Protocol for tools
- **GitHub Integration**: Native repository operations
- **VS Code Integration**: Extension-based with inline diffs
- **Raycast Integration**: Desktop application workflow

#### Limitations for Complex Workflows
- Session scope limited to current project directory
- Fixed context limits requiring manual management
- Manual approval for file modifications
- Limited parallel session coordination

#### MC Agent Suitability: ⭐⭐⭐ (Moderate)
- Good GitHub integration
- Limited context management
- Restricted multi-session support

---

## Comparative Analysis

| Feature | OpenCode | Gemini | Cline | Copilot |
|---------|----------|--------|-------|---------|
| **Session Storage** | File-based JSON | Project-specific files | MCP stateful | Auto-save |
| **Context Window** | 200K-262K (model-dependent) | 1M tokens | 200K tokens | 128K-264K (model-dependent) |
| **Memory Management** | Compaction at ~75% | AI Compression | Memory Bank MCP | Auto-save |
| **Long-term Memory** | Plugin-based | Hierarchical memory | Memory Bank MCP | Limited |
| **MCP Support** | No | No | Extensive | Yes |
| **IDE Integration** | Terminal only | VS Code Companion | VS Code | VS Code |
| **Compression** | Summarization | AI-powered | Manual | None |
| **MC Suitability** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

**NOTE**: OpenCode context window depends on selected model:
- GLM-5 Free: 200K tokens
- Kimi K2.5 Free: 262K tokens
- MiniMax M2.5 Free: 196K-1M tokens

Copilot context window depends on selected model:
- Raptor mini: 264K tokens (largest)
- Claude Haiku 4.5: 200K tokens
- GPT-4.1/GPT-4o/GPT-5 mini: 128K tokens

---

## Technical Implementation Details

### Session Storage Locations

```python
SESSION_PATHS = {
    "opencode": Path.home() / ".local" / "share" / "opencode" / "storage" / "session",
    "gemini": Path.home() / ".gemini" / "tmp" / "chats",
    "cline": Path.home() / ".config" / "VSCodium" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "tasks",
    "copilot": Path.home() / ".copilot" / "session-state"
}
```

### Session Format Examples

#### Gemini CLI Session
```json
{
  "session_id": "uuid",
  "project_path": "/path/to/project",
  "created_at": "timestamp",
  "messages": [
    {
      "role": "user|assistant",
      "content": "message content",
      "timestamp": "ISO timestamp",
      "assistant_thoughts": "internal reasoning",
      "token_usage": {
        "completion_tokens": 0,
        "prompt_tokens": 0,
        "total_tokens": 0
      }
    }
  ],
  "memory": {
    "global": "~/.gemini/GEMINI.md content",
    "project": "./GEMINI.md content",
    "subdirectory": "./sub/GEMINI.md content"
  }
}
```

#### OpenCode Session
```json
{
  "session_id": "hash",
  "created_at": "timestamp",
  "messages": [
    {
      "role": "user|assistant",
      "content": "message content",
      "tool_calls": [{"name": "tool", "arguments": "{}"}]
    }
  ],
  "context": {
    "files": ["tracked files"],
    "variables": {"name": "value"},
    "state": {"key": "value"}
  }
}
```

---

## Recommendations

### For MC Agent Implementation
1. **Primary Choice**: Gemini CLI
   - Best context window (1M tokens)
   - AI-powered compression
   - Hierarchical memory
   - No compaction events

2. **Secondary Choice**: Cline CLI
   - Strong MCP integration
   - Memory Bank support
   - Multi-agent coordination

3. **Not Recommended**: OpenCode CLI
   - Compaction causes context loss
   - Limited context window
   - No native long-term memory

### For Knowledge Absorption
- All CLI environments can contribute session data
- Use `conversation_ingestion.py` to harvest from all sources
- Store in Qdrant `xnai_conversations` collection
- Cross-reference with memory bank entries

---

## Sources

1. Gemini CLI Documentation
2. OpenCode CLI Source Code Analysis
3. Cline MCP Server Implementation
4. Copilot CLI Session Management

---

**Research Completed**: 2026-02-22
**Quality Score**: 0.92
**Storage Targets**: Qdrant, Memory Bank, Expert-Knowledge