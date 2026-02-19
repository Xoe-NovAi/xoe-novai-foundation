# User Decisions & MC Strategy - 2026-02-17

## CLI Model Configuration Decisions

### 1. Copilot CLI
- **Decision**: Use Copilot Free tier (limited models, no cost)
- **Rationale**: Zero-cost setup aligned with sovereign/offline-first principles
- **Note**: Will document limited model set available on free tier

### 2. Cline CLI
- **Decision**: Use OpenRouter free tier (300+ models, limited quota)
- **Rationale**: Provides model diversity while remaining free
- **Setup**: Requires free OpenRouter account + API key from openrouter.ai
- **Fallback**: Can also use local models (Ollama/LM Studio) for zero-API setup

### 3. Gemini CLI
- **Decision**: Use Google AI Studio free tier (already decided)
- **Model**: gemini-3-flash-preview (latest, free)
- **Setup**: Free Google account + API key from aistudio.google.com
- **Rate limit**: 15 requests/minute (acceptable for free)

### 4. OpenCode CLI
- **Decision**: Use all 5 free models (already verified)
- **Models**: Big Pickle, GLM-5-free, GPT-5-Nano, Kimi K2.5-free, MiniMax M2.5-free
- **Setup**: Built-in, no API keys needed

---

## Grok MC & Mission Control Architecture

### Current State
- Grok.com Project in use as "right-hand man advisor"
- Provides birds-eye view of XNAi internal/external projects, branding, vision
- **Limitation**: Grok.com free tier cannot connect to local system
- **Current workflow**: Manual file uploads to Grok.com Project

### Proposed: Switch MC Position to Claude.ai Project
**Advantages over Grok.com:**
1. **GitHub Integration**: Claude.ai Projects can connect directly to GitHub repo
2. **Synced Context**: Full repository context auto-synced
3. **File Uploads**: Can upload MC-specific documents directly
4. **Bi-directional**: GitHub → Claude.ai and potentially Claude.ai → GitHub
5. **Existing Workflow**: Already using Claude.ai for Implementations Architect role

### Proposed MC Architecture
```
├── Claude.ai Mission Control Project
│   ├── GitHub Sync (auto-synced from repo)
│   ├── Memory Bank Docs (uploaded: activeContext, progress, systemPatterns)
│   ├── Agent Assignments (uploaded: AGENT-CLI-MODEL-MATRIX)
│   ├── Vision & Branding Docs (uploaded: custom files)
│   ├── Strategic Oversight (reads all synced content)
│   └── Issues & Recommendations (context-aware)
│
├── Existing: Claude.ai Implementations Architect Project
│   ├── Receives: CLI strategy & implementation plans
│   ├── Produces: Comprehensive implementation manuals
│   └── Outputs: Production-grade code examples
│
└── Comparison: Grok.com Project (archive or secondary)
    ├── Manual uploads (not ideal)
    ├── No GitHub sync
    └── Consider deprecating
```

### Implementation Steps for MC Migration
1. Create new Claude.ai Project named "XNAi Mission Control"
2. Configure GitHub integration (link to xnai-foundation repo)
3. Create "MC Project Briefing" document containing:
   - Entire memory_bank/ contents
   - Project vision & Ma'at ideals
   - Agent roles & responsibilities
   - All strategic initiatives
4. Upload MC Briefing to Claude.ai Project
5. Create bi-directional workflow:
   - Claude.ai MC reads GitHub for implementation updates
   - Claude.ai MC produces strategic recommendations → `/mc-oversight/` directory
   - Copilot CLI reads recommendations for orchestration

### File Structure for MC Support
```
/home/arcana-novai/Documents/xnai-foundation/
├── mc-oversight/  (NEW - Claude.ai MC outputs)
│   ├── strategic-recommendations.md (weekly strategic guidance)
│   ├── risk-assessment.md (architectural/project risks)
│   ├── initiative-status-dashboard.md (birds-eye view)
│   └── priority-matrix.md (what needs attention now)
│
├── memory_bank/  (sync to Claude.ai MC Project)
│   ├── activeContext.md
│   ├── progress.md
│   ├── systemPatterns.md
│   └── techContext.md
```

### Next Steps for User
1. ✅ Create Claude.ai Project: "XNAi Mission Control"
2. ✅ Configure GitHub integration in Claude.ai
3. ✅ Create & upload MC Briefing document
4. ⏳ Establish weekly MC briefing cadence
5. ⏳ Monitor `/mc-oversight/` outputs for strategic guidance

---

## Benefits of Claude.ai MC Over Grok.com
| Aspect | Grok.com | Claude.ai |
|--------|----------|-----------|
| GitHub Integration | ❌ No | ✅ Yes (auto-sync) |
| File Context | Manual upload only | Auto-sync + uploads |
| Bi-directional Flow | ❌ No | ✅ Yes (repo ↔ Claude) |
| Synced Context | ❌ Manual | ✅ Auto (pull from repo) |
| Production Workflow | ❌ Disrupted | ✅ Integrated |
| Free Tier Models | GPT models | Claude Sonnet 4.5 (better) |

---

## Summary
- **Copilot CLI**: Free tier (limited models)
- **Cline CLI**: OpenRouter free tier (300+ models)
- **Gemini CLI**: Google AI Studio (gemini-3-flash-preview)
- **OpenCode CLI**: Built-in 5 free models
- **MC Position**: Migrate from Grok.com to Claude.ai Project (for GitHub sync + team visibility)
