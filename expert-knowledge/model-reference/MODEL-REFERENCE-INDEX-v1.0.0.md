---
title: Model Reference Index & Quick Navigation
version: 1.0.0
last_updated: 2026-02-17
status: active
---

# Model Reference Index – 30+ Free Frontier Models

**Quick Navigation for XNAi Foundation Model Documentation**

---

## 📚 Complete Documentation Set (2026-02-17)

### Core Reference Documents (Read These First)

#### 1. **CLI Model Selection Strategy** ⭐ START HERE
📄 **File**: `cli-model-selection-strategy-v1.0.0.md`  
📏 **Length**: 624 lines  
**Purpose**: Unified decision framework across all 3 CLIs  
**Best For**: Architects, team leads, decision-making

**Quick Wins**:
- Decision tree by task type
- Model performance metrics
- Integration patterns
- Escalation matrix
- Quick reference card

---

### CLI-Specific Model Catalogs

#### 2. **OpenCode Terminal – 5 Free Models**
📄 **File**: `opencode-free-models-v1.0.0.md`  
📏 **Length**: 467 lines  
**Focus**: Kimi K2.5, Big Pickle, GPT-5 Nano, MiniMax M2.5, GLM-5

**Sections**:
- Model details & capabilities
- Strengths/weaknesses
- Recommended use cases
- Cost analysis
- XNAi integration examples

**Key Models**:
- **Frontier Reasoning**: Kimi K2.5 (262k context)
- **Speed Optimized**: MiniMax M2.5, GPT-5 Nano
- **Logic Specialist**: GLM-5
- **Workhorse**: Big Pickle

---

#### 3. **Cline IDE – 9 Free Models**
📄 **File**: `cline-cli-models-v1.0.0.md`  
📏 **Length**: 509 lines  
**Focus**: Claude suite, GPT series, Gemini, Grok, Trinity

**Sections**:
- Primary vs secondary models
- IDE integration patterns
- Extended thinking capabilities
- Multimodal vision models
- Selection logic for Cline

**Key Models**:
- **Daily Driver**: Claude Haiku 4.5
- **Deep Analysis**: Claude Opus 4.6
- **Large Context**: Kimi K2.5 (262k)
- **Code Specialist**: Grok Code Fast 1
- **Multimodal**: Gemini 2.5 Pro

---

#### 4. **Copilot CLI – 12+ Free Models**
📄 **File**: `copilot-cli-models-v1.0.0.md`  
📏 **Length**: 639 lines  
**Focus**: Comprehensive terminal CLI integration

**Sections**:
- Claude models (Haiku/Sonnet/Opus)
- OpenAI GPT series (5/5.1/5.2, Codex)
- Google Gemini (2.5, 3 Pro, 3 Flash)
- xAI Grok Code Fast 1
- Model selection matrix

**Key Features**:
- **Largest Output**: GPT-5.1-Codex-32k (32k tokens!)
- **Fastest**: GPT-5-Mini, Claude Haiku, Gemini 3 Flash
- **Most Capable**: Claude Opus, GPT-5, Kimi K2.5
- **Best Code**: Codex variants & Grok Code Fast 1

---

## 🎯 Navigation by Use Case

### "I need to code right now" 
👉 `cli-model-selection-strategy-v1.0.0.md` → Section "Real-Time Interactive Terminal Coding"  
→ Use: **Copilot CLI** + GPT-5-Mini or Claude Haiku

### "I need to analyze a huge codebase"
👉 `cline-cli-models-v1.0.0.md` → Section "Large Document Analysis"  
→ Use: **Cline IDE** + Kimi K2.5 (262k context)

### "I need to research multiple perspectives"
👉 `cli-model-selection-strategy-v1.0.0.md` → Section "Research Synthesis"  
→ Use: **OpenCode** + multi-model (Kimi → Big Pickle → MiniMax)

### "I need large code output (>8k tokens)"
👉 `copilot-cli-models-v1.0.0.md` → Section "GPT-5.1-Codex-32k"  
→ Use: **Copilot CLI** + GPT-5.1-Codex-32k

### "I need visual design → code"
👉 `cline-cli-models-v1.0.0.md` → Section "Visual/Design-to-Code"  
→ Use: **Cline IDE** + Kimi K2.5 (vision + 262k context)

### "I'm stuck and need deep reasoning"
👉 `cli-model-selection-strategy-v1.0.0.md` → Section "Reasoning-Heavy Problems"  
→ Use: **Cline IDE** + Claude Opus with thinking mode

---

## 📊 Model Matrix Quick Reference

### By Speed (Fastest First)
```
1. GPT-5-Mini (Copilot) - <2s
2. Claude Haiku 4.5 (all CLIs) - <3s
3. Gemini 3 Flash (Copilot) - <3s
```

### By Reasoning Quality
```
1. Claude Opus 4.6 (Cline/Copilot)
2. Kimi K2.5 (Cline/OpenCode)
3. GPT-5 (Copilot)
```

### By Context Window
```
1. GPT-5 Nano (Copilot) - 400k
2. Kimi K2.5 (Cline/OpenCode) - 262k
3. Others (Copilot/Cline) - 128k-204.8k
```

### By Code Quality
```
1. GPT-5.1-Codex variants (Copilot)
2. Grok Code Fast 1 (Copilot/Cline)
3. Kimi K2.5 (Cline/OpenCode)
```

### By Multimodal Vision
```
1. Kimi K2.5 (Cline/OpenCode) - Best
2. Gemini 2.5 Pro (Copilot) - Excellent
3. Claude models (all) - Good
```

---

## 🤖 Recommended Agent Configurations

### For Software Engineers
**Primary**: Copilot CLI (terminal-first)  
- Daily: `claude-haiku-4.5` or `gpt-5-mini`
- Complex: `gpt-5.1-codex` or `grok-code-fast-1`
- Large output: `gpt-5.1-codex-32k`

**Secondary**: Cline IDE (when coding)  
- Complex refactors: `claude-opus-4.6`
- Large context: `kimi-k2.5`

---

### For Researchers
**Primary**: OpenCode (multi-model)  
- Lead: `kimi-k2.5-free`
- Validation: `big-pickle`
- Efficiency: `minimax-m2.5-free`
- Logic: `glm-5-free`

**Secondary**: Copilot CLI (fast iteration)  
- Quick checks: `gpt-5-mini` or `claude-haiku`

---

### For Architects
**Primary**: Cline IDE (large context + reasoning)  
- Planning: `claude-opus-4.6` (thinking mode)
- Large files: `kimi-k2.5` (262k context)
- Design: `kimi-k2.5` (vision)

**Secondary**: OpenCode (research synthesis)  
- Validation: `kimi-k2.5` + `big-pickle` consensus

---

## 📖 Document Map

```
expert-knowledge/model-reference/
├── cli-model-selection-strategy-v1.0.0.md    ⭐ START HERE
├── opencode-free-models-v1.0.0.md            (5 models)
├── cline-cli-models-v1.0.0.md                (9 models)
├── copilot-cli-models-v1.0.0.md              (12+ models)
├── MODEL-CARDS-INDEX.md                      (older index)
├── LOCAL-MODELS-REFERENCE-2026-02-16.md      (local models)
├── TIERED-MODEL-REFINEMENT-STRATEGY-v1.0.0.md (infrastructure)
├── _archived/
│   ├── ARCHIVE-MANIFEST.md
│   ├── opencode-models-breakdown-v1.0.0.md.archived
│   └── ... (older model docs)
```

---

## 🔗 Cross-References in Memory Bank

**Updated Files**:
- `memory_bank/activeContext.md` - Agent model assignments
- `.clinerules/00-core-context.md` - Model selection matrix

---

## 💡 Quick Selection Command

```bash
# For Copilot CLI
gh copilot suggest "your task" --model $(
  case "$task_type" in
    "fast") echo "gpt-5-mini" ;;
    "code") echo "gpt-5.1-codex" ;;
    "reason") echo "claude-opus-4.5" ;;
    "vision") echo "gemini-2.5-pro" ;;
    "large") echo "gpt-5.1-codex-32k" ;;
    *) echo "claude-haiku-4.5" ;;
  esac
)
```

---

## 📋 Documentation Statistics

| Document | Lines | Models | Scope |
|----------|-------|--------|-------|
| opencode-free-models-v1.0.0.md | 467 | 5 | OpenCode |
| cline-cli-models-v1.0.0.md | 509 | 9 | Cline |
| copilot-cli-models-v1.0.0.md | 639 | 12+ | Copilot |
| cli-model-selection-strategy-v1.0.0.md | 624 | 30+ | Unified |
| **Total** | **2,239** | **30+** | **All CLIs** |

**Coverage**:
- ✅ 30+ free frontier models documented
- ✅ 3 CLI platforms covered
- ✅ 50+ use case patterns
- ✅ Cost/performance analysis
- ✅ Integration examples
- ✅ XNAi-specific guidance

---

## 🚀 Getting Started

### Step 1: Understand Your Task
Read: `cli-model-selection-strategy-v1.0.0.md` (start here!)

### Step 2: Choose Your CLI
- Terminal? → Copilot CLI or OpenCode
- IDE? → Cline
- Research? → OpenCode

### Step 3: Select Your Model
Find your task type in the decision tree, get your model

### Step 4: Refer to CLI-Specific Doc
- OpenCode → `opencode-free-models-v1.0.0.md`
- Cline → `cline-cli-models-v1.0.0.md`
- Copilot → `copilot-cli-models-v1.0.0.md`

### Step 5: Use Your Model
```bash
# Copilot
gh copilot suggest "task" --model selected-model

# OpenCode
opencode --model selected-model "task"

# Cline
# Cmd+Shift+C → Select model
```

---

## ❓ FAQ

**Q: Which model should I use?**  
A: See `cli-model-selection-strategy-v1.0.0.md` decision tree

**Q: What's the fastest model?**  
A: GPT-5-Mini or Claude Haiku 4.5 (<3s)

**Q: What handles the largest context?**  
A: Kimi K2.5 (262k) in Cline/OpenCode or GPT-5 Nano (400k) in Copilot

**Q: Which is best for code?**  
A: GPT-5.1-Codex or Grok Code Fast 1

**Q: Can I use OpenCode models in Cline?**  
A: No - different platforms. Cline has its own 9 models.

**Q: How do I get more context?**  
A: Use Kimi K2.5 (262k) in Cline or OpenCode

**Q: All models are free?**  
A: Yes! All 30+ models are 100% free.

---

**Last Updated**: 2026-02-17  
**Maintained By**: Copilot CLI + team  
**Next Review**: 2026-02-24
