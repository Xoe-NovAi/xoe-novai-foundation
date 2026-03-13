# Gemini CLI Model Card v1.0.0

**CLI**: Gemini CLI  
**Version**: v0.28.2  
**Free Tier**: Yes (Google AI Studio)  
**Last Updated**: 2026-02-17  
**Persona Focus**: Synthesis, Complex Reasoning, Large Context Processing

---

## Overview

Gemini CLI provides terminal access to Google's Gemini models via the free Google AI Studio. No credit card required for free tier access, making it ideal for large context processing and synthesis tasks.

---

## Free Tier Models

### Available on Google AI Studio Free Tier

| Model | Version | Context | Released | Best For |
|-------|---------|---------|----------|----------|
| **gemini-3-flash-preview** | Latest | 1M | Feb 2026 | RECOMMENDED - speed, latest |
| **gemini-3-pro-preview** | Latest | 1M | Feb 2026 | Complex reasoning |
| **gemini-2.5-pro** | Stable | 1M | 2025 | Advanced reasoning |
| **gemini-2.5-flash** | Stable | 1M | 2025 | Speed-optimized |
| **gemini-1.5-pro** | Legacy | 2M | 2024 | Huge context (2M) |
| **gemini-1.5-flash** | Legacy | 1M | 2024 | Legacy fast |

**All**: FREE tier, no credit card required, rate-limited to 15 req/min

---

## Rate Limits

### Free Tier Quotas
- **Requests per minute**: 15 (soft limit)
- **Tokens per minute**: 1M (soft limit)
- **Daily quota**: Unlimited (as of Feb 2026)
- **Cost**: $0

### Upgrade to Paid (Optional)
- **Gemini API**: $0.075 per 1M input tokens
- **Higher quotas**: Available on paid tier
- **Enterprise**: Contact Google for custom limits

---

## Setup Instructions

### Step 1: Create Google Account (if needed)
```bash
# Visit https://aistudio.google.com
# Sign in with Google account (free tier only)
# No credit card required
```

### Step 2: Get API Key
```bash
# At aistudio.google.com, generate API key
# Copy the key (looks like: AIza...)
```

### Step 3: Configure Gemini CLI
```bash
# Set environment variable
export GEMINI_API_KEY="AIza..."

# Or create config file
mkdir -p ~/.gemini
cat > ~/.gemini/config.json << 'EOF'
{
  "apiKey": "AIza...",
  "defaultModel": "gemini-3-flash-preview"
}
EOF
```

### Step 4: Verify Setup
```bash
# Test connection
gemini --test

# List available models
gemini --list-models

# Version check
gemini --version
```

### Step 5: Use Gemini CLI
```bash
# Basic usage
gemini "summarize this codebase"

# With specific model
gemini --model gemini-3-pro-preview "analyze this architecture"

# With file input
gemini --file=./large-document.md "extract key insights"

# Interactive mode
gemini --interactive
```

---

## Best Use Cases for XNAi

### gemini-3-flash-preview (RECOMMENDED)
- **Use**: Most tasks - synthesis, analysis, large document processing
- **Why**: Latest model, free tier, good speed/quality balance
- **Strengths**: 
  - 1M context window (huge!)
  - Latest training data
  - Excellent at synthesis
  - Fast enough for real-time use
- **Limitations**: 15 req/min rate limit
- **Example**:
  ```bash
  export GEMINI_API_KEY="AIza..."
  gemini --model gemini-3-flash-preview "synthesize findings from all memory_bank docs"
  ```

### gemini-3-pro-preview (for complex reasoning)
- **Use**: Hard problems, deep analysis, architecture decisions
- **Why**: Most capable preview model
- **Strengths**: Superior reasoning, handles complex multi-step problems
- **Limitations**: Slightly slower, same 15 req/min limit
- **Example**:
  ```bash
  gemini --model gemini-3-pro-preview "design resilience strategy for distributed system"
  ```

### gemini-1.5-pro (for maximum context)
- **Use**: Entire codebase analysis, 2M token documents
- **Why**: 2M context window (largest available)
- **Strengths**: Can process entire large projects in single request
- **Limitations**: Slightly older model, still free tier
- **Example**:
  ```bash
  gemini --model gemini-1.5-pro "analyze patterns across entire XNAi codebase"
  ```

---

## Integration with XNAi

### Recommended Workflow
```
Agent: Copilot (orchestrates)
  ↓
Agent: Cline (implements)
  ↓
Agent: OpenCode (verifies)
  ↓
Agent: Gemini (synthesizes)
  │
  └─ Uses: gemini-3-flash-preview (free tier)
     Or: gemini-3-pro-preview (complex reasoning)
```

### Strengths for XNAi
- ✅ **Massive context**: 1M-2M tokens (entire projects)
- ✅ **Completely free**: No cost for free tier
- ✅ **No credit card**: Google account only
- ✅ **Vision capable**: Can process images, PDFs
- ✅ **Synthesis strength**: Excellent at synthesizing insights
- ✅ **Latest models**: Access to preview models before public release

### Challenges
- ⚠️ **Rate limited**: 15 req/min (can't use for high-frequency tasks)
- ⚠️ **Preview quality**: Preview models may have issues
- ⚠️ **Google dependency**: Requires internet + Google account

---

## Use Case Matrix

| Task | Model | Why |
|------|-------|-----|
| Quick question | gemini-3-flash-preview | Speed |
| Complex analysis | gemini-3-pro-preview | Reasoning |
| Huge document (>500k tokens) | gemini-1.5-pro | Context window |
| Vision/PDF analysis | Any model | All support vision |
| Synthesis from multiple docs | gemini-3-flash-preview | Strength area |
| Architecture decision | gemini-3-pro-preview | Complex reasoning |
| Codebase summary | gemini-1.5-pro | Max context |

---

## Commands Reference

```bash
# Check version
gemini --version

# List available models
gemini --list-models

# Test API connection
gemini --test

# Use specific model
gemini --model gemini-3-pro-preview "Your prompt"

# Process file
gemini --file=document.txt "Analyze this document"

# Multi-file input
gemini --files=file1.txt,file2.txt "Compare these documents"

# Interactive chat
gemini --interactive

# Set default model
export GEMINI_DEFAULT_MODEL=gemini-3-flash-preview

# Help
gemini --help
```

---

## Vision/Multimodal Capabilities

### Supported Input Types
- Text (primary)
- Images (JPG, PNG, WebP, GIF)
- PDFs (all models)
- Videos (upcoming)

### Example Vision Usage
```bash
# Analyze image
gemini --file=screenshot.png "what does this UI show?"

# Analyze PDF
gemini --file=document.pdf "extract key points"

# Multiple images
gemini --files=img1.png,img2.png "compare these architectures"
```

---

## Rate Limit Management

### If Rate Limited
1. **Wait 1 minute** - Limit resets per minute
2. **Use smaller prompts** - Fewer tokens = more available
3. **Batch requests** - Combine multiple small prompts
4. **Switch to paid tier** - Upgrade if needed for more quota

### Monitor Usage
```bash
# Check remaining quota (estimated)
gemini --quota-status

# Get current usage
gemini --stats
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key invalid" | Verify key at aistudio.google.com, check export |
| "Rate limited" | Wait 60 seconds, try again |
| "Model not available" | Use `gemini --list-models`, may need paid tier |
| "Authentication failed" | Ensure Google account verified, key not expired |
| "Connection timeout" | Check internet, Google API servers status |
| "Vision not working" | Ensure file format supported (JPG, PNG, WebP, GIF) |

---

## Cost Analysis

| Tier | Cost | Rate Limit | Context |
|------|------|-----------|---------|
| Free (AI Studio) | FREE | 15 req/min | 1M tokens |
| Gemini API Tier 1 | $0.075/1M input | 100 req/min | 1M tokens |
| Gemini API Tier 2 | $0.30/1M input | 1000 req/min | 2M tokens |
| Enterprise | Custom | Custom | Custom |

**Recommendation**: Start with free tier, upgrade to paid API if hitting rate limits.

---

## Related Documentation

- `AGENT-CLI-MODEL-MATRIX-v1.0.0.md` - Agent role assignments
- `COPILOT-CLI-MODELS-v1.0.0.md` - Copilot CLI models
- `CLINE-CLI-MODELS-v1.0.0.md` - Cline CLI models
- `OPENCODE-CLI-MODELS-v1.0.0.md` - OpenCode CLI models
- `CLI-NOMENCLATURE-GUIDE-v1.0.0.md` - Naming conventions

---

## Resources

- Google AI Studio: https://aistudio.google.com
- Gemini API Docs: https://ai.google.dev
- Model Cards: https://ai.google.dev/models
- Pricing: https://ai.google.dev/pricing
