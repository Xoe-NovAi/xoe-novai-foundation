# Research Jobs: Docker Refactor Knowledge Gaps
**Date**: 2026-03-02
**Assigned To**: Cline Kat (`kate-coder-pro`)
**Coordination Key**: DOCKER-REFAC-2026-03-02

This document lists outstanding questions and investigation tasks generated during the March 2 Docker image refactor session.  Cline Kat is responsible for executing these research jobs, populating findings in the memory bank, and preparing brief summaries for Opus 4.6.

## 🧩 Knowledge Gaps / Research Items
1. **Open-WebUI Image Bloat**
   - Analyze the official `ghcr.io/open-webui/webui:latest` (or local cached copy) and identify which layers contribute the most to its ~4 GB size.
   - Determine whether a slimmed Dockerfile can be built (fork upstream, remove unused models, assets, or use distroless base).
   - Document steps for performing `dive` analysis and layer inspection to reproduce findings.

2. **Image Size Budgeting & CI**
   - Research best practices for automated image size enforcement (tools like `docker-slim`, GitHub Actions `docker/build-push-action` with `--max-size` checks, or custom scripts).
   - Propose thresholds for each service (e.g., API 300 MB, UI 500 MB) considering current runtime dependencies.
   - Draft a CI pipeline snippet (GitHub Actions or Makefile) that fails the build if images exceed budget.

3. **Artifact Management**
   - Confirm pattern of mounting large model assets vs. baking into images; document recommended directory structure and mount conventions.
   - Research alternative approaches (e.g., OCI image manifests with foreign layers, sidecar containers serving models, volume plugins).

4. **Build vs Runtime Workflow**
   - Clarify when developers should rebuild `xnai-base-build` versus `xnai-base` and how caching is managed across local development, staging, and production.
   - Investigate use of multi-platform builds or buildx for cross-arch support if required.

5. **Postgres / Gnosis Engine Role**
   - Document the current and planned responsibilities of `xnai_postgres` within the stack.
   - Determine whether the database should be included in standard compose files or remain optional; outline migration/seed procedures.

6. **Further Trimming Opportunities**
   - Audit other service images (RAG API, Chainlit UI, crawler, curation_worker) for unused packages or Python wheels that can be removed.
   - Investigate use of smaller base images (e.g., `python:3.12-alpine` or distroless) and whether build-time wheel compilation supports them.

7. **Alternative UI Research**
   - Investigate lightweight alternatives to Open-WebUI (e.g., Lemonade, ChatUI-lite, custom FastAPI/React) that provide polished interfaces without heavy weight.
   - Evaluate UX tradeoffs and integration effort; prepare comparison table.

## ✅ Deliverables
- Summaries for each research item (written markdown with findings).
- Updated memory bank entries under `research/` or `expert-knowledge/` as appropriate.
- Recommendations to Opus 4.6 for image sizing strategy, UI options, and deployment practices.

## 📌 Next Steps for Cline Kat
1. Begin with layer analysis of `open-webui` using `dive` or `docker history`.
2. Draft a CI check example and test locally with existing images.
3. Update this document with progress logs and results; tag as complete when each item is done.
4. Coordinate with Opus 4.6 by posting findings to the handoff document or creating separate summary docs.

Good luck! Ensure all output is concise and actionable for the next agent wave.
