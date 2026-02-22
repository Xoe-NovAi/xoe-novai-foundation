# Copilot CLI Model Card v1.0.0

**CLI**: GitHub Copilot CLI  
**Version**: v0.0.410  
**Free Tier**: Yes (limited model set)  
**Last Updated**: 2026-02-17  
**Persona Focus**: Orchestration, Planning, Task Decomposition

---

## Overview

GitHub Copilot CLI provides terminal-based access to multiple AI models through GitHub's subscription tiers. The **free tier** is available but with limited model access compared to paid tiers.

---

## Free Tier Models

### Available on Copilot Free

| Model | Provider | Context Window | Best For | Cost |
|-------|----------|-----------------|----------|------|
| **claude-haiku-4.5** | Anthropic | 200k | Quick tasks, fast responses | FREE |
| **gpt-5-mini** | OpenAI | 128k | Balanced speed/quality | FREE |
| **gemini-3-flash-preview** | Google | 1M | Large context, multimodal | FREE |

**Total on free tier**: 3 models (limited set)

---

## Premium Models (Copilot Pro Subscription)

These models require Copilot Pro ($20/month) or Pro trial:

| Model | Provider | Context Window | Best For |
|-------|----------|-----------------|----------|
| claude-sonnet-4.5 | Anthropic | 200k | Complex reasoning |
| claude-opus-4.6 | Anthropic | 200k | Advanced tasks |
| claude-opus-4.6-fast | Anthropic | 200k | Fast opus |
| claude-opus-4.5 | Anthropic | 200k | Legacy advanced |
| claude-sonnet-4 | Anthropic | 200k | Legacy sonnet |
| gpt-5.3-codex | OpenAI | 128k | Code generation |
| gpt-5.2-codex | OpenAI | 128k | Code reasoning |
| gpt-5.2 | OpenAI | 128k | General purpose |
| gpt-5.1-codex-max | OpenAI | 256k | Max context code |
| gpt-5.1-codex | OpenAI | 128k | Code editing |
| gpt-5.1 | OpenAI | 128k | Reasoning |
| gpt-5 | OpenAI | 128k | Base model |
| gpt-5.1-codex-mini | OpenAI | 128k | Mini code |
| gpt-4.1 | OpenAI | 8k | Legacy base |

---

## Setup Instructions

### Prerequisites
- GitHub account (free or paid)
- Copilot CLI installed (`brew install copilot-cli` or similar)
- Internet connection (required for API access)

### Free Tier Configuration

```bash
# Check available models
copilot models

# Use a free tier model
copilot --model claude-haiku-4.5 "your prompt here"

# Set default model
export COPILOT_DEFAULT_MODEL=gpt-5-mini
```

### Verify Free Tier Access
```bash
# List available models
copilot --help

# Check current subscription
copilot status
```

---

## Best Use Cases for XNAi

### claude-haiku-4.5 (RECOMMENDED for most tasks)
- **Use**: Orchestration, task decomposition, planning
- **Why**: Fast, free, sufficient for most CLI orchestration tasks
- **Limit**: Simpler reasoning than Opus
- **Example**:
  ```bash
  copilot --model claude-haiku-4.5 "decompose this feature into tasks"
  ```

### gpt-5-mini (RECOMMENDED for balanced approach)
- **Use**: Medium complexity planning, code review guidance
- **Why**: Good balance of speed and capability
- **Limit**: Smaller context window
- **Example**:
  ```bash
  copilot --model gpt-5-mini "analyze this architecture for improvements"
  ```

### gemini-3-flash-preview (for large context)
- **Use**: Whole-codebase analysis, large document processing
- **Why**: 1M context window, excellent for big picture
- **Limit**: Newest/least tested model
- **Example**:
  ```bash
  copilot --model gemini-3-flash-preview "summarize entire codebase patterns"
  ```

---

## Limitations

### Free Tier Constraints
- **Limited model set**: Only 3 models vs 17 available on Pro
- **Rate limiting**: Subject to GitHub API rate limits
- **Authentication**: Requires GitHub account login
- **No local models**: Must use GitHub-hosted infrastructure

### Recommended Workaround
For unlimited models and local execution, pair Copilot CLI (orchestration) with:
- **Cline CLI** + OpenRouter free tier (300+ models, local support)
- **OpenCode CLI** (5 built-in free models, no API keys)
- **Gemini CLI** (free tier via Google AI Studio)

---

## Integration with XNAi

### As Primary Orchestrator
```
Copilot CLI (planning/orchestration)
  ↓
Cline CLI (implementation via OpenRouter)
  ↓
OpenCode CLI (verification/research)
  ↓
Gemini CLI (synthesis/reasoning)
```

### Strengths for XNAi
- ✅ Built by GitHub, good integration with repos
- ✅ Free tier available (no cost)
- ✅ Multiple providers (Anthropic, OpenAI, Google)
- ✅ Terminal-first design matches CLI-focused team

### Challenges
- ⚠️ Limited model variety on free tier
- ⚠️ Requires internet access
- ⚠️ Dependent on GitHub authentication

---

## Alternative Setups

### If More Models Needed
Upgrade to Copilot Pro ($20/month) to access all 17 models, or:
- Use **Cline CLI** + OpenRouter (300+ models, free tier)
- Use **OpenCode CLI** (5 built-in free models)

### If Zero API Cost Required
- Use **Cline CLI** with local Ollama/LM Studio
- Use **OpenCode CLI** exclusively (built-in models, no setup)

---

## Commands Reference

```bash
# Check version
copilot --version

# List available models
copilot models

# Use specific model
copilot --model MODEL_NAME "Your prompt"

# Set default model
export COPILOT_DEFAULT_MODEL=claude-haiku-4.5

# Check authentication status
copilot status

# Help
copilot --help
```

---

## Resources

- GitHub Copilot CLI: https://github.com/github/copilot-cli
- GitHub Copilot Plans: https://github.com/features/copilot/plans
- Documentation: https://docs.github.com/en/copilot

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No models available" | Check `copilot status` - may need GitHub login |
| "Rate limited" | Wait before next request, consider Cline/OpenCode for local |
| "Model not found" | Run `copilot models` to see current free tier set |

---

## Related Documentation

- `AGENT-CLI-MODEL-MATRIX-v1.0.0.md` - Agent role assignments
- `CLINE-CLI-MODELS-v1.0.0.md` - Cline CLI model options
- `OPENCODE-CLI-MODELS-v1.0.0.md` - OpenCode CLI free models
- `GEMINI-CLI-MODELS-v1.0.0.md` - Gemini CLI model details
- `CLI-NOMENCLATURE-GUIDE-v1.0.0.md` - Naming conventions
