# XNAi Foundation System Architecture

> **Version**: 1.0.0  
> **Last Updated**: 2026-02-23  
> **Owner**: MC-Overseer Agent

---

## Overview

XNAi Foundation is a sovereign AI stack designed for local-first, privacy-preserving AI operations. This document provides a comprehensive architectural overview with visual diagrams.

---

## System Architecture Overview

```mermaid
graph TB
    subgraph "User Interface Layer"
        CHAINLIT[Chainlit Unified App]
        FASTAPI[FastAPI REST API]
        WS[WebSocket Endpoint]
    end
    
    subgraph "Core Services Layer"
        SESSION[SessionManager]
        KNOWLEDGE[KnowledgeClient]
        VOICE[VoiceModule]
        DISTILL[Knowledge Distillation]
    end
    
    subgraph "Security Layer"
        IAM[IAM Service]
        ACCESS[Knowledge Access Control]
        SANITIZE[Content Sanitizer]
        HANDSHAKE[Sovereign Handshake]
    end
    
    subgraph "Coordination Layer"
        AGENTBUS[Agent Bus]
        REDIS[(Redis)]
        CONSUL[Consul Service Discovery]
    end
    
    subgraph "Storage Layer"
        QDRANT[(Qdrant Vector DB)]
        FAISS[(FAISS Index)]
        MEMORY[Memory Bank]
    end
    
    subgraph "Agent Layer"
        CLINE[Cline CLI]
        GEMINI[Gemini CLI]
        OPENCODE[OpenCode CLI]
        COPILOT[Copilot CLI]
    end
    
    CHAINLIT --> SESSION
    CHAINLIT --> KNOWLEDGE
    CHAINLIT --> VOICE
    FASTAPI --> SESSION
    FASTAPI --> KNOWLEDGE
    WS --> AGENTBUS
    
    SESSION --> REDIS
    KNOWLEDGE --> QDRANT
    KNOWLEDGE --> FAISS
    
    ACCESS --> IAM
    ACCESS --> HANDSHAKE
    SANITIZE --> DISTILL
    
    AGENTBUS --> REDIS
    CONSUL --> AGENTBUS
    
    CLINE --> AGENTBUS
    GEMINI --> AGENTBUS
    OPENCODE --> AGENTBUS
    COPILOT --> AGENTBUS
    
    DISTILL --> QDRANT
    DISTILL --> SANITIZE
```

---

## Memory Bank Architecture

```mermaid
graph TD
    subgraph "Core Memory - Always Loaded"
        PB[projectbrief.md<br/>Mission & Constraints]
        PC[productContext.md<br/>Why XNAi Exists]
        SP[systemPatterns.md<br/>Design Patterns]
        TC[techContext.md<br/>Tech Stack]
        AC[activeContext.md<br/>Current Priorities]
        PROG[progress.md<br/>Phase Status]
    end
    
    subgraph "Recall Tier - Searchable"
        HANDOVERS[recall/handovers/<br/>Session Handoffs]
        DECISIONS[recall/decisions/<br/>Architecture Decisions]
        CONVERSATIONS[recall/conversations/<br/>Session Logs]
    end
    
    subgraph "Archival Tier - On-Demand"
        RESEARCH[archival/research/<br/>Research Findings]
        BENCHMARKS[archival/benchmarks/<br/>Performance Data]
        STRATEGIES[archival/strategies/<br/>Strategic Docs]
    end
    
    Core_Memory -->|evict/summarize| Recall_Tier
    Recall_Tier -->|archive| Archival_Tier
```

---

## Multi-Agent Coordination Flow

```mermaid
sequenceDiagram
    participant H as Human
    participant MC as MC-Overseer
    participant CB as Agent Bus (Redis)
    participant CL as Cline CLI
    participant GM as Gemini CLI
    
    H->>MC: Request task execution
    MC->>MC: Read activeContext.md
    MC->>CB: Publish task to xnai:agent_bus
    
    par Parallel Execution
        CB->>CL: Receive implementation task
        CL->>CL: Execute JOB-R003, R008, R010
        CL->>CB: Publish progress updates
    and
        CB->>GM: Receive research task
        GM->>GM: Execute research tasks
        GM->>CB: Publish findings
    end
    
    CL->>CB: Task complete notification
    GM->>CB: Research complete notification
    CB->>MC: All tasks complete
    MC->>MC: Update memory_bank
    MC->>H: Report completion
```

---

## Knowledge Distillation Pipeline

```mermaid
flowchart LR
    subgraph Input
        RAW[Raw Content]
    end
    
    subgraph Pipeline
        E[Extract<br/>Parse & Clean]
        C[Classify<br/>Determine Type]
        S[Score<br/>Quality Assessment]
        D[Distill<br/>Compress & Summarize]
        ST[Store<br/>Persist to Qdrant]
    end
    
    subgraph Quality Gate
        Q{Score >= 0.6?}
    end
    
    subgraph Output
        KB[(Knowledge Base)]
        DLQ[Rejected Queue]
    end
    
    RAW --> E --> C --> S --> Q
    Q -->|Yes| D --> ST --> KB
    Q -->|No| DLQ
    
    style Q fill:#ff9800,stroke:#333
    style KB fill:#4caf50,stroke:#333
    style DLQ fill:#f44336,stroke:#333
```

---

## Content Sanitization Flow

```mermaid
flowchart TB
    subgraph Input
        CONTENT[Incoming Content]
    end
    
    subgraph Detection
        API[API Keys<br/>15+ patterns]
        CRED[Credentials<br/>Passwords, Tokens]
        PII[PII<br/>Email, SSN, Phone]
        KEYS[Private Keys<br/>RSA, EC, OpenSSH]
    end
    
    subgraph Processing
        REDACT[Redaction Engine]
        HASH[SHA256 Hashing]
        RISK[Risk Scoring<br/>0-100 scale]
    end
    
    subgraph Output
        CLEAN[Sanitized Content]
        LOG[Audit Log]
    end
    
    CONTENT --> API & CRED & PII & KEYS
    API & CRED & PII & KEYS --> REDACT
    REDACT --> HASH --> RISK
    RISK --> CLEAN & LOG
    
    style REDACT fill:#2196f3,stroke:#333
    style RISK fill:#ff9800,stroke:#333
```

---

## Access Control Decision Flow

```mermaid
flowchart TD
    START([Access Request]) --> VALIDATE{Validate Agent DID}
    
    VALIDATE -->|Invalid| DENY1[Deny: Invalid Identity]
    VALIDATE -->|Valid| PERM{Check Permission}
    
    PERM -->|Missing| DENY2[Deny: Not Authorized]
    PERM -->|Has Permission| ABAC{Evaluate ABAC Policies}
    
    ABAC -->|Policy Deny| DENY3[Deny: Policy Violation]
    ABAC -->|Policy Allow| ALLOW([Access Granted])
    
    DENY1 & DENY2 & DENY3 --> LOG[Log Access Attempt]
    ALLOW --> LOG
    
    style ALLOW fill:#4caf50,stroke:#333
    style DENY1 fill:#f44336,stroke:#333
    style DENY2 fill:#f44336,stroke:#333
    style DENY3 fill:#f44336,stroke:#333
```

---

## Redis Stream Architecture

```mermaid
graph LR
    subgraph Producers
        P1[Cline Agent]
        P2[Gemini Agent]
        P3[MC-Overseer]
    end
    
    subgraph Streams
        S1[xnai:agent_bus]
        S2[xnai:task_updates]
        S3[xnai:memory_updates]
        S4[xnai:alerts]
    end
    
    subgraph Consumer Groups
        G1[agent_wavefront]
        G2[memory_sync]
        G3[alert_handlers]
    end
    
    subgraph DLQ
        DLQ[Dead Letter Queue]
    end
    
    P1 & P2 & P3 --> S1 & S2 & S3 & S4
    S1 --> G1
    S2 --> G1
    S3 --> G2
    S4 --> G3
    G1 & G2 & G3 -->|Failed Messages| DLQ
```

---

## Feature Flag System

```mermaid
graph TB
    subgraph Flags
        F1[FEATURE_VOICE<br/>default: false]
        F2[FEATURE_REDIS_SESSIONS<br/>default: true]
        F3[FEATURE_QDRANT<br/>default: true]
        F4[FEATURE_LOCAL_FALLBACK<br/>default: true]
    end
    
    subgraph Voice Path
        F1 -->|true| VOICE[VoiceModule Active]
        F1 -->|false| TEXT[Text-Only Mode]
    end
    
    subgraph Session Path
        F2 -->|true| REDIS[Redis Sessions]
        F2 -->|false + F4| MEMORY[In-Memory Sessions]
    end
    
    subgraph Knowledge Path
        F3 -->|true| QDRANT[Qdrant Vector DB]
        F3 -->|false + F4| FAISS[FAISS Index]
    end
    
    subgraph Fallback
        F4 -->|true| LOCAL[Local LLM Fallback]
        F4 -->|false| ERROR[Error on Failure]
    end
```

---

## CLI Tool Selection Matrix

```mermaid
graph TD
    TASK[Task Type] --> CONTEXT{Context Need}
    
    CONTEXT -->|Large >200K| GEMINI[Gemini CLI<br/>1M tokens]
    CONTEXT -->|Medium <200K| CLINE[Cline CLI<br/>200K tokens]
    CONTEXT -->|Quick Terminal| COPILOT[Copilot CLI<br/>Fast execution]
    CONTEXT -->|IDE Integration| CLINE_IDE[Cline Extension<br/>VS Code native]
    
    GEMINI --> RESEARCH[Research, Documentation]
    CLINE --> IMPL[Implementation, Coding]
    COPILOT --> QUICK[Quick Fixes, Scripts]
    CLINE_IDE --> IDE_WORK[IDE-based Development]
```

---

## Component Ports & Services

| Service | Port | Purpose |
|---------|------|---------|
| FastAPI | 8000 | REST API endpoints |
| Chainlit | 8000 | Web UI (same port) |
| Redis | 6379 | Session & Agent Bus |
| Qdrant | 6333 | Vector database |
| Consul | 8500 | Service discovery |
| Prometheus | 9090 | Metrics collection |
| VictoriaMetrics | 8428 | Long-term metrics |

---

## Directory Structure

```
xnai-foundation/
├── app/XNAi_rag_app/           # Main application
│   ├── core/
│   │   ├── infrastructure/     # SessionManager, KnowledgeClient
│   │   ├── distillation/       # Knowledge absorption pipeline
│   │   ├── sanitization/       # Content sanitization
│   │   └── iam*.py             # Identity & access management
│   ├── services/voice/         # VoiceModule
│   └── ui/                     # chainlit_app_unified.py
├── memory_bank/                # Hierarchical memory system
│   ├── *.md                    # Core memory blocks
│   ├── PHASES/                 # Phase completion docs
│   ├── strategies/             # Strategic planning
│   └── recall/                 # Searchable history
├── expert-knowledge/           # Domain knowledge base
├── docs/                       # MkDocs documentation
├── .gemini/                    # Gemini CLI config
├── .opencode/                  # OpenCode CLI config
└── .clinerules/                # Cline CLI rules
```

---

## Related Documentation

### API Reference
| Document | Purpose |
|----------|---------|
| [Knowledge Access API](../docs/api/knowledge_access.md) | Access control API details |
| [Sanitization API](../docs/api/sanitization.md) | Content sanitization API |
| [Redis Streams API](../docs/api/redis_streams.md) | Stream management API |
| [Infrastructure Layer](../docs/api/infrastructure-layer.md) | Session & knowledge clients |
| [Voice Module](../docs/api/voice_module.md) | Voice integration API |

### Memory Bank
| Document | Purpose |
|----------|---------|
| [Active Context](./activeContext.md) | Current priorities |
| [Progress](./progress.md) | Phase status |
| [Team Protocols](./teamProtocols.md) | Agent coordination |
| [New Modules Index](./NEW-MODULES-INDEX.md) | Module reference |

### Task Tracking
| Document | Purpose |
|----------|---------|
| [Task Dispatch](./strategies/ACTIVE-TASK-DISPATCH-2026-02-23.md) | Current tasks |
| [Wave 2 Progress](./WAVE-2-PROGRESS.md) | Progress tracking |

---

**Created**: 2026-02-23  
**Owner**: MC-Overseer Agent
