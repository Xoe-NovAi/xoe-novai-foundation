# Claude Sonnet 4.5 — Vikunja Knowledge Gaps & Critical Research Request (UPDATED)

Background
- Local Vikunja instance available at: http://localhost:8000/vikunja (observed). The repository contains an export script (`scripts/memory_bank_export.py`) and a sample manifest (`vikunja-import.json`).
- Notes from quick scan: the Vikunja info endpoint reports available_migrators: ["vikunja-file","ticktick"] and several import/migrator endpoints (/api/v1/import, /api/v1/migrator, /api/v1/tasks, /api/v1/projects) return 401 when unauthenticated. The previous compose (`docker-compose.vikunja.yml`) has been archived and references consolidated into `docker-compose.yml`.

Goal (updated)
- Produce an actionable, priority-ranked research report that enables automated, programmatic migration of memory_bank items into Vikunja for agent consumption (Grok MC and Claude Implementation Architect). Focus on both: (A) migrator-file approach (vikunja-file) and (B) per-task REST creation (/api/v1/tasks), with robust auth and secrets handling for an air-gapped, rootless Podman environment.

Repo observations (use these as starting facts)
- Vikunja API base (local): http://localhost:8000/vikunja
- `scripts/memory_bank_export.py` exists and maps frontmatter -> Vikunja task fields (title, description, labels, custom_fields)
- `vikunja-import.json` is present as an example manifest
- Import/migration endpoints respond 401 without token (requires authentication header)
- Available migrators include `vikunja-file` (file upload migrator) — verify schema
- compose file unified: `docker-compose.yml` (old compose archived)

Scope / Research Questions (priority order)
1) Authentication & Tokens
   - Precisely how to obtain a programmatic token for Vikunja (local install): endpoint(s), payload, response, token lifetime, and JWT vs session cookie behavior.
   - Best practices for service accounts and token rotation in a sovereign, offline environment (Podman secrets / runtime files).

2) Migrator / Import API (vikunja-file)
   - Exact API surface for `vikunja-file` migrator: endpoint URL, HTTP method, multipart/form-data semantics (if any), and expected file format/schema (the exact JSON schema accepted by migrator). If migrator accepts a ZIP file or Vikunja JSON, document examples.
   - If migrator is not available or restricted, provide per-task creation equivalent via /api/v1/tasks (batching recommendations and rate-limiting behavior).

3) Projects, Labels, and Custom Fields
   - Endpoints to create projects and labels before import (if required). Sample payloads to ensure tasks land in the correct project and retain frontmatter metadata as custom_fields.
   - Guidance on name collisions and idempotency.

4) Programmatic Examples (must be runnable locally)
   - Example curl and Python (requests) scripts for:
     a) authenticate and obtain token
     b) create project if missing
     c) upload migrator file or create tasks in batches
     d) error handling for 401/429/5xx responses
   - Provide both dry-run examples and real-run examples using placeholders for secrets and Podman secrets usage.

5) Operational Constraints & Performance
   - Recommended batch sizes for imports given Ryzen 7 5700U with ~6–8GB RAM (conservative suggestions: 5–20 tasks/batch depending on attachments).
   - Identify resource-heavy operations (attachment uploads, DB migrations, index rebuild) and mitigation patterns (staggered uploads, DB maintenance windows).

6) Security & Sovereignty
   - Podman secrets recommended patterns, local-only secret files, and policy for rotating `VIKUNJA_JWT_SECRET` and DB passwords in an offline environment.
   - Ensure no external telemetry, and show how to run CLI operations locally.

7) Validation & Acceptance (10-task dry-run)
   - Provide a 10-task verification runbook (commands and API assertions) that a local operator can execute to confirm a successful import.

Deliverables (updated)
- Priority-ranked research report (markdown) with direct answers and sample code (curl + Python). Include clear artifacts: example migrator payload, example per-task create payloads, and a recommended import workflow.
- Runbook (markdown) with a 10-task dry-run and minimal verification checks (API asserts and expected UI checks).
- Minimal PR patch plan listing repository files to update (scripts/use-cases) and a suggested small code patch for `scripts/memory_bank_export.py` or a new `scripts/vikunja_migrator_upload.py` helper.

Notes for Claude researcher
- You have repository access; Vikunja server is local. If authentication credentials are not available, provide fully reproducible curl/Python snippets that the repo owner (or Gemini CLI) can run locally with secrets injected at runtime.
- Do NOT commit any secrets into the repository. Use placeholders (e.g., $VIKUNJA_JWT) and recommend Podman secret commands where appropriate.
- Maintain zero-telemetry posture: all recommendations must work offline or with local networking only.

Priority: High
Deadline: Deliver initial report and runbook as separate markdown files; include example scripts as fenced code blocks.

---

(End of updated brief)
