# Project Distinction: XNAi Foundation vs Nova Voice App

## Clear Separation Statement

**These are TWO SEPARATE projects under the Xoe-NovAi organization:**

---

## XNAi Foundation (Primary Platform)

### Identity
- **Location**: `/home/arcana-novai/Documents/xnai-foundation/`
- **Platform**: Linux (Ryzen 7 dev machine)
- **Purpose**: Sovereign AI platform with RAG, voice interfaces, multi-agent orchestration
- **Architecture**: Containerized, rootless, torch-free, zero-telemetry

### Core Principles
| Principle | Implementation |
|-----------|----------------|
| **Torch-Free** | ONNX, GGUF, Vulkan only |
| **Sovereign** | Zero external telemetry, air-gap capable |
| **Resource-Efficient** | <6GB RAM, <500ms latency |
| **Accessible** | Free tier, consumer hardware |

### Technology Stack
- **Python**: 3.12-slim containers
- **Containers**: Rootless Podman
- **Coordination**: Redis Streams (Agent Bus)
- **Discovery**: Consul
- **Vector DB**: Qdrant
- **Task Management**: Vikunja
- **Caching**: OpenPipe

### Current State
- **Production-Ready**: Semantic search, voice interface, multi-agent bus
- **Documentation**: Comprehensive (memory bank, research, strategies)
- **Branch Ready**: `xnai-agent-bus/harden-infra`

---

## Nova Voice App (Mac-Specific Project)

### Identity
- **Location**: `/home/arcana-novai/Documents/xnai-foundation/projects/nova/`
- **Platform**: macOS (Mac Mini Pro, developed on friend's machine)
- **Purpose**: Blind-accessible voice coding assistant
- **Architecture**: Direct macOS integration with CoreAudio, LaunchAgents

### Core Features
| Feature | Purpose |
|---------|---------|
| **AirPods Detection** | Auto-detect for input device |
| **Speaker Routing** | Mac mini speakers for output |
| **AudioGuardian** | Prevents audio hijacking |
| **Blind-Accessible CLI** | Voice-first interaction |

### Technology Stack
- **STT**: Whisper (faster-whisper) on port 2022
- **TTS**: Kokoro on port 8880
- **LLM**: Ollama (Llama 3.2, Mistral, Gemma 2, Phi-3)
- **Memory**: SQLite + sentence-transformers (semantic search)
- **MCP**: Full protocol support

### macOS-Specific Dependencies (~40% of codebase)
| Category | Files | Migration Complexity |
|----------|-------|---------------------|
| Audio Device Management | 2 files | HIGH |
| Bluetooth/AirPods | 2 files | HIGH |
| Service Management | 4 files | MEDIUM |
| App Bundle | 1 directory | HIGH |

### Cross-Platform Components (~60% of codebase)
| Component | Extraction Potential |
|-----------|---------------------|
| Memory Bank | HIGH |
| CLI Abstraction | HIGH |
| Health Monitor | HIGH |
| Config Manager | HIGH |
| MCP Server | HIGH |

---

## Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Xoe-NovAi Organization                       │
│                                                                  │
│  ┌─────────────────────────┐    ┌─────────────────────────────┐ │
│  │   XNAi Foundation       │    │    Nova Voice App          │ │
│  │   (Linux/Ryzen 7)       │    │    (macOS/Mac Mini Pro)    │ │
│  │                         │    │                             │ │
│  │  • Sovereign AI Platform│    │  • Blind-Accessible Voice  │ │
│  │  • RAG + Multi-Agent    │    │  • AirPods + Speaker Split │ │
│  │  • Container-Based      │    │  • macOS Integration       │ │
│  │  • Torch-Free           │    │  • Claude Code + Ollama    │ │
│  │                         │    │                             │ │
│  │  Technology:            │    │  Technology:                │ │
│  │  • Qdrant (vectors)     │    │  • SQLite (memory)         │ │
│  │  • Redis Streams        │    │  • CoreAudio (audio)       │ │
│  │  • Consul (discovery)   │    │  • LaunchAgents (services) │ │
│  │  • Podman (containers)  │    │  • Kokoro TTS (local)      │ │
│  │                         │    │                             │ │
│  │  Principles:            │    │  Features:                 │ │
│  │  • Zero Telemetry       │    │  • Voice-First CLI        │ │
│  │  • Air-Gap Capable      │    │  • AudioGuardian Daemon   │ │
│  │  • Consumer Hardware    │    │  • Wake Word Detection    │ │
│  └───────────┬─────────────┘    └─────────────┬───────────────┘ │
│              │                                 │                  │
│              └─────────────┬───────────────────┘                  │
│                            │                                      │
│              ┌─────────────▼───────────────┐                     │
│              │   INTEGRATION OPPORTUNITIES   │                     │
│              │                              │                     │
│              │  • Memory System Integration │                     │
│              │  • CLI Abstraction Reuse     │                     │
│              │  • MCP Protocol Sharing      │                     │
│              │  • Health Monitor Patterns   │                     │
│              └──────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Integration Opportunities

### What Nova Can Contribute to XNAi Foundation
| Component | Value | Extraction Complexity |
|-----------|-------|----------------------|
| Memory Bank (SQLite + semantic search) | HIGH | LOW |
| CLI Abstraction Factory Pattern | HIGH | LOW |
| Circuit Breaker Pattern | MEDIUM | LOW |
| MCP Server Implementation | HIGH | LOW |
| Wake Word Detection | MEDIUM | MEDIUM |
| Voice Session Management | HIGH | MEDIUM |

### What XNAi Foundation Can Contribute to Nova
| Component | Value | Integration Complexity |
|-----------|-------|----------------------|
| Qdrant Vector Database | HIGH | MEDIUM |
| Agent Bus Coordination | HIGH | MEDIUM |
| Consul Service Discovery | MEDIUM | LOW |
| Knowledge Absorption System | HIGH | HIGH |
| Chainlit Infrastructure Layer | HIGH | MEDIUM |

### Standalone Tools (Community-Sharable)
| Tool | Description | Community Value |
|------|-------------|-----------------|
| AudioGuardian | Prevents audio device hijacking | HIGH (Mac users) |
| Bluetooth Audio Router | AirPods + speakers split routing | HIGH (blind users) |
| Memory Bank | SQLite + semantic search | HIGH (all voice apps) |
| Wake Word Detector | Simple pattern matching | MEDIUM |
| CLI Abstraction | Multi-environment support | HIGH |

---

## Development Context

### XNAi Foundation Status
- **Strategy**: LOCKED for execution
- **Phase 1**: Chainlit consolidation (3.5 days)
- **Phase 2**: Gemini CLI MC setup (2 days)
- **Phase 3**: Knowledge Absorption (1 week)

### Nova Voice App Status
- **Version**: 1.0 Production Ready
- **Platform**: macOS only
- **Documentation**: 9 comprehensive guides
- **Testing**: Integration test stub only

---

## Key Differences

| Aspect | XNAi Foundation | Nova Voice App |
|--------|-----------------|----------------|
| **Target Platform** | Linux (rootless containers) | macOS (native integration) |
| **Hardware Target** | Consumer/Ryzen 7 | Mac Mini Pro |
| **Container Strategy** | Podman rootless | No containers |
| **Audio System** | Generic (Chainlit voice module) | CoreAudio + AirPods |
| **Memory System** | Qdrant (vectors) | SQLite + embeddings |
| **Agent Coordination** | Redis Streams | Single-process |
| **Accessibility Focus** | General | Blind users specifically |
| **Service Discovery** | Consul | Hardcoded localhost |

---

**Status**: Analysis complete
**Created**: 2026-02-22
**Purpose**: Clear distinction for integration planning