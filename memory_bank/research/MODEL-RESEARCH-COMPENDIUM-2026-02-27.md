# XNAi Foundation AI Model Research Compendium

**Created**: 2026-02-27  
**Status**: IN PROGRESS  
**Purpose**: Detailed research and findings for all main AI models used in the Foundation Stack

---

## Overview

This document maintains detailed research findings for all AI models used in the XNAi Foundation, specifically focusing on free tier and preview versions. The goal is to track context windows, capabilities, limitations, and best practices for each model.

---

## Model Inventory

| Model | Provider | Status | Context Window | Notes |
|-------|----------|--------|----------------|-------|
| **Raptor Mini** | GitHub Copilot | Active | TBD (192K observed) | Fine-tuned GPT-5 mini, research in progress |
| **Haiku 4.5** | Anthropic/Copilot | Active | 200K | claude-haiku-4-5, Free tier available |
| **MiniMax M2.5 Free** | OpenCode | Active | 196K-1M | opencode/minimax-m2.5-free |
| **kat-coder-pro** | Cline CLI 2.0 | Active | 262K | kat-coder-pro via OpenRouter |
| **Trinity-large-preview** | TBD | Research | TBD | Investigating |
| **ruvltra-claude-code** | Local | Available | 2K | 380MB GGUF |
| **Qwen3-0.6B** | Local | Available | 32K | 473MB GGUF |

### Updated 2026-02-27

**Raptor Mini** (from GitHub Official Docs):
- Type: Fine-tuned GPT-5 mini
- Release: Public preview (Nov 2025)
- Pricing: Free = 1x multiplier, Paid = 0x (unlimited)
- Available: VS Code, all plans
- Note: Claude Opus 4.1 retired 2026-02-17

---

## Research Templates

### Model Research Template

For each model, document:

```markdown
### [Model Name]

#### Basic Information
| Attribute | Value |
|-----------|-------|
| Provider | |
| Model ID | |
| Context Window | |
| Format | API / CLI / Local GGUF |
| Cost | Free / Paid / Preview |

#### Capabilities
- 

#### Limitations
- 

#### Best Practices
- 

#### Configuration
```yaml
```

#### Research History
| Date | Finding | Source |
|------|---------|--------|
| 2026-02-27 | Initial research | |
```

---

## Pending Research

### Raptor Mini (PRIORITY)
- **Status**: Context window changed from 264K to 192K?
- **Questions**: 
  - Has the context window changed?
  - Is it different via CLI vs Extension?
  - How to restore larger context?

### Trinity-large-preview
- **Status**: Unknown availability
- **Questions**:
  - Is this model available?
  - What is its context window?
  - How to access?

---

## Source Management

All model research should be stored in:
- `memory_bank/research/models/` directory
- Named: `MODEL-[NAME]-YYYY-MM-DD.md`

---

**Last Updated**: 2026-02-27
**Next Review**: After Raptor research complete
