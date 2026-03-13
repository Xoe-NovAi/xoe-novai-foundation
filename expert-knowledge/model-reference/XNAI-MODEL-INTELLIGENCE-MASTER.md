# XNAi Model Intelligence Master Report

**Version**: 2.0.0 | **Date**: 2026-02-28 | **Status**: AUTHORITATIVE
**Consolidates**: XNAi Model Intelligence Report (v1.3.0) + Antigravity Free-Tier Models Reference

---

## 📋 Executive Summary

This master report provides a comprehensive catalog and strategic guide for the AI models utilized within the Xoe-NovAi ecosystem. It covers frontier models (Claude, Gemini, GPT), free-tier providers (Antigravity, OpenCode, Copilot), and local sovereign models.

### Key Strategic Pillars:
1.  **Context Superiority**: Leveraging Gemini 3 Pro's 1M context for full-codebase analysis.
2.  **Reasoning Depth**: Utilizing Claude Opus 4.6 Thinking for complex architecture and security decisions.
3.  **Operational Speed**: Employing Claude Sonnet 4.6 and Gemini 3 Flash for rapid iteration.
4.  **Sovereign Resilience**: Maintaining local GGUF models for air-gap and offline operations.

---

## ♊ Antigravity Free-Tier Models (TIER 1)

Antigravity provides free access to frontier models via OpenCode CLI using Google OAuth. It is the primary tier for heavy AI work.

| Model | CLI ID | Context | Best For |
|-------|--------|---------|----------|
| **Claude Opus 4.6 Thinking** | `google/antigravity-claude-opus-4-6-thinking` | 200K | Deep reasoning, Architecture |
| **Claude Sonnet 4.6** | `google/antigravity-claude-sonnet-4-6` | 200K | Daily coding, fast iteration |
| **Gemini 3 Pro** | `google/antigravity-gemini-3-pro` | **1M** | Full-codebase analysis |
| **Gemini 3 Flash** | `google/antigravity-gemini-3-flash` | **1M** | Fast large-context tasks |

---

## 🤖 OpenCode Built-in Free Models (TIER 4)

OpenCode provides several built-in models that serve as reliable fallbacks.

| Model | OpenRouter/Provider | Context | SWE-Bench |
|-------|---------------------|---------|-----------|
| **Kimi K2.5** | Moonshot AI | 256K | 76.8% |
| **MiniMax M2.5** | MiniMax | 197K | **80.2%** |
| **GLM-5** | Zhipu AI (Z.ai) | 205K | High Reasoning |
| **Big Pickle** | Opaque (Internal) | ~200K | General Purpose |

---

## 🐙 GitHub Copilot CLI Models (TIER 3)

The `copilot` CLI (not `gh copilot`) provides agentic coding capabilities.

| Copilot Label | Context | Likely Underlying Model |
|---------------|---------|------------------------|
| `claude-haiku-4.5` | 200K | Claude Haiku 4.5 |
| `gpt-5-mini` | 128K | o4-mini class |
| `gemini-3-flash-preview` | 1M | Gemini 2.5 Flash |

---

## 🖥️ Local Sovereign Models (TIER 5)

Vulkan-accelerated GGUF models running on local hardware (Ryzen 5700U).

| Model | VRAM | Context | Usage |
|-------|------|---------|-------|
| **Qwen 2.5 7B Q4** | ~4.4GB | 32K | Fast coding, offline |
| **DeepSeek-R1-Distill-7B** | ~4.5GB | 32K | Offline reasoning |
| **Phi-3.5-mini Q4** | ~2.2GB | 128K | Low resource, large context |

---

## 🎯 Model Selection Decision Matrix

| Task Requirement | Recommended Model | Tool |
|------------------|-------------------|------|
| **Full codebase audit** | Gemini 3 Pro | OpenCode/Gemini CLI |
| **Complex architecture** | Claude Opus 4.6 Thinking | OpenCode |
| **Daily coding/refactor** | Claude Sonnet 4.6 | Cline/OpenCode |
| **Large context + Speed** | Gemini 3 Flash | OpenCode |
| **Quick routing/simple fix** | Claude Haiku 4.5 | Copilot CLI |
| **Offline/Air-gap** | Qwen 2.5 7B | OpenCode (local) |

---

## 🔑 Account & Quota Management

- **Antigravity**: 8 accounts, 500K tokens/week each (4M total/week). Resets Sundays.
- **Gemini CLI**: 25 requests/day free quota via Google account.
- **Copilot**: ~50 chat messages/day on free tier.
- **Rotation**: Automated via `MultiProviderDispatcher` and account rotation scripts.

---

**Last Updated**: 2026-02-28
**Owner**: MC-Overseer
