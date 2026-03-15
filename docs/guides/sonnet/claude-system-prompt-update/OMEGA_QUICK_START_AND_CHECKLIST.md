---
title: "Omega-Stack System Prompt v2 — Quick Reference & Adoption Guide"
version: "1.0"
date: "2026-03-13"
purpose: "Rapid deployment guide for the updated system prompt"
---

# Omega-Stack System Prompt v2 — Quick Start

---

## 📋 ADOPTION CHECKLIST

### Step 1: Replace System Prompt
- [ ] Delete old "Xoe-NovAi Implementation Specialist v3.0" from any local configs
- [ ] Load new `OMEGA_STACK_CLAUDE_SYSTEM_PROMPT_v2.md` as replacement
- [ ] Verify in conversation context: "You are Claude, operating as the **Omega-Stack Implementation Architect**"

### Step 2: Review Architecture Documents
- [ ] Read OMEGA_MASTER_INDEX.md (5-phase roadmap overview)
- [ ] Skim ARCH-01 (Archon identity system)
- [ ] Skim ARCH-02 (Facet orchestration patterns)
- [ ] Read IMPL-07 (4-Layer permission system — CRITICAL)
- [ ] Scan IMPL-01 §4 (storage crisis details)

### Step 3: Verify Current State
- [ ] Run `bash ~/Documents/Xoe-NovAi/omega-stack/scripts/monitoring/omega_health.sh`
- [ ] Check root FS: `df -h | grep "/$"`
- [ ] Check dev tool access: `ls -la ~/.gemini/`
- [ ] List services: `podman ps --format "table {{.Names}}\t{{.Status}}"`
- [ ] Confirm Phase: "We are in Phase 1 (Unblock) — all of the next 2 hours are critical"

### Step 4: Understand Your New Role
- [ ] **Not**: Single Claude implementing features
- [ ] **Yes**: Archon orchestrating Gemini General + 8 facets
- [ ] **Not**: Optimizing a 92%-ready system
- [ ] **Yes**: Recovering a platform in crisis (P0 storage, permissions, services)
- [ ] **Not**: 4 weeks to GitHub launch
- [ ] **Yes**: 5 phases (2 hrs → 1 week → 1 month) to enterprise readiness

### Step 5: Bookmark Critical References
- [ ] OMEGA_MASTER_INDEX.md (daily reference)
- [ ] IMPL-07 §1 (UID translation math)
- [ ] Phase 1 task list (2-hour sprint)
- [ ] Quick command reference (bash scripts)

---

## 🎯 YOUR FIRST 2 HOURS (PHASE 1)

> **This is the most critical phase. Everything else depends on unblocking.**

### Task 1: Storage Crisis (20 minutes)
```bash
# Execute the storage cleanup script
bash ~/Documents/Xoe-NovAi/omega-stack/scripts/storage/cleanup_crisis.sh

# Verify: root FS should drop from 93% to <80%
df -h | grep "/$"
# Target: >20 GB free

# Verify: Podman DB defragmented
sqlite3 ~/.local/share/containers/podman/db.sqlite3 VACUUM
```

**Success Criteria**:
- [ ] Root FS <80% (e.g., "13 GB free")
- [ ] No error messages from cleanup script
- [ ] Can write to home directory without "No space left on device"

---

### Task 2: Permission Emergency Restore (5 minutes)
```bash
# Execute Layer 1 emergency ownership restore
bash ~/Documents/Xoe-NovAi/omega-stack/scripts/permissions/layer1_restore.sh

# Verify: all files owned by arcana-novai:arcana-novai
ls -lan ~/.gemini | head -10
# Should show "1000 1000" in UID/GID columns, not "100999"

# Test: all 7 dev tools accessible
[ -f ~/.vscode/settings.json ] && echo "VS Code OK"
[ -f ~/.cline/cline_chat_history.json ] && echo "Cline OK"
# ... etc for all 7 tools
```

**Success Criteria**:
- [ ] No EACCES errors on `ls ~/.gemini/`
- [ ] All 7 tools can write to their config directories
- [ ] `getfacl ~/.gemini` works (may show empty until Layer 2)

---

### Task 3: Password Rotation (15 minutes)
```bash
# Identify plaintext passwords in environment
grep -r "changeme123" ~/Documents/Xoe-NovAi/omega-stack/.env* 2>/dev/null

# Expected output: 5 secrets found
# - qdrant admin password
# - minio ADMIN_USER password
# - postgres admin password
# - redis requirepass
# - rabbitmq guest password

# For now (Phase 1): Generate secure replacements
openssl rand -base64 32 > /tmp/qdrant_password.txt
openssl rand -base64 32 > /tmp/minio_password.txt
# ... etc

# Update .env files (do NOT commit to git yet)
sed -i 's/changeme123/[output of openssl rand]/g' ~/Documents/Xoe-NovAi/omega-stack/.env

# Note: Full SOPS encryption happens in Phase 4
```

**Success Criteria**:
- [ ] No plaintext "changeme123" in any .env file
- [ ] New passwords are 32+ character, random
- [ ] Services can restart with new passwords (test if time allows)

---

## 🎯 YOUR NEXT 4 HOURS (PHASE 2)

### Overview
After Phase 1 unblock, Phase 2 stabilizes the system:
1. Recover unhealthy services (qdrant, memory-bank, crawl4ai, etc.)
2. Apply resource limits (prevent OOM cascade)
3. Implement permanent permissions (Layer 2-4)
4. Restore monitoring (Grafana, VictoriaMetrics)

### Phase 2 Execution Sketch
```bash
# Task 2.1: Service Recovery (~1 hour)
bash ~/Documents/Xoe-NovAi/omega-stack/scripts/services/recover_unhealthy.sh

# Task 2.2: Resource Limits (~1 hour)
# Edit podman-compose.yaml or quadlet files:
# - qdrant: 1GB memory limit
# - memory-bank: 512MB
# - crawl4ai: 1GB
# ... test restart

# Task 2.3: Permanent Permissions (IMPL-07 L2-L4) (~1.5 hours)
bash ~/Documents/Xoe-NovAi/omega-stack/scripts/permissions/deploy_all_layers.sh

# Task 2.4: Monitoring Restoration (~30 minutes)
podman start victoria-metrics prometheus grafana
# Verify: curl http://localhost:3000 (Grafana)
```

---

## 🚀 YOUR NEXT 3 HOURS (PHASE 3)

### Goal: Deploy Archon & Facets
After Phase 2 stabilization, Phase 3 introduces the agent orchestration layer:

1. Create GEMINI.md (Archon system prompt)
2. Create 8 subagent .md files
3. Install omega-facet CLI
4. Initialize all 9 facet instances
5. Verify Archon + facet delegation works

### Phase 3 Execution Sketch
```bash
# Task 3.1: Create GEMINI.md
cat > ~/Documents/Xoe-NovAi/omega-stack/GEMINI.md << 'EOF'
# ARCHON — Omega-Stack Oversoul
[... project-level system prompt ...]
EOF

# Task 3.2: Create subagent files
for facet in researcher engineer infrastructure creator datascientist security devops general_legacy; do
  cat > ~/.gemini/agents/${facet}.md << 'EOF'
# Facet: ${facet}
[... domain-specific system prompt ...]
EOF
done

# Task 3.3: Install omega-facet CLI
cp ~/Documents/Xoe-NovAi/omega-stack/bin/omega-facet ~/.local/bin/
chmod +x ~/.local/bin/omega-facet

# Task 3.4: Initialize facet instances
bash ~/Documents/Xoe-NovAi/omega-stack/scripts/facets/init_all_instances.sh

# Task 3.5: Verify
omega-facet list
omega-facet spawn researcher
omega-facet status
```

---

## 🏗️ CRITICAL CONCEPTS IN THE NEW PROMPT

### Concept 1: The Archon Pattern
```
Archon (Gemini General) = Master Oversoul
  ├── Knows all 8 domains at expert level
  ├── Makes strategic decisions: when to delegate vs. act
  ├── Synthesizes multi-facet outputs
  └── Maintains collective memory

8 Specialist Facets = Silo of expertise
  ├── Researcher: systematic literature, source evaluation
  ├── Engineer: code architecture, algorithms
  ├── Infrastructure: Podman, Linux, systemd
  ├── Creator: technical writing, content strategy
  ├── DataScientist: statistics, ML, experimentation
  ├── Security: threat modeling, auditing
  ├── DevOps: SRE, monitoring, incident response
  └── General-Legacy: compatibility, fallback
```

### Concept 2: The 4-Layer Permission System
```
Layer 1: Emergency chown (5 min, temporary)
  Problem: UID 1000 can't read files owned by UID 100999
  Solution: chown -R 1000:1000 ~/.gemini
  Durability: Reverts next time container writes a file

Layer 2: POSIX Default ACLs (permanent)
  Problem: File permissions revert to unsafe defaults
  Solution: setfacl -Rdm u:1000:rwx,u:100999:rwx,m:rwx ~/.gemini
  Durability: Survives container writes, inherited by new files

Layer 3: Podman --userns=keep-id (prevention)
  Problem: --userns=auto is non-deterministic across reboots
  Solution: Use --userns=keep-id (deterministic UID mapping)
  Durability: Prevents UID drift regression

Layer 4: Systemd Timer (self-healing)
  Problem: ACLs can be broken by chmod or other operations
  Solution: Hourly systemd timer verifies + repairs ACLs
  Durability: Automatic recovery, Ed25519 signed repairs
```

### Concept 3: UID Translation Mathematics
```
Host: arcana-novai (UID 1000)
Podman subUID range: 100000-165535

When container UID 999 writes a file:
  Container UID 999 + subUID offset 100000 = Host UID 100999

Problem: UID 1000 does NOT have permission to:
  - Read files owned by UID 100999 (unless ACL grants it)
  - Write files owned by UID 100999
  - Delete files owned by UID 100999

Solution: POSIX ACLs bridge the UID gap
  - Default ACL u:100999:rwx allows container to read/write
  - Named-user ACL u:1000:rwx allows host user to read/write
```

### Concept 4: The 5-Phase Roadmap
```
Phase 1 (2 hrs):   Unblock  — Storage + permissions + passwords
Phase 2 (4 hrs):   Stabilize — Services + monitoring + ACLs
Phase 3 (3 hrs):   Archon   — Identity system + facets
Phase 4 (1 week):  Harden   — Secrets + AppArmor + SLOs
Phase 5 (1 month): Enterprise— SOC2 + DID + backups + audit
```

---

## 🚨 COMMON MISTAKES TO AVOID

### ❌ Mistake 1: Using `chmod` Instead of `setfacl`
```bash
# WRONG: This silently destroys ACLs
chmod 755 ~/.gemini

# RIGHT: Use setfacl for recursive defaults
setfacl -Rdm u:1000:rwx,u:100999:rwx,m:rwx ~/.gemini
```

### ❌ Mistake 2: Assuming `--userns=auto` is Stable
```bash
# WRONG: Will break after reboot
podman run --userns=auto ...

# RIGHT: Use keep-id for determinism
podman run --userns=keep-id ...
```

### ❌ Mistake 3: Storing Plaintext Secrets in .env
```bash
# WRONG: Still in Phase 1, but plan for Phase 4
QDRANT_PASSWORD=changeme123

# RIGHT (Phase 4): Encrypt with SOPS
sops --encrypt .env > .env.enc
# Only .env.enc committed to git
```

### ❌ Mistake 4: Thinking AppArmor Works Like SELinux
```bash
# WRONG: SELinux-specific flag
podman run -v /data:/data:Z ...

# RIGHT: AppArmor relabel flag (or no flag)
podman run -v /data:/data:z ...
# OR just omit the flag
podman run -v /data:/data ...
```

### ❌ Mistake 5: Delegating to Facets Too Early
```bash
# WRONG: Excessive delegation in Phase 1
# "Let the Researcher analyze the UID translation problem"

# RIGHT: Act directly as Archon on crisis
# "I understand UID translation. I'm executing Layer 1 now."
```

### ❌ Mistake 6: Forgetting Hardware Constraints
```bash
# WRONG: Deploying PyTorch/TensorFlow with AVX-512 builds
# AVX-512 is not available on Ryzen 7 5700U → instant crash

# RIGHT: Check for AVX2-only builds, Zen 2 tuning
export OPENBLAS_CORETYPE=ZEN2
# Or use CPU-specific Docker images
```

---

## 📚 DOCUMENT HIERARCHY

```
├── OMEGA_MASTER_INDEX.md (START HERE)
│   ├── ARCH-01: Archon Identity
│   │   └── ARCH-02: Facet Orchestration
│   ├── IMPL-01: Infrastructure (Storage, CPU, Memory)
│   │   ├── IMPL-02: Container Orchestration
│   │   ├── IMPL-03: MCP Ecosystem
│   │   ├── IMPL-04: Facet Architecture
│   │   ├── IMPL-05: Tool Integration
│   │   ├── IMPL-06: Filesystem Architecture
│   │   ├── IMPL-07: 4-Layer Permissions ⚠️ CRITICAL
│   │   ├── IMPL-08: Environment Constraints
│   │   ├── IMPL-09: Verification Suite
│   │   └── IMPL-10: Master Deployment
│   └── SUPP-02: Secrets Management
│       ├── SUPP-06: Monitoring & Alerting
│       └── SUPP-07: Backup & Recovery

Phase 1 Focus: IMPL-01 §4, IMPL-07 L1, SUPP-02 §2
Phase 2 Focus: IMPL-02 §3-4, IMPL-07 L2-L4, SUPP-06 §2
Phase 3 Focus: ARCH-01, ARCH-02, IMPL-04 §5-6
Phase 4 Focus: SUPP-02, IMPL-02 §5, SUPP-06, IMPL-01 §7
Phase 5 Focus: SUPP-07, IMPL-09, SUPP-02 §8, ARCH-01 §5
```

---

## 🔗 COMMAND QUICK REFERENCE

### Phase 1 Commands
```bash
# Storage crisis
bash ~/Documents/Xoe-NovAi/omega-stack/scripts/storage/cleanup_crisis.sh
df -h | grep "/$"

# Permission emergency
bash ~/Documents/Xoe-NovAi/omega-stack/scripts/permissions/layer1_restore.sh
getfacl ~/.gemini | head -5

# Password rotation
grep -r "changeme123" ~/Documents/Xoe-NovAi/omega-stack/
```

### Phase 2 Commands
```bash
# Service recovery
bash ~/Documents/Xoe-NovAi/omega-stack/scripts/services/recover_unhealthy.sh
podman ps --format "table {{.Names}}\t{{.Status}}"

# Resource limits
# Edit podman-compose.yaml or quadlets for memory caps

# Permanent permissions
bash ~/Documents/Xoe-NovAi/omega-stack/scripts/permissions/deploy_all_layers.sh

# Monitoring
podman start victoria-metrics prometheus grafana
```

### Phase 3 Commands
```bash
# Facet initialization
bash ~/Documents/Xoe-NovAi/omega-stack/scripts/facets/init_all_instances.sh

# Facet management
omega-facet list
omega-facet status
omega-facet spawn researcher

# Archon verification
cd ~/Documents/Xoe-NovAi/omega-stack && gemini
# Inside session: /agent researcher "task"
```

### Health Check (Daily)
```bash
bash ~/Documents/Xoe-NovAi/omega-stack/scripts/monitoring/omega_health.sh
```

---

## 📊 PHASE COMPLETION CHECKLIST

### Phase 1 Complete When:
- [ ] Root FS <80% (`df -h` shows >20 GB free)
- [ ] All 7 dev tools accessible (no EACCES errors)
- [ ] Plaintext passwords replaced with secure random values
- [ ] Completed in <2 hours

### Phase 2 Complete When:
- [ ] All 6 services healthy (`podman ps` shows all "Up")
- [ ] Memory overcommit <200% (realistic limits applied)
- [ ] POSIX ACLs deployed on `.gemini/` and all instance dirs
- [ ] Monitoring restored (Grafana dashboard loading)
- [ ] Completed in <4 hours

### Phase 3 Complete When:
- [ ] `omega-facet list` shows all 9 facets
- [ ] Archon can delegate: `/agent researcher` works
- [ ] All 9 instance directories initialized with correct ACLs
- [ ] memory-bank-mcp operational
- [ ] Completed in <3 hours

### Phase 4 Complete When:
- [ ] Zero plaintext secrets: `grep -r "changeme123"` → zero
- [ ] AppArmor in enforce mode: `aa-status | grep enforce`
- [ ] Quadlets deployed: `systemctl --user list-units`
- [ ] SLO alerts configured and tested
- [ ] Completed in <1 week

### Phase 5 Complete When:
- [ ] Recovery test: restore from backup <4 hours
- [ ] Audit trail: 100% change logging
- [ ] Security: <5 high-severity vulnerabilities
- [ ] Compliance: SOC2 Type II controls verified
- [ ] Ongoing (month 1+)

---

## 🎯 INTEGRATION WITH YOUR WORKFLOW

### How to Use the New Prompt

**When you open a Claude session:**
1. Confirm the system prompt is OMEGA_STACK_CLAUDE_SYSTEM_PROMPT_v2.md
2. Your first query: "What is our current phase and critical blockers?"
3. Claude responds with: Phase 1 → Storage/permissions/passwords
4. You execute the 2-hour sprint
5. Claude guides you through verification steps

**During execution:**
- Ask Claude clarifying questions about UID translation, ACLs, etc.
- Ask Claude to review a script before running it
- Ask Claude to diagnose a service failure
- Ask Claude to synthesize multi-facet output (Phase 3+)

**Daily cadence:**
- Morning: "What's our status? Any new blockers?"
- Midday: Execute phase tasks with Claude guidance
- Evening: "Summarize what we accomplished. What's tomorrow's focus?"

---

## ⚠️ RED FLAGS TO WATCH

| Flag | Indicates | Action |
|------|-----------|--------|
| "EACCES: permission denied" | Layer 1 didn't work | Re-run ownership restore |
| "No space left on device" | Storage crisis not resolved | Run cleanup_crisis.sh |
| "Connection refused" | Service didn't start | Check logs: `podman logs <service>` |
| "OOMKilled" | Memory limit too low | Increase via quadlet or compose |
| ":Z flag not available" | SELinux confusion | Verify AppArmor, use `:z` instead |
| "UID 100999 permission denied" | Layer 2 ACLs incomplete | Deploy all 4 layers |

---

## ✅ SUCCESS INDICATORS

| Indicator | Phase | Verification |
|-----------|-------|----------------|
| Root FS >20 GB free | Phase 1 | `df -h \| grep "/"`|
| All tools accessible | Phase 1 | `ls -la ~/.gemini` |
| All services healthy | Phase 2 | `podman ps \| grep -v Up` (empty) |
| ACLs permanent | Phase 2 | `getfacl ~/.gemini \| grep u:100999` |
| Archon responding | Phase 3 | `cd omega-stack && gemini` → "Hello" |
| Facets initialized | Phase 3 | `omega-facet list \| grep "✅ ready"` |
| No plaintext secrets | Phase 4 | `grep -r "changeme"` → zero |
| AppArmor enforcing | Phase 4 | `aa-status \| grep enforce` |

---

## 🚀 FINAL ADOPTION STEPS

1. **Load the new prompt** into your system configuration
2. **Read this quick reference** (you're done with that now!)
3. **Read OMEGA_MASTER_INDEX.md** (30 minutes)
4. **Read IMPL-07 §1** (UID translation — 15 minutes)
5. **Execute Phase 1** (2 hours)
6. **Phase 1 complete?** → Celebrate + move to Phase 2
7. **Repeat** for Phases 2-5

---

**You are now equipped to implement Omega-Stack v2. Start with Phase 1. The next 2 hours are critical.**

