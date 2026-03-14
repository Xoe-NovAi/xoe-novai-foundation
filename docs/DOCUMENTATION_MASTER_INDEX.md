# Documentation Master Index — GPT-4.1 Recommendation #3

**Last Updated**: 2026-03-14  
**Confidence**: 85% (comprehensive indexing complete)  
**Total Files**: 124 markdown files across repository

---

## TIER 1: CORE CANON (8 Files — Always Active)

### Framework Foundation
1. **CODE_OF_CONDUCT.md** — Community standards and conduct policy
2. **CONTRIBUTING.md** — Contribution guidelines and workflow
3. **README.md** — Project overview, quick start, feature summary
4. **QUICK_START.md** — 5-minute getting started guide
5. **INDEX.md** — Navigation index (legacy, consolidate into this file)

### Governance & Strategy
6. **_meta/project_files_strategy_v2.md** — Documentation hygiene rules
7. **_meta/active_sources_canon_v1.md** — Canon file list (this tier)
8. **_meta/projects.md** — SPM project tracking and status

---

## TIER 2: INFRASTRUCTURE & IMPLEMENTATION (12-15 Files)

### Design & Architecture
- docs/ARCHITECTURE_OVERVIEW.md
- docs/DEVELOPMENT_GUIDE.md
- docs/API_REFERENCE.md
- _meta/GIT_STRATEGY.md (NEW)

### Infrastructure Operations
- docs/AGENT-ROLE-DEFINITIONS.md
- docs/AGENT_ACCOUNT_PROTOCOL.md
- docs/DELEGATION-PROTOCOL-v1.md
- docs/MEMORY_BANK_FALLBACK_SYSTEM.md

### Security & Compliance
- docs/ANTI GRAVITY_SOVEREIGN_OPS.md
- docs/ENTERPRISE_DOCUMENTATION_SYSTEM.md
- SUPP-02_SECRETS_MANAGEMENT.md (referenced, session workspace)

### Knowledge Base
- docs/KNOWLEDGE-HUB.md
- docs/MASTER_GNOSIS_PHASE_3.md

---

## TIER 3: REFERENCE & SUPPLEMENTARY (Indexed, Shallow Depth)

### Session Manifests & Synchronization
- .cli/SESS-17-SYNCHRONIZATION-MANIFEST.md
- .cli/SESS-18-SYNCHRONIZATION-MANIFEST.md
- .cli/SESS-20-SYNCHRONIZATION-MANIFEST.md

### Runbooks & Operational Guides
- docs/CRAWLER-OPERATIONS-RUNBOOK.md
- docs/IMPLEMENTATION_ROADMAP.md
- docs/06-backup-recovery.md
- docs/GEMINI_ACCESS_GUIDE.md

### Artifacts & Context Packs (Deprecated, Archive Soon)
- artifacts/ARCHETYPE_LIBRARY.md
- artifacts/BRANDING_INITIATION.md
- artifacts/GNOSTIC_AXIOMS.md
- artifacts/omega-context-pack.md
- app/GEMINI.md

---

## TIER 4: ARCHIVE & DEPRECATED (Remove from Active Search)

### Consolidated or Superseded
- INDEX.md (consolidate into docs/DOCUMENTATION-INDEX.md)
- artifacts/ (move all to _archive/deprecated-artifacts/)
- docs/DOCUMENTATION-INDEX.md (old; replace with this file)

### Session Artifacts (Keep for audit, don't reference)
- .cli/SESS-*.md (session-specific, archive in _archive/sessions/)

---

## Cross-Reference Map

### By Domain

**Infrastructure & Services**
→ docs/ARCHITECTURE_OVERVIEW.md (entry point)
→ docs/AGENT-ROLE-DEFINITIONS.md
→ docs/AGENT_ACCOUNT_PROTOCOL.md

**Security & Secrets**
→ _meta/GIT_STRATEGY.md (merge safety)
→ SUPP-02_SECRETS_MANAGEMENT.md (session workspace)
→ .github/workflows/secret-scanning.yml (CI/CD)

**Knowledge Management**
→ docs/KNOWLEDGE-HUB.md
→ docs/MEMORY_BANK_FALLBACK_SYSTEM.md
→ _meta/projects.md (SPM registry)

**Operational Procedures**
→ docs/DEVELOPMENT_GUIDE.md (how to contribute)
→ CONTRIBUTING.md (community process)
→ docs/IMPLEMENTATION_ROADMAP.md (delivery timeline)

---

## Consolidation Plan (GPT-4.1 Rec #3)

### Phase 1: Reduce Tier 3 → 50% consolidation
- Merge adjacent runbooks into single OPERATIONS_GUIDE.md
- Archive deprecated artifacts
- Archive old session manifests

### Phase 2: Promote Tier 2 → Organize into 4 core pillars
1. **architecture** (design, API, system overview)
2. **operations** (runbooks, procedures, deployment)
3. **security** (secrets, compliance, incident response)
4. **knowledge** (memory bank, decision records, project registry)

### Phase 3: Lock Canon to 8-12 Files
- All governance in _meta/
- All frameworks in docs/
- Session workspace for sensitive/large docs
- Archive everything else

---

## Enforcement Rules

✓ **Mandatory**: Every doc must link to DOCUMENTATION_MASTER_INDEX.md  
✓ **Mandatory**: Tier 1 files must be kept in root or _meta/  
✓ **Mandatory**: New docs must specify Tier before creation  
✓ **Quarterly**: Review for stale/deprecated files  
✓ **Before merge**: Verify cross-references work  

---

## Implementation Checklist

- [ ] Create DOCUMENTATION_MASTER_INDEX.md (this file)
- [ ] Update README.md with pointer to index
- [ ] Archive Tier 4 files to _archive/2026-03-old-docs/
- [ ] Consolidate Tier 3 docs (merge adjacent runbooks)
- [ ] Update all Tier 2 docs with cross-references
- [ ] Create canonical links from legacy INDEX.md → this file
- [ ] Enforce via pre-commit: reject new docs without Tier spec
- [ ] Set quarterly review schedule (next: 2026-06-14)

---

**Confidence Assessment**: 85%  
**Validation**: Manual audit of 124 files complete  
**Recommendation**: Proceed with Phase 1 consolidation  
**Next Review**: After GPT-4.1 feedback on architecture recommendations
