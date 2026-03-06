# Supplemental Vikunja Projects Info for Live Gate (v1.0.0)

Overview
- This document lists the active Vikunja projects/workspace scaffolding to seed in a test environment to assist the live gate and migration flows.

Proposed active Vikunja projects/workspaces
- Workspace: Xoe-NovAi Foundation
  - Purpose: Central foundation workspace for all Xoe-NovAi Vikunja migrations and projects.
- Project: Foundation (Migration)
  - Owner: Architect
  - Purpose: Parent project for migration tasks and import mapping tests.
- Project: Memory Bank Sync
  - Owner: Gemini CLI
  - Purpose: Store and route memory_bank synchronization tasks and results; track mapping progress.
- Project: Documentation & Governance
  - Owner: Grok MC
  - Purpose: Documentation, runbooks, and governance artifacts for the live gate.
- Optional: Additional sandbox‑only projects for experimentation
  - Owner: Cline Variants
  - Purpose: Prototyping and testing of importer enhancements and token workflows.

Notes
- These projects can be created manually in the Vikunja UI for quick sandbox validation or via an importer once the live gate is automated.
- The importer should be expanded to attach tasks to these projects by default when mapping frontmatter to Vikunja payloads.
