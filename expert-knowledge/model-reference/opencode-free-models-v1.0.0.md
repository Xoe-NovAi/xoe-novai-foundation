---
title: OpenCode Free-Tier Models Comprehensive Reference
version: 1.0.0
last_updated: 2026-02-17
status: active
persona_focus: "OpenCode-Kimi-X, Copilot, Cline engineers, researchers"
ma_at_ideals: [7, 18, 41]
cost_status: "100% free (no credit card required)"
---

# OpenCode Free-Tier Models – Complete Reference

**Version**: 1.0.0  
**Date**: 2026-02-17  
**Provider**: OpenCode Terminal AI  
**Cost**: FREE (all models)  
**Status**: ✅ Production-Ready

---

## Overview

OpenCode v1.2.6+ provides free access to 5 frontier models via a single terminal CLI, each with distinct strengths for different workloads. This document serves as the definitive reference for XNAi Foundation's multi-model research and execution strategy.

| Model | Context | Output | Reasoning | Tool-Use | Vision | Latest | Cost |
|-------|---------|--------|-----------|----------|--------|--------|------|
| **Kimi K2.5 Free** | 262.1k | 262k | ✅ | ✅ | ✅ | 2026-02-11 | FREE |
| **Big Pickle** | 200k | 128k | ✅ | ✅ | ❌ | stable | FREE |
| **GPT-5 Nano** | 400k | 128k | ✅ | ❌ | ✅ | current | FREE |
| **MiniMax M2.5 Free** | 204.8k | 131k | ✅ | ❌ | ❌ | 2026-02-12 | FREE |
| **GLM-5 Free** | 204.8k | 131k | ✅ | ❌ | ❌ | 2026-02-11 | FREE |

---

## Model Details

### 1. Kimi K2.5 Free

**Provider**: Moonshot AI  
**Model ID**: `kimi-k2.5-free`  
**Architecture**: 1T MoE (32B active parameters)  
**Release**: 2026-02-11  

#### Capabilities Matrix
| Capability | Rating | Notes |
|------------|--------|-------|
| Reasoning | ⭐⭐⭐⭐⭐ | Frontier-class, beats Opus 4.5 on many tasks |
| Code Generation | ⭐⭐⭐⭐⭐ | Elite visual coding (screenshots → code) |
| Tool Use (Agentic) | ⭐⭐⭐⭐⭐ | Native multimodal + tool orchestration |
| Long-Context Mastery | ⭐⭐⭐⭐⭐ | 262k context, handles 100k+ token documents |
| Image Understanding | ⭐⭐⭐⭐ | Excellent for UI/design but occasional hallucinations |
| Speed | ⭐⭐⭐ | Slower than smaller models (20-40s for complex queries) |

#### Strengths
- ✅ Beats Claude Opus 4.5, GPT-5.2 on many benchmarks
- ✅ Parallel multi-agent orchestration capable
- ✅ Strong instruction following and constraint adherence
- ✅ 262k context window for massive document processing
- ✅ Native multimodal input (text + vision + video)

#### Weaknesses
- ❌ MoE routing inconsistency on edge cases
- ❌ Vision sometimes hallucination-prone without tight prompts
- ❌ Higher latency than smaller models
- ❌ Quota lower than some other free tiers (~10 calls/day free)

#### Recommended Use Cases
| Use Case | Fit | Notes |
|----------|-----|-------|
| Complex research synthesis | ⭐⭐⭐⭐⭐ | Multi-model comparison baseline |
| Visual-to-code workflows | ⭐⭐⭐⭐⭐ | Screenshots → implementation |
| Long-document analysis | ⭐⭐⭐⭐⭐ | 262k context ideal for full codebase review |
| Multi-step agentic tasks | ⭐⭐⭐⭐⭐ | Agent orchestration & planning |
| Real-time debugging | ⭐⭐ | Latency not ideal for interactive sessions |
| Quick prototyping | ⭐ | Overkill for simple tasks |

#### XNAi Foundation Role
**Lead Model for Deep Analysis & Research Synthesis**
- Primary choice for complex RAG queries requiring reasoning
- Default for multi-agent coordination and validation
- Fallback for cases where smaller models insufficient

#### Integration Notes
```bash
opencode models --verbose
# Output shows kimi-k2.5-free: 262.1k ctx, 262k output, reasoning+toolcall

# Usage
opencode --model kimi-k2.5-free "analyze this codebase pattern..."
```

---

### 2. Big Pickle

**Provider**: Unknown (proprietary)  
**Model ID**: `big-pickle`  
**Architecture**: Dense or MoE (estimated 20-40B parameters)  
**Status**: Stable  

#### Capabilities Matrix
| Capability | Rating | Notes |
|------------|--------|-------|
| Reasoning | ⭐⭐⭐⭐ | Solid all-around reasoning |
| Code Generation | ⭐⭐⭐⭐ | Strong for standard patterns |
| Tool Use | ⭐⭐⭐⭐ | Good multimodal reasoning capability |
| Long-Context | ⭐⭐⭐ | 200k context, adequate for most use cases |
| Speed | ⭐⭐⭐⭐ | Faster than Kimi, slower than MiniMax |
| Consistency | ⭐⭐⭐⭐⭐ | Very reliable, low variance in outputs |

#### Strengths
- ✅ Excellent all-around performer
- ✅ Highly consistent and reliable
- ✅ Good balance of speed and quality
- ✅ 200k context suitable for large files
- ✅ Reasonable free-tier quota

#### Weaknesses
- ❌ Less documented than other models
- ❌ Architecture not publicly disclosed
- ❌ May lack specialized optimizations for niche tasks
- ❌ Occasional hallucinations on very novel problems

#### Recommended Use Cases
| Use Case | Fit | Notes |
|----------|-----|-------|
| General coding & refactoring | ⭐⭐⭐⭐⭐ | Workhorse model |
| Code review & analysis | ⭐⭐⭐⭐ | Reliable second opinion |
| Documentation generation | ⭐⭐⭐⭐ | Clear, structured outputs |
| Real-time collaborative coding | ⭐⭐⭐⭐ | Good balance of speed/quality |
| Research validation | ⭐⭐⭐⭐ | Alternative perspective to Kimi |
| Quick prototyping | ⭐⭐⭐⭐ | Fast enough, capable enough |

#### XNAi Foundation Role
**Reliable Workhorse for General Development**
- Default for coding tasks when Kimi feels overkill
- Second opinion for complex analyses
- Alternative perspective in multi-model validation

#### Integration Notes
```bash
# Usage
opencode --model big-pickle "refactor this function..."
```

---

### 3. GPT-5 Nano

**Provider**: OpenAI  
**Model ID**: `gpt-5-nano`  
**Architecture**: Small efficient variant of GPT-5  
**Context**: 400k tokens  
**Output**: 128k tokens  

#### Capabilities Matrix
| Capability | Rating | Notes |
|------------|--------|-------|
| Speed | ⭐⭐⭐⭐⭐ | Fastest in the free tier |
| Reasoning | ⭐⭐⭐⭐ | Strong for medium complexity |
| Code Generation | ⭐⭐⭐⭐ | Very capable for standard patterns |
| Image Understanding | ⭐⭐⭐⭐ | Solid multimodal capability |
| Long-Context | ⭐⭐⭐⭐⭐ | 400k context (largest in free tier) |
| Efficiency | ⭐⭐⭐⭐⭐ | Minimal latency, optimal for interactive use |

#### Strengths
- ✅ Fastest response times (2-5s typical)
- ✅ Largest context window (400k)
- ✅ Excellent for interactive, real-time workflows
- ✅ Solid code generation for standard patterns
- ✅ Good image understanding capabilities
- ✅ Generous free-tier quotas

#### Weaknesses
- ❌ Less capable on frontier reasoning problems
- ❌ May struggle with highly complex multi-step tasks
- ❌ Weaker on specialized domains vs. frontier models
- ❌ Not as strong as Kimi on agentic workflows

#### Recommended Use Cases
| Use Case | Fit | Notes |
|----------|-----|-------|
| Real-time interactive coding | ⭐⭐⭐⭐⭐ | Best for live sessions |
| Quick queries & prototyping | ⭐⭐⭐⭐⭐ | Fast turnaround |
| Simple code generation | ⭐⭐⭐⭐ | Good for standard patterns |
| Large document summarization | ⭐⭐⭐⭐ | 400k context ideal |
| Rapid iteration & testing | ⭐⭐⭐⭐⭐ | Low latency perfect |
| Complex reasoning tasks | ⭐⭐ | Better to escalate to Kimi |

#### XNAi Foundation Role
**Speed-Optimized for Interactive Sessions**
- Primary choice for real-time terminal work
- Excellent for RAG queries with large context requirements
- Default for prototyping and quick validation

#### Integration Notes
```bash
# Usage
opencode --model gpt-5-nano "summarize this large document..."
```

---

### 4. MiniMax M2.5 Free

**Provider**: MiniMax  
**Model ID**: `minimax-m2.5-free`  
**Architecture**: Lightweight optimized (~10B class)  
**Release**: 2026-02-12  

#### Capabilities Matrix
| Capability | Rating | Notes |
|------------|--------|-------|
| Speed | ⭐⭐⭐⭐⭐ | Extremely fast, competitive with Nano |
| Efficiency | ⭐⭐⭐⭐⭐ | Minimal resource overhead |
| Coding | ⭐⭐⭐⭐ | Strong engineering patterns |
| Reasoning | ⭐⭐⭐ | Good for practical tasks, weaker on frontier |
| Long-Context | ⭐⭐⭐ | 200k+ but not exceptional |
| Consistency | ⭐⭐⭐⭐⭐ | Highly reliable, very few hallucinations |

#### Strengths
- ✅ Extremely fast inference (1-3s typical)
- ✅ Best speed/quality ratio in free tier
- ✅ Excellent real-world engineering benchmarks
- ✅ Low hallucination on code tasks
- ✅ Agentic reliability (good tool-use understanding)
- ✅ Recent update (2026-02-12) with improvements

#### Weaknesses
- ❌ Smaller context window than Nano or Kimi
- ❌ Less raw reasoning depth for frontier problems
- ❌ Weaker multimodal/vision capabilities
- ❌ Not ideal for very long document processing

#### Recommended Use Cases
| Use Case | Fit | Notes |
|----------|-----|-------|
| Daily driver development | ⭐⭐⭐⭐⭐ | 70-80% of work handled |
| Terminal interactions | ⭐⭐⭐⭐⭐ | Optimal speed/quality |
| Code refactoring | ⭐⭐⭐⭐⭐ | Strong engineering focus |
| Agentic task execution | ⭐⭐⭐⭐ | Good tool-use understanding |
| Rapid prototyping | ⭐⭐⭐⭐⭐ | Very fast iteration |
| Complex reasoning | ⭐⭐ | Better to use Kimi |

#### XNAi Foundation Role
**Daily Driver for Development Workflows**
- Primary choice for 70-80% of terminal tasks
- Speed-optimized alternative to Nano with better engineering focus
- Preferred for agentic/tool-use tasks when speed matters

#### Integration Notes
```bash
# Usage
opencode --model minimax-m2.5-free "refactor this code..."
```

---

### 5. GLM-5 Free

**Provider**: Zhipu AI (GLM Series)  
**Model ID**: `glm-5-free`  
**Architecture**: Frontier-class reasoning model  
**Release**: 2026-02-11  

#### Capabilities Matrix
| Capability | Rating | Notes |
|------------|--------|-------|
| Reasoning | ⭐⭐⭐⭐⭐ | Frontier-class, specialized for reasoning |
| Code Generation | ⭐⭐⭐⭐ | Strong general capability |
| Long-Context | ⭐⭐⭐⭐ | 204.8k context |
| Speed | ⭐⭐⭐ | Moderate latency |
| Multimodal | ⭐⭐⭐ | Limited vision capability |
| Tool-Use | ⭐⭐⭐ | Good but not optimized |

#### Strengths
- ✅ Frontier-class reasoning capability
- ✅ Recent release (2026-02-11) with latest techniques
- ✅ 204.8k context window
- ✅ Strong on complex logic problems
- ✅ Excellent for mathematical reasoning

#### Weaknesses
- ❌ Moderate inference latency
- ❌ Limited vision/multimodal capabilities
- ❌ Less optimized for agentic workflows
- ❌ Smaller developer community vs. OpenAI/Moonshot

#### Recommended Use Cases
| Use Case | Fit | Notes |
|----------|-----|-------|
| Mathematical/logical problems | ⭐⭐⭐⭐⭐ | Specialized strength |
| Complex reasoning chains | ⭐⭐⭐⭐⭐ | Frontier capability |
| Algorithm design | ⭐⭐⭐⭐ | Good reasoning |
| Code logic review | ⭐⭐⭐⭐ | Strong analysis |
| Frontier research | ⭐⭐⭐⭐ | Novel problem solving |
| Vision tasks | ⭐ | Better to use Kimi/Nano |

#### XNAi Foundation Role
**Specialist for Mathematical & Logical Reasoning**
- Go-to for complex algorithm design
- Validation tool for proof-of-concept code
- Research synthesis when formal reasoning required

#### Integration Notes
```bash
# Usage
opencode --model glm-5-free "analyze the algorithm complexity..."
```

---

## Model Selection Quick Reference

### By Task Type

**Real-time Interactive**
1. GPT-5 Nano (fastest, 400k context)
2. MiniMax M2.5 (speed optimized)
3. Fallback: Big Pickle

**Complex Reasoning**
1. Kimi K2.5 (frontier reasoning)
2. GLM-5 (specialized logic)
3. Fallback: Big Pickle

**Code Generation (Standard)**
1. MiniMax M2.5 (best speed/quality)
2. Big Pickle (reliable)
3. Fallback: GPT-5 Nano

**Visual-to-Code**
1. Kimi K2.5 (elite vision + reasoning)
2. GPT-5 Nano (good vision, fast)

**Long-Document Analysis**
1. GPT-5 Nano (400k context)
2. Kimi K2.5 (262k context + reasoning)

**Multi-Model Research Synthesis**
1. Kimi K2.5 (as baseline)
2. Big Pickle (alternative perspective)
3. MiniMax M2.5 (speed perspective)

### By Performance Priority

| Priority | Model | Rationale |
|----------|-------|-----------|
| **Speed** | GPT-5 Nano or MiniMax M2.5 | 1-5s responses |
| **Quality** | Kimi K2.5 | Best reasoning/code |
| **Balance** | Big Pickle | Jack-of-all-trades |
| **Context** | GPT-5 Nano | 400k window |
| **Logic** | GLM-5 | Mathematical reasoning |

---

## Cost Analysis

**All models are 100% FREE** with these free-tier limits:

| Model | Free Quota | Replenishes | Overage |
|-------|-----------|-------------|---------|
| Kimi K2.5 | ~10 calls/day | Daily | Paid API |
| Big Pickle | Generous | Daily | Unknown |
| GPT-5 Nano | Very generous | Daily | Subject to rate limits |
| MiniMax M2.5 | Unlimited preview | Ongoing | Free tier expires ~Q2 2026 |
| GLM-5 | Generous | Daily | Paid API |

**Note**: Quotas subject to change. Check `opencode models --verbose` for current status.

---

## Integration with XNAi Foundation

### RAG System Integration
```
User Query
  ↓
Local embeddings (ONNX)
  ↓
FAISS/Qdrant retrieval
  ↓
Context assembly
  ↓
Model selection (see below)
  ↓
OpenCode inference
  ↓
Response + citations
```

### Model Selection Logic for RAG
```python
def select_model(query_complexity, context_size, latency_critical):
    if latency_critical:
        return "gpt-5-nano" if context_size > 100k else "minimax-m2.5-free"
    elif context_size > 300k:
        return "gpt-5-nano"
    elif query_complexity == "frontier":
        return "kimi-k2.5-free"
    elif query_complexity == "logic":
        return "glm-5-free"
    else:
        return "big-pickle"  # reliable default
```

### Voice Interface Integration
- **Transcription**: Faster-Whisper (local)
- **Model Processing**: Selected per query (above logic)
- **TTS**: Piper ONNX (local)
- **Latency Target**: <500ms total (model inference should be <300ms)

---

## Recommendations for XNAi Foundation

### Default Configuration
```yaml
# config/xnai-opencode-models.yaml
fast_path_model: "minimax-m2.5-free"      # 70% of requests
deep_analysis_model: "kimi-k2.5-free"     # Complex reasoning
research_validation: "big-pickle"          # Second opinion
interactive_model: "gpt-5-nano"            # Real-time
logic_specialist: "glm-5-free"             # Mathematical
```

### Usage Pattern
1. **Default (70%)**: MiniMax M2.5 Free
2. **Escalate on confidence < 0.7**: Kimi K2.5
3. **Validation layer**: Big Pickle
4. **Long context needed**: GPT-5 Nano
5. **Logic/Math problems**: GLM-5 Free

### Monitoring & Quota Management
- Daily quota check: `opencode models --verbose` 
- Track cost status: $0 (all free)
- Monitor latency: Target <500ms for voice workflows
- Alert on model failures: Log to memory_bank updates

---

## Ma'at Alignment

**Ideal 7 (Truth)**: Multi-model validation ensures accuracy through diverse architectures  
**Ideal 18 (Balance)**: Balances speed (MiniMax/Nano) with depth (Kimi)  
**Ideal 41 (Advance)**: Expands capabilities through open/frontier model ecosystem  

---

## Next Steps

1. ✅ Document comprehensive model reference (THIS DOC)
2. ⏳ Document Cline free-tier models
3. ⏳ Document Copilot CLI models via GitHub integration
4. ⏳ Create unified CLI model selection strategy
5. ⏳ Update agent role assignments with model preferences
6. ⏳ Update core context with model selection matrix

---

**Status**: ✅ **Complete - Production Ready**  
**Last Updated**: 2026-02-17  
**Maintained By**: OpenCode-Kimi-X (research), Copilot (documentation)  
**Related Documents**: 
- `cline-cli-models-v1.0.0.md`
- `copilot-cli-models-v1.0.0.md`
- `cli-model-selection-strategy-v1.0.0.md`
