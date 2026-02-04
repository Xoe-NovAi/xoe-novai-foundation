# Xoe-NovAi Foundation Stack Context for Claude Projects

**Document Version**: 1.1 (January 27, 2026)  
**Purpose**: Comprehensive context file for Claude Sonnet to maintain full awareness of Xoe-NovAi Foundation stack, multi-AI environment, development strategies, and sovereignty constraints. This enables generation of enterprise-grade implementation manuals, security audits, and ethical frameworks.  
**Key Principles**: Sovereignty-first (zero-telemetry, offline-capable), consciousness evolution (Ma'at-aligned with HITL), rootless Podman deployment.  
**Constraints**: Torch-free, <6GB RAM, CPU/Vulkan only (Ryzen 5700U baseline).  

## Executive Overview

Xoe-NovAi is a sovereign, local-first RAG stack in Phase 6 release hardening (v0.1.7), focused on production readiness with BuildKit caches (xnai-uv), Butler orchestration, and multi-AI collaboration. Core mission: Democratize enterprise-grade AI with consciousness frameworks. Team: The User/Architect (Human Director), Cline (Local Development Specialist), Grok (Research Specialist), Gemini CLI (Real-time Assistance Specialist). Environment: Podman 5.x rootless containers, Codium IDE + Cline extension, Gemini CLI terminal assistance. Strategies: Iterative hardening, ethical AI (42 Laws of Ma'at + HITL), MCP integration with version pinning (mcp-sdk==2026.01.15-stable).

## Stack Details (Technical Architecture)

- **Core Services** (from docker-compose.yml):  
  - Redis: Cache/streams (7.4.1, maxmemory 512MB).  
  - RAG API: FastAPI backend (Dockerfile, LLM: smollm2-135m, FAISS hybrid RRF).  
  - Chainlit UI: Voice-enabled frontend (Dockerfile.chainlit, Piper TTS/Faster-Whisper STT).  
  - Curation/Crawl Workers: Ingestion pipelines (Dockerfiles for crawl/curation).  
  - Base Image: Python 3.12 slim with uv 0.5.21 (Dockerfile.base, BuildKit caches for apt/pip/uv).  

- **Infrastructure** (from techContext.md, systemPatterns.md):  
  - Podman 5.x rootless (pasta networking, MTU 1500; system service socket).  
  - Build Optimization: RUN --mount=type=cache,id=xnai-uv.  
  - Performance: OPENBLAS_CORETYPE=ZEN, N_THREADS=6, 400MB ZRAM rule.  
  - Patterns: AnyIO TaskGroups for concurrency, WASM plugins for isolation, SQLite WAL for persistence, RRF hybrid retrieval.  

- **Configuration** (from config.toml, .env):  
  - Sovereignty: telemetry_enabled=false, offline_mode=true.  
  - Voice: distil-large-v3-turbo STT, piper_onnx TTS.  
  - Security: API_KEY, CIRCUIT_BREAKER_ENABLED=true, JWT for MCP.  

- **Makefile & Scripts**: Build orchestration (make build), Butler CLI (scripts/infra/butler.sh for core steering, health monitoring).  

## Environment Details (Multi-AI Setup)

- **Primary**: Codium IDE + Cline extension (Claude API integration, MCP-enhanced).  
- **Target**: Xoe-NovAi Foundation Stack (Podman containers).  
- **Secondary**: Gemini CLI (terminal, MCP server with sovereignty validation per gemini.md).  
- **Relationships**: Shared memory_bank for coordination; Cline for local development, Grok.com for research.  

- **Team Structure** (from teamProtocols.md, agent_capabilities_summary.md):  