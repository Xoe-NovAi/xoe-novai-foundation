# XNAi OpenCode Agent Rules

These rules were moved from `opencode.json` (where `"rules"` is not a valid schema key)
to this markdown file for reference. Load these into your context manually or via system prompt.

## Active Rules

1. Read `memory_bank/activeContext.md` before starting any task
2. Read `memory_bank/progress.md` to understand current phase
3. **NEVER** use `asyncio.gather()` — use AnyIO TaskGroups only
4. No PyTorch, CUDA, Triton, or sentence-transformers — ONNX + GGUF + Vulkan only
5. All containers run as UID 1001 — fix permissions with `scripts/fix-permissions.sh`
6. Zero external telemetry — sovereign stack only
7. Update `memory_bank/activeContext.md` after significant changes
8. Follow `expert-knowledge/AGENT-CLI-MODEL-MATRIX-v3.0.0.md` for model selection (v3.0.1 is current — v2.0.0 is OBSOLETE)
9. Log decisions and findings to sprint log in `internal_docs/00-system/implementation-executions/`

## Model Discovery Protocol

**CRITICAL**: Agents frequently fail at model discovery due to training cutoff blindness. Follow this protocol BEFORE claiming any model "doesn't exist":

10. **NEVER claim a model doesn't exist based on training data alone** — AI model landscape changes faster than training cutoffs
11. **Check OpenRouter API** for live model list: `curl https://openrouter.ai/api/v1/models | python3 -c "import sys,json; [print(m['id']) for m in json.load(sys.stdin)['data']]"`
12. **Authoritative knowledge files** (read in this order if uncertain about a model):
    1. `expert-knowledge/MODEL-DISCOVERY-SYSTEM-v1.0.0.md` — comprehensive confirmed model list with OpenRouter IDs
    2. `expert-knowledge/XNAI-MODEL-INTELLIGENCE-REPORT-2026-02-18.md` — full model cards v1.3.0
    3. `expert-knowledge/AGENT-CLI-MODEL-MATRIX-v3.0.0.md` — model routing matrix v3.0.1
13. **Confirmed real models** that previous agents incorrectly called "hallucinated" or "uncertain":
    - `moonshotai/kimi-k2.5` — REAL (1T MoE, 256K ctx, 76.8% SWE-Bench)
    - `minimax/minimax-m2.5` — REAL (197K ctx, 80.2% SWE-Bench)
    - `z-ai/glm-5` — REAL (205K ctx, Z.ai/Zhipu AI)
    - `google/gemini-3-pro-preview` — REAL PUBLIC on OpenRouter ($2/$12, 1.05M ctx)
    - `google/gemini-3-flash-preview` — REAL PUBLIC on OpenRouter ($0.50/$3, 1.05M ctx)
    - `claude-sonnet-4-6` — REAL (current Cline model, Jan 2026 cutoff)
    - `claude-opus-4-6` — REAL (128K output, Aug 2025 cutoff)
14. **Cline free tier**: User is on a **limited-time special free tier** for `claude-sonnet-4-6` — NOT standard paid API. This may expire; have contingency plans using Antigravity/OpenCode free models

## Document Signing Protocol

**MANDATORY**: All new files created by agents MUST be signed per `expert-knowledge/protocols/DOCUMENT-SIGNING-PROTOCOL.md`.

15. **All new .md files MUST include YAML frontmatter** as the very first content:
    ```yaml
    ---
    tool: cline|opencode|gemini-cli|copilot|human
    model: claude-sonnet-4-6|gemini-2.0-flash|...   # get exact model from configs/agent-identity.yaml
    account: arcana-novai
    git_branch: main
    session_id: sprint<N>-YYYY-MM-DD
    version: v1.0.0
    created: YYYY-MM-DD
    tags: [tag1, tag2]
    ---
    ```
16. **All new .py and .sh files MUST include a signed comment header** immediately after the shebang (if any):
    ```python
    # ---
    # tool: cline
    # model: claude-sonnet-4-6
    # session_id: sprint<N>-YYYY-MM-DD
    # version: v1.0.0
    # created: YYYY-MM-DD
    # ---
    ```
17. **Frontmatter must be FIRST** — before any title, content, or imports. Use `scripts/sign-document.sh` to retroactively sign unsigned files.

## Session Output Discipline

**MANDATORY**: Agents must save all meaningful outputs to the project. Nothing of value stays only in session state.

18. **ALL research findings** → `expert-knowledge/research/TOPIC-YYYY-MM-DD.md`
19. **ALL protocol definitions** → `expert-knowledge/protocols/PROTOCOL-NAME.md`
20. **ALL plans and decisions** → `memory_bank/activeContext.md` or `memory_bank/activeContext/sprint-N-handover-YYYY-MM-DD.md`
21. **CLI session data** → harvested via `scripts/harvest-cli-sessions.sh` into `xoe-novai-sync/mc-imports/`
22. **Post-task**: Update `ADDITIONAL-RESEARCH-NEEDED.md` with any gaps discovered during the session
22b. **Cognitive feedback loop**: When benchmark results reveal documentation architecture weaknesses (poor scores in specific environments/tests), log enhancement proposals to `benchmarks/COGNITIVE-ENHANCEMENTS.md` using the template defined there. Categories: MB (Memory Bank), HO (Handover), CF (Config), CP (Context Packing), AC (Agent Coordination), BM (Benchmark). Reference the benchmark version and affected test/environment IDs.

## Configs Reference

23. **Model routing**: `configs/model-router.yaml` — single source of truth for all providers/models
24. **Free providers**: `configs/free-providers-catalog.yaml` — focused free-tier catalog
25. **Complex tasks**: Follow `expert-knowledge/protocols/COMPLEX-TASK-PROTOCOL.md` for multi-deliverable tasks
26. **Agent identity**: `configs/agent-identity.yaml` — authoritative registry of each agent's current model/tool/account. Always read this before signing a document. `scripts/sign-document.sh` reads it automatically.

## Agent Taxonomy (MANDATORY — Do Not Misclassify)

**CRITICAL taxonomy rules — violations corrupt all documentation:**

- **Cline (VSCodium)**: model = `claude-sonnet-4-6` (NOT claude-opus-4-5 — that was a Sprint 5 error)
- **OpenCode CLI**: Status = **ACTIVE**. The upstream GitHub repo was archived by its original maintainers — this does NOT affect use. arcana-novai is the primary user and plans to **fork OpenCode** to create a custom XNAi TUI. Never describe OpenCode as "archived" in user-facing documentation.
- **Antigravity** (`opencode-antigravity-auth@latest`) is an **OAuth plugin that runs INSIDE OpenCode CLI**. It is NOT a separate CLI, NOT a separate agent. It unlocks premium GitHub OAuth-authenticated models within OpenCode. Always reference it as `opencode.plugin_antigravity`, never as a top-level tool.
- **Full taxonomy**: see `docs/architecture/XNAI-AGENT-TAXONOMY.md`
