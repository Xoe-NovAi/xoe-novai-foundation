# Engineering Deep Dive: The uv Standardization & Build System Consolidation
**Date**: January 27, 2026
**Author**: Gemini CLI
**Status**: Active Standard

## 1. The Challenge: Tooling Fragmentation
Historically, Xoe-NovAi's build system suffered from fragmentation:
*   **Mixed Package Managers**: Some services used `pip` (slow), others `uv` (fast).
*   **Duplicate Orchestration**: `podman-compose.yml` and `docker-compose.yml` were identical but drifted over time.
*   **Sovereignty Risks**: Hardcoded mirrors (e.g., Tsinghua) in `Dockerfile.base` threatened global portability.

## 2. The Solution: Unified Velocity

### 2.1. The `uv` Standard
We have standardized on **`uv` (v0.5.21)** as the sole package manager for all Python services.
*   **Implementation**: `uv` is installed *once* in `Dockerfile.base` via `pip install uv==0.5.21`.
*   **Inheritance**: All downstream services (`rag`, `chainlit`, `crawl`, etc.) inherit this binary.
*   **Usage**: `RUN ... uv pip install --system -r requirements.txt`.
*   **Benefits**:
    *   **Speed**: 10-100x faster dependency resolution than pip.
    *   **Caching**: Unified `xnai-uv-cache` BuildKit mount.
    *   **Simplicity**: No need for virtualenvs inside containers (`--system` flag).

### 2.2. BuildKit Cache Architecture
We leverage rootless-compatible BuildKit cache mounts to achieve "Elite" build speeds without external proxies.

**The Syntax**:
```dockerfile
RUN --mount=type=cache,id=xnai-pip-cache,target=/root/.cache/pip,uid=1001,gid=1001 \
    --mount=type=cache,id=xnai-uv-cache,target=/root/.cache/uv,uid=1001,gid=1001 \
    uv pip install --system ...
```

**Key Constraints**:
*   **UID/GID**: Must match the runtime user (1001) to prevent permission denied errors in rootless Podman.
*   **No `sharing=locked`**: Avoided to maintain compatibility with Podman 5.x's overlay driver limitations.

### 2.3. Orchestration Consolidation
*   **Decision**: `podman-compose.yml` was deleted.
*   **Source of Truth**: `docker-compose.yml` is the single source of truth.
*   **Compatibility**: `podman-compose` natively supports `docker-compose.yml` syntax (v3+).
*   **Impact**: Eliminates configuration drift and simplifies `Makefile` logic.

## 3. Migration Guide for New Services
When adding a new service:
1.  **Inherit**: `FROM xnai-base:latest`.
2.  **Mount**: Copy the standard `RUN --mount...` block from existing Dockerfiles.
3.  **Install**: Use `uv pip install --system`.
4.  **User**: Switch to `USER appuser` (1001) at the end.

## 4. Sovereignty & Mirrors
*   **Policy**: Do NOT hardcode regional mirrors (China/Europe) in the base image.
*   **Reason**: Violates "Global Portability".
*   **Mechanism**: Rely on standard PyPI. If a mirror is needed, pass it via `ARG PIP_INDEX_URL` at build time, but defaults must remain upstream.

---
**References**:
*   `expert-knowledge/coder/buildkit_best_practices.md`
*   `memory_bank/techContext.md`
