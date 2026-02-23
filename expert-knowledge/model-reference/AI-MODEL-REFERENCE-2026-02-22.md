# XNAi Foundation — AI Model Reference

## Executive Summary

This document provides accurate, verified specifications for all AI models available through free CLI environments. **CRITICAL CORRECTION**: OpenCode context limits were previously misstated - the model context window is separate from OpenCode's internal memory management.

---

## OpenCode Zen Free Models

### All Free Models Available

| Model | Context Window | Max Output | SWE-bench | Best For |
|-------|---------------|------------|-----------|----------|
| **GLM-5 Free** | 200K tokens | 128K tokens | 77.8% | Complex coding, agentic tasks |
| **Kimi K2.5 Free** | 262K tokens | 33K tokens | 76.8% | Vision-to-code, multimodal |
| **MiniMax M2.5 Free** | 196K-1M tokens | 65K-128K tokens | **80.2%** | Highest SWE-bench (free) |
| **Big Pickle** (GLM-4.6) | 200K tokens | 128K tokens | ~73% | Reliable daily driver |
| **GPT 5 Nano** | Unknown | Unknown | Entry-level | General tasks |

### GLM-5 Specifications (Current User Model)

| Specification | Value |
|--------------|-------|
| **Context Window** | **200,000 tokens** ✓ |
| **Max Output** | 128,000 tokens |
| **Architecture** | 744B total / 40B active (MoE) |
| **Training Data** | 28.5T tokens |
| **SWE-bench** | 77.8% (rivals Claude Opus 4.5) |
| **License** | MIT |
| **Free Tier Note** | Data used for training |

### Model Strengths & Weaknesses

| Model | Strengths | Weaknesses |
|-------|-----------|------------|
| **GLM-5 Free** | SOTA open-weights, excellent reasoning, tool use | Data used for training |
| **Kimi K2.5 Free** | Vision support, largest free context, strong reasoning | 33K output limit |
| **MiniMax M2.5 Free** | Highest SWE-bench, full-stack coding | Conflicting context specs |
| **Big Pickle** | Proven stable, GLM-4.6 quality | Less capable than GLM-5 |

### Context Window vs OpenCode Memory Management

**CRITICAL DISTINCTION:**

| Concept | Value | Description |
|---------|-------|-------------|
| **Model Context Window** | 200K (GLM-5) | Maximum tokens the MODEL can process |
| **OpenCode Compaction** | ~75% threshold | When OpenCode triggers summarization |
| **OpenCode Buffer** | Reserved space | Space reserved for response generation |

```
┌─────────────────────────────────────────────────────────┐
│                MODEL CONTEXT WINDOW (200K)               │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐    │
│  │           CONVERSATION HISTORY                   │    │
│  │  • User messages                                 │    │
│  │  • Assistant responses                           │    │
│  │  • Tool outputs                                  │    │
│  └─────────────────────────────────────────────────┘    │
│                        ↓                                │
│              [75% THRESHOLD = ~150K]                    │
│                        ↓                                │
│  ┌─────────────────────────────────────────────────┐    │
│  │           COMPACTION PROCESS                     │    │
│  │  Summarize old context, preserve recent files    │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

**NOTES:**
- The "10K buffer" mentioned in documentation refers to OpenCode's internal compaction behavior, NOT the model context window
- Models with large context (200K+) can degrade before compaction fires (GitHub issue #11314)
- Feature request exists to make compaction threshold configurable

---

## GitHub Copilot Free Models

### All Free Models Available

| Model | Context Window | Max Output | Multiplier | Best For |
|-------|---------------|------------|------------|----------|
| **Claude Haiku 4.5** | 200K tokens | 64K tokens | 1 | Fast, routine tasks |
| **GPT-4.1** | 128K tokens | 16K tokens | 1 | General-purpose |
| **GPT-4o** | 128K tokens | 16K tokens | 1 | Multimodal, visuals |
| **GPT-5 mini** | 128K tokens | 16K tokens | 1 | Balanced default |
| **Raptor mini** | **264K tokens** | 64K tokens | 1 | Multi-file, refactoring |

### Model Specifications

#### Claude Haiku 4.5
- **Context**: 200K tokens
- **Output**: 64K tokens
- **Vision**: ✅ Yes
- **Speed**: ⚡⚡⚡⚡⚡ (fastest)
- **Best For**: Quick syntax, small edits, documentation

#### Raptor Mini (GitHub Fine-tuned)
- **Context**: 264K tokens (LARGEST)
- **Output**: 64K tokens
- **Base**: Fine-tuned GPT-5-mini
- **Speed**: 4x faster than comparable models
- **Best For**: Multi-file refactoring, large context, agent mode

### Free Tier Limitations

| Resource | Limit |
|----------|-------|
| Completions | 2,000/month |
| Premium Requests | 50/month |
| Models with 1.0 multiplier | 5 models |

---

## Gemini CLI Models

### Free Tier Models

| Model | Context Window | Max Output | Best For |
|-------|---------------|------------|----------|
| **Gemini 3 Flash** | 1M tokens | 8K tokens | Fast, large context |
| **Gemini 3 Pro** | 1M tokens | 8K tokens | Research, complex tasks |

### Gemini CLI Features
- **AI Compression**: Automatic at 70% threshold
- **Hierarchical Memory**: Global/project/subdirectory
- **Session Management**: Project-specific with auto-save
- **Checkpointing**: `/restore` command for rollback

---

## CLI Environment Context Comparison (CORRECTED)

| CLI/Environment | Model Context | Internal Memory | Notes |
|-----------------|---------------|-----------------|-------|
| **OpenCode + GLM-5** | 200K | Compaction at ~75% | User's current setup |
| **OpenCode + Kimi K2.5** | 262K | Compaction at ~75% | Largest free context |
| **Gemini CLI** | 1M | AI compression at 70% | Best for research |
| **Cline CLI** | 200K | Manual | VS Code dependent |
| **Copilot CLI + Raptor** | 264K | Automatic | Best multi-file |
| **Copilot CLI + Haiku** | 200K | Automatic | Fastest |

---

## Recommendations by Use Case

### Maximum Context (Free)
1. **Gemini CLI** (1M tokens) - Best for research, large codebases
2. **Kimi K2.5 Free** (262K tokens) - Best for vision-to-code
3. **Raptor mini** (264K tokens) - Best for multi-file refactoring

### Best Coding Performance (Free)
1. **MiniMax M2.5 Free** - 80.2% SWE-bench (highest)
2. **GLM-5 Free** - 77.8% SWE-bench, MIT licensed
3. **Kimi K2.5 Free** - 76.8% SWE-bench, vision support

### Fastest Response (Free)
1. **Claude Haiku 4.5** - 2x faster than Sonnet
2. **GPT-5 mini** - Balanced speed/quality
3. **Raptor mini** - 4x faster than comparable models

### MC Agent Recommendation
**Primary**: Gemini CLI (1M context, AI compression, hierarchical memory)
**Alternative**: OpenCode + GLM-5 Free (200K context, current user setup)

---

## Data Usage Notes

| Environment | Data Usage |
|-------------|------------|
| OpenCode Free Models | Data used for training |
| Copilot Free | Per provider policy |
| Gemini CLI Free | Google AI Studio terms |
| Paid Models | Zero retention available |

---

**Last Updated**: 2026-02-22
**Sources**: Official documentation, community reports, model specifications