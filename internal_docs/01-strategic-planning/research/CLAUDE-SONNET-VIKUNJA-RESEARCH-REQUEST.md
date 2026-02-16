# Claude Sonnet 4.5 — Vikunja Knowledge Gaps & Critical Research Request

Background
- Vikunja is running locally at http://localhost:8000/vikunja and the repo contains a memory_bank export script (scripts/memory_bank_export.py) and a prepared manifest (vikunja-import.json).
- docker-compose.vikunja.yml has been archived because Vikunja services were merged into docker-compose.yml; several repo files referenced the old compose and were updated.

Objective
- Use Claude Sonnet 4.5 to research and produce a prioritized, actionable report that fills the remaining knowledge gaps required for fully automating Vikunja integration and task import/migration.

Scope / Research Questions (high priority)
1. Authentication & Tokens
   - How to obtain a programmatic token for Vikunja (login flow, endpoint, request payload, expected response, headers to use).
   - Best practice for service accounts / API tokens in Vikunja; token rotation and secure storage recommendations.

2. Task Import / Migrator API
   - Exact API endpoints and payloads for bulk task import (vikunja-file migrator or REST import endpoints).
   - Required JSON schema for tasks (fields, labels, custom_fields, project mapping) and attachment handling.
   - Whether migration endpoint accepts a full file upload or requires per-task creation via /api/v1/tasks.

3. Project & Label Management
   - API routes to create projects, labels, and ensure tasked project exists prior to import.
   - Mapping frontmatter labels to Vikunja labels (including Ma'at ideals mapping) and rate-limiting considerations.

4. Programmatic Examples
   - Provide example curl and Python (requests) snippets to:
     a) authenticate and obtain token
     b) create a project if missing
     c) create tasks in batches or call migrator with a file upload
   - Provide robust error-handling examples for 401/429/5xx responses.

5. Operational Constraints & Performance
   - Recommended batch sizes for imports given host constraints (Ryzen 7 5700U ~6–8GB RAM).
   - Any known resource-heavy operations (attachments upload, DB migrations) and mitigation patterns.

6. Security & Sovereignty
   - Recommendations that respect zero-telemetry and offline-first, secure secret handling recommendations (Podman secrets, runtime injection, rotation policy).

7. Validation & Acceptance
   - A small verification plan to confirm a successful import (10 tasks sample): sequence of commands and API assertions to run locally.

8. Documentation & PR Changes
   - A draft PR description and a minimal change-set to update repo docs or scripts (scripts/deploy_vikunja_secure.py, scripts/recovery/vikunja_recovery_flow.sh, scripts/setup_vikunja_secrets.py, README.md) with concrete commands for automation.

Deliverables
- A prioritized research report (markdown) with answers to the above, actionable steps, and example code snippets.
- A short runbook (markdown) with step-by-step local verification steps (10-task dry-run) and a recommended automation script template to perform the import.
- A checklist of repo edits and a proposed small patch (list of files & changes) that the Copilot agent should apply.

Inputs & References (repo)
- scripts/memory_bank_export.py
- vikunja-import.json
- docker-compose.yml
- internal_docs/03-infrastructure-ops/archived/docker-compose.vikunja.yml
- scripts/deploy_vikunja_secure.py
- scripts/setup_vikunja_secrets.py
- pre-flight-check.sh

Constraints
- Zero-telemetry: do not recommend cloud-hosted services; all steps must be local or self-hosted.
- Host memory constraints: propose conservative batch sizes and sample code tuned for low memory.

Priority: High
Estimated Effort: 2-4 hours research + write-up

Acceptance Criteria
- Clear instructions to authenticate and import tasks programmatically (sample working curl and Python snippets) that succeed against local Vikunja (assuming admin credentials available).
- A verification runbook that an operator can follow to validate success.

Please provide the research output as a markdown report and a separate runbook file; attach example scripts as code blocks.
