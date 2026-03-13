# XNAi Foundation - Gemini CLI Comprehensive Onboarding v1.0

**Created**: 2026-02-21
**Author**: GLM-5 (Implementation Agent)
**Context**: Post-Cline Research Integration
**Status**: READY FOR EXECUTION

---

## 🎯 EXECUTIVE SUMMARY

You have been assigned **TWO CRITICAL TASKS** that must be completed in sequence:

1. **P-017: AWQ Removal & CPU+Vulkan Optimization** (Primary)
   - Remove PyTorch/AWQ dependencies from the stack
   - Archive GPU research knowledge
   - Maintain torch-free mandate

2. **Session-State Consolidation** (Secondary)
   - Consolidate 38+ files into Diataxis-compliant project structure
   - Update all cross-references and navigation
   - Eliminate session-state pollution

---

## 🧠 CONTEXT FROM PREVIOUS AGENT (CLINE)

### Research Completed (Sprint 5-9)

Cline (claude-sonnet-4-6) has completed extensive research that informs your tasks:

#### 1. Model Intelligence Report
**Location**: `expert-knowledge/XNAI-MODEL-INTELLIGENCE-REPORT-2026-02-18.md`
**Key Findings**:
- **CONFIRMED REAL**: `claude-opus-4-6`, `claude-sonnet-4-6`, `gemini-3-pro-preview`, `gemini-3-flash-preview`
- **CONFIRMED HALLUCINATED**: "Cline FREE Opus promo"
- **Cline Model**: Uses `claude-sonnet-4-6` (not 4-5)

#### 2. Antigravity Auth Discovery
**Location**: `expert-knowledge/research/ANTIGRAVITY-AUTH-DISCOVERY-2026-02-18.md`
**Key Findings**:
- Free frontier models via Google OAuth
- Models: Opus 4.6 (thinking), Sonnet 4.6, Gemini 3 Pro/Flash
- All available at zero cost after OAuth setup

#### 3. CLI Session Storage Deep Dive
**Location**: `expert-knowledge/research/CLI-SESSION-STORAGE-DEEP-DIVE-2026-02-18.md`
**Key Findings**:
- Copilot CLI: 34 sessions found at `~/.copilot/session-state/`
- Session data includes: events.jsonl, plan.md, workspace.yaml
- Harvest strategy defined for institutional memory

#### 4. Agent-CLI Model Matrix
**Location**: `expert-knowledge/AGENT-CLI-MODEL-MATRIX-v3.0.0.md`
**Key Findings**:
- Authoritative CLI orchestration map
- Corrections from v2.0.0 hallucinations
- Tiered AI orchestration model across 5 tool layers

---

## 📋 TASK 1: AWQ REMOVAL (P-017)

### Task Document
**Primary**: `expert-knowledge/gemini-inbox/P-017-AWQ-REMOVAL-TASK.md`
**Guide**: `plans/AWQ-REMOVAL-REFACTORING-GUIDE.md`

### Critical Constraint
**TORCH-FREE MANDATE**: No PyTorch dependencies allowed

### Current Architecture
- **Base Image**: `xnai-base:latest` (Python 3.12-slim)
- **Inference**: llama-cpp-python with Vulkan + OpenBLAS
- **Voice**: Piper TTS (ONNX) + Faster-Whisper (CTranslate2)
- **Vector DB**: FAISS CPU + Qdrant ready
- **Orchestration**: LangChain (torch-free)

### Task Groups (Parallel Execution)

#### GROUP A: File System Cleanup (30 min)
- [ ] A.1: Audit all files for AWQ references
- [ ] A.2: Create deletion checklist
- [ ] A.3: Verify no runtime dependencies
- [ ] A.4: Document shared dependencies

**Deliverable**: `plans/awq-removal-file-audit.md`

#### GROUP B: Memory Bank & Documentation (1 hour)
- [ ] B.1: Create GPU Research Archive at `expert-knowledge/_archive/gpu-research/`
- [ ] B.2: Document AWQ Architecture
- [ ] B.3: Update memory_bank/activeContext.md
- [ ] B.4: Update memory_bank/progress.md

**Deliverable**: `expert-knowledge/_archive/gpu-research/AWQ-ARCHITECTURE.md`

#### GROUP C: GPU Research Archive (30 min)
- [ ] C.1: Identify all GPU-related research documents
- [ ] C.2: Create archive structure
- [ ] C.3: Move documents with metadata preservation
- [ ] C.4: Create archive index

**Deliverable**: `expert-knowledge/_archive/gpu-research/INDEX.md`

#### GROUP D: Validation & Testing (30 min)
- [ ] D.1: Verify torch-free status
- [ ] D.2: Test build process
- [ ] D.3: Validate documentation integrity
- [ ] D.4: Performance validation

**Deliverable**: `plans/awq-removal-validation-report.md`

---

## 📋 TASK 2: SESSION-STATE CONSOLIDATION

### Task Document
**Primary**: `session-state-archives/2026-02-17-comprehensive-import/GEMINI-HANDOFF-2026-02-21.md`

### Sessions to Consolidate

| Session ID | Focus | Files | Target Phase |
|------------|-------|-------|--------------|
| `copilot-session-600a4354` | Agent Bus Implementation | 30+ | PHASE-7 |
| `copilot-session-b601691a` | CLI Hardening | 6 | PHASE-8 |
| `copilot-session-392fed92` | Documentation Audit | 2 | PHASE-0 |

### Diataxis Categorization

| Category | Purpose | Examples |
|----------|---------|----------|
| 🚀 TUTORIALS | Learning-oriented | Getting started, onboarding, quick starts |
| 🛠️ HOW-TO GUIDES | Problem-oriented | Implementation guides, troubleshooting |
| 📖 REFERENCE | Information-oriented | API docs, specs, checklists |
| 🧠 EXPLANATION | Understanding-oriented | Architecture, design decisions, summaries |

### Consolidation Sequence

1. **Phase 0**: Documentation Audit (2 files)
   - Move audit plan to `🚀 TUTORIALS/`
   - Move implementation plan to `🛠️ HOW-TO-GUIDES/`

2. **Phase 7**: Agent Bus Completion (30+ files)
   - Categorize each file by content type
   - Move to appropriate Diataxis subdirectory
   - Update cross-references

3. **Phase 8**: CLI Hardening (6 files)
   - Preserve CLI configuration decisions
   - Move research findings to reference
   - Update navigation indexes

### Cross-Reference Updates Required

- [ ] Update `internal_docs/01-strategic-planning/index.md`
- [ ] Update `memory_bank/activeContext.md`
- [ ] Update `session-state-organization/MAPPING.md`
- [ ] Update all PHASE-EXECUTION-INDEXES
- [ ] Verify all internal links

---

## 🛠️ AVAILABLE RESOURCES

### Gemini CLI Configuration
- **Binary**: `~/.nvm/versions/node/v25.3.0/bin/gemini`
- **Auth**: Google OAuth (personal quota)
- **Models**: 
  - `gemini-2.5-pro` (research, analysis)
  - `gemini-3-pro-preview` (1M context)
  - `gemini-3-flash-preview` (fast operations)
- **Rate Limits**: 25 req/day (Pro), higher for Flash

### Antigravity Models (Via OpenCode)
- `claude-opus-4-6-thinking` (200K context)
- `claude-sonnet-4-6` (200K context)
- `gemini-3-pro` (1M context)
- `gemini-3-flash` (1M context)

### Project Files
- Memory Bank: `memory_bank/`
- Expert Knowledge: `expert-knowledge/`
- Plans: `plans/`
- Session Archives: `session-state-archives/`

---

## 📊 EXECUTION PRIORITY

### Phase 1: AWQ Removal (Primary)
**Rationale**: Blocks other work, critical for torch-free mandate
**Time**: 2.5 hours total
**Order**: Group A → B → C → D (sequential dependencies)

### Phase 2: Session-State Consolidation (Secondary)
**Rationale**: Can be done in parallel with validation
**Time**: 2 hours total
**Order**: Phase 0 → Phase 7 → Phase 8 → Cross-references

---

## ⚠️ RISK MITIGATION

### Risk 1: Breaking Dependencies
- **Mitigation**: Complete GROUP A audit before any file operations
- **Check**: Verify shared dependencies before removal

### Risk 2: Loss of GPU Research Knowledge
- **Mitigation**: Create archive before removing files
- **Check**: Preserve all technical details with metadata

### Risk 3: Broken Cross-References
- **Mitigation**: Use grep to find all references before moves
- **Check**: Validate all links after consolidation

### Risk 4: Incorrect Diataxis Categorization
- **Mitigation**: Analyze content before assigning category
- **Check**: Review categorization with content analysis

---

## ✅ COMPLETION CHECKLIST

### AWQ Removal
- [ ] File audit complete (`plans/awq-removal-file-audit.md`)
- [ ] GPU research archived (`expert-knowledge/_archive/gpu-research/`)
- [ ] Dockerfile.awq removed
- [ ] Documentation updated
- [ ] Torch-free status verified
- [ ] Build process tested
- [ ] Validation report complete

### Session-State Consolidation
- [ ] Phase 0 files moved (2 files)
- [ ] Phase 7 files moved (30+ files)
- [ ] Phase 8 files moved (6 files)
- [ ] All Diataxis categories applied
- [ ] Cross-references updated
- [ ] Navigation validated
- [ ] Links verified working

### Strategy Updates
- [ ] Memory bank updated
- [ ] Research queue updated
- [ ] Active context current

---

## 📝 FINAL REPORT REQUIREMENTS

After completion, provide:

1. **AWQ Removal Report**:
   - Files removed
   - Files archived
   - Documentation updated
   - Validation results

2. **Consolidation Report**:
   - Files moved (source → destination)
   - Directories created
   - Cross-references updated
   - Link validation results

3. **Performance Validation**:
   - Build time
   - Memory usage
   - Torch-free confirmation

4. **Recommendations**:
   - Follow-up tasks
   - Process improvements
   - Documentation gaps

---

## 🎯 SUCCESS METRICS

### AWQ Removal
- ✅ Zero PyTorch dependencies
- ✅ GPU research preserved
- ✅ Build succeeds
- ✅ Documentation current
- ✅ Performance maintained (<6GB RAM, <500ms)

### Session-State Consolidation
- ✅ 38+ files consolidated
- ✅ Diataxis compliance
- ✅ Cross-references working
- ✅ Navigation functional
- ✅ Zero content loss

---

## 📞 SUPPORT RESOURCES

### Key Documents
- Memory Bank: `memory_bank/activeContext.md`
- Strategy: `memory_bank/strategies/OPUS-TOKEN-STRATEGY.md`
- Research Queue: `memory_bank/strategies/RESEARCH-JOBS-QUEUE.md`
- Project Queue: `memory_bank/strategies/PROJECT-QUEUE.yaml`

### CLI Help
- Gemini CLI: `gemini --help`
- OpenCode: `opencode --help`

### Environment
- Working Directory: `/home/arcana-novai/Documents/xnai-foundation`
- Git Branch: `main`
- Current Time: 2026-02-21

---

**Document Version**: 1.0.0
**Status**: READY FOR GEMINI CLI EXECUTION
**Next Review**: Post-completion

