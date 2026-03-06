# Research Task: AI Model Context Window Investigation

## Mission

You are the XNAi Foundation Research Agent. Your mission is to investigate context window changes for AI models and create comprehensive research documents.

## Context

### Critical Issue
While using Raptor in Copilot Extension (VS Code Insiders), the user observed a context limit of **192K tokens**, not the expected **264K tokens** they believe they had before. This needs investigation.

### Other Models to Research
We also need detailed research on:
1. **Raptor-mini-preview** - Context window changes, CLI vs Extension differences
2. **Haiku 4.5** - Current free tier context window
3. **kat-coder-pro** - Via Cline CLI 2.0, context window
4. **MiniMax M2.5 Free** - OpenCode built-in, context window
5. **Trinity-large-preview** - Availability and context

## Research Tasks

### Task 1: Raptor Context Window Investigation

Research questions:
1. What is the current context window for `raptor-mini-preview`?
2. Has it changed recently? When?
3. Is the context different between:
   - Copilot Extension in VS Code
   - Copilot Extension in VS Code Insiders
   - Copilot CLI (`copilot -m raptor-mini-preview`)
4. How can we restore/get the larger context window?
5. Are there any API configuration options to change context?

Search terms:
- "raptor-mini-preview context window 2026"
- "GitHub Copilot raptor context limit"
- "copilot CLI raptor-mini-preview context"

### Task 2: Free Tier Model Research

For each model, find:
1. Model ID / Provider
2. Current context window
3. Any limitations or caveats
4. How to access (CLI, API, etc.)
5. Best practices for that model

Models to research:
- `claude-haiku-4.5` via Copilot
- `kat-coder-pro` via Cline/OpenRouter
- `minimax-m2.5-free` via OpenCode
- Any other free models discovered

### Task 3: Create Model Research Documents

For each model, create a document at:
`memory_bank/research/models/MODEL-[NAME]-YYYY-MM-DD.md`

Include:
- Basic information (provider, model ID, context window)
- Capabilities and limitations
- Best practices
- Configuration examples
- Research history with sources

## Output Requirements

1. **Raptor Research Document**: Create `memory_bank/research/models/RAPTOR-MINI-2026-02-27.md`
2. **Update Compendium**: Update `memory_bank/research/MODEL-RESEARCH-COMPENDIUM-2026-02-27.md` with findings
3. **Config Updates**: Note any needed changes to `configs/model-router.yaml`

## Constraints

- Focus on **free tier** and **preview** versions
- Verify all claims with sources
- Include dates of research
- Note any discrepancies found

Begin your research now.