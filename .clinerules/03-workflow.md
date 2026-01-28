
---
priority: high
context: general
activation: always
last_updated: 2026-01-27
version: 1.0
---

# Development Workflow

**Memory Bank Integration**: Query memory_bank/activeContext.md for current priorities and memory_bank/progress.md for implementation status before starting tasks.

- **Plan Mode First**: For complex tasks, outline steps, gaps, verification, and potential issues. Include dry-runs and rollbacks. Manage context window actively.
- **Atomic & Verifiable**: Use backups (timestamped), dry-runs, checksums (SHA256 manifests), logging (migration-log-*.json). Verify integrity post-migration.
- **Voice-Guided Democratization**: Suggest voice-first setup, hardware auto-detection, one-click Podman deploys.
- **Automatic Evolution**: If request exceeds current stack, trigger gap analysis → research → prototype → benchmark → integrate.
- **Testing & Validation**: Verify with podman logs, curl, site browse[](http://localhost:8000), permissions checks (`ls -la`). Use strict mode for MkDocs builds.
- **Documentation**: Update MkDocs on changes (build --clean). Use Diátaxis structure. Troubleshoot with logs and official docs.
- **Production**: Static MkDocs builds + reverse proxy over `mkdocs serve`. Monitor with OpenTelemetry/Prometheus/Grafana.
- **Project Tracking**: Always reference/update `project-tracking/PROJECT_STATUS_DASHBOARD.md` and relevant sub-trackers in `project-tracking-consolidation-resources/` for status, milestones, and changes.

Provide step-by-step commands with explanations, verification, and reversibility. For migrations: Dry-run first, then live with rollback option. Use memory banks for persistent knowledge.

Example migration:
```bash
python atomic_migrate.py --dry-run
python atomic_migrate.py
python validate_migration_comprehensive.py
