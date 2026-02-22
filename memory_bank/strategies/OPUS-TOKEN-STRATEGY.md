# Opus 4.6 & Gemini Token Optimization Strategy v2.0

> **Author**: Claude Opus 4.6 (Strategic Review)
> **Date**: 2026-02-19
> **Status**: ACTIVE
> **Supersedes**: v1.0 (Gemini draft)

---

## 1. Resource Inventory

### 1.1 Antigravity Accounts (from antigravity-accounts.json)

| # | Account | Claude Quota | Gemini Quota | Status |
|---|---------|-------------|--------------|--------|
| 0 | xoe.nova.ai | 0% | 100% | Enabled - Claude exhausted |
| 1 | arcana.novai | 0% | 100% | Enabled - Claude exhausted |
| 2 | taylorbare27 | 0% | 100% | Enabled - Claude exhausted |
| 3 | lilithasterion | **80%** | 100% | **Primary Claude reserve** |
| 4 | antipode7474 | **80%** | 100% | **Secondary Claude reserve** |
| 5 | antipode2727 | — | — | Disabled (verification required) |
| 6 | thejedifather | **40%** | 100% | Moderate Claude remaining |
| 7 | arcananovaai | Unknown | Unknown | Enabled, no cached quota |

**Key insight**: Only 3 accounts have Claude quota remaining. Gemini is at 100% across all accounts. This means Gemini is effectively unlimited via Antigravity, while Claude is the scarce resource.

### 1.2 Model Inventory (from opencode.json)

**Antigravity-routed (shared quota)**:
- `antigravity-claude-opus-4-6-thinking` — 200K context, 64K output
- `antigravity-claude-sonnet-4-6` — 200K context, 64K output
- `antigravity-gemini-3-pro` — 1M context, 65K output
- `antigravity-gemini-3-flash` — 1M context, 65K output

**Gemini CLI-routed (personal OAuth, separate quota)**:
- `gemini-2.5-flash` — 1M context, 65K output
- `gemini-2.5-pro` — 1M context, 65K output
- `gemini-3-flash-preview` — 1M context, 65K output
- `gemini-3-pro-preview` — 1M context, 65K output

### 1.3 Context Window Budgets

| Model | Hard Limit | Safe Operating Range | Compaction Trigger |
|-------|-----------|---------------------|-------------------|
| Opus 4.6 | 200K | < 120K (60%) | 100K (50%) |
| Sonnet 4.6 | 200K | < 140K (70%) | 120K (60%) |
| Gemini 3 Pro | 1M | < 600K (60%) | 400K (40%) |
| Gemini 3 Flash | 1M | < 700K (70%) | 500K (50%) |

---

## 2. Token Conservation Protocols

### 2.1 The "Two-Channel" Architecture

**Channel A: Antigravity (scarce Claude, abundant Gemini)**
- Use for: Opus reviews, Sonnet implementation, Gemini research
- Claude quota is shared across accounts; rotate via `activeIndex`
- Gemini quota is effectively unlimited here

**Channel B: Gemini CLI (separate personal quota)**
- Use for: Bulk research, file scanning, context recovery
- Completely independent from Antigravity quotas
- Preferred for tasks that generate large tool outputs
- Binary: `/home/arcana-novai/.nvm/versions/node/v25.3.0/bin/gemini`

**Routing Decision Tree**:
```
Is the task architectural review or conflict resolution?
  YES → Opus 4.6 (Antigravity, accounts 3/4/6)
  NO  → Is it code implementation or planning?
    YES → Sonnet 4.6 (Antigravity) or Gemini 3 Pro (Antigravity)
    NO  → Is it bulk research or file scanning?
      YES → Gemini CLI (personal quota, not Antigravity)
      NO  → Gemini 3 Flash (Antigravity, unlimited)
```

### 2.2 Session Startup Protocol (Template)

Every new agent session MUST begin with:

```
1. READ memory_bank/activeContext.md        (~40 lines, <1K tokens)
2. READ memory_bank/progress.md             (scan headers only, ~2K tokens)
3. READ memory_bank/strategies/OPUS-TOKEN-STRATEGY.md  (this file)
4. CHECK current context size (if available from tool)
5. SET token budget for this session:
   - Opus: max 80K tokens total (input + output)
   - Sonnet: max 120K tokens total
   - Gemini: max 400K tokens total
6. DECLARE session goal in first response
```

### 2.3 Context Compaction Protocol

**Trigger**: Context exceeds the "Compaction Trigger" threshold (see 1.3).

**Procedure**:
1. Write a `CONTEXT-STATE-RECOVERY-[DATE]-[SESSION].md` with:
   - Decisions made (bullet points, max 10)
   - Files modified (paths only)
   - Open questions
   - Next actions
2. Inform the user: "Context at X%. Recommend starting a new session."
3. If continuing: summarize all previous tool outputs in 2-3 sentences each.

### 2.4 Opus Conservation Rules

1. **Never use Opus for file discovery**. Use Gemini Flash or CLI first.
2. **Batch all reads**. Read 3-5 files in parallel, never one at a time.
3. **Cap thinking budget**. Use `low` variant (8K thinking) for routine reviews; `max` (32K) only for architectural decisions.
4. **Front-load context**. Read the memory bank ONCE at session start; don't re-read files.
5. **Compact proactively**. Don't wait for the user to ask; checkpoint at 50% context.
6. **Delegate to subagents**. Use the Task tool to dispatch research to explore agents.

---

## 3. Account Rotation Protocol

When Claude quota is exhausted on the active account:

1. Check `antigravity-accounts.json` → `cachedQuota.claude.remainingFraction`
2. Switch `activeIndexByFamily.claude` to the account with highest remaining fraction
3. Accounts 3 (lilithasterion, 80%) and 4 (antipode7474, 80%) are current reserves
4. Account 6 (thejedifather, 40%) is the tertiary reserve
5. If all accounts are at 0%: switch to Gemini-only mode until reset times pass

**Reset times are per-account, approximately 24h rolling windows.**

---

## 4. Google AI Studio Integration (Future Enhancement)

**Current state**: The Gemini CLI uses `oauth-personal` auth (from `~/.gemini/settings.json`). This is separate from Antigravity.

**Recommended enhancement**: Add a `GOOGLE_API_KEY` environment variable pointing to a Google AI Studio API key. This would allow the `opencode.json` to define models that route through AI Studio rather than Antigravity OAuth, further isolating quota pools.

**Implementation**:
1. Generate API key at `aistudio.google.com`
2. Add to `~/.bashrc`: `export GOOGLE_API_KEY=<key>`
3. In `opencode.json`, add a `google-aistudio` provider block (requires OpenCode plugin support verification)

**Status**: Deferred — the current two-channel architecture (Antigravity + Gemini CLI) is sufficient. Revisit if Antigravity Gemini quotas ever become constrained.

---

## 5. Anti-Patterns (Lessons from This Session)

1. **Never read entire directory trees**. The `ls -R` command earlier consumed ~15K tokens of VS Code cache listings. Use `glob` with specific patterns instead.
2. **Never let tool output accumulate unread**. Summarize or discard immediately.
3. **Don't trust `edit` with guessed content**. Always `read` the file first. Two failed edits in this session wasted ~4K tokens.
4. **Don't write the same file twice**. Plan the content, write once.
5. **The 290K overflow was caused by**: accumulated tool outputs (especially the massive `ls -R` and `grep` results) that were never pruned from the message history. The OpenCode CLI does not auto-prune, so the agent must self-regulate.

---
**Version**: 2.0
**Effective**: 2026-02-19
**Approved by**: Claude Opus 4.6 (this session)
