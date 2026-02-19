---
priority: critical
context: general
activation: always
last_updated: 2026-02-17
version: 2.0
---

# XNAi Foundation Core Context

## Mission
Democratize enterprise-grade local AI (RAG, voice-first, multi-agent) for anyone with basic hardware. Sovereign, offline-first, zero-telemetry, air-gapped capable.

## Golden Trifecta
1. **Sovereign Data**: LangChain + FAISS/Qdrant hybrid retrieval (BM25 + dense)
2. **High-Performance Local Inference**: GGUF quantized models (INT8/INT4 adaptive)
3. **Seamless UX**: Voice-first (Piper TTS + Faster-Whisper STT), Chainlit interface, <300ms latency

## Key Principles
- **Torch-free everywhere** (no PyTorch/Torch/Triton/CUDA/Sentence-Transformers)
- **CPU + Vulkan only** (Ryzen-optimized)
- **Privacy-first**: Zero external data transmission
- **Ethical Guardrails**: Ma'at's 42 Ideals (truth, justice, compassion, sovereignty, wisdom)
- **Sovereign Trinity (Phase 4.2)**: Consul service mesh, Redis persistent circuit breakers, Ed25519 agent handshakes
- **Resource Mastery**: Optimized for Ryzen 7 5700U (6.6GB RAM), Multi-Tiered zRAM (lz4+zstd)

## Tech Stack
| Component | Technology |
|-----------|------------|
| Orchestration | LangChain (torch-free) |
| Vector DB | FAISS primary, Qdrant ready |
| Models | GGUF quantized (q4-q6), Vulkan acceleration |
| Voice | Piper ONNX TTS, Faster-Whisper STT |
| API/UI | FastAPI, Chainlit |
| Concurrency | AnyIO TaskGroups |
| Observability | OpenTelemetry, Prometheus, Grafana |
| Containers | Rootless Podman, python:3.12-slim |
| Package Manager | uv (mirrors: USTC/SDUT) |
| **CLI AI Agents** | OpenCode, Cline (VS Code), Copilot CLI |

## Model Selection Matrix (30+ Free Frontier Models)

### By Task Type

| Task | Primary CLI | Model(s) | Why |
|------|-------------|----------|-----|
| **Real-time terminal coding** | Copilot CLI | GPT-5-Mini, Claude Haiku | Fast (<3s), interactive |
| **Large code output (>8k)** | Copilot CLI | GPT-5.1-Codex-32k | 32k output limit |
| **VS Code IDE refactor** | Cline | Claude Opus, Kimi K2.5 | IDE integration, 262k context |
| **Large context analysis** | Cline | Kimi K2.5 (262k) | Largest available |
| **Code generation** | Copilot CLI | Grok Code Fast 1, GPT-5.1-Codex | Code-specialized |
| **Visual/design → code** | Cline | Kimi K2.5 | Vision + 262k context |
| **Complex reasoning** | Cline | Claude Opus (thinking) | Deep analysis with thinking |
| **Research synthesis** | OpenCode | Kimi K2.5 + Big Pickle | Multi-model validation |
| **Quick prototyping** | Copilot CLI | GPT-5-Mini | Fastest |
| **Deep problem solving** | OpenCode | Kimi K2.5, GLM-5 | Reasoning diversity |

### Quick Selection Logic (Cline Focus)

```
Cline Model Selection Decision Tree:

Task complexity?
├─ Simple (CRUD, standard patterns)
│  └─ → Claude Haiku 4.5 (fast, capable)
├─ Medium (multi-file refactor, architecture)
│  └─ → Claude Sonnet 4.5 (balanced)
├─ Complex (reasoning, design, analysis)
│  └─ → Claude Opus 4.6 (frontier reasoning)
└─ Complex + large codebase (>200k tokens)
   └─ → Kimi K2.5 (262k context!)

Vision/Design task?
└─ → Kimi K2.5 (best multimodal)

Need Extended Thinking?
└─ → Claude Opus 4.6 or Haiku with --thinking

Emergency Large Output (>8k)?
└─ → Switch to Copilot: GPT-5.1-Codex-32k
```

### Recommended Cline Workflow

1. **Daily driver (70%)**: Claude Haiku 4.5 (fast + capable)
2. **Standard work (20%)**: Claude Sonnet 4.5 (balanced)
3. **Complex (9%)**: Claude Opus 4.6 (thinking mode)
4. **Large context (1%)**: Kimi K2.5 (262k)

## Performance Targets
- Text latency: <500ms
- Voice latency: <300ms
- RAM usage: <6GB
- Atomic durability for all operations

## Workflow Protocol
1. **Memory Bank First**: Read `memory_bank/*.md` before any task
2. **Plan Mode**: Outline steps, gaps, verification for complex tasks
3. **Atomic Operations**: Timestamped backups, dry-runs, checksums
4. **Verification**: podman logs, curl, permissions checks (`ls -la`)
5. **Documentation**: Update MkDocs on changes (Diátaxis structure)

## File References
- Mission alignment: `memory_bank/projectbrief.md`
- Architecture: `memory_bank/systemPatterns.md`
- Current priorities: `memory_bank/activeContext.md`
- Implementation status: `memory_bank/progress.md`
- Project tracking: `project-tracking/PROJECT_STATUS_DASHBOARD.md`
