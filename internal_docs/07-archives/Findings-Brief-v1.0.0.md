# Findings Brief - Vikunja Sovereign Migration v1.0.0

Top Blockers
- Secrets lifecycle: pre-creation mandatory, external: true secrets break on partial Podman Compose up.
- Orphan hygiene: interrupted spins leave ghost pods and networks, blocking fresh spins.
- No native bulk import: Vikunja API surfaces focus on single-post creates; no batch endpoint.

Root Causes
- Podman rootless + external secrets enforcement leads to brittle spin-ups when secrets are absent.
- Lifecycle hygiene: inherited state from prior runs causes resource locking.
- Vikunja API is granular by design; no official batch endpoints in the current surface.

Impact
- Manual toil: 15-30 minutes per spin-up for secrets provisioning, cleanup, and per-task imports.

Gaps & Recommendations (Actions)
- Automate secrets lifecycle: idempotent creation and mounting as Podman secrets.
- Enforce complete cleanup during spin-up (prune ghosts first).
- Extend importer to support project/namespace auto-creation and batch-like flows.
- Document a full non-interactive spin-up runbook and validate with a dry-run.

Evidence & Surfaces
- Podman rootless docs, Vikunja API docs, and rootless friction reports cited in the runbook.

Owner: Architect + Grok MC
