# Research Findings: Raptor Mini Context Window

**Date**: 2026-02-27  
**Status**: FINDINGS DOCUMENTED  
**Source**: GitHub Official Documentation (docs.github.com)

---

## Key Findings

### From GitHub Official Docs (2026-02-27)

| Model | Type | Release Status | Multiplier (Free) | Multiplier (Paid) |
|-------|------|---------------|-------------------|-------------------|
| **Raptor mini** | Fine-tuned GPT-5 mini | Public preview | 1 | 0 |
| **Claude Haiku 4.5** | Anthropic | GA | 1 | 0.33 |
| Claude Opus 4.6 | Anthropic | GA | N/A | 3 |

### Raptor Mini Details
- **Type**: Fine-tuned GPT-5 mini
- **Release**: Public preview (November 2025)
- **Availability**: VS Code, all plans (Free, Pro, Pro+, Business, Enterprise)
- **Pricing**: Free = 1x multiplier, Paid = 0x (effectively unlimited on paid plans)

---

## Context Window Investigation

### Issue
- User observed **192K context** in VS Code Insiders Copilot Extension
- Previously believed to be **264K**

### Findings
- GitHub docs do NOT list specific context window sizes for Raptor Mini
- Docs list model availability, modes (Agent/Ask/Edit), but not context limits
- **No official context window specification found** in GitHub docs

### Possible Explanations
1. Context window varies by client (CLI vs Extension vs Insiders)
2. Context window was reduced in recent updates
3. Context window is managed dynamically by GitHub
4. Different from "token limit" - context may be split between input/output

---

## Recommendation

### Actions Needed
1. **Test via Copilot CLI** - Compare context limit between CLI and Extension
2. **Check GitHub Community** - Search for Raptor Mini context discussions
3. **Test with different accounts** - Free vs Pro may differ

### CLI Test Command
```bash
# Test Raptor Mini via CLI
copilot -m raptor-mini-preview "What is your context window?"
```

---

## Related Findings

### Claude Haiku 4.5 (Free Tier)
- Available on Copilot Free
- Multiplier: 1x (same as Raptor Mini)
- Model: Claude Haiku 4.5

### Model Availability (Copilot Free)
From docs:
- Claude Haiku 4.5 ✅
- GPT-4.1 ✅
- GPT-4o ✅
- GPT-5 mini ✅
- Raptor mini ✅
- Goldeneye ✅

---

## Sources

1. GitHub Docs: "Supported AI models in GitHub Copilot" - https://docs.github.com/copilot/reference/ai-models/supported-models
2. GitHub Changelog: "Raptor mini is rolling out in public preview" - November 10, 2025

---

**Research Date**: 2026-02-27  
**Next Step**: Test via CLI to compare context limits
