# Grok MC Research Plan: Vikunja Integration Pain Points

Scope
- Investigate rootless Podman deployment pain points affecting Vikunja: secrets, network, and container lifecycle.
- Produce actionable recommendations to harden deployment, reduce failure modes, and accelerate fresh spin-ups.

Deliverables
- 1-page findings brief outlining top blockers and root causes.
- 2-3 concrete action items with owners and success criteria.
- A lightweight recovery/autonomy script sketch for non-interactive spin-ups (if needed).

Research Questions
- RQ1: What are robust, non-interactive methods to manage Podman rootless secrets for all services (db-pass, jwt-secret, etc.)?
- RQ2: What is the minimal, safe sequence to deploy Vikunja from scratch in a rootless Podman environment (including network isolation and volume handling)?
- RQ3: How can memory_bank → Vikunja migration be automated end-to-end with minimal human intervention (frontmatter mapping, bulk import, error handling)?

Approach & Outputs
- Review current docker-compose.yml and secrets flow; validate against best practices for rootless Podman.
- Produce a proposed runbook for fresh spin-up, including prerequisites, secrets, and health checks.
- Propose code/config changes (if any) to scripts/memory_bank_export.py and scripts/vikunja_importer.py to support a robust pipeline.

Timing
- Initial findings due within 2 business days of this document’s approval.

Owner
- Grok MC (Research & Governance) with collaboration from the Foundation DevOps lead.

## Deliverables for Grok MC
- Findings Brief (1 page)
- Deep Dive (optional 2-3 pages)
- Fresh Spin-up Runbook (non-interactive)
- Mapping Guide: Memory Bank frontmatter -> Vikunja fields
- Runbook automation sketch
- Handoff templates (stakeholders, responsibilities)

## Research Artifacts (to be produced by Grok MC)
- grok-mc-findings-brief.md
- grok-mc-runbook.md
- grok-mc-mapping.md
- grok-mc-glossary.md
- grok-mc-stakeholders.md
- grok-mc-checklist.md
 
