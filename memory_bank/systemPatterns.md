# System Patterns & Architecture Decisions

## Core Architecture: The Unified Entity
```mermaid
graph TD
    A[Xoe-NovAi Platform] --> B[RAG Engine]
    A --> C[Voice Interface]
    A --> D[Elite Documentation]

    B --> E[AnyIO TaskGroup Orchestration]
    B --> F[Hybrid RRF Standard (FAISS + BM25)]

    C --> G[Piper TTS (Emotional Target)]
    C --> H[Faster-Whisper (Zero-Copy IPC Target)]

    D --> I[Diátaxis Quadrants]
    D --> J[Hardware Mastery Manuals]
```

## Key Architectural Decisions

### Unified Entity Pattern (AnyIO)
**Decision**: Standardized on **AnyIO 4.x TaskGroups** for all concurrent services.
**Rationale**: Ensures atomic failure handling via `ExceptionGroup`. If the generation stream fails, sibling STT/TTS tasks are canceled, preventing "robotic" audio ghosting.

### Modular Plugin Ecosystem (WASM)
**Decision**: Transitioning from monolithic scripts to **WASM-isolated plugins**.
**Rationale**: Achieves <100ms load times with soft-isolation and fine-grained permissions, bridging the gap between scripts and full containers.

### Sovereign Data Architecture
**Decision**: All processing local, zero external calls.
**Rational**: Air-gapped reliability and user privacy (Ma'at Ideals 40, 41).

---

## ⚖️ Ethical Foundation (Ma'at Framework)
The Xoe-NovAi Foundation stack is governed by **The 42 Ideals of Ma'at**. All agents must consult `memory_bank/maatIdeals.md` before performing high-impact operations.

### Technical Mapping of Ideals
- **Integrity of Data (7, 36, 40):** Zero-telemetry, clean data ingestion, and RAG accuracy.
- **Resource Stewardship (10, 15, 39):** Optimized Ryzen performance, low RAM footprint, and humble hardware requirements.
- **Torch-free Capable (41):** The Foundation is **Torch-free by default** (GGUF, ONNX, CTranslate2) to shatter accessibility limits for mid-grade hardware. However, the stack is **Torch-capable**, allowing users to deploy optional GPU-accelerated modules as "Elite Extensions."


### Hybrid Retrieval (RRF Standard)
**Decision**: Combine Lexical (BM25) and Semantic (Dense) search.
**Pattern**: Reciprocal Rank Fusion (RRF) with $k=60$.
**Tie-Breaker**: Raw BM25 score as secondary sort key for technical accuracy.

---

## Advanced Technical Patterns

### Zero-Copy IPC Pattern
**Pattern**: Shared Memory (/dev/shm) for audio streams.
**Target**: Eliminate network bridge latency for sub-150ms voice responses.
**Cleanup**: Pre-start `rm -f /tmp/audio_pipe` routine to clear stale crash state.

### Persistence Model (SQLite WAL & MMAP)
**Pattern**: Memory-mapped persistence for near-zero I/O.
**Implementation**:
- `PRAGMA mmap_size = 256MB` for database address-space mapping.
- `PRAGMA wal_checkpoint(PASSIVE)` to prevent UI stalls during ingestion.

---

## Technical Implementation Patterns (Hardware Native)

### Vulkan GPU Acceleration
```mermaid
graph LR
    A[Matrix Warmup] --> B[Vulkan 1.4 Detection]
    B --> C[RADV_PERFTEST=gpl]
    C --> D[Scalar Block Layouts]
    D --> E[8-bit KV Cache]
    E --> F[70% VRAM Buffer Rule]
```

### Concurrency Guard (File Locking)
**Pattern**: Multi-process write protection.
**Implementation**: `fcntl.flock` exclusive locks on FAISS index operations to prevent segment violations during concurrent crawl/search.

---

## Quality Assurance & Evolution Patterns

### The Sovereign Governor
- **Thermal-Aware Audio**: Shift PipeWire quantum to 256 samples when CPU > 80°C.
- **Dynamic Precision**: Thermal-aware precision switching (Q8_0 to Q4_K_S).

### Testing Strategy
- **Benchmark-First**: Mandatory warmup matrix ($64 \times 64$) on startup.
- **Watchdog Logic**: Real-time 400MB soft-stop POST rejection middleware.

### 🏗️ Infrastructure Patterns

### 🧠 The Knowledge Runtime (Expert Knowledge Base)
The `expert-knowledge/` system is the shared "Long-Term Memory" for the Xoe-NovAi Foundation stack. 
- **Pattern**: **Graph-Markdown Hybrid**.
- **Implementation**: 
    - **Markdown + YAML**: Human-readable and RAG-optimized.
    - **Wikilinks (`[[link]]`)**: Bidirectional relationship mapping for AI reasoning.
- **Compatibility**: Designed to be managed via **Obsidian** or **Logseq** for human visualization and knowledge-graph discovery.
- **Strategic Utility**: A Dual-Purpose core feature. It serves the Xoe-NovAi Foundation stack natively but is architected to be a portable source of truth for external AI assistants.

### 🛡️ Sovereign Security Trinity Pattern
**Pattern**: **Waterfall of Proof (Inventory -> CVE -> Safety)**.
**Implementation**:
1.  **Syft**: Generates **CycloneDX JSON** SBOM (The Identity Document).
2.  **Grype**: Precision vulnerability scan of the SBOM (The Precision Auditor).
3.  **Trivy**: Safety scrub of raw image layers for secrets/misconfigs (The Safety Guardrail).
**Why**: Separates the "What is inside" from "What is wrong with it," ensuring an immutable audit trail for sovereignty.

### 📦 Bulletproof Tarball Scanning
**Pattern**: **Export-to-Scan**.
**Implementation**: `podman save -o image.tar [IMAGE]` followed by `trivy image --input image.tar`.
**Rationale**: Bypasses complex rootless Podman socket permission issues (`statfs` errors) by treating the image as a local file. Essential for cross-distro reliability in rootless mode.

### 🚦 Graduated Policy Gatekeeping
**Pattern**: **Config-Driven Enforcement**.
**Implementation**: `configs/security_policy.yaml` defines thresholds (e.g., `critical.max_exploitable: 0`).
**Rationale**: Moves security logic out of code and into declarative policy. Allows for nuanced rules (e.g., "Warn on High CVEs, Block on Criticals").

### 📦 Absolute Package Import Standard
**Decision**: Standardized on absolute imports starting from the `XNAi_rag_app` package root.
**Pattern**: `from XNAi_rag_app.core.circuit_breakers import ...` instead of `from circuit_breakers import ...`.
**Rationale**: Eliminates `ModuleNotFoundError` during container orchestration where the working directory might vary. Ensures all sub-modules are consistently resolvable as part of a unified package.

### 🚀 Consolidated Package Entrypoint Pattern
**Decision**: Standardized on `api/entrypoint.py` as the primary FastAPI engine and `ui/chainlit_app_voice.py` as the UI engine.
**Implementation**: 
- Docker CMD: `uvicorn XNAi_rag_app.api.entrypoint:app`
- PYTHONPATH: Standardized to `/app` (the parent of `XNAi_rag_app`).
**Rationale**: Provides a clear separation between API logic, UI frontend, and worker background tasks while maintaining a shared package root.

### ⚡ Unified BuildKit Pattern
Used for accelerating builds without external proxy infrastructure.
- **Pattern**: `RUN --mount=type=cache,id=xnai-...,uid=1001...`.
- **Why**: Provides "Elite" speed (2-4x cache hit) with zero config. Supports rootless Podman via explicit UID mapping.

### 📦 uv Standardization Pattern
Standardized package management for velocity and consistency.
- **Pattern**: `uv pip install --system`.
- **Why**: Replaces `pip` (slow) and `wheelhouse` (complex). `uv` is installed globally in `xnai-base`.

### 🛡️ Rootless Quadlet Standard
Standardized service definition for Podman 5.x.
- **Pattern**: `configs/quadlets/` -> `~/.config/containers/systemd/`.

### 🔧 Infrastructure Permission Pattern (Rootless :U Standard)
**Pattern**: **Automatic User Namespace (NS) Mapping via Compose**.
**Implementation**: Use the `:Z,U` volume flag suffix in `docker-compose.yml`.

### 📡 Observability Lifecycle Pattern
**Pattern**: Async Lifespan management for observability instrumentation.

*Updated by Gemini CLI (Security Hardening & Sovereign Trinity Pattern)*

## 🤖 AI Partnership with Claude (NEW)

**Current Collaboration:**
- **Hybrid Path Research Initiative**: Partnering with Claude to provide comprehensive stack-specific context for advanced refactoring guidance
- **10 Knowledge Gap Research**: Claude is conducting research on critical areas including BuildKit optimization, Security Trinity integration, Performance benchmarking, Memory Bank synchronization, and Ryzen core steering
- **Production-Grade Implementation Manual**: Target delivery of 50-60 page manual with code examples, configuration templates, and validation procedures

**Partnership Benefits:**
- **Stack-Specific Context**: Providing Claude with comprehensive Xoe-NovAi Foundation stack knowledge including Ma'at Guardrails, Sovereign Security Trinity, Memory Bank Protocol, and hardware optimization patterns
- **Enhanced Research Quality**: Ensuring research is 85-90% specific to Xoe-NovAi constraints rather than generic best practices
- **Production-Ready Deliverables**: Focus on immediately actionable guidance with copy-paste code examples and configuration templates

**Research Timeline:**
- **Day 1-3**: Parallel data gathering and research initiation
- **Day 3**: Checkpoint 1 - Data delivery and direction refinement
- **Day 6**: Checkpoint 2 - Mid-research status review
- **Day 9**: Checkpoint 3 - Draft manual review
- **Day 10**: Final delivery of implementation manual

**Integration with Refactoring:**
- Research findings will be integrated with the v0.1.0-alpha modular refactoring plan
- Focus on practical implementation patterns that align with Xoe-NovAi's sovereign, offline-first architecture
- Emphasis on production-grade solutions that maintain the stack's core principles
