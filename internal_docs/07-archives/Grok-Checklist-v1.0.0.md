# Grok Readiness Checklist - Vikunja Sovereign Migration (v1.0.0)

- [ ] Secrets: db-pass and jwt-secret created as Podman secrets
- [ ] Rootless Podman spin-up script validated (non-interactive path)
- [ ] Fresh Vikunja spin-up health checks pass
- [ ] vikunja-import.json exists and maps to desired memory_bank data
- [ ] Importer script enhanced for batch-like flows (project/namespace auto-create)
- [ ] Memory Bank → Vikunja mapping doc reviewed and applied
- [ ] Recovery runbook automated and idempotent
- [ ] Runbook run in dry-run mode shows expected payloads
- [ ] Documentation bundle versioned as v1.0.0
