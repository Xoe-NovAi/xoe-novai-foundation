---
tool: cline
model: claude-sonnet-4-6
account: arcana-novai
git_branch: main
session_id: sprint6-2026-02-18
version: v1.1.0
created: 2026-02-18
updated: 2026-02-18
changelog: Renamed from OPENCODE-ARCHIVED-DISCOVERY. Corrected framing (upstream archive ≠ user archive). Fixed OAuth type for Antigravity (GitHub, not Google). Corrected researcher model.
tags: [opencode, upstream, archive-context, active-tool]
---

# OpenCode CLI — Upstream Repository Archive Context

> ⚠️ **FRAMING NOTE**: This document describes the archival of the **upstream GitHub repository**
> by original maintainers. arcana-novai **continues using OpenCode actively** as the primary TUI.
> OpenCode is NOT deprecated for this project. A fork (`arcana-novai/opencode-xnai`) is planned.
> See: `internal_docs/01-strategic-planning/OPENCODE-XNAI-FORK-PLAN.md`

**Discovered**: 2026-02-18
**Researcher**: Cline (claude-sonnet-4-6)
**Status**: ✅ Verified — Reference for fork planning

---

## What Happened to the Upstream Repo

The original `opencode-ai/opencode` GitHub repository was **archived on September 18, 2025** and
is no longer maintained by its original authors. The project migrated to a new organization.

**This has zero impact on arcana-novai's use of OpenCode.** The binary continues to work.
The Antigravity Auth plugin continues to work. Daily use continues uninterrupted.

---

## Repository Timeline

| Date | Event |
|------|-------|
| ~2024 | `opencode-ai/opencode` launched (Go-based AI TUI) |
| Sep 18, 2025 | `opencode-ai/opencode` **archived** — read-only, original maintainers done |
| Sep 2025 | Project migrated upstream to `charmbracelet/crush` |
| Oct 2025+ | Active development continues under `charmbracelet/crush` |
| 2026-02-18 | arcana-novai confirms: binary works, Antigravity works, usage continues |
| TBD | arcana-novai to fork as `arcana-novai/opencode-xnai` |

---

## Current Active Upstream Repository

**GitHub**: `https://github.com/charmbracelet/crush`

The **binary name remains `opencode`** even under the new repository name. Existing shell
scripts, aliases, and the Antigravity plugin all continue to work without change.

---

## CLI Flag Changes (Upstream Migration Side-Effect)

These are documented because agents using old documentation may reference incorrect flags.

### Non-interactive / prompt mode

| Version | Flag | Notes |
|---------|------|-------|
| `opencode-ai/opencode` (archived) | `--print` | Deprecated, no longer works |
| `charmbracelet/crush` (current) | `-p` or `--prompt` | Use this |

### Quiet mode

```bash
-q    # suppress interactive spinner/TUI
```

### Correct non-interactive invocation

```bash
# ✅ CORRECT (current charmbracelet/crush)
opencode --model opencode/glm-5-free --session my-session -q -p "Your task here"

# ❌ WRONG (archived opencode-ai/opencode syntax — will error)
opencode --model opencode/glm-5-free --session my-session --print "Your task here"
```

---

## Antigravity Auth Plugin — Taxonomy Correction

> ⚠️ **CRITICAL**: The original version of this document incorrectly stated Antigravity uses
> "Google OAuth". **Antigravity uses GitHub OAuth.** This is confirmed in
> `configs/agent-identity.yaml` and `docs/architecture/XNAI-AGENT-TAXONOMY.md`.

Antigravity (`opencode-antigravity-auth@latest`) is an **OAuth plugin that runs inside OpenCode**.
It is NOT a separate CLI. It uses **GitHub OAuth** to unlock premium models.

```bash
opencode install opencode-antigravity-auth@latest
# Opens browser for GitHub OAuth on first run
```

Free models unlocked via Antigravity (GitHub OAuth):
- `claude-sonnet-4-6` (200K context)
- `claude-opus-4-5-thinking` (200K, extended thinking)
- `gemini-3-pro` (1M context, multimodal)
- `gemini-3-flash` (1M context, fast)

---

## AnyIO Integration Pattern

When spawning OpenCode from async Python, use `anyio.run_process` (NOT `asyncio.create_subprocess_exec`):

```python
import anyio

result = await anyio.run_process(
    [
        "opencode",
        "--model", "opencode/glm-5-free",
        "--session", session_id,
        "-q",        # quiet (suppress TUI)
        "-p", task,  # prompt (NOT --print — that's the archived syntax)
    ],
    cwd=working_dir,
    check=False,
)

output = result.stdout.decode("utf-8", errors="replace")
```

---

## OpenCode Config

Location: `.opencode/opencode.json` (project-level) or `~/.opencode/opencode.json` (global)

```json
{
  "model": "opencode/glm-5-free",
  "providers": {
    "antigravity": {
      "npm": "opencode-antigravity-auth@latest"
    }
  }
}
```

---

## Impact on XNAi Foundation

| File | Change Required | Status |
|------|----------------|--------|
| `app/XNAi_rag_app/core/sovereign_mc_agent.py` | `--print` → `-p` flag | ✅ Fixed in v1.1.0 |
| `expert-knowledge/OPENCODE-CLI-COMPREHENSIVE-GUIDE-v1.0.0.md` | Flag correction confirmed | ✅ |
| `internal_docs/01-strategic-planning/OPENCODE-XNAI-FORK-PLAN.md` | Fork planning doc | ✅ Created Sprint 6 |

---

## References

- Archived upstream: `https://github.com/opencode-ai/opencode` (read-only)
- Current upstream: `https://github.com/charmbracelet/crush`
- Antigravity plugin: `https://github.com/opencode-antigravity/opencode-antigravity-auth`
- Fork plan: `internal_docs/01-strategic-planning/OPENCODE-XNAI-FORK-PLAN.md`
- Taxonomy: `docs/architecture/XNAI-AGENT-TAXONOMY.md`
