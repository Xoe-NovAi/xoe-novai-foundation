# Research Job: Raptor Mini Context Window Deep Dive

**Job ID**: RJ-2026-02-27-RAPTOR-CONTEXT  
**Priority**: P0  
**Status**: PENDING  
**Created**: 2026-02-27

---

## Mission

Conduct comprehensive research on Raptor Mini preview context window for GitHub Copilot Free tier. Find all available information about token limits, context handling, and differences across clients.

---

## Research Questions

### Primary Questions
1. What is the exact context window for Raptor Mini?
2. Has it changed since release (November 2025)?
3. Does it differ between:
   - VS Code Extension
   - VS Code Insiders Extension
   - Copilot CLI
   - GitHub.com

### Secondary Questions
1. How does Raptor Mini compare to Claude Haiku 4.5 context?
2. What factors affect available context (account type, usage, etc.)?
3. Are there any official announcements about context limits?

---

## Search Strategy

### Primary Searches
```
"raptor mini" context window tokens
"raptor-mini-preview" context limit
GitHub Copilot Raptor mini token limit
raptor mini vs haiku context window
```

### Alternative Searches
```
site:github.com raptor mini context
site:docs.github.com raptor mini
raptor mini vscode context
copilot free tier context limits 2026
```

### Community Searches
```
Reddit raptor mini context
Twitter raptor mini tokens
GitHub community raptor mini
```

---

## Required Outputs

### 1. Context Window Document
Create: `memory_bank/research/RAPTOR-MINI-CONTEXT-DEEP-DIVE-2026-02-27.md`

Include:
- Exact context window (if found)
- Source citations
- Any discrepancies found
- Timeline of changes (if any)

### 2. Comparison Matrix
Update: `memory_bank/research/MODEL-RESEARCH-COMPENDIUM-2026-02-27.md`

| Model | Provider | Context | Source |
|-------|----------|---------|--------|
| Raptor Mini | Copilot | [FOUND] | [SOURCE] |

### 3. Findings Summary
Brief summary for activeContext.md update

---

## Constraints

- Focus on FREE TIER (Copilot Free)
- Verify all claims with sources
- Note any uncertainty or discrepancies

---

## Success Criteria

- [ ] Find exact context window for Raptor Mini
- [ ] Document any differences between clients
- [ ] Compare to Haiku 4.5 context
- [ ] Update all relevant documents

---

**Assigned To**: GLM-5 (via Cline CLI)  
**Escalation**: If no definitive answer found after exhaustive search, note as "unconfirmed" and suggest direct testing
