# GLM-5 Cline CLI Onboarding - XNAi Foundation

**Created**: 2026-02-27  
**Purpose**: Comprehensive onboarding for GLM-5 to take over model research and memory management tasks  
**Agent**: GLM-5 (via Cline CLI)

---

## Executive Summary

You are being handed a complex multi-project system with ongoing research in AI model evaluation, memory management, and system hardening. This document provides all context needed to continue the work effectively.

**Current Priority Focus**:
1. **Memory Management**: Fix OpenCode memory leak, implement Memory Guard
2. **Model Research**: Complete Raptor Mini context window research, update model compendium
3. **Gnosis Engine**: Continue knowledge synthesis system

---

## Part 1: Project Overview

### What is XNAi Foundation?

The XNAi Foundation is a **sovereign AI development stack** - a local-first, privacy-focused AI development environment using multiple AI models and providers.

### Hardware Constraints

| Resource | Specification | Notes |
|----------|---------------|-------|
| Physical RAM | 6.6 GB | One 8GB stick + iGPU sharing |
| zRAM Swap | 12 GB | zstd compression |
| Total Effective | ~18 GB | Physical + zRAM combined |
| CPU | AMD Ryzen 5700U | 8 cores / 16 threads |
| Storage | 109GB NVMe | 87GB used (85%) |

### Critical Issue: Memory Crisis

**2026-02-27**: OpenCode caused system-wide OOM by filling entire 12GB zRAM. Details:
- OpenCode has a **never-ending memory leak**
- Progressively fills RAM AND zRAM until OOM
- Must restart OpenCode every 2-3 hours
- Documented in: `docs/reference/IDE-CLI-KNOWN-ISSUES.md`

---

## Part 2: Current Work Status

### Active Branches

```
feature/gnosis-engine           # Knowledge synthesis system (FOUNDED)
feature/memory-management-system   # Memory management & research (ACTIVE)
feature/multi-account-hardening   # Previous work
```

### Key Files Created This Session

| File | Purpose |
|------|---------|
| `docs/gnosis/GNOSIS-ENGINE-2026-02-27.md` | Knowledge synthesis system main doc |
| `docs/gnosis/TEMPLATES/gnosis-templates.md` | Synthesis templates |
| `docs/reference/IDE-CLI-KNOWN-ISSUES.md` | IDE/CLI issues tracking |
| `memory_bank/research/RJ-RAPTOR-MINI-CONTEXT-2026-02-27.md` | Raptor research job |
| `memory_bank/MEMORY-CRISIS-RESOLUTION-2026-02-27.md` | Memory crisis strategy |
| `memory_bank/MEMORY-MANAGEMENT-SYSTEM-2026-02-27.md` | Memory management plan |

---

## Part 3: Priority Tasks

### P0: Memory Management

#### Problem
OpenCode has a progressive memory leak that fills both RAM and zRAM until system crash.

#### Current Work
- Created memory management strategy
- Researched systemd-oomd, PSI monitoring
- Identified Qwen3-0.6B as Memory Guard model

#### Your Tasks
1. **Fix Redis/Qdrant** integration for split test:
   - Write `changeme123` to `secrets/redis_password.txt`
   - Fix Qdrant vector dimension mismatch (64 → 384)
   - Update docker-compose for AOF persistence

2. **Implement Memory Guard**:
   - Create `scripts/xnai-memory-guard.sh`
   - Use Qwen3-0.6B model (~800MB)
   - Implement rule-based fallback for critical states

3. **Test split test framework**:
   - Run one model test to verify fixes

#### Reference Files
- `scripts/split_test/__init__.py` - Split test framework
- `configs/split-test-defaults.yaml` - Configuration
- `memory_bank/MEMORY-MANAGEMENT-SYSTEM-2026-02-27.md` - Full strategy

---

### P0: Model Research

#### Current Status

| Model | Provider | Context | Status |
|-------|----------|---------|--------|
| Raptor Mini | GitHub Copilot | 192K observed | RESEARCH IN PROGRESS |
| Claude Haiku 4.5 | GitHub Copilot | 200K | VERIFIED |
| MiniMax M2.5 | OpenCode | 196K-1M | VERIFIED |
| kat-coder-pro | Cline CLI | 262K | VERIFIED |

#### Research Job Created
See: `memory_bank/research/RJ-RAPTOR-MINI-CONTEXT-2026-02-27.md`

#### Your Tasks
1. **Complete Raptor Mini research**:
   - Find exact context window from online sources
   - Test via CLI vs Extension comparison
   - Update compendium

2. **Update model configs**:
   - Verify all model IDs correct
   - Update context windows in `configs/model-router.yaml`

#### Reference Files
- `configs/model-router.yaml` - Model configuration
- `memory_bank/research/MODEL-RESEARCH-COMPENDIUM-2026-02-27.md` - Compendium

---

### P1: Gnosis Engine

#### What is Gnosis Engine?
The knowledge synthesis system that transforms research into documentation and expert knowledge bases.

#### Your Tasks (if time permits)
1. Execute RJ-Synth-Memory (synthesize memory research → docs)
2. Execute RJ-Synth-Models (synthesize model research → expert-knowledge)
3. Update knowledge audit

#### Reference
- `docs/gnosis/GNOSIS-ENGINE-2026-02-27.md` - Full documentation

---

## Part 4: Key Resources

### Memory Bank Files

| File | Purpose |
|------|---------|
| `memory_bank/activeContext.md` | Current session context - ALWAYS READ FIRST |
| `memory_bank/MEMORY-CRISIS-RESOLUTION-2026-02-27.md` | Memory crisis details |
| `memory_bank/MEMORY-MANAGEMENT-SYSTEM-2026-02-27.md` | Memory strategy |
| `memory_bank/research/MODEL-RESEARCH-COMPENDIUM-2026-02-27.md` | Model compendium |

### Documentation Files

| File | Purpose |
|------|---------|
| `docs/reference/IDE-CLI-KNOWN-ISSUES.md` | IDE/CLI issues - READ THIS |
| `docs/gnosis/GNOSIS-ENGINE-2026-02-27.md` | Knowledge synthesis |
| `expert-knowledge/OPENCODE-CLI-COMPREHENSIVE-GUIDE-v1.0.0.md` | OpenCode guide |

### Configuration Files

| File | Purpose |
|------|---------|
| `configs/model-router.yaml` | Model configurations |
| `configs/split-test-defaults.yaml` | Split test config |
| `docker-compose.yml` | Stack services |

---

## Part 5: Critical Context

### The Memory Crisis (2026-02-27)

**What Happened**:
1. OpenCode memory grew from 500MB → 1.9GB over 3 hours
2. System RAM hit 97% (6.4GB/6.6GB)
3. zRAM hit 94% (11.3GB/12GB) - **ENTIRE SWAP FILLED**
4. System OOM - all processes killed

**Root Cause**: Unknown memory leak in OpenCode session/context management

**Mitigation**:
- Restart OpenCode every 2-3 hours
- Clear session: `rm -rf ~/.local/share/opencode/storage/session/*`
- Clear tool outputs: `rm -rf ~/.local/share/opencode/tool-output/*`

### OpenCode Issues Documented

From `docs/reference/IDE-CLI-KNOWN-ISSUES.md`:
- Never-ending memory leak (fills zRAM)
- Progressive growth: 500MB → 2GB+
- Database growth (opencode.db 100MB+)
- Context compaction at ~75% of model limit

### VSCodium/VS Code Issues

- Extension host crashes (OOM killer)
- Context window discrepancy (192K vs expected 264K)
- Memory exhaustion in extension host

---

## Part 6: Testing Commands

### Test Redis
```bash
redis-cli -h localhost -p 6379 -a changeme123 ping
```

### Test Qdrant
```bash
curl http://localhost:6333/collections
```

### Run Split Test
```bash
cd /home/arcana-novai/Documents/xnai-foundation
python3 scripts/split_test/__init__.py --models raptor-mini
```

### Check Memory
```bash
free -h
btop
```

---

## Part 7: Decision Framework

### If Redis/Qdrant Fix Works
→ Continue with split test execution
→ Move to model research completion

### If Memory Issues Return
→ Implement Memory Guard immediately
→ Consider alternative to OpenCode
→ Use shorter work cycles

### If Research Blocked
→ RJ-RAPTOR-MINI-CONTEXT-2026-02-27 has search strategies
→ Escalate to user if no progress after 30 minutes

---

## Part 8: Handoff Notes

### What Was Accomplished
- ✅ Gnosis Engine foundation established
- ✅ IDE/CLI issues documented
- ✅ Memory strategy designed
- ✅ Model compendium started
- ✅ Raptor research job created

### What's Ready for You
- All documentation created
- Strategy documented
- Research job defined
- Configuration files analyzed

### Your Goal
Complete the memory fixes and model research. Update memory_bank/activeContext.md with progress.

---

## Quick Start Checklist

- [ ] Read `memory_bank/activeContext.md` first
- [ ] Check current memory: `free -h`
- [ ] Review memory strategy: `memory_bank/MEMORY-MANAGEMENT-SYSTEM-2026-02-27.md`
- [ ] Start with Redis password fix
- [ ] Continue with Memory Guard implementation
- [ ] Complete Raptor research
- [ ] Update activeContext.md with progress

---

**Good luck! The system is ready for your expertise.**

---

**Onboarding Created**: 2026-02-27  
**By**: MC-Overseer (Research Mode)  
**For**: GLM-5 via Cline CLI
