# GitHub Status & Branching Strategy Analysis

**Date**: 2026-02-26  
**Status**: Analysis & Recommendations  
**Purpose**: Guide on GitHub branching, project structure, and split test infrastructure

---

## 1. Current GitHub Repository Status

### 1.1 Repository Overview

| Property | Value |
|----------|-------|
| **Repository** | `Xoe-NovAi/xoe-novai-foundation` |
| **Current Branch** | `xnai-agent-bus/harden-infra` |
| **Remote** | `origin` (GitHub) |
| **Commits Ahead of Main** | 33 commits |
| **Last Commit** | `fecd751` - Session 4 complete |

### 1.2 Branch Structure

```
main (protected)
├── phase5a/account-naming-onboarding
├── phase5a/rollback-automation
└── xnai-agent-bus/harden-infra (current)
    └── Working on: Agent Bus hardening, Phase 3C
```

### 1.3 Current Changes (Uncommitted)

| Category | Count | Description |
|----------|-------|-------------|
| **Deleted Files** | ~150+ | Archived projects, old session files |
| **Modified Files** | 10+ | ActiveContext, quota scripts, etc. |
| **New Files** | 80+ | New docs, benchmarks, memory_bank updates |

---

## 2. GitHub Branching Strategy Guidance

### 2.1 Understanding Branch Types

For a project like XNAi Foundation, here's the recommended approach:

| Branch Type | Purpose | Lifetime | Merge To |
|-------------|---------|----------|----------|
| **main** | Production-ready code | Permanent | - |
| **feature/*** | New features | Days-Weeks | develop or main |
| **bugfix/*** | Bug fixes | Days | main |
| **experiment/*** | Research/trying | Days | Usually discarded |
| **hotfix/*** | Emergency fixes | Hours | main immediately |

### 2.2 Your Current Situation

**You're on**: `xnai-agent-bus/harden-infra`  
**Ahead of main**: 33 commits  
**Status**: Work in progress (not pushed)

### 2.3 Should You Create a Branch for Split Test?

**YES** — Here's why:

1. **Isolation**: Keep experimental work separate from production code
2. **History**: Track changes without affecting main
3. **Collaboration**: Easy to merge when ready
4. **Rollback**: Simple to revert if needed

### 2.4 Recommended Branching Strategy

```
main (production)
    │
    ├── develop (integration)
    │       │
    │       ├── feature/split-test-infrastructure (NEW)
    │       │       └── For the metrics infrastructure
    │       │
    │       └── feature/wave5-manual-reconstruction
    │               └── For Wave 5 manual work
    │
    └── hotfix/ (if needed)
```

### 2.5 Merge Strategy Options

| Strategy | When to Use | Pros | Cons |
|----------|-------------|------|------|
| **Merge to main** | Stable, production-ready | Simple, linear history | Can break main |
| **Merge to develop** | Before main, for testing | Safer, testing first | Extra step |
| **Squash and merge** | Feature complete, clean history | Clean commits | Loses history |
| **Rebase and merge** | Keep linear history | Clean log | Rewrites history |

**Recommendation for XNAi**:
- **Squash small commits** into meaningful units
- **Merge to main** when feature is tested and stable
- **Keep branches** for long-running experiments (like split test)

---

## 3. Split Test Infrastructure Project Phases

### 3.1 Recommended Phases

| Phase | Name | Duration | Deliverables |
|-------|------|----------|--------------|
| **Phase 1** | Infrastructure Setup | 2-4 hours | Scripts, database schema, Redis config |
| **Phase 2** | Data Collection | 1-2 hours/run | Session logs, metrics JSON |
| **Phase 3** | Analysis | 1-2 hours | Comparison report, scoring |
| **Phase 4** | Dashboard | 2-4 hours | Visual comparison, insights |

### 3.2 Task Breakdown

```
split-test-infrastructure/
├── Phase 1: Setup
│   ├── [ ] Create metrics collection scripts
│   ├── [ ] Set up PostgreSQL tables
│   ├── [ ] Configure Redis streams
│   └── [ ] Test infrastructure
│
├── Phase 2: Execution
│   ├── [ ] Run Raptor Mini
│   ├── [ ] Run Haiku 4.5
│   ├── [ ] Run MiniMax M2.5
│   └── [ ] Capture all data
│
├── Phase 3: Analysis  
│   ├── [ ] Compare outputs
│   ├── [ ] Score quality
│   ├── [ ] Generate report
│   └── [ ] Document findings
│
└── Phase 4: Enhancement
    ├── [ ] Build dashboard
    ├── [ ] Automate future runs
    └── [ ] Standardize protocols
```

### 3.3 Create as Vikunja Tasks?

**YES** — This would be ideal for tracking:

```yaml
# Example Vikunja structure
- title: "Split Test Infrastructure - Phase 1"
  tasks:
    - Create metrics collection scripts
    - Set up PostgreSQL tables
    - Configure Redis streams
    - Test infrastructure
    
- title: "Split Test Execution - Raptor vs Haiku vs MiniMax"
  tasks:
    - Execute Raptor Mini
    - Execute Haiku 4.5
    - Execute MiniMax M2.5
    - Collect all data
```

---

## 4. Recommendations

### 4.1 Immediate Actions

1. **Create new branch** for split test:
   ```bash
   git checkout -b feature/split-test-infrastructure
   ```

2. **Commit current work** on `xnai-agent-bus/harden-infra`:
   ```bash
   # Review changes first
   git status
   
   # Add meaningful files (not archives)
   git add memory_bank/handovers/split-test/
   git add memory_bank/handovers/WAVE-5-MANUAL-SPLIT-TEST-PLAN.md
   git add memory_bank/handovers/ENHANCED-SPLIT-TEST-METRICS.md
   
   # Commit with descriptive message
   git commit -m "feat: Add Wave 5 split test infrastructure
   
   - Add split test plan (Raptor vs Haiku vs MiniMax)
   - Add enhanced metrics infrastructure design
   - Create evaluation criteria"
   ```

3. **Consider pushing** current branch to remote:
   ```bash
   git push -u origin xnai-agent-bus/harden-infra
   ```

### 4.2 Branch Strategy Summary

| Decision | Recommendation |
|----------|-----------------|
| **Create branch for split test?** | YES - `feature/split-test-infrastructure` |
| **Merge to main when done?** | YES - after testing |
| **Keep old branches?** | YES - archive, don't delete |
| **Push to remote?** | YES - backup and collaboration |

### 4.3 Next Steps

1. ✅ Decide on branching approach
2. ⏳ Create branch for split test
3. ⏳ Commit current changes
4. ⏳ Run split test with enhanced metrics
5. ⏳ Document results
6. ⏳ Merge to main when stable

---

## 5. Git Commands Quick Reference

| Command | Purpose |
|---------|---------|
| `git status` | Check current state |
| `git branch -a` | List all branches |
| `git checkout -b <name>` | Create and switch to new branch |
| `git add <file>` | Stage file for commit |
| `git commit -m "message"` | Commit staged changes |
| `git push` | Upload to remote |
| `git pull` | Download from remote |
| `git merge <branch>` | Merge branch into current |
| `git log --oneline` | View commit history |

---

## 6. File Created This Session

| File | Purpose |
|------|---------|
| `memory_bank/handovers/WAVE-5-MANUAL-SPLIT-TEST-PLAN.md` | Split test execution plan |
| `memory_bank/handovers/ENHANCED-SPLIT-TEST-METRICS.md` | Comprehensive metrics infrastructure |
| `memory_bank/handovers/RAPTOR-ONBOARDING-CONTEXT-DOCUMENT.md` | Context for Raptor |
| `memory_bank/handovers/WAVE-5-PREP-RESOURCES.md` | Wave 5 resources |
| `memory_bank/handovers/split-test/` | Test directory structure |

---

**Last Updated**: 2026-02-26  
**Guidance**: Create feature branch, commit current work, proceed with split test infrastructure
