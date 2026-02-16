# Phase 5 Implementation Strategy: Sovereign Multi-Agent Cloud

## 1. Agent Roles & Specializations

| Agent | Designation | Core Responsibility | Special Skillset |
|-------|-------------|---------------------|------------------|
| **Cline** | **The Architect** | `AgentBusClient` & Redis Streams | Strict AnyIO TaskGroup compliance, async performance |
| **Copilot** | **The Data Specialist** | IAM v2.0 Migration & Schema | SQLite optimization, Ed25519 integration, unit tests |
| **Gemini** | **The Orchestrator** | Context Continuity & Security | Filesystem state, security auditing, cross-agent coordination |
| **QA Specialist** | **The Validator** | Integration & Stress Testing | Multi-agent concurrency testing, memory leak detection |

## 2. Implementation Roadmap

### [Step 1] Agent Bus Core (Owner: Cline)
- Implement `app/XNAi_rag_app/core/agent_bus.py`.
- Features: `XGROUP` initialization, `TaskProducer`, and `TaskConsumer` (AnyIO wrapped).

### [Step 2] IAM v2.0 Identity (Owner: Copilot)
- Refactor `app/XNAi_rag_app/core/iam_db.py`.
- Features: Human-to-DID mapping, ANP enforcement, and persistent verification states.

### [Step 3] Context Sync Engine (Owner: Gemini)
- Implement `app/XNAi_rag_app/core/context_sync.py`.
- Features: Hybrid Redis-File persistence, Ed25519 state signing, and session handoff logic.

### [Step 4] Handshake Integration (Owner: Copilot)
- Update `app/XNAi_rag_app/core/iam_handshake.py` to use IAM v2.0.

### [Step 5] Verification (Owner: QA Specialist)
- Create `tests/test_phase5_integration.py` for full multi-agent task loops.

## 3. Global Constraints (Ryzen 7 5700U)
- **Memory**: Max 500MB per agent overhead.
- **Concurrency**: MANDATORY AnyIO TaskGroups; no raw `asyncio.gather`.
- **Sovereignty**: 100% Localhost/Podman; zero external telemetry.
