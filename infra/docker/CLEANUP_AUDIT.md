# 🧹 Omega Stack: Infrastructure Cleanup Audit (2026-03-10)

The following files in `infra/docker/` have been identified as redundant, stale, or duplicate based on the current Metropolis v4.1.2-HARDENED architecture.

## 🗑️ Candidates for Removal

| File | Reason |
|:-----|:-------|
| `Dockerfile.base` | Redundant. The `xnai-base` image is already stable and built. |
| `Dockerfile.build` | Stale. Replaced by the multi-stage `Dockerfile`. |
| `Dockerfile.curator` | Duplicate. `Dockerfile.curation_worker` is the active target. |
| `Dockerfile.cline` | Stale. No longer used in the current orchestration. |
| `docker-compose-noninit.yml` | Redundant. Superseded by the hardened `docker-compose.yml`. |
| `docker-compose.production.yml` | Outdated. Does not reflect current mesh standards (port 8002, TLS, etc.). |
| `docs-new/` | Stale directory. Official docs are in `docs/`. |

## 🛠️ Proposed Actions
1. **Prune**: Remove the files listed above.
2. **Consolidate**: Ensure any unique logic in `Dockerfile.curator` is merged into `Dockerfile.curation_worker`.
3. **Audit**: Verify `docker-compose.yml` is the single source of truth for all environment variables.

---
*Audit by Gemini General 2. Standing by for confirmation to prune. 🔱*
