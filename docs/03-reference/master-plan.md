# Xoe-NovAi Master Plan: Remediation & Observability
**Date**: 2026-01-27
**Version**: 1.0 (Consolidated)
**Project Target**: 8GB RAM / Ryzen 5700U / Vulkan 1.4
**AI Team**: Cline (Implementation), Nova (Research), Gemini (Architecture)

---

## 1. Infrastructure & Namespace Security
**Goal**: Resolve rootless Podman permission collisions and maximize I/O performance.

### 1.1 Rootless UID Mapping (The "Unshare" Rule)
- **Standard**: Standard `chown` fails in rootless mode because host UID 1001 maps to a high-range subordinate UID (e.g., 101000).
- **Strategy**: Use `podman unshare chown -R 1001:1001 <path>` in all bootstrap scripts.
- **Volume Policy**: Append `:Z` to all volume strings in `podman-compose.yml` for automatic SELinux and permission labeling.

### 1.2 Networking Efficiency
- **Standard**: Podman 5.x `pasta` driver.
- **Optimization**: Implement **Socket Activation** for the RAG API to bypass bridge overhead, achieving 94%+ native throughput for high-concurrency voice streams.

---

## 2. Data Persistence & Retrieval Mastery
**Goal**: Achieve 91% search accuracy with zero-loss data durability.

### 2.1 SQLite "Elite" Persistence
- **Implementation**: Replace in-memory mocks with **SQLite (WAL Mode)** via `sqlite-utils`.
- **Performance Tweaks**: 
    - Set `PRAGMA mmap_size = 268435456` (256MB) to keep indexes in address space.
    - Set `PRAGMA synchronous = NORMAL` for NVMe-optimized durability.
- **Edge Case**: WAL file bloat. 
- **Remediation**: Cline must implement a background thread calling `PRAGMA wal_checkpoint(PASSIVE)` every 5 minutes.

### 2.2 Hybrid Retrieval (RRF Standard)
- **Standard**: Reciprocal Rank Fusion (RRF) with $k=60$.
- **Refinement**: Implement **Alpha-Weighting** (prefer Dense for creative intent, Lexical for technical intent).
- **Tie-Breaking**: Use raw BM25 scores as a secondary sort key to resolve RRF collisions.

---

## 3. Hardware-Native Optimization (Ryzen 5700U)
**Goal**: Maximize the 25W TDP envelope and 8GB RAM constraint.

### 3.1 CPU & Memory Orchestration
- **EPP Tuning**: Set `energy_performance_preference` to `performance` during active inference.
- **Core Masking**: 
    - **Cores 0-5**: LLM Generation (Matrix math heavy).
    - **Cores 6-7**: UI, STT, and TTS (Latency sensitive).
- **ZRAM Configuration**: Force `vm.swappiness=180` and `vm.page-cluster=0` to ensure the 8GB RAM prefers compressed ZRAM over NVMe swap.

### 3.2 Vulkan 1.4 / Mesa 25.3 Acceleration
- **Target Extensions**: Enable **Scalar Block Layouts** and **Push Descriptors** to reduce memory bandwidth overhead.
- **Shader Strategy**: Enable `RADV_PERFTEST=gpl` (Graphics Pipeline Library) to eliminate stutter during the first voice interaction.
- **VRAM Budgeting**: Reserve 20% of VRAM for implicit RADV resources to prevent allocation failures.

---

## 4. Observability & Diagnosis Strategy
**Goal**: Reduce Mean-Time-To-Diagnosis (MTTD) to under 30 seconds.

### 4.1 Unified Observability (OTel + Structlog)
- **Logging**: Standardize on `structlog` with **Contextual Enrichment** (injecting `request_id`, `hardware_mode`, and `memory_pressure` into every JSON entry).
- **Tracing**: Pass `TraceID` across all internal service boundaries (even in local mode) to link the Voice UI to specific FAISS/LLM spans.
- **Metrics (Golden Signals)**:
    - **TTFT**: Time to First Token (Target <200ms).
    - **Token Flux**: Generation rate relative to CPU thermal throttling.
    - **ZRAM Ratio**: Monitor compression ratio; alert if < 2.0.

### 4.2 Error Handling Hierarchy
- **Ma'at Exception Categories**:
    - **Transient**: (Network/Redis) -> Auto-retry with backoff.
    - **Resource**: (VRAM/OOM) -> Trigger **Dynamic Precision Shift** (FP16 -> INT8).
    - **Fatal**: (SQLite Corruption) -> Emergency stop and vault recovery.
- **AnyIO Pattern**: Mastery of `ExceptionGroup` via `except*` syntax to handle concurrent pipeline failures.

---

## 5. Cline Implementation Roadmap (SOP)

| Phase | Task | Cline Instruction |
| :--- | :--- | :--- |
| **Phase 1** | FS & UID | "Cline: Update `setup_permissions.sh` to use the `podman unshare` pattern for 1001:1001 mapping." |
| **Phase 2** | SQLite WAL | "Cline: Implement the `PersistentIAM` class using `sqlite-utils` with WAL and 256MB MMAP." |
| **Phase 3** | Hybrid RRF | "Cline: Integrate RRF (k=60) with BM25 tie-breaking into the `query` endpoint." |
| **Phase 4** | OTel Layers | "Cline: Implement `structlog` contextual processors and OTel TTFT metrics." |
| **Phase 5** | Core Pinning | "Cline: Implement CPU affinity logic in `dependencies.py` to isolate generation from interface cores." |

---
**Signed**: Gemini CLI (Audit & Research Lead)
**Authorized By**: Ma'at Principles ⚖️
**Status**: MASTER PLAN FINALIZED 🚀🤖💫
