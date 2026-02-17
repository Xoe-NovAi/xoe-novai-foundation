# syntax=docker/dockerfile:1
# ============================================================================ 
# Xoe-NovAi Phase 1 v0.1.7 - FastAPI RAG Service Dockerfile (BuildKit Optimized) 
# ============================================================================ 

FROM xnai-base:latest

LABEL maintainer="Xoe-NovAi Team"
LABEL version="0.1.7"
LABEL description="Xoe-NovAi RAG API Service - BuildKit Optimized"

WORKDIR /app

# Copy requirements for dependency resolution
COPY pyproject.toml .
COPY requirements-api.in .

# --- BUILD OPTIMIZATION: BuildKit Cache Mounts ---
# FIX: Use root (uid=0) for system-wide uv pip installs to allow hardlinking to the cache.
RUN echo "📦 Installing system-level dependencies..." && \
    uv pip install --system --verbose --upgrade pip "scikit-build-core>=0.9.2" && \
    uv pip install --system --verbose -r requirements-api.in

# Install llama-cpp-python with Vulkan/OpenBLAS support
# NOTE: This step can take a long time if building from source.
ENV CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS -DLLAMA_AVX2=ON -DLLAMA_FMA=ON -DLLAMA_F16C=ON -DLLAMA_VULKAN=ON" \
    FORCE_CMAKE=1
RUN echo "🔨 Building llama-cpp-python with Vulkan/OpenBLAS (this may take several minutes)..." && \
    uv pip install --system --verbose llama-cpp-python

# Copy application code
ENV CACHE_BUSTER=20260126_v2
COPY app/XNAi_rag_app /app/XNAi_rag_app

# Set up directories and permissions
RUN mkdir -p /app/logs /app/data/faiss_index /library /knowledge/curator && \
    chown -R appuser:appuser /app /library /knowledge && \
    chmod -R 1777 /app/logs /app/data /library /knowledge /app/data/faiss_index

# Optimization: Remove pycache
RUN find /usr/local/lib/python3.12/site-packages -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

# --- PRODUCTION ENVIRONMENT (RYZEN TUNED) ---
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    LLAMA_CPP_N_THREADS=6 \
    LLAMA_CPP_F16_KV=true \
    LLAMA_CPP_USE_MLOCK=true \
    LLAMA_CPP_USE_MMAP=true \
    OPENBLAS_NUM_THREADS=6 \
    OPENBLAS_CORETYPE=ZEN \
    OPENBLAS_VERBOSE=0 \
    OMP_NUM_THREADS=1

EXPOSE 8000 8002

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=15s --retries=10 --start-period=180s \
    CMD python3 /app/XNAi_rag_app/api/healthcheck.py || exit 1

CMD ["uvicorn", "XNAi_rag_app.api.entrypoint:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
