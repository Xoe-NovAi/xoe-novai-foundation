# XNAi Ecosystem — AI Assistant Quickstart & Next Steps

> **Issued by**: Claude Opus 4.6 + GLM-5 (Implementation)
> **Date**: 2026-02-19
> **For**: All AI assistants operating on the XNAi Foundation codebase
> **Read time**: ~3 minutes

---

## Who You Are Working For

**The Architect** is building a sovereign, offline-first AI platform. There are two layers:
- **XNAi Foundation** (`~/Documents/xnai-foundation/`) — The technical infrastructure. This is where you work.
- **Arcana-Nova** — An esoteric superstructure built on top. **Do not mix these layers.**

---

## Project State (as of 2026-02-19)

- **Phases 1-7**: Complete
- **Phase 8**: Next (Advanced Features)
- **Sprint 8**: In progress (3/4 Tier 1 complete)
- **Production health**: 95%
- **Git branch**: `xnai-agent-bus/harden-infra`

---

## Files You Must Read First

1. `docs/01-start/ONBOARDING-CHECKLIST.md` — **NEW AGENT START HERE**
2. `memory_bank/activeContext.md` — Current sprint status
3. `memory_bank/strategies/OPUS-TOKEN-STRATEGY.md` — Token budgets
4. `memory_bank/strategies/OPUS-STRATEGIC-REVIEW-2026-02-19.md` — Templates

---

## OpenCode Agents Available

### Primary Agents (Tab-switchable)
Press **Tab** to cycle: `build` → `plan` → `research` → `architect`

| Agent | Purpose | Tools |
|-------|---------|-------|
| `build` | Implementation | All |
| `plan` | Planning/analysis | Read-only |
| `research` | Research/investigation | Read + WebSearch |
| `architect` | Architecture decisions | Read-only |

### Subagents & Skills (@mention invokable)
Type `@` to invoke: `@explore`, `@review`, `@security`, `@cli-dispatch`

| Item | Type | Purpose |
|------|------|---------|
| `explore` | subagent | Fast codebase scanning |
| `review` | subagent | Code quality review |
| `security` | subagent | Security audit |
| `cli-dispatch` | subagent/skill | Dispatch to external CLIs via bash |

---

## External CLIs Available

| CLI | Path | Best For |
|-----|------|----------|
| **Cline** | `~/.nvm/versions/node/v25.3.0/bin/cline` | Coding (kat-coder-pro) |
| **Gemini** | `~/.nvm/versions/node/v25.3.0/bin/gemini` | Research (1M context) |
| **Copilot** | `~/.local/bin/copilot` | GitHub integration |

---

## OpenCode Providers Available

### Free Tier Providers
| Provider | Free Limit | Best For | Env Var |
|----------|-----------|----------|---------|
| Gemini (Antigravity) | 100% quota | Research, scanning | Built-in |
| Gemini CLI | Personal quota | Bulk operations | Built-in |
| Groq | Generous free | Fast inference | `GROQ_API_KEY` |
| OpenRouter | 31+ free models | Variety | `OPENROUTER_API_KEY` |
| Cerebras | 1M tokens/day | Speed (2000+ t/s) | `CEREBRAS_API_KEY` |
| SambaNova | Persistent free | DeepSeek-R1 671B | `SAMBANOVA_API_KEY` |
| DeepSeek | 5M tokens | Reasoning | `DEEPSEEK_API_KEY` |

### Scarce Resources
| Provider | Status | Action |
|----------|--------|--------|
| Claude (Antigravity) | ~3 accounts with quota | Reserve for critical decisions |

---

## Tier 1 Status (2026-02-19)

| ID | Task | Status |
|----|------|--------|
| P-001 | Doc sync (stream keys) | ✅ Complete |
| P-002 | Permissions fix | ⏳ Script ready, needs execution |
| P-003 | zRAM persistence | ✅ Complete (12GB zstd active) |
| P-004 | Chinese mirror | ✅ Complete (not found) |

---

## Model Delegation Matrix

| Task Category | Primary Model | Fallback |
|---------------|---------------|----------|
| Discovery/Scan | Gemini 3 Flash | Gemini CLI |
| Planning | Gemini 3 Flash | Sonnet 4.6 |
| Research | Gemini 3 Pro | Gemini CLI |
| Implementation | Sonnet 4.6 | Gemini 3 Pro |
| Architecture Review | Opus 4.6 | GLM-5 |
| Tests/QA | Gemini 3 Flash | Groq |

---

## Token Conservation Rules

- **Never** use `ls -R` — use `glob` with patterns
- **Never** read entire files — use `offset`/`limit`
- **Batch reads** — read multiple files in parallel
- **Summarize immediately** — don't accumulate tool output
- **Checkpoint at 50%** — write to `CONTEXT-STATE-RECOVERY-[DATE].md`

---

## Code Standards

- **Async**: AnyIO TaskGroups (never asyncio.gather)
- **Containers**: Rootless Podman, UID 1001
- **No PyTorch/CUDA**: ONNX, GGUF, Vulkan only
- **No telemetry**: Zero phone-home
- **Package manager**: `uv` with lock files

---

## Quick Reference: Key Paths

| What | Where |
|------|-------|
| Sprint status | `memory_bank/activeContext.md` |
| Project queue | `memory_bank/strategies/PROJECT-QUEUE.yaml` |
| Token rules | `memory_bank/strategies/OPUS-TOKEN-STRATEGY.md` |
| Agents config | `.opencode/agents/*.md` |
| Providers config | `~/.config/opencode/opencode.json` |
| API keys | `~/.bashrc` |

---

**You are cleared to begin. Read your startup files and execute.**
