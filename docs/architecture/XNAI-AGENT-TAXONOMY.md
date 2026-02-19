---
tool: cline
model: claude-sonnet-4-6
account: arcana-novai
git_branch: main
session_id: sprint7-2026-02-18
version: v1.1.0
created: 2026-02-18
updated: 2026-02-18
tags: [architecture, taxonomy, agents, mermaid, crush, charm]
---

# XNAi Agent Taxonomy

> **Authoritative classification of every AI agent, CLI tool, and plugin in the XNAi ecosystem.**
> All agents, documentation, configs, and code must conform to this taxonomy.
> Source of truth: `configs/agent-identity.yaml`

---

## Agent Map

```mermaid
graph TD
    subgraph IDE["💻 IDE Agent"]
        CLINE["Cline VSCodium Extension<br/><b>model: claude-sonnet-4-6</b><br/>account: arcana-novai<br/>context: 200K (shadow 400K?)"]
    end

    subgraph TERMINAL["🖥️ Terminal Agents"]
        subgraph OC["OpenCode CLI — PRIMARY TUI<br/><i>ACTIVE · Fork planned for XNAi custom TUI</i>"]
            OC_BUILTIN["Built-in Free Models<br/>(no auth required)"]
            OC_AG["Antigravity Auth Plugin<br/><code>opencode-antigravity-auth@latest</code><br/><i>NOT a separate CLI — runs inside OpenCode</i>"]
        end
        GEMINI["Gemini CLI<br/>Google OAuth · 1M context<br/>Search grounding"]
        COPILOT["GitHub Copilot CLI<br/>GitHub OAuth<br/>Code + PR focus"]
        LOCAL["llama-cpp-python<br/>Sovereign · No network<br/>Vulkan/RDNA2 GPU"]
    end

    subgraph AG_MODELS["🔑 Antigravity Auth — Unlocked Models<br/>(GitHub OAuth, free)"]
        AG1["claude-sonnet-4-6 · 200K"]
        AG2["claude-opus-4-5-thinking · 200K"]
        AG3["gemini-3-pro · 1M ctx"]
        AG4["gemini-3-flash · 1M ctx"]
    end

    subgraph OC_MODELS["🆓 OpenCode Built-in Free Models"]
        OC1["big-pickle · 200K<br/><i>best quality</i>"]
        OC2["kimi-k2.5-free · 262K<br/><i>largest context</i>"]
        OC3["gpt-5-nano · 400K<br/><i>largest free context</i>"]
        OC4["minimax-m2.5-free · 204K<br/><i>fastest</i>"]
        OC5["glm-5-free · 200K<br/><i>multilingual</i>"]
    end

    OC_AG -->|"unlocks via GitHub OAuth"| AG_MODELS
    OC_BUILTIN --> OC_MODELS
    OC --> OC_AG
    OC --> OC_BUILTIN
```

---

## Classification Rules

> ⚠️ **These rules are enforced in `.opencode/RULES.md` rules 14, 26, and the Agent Taxonomy section.**

| Entity | Correct Classification | Wrong Classification |
|--------|----------------------|---------------------|
| `opencode-antigravity-auth@latest` | OAuth **plugin** running **inside** OpenCode CLI | ❌ "Antigravity CLI", "separate agent", pip package |
| OpenCode CLI | **ACTIVE** primary TUI, fork planned | ❌ "archived", "deprecated" |
| Cline extension model | `claude-sonnet-4-6` | ❌ `claude-opus-4-5` (Sprint 5 error — corrected Sprint 6) |
| Antigravity auth type | GitHub OAuth | ❌ Google OAuth |

---

## Provider Tier Summary

| Tier | Provider | Auth | Best For | Context |
|------|----------|------|----------|---------|
| 1 | **OpenCode + Antigravity Plugin** | GitHub OAuth | Daily coding, architecture, 1M tasks | 200K–1M |
| 1b | **Cline VSCodium** | Anthropic API | IDE-integrated file editing | 200K |
| 2 | **Gemini CLI** | Google OAuth | Research, search-grounded synthesis | 1M |
| 3 | **GitHub Copilot CLI** | GitHub OAuth | PR review, GitHub-native tasks | 128K–1M |
| 4 | **OpenCode Built-ins** | None | Zero-auth fallback | 200K–400K |
| 5 | **OpenRouter** | API key | Paid frontier access | varies |
| 6 | **llama-cpp-python** | None (local) | Air-gap, zero telemetry | varies |

---

## Routing Decision Tree

```mermaid
flowchart TD
    START([Task starts]) --> Q1{Task type?}

    Q1 -->|IDE file editing| CLINE_R["Use Cline VSCodium<br/>claude-sonnet-4-6"]
    Q1 -->|Full codebase audit| Q_CTX1{Context &gt; 200K?}
    Q1 -->|Architecture decision| AG_OPUS["OpenCode + Antigravity<br/>claude-opus-4-5-thinking<br/>--variant=max"]
    Q1 -->|Research + web grounding| GEMINI_R["Gemini CLI<br/>gemini-2.5-pro"]
    Q1 -->|GitHub PR/issue| COPILOT_R["Copilot CLI<br/>claude-haiku-4.5"]
    Q1 -->|Air-gap / sovereign| LOCAL_R["llama-cpp-python<br/>Qwen 2.5 7B Q4"]
    Q1 -->|Fast prototyping| OC_MINI["OpenCode built-in<br/>minimax-m2.5-free"]

    Q_CTX1 -->|Yes - need 1M ctx| AG_GEM["OpenCode + Antigravity<br/>gemini-3-pro<br/>--variant=high"]
    Q_CTX1 -->|No - 200K enough| AG_SON["OpenCode + Antigravity<br/>claude-sonnet-4-6"]

    AG_GEM --> RATELIMIT{Rate limited?}
    RATELIMIT -->|No| AG_GEM
    RATELIMIT -->|Yes, rotate acct| AG_GEM
    RATELIMIT -->|All 3 accts exhausted| GEMINI_R

    style CLINE_R fill:#4a90d9,color:#fff
    style AG_OPUS fill:#7b68ee,color:#fff
    style AG_GEM fill:#7b68ee,color:#fff
    style AG_SON fill:#7b68ee,color:#fff
    style GEMINI_R fill:#4285f4,color:#fff
    style COPILOT_R fill:#238636,color:#fff
    style LOCAL_R fill:#6e7681,color:#fff
    style OC_MINI fill:#e6ac00,color:#000
```

---

## OpenCode Fork Plan

OpenCode CLI upstream (`opencode-ai/opencode`) was archived by original maintainers.
**This does NOT affect usage.** arcana-novai:
- Continues using OpenCode as primary TUI
- Plans to fork the repository as `arcana-novai/opencode-xnai` or `xnai-tui`
- Fork will add: XNAi RAG integration, Qdrant memory, sovereign MC agent hooks, custom RULES loader

See: `internal_docs/01-strategic-planning/OPENCODE-XNAI-FORK-PLAN.md`

---

## Files

| File | Purpose |
|------|---------|
| `configs/agent-identity.yaml` | Authoritative model/account registry per agent |
| `configs/model-router.yaml` | Full provider + model routing config |
| `configs/free-providers-catalog.yaml` | Free-tier focused catalog |
| `.opencode/RULES.md` | Agent behavioral rules (includes taxonomy section) |
| `scripts/sign-document.sh` | Document signing (reads agent-identity.yaml) |
| `docs/architecture/XNAI-STACK-OVERVIEW.md` | C4 system diagram |

---

## Sprint 7 Additions (2026-02-18)

### Crush — OpenCode's Successor (Experimental)

**Status**: 🟡 Experimental — NOT replacing OpenCode as primary TUI

Crush is the successor to OpenCode CLI, transferred to Charmbracelet on July 29, 2025.

| Aspect | Status | XNAi Relevance |
|--------|--------|----------------|
| Open Source | ✅ MIT | Good |
| MCP Support | ✅ Yes | Good |
| Free Tier | ❌ Requires own API keys | **Critical gap** |
| Stability | 🟡 Early stage (6 months) | Monitor |
| Antigravity | ❌ Not ported | Dealbreaker for primary use |

**Why OpenCode remains primary**: Crush dropped the Antigravity plugin. Without GitHub OAuth free model access, Crush requires paid API keys. OpenCode + Antigravity remains XNAi's most cost-effective tool.

**Recommendation**: Install experimentally, track development, reconsider in 6-12 months.

### Charm Ecosystem — Complementary Tools

Production-ready tools from Charmbracelet that enhance the XNAi stack:

| Tool | Purpose | XNAi Verdict | Install |
|------|---------|--------------|---------|
| **mods** | AI pipelines for CLI — pipe stdin → LLM → stdout | 🟢 **Immediate add** | `go install github.com/charmbracelet/mods@latest` |
| **gum** | TUI components for shell scripts | 🟢 **Immediate add** | `go install github.com/charmbracelet/gum@latest` |
| **glow** | Markdown terminal renderer | 🟢 **Immediate add** | `go install github.com/charmbracelet/glow@latest` |
| **skate** | Key-value store with cloud sync | 🟡 Optional | `go install github.com/charmbracelet/skate@latest` |

**Example usage**:
```bash
# Pipeline AI with mods
cat logs/error.log | mods "root cause analysis" | glow

# Interactive model selection with gum
MODEL=$(gum choose "claude-sonnet" "gemini-2.0-flash" "llama-3.3-70b")
```

### New Free Providers

Added to `configs/free-providers-catalog.yaml` in Sprint 7:

| Provider | Killer Feature | Free Models | Speed | Waterfall Position |
|----------|---------------|-------------|-------|-------------------|
| **Cerebras** | Fastest inference on Earth | llama-3.3-70b, qwen-3-32b | 2,000-3,000 t/s | Step 4 (speed fallback) |
| **SambaNova** | Full DeepSeek-R1 671B FREE | DeepSeek-R1, DeepSeek-V3 | Fast | Step 3 (reasoning tasks) |
| **iFlow CLI** | ⚠️ CN backend — Non-sovereign | Kimi K2, Qwen3 Coder | Medium | **EXCLUDED** (sovereignty) |

**Updated Rate Limit Waterfall**:
1. Gemini CLI (1M ctx, 1500 req/day)
2. OpenCode/Antigravity (Claude Sonnet free)
3. **SambaNova** (DeepSeek-R1 671B — complex reasoning)
4. **Cerebras** (3000 t/s — fastest iteration)
5. Groq (fast inference)
6. OpenRouter free (frontier models)
7. llama-cpp-python (local, sovereign)

### iFlow CLI — Sovereignty Verdict

❌ **NOT recommended for sovereign work.** All requests processed on Chinese infrastructure (`apis.iflow.cn`). Documented for awareness only. Use Cerebras or SambaNova for free frontier models with US-based processing instead.

---

## Research References

| Document | Topic |
|----------|-------|
| `expert-knowledge/research/CRUSH-CHARM-ECOSYSTEM-2026-02-18.md` | Crush analysis, Charm tools |
| `expert-knowledge/research/CEREBRAS-SAMBANOVA-PROVIDER-2026-02-18.md` | New free providers |
| `expert-knowledge/research/IFLOW-CLI-ANALYSIS-2026-02-18.md` | iFlow sovereignty assessment |
