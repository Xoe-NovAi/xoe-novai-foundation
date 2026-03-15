# 🎯 SESS-16 Strategy: Multi-Stage Image Optimization

**Objective**: Reduce the Xoe-NovAi container footprint by 1.6GB+ through multi-stage refactoring and dependency pruning.

---

## 🏗️ 1. Architecture: The Tiered Base Image
Instead of a single "everything" base image, we split into three distinct layers:

1.  **`xnai-build-base`**:
    - Based on `python:3.12-slim`.
    - Contains: `build-essential`, `cmake`, `pkg-config`, `libopenblas-dev`, `git`.
    - Purpose: Compiling heavy C++ extensions (llama-cpp, fast-text).
2.  **`xnai-runtime-base`**:
    - Based on `python:3.12-slim`.
    - Contains: `libopenblas0`, `libgomp1`, `ca-certificates`, `curl` (for healthchecks).
    - **Removed**: `build-essential`, `cmake`, `git`, `pkg-config` (Saves ~450MB).
3.  **`xnai-final` (Service Specific)**:
    - Inherits from `xnai-runtime-base`.
    - Copies ONLY the application code and the compiled `site-packages` from the builder stage.

---

## 🛠️ 2. Pruning Strategy

### Python Dependency Audit
- **`torch`**: Ensure it's not present in the RAG or Crawler images unless specifically required.
- **`nvidia-*`**: Strip all CUDA-specific libraries from CPU-only (Zen 2) images.
- **Compiled Assets**: Move all GGUF models out of the image and into persistent volumes (already partially implemented).

### Layer Compression
- Combine `apt-get install` and `apt-get clean` into a single `RUN` layer.
- Use `.dockerignore` aggressively to prevent copying `.git`, `.venv`, and `tests/` into the production runtime.

---

## 📈 3. Targeted Reductions

| Service | Current (Est) | Target | Savings |
|:---|:---|:---|:---|
| `xnai-rag` | 2.8GB | 1.2GB | 1.6GB |
| `xnai-crawler` | 1.5GB | 800MB | 700MB |
| `xnai-base` | 1.2GB | 400MB | 800MB |

---

## 🚀 4. Implementation Steps
1.  **Refactor `Dockerfile.base`**: Create the tiered build/runtime split.
2.  **Service Migration**: Update `infra/docker/Dockerfile` to use the new multi-stage pattern.
3.  **Validation**: Verify that the RAG service still functions correctly with the slimmed-down runtime libs.
