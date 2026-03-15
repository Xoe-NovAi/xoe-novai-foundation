---
title: "Omega-Stack Glossary & Acronym Reference"
version: "1.0"
date: "2026-03-13"
purpose: "Comprehensive reference for all terms, acronyms, and concepts"
organization: "Xoe-NovAi Foundation (XNA)"
---

# Omega-Stack Glossary & Acronym Reference
## Complete Technical and Conceptual Dictionary

---

## ORGANIZATION & TERMINOLOGY

### XNA Foundation
**Full Name**: Xoe-NovAi Foundation  
**Abbreviation**: XNA  
**Alternate Names**: 
- "Xoe-NovAi" (formal)
- "XNA Foundation" (official)
- "The Foundation" (informal)

### Omega-Stack
**Definition**: The containerized 25-service platform architecture  
**Also Called**: 
- "The Stack" (informal)
- "Omega" (abbreviated)
- "XNA Foundation Stack" (formal, deprecated)
**Current Status**: Active development, Phase 1 crisis recovery

---

## TECHNICAL ARCHITECTURE TERMS

### Archon (The Oversoul)
**Definition**: The master intelligence coordinating the entire system  
**Currently**: Gemini General (facet-4) upgraded to Archon  
**Capabilities**:
- Expert-level knowledge in all 8 specialist domains
- Delegates to specialists when appropriate
- Synthesizes multi-facet outputs
- Maintains collective memory

**Reference**: ARCH-01

### Facet / Subagent
**Definition**: A specialist agent with deep expertise in one domain  
**Total Count**: 9 facets (1 Archon + 8 specialists)
**The 8 Specialists**:
1. **Researcher** (facet-1) — Literature analysis, verification, research synthesis
2. **Engineer** (facet-2) — Software architecture, code, algorithms
3. **Infrastructure** (facet-3) — Podman, Linux, systemd, networking
4. **Creator** (facet-5) — Technical writing, content, documentation
5. **DataScientist** (facet-6) — Statistics, ML, experiments
6. **Security** (facet-7) — Threat modeling, auditing, hardening
7. **DevOps** (facet-8) — SRE, monitoring, incident response
8. **General-Legacy** (facet-9) — Backward compatibility, fallback

**Archon** (facet-4) — Master coordinator (Gemini General)

**Reference**: ARCH-02

### Delegation
**Definition**: Archon assigning a task to a specialist facet  
**Three Patterns**:
1. **Native /agent** — In-session delegation within Gemini
2. **Subprocess** — Shell-based invocation via omega-facet CLI
3. **MCP Agentbus** — Async via agentbus (port 8011)

**When to Delegate**: When task needs isolated expertise, clean context, or is long-running

---

## PERMISSION SYSTEM TERMS

### UID / GID (User ID / Group ID)
**Definition**: Numeric identifiers for users/groups in Unix/Linux  
**In Omega-Stack**:
- Host user UID: **1000** (arcana-novai)
- Podman rootless container UID: **100999** (app user within container)
- This mismatch is the source of permission challenges

**Root User UID**: 0 (exists in both host and container namespaces)

### Subuid / Subgid
**Definition**: Subordinate UID/GID ranges for rootless containers  
**Omega-Stack Configuration**:
```
/etc/subuid: arcana-novai:100000:65536
/etc/subgid: arcana-novai:100000:65536
```
**Meaning**: 
- Container UID 0 (root) maps to host UID 1000
- Container UID 1 maps to host UID 100000
- Container UID 999 (app) maps to host UID 100999

### POSIX ACL (Access Control List)
**Definition**: Extended file permissions beyond traditional Unix mode (rwx)  
**Components**:
- **User entries** (u:UID:rwx) — Grant specific UID access
- **Group entries** (g:GID:rwx) — Grant specific GID access
- **Default ACLs** (d:*) — Inherited by new files in directory
- **Mask** (m:rwx) — Limits maximum permissions

**Example**:
```
user::rwx                    # File owner
user:1000:rwx               # Grant UID 1000
user:100999:rwx             # Grant UID 100999
default:user:1000:rwx       # Inherit for new files (UID 1000)
default:user:100999:rwx     # Inherit for new files (UID 100999)
```

**Reference**: IMPL-07

### ACL Commands
- `getfacl <path>` — Display ACLs on a path
- `setfacl -m` — Modify ACLs
- `setfacl -R` — Recursive (all files in directory)
- `setfacl -d` — Default ACL (inherited by new files)

### The 4-Layer Permission Model
**Layer 1**: Emergency chown (5 min, temporary)
- Quick fix for UID 1000 access
- Reverts when container writes next file
- Use when tools are completely blocked

**Layer 2**: POSIX Default ACLs (permanent)
- `setfacl -Rdm u:1000:rwx,u:100999:rwx,m:rwx ~/.gemini`
- Persists across container writes
- Inherited by new files automatically

**Layer 3**: Podman --userns=keep-id (prevention)
- Ensures UID 999 always maps to 100999 (not random)
- Prevents regression from UID drift
- Replaces non-deterministic `--userns=auto`

**Layer 4**: Systemd Self-Healing Timer (ongoing)
- Hourly check/repair of ACLs
- Uses Ed25519 DID cryptographic verification
- Automatic recovery from chmod/other breakage

**Reference**: IMPL-07

---

## CONTAINERIZATION TERMS

### Podman
**Definition**: Daemonless container engine (Docker alternative)  
**Key Feature**: Rootless support (runs containers as non-root user)  
**Current Version**: 5.4.2  
**Key Commands**:
- `podman ps` — List containers
- `podman inspect` — Inspect container details
- `podman stats` — Container resource usage
- `podman logs` — Container output

### Quadlet
**Definition**: Systemd-native container definition format  
**Benefit**: Native integration with systemd, simpler lifecycle  
**File Location**: `~/.config/containers/systemd/*.container`  
**Example**:
```
[Container]
Image=redis:latest
PublishPort=6379:6379
```

**Status in Omega-Stack**: Replacing podman-compose in Phase 4

**Reference**: IMPL-02 §5

### Pod / Container Group
**Definition**: Group of containers that share network namespace  
**Omega-Stack**: 8 pods containing 25 total services  
**Example Pod**: Pod 1 contains qdrant (vector database)

### --userns=keep-id vs auto
**keep-id**:
- Deterministic UID mapping
- Same UID mapping after reboot
- **Recommended for Omega-Stack**

**auto**:
- Non-deterministic (different UID after reboot)
- First-come, first-served allocation
- **Avoid — causes problems**

**Reference**: IMPL-07 §1.3

### Volume Mount Flags
**:Z** — SELinux relabel (NOT applicable on AppArmor systems)  
**:z** — AppArmor relabel (use this on Ubuntu)  
**:U** — Auto-chown to container user (idempotent within Layer 4)  
**:RO** — Read-only mount

---

## STORAGE & FILESYSTEM TERMS

### Root Filesystem (/)
**Definition**: Main system drive  
**Omega-Stack**:
- Size: 117 GB
- Current: 93% full (CRITICAL)
- Target: <80% usage

### omega_library
**Definition**: External mounted drive for project/documentation storage  
**Size**: 110 GB  
**Path**: `/media/arcana-novai/omega_library/`  
**Usage**: Current projects, documentation, archives  
**Current**: 40% used (healthy)

### omega_vault
**Definition**: External mounted drive for backups and compliance archives  
**Size**: 16 GB  
**Path**: `/media/arcana-novai/omega_vault/`  
**Usage**: Backups, GDPR evidence, compliance records  
**Current**: 75% used (approaching capacity)

### Tiered Storage Strategy
**Tier 1 (Hot)**: Root filesystem `/` — Active data, <70% usage  
**Tier 2 (Warm)**: omega_library — Year-old projects, archives  
**Tier 3 (Cold)**: omega_vault — Backups, compliance archives  
**Tier 4 (External)**: Cloud storage (S3-compatible) — Redundant/offsite

---

## SECURITY TERMS

### AppArmor
**Definition**: Mandatory Access Control system (Ubuntu default)  
**Current Status**: Permissive mode (not enforcing)  
**Target**: Enforce mode (Phase 4)  
**Key Commands**:
- `aa-status` — Check status
- `aa-enforce` — Enable enforcement
- `aa-complain` — Permissive mode

**NOT SELinux** — Different system, different rules

**Reference**: SUPP-02 §8

### SOPS (Secrets Operations)
**Definition**: Encrypts secrets at rest with age encryption  
**Key Features**:
- Keeps .env files in git but encrypted
- Rotation-friendly (monthly key changes)
- Audit trail (records all access)

**Reference**: SUPP-02 §2

### Ed25519
**Definition**: Cryptographic signature algorithm  
**Usage in Omega-Stack**: Layer 4 self-healing timer verification  
**Key Size**: 32 bytes (256 bits)  
**Benefits**: Smaller than RSA, faster verification

### DID (Decentralized Identifier)
**Definition**: Cryptographic identity credential  
**In Omega-Stack**: Per-facet Ed25519 identity  
**Purpose**: Proves agent identity, enables A2A (agent-to-agent) authentication  
**Example**: `did:omega:researcher:ed25519:...`

---

## MONITORING & OBSERVABILITY TERMS

### Prometheus
**Definition**: Metrics collection and storage system  
**In Omega-Stack**: Port 9090  
**Metrics**: CPU, memory, disk, network per service

### VictoriaMetrics
**Definition**: Time-series database optimized for Prometheus metrics  
**In Omega-Stack**: Stores long-term metrics  
**Benefit**: Higher compression, better performance at scale

### Grafana
**Definition**: Visualization dashboard system  
**In Omega-Stack**: Port 3000  
**Current Status**: Down (needs restoration Phase 2)  
**Dashboards**: 18 panels for system monitoring  
**Use**: Real-time visualization of system health

### SLI / SLO
**SLI** (Service Level Indicator): Measurable metric (e.g., "p95 latency <500ms")  
**SLO** (Service Level Objective): Target value (e.g., "99.9% uptime")  
**Usage**: Define what "healthy" means for each service

### oom-killer
**Definition**: Linux kernel process that kills services when RAM exhausted  
**Risk**: Can kill critical services unexpectedly  
**Prevention**: Memory limits, oom_score_adj settings  
**Symptom in Logs**: `Killed` with high memory usage

---

## DEVELOPMENT TOOL TERMS

### The 7 Dev Tools
**All Currently EACCES Blocked**:
1. **Cline** — AI-powered IDE extension
2. **Copilot** — GitHub Copilot integration
3. **Gemini** — Google Gemini integration
4. **VS Code** — Visual Studio Code editor
5. **Node.js** — JavaScript/TypeScript runtime
6. **Python** — Python runtime
7. **Bash** — Shell scripting

**Block Cause**: UID 100999 files inaccessible to UID 1000  
**Solution**: IMPL-07 (4-Layer Permission Model)

---

## SERVICE TERMS

### The 25 Services
**Critical Services** (P0):
- **memory-bank-mcp** (port 8005) — State hub, cross-facet memory
- **qdrant** — Vector database for embeddings
- **postgres** — Relational database

**Database/Cache Services** (P1):
- **redis** (port 6379) — Cache and queue
- **rabbitmq** — Message broker
- **minio** — Object storage (S3-compatible)

**Observability Stack** (P1):
- **prometheus** (port 9090) — Metrics collection
- **victoriametrics** — Time-series database
- **grafana** (port 3000) — Dashboards

**Web/Crawling Services** (P2):
- **crawl4ai** — Web scraping and content extraction
- Plus 13 others (various specialized functions)

**Current Status**: 6 unhealthy (Phase 2 to fix)

### Port Numbering Convention
**8005-8014**: MCP servers (memory-bank at 8005)  
**6379**: Redis  
**5432**: PostgreSQL  
**9000**: MinIO  
**9090**: Prometheus  
**3000**: Grafana  
**15672**: RabbitMQ Management  

---

## PHASE & TIMELINE TERMS

### The 5 Phases
**Phase 1 — Unblock** (2 hrs)  
- Storage crisis + permissions + password rotation
- Target: Restore development capability

**Phase 2 — Stabilize** (4 hrs)  
- Service recovery + resource limits + monitoring  
- Target: Stop cascading failures

**Phase 3 — Archon** (3 hrs)  
- Deploy agent orchestration system  
- Target: Activate 9-facet Archon pattern

**Phase 4 — Harden** (1 week)  
- Secrets encryption + AppArmor + SLOs  
- Target: Enterprise baseline security

**Phase 5 — Enterprise** (1 month)  
- Backups + DID registry + SOC2 audit  
- Target: Compliance readiness

---

## COMPLIANCE & AUDIT TERMS

### SOC2 Type II
**Definition**: Security audit certification  
**Trust Service Categories**: 17 categories covering security, availability, integrity  
**Omega-Stack Target**: Phase 5 (eligible for audit)

### GDPR (General Data Protection Regulation)
**Definition**: EU data protection regulation  
**Key Requirements**:
- Data subject rights (access, deletion, export)
- Breach notification (72 hours)
- Privacy by design
- Data minimization

**Omega-Stack Target**: Phase 5 implementation

### Audit Trail
**Definition**: Complete log of all changes and who made them  
**Requirements**:
- Timestamp (when)
- Actor (who)
- Action (what)
- Result (outcome)
- Signature (cryptographic verification)

---

## ACRONYM QUICK REFERENCE

| Acronym | Full Name | Context |
|---------|-----------|---------|
| XNA | Xoe-NovAi Foundation | Organization |
| ACL | Access Control List | Permissions |
| UID | User ID | Unix/Linux identity |
| GID | Group ID | Unix/Linux group identity |
| MCP | Model Context Protocol | Integration protocol |
| POSIX | Portable OS Interface | Unix/Linux standard |
| SELinux | Security-Enhanced Linux | Mandatory AC (not used here) |
| AppArmor | Application Armor | Mandatory AC (used here) |
| SOPS | Secrets Operations | Secret encryption |
| DID | Decentralized Identifier | Agent identity |
| SLI | Service Level Indicator | Performance metric |
| SLO | Service Level Objective | Performance target |
| OOM | Out of Memory | Memory exhaustion |
| zRAM | Compressed RAM | Swap compression |
| A2A | Agent-to-Agent | Service communication |
| EC2 | Elastic Compute Cloud | AWS (reference) |
| GDPR | General Data Protection Regulation | EU law |
| SOC2 | Service Organization Control 2 | Audit standard |

---

## REFERENCE GUIDE

### Finding Information
- **Architecture**: ARCH-01, ARCH-02
- **Infrastructure**: IMPL-01
- **Containers**: IMPL-02
- **Permissions**: IMPL-07
- **Secrets**: SUPP-02
- **Monitoring**: SUPP-06
- **Backups**: SUPP-07

### Common Procedures
- **Permission fix**: IMPL-07 (4 layers)
- **Service recovery**: IMPL-02 §3
- **Secret rotation**: SUPP-02 §2
- **Disk cleanup**: IMPL-01 §4
- **Memory management**: IMPL-02 §4

### Quick Diagnostics
- `df -h /` — Disk space
- `free -h` — Memory status
- `podman ps` — Container status
- `systemctl list-units --type=service | grep omega` — Service status
- `getfacl ~/.gemini` — Check ACLs

---

**Last Updated**: 2026-03-13  
**For Questions**: Refer to specific manual listed under each term  
**Status**: ACTIVE reference document  

