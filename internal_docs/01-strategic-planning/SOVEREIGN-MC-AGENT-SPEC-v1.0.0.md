# Sovereign MC Agent Specification v1.0.0

**Status**: DRAFT  
**Created**: 2026-02-18T05:35:00Z  
**Author**: OpenCode CLI (GLM-5-free)  
**Target Implementation**: TASK-021b (Cline/Opus 4.6)

---

## 1. Executive Summary

The Sovereign MC Agent is a locally-running orchestration agent that uses the XNAi Foundation Stack as its cognitive infrastructure. It serves as the daily project manager for all XNAi initiatives, delegating tasks to CLI agents and maintaining strategic context.

**Key Principle**: Zero external data transmission for internal project decisions. The stack IS the Mission Control.

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SOVEREIGN MC AGENT                                │
│                                                                      │
│  ┌──────────────┐   ┌─────────────┐   ┌───────────────┐            │
│  │  CONTEXT     │   │   TASK      │   │  DELEGATION   │            │
│  │  MANAGER     │   │  MANAGER    │   │  ENGINE       │            │
│  │              │   │             │   │               │            │
│  │ • Qdrant RAG │   │ • Vikunja   │   │ • Agent Bus   │            │
│  │ • memory_bank│   │ • Redis     │   │ • CLI routing │            │
│  │ • Git state  │   │ • Priorities│   │ • Handshakes  │            │
│  └──────────────┘   └─────────────┘   └───────────────┘            │
│          │                  │                  │                    │
│          └──────────────────┼──────────────────┘                    │
│                             ▼                                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    HEALTH MONITOR                             │  │
│  │              (Consul + Prometheus + Circuit Breakers)         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼ MCP Interface
        ┌─────────────────────────────────────────────┐
        │          Cline IDE / CLI Agents              │
        │  (xnai-agentbus, xnai-rag, xnai-vikunja)     │
        └─────────────────────────────────────────────┘
```

---

## 3. Core Components

### 3.1 Context Manager

**Purpose**: Load and maintain project context from multiple sources.

**Data Sources**:

| Source | Type | Purpose | Refresh |
|--------|------|---------|---------|
| `memory_bank/activeContext.md` | Strategic | Current priorities, agent assignments | On session start |
| `memory_bank/progress.md` | Status | Phase completion, milestones | On session start |
| Qdrant collections | Semantic | Past decisions, patterns, knowledge | On demand |
| Redis state | Session | Circuit breaker states, agent health | Real-time |
| Git status | Operational | Branch, uncommitted changes | On demand |

**Python Interface**:
```python
@dataclass
class ProjectContext:
    current_phase: str
    active_priorities: list[Priority]
    agent_assignments: dict[str, AgentRole]
    service_health: SystemHealth
    pending_research: list[ResearchRequest]
    git_state: GitState
    memory_bank_version: str

class ContextManager:
    async def load_context() -> ProjectContext
    async def refresh_memory_bank() -> None
    async def query_qdrant(query: str, limit: int) -> list[SearchResult]
    async def get_service_health() -> SystemHealth
    async def get_git_state() -> GitState
```

---

### 3.2 Task Manager

**Purpose**: Create, update, and prioritize tasks in Vikunja.

**Vikunja Integration**:
- Base URL: `http://localhost:3456/api/v1`
- Auth: API token from environment
- Projects: Map to XNAi initiatives

**Python Interface**:
```python
@dataclass
class VikunjaTask:
    id: int
    title: str
    description: str
    project_id: int
    priority: int  # 1-5
    assignee: str | None
    labels: list[str]
    due_date: datetime | None
    status: TaskStatus

class TaskManager:
    async def create_task(spec: TaskSpec) -> VikunjaTask
    async def update_task(task_id: int, updates: dict) -> VikunjaTask
    async def get_tasks_by_project(project_id: int) -> list[VikunjaTask]
    async def get_tasks_by_priority(min_priority: int) -> list[VikunjaTask]
    async def complete_task(task_id: int) -> None
    async def sync_with_mc_oversight() -> None  # Generate dashboard files
```

**Project Mapping**:
| Vikunja Project ID | Initiative |
|-------------------|------------|
| 1 | XNAi Core Stack |
| 2 | Documentation Excellence |
| 3 | Sovereign MC Agent |
| 4 | Phase 8 Execution |
| 5 | Research Queue |

---

### 3.3 Delegation Engine

**Purpose**: Route tasks to appropriate CLI agents via Agent Bus.

**Agent Routing Logic**:
```python
def select_agent(task: Task, context: ProjectContext) -> AgentAssignment:
    complexity = score_complexity(task)
    
    if complexity >= 8 and "opus_free" in context.promotions:
        return AgentAssignment(
            agent="cline",
            model="claude-opus-4.6",
            reason="High complexity + free Opus promotion"
        )
    
    if task.type == TaskType.RESEARCH and task.estimated_tokens > 100000:
        return AgentAssignment(
            agent="opencode",
            model="kimi-k2.5-free",
            reason="Large context research task"
        )
    
    if task.type == TaskType.STRUCTURED_ANALYSIS:
        return AgentAssignment(
            agent="opencode",
            model="glm-5-free",
            reason="Structured reasoning specialist"
        )
    
    if task.type == TaskType.VALIDATION:
        return AgentAssignment(
            agent="opencode",
            model="big-pickle",
            reason="Validation with reasoning variants"
        )
    
    if task.requires_offline:
        return AgentAssignment(
            agent="ollama",
            model="qwen2.5:7b",
            reason="Offline/sovereign requirement"
        )
    
    return AgentAssignment(
        agent="opencode",
        model="big-pickle",
        reason="Default balanced choice"
    )
```

**Python Interface**:
```python
@dataclass
class AgentAssignment:
    agent: str  # "cline", "opencode", "gemini", "ollama"
    model: str
    reason: str
    priority: int
    deadline: datetime | None

class DelegationEngine:
    async def delegate(task: VikunjaTask, context: ProjectContext) -> AgentBusMessage
    async def track_delegation(message_id: str) -> DelegationStatus
    async def handle_result(result: AgentResult) -> None
    async def retry_failed(message_id: str) -> None
```

**Agent Bus Message Format**:
```python
@dataclass
class AgentBusMessage:
    id: str  # UUID
    timestamp: datetime
    task_id: int  # Vikunja task ID
    target_agent: str
    model: str
    prompt: str
    context_files: list[str]
    expected_output: OutputSpec
    priority: int
    retry_count: int = 0
    max_retries: int = 3
```

---

### 3.4 Health Monitor

**Purpose**: Track system health and service availability.

**Health Checks**:

| Service | Endpoint | Frequency |
|---------|----------|-----------|
| Consul | `localhost:8500/v1/status/leader` | 30s |
| Redis | `PING` | 30s |
| Qdrant | `localhost:6333/health` | 30s |
| Vikunja | `localhost:3456/api/v1/info` | 60s |

**Python Interface**:
```python
@dataclass
class SystemHealth:
    consul: ServiceHealth
    redis: ServiceHealth
    qdrant: ServiceHealth
    vikunja: ServiceHealth
    overall_status: str  # "healthy", "degraded", "down"

class HealthMonitor:
    async def check_all() -> SystemHealth
    async def check_service(service: str) -> ServiceHealth
    async def get_circuit_breaker_states() -> dict[str, BreakerState]
    async def get_prometheus_metrics() -> dict[str, float]
```

---

## 4. MCP Server Interface

### 4.1 MCP Tools

The Sovereign MC Agent exposes these tools via MCP for Cline IDE:

```python
# Tool: mc_get_status
# Description: Get current project status summary
# Parameters: None
# Returns: ProjectContext as JSON

# Tool: mc_create_task
# Description: Create a new task in Vikunja
# Parameters: title, description, priority, project
# Returns: VikunjaTask

# Tool: mc_delegate_task
# Description: Delegate a task to a CLI agent
# Parameters: task_id, agent (optional), model (optional)
# Returns: AgentBusMessage ID

# Tool: mc_get_health
# Description: Get system health status
# Parameters: None
# Returns: SystemHealth

# Tool: mc_search_knowledge
# Description: Search Qdrant for past decisions/patterns
# Parameters: query, limit
# Returns: list[SearchResult]

# Tool: mc_update_memory_bank
# Description: Update memory bank files
# Parameters: file, content
# Returns: Success/failure
```

### 4.2 MCP Configuration

```json
{
  "mcpServers": {
    "xnai-mc-agent": {
      "command": "python",
      "args": ["mcp-servers/xnai-mc-agent/server.py"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "REDIS_URL": "redis://localhost:6379",
        "VIKUNJA_URL": "http://localhost:3456",
        "CONSUL_URL": "http://localhost:8500",
        "MEMORY_BANK_PATH": "./memory_bank"
      }
    }
  }
}
```

---

## 5. Implementation Plan

### Phase 1: Core Agent (TASK-021b)
**Assignee**: Cline/Opus 4.6  
**Duration**: 2-3 days  
**Files**:
- `app/XNAi_rag_app/core/sovereign_mc_agent.py`
- `app/XNAi_rag_app/core/context_manager.py`
- `app/XNAi_rag_app/core/task_manager.py`
- `app/XNAi_rag_app/core/delegation_engine.py`

**Dependencies**:
- Services operational (Redis, Qdrant, Vikunja)
- Existing Agent Bus infrastructure
- Existing IAM handshake system

### Phase 2: MCP Server (TASK-021c)
**Assignee**: Cline  
**Duration**: 1-2 days  
**Files**:
- `mcp-servers/xnai-mc-agent/server.py`
- `mcp-servers/xnai-mc-agent/tools.py`

### Phase 3: MC Oversight Integration (TASK-021d)
**Assignee**: Sovereign MC Agent (self)  
**Duration**: 1 day  
**Files**:
- Auto-generate `mc-oversight/*.md` files
- Integrate with existing dashboard files

---

## 6. API Contracts

### 6.1 Context Manager API

```python
# GET /mc/context
# Returns: ProjectContext

# POST /mc/context/refresh
# Refreshes memory bank and returns updated context

# GET /mc/context/search?q={query}&limit={limit}
# Searches Qdrant and returns results
```

### 6.2 Task Manager API

```python
# POST /mc/tasks
# Body: TaskSpec
# Returns: VikunjaTask

# GET /mc/tasks?project={id}&priority={min}
# Returns: list[VikunjaTask]

# PATCH /mc/tasks/{id}
# Body: updates dict
# Returns: VikunjaTask
```

### 6.3 Delegation API

```python
# POST /mc/delegate
# Body: { task_id, agent?, model? }
# Returns: { message_id, agent, model }

# GET /mc/delegate/{message_id}/status
# Returns: DelegationStatus

# POST /mc/delegate/{message_id}/retry
# Returns: new message_id
```

---

## 7. Error Handling

### Circuit Breaker Integration

```python
class MCACircuitBreaker:
    def __init__(self, service: str, threshold: int = 5, timeout: int = 60):
        self.service = service
        self.threshold = threshold
        self.timeout = timeout
        self.failures = 0
        self.state = "closed"
    
    async def call(self, func, *args, **kwargs):
        if self.state == "open":
            raise ServiceUnavailableError(self.service)
        
        try:
            result = await func(*args, **kwargs)
            self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            if self.failures >= self.threshold:
                self.state = "open"
                asyncio.create_task(self._reset_after_timeout())
            raise
```

### Fallback Strategies

| Service | Fallback |
|---------|----------|
| Redis | In-memory state (ephemeral) |
| Qdrant | File-based search (slower) |
| Vikunja | Local task queue |
| Consul | Direct service URLs |

---

## 8. Security Considerations

### Authentication
- Uses existing IAM Ed25519 handshake for agent-to-agent communication
- Vikunja API token stored in environment variable
- No external API keys in code

### Authorization
- All operations require valid agent identity
- Task creation requires MC Agent role
- Memory bank updates require write permission

### Data Sovereignty
- All data stays local
- No external API calls for core operations
- Optional: external API calls only for delegated research tasks

---

## 9. Success Criteria

| Criterion | Verification |
|-----------|--------------|
| Loads memory bank context | `mc_get_status` returns valid ProjectContext |
| Creates Vikunja task | Task appears in Vikunja UI |
| Routes task to agent | Agent Bus message sent, agent receives |
| Tracks health | Health dashboard shows all services |
| MCP accessible | Cline can invoke all tools |
| Zero external transmission | Network monitoring shows no unexpected calls |

---

## 10. Related Documents

- `expert-knowledge/AGENT-CLI-MODEL-MATRIX-v2.0.0.md` - Agent assignments
- `internal_docs/00-system/STRATEGIC-REVIEW-CLINE-2026-02-18.md` - Strategic context
- `mc-oversight/` - Output directory
- `memory_bank/` - Context directory

---

## 11. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-18 | Initial specification |

---

**Next Step**: TASK-021b - Implementation by Cline/Opus 4.6
