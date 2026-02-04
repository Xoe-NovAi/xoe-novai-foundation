
---
priority: high
context: general
activation: always
last_updated: 2026-01-27
version: 1.0
---

# Tech Stack and Patterns

**Core Constraints**:
- Torch-free everywhere (pure CPU/Vulkan, no PyTorch/Torch/Triton/CUDA/Sentence-Transformers).
- Python 3.12-slim base images.
- uv for dependency management (mirrors: https://pypi.mirrors.ustc.edu.cn/simple/ or http://pypi.sdutlinux.org/).
- Containerization: Rootless Podman, fuse-overlayfs, custom bridge networks.
- Installations: Never install wheels or dependencies outside Podman containers—always containerize to avoid local env pollution.

**Key Components**:
- Orchestration: LangChain (torch-free, hybrid BM25 + dense retrieval).
- Vector DB: FAISS primary (HNSW, memory-mapped); Qdrant ready (agentic filtering, <75ms latency).
- Models: Quantized GGUF format (no less than q4, no greater than q6), Vulkan acceleration (AWQ not used—GPU-only with immature CPU support).
- Voice: Piper ONNX TTS (Kokoro v2, multilingual), Faster-Whisper STT (distil-large-v3-turbo, CTranslate2).
- API/UI: FastAPI (circuit breakers, OpenTelemetry), Chainlit (voice-first, streaming).
- Concurrency: AnyIO (structured, zero-leak).
- Crawling: Craw4AI (JS rendering, anti-detection).
- Observability: OpenTelemetry GenAI, pycircuitbreaker, Redis (async fault-tolerant), Prometheus (metrics collection), Grafana (dashboards/visualization).
- Infra: uv builds, Podman/BuildKit optimization, WASM plugins, ONNX Runtime.
- MkDocs: Torch-free enterprise platform (Material theme, plugins: gen-files, literate-nav, section-index, glightbox, minify, redirects). Diátaxis nav, strict mode, containerized with non-root user.

Preferred Dockerfile:
```dockerfile
FROM python:3.12-slim
RUN useradd -m -u 1001 appuser
USER appuser
WORKDIR /app
