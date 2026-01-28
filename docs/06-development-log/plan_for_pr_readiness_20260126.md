# Plan for PR Readiness - January 27, 2026

**Status**: Active
**Phase**: RAG API & Service Stability Improvement

## Objective

To resolve critical runtime blockers (RAG API observability, service hangs) and address build warnings (`uv` hardlinking, missing dependency) to achieve PR readiness for the Xoe-NovAi Foundation Stack.

## Current Understanding & Issues

*   **RAG API Observability Failure**: Persistent import errors due to deprecated Jaeger dependencies. Plan to rewrite using `ConsoleSpanExporter` and FastAPI lifespan exists but requires successful implementation.
*   **Service Hangs**:
    *   **Curation Worker**: Starts but hangs, potentially due to Redis connection timeouts or resource contention.
    *   **Crawler**: Hangs, possibly related to rootless Podman permissions or runtime issues with `playwright`/`crawl4ai`.
*   **Build Warnings**: `build_full.log` shows `uv` hardlinking failures, indicating potential performance or caching issues.
*   **Dependency Management:**
    *   `opentelemetry-exporter-prometheus` is noted as missing in `.txt` requirements but present in `.in` files.
    *   `sentence-transformers` is listed in `pyproject.toml` and violates the "Torch-free" guardrail (explicitly excludes `sentence-transformers`).
*   **Project Context**: Emphasizes Sovereignty, Local-First, Torch-free architecture, and Ma'at principles. BuildKit optimizations and rootless Podman are active.

## Proposed Plan of Action

### Phase 1: Resolve RAG API Observability Blocker (High Priority)
1.  **Implement Rewrite**: Execute the plan from `docs/06-development-log/final_observability_implementation_plan.md`. Focus on rewriting `app/XNAi_rag_app/observability.py` using `ConsoleSpanExporter` and integrating with FastAPI's lifespan, ensuring Ma'at compliance.
2.  **Test RAG API**: Verify successful startup and basic functionality after the rewrite.

### Phase 2: Debug Service Hangs
1.  **Curation Worker Hang**:
    *   Analyze Redis connection logs and resource usage (ZRAM/CPU).
    *   Investigate potential deadlocks or timeouts.
2.  **Crawler Hang**:
    *   Review rootless Podman permissions for `/app/logs`, `/app/.crawl4ai`, and host directories.
    *   Examine Playwright and `crawl4ai` runtime behavior in rootless containers.

### Phase 3: Address Build & Dependency Issues
1.  **Dependency Management**:
    *   Ensure `opentelemetry-exporter-prometheus` is correctly included in all relevant requirements files (`.txt`).
    *   **`sentence-transformers` Guardrail Conflict**:
        *   Audit codebase for all uses of `sentence-transformers`.
        *   Analyze its dependencies. If `torch`-dependent, research and propose `torch`-free alternatives for embedding generation (e.g., ONNX, GGUF models, CTranslate2).
2.  **`uv` Hardlinking Warnings**:
    *   Review `Dockerfile.base` and `pyproject.toml` for `uv` configuration.
    *   Research Podman 5.x and BuildKit best practices related to cache mounting and hardlinking in rootless environments.

### Phase 4: Testing & Verification
1.  **Clean Build & Run**: Execute `podman system prune`, `make build`, `make up`.
2.  **End-to-End Testing**: Thoroughly test all services, with a specific focus on RAG API, Curation Worker, and Crawler.
3.  **Performance Benchmarking**: Re-evaluate build times and service response times, noting any improvements or regressions.

## Knowledge Gaps & Research Strategy

*   **RAG API Observability:** Requires detailed audit of `app/XNAi_rag_app/observability.py` and `app/XNAi_rag_app/main.py` for implementation verification.
*   **Service Hangs:** Requires code inspection in relevant service files and Dockerfiles.
*   **`uv` Hardlinking Warnings:** Research Podman/BuildKit cache interactions and `uv` configuration.
*   **`sentence-transformers` Conflict:** Research `torch`-free embedding libraries and assess impact on RAG functionality.

## Memory Bank Updates

*   Update `activeContext.md` with current task status and priorities.
*   Update `progress.md` with details of implemented fixes and new blockers.
*   Log any new research findings or architectural decisions in `expert-knowledge/` as appropriate.

---
**Status**: READY FOR CODEBASE AUDIT & RESEARCH
**Confidence**: HIGH (Plan is detailed and addresses key blockers)
**Next Action**: Begin codebase audit for RAG API observability and service hang issues.