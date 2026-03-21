# 🐍 Podman Python 3.12 Optimization Guide (XNAi Standard)
**Date**: Wednesday, March 18, 2026
**Target**: Ryzen 7 5700U (Zen2) | 16GB Total System RAM
**Objective**: Hardened, low-footprint Python 3.12 containers.

---

## 1. The XNAi Gold Standard: `python:3.12-slim`
We prioritize `3.12-slim` (Debian-based) over Alpine for better compatibility with C-extensions (llama-cpp, etc.) while maintaining a ~120MB image size.

---

## 2. Hardened Dockerfile Template
Use this pattern for all new microservices in the stack.

```dockerfile
# syntax=docker/dockerfile:1
# ----------------------------------------------------------------------------
# BUILD STAGE (The "Forge")
# ----------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /build

# 1. Install build-essential only in this stage
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ cmake pkg-config libgomp1

# 2. Use 'uv' for high-speed, deterministic installs
RUN pip install --no-cache-dir uv==0.5.21

COPY requirements.in .
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    uv pip install --system --no-cache -r requirements.in

# ----------------------------------------------------------------------------
# RUNTIME STAGE (The "Hearth")
# ----------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

# Security: Non-root user (UID 1000)
RUN groupadd -g 1000 appuser && useradd -m -u 1000 -g 1000 appuser

WORKDIR /app

# 3. Copy only the compiled site-packages from the builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 4. Copy app code
COPY . .

# 5. Runtime Hardening
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    OMP_NUM_THREADS=4

USER appuser
CMD ["python", "main.py"]
```

---

## 3. Optimization Techniques
- **BuildKit Cache Mounts**: Use `--mount=type=cache` for `apt` and `uv` to keep the final image clean of intermediate artifacts.
- **Stage Separation**: Never include `gcc` or `make` in the final `runtime` image. This reduces image size from ~450MB to ~140MB.
- **Ryzen 7 (Zen2) Tuning**:
  - `OMP_NUM_THREADS`: Set to `4` (half of physical cores) for optimal LLM throughput without choking the host.
  - `PYTHONDONTWRITEBYTECODE`: Prevents `.pyc` clutter in the container's writable layer.

---

## 4. Size-Hardening Checklist
- [x] Base image is `python:3.12-slim`.
- [x] `apt-get clean && rm -rf /var/lib/apt/lists/*` used in single `RUN` layers.
- [x] `.dockerignore` excludes `storage/`, `logs/`, and `.git`.
- [x] Multi-stage build (No build tools in production).
- [x] Non-root `appuser` (UID 1000) for host-parity.

# 5. Enterprise Runtime Hardening
To ensure service health is detectable by the Podman engine and to minimize layer bloat.

### **HEALTHCHECK Instruction**
Include this in every `Dockerfile` to integrate with the XNAi observability layer.
```dockerfile
# 6. Health Check (v0.1.4 Logic)
HEALTHCHECK --interval=30s --timeout=15s --start-period=60s --retries=3 \
  CMD python3 /app/XNAi_rag_app/healthcheck.py || exit 1
```

### **The Python .dockerignore (Optimized)**
Critical for preventing `__pycache__` version collisions (3.13 vs 3.12) and reducing build context size.
```text
# Exclude Python artifacts
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.venv/
venv/

# Exclude large data/logs
storage/
logs/
data/

# Exclude Git and IDE config
.git/
.vscode/
.gemini/sessions/
```

---
**Verdict**: Following this standard ensures high-performance, secure, and low-latency deployments across the XNAi mesh.
