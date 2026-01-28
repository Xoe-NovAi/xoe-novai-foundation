# Sovereign Entity Architecture: The Unified Logic
**Status**: Elite Hardened (Phase 6 Era)
**Philosophy**: Ma'at Principles (Truth, Justice, Balance, Harmony)

## 1. Concurrency Model: Structured Orchestration
Xoe-NovAi utilizes **AnyIO 4.x TaskGroups** to manage its high-concurrency voice, RAG, and generation pipelines. This architecture ensures that the system behaves as a single, coordinated entity rather than a collection of loosely coupled scripts.

### 1.1 ExceptionGroup Handling
- **Resilience**: The system uses the `except*` syntax to handle concurrent failures. If a non-critical component (e.g., Audio Visualization) fails, the core generation pipeline remains active.
- **Cancellation**: TaskGroups ensure that if a mandatory task (e.g., the LLM Stream) fails, all sibling tasks (STT/TTS) are canceled immediately to prevent resource leaks and "robotic" audio ghosting.

### 1.2 Zero-Copy IPC & SHM
- **Shared Memory**: High-frequency audio streams are moved through `/dev/shm` (shared memory) to achieve sub-150ms voice-to-voice response times.
- **Socket Cleanup SOP**: To prevent connection stalls, the service pre-start routine MUST execute `rm -f /tmp/audio_pipe` to clear stale crash state.

---

## 2. Persistence Model: SQLite WAL & MMAP
Identity, metadata, and small-form knowledge are managed via **SQLite** tuned for NVMe performance.

### 2.1 The Elite Persistence Standard
- **WAL Mode**: Write-Ahead Logging allows for concurrent reads during heavy ingestion cycles without locking the UI.
- **MMAP Acceleration**: Set `PRAGMA mmap_size = 268435456` (256MB) to keep the database in the system's address space, reducing I/O latency to near-zero.
- **Passive Checkpointing**: The system uses `PRAGMA wal_checkpoint(PASSIVE)` to merge logs without blocking active user queries.

---

## 3. Modular Plugin Ecosystem (WASM)
Xoe-NovAi is transitioning from a monolithic script architecture to a **WASM-isolated Plugin System**.

### 3.1 Soft-Isolation Architecture
- **Performance**: Utility plugins (e.g., Metadata Extractors) run in a WASM runtime, providing <100ms load times vs. the <500ms overhead of full containerization.
- **Fine-Grained Permissions**: Plugins are granted explicit access to specific host paths or network domains, following the Zero-Trust security model.

### 3.2 Hardware-Native Offloading
- **iGPU Control**: The plugin framework allows for specific offloading of transformer layers to the Vulkan iGPU (Vega 8) based on current thermal headroom.

---

## 4. Sovereignty & Namespace Security
All components run in **Rootless Podman** namespaces, ensuring complete isolation from the host system.

### 4.1 UID Mapping (1001:1001)
- **Standard**: All data directories (`/library`, `/knowledge`, `/data`) are owned by internal UID `1001` (appuser).
- **The Unshare SOP**: Use `podman unshare chown -R 1001:1001 <path>` for all host-side volume preparations.

### 4.2 The "Double-Z" Volume Policy
- **Shared Path (:z)**: Use lowercase `:z` for directories accessed by multiple containers (e.g., the FAISS index).
- **Private Path (:Z)**: Use uppercase `:Z` for service-specific paths (e.g., service-specific logs or tmpfs mounts) to prevent inter-service lockout.

---

## 5. Retrieval Standard: Hybrid RRF
The "Truth" layer relies on a dual-engine retrieval system optimized for 91% accuracy.

- **The Gold Standard**: FAISS (Dense) + Neural BM25 (Lexical) fused via **Reciprocal Rank Fusion (k=60)**.
- **Tie-Breaking Logic**: In the event of RRF score collisions, the raw BM25 score is used as the secondary sort key to prioritize exact technical documentation matches.
- **Concurrency Guard**: All index read/write operations use `fcntl.flock` to prevent Segment Violations during parallel ingestion and search.