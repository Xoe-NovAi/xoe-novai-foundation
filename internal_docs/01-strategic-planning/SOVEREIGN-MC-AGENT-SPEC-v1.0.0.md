# Sovereign MC Agent — Technical Specification v1.0.0
**Status**: ✅ IMPLEMENTED  
**Implementation**: `app/XNAi_rag_app/core/sovereign_mc_agent.py`  
**Date**: 2026-02-18  
**Author**: Claude Opus 4.6 (Cline) — Session Opus-Sprint-001  
**Task Reference**: TASK-021b from `internal_docs/00-system/STRATEGIC-REVIEW-CLINE-2026-02-18.md`

---

## 1. Overview

The **Sovereign MC Agent** is the self-directing intelligence layer of the XNAi Foundation stack. It enables the XNAi Foundation to direct, monitor, and coordinate itself — delegating tasks to AI agents, tracking decisions in semantic memory, managing project tasks via Vikunja, and maintaining strategic context via the memory bank.

### Design Principles
1. **Sovereign**: No external dependencies for core function — can operate air-gap with Ollama fallback
2. **AnyIO-first**: Zero `asyncio.gather`, zero `asyncio.*` — all concurrency via AnyIO TaskGroups
3. **ONNX/GGUF only**: No PyTorch, no CUDA, no Triton, no sentence-transformers
4. **Memory-persistent**: Decisions stored in Qdrant for recall across sessions
5. **Observable**: Health via Consul, logs to stdout/structured logging

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   SovereignMCAgent                      │
│                                                         │
│  ┌──────────────────┐  ┌──────────────────────────┐    │
│  │  MemoryBankReader │  │      VikunjaClient        │    │
│  │                  │  │                          │    │
│  │ reads/writes     │  │ async httpx              │    │
│  │ memory_bank/*.md │  │ → localhost:3456/api/v1  │    │
│  └──────────────────┘  └──────────────────────────┘    │
│                                                         │
│  ┌──────────────────┐  ┌──────────────────────────┐    │
│  │   QdrantMemory   │  │   OpenCodeDispatcher      │    │
│  │                  │  │                          │    │
│  │ AsyncQdrantClient│  │ anyio.run_process         │    │
│  │ collection:      │  │ → opencode CLI           │    │
│  │ sovereign_mc_    │  │ with model selection     │    │
│  │ decisions        │  └──────────────────────────┘    │
│  │ dim: 384, COSINE │                                   │
│  └──────────────────┘                                   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │              Redis AgentBus                      │  │
│  │         stream: xnai:agent_bus                   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
         ↕                    ↕                  ↕
    memory_bank/         Vikunja PM          Consul
    (strategic ctx)    (task tracking)    (health data)
```

---

## 3. Component Specifications

### 3.1 MemoryBankReader
**Purpose**: Read and write strategic context from `memory_bank/*.md` files.

```python
class MemoryBankReader:
    def __init__(self, memory_bank_path: str = "memory_bank")
    async def read_file(self, filename: str) -> str
    async def read_all(self) -> dict[str, str]
    async def write_file(self, filename: str, content: str) -> None
```

**Behavior**:
- In-memory cache: once read, files cached in `self._cache: dict[str, str]`
- Reads: `anyio.Path` async file I/O
- Writes: full file replacement (not append)
- Error handling: returns `""` on FileNotFoundError (graceful degradation)

**Key files read**:
- `activeContext.md` — current priorities, phase status
- `projectbrief.md` — project identity, constraints
- `techContext.md` — stack specs, tech choices
- `systemPatterns.md` — architecture patterns
- `teamProtocols.md` — agent protocols

---

### 3.2 VikunjaClient
**Purpose**: Async REST client for Vikunja project management API.

```python
class VikunjaClient:
    def __init__(self, base_url: str, api_token: str)
    async def get_projects(self) -> list[dict]
    async def create_task(self, project_id: int, title: str, 
                          description: str = "", priority: int = 0,
                          due_date: str | None = None) -> dict
    async def get_tasks(self, project_id: int) -> list[dict]
    async def update_task(self, task_id: int, **kwargs) -> dict
```

**Configuration**:
- Default URL: `http://localhost:3456` (host-mapped since this session)
- Auth: Bearer token in `Authorization` header
- Client: `httpx.AsyncClient` with 30s timeout

**Vikunja API endpoints used**:
- `GET /api/v1/projects` — list all projects
- `POST /api/v1/projects/{id}/tasks` — create task
- `GET /api/v1/projects/{id}/tasks` — list tasks
- `POST /api/v1/tasks/{id}` — update task

---

### 3.3 QdrantMemory
**Purpose**: Semantic memory for past decisions, enabling recall across sessions.

```python
class QdrantMemory:
    COLLECTION = "sovereign_mc_decisions"
    VECTOR_SIZE = 384  # ONNX all-MiniLM-L6-v2 compatible
    
    def __init__(self, qdrant_url: str = "http://localhost:6333")
    async def initialize(self) -> None  # creates collection if not exists
    async def store_decision(self, decision: str, metadata: dict) -> str
    async def recall_similar(self, query: str, limit: int = 5) -> list[dict]
```

**Vector storage**:
- Client: `AsyncQdrantClient` (qdrant-client v1.16.2+)
- Collection: `sovereign_mc_decisions`
- Distance: `COSINE` (normalized 384-dim embeddings)
- Payload: `{decision, agent, timestamp, session, tags[]}`

**Embedding approach**: TF-IDF-based hashing for offline operation (no sentence-transformers). For production, replace with ONNX embedding model.

---

### 3.4 OpenCodeDispatcher
**Purpose**: Delegate complex tasks to OpenCode CLI with model selection.

```python
class OpenCodeDispatcher:
    def __init__(self, working_dir: str)
    async def dispatch(self, prompt: str, model: str = "opencode/big-pickle",
                       timeout: float = 120.0) -> str
```

**Subprocess management**:
- Command: `["opencode", "--model", model, "--print", prompt]`
- Async spawn: `anyio.run_process()` — never `asyncio.create_subprocess_exec`
- Stdout captured, stderr logged
- Timeout: configurable, default 120s

**Available models**:
- `opencode/big-pickle` — general reasoning (default)
- `opencode/kimi-k2.5-free` — research, large context
- `opencode/gpt-5-nano` — fast, 400K context
- `antigravity/gemini-3-pro` — 1M context (after `opencode auth login`)
- `antigravity/claude-opus-4-5-thinking` — extended reasoning
- `ollama/qwen2.5:7b` — offline/air-gap fallback

---

### 3.5 SovereignMCAgent (Main Orchestrator)
**Purpose**: Top-level coordinator using AnyIO TaskGroups for all concurrent operations.

```python
class SovereignMCAgent:
    def __init__(self, memory_reader, vikunja_client, qdrant_memory,
                 opencode_dispatcher, redis_url, consul_url)
    
    # Context loading
    async def load_context(self) -> dict  # parallel: memory + consul health
    
    # Project management
    async def get_project_status(self) -> list[dict]
    async def create_vikunja_task(self, title, description, priority, due_date) -> dict
    
    # Agent delegation
    async def delegate_to_opencode(self, prompt, model) -> str
    async def route_via_agent_bus(self, task_type, payload) -> str
    
    # Memory operations
    async def update_memory(self, filename, content) -> None
    async def recall_decisions(self, query, limit) -> list[dict]
    
    # Health & reporting
    async def get_service_health(self) -> dict
    async def generate_status_report(self) -> str
    async def write_status_report(self, output_path) -> None
```

**AnyIO TaskGroup usage** — all parallel operations use:
```python
async with anyio.create_task_group() as tg:
    tg.start_soon(task_a)
    tg.start_soon(task_b)
```
**NEVER**: `await asyncio.gather(task_a(), task_b())`

---

### 3.6 Factory Function
```python
async def create_sovereign_mc(
    memory_bank_path: str = "memory_bank",
    vikunja_url: str = "http://localhost:3456",
    vikunja_token: str = "",
    qdrant_url: str = "http://localhost:6333",
    redis_url: str = "redis://localhost:6379",
    consul_url: str = "http://localhost:8500",
    opencode_working_dir: str = ".",
) -> SovereignMCAgent:
```
Initializes all sub-clients, calls `qdrant_memory.initialize()`, returns configured agent.

---

## 4. Data Models

### Decision Record (Qdrant payload)
```python
{
    "decision": str,          # The decision text
    "agent": str,             # "claude-opus-4.6-cline"
    "timestamp": str,         # ISO 8601
    "session": str,           # "Opus-Sprint-001"
    "tags": list[str],        # ["architecture", "agent-bus", "qdrant"]
    "rationale": str,         # Why this decision was made
    "outcome": str | None,    # Filled in on resolution
}
```

### Task Creation Request (Vikunja)
```python
{
    "title": str,             # Task title
    "description": str,       # Markdown description
    "priority": int,          # 0-5 (5=highest)
    "due_date": str | None,   # ISO 8601 datetime
    "project_id": int,        # Vikunja project ID
}
```

### Agent Bus Message (Redis Streams)
```python
{
    "task_type": str,         # "research", "implement", "review", "delegate"
    "payload": dict,          # Task-specific data
    "agent_target": str,      # "opencode", "gemini", "cline", "broadcast"
    "priority": str,          # "critical", "high", "medium", "low"
    "session_id": str,        # For response correlation
}
```

---

## 5. Configuration

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `SOVEREIGN_MC_MEMORY_PATH` | `memory_bank` | Path to memory bank dir |
| `SOVEREIGN_MC_VIKUNJA_URL` | `http://localhost:3456` | Vikunja API base URL |
| `SOVEREIGN_MC_VIKUNJA_TOKEN` | `""` | Vikunja auth token |
| `SOVEREIGN_MC_QDRANT_URL` | `http://localhost:6333` | Qdrant URL |
| `SOVEREIGN_MC_REDIS_URL` | `redis://localhost:6379` | Redis URL |
| `SOVEREIGN_MC_CONSUL_URL` | `http://localhost:8500` | Consul URL |

### Required Services
| Service | Port | Required | Notes |
|---------|------|----------|-------|
| Redis | 6379 | ✅ Yes | Agent Bus stream |
| Qdrant | 6333 | ✅ Yes | Decision memory |
| Vikunja | 3456 | ✅ Yes | Task management (port now exposed) |
| Consul | 8500 | ⚠️ Optional | Health degraded without it |
| OpenCode CLI | n/a | ⚠️ Optional | Falls back gracefully |

---

## 6. Usage Examples

### Standalone (CLI demo)
```bash
cd /home/arcana-novai/Documents/xnai-foundation
python3 -m app.XNAi_rag_app.core.sovereign_mc_agent
```

### Programmatic
```python
import anyio
from app.XNAi_rag_app.core.sovereign_mc_agent import create_sovereign_mc

async def main():
    agent = await create_sovereign_mc(
        vikunja_token=os.getenv("VIKUNJA_TOKEN"),
    )
    
    # Load strategic context
    context = await agent.load_context()
    
    # Create a task
    task = await agent.create_vikunja_task(
        title="Fix Agent Bus stream key split",
        description="Unify xnai:agent_bus stream key across all components",
        priority=5,
    )
    
    # Delegate research to OpenCode
    result = await agent.delegate_to_opencode(
        "Analyze the Agent Bus architecture and propose stream key unification",
        model="antigravity/gemini-3-pro",
    )
    
    # Write status report
    await agent.write_status_report("mc-oversight/status-report.md")

anyio.run(main)
```

---

## 7. Known Limitations & Future Work

### Current Limitations
1. **Embedding is TF-IDF hash** — not semantic. For true semantic search, integrate ONNX all-MiniLM-L6-v2 model
2. **No auto-boot** — must be explicitly invoked. Future: FastAPI lifespan service
3. **No retry logic on Qdrant init** — if Qdrant down on start, agent fails entirely
4. **VikunjaClient has no token refresh** — assumes long-lived token

### Planned Enhancements (from strategic-recommendations.md)
- **REC-004**: Extract `MemoryBankReader` to `core/memory_bank.py` as shared module
- **REC-005**: Create `services/sovereign_mc_service.py` as FastAPI lifespan service
  - REST endpoints: `/mc/status`, `/mc/dispatch`, `/mc/context`
  - Consul registration as `sovereign-mc`
- **REC-007**: Write `tests/test_sovereign_mc_agent.py` (Sprint 2)

### TASK-001 Dependency
The `route_via_agent_bus()` method publishes to `xnai:agent_bus`. However, `mcp-servers/xnai-agentbus/server.py` uses `xnai:tasks` / `xnai:results`. Until TASK-001 (stream key unification) is complete, Agent Bus routing between MCP tools and the Sovereign MC Agent will not connect.

---

## 8. Testing Guide

### Unit Tests (Sprint 2 — `tests/test_sovereign_mc_agent.py`)
```python
# Recommended test cases:
async def test_memory_bank_reader_reads_file()
async def test_memory_bank_reader_returns_empty_on_missing()
async def test_vikunja_client_creates_task(mock_httpx)
async def test_qdrant_memory_stores_and_recalls(mock_qdrant)
async def test_opencode_dispatcher_spawns_process(mock_anyio_run)
async def test_sovereign_mc_load_context_parallel()
async def test_sovereign_mc_uses_taskgroup_not_gather()
async def test_sovereign_mc_integration(running_stack)  # marks: integration
```

### Manual Smoke Test
```bash
# Ensure stack is running
docker-compose up -d redis qdrant vikunja

# Run agent demo
python3 -m app.XNAi_rag_app.core.sovereign_mc_agent

# Expected: status report written to mc-oversight/
```

---

*Spec author: Claude Opus 4.6 (Cline) | Version: 1.0.0 | Date: 2026-02-18*
