# Opus 4.6 Handoff Package – 2026-03-02

**Coordination Key**: OPUS-HANDOFF-2026-03-02
**Prepared by**: Copilot Raptor / MC-Overseer
**Primary Liaison**: Cline Kat (`kate-coder-pro`)

This document consolidates the current system state, recent changes, outstanding work, and resources needed for the Opus 4.6 agent to take over strategic planning and refactoring.  It is designed to allow Opus to begin work with minimal context overhead.

---

## 📁 Core Resources
- **Memory Bank**: see `memory_bank/` directory; key files updated on 2026-03-02
- **Architecture docs**: `docs/architecture/*`, including new `service-wiring.md`
- **Operations guide**: `memory_bank/OPERATIONS.md` (build and deploy procedures)
- **Research queue**: `memory_bank/research/RESEARCH-QUEUE-2026-03-02.md`
- **Handoff docs**:
  - UI debugging: `handovers/RAPTOR-HANDOFF-UI-DEBUGGING-2026-03-02.md`
  - Docker refactor: `handovers/RAPTOR-HANDOFF-DOCKER-REFAC-2026-03-02.md`
  - This file (Opus summary)

## 🔄 Recent Work (March 1–2, 2026)
1. Completed Phase 3: dual UI (Chainlit + Open-WebUI) deployment, Base image build success.
2. Implemented Metropolis architecture with persistent expert entities.
3. Conducted major Docker refactor:
   - Builder/runtime split, base image trimmed.
   - Image size budget tooling added.
   - Pruned environment, rebuilt stack (partial, DNS/registry error pending).
4. Identified larger issues:
   - WebUI image ~4 GB – candidate for slimming or replacement.
   - Caddy routing conflicts and permission errors in Chainlit.

## ✅ Status Summary
- **Core stack**: 17 services defined in `docker-compose.yml`, 20 services after March 1.
- **Base image**: `xnai-base:latest` (~1.14 GB) plus build image `xnai-base-build`.
- **Documentation**: All architecture, operations, and memory bank docs updated as of March 2.
- **Research backlog**: Two new active research docs (Docker and UI) assigned to Cline Kat.
- **Agent assignments**: Cline Kat handling research and Opus liaison; other agents per `teamProtocols.md`.

## 🚧 Open Issues for Opus
- Formulate strategy to shrink or replace the `open-webui` container.
- Define CI automation for image size enforcement and build hygiene.
- Assist with finalizing `docker-compose` rebuild (registry/DNS issue) and ensure reliable startup process; note that recent Makefile changes now build `xnai-base` with both podman and docker, and `make up` depends on `build-base` to prevent `docker-compose` from pulling Debian every time.
- Review and extend service wiring guidelines; evaluate further service splitting.
- Validate the Gnosis engine and Postgres role; decide on inclusion/exclusion.

## 🛠️ Immediate Tasks
- Review research docs and start executing knowledge-gap tasks.
- Provide high-level container optimization strategy and CI design.
- Analyze UI issues and propose robust routing/permissions fixes.
- Update memory bank entries with any new insights.

## 📆 Next Review
- Anticipate a follow-up session after Opus 4.6 provides strategy; ideally within one week.
- Cline Kat to prepare summary notes and escalate any blockers via Agent Bus.

---

**Note**: All documents in this package are expected to be referenced directly.  Opus is free to create additional files under `memory_bank/research/` or `handovers/` as needed.

Good luck, Opus 4.6.  The foundation stack awaits your optimization and strategic oversight.
