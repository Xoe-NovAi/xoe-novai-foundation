---
title: "Omega-Stack Master Implementation Index"
type: "navigation"
status: "Living Document — v2"
owner: "arcana-novai (UID 1000)"
last_updated: "2026-03-13"
gemini_review: "Gemini 3.1 Pro validated — 6 critical corrections integrated"
total_manuals: 15
---

# Omega-Stack Master Implementation Index
## Agent Navigation & Execution Guide — v2

> **🤖 AGENT DIRECTIVE:** This is the single source of truth for execution order. Read this before opening any other document. New in v2: **ARCH-01** (Archon design) and **ARCH-02** (facet orchestration CLI) — these are required reading before implementing the facet system.

---

## Critical Situation Summary

| Issue | Severity | Manual |
|-------|---------|--------|
| Root filesystem 93% full | 🔴 P0 | IMPL-01 §4 |
| All 7 dev tools EACCES blocked | 🔴 P0 | IMPL-07 |
| 6 unhealthy services blocking API | 🔴 P0 | IMPL-02 §3 |
| Memory 350% overcommit + OOM risk | 🟠 P1 | IMPL-02 §4, IMPL-08 |
| 5 plaintext default passwords | 🟠 P1 | SUPP-02 |
| No monitoring, Grafana down | 🟠 P1 | SUPP-06 |
| Facets inaccessible (permissions) | 🟠 P1 | IMPL-07 → IMPL-04 |
| No backup strategy | 🟡 P2 | SUPP-07 |
| AppArmor permissive | 🟡 P2 | SUPP-02 §8 |

---

## Execution Order

```
PHASE 1 — Unblock (Day 1, ~2 hours)
├── IMPL-01 §4    Storage crisis: free 20+ GB
├── IMPL-07 L1    Emergency chown (unblocks all 7 dev tools in ~5 min)
├── IMPL-07 L2    POSIX Default ACLs (makes it permanent)
├── IMPL-07 L4    Systemd timer (self-healing)
└── SUPP-02 §2    Rotate default passwords (changeme123 → secure)

PHASE 2 — Stabilize (Day 1–2, ~4 hours)
├── IMPL-02 §3    Recover 6 unhealthy services (qdrant first)
├── IMPL-02 §4    Add resource limits (prevent OOM cascade)
├── IMPL-07 L3    Podman keep-id (prevent future UID drift)
└── SUPP-06 §2    Restore VictoriaMetrics + alerting

PHASE 3 — Archon & Facets (Day 2–3, ~3 hours)
├── ARCH-01       Deploy Archon identity (GEMINI.md + 8 subagent files)
├── ARCH-02 §2    Install omega-facet CLI
├── IMPL-04 §6    Initialize all 9 instance directories
└── IMPL-04 §5    Verify per-facet permissions

PHASE 4 — Harden (Week 1)
├── IMPL-02 §5    Migrate to Quadlets (replace podman-compose)
├── SUPP-02       Full SOPS+age secrets management
├── SUPP-06       Complete monitoring stack
└── IMPL-01 §7    OS hardening baseline

PHASE 5 — Enterprise Grade (Month 1)
├── SUPP-02 §8    AppArmor enforcement
├── ARCH-01 §5    Ed25519 DID agent registry
├── SUPP-07       Backup automation (all 3 tiers)
└── IMPL-09       Full stack verification (target: 100% pass)
```

---

## All Documents

### Architecture Manuals (NEW in v2)

| Manual | Title | Priority | Key Content |
|--------|-------|---------|------------|
| **[ARCH-01](./ARCH_01_OVERSOUL_ARCHON.md)** | **Gemini General as Archon — Oversoul Pattern** | **P1** | GEMINI.md template, all 8 subagent .md files, delegation logic, memory architecture |
| **[ARCH-02](./ARCH_02_FACET_ORCHESTRATION.md)** | **Facet Orchestration — CLI, Delegation, Subagent Patterns** | **P1** | `omega-facet` CLI full implementation, 3 invocation patterns, Makefile targets, context passing |

### Core Implementation Manuals

| Manual | Title | Priority | Status |
|--------|-------|---------|--------|
| [IMPL-01](./IMPL_01_INFRASTRUCTURE.md) | Infrastructure & Platform Layer | P0 | Complete |
| [IMPL-02](./IMPL_02_CONTAINER_ORCHESTRATION.md) | Container Orchestration & Service Recovery | P0 | Complete |
| [IMPL-03](./IMPL_03_MCP_ECOSYSTEM.md) | MCP Server Ecosystem | P1 | Complete |
| **[IMPL-04](./IMPL_04_FACET_ARCHITECTURE.md)** | **Facet Instance Architecture** | **P1** | **Rewritten with Archon** |
| [IMPL-05](./IMPL_05_TOOL_INTEGRATION.md) | Development Tool Integration | P1 | Complete |
| [IMPL-06](./IMPL_06_FILESYSTEM_ARCHITECTURE.md) | Filesystem Architecture | P1 | Complete |
| **[IMPL-07](./IMPL_07_PERMISSIONS_4LAYER.md)** | **4-Layer Permission Resolution** | **P0** | **Primary Fix** |
| [IMPL-08](./IMPL_08_ENV_CONSTRAINTS.md) | Environment Constraints | P1 | Complete |
| [IMPL-09](./IMPL_09_VERIFICATION.md) | Verification & Confidence Suite | P2 | Complete |
| [IMPL-10](./IMPL_10_MASTER_DEPLOYMENT.md) | Master Deployment Orchestration | P0 | Complete |

### Supplemental Hardening Manuals

| Manual | Title | Priority | Status |
|--------|-------|---------|--------|
| [SUPP-02](./SUPP_02_SECRETS_MANAGEMENT.md) | Secrets Management & Credential Hardening | P1 | Complete |
| [SUPP-06](./SUPP_06_MONITORING_ALERTING.md) | Monitoring, Alerting & Observability | P1 | Complete |
| [SUPP-07](./SUPP_07_BACKUP_RECOVERY.md) | Backup, Recovery & Business Continuity | P2 | Complete |

---

## Six Critical Corrections (Gemini 3.1 Pro + Research)

1. **`--userns=auto` non-deterministic** → Use `--userns=keep-id` (IMPL-07 L3, IMPL-02 §5)
2. **Ubuntu ext4 ACLs already enabled** → No fstab change needed (IMPL-07 L2)
3. **`:Z` flag is SELinux-only** → No-op on AppArmor; use `:z` for AppArmor label (all volume docs)
4. **Quadlets > podman-compose** → Promoted to primary orchestration (IMPL-02 §5)
5. **chmod recalculates ACL mask** → `chmod 600` silently revokes named-user ACLs; Layer 4 repairs (IMPL-07 §8)
6. **SQLite VACUUM after disk crisis** → After >90% disk, Podman metadata fragments; vacuum after cleanup (IMPL-01 §4.2)

---

## The Archon System — Quick Reference

```
Gemini General (facet-4) is the Archon — Polymath Oversoul
  System prompt: ~/omega-stack/GEMINI.md
  Subagents: ~/.gemini/agents/*.md (8 files)
  Settings: enableAgents: true
  
To start an Archon session:
  cd ~/Documents/Xoe-NovAi/omega-stack && gemini

To spawn a specialist:
  omega-facet spawn researcher
  omega-facet spawn security

To delegate a task:
  omega-facet delegate security "Audit .env for plaintext credentials" /tmp/audit.md

To synthesize multiple facet reports:
  omega-facet synthesize /tmp/security.md /tmp/engineer.md "Create unified plan"

In-session subagent delegation:
  /agent researcher Survey recent Podman security advisories
  (or: Archon auto-routes via generalist agent v0.32.0+)
```

---

## Quick Command Reference

```bash
# Full health check
bash ~/Documents/Xoe-NovAi/omega-stack/scripts/monitoring/omega_health.sh

# Emergency permission restore
bash ~/Documents/Xoe-NovAi/omega-stack/scripts/permissions/layer1_restore.sh

# Deploy all 4 permission layers
bash ~/Documents/Xoe-NovAi/omega-stack/scripts/permissions/deploy_all_layers.sh

# Facet management
omega-facet list                            # All facets + status
omega-facet status                          # Backend + subagent check
omega-facet activate archon                 # Switch to Archon
omega-facet spawn researcher               # Start Researcher session
omega-facet delegate security "<task>"      # Delegate & capture output
omega-facet memory show                     # Show world model
omega-facet synthesize f1.md f2.md "<task>" # Archon synthesis

# Stack management
podman ps --format "table {{.Names}}\t{{.Status}}"
systemctl --user list-timers --no-pager
journalctl --user -t omega-alert -n 10 --no-pager
```

---

> **📋 START HERE:**
> 1. Read this index
> 2. Execute `IMPL-01 §4` (storage cleanup — P0)
> 3. Execute `IMPL-07` all 4 layers (permission fix — P0)
> 4. Read `ARCH-01` + `ARCH-02` (Archon design — P1)
> 5. Execute `IMPL-04 §6` (initialize all instances — P1)
