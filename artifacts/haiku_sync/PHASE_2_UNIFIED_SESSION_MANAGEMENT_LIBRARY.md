# 🏗️ PHASE 2: UNIFIED SESSION MANAGEMENT LIBRARY (Design Spec)
**Author**: Praxis (Haiku 4.5) | **Status**: RATIFIED
**Target**: Python Library (`session_library`)

## 1. Architecture: The 3-Layer Storage
To balance speed and persistence within the **16GB RAM** (Updated) constraint.

| Layer | Technology | Role | TTL |
| :--- | :--- | :--- | :--- |
| **Hot** | Redis Streams | Real-time Context Sync | 7 Days |
| **Warm** | Disk (JSON/MD) | Persistence & Recovery | 90 Days |
| **Cold** | Archive (Gzip) | Long-term Compliance | 2 Years |

## 2. Core Components

### A. `SessionState` (Dataclass)
```python
@dataclass
class SessionState:
    session_id: str
    agent_id: str
    context_window: List[Message]
    artifacts: List[str]
    decisions: List[Decision]
    timestamp: float
```

### B. `SessionManager` (Orchestrator)
-   **Async First**: Built on `AnyIO`.
-   **Locking**: Uses Redis Locks to prevent race conditions during "Handoff."
-   **Integrations**:
    -   `MemoryBankMCP` (Port 8005)
    -   `AgentBus` (Redis Stream `xnai:agent_bus`)

## 3. Implementation Roadmap
-   **Day 1-2**: Core Class Structure.
-   **Day 3**: Redis/Disk Persistence Layer.
-   **Day 4**: CLI Hooks (Gemini, OpenCode).
-   **Day 5**: Testing & Validation.
