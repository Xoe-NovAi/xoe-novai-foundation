# Cline Implementation Plan for Gemini CLI Tasks

**Created**: 2026-02-21
**Author**: Cline (claude-sonnet-4-6)
**Context**: Post-Gemini CLI Onboarding Review
**Status**: READY FOR EXECUTION

---

## 🎯 EXECUTIVE SUMMARY

Based on the memory bank review and Gemini CLI onboarding document, I have developed a comprehensive implementation plan for the two critical tasks assigned to Gemini CLI:

1. **P-017: AWQ Removal & CPU+Vulkan Optimization** (Primary)
2. **Session-State Consolidation** (Secondary)

---

## 📋 TASK BREAKDOWN

### Phase 1: AWQ Removal (Primary Task)

#### GROUP A: File System Cleanup (30 min)
**Objective**: Audit all files for AWQ references and create deletion checklist

**Steps**:
1. **A.1**: Audit all files for AWQ references
   - Search for "AWQ", "pytorch", "torch" in all files
   - Identify files that reference AWQ components
   - Document current usage patterns

2. **A.2**: Create deletion checklist
   - List all files to be removed
   - Identify dependencies and shared components
   - Create backup plan for GPU research knowledge

3. **A.3**: Verify no runtime dependencies
   - Check Dockerfiles for AWQ references
   - Verify build process dependencies
   - Test current functionality

4. **A.4**: Document shared dependencies
   - Identify components that might be affected
   - Create dependency mapping
   - Document mitigation strategies

**Deliverable**: `plans/awq-removal-file-audit.md`

#### GROUP B: Memory Bank & Documentation (1 hour)
**Objective**: Create GPU Research Archive and update documentation

**Steps**:
1. **B.1**: Create GPU Research Archive at `expert-knowledge/_archive/gpu-research/`
   - Create directory structure
   - Set up metadata preservation
   - Create archive index

2. **B.2**: Document AWQ Architecture
   - Create comprehensive AWQ architecture document
   - Document GPU research findings
   - Preserve technical details

3. **B.3**: Update memory_bank/activeContext.md
   - Add AWQ removal progress
   - Update current sprint status
   - Document decisions

4. **B.4**: Update memory_bank/progress.md
   - Add task completion status
   - Update project queue
   - Document next steps

**Deliverable**: `expert-knowledge/_archive/gpu-research/AWQ-ARCHITECTURE.md`

#### GROUP C: GPU Research Archive (30 min)
**Objective**: Identify and archive all GPU-related research documents

**Steps**:
1. **C.1**: Identify all GPU-related research documents
   - Search for GPU, Vulkan, performance research
   - Identify relevant documents
   - Create inventory

2. **C.2**: Create archive structure
   - Organize by research topic
   - Create metadata schema
   - Set up preservation strategy

3. **C.3**: Move documents with metadata preservation
   - Move files to archive
   - Preserve creation dates
   - Update cross-references

4. **C.4**: Create archive index
   - Create comprehensive index
   - Document archive structure
   - Create search functionality

**Deliverable**: `expert-knowledge/_archive/gpu-research/INDEX.md`

#### GROUP D: Validation & Testing (30 min)
**Objective**: Verify torch-free status and validate implementation

**Steps**:
1. **D.1**: Verify torch-free status
   - Check for any remaining PyTorch dependencies
   - Verify build process
   - Test functionality

2. **D.2**: Test build process
   - Run Docker build
   - Verify container creation
   - Test runtime functionality

3. **D.3**: Validate documentation integrity
   - Check all links
   - Verify cross-references
   - Validate content accuracy

4. **D.4**: Performance validation
   - Test memory usage
   - Verify latency targets
   - Validate functionality

**Deliverable**: `plans/awq-removal-validation-report.md`

---

### Phase 2: Session-State Consolidation (Secondary Task)

#### Phase 0: Documentation Audit (2 files)
**Objective**: Move Phase 0 documentation to appropriate Diataxis categories

**Steps**:
1. **0.1**: Move audit plan to `🚀 TUTORIALS/`
2. **0.2**: Move implementation plan to `🛠️ HOW-TO-GUIDES/`
3. **0.3**: Update cross-references
4. **0.4**: Validate links

#### Phase 7: Agent Bus Completion (30+ files)
**Objective**: Move Phase 7 files to appropriate Diataxis categories

**Steps**:
1. **7.1**: Categorize each file by content type
2. **7.2**: Move to appropriate Diataxis subdirectory
3. **7.3**: Update cross-references
4. **7.4**: Validate links

#### Phase 8: CLI Hardening (6 files)
**Objective**: Move Phase 8 files to appropriate Diataxis categories

**Steps**:
1. **8.1**: Preserve CLI configuration decisions
2. **8.2**: Move research findings to reference
3. **8.3**: Update navigation indexes
4. **8.4**: Validate links

#### Cross-Reference Updates
**Objective**: Update all navigation and cross-references

**Steps**:
1. **CR.1**: Update `internal_docs/01-strategic-planning/index.md`
2. **CR.2**: Update `memory_bank/activeContext.md`
3. **CR.3**: Update `session-state-organization/MAPPING.md`
4. **CR.4**: Update all PHASE-EXECUTION-INDEXES
5. **CR.5**: Verify all internal links

---

## 🛠️ EXECUTION SEQUENCE

### Priority 1: AWQ Removal (Primary)

**Order**: Group A → B → C → D (sequential dependencies)

**Rationale**: Blocks other work, critical for torch-free mandate

**Time**: 2.5 hours total

### Priority 2: Session-State Consolidation (Secondary)

**Order**: Phase 0 → Phase 7 → Phase 8 → Cross-references

**Rationale**: Can be done in parallel with validation

**Time**: 2 hours total

---

## 📊 RISK MITIGATION

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

---

## 🚀 EXECUTION COMMANDS

### Start AWQ Removal
```bash
# Begin with Group A audit
gemini --model gemini-3-pro-preview "Execute AWQ Removal Group A: Audit all files for AWQ references and create deletion checklist"
```

### Start Session-State Consolidation
```bash
# Begin with Phase 0 documentation audit
gemini --model gemini-3-pro-preview "Execute Session-State Consolidation Phase 0: Move Phase 0 documentation to appropriate Diataxis categories"
```

---

**This plan leverages Gemini CLI's 1M token context window for comprehensive ecosystem analysis and execution.**