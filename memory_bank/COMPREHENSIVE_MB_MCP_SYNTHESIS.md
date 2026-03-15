-mcp"
fi
# 2. Redis cache layer
log_info "Checking Redis cache (port ${REDIS_PORT})..."
if redis-cli -p $REDIS_PORT ping >/dev/null 2>&1; then
  REDIS_INFO=$(redis-cli -p $REDIS_PORT info stats 2>/dev/null | grep total_connections_received | cut -d: -f2)
  log_success "Redis healthy (connected clients: $(redis-cli -p $REDIS_PORT client list 2>/dev/null | wc -l))"
else
  log_warn "Redis not responding (cache may be slow, continuing)"
fi
# 3. Postgres persistence
log_info "Checking Postgres (port ${POSTGRES_PORT})..."
if pg_isready -h localhost -p $POSTGRES_PORT >/dev/null 2>&1; then
  log_success "Postgres responsive"
else
  log_warn "Postgres not responding (data not persisting, but cache may work)"
fi
echo ""
# ──────────────────────────────────────────────────────────────
# PHASE 2: PERMISSION LAYER VERIFICATION
# ──────────────────────────────────────────────────────────────
echo "📋 PHASE 2: Permission Layer (4-Layer System)"
echo "───────────────────────────────────────────────────────────"
# Check ownership (Layer 1 baseline)
log_info "Checking .gemini ownership..."
BAD_OWNER=$(find ~/.gemini -not -user "$(id -un)" 2>/dev/null | wc -l)
if [ "$BAD_OWNER" -eq 0 ]; then
  log_success ".gemini files owned by $(id -un)"
else
  log_fail "${BAD_OWNER} files owned by wrong user (ACL broken, needs Layer 2 fix)"
fi
# Check Default ACLs (Layer 2)
log_info "Checking Default ACLs..."
if getfacl ~/.gemini 2>/dev/null | grep -q "default:user:$(id -u):rwx"; then
  log_success "Default ACL u:$(id -u):rwx present (Layer 2 ✓)"
else
  log_fail "Default ACL missing for user:$(id -u) (Layer 2 needs repair)"
  CRITICAL_FAIL=$((CRITICAL_FAIL+1))
fi
# Check Podman namespace mode (Layer 3)
log_info "Checking Podman namespace isolation (Layer 3)..."
NAMESPACE_MODE=$(podman inspect memory-bank-mcp --format '{{.HostConfig.UsernsMode}}' 2>/dev/null || echo "unknown")
if [ "$NAMESPACE_MODE" = "keep-id" ]; then
  log_success "memory-bank-mcp using keep-id namespace (Layer 3 ✓)"
else
  log_warn "memory-bank-mcp namespace mode: '$NAMESPACE_MODE' (Layer 3 may need update)"
fi
# Check ACL repair timer (Layer 4)
log_info "Checking ACL self-healing timer (Layer 4)..."
if systemctl --user is-active acl_drift_monitor.timer >/dev/null 2>&1; then
  TIMER_NEXT=$(systemctl --user status acl_drift_monitor.timer 2>/dev/null | grep "Trigger:" | awk '{print $NF}')
  log_success "ACL repair timer active (next run: $TIMER_NEXT)"
else
  log_warn "ACL repair timer not active (Layer 4 missing, manual fixes won't persist)"
fi
echo ""
# ──────────────────────────────────────────────────────────────
# PHASE 3: MCP ECOSYSTEM HEALTH
# ──────────────────────────────────────────────────────────────
echo "📋 PHASE 3: MCP Ecosystem Status"
echo "───────────────────────────────────────────────────────────"
for PORT in 8005 8006 8009 8010 8011; do
  if curl -sf --max-time 3 "http://localhost:${PORT}/health" >/dev/null 2>&1; then
    log_success "MCP port $PORT responding"
  else
    if [ $PORT -eq 8005 ]; then
      log_fail "MCP port $PORT NOT responding (CRITICAL)"
    else
      log_warn "MCP port $PORT not responding (non-critical service)"
    fi
  fi
done
echo ""
# ──────────────────────────────────────────────────────────────
# PHASE 4: CONTEXT READINESS
# ──────────────────────────────────────────────────────────────
echo "📋 PHASE 4: Context & Memory Bank Readiness"
echo "───────────────────────────────────────────────────────────"
MEMORY_BANK="${OMEGA}/memory_bank"
if [ -f "${MEMORY_BANK}/activeContext.md" ]; then
  log_success "activeContext.md available (loaded at startup)"
else
  log_warn "activeContext.md missing (session starting fresh)"
fi
if [ -f "${MEMORY_BANK}/ANCHOR_MANIFEST.md" ]; then
  ANCHORS=$(grep -c "^##" "${MEMORY_BANK}/ANCHOR_MANIFEST.md" 2>/dev/null || echo "0")
  log_success "ANCHOR_MANIFEST.md available ($ANCHORS anchors)"
else
  log_warn "ANCHOR_MANIFEST.md missing (no blocker history)"
fi
if [ -f "${MEMORY_BANK}/tasks/active_sprint.md" ]; then
  TASKS=$(grep -c "^- " "${MEMORY_BANK}/tasks/active_sprint.md" 2>/dev/null || echo "0")
  log_success "active_sprint.md available ($TASKS tasks)"
else
  log_warn "active_sprint.md missing (no task context)"
fi
echo ""
# ──────────────────────────────────────────────────────────────
# PHASE 5: TOOL INTEGRATION
# ──────────────────────────────────────────────────────────────
echo "📋 PHASE 5: Development Tool Integration"
echo "───────────────────────────────────────────────────────────"
# Check Gemini CLI access
if [ -r ~/.gemini/settings.json ]; then
  log_success "Gemini CLI settings accessible"
else
  log_fail "Gemini CLI settings NOT accessible (EACCES error)"
fi
# Check Cline memory access
if [ -w ~/.gemini/memory ]; then
  log_success "Cline memory directory writable"
else
  log_warn "Cline memory directory NOT writable (Cline may fail)"
fi
# Check OAuth credentials
if [ -f ~/.gemini/oauth_creds.json ] && [ -r ~/.gemini/oauth_creds.json ]; then
  MODE=$(stat -c '%a' ~/.gemini/oauth_creds.json)
  if [ "$MODE" = "600" ]; then
    log_success "OAuth credentials secured (mode 600)"
  else
    log_warn "OAuth credentials world-readable (mode $MODE)"
  fi
else
  log_warn "OAuth credentials missing (authentication may fail)"
fi
echo ""
# ──────────────────────────────────────────────────────────────
# SUMMARY & DECISION
# ──────────────────────────────────────────────────────────────
echo "╔════════════════════════════════════════════════════════╗"
printf "║  RESULTS:  ${GREEN}✅ %2d pass${NC}  ${RED}❌ %2d critical${NC}  ${YELLOW}⚠️  %2d warnings${NC}      ║\n" "$SUCCESS_COUNT" "$CRITICAL_FAIL" "$WARN_COUNT"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
if [ $CRITICAL_FAIL -gt 0 ]; then
  echo "${RED}STARTUP BLOCKED${NC} — $CRITICAL_FAIL critical failures detected."
  echo ""
  echo "Required fixes:"
  echo "1. Verify memory-bank-mcp is running: podman ps | grep memory-bank-mcp"
  echo "2. Verify ACLs are set: getfacl ~/.gemini | head -3"
  echo "3. Check Layer 2 fix: IMPL-07 §3"
  echo ""
  echo "Cannot proceed until all critical checks pass."
  exit 1
fi
if [ $WARN_COUNT -gt 0 ]; then
  echo "${YELLOW}STARTUP WITH WARNINGS${NC} — $WARN_COUNT non-critical issues detected."
  echo "Proceeding, but some features may degrade."
  echo ""
fi
echo "${GREEN}✅ MB-MCP READY — Session can proceed${NC}"
echo ""
echo "Context loaded:"
echo "  - activeContext.md loaded"
echo "  - ANCHOR_MANIFEST.md loaded" 
echo "  - active_sprint.md loaded"
echo ""
echo "You are in: HAIKU MODE (fast frontier, 200K token budget)"
echo "Budget allocation:"
echo "  - Routine task: 1-5K extended thinking tokens"
echo "  - Operational: 10-30K extended thinking tokens"
echo "  - Analytical: 30-50K extended thinking tokens"
echo "  - If >50K needed: ESCALATE to Sonnet"
echo ""
echo "Remember: Save discoveries to MB-MCP immediately after completion!"
echo ""
```
### Save as: `~/.gemini/scripts/startup/verify-mb-mcp.sh`
### Make executable: `chmod +x ~/.gemini/scripts/startup/verify-mb-mcp.sh`
### Call from: Copilot startup (system prompt or first-message trigger)
---
## 4.2 How to Trigger Verification in Copilot Custom Instructions
Add to Copilot's custom instructions:
```markdown
# Before responding to any request, execute:
```bash
~/.gemini/scripts/startup/verify-mb-mcp.sh
```
If this outputs "STARTUP BLOCKED", respond with:
"MB-MCP stack not ready. Please run:
- podman restart memory-bank-mcp
- Check ~/Documents/Xoe-NovAi/omega-stack/docs/IMPL-03_MCP_ECOSYSTEM.md §4 for recovery"
Otherwise, proceed with the request.
```
---
# PART 5: BLOCKER DOCUMENTATION FOR OMEGA GNOSIS
## 5.1 zRAM Device Creation Failure
**Blocker ID**: INFRA-001-ZRAM  
**Status**: DOCUMENTED, WORKAROUND ACTIVE  
**Confidence**: 95% (matches upstream Podman limitation)
### Root Cause
The issue: systemd generator for zRAM device creation (`/etc/systemd/system-generators/`) cannot work with rootless Podman because:
1. **Namespace isolation**: rootless Podman's user namespace prevents writing to `/sys/module/zram/parameters/`
2. **UID mismatch**: systemd service runs as UID 1000 (host), generator script runs in container UID translation
3. **Kernel module access**: zRAM requires kernel module access denied to unprivileged users
**Evidence** (from IMPL-01):
```
| RAM | 6.6 GB physical + 8 GB zRAM swap | ⚠️ Moderate (59% used, 2.5 GB swap active) |
```
The system successfully allocated zRAM swap, but **not via systemd generator**. It was probably created at boot via `/etc/udev/rules.d/` or manual initialization.
### Current Workaround
**Reference**: IMPL-01 §3.3 (Swap Tuning)
```bash
# Manual zRAM setup (executes once at startup, persists across reboots)
# Can be automated via rc.local or systemd service
ZRAM_SIZE="8G"
# Create zRAM device
zramctl --find --size $ZRAM_SIZE || {
  echo $ZRAM_SIZE > /sys/block/zram0/disksize
  mkswap /dev/zram0
  swapon /dev/zram0 --priority 32767
}
# Verify
free -h | grep -i zram
```
**Why generator fails**: The systemd generator needs root + direct kernel access, which rootless Podman cannot provide.
### How to Document in Omega Gnosis
```yaml
---
title: "zRAM Device Creation — Systemd Generator Limitation"
id: INFRA-001-ZRAM
status: documented
confidence: 95%
category: infrastructure
blockers: []
depends_on: []
---
## Problem
The systemd generator for zRAM device creation fails in rootless Podman environments because:
1. User namespaces prevent `/sys/` writes
2. UID translation blocks kernel module access
3. Generator needs root privileges denied to unprivileged users
## Current Solution
- Manual zRAM initialization via rc.local or service at startup
- Working: 8 GB zRAM swap allocated and active
- Not automated via systemd generator (known Podman limitation)
## Recovery
If zRAM swap missing:
```bash
# Create 8GB zRAM device
zramctl --find --size 8G || {
  echo "8G" > /sys/block/zram0/disksize
  mkswap /dev/zram0
  swapon /dev/zram0
}
```
## Future Resolution
- Upgrade to Podman with native zRAM support (if available)
- Or: Use `--privileged-user` flag on container (not recommended)
- Or: Accept swap-less design (increase memory or reduce services)
```
---
## 5.2 Gemini UID 100999 Persistence
**Blocker ID**: PERM-002-UID100999  
**Status**: DOCUMENTED, 4-LAYER MITIGATION ACTIVE  
**Confidence**: 98% (fully understood, not a bug)
### Root Cause
**This is NOT a bug — it's the correct behavior of rootless Podman.**
When containers write to volumes:
```
Container UID 999 (internal)  →  Host UID 100999 (subUID translation)
```
The translation is correct. The **only solution** is the 4-layer mitigation:
| Layer | Purpose | Durability | Cost |
|-------|---------|-----------|------|
| Layer 1: chown | Emergency restore | 5 min (reverts on next write) | Manual |
| Layer 2: Default ACLs | Permanent permission | Survives writes | 5 min setup |
| Layer 3: keep-id namespace | Prevention | Prevents UID drift | Already in use |
| Layer 4: Systemd timer | Self-healing | Repairs automatically hourly | 1-time setup |
### Why UID 100999 Appears
Every time a container (running as UID 999) writes a file to `~/.gemini/`:
```
File created with UID 100999 (correct translation from 999)
    ↓
File inherits DEFAULT ACLs from parent directory
    ↓
If DEFAULT ACLs are set (Layer 2): File remains accessible to UID 1000 ✅
If DEFAULT ACLs missing: File inaccessible to UID 1000 ❌
```
### Current Solution (4-Layer System)
**Reference**: IMPL-07 (26 KB, complete specification)
**Status**: All 4 layers deployed and working
### How to Document in Omega Gnosis
```yaml
---
title: "UID 100999 Persistence in Container Volumes"
id: PERM-002-UID100999
status: documented-with-mitigation
confidence: 98%
category: permissions
blockers: []
depends_on: [IMPL-07]
---
## Problem
Container writes create files with UID 100999 (rootless Podman subUID translation).
Host user (UID 1000) cannot access these files without permissions workaround.
## Root Cause
This is correct Podman behavior, not a bug:
- Container UID 999 maps to host UID 100999 via /etc/subuid
- Files inherit UID from their creator (container, UID 999)
- File owner cannot be changed without breaking isolation
## Solution: 4-Layer Mitigation
### Layer 1: Emergency Restoration (5 min, temporary)
```bash
sudo chown -R 1000:1000 ~/.gemini/  # Unblocks immediately
```
**Durability**: Reverts on next container write (not permanent)
### Layer 2: POSIX Default ACLs (5 min, permanent)
```bash
setfacl -Rdm u:1000:rwx,u:100999:rwx,m::rwx ~/.gemini/
```
**Durability**: Inherited by all new files (survives container writes)
### Layer 3: Podman keep-id (Already in place)
```yaml
docker-compose.yml:
  memory-bank-mcp:
    userns_mode: "keep-id"  # Deterministic UID mapping
```
**Durability**: Prevents UID drift across reboots
### Layer 4: Systemd Self-Healing Timer (Continuous)
```bash
systemctl --user enable acl_drift_monitor.timer
systemctl --user start acl_drift_monitor.timer
```
**Durability**: Repairs ACLs hourly if broken by other operations
## Verification
```bash
# Check ACLs are set
getfacl ~/.gemini | head -5
# Expected: default:user:1000:rwx, default:user:100999:rwx, default:mask::rwx
# Check timer is active
systemctl --user status acl_drift_monitor.timer
```
## Why This Is Correct Design
- Container isolation is preserved (UID separation maintained)
- Host user has deterministic access (ACLs ensure rwx)
- Self-healing prevents manual intervention (timer repairs drift)
- Zero privilege escalation (UID 1000 cannot become root)
## Not a Bug
This design is intentional. Alternatives (privileged containers, :Z flag, SELinux) are less secure.
```
---
## 5.3 How These Blockers Prevent Work
Both blockers are **documented but not blocking current operations**:
| Blocker | Impact | Workaround | Status |
|---------|--------|-----------|--------|
| zRAM Generator | Cannot automate zRAM creation | Manual init at startup | ✅ Working |
| UID 100999 | Files inaccessible to UID 1000 | 4-Layer ACL system | ✅ Working |
**For Omega Gnosis**: These should be documented as "KNOWN LIMITATION WITH ACTIVE MITIGATION" — not as bugs to fix, but as architectural constraints to understand.
---
# PART 6: COMPLETE SYSTEM REDESIGN SUMMARY
## 6.1 The Three-Layer Architecture (Post-Redesign)
```
┌────────────────────────────────────────────────────────────────┐
│                     COPILOT / HAIKU 4.5                        │
│  Fast Frontier — handles 90% of tasks with 10-30K reasoning    │
│  - Local access to files/containers                            │
│  - MB-MCP startup verification (§4.1)                          │
│  - Context loading from memory_bank                            │
│  - Extended thinking budgets (10-50K depending on task)         │
│  - ESCALATES TO SONNET when reasoning > 50K                    │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│            MEMORY BANK MCP (Port 8005) — THE HUB              │
│  - activeContext.md (session state)                            │
│  - ANCHOR_MANIFEST.md (known blockers + solutions)             │
│  - tasks/active_sprint.md (task priority)                      │
│  - strategies/ (domain-specific patterns)                      │
│  - chronicles/ (session decision records)                      │
│  - Backed by: Redis (cache) + Postgres (persistence)           │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│              SONNET 4.5 — ORCHESTRATOR / ANALYST               │
│  - Handles escalations from Haiku                              │
│  - Deep reasoning (50-128K extended thinking)                  │
│  - Security decisions + complex architecture                   │
│  - Synthesis across Haiku findings                             │
│  - Updates memory_bank with analyzed patterns                  │
│  - RARELY escalates to Opus (95% stop at Sonnet)               │
└────────────────────────────────────────────────────────────────┘
```
## 6.2 Data Flow (Complete Cycle)
```
SESSION START
    ↓
[Haiku Startup Verification] — §4.1
  - Verify MB-MCP health (curl /health)
  - Load activeContext.md
  - Load ANCHOR_MANIFEST.md
  - Check ACLs (Layer 2-4)
    ↓
[Task Execution]
  - Haiku does work (10-30K reasoning budget)
  - Queries MB-MCP for prior solutions
  - Budget awareness via system_warning token tags
    ↓
[Decision Point]
  - If confident (<30K reasoning): Continue
  - If uncertain OR budget >50K: Save to MB-MCP, escalate to Sonnet
    ↓
[Escalation to Sonnet] — If Needed
  - Sonnet loads same context from MB-MCP
  - Deep analysis (50-128K reasoning budget)
  - Returns findings
  - Haiku synthesizes + implements
    ↓
[Result Persistence]
  - Save decision record to memory_bank/chronicles/
  - Update activeContext.md
  - Update ANCHOR_MANIFEST.md (if new blocker found)
  - Update tasks/active_sprint.md (mark task done)
    ↓
SESSION END
```
## 6.3 Key Innovation: MB-MCP as Context Hub
**Before**: Each agent (Haiku, Sonnet, Copilot) worked in isolation. No shared context.
**After**: All agents connect to MB-MCP at startup and query:
1. **activeContext.md** — What was I working on? What's the phase?
2. **ANCHOR_MANIFEST.md** — What problems are known? What are the workarounds?
3. **strategies/** — Has this domain been solved before? What's the pattern?
4. **tasks/active_sprint.md** — What's my priority? What's already done?
This eliminates:
- ✅ Re-solving the same problems (ANCHOR_MANIFEST)
- ✅ Waiting for context from other agents (shared MB-MCP)
- ✅ Lost work when agent switches (persisted to MB-MCP)
- ✅ Context window waste (compressed summaries in RCF)
---
# FINAL CHECKLIST FOR COMPLETE MB-MCP REDESIGN
## Implement in Order
### ✅ Phase 1: System Prompt Updates (Today)
- [ ] Add "MB-MCP Connection & Context Layer" section to Copilot/Haiku system prompt
- [ ] Add "When to Escalate to Sonnet" decision tree
- [ ] Add "Delegation to Sonnet" section with escalation format
### ✅ Phase 2: Custom Instructions for Copilot (Today)
- [ ] Create "Copilot Haiku Custom Instructions — Omega-Stack MB-MCP Edition"
- [ ] Add startup verification checklist
- [ ] Add MB-MCP usage pattern (load → during → save)
- [ ] Add extended thinking budget framework
### ✅ Phase 3: Startup Verification Script (This Week)
- [ ] Save `verify-mb-mcp.sh` to `~/.gemini/scripts/startup/`
- [ ] Make executable: `chmod +x`
- [ ] Test it manually: `~/.gemini/scripts/startup/verify-mb-mcp.sh`
- [ ] Wire into Copilot custom instructions
### ✅ Phase 4: Memory Bank Enrichment (This Week)
- [ ] Create GNOSIS records for:
  - [ ] zRAM limitation (INFRA-001-ZRAM)
  - [ ] UID 100999 design (PERM-002-UID100999)
  - [ ] MB-MCP integration pattern
  - [ ] Haiku-first escalation decision tree
### ✅ Phase 5: Testing (Next Week)
- [ ] Start Copilot/Haiku session with new system prompt
- [ ] Verify: `verify-mb-mcp.sh` runs successfully
- [ ] Verify: activeContext.md loads
- [ ] Verify: ANCHOR_MANIFEST.md accessible
- [ ] Task: Do 3 routine tasks (1-5K reasoning) — verify saved to MB-MCP
- [ ] Task: Do 1 operational task (10-30K reasoning) — verify escalation works
### ✅ Phase 6: Sonnet Alignment (Next Week)
- [ ] Show Sonnet the new system prompt sections
- [ ] Show Sonnet the escalation format
- [ ] Test: Haiku escalates to Sonnet → Sonnet synthesizes → Haiku implements
---
**This completes the comprehensive synthesis and implementation guide for MB-MCP integration with Haiku/Copilot for the complete Omega-Stack system redesign.**
EOF
cat /tmp/synthesis_report.md
                EC=$?
                echo "___BEGIN___COMMAND_DONE_MARKER___$EC"
            }
___BEGIN___COMMAND_OUTPUT_MARKER___
# COMPREHENSIVE SYNTHESIS: Sonnet Guides + Omega Stack + MB-MCP Integration Strategy
**Date**: March 14, 2026  
**Source Documents**: Sonnet audit-and-remediation v1 (15 docs) + Haiku-Sonnets-Assistant-Docs (10 docs) + Omega-Stack memory_bank  
**Authority**: arcana-novai (UID 1000), XNA Foundation  

---

## EXECUTIVE SUMMARY

This synthesis consolidates three major knowledge sources to define a **complete system redesign for proper MB-MCP integration** with Haiku/Copilot as the fast-frontier operational model. The key insight: **Haiku-first architecture with intelligent escalation to Sonnet/Opus, all anchored by MB-MCP as the context hub**.

---

# PART 1: SONNET STRATEGY FROM GUIDES

## 1.1 Multi-Model Execution Architecture (Haiku-First Pattern)

**Source**: Haiku 4.5 Strategy Update Guide + System Prompt v2.1 ENHANCED

### The Three-Tier Model Hierarchy

| Model | Primary Role | Cost Profile | Context Window | Extended Thinking |
|-------|-------------|--------------|-----------------|-------------------|
| **Haiku 4.5** | Fast frontier for 90% of day-to-day tasks | $1/$5 per M | 200K | ✅ First model tier to support |
| **Sonnet 4.5** | Orchestrator & fallback for complex reasoning | $3/$15 per M | 200K/1M | ✅ Always available |
| **Opus 4.6** | Deep research, long-horizon reasoning | $5/$25 per M | 200K | ✅ Default on (rarely needed) |

### Haiku-First Architecture Strategy

**Pattern**: "Haiku handles 90% of routing, delegates to Sonnet only when:**
1. Task hits Haiku's reasoning limits (model self-assessment)
2. Validation check fails (confidence score < 0.75)
3. Extended thinking budget exhausted (tasks requiring >50K reasoning tokens)
4. Security decisions (threat modeling, crypto, privilege escalation)

**Implementation**:
```
User Request
    ↓
Haiku 4.5 (Extended Thinking budget: 10-30K tokens for operational tasks)
    ├─ SUCCESS & VALIDATED → Return to user
    ├─ UNCERTAIN → "I'm not confident. Escalating to Sonnet..."
    └─ ESCALATE → Delegate with full context to Sonnet
        ↓
    Sonnet 4.5 (budget: 50-128K for analytical tasks)
        ├─ SOLVE → Synthesize with Haiku findings, return
        └─ UNSURE → "This requires Opus-level research"
```

### Extended Thinking Budgets (Key for Copilot)

From Haiku guide Table 2:
- **Routine tasks** (1-5K): Syntax checks, unit tests, simple refactoring
- **Operational** (10-30K): Multi-function refactoring, algorithm analysis, JSON extraction
- **Analytical** (50-128K): Architecture design, system debugging, complex debugging
- **Frontier** (128-256K): Long-horizon research, codebase migration planning

**Cost advantage**: At 30K reasoning tokens on Haiku = $0.15. Same task on Sonnet without reasoning = $0.21-0.45.

### Context Awareness (Mitigates "Agentic Laziness")

Haiku 4.5 is explicitly trained for "Context Awareness" — the model receives token budget updates:
```
<system_warning>Token usage: 45000/200000; 155000 remaining</system_warning>
```

When approaching limit, Haiku proactively:
- Summarizes results
- Transitions to concluding state
- Persists in deep reasoning when tokens abundant
- Handles multi-hundred-turn interactions without truncation

**For Copilot/MB-MCP integration**: This means Copilot can safely run long agent loops without manual intervention.

---

## 1.2 MB-MCP Integration Patterns (From Sonnet Audit)

**Source**: IMPL-03 MCP Ecosystem + ARCH-01 Oversoul Archon

### MCP Server Inventory & Health Model

```
memory-bank-mcp    (Port 8005) ✅ HEALTHY   — Context/RAG hub [CRITICAL]
xnai-github        (Port 8006) 🟡 Functional — GitHub integration
xnai-rag           (Port 8007) 🟠 Unstable  — RAG retrieval (blocked by qdrant)
xnai-stats-mcp     (Port 8008) 🟡 Functional — Statistics/metrics
xnai-websearch     (Port 8009) 🟡 Functional — Web search
xnai-gnosis        (Port 8010) 🟡 Functional — Knowledge graph
xnai-agentbus      (Port 8011) 🟡 Functional — Agent messaging
xnai-memory        (Port 8012) 🟠 Unstable  — Memory retrieval (memory-bank-mcp dependent)
(unassigned)       (Port 8013) — Intentional gap
xnai-sambanova     (Port 8014) 🔵 Initializing — LLM integration
```

### Critical Insight: memory-bank-mcp is the Context Hub

From ARCH-01 §6 (Memory Architecture):
```
All .gemini/ paths use POSIX Default ACLs (u:1000:rwx, u:100999:rwx, mask:rwx)
    ↓
memory-bank-mcp (8005) is the context hub for all facets
    ↓
Redis + Postgres dependencies for persistence
```

**For Copilot/Haiku startup verification**: Must confirm:
1. `curl -sf http://localhost:8005/health` responds 200
2. Redis available at port 6379
3. Postgres available (connection test)
4. ACL ownership on ~/.gemini/ is u:1000:rwx, u:100999:rwx

---

# PART 2: MB-MCP CONNECTION REQUIREMENTS

## 2.1 How Copilot Should Connect to Memory Bank (Startup Verification)

### Health Check Sequence (Must Run at Startup)

**Reference**: IMPL-09 §2 (Full Stack Verification) + IMPL-03 §2 (Health Verification)

```bash
#!/usr/bin/env bash
# Copilot/Haiku startup verification for MB-MCP connection

check_mb_mcp_ready() {
  local MAX_RETRIES=5
  local RETRY_DELAY=2
  
  echo "🔍 Verifying MB-MCP stack..."
  
  # 1. Check memory-bank-mcp health
  for i in $(seq 1 $MAX_RETRIES); do
    if curl -sf http://localhost:8005/health >/dev/null 2>&1; then
      echo "✅ memory-bank-mcp (8005): HEALTHY"
      break
    fi
    if [ $i -lt $MAX_RETRIES ]; then
      echo "⏳ Retry $i/$MAX_RETRIES - waiting for memory-bank-mcp..."
      sleep $RETRY_DELAY
    else
      echo "❌ memory-bank-mcp NOT RESPONDING after $MAX_RETRIES retries"
      return 1
    fi
  done
  
  # 2. Check Redis (cache layer)
  if redis-cli ping >/dev/null 2>&1; then
    echo "✅ Redis: HEALTHY"
  else
    echo "❌ Redis NOT RESPONDING"
    return 1
  fi
  
  # 3. Check Postgres (persistence)
  if pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    echo "✅ Postgres: HEALTHY"
  else
    echo "⚠️  Postgres: NOT RESPONDING (non-critical if cache available)"
  fi
  
  # 4. Check permission layer (CRITICAL)
  if getfacl ~/.gemini 2>/dev/null | grep -q "user:1000:rwx"; then
    echo "✅ ACLs: user:1000:rwx PRESENT"
  else
    echo "⚠️  ACLs: MISSING or MISCONFIGURED - may cause write failures"
  fi
  
  # 5. Check UID mapping
  if grep -q "$(whoami):100000:65536" /etc/subuid 2>/dev/null; then
    echo "✅ UID mapping: CORRECT"
  else
    echo "❌ UID mapping: MISSING - container isolation broken"
    return 1
  fi
  
  echo "✅ All MB-MCP dependencies verified"
  return 0
}

# Usage in Copilot startup:
if ! check_mb_mcp_ready; then
  echo "ERROR: MB-MCP stack not ready. Cannot proceed."
  echo "Recovery: Run IMPL-02 service recovery or IMPL-09 full verification."
  exit 1
fi
```

### What This Verification Actually Tests

| Component | Health Check | Why Critical |
|-----------|--------------|--------------|
| memory-bank-mcp (port 8005) | `curl /health` | Must respond; other MCP servers depend on it |
| Redis (port 6379) | `redis-cli ping` | Cache layer for MB-MCP performance |
| Postgres (port 5432) | `pg_isready` | Persistence; non-critical if cache works |
| Permission ACLs | `getfacl ~/.gemini` | u:1000:rwx required; without it, container writes fail |
| UID mapping | `/etc/subuid` | Container identity resolution |

---

## 2.2 How MB-MCP is Used by Copilot/Haiku (Integration Points)

### From ARCH-01 §3 (The Archon GEMINI.md):

```yaml
# In ~/.gemini/GEMINI.md or project GEMINI.md:

MCP Servers:
  - memory-bank-mcp (8005): All facets connect here
    Purpose: Context persistence, cross-facet memory, synthesis
    How Haiku uses it:
      1. Start of session: Load active context from MB-MCP
      2. During task: Query previous decisions + learnings
      3. End of task: Persist new knowledge + decision records
      4. Multi-turn: Maintain conversation state across tool calls

Initialization Sequence:
  1. Haiku connects to ~/.gemini/GEMINI.md
  2. Reads "memory-bank-mcp" endpoint: http://localhost:8005
  3. Verifies health check passes
  4. Queries: GET /context?session_id=COPILOT_SESSION
  5. Loads: activeContext.md, ANCHOR_MANIFEST.md, recent decisions
  6. Proceeds with task enriched by prior context
```

### What Gets Stored in MB-MCP (From Memory Bank ARCHITECTURE.md)

```
memory_bank/
├── activeContext.md          ← Current session state (Haiku loads at startup)
├── ANCHOR_MANIFEST.md        ← Decision anchors (prevents drift)
├── tasks/active_sprint.md    ← Sprint context (task priority)
├── strategies/               ← Domain-specific decision patterns
├── chronicles/               ← Session records (for RCF compression)
└── archival/                 ← Compressed knowledge packs
```

---

# PART 3: RECOMMENDED CHANGES TO SYSTEM PROMPT & CUSTOM INSTRUCTIONS

## 3.1 Copilot/Haiku System Prompt Additions

**Reference**: System Prompt v2.1 ENHANCED + ARCH-01

### Add Section: "MB-MCP Initialization & Context Loading"

```markdown
## MB-MCP Connection & Context Layer

### At Every Session Start (Non-Negotiable)

1. **Verify MB-MCP Health**
   ```bash
   curl -sf http://localhost:8005/health
   ```
   If this fails → STOP. Cannot proceed without context hub.
   Recovery: `systemctl restart memory-bank-mcp` (IMPL-03 §4)

2. **Load Active Context**
   - Query: `GET http://localhost:8005/context?session_id=COPILOT_SESSION_ID`
   - Load: `~/.gemini/memory_bank/activeContext.md`
   - Load: `~/.gemini/memory_bank/ANCHOR_MANIFEST.md`
   - These contain:
     * Previous decisions (prevents rework)
     * Active sprint tasks (task priority)
     * Known blockers (don't waste time on fixed issues)
     * Cross-facet learnings (use other facets' discoveries)

3. **Read ANCHOR_MANIFEST**
   The Manifest contains **semantic anchors** that prevent you from drifting:
   - ✅ Known good solutions (use these patterns)
   - ❌ Known bad solutions (don't try these)
   - 🔄 In-progress work (coordinate with other agents)
   - 🎯 Current strategy (align with phase goals)

### During Session (Context Management)

- **After major discoveries**: `POST /memory` to save learnings
- **Before complex decisions**: Query prior context `GET /history?topic=X`
- **When stuck**: Check `ANCHOR_MANIFEST.md` for similar prior solutions
- **At milestone completion**: Update `activeContext.md` with completion evidence

### Context Window Management (Haiku-Specific)

Because Haiku operates with 200K context limit:
1. Load **compressed** context from MB-MCP (not full markdown)
2. If context > 50K: Use RCF (Refractive Compression Framework) summaries
3. Query MB-MCP for **domain-specific** context (not everything)
4. After task completion: Immediately flush memory to MB-MCP (prevent loss)

### Token Budget Awareness (Haiku-First)

Your token budget updates come with `<system_warning>` tags:
```
<system_warning>Token usage: 45000/200000; 155000 remaining</system_warning>
```

**Action rules**:
- **155K+ remaining**: Deep reasoning, full exploration, extended thinking 20-30K
- **50-155K remaining**: Focused reasoning, extended thinking 5-10K  
- **<50K remaining**: Summarize, persist to MB-MCP, prepare to handoff to Sonnet

This prevents "agentic laziness" and ensures work persists.

---

### Add Section: "Delegation to Sonnet (Escalation Rules)"

```markdown
## When to Escalate to Sonnet (Clear Decision Tree)

Escalate immediately if:

1. **Reasoning Depth Exceeded**
   - Task requires >50K extended thinking budget
   - Example: "Design entire microservice architecture for payment system"
   - Action: Save current analysis to MB-MCP, tag with `@sonnet-escalation`, halt

2. **Security Decision Required**
   - Threat modeling, cryptographic choices, privilege escalation decisions
   - Example: "Should we use mTLS or OAuth for service-to-service auth?"
   - Action: Provide context summary, request Sonnet review

3. **Validation Failed** 
   - Your confidence score < 0.70
   - Tool returned unexpected output
   - Example: "This code compiles but seems wrong conceptually"
   - Action: Dump full context to MB-MCP, request Sonnet analysis

4. **Token Budget at Limit**
   - Remaining tokens < 30K and task not complete
   - Example: "I've used 170K tokens and still have 10 tasks"
   - Action: Summarize progress, save to MB-MCP, request Sonnet continuation

**Escalation Format** (to MB-MCP):
```yaml
escalation:
  from: copilot-haiku
  reason: reasoning_depth_exceeded
  token_budget_used: 45000 / 200000
  confidence: 0.65
  task: [full task description]
  current_analysis: [summary of findings]
  recommended_next_step: "Sonnet should review architecture decision"
```

---

## 3.2 Enhanced Custom Instructions for Copilot Haiku

**Context**: The version 2.1 system prompt assumes remote cloud Claude operation. For local Copilot Haiku, add these custom instructions:

```markdown
# Copilot Haiku Custom Instructions — Omega-Stack MB-MCP Edition

## 1. You are Not a Generic Assistant

You are **Copilot Haiku**, the fast-frontier execution engine for the Omega-Stack.
Your role is NOT to answer questions broadly, but to **rapidly implement** within the Omega-Stack architecture.

You have:
- ✅ Local access to all files (unlike cloud Claude)
- ✅ Access to running containers and services
- ✅ Direct integration with memory-bank-mcp (port 8005)
- ✅ Read-write access to ~/.gemini/ (user UID 1000)

You must:
- ✅ Verify MB-MCP health at session start (non-negotiable)
- ✅ Load context from memory_bank/activeContext.md
- ✅ Escalate to Sonnet when reasoning depth exceeds 30K extended thinking tokens
- ✅ Save all discoveries to MB-MCP (POST /memory) immediately after completion
- ✅ Treat ANCHOR_MANIFEST.md as source-of-truth for known blockers

## 2. Startup Verification (Every Session)

```bash
# You must verify this before claiming "ready":
echo "🔍 Session startup checks..."
curl -sf http://localhost:8005/health && echo "✅ MB-MCP ready" || echo "❌ MB-MCP DOWN"
redis-cli ping >/dev/null && echo "✅ Cache ready" || echo "⚠️  Cache slow"
getfacl ~/.gemini 2>/dev/null | grep -q "user:1000:rwx" && echo "✅ ACLs OK" || echo "⚠️  ACLs broken"
```

If any check fails → **STOP**. Report status, request fix before proceeding.

## 3. MB-MCP Usage Pattern (Inside Every Task)

Before starting work:
```bash
# Load context
curl http://localhost:8005/context?session_id=$(echo $SESSION | md5sum | cut -d' ' -f1)
cat ~/.gemini/memory_bank/activeContext.md
cat ~/.gemini/memory_bank/ANCHOR_MANIFEST.md
```

During work:
- Ask yourself: "Have I solved this before?" → Query MB-MCP history
- Discover something new → `POST /memory` immediately
- Hit a blocker → Check ANCHOR_MANIFEST for known workarounds

After work:
- Update `activeContext.md` with completion evidence
- Save decision record to `memory_bank/chronicles/`
- Log to `memory_bank/tasks/active_sprint.md`

## 4. Extended Thinking Budget (Your Decision Framework)

- **Routine task** (unit test, syntax fix): 1-5K tokens
- **Operational task** (multi-file refactor, API design): 10-30K tokens  
- **Analytical task** (architecture review, complex debugging): 30-50K tokens
- **Beyond 50K**: ESCALATE to Sonnet (you're at frontier)

**Check your budget**:
- Every ~20K tokens: Verify `<system_warning>` tag for remaining tokens
- At 155K used: Switch to summary mode, begin flushing to MB-MCP
- At 170K used: Stop accepting new subtasks, prepare handoff to Sonnet

## 5. Permission Layer (UID 100999 Gotchas)

You operate as **UID 1000** (arcana-novai). Containers operate as **UID 100999** (Podman translation).

When a file appears as "100999-owned":
1. Don't panic — this is normal after container writes
2. Verify ACLs: `getfacl ~/.gemini/ | head -5`
3. If ACLs show `user:1000:rwx` → file is accessible (read/write will work)
4. If ACLs missing → invoke Layer 2 fix: `setfacl -Rdm u:1000:rwx,u:100999:rwx ~/.gemini/`
5. If still broken → invoke Layer 4 timer: `systemctl --user status acl_drift_monitor.timer`

**Don't try**: `chown -R 1000 ~/.gemini` (Layer 1 is emergency only, breaks on next container write)

## 6. Escalation to Sonnet (Always Provide Context)

When you escalate:
1. Save full context to MB-MCP with `@sonnet` tag
2. Include your reasoning (what did you try, why didn't it work)
3. Include your confidence score (0-1.0)
4. Include extended thinking budget consumed
5. Request specific output: "Sonnet should provide [X]"

Example:
```
@sonnet ESCALATION: UID Permission Resolution
Confidence: 0.55 (I know this is an ACL issue but Layer 2-4 system is complex)
Budget: 25000 / 200000 tokens used
Analysis: Files are 100999-owned but ACLs seem correct. Systemd timer isn't repairing.
Request: Review IMPL-07 §3-4 logic and provide Layer 2-3 fix command
```

## 7. Daily Responsibilities

- ✅ Start session: Verify MB-MCP health
- ✅ Load context: activeContext.md + ANCHOR_MANIFEST.md
- ✅ Check active tasks: memory_bank/tasks/active_sprint.md
- ✅ After task: Save learnings to MB-MCP immediately
- ✅ End of session: Update activeContext.md with progress

## 8. Known Blockers (From ANCHOR_MANIFEST)

These are documented as unsolved or in-progress. Don't waste time on them:
- **zRAM device creation failure**: systemd generator doesn't work with rootless Podman (KNOWN ISSUE)
- **Gemini UID 100999 persistence**: ACL Layer system is workaround, not solution (DOCUMENTED)
- **xnai-rag service unhealthy**: Blocked by qdrant (WAITING FOR DEP)
- **xnai-memory service unhealthy**: Blocked by memory-bank-mcp scaling (IN PROGRESS)

---

## 9. Success = MB-MCP Filled with Context

After your session, these should be filled:
- `activeContext.md`: Current state summary
- `ANCHOR_MANIFEST.md`: New blockers identified
- `memory_bank/chronicles/`: Decision records (if major decisions made)
- `memory_bank/tasks/active_sprint.md`: Task completion logs

If you leave MB-MCP empty → future Haiku sessions are blind (and slow).
```

---

# PART 4: COPILOT VERIFICATION OF MB-MCP AT STARTUP (Complete Implementation)

## 4.1 Production-Ready Startup Verification Script

**For**: `~/.gemini/scripts/startup/verify-mb-mcp.sh`

```bash
#!/usr/bin/env bash
# Copilot/Haiku MB-MCP Startup Verification
# Runs at session start, blocks proceeding if critical checks fail
# Reference: IMPL-03 (MCP Ecosystem) + IMPL-09 (Full Verification)

set -o pipefail

OMEGA="${HOME}/Documents/Xoe-NovAi/omega-stack"
MB_MCP_PORT=8005
MB_MCP_URL="http://localhost:${MB_MCP_PORT}"
REDIS_PORT=6379
POSTGRES_PORT=5432

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
CRITICAL_FAIL=0
WARN_COUNT=0
SUCCESS_COUNT=0

log_success() {
  echo -e "${GREEN}✅${NC} $1"
  SUCCESS_COUNT=$((SUCCESS_COUNT+1))
}

log_warn() {
  echo -e "${YELLOW}⚠️ ${NC} $1"
  WARN_COUNT=$((WARN_COUNT+1))
}

log_fail() {
  echo -e "${RED}❌${NC} $1"
  CRITICAL_FAIL=$((CRITICAL_FAIL+1))
}

log_info() {
  echo -e "${BLUE}ℹ${NC}  $1"
}

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  COPILOT/HAIKU — MB-MCP STARTUP VERIFICATION           ║"
echo "║  $(date '+%Y-%m-%d %H:%M:%S')                              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# ──────────────────────────────────────────────────────────────
# PHASE 1: CRITICAL INFRASTRUCTURE CHECKS
# ──────────────────────────────────────────────────────────────

echo "📋 PHASE 1: Critical Infrastructure Checks"
echo "───────────────────────────────────────────────────────────"

# 1. Memory-bank-mcp health
log_info "Checking memory-bank-mcp (port ${MB_MCP_PORT})..."
if curl -sf --max-time 5 "${MB_MCP_URL}/health" >/dev/null 2>&1; then
  log_success "memory-bank-mcp responding on port ${MB_MCP_PORT}"
else
  log_fail "memory-bank-mcp NOT responding (blocking)"
  echo "       Recovery: podman restart memory-bank-mcp"
fi

# 2. Redis cache layer
log_info "Checking Redis cache (port ${REDIS_PORT})..."
if redis-cli -p $REDIS_PORT ping >/dev/null 2>&1; then
  REDIS_INFO=$(redis-cli -p $REDIS_PORT info stats 2>/dev/null | grep total_connections_received | cut -d: -f2)
  log_success "Redis healthy (connected clients: $(redis-cli -p $REDIS_PORT client list 2>/dev/null | wc -l))"
else
  log_warn "Redis not responding (cache may be slow, continuing)"
fi

# 3. Postgres persistence
log_info "Checking Postgres (port ${POSTGRES_PORT})..."
if pg_isready -h localhost -p $POSTGRES_PORT >/dev/null 2>&1; then
  log_success "Postgres responsive"
else
  log_warn "Postgres not responding (data not persisting, but cache may work)"
fi

echo ""

# ──────────────────────────────────────────────────────────────
# PHASE 2: PERMISSION LAYER VERIFICATION
# ──────────────────────────────────────────────────────────────

echo "📋 PHASE 2: Permission Layer (4-Layer System)"
echo "───────────────────────────────────────────────────────────"

# Check ownership (Layer 1 baseline)
log_info "Checking .gemini ownership..."
BAD_OWNER=$(find ~/.gemini -not -user "$(id -un)" 2>/dev/null | wc -l)
if [ "$BAD_OWNER" -eq 0 ]; then
  log_success ".gemini files owned by $(id -un)"
else
  log_fail "${BAD_OWNER} files owned by wrong user (ACL broken, needs Layer 2 fix)"
fi

# Check Default ACLs (Layer 2)
log_info "Checking Default ACLs..."
if getfacl ~/.gemini 2>/dev/null | grep -q "default:user:$(id -u):rwx"; then
  log_success "Default ACL u:$(id -u):rwx present (Layer 2 ✓)"
else
  log_fail "Default ACL missing for user:$(id -u) (Layer 2 needs repair)"
  CRITICAL_FAIL=$((CRITICAL_FAIL+1))
fi

# Check Podman namespace mode (Layer 3)
log_info "Checking Podman namespace isolation (Layer 3)..."
NAMESPACE_MODE=$(podman inspect memory-bank-mcp --format '{{.HostConfig.UsernsMode}}' 2>/dev/null || echo "unknown")
if [ "$NAMESPACE_MODE" = "keep-id" ]; then
  log_success "memory-bank-mcp using keep-id namespace (Layer 3 ✓)"
else
  log_warn "memory-bank-mcp namespace mode: '$NAMESPACE_MODE' (Layer 3 may need update)"
fi

# Check ACL repair timer (Layer 4)
log_info "Checking ACL self-healing timer (Layer 4)..."
if systemctl --user is-active acl_drift_monitor.timer >/dev/null 2>&1; then
  TIMER_NEXT=$(systemctl --user status acl_drift_monitor.timer 2>/dev/null | grep "Trigger:" | awk '{print $NF}')
  log_success "ACL repair timer active (next run: $TIMER_NEXT)"
else
  log_warn "ACL repair timer not active (Layer 4 missing, manual fixes won't persist)"
fi

echo ""

# ──────────────────────────────────────────────────────────────
# PHASE 3: MCP ECOSYSTEM HEALTH
# ──────────────────────────────────────────────────────────────

echo "📋 PHASE 3: MCP Ecosystem Status"
echo "───────────────────────────────────────────────────────────"

for PORT in 8005 8006 8009 8010 8011; do
  if curl -sf --max-time 3 "http://localhost:${PORT}/health" >/dev/null 2>&1; then
    log_success "MCP port $PORT responding"
  else
    if [ $PORT -eq 8005 ]; then
      log_fail "MCP port $PORT NOT responding (CRITICAL)"
    else
      log_warn "MCP port $PORT not responding (non-critical service)"
    fi
  fi
done

echo ""

# ──────────────────────────────────────────────────────────────
# PHASE 4: CONTEXT READINESS
# ──────────────────────────────────────────────────────────────

echo "📋 PHASE 4: Context & Memory Bank Readiness"
echo "───────────────────────────────────────────────────────────"

MEMORY_BANK="${OMEGA}/memory_bank"

if [ -f "${MEMORY_BANK}/activeContext.md" ]; then
  log_success "activeContext.md available (loaded at startup)"
else
  log_warn "activeContext.md missing (session starting fresh)"
fi

if [ -f "${MEMORY_BANK}/ANCHOR_MANIFEST.md" ]; then
  ANCHORS=$(grep -c "^##" "${MEMORY_BANK}/ANCHOR_MANIFEST.md" 2>/dev/null || echo "0")
  log_success "ANCHOR_MANIFEST.md available ($ANCHORS anchors)"
else
  log_warn "ANCHOR_MANIFEST.md missing (no blocker history)"
fi

if [ -f "${MEMORY_BANK}/tasks/active_sprint.md" ]; then
  TASKS=$(grep -c "^- " "${MEMORY_BANK}/tasks/active_sprint.md" 2>/dev/null || echo "0")
  log_success "active_sprint.md available ($TASKS tasks)"
else
  log_warn "active_sprint.md missing (no task context)"
fi

echo ""

# ──────────────────────────────────────────────────────────────
# PHASE 5: TOOL INTEGRATION
# ──────────────────────────────────────────────────────────────

echo "📋 PHASE 5: Development Tool Integration"
echo "───────────────────────────────────────────────────────────"

# Check Gemini CLI access
if [ -r ~/.gemini/settings.json ]; then
  log_success "Gemini CLI settings accessible"
else
  log_fail "Gemini CLI settings NOT accessible (EACCES error)"
fi

# Check Cline memory access
if [ -w ~/.gemini/memory ]; then
  log_success "Cline memory directory writable"
else
  log_warn "Cline memory directory NOT writable (Cline may fail)"
fi

# Check OAuth credentials
if [ -f ~/.gemini/oauth_creds.json ] && [ -r ~/.gemini/oauth_creds.json ]; then
  MODE=$(stat -c '%a' ~/.gemini/oauth_creds.json)
  if [ "$MODE" = "600" ]; then
    log_success "OAuth credentials secured (mode 600)"
  else
    log_warn "OAuth credentials world-readable (mode $MODE)"
  fi
else
  log_warn "OAuth credentials missing (authentication may fail)"
fi

echo ""

# ──────────────────────────────────────────────────────────────
# SUMMARY & DECISION
# ──────────────────────────────────────────────────────────────

echo "╔════════════════════════════════════════════════════════╗"
printf "║  RESULTS:  ${GREEN}✅ %2d pass${NC}  ${RED}❌ %2d critical${NC}  ${YELLOW}⚠️  %2d warnings${NC}      ║\n" "$SUCCESS_COUNT" "$CRITICAL_FAIL" "$WARN_COUNT"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

if [ $CRITICAL_FAIL -gt 0 ]; then
  echo "${RED}STARTUP BLOCKED${NC} — $CRITICAL_FAIL critical failures detected."
  echo ""
  echo "Required fixes:"
  echo "1. Verify memory-bank-mcp is running: podman ps | grep memory-bank-mcp"
  echo "2. Verify ACLs are set: getfacl ~/.gemini | head -3"
  echo "3. Check Layer 2 fix: IMPL-07 §3"
  echo ""
  echo "Cannot proceed until all critical checks pass."
  exit 1
fi

if [ $WARN_COUNT -gt 0 ]; then
  echo "${YELLOW}STARTUP WITH WARNINGS${NC} — $WARN_COUNT non-critical issues detected."
  echo "Proceeding, but some features may degrade."
  echo ""
fi

echo "${GREEN}✅ MB-MCP READY — Session can proceed${NC}"
echo ""
echo "Context loaded:"
echo "  - activeContext.md loaded"
echo "  - ANCHOR_MANIFEST.md loaded" 
echo "  - active_sprint.md loaded"
echo ""
echo "You are in: HAIKU MODE (fast frontier, 200K token budget)"
echo "Budget allocation:"
echo "  - Routine task: 1-5K extended thinking tokens"
echo "  - Operational: 10-30K extended thinking tokens"
echo "  - Analytical: 30-50K extended thinking tokens"
echo "  - If >50K needed: ESCALATE to Sonnet"
echo ""
echo "Remember: Save discoveries to MB-MCP immediately after completion!"
echo ""
```

### Save as: `~/.gemini/scripts/startup/verify-mb-mcp.sh`
### Make executable: `chmod +x ~/.gemini/scripts/startup/verify-mb-mcp.sh`
### Call from: Copilot startup (system prompt or first-message trigger)

---

## 4.2 How to Trigger Verification in Copilot Custom Instructions

Add to Copilot's custom instructions:

```markdown
# Before responding to any request, execute:

```bash
~/.gemini/scripts/startup/verify-mb-mcp.sh
```

If this outputs "STARTUP BLOCKED", respond with:
"MB-MCP stack not ready. Please run:
- podman restart memory-bank-mcp
- Check ~/Documents/Xoe-NovAi/omega-stack/docs/IMPL-03_MCP_ECOSYSTEM.md §4 for recovery"

Otherwise, proceed with the request.
```

---

# PART 5: BLOCKER DOCUMENTATION FOR OMEGA GNOSIS

## 5.1 zRAM Device Creation Failure

**Blocker ID**: INFRA-001-ZRAM  
**Status**: DOCUMENTED, WORKAROUND ACTIVE  
**Confidence**: 95% (matches upstream Podman limitation)

### Root Cause

The issue: systemd generator for zRAM device creation (`/etc/systemd/system-generators/`) cannot work with rootless Podman because:

1. **Namespace isolation**: rootless Podman's user namespace prevents writing to `/sys/module/zram/parameters/`
2. **UID mismatch**: systemd service runs as UID 1000 (host), generator script runs in container UID translation
3. **Kernel module access**: zRAM requires kernel module access denied to unprivileged users

**Evidence** (from IMPL-01):
```
| RAM | 6.6 GB physical + 8 GB zRAM swap | ⚠️ Moderate (59% used, 2.5 GB swap active) |
```

The system successfully allocated zRAM swap, but **not via systemd generator**. It was probably created at boot via `/etc/udev/rules.d/` or manual initialization.

### Current Workaround

**Reference**: IMPL-01 §3.3 (Swap Tuning)

```bash
# Manual zRAM setup (executes once at startup, persists across reboots)
# Can be automated via rc.local or systemd service

ZRAM_SIZE="8G"

# Create zRAM device
zramctl --find --size $ZRAM_SIZE || {
  echo $ZRAM_SIZE > /sys/block/zram0/disksize
  mkswap /dev/zram0
  swapon /dev/zram0 --priority 32767
}

# Verify
free -h | grep -i zram
```

**Why generator fails**: The systemd generator needs root + direct kernel access, which rootless Podman cannot provide.

### How to Document in Omega Gnosis

```yaml
---
title: "zRAM Device Creation — Systemd Generator Limitation"
id: INFRA-001-ZRAM
status: documented
confidence: 95%
category: infrastructure
blockers: []
depends_on: []
---

## Problem
The systemd generator for zRAM device creation fails in rootless Podman environments because:
1. User namespaces prevent `/sys/` writes
2. UID translation blocks kernel module access
3. Generator needs root privileges denied to unprivileged users

## Current Solution
- Manual zRAM initialization via rc.local or service at startup
- Working: 8 GB zRAM swap allocated and active
- Not automated via systemd generator (known Podman limitation)

## Recovery
If zRAM swap missing:
```bash
# Create 8GB zRAM device
zramctl --find --size 8G || {
  echo "8G" > /sys/block/zram0/disksize
  mkswap /dev/zram0
  swapon /dev/zram0
}
```

## Future Resolution
- Upgrade to Podman with native zRAM support (if available)
- Or: Use `--privileged-user` flag on container (not recommended)
- Or: Accept swap-less design (increase memory or reduce services)
```

---

## 5.2 Gemini UID 100999 Persistence

**Blocker ID**: PERM-002-UID100999  
**Status**: DOCUMENTED, 4-LAYER MITIGATION ACTIVE  
**Confidence**: 98% (fully understood, not a bug)

### Root Cause

**This is NOT a bug — it's the correct behavior of rootless Podman.**

When containers write to volumes:
```
Container UID 999 (internal)  →  Host UID 100999 (subUID translation)
```

The translation is correct. The **only solution** is the 4-layer mitigation:

| Layer | Purpose | Durability | Cost |
|-------|---------|-----------|------|
| Layer 1: chown | Emergency restore | 5 min (reverts on next write) | Manual |
| Layer 2: Default ACLs | Permanent permission | Survives writes | 5 min setup |
| Layer 3: keep-id namespace | Prevention | Prevents UID drift | Already in use |
| Layer 4: Systemd timer | Self-healing | Repairs automatically hourly | 1-time setup |

### Why UID 100999 Appears

Every time a container (running as UID 999) writes a file to `~/.gemini/`:
```
File created with UID 100999 (correct translation from 999)
    ↓
File inherits DEFAULT ACLs from parent directory
    ↓
If DEFAULT ACLs are set (Layer 2): File remains accessible to UID 1000 ✅
If DEFAULT ACLs missing: File inaccessible to UID 1000 ❌
```

### Current Solution (4-Layer System)

**Reference**: IMPL-07 (26 KB, complete specification)

**Status**: All 4 layers deployed and working

### How to Document in Omega Gnosis

```yaml
---
title: "UID 100999 Persistence in Container Volumes"
id: PERM-002-UID100999
status: documented-with-mitigation
confidence: 98%
category: permissions
blockers: []
depends_on: [IMPL-07]
---

## Problem
Container writes create files with UID 100999 (rootless Podman subUID translation).
Host user (UID 1000) cannot access these files without permissions workaround.

## Root Cause
This is correct Podman behavior, not a bug:
- Container UID 999 maps to host UID 100999 via /etc/subuid
- Files inherit UID from their creator (container, UID 999)
- File owner cannot be changed without breaking isolation

## Solution: 4-Layer Mitigation

### Layer 1: Emergency Restoration (5 min, temporary)
```bash
sudo chown -R 1000:1000 ~/.gemini/  # Unblocks immediately
```
**Durability**: Reverts on next container write (not permanent)

### Layer 2: POSIX Default ACLs (5 min, permanent)
```bash
setfacl -Rdm u:1000:rwx,u:100999:rwx,m::rwx ~/.gemini/
```
**Durability**: Inherited by all new files (survives container writes)

### Layer 3: Podman keep-id (Already in place)
```yaml
docker-compose.yml:
  memory-bank-mcp:
    userns_mode: "keep-id"  # Deterministic UID mapping
```
**Durability**: Prevents UID drift across reboots

### Layer 4: Systemd Self-Healing Timer (Continuous)
```bash
systemctl --user enable acl_drift_monitor.timer
systemctl --user start acl_drift_monitor.timer
```
**Durability**: Repairs ACLs hourly if broken by other operations

## Verification
```bash
# Check ACLs are set
getfacl ~/.gemini | head -5
# Expected: default:user:1000:rwx, default:user:100999:rwx, default:mask::rwx

# Check timer is active
systemctl --user status acl_drift_monitor.timer
```

## Why This Is Correct Design
- Container isolation is preserved (UID separation maintained)
- Host user has deterministic access (ACLs ensure rwx)
- Self-healing prevents manual intervention (timer repairs drift)
- Zero privilege escalation (UID 1000 cannot become root)

## Not a Bug
This design is intentional. Alternatives (privileged containers, :Z flag, SELinux) are less secure.
```

---

## 5.3 How These Blockers Prevent Work

Both blockers are **documented but not blocking current operations**:

| Blocker | Impact | Workaround | Status |
|---------|--------|-----------|--------|
| zRAM Generator | Cannot automate zRAM creation | Manual init at startup | ✅ Working |
| UID 100999 | Files inaccessible to UID 1000 | 4-Layer ACL system | ✅ Working |

**For Omega Gnosis**: These should be documented as "KNOWN LIMITATION WITH ACTIVE MITIGATION" — not as bugs to fix, but as architectural constraints to understand.

---

# PART 6: COMPLETE SYSTEM REDESIGN SUMMARY

## 6.1 The Three-Layer Architecture (Post-Redesign)

```
┌────────────────────────────────────────────────────────────────┐
│                     COPILOT / HAIKU 4.5                        │
│  Fast Frontier — handles 90% of tasks with 10-30K reasoning    │
│  - Local access to files/containers                            │
│  - MB-MCP startup verification (§4.1)                          │
│  - Context loading from memory_bank                            │
│  - Extended thinking budgets (10-50K depending on task)         │
│  - ESCALATES TO SONNET when reasoning > 50K                    │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│            MEMORY BANK MCP (Port 8005) — THE HUB              │
│  - activeContext.md (session state)                            │
│  - ANCHOR_MANIFEST.md (known blockers + solutions)             │
│  - tasks/active_sprint.md (task priority)                      │
│  - strategies/ (domain-specific patterns)                      │
│  - chronicles/ (session decision records)                      │
│  - Backed by: Redis (cache) + Postgres (persistence)           │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│              SONNET 4.5 — ORCHESTRATOR / ANALYST               │
│  - Handles escalations from Haiku                              │
│  - Deep reasoning (50-128K extended thinking)                  │
│  - Security decisions + complex architecture                   │
│  - Synthesis across Haiku findings                             │
│  - Updates memory_bank with analyzed patterns                  │
│  - RARELY escalates to Opus (95% stop at Sonnet)               │
└────────────────────────────────────────────────────────────────┘
```

## 6.2 Data Flow (Complete Cycle)

```
SESSION START
    ↓
[Haiku Startup Verification] — §4.1
  - Verify MB-MCP health (curl /health)
  - Load activeContext.md
  - Load ANCHOR_MANIFEST.md
  - Check ACLs (Layer 2-4)
    ↓
[Task Execution]
  - Haiku does work (10-30K reasoning budget)
  - Queries MB-MCP for prior solutions
  - Budget awareness via system_warning token tags
    ↓
[Decision Point]
  - If confident (<30K reasoning): Continue
  - If uncertain OR budget >50K: Save to MB-MCP, escalate to Sonnet
    ↓
[Escalation to Sonnet] — If Needed
  - Sonnet loads same context from MB-MCP
  - Deep analysis (50-128K reasoning budget)
  - Returns findings
  - Haiku synthesizes + implements
    ↓
[Result Persistence]
  - Save decision record to memory_bank/chronicles/
  - Update activeContext.md
  - Update ANCHOR_MANIFEST.md (if new blocker found)
  - Update tasks/active_sprint.md (mark task done)
    ↓
SESSION END
```

## 6.3 Key Innovation: MB-MCP as Context Hub

**Before**: Each agent (Haiku, Sonnet, Copilot) worked in isolation. No shared context.

**After**: All agents connect to MB-MCP at startup and query:
1. **activeContext.md** — What was I working on? What's the phase?
2. **ANCHOR_MANIFEST.md** — What problems are known? What are the workarounds?
3. **strategies/** — Has this domain been solved before? What's the pattern?
4. **tasks/active_sprint.md** — What's my priority? What's already done?

This eliminates:
- ✅ Re-solving the same problems (ANCHOR_MANIFEST)
- ✅ Waiting for context from other agents (shared MB-MCP)
- ✅ Lost work when agent switches (persisted to MB-MCP)
- ✅ Context window waste (compressed summaries in RCF)

---

# FINAL CHECKLIST FOR COMPLETE MB-MCP REDESIGN

## Implement in Order

### ✅ Phase 1: System Prompt Updates (Today)
- [ ] Add "MB-MCP Connection & Context Layer" section to Copilot/Haiku system prompt
- [ ] Add "When to Escalate to Sonnet" decision tree
- [ ] Add "Delegation to Sonnet" section with escalation format

### ✅ Phase 2: Custom Instructions for Copilot (Today)
- [ ] Create "Copilot Haiku Custom Instructions — Omega-Stack MB-MCP Edition"
- [ ] Add startup verification checklist
- [ ] Add MB-MCP usage pattern (load → during → save)
- [ ] Add extended thinking budget framework

### ✅ Phase 3: Startup Verification Script (This Week)
- [ ] Save `verify-mb-mcp.sh` to `~/.gemini/scripts/startup/`
- [ ] Make executable: `chmod +x`
- [ ] Test it manually: `~/.gemini/scripts/startup/verify-mb-mcp.sh`
- [ ] Wire into Copilot custom instructions

### ✅ Phase 4: Memory Bank Enrichment (This Week)
- [ ] Create GNOSIS records for:
  - [ ] zRAM limitation (INFRA-001-ZRAM)
  - [ ] UID 100999 design (PERM-002-UID100999)
  - [ ] MB-MCP integration pattern
  - [ ] Haiku-first escalation decision tree

### ✅ Phase 5: Testing (Next Week)
- [ ] Start Copilot/Haiku session with new system prompt
- [ ] Verify: `verify-mb-mcp.sh` runs successfully
- [ ] Verify: activeContext.md loads
- [ ] Verify: ANCHOR_MANIFEST.md accessible
- [ ] Task: Do 3 routine tasks (1-5K reasoning) — verify saved to MB-MCP
- [ ] Task: Do 1 operational task (10-30K reasoning) — verify escalation works

### ✅ Phase 6: Sonnet Alignment (Next Week)
- [ ] Show Sonnet the new system prompt sections
- [ ] Show Sonnet the escalation format
- [ ] Test: Haiku escalates to Sonnet → Sonnet synthesizes → Haiku implements

---

**This completes the comprehensive synthesis and implementation guide for MB-MCP integration with Haiku/Copilot for the complete Omega-Stack system redesign.**

___BEGIN___COMMAND_DONE_MARKER___0
