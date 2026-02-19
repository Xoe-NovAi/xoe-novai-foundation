# XNAi Foundation - Agent Instructions

## Project Overview
XNAi Foundation is a sovereign, offline-first AI platform providing RAG, voice-first interfaces, and multi-agent orchestration. Built for accessibility on consumer hardware.

## Core Principles
1. **Torch-free**: No PyTorch/Torch/Triton/CUDA - use ONNX, GGUF, Vulkan
2. **Sovereign**: Zero external telemetry, air-gap capable
3. **Resource-efficient**: Target <6GB RAM, <500ms latency
4. **Ethical**: Ma'at's 42 Ideals guide all decisions

## Memory Bank Protocol
**CRITICAL**: Read `memory_bank/*.md` before any task:
- `activeContext.md` - Current priorities
- `progress.md` - Implementation status
- `systemPatterns.md` - Architecture patterns
- `techContext.md` - Tech stack constraints

Update memory bank after architectural decisions or multi-file changes.

## Available Skills
| Skill | Purpose | Trigger |
|-------|---------|---------|
| memory-bank-loader | Load project context | Session start |
| agent-bus-coordinator | Multi-agent coordination | Parallel work |
| phase-validator | Phase completion verification | Milestones |
| sovereign-security-auditor | Security hardening | Before commits |
| doc-taxonomy-writer | Documentation classification | Doc changes |
| vikunja-task-manager | Task tracking | Planning |
| semantic-search | RAG queries | Research |

## Stack Constraints
- **Python**: 3.12-slim containers
- **Containers**: Rootless Podman with `:Z,U` volumes
- **Package Manager**: uv with hash-verified lock files
- **Async**: AnyIO TaskGroups (never asyncio.gather)
- **Docs**: MkDocs 1.6.1 + Material 10.0.2

## Development Workflow
1. Read memory bank for context
2. Plan changes with dry-runs
3. Implement with atomic operations
4. Verify with tests and permissions checks
5. Update memory bank and docs
6. Run security audit before commit

## Foundation Stack Endpoints
| Service | Endpoint | Purpose |
|---------|----------|---------|
| Semantic Search | `localhost:8000/search` | RAG queries |
| Agent Bus | `localhost:6379` | Redis Streams |
| Consul | `localhost:8500` | Service discovery |
| Vikunja | `localhost:3456` | Task management |

## Code Style
- No comments unless requested
- Meaningful variable/function names
- Async-first with AnyIO
- Bounded buffers (deque with maxlen)
- Dependency injection over globals
