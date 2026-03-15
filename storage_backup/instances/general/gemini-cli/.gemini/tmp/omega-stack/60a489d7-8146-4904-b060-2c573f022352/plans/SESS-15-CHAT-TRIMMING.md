# 🔱 Implementation Plan: SESS-15 Chat Trimming & Recursive State Management

**Objective**: Architect a frontier-grade session-state management protocol for the Omega Stack. This system (codenamed "The Librarian") will maximize **Resource Sovereignty** (local context optimization) and **Information Persistence** (long-term session memory) through asynchronous, recursive summarization and deep state observability, fully integrated with the **MemGPT-style hierarchical memory architecture**.

---

## 📍 1. Local Inference Optimization: The "Squeeze"
**Goal**: Push `n_ctx` limits from 2048 to 8192+ within the 6.6GB RAM budget.

### 📚 Prerequisite Research
- [ ] **Llama.cpp Bit-Quantization**: Research `q4_0` and `q8_0` KV cache quantization impacts on Qwen 0.5B and Llama 8B. Analyze RAM vs. Perplexity trade-offs.
- [ ] **Vulkan/UMA Memory Tuning**: Investigate `GGML_VULKAN_MAX_ALLOCATION` for the Ryzen 7 5700U (Zen 2) architecture.
- [ ] **Zen 2 Thread-Pinning**: Study CCX (Core Complex) boundaries on the 5700U to optimize `LLAMA_CPP_N_THREADS` and avoid SMT thrashing.
- [ ] **Flash Attention (CPU/Vulkan)**: Research support and performance gains for small-context models.

### 🛠️ Execution Skeleton
- [ ] **Task**: Implement a benchmark suite for Qwen 0.5B measuring `RSS`, `TTFT`, and `TPS` at `n_ctx` steps: 2048, 4096, 8192, 16384.
- [ ] **Task**: Configure `LLAMA_CPP_N_THREADS` and `taskset` to pin inference to physical cores.
- [ ] **Deliverable**: A documented Matrix of `n_ctx` vs. `RAM` vs. `Quantization`.

---

## 📍 2. "The Librarian": Asynchronous State Worker
**Goal**: Manage session bloat and persistence via an offline mesh service, acting as the active agent for the **MemGPT-style memory hierarchy**.

### 📚 Prerequisite Research
- [ ] **MemGPT Tier Integration**: Study the transition between **Core Memory** (Active Context), **Recall Tier** (Searchable History), and **Archival Tier** (Long-term Knowledge) as defined in `memory_bank/INDEX.md`.
- [ ] **Automated Curation Pipeline Integration**: Study `AutomatedCurationPipeline` (in `scripts/automated_curation_pipeline.py`) as a template for the Librarian's background loop.
- [ ] **State Serialization Formats**: Compare `YAML` vs. `JSON` for model "parseability" of complex state anchors (File paths, Git hashes, CLI outputs).
- [ ] **Zstd-Stream Archival**: Research `zstd` compression ratios and CPU impact for real-time session log archival.

### 🛠️ Execution Skeleton
- [ ] **Task**: Implement `librarian.py` as a Redis Stream listener, modeled after the `curation_worker.py`.
- [ ] **Task**: Develop the "State-of-Play" recursive summarization prompt (YAML structured), aligning with the **Curation & Knowledge Management Memory Bank** ontology.
- [ ] **Task**: Implement differential snapshots and `zstd` archival in `memory_bank/recall/conversations/` and `memory_bank/archival/research/`.
- [ ] **Deliverable**: A robust background worker for automated session trimming, summarization, and hierarchical archival.

---

## 📍 3. Recursive Observability: Entropy & Health
**Goal**: Measure information loss and system health through deep instrumentation.

### 📚 Prerequisite Research
- [ ] **Information Density & Entropy**: Research metrics to measure the "semantic gap" between raw history and summarized seeds.
- [ ] **Prometheus Gauge Standards**: Study how to track "KV Cache Saturation" and "Resident Memory Drift" effectively.
- [ ] **Jaeger OTLP Tracing**: Research linking parent session traces to asynchronous Librarian sub-traces.

### 🛠️ Execution Skeleton
- [ ] **Task**: Add `xnai_state_entropy_score` and `xnai_history_serialization_time_ms` to `metrics.py`.
- [ ] **Task**: Hook the Librarian's loop into Jaeger (OTLP) for visual debugging.
- [ ] **Task**: Create a "Session Health" Grafana dashboard.

---

## 📍 4. Integration & CLI/UI Tooling
**Goal**: Make the Librarian accessible and seamless across all interfaces.

### 📚 Prerequisite Research
- [ ] **Chainlit Hydration Hooks**: Study `chainlit_app_unified.py` and `chainlit_curator_interface.py` for history injection points.
- [ ] **fzf Python Integration**: Research using `fzf` for interactive terminal history searching.

### 🛠️ Execution Skeleton
- [ ] **Tooling**: Add `/checkpoint`, `/rehydrate <session_id>`, and `/summarize` commands to the CLI.
- [ ] **UI Task**: Update Chainlit to support `Librarian Summary + N Recent Turns` (Hybrid Context).
- [ ] **Task**: Integrate `fzf` for rapid searching of Librarian archives.

---

## 📍 5. Refactoring & Alignment (Attention Required)
**Goal**: Align existing library and curation components with the new "Librarian" state protocol.

### 🔧 Curation Bridge Refactor
- [ ] **Issue**: `curation_bridge.py` uses hardcoded defaults for Vikunja/API settings.
- [ ] **Task**: Refactor to use `config.toml` and the central `load_config()` utility.
- [ ] **Alignment**: Ensure curation tasks are enqueued with the same metadata schema used by the Librarian.

### 🔧 Library Ingestion Hardening
- [ ] **Issue**: `offline_library_manager.py` manually pushes to `curation_queue`.
- [ ] **Task**: Refactor to use the Librarian's unified state-serialization engine to ensure consistency between "Knowledge Curation" and "Session Curation."

### 🔧 Vector Search Optimization
- [ ] **Issue**: Current retrieval uses a flat `top_k` approach.
- [ ] **Task**: Implement **Tiered Retrieval** from `qdrant-query-strategy.md` (Vector $\rightarrow$ Reciprocal Rank Fusion $\rightarrow$ Rerank).

---

## 📍 6. Verification & Stress Testing
### 📚 Prerequisite Research
- [ ] **Small-Model Context Limits**: Research "Needle-in-a-Haystack" behavior for 0.5B-3B models at 8k+ context.
- [ ] **Automated Marathon Testing**: Study scripts for long-running, multi-turn LLM session simulation.

### 🛠️ Execution Skeleton
- [ ] **Task**: Run a 1000+ turn "Marathon Session" script and verify zero OOMs and >90% "Context Anchor" retention.
- [ ] **Verification**: Validate the Librarian's summary against raw history using a secondary "Verifier" model pass.
