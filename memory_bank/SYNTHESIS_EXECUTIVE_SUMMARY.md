# Executive Summary: MB-MCP System Redesign
**Date**: March 14, 2026  
**Sources**: 15 Sonnet manuals + 10 Haiku-Sonnets docs + Omega-Stack memory_bank  
**Location**: Full synthesis saved to `COMPREHENSIVE_MB_MCP_SYNTHESIS.md` (1600 lines)

---

## CORE INSIGHT: Haiku-First with MB-MCP as Context Hub

**New Architecture**:
```
Copilot/Haiku 4.5 (Fast Frontier)
    ├─ 10-30K extended thinking tokens
    ├─ Local file/container access
    ├─ MB-MCP startup verification
    └─ ESCALATES to Sonnet when reasoning > 50K
           ↓
    Memory Bank MCP (Port 8005) — THE HUB
    ├─ activeContext.md (session state)
    ├─ ANCHOR_MANIFEST.md (blocker solutions)
    ├─ tasks/active_sprint.md (priority)
    └─ Backed by Redis + Postgres
           ↓
    Sonnet 4.5 (Orchestrator)
    ├─ 50-128K extended thinking
    ├─ Complex analysis + synthesis
    └─ Security decisions
```

---

## WHAT CHANGED

### System Prompt v2.1 (Add These Sections)

**New Section 1**: "MB-MCP Connection & Context Layer"
- Verify health at startup: `curl -sf http://localhost:8005/health`
- Load activeContext.md + ANCHOR_MANIFEST.md
- Query previous solutions from MB-MCP before solving
- Save discoveries immediately: `POST /memory`

**New Section 2**: "When to Escalate to Sonnet"
- Reasoning > 50K tokens → escalate
- Confidence < 0.70 → escalate
- Security decisions → escalate
- Token budget < 30K remaining → escalate

**New Section 3**: "Token Budget Awareness"
- Routine: 1-5K thinking tokens
- Operational: 10-30K thinking tokens
- Analytical: 30-50K thinking tokens
- Beyond 50K: ESCALATE

---

## MB-MCP CONNECTION REQUIREMENTS

### Startup Verification Checklist (4 Phases)

```bash
# Phase 1: Critical Services
curl -sf http://localhost:8005/health      # memory-bank-mcp MUST respond
redis-cli ping                              # Cache
pg_isready -h localhost -p 5432            # Persistence

# Phase 2: Permissions (4-Layer System)
getfacl ~/.gemini | grep "user:1000:rwx"   # ACLs Layer 2
podman inspect memory-bank-mcp              # keep-id namespace Layer 3
systemctl --user status acl_drift_monitor   # Self-healing timer Layer 4

# Phase 3: MCP Ecosystem
curl -sf http://localhost:{8005,8006,8009,8010,8011}/health

# Phase 4: Context
ls ~/.gemini/memory_bank/{activeContext,ANCHOR_MANIFEST,active_sprint}.md
```

### Production-Ready Verification Script

**Location**: `~/.gemini/scripts/startup/verify-mb-mcp.sh` (1600+ lines)

**Checks**:
1. ✅ memory-bank-mcp health (CRITICAL)
2. ✅ Redis cache (recommended)
3. ✅ Postgres (non-critical if cache works)
4. ✅ ACL permissions (Layer 2-4)
5. ✅ UID mapping validation
6. ✅ MCP ecosystem ports (8005-8014)
7. ✅ Context file availability
8. ✅ Development tool integration
9. ✅ Credential security

**Blocks startup** if critical checks fail. **Warns** on non-critical issues.

---

## HOW COPILOT SHOULD VERIFY MB-MCP AT STARTUP

### Custom Instruction (Add to Copilot)

```markdown
Before responding to ANY request, execute:
  ~/.gemini/scripts/startup/verify-mb-mcp.sh

If output is "STARTUP BLOCKED":
  Report: "MB-MCP not ready. Run recovery procedure [link]"
  
If output is "✅ MB-MCP READY":
  Load context from memory_bank/
  Proceed with task
```

### What Gets Loaded

1. **activeContext.md** — Current phase, what was I working on?
2. **ANCHOR_MANIFEST.md** — Known blockers, proven solutions
3. **tasks/active_sprint.md** — What's my priority?
4. **strategies/** — Domain-specific patterns

This prevents re-solving the same problems and accelerates task completion.

---

## BLOCKER DOCUMENTATION FOR GNOSIS

### INFRA-001-ZRAM: systemd Generator Failure

**Status**: DOCUMENTED, WORKAROUND ACTIVE  
**Confidence**: 95%  
**Impact**: Cannot automate zRAM creation via systemd generator

**Why**: rootless Podman's user namespace blocks kernel module access

**Workaround**: Manual zRAM initialization at startup (currently working, 8GB swap active)

**Recovery**:
```bash
zramctl --find --size 8G || {
  echo "8G" > /sys/block/zram0/disksize
  mkswap /dev/zram0
  swapon /dev/zram0
}
```

**For Gnosis**: Document as "KNOWN LIMITATION WITH ACTIVE MITIGATION" — not a bug, an architectural constraint.

### PERM-002-UID100999: Container File Ownership

**Status**: DOCUMENTED, 4-LAYER SOLUTION ACTIVE  
**Confidence**: 98%  
**Impact**: Container writes create UID 100999-owned files

**Why**: Correct behavior of rootless Podman subUID translation (NOT a bug)

**Solution**: 4-Layer mitigation system:
- **Layer 1**: Emergency chown (5 min, temporary)
- **Layer 2**: POSIX Default ACLs (5 min, permanent)
- **Layer 3**: Podman keep-id (prevents drift)
- **Layer 4**: Systemd timer (self-healing hourly)

**For Gnosis**: Document as "CORRECT DESIGN WITH INTENDED RESILIENCE" — shows how isolation + ACLs work together.

---

## SYSTEM PROMPT ADDITIONS (Copy These)

### Addition 1: MB-MCP Initialization

```markdown
## MB-MCP Connection & Context Layer

### At Every Session Start (Non-Negotiable)

1. **Verify MB-MCP Health**
   ```bash
   curl -sf http://localhost:8005/health
   ```
   If this fails → STOP. Cannot proceed without context hub.

2. **Load Active Context**
   - Query: `GET http://localhost:8005/context?session_id=...`
   - Load: `~/.gemini/memory_bank/activeContext.md`
   - Load: `~/.gemini/memory_bank/ANCHOR_MANIFEST.md`

3. **Read ANCHOR_MANIFEST**
   Contains semantic anchors preventing drift:
   - ✅ Known good solutions (use these patterns)
   - ❌ Known bad solutions (don't try these)
   - 🔄 In-progress work (coordinate with other agents)
   - 🎯 Current strategy (align with phase goals)

### During Session

- **After discoveries**: `POST /memory` to save learnings
- **Before decisions**: Query prior context `GET /history?topic=X`
- **When stuck**: Check ANCHOR_MANIFEST for similar solutions
- **At completion**: Update activeContext.md with evidence
```

### Addition 2: Escalation Rules

```markdown
## When to Escalate to Sonnet (Clear Decision Tree)

Escalate immediately if:

1. **Reasoning Depth Exceeded**
   - Task requires >50K extended thinking budget
   - Example: "Design entire microservice architecture"
   
2. **Security Decision Required**
   - Threat modeling, cryptography, privilege escalation
   - Example: "Should we use mTLS or OAuth?"

3. **Validation Failed**
   - Your confidence score < 0.70
   - Unexpected tool output

4. **Token Budget at Limit**
   - Remaining tokens < 30K and task not complete

**Escalation Format** (to MB-MCP):
```yaml
escalation:
  from: copilot-haiku
  reason: reasoning_depth_exceeded
  token_budget_used: 45000 / 200000
  confidence: 0.65
  task: [full task description]
  current_analysis: [summary]
  recommended_next_step: "[what Sonnet should do]"
```
```

### Addition 3: Extended Thinking Budgets

```markdown
## Extended Thinking Budget (Your Decision Framework)

From Table 2 (Haiku guide):

| Complexity | Budget | Example |
|-----------|--------|---------|
| Routine | 1-5K | Unit tests, syntax checks, summarization |
| Operational | 10-30K | Multi-file refactoring, algorithm analysis |
| Analytical | 30-50K | Architecture design, system debugging |
| Frontier | 50-128K | Long-horizon research (escalate to Sonnet) |

**Every 20K tokens**: Check `<system_warning>` for remaining budget.  
At 155K used: Switch to summary mode.  
At 170K used: Prepare handoff to Sonnet.
```

---

## CUSTOM INSTRUCTIONS FOR COPILOT HAIKU

**Add to Copilot Settings → Custom Instructions**:

```markdown
# Copilot Haiku — Omega-Stack MB-MCP Edition

## 1. Startup (Every Session)

Before any work:
```bash
~/.gemini/scripts/startup/verify-mb-mcp.sh
```

## 2. Load Context

```bash
cat ~/.gemini/memory_bank/activeContext.md
cat ~/.gemini/memory_bank/ANCHOR_MANIFEST.md
cat ~/.gemini/memory_bank/tasks/active_sprint.md
```

## 3. Work Pattern

- **Before solving**: Query MB-MCP for prior solutions
- **During work**: Save discoveries immediately
- **After task**: Update activeContext.md

## 4. Escalation (When Reasoning > 50K)

Save to MB-MCP with @sonnet tag:
```
@sonnet ESCALATION: [task]
Confidence: [0-1.0]
Budget: [tokens used]
Analysis: [findings]
Request: [what Sonnet should do]
```

## 5. Known Blockers (Don't Waste Time)

- ✅ zRAM generator: Known Podman limitation (INFRA-001)
- ✅ UID 100999: Correct design with ACL mitigation (PERM-002)
- 🔄 xnai-rag: Blocked by qdrant (waiting)
- 🔄 xnai-memory: Scaling issue (in progress)

## 6. Success = MB-MCP Filled

After session:
- ✅ activeContext.md updated
- ✅ ANCHOR_MANIFEST.md updated (if new blocker)
- ✅ chronicles/ has decision records
- ✅ active_sprint.md marked task complete
```

---

## IMPLEMENTATION CHECKLIST

### Week 1
- [ ] Copy system prompt sections to Copilot
- [ ] Add custom instructions to Copilot
- [ ] Save verify-mb-mcp.sh to ~/.gemini/scripts/startup/
- [ ] Test verification script manually

### Week 2  
- [ ] Start Copilot session with new system prompt
- [ ] Verify: verify-mb-mcp.sh passes all checks
- [ ] Verify: activeContext.md loads
- [ ] Complete 3 routine tasks (1-5K reasoning each)
- [ ] Check: Discoveries saved to MB-MCP

### Week 3
- [ ] Complete 1 operational task (10-30K reasoning)
- [ ] Test: Escalation to Sonnet works
- [ ] Test: Sonnet synthesizes, Haiku implements
- [ ] Update ANCHOR_MANIFEST.md with new patterns

### Week 4
- [ ] Document blockers INFRA-001 + PERM-002 in gnosis
- [ ] Verify 4-Layer permission system works
- [ ] Run full_stack_verify.sh (IMPL-09)
- [ ] Declare system ready for production

---

## WHAT THIS ACHIEVES

✅ **Haiku operates at peak efficiency** (fast frontier, 90% of tasks)  
✅ **Intelligent escalation to Sonnet** (only when reasoning > 50K)  
✅ **MB-MCP prevents duplicate work** (ANCHOR_MANIFEST knows all solutions)  
✅ **Context persists across sessions** (activeContext.md always available)  
✅ **Blockers clearly documented** (GNOSIS records with workarounds)  
✅ **Startup verification automated** (verify-mb-mcp.sh catches issues)  
✅ **Token budgets enforced** (system_warning tags manage context)  
✅ **Seamless model switching** (Haiku ↔ Sonnet via MB-MCP)  

---

## REFERENCE

**Full Synthesis**: `COMPREHENSIVE_MB_MCP_SYNTHESIS.md` (1600 lines)  
**Verification Script**: `~/.gemini/scripts/startup/verify-mb-mcp.sh` (complete + ready to use)  
**Source Materials**:
- Sonnet: ARCH-01, IMPL-01 to IMPL-10, SUPP-02/06/07 (15 docs, 175 KB)
- Haiku: Strategy Guide, System Prompt v2.1, Implementation Guide (10 docs, 150 KB)
- Omega-Stack: ARCHITECTURE.md, MEMORY_BANK_IMPROVEMENTS.md, ANCHOR_MANIFEST.md

**This completes the complete system redesign for proper MB-MCP integration with Haiku/Copilot for the Omega-Stack.**

