# 🧹 Planning Documents Cleanup Action Checklist

**Generated**: 2026-03-07  
**Status**: Ready for Implementation  
**Estimated Time**: 30-45 minutes total

---

## ⚡ QUICK WINS (5-10 min, Do First)

### Phase 1: Delete Duplicate Consolidation Folder
- [ ] Verify no unique content in `./memory_bank/recall/handovers_consolidated/`
  ```bash
  # Check what's there
  ls -la ./memory_bank/recall/handovers_consolidated/
  ```
- [ ] Backup folder (optional, but safe)
  ```bash
  mv ./memory_bank/recall/handovers_consolidated/ ./memory_bank/archival/backup_consolidated_20260307/
  ```
- [ ] **Delete the folder** (12 duplicate files removed)
  ```bash
  rm -rf ./memory_bank/recall/handovers_consolidated/
  ```
- [ ] Commit: `refactor: remove duplicate handover consolidation folder`

---

## 📦 MEDIUM TASKS (10-15 min)

### Phase 2: Create Archive Structure & Move Completed Implementations

#### Step 2A: Create new archive subdirectories
```bash
mkdir -p ./memory_bank/archival/completed_implementations/
mkdir -p ./memory_bank/archival/completed_waves/
mkdir -p ./memory_bank/archival/research_archive/2026-02/
mkdir -p ./memory_bank/archival/sessions/2026-02/
```

#### Step 2B: Move completed implementations (6 files)
```bash
# Phase implementation status docs
mv ./memory_bank/recall/PHASE-3C-2A-IMPLEMENTATION-STATUS.md ./memory_bank/archival/completed_implementations/
mv ./memory_bank/recall/PHASE-3C-2B-IMPLEMENTATION-STATUS.md ./memory_bank/archival/completed_implementations/
mv ./memory_bank/recall/PHASE-3B-DISPATCHER-IMPLEMENTATION.md ./memory_bank/archival/completed_implementations/
mv ./memory_bank/recall/PHASE-3A-IMPLEMENTATION-GUIDE.md ./memory_bank/archival/completed_implementations/

# System integration completion docs
mv ./memory_bank/handovers/MULTI-ACCOUNT-SYSTEM-COMPLETE.md ./memory_bank/archival/completed_implementations/
mv ./memory_bank/recall/ANTIGRAVITY-TIER1-INTEGRATION-COMPLETE.md ./memory_bank/archival/completed_implementations/
```

#### Step 2C: Move completed task dispatch waves (3 files)
```bash
mv ./memory_bank/strategies/ACTIVE-TASK-DISPATCH-2026-02-22.md ./memory_bank/archival/completed_waves/
mv ./memory_bank/strategies/ACTIVE-TASK-DISPATCH-2026-02-23.md ./memory_bank/archival/completed_waves/
mv ./memory_bank/strategies/ACTIVE-TASK-DISPATCH-WAVE-3-2026-02-23.md ./memory_bank/archival/completed_waves/
```

#### Step 2D: Move old research task results (5 files)
```bash
mv ./memory_bank/recall/RESEARCH-TASK-1-RESULTS.md ./memory_bank/archival/research_archive/2026-02/
mv ./memory_bank/recall/RESEARCH-TASK-2-RESULTS.md ./memory_bank/archival/research_archive/2026-02/
mv ./memory_bank/recall/RESEARCH-TASK-3-RESULTS.md ./memory_bank/archival/research_archive/2026-02/
mv ./memory_bank/recall/RESEARCH-TASK-4-RESULTS.md ./memory_bank/archival/research_archive/2026-02/
mv ./memory_bank/recall/RESEARCH-TASK-5-RESULTS.md ./memory_bank/archival/research_archive/2026-02/
```

- [ ] Verify moves completed successfully
- [ ] Commit: `refactor: archive 14 completed implementation & task docs`

---

## 🎯 CONSOLIDATION TASKS (10-15 min)

### Phase 3: Create Summary/Index Documents

#### Step 3A: Create TASK_DISPATCH_HISTORY.md
- [ ] Create `./memory_bank/archival/completed_waves/TASK_DISPATCH_HISTORY.md`
  
```markdown
# Task Dispatch Execution History

## Summary
- **Wave 1**: ✅ 17/17 tasks complete
- **Wave 2**: ✅ All complete (See ACTIVE-TASK-DISPATCH-2026-02-23.md)
- **Wave 3**: ✅ All complete (See ACTIVE-TASK-DISPATCH-WAVE-3-2026-02-23.md)
- **Total**: 57+ coordinated tasks across Cline, Gemini, and MC-Overseer agents

## Files
- ACTIVE-TASK-DISPATCH-2026-02-22.md - Wave 1 (162 lines)
- ACTIVE-TASK-DISPATCH-2026-02-23.md - Wave 2 (202 lines)
- ACTIVE-TASK-DISPATCH-WAVE-3-2026-02-23.md - Wave 3 (247 lines)

## Timeline
- Feb 22: Wave 1 planning & execution start
- Feb 23: Wave 2 follows Wave 1 completion
- Feb 23-present: Wave 3 execution

See primary docs for task details.
```

#### Step 3B: Create RESEARCH_RESULTS_INDEX.md
- [ ] Create `./memory_bank/archival/research_archive/2026-02/INDEX.md`
  
```markdown
# February 2026 Research Results Archive

## Task Results (5 files)
- RESEARCH-TASK-1-RESULTS.md
- RESEARCH-TASK-2-RESULTS.md
- RESEARCH-TASK-3-RESULTS.md
- RESEARCH-TASK-4-RESULTS.md
- RESEARCH-TASK-5-RESULTS.md

## Session Reports
- See `./memory_bank/archival/sessions/2026-02/` for session notes

## Cross-references
- Main research: `./memory_bank/research/`
- Active research: `./knowledge_base/expert-knowledge/research/`
```

#### Step 3C: Create OPUS_STRATEGY_INDEX.md
- [ ] Create `./memory_bank/strategies/OPUS_STRATEGY_INDEX.md`
  
```markdown
# Opus AI Strategy Documents - Index

## Deployment & Implementation
- `OPUS-COMPREHENSIVE-DEPLOYMENT-STRATEGY.md` - Full deployment guide
- `OPUS-TOKEN-OPTIMIZATION-STRATEGY.md` - Token usage optimization
- `OPUS-4.6-HANDOFF.md` - Agent handoff documentation
- `OPUS-4.6-HANDOFF-PACKAGE.md` - Complete handoff package

## Research & Configuration
- Located in: `./memory_bank/handovers/OPUS-*.md`
- Reference: `./docs/handovers/OPUS-*.md`
- Older versions archived in: `./memory_bank/archival/`

## Selection Criteria
- Use COMPREHENSIVE-DEPLOYMENT-STRATEGY for new deployments
- Use TOKEN-OPTIMIZATION-STRATEGY for cost optimization
- Use HANDOFF for agent transition guidance
```

- [ ] Commit: `docs: add archive index files for discoverability`

---

## 🔧 CONSOLIDATION CLEANUPS (Optional/Next Week)

### Phase 4: Strategy Version Consolidation
- [ ] Review UNIFIED-STRATEGY-v1.0.md vs v1.1
  - If v1.1 is more recent, delete v1.0
  ```bash
  # Compare
  diff ./memory_bank/strategies/UNIFIED-STRATEGY-v1.0.md \
       ./memory_bank/strategies/UNIFIED-STRATEGY-ENHANCED-v1.1.md
  
  # Delete old version
  rm ./memory_bank/strategies/UNIFIED-STRATEGY-v1.0.md
  ```

- [ ] Archive old OPUS strategy versions
  ```bash
  # Move to archival with version number
  mv ./memory_bank/strategies/OPUS-TOKEN-STRATEGY.md \
     ./memory_bank/archival/OPUS-TOKEN-STRATEGY-v1.0_deprecated.md
  ```

- [ ] Clean up FINAL-STRATEGY-PACKAGE-v1.0.md
  - Verify if still active, if superseded, archive it

- [ ] Commit: `refactor: consolidate strategy document versions`

### Phase 5: Session Note Organization
- [ ] Move old session notes (Feb 2026) to archival
  ```bash
  mv ./memory_bank/recall/SESSION-600a4354-KNOWLEDGE-CAPTURE.md \
     ./memory_bank/archival/sessions/2026-02/
  ```
  
- [ ] Keep ONLY recent/active sessions in recall/
  - Keep: SESSION_COMPLETION_SUMMARY.md (Mar 7 - very recent)

- [ ] Commit: `refactor: organize old session notes into archival`

---

## ✅ VALIDATION CHECKLIST

After all phases complete, verify:

- [ ] `ls memory_bank/recall/handovers_consolidated/` → NO SUCH FILE/DIRECTORY
- [ ] `ls memory_bank/archival/completed_implementations/` → 6 files present
- [ ] `ls memory_bank/archival/completed_waves/` → 3 files + INDEX
- [ ] `ls memory_bank/archival/research_archive/2026-02/` → 5 files + INDEX
- [ ] `ls memory_bank/strategies/` → Cleaner, fewer files
- [ ] No duplicate files with identical checksums (do spot check)

Count verification:
```bash
# Before: ~91 active, 31 archived
find . ! -path "*/_archive/*" -type f \( -name "*PLAN*.md" -o -name "*STRATEGY*.md" -o -name "*TASK*.md" -o -name "*SESSION*.md" -o -name "*HANDOVER*.md" -o -name "*IMPLEMENTATION*.md" \) | wc -l

# After should be ~60-70 active docs
```

---

## 📋 COMMIT STRATEGY

Make commits in this order:
1. **Commit 1**: `refactor: remove duplicate handover consolidation folder` (Phase 1)
2. **Commit 2**: `refactor: archive 14 completed implementation & task dispatch docs` (Phase 2)
3. **Commit 3**: `docs: add archive index files for discoverability` (Phase 3)
4. **Commit 4-5**: Individual strategy consolidation commits (Phase 4-5)

---

## 📝 NOTES

- All archived docs remain accessible, just organized better
- No data loss, only reorganization
- `_archive/` folder contains older consolidated items (keep as reference)
- Consider adding `.cleanupLog` file tracking archives

---

## 🎯 ESTIMATED IMPACT

**Time Investment**: 30-45 minutes  
**Storage Saved**: ~500 KB duplicate removal, ~2-3 MB reorganization  
**Clarity Gained**: 30-40% reduction in active doc cognitive load  
**Risk Level**: LOW (reversible, only reorganization)

**When to run**: Next planning session or light dev day  
**Priority**: Medium (nice-to-have but valuable)

