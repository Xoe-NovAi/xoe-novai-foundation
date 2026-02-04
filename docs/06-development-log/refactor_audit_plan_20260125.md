# Systematic Audit & Refactor Plan - XNAi Foundation Stack
**Date**: January 27, 2026
**Version**: 1.0
**Status**: ACTIVE
**Agent**: Gemini CLI

## 1. Executive Summary
This document outlines the systematic findings, remediation steps, and strategic plan for finalizing the XNAi Foundation Stack refactor. The stack is currently at **83% functional readiness**, with critical blockers in the RAG API and dependency inconsistencies across services.

### Core Objectives
- Resolve RAG API startup crashes (DONE: Observability, griffe; PENDING: bcrypt, read-only FS).
- Standardize dependencies across 4 core Python services.
- Harden infrastructure for rootless Podman 5.x compliance.
- Implement Ma'at's 42 Ideals at the code level.

---

## 2. Audit Findings

### 2.1 Dependency Gaps (CRITICAL)
- **RAG API**: Missing `bcrypt`, `pyjwt`, `cryptography`, `sqlite-utils`, and `griffe`.
- **UI/Crawler**: Inconsistent versions of `pydantic` and `langchain`.
- **Curation Worker**: Minimalist but missing newer IAM integration points if needed.

### 2.2 Infrastructure Hardening
- **Read-Only FS**: `rag` service uses `read_only: true` but lacks writable log paths, causing crashes when `observability.py` or `memory_bank_integration.py` attempts writes.
- **UID/GID Mapping**: Redis and Crawler successfully mapped to `997:997`, but RAG/UI/Curation still use `1001:1001` (host UID 1000). This inconsistency may cause volume permission drifts.

### 2.3 Code Standards (Ma'at)
- **Observability**: Successfully refactored to "Safe Module Loading" pattern.
- **API Documentation**: Made robust with lazy-loading fallbacks for `griffe`.
- **IAM Service**: Uses `bcrypt` work factor 12 (Ryzen optimized), but lacks persistent DB path stability in read-only environment.

---

## 3. Remediation & Systematic Action

### Phase 1: Dependency Harmonization (IMMEDIATE)
- **Action**: Update `requirements-*.in` for all services to include IAM and Observability defaults.
- **Rationale**: Ensures the Zero-Trust pattern works across the entire stack, not just RAG.

### Phase 2: Read-Only Filesystem Hardening (IMMEDIATE)
- **Action**: Add `tmpfs` mounts for `/app/logs` and `/app/XNAi_rag_app/logs` in `docker-compose.yml`.
- **Rationale**: Fixes `[Errno 30] Read-only file system` crashes while maintaining security.

### Phase 3: Ryzen Core Steering & Performance (PENDING)
- **Action**: Audit `N_THREADS` and `OPENBLAS` settings across all Dockerfiles.
- **Rationale**: Optimize for 5700U (8C/16T) - Target 6 threads for AI, 2 for background.

---

## 4. Strategic Refactor Todo List

### Infrastructure
- [x] Fix RAG Observability (Jaeger NameError)
- [x] Fix RAG API Docs (Griffe ImportError)
- [ ] Add `bcrypt`, `pyjwt`, `cryptography`, `sqlite-utils` to all relevant `.in` files.
- [ ] Implement `tmpfs` log mounts for all Python services in `docker-compose.yml`.
- [ ] Standardize `user: "1001:1001"` vs `user: "997:997"` mapping strategy.

### Codebase
- [ ] Audit `iam_service.py` for DB path persistence.
- [ ] Verify `memory_bank_integration.py` across all services.
- [ ] Implement Ma'at compliance checks in `main.py` startup sequences.

### Validation
- [ ] Health check pass for all 6 services.
- [ ] RAM audit (<5.6GB total).
- [ ] Zero-telemetry verification (No external DNS/IP hits).

---

## 5. Next Steps
1. **Apply Dependency Fixes**: Update all `requirements-*.in`.
2. **Apply Compose Fixes**: Hardening volumes/tmpfs.
3. **Trigger Nuclear Rebuild**: `SKIP_DOCKER_PERMISSIONS=true make build` (if timeout increased) or service-by-service rebuild.
4. **Synchronize Memory Bank**: Final update to `progress.md` and `activeContext.md`.

**Systematic Action initiated. Transitioning context window to Strategy/Research mode.** 🔱🚀
