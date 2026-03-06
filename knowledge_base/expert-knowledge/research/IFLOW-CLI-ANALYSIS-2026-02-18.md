# ---
# tool: cline
# model: claude-sonnet-4-6
# account: arcana-novai
# git_branch: main
# session_id: sprint7-2026-02-18
# version: v1.0.0
# created: 2026-02-18
# ---

# iFlow CLI Analysis: Free Models with Sovereignty Concerns

**Research Date**: 2026-02-18
**Verdict**: 🟡 Document for awareness — NOT recommended for sovereign work

---

## Executive Summary

iFlow CLI is a Chinese AI coding CLI offering genuinely free access to frontier models (Kimi K2, Qwen3 Coder, DeepSeek V3). However, **all prompts are processed on Chinese infrastructure**, making it unsuitable for XNAi's sovereign-first architecture.

| Aspect | Status | XNAi Relevance |
|--------|--------|----------------|
| Free Models | ✅ Kimi K2, Qwen3, DeepSeek | Excellent value |
| Open Source | ✅ MIT (CLI wrapper only) | Good |
| MCP Support | ✅ Yes | Good |
| Data Sovereignty | ❌ CN backend | **Critical concern** |
| Registration | ⚠️ Mixed reports (Google OAuth vs CN phone) | Friction |

---

## Overview

### What Is iFlow CLI?
- **GitHub**: `iflow-ai/iflow-cli`
- **Stars**: 4.4k ⭐, 302 forks
- **Language**: Node.js (npm install)
- **Platform**: `cli.iflow.cn`
- **License**: MIT (CLI only — backend is proprietary)

### Architecture
The CLI is an open-source wrapper around iFlow's proprietary cloud platform. ALL requests go to `apis.iflow.cn` — there is no local processing option.

---

## Free Models Available

| Model | Context Window | Notes |
|-------|---------------|-------|
| Kimi K2 | 128K+ | MoonshotAI's frontier model — excellent |
| Qwen3 Coder | 128K | Alibaba's coding model — strong |
| DeepSeek V3 | 128K | Frontier reasoning model |

These are genuinely free with generous daily limits. No credit card required.

---

## Feature Comparison

| Feature | iFlow | Claude Code | Gemini CLI |
|---------|-------|-------------|------------|
| Todo Planning | ✅ | ✅ | ❌ |
| SubAgents | ✅ | ✅ | ❌ |
| Plan Mode | ✅ | ✅ | ❌ |
| **Open Market** | ✅ | ❌ | ❌ |
| MCP (one-click) | ✅ | ✅ | ❌ |
| Workflow automation | ✅ | ❌ | ❌ |
| Memory auto-compression | ✅ | ✅ | ✅ |
| Multimodal | ✅ | ⚠️ | ⚠️ |
| Built-in Search | ✅ | ❌ | ⚠️ |
| **Free** | ✅ | ❌ | ⚠️ limited |

### 4 Operating Modes
- `--mode yolo` — Full system access (CI/CD only)
- `--mode edit` — File modifications only
- `--mode plan` — Read-only planning
- `default` — Q&A only (safest)

---

## Sovereignty Assessment

### Critical Concerns

1. **Chinese Backend**: ALL requests go to `apis.iflow.cn`
   - Your prompts, code, and context leave your machine
   - Processed on Chinese infrastructure
   - Subject to CN data regulations

2. **No Offline Mode**: The CLI is useless without iFlow's cloud

3. **Registration Friction**: Mixed reports — some users can use Google OAuth, others report mainland China phone number required

4. **Early Stage**: Only 34 commits, 7 contributors, no GitHub releases

5. **"Open Source" Caveat**: The CLI is MIT-licensed, but it's a client for proprietary infrastructure. If iFlow shuts down or changes terms, the tool vanishes.

### XNAi Sovereignty Verdict

| Work Type | iFlow Suitable? |
|-----------|-----------------|
| Sensitive/personal code | ❌ No |
| Proprietary business logic | ❌ No |
| Research/experimental | 🟡 Maybe |
| Public/open-source work | ✅ Yes |
| Non-sensitive testing | ✅ Yes |

---

## Use Cases Where iFlow Makes Sense

1. **Model experimentation**: Try Kimi K2 or Qwen3 Coder before committing API spend elsewhere
2. **Public projects**: Open-source work where code is already public
3. **Learning/education**: No cost barrier for students
4. **Benchmarking**: Compare model outputs against other providers

---

## Installation

```bash
# npm
npm install -g @iflow-ai/iflow-cli

# Or one-click install
bash -c "$(curl -fsSL https://cloud.iflow.cn/iflow-cli/install.sh)"
```

---

## XNAi Recommendation

### For `free-providers-catalog.yaml`
Add iFlow as **Tier 1 with caveats**:
- Label: "Non-sovereign — CN backend"
- Use case: Experimental, non-sensitive work only
- Not in the rate limit waterfall (sovereignty-first architecture)

### For Daily Use
❌ **Not recommended** for XNAi primary workflows. The sovereignty cost outweighs the free model benefit. Use Cerebras or SambaNova for free frontier models with US-based processing instead.

---

## References

- iFlow CLI: https://github.com/iflow-ai/iflow-cli
- Platform: https://cli.iflow.cn
- Models: https://platform.iflow.cn/en/models

---

*Research conducted: 2026-02-18*