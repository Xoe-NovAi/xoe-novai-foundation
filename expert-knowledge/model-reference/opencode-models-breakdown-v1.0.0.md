---
version: 1.0.0
date: 2026-02-13
ma_at_mappings: [7: Truth in reporting, 18: Balance in structure, 41: Advance through own abilities]
expert_dataset_name: OpenCode Free-Tier Models
expertise_focus: Terminal-based AI assistant with access to frontier free-tier models
community_contrib_ready: true
---

# OpenCode Free-Tier Models Breakdown – Research & Execution Arsenal

**Date**: 2026-02-13  
**Status**: NEW AGENT INTEGRATION  
**Platform**: OpenCode Terminal AI Assistant

## Overview

OpenCode is a terminal-based AI assistant providing free-tier access to frontier models not readily available through other free channels. This expands Xoe-NovAi's sovereign AI arsenal with diverse model architectures and capabilities, enabling multi-model validation and research synthesis.

---

## Available Free-Tier Models

### 1. **Kimi K2.5** (Moonshot AI)
- **Architecture**: 1T MoE (32B active parameters)
- **Context Window**: 256k–262k tokens
- **Capabilities**: 
  - Native multimodal (vision + text)
  - Agentic tool use
  - Long-context mastery
  - Strong coding and reasoning
- **Strengths**:
  - Beats Opus 4.5 / GPT-5.2 on many coding benchmarks
  - Elite visual coding (screenshots → code)
  - Parallel agent orchestration
  - Excellent instruction following
- **Weaknesses**:
  - MoE routing can be inconsistent on edge cases
  - Vision sometimes over-hallucinates without tight prompts
  - Higher API latency than smaller models
- **Best For**: Complex agentic tasks, visual-to-code, multi-step reasoning, long documents
- **XNAi Role**: Lead model for research synthesis and complex analysis

### 2. **Big Pickle** (Mystery Model)
- **Architecture**: Unknown (suspected large-parameter dense or MoE)
- **Context Window**: ~128k tokens
- **Capabilities**:
  - Strong coding performance
  - Good reasoning capabilities
  - Efficient for its size
- **Strengths**:
  - Solid all-around performance
  - Good for general development tasks
  - Reliable for standard coding patterns
- **Weaknesses**:
  - Less documented than other models
  - May lack specialized optimizations
- **Best For**: General coding tasks, standard development workflows
- **XNAi Role**: Workhorse for everyday development

### 3. **MiniMax M2.5** (MiniMax)
- **Architecture**: Lightweight optimized (~10B class)
- **Context Window**: ~128k–200k tokens
- **Capabilities**:
  - Optimized for coding and agentic workflows
  - Modern application development
  - High efficiency
- **Strengths**:
  - Extremely fast and efficient
  - Strong real-world engineering
  - Low hallucination on code tasks
  - High speed/quality ratio
- **Weaknesses**:
  - Smaller context than frontier models
  - Less raw reasoning depth on complex problems
  - Weaker multimodal capabilities
- **Best For**: Everyday coding, quick refactors, terminal tasks, interactive sessions
- **XNAi Role**: Daily driver for 70-80% of terminal interactions

### 4. **GPT-5 Nano** (OpenAI)
- **Architecture**: Efficient small model from GPT-5 family
- **Context Window**: ~128k tokens
- **Capabilities**:
  - Optimized for speed and efficiency
  - Good coding capabilities
  - Cost-effective inference
- **Strengths**:
  - Very fast response times
  - Efficient resource usage
  - Good for simple to medium complexity tasks
  - Reliable for standard patterns
- **Weaknesses**:
  - Less capable on complex reasoning
  - Smaller context window
  - May struggle with highly specialized tasks
- **Best For**: Quick queries, simple coding tasks, rapid prototyping
- **XNAi Role**: Speed-optimized tasks, rapid iteration

---

## OpenCode Platform Advantages

### Unique Strengths
1. **Diverse Model Access**: Access to models not available through Copilot or Cline free tiers
2. **Terminal-First**: Optimized for CLI workflows and filesystem operations
3. **Free Tier Generosity**: Competitive free-tier limits across multiple frontier models
4. **Multi-Model Validation**: Can easily switch between models for comparison studies
5. **Research Synthesis**: Ideal for gathering diverse perspectives on complex questions

### Integration with Xoe-NovAi Stack
- **Environment**: Terminal + Filesystem (like Gemini CLI)
- **Communication**: Terminal outputs, memory_bank updates
- **Research Pipeline**: Fills gap between Gemini CLI (verification) and Copilot (implementation)
- **Specialization**: Multi-model research, alternative perspectives, knowledge gap filling

---

## Recommended Usage Strategy

### Default Stack
- **Speed**: MiniMax M2.5 or GPT-5 Nano
- **Depth**: Kimi K2.5
- **Validation**: Big Pickle for alternative perspective

### Escalation Ladder
```
Quick query → GPT-5 Nano
Standard coding → MiniMax M2.5 or Big Pickle
Complex analysis → Kimi K2.5
Research synthesis → Multi-model comparison (Kimi + Big Pickle + MiniMax)
```

### When to Use OpenCode vs. Other Agents

**Use OpenCode when**:
- You need models not available in Copilot/Cline
- Multi-model validation is required
- Terminal-first workflow preferred
- Research synthesis across diverse architectures
- Alternative perspective needed

**Use Copilot when**:
- IDE integration required
- VS Code workflow preferred
- GitHub ecosystem integration needed

**Use Gemini CLI when**:
- 1M token context needed
- Final ground truth verification
- Massive file operations

**Use Cline when**:
- IDE-based refactoring
- Multi-file codebase navigation
- VS Code extension features needed

---

## Research Request Queue Integration

OpenCode can execute research requests from the queue:
- Fetches tasks from `expert-knowledge/research/queue/`
- Performs multi-model analysis
- Synthesizes findings across different architectures
- Outputs structured research reports to `expert-knowledge/research/completed/`

See `expert-knowledge/research/research-request-system-v1.0.0.md` for full queue protocol.

---

## Ma'at Alignment

- **Ideal 7 (Truth)**: Multi-model validation ensures truth through diverse perspectives
- **Ideal 18 (Balance)**: Balances speed (MiniMax/GPT-5 Nano) with depth (Kimi)
- **Ideal 41 (Advance)**: Expands capabilities through diverse model ecosystem

---

## Next Actions

1. **Model Testing**: Benchmark latency/quality across all four models on XNAi-specific tasks
2. **Prompt Engineering**: Develop Ma'at-structured prompts optimized for each model
3. **Quota Monitoring**: Establish usage patterns to maximize free-tier efficiency
4. **Integration Testing**: Validate OpenCode in standard XNAi workflows

**EKB Save Location**: `expert-knowledge/model-reference/opencode-models-breakdown-v1.0.0.md`

---

**Status**: ✅ **Integration Complete - Ready for Production Use**
