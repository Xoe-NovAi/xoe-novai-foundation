---
tool: cline
model: claude-sonnet-4-6
account: arcana-novai
git_branch: main
session_id: sprint5-2026-02-18
version: v1.0.0
created: 2026-02-18
tags: [cline, context-window, compaction, shadow-400k, research]
---

# Cline Context Window Research
**v1.0.0 | 2026-02-18 | Sprint 5**

## Status: PARTIALLY CONFIRMED — Research Ongoing

> This document captures what is known, what is observed, and what requires further
> investigation regarding Cline's context window behavior, specifically the "shadow 400K"
> phenomenon observed by the XNAi project lead.

---

## 1. Official / Documented Behavior

### Nominal Context Limits
| Model | Official Context | Cline Displayed |
|-------|-----------------|-----------------|
| claude-opus-4-5 | 200K tokens | 200K |
| claude-sonnet-4-5 | 200K tokens | 200K |
| claude-haiku-3-5 | 200K tokens | 200K |
| gemini-2.0-flash | 1M tokens | varies |

### Cline Compaction Mechanism
- Cline auto-compacts context when approaching the model's context limit
- Compaction uses a summarization pass to compress old context
- The compaction threshold is configurable (default: ~80% of context limit)
- After compaction, a summary is injected at the start of the new context window
- Full history remains in `api_conversation_history.json` even after compaction

### Configuration Options
From Cline settings (VSCodium extension settings):
```json
{
  "cline.contextWindowTokens": 200000,
  "cline.maxTokens": 8096,
  "cline.autoCompact": true,
  "cline.compactThreshold": 0.8
}
```

---

## 2. The "Shadow 400K" Observation

### What Was Observed (2026-02-18)
- **Session**: Sprint 4/5 work session with claude-sonnet-4-6
- **Observed token count**: 250,800 tokens shown in Cline UI BEFORE compaction triggered
- **Progress bar position**: ~halfway on the displayed scale
- **Implication**: If 250.8K = ~halfway, the true scale would be ~500K (or roughly 400K
  if accounting for overhead)
- **Expected behavior**: Compaction should trigger at ~160K (80% of 200K)

### Hypothesis 1: Extended Context Beta
Anthropic has provided extended context beta access to certain API tiers. The `claude-opus-4-5`
model may support up to 400K or 500K tokens via the beta feature flag:
```
anthropic-beta: interleaved-thinking-2025-05-14
anthropic-beta: extended-context-2025-XX-XX  # hypothetical flag
```

Cline may be requesting extended context and displaying the actual available window
rather than the nominal 200K limit.

### Hypothesis 2: Display Bug
The progress bar scale may be incorrect — showing a larger denominator than the actual
available context. Possible off-by-one or scaling factor bug in the Cline UI.

### Hypothesis 3: Token Counting Discrepancy
Different token counting methods (cl100k, tiktoken, Anthropic's internal counter) may
produce different counts. Cline may use a different tokenizer than the API, leading to
apparent over-counting or under-counting.

### Hypothesis 4: Multi-Window Accumulation
Cline tracks total tokens used across the session (including pre-compaction history)
rather than just the current active window. This would explain seeing 250.8K even though
the active context is within the 200K limit.

---

## 3. What Needs Further Research

### Research Actions Required

**R1: Check Cline Source Code (CONFIRMED APPROACH)**
```bash
# Cline is open source on GitHub
# Repository: https://github.com/cline/cline
# Key file: src/api/providers/anthropic.ts
# Look for: contextWindow, maxTokens, beta flags
grep -r "contextWindow\|maxTokens\|400000\|extended" ~/.vscode-oss/extensions/saoudrizwan.claude-dev-*/
```

**R2: Check API Request Headers**
Enable Cline debug logging and inspect the actual API calls:
```bash
# Set env var before launching VSCodium
CLINE_DEBUG=1 codium .
# Then check ~/.config/VSCodium/User/globalStorage/saoudrizwan.claude-dev/logs/
```

**R3: Check Anthropic API Response**
The actual context window available is returned in the API response headers:
```
x-anthropic-context-window: 400000  # hypothetical
```

**R4: Compare with claude.ai**
Claude.ai interface shows token count — compare with Cline's count for same content
to identify if there's a counting discrepancy.

**R5: Monitor `api_conversation_history.json` Size**
```bash
# Check token counts in saved history files
ls -lh ~/.config/VSCodium/User/globalStorage/saoudrizwan.claude-dev/tasks/*/api_conversation_history.json
# The largest files will indicate maximum observed context
```

---

## 4. Practical Implications

### If Shadow 400K is Real
- Cline provides ~2x the effective context of other tools at the same tier
- Sprint work should bias toward Cline for complex, long-running tasks
- Context pacing strategy should target 350K (not 160K) as the conservative limit
- model-router.yaml should be updated: `cline.effective_context: 400000`

### If Shadow 400K is a Display Artifact
- Standard 200K limit applies
- Compaction threshold remains 160K
- No change to routing strategy needed

### Current Conservative Strategy
Until confirmed, treat Cline's effective context as **200K nominal / 400K possible**.
Plan sessions assuming 200K, but don't panic if usage shows higher numbers — the session
may still complete successfully.

---

## 5. Cline-Specific Context Management Tips

### Maximize Context Efficiency
1. **Use `<context_window>` aware prompting**: Provide dense, structured context
2. **Prefer subagents for exploration**: Use `use_subagents` to avoid main context pollution
3. **Batch file writes**: Write multiple files per response to reduce tool-result tokens
4. **Compress summaries**: Request compressed handover notes rather than verbose ones

### Context Window Monitoring
```bash
# Monitor Cline's active task file sizes
watch -n 30 'ls -lh ~/.config/VSCodium/User/globalStorage/saoudrizwan.claude-dev/tasks/*/api_conversation_history.json 2>/dev/null | tail -5'
```

### Compaction Recovery
After compaction, Cline injects a summary. To preserve full fidelity:
```bash
# Before compaction triggers, save the full history
cp ~/.config/VSCodium/User/globalStorage/saoudrizwan.claude-dev/tasks/<task-id>/api_conversation_history.json \
   /home/arcana-novai/Documents/xnai-foundation/xoe-novai-sync/mc-imports/cline/<task-id>-full-$(date +%Y%m%d).json
```

---

## 6. Links and References

- Cline GitHub: https://github.com/cline/cline
- Anthropic API Docs (context windows): https://docs.anthropic.com/en/docs/about-claude/models
- Cline Issues (context-related): https://github.com/cline/cline/issues?q=context+window
- Extended Context Beta: https://docs.anthropic.com/en/docs/build-with-claude/extended-context

---

## 7. Next Steps

1. [ ] Run R5 (check api_conversation_history.json sizes for largest tasks)
2. [ ] Run R1 (grep Cline extension source for 400K references)
3. [ ] Enable debug logging and capture API headers for one session
4. [ ] Update model-router.yaml once confirmed
5. [ ] Update AGENT-CLI-MODEL-MATRIX with confirmed effective context
