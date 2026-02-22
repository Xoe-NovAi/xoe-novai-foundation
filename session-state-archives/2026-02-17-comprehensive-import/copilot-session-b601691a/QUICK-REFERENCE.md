# OpenCode & CLI Models - Quick Reference

**Last Updated**: 2026-02-17T21:30 UTC  
**Status**: ✅ All operational

---

## 🚀 Quick Start

### OpenCode (Back Online!)
```bash
# Start OpenCode with Kimi K2.5
opencode

# Run a quick research task
opencode "Analyze this codebase for RAG optimization opportunities"

# Check available models
opencode models
```

### Cline (VS Code)
- Config: `.clinerules/00-core-context.md`
- Models: Check `expert-knowledge/model-reference/cline-cli-models-v1.0.0.md`
- Primary: GPT-5.1-Codex (code generation)
- Fallback: Claude Opus 4.6 (reasoning)

### Copilot (CLI)
- Models: Check `expert-knowledge/model-reference/copilot-cli-models-v1.0.0.md`
- Primary: Claude Haiku 4.5 (speed)
- Fallback: GPT-5-mini (balance)

---

## 📊 Model Selection Matrix

### By Speed
**Fast** (<3 seconds):
- Claude Haiku 4.5
- GPT-5-mini
- Big Pickle

**Medium** (3-10 seconds):
- Claude Sonnet 4.5
- GPT-5
- Kimi K2.5-free

**Slow** (10+ seconds, deep thinking):
- Claude Opus 4.6
- GPT-5.2
- Grok Code Fast

### By Task Type
**Code Generation**: GPT-5.1-Codex, GPT-5.2-Codex  
**Research**: Kimi K2.5-free (262k context)  
**Reasoning**: Claude Opus 4.6, GPT-5.2  
**Quick Tasks**: Claude Haiku 4.5, GPT-5-mini  
**Vision/Multimodal**: Kimi K2.5, Gemini 2.5 Pro  
**Lightweight**: GLM-5-free, MiniMax M2.5-free  

### By Context Needed
**Large Context** (200k+):
- GPT-5 Nano (400k)
- Kimi K2.5 (262k)
- GLM-5-free (204.8k)

**Medium Context** (100k-200k):
- Big Pickle (200k)
- Claude family (128k)
- Most GPT/Gemini (128k)

---

## 🎯 Agent Assignments

| Agent | Primary | Secondary | When to Use |
|-------|---------|-----------|------------|
| **Copilot** | Claude Haiku 4.5 | GPT-5-mini | Tactical support, quick generation |
| **Cline** | GPT-5.1-Codex | Claude Opus 4.6 | Implementation, refactoring, code |
| **Gemini** | GPT-5.2-Codex | Kimi K2.5 | Execution, synthesis, research |
| **OpenCode** | Kimi K2.5-free | GPT-5-Nano | Multi-model research, analysis |
| **Grok MC** | Claude Opus 4.6 | GPT-5.2 | Strategic decisions, oversight |

---

## 📁 Documentation Files

### Model Reference
- `expert-knowledge/model-reference/opencode-free-models-v1.0.0.md`
- `expert-knowledge/model-reference/cline-cli-models-v1.0.0.md`
- `expert-knowledge/model-reference/copilot-cli-models-v1.0.0.md`

### Strategy & Selection
- `expert-knowledge/cli-model-selection-strategy-v1.0.0.md` ← **START HERE**

### Agent Configuration
- `.clinerules/00-core-context.md` (Model Selection Matrix section)
- `memory_bank/activeContext.md` (Free Models Integration section)

---

## 🔧 Configuration Files

### OpenCode
**Location**: `.opencode/opencode.json`  
**Current**: Minimal schema (model + MCP servers only)  
**Status**: ✅ Validated & working
```json
{
  "model": "opencode/big-pickle",
  "mcp": {
    "servers": {
      "xnai-rag": { ... }
    }
  }
}
```

### Cline
**Location**: `.clinerules/` (auto-loaded)  
**Current**: 6 lean rule files  
**Status**: ✅ Active
```bash
00-core-context.md          # Mission & tech stack
02-memory-bank.md           # How to read memory bank
03-coding-standards.md      # Code style
04-documentation.md         # Doc standards
05-dependencies.md          # Package mgmt
06-agents-coordination.md   # Multi-agent protocols
```

### Copilot
**Location**: `.github/copilot-instructions.md`  
**Status**: ✅ Active  
Auto-loads on CLI startup

---

## ⚡ Pro Tips

### OpenCode Power Moves
```bash
# Use Kimi K2.5 for complex research (262k context)
opencode --model opencode/kimi-k2.5-free "Analyze architecture"

# Use GPT-5-Nano for large codebases (400k context)
opencode --model opencode/gpt-5-nano "Review codebase"

# Use Big Pickle for balanced tasks
opencode --model opencode/big-pickle "Refactor patterns"
```

### Cline Power Moves
- For **code generation**: Use GPT-5.1-Codex (128k output!)
- For **complex reasoning**: Use Claude Opus 4.6
- For **refactoring**: Use GPT-5.1-Codex
- For **debugging**: Use Claude Opus 4.6 (better at edge cases)

### Copilot Power Moves
- Default to Claude Haiku 4.5 (fastest)
- Use GPT-5-mini when Haiku doesn't work
- Use Claude Opus when you need deep analysis

---

## 🛡️ Constraints & Rules

### Zero-Telemetry
✅ All models are free tier  
✅ No external data transmission  
✅ Sovereign & air-gap capable  

### Torch-Free
✅ No PyTorch, Triton, CUDA  
✅ ONNX/GGUF/Vulkan only  
✅ RAM-efficient (target <6GB)  

### Cost
✅ All $0 (completely free)  
✅ No premium tiers used  
✅ Community & developer tier models only  

---

## 🐛 Troubleshooting

### OpenCode won't start
```bash
# Check config validity
cat .opencode/opencode.json | python -m json.tool

# Verify CLI version
opencode --version

# List available models
opencode models
```

### Model not responding
```bash
# Try fallback model
opencode --model opencode/big-pickle "your task"

# Check network (if using API-based models)
curl https://opencode.ai/zen/v1/status
```

### Slow responses
- Use Claude Haiku 4.5 instead of Claude Opus
- Use GPT-5-mini instead of GPT-5
- Check network latency: `ping api.githubcopilot.com`

---

## 📞 Getting Help

1. **Model selection confused?**  
   → Read: `expert-knowledge/cli-model-selection-strategy-v1.0.0.md`

2. **Want model specs?**  
   → Read: `expert-knowledge/model-reference/*-models-v1.0.0.md`

3. **Agent workflow questions?**  
   → Read: `.clinerules/06-agents-coordination.md`

4. **General context?**  
   → Read: `.clinerules/00-core-context.md`

---

**All systems operational. You're ready to go!** 🚀
