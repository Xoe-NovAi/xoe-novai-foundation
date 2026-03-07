# 🏁 HANDOVER: OMEGA STACK REPOSITORY RESTRUCTURING (v1.0)

**Date**: 2026-03-03
**From**: Gemini CLI (Architect)
**To**: Opus 4.6 / Senior AI Engineering Team
**Status**: COMPLETED (Restructuring & Initial Fixes) | **Criticality**: HIGH

---

## 🏗️ New Repository Hierarchy

To resolve extreme root clutter (>120 items) and enforce **Omega Stack Phase 4 Protocols**, the following structure has been implemented:

| Directory | Purpose | Original Items (Moved) |
|-----------|---------|------------------------|
| `infra/` | Infrastructure-as-code | `docker/`, `containers/`, `migrations/`, `monitoring/`, `systemd/` |
| `storage/` | Persistent Data Layers | `data/`, `db/`, `models/`, `embeddings/`, `library/`, `backups/` |
| `orchestration/` | Multi-Agent Coordination | `handovers/`, `communication_hub/`, `conductor/`, `mc-oversight/`, `vikunja_tasks/` |
| `knowledge_base/` | Strategic Documentation | `internal_docs/`, `knowledge/`, `expert-knowledge/`, `architecture/`, `PHASES/` |
| `config/` | System Configuration | All `*.yaml`, `*.toml`, `*.ini`, `Caddyfile`, `alembic.ini`, `pytest.ini`, `tox.ini` |
| `requirements/` | Dependency Management | All `requirements*.txt` and `requirements*.in` |
| `setup/` | Scripts & Maintenance | All root-level `.sh`, `.py` scripts, `standalone_setup.py`, `pre-flight-check.sh` |
| `artifacts/` | Build & Test Outputs | `reports/`, `ekb-exports/`, `GetDBInfo/`, test result JSONs |
| `_archive/` | Deprecated & Legacy | `venv_llama/`, `versions/`, `xoe-novai-sync/` |

---

## ⚡ Domain-Driven Agent Strategy
Implemented localized **`GEMINI.md`** files in key domains to support "Expert Contexts" when launching CLI agents from subdirectories:
- **`docs/GEMINI.md`**: Context for Documentation Specialists (MkDocs).
- **`app/GEMINI.md`**: Context for Application/Core Engineers (FastAPI, AnyIO, Redis).

---

## 🛠 Fixes Applied
- **Bulk sed replacement** performed on:
  - `.github/workflows/ci.yml`
  - `infra/docker/Dockerfile*`
  - `Makefile`
- **Updated Patterns**:
  - `scripts/` → `setup/`
  - `requirements-*.txt` → `requirements/requirements-*.txt`
  - `data/` → `storage/data/`
  - `models/` → `storage/models/`
  - `db/` → `storage/db/`

---

## ⚠️ Remaining Work / Risks (Action Items for Opus 4.6)
1. **Docker Build Context**: Verify that `docker build -f infra/docker/Dockerfile .` (run from root) still behaves as expected. Some `COPY` commands might need absolute root paths or relative adjustments.
2. **Python Import Paths**: I moved `langchain_community/` to `packages/`. Ensure `PYTHONPATH` includes `packages/` or update imports to `from packages import langchain_community`.
3. **CI Validation**: Run a test CI job to ensure all `pip install` commands and script calls in `setup/` are functioning correctly with the new relative paths.
4. **Symlink Audit**: Check for broken symlinks in `storage/` and `docs/`.
5. **Memory Bank Freshness**: Verify that `memory_bank/activeContext.md` accurately reflects this massive structural shift.

---
**Coordination Key**: `OMEGA-RESTRUCTURE-2026-03-03`
**Final State**: Root directory reduced from 120+ items to ~25.

## 💎 Antigravity Token & Agent Strategy (New Directive)
- **Token Conservation**: Opus 4.6 MUST prioritize token efficiency on the Antigravity account. 
- **Task Delegation**: High-token tasks (large file reads, comprehensive analysis) should be offloaded to specialized agents via the **Agent Bus** (e.g., dedicated sub-agents or local model instances) rather than consumed by the primary orchestrator.
- **Quota Awareness**: Monitor `configs/model-router.yaml` and `app/XNAi_rag_app/core/quota_checker.py` to ensure rotation and fallback chains are healthy.

## 🔍 Final Directive: Comprehensive Audit
Opus 4.6 is officially tasked with a **Full System Audit**:
1. **Codebase Structural Audit**: Validate that the new hierarchy (infra, storage, knowledge_base) is fully functional and all paths are correctly linked.
2. **Strategy Alignment**: Review the "Metropolis of Persistent Experts" strategy against current implementation.
3. **Implementation Deep-Dive**: Audit for async safety (AnyIO), hardware optimizations (Ryzen 5700U), and circuit breaker robustness.
