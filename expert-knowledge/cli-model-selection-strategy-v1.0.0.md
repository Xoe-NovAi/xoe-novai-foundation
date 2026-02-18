---
title: CLI Model Selection Strategy for XNAi Foundation
version: 1.0.0
last_updated: 2026-02-17
status: active
persona_focus: "All agents (Copilot, OpenCode, Cline, Gemini), team architects"
ma_at_ideals: [7, 18, 41]
related_documents: ["opencode-free-models-v1.0.0.md", "cline-cli-models-v1.0.0.md", "copilot-cli-models-v1.0.0.md"]
---

# CLI Model Selection Strategy – Unified Framework

**Version**: 1.0.0  
**Date**: 2026-02-17  
**Status**: ✅ Production-Ready  
**Scope**: All 3 CLI agents (OpenCode, Cline, Copilot) across all XNAi tasks

---

## Executive Summary

XNAi Foundation now has access to **30+ free frontier models** across three complementary CLI agents:

1. **OpenCode**: 5 free models (Kimi K2.5, Big Pickle, GPT-5 Nano, MiniMax M2.5, GLM-5)
2. **Cline**: 9 free models (Claude suite, GPT series, Gemini, Grok, Trinity)
3. **Copilot CLI**: 12+ free models (Claude, GPT-5 series, Gemini, Grok)

This document provides a **unified decision framework** for selecting the right CLI and model for any task.

---

## CLI Selection Decision Tree

### Primary Decision: Task Context & Environment

```
Task Assigned
    ├─→ Terminal-first? → Copilot CLI (default) or OpenCode
    ├─→ VS Code IDE? → Cline
    ├─→ Research/Analysis? → OpenCode (multi-model)
    ├─→ Real-time interactive? → Copilot CLI (fast models)
    ├─→ Deep reasoning needed? → Cline (extended thinking)
    └─→ Final verification? → Gemini CLI (1M context)
```

### By Primary Use Case

| Use Case | Best CLI | Reason | Secondary |
|----------|----------|--------|-----------|
| **Real-time terminal coding** | Copilot CLI | Native terminal, fast models | OpenCode |
| **VS Code IDE refactoring** | Cline | IDE-integrated, large context | Copilot CLI |
| **Research synthesis** | OpenCode | Multi-model comparison | Cline |
| **Complex reasoning** | Cline | Extended thinking, Opus/Sonnet | Copilot CLI |
| **Visual design → code** | Cline | Vision-optimized, then Copilot | OpenCode |
| **Quick prototyping** | Copilot CLI | Speed (Haiku, Mini, Flash) | OpenCode |
| **Large codebase analysis** | Cline | 262k context (Kimi) | Copilot CLI |
| **Code generation** | Copilot CLI | Codex variants (8k output) | Cline |
| **Interactive problem-solving** | Copilot CLI | Fast iteration loop | OpenCode |
| **Final verification** | Gemini CLI | 1M context, ground truth | Copilot CLI |

---

## CLI Specialization Matrix

### Copilot CLI (Terminal-First)
**Strengths**:
- ✅ Native GitHub ecosystem integration (`gh copilot`)
- ✅ 12+ models (fastest access switching)
- ✅ Ultra-fast models for interactive work
- ✅ Code-optimized variants (Codex 8k/32k output)
- ✅ Multi-modal support (Gemini series)

**Ideal For**:
- Daily terminal coding (70% of work)
- Real-time iteration and debugging
- Quick shell command generation
- Large code output tasks (GPT-5.1-Codex-32k)
- Multi-model quick validation

**Not Ideal For**:
- ❌ IDE-integrated refactoring
- ❌ Very long-context analysis (128k limit)
- ❌ Deep research synthesis (single-model limitation)

---

### OpenCode (Multi-Model Research)
**Strengths**:
- ✅ 5 diverse frontier models
- ✅ Best for multi-model validation
- ✅ Terminal-first like Copilot
- ✅ Excellent for research synthesis
- ✅ Large context windows (262k Kimi)

**Ideal For**:
- Research validation across diverse architectures
- Complex problem analysis requiring multiple perspectives
- Long-document processing (262k Kimi context)
- Architecture decisions needing consensus
- Novel problem-solving approaches

**Not Ideal For**:
- ❌ VS Code IDE integration
- ❌ Quick iterations (Kimi latency)
- ❌ Specialized code generation (no Codex variants)

---

### Cline (IDE-Integrated Deep Analysis)
**Strengths**:
- ✅ VS Code native integration
- ✅ Largest context (262k Kimi K2.5)
- ✅ Extended thinking modes (Claude)
- ✅ 9 frontier models
- ✅ Multi-file codebase understanding

**Ideal For**:
- IDE-based refactoring and coding
- Complex architectural decisions
- Multi-file coordinated changes
- Design specifications → implementation
- Extended-thinking problem solving

**Not Ideal For**:
- ❌ Terminal-first workflows (IDE required)
- ❌ Quick iterations in shell
- ❌ Research synthesis (fewer models)

---

## Task-by-Task Model Selection

### 1. Real-Time Interactive Terminal Coding

**Recommended Flow**:
```
Task: "quick bash script fix"
    ↓
Copilot CLI: GPT-5-Mini (fastest)
    ↓
Need reasoning? → GPT-5.1 or Claude Haiku
    ↓
Need vision? → Gemini 3 Flash
```

**Model Selection**:
1. **Speed critical**: GPT-5-Mini (Copilot)
2. **Balanced**: Claude Haiku (Copilot)
3. **Vision needed**: Gemini 3 Flash (Copilot)

**Command**:
```bash
gh copilot suggest "implement quick fix" --model gpt-5-mini
```

---

### 2. Complex Code Refactoring (Multi-File)

**Recommended Flow**:
```
Task: "refactor authentication module"
    ↓
Check environment:
    IDE open? → Cline with Kimi K2.5 (262k context)
    Terminal? → Copilot CLI with GPT-5.1-Codex (8k output)
    ↓
If deep planning needed → Claude Opus with thinking
```

**Model Selection**:
1. **In VS Code**: Cline → Kimi K2.5 or Claude Opus
2. **Terminal**: Copilot CLI → GPT-5.1-Codex
3. **Need reasoning**: Cline → Claude Opus (thinking)

**Commands**:
```bash
# VS Code (Cline)
# Cmd+Shift+C → Select Kimi K2.5 or Opus

# Terminal (Copilot CLI)
gh copilot suggest "refactor auth module" --model gpt-5.1-codex
```

---

### 3. Research Synthesis & Validation

**Recommended Flow**:
```
Task: "validate API design pattern"
    ↓
OpenCode: Multi-model analysis
    1. Kimi K2.5 (baseline reasoning)
    2. Big Pickle (alternative perspective)
    3. MiniMax M2.5 (efficiency perspective)
    ↓
Compare outputs → Consensus recommendation
```

**Model Selection**:
1. **Lead model**: OpenCode → Kimi K2.5
2. **Validation**: OpenCode → Big Pickle
3. **Efficiency check**: OpenCode → MiniMax M2.5

**Commands**:
```bash
# Chain multiple model analyses
opencode --model kimi-k2.5-free "analyze this pattern..."
opencode --model big-pickle "validate from different angle..."
opencode --model minimax-m2.5-free "efficiency assessment..."
```

---

### 4. Large Document Analysis (>100k tokens)

**Recommended Flow**:
```
Task: "analyze entire codebase architecture"
    ↓
Context needed > 128k? → Use large-context models
    Kimi K2.5 (262k) in:
        - Cline IDE
        - OpenCode terminal
    GPT-5 Nano (400k) in:
        - Copilot CLI (largest native context)
    ↓
Process and summarize
```

**Model Selection**:
1. **262k context**: Cline → Kimi K2.5
2. **400k context**: Copilot CLI → GPT-5 Nano
3. **Fallback**: Copilot CLI → GPT-5.1 (128k)

**Commands**:
```bash
# Cline IDE (Kimi K2.5 - 262k)
# Load entire codebase → Cline → Select Kimi K2.5

# Copilot CLI (GPT-5 Nano - 400k)
gh copilot explain "analyze architecture" --model gpt-5-nano
```

---

### 5. Code Generation (Large Output)

**Recommended Flow**:
```
Task: "generate complete REST API module"
    ↓
Output size needed:
    < 4k tokens → Any model (Copilot Codex, OpenCode)
    4-8k tokens → GPT-5.1-Codex or Grok Code Fast 1
    8-32k tokens → GPT-5.1-Codex-32k (Copilot only)
    > 32k → Split into phases
```

**Model Selection**:
1. **Largest output (32k)**: Copilot → GPT-5.1-Codex-32k
2. **Code-optimized (8k)**: Copilot → Grok Code Fast 1
3. **Balanced output**: Copilot → GPT-5.1-Codex
4. **IDE-based**: Cline → Claude Opus or Kimi

**Commands**:
```bash
# Largest single output
gh copilot suggest "generate complete REST API" --model gpt-5.1-codex-32k

# Code-specialized but faster
gh copilot suggest "generate authentication module" --model grok-code-fast-1

# IDE-based
# Cline: Select Claude Opus or Kimi K2.5
```

---

### 6. Reasoning-Heavy Problems

**Recommended Flow**:
```
Task: "design fault-tolerant consensus algorithm"
    ↓
Deep reasoning needed:
    With IDE? → Cline: Claude Opus (thinking) or Kimi K2.5
    Terminal? → Copilot: Claude Opus or GPT-5 (reasoning models)
    Research? → OpenCode: Kimi K2.5 + GLM-5 (logic specialist)
```

**Model Selection**:
1. **IDE + reasoning**: Cline → Claude Opus with thinking
2. **Terminal + reasoning**: Copilot → Claude Opus or GPT-5
3. **Research + logic**: OpenCode → Kimi K2.5, then GLM-5
4. **Alternative**: Copilot → Gemini 3 Pro (frontier reasoning)

**Commands**:
```bash
# Copilot CLI (frontier reasoning)
gh copilot suggest "design consensus algorithm" --model gpt-5

# Copilot CLI (alternative frontier reasoning)
gh copilot suggest "algorithm design" --model gemini-3-pro

# OpenCode (multi-model)
opencode --model kimi-k2.5-free "design algorithm..."
opencode --model glm-5-free "logic verification..."
```

---

### 7. Visual/Design-to-Code Tasks

**Recommended Flow**:
```
Task: "convert UI mockup to React components"
    ↓
Multimodal vision required:
    IDE? → Cline: Kimi K2.5 (vision + 262k context)
    Terminal? → Copilot: Gemini 2.5 Pro or Gemini 3 Pro
    Research? → OpenCode: Kimi K2.5 (multimodal)
```

**Model Selection**:
1. **Best vision + code**: Cline → Kimi K2.5
2. **Terminal vision**: Copilot → Gemini 2.5 Pro (frontier)
3. **Fast vision**: Copilot → Gemini 3 Flash
4. **Alternative**: Copilot → Claude Opus (good vision)

**Commands**:
```bash
# Cline IDE
# Load mockup → Cline → Select Kimi K2.5

# Copilot CLI
gh copilot suggest "generate React from mockup" --model gemini-2.5-pro

# Fast variant
gh copilot suggest "convert design to code" --model gemini-3-flash
```

---

### 8. Agentic/Tool-Use Tasks

**Recommended Flow**:
```
Task: "autonomously refactor and test"
    ↓
Tool-orchestration needed:
    Multi-turn in IDE? → Cline: Kimi K2.5 or Opus
    Multi-turn in terminal? → OpenCode: Kimi K2.5 or Big Pickle
    Single-turn tool calls? → Copilot: Any Claude or Grok
```

**Model Selection**:
1. **IDE agentic**: Cline → Kimi K2.5 (best agentic)
2. **Terminal agentic**: OpenCode → Kimi K2.5
3. **Tool-use focused**: Copilot → Grok Code Fast 1
4. **Reasoning-heavy**: Cline → Claude Opus

---

## XNAi Foundation Daily Workflow

### Recommended Agent Assignments by Role

#### Software Engineers (60% of work)
```yaml
# Primary CLI: Copilot CLI (terminal-first)
daily_tasks:
  - Quick coding: claude-haiku-4.5 (fast interactive)
  - Standard refactoring: gpt-5.1-codex (code-optimized)
  - Visual tasks: gemini-3-flash (fast multimodal)
  - Complex: grok-code-fast-1 (frontier code)

# Secondary CLI: Cline (when in IDE)
ide_tasks:
  - Complex refactoring: cline-kimi-k2.5 (262k context)
  - Architecture: cline-claude-opus-4.6 (thinking mode)

# Fallback: OpenCode (validation)
validation:
  - Multi-perspective: opencode multi-model
  - Research: opencode-kimi-k2.5
```

#### Researchers (80% of work)
```yaml
# Primary CLI: OpenCode (multi-model research)
research_tasks:
  - Analysis baseline: kimi-k2.5-free (frontier)
  - Validation: big-pickle (alternative perspective)
  - Efficiency: minimax-m2.5-free (speed check)
  - Logic-heavy: glm-5-free (reasoning specialist)

# Secondary CLI: Copilot CLI (fast iteration)
iteration:
  - Quick validation: claude-haiku-4.5
  - Reasoning check: gpt-5 or claude-opus

# Tertiary CLI: Cline (IDE verification)
verification:
  - Final check: cline-claude-opus-4.6
```

#### Architects (40% coding, 60% planning)
```yaml
# Primary CLI: Cline (deep analysis + IDE)
planning:
  - Architecture: cline-claude-opus-4.6 (thinking)
  - Large-context: cline-kimi-k2.5 (262k)
  - Design: cline-kimi-k2.5 (vision + context)

# Secondary CLI: OpenCode (research synthesis)
research:
  - Validation: opencode-multi-model
  - Consensus: kimi + big-pickle + glm-5

# Tertiary CLI: Copilot CLI (quick impl)
implementation:
  - Quick code: copilot-gpt-5.1-codex-32k
  - Large output: copilot-gpt-5.1-codex-32k
```

---

## Model Selection by Performance Metric

### By Speed (Latency Critical)
```
1. GPT-5-Mini (Copilot) - <2s
2. Claude Haiku 4.5 (Copilot) - <3s
3. Gemini 3 Flash (Copilot) - <3s
4. MiniMax M2.5 (OpenCode) - 3-5s
5. Grok Code Fast 1 (Copilot) - 4-5s

→ Use for real-time terminal work
```

### By Quality (Reasoning Heavy)
```
1. Claude Opus 4.6 (Cline/Copilot) - Frontier
2. Kimi K2.5 (Cline/OpenCode) - Frontier
3. GPT-5 (Copilot) - Frontier
4. Gemini 3 Pro (Copilot) - Frontier
5. Claude Sonnet 4.5 (Copilot) - Strong

→ Use for complex architecture decisions
```

### By Context Window (Large Documents)
```
1. GPT-5 Nano (Copilot) - 400k
2. Kimi K2.5 (Cline/OpenCode) - 262k
3. MiniMax M2.5 (OpenCode) - 204.8k
4. GLM-5 (OpenCode) - 204.8k
5. Claude/GPT/Gemini (Copilot) - 128k

→ Use for full-codebase analysis
```

### By Cost (All Free, But Quota-Limited)
```
Truly unlimited: MiniMax M2.5, GLM-5, Preview models
Generous daily: Kimi K2.5 (~10/day), Big Pickle
Rate-limited: OpenAI models (with free tier limits)

→ Check opencode --verbose for real-time quota
```

---

## Integration Patterns

### Pattern 1: Rapid Prototyping
```
Copilot CLI (fast iteration)
  ↓ GPT-5-Mini for initial structure
  ↓ (if needs thinking) Claude Haiku with thinking
  ↓ (if vision) Gemini 3 Flash
  ↓ (validate) OpenCode - Big Pickle alternative view
```

### Pattern 2: Enterprise Refactoring
```
Cline IDE (large context)
  ↓ Kimi K2.5 for full codebase analysis (262k)
  ↓ Claude Opus for architecture with thinking mode
  ↓ (validate with) OpenCode multi-model
  ↓ (final check) Gemini CLI for ground truth
```

### Pattern 3: Research-Driven Development
```
OpenCode (multi-model)
  ↓ Kimi K2.5 (lead analysis)
  ↓ Big Pickle (validation)
  ↓ MiniMax M2.5 (efficiency perspective)
  ↓ GLM-5 (logic verification)
  ↓ (implement) Copilot CLI or Cline
  ↓ (verify) Gemini CLI
```

### Pattern 4: Visual Design System
```
Cline IDE (best vision)
  ↓ Kimi K2.5 (vision + large context)
  ↓ (quick iteration) Copilot CLI Gemini 2.5 Pro
  ↓ (fast prototyping) Copilot CLI Gemini 3 Flash
  ↓ (validate) OpenCode consensus
```

---

## Escalation Matrix

### Problem: Standard Solution Insufficient

| Situation | Escalation Path |
|-----------|-----------------|
| Model output too small | Copilot GPT-5.1-Codex-32k (32k output) |
| Context insufficient | Cline Kimi K2.5 (262k) or Copilot GPT-5 Nano (400k) |
| Reasoning needed | Cline Claude Opus (thinking) or OpenCode Kimi K2.5 |
| Multiple perspectives | OpenCode (Kimi → Big Pickle → MiniMax consensus) |
| Visual required | Cline Kimi K2.5 or Copilot Gemini 2.5 Pro |
| Latency critical | Copilot GPT-5-Mini or Claude Haiku |
| Final verification | Gemini CLI (1M context, ground truth) |

---

## Cost & Quota Management

**All models are 100% FREE.** Quota management:

```bash
# Check available quotas
opencode models --verbose

# Monitor Copilot CLI (integrated with gh)
gh auth status

# Monitor Cline (VS Code settings)
# Cline → Settings → API Keys → Rate Limits

# Strategy: Tier daily usage
# 70% quick iterations (GPT-5-Mini, Haiku, Flash) - generous quotas
# 20% standard work (Codex, Kimi preview) - moderate quotas
# 10% frontier research (Claude Opus, Kimi) - limited but sufficient
```

---

## Ma'at Alignment

**Ideal 7 (Truth)**: Multiple models enable verification through diverse architectures  
**Ideal 18 (Balance)**: Speed (Mini, Haiku, Flash) balanced with depth (Opus, Kimi, GPT-5)  
**Ideal 41 (Advance)**: Frontier models expand capabilities through open ecosystem  
**Ideal 21 (Responsibility)**: Optimal model selection ensures efficient resource use  

---

## Quick Reference Card

### For Copilot CLI (Terminal)
```bash
# Speed: GPT-5-Mini
gh copilot suggest "quick task" --model gpt-5-mini

# Balanced: Claude Haiku
gh copilot suggest "standard task" --model claude-haiku-4.5

# Code-heavy: Grok Code Fast 1
gh copilot suggest "refactor" --model grok-code-fast-1

# Large output: GPT-5.1-Codex-32k
gh copilot suggest "large impl" --model gpt-5.1-codex-32k

# Visual: Gemini 2.5 Pro
gh copilot suggest "design to code" --model gemini-2.5-pro
```

### For Cline (IDE)
```
Cmd+Shift+C → Select model:
- Daily: Claude Haiku 4.5
- Complex: Claude Opus 4.6 (thinking)
- Large context: Kimi K2.5 (262k)
- Design: Kimi K2.5 (vision)
```

### For OpenCode (Terminal Research)
```bash
# Lead model: Kimi K2.5
opencode --model kimi-k2.5-free "analyze..."

# Validation: Big Pickle
opencode --model big-pickle "validate..."

# Efficiency: MiniMax M2.5
opencode --model minimax-m2.5-free "efficiency..."

# Logic: GLM-5
opencode --model glm-5-free "logic..."
```

---

**Status**: ✅ **Complete - Production Ready**  
**Last Updated**: 2026-02-17  
**Maintained By**: All agents (collaborative documentation)  
**Review Frequency**: Quarterly (as new models released)  

---

## Next Steps

1. ✅ Document selection strategy (THIS DOC)
2. ⏳ Update activeContext.md with agent model preferences
3. ⏳ Update .clinerules/00-core-context.md with matrix
4. ⏳ Create quick-reference cheat sheet
5. ⏳ Monitor quota usage patterns for optimization
