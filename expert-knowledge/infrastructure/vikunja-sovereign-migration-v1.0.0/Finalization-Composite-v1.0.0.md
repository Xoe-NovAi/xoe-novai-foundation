# Vikunja Sovereign Migration Finalization Pack - Composite v1.0.0

Date: 2026-02-07
Version: v1.0.0
Author: Architect + Grok MC (Grok Delivery)

Executive Summary
This document consolidates all artifacts, runbooks, mappings, and API surfaces required to finalize Vikunja implementation in a rootless Podman environment with Memory Bank integration. It codifies the research findings, operational runbooks, and data-migration paths into a single, versioned finalization bundle (v1.0.0).

Scope and Goals
- Deliver a fully automated, rootless Vikunja spin-up with a fresh PostgreSQL DB, including secret provisioning, resource hygiene, and end-to-end memory_bank → Vikunja migration.
- Enforce sovereignty constraints (Ma'at integrity), zero telemetry, and no built-in cloud telemetry.
- Provide idempotent, auditable, and operator-friendly runbooks and a robust importer surface to handle per-item and batch-like migrations where possible.

Pain Points and Root Causes (as distilled by Grok)
- Secrets lifecycle: pre-creation mandatory; external: true secrets break on partial Podman Compose up. Rootless Podman enforces strict secret presence.
- Orphan hygiene: interruptions spawn ghost pods and networks that block fresh spins.
- Migration friction: Vikunja API exposes per-item POST; no official batch endpoint; requires iterative imports and post-setup of projects/namespaces.

Impact and Business Value
- Automation reduces spin-up time from 15–30 minutes to under 5 minutes for a fresh start and ensures consistent, repeatable deployments.
- Reduces human error and improves auditability; aligns with sovereignty and zero telemetry policies.

Grok Deliverables (v1.0.0) and File Map
- Findings Brief (v1.0.0) — expert-knowledge/infrastructure/vikunja-sovereign-migration-v1.0.0/Findings-Brief-v1.0.0.md
- Fresh Spin-Up Runbook (v1.0.0) — expert-knowledge/infrastructure/vikunja-sovereign-migration-v1.0.0/Fresh-Spin-Up-Runbook-v1.0.0.md
- Memory Bank → Vikunja Mapping (v1.0.0) — expert-knowledge/infrastructure/vikunja-sovereign-migration-v1.0.0/MemoryBank-to-Vikunja-Mapping-v1.0.0.md
- Glossary (v1.0.0) — expert-knowledge/infrastructure/vikunja-sovereign-migration-v1.0.0/Grok-Glossary-v1.0.0.md
- Stakeholders (v1.0.0) — expert-knowledge/infrastructure/vikunja-sovereign-migration-v1.0.0/Grok-Stakeholders-v1.0.0.md
- Checklist (v1.0.0) — expert-knowledge/infrastructure/vikunja-sovereign-migration-v1.0.0/Grok-Checklist-v1.0.0.md
- Research Plan (v1.0.0) — expert-knowledge/infrastructure/vikunja-sovereign-migration-v1.0.0/Grok-Research-Plan-v1.0.0.md
- Importer API Surface (v1.0.0) — expert-knowledge/infrastructure/vikunja-sovereign-migration-v1.0.0/Grok-Importer-API-Surface-v1.0.0.md
- Vikunja Spin-Up Script (v1.0.0) — expert-knowledge/infrastructure/vikunja-sovereign-migration-v1.0.0/vikunja-spinup.sh
- Recovery Script (non-interactive) — scripts/recovery/vikunja_recovery_flow.sh

How Grok Should Deliver (What to fill in)
- Findings Brief: provide concrete blockers, root causes, impact, actions, risk, and mitigations.
- Fresh Spin-Up Runbook: provide a fully non-interactive, idempotent spin-up script along with health checks and rollback guidance.
- Memory Bank Mapping: provide a robust mapping from frontmatter to Vikunja payloads with examples.
- Glossary, Stakeholders, and Checklist: ensure everyone and every step is aligned.
- Research Plan: confirm scope, deliverables, and timeline for ongoing work.
- Importer API Surface: outline REST API contracts and payloads, with sample calls.

End-to-End Spin-Up and Migration Architecture (high-level)
- Rootless Podman stack running Vikunja API + frontend + Postgres with a Caddy reverse proxy.
- Secrets stored as Podman secrets (db-pass, jwt-secret) and mounted by the Compose stack.
- Memory Bank exports to Vikunja JSON; importer translates to Vikunja tasks via the API.
- Idempotent prune and cleanup steps guard against residual ghost resources after interruptions.
- The runbook and scripts are designed for automation and reproducibility with zero telemetry.

Validation, Testing, and Acceptance Criteria
- Fresh spin-up completes and Vikunja API health endpoint returns 200.
- Secrets are created as Podman secrets and consumed by services; no errors on startup due to missing secrets.
- Memory Bank export (vikunja-import.json) is present and matches Vikunja’s shape requirements; importer can run in dry-run and with live import using a real token.
- The mapping is coherent with the frontmatter to Vikunja fields (MemoryBank-to-Vikunja-Mapping-v1.0.0).
- Rollback path is documented and tested (prune/teardown procedures usable without data loss in the baseline environment).

Data Model and Mapping (Summary)
- Memory Bank frontmatter fields are translated into Vikunja task fields via MemoryBank-to-Vikunja-Mapping-v1.0.0.md.
- Namespaces/Projects are created if missing, using a pragmatic importer flow (Grok Importer API Surface).

Security and Compliance (Ma'at Integrity)
- Zero telemetry: explicitly enforced.
- Rootless, non-privileged containers with restricted network access.
- Secrets governance through Podman secrets; no secrets stored in plaintext in repo.

Versioning and Change Management
- This Finalization Pack is v1.0.0. Future increments (v1.0.1, v1.1.0) will capture new blockers, API changes, and improvements.
- Changes should be logged in the finalization pack and linked artifacts.

Appendix: Quick Reference Commands and Paths
- Spin-up script path: expert-knowledge/infrastructure/vikunja-sovereign-migration-v1.0.0/vikunja-spinup.sh
- Recovery script path: scripts/recovery/vikunja_recovery_flow.sh
- Fresh Spin-Up Runbook path: expert-knowledge/infrastructure/vikunja-sovereign-migration-v1.0.0/Fresh-Spin-Up-Runbook-v1.0.0.md
- Findings Brief path: expert-knowledge/infrastructure/vikunja-sovereign-migration-v1.0.0/Findings-Brief-v1.0.0.md
- Mapping path: expert-knowledge/infrastructure/vikunja-sovereign-migration-v1.0.0/MemoryBank-to-Vikunja-Mapping-v1.0.0.md
- Glossary path: expert-knowledge/infrastructure/vikunja-sovereign-migration-v1.0.0/Grok-Glossary-v1.0.0.md
- Stakeholders path: expert-knowledge/infrastructure/vikunja-sovereign-migration-v1.0.0/Grok-Stakeholders-v1.0.0.md
- Checklist path: expert-knowledge/infrastructure/vikunja-sovereign-migration-v1.0.0/Grok-Checklist-v1.0.0.md
- Research Plan path: expert-knowledge/infrastructure/vikunja-sovereign-migration-v1.0.0/Grok-Research-Plan-v1.0.0.md
- Importer API Surface path: expert-knowledge/infrastructure/vikunja-sovereign-migration-v1.0.0/Grok-Importer-API-Surface-v1.0.0.md
- Vikunja export path: vikunja-import.json (at repo root, produced by memory_bank_export.py)
- Memory Bank export script: scripts/memory_bank_export.py
- Importer: scripts/vikunja_importer.py
