---
tool: cline
model: claude-sonnet-4-6
account: arcana-novai
git_branch: main
session_id: sprint6-2026-02-18
version: v0.1.0
created: 2026-02-18
status: planning
tags: [opencode, fork, tui, strategic-planning]
---

# OpenCode → XNAi Fork Plan

> **Status**: Planning phase — fork not yet initiated
> **Priority**: Medium (OpenCode works fine as-is; fork needed for deep XNAi integration)

---

## Context

The upstream OpenCode CLI repository (`opencode-ai/opencode`) was archived by its original
maintainers in early 2026. This has **no impact on current use** — the binary works, the
Antigravity Auth plugin works, and arcana-novai uses OpenCode daily as the primary terminal TUI.

The fork is motivated by **wanting to add XNAi-specific integrations** that would be impractical
to maintain as patches against an archived upstream.

---

## Current State

| Item | Status |
|------|--------|
| OpenCode CLI daily use | ✅ Active |
| Antigravity Auth plugin | ✅ Active |
| Upstream GitHub repo | ⚠️ Archived (original maintainers) — does NOT affect use |
| arcana-novai fork | ❌ Not yet created |

---

## Fork Goals

### Phase 1 — Minimal Fork (clone + rename)
- Fork `opencode-ai/opencode` to `arcana-novai/opencode-xnai`
- Add XNAi branding and README
- Ensure Antigravity Auth plugin compatibility preserved
- No functional changes

### Phase 2 — XNAi RAG Integration
- Add `--rag` flag: inject Qdrant `xnai_conversations` context into system prompt
- Hook into `app/XNAi_rag_app/` Python modules via subprocess or REST
- Session data auto-export to `xoe-novai-sync/mc-imports/` on session end

### Phase 3 — Sovereign MC Agent Hooks
- Add `--dispatch` flag to route tasks to `sovereign_mc_agent.py`
- Model routing reads `configs/model-router.yaml` (YAML → shell env)
- Session metadata written to Qdrant on completion

### Phase 4 — Custom RULES Loader
- Auto-load `.opencode/RULES.md` at startup (currently manual)
- Support per-directory RULES files
- Render RULES summary in TUI sidebar

### Phase 5 — XNAi TUI Branding
- Custom theme with XNAi colors
- Status bar showing: current model, context %, provider tier
- Session memory indicator (Qdrant conversation count)

---

## Technical Notes

### OpenCode Architecture (from OPENCODE-CLI-COMPREHENSIVE-GUIDE-v1.0.0.md)
- Written in Go
- TUI via Bubble Tea framework
- Provider plugins via `opencode install <plugin>@<version>`
- Session data stored in `~/.opencode/sessions/*.json`
- Config in `~/.config/opencode/` and `opencode.json` in project root

### Antigravity Plugin Compatibility
- Plugin (`opencode-antigravity-auth@latest`) installs as an OpenCode provider plugin
- Must be re-tested after fork build
- Auth tokens stored in `~/.config/opencode/antigravity-accounts.json`

### Build Requirements
- Go 1.21+
- Make
- goreleaser (for release builds)

---

## Fork Naming Options

| Option | Pros | Cons |
|--------|------|------|
| `arcana-novai/opencode-xnai` | Clear provenance | Long name |
| `arcana-novai/xnai-tui` | Clean XNAi brand | Loses OpenCode recognition |
| `arcana-novai/xcode-novai` | Distinctive | Possible Apple trademark concern |
| **`arcana-novai/opencode`** | Simple, familiar | Less distinctive |

**Recommendation**: `arcana-novai/opencode-xnai` — clear that it's the XNAi fork of OpenCode.

---

## Pre-Fork Checklist

- [ ] Confirm Go build environment available (`go version`)
- [ ] Fork `opencode-ai/opencode` on GitHub
- [ ] Clone locally: `git clone git@github.com:arcana-novai/opencode-xnai.git`
- [ ] Verify build: `make build && ./opencode --version`
- [ ] Verify Antigravity plugin: `./opencode install opencode-antigravity-auth@latest`
- [ ] Test Antigravity auth flow with all 3 GitHub accounts
- [ ] Create `docs/architecture/OPENCODE-XNAI-INTEGRATION.md` with Phase 2 design

---

## Related Files

| File | Purpose |
|------|---------|
| `expert-knowledge/OPENCODE-CLI-COMPREHENSIVE-GUIDE-v1.0.0.md` | Full OpenCode usage guide |
| `expert-knowledge/research/OPENCODE-UPSTREAM-ARCHIVE-CONTEXT-2026-02-18.md` | What the upstream archival means (and doesn't mean) |
| `expert-knowledge/research/ANTIGRAVITY-AUTH-DISCOVERY-2026-02-18.md` | Antigravity plugin discovery notes |
| `expert-knowledge/research/ANTIGRAVITY-OAUTH-QUICKGUIDE-2026-02-18.md` | Antigravity setup quickguide |
| `configs/agent-identity.yaml` | OpenCode + Antigravity taxonomy |
| `docs/architecture/XNAI-AGENT-TAXONOMY.md` | Full agent taxonomy with Mermaid diagrams |
