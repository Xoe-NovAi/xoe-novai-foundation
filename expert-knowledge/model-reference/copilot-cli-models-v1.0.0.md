---
title: GitHub Copilot CLI Free Models Reference
version: 1.0.0
last_updated: 2026-02-17
status: active
persona_focus: "Copilot CLI users, terminal engineers, GitHub ecosystem"
ma_at_ideals: [7, 18, 41]
cost_status: "Free tier through GitHub Copilot Free"
---

# GitHub Copilot CLI – Free Models Reference

**Version**: 1.0.0  
**Date**: 2026-02-17  
**Platform**: GitHub Copilot CLI (Terminal)  
**Status**: ✅ Production-Ready  

---

## Overview

GitHub Copilot CLI provides free access to a diverse suite of frontier models through the GitHub Copilot Free subscription. Unlike OpenCode (proprietary OpenCode service) and Cline (VS Code IDE), Copilot CLI is a **terminal-based agent** with built-in multi-model support and GitHub ecosystem integration.

This document catalogs the **12+ free models** available through Copilot CLI as of Feb 2026, focusing on models accessible via free-tier GitHub Copilot subscription.

| Model | Provider | Context | Output | Speed | Reasoning | Vision | Free Tier | Use Case |
|-------|----------|---------|--------|-------|-----------|--------|-----------|----------|
| **Claude Haiku 4.5** | Anthropic | 128k | 4k | ⭐⭐⭐⭐⭐ | ✅ | ✅ | YES | Fast tactical |
| **Claude Opus 4.5** | Anthropic | 128k | 4k | ⭐⭐⭐⭐ | ✅✅ | ✅ | YES | Deep analysis |
| **Claude Sonnet 4.5** | Anthropic | 128k | 4k | ⭐⭐⭐⭐ | ✅✅ | ✅ | YES | Balanced |
| **GPT-5** | OpenAI | 128k | 4k | ⭐⭐⭐ | ✅✅✅ | ✅ | YES | Reasoning |
| **GPT-5 Mini** | OpenAI | 128k | 4k | ⭐⭐⭐⭐⭐ | ✅ | ✅ | YES | Quick inference |
| **GPT-5.1** | OpenAI | 128k | 8k | ⭐⭐⭐⭐ | ✅✅ | ✅ | YES | Balanced |
| **GPT-5.2** | OpenAI | 128k | 4k | ⭐⭐⭐⭐ | ✅✅ | ✅ | YES | Latest |
| **GPT-5.1-Codex** | OpenAI | 128k | 8k | ⭐⭐⭐⭐ | ✅ | ❌ | YES | Code-optimized |
| **GPT-5.2-Codex** | OpenAI | 128k | 8k | ⭐⭐⭐⭐ | ✅ | ❌ | YES | Latest code |
| **GPT-5.1-Codex-32k** | OpenAI | 128k | 32k | ⭐⭐⭐ | ✅ | ❌ | YES | Large output |
| **Gemini 2.5 Pro** | Google | 128k | 4k | ⭐⭐⭐⭐ | ✅✅ | ✅✅ | YES | Multimodal |
| **Gemini 3 Flash** | Google | 128k | 4k | ⭐⭐⭐⭐⭐ | ✅ | ✅✅ | YES | Speed |
| **Gemini 3 Pro** | Google | 128k | 4k | ⭐⭐⭐⭐ | ✅✅ | ✅✅ | YES | Quality |
| **Grok Code Fast 1** | xAI | 128k | 8k | ⭐⭐⭐⭐⭐ | ✅ | ❌ | YES | Code-fast |

---

## Core Copilot CLI Models

### Claude Models (Anthropic)

#### Claude Haiku 4.5

**Model ID**: `claude-haiku-4.5`  
**Provider**: Anthropic  
**Context**: 128k tokens  
**Output**: 4k tokens  
**Specialization**: Fast tactical operations

#### Overview
The fastest Claude model with extended thinking capability. Excellent for real-time interactions and quick decisions in terminal workflows.

#### Capabilities
| Capability | Rating | Notes |
|------------|--------|-------|
| Speed | ⭐⭐⭐⭐⭐ | Fastest Claude variant |
| Thinking Mode | ⭐⭐⭐⭐ | Extended reasoning |
| Coding | ⭐⭐⭐⭐ | Very capable |
| Terminal Integration | ⭐⭐⭐⭐⭐ | Designed for CLI |
| Reliability | ⭐⭐⭐⭐⭐ | Anthropic quality |

#### Strengths
- ✅ Fastest Claude for interactive terminal work
- ✅ Extended thinking for complex decisions
- ✅ 128k context for file operations
- ✅ Excellent for real-time workflows
- ✅ Free via Copilot Free

#### Recommended Use Cases
- Real-time code review in terminal
- Quick debugging and iteration
- Interactive shell command generation
- Rapid prototyping and exploration
- Daily driver for terminal tasks

#### When to Use
```bash
# Default for most terminal interactions
gh copilot explain "command that failed"
gh copilot suggest "refactor this function"

# Interactive workflows where latency matters
for task in $(cat todo.txt); do
  gh copilot suggest "$task" --model claude-haiku-4.5
done
```

---

#### Claude Opus 4.5

**Model ID**: `claude-opus-4.5`  
**Provider**: Anthropic  
**Context**: 128k tokens  
**Output**: 4k tokens  
**Specialization**: Deep analysis & reasoning

#### Overview
Frontier Claude with extended thinking, excellent for complex reasoning problems, code architecture, and multi-step analysis.

#### Capabilities
| Capability | Rating | Notes |
|------------|--------|-------|
| Reasoning | ⭐⭐⭐⭐⭐ | Frontier-class |
| Thinking Depth | ⭐⭐⭐⭐⭐ | Best in Copilot free |
| Code Quality | ⭐⭐⭐⭐⭐ | Excellent |
| Speed | ⭐⭐⭐ | Slower (deep reasoning) |
| Multi-File | ⭐⭐⭐⭐⭐ | Excellent coordination |

#### Strengths
- ✅ Most capable Claude in free tier
- ✅ Extended thinking with deep reasoning
- ✅ 128k context for large codebases
- ✅ Excellent for architecture decisions
- ✅ Free via Copilot Free

#### Recommended Use Cases
- Complex code architecture decisions
- Deep system analysis
- Multi-file refactoring strategy
- Proof-of-concept validation
- Research & investigation tasks

#### When to Use
```bash
# Complex problem analysis
gh copilot suggest "design a new microservice for..." --model claude-opus-4.5

# Deep code review
gh copilot explain "analyze this architecture pattern" --model claude-opus-4.5
```

---

#### Claude Sonnet 4.5

**Model ID**: `claude-sonnet-4.5`  
**Provider**: Anthropic  
**Context**: 128k tokens  
**Output**: 4k tokens  
**Specialization**: Balanced speed/quality

#### Overview
Balanced variant between Haiku and Opus. Good speed with strong reasoning capability. Ideal for most general-purpose terminal tasks.

#### Capabilities
| Capability | Rating | Notes |
|------------|--------|-------|
| Speed | ⭐⭐⭐⭐ | Balanced |
| Reasoning | ⭐⭐⭐⭐ | Strong |
| Coding | ⭐⭐⭐⭐⭐ | Excellent |
| Reliability | ⭐⭐⭐⭐⭐ | High |

#### Strengths
- ✅ Best balance of speed and quality
- ✅ Good for most use cases
- ✅ Fast enough for interactive work
- ✅ Strong reasoning capability
- ✅ Free via Copilot Free

---

### OpenAI Models (GPT Series)

#### GPT-5 (Full Model)

**Model ID**: `gpt-5`  
**Provider**: OpenAI  
**Context**: 128k tokens  
**Output**: 4k tokens  
**Specialization**: Frontier reasoning

#### Overview
OpenAI's frontier model with advanced reasoning capability. Excellent for complex problem-solving and sophisticated analysis.

#### Capabilities
| Capability | Rating | Notes |
|------------|--------|-------|
| Reasoning | ⭐⭐⭐⭐⭐ | Frontier-class |
| Code Quality | ⭐⭐⭐⭐⭐ | Excellent |
| Speed | ⭐⭐⭐ | Slower (complex reasoning) |
| Context | ⭐⭐⭐⭐ | 128k adequate |

#### Strengths
- ✅ Most advanced reasoning in OpenAI tier
- ✅ Free via Copilot Free
- ✅ Excellent for frontier problems
- ✅ Strong on novel architectures

#### Recommended Use Cases
- Novel algorithm design
- Complex system analysis
- Advanced code generation
- Research-grade problem solving

---

#### GPT-5 Mini

**Model ID**: `gpt-5-mini`  
**Provider**: OpenAI  
**Context**: 128k tokens  
**Output**: 4k tokens  
**Specialization**: Speed-optimized

#### Overview
Lightweight, ultra-fast variant. Best choice when speed is critical and task complexity is moderate.

#### Capabilities
| Capability | Rating | Notes |
|------------|--------|-------|
| Speed | ⭐⭐⭐⭐⭐ | Fastest in free tier |
| Coding | ⭐⭐⭐⭐ | Very capable |
| Reasoning | ⭐⭐⭐ | Adequate for practical tasks |

#### Strengths
- ✅ Fastest inference in free tier
- ✅ Excellent for interactive terminal work
- ✅ Good for quick iterations
- ✅ Free via Copilot Free

#### When to Use
```bash
# Quick, fast operations
gh copilot suggest "implement quick sort" --model gpt-5-mini

# Interactive sessions
gh copilot explain "what does this do" --model gpt-5-mini
```

---

#### GPT-5.1

**Model ID**: `gpt-5.1`  
**Provider**: OpenAI  
**Context**: 128k tokens  
**Output**: 8k tokens  
**Specialization**: Balanced (8k output)

#### Overview
Latest stable GPT-5 variant with improved reasoning and larger output window. Good balanced choice.

#### Capabilities
| Capability | Rating | Notes |
|------------|--------|-------|
| Speed | ⭐⭐⭐⭐ | Good balance |
| Output | ⭐⭐⭐⭐ | 8k tokens (better than base) |
| Reasoning | ⭐⭐⭐⭐ | Strong |
| Coding | ⭐⭐⭐⭐⭐ | Excellent |

#### Strengths
- ✅ 8k output (larger responses)
- ✅ Good reasoning capability
- ✅ Balanced speed
- ✅ Free via Copilot Free

---

#### GPT-5.2

**Model ID**: `gpt-5.2`  
**Provider**: OpenAI  
**Context**: 128k tokens  
**Output**: 4k tokens  
**Status**: Latest release

#### Overview
Latest GPT-5 iteration with improvements across benchmarks. Current best OpenAI choice for general use.

#### Capabilities
| Capability | Rating | Notes |
|------------|--------|-------|
| Speed | ⭐⭐⭐⭐ | Good |
| Reasoning | ⭐⭐⭐⭐ | Strong (latest) |
| Coding | ⭐⭐⭐⭐⭐ | Excellent (latest) |
| Reliability | ⭐⭐⭐⭐⭐ | Best in OpenAI free tier |

---

#### GPT-5.1-Codex & GPT-5.2-Codex

**Model IDs**: `gpt-5.1-codex`, `gpt-5.2-codex`  
**Provider**: OpenAI  
**Specialization**: Code-optimized  
**Output**: 8k tokens  

#### Overview
Code-specialized variants of GPT-5 series. Better at software engineering tasks with larger output window.

#### Capabilities
| Capability | Rating | Notes |
|------------|--------|-------|
| Code Quality | ⭐⭐⭐⭐⭐ | Best for pure coding |
| Speed | ⭐⭐⭐⭐ | Good |
| Output | ⭐⭐⭐⭐ | 8k (larger) |
| Reasoning | ⭐⭐⭐ | Adequate (not specialized) |

#### Strengths
- ✅ Purpose-built for coding tasks
- ✅ 8k output for large code changes
- ✅ Free via Copilot Free
- ✅ Best speed/code-quality ratio

#### When to Use
```bash
# Pure coding tasks
gh copilot suggest "implement binary search tree" --model gpt-5.1-codex

# Large code generation
gh copilot suggest "create a complete REST API handler" --model gpt-5.1-codex
```

---

#### GPT-5.1-Codex-32k

**Model ID**: `gpt-5.1-codex-32k`  
**Provider**: OpenAI  
**Specialization**: Large output code generation  
**Output**: 32k tokens  

#### Overview
Extended-output variant for code generation tasks requiring very large responses (entire modules, complex implementations).

#### Capabilities
| Capability | Rating | Notes |
|------------|--------|-------|
| Output Size | ⭐⭐⭐⭐⭐ | 32k tokens (largest) |
| Code Quality | ⭐⭐⭐⭐⭐ | Excellent |
| Speed | ⭐⭐⭐ | Slower (large output) |

#### Strengths
- ✅ Largest output window in free tier
- ✅ Excellent for complete implementations
- ✅ Free via Copilot Free
- ✅ Great for scaffold generation

#### When to Use
```bash
# Large implementations
gh copilot suggest "create a complete authentication system" --model gpt-5.1-codex-32k

# Complex module generation
gh copilot suggest "generate a full ORM implementation" --model gpt-5.1-codex-32k
```

---

### Google Models (Gemini Series)

#### Gemini 2.5 Pro

**Model ID**: `gemini-2.5-pro`  
**Provider**: Google  
**Context**: 128k tokens  
**Output**: 4k tokens  
**Specialization**: Multimodal reasoning

#### Overview
Google's frontier multimodal model. Excellent for tasks involving vision, audio, and complex reasoning.

#### Capabilities
| Capability | Rating | Notes |
|------------|--------|-------|
| Multimodal Vision | ⭐⭐⭐⭐⭐ | Best in free tier |
| Audio Understanding | ⭐⭐⭐⭐ | Native audio support |
| Reasoning | ⭐⭐⭐⭐ | Strong |
| Code Quality | ⭐⭐⭐⭐ | Good (not specialized) |

#### Strengths
- ✅ Best multimodal capability in free tier
- ✅ Audio understanding (unique)
- ✅ Strong general reasoning
- ✅ Free via Copilot Free
- ✅ Excellent for design handoff

#### Recommended Use Cases
- Visual design specifications analysis
- UI mockup → code generation
- Audio transcription + analysis
- Complex multimodal problems

#### When to Use
```bash
# Design to code workflows
gh copilot suggest "generate code from this UI mockup" --model gemini-2.5-pro

# Audio transcript analysis
gh copilot explain "analyze this voice transcript and suggest code" --model gemini-2.5-pro
```

---

#### Gemini 3 Flash

**Model ID**: `gemini-3-flash`  
**Provider**: Google  
**Context**: 128k tokens  
**Output**: 4k tokens  
**Specialization**: Speed-optimized multimodal

#### Overview
Fast variant of Gemini 3 with good multimodal capability. Excellent for interactive terminal work requiring vision.

#### Capabilities
| Capability | Rating | Notes |
|------------|--------|-------|
| Speed | ⭐⭐⭐⭐⭐ | Very fast |
| Vision | ⭐⭐⭐⭐⭐ | Excellent multimodal |
| Reasoning | ⭐⭐⭐⭐ | Good |

#### Strengths
- ✅ Fastest multimodal in free tier
- ✅ Excellent for real-time terminal work
- ✅ Good vision capability
- ✅ Free via Copilot Free

---

#### Gemini 3 Pro

**Model ID**: `gemini-3-pro`  
**Provider**: Google  
**Context**: 128k tokens  
**Output**: 4k tokens  
**Specialization**: Multimodal reasoning

#### Overview
Professional-grade Gemini 3 with strong multimodal and reasoning capability. Best balance of quality and capability in Google tier.

#### Capabilities
| Capability | Rating | Notes |
|------------|--------|-------|
| Reasoning | ⭐⭐⭐⭐⭐ | Frontier-class |
| Vision | ⭐⭐⭐⭐⭐ | Excellent |
| Speed | ⭐⭐⭐⭐ | Good |
| Code Quality | ⭐⭐⭐⭐ | Strong |

#### Strengths
- ✅ Most capable Gemini in free tier
- ✅ Excellent multimodal + reasoning
- ✅ Free via Copilot Free
- ✅ Best Google choice for complex work

---

### xAI Models

#### Grok Code Fast 1

**Model ID**: `grok-code-fast-1`  
**Provider**: xAI  
**Context**: 128k tokens  
**Output**: 8k tokens  
**Specialization**: Code-optimized speed

#### Overview
Code-specialized frontier model from xAI optimized for speed. Excellent for pure coding tasks requiring fast inference.

#### Capabilities
| Capability | Rating | Notes |
|------------|--------|-------|
| Code Speed | ⭐⭐⭐⭐⭐ | Frontier coding + fast |
| Code Quality | ⭐⭐⭐⭐⭐ | Excellent |
| Output | ⭐⭐⭐⭐ | 8k tokens |
| Reasoning | ⭐⭐⭐⭐ | Good |

#### Strengths
- ✅ Fastest frontier code model in free tier
- ✅ 8k output for large implementations
- ✅ Free via Copilot Free
- ✅ Perfect balance for coding terminal work
- ✅ Fast inference without quality loss

#### Recommended Use Cases
- Real-time coding in terminal
- Complex code refactoring
- Large implementation generation
- Code-heavy engineering tasks

#### When to Use
```bash
# Fast complex coding
gh copilot suggest "refactor this microservice into modules" --model grok-code-fast-1

# Large code generation with speed
gh copilot suggest "create complete web framework" --model grok-code-fast-1
```

---

## Copilot CLI Model Selection Matrix

### By Task Type

| Task | Model 1 | Model 2 | Model 3 |
|------|---------|---------|---------|
| **Real-time interactive** | Claude Haiku | GPT-5 Mini | Gemini 3 Flash |
| **Complex reasoning** | Claude Opus | GPT-5 | Gemini 3 Pro |
| **Code generation** | Grok Code Fast 1 | GPT-5.1-Codex | Claude Sonnet |
| **Large code output** | GPT-5.1-Codex-32k | Grok Code Fast 1 | - |
| **Visual/design tasks** | Gemini 2.5 Pro | Gemini 3 Pro | Claude Opus |
| **Quick iterations** | GPT-5 Mini | Claude Haiku | Gemini 3 Flash |
| **Deep analysis** | Claude Opus | GPT-5 | Gemini 3 Pro |
| **Balanced general use** | Claude Sonnet | GPT-5.1 | Grok Code Fast 1 |

### Quick Selection Logic

```bash
# Terminal command for quick task selection
function select_model() {
    local task=$1
    case $task in
        "fast") echo "gpt-5-mini" ;;
        "code") echo "grok-code-fast-1" ;;
        "reason") echo "claude-opus-4.5" ;;
        "vision") echo "gemini-2.5-pro" ;;
        "balanced") echo "claude-sonnet-4.5" ;;
        "large-output") echo "gpt-5.1-codex-32k" ;;
        *) echo "claude-haiku-4.5" ;;
    esac
}

# Usage
gh copilot suggest "your task" --model $(select_model fast)
```

---

## Integration with XNAi Foundation

### Copilot CLI Role in Stack
```
Copilot CLI (tactical execution)
    ↓
OpenCode (research synthesis)
    ↓
Cline (VS Code implementation)
    ↓
Gemini CLI (ground truth verification)
```

### When to Use Copilot CLI
- **✅ Terminal-first workflows**: Native terminal integration
- **✅ GitHub ecosystem**: Native `gh` command integration
- **✅ Quick operations**: Fast model selection & switching
- **✅ Real-time iteration**: Haiku/Mini for interactive work
- **✅ Code generation**: Codex variants optimized for coding

### When NOT to Use Copilot CLI
- **❌ VS Code IDE work**: Use Cline instead
- **❌ Long-context requirements**: Use Copilot CLI with GPT-5.1 or larger
- **❌ Research synthesis**: Use OpenCode for multi-model research
- **❌ Final verification**: Use Gemini CLI for ground truth

---

## XNAi Foundation Recommended Configuration

```bash
# ~/.gh/hosts.yml (Copilot CLI configuration)
github.com:
    git_protocol: https
    api_endpoint: https://api.github.com

# Model preferences for XNAi workflows
COPILOT_DEFAULT_MODEL="claude-haiku-4.5"

# Environment aliases
alias copilot-fast="gh copilot suggest --model gpt-5-mini"
alias copilot-deep="gh copilot suggest --model claude-opus-4.5"
alias copilot-code="gh copilot suggest --model grok-code-fast-1"
alias copilot-vision="gh copilot suggest --model gemini-2.5-pro"
```

### Recommended Terminal Integration

```bash
# Smart model selection for different task types
copilot() {
    local task="${@}"
    
    if [[ "$task" == *"visual"* ]] || [[ "$task" == *"design"* ]]; then
        gh copilot suggest "$task" --model gemini-2.5-pro
    elif [[ "$task" == *"refactor"* ]] || [[ "$task" == *"module"* ]]; then
        gh copilot suggest "$task" --model grok-code-fast-1
    elif [[ "$task" == *"complex"* ]] || [[ "$task" == *"architecture"* ]]; then
        gh copilot suggest "$task" --model claude-opus-4.5
    else
        gh copilot suggest "$task" --model claude-haiku-4.5
    fi
}
```

---

## Cost Analysis

**All models are FREE via GitHub Copilot Free subscription**

- No per-use cost
- No rate limiting (reasonable usage)
- Unlimited model switching
- Free access to 12+ frontier models

---

## Ma'at Alignment

**Ideal 7 (Truth)**: Multiple models enable diverse perspectives on problems  
**Ideal 18 (Balance)**: Free models balance capability with accessibility  
**Ideal 41 (Advance)**: Frontier models expand terminal capabilities  

---

## Next Steps

1. ✅ Document Copilot CLI free models (THIS DOC)
2. ⏳ Create unified CLI model selection strategy
3. ⏳ Update agent role assignments with Copilot model preferences
4. ⏳ Update core context with Copilot integration guidance

---

**Status**: ✅ **Complete - Production Ready**  
**Last Updated**: 2026-02-17  
**Maintained By**: Copilot (self-documentation)  
**Related Documents**:
- `opencode-free-models-v1.0.0.md`
- `cline-cli-models-v1.0.0.md`
- `cli-model-selection-strategy-v1.0.0.md`
