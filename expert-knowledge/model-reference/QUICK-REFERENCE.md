# AI Model Quick Reference Guide

**Last Updated**: 2026-02-28 | **Status**: Active

---

## 🚀 Tier 1: Frontier Models (Antigravity Auth)

Best for complex reasoning, architecture, and large-context tasks.

| Model | Context | Key Capability |
|-------|---------|----------------|
| **Gemini 3 Pro** | **1,000,000** | Full-codebase analysis |
| **Claude Opus 4.6 Thinking** | 200,000 | Deep step-by-step reasoning |
| **Claude Sonnet 4.6** | 200,000 | Balanced speed & quality |
| **Gemini 3 Flash** | **1,000,000** | Fast large-context tasks |

---

## 🤖 Tier 4: OpenCode Free Built-ins

Reliable fallbacks with high benchmarks.

| Model | Context | SWE-Bench | Key Strength |
|-------|---------|-----------|--------------|
| **MiniMax M2.5** | 197,000 | **80.2%** | Top-tier coding quality |
| **Kimi K2.5** | 256,000 | 76.8% | Large context agentic work |
| **GLM-5** | 205,000 | N/A | Logical/structured tasks |
| **Big Pickle** | ~200,000 | N/A | General purpose reasoning |

---

## 🐙 Tier 3: Copilot CLI (Agentic)

Agentic workflow specialists for GitHub ecosystem.

| Model | Context | Best Use Case |
|-------|---------|---------------|
| **Claude Haiku 4.5** | 200,000 | Rapid iteration, simple fixes |
| **Gemini 3 Flash** | **1,000,000** | Context-heavy GitHub tasks |
| **GPT-5 Mini (o4-mini)** | 128,000 | General coding & suggestions |

---

## 🖥️ Tier 5: Local GGUF (Sovereign)

Offline, zero-telemetry, and air-gap compliant.

| Model | Quant | Context | Speed (Ryzen iGPU) |
|-------|-------|---------|--------------------|
| **Qwen 2.5 7B** | Q4_K_M | 32,000 | ~15-20 tok/sec |
| **DeepSeek-R1-7B** | Q4_K_M | 32,000 | ~12-18 tok/sec |
| **Phi-3.5-mini** | Q4_K_M | 128,000 | ~25+ tok/sec |

---

## 🎯 Model Selection Shortcut

- **Need whole repo analyzed?** → Gemini 3 Pro (Tier 1)
- **Need deep architectural reasoning?** → Claude Opus 4.6 Thinking (Tier 1)
- **Need fast, high-quality coding?** → Claude Sonnet 4.6 (Tier 1) or MiniMax M2.5 (Tier 4)
- **Offline or privacy-critical?** → Qwen 2.5 7B (Tier 5)
- **GitHub PR/Issue workflow?** → Claude Haiku 4.5 (Tier 3)

---

**Source**: [XNAi Model Intelligence Master Report](XNAI-MODEL-INTELLIGENCE-MASTER.md)
