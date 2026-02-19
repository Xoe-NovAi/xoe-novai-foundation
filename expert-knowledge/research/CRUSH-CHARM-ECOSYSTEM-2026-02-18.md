# ---
# tool: cline
# model: claude-sonnet-4-6
# account: arcana-novai
# git_branch: main
# session_id: sprint7-2026-02-18
# version: v1.0.0
# created: 2026-02-18
# ---

# Crush & Charm Ecosystem: OpenCode's Successor Analysis

**Research Date**: 2026-02-18
**Verdict**: 🟡 Experimental tracking only — NOT replacing OpenCode for XNAi primary CLI

---

## Executive Summary

**Crush** is the successor to OpenCode CLI, transferred to Charmbracelet on July 29, 2025. It's a Go-based TUI AI coding assistant built on the BubbleTea framework. While promising, it **lacks the Antigravity plugin** that made OpenCode unique (free Claude/Gemini via GitHub OAuth).

| Aspect | Status | XNAi Relevance |
|--------|--------|----------------|
| Open Source | ✅ MIT | Good |
| MCP Support | ✅ Yes | Good |
| Free Tier | ❌ Requires own API keys | **Critical gap** |
| Stability | 🟡 Early stage (6 months) | Monitor |
| Antigravity | ❌ Not ported | Dealbreaker for primary use |

---

## Crush: Technical Overview

### Origin Story
- **Original**: OpenCode CLI by Kujtim Hoxha (`opencode-ai/opencode`)
- **Transfer**: July 29, 2025 → Charmbracelet
- **Rename**: OpenCode → Crush
- **GitHub**: `charmbracelet/crush`

### Architecture
- **Language**: Go (single binary, fast startup)
- **TUI Framework**: BubbleTea (Charm's own terminal UI library)
- **Styling**: Lipgloss (Charm's styling library)
- **Components**: Bubbles (reusable TUI components)

### Key Features
1. **Multi-model support**: Claude, GPT, Groq, Gemini, Grok — switch mid-session preserving context
2. **MCP integration**: Yes — tool use via MCP servers
3. **Permission system**: Similar to Claude Code — approve file edits
4. **`--yolo` mode**: Skip all permissions (CI/CD only)
5. **CRUSH.md**: Auto-generated project context file (like CLAUDE.md)
6. **LSP integration**: Add language servers for code intelligence
7. **Session persistence**: State preserved across model switches

### Stability Assessment (Feb 2026)
Per production review (TNS, David Eastman):
- ❌ Cannot use mouse to place cursor while typing
- ❌ Cannot copy text from response
- ⚠️ Terminal emulation conflicts reported
- ⚠️ No clear permission boundaries for outside-project changes
- ⚠️ Ran out of tokens mid-task

**Verdict**: Not production-ready for daily driver use. Excellent potential, but 6-12 months from maturity.

---

## The Antigravity Gap

**Why OpenCode + Antigravity is irreplaceable:**

| Feature | OpenCode + Antigravity | Crush |
|---------|------------------------|-------|
| Free Claude access | ✅ GitHub OAuth | ❌ Own API key |
| Free Gemini 1M ctx | ✅ GitHub OAuth | ❌ Own API key |
| Credit card required | ❌ No | ✅ Yes (via API keys) |
| Billing setup | ❌ None needed | ✅ Anthropic/OpenAI account |

The Antigravity plugin (`opencode-antigravity-auth@latest`) is **not ported to Crush**. This is the single reason OpenCode remains XNAi's primary CLI despite being archived.

---

## Charm Ecosystem: Complementary Tools

### 1. `mods` — AI Pipelines for CLI
- **GitHub**: `charmbracelet/mods`
- **Stars**: 4.4k ⭐
- **Maturity**: ✅ Production-stable
- **License**: MIT

**Purpose**: "AI for the command line, built for pipelines"

```bash
# Pipe command output to AI
cat logs/error.log | mods "root cause analysis, output as JSON"

# Use with glow for markdown rendering
mods "explain this code" < script.py | glow
```

**Key Features**:
- MCP support (`--mcp-list`, `--mcp-list-tools`)
- Saved conversations (SHA-1 based, git-like)
- Custom roles (system prompts)
- Providers: OpenAI, Groq, Gemini, Cohere, LocalAI

**XNAi Verdict**: 🟢 **Immediate add** — production-ready, excellent for pipeline AI

### 2. `gum` — Glamorous Shell Script UI
- **GitHub**: `charmbracelet/gum`
- **Purpose**: TUI components for shell scripts

```bash
# Interactive model selection
MODEL=$(gum choose "claude-sonnet" "gemini-2.0-flash" "llama-3.3-70b")
crush --model "$MODEL"

# Confirmation prompt
gum confirm "Deploy to production?" && ./deploy.sh
```

**Components**: `choose`, `input`, `confirm`, `spin`, `filter`, `table`, `write`

**XNAi Verdict**: 🟢 **Immediate add** — makes CLI scripts dramatically better

### 3. `glow` — Markdown Terminal Renderer
- **GitHub**: `charmbracelet/glow`
- **Purpose**: Render markdown beautifully in terminal

```bash
# Render AI output
crush output.md | glow

# Read docs
glow README.md
```

**XNAi Verdict**: 🟢 **Immediate add** — essential for AI markdown output

### 4. `skate` — Key-Value Store
- **GitHub**: `charmbracelet/skate`
- **Purpose**: Personal KV store with optional cloud sync

**XNAi Verdict**: 🟡 Optional — useful for state, but adds Charm Cloud dependency

---

## OpenCode Architecture (For Fork Reference)

The last OpenCode snapshot before Charmbracelet transfer had this structure:

```
opencode-ai/opencode/internal/
├── app/         — App wiring, LSP client, agent init
├── tui/         — Full BubbleTea TUI (pages, components, dialogs, themes)
├── llm/         — Agent loop, providers (Anthropic, OpenAI, Gemini, Bedrock, Azure, Copilot, Vertex)
├── permission/  — Permission broker (pubsub-based, session-scoped grants)
├── config/      — JSON config + viper, MCPServer/Agent/LSPConfig structs
├── db/          — SQLite (ncruces/go-sqlite3 + sqlc queries)
├── session/     — Session management
├── message/     — Message history
├── pubsub/      — Generic in-process event bus
└── lsp/         — LSP client integration
```

**Key Go Dependencies**:
- `charmbracelet/bubbletea` — TUI framework
- `charmbracelet/lipgloss` — Styling
- `charmbracelet/bubbles` — TUI components
- `ncruces/go-sqlite3` — SQLite (WASM-based, no CGO)

---

## XNAi Strategy Recommendation

### Immediate (Sprint 7-8)
1. **Keep OpenCode as primary CLI** — Antigravity free access is irreplaceable
2. **Install Crush experimentally** — track development, test features
3. **Add mods + gum + glow** — production-ready complementary tools

### Fork Strategy
**Fork the last OpenCode snapshot** (not Crush):
- ✅ Preserves Antigravity plugin
- ✅ Clean Go architecture
- ✅ Full control for XNAi customization

The OPENCODE-XNAI-FORK-PLAN.md phases remain valid:
- Phase 1: Fork + rename
- Phase 2: RAG integration
- Phase 3: MC agent hooks
- Phase 4: Custom RULES loader
- Phase 5: XNAi TUI branding

### Long-term (6-12 months)
Build a fresh XNAi TUI using BubbleTea, borrowing patterns from both OpenCode and Crush. The fork is the learning vehicle for the real build.

---

## Installation

### Crush (experimental)
```bash
go install github.com/charmbracelet/crush@latest
```

### mods
```bash
# macOS/Linux
brew install charmbracelet/tap/mods

# Go
go install github.com/charmbracelet/mods@latest
```

### gum
```bash
brew install charmbracelet/tap/gum
# or
go install github.com/charmbracelet/gum@latest
```

### glow
```bash
brew install charmbracelet/tap/glow
# or
go install github.com/charmbracelet/glow@latest
```

---

## Action Items

- [x] Research complete
- [ ] Install mods, gum, glow
- [ ] Add to XNAI-AGENT-TAXONOMY.md
- [ ] Update fork plan to target OpenCode snapshot (not Crush)
- [ ] Track Crush development monthly

---

## References

- Crush: https://github.com/charmbracelet/crush
- mods: https://github.com/charmbracelet/mods
- gum: https://github.com/charmbracelet/gum
- glow: https://github.com/charmbracelet/glow
- skate: https://github.com/charmbracelet/skate
- Charm: https://charm.sh

---

*Research conducted: 2026-02-18*