---
account: arcana.novai
version: 1.1.0
title: Vikunja Implementation & Memory Bank Migration Roadmap
date: 2026-02-06
status: 🚀 Ready for Implementation (Elite Strategy)
ma_at_ideals: [7, 18, 41]
tags: [vikunja, implementation, roadmap, memory-bank-migration, project-management]
---

# Vikunja Implementation & Memory Bank Migration Roadmap

**Vision**: Transform Vikunja into the central synchronization hub for all Xoe-NovAi agents, replacing the legacy memory_bank system as the source of truth for task coordination while preserving its value as historical archive and RAG source. 

This roadmap implements Grok MCA's **Elite Strategy**—prioritizing rootless Podman deployment, FastMCP MCP integration for Gemini CLI, and systematic Diátaxis-aligned organization.

---

## Phase 0: Pre-Deployment Audit & Prep (2 Days)

### 0.1 Foundation Audit
- [ ] Verify current stack health via Trinity scans
- [ ] Run `preflight_checks.py` on foundation services
- [ ] Ensure all Dockerfiles use rootless users
- [ ] Test Podman quad deployment locally

### 0.2 Migration Blueprint Creation
- [ ] Create `memory_bank_export.py` script to export tasks with frontmatter
- [ ] Define migration mapping (memory_bank → Vikunja labels/custom fields)
- [ ] Dry-run import via Python requests bulk endpoint
- [ ] Test Vikunja API token generation and rotation

---

## Phase 1: Migration & Deployment (Week 1-2)

### 1.1 Vikunja Rootless Deployment
- [ ] Create `docker-compose.vikunja.yml` with:
  - `userns_mode: keep-id` for rootless security
  - Postgres 16 backend with persistent volumes
  - Vikunja API (latest, scanned via Trinity)
  - Local-only frontend deployment
- [ ] Deploy and verify quad functionality (frontend/api/db/migrator)
- [ ] Configure reverse proxy (Nginx local-only)
- [ ] Test CORS bypass for local agent integration

### 1.2 Memory Bank Migration
- [ ] Run `memory_bank_export.py` to extract all tasks as JSON
- [ ] Execute bulk import via Vikunja API
- [ ] Verify task creation, labels, and custom fields
- [ ] Tag migrated tasks with `indefinite-archive`
- [ ] Archive original memory_bank files in git

---

## Phase 2: MCP Integration Layer (Week 3-4)

### 2.1 FastMCP Vikunja MCP Server
- [ ] Create `scripts/mcp_servers/vikunja_mcp.py` based on FastMCP
- [ ] Implement core functions:
  - `create_task`: Namespace-aware task creation
  - `update_status`: Move tasks through workflow
  - `get_board`: Query tasks by namespace/project
  - `bulk_import`: For memory_bank fallback
- [ ] Register MCP server in Gemini CLI config
- [ ] Test API calls with CLI authentication

### 2.2 Cline Integration
- [ ] Add IDE hook for refactor tasks
- [ ] Post task updates on file save
- [ ] Implement Ma'at label injection from frontmatter
- [ ] Test dual-write pattern (Vikunja + memory_bank)

---

## Phase 3: Agent Workflow Integration (Week 5-6)

### 3.1 Task Creation Protocol
- [ ] Finalize Ma'at-aligned task templates
- [ ] Train agents on new namespace/project structure
- [ ] Implement custom fields:
  - `EKB-Link`: Dataset paths for reference
  - `Commit-Hash`: Traceability for code changes
  - `Owner`: Agent/user assignment
- [ ] Configure view filters (Kanban, Gantt, Table, Calendar)

### 3.2 Sync Protocols Update
- [ ] Update sync protocols for Vikunja-first workflow
- [ ] Remove memory_bank dependencies from agents
- [ ] Implement fallback for air-gapped environments
- [ ] Test offline/online sync scenarios

---

## Phase 4: Advanced Features (Week 7-8)

### 4.1 Automated Sync Pipeline
- [ ] Create `scripts/vikunja_sync_daemon.py`
- [ ] Implement cron job for periodic sync
- [ ] Monitor sync status via Trinity
- [ ] Test edge cases (failed connections, large imports)

### 4.2 MkDocs Knowledge Portal
- [ ] Build `scripts/vikunja_to_mkdocs.py`
- [ ] Export tasks/descriptions to Markdown files
- [ ] Add to MkDocs Material site with Diátaxis structure
- [ ] Enable search functionality for tasks

---

## Phase 5: Optimization & Hardening (Week 9-10)

### 5.1 Performance Tuning
- [ ] Postgres tuning for Ryzen 5700U
- [ ] Enable indexes on frequently queried fields
- [ ] Test query performance with large datasets
- [ ] Optimize container startup times

### 5.2 Security Hardening
- [ ] Implement Trinity audits pre-deploy
- [ ] Set up podman auto-update for containers
- [ ] Add Trivy/Grype scans in CI/CD
- [ ] Test failover and recovery procedures

---

## Success Metrics

### Week 2 Checkpoints
- [ ] Vikunja deployed and accessible (3456 port local-only)
- [ ] 100% memory_bank tasks migrated and verified
- [ ] MCP server operational
- [ ] Agents onboarding script tested

### Week 6 Completion
- [ ] 100% task creation in Vikunja
- [ ] Zero new entries in legacy memory_bank
- [ ] MCP integration tested
- [ ] Documentation updated to reflect new workflow

---

## Ma'at Alignment

| Ideal | Implementation |
|-------|---------------|
| **7 - Truth** | Single source of truth (Vikunja), accurate documentation |
| **18 - Balance** | Harmonious agent coordination via central hub |
| **41 - Advance** | Modern PM tooling, automated workflows, scalable architecture |

---

**Status**: 🚀 **Ready for Implementation (Elite Strategy)**  
**Next Action**: Create `memory_bank_export.py` and `docker-compose.vikunja.yml`  
**Owner**: Cline-Kat (with Trinity for security audits)

*"From scattered memory to centralized harmony — the temple rises."*