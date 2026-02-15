Here is the revised **Xoe-NovAi Research Plan (v2)**, adjusted to prioritize a robust FAISS implementation while maintaining the high-performance goals for Vulkan and Voice.

This plan removes the Qdrant migration path and replaces it with **Unit 3: Advanced FAISS Architecture**, focusing on squeezing maximum performance and recall from your existing torch-free vector store.

------

### **Research Unit 1: Vulkan-Native Inference (The Compute Layer)**

Objective: Eliminate CPU bottlenecks by offloading inference to the iGPU via Vulkan, strictly maintaining the "Torch-Free" architecture.

Priority: Critical (22.3% Integration Score)

- **Research Task 1.1: Driver & Firmware Validation**
  - **Goal:** Ensure the container can communicate with the hardware via Mesa 25.3+.
  - **Experiment:** Verify RADV driver initialization within the Debian-based Docker container and validate AGESA 1.2.0.8+ detection logic (critical for Ryzen iGPU stability).
  - **Deliverable:** `setup_vulkan_drivers.sh` script for container initialization.
- **Research Task 1.2: Llama.cpp Vulkan Backend**
  - **Goal:** Enable hardware acceleration for the LLM.
  - **Experiment:** Recompile `llama-cpp-python` with `-DGGML_VULKAN=1` in `Dockerfile.api`. Benchmark GGUF Q5_K_M performance (tok/s) on Vega 8 iGPU vs. Ryzen CPU.
  - **Deliverable:** Optimized `Dockerfile.api` with Vulkan build args.
- **Research Task 1.3: Memory Pinning (mlock)**
  - **Goal:** Prevent swapping during tensor offloading.
  - **Experiment:** Implement `mlock` natively to guarantee RAM residency for the active model, ensuring the `<6GB` memory target is met.
  - **Deliverable:** `memory_manager.py` utility for strict memory enforcement.

------

### **Research Unit 2: Kokoro v2 Voice Synthesis (The Interface Layer)**

Objective: Upgrade the voice interface to "1.8x naturalness" using Kokoro v2, while remaining Torch-free.

Priority: High (32.4% Integration Score)

- **Research Task 2.1: ONNX Export & Runtime**
  - **Goal:** Run Kokoro v2 without PyTorch.
  - **Experiment:** Create/Validate an ONNX export of the Kokoro v2 model (~80MB). Implement an `onnxruntime` inference loop in Python to replace the current Piper implementation.
  - **Deliverable:** Standalone, Torch-free `KokoroTTS` class in `voice_interface.py`.
- **Research Task 2.2: Phonemizer Integration**
  - **Goal:** Handle text preprocessing for the new model.
  - **Experiment:** Integrate a lightweight phonemizer (compatible with Kokoro's tokens) into the Docker build without adding bloat.
  - **Deliverable:** `text_processing.py` module for phoneme conversion.
- **Research Task 2.3: Latency Benchmarking**
  - **Goal:** Ensure voice generation stays under 500ms.
  - **Experiment:** Benchmark "Time to First Audio Byte" (TTFB) on Ryzen CPU. Determine if int8 quantization is required for real-time performance.
  - **Deliverable:** Optimization report and configuration.

------

### **Research Unit 3: Advanced FAISS Architecture (The Knowledge Layer)**

Objective: Maximize recall and performance of the existing FAISS stack without adding new database services.

Priority: High (Focus Area: Solid Foundation)

- **Research Task 3.1: Hybrid Search (Dense + Sparse)**
  - **Goal:** Improve retrieval accuracy for technical queries (keyword matching).
  - **Experiment:** Integrate `rank_bm25` (sparse retrieval) alongside FAISS (dense retrieval) and implement Reciprocal Rank Fusion (RRF) to merge results.
  - **Deliverable:** `HybridRetriever` class in `main.py` that combines keyword and semantic search.
- **Research Task 3.2: FAISS Hyperparameter Auto-Tuning**
  - **Goal:** Optimize trade-off between speed and accuracy.
  - **Experiment:** Create a script that dynamically adjusts `nprobe` (number of clusters to search) based on dataset size and available CPU time, utilizing the `faiss_optimizer.py` logic.
  - **Deliverable:** `optimize_index()` function that auto-configures the index at startup.
- **Research Task 3.3: IVF Index Optimization & Persistence**
  - **Goal:** Efficiently handle larger datasets within memory limits.
  - **Experiment:** Implement `IndexIVFFlat` (clustering) to replace `IndexFlatL2` (brute force) for datasets >10k vectors. Implement robust serialization to disk to speed up restart times.
  - **Deliverable:** Updated `vectorstore` dependency with IVF support and safe disk persistence.

------

### **Research Unit 4: System Resilience & Extensibility (The Architecture Layer)**

Objective: Harden the system against failures and allow safe extensibility.

Priority: Medium

- **Research Task 4.1: WASM Plugin Sandbox**
  - **Goal:** Allow safe extension of the AI's capabilities.
  - **Experiment:** Integrate `wasmtime-py` to run untrusted code (plugins) for text transformation or simple logic, isolating them from the core RAG stack.
  - **Deliverable:** `PluginManager` class for executing `.wasm` modules.
- **Research Task 4.2: Predictive Circuit Breaking**
  - **Goal:** Prevent system crashes before they happen.
  - **Experiment:** Connect `pybreaker` to Prometheus metrics. Trigger an "Open" state based on pre-failure signals (e.g., rising latency trend, high memory pressure) rather than just error counts.
  - **Deliverable:** `PredictiveBreaker` class extending the current circuit breaker implementation.

------

### **Research Unit 5: Blue Sky Paradigms (Future Horizons)**

Objective: Theoretical exploration of cutting-edge efficiency techniques.

Priority: Low (Long-term)

- **Research Task 5.1: Neural Compilation Feasibility**
  - **Goal:** Explore compiling models directly to hardware instructions.
  - **Experiment:** Literature review on inference-only compilation techniques compatible with CPU/Vulkan (e.g., TVM, IREE) to see if they offer benefits over the current GGUF/Llama.cpp approach.
  - **Deliverable:** Feasibility Report.

------

### **Immediate Next Step:**

Since the foundation of your high-performance stack relies on the **Compute Layer**, I recommend starting with **Research Task 1.2 (Llama.cpp Vulkan Backend)**.

Would you like me to generate the **Docker build configuration** (`CMAKE_ARGS` and dependencies) required to enable Vulkan support in `llama-cpp-python`?