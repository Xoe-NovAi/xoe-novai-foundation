# Research Jobs: Build Process Hardening & Caching
**Date**: 2026-03-02
**Assigned To**: Cline Kat (`kate-coder-pro`)
**Coordination Key**: BUILD-HARDENING-2026-03-02

The recent failure (`xnai-base` not found) and repeated Debian downloads during compose builds highlight weaknesses in the build workflow.  This document outlines investigation tasks to make the system robust and offline-friendly.

## 🧩 Knowledge Gaps / Research Items
1. **Base Image Build Dependency**
   - Determine how to structure `docker-compose.yml` so that `xnai-base` is built automatically before any service that uses it.
   - Investigate `depends_on` with `build` or multi-stage compose support.
   - Test by creating a minimal compose setup where base builds and then rag builds using it, verifying no internet fetch for Debian layers when base is local.

2. **Local Registry & Build Cache**
   - Evaluate running a lightweight local registry (e.g., `registry:2`) to store `xnai-base` and other images.
   - Research Docker/Podman build cache options (`--cache-from`, `buildx`, `--secret`) to reuse previously downloaded layers and avoid repeated Debian pulls.
   - Document commands and Makefile changes required to populate and use the cache/registry.

3. **Offline/Locked-Down Builds**
   - Identify all external network calls during build (Debian apt, pip downloads) and propose methods to mirror them (apt-mirror, wheel cache).  Create a helper script to pre-fetch packages.
   - Research `docker build --network none` and methods to supply offline artifacts.
   - Document steps for fully air-gapped build environment.

4. **Security Hardening**
   - Research signing images (cosign/notary) and verifying before deployment.
   - Investigate scanning build contexts for secrets (trivy syft) and automatically fail builds on findings.
   - Propose Makefile targets or pre-commit hooks to enforce hardening.

5. **Build Workflow Documentation**
   - Update `OPERATIONS.md` with definitive build flow: `make build` -> `docker-compose up -d --build` or `make up` etc.
   - Clarify when base image must be manually rebuilt (e.g., when Dockerfile.base changes).
   - Provide troubleshooting tips for common errors (e.g., missing base, registry credentials).

## ✅ Deliverables
- Step-by-step guide for building images locally without network dependency.
- Example `docker-compose.yml` snippet or `Makefile` rule demonstrating base dependency and cache usage.
- Recommendations for CI pipeline modifications to enforce hardening and caching (e.g., use buildx with CI cache, run trivy scans).
- Updated documentation entries and research notes posted to memory bank.

## 🔁 Next Steps
1. Start with reproducing the failure and crafting fix.
2. Extend Makefile with `make build-base` and adjust `make up` to ensure correct order.
3. Draft caching workflow and test offline scenario.
4. Report findings and update `handovers/OPUS-HANDOFF-2026-03-02.md` with recommendations.
