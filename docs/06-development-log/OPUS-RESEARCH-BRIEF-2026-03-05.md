# Opus Research Brief: Deep Exploration Tasks for Agents

**Date**: 2026-03-05
**Author**: Opus (Antigravity Claude Opus 4.6)
**Purpose**: Research tasks for agents to execute for deeper insight and best practices
**Coordination Key**: `OMEGA-RESEARCH-V6-2026`

---

## How to Use This Document

Each research task below is self-contained and can be assigned to any Level 2 agent (OpenCode, Cline, Copilot). Tasks are ordered by priority. Each includes:
- **Objective**: What to investigate
- **Search Queries**: Specific terms to research
- **Expected Output**: What the agent should produce
- **Integration Point**: Where findings should be applied in the Omega Stack

---

## Research Task R1: whisper.cpp Vulkan Acceleration on AMD Ryzen 5700U

### Objective
Determine whether `whisper.cpp` can leverage the Vega 8 iGPU on the Ryzen 7 5700U via Vulkan compute for real-time speech-to-text. Benchmark CPU vs Vulkan performance on the `base.en` model.

### Search Areas
1. whisper.cpp Vulkan backend status (is it production-ready or experimental?)
2. AMD Vega 8 Vulkan compute support (compatible Vulkan extensions)
3. Real-time factor (RTF) benchmarks for whisper.cpp on similar AMD APUs
4. Memory requirements for the base.en model in Vulkan mode
5. Build flags required: `cmake -DWHISPER_VULKAN=ON`

### Expected Output
- A benchmark report comparing CPU (8 threads) vs Vulkan inference on a 30-second audio sample
- Build instructions for whisper.cpp with Vulkan on Ubuntu/Debian with Mesa drivers
- Recommended model size (tiny.en vs base.en vs small.en) for real-time factor < 1.0

### Integration Point
- `mcp-servers/xnai-whisper/` implementation
- `Makefile` target: `make whisper-build`

---

## Research Task R2: Piper TTS ONNX Performance and Voice Quality

### Objective
Evaluate Piper TTS voice quality and latency on the Ryzen 5700U. Identify the best English voices that balance quality and inference speed without PyTorch.

### Search Areas
1. Piper TTS available English voices and their quality ratings
2. ONNX Runtime CPU inference latency for medium vs high quality voices
3. Streaming synthesis (can Piper output audio chunks before full synthesis completes?)
4. Integration with the existing voice interface (`app/XNAi_rag_app/voice_interface.py`)
5. Voice cloning capabilities (custom voice training without PyTorch)

### Expected Output
- A ranked list of top 5 English voices with latency measurements
- Integration guide for adding Piper to the existing `VoiceConfig` system
- Streaming synthesis implementation notes (if supported)

### Integration Point
- `mcp-servers/xnai-piper/` implementation
- `app/XNAi_rag_app/voice_interface.py` enhancement

---

## Research Task R3: Redis Streams Exactly-Once Semantics Best Practices

### Objective
The current `AgentBusClient` uses `XREADGROUP` with manual `XACK` but does not implement exactly-once delivery. Research best practices for ensuring no duplicate task processing and no lost tasks.

### Search Areas
1. Redis Streams PEL (Pending Entries List) recovery patterns
2. `XAUTOCLAIM` vs manual `XCLAIM` for stale message recovery
3. Idempotency keys for task processing (how to detect re-delivered messages)
4. Consumer group rebalancing when agents crash
5. Dead-letter queue implementation with Redis Streams

### Expected Output
- A best-practice implementation guide for exactly-once semantics with Redis Streams
- Code snippets for PEL recovery, dead-letter queues, and idempotency keys
- Recommended configuration: `MAXLEN`, `BLOCK` timeout, `COUNT` per read

### Integration Point
- `app/XNAi_rag_app/core/agent_bus.py` hardening
- `scripts/metropolis-broker.py` reliability

---

## Research Task R4: MCP Server Performance Profiling

### Objective
The Omega Stack runs 7 MCP servers. Research best practices for MCP server performance, resource consumption, and lifecycle management.

### Search Areas
1. MCP server startup latency (cold start vs warm pool)
2. Connection pooling for MCP servers that use Redis/HTTP backends
3. MCP server health checking and auto-restart patterns
4. Memory footprint of FastMCP vs MCP SDK servers
5. MCP server lifecycle management (systemd units vs process supervisors)

### Expected Output
- Performance baseline for each of the 7 MCP servers (startup time, memory, latency per tool call)
- Recommendation: which servers should run as persistent daemons vs on-demand
- Systemd unit file templates for persistent MCP servers

### Integration Point
- `config/` directory (new MCP lifecycle config)
- `Makefile` targets: `make mcp-start`, `make mcp-stop`, `make mcp-status`

---

## Research Task R5: Qdrant Collection Management and Embedding Migration

### Objective
Research Qdrant best practices for collection versioning, alias swapping, and embedding model migration. The Omega Stack currently has no migration path when embedding models change.

### Search Areas
1. Qdrant collection aliases (create alias, swap alias atomically)
2. Qdrant snapshot/backup and restore procedures
3. Re-embedding strategies (batch re-embed with progress tracking)
4. Multi-tenancy patterns (domain-tagged payloads vs separate collections per domain)
5. Qdrant quantization options for reducing memory on the Ryzen 5700U

### Expected Output
- Migration script template: `scripts/qdrant-migrate-embeddings.py`
- Collection naming convention: `<base_name>_v<model_version>`
- Alias swap procedure with zero-downtime guarantee
- Recommendation on single-collection-with-domain-tags vs per-domain-collections

### Integration Point
- `mcp-servers/xnai-rag/` enhancement
- New `Makefile` target: `make rag-migrate-embeddings`

---

## Research Task R6: AnyIO Structured Concurrency Patterns for the Broker

### Objective
The broker currently uses a blocking `subprocess.run`. Research AnyIO's process execution capabilities and structured concurrency patterns for running multiple expert tasks concurrently.

### Search Areas
1. `anyio.run_process` API: capture stdout/stderr, timeout handling, cancellation
2. `anyio.CapacityLimiter` for bounding concurrent expert processes
3. Structured cancellation: what happens when the broker shuts down mid-task?
4. Process group management: can AnyIO manage process trees (parent + children)?
5. Comparison: `anyio.run_process` vs `anyio.open_process` for long-running tasks

### Expected Output
- Refactored `metropolis-broker.py` using `anyio.run_process` with capacity limiting
- Error handling patterns for subprocess failures (exit code, stderr capture, timeout)
- Graceful shutdown implementation using `anyio.open_signal_receiver`

### Integration Point
- `scripts/metropolis-broker.py` refactoring

---

## Research Task R7: Soul Evolution Engine Enhancement

### Objective
The soul evolution engine (`scripts/soul-evolution-engine.py`) shells out to the Gemini CLI for each audit. Research faster alternatives using local models (Level 3) or the SambaNova MCP server.

### Search Areas
1. Can the `xnai-sambanova` MCP server be invoked from Python without the CLI dispatcher?
2. Local model alternatives for text summarization/reflection (Qwen3-0.6B via llama.cpp server)
3. Structured output: can we get JSON-formatted audit results from the reflection models?
4. Batch reflection: reflecting on all 8 domains in parallel vs sequential
5. Quality metrics: how to measure whether a soul reflection actually improved the expert

### Expected Output
- Revised `soul-evolution-engine.py` that uses local models or SambaNova API directly (no subprocess)
- Quality metric: before/after comparison of expert soul document (character count, topic coverage, technical depth)
- Batch mode: reflect all 8 domains in < 60 seconds using parallel API calls

### Integration Point
- `scripts/soul-evolution-engine.py` rewrite
- `scripts/expert-soul-reflector.py` rewrite

---

## Research Task R8: Memory Bank Progressive Loading for Large Context Windows

### Objective
The `memory-bank-mcp` server implements progressive loading (Hot/Warm/Cold) but the tiers are based on static size thresholds. Research adaptive loading strategies that consider context window budget and query relevance.

### Search Areas
1. Context window budgeting: allocating tokens between system prompt, memory, and conversation
2. Relevance-based loading: using embedding similarity to load only relevant memory blocks
3. Summarization cascades: progressively summarizing memory as it ages
4. MemGPT-style virtual memory: paging memory blocks in and out during conversation
5. Cross-agent memory sharing: how should Domain 1 (Architect) access Domain 5 (Data) knowledge?

### Expected Output
- A design document for adaptive memory loading with token budgets
- Implementation guide for relevance-based block selection using Qdrant
- Cross-domain memory sharing protocol specification

### Integration Point
- `mcp-servers/memory-bank-mcp/server.py` enhancement
- `mcp-servers/xnai-memory/server.py` enhancement

---

## Research Task R9: Hardcoded Path Elimination Strategy

### Objective
Multiple scripts contain hardcoded paths to `/home/arcana-novai/`. Research and implement a portable path resolution strategy.

### Search Areas
1. XDG Base Directory specification compliance
2. `$HOME` vs `$(dirname "$0")` vs `${BASH_SOURCE[0]}` for script portability
3. Python `pathlib.Path` patterns for resolving project root
4. Environment variable cascade: `$XNAI_ROOT` -> `$PROJECT_ROOT` -> autodetect

### Expected Output
- A comprehensive list of all hardcoded paths in the codebase (grep for `/home/arcana-novai/`)
- Replacement strategy for each file (which pattern to use)
- A `scripts/portability-check.sh` script that validates no hardcoded paths remain

### Integration Point
- All files in `scripts/` directory
- `Makefile` target: `make portability-check`

---

## Research Task R10: Community MCP Server Ecosystem Assessment

### Objective
Survey the MCP server ecosystem for additional servers that could benefit the Omega Stack, focusing on Torch-free, local-first tools.

### Search Areas
1. Official Anthropic MCP servers (filesystem, git, databases)
2. Community MCP servers for: SQLite, Podman/Docker, system monitoring
3. MCP server for Prometheus/VictoriaMetrics (metrics query tool)
4. MCP server for Git operations (commit, diff, branch management)
5. MCP server aggregation/proxy patterns (single endpoint for multiple servers)

### Expected Output
- Ranked list of top 10 community MCP servers relevant to the Omega Stack
- Installation and configuration guide for top 3
- Assessment of each against sovereignty criteria (local-only, no telemetry, Torch-free)

### Integration Point
- `mcp-servers/` directory expansion
- `OMEGA_TOOLS.yaml` registry update

---

**Coordination Key**: `OMEGA-RESEARCH-V6-2026`
**Assignment**: Any Level 2 agent. Start with R1, R3, R6 (highest impact).
**Delivery**: Findings should be committed to `docs/05-research/` with date-prefixed filenames.
