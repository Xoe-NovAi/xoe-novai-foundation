# Llama.cpp Python Optimization Guide (Ryzen 5700U)

**Status**: 🟢 ACTIVE | **Hardware**: AMD Ryzen 5700U (Zen 2)

---

## 🚀 Optimization Strategy

For the AMD Ryzen 5700U (8 Cores / 16 Threads), `llama-cpp-python` must be tuned to balance latency and throughput without causing thread contention or memory thrashing.

### 1. Threading Model
- **Physical Cores**: 8
- **Recommended Threads (`n_threads`)**: **6 to 8**.
- **Explanation**: Using all 16 logical threads often degrades performance due to context switching overhead. 6 threads leaves room for the OS and background services (Redis, Qdrant).

### 2. Memory Management (`mmap`)
- **Setting**: `use_mmap=True` (Default)
- **Benefit**: Allows the OS to manage model loading. The model is mapped into virtual memory, and pages are loaded on demand. This is crucial for the 5700U's shared RAM architecture.
- **`mlock`**: Avoid `use_mlock=True` unless you have dedicated RAM to spare (32GB+). It forces the entire model into RAM, which can trigger OOM kills if the system is under pressure.

### 3. Batching & Context
- **`n_batch`**: 512 (Default). Increasing to 1024 or 2048 helps prompt processing speed but increases peak RAM usage.
- **`n_ctx`**: 32768 (32k). Qwen-3 and Krikri models support long contexts. Ensure `n_batch` is sufficient to process prompt chunks efficiently.

### 4. GPU Offloading (Integrated Graphics)
- **Status**: **Disabled (`n_gpu_layers=0`)**.
- **Reason**: `llama-cpp-python`'s OpenBLAS backend is CPU-optimized. Vulkan/ROCm support for the 5700U's iGPU is experimental and often slower than the Zen 2 CPU cores for transformer inference.

---

## 🛠 Docker Configuration (Standard)

```yaml
  llama_server:
    image: ghcr.io/abetlen/llama-cpp-python:latest
    command: python3 -m llama_cpp.server --model /models/Qwen3-0.6B-Q6_K.gguf --n_gpu_layers 0 --n_threads 6 --n_ctx 32768 --host 0.0.0.0 --port 8000
    environment:
      - N_THREADS=6
    volumes:
      - ./models:/models:ro
```

---

## ⚠️ Troubleshooting

| Symptom | Cause | Fix |
| :--- | :--- | :--- |
| **High Latency** | Thread contention | Reduce `n_threads` to 4 or 6. |
| **System Freeze** | OOM / Swap Thrashing | Ensure `use_mlock=False`. Check total system RAM usage. |
| **Slow Prompt Eval** | Small batch size | Increase `n_batch` to 1024 (if RAM permits). |
