# OpenCode CLI Model Card v1.0.0

**CLI**: OpenCode CLI  
**Version**: v1.2.6  
**Free Tier**: Yes (all models built-in, zero cost)  
**Last Updated**: 2026-02-17  
**Persona Focus**: Research, Code Exploration, Large Context Analysis

---

## Overview

OpenCode CLI provides **5 built-in free models** with zero API keys required. All models have massive context windows (200k-400k tokens) and are completely free to use. Excellent for research and code exploration.

---

## Free Tier Models (All Verified ✅)

| Model | Provider | Context | Released | Best For |
|-------|----------|---------|----------|----------|
| **GPT-5-Nano** | OpenAI | 400k | Feb 2026 | LARGEST context, code-aware |
| **Kimi K2.5-free** | Moonshot | 262k | Feb 2026 | Multimodal, video support |
| **GLM-5-free** | Zhipu | 204.8k | Feb 2026 | Reasoning, latest |
| **Big Pickle** | Custom | 200k | 2025 | Reasoning-optimized |
| **MiniMax M2.5-free** | MiniMax | 204.8k | Feb 2026 | Fast, reasoning |

**All**: Built-in, FREE ($0), no API keys, no authentication

---

## Detailed Model Specs

### GPT-5-Nano (RECOMMENDED for Large Context)
- **Provider**: OpenAI
- **Context Window**: 400k tokens (LARGEST)
- **Strengths**:
  - Enormous context (can process entire large codebases)
  - Code-aware training
  - Vision capable
  - Excellent for summarization
- **Weaknesses**: Not specialized like other models
- **Best For**: Whole-project analysis, large document processing
- **Example**:
  ```bash
  opencode --model gpt-5-nano "analyze patterns across entire repository"
  ```

### Kimi K2.5-free (RECOMMENDED for Multimodal)
- **Provider**: Moonshot AI
- **Context Window**: 262k tokens
- **Strengths**:
  - Multimodal (text + images + video)
  - Video understanding capability
  - Great for architecture diagrams
  - Recent training
- **Weaknesses**: Less familiar to Western teams
- **Best For**: Multimodal research, architecture analysis, video docs
- **Example**:
  ```bash
  opencode --model kimi-k2.5-free "analyze this architecture diagram and video walkthrough"
  ```

### GLM-5-free (RECOMMENDED for Reasoning)
- **Provider**: Zhipu (Tsinghua University)
- **Context Window**: 204.8k tokens
- **Strengths**:
  - Excellent reasoning
  - Latest training (Feb 2026)
  - Balanced performance
  - Good for complex problems
- **Weaknesses**: None significant
- **Best For**: Deep analysis, reasoning, complex requirements
- **Example**:
  ```bash
  opencode --model glm-5-free "break down this architectural challenge into components"
  ```

### Big Pickle (RECOMMENDED for Reasoning)
- **Provider**: Custom/Internal
- **Context Window**: 200k tokens
- **Strengths**:
  - Reasoning-optimized
  - Stable performance
  - Good for step-by-step analysis
- **Weaknesses**: Smallest context window
- **Best For**: Step-by-step reasoning, problem solving
- **Example**:
  ```bash
  opencode --model big-pickle "reason through this design decision"
  ```

### MiniMax M2.5-free (RECOMMENDED for Speed)
- **Provider**: MiniMax
- **Context Window**: 204.8k tokens
- **Strengths**:
  - Fast response time
  - Latest model (Feb 2026)
  - Good reasoning
  - Balanced capabilities
- **Weaknesses**: Not specialized
- **Best For**: Quick research, fast feedback, iteration
- **Example**:
  ```bash
  opencode --model minimax-m2.5-free "quickly identify issues in this code"
  ```

---

## Setup Instructions

### Step 1: Install OpenCode CLI
```bash
# Using Homebrew (macOS/Linux)
brew install opencode

# Using npm
npm install -g opencode

# Using cargo
cargo install opencode

# Verify installation
opencode --version
```

### Step 2: Fix Configuration (if needed)
OpenCode schema accepts ONLY these top-level keys:
- `model` (string, required)
- `mcp.servers` (object, optional)

```bash
# Valid minimal config
mkdir -p ~/.opencode
cat > ~/.opencode/opencode.json << 'EOF'
{
  "model": "gpt-5-nano",
  "mcp": {
    "servers": {}
  }
}
EOF
```

### Step 3: Verify Setup
```bash
# Test CLI
opencode --version

# List available models
opencode --list-models

# Test with a prompt
opencode "hello, list your free models"
```

### Step 4: Use OpenCode CLI
```bash
# Basic usage (uses default model)
opencode "analyze this code pattern"

# Use specific model
opencode --model gpt-5-nano "summarize this architecture"

# Interactive mode
opencode --interactive

# With file input
opencode --file=code.py "identify issues"

# Set default model
export OPENCODE_DEFAULT_MODEL=gpt-5-nano
```

---

## Model Selection Guide

### Choose GPT-5-Nano when:
- Processing large documents (>200k tokens)
- Need code-specific understanding
- Analyzing entire projects
- Processing images/vision tasks
- Need maximum context window

### Choose Kimi K2.5-free when:
- Working with images/diagrams
- Need video understanding
- Multimodal analysis required
- Architecture visualization
- Cross-modal reasoning

### Choose GLM-5-free when:
- Need deep reasoning
- Complex problem solving
- Want latest training
- Analyzing complex requirements
- Architecture decisions

### Choose Big Pickle when:
- Step-by-step reasoning needed
- Detailed problem breakdown
- Design justification
- Educational/learning purposes
- Clear reasoning trace

### Choose MiniMax M2.5-free when:
- Need fast feedback
- Quick iterations
- Resource-constrained
- Real-time analysis
- Speed important

---

## Integration with XNAi

### Recommended Workflow
```
Agent: Copilot (orchestrates)
  ↓
Agent: Cline (implements)
  ↓
Agent: OpenCode (researches/verifies)
  │
  ├─ Primary: gpt-5-nano (large context)
  ├─ Multimodal: kimi-k2.5-free (architecture)
  └─ Reasoning: glm-5-free (complex analysis)
  ↓
Agent: Gemini (synthesizes)
```

### Strengths for XNAi
- ✅ **All free**: Zero cost, no API keys
- ✅ **Massive context**: 200k-400k tokens
- ✅ **Multi-provider**: Diversity of models
- ✅ **Multimodal**: Vision/video support
- ✅ **No setup**: Built-in models
- ✅ **Latest**: Feb 2026 training data
- ✅ **Offline capable**: No external dependencies
- ✅ **Sovereign**: No telemetry, self-contained

### Challenges
- ⚠️ Less familiar than US-based models
- ⚠️ Requires understanding of different model providers
- ⚠️ No rate limits listed (assume reasonable)

---

## Best Practices for XNAi

### For Code Research (Agent: OpenCode)
```bash
# Use GPT-5-Nano for large codebase analysis
opencode --model gpt-5-nano "map all async patterns in this codebase"

# Use GLM-5 for design analysis
opencode --model glm-5-free "analyze this event loop implementation"

# Use Kimi for architecture diagrams
opencode --model kimi-k2.5-free "review this system architecture diagram"
```

### For Verification (After Agent: Cline)
```bash
# Quick check with MiniMax
opencode --model minimax-m2.5-free "spot check this implementation"

# Deep analysis with GLM
opencode --model glm-5-free "verify this design meets requirements"
```

### For Synthesis (Before Agent: Gemini)
```bash
# Prepare data with GPT-5-Nano
opencode --model gpt-5-nano "extract key patterns from entire codebase"

# Then pass to Gemini for high-level synthesis
```

---

## Commands Reference

```bash
# Version and info
opencode --version
opencode --info

# List models
opencode --list-models
opencode --models

# Use specific model
opencode --model gpt-5-nano "your prompt"

# With file input
opencode --file=document.txt "analyze this"

# Multiple files
opencode --files=file1.py,file2.py "compare these"

# Interactive mode
opencode --interactive
opencode -i

# Set default model
export OPENCODE_DEFAULT_MODEL=gpt-5-nano

# Get help
opencode --help
opencode -h
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Model not found" | Run `opencode --list-models`, ensure spelling correct |
| "Configuration invalid" | Check `.opencode/opencode.json` - only `model` and `mcp.servers` allowed |
| "Cannot connect" | Verify internet connection, no proxies blocking OpenCode servers |
| "Timeout" | Try simpler prompt or smaller file, models may be busy |

---

## Configuration (Minimal Schema)

OpenCode v1.2.6 **strictly enforces** schema - these are the ONLY valid top-level keys:

```json
{
  "model": "gpt-5-nano",
  "mcp": {
    "servers": {
      "example-server": {
        "command": "node",
        "args": ["server.js"]
      }
    }
  }
}
```

**Invalid keys** (will cause error):
- `version` ❌
- `project` ❌
- `agents` ❌
- `commands` ❌
- `memory` ❌
- `security` ❌
- `observability` ❌

---

## Comparison with Other CLIs

| Aspect | OpenCode | Copilot | Cline | Gemini |
|--------|----------|---------|-------|--------|
| Cost | FREE | FREE (limited) | FREE (OpenRouter) | FREE |
| Setup | None | GitHub login | API key | Google login |
| Models | 5 (built-in) | 3 (free tier) | 300+ | 6 |
| Context | 200k-400k | 128k-1M | 128k | 1M-2M |
| Vision | Yes | Yes | Yes | Yes |
| Speed | Fast | Fast | Variable | Variable |
| Multimodal | Yes | No | Yes | Yes |
| Strengths | Research, context | Orchestration | Implementation | Synthesis |

---

## Related Documentation

- `AGENT-CLI-MODEL-MATRIX-v1.0.0.md` - Agent role assignments
- `COPILOT-CLI-MODELS-v1.0.0.md` - Copilot CLI models
- `CLINE-CLI-MODELS-v1.0.0.md` - Cline CLI models
- `GEMINI-CLI-MODELS-v1.0.0.md` - Gemini CLI models
- `CLI-NOMENCLATURE-GUIDE-v1.0.0.md` - Naming conventions

---

## Resources

- OpenCode GitHub: https://github.com/opencode/opencode
- Documentation: https://docs.opencode.dev
- Model Providers:
  - OpenAI: https://openai.com
  - Moonshot (Kimi): https://www.moonshot.cn
  - Zhipu (GLM): https://www.zhipuai.cn
  - MiniMax: https://www.minimaxi.com
