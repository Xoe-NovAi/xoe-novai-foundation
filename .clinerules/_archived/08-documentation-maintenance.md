---
priority: high
context: general
activation: always
last_updated: 2026-01-27
version: 1.1
---

# Documentation Maintenance & Synchronization

**Core Philosophy**: Documentation is code. Changes to code must be reflected in documentation immediately. Trackers provide operational visibility and ensure nothing falls through the cracks.

**Memory Bank Integration**: Update memory_bank/progress.md with documentation milestones and memory_bank/activeContext.md with documentation blockers. Reference memory_bank/techContext.md for documentation technology constraints.

## 📋 Tracker Usage Standards

### **Project Status Dashboard**
- **Location**: `docs/project-tracking/PROJECT_STATUS_DASHBOARD.md`
- **Update Frequency**: Real-time for active tasks, daily summary for ongoing work
- **Content Requirements**:
  - Current phase and milestone status
  - Active blockers with mitigation plans
  - Resource utilization and timeline projections
  - Risk assessments and contingency plans
  - Stakeholder communication log

### **Task Progress Tracking**
- **task_progress Parameter**: Include in every multi-step tool call
- **Format Standards**:
  ```markdown
  - [x] Completed task with timestamp
  - [ ] Active task with clear description
  - [ ] Future task with prerequisites noted
  ```
- **Progress Updates**: Mark completed items immediately, update status regularly

### **Consolidation Resources**
- **Planning**: `project-tracking-consolidation-resources/planning/`
  - `CONSOLIDATION_MAPPING_MATRIX.md` - Content reorganization tracking
  - `CONTENT_INVENTORY_DATABASE.json` - File metadata and relationships
- **Execution**: `project-tracking-consolidation-resources/execution/`
  - `EXECUTION_CHECKLIST.md` - Step-by-step implementation tracking
  - `REFERENCE_MAPPING_TRACKER.md` - Cross-reference validation
  - `STAKEHOLDER_COMMUNICATION_PLAN.md` - Communication coordination

## 📚 Critical Documentation Synchronization

### **README Files**
- **Root README.md**: High-level project overview, quick start guide
- **Directory READMEs**: Purpose, contents, navigation guidance
- **Update Triggers**:
  - API changes affecting usage
  - New features or capabilities
  - Dependency updates with breaking changes
  - Security updates requiring user action

### **Architecture Documents**
- **Location**: `docs/03-reference/architecture/`
- **Architectural Decision Records (ADRs)**:
  - **Location**: `docs/03-reference/architecture/ADR/`
  - **Requirement**: Create an ADR for any change involving new dependencies, core data flow pivots, or performance/security boundary changes.
  - **Naming**: `NNNN-kebab-case-title.md`
- **Required Updates**:
  - Component diagrams and data flows
  - API specifications and contracts
  - Performance characteristics and limits
  - Security boundaries and controls

### **Operations Handbook**
- **Location**: `docs/project-tracking/operations-handbook.md`
- **Maintenance Schedule**: Weekly reviews, monthly updates
- **Coverage Areas**:
  - Deployment procedures and checklists
  - Monitoring and alerting configurations
  - Troubleshooting runbooks
  - Incident response procedures

### **Integration Guide**
- **Location**: `docs/project-tracking/integration-guide.md`
- **Update Triggers**: New integrations or API changes
- **Content Requirements**:
  - Setup and configuration steps
  - Authentication and authorization
  - Error handling and logging
  - Performance optimization tips

## 📝 Changelog Management

### **Changelog Standards**
- **Location**: `docs/03-reference/project-history/CHANGELOG.md`
- **Format**: Keep a Changelog 1.2.0 specification
- **Entry Types**:
  - `[Added]` - New features and capabilities
  - `[Changed]` - Breaking changes and modifications
  - `[Deprecated]` - Soon-to-be removed features
  - `[Removed]` - Removed features
  - `[Fixed]` - Bug fixes and patches
  - `[Security]` - Security-related changes

### **Version Numbering**
- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Pre-release Identifiers**: alpha, beta, rc
- **Update Triggers**:
  - Breaking changes → MAJOR version bump
  - New features → MINOR version bump
  - Bug fixes → PATCH version bump

### **Release Process**
```bash
# Pre-release checklist
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Changelog finalized
- [ ] Security audit completed
- [ ] Performance benchmarks verified

# Release commands
git tag -a v1.2.3 -m "Release version 1.2.3"
git push origin v1.2.3
# Update package registries
# Update documentation deployment
```

## 🔄 Documentation Synchronization Workflow

### **Code Change → Documentation Update**
1. **Immediate Recognition**: Identify documentation impact during code review
2. **Documentation Updates**:
   - Update relevant guides and references
   - Update API documentation if applicable
   - Update configuration examples
   - Update troubleshooting guides

3. **Verification Steps**:
   - Cross-reference validation
   - Link checking (internal/external)
   - Build verification (MkDocs --strict)
   - Accessibility testing

### **Automated Synchronization**
- **Git Hooks**: Pre-commit checks for documentation completeness
- **CI/CD Integration**: Documentation build and validation in pipelines
- **Cross-Reference Tools**: Automated link and reference validation
- **Change Detection**: Scripts to identify documentation drift

## 📊 Maintenance Procedures

### **Weekly Documentation Review**
- **Monday Standup**: Review pending documentation updates
- **Documentation Debt**: Identify and prioritize documentation gaps
- **Freshness Checks**: Verify all dates, versions, and examples are current

### **Monthly Documentation Audit**
- **Comprehensive Review**: All documentation files and links
- **User Feedback Integration**: Incorporate user-reported issues
- **Performance Validation**: Ensure documentation loads and searches properly

### **Quarterly Documentation Planning**
- **Content Strategy Review**: Assess documentation effectiveness
- **User Research**: Gather feedback on documentation usability
- **Technology Updates**: Evaluate new documentation tools and approaches

## 🏷️ Documentation Metadata Standards

### **Frontmatter Requirements**
```yaml
---
title: "Clear, descriptive title"
description: "Brief description for SEO and navigation"
tags: ["tag1", "tag2", "tag3"]
last_updated: 2026-01-27
version: 1.2.3
author: "Cline"
status: "active|deprecated|draft"
priority: "critical|high|medium|low"
---
```

### **File Naming Conventions**
- **Kebab-case**: `documentation-maintenance.md`
- **Descriptive Names**: Avoid generic names like `readme.md`
- **Version Suffixes**: `api-v2-specification.md` for versioned content

### **Directory Structure Standards**
```
docs/
├── 01-getting-started/     # User onboarding
├── 02-development/         # Developer guides
├── 03-architecture/        # System design
├── 04-operations/          # Operational procedures
├── 05-governance/          # Project management
└── 06-meta/               # Documentation about documentation
```

## 🔍 Quality Assurance

### **Documentation Metrics**
- **Freshness Score**: Percentage of documentation updated within 90 days
- **Link Health**: Percentage of valid internal/external links
- **Search Effectiveness**: User search success rate
- **User Satisfaction**: Documentation usability ratings

### **Automated Validation**
```bash
# Documentation quality checks
mkdocs build --strict                    # Build validation
linkinator docs/                        # Link checking
lighthouse http://localhost:8000        # Performance/accessibility
grep -r "TODO\|FIXME" docs/             # Incomplete content detection
```

### **Peer Review Standards**
- **Technical Accuracy**: Subject matter expert review
- **Clarity and Readability**: General audience comprehension
- **Completeness**: All edge cases and error conditions covered
- **Consistency**: Adheres to established patterns and standards

## 🚨 Documentation Emergency Procedures

### **Critical Documentation Gaps**
1. **Immediate Assessment**: Evaluate impact and urgency
2. **Temporary Solutions**: Create placeholder content with "Coming Soon"
3. **Priority Escalation**: Add to project dashboard as critical item
4. **Resource Allocation**: Assign dedicated time for completion

### **Documentation Data Loss**
1. **Recovery Priority**: Documentation = Code priority
2. **Backup Restoration**: Use timestamped backups
3. **Version Control Recovery**: Git history reconstruction
4. **Stakeholder Communication**: Transparent incident communication

### **Breaking Changes Without Documentation**
1. **Immediate Halt**: Stop deployment until documentation is ready
2. **Rollback Plan**: Ability to revert if documentation cannot be completed
3. **Exception Process**: Executive approval for emergency deployments
4. **Post-Mortem**: Documentation of why the process failed

## 🛠️ The State Snapshot Protocol (v2.0.5 Standard)

Every significant task completion MUST be finalized with a `<state_snapshot>` update in the agent's thought process or scratchpad. This snapshot serves as the authoritative source for `CHANGELOG.md` and `memory_bank/progress.md`.

### **Snapshot Structure:**
- **overall_goal**: The current high-level objective.
- **key_knowledge**: New technical discoveries, "gotchas", or optimized patterns (source for EKB).
- **file_system_state**: Atomic list of MODIFIED, CREATED, or DELETED files.
- **recent_actions**: High-fidelity log of technical steps taken (the "How").
- **current_plan**: Remaining TODOs for the current phase.

### **Synchronization Workflow:**
1.  **Extract**: Pull `recent_actions` and `key_knowledge` from the final snapshot of a session.
2.  **Translate**: Convert technical actions into human-readable entries for `CHANGELOG.md`.
3.  **Audit**: Cross-reference `file_system_state` against the changelog to ensure no "phantom" entries.
4.  **Promote**: Identify `key_knowledge` items that warrant a new entry in `expert-knowledge/`.

## 📈 Success Metrics

### **Documentation Health Indicators**
- ✅ **Update Frequency**: >90% of docs updated within 30 days of code changes
- ✅ **Link Validity**: >99% of internal links working
- ✅ **Search Success**: >85% of user searches return relevant results
- ✅ **User Feedback**: >4.5/5 documentation satisfaction rating

### **Process Compliance**
- ✅ **Tracker Updates**: 100% of active tasks have current progress
- ✅ **Changelog Maintenance**: All releases have complete changelog entries
- ✅ **Review Completion**: 100% of documentation changes reviewed
- ✅ **Automation Coverage**: >80% of documentation validation automated

## 🛠️ Tools and Automation

### **Documentation Generation**
- **API Docs**: Automated from code comments and schemas
- **Dependency Diagrams**: Generated from code analysis
- **Performance Reports**: Automated benchmark documentation
- **Security Reports**: Automated compliance documentation

### **Quality Assurance Tools**
- **MkDocs Strict Mode**: Build-time validation
- **Link Checkers**: Automated link validation
- **Accessibility Scanners**: WCAG compliance verification
- **Search Analytics**: User search behavior analysis

### **Integration Points**
- **Git Hooks**: Pre-commit documentation validation
- **CI/CD Pipelines**: Automated documentation deployment
- **Monitoring Systems**: Documentation health dashboards
- **Feedback Systems**: User documentation improvement suggestions