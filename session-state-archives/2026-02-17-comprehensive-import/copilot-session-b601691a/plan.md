# OpenCode & Multi-CLI Hardening Plan - CORRECTED

**Created**: 2026-02-17T21:11 UTC  
**Corrected**: 2026-02-17T21:52 UTC  
**Status**: PHASE 1 COMPLETE (OpenCode Fixed) → PHASE 2 (Correcting Hallucinations)  
**Scope**: Fix OpenCode, research **CLI-only** free models, establish clear nomenclature

---

## CRITICAL CORRECTION: Nomenclature & Hallucinations

### Issues Identified
- ❌ Previous research had **hallucinations** in agent assignments
- ❌ Grok MC assigned "Claude Opus" (Grok runs Grok models, not Claude)
- ❌ Gemini-CLI assigned "GPT-5.2-Codex" (Gemini CLI runs Gemini models only)
- ❌ Cline-Kat nomenclature confused (refers to VS Code extension + kat-coder-pro, NOT Cline CLI)
- ❌ Mixed CLI and IDE plugins without clear distinction

### Nomenclature Decision
**Going forward:**
- **Cline** = Cline CLI (terminal-based, v2.2.3)
- **OpenCode** = OpenCode CLI (terminal-based, v1.2.6)
- **Copilot** = Copilot CLI (terminal-based, v0.0.410)
- **Gemini** = Gemini CLI (terminal-based, v0.28.2)

**For IDE plugins, explicit naming:**
- "Cline VS Code Extension"
- "Copilot VS Code Extension"
- "OpenCode IDE"

---

## 1. PHASE 1: OPENCODE CONFIGURATION FIX ✅ COMPLETE

- [x] 1.1 Fixed opencode.json to valid schema
- [x] 1.2 Preserved MCP servers configuration
- [x] 1.3 Verified opencode --version works (v1.2.6)
- [x] 1.4 OpenCode CLI operational

**Status**: ✅ DONE - OpenCode CLI back online

---

## 2. PHASE 2: ESTABLISH NOMENCLATURE (IN PROGRESS)

### 2.1 Create CLI Nomenclature Guide
- [ ] 2.1.1 Document: CLI vs IDE distinction rules
- [ ] 2.1.2 File: `expert-knowledge/CLI-NOMENCLATURE-GUIDE-v1.0.0.md`
- [ ] 2.1.3 Update: `.clinerules/00-core-context.md` with nomenclature rules
- [ ] 2.1.4 Update: `memory_bank/activeContext.md` to reflect CLI-first approach

---

## 3. PHASE 3: RESEARCH CLI-ONLY FREE MODELS (IN PROGRESS)

### 3.1 Copilot CLI Free Models ✅ RESEARCHED
**Models available in Copilot CLI (v0.0.410):**
- claude-sonnet-4.5
- claude-haiku-4.5
- claude-opus-4.6
- claude-opus-4.6-fast
- claude-opus-4.5
- claude-sonnet-4
- gemini-3-pro-preview
- gpt-5.3-codex
- gpt-5.2-codex
- gpt-5.2
- gpt-5.1-codex-max
- gpt-5.1-codex
- gpt-5.1
- gpt-5
- gpt-5.1-codex-mini
- gpt-5-mini
- gpt-4.1

**Which are free tier?** → NEED TO RESEARCH (GitHub subscription required?)

### 3.2 Cline CLI Free Models (IN PROGRESS)
**From research:** Cline CLI (v2.2.3) supports:
- Providers: openai-native (GPT), anthropic (Claude), moonshot (Kimi), custom via baseurl
- Can auth with API keys
- Supports models: gpt-4o, claude-sonnet-4-5-20250929, kimi-k2.5, custom

**Which are free tier?** → NEED TO RESEARCH (free trial vs paid)

### 3.3 OpenCode CLI Free Models ✅ VERIFIED
**From previous research (opencode models --verbose):**
- Big Pickle - FREE
- GLM-5-free - FREE  
- GPT-5-Nano - FREE
- Kimi K2.5-free - FREE
- MiniMax M2.5-free - FREE

**Status**: ✅ Verified all are free tier

### 3.4 Gemini CLI Models (IN PROGRESS)
**From research:** Gemini CLI (v0.28.2) uses `--model` option
- Defaults to Gemini models
- Supports multiple Gemini versions

**Which models available? Which are free?** → NEED TO RESEARCH

---

## 4. PHASE 4: CREATE ACCURATE MODEL CARDS

### 4.1 Copilot CLI Model Cards
- [ ] 4.1.1 Research: Which Copilot models are on free tier?
- [ ] 4.1.2 Research: Authentication requirements?
- [ ] 4.1.3 Create: `copilot-cli-free-models-v1.0.0.md`

### 4.2 Cline CLI Model Cards
- [ ] 4.2.1 Research: Which Cline models are on free tier?
- [ ] 4.2.2 Research: API key requirements?
- [ ] 4.2.3 Create: `cline-cli-free-models-v1.0.0.md`

### 4.3 OpenCode CLI Model Cards
- [ ] 4.3.1 Update existing: `opencode-free-models-v1.0.0.md` (verify accuracy)
- [ ] 4.3.2 Ensure: All models marked as free tier

### 4.4 Gemini CLI Model Cards
- [ ] 4.4.1 Research: What Gemini models available in Gemini CLI?
- [ ] 4.4.2 Research: Free vs paid models?
- [ ] 4.4.3 Create: `gemini-cli-free-models-v1.0.0.md`

---

## 5. PHASE 5: CORRECT AGENT-CLI-MODEL ASSIGNMENTS

### 5.1 Research Actual Agent Models
- [ ] 5.1.1 Copilot (this CLI) → What models? Free tier?
- [ ] 5.1.2 Cline (agent/CLI) → What models? Free tier?
- [ ] 5.1.3 Gemini (agent/CLI) → What Gemini models?
- [ ] 5.1.4 OpenCode (agent/CLI) → Confirm Big Pickle + Kimi K2.5-free + GPT-5-Nano
- [ ] 5.1.5 Grok MC (agent) → What models does Grok actually use? (NOT Claude!)

### 5.2 Create Accurate Matrix
- [ ] 5.2.1 Create: `AGENT-CLI-MODEL-MATRIX-v1.0.0.md`
- [ ] 5.2.2 Document: CLI → Available Models
- [ ] 5.2.3 Document: Agent → Primary CLI → Primary Model
- [ ] 5.2.4 Document: Fallback chains & why

---

## 6. PHASE 6: UPDATE ALL DOCUMENTATION

### 6.1 Create New Docs
- [ ] 6.1.1 CLI-NOMENCLATURE-GUIDE-v1.0.0.md
- [ ] 6.1.2 AGENT-CLI-MODEL-MATRIX-v1.0.0.md
- [ ] 6.1.3 Model card for each CLI's free models

### 6.2 Update Existing Docs
- [ ] 6.2.1 `.clinerules/00-core-context.md` - Add nomenclature rules
- [ ] 6.2.2 `memory_bank/activeContext.md` - Fix agent assignments
- [ ] 6.2.3 `memory_bank/progress.md` - Reflect corrected status
- [ ] 6.2.4 Archive previous hallucinated docs

### 6.3 Cross-Reference Check
- [ ] 6.3.1 Verify all links work
- [ ] 6.3.2 Verify no contradictions
- [ ] 6.3.3 Verify nomenclature consistent throughout

---

## Success Criteria
✅ Clear CLI vs IDE nomenclature established  
✅ No hallucinations in model research (verified from `--help` output)  
✅ Free tier models clearly documented for each CLI  
✅ Agent assignments accurate to reality  
✅ All documentation updated without contradictions  
✅ Ready for team use without confusion
