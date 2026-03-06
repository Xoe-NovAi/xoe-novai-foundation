# AI CLI Tools: Headless/Automation Mode Research

**Research Date**: 2026-02-23  
**Purpose**: Comparative analysis of AI CLI tools supporting headless/automation workflows

---

## Executive Summary

| CLI Tool | Headless Support | Auth Method | Free Tier | Best Use Case |
|----------|------------------|-------------|-----------|---------------|
| **Cline CLI 2.0** | Full (`-y`, `--json`, pipes) | OAuth, API Key, BYOK | ChatGPT sub or BYOK | CI/CD, automation, pipelines |
| **OpenCode** | Full (`run`, `serve`, attach) | API Key (BYOK) | Yes (BYOK) | Model flexibility, API server |
| **Gemini CLI** | Full (`-p`, pipes, JSON) | Google OAuth | Yes (generous) | Large context, free tier |
| **GitHub Copilot CLI** | Partial (`-p`, `--allow-all`) | GitHub OAuth | No (requires sub) | GitHub ecosystem integration |
| **Aider** | Full (`--message`, `--yes`) | API Key (BYOK) | Yes (BYOK) | Model-agnostic, git integration |
| **Cursor CLI** | Partial (`-p`, `--force`) | Cursor account | No (requires sub) | IDE + CLI workflow |
| **Codex CLI** | Full | ChatGPT Plus or API | No | OpenAI ecosystem, sandbox |

---

## 1. Cline CLI 2.0

**Source**: https://docs.cline.bot/cline-cli/getting-started  
**License**: Proprietary with free tier options  
**GitHub**: ~30K stars (estimated)

### Headless Support: **Full**

Cline CLI 2.0 (released Feb 2026) offers comprehensive headless support:

| Flag | Description |
|------|-------------|
| `-y, --yolo` | Auto-approve all actions, runs autonomously |
| `--json` | Machine-readable structured output |
| stdin pipe | Reads from piped input automatically |
| stdout redirect | Forces headless mode |

**Examples**:
```bash
# Auto-approve headless execution
cline -y "Run tests and fix any failures"

# JSON output for parsing
cline --json "List all TODO comments" | jq '.text'

# Pipe workflows
cat README.md | cline "Summarize this document"
git diff | cline -y "explain these changes"
```

### Authentication Methods

| Method | Description |
|--------|-------------|
| OAuth (Cline account) | Recommended - browser-based sign-in |
| ChatGPT Subscription | Uses OpenAI Codex OAuth |
| Import from Codex/OpenCode | Migrates existing credentials |
| BYOK (Bring Your Own Key) | Manual API key configuration |

**Provider Support**: Anthropic, OpenAI, OpenRouter, AWS Bedrock, Google Gemini, X AI (Grok), Cerebras, DeepSeek, Ollama, LM Studio, OpenAI-compatible

### Free Tier Availability

- **ChatGPT Plus/Pro subscription**: Can use Codex OAuth
- **BYOK**: Free if you have API keys
- **No standalone free tier**: Requires either subscription or API keys

### Best Use Cases
- CI/CD pipeline integration
- Automated code maintenance
- Shell script chaining
- Multi-agent parallel execution

---

## 2. OpenCode CLI

**Source**: https://opencode.ai/docs/cli/  
**License**: MIT (open source)  
**GitHub**: ~108K stars

### Headless Support: **Full**

OpenCode provides multiple headless execution modes:

| Command | Description |
|---------|-------------|
| `opencode run` | Single non-interactive execution |
| `opencode serve` | Headless HTTP API server |
| `opencode attach` | Attach to running server |
| `opencode acp` | Agent Client Protocol server |

**Examples**:
```bash
# Direct non-interactive run
opencode run "Explain how closures work in JavaScript"

# Headless API server
opencode serve --port 4096 --hostname 0.0.0.0

# Attach to running server (avoids MCP cold boot)
opencode run --attach http://localhost:4096 "Explain async/await"

# With auth
OPENCODE_SERVER_PASSWORD=secret opencode serve
```

### Authentication Methods

| Method | Description |
|--------|-------------|
| `opencode auth login` | Interactive provider configuration |
| Environment variables | API keys via env vars |
| `.env` file | Project-level configuration |
| `~/.local/share/opencode/auth.json` | Credentials storage |

**Provider Support**: 75+ providers via models.dev integration

### Subagent Support

OpenCode supports custom agents:
```bash
opencode agent create    # Create custom agent
opencode agent list      # List available agents
opencode --agent <name>  # Use specific agent
```

### Free Tier Availability

- **Completely free**: Open source, BYOK model
- **No vendor lock-in**: Use any provider's API

### Best Use Cases
- API server for programmatic access
- Model flexibility (75+ providers)
- Custom agent development
- Remote server deployment

---

## 3. GitHub Copilot CLI

**Source**: https://docs.github.com/en/copilot/how-tos/copilot-cli  
**License**: Proprietary  
**Status**: Public Preview (as of Feb 2026)

### Headless Support: **Partial**

| Flag | Description |
|------|-------------|
| `-p, --prompt` | Non-interactive single prompt |
| `--allow-all` | Auto-approve permissions (caution) |
| `--output-format` | Output format (text/json) |

**Examples**:
```bash
# Non-interactive mode
copilot -p "What's the git command to undo my last commit?"

# Capture output
RESULT=$(copilot -p "Generate a commit message")

# Programmatic usage
git diff | copilot -p "Review these changes"
```

### Authentication

- **GitHub OAuth**: Required, links to GitHub account
- **Copilot subscription**: Requires active Copilot subscription

### Free Tier Availability

- **No free tier**: Requires GitHub Copilot subscription ($10-19/mo)
- **Enterprise**: Available with GitHub Enterprise

### Best Use Cases
- GitHub ecosystem integration
- IDE + CLI workflow continuity
- GitHub Actions automation

### Known Issues
- Some reports of `-p` mode hanging (as of Jan 2026)
- Requires trusted directory confirmation

---

## 4. Gemini CLI

**Source**: https://google-gemini.github.io/gemini-cli/docs/cli/headless.html  
**License**: Open source (Apache 2.0)  
**GitHub**: ~95K stars

### Headless Support: **Full**

| Flag | Description |
|------|-------------|
| `-p, --prompt` | Direct prompt execution |
| stdin pipe | Read from piped input |
| `--format json` | Structured JSON output |

**Examples**:
```bash
# Direct prompt
gemini --prompt "What is machine learning?"

# Pipe input
cat error.log | gemini "Explain why this failed"
git diff | gemini "Write a commit message"

# JSON output for scripting
gemini -p "List all functions" --format json | jq '.response'
```

### Authentication

- **Google OAuth**: Primary authentication method
- **API Key**: Also supported for programmatic access

### Free Tier Availability

- **Generous free tier**: Gemini 2.5 Flash available free
- **1M token context**: Largest context window among CLI tools

### Performance Considerations

Current cold-start latency issue (as of Feb 2026):
- Loads MCPs/tools even for simple prompts
- Feature request for `--lite` or `--fast` mode
- Can take 45-60s for tasks that should take 10-15s

### Best Use Cases
- Large context processing (1M tokens)
- Free tier usage
- Google Cloud ecosystem integration
- Batch documentation generation

---

## 5. Aider

**Source**: https://aider.chat/docs/scripting.html  
**License**: Apache 2.0 (open source)  
**GitHub**: 40K+ stars

### Headless Support: **Full**

| Flag | Description |
|------|-------------|
| `--message, -m` | Single message, then exit |
| `--message-file, -f` | Message from file |
| `--yes` | Auto-confirm all prompts |
| `--dry-run` | Preview without changes |
| `--commit` | Commit and exit |

**Examples**:
```bash
# Single message execution
aider --message "make a script that prints hello" hello.js

# Batch processing
for FILE in *.py; do
    aider --message "add docstrings" $FILE
done

# Auto-approve everything
aider --yes --message "refactor to async/await" *.py
```

### Authentication

- **BYOK only**: No built-in auth, use your own API keys
- **Supports 75+ providers**: Claude, GPT, DeepSeek, Gemini, Ollama

### Free Tier Availability

- **Free software**: Open source
- **BYOK model**: You pay for your API usage

### Best Use Cases
- Model-agnostic workflows
- Git-integrated coding (auto-commits)
- Batch file processing
- Local model usage (Ollama)

---

## 6. Cursor CLI

**Source**: https://cursor.com/docs/cli/headless  
**License**: Proprietary

### Headless Support: **Partial**

| Flag | Description |
|------|-------------|
| `-p` | Print/headless mode |
| `--force` | Auto-approve permissions |
| `--output-format` | Output format |

**Examples**:
```bash
# Headless execution
cursor agent -p --force "code review the latest commit"

# With specific output
cursor agent -p --output-format text "Say hello"
```

### Known Issues

- `-p` mode reported to hang indefinitely (Jan 2026)
- Still being actively developed

### Authentication

- **Cursor account**: Required
- **Subscription**: Requires Cursor Pro ($20/mo)

### Free Tier Availability

- **No free tier**: Requires paid subscription

---

## 7. Codex CLI (OpenAI)

**Source**: OpenAI  
**License**: CLI is open source (Rust)  
**GitHub**: ~40K stars

### Headless Support: **Full**

- Supports non-interactive execution
- Cloud sandbox execution
- Background task support

### Authentication

- **ChatGPT Plus/Pro**: $20/mo subscription
- **API**: Usage-based pricing

### Key Features

- **SWE-bench Verified**: 69.1%
- **Cloud sandbox**: Isolated execution environment
- **Background tasks**: Cloud handoff capability

### Best Use Cases
- OpenAI ecosystem
- Background/cloud execution
- Sandboxed code execution

---

## Comparison Matrix

| Feature | Cline | OpenCode | Gemini | Copilot | Aider | Cursor | Codex |
|---------|-------|----------|--------|---------|-------|--------|-------|
| **Full Headless** | Yes | Yes | Yes | Partial | Yes | Partial | Yes |
| **API Server** | No | Yes | No | No | No | No | No |
| **JSON Output** | Yes | Yes | Yes | Yes | No | Yes | Yes |
| **Free Tier** | BYOK | Yes | Yes | No | BYOK | No | No |
| **Local Models** | Yes | Yes | No | No | Yes | No | No |
| **MCP Support** | Yes | Yes | Yes | Limited | No | Yes | No |
| **Custom Agents** | No | Yes | No | No | No | No | No |
| **CI/CD Ready** | Yes | Yes | Yes | Partial | Yes | Partial | Yes |

---

## Recommendations by Use Case

### For CI/CD Pipelines
1. **Cline CLI** - Best `-y` mode, clean exit codes
2. **OpenCode** - API server mode for complex workflows
3. **Gemini CLI** - Large context, JSON output

### For Cost-Conscious Users
1. **OpenCode** - Free, BYOK
2. **Aider** - Free, BYOK, model-agnostic
3. **Gemini CLI** - Generous free tier

### For Model Flexibility
1. **OpenCode** - 75+ providers
2. **Aider** - 100+ models
3. **Cline** - 12+ providers

### For API Integration
1. **OpenCode** - Built-in `serve` command
2. **Gemini CLI** - Clean JSON output
3. **Cline** - JSON mode with jq integration

### For Free/Local Usage
1. **OpenCode + Ollama** - Completely local
2. **Aider + Ollama** - Local models
3. **Gemini CLI** - Free tier with cloud models

---

## References

- Cline CLI Docs: https://docs.cline.bot/cline-cli/getting-started
- OpenCode Docs: https://opencode.ai/docs/cli/
- Gemini CLI Headless: https://google-gemini.github.io/gemini-cli/docs/cli/headless.html
- GitHub Copilot CLI: https://docs.github.com/en/copilot/how-tos/copilot-cli
- Aider Scripting: https://aider.chat/docs/scripting.html
- Comparison Article: https://awesomeagents.ai/tools/best-ai-coding-cli-tools-2026/

---

**Last Updated**: 2026-02-23  
**Next Review**: 2026-03-23
