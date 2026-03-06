# 🧩 Handoff: Docker Image Refactor & Strategy
**Date**: 2026-03-02
**Agent**: Copilot Raptor (preparing work for Opus 4.6)
**Coordination Key**: `DOCKER-REFAC-2026-03-02`

---

## 🔄 Current state after Raptor implementation

1. **Base image trimmed**: `Dockerfile.base` now contains only runtime dependencies
   (curl, git, ffmpeg, audio libs, OpenBLAS) – build tools removed. A new
   `Dockerfile.build` retains the original full set and builds `xnai-base-build:latest`.
2. **Service Dockerfiles rewritten**: `Dockerfile`, `Dockerfile.chainlit`,
   `Dockerfile.crawl`, and `Dockerfile.curation_worker` now follow a multi-stage
   builder/runtime pattern. Builder stage installs compilers/`cmake` to build
   Python wheels; runtime stage copies only the resulting artifacts on top of
   `xnai-base:latest`.
3. **Documentation added**:
   - `docs/architecture/service-wiring.md` outlines service relationships and
     contains build/runtime guidelines (with an example pattern).
   - Reference doc updated to note the external `open-webui` image size.
4. **Build tooling updates**:
   - `Makefile` now builds both runtime and build base images and includes a
     `check-image-sizes` target.
   - `scripts/check_image_sizes.sh` enforces a 500 MB budget for key images.
5. **Validation script** extended** to verify separation of build/runtime tools.
6. **.dockerignore** already present at repo root covers large data directories.

---

## 🚧 Remaining gaps & open questions (for Opus to address)

- **WebUI bloat**: external GHCR image is ~4 GB. We need a strategy to trim or
  replace it.  Should we fork and build a slimmed version? Which layers are the
  largest? Could we run `dive` or inspect manifests? Provide specific
  suggestions.
- **Image size targets**: 500 MB is provisional.  Recommend a realistic budget
  per image and CI gating strategy (e.g., failure thresholds, automated alerts).
- **Model artifacts**: current images avoid bundling models (they are mount
  volumes). Confirm this pattern and propose rules for keeping large assets out
  of containers.
- **Build/production workflow**: document when developers should use
  `xnai-base-build` vs. `xnai-base`; clarify `docker-compose.production.yml`
  vs. dev compose.  Suggest simplifications or automation.
- **Postgres role**: The Gnosis engine is partially documented; define when
  it's required and whether it should remain optional in image builds.
- **Further trimming opportunities**: analyze other images (RAG, UI, etc.) and
  propose concrete wins (e.g., remove unused packages, convert Python libs to
  manylinux2014 wheels, use distroless runtime, etc.).

---

## 📦 Task for Opus 4.6 (minimal token usage guidance)

Please review the changes above and deliver:

1. A high‑level strategy for reducing container sizes across the stack,
   prioritizing effort-to-gain tradeoffs.  For each major image provide a
   bullet‑point plan (e.g., "split out audio tools", "drop pip cache").
2. A proposed CI/automation design to enforce size budgets and build hygiene
   without repeated manual checks.  Outline scripts or Makefile targets.
3. Recommendations for handling the `open-webui` image (fork, alternative
   UI, manifest analysis).  You need not implement--just describe the approach.
4. Any additional architectural suggestions (e.g., breaking services,
   moving heavy components to sidecars) that could further improve modularity
   and shrinkage.

> **Important**: the goal is to produce strategy, examples, and pseudo-code.
> Do **not** re-execute the refactor work—our token budget is limited.  We will
> implement based on your guidance afterwards.

---

Good luck, Opus.  Your outputs will shape the next phase of the image-sizing
initiative.  The Metropolis depends on efficient containers.
