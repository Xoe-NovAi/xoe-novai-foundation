---
document_type: report
title: SONNET IMPL INTEGRATION CHECKLIST
created_by: Haiku-4.5 (Phase 2C Automation)
created_date: 2026-03-14
version: 1.0
status: active
hash_sha256: 0e1e9ea5c5b9a8086e3ef0809607a80be55bdb627fafdb542a9dbe96142dce21
---

# ✅ Sonnet IMPL Integration Checklist

**Source**: IMPL-01, IMPL-02, SUPP-02 (3,049 lines total)  
**Date**: 2026-03-13  
**Status**: COMPREHENSIVE EXTRACTION — All refactoring items extracted

---

## Overview

This checklist extracts ALL refactoring items from the three Sonnet implementation manuals and maps them to Omega Stack files and execution phases. Each item includes:
- **Task ID**: Unique identifier (e.g., ST-001)
- **Source**: Which section of IMPL guide
- **Description**: What needs to be done
- **Omega Stack File**: Which file(s) to modify
- **Estimated Effort**: Time to complete
- **Dependencies**: What must be done first
- **Phase**: Which phase to execute in (0–5)
- **Priority**: P0 (blocking), P1 (high), P2 (medium), P3 (nice-to-have)

---

## IMPL-01: Infrastructure & Platform Layer (899 lines)

### Section 1: Platform Overview & Hardware Validation

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **INF-101** | Create validation script (hardware, CPU, memory, disk, podman, kernel, network, AppArmor) | `scripts/validate_infrastructure.sh` | 15 min | 0–1 | P1 | 🔴 NEW |
| **INF-102** | Run and document hardware baseline (CPU utilization, RAM, zRAM, disk usage) | Session notes | 10 min | 0 | P2 | 🔴 NEW |
| **INF-103** | Verify Zen 2 instruction set (AVX2, FMA, SHA-NI, no AVX-512) | `scripts/verify_cpu_features.sh` | 5 min | 0 | P2 | 🔴 NEW |

---

### Section 2: CPU Optimization — Zen 2 Specifics

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **CPU-201** | Add Zen 2 optimization profile to ~/.profile | `~/.profile` | 5 min | 0 | P2 | 🔴 NEW |
| **CPU-202** | Set CPU thread count: N_THREADS=6 (thermal safety) | `~/.profile` | 2 min | 0 | P1 | 🔴 NEW |
| **CPU-203** | Configure OpenBLAS for Zen 2 ISA (OPENBLAS_CORETYPE=ZEN2) | `~/.profile` | 2 min | 0 | P2 | 🔴 NEW |
| **CPU-204** | Set OpenMP threads: OMP_NUM_THREADS=6 | `~/.profile` | 1 min | 0 | P2 | 🔴 NEW |
| **CPU-205** | Configure Node.js heap: NODE_OPTIONS="--max_old_space_size=4096" | `~/.profile` | 1 min | 0 | P2 | 🔴 NEW |
| **CPU-206** | Set Go CPU optimization: GOAMD64=v3 (AVX2 level) | `~/.profile` | 1 min | 0 | P3 | 🔴 NEW |
| **CPU-207** | Set Rust optimization: RUSTFLAGS="-C target-cpu=znver2" | `~/.profile` | 1 min | 0 | P3 | 🔴 NEW |
| **CPU-208** | Create thermal monitoring script | `scripts/monitor_cpu_temp.sh` | 10 min | 0 | P3 | 🔴 NEW |
| **CPU-209** | Test thermal behavior under load (verify <80°C, no throttle) | Session notes | 15 min | 0 | P2 | 🔴 NEW |

---

### Section 3: Memory Architecture & OOM Strategy

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **MEM-301** | Apply sysctl memory tuning (swappiness=10, dirty ratios, overcommit) | `/etc/sysctl.d/99-omega-stack.conf` | 10 min | 0 | P1 | 🔴 NEW |
| **MEM-302** | Increase inotify limits (for VS Code + systemd watchers) | `/etc/sysctl.d/99-omega-stack.conf` | 5 min | 0 | P2 | 🔴 NEW |
| **MEM-303** | Enable unprivileged port binding (for Caddy on 80/443) | `/etc/sysctl.d/99-omega-stack.conf` | 2 min | 0 | P2 | 🔴 NEW |
| **MEM-304** | Create OOM score protection script for critical containers | `scripts/set_oom_protection.sh` | 15 min | 0 | P1 | 🔴 NEW |
| **MEM-305** | Protect postgres, redis, memory-bank-mcp from OOM kill | `scripts/set_oom_protection.sh` | 10 min | 1 | P1 | 🔴 NEW |
| **MEM-306** | Apply lighter OOM protection to qdrant, rag_api (recoverable) | `scripts/set_oom_protection.sh` | 5 min | 1 | P1 | 🔴 NEW |
| **MEM-307** | Monitor memory pressure (RAM + swap usage) | `scripts/monitor_memory.sh` | 10 min | 0 | P2 | 🔴 NEW |

---

### Section 4: Storage Crisis Resolution — **P0 BLOCKING**

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **ST-001** | Create rapid assessment script (disk usage, top consumers) | `scripts/storage_assess.sh` | 10 min | 0 | 🔴 P0 | 🔴 NEW |
| **ST-002** | Run Podman prune (images, containers, volumes, build cache) | Manual | 10 min | 0 | 🔴 P0 | 🔴 NEW |
| **ST-003** | SQLite VACUUM on Podman bolt_state.db | `scripts/storage_cleanup.sh` | 5 min | 0 | 🔴 P0 | 🔴 NEW |
| **ST-004** | Journal cleanup (vacuum 7 days) | `scripts/storage_cleanup.sh` | 3 min | 0 | 🔴 P0 | 🔴 NEW |
| **ST-005** | Package cache purge (pip, npm) | `scripts/storage_cleanup.sh` | 5 min | 0 | 🔴 P0 | 🔴 NEW |
| **ST-006** | Python bytecode cleanup (__pycache__ recursion) | `scripts/storage_cleanup.sh` | 5 min | 0 | 🔴 P0 | 🔴 NEW |
| **ST-007** | Git GC --aggressive (repo compaction, 40–60% reduction) | `scripts/storage_cleanup.sh` | 15 min | 0 | 🔴 P0 | 🔴 NEW |
| **ST-008** | Temp file cleanup (/tmp, >3 days) | `scripts/storage_cleanup.sh` | 3 min | 0 | 🔴 P0 | 🔴 NEW |
| **ST-009** | Review & targeted deletion (node_modules, old logs, backups) | Manual | 20 min | 0 | 🔴 P0 | 🔴 NEW |
| **ST-010** | Verify disk <85% before proceeding to Phase 1 | Session notes | 2 min | 0 | 🔴 P0 | 🔴 NEW |
| **ST-011** | Configure logrotate for omega-stack logs | `/etc/logrotate.d/omega-stack` | 5 min | 0 | P1 | 🔴 NEW |
| **ST-012** | **[Fallback]** Storage relocation to omega_library (if >85% remains) | `~/.config/containers/storage.conf` | 60 min | 0 | P1 | 🔴 NEW |

---

### Section 5: Podman 5.x Runtime — Complete Configuration

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **POD-501** | Verify subuid/subgid entries (arcana-novai:100000:65536) | Session notes | 5 min | 0 | P1 | 🔴 NEW |
| **POD-502** | **[Fallback]** Repair subuid/subgid if missing | Manual (usermod) | 10 min | 0 | P1 | 🔴 NEW |
| **POD-503** | Test UID mapping (podman run alpine cat /proc/self/uid_map) | Manual | 5 min | 0 | P2 | 🔴 NEW |
| **POD-504** | Verify Podman uses pasta networking (not slirp4netns) | `podman info` | 2 min | 0 | P2 | 🔴 NEW |
| **POD-505** | Document pause process behavior (keeps userns=auto alive) | `docs/PODMAN_ARCHITECTURE.md` | 10 min | 0 | P3 | 🔴 NEW |
| **POD-506** | Configure Podman 5.x for rootless usage | `~/.config/containers/storage.conf` | 10 min | 0 | P1 | 🔴 NEW |
| **POD-507** | Verify OverlayFS is native (no fuse-overlayfs needed) | `podman info` | 2 min | 0 | P2 | 🔴 NEW |

---

### Section 6: Networking — pasta vs slirp4netns

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **NET-601** | Confirm Podman 5.3+ pasta fixes container-to-host comms | Session notes | 5 min | 0 | P2 | 🔴 NEW |
| **NET-602** | Test container-to-host ping (localhost:8102 from container) | Manual | 5 min | 0 | P2 | 🔴 NEW |
| **NET-603** | Document network backend in infrastructure validation | `docs/PODMAN_NETWORKING.md` | 10 min | 0 | P3 | 🔴 NEW |

---

### Section 7: OS Hardening Baseline

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **OS-701** | Verify AppArmor is enforcing (not permissive) | Session notes | 2 min | 0 | P2 | 🔴 NEW |
| **OS-702** | Apply sysctl network hardening (tcp_syncookies, rp_filter) | `/etc/sysctl.d/99-omega-stack.conf` | 5 min | 0 | P2 | 🔴 NEW |
| **OS-703** | Document kernel version and AppArmor profile | `docs/OS_HARDENING.md` | 10 min | 0 | P3 | 🔴 NEW |

---

### Section 8–11: Decision Trees, Fallback Strategies, Diagnostics, Verification

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **INF-801** | Create decision tree script (diagnose hardware issues) | `scripts/diagnose_hardware.sh` | 20 min | 0–1 | P2 | 🔴 NEW |
| **INF-802** | Implement fallback strategies (documented in code) | `docs/FALLBACK_STRATEGIES.md` | 30 min | 0 | P2 | 🔴 NEW |
| **INF-803** | Create diagnostic command reference | `docs/DIAGNOSTIC_COMMANDS.md` | 20 min | 0 | P3 | 🔴 NEW |
| **INF-804** | Create verification checklist (printable + automated) | `scripts/verify_infrastructure_complete.sh` | 15 min | 0 | P1 | 🔴 NEW |

---

## IMPL-02: Container Orchestration & Service Recovery (1,112 lines)

### Section 1: Service Inventory & Tier Classification

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **SVC-101** | Create service inventory script (lists all 25 services, tier classification) | `scripts/service_inventory.sh` | 15 min | 1 | P1 | 🔴 NEW |
| **SVC-102** | Document complete port map (5432, 6379, 6333, 8102, 8005, etc.) | `docs/SERVICE_PORTS.md` | 10 min | 1 | P2 | 🔴 NEW |
| **SVC-103** | Create service dependency graph (visual or JSON) | `docs/SERVICE_DEPENDENCIES.json` | 20 min | 1 | P2 | 🔴 NEW |

---

### Section 2: Cascade Failure Diagnosis — Decision Tree

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **DIA-201** | Create cascade failure decision tree script | `scripts/diagnose_cascade.sh` | 20 min | 1 | P1 | 🔴 NEW |
| **DIA-202** | Implement quick health check (qdrant, redis, postgres, memory-bank-mcp) | `scripts/health_check.sh` | 15 min | 1 | P1 | 🔴 NEW |

---

### Section 3: Pre-Recovery Diagnostic Protocol

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **DIA-301** | Create comprehensive diagnostic report script | `scripts/diagnose.sh` | 20 min | 1 | P1 | 🔴 NEW |
| **DIA-302** | Log disk usage, memory, swap, containers, OOM kills | `scripts/diagnose.sh` | 10 min | 1 | P1 | 🔴 NEW |
| **DIA-303** | Check dependency reachability (nc to all ports) | `scripts/diagnose.sh` | 5 min | 1 | P1 | 🔴 NEW |

---

### Section 4: Service Recovery — All 6 Unhealthy Services

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **REC-401** | **qdrant recovery** (diagnose, apply memory limit, restart, wait 90s) | `scripts/recover_qdrant.sh` | 30 min | 1 | 🔴 P0 | 🔴 NEW |
| **REC-402** | **rag_api recovery** (verify qdrant first, restart, wait 60s) | `scripts/recover_rag_api.sh` | 20 min | 1 | 🔴 P0 | 🔴 NEW |
| **REC-403** | **oikos recovery** (independent restart, verify port) | `scripts/recover_oikos.sh` | 15 min | 1 | 🔴 P0 | 🔴 NEW |
| **REC-404** | **librarian recovery** (independent restart, verify port) | `scripts/recover_librarian.sh` | 15 min | 1 | 🔴 P0 | 🔴 NEW |
| **REC-405** | **grafana recovery** (verify postgres T1, restart, verify 3000) | `scripts/recover_grafana.sh` | 20 min | 1 | 🔴 P0 | 🔴 NEW |
| **REC-406** | **caddy recovery** (verify port 80/443 binding) | `scripts/recover_caddy.sh` | 10 min | 1 | 🔴 P0 | 🔴 NEW |

---

### Section 5: qdrant WAL Corruption — Complete Recovery

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **WAL-501** | Create WAL corruption detection script (check logs, test /collections, inspect storage) | `scripts/detect_qdrant_wal_corruption.sh` | 15 min | 1 | P1 | 🔴 NEW |
| **WAL-502** | **Tier-1 recovery**: Remove lock files, retry (non-destructive) | `scripts/qdrant_wal_recovery_tier1.sh` | 15 min | 1 | 🔴 P0 | 🔴 NEW |
| **WAL-503** | **Tier-2 recovery**: Destroy + recreate volume (destructive, data loss) | `scripts/qdrant_wal_recovery_tier2.sh` | 30 min | 1 | 🔴 P0 | 🔴 NEW |
| **WAL-504** | Post-recovery: Recreate collections with correct dimensions (384 dim, Cosine) | `scripts/qdrant_wal_recovery_tier2.sh` | 10 min | 1 | 🔴 P0 | 🔴 NEW |
| **WAL-505** | Document Tier-1 vs Tier-2 decision tree | `docs/QDRANT_WAL_RECOVERY.md` | 20 min | 1 | P2 | 🔴 NEW |

---

### Section 6: Resource Limits Hardening

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **LIM-601** | Add deploy.resources blocks to docker-compose.yml (all 25 services) | `docker-compose.yml` | 45 min | 1 | 🔴 P0 | 🔴 NEW |
| **LIM-602** | Set T1 limits (postgres 768M, redis 384M, vikunja_db 256M, victoriametrics 384M) | `docker-compose.yml` | 10 min | 1 | 🔴 P0 | 🔴 NEW |
| **LIM-603** | Set T2 limits (memory-bank-mcp 768M, qdrant 768M reduced from 1G, oikos/librarian 384M) | `docker-compose.yml` | 10 min | 1 | 🔴 P0 | 🔴 NEW |
| **LIM-604** | Set T3 limits (rag_api 1024M reduced from 2G, xnai-rag 512M) | `docker-compose.yml` | 10 min | 1 | 🔴 P0 | 🔴 NEW |
| **LIM-605** | Set T4–T5 limits (grafana, mkdocs, optional services) | `docker-compose.yml` | 5 min | 1 | P1 | 🔴 NEW |
| **LIM-606** | Verify total allocation ~5.4GB (82% of 6.6GB physical) | Session notes | 5 min | 1 | P1 | 🔴 NEW |
| **LIM-607** | Create resource audit script (verify all limits applied) | `scripts/audit_resource_limits.sh` | 15 min | 1 | P2 | 🔴 NEW |

---

### Section 7: Quadlet Migration — Primary Orchestration

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **QDL-701** | Create Quadlet directory structure | `~/.config/containers/systemd/` | 5 min | 1.5 | P1 | 🔴 NEW |
| **QDL-702** | Migrate postgres to Quadlet (.container file) | `~/.config/containers/systemd/postgres.container` | 15 min | 1.5 | 🟡 P1 | 🔴 NEW |
| **QDL-703** | Migrate redis to Quadlet | `~/.config/containers/systemd/redis.container` | 15 min | 1.5 | 🟡 P1 | 🔴 NEW |
| **QDL-704** | Migrate qdrant to Quadlet | `~/.config/containers/systemd/qdrant.container` | 15 min | 1.5 | 🟡 P1 | 🔴 NEW |
| **QDL-705** | Migrate rag_api to Quadlet | `~/.config/containers/systemd/rag_api.container` | 15 min | 1.5 | 🟡 P1 | 🔴 NEW |
| **QDL-706** | Migrate memory-bank-mcp to Quadlet | `~/.config/containers/systemd/memory-bank-mcp.container` | 15 min | 1.5 | 🟡 P1 | 🔴 NEW |
| **QDL-707** | Add After=/Before= service ordering (dependency graph) | `~/.config/containers/systemd/*.container` | 20 min | 1.5 | P1 | 🔴 NEW |
| **QDL-708** | Enable systemd user session (`loginctl enable-linger`) | Manual | 5 min | 1.5 | P1 | 🔴 NEW |
| **QDL-709** | Test: systemctl --user restart redis.service | Manual | 10 min | 1.5 | P1 | 🔴 NEW |
| **QDL-710** | Test: System reboot, verify services auto-start | Manual | 15 min | 1.5 | P1 | 🔴 NEW |

---

### Section 8: Health Check Implementation

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **HLT-801** | Add healthchecks to all 25 services in docker-compose.yml | `docker-compose.yml` | 45 min | 1 | P1 | 🔴 NEW |
| **HLT-802** | Document healthcheck endpoints for each service | `docs/SERVICE_HEALTHCHECKS.md` | 20 min | 1 | P2 | 🔴 NEW |
| **HLT-803** | Test: Kill qdrant, verify marked unhealthy in 90s | Manual | 10 min | 1 | P1 | 🔴 NEW |

---

### Section 9–12: Ordered Startup, Container Lifecycle, Fallback, Verification

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **ORD-901** | Create ordered startup script (respects dependency graph) | `scripts/startup_ordered.sh` | 20 min | 1 | P2 | 🔴 NEW |
| **LIFE-1001** | Document container lifecycle management (start/stop/restart/pause) | `docs/CONTAINER_LIFECYCLE.md` | 20 min | 1 | P3 | 🔴 NEW |
| **FB-1101** | Implement fallback strategies (documented) | `docs/FALLBACK_STRATEGIES_SVC.md` | 30 min | 1 | P2 | 🔴 NEW |
| **VER-1201** | Create verification checklist (all services healthy) | `scripts/verify_services_complete.sh` | 15 min | 1 | P1 | 🔴 NEW |

---

## SUPP-02: Secrets Management & Credential Hardening (922 lines)

### Section 1: Threat Assessment & Scope

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **SEC-101** | Identify plaintext secrets (scan .env, oauth_creds.json, git history) | Manual | 10 min | 2 | 🔴 P0 | 🔴 NEW |
| **SEC-102** | Document known exposures (5 plaintext secrets + Google API key in history) | `docs/SECRETS_AUDIT.md` | 15 min | 2 | 🔴 P0 | 🔴 NEW |
| **SEC-103** | Assess blast radius (who has access to .env, git history, servers) | Session notes | 10 min | 2 | 🔴 P0 | 🔴 NEW |

---

### Section 2: Immediate Credential Rotation

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **CRED-201** | Generate 6 new cryptographically secure passwords | Manual | 5 min | 2 | 🔴 P0 | 🔴 NEW |
| **CRED-202** | Store new credentials in password manager (before applying) | Manual | 10 min | 2 | 🔴 P0 | 🔴 NEW |
| **CRED-203** | Rotate PostgreSQL password (ALTER USER + .env + restart services) | `scripts/rotate_postgres_password.sh` | 15 min | 2 | 🔴 P0 | 🔴 NEW |
| **CRED-204** | Rotate Redis password (CONFIG SET + .env + restart services) | `scripts/rotate_redis_password.sh` | 15 min | 2 | 🔴 P0 | 🔴 NEW |
| **CRED-205** | Rotate MariaDB/Vikunja password | `scripts/rotate_mariadb_password.sh` | 10 min | 2 | P1 | 🔴 NEW |
| **CRED-206** | Rotate Vikunja secret (random base64) | `.env` | 5 min | 2 | P1 | 🔴 NEW |
| **CRED-207** | Rotate Grafana admin password | Manual (Grafana API or SQL) | 10 min | 2 | P1 | 🔴 NEW |
| **CRED-208** | Verify all services healthy after rotation (no auth errors) | Manual | 10 min | 2 | 🔴 P0 | 🔴 NEW |

---

### Section 3: Git History Cleanup — Removing Exposed Secrets

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **GIT-301** | Create backup of git history before cleaning | Manual | 5 min | 2 | P1 | 🔴 NEW |
| **GIT-302** | Use git-filter-repo to remove .env files | Manual | 10 min | 2 | 🔴 P0 | 🔴 NEW |
| **GIT-303** | Use git-filter-repo to remove *.pem, *.key files | Manual | 10 min | 2 | 🔴 P0 | 🔴 NEW |
| **GIT-304** | Use git-filter-repo to remove oauth_creds.json | Manual | 5 min | 2 | 🔴 P0 | 🔴 NEW |
| **GIT-305** | Update .gitignore with secrets patterns (.env, *.pem, *.key, oauth_creds.json, credentials/) | `.gitignore` | 5 min | 2 | 🔴 P0 | 🔴 NEW |
| **GIT-306** | Force push to origin (requires user authorization) | Manual | 5 min | 2 | 🔴 P0 | 🔴 NEW |
| **GIT-307** | Notify all collaborators to re-clone | Email/chat | 5 min | 2 | P1 | 🔴 NEW |
| **GIT-308** | Verify git log clean (no password/secret/token mentions) | `scripts/verify_git_clean.sh` | 5 min | 2 | 🔴 P0 | 🔴 NEW |
| **GIT-309** | **[Fallback]** Use BFG Repo Cleaner if git-filter-repo unavailable | Manual | 30 min | 2 | P2 | 🔴 NEW |
| **GIT-310** | Revoke exposed credentials (Google API key, GitHub tokens) | Manual (consoles.cloud.google.com, github.com/settings) | 10 min | 2 | 🔴 P0 | 🔴 NEW |

---

### Section 4: Pre-commit Hooks — Prevent Future Leaks

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **PRE-401** | Install pre-commit framework | Manual | 5 min | 2 | P1 | 🔴 NEW |
| **PRE-402** | Install detect-secrets plugin | Manual | 5 min | 2 | P1 | 🔴 NEW |
| **PRE-403** | Create .pre-commit-config.yaml with detect-secrets + file checks | `.pre-commit-config.yaml` | 15 min | 2 | P1 | 🔴 NEW |
| **PRE-404** | Add custom hooks: block-.env, block-private-keys, block-default-passwords, block-oauth | `.pre-commit-config.yaml` | 20 min | 2 | P1 | 🔴 NEW |
| **PRE-405** | Create .secrets.baseline (detect-secrets baseline) | `.secrets.baseline` | 5 min | 2 | P1 | 🔴 NEW |
| **PRE-406** | Install hooks into .git/hooks/ | Manual | 5 min | 2 | P1 | 🔴 NEW |
| **PRE-407** | Test: Attempt to commit .env, verify blocked | Manual | 5 min | 2 | P1 | 🔴 NEW |
| **PRE-408** | Test: Attempt to commit private key, verify blocked | Manual | 5 min | 2 | P1 | 🔴 NEW |
| **PRE-409** | Test: Attempt to commit `changeme123`, verify blocked | Manual | 5 min | 2 | P1 | 🔴 NEW |

---

### Section 5: SOPS + age — Encrypted Secrets at Rest

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **SOPS-501** | Install age | Manual | 5 min | 2 | P1 | 🔴 NEW |
| **SOPS-502** | Install SOPS | Manual | 5 min | 2 | P1 | 🔴 NEW |
| **SOPS-503** | Generate age encryption key (age-keygen) | Manual | 5 min | 2 | P1 | 🔴 NEW |
| **SOPS-504** | Create .sops.yaml with age public key | `.sops.yaml` | 10 min | 2 | P1 | 🔴 NEW |
| **SOPS-505** | Encrypt .env → .env.encrypted | Manual | 10 min | 2 | P1 | 🔴 NEW |
| **SOPS-506** | Update docker-compose.yml to use .env.encrypted (decrypt at runtime or pre-load) | `docker-compose.yml` | 20 min | 2 | P1 | 🔴 NEW |
| **SOPS-507** | Remove .env from tracking (git rm --cached .env) | Manual | 5 min | 2 | P1 | 🔴 NEW |
| **SOPS-508** | Add .env to .gitignore | `.gitignore` | 2 min | 2 | P1 | 🔴 NEW |
| **SOPS-509** | Test: sops -d .env.encrypted → decrypts correctly | Manual | 5 min | 2 | P1 | 🔴 NEW |
| **SOPS-510** | Store age private key in secure location (e.g., ~/.age/key.txt, mode 600) | Manual | 5 min | 2 | 🔴 P0 | 🔴 NEW |

---

### Section 6: Podman Native Secrets

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **PDS-601** | Understand Podman secrets (stored at mode 600, not encrypted, only for containers) | Docs | 10 min | 2 | P3 | 🔴 NEW |
| **PDS-602** | **[Optional]** Use Podman secrets for database passwords | Manual | 20 min | 2 | P3 | 🔴 NEW |
| **PDS-603** | Create secrets: podman secret create POSTGRES_PASSWORD - | Manual | 5 min | 2 | P3 | 🔴 NEW |
| **PDS-604** | Reference in docker-compose: `postgres_password_file: /run/secrets/POSTGRES_PASSWORD` | `docker-compose.yml` | 10 min | 2 | P3 | 🔴 NEW |

---

### Section 7: oauth_creds.json — OAuth Token Hardening

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **OAUTH-701** | Secure oauth_creds.json permissions (mode 600, no ACLs for other users) | Manual | 5 min | 2 | P1 | 🔴 NEW |
| **OAUTH-702** | Verify UID 1000 only can read (no UID 100999 access) | Manual | 5 min | 2 | P1 | 🔴 NEW |
| **OAUTH-703** | Backup oauth_creds.json to secure location | Manual | 5 min | 2 | P1 | 🔴 NEW |
| **OAUTH-704** | Encrypt oauth_creds.json with SOPS (optional but recommended) | Manual | 10 min | 2 | P2 | 🔴 NEW |

---

### Section 8: API Key Rotation Procedures

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **APIKEY-801** | Document API key rotation for GitHub, Google, SambaNova, WebSearch | `docs/API_KEY_ROTATION.md` | 20 min | 2 | P1 | 🔴 NEW |
| **APIKey-802** | Identify all API keys in environment (GitHub, Google, SambaNova, etc.) | `.env` audit | 10 min | 2 | P1 | 🔴 NEW |
| **APIKEY-803** | Rotate GitHub API key | Manual (github.com/settings/tokens) | 10 min | 2 | P1 | 🔴 NEW |
| **APIKEY-804** | Rotate Google API key | Manual (console.cloud.google.com/apis/credentials) | 10 min | 2 | P1 | 🔴 NEW |
| **APIKEY-805** | Rotate SambaNova API key | Manual | 10 min | 2 | P1 | 🔴 NEW |
| **APIKEY-806** | Rotate WebSearch API key | Manual | 10 min | 2 | P1 | 🔴 NEW |

---

### Section 9: AppArmor Enforcement for Containers

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **AA-901** | Verify AppArmor is enforcing (not permissive) | Session notes | 5 min | 2 | P2 | 🔴 NEW |
| **AA-902** | Document current AppArmor profile for containers | `docs/APPARMOR_PROFILE.md` | 15 min | 2 | P3 | 🔴 NEW |
| **AA-903** | **[Optional]** Create stricter AppArmor profile for production | Manual | 60 min | 2 | P3 | 🔴 NEW |

---

### Section 10–12: Decision Tree, Fallback, Verification

| Task ID | Description | File(s) | Effort | Phase | Priority | Status |
|---------|-------------|---------|--------|-------|----------|--------|
| **SEC-1001** | Create decision tree: "What to do if credentials exposed" | `docs/SECRETS_INCIDENT_RESPONSE.md` | 20 min | 2 | P2 | 🔴 NEW |
| **SEC-1101** | Document fallback strategies (if SOPS unavailable, etc.) | `docs/FALLBACK_STRATEGIES_SEC.md` | 20 min | 2 | P3 | 🔴 NEW |
| **SEC-1201** | Create verification checklist (no plaintext secrets, git clean, hooks working) | `scripts/verify_secrets_complete.sh` | 15 min | 2 | P1 | 🔴 NEW |

---

## Summary: Total Refactoring Items by Phase

| Phase | Count | Est. Total Effort | Status |
|-------|-------|------------------|--------|
| **Phase 0 (Prep)** | 28 items | 5–6h | 🔴 BLOCKING |
| **Phase 1 (Services)** | 47 items | 5–7h | 🔴 BLOCKING |
| **Phase 1.5 (Quadlets)** | 10 items | 2–3h | 🟡 HIGH |
| **Phase 2 (Secrets)** | 51 items | 3–5h | 🔴 CRITICAL |
| **Phases 3+ (Agent, Scaling)** | Referenced in separate documents | — | 🟡 PENDING |

**Total from Sonnet Guides**: 136 refactoring items, ~15–21h effort

---

## Implementation Notes

1. **Scripting**: All bash scripts should be created in `scripts/` with `.sh` extension, shebang, and error handling
2. **Documentation**: All docs in `docs/` with clear headers, examples, and verification steps
3. **Parallelization**: Many Phase 1 items can run in parallel (services are independent)
4. **Testing**: Each item should include verification step (test the change immediately)
5. **Rollback**: Document rollback procedure for each critical item (especially secrets)

---

**Status**: READY FOR EXECUTION  
**Last Updated**: 2026-03-13 23:55 UTC
