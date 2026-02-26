# Wave 5 Manual Split Test — Raptor vs Haiku vs MiniMax vs kat-coder-pro

**Date**: 2026-02-26  
**Status**: Test Plan (Updated - 4-Way)  
**Type**: Comparative Evaluation  
**Coordination Key**: `WAVE-5-MANUAL-SPLIT-TEST-2026-02-26`  
**Branch**: `feature/multi-account-hardening`

---

## 0. Multi-Account Integration

### 0.1 Account Status (Updated)

Run audit before split test:
```bash
python3 scripts/github-account-audit.py --recommend
```

**Current Status**:
| Account | Email | Copilot | Status |
|---------|-------|---------|--------|
| admin | xoe.nova.ai@gmail.com | 50/50 (100%) | 🟢 Daily Driver |
| contrib-01 | arcananovaai@gmail.com | 25/50 (50%) | 🟡 Split Test Ready |
| Other 5 | various | 50/50 (100%) | 🟢 Ready |

**Total Available**: 325 messages across 7 accounts

### 0.2 Account Selection

For split test, use **arcananovaai@gmail.com** (non-daily-driver, 25 messages remaining):
```bash
# Switch to split test account
gh auth switch --user Xoe-NovAi

# Verify
gh auth status
```

### 0.3 Quick Commands

```bash
# Pre-test: Check account status
python3 scripts/github-account-audit.py --recommend

# Switch account (for Copilot CLI)
gh auth switch --user Xoe-NovAi

# Run Raptor
copilot -m raptor-mini-preview "Create Wave 5 Manual..."

# Run Haiku
copilot -m claude-haiku-4-5 "Create Wave 5 Manual..."

# Run MiniMax (no GitHub needed)
opencode --model minimax-m2.5-free "Create Wave 5 Manual..."

# Run Cline (no GitHub needed)
cline --model kat-coder-pro "Create Wave 5 Manual..."
```

---

## 1. Executive Summary

This document outlines a 4-way split test to compare the performance of four AI models in creating a Wave 5 Implementation Manual:

| Model | Provider | Context Window | CLI Tool | Best For |
|-------|----------|---------------|----------|----------|
| **Raptor Mini** | GitHub Copilot | 264K | Copilot CLI | Multi-file refactoring, large context |
| **Haiku 4.5** | GitHub Copilot | 200K | Copilot CLI | Fast tactical tasks |
| **MiniMax M2.5** | OpenCode | 204K | OpenCode CLI | Speed, efficiency, SWE-bench 80.2% |
| **kat-coder-pro** | Cline CLI | 262K | Cline CLI | Free unlimited, large context |

**Primary Objective**: Evaluate each model's ability to create a comprehensive Wave 5 manual from identical context packages, measuring quality, completeness, and efficiency.

---

## 2. Model Specifications

### 2.1 Raptor Mini (Copilot CLI)

| Specification | Value |
|---------------|-------|
| **Provider** | GitHub Copilot |
| **Context Window** | 264,000 tokens |
| **Output Window** | 64,000 tokens |
| **Model ID** | `raptor-mini-preview` |
| **CLI** | `copilot` |
| **Command** | `copilot -m raptor-mini-preview "..."` |
| **Strengths** | Multi-file analysis, large context retention |
| **Weaknesses** | Rate limited (50 msgs/month/account) |

### 2.2 Claude Haiku 4.5 (Copilot CLI)

| Specification | Value |
|---------------|-------|
| **Provider** | GitHub Copilot (Anthropic) |
| **Context Window** | 200,000 tokens |
| **Output Window** | 64,000 tokens |
| **Model ID** | `claude-haiku-4-5` |
| **CLI** | `copilot` |
| **Command** | `copilot -m claude-haiku-4-5 "..."` |
| **Strengths** | Fast tactical tasks, speed |
| **Weaknesses** | Rate limited (50 msgs/month/account) |

### 2.3 MiniMax M2.5 Free (OpenCode CLI)

| Specification | Value |
|---------------|-------|
| **Provider** | MiniMax via OpenRouter |
| **Context Window** | 204,800 tokens |
| **Output Window** | 131,072 tokens |
| **Model ID** | `minimax-m2.5-free` |
| **CLI** | `opencode` |
| **Command** | `opencode --model minimax-m2.5-free "..."` |
| **Strengths** | Highest SWE-bench (80.2%), speed, unlimited |
| **Weaknesses** | Shared rate limit pool |

### 2.4 kat-coder-pro (Cline CLI)

| Specification | Value |
|---------------|-------|
| **Provider** | Cline CLI |
| **Context Window** | 262,144 tokens |
| **Output Window** | 32,768 tokens |
| **Model ID** | `kat-coder-pro` |
| **CLI** | `cline` |
| **Command** | `cline --model kat-coder-pro "..."` |
| **Strengths** | Large context (262K), free unlimited |
| **Weaknesses** | Requires Cline CLI setup |

**Reference**: `expert-knowledge/model-reference/OPENCODE-MODEL-COMPARISON-MATRIX-v1.0.0.md`

---

## 3. Split Test Architecture

### 3.1 Isolation Strategy

To ensure fair comparison, each model receives:
- **Identical context package** (same files, same information)
- **Same task instructions**
- **Isolated output directory** (no file sharing)
- **Separate evaluation**

```
┌─────────────────────────────────────────────────────────────┐
│                    IDENTICAL INPUT                           │
│  - RAPTOR-ONBOARDING-CONTEXT-DOCUMENT.md                  │
│  - WAVE-5-PREP-RESOURCES.md                                │
│  - WAVE-5-IMPLEMENTATION-MANUAL.md (existing)              │
│  - Task Instructions                                       │
└─────────────────────────────────────────────────────────────┘
            ↓       ↓       ↓       ↓
      ┌──────────┐┌──────────┐┌──────────┐┌──────────┐
      │ RAPTOR   ││  HAIKU   ││MINIMAX   ││   KAT    │
      │   MINI   ││   4.5    ││   M2.5   ││CODER-PRO │
      └──────────┘└──────────┘└──────────┘└──────────┘
            ↓       ↓       ↓       ↓
      ┌──────────┐┌──────────┐┌──────────┐┌──────────┐
      │ OUTPUT/  ││ OUTPUT/  ││ OUTPUT/  ││ OUTPUT/  │
      │ RAPTOR/  ││ HAIKU/   ││MINIMAX/  ││   KAT/   │
      └──────────┘└──────────┘└──────────┘└──────────┘
            ↓       ↓       ↓       ↓
      ┌──────────────────────────────────────────────┐
      │           EVALUATION PANEL                   │
      │  - Quality Metrics                            │
      │  - Completeness Score                         │
      │  - Token Efficiency                           │
      │  - Accuracy Rating                           │
      └──────────────────────────────────────────────┘
```

### 3.2 Output Directories

```
outputs/
├── raptor-wave5-manual/          # Raptor Mini output
│   ├── WAVE-5-MANUAL.md
│   ├── METRICS.json
│   └── EVALUATION.md
├── haiku-wave5-manual/           # Haiku 4.5 output
│   ├── WAVE-5-MANUAL.md
│   ├── METRICS.json
│   └── EVALUATION.md
├── minimax-wave5-manual/         # MiniMax M2.5 output
│   ├── WAVE-5-MANUAL.md
│   ├── METRICS.json
│   └── EVALUATION.md
└── katcoder-wave5-manual/          # kat-coder-pro output
    ├── WAVE-5-MANUAL.md
    ├── METRICS.json
    └── EVALUATION.md
```

---

## 4. Context Package

### 4.1 Required Files

Each model receives these files:

| File | Purpose |
|------|---------|
| `RAPTOR-ONBOARDING-CONTEXT-DOCUMENT.md` | Full project context |
| `WAVE-5-PREP-RESOURCES.md` | Wave 5 resources |
| `WAVE-5-IMPLEMENTATION-MANUAL.md` | Existing reference |
| `TASK-INSTRUCTIONS.md` | Specific task |
| `EVALUATION-CRITERIA.md` | Quality metrics |

### 4.2 Task Instructions

**Primary Task**: Create a comprehensive Wave 5 Implementation Manual that:
1. Builds upon existing Wave 5 documentation
2. Incorporates all Opus 4.6 recommendations
3. Includes multi-account CLI dispatch strategy
4. Is token-optimized for 200K context window
5. Contains clear phase-by-phase implementation guides

**Deliverables**:
- Phase 5A-5E implementation guides
- Acceptance criteria checklist
- Testing procedures
- Troubleshooting section
- Quick reference cards

---

## 5. Evaluation Criteria

### 5.1 Quality Metrics

| Metric | Weight | Description |
|--------|--------|-------------|
| **Completeness** | 25% | All 5 phases covered with implementation details |
| **Accuracy** | 25% | Correct technical details, valid file paths |
| **Actionability** | 20% | Clear steps, testable criteria |
| **Token Efficiency** | 15% | Quality per token spent |
| **Structure** | 15% | Logical organization, navigation |

### 5.2 Scoring Rubric

| Score | Rating | Definition |
|-------|--------|------------|
| 5 | Excellent | Exceeds expectations, innovative approaches |
| 4 | Good | Meets all requirements with high quality |
| 3 | Acceptable | Meets basic requirements |
| 2 | Poor | Missing significant components |
| 1 | Fail | Incomplete or incorrect |

### 5.3 Specific Evaluation Points

**Technical Accuracy**:
- [ ] All file paths valid and current
- [ ] Phase completion percentages accurate
- [ ] RQ items correctly identified
- [ ] Account configuration accurate

**Completeness**:
- [ ] All 5 phases (5A-5E) covered
- [ ] Acceptance criteria for each phase
- [ ] Testing procedures included
- [ ] Troubleshooting section present

**Usability**:
- [ ] Clear step-by-step instructions
- [ ] Copy-paste ready code blocks
- [ ] Quick reference sections
- [ ] Navigation clear

---

## 6. Execution Protocol

### 6.1 Pre-Execution Checklist

- [ ] Context packages created for each model
- [ ] Output directories prepared
- [ ] Evaluation criteria documented
- [ ] Account quotas verified (Copilot accounts)
- [ ] OpenCode session verified

### 6.2 Execution Order

**Phase 1: Raptor Mini (264K context)**
1. Load context package
2. Create Wave 5 manual
3. Save to `outputs/raptor-wave5-manual/`
4. Capture metrics

**Phase 2: Haiku 4.5 (200K context)**
1. Load context package (fresh)
2. Create Wave 5 manual
3. Save to `outputs/haiku-wave5-manual/`
4. Capture metrics

**Phase 3: MiniMax M2.5 (204K context)**
1. Load context package (fresh)
2. Create Wave 5 manual
3. Save to `outputs/minimax-wave5-manual/`
4. Capture metrics

**Phase 4: kat-coder-pro (262K context)**
1. Load context package (fresh)
2. Create Wave 5 manual
3. Save to `outputs/katcoder-wave5-manual/`
4. Capture metrics

### 6.3 Command Templates

**Raptor Mini**:
```bash
cd /home/arcana-novai/Documents/xnai-foundation
copilot -m raptor-mini-preview "Create a Wave 5 Implementation Manual using the provided context files. Output to outputs/raptor-wave5-manual/WAVE-5-MANUAL.md"
```

**Haiku 4.5**:
```bash
cd /home/arcana-novai/Documents/xnai-foundation
copilot -m claude-haiku-4-5 "Create a Wave 5 Implementation Manual using the provided context files. Output to outputs/haiku-wave5-manual/WAVE-5-MANUAL.md"
```

**MiniMax M2.5**:
```bash
cd /home/arcana-novai/Documents/xnai-foundation
opencode --model minimax-m2.5-free "Create a Wave 5 Implementation Manual using the provided context files. Output to outputs/minimax-wave5-manual/WAVE-5-MANUAL.md"
```

**kat-coder-pro**:
```bash
cd /home/arcana-novai/Documents/xnai-foundation
cline --model kat-coder-pro "Create a Wave 5 Implementation Manual using the provided context files. Output to outputs/katcoder-wave5-manual/WAVE-5-MANUAL.md"
```

---

## 7. Knowledge Gaps Identified

### 7.1 Research Needed

| Gap | Status | Priority |
|-----|--------|----------|
| Raptor Mini vs Haiku 4.5 quality comparison | ❓ Unknown | HIGH |
| MiniMax M2.5 vs other models for documentation | ❓ Unknown | HIGH |
| kat-coder-pro vs other models | ❓ Unknown | HIGH |
| Optimal prompt engineering for each model | ❓ Unknown | MEDIUM |
| Token efficiency benchmarks | ❓ Unknown | MEDIUM |

### 7.2 Hypotheses to Test

1. **Context Window Hypothesis**: Raptor's 264K will produce more comprehensive output
2. **Speed Hypothesis**: MiniMax M2.5 will complete fastest
3. **Quality Hypothesis**: Haiku 4.5 will have best speed/quality balance
4. **SWE-bench Correlation**: MiniMax's 80.2% SWE-bench correlates to better code accuracy
5. **Free Model Hypothesis**: kat-coder-pro provides best free unlimited option

---

## 8. Success Criteria

### 8.1 Test Success

| Criterion | Target |
|-----------|--------|
| All 4 models complete | 100% |
| Output files generated | 4/4 |
| Evaluation completed | 4/4 |
| Clear winner identified | Yes/No |

### 8.2 Outcome Categories

**If Raptor Wins**:
- Recommend for complex multi-file tasks
- Prioritize for large context requirements

**If Haiku Wins**:
- Recommend for daily tactical tasks
- Optimal balance of speed and quality

**If MiniMax Wins**:
- Recommend for documentation tasks
- Best value (free, unlimited)

**If kat-coder-pro Wins**:
- Recommend for budget-constrained tasks
- Best free unlimited option with large context

---

## 9. Timeline

| Phase | Duration | Model |
|-------|----------|-------|
| Setup | 30 min | N/A |
| Raptor Execution | 2-4 hours | Raptor Mini |
| Haiku Execution | 2-4 hours | Haiku 4.5 |
| MiniMax Execution | 2-4 hours | MiniMax M2.5 |
| Cline Execution | 2-4 hours | kat-coder-pro |
| Evaluation | 1 hour | All |
| **Total** | **10-18 hours** | |

---

## 10. File Manifest

### Documents in This Test Plan

| File | Purpose |
|------|---------|
| `SPLIT-TEST-PLAN.md` | This document - test design |
| `outputs/raptor-wave5-manual/` | Raptor output directory |
| `outputs/haiku-wave5-manual/` | Haiku output directory |
| `outputs/minimax-wave5-manual/` | MiniMax output directory |
| `outputs/katcoder-wave5-manual/` | kat-coder-pro output directory |

### Context Files (to be provided)

| File | Purpose |
|------|---------|
| `context/RAPTOR-ONBOARDING-CONTEXT-DOCUMENT.md` | Project context |
| `context/WAVE-5-PREP-RESOURCES.md` | Wave 5 resources |
| `context/TASK-INSTRUCTIONS.md` | Task details |
| `context/EVALUATION-CRITERIA.md` | Quality metrics |

---

## 11. Next Steps

1. **Create context packages** for each model
2. **Set up output directories**
3. **Verify account quotas** for Copilot accounts
4. **Verify Cline CLI** installation with kat-coder-pro model
5. **Execute Raptor first** (largest context, highest expectations)
6. **Execute Haiku second**
7. **Execute MiniMax third**
8. **Execute Cline fourth** (new CLI, evaluate compatibility)
9. **Evaluate all outputs** using criteria in Section 5

---

**Last Updated**: 2026-02-26  
**Status**: Ready for Execution  
**Coordination Key**: `WAVE-5-MANUAL-SPLIT-TEST-2026-02-26`
