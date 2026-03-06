---
tool: cline
model: claude-sonnet-4-6
account: arcana-novai
git_branch: main
session_id: sprint5-2026-02-18
version: v1.0.0
created: 2026-02-18
tags: [research-gaps, todo, future-sessions, backlog]
---

# Additional Research Needed
**v1.0.0 | 2026-02-18 | Sprint 5 Gaps**

> Living document. Add research gaps as they are discovered.
> Each item should include: topic, why it matters, suggested agent/tool.

---

## Research Findings (March 1, 2026)

### R1: Cline Context Window — ✅ CONFIRMED
- **Finding**: GPT-5-Codex has 400K context available in Cline
- **Source**: Cline Blog (Sept 2025)
- **Additional**: Code-supernova has 1M token context
- **Status**: ✅ CONFIRMED - 400K available via GPT-5-Codex model

### R2: Qdrant Collections — ⏳ PENDING (Need running stack)
- **Approach**: `curl http://localhost:6333/collections`
- **Design doc exists**: `internal_docs/qdrant-collections-design.md`
- **Collections designed**: xnai_core (384d), xnai_linguistic (768d), xnai_hybrid (1152d)

### R3: Antigravity Models — ✅ CONFIRMED
- **Models available**: 7+ models via Antigravity
- **Free tier**: Yes, unlimited access to frontier models
- **Models**: Gemini 3 Pro/Flash, Claude Sonnet 4.6, Claude Opus 4.5-4.6
- **Source**: Multiple articles confirm free access

### R5: Redis Configuration — ⏳ PENDING (Need running stack)
- **Current**: Standalone Redis (docker-compose shows single instance)
- **Recommendation**: Standalone sufficient for current scale
- **For HA**: Consider Sentinel if mission-critical

### R7: Gemini 3 CLI — ⏳ PENDING (Need running CLI)
- **Note**: Gemini 3 appears to be Antigravity internal label
- **Check**: `gemini --model gemini-3-flash "test"`

### R11: Vikunja Integration — ✅ CONFIRMED WORKING
- **Service**: Running on port 3456
- **API**: Full REST API available at `/api/v1/docs`
- **Skills**: Multiple CLI skills available for integration

### R12: BM25 Implementation — ⏳ NEEDS CODE SEARCH
- **Status**: Not verified in codebase

---

## Updated Research Queue

| Priority | ID | Topic | Status |
|----------|-----|-------|--------|
| 🔴 | R1 | Cline 400K context | ✅ DONE |
| 🔴 | R2 | Qdrant collections audit | ⏳ PENDING |
| 🟠 | R3 | Antigravity models | ✅ DONE |
| 🟠 | R5 | Redis configuration | ⏳ PENDING |
| 🟠 | R7 | Gemini 3 CLI | ⏳ PENDING |
| 🟡 | R11 | Vikunja integration | ✅ DONE |
| 🟡 | R12 | BM25 implementation | ⏳ PENDING |

---

## 🔴 CRITICAL — Block work or affect architecture

### R1: Cline "Shadow 400K" Context Window — CONFIRM OR DENY
- **Question**: Does Cline actually support 400K tokens via extended context beta?
- **Observed**: 250.8K tokens shown before compaction; progress bar ~halfway
- **Why it matters**: Changes all context pacing strategies and task sizing guidelines
- **Approach**:
  1. `grep -r "400000\|contextWindow" ~/.vscode-oss/extensions/saoudrizwan.claude-dev-*/`
  2. Enable Cline debug logging, inspect API request headers
  3. Check Cline GitHub issues: https://github.com/cline/cline/issues
- **Assigned to**: Next Cline session (targeted file read, not subagent)
- **Output file**: `expert-knowledge/research/CLINE-CONTEXT-WINDOW-RESEARCH-2026-02-18.md` (update existing)

### R2: Qdrant Collection State — What's Actually Indexed?
- **Question**: What collections exist in Qdrant? What's indexed? Is `xnai_conversations` created?
- **Why it matters**: conversation_ingestion.py and RAG pipeline depend on this
- **Approach**: `curl http://localhost:6333/collections` when Qdrant is running
- **Assigned to**: Stack health check session
- **Output file**: `expert-knowledge/infrastructure/QDRANT-COLLECTION-AUDIT-2026-02-18.md`

---

## 🟠 HIGH — Should resolve in next 1-2 sprints

### R3: Antigravity CLI — Complete Model List
- **Question**: What is the full model list available via Antigravity? Is the free tier truly unlimited?
- **Known**: claude-sonnet-4-5, gemini-2.0-flash, gpt-4o confirmed accessible
- **Unknown**: Rate limits, max context via Antigravity routing, newest models
- **Approach**: `antigravity --list-models` or check Antigravity docs/GitHub
- **Output file**: `expert-knowledge/research/ANTIGRAVITY-COMPLETE-MODEL-LIST-2026.md`

### R4: OpenCode → Antigravity Migration — What Was Lost?
- **Question**: OpenCode was archived 2026-02-14. What features/commands did OpenCode have that Antigravity doesn't?
- **Why it matters**: Some workflows may need migration
- **Approach**: Review OpenCode GitHub (archived), compare with Antigravity docs
- **Output file**: Update `expert-knowledge/research/OPENCODE-ARCHIVED-DISCOVERY-2026-02-18.md`

### R5: Redis Sentinel vs Redis Standalone — Stack Impact
- **Question**: config.toml has Redis config. Is the stack running Redis standalone or Sentinel?
- **Known issue**: Vikunja Redis auth bug documented in memory_bank
- **Approach**: Check docker-compose.yml Redis service config, test connection
- **Output file**: `expert-knowledge/infrastructure/REDIS-CONFIGURATION-AUDIT-2026.md`

### R6: fastembed + ONNX Runtime — Current Version Compatibility
- **Question**: Are the fastembed and ONNX Runtime versions in requirements-api.txt still optimal?
- **Why it matters**: FASTEMBED-ONNX-EMBEDDING-GUIDE created but may need version updates
- **Approach**: Check PyPI for latest fastembed release, test embedding pipeline
- **Output file**: Update `expert-knowledge/research/FASTEMBED-ONNX-EMBEDDING-GUIDE-2026-02-18.md`

### R7: Gemini 3 / Gemini 2.5 Pro — Confirmed Availability Window
- **Question**: Gemini 3 was noted as "now public on OpenRouter" in v1.3.0. Is it also in Gemini CLI?
- **Current status**: Listed in model-router.yaml but needs confirmation via Gemini CLI
- **Approach**: `gemini --model gemini-3-flash "test"` and verify response
- **Output file**: Update `expert-knowledge/XNAI-MODEL-INTELLIGENCE-REPORT-2026-02-18.md`

---

## 🟡 MEDIUM — Valuable but not blocking

### R8: MkDocs Material — Optimal Configuration for This Project
- **Question**: What's the best MkDocs Material config for navigating 200+ docs?
- **Relevant files**: docs/ directory, multiple research requests already filed
- **Approach**: Deep research with Gemini CLI on MkDocs Material best practices
- **Output file**: `docs/mkdocs/MKDOCS-OPTIMAL-CONFIG-2026.md`

### R9: Copilot CLI — Full Event Type Taxonomy
- **Question**: What are ALL event types in Copilot's events.jsonl beyond user/assistant message?
- **Why it matters**: harvest-cli-sessions.sh only handles known types; unknown types dropped
- **Approach**: Sample actual events.jsonl files from the 34 sessions on disk
- **Command**: `jq '.type' ~/.copilot/session-state/*/events.jsonl | sort | uniq -c | sort -rn`
- **Output file**: Update `expert-knowledge/research/CLI-SESSION-STORAGE-DEEP-DIVE-2026-02-18.md`

### R10: AWQ Production Pipeline — Current Status
- **Question**: docs/01-getting-started/05-awq-production-pipeline-guide.md was written — is AWQ quantization actually working in the stack?
- **Approach**: Review the guide, check if awq Python package is in requirements-api.txt
- **Output file**: `expert-knowledge/research/AWQ-PIPELINE-STATUS-2026.md`

### R11: Vikunja Project Management Integration
- **Question**: Is Vikunja running? Is the task sync working?
- **Known**: Vikunja Redis auth bug documented
- **Approach**: Check docker-compose.yml, test Vikunja health endpoint
- **Output file**: `expert-knowledge/infrastructure/VIKUNJA-INTEGRATION-STATUS-2026.md`

### R12: Neural BM25 Retrieval — Integration Status
- **Question**: docs/01-getting-started/06-neural-bm25-retrieval-guide.md exists — is BM25 implemented?
- **Approach**: Search codebase for BM25 references
- **Output file**: `expert-knowledge/research/NEURAL-BM25-INTEGRATION-STATUS-2026.md`

---

## 🟢 LOW — Nice to have

### R13: Sovereign MC Agent — Phase 3 Test Dependencies
- **Question**: TASK-005 mentions Phase 3 test dependencies. What are they?
- **Approach**: Review internal_docs/01-strategic-planning/SOVEREIGN-MC-AGENT-SPEC-v1.0.0.md
- **Output file**: `tests/test_sovereign_mc_agent.py` (already exists, needs review)

### R14: Docker Compose vs Podman Compose — Any Gaps?
- **Question**: The stack uses Podman but docker-compose.yml. Are all features compatible?
- **Approach**: Run `podman-compose config` and check for warnings
- **Output file**: `expert-knowledge/infrastructure/PODMAN-COMPOSE-COMPAT-2026.md`

### R15: Git Branch Strategy — Main vs Feature Branches
- **Question**: All documents say `git_branch: main` — should feature branches be used?
- **Approach**: Review Git workflow, define branch strategy for the project
- **Output file**: `expert-knowledge/protocols/GIT-WORKFLOW-PROTOCOL.md`

---

## Research Queue Summary

| Priority | ID | Topic | Suggested Tool |
|----------|-----|-------|----------------|
| 🔴 | R1 | Cline 400K shadow window | Cline (targeted) |
| 🔴 | R2 | Qdrant collection audit | Stack health session |
| 🟠 | R3 | Antigravity full model list | Antigravity CLI |
| 🟠 | R4 | OpenCode → Antigravity migration | Gemini CLI research |
| 🟠 | R5 | Redis Sentinel audit | Stack health session |
| 🟠 | R6 | fastembed version compat | Cline (pip check) |
| 🟠 | R7 | Gemini 3 CLI availability | Gemini CLI test |
| 🟡 | R8 | MkDocs optimal config | Gemini CLI deep research |
| 🟡 | R9 | Copilot event type taxonomy | Bash (jq analysis) |
| 🟡 | R10 | AWQ pipeline status | Cline (codebase search) |
| 🟡 | R11 | Vikunja integration status | Stack health session |
| 🟡 | R12 | Neural BM25 integration | Cline (codebase search) |
| 🟢 | R13 | Sovereign MC Phase 3 deps | Cline |
| 🟢 | R14 | Podman-compose compat | Podman test |
| 🟢 | R15 | Git branch strategy | Human decision |

---

## How to Add New Research Gaps

When you discover a research gap during a session, add an entry here:

```markdown
### RN: <Topic>
- **Question**: <Specific question to answer>
- **Why it matters**: <Impact on the project>
- **Approach**: <Suggested method/command>
- **Output file**: <Where to save the findings>
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0.0 | 2026-02-18 | Initial list from Sprint 5 gaps |
