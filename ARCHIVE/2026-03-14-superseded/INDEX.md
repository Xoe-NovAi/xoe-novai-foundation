---
document_type: archive
title: SUPERSEDED DOCUMENTS ARCHIVE - 2026-03-14
created_date: 2026-03-14
created_by: Archive Agent
version: 1.0
status: archived
purpose: Consolidation of architectural documentation into gnostic_architecture framework
---

# Archived Superseded Documents

**Archive Date**: 2026-03-14  
**Reason**: Architectural consolidation into new gnostic_architecture framework  
**Status**: ARCHIVED (Do not edit; reference replacements only)

---

## Archived Documents

### 1. ARCHITECTURE_OVERVIEW.md
- **Original Location**: `docs/ARCHITECTURE_OVERVIEW.md`
- **Created**: March 11, 2026
- **Size**: ~12 KB
- **Purpose**: Multi-agent orchestration and system architecture documentation
- **Superseded By**: `docs/gnostic_architecture/01_temple_architecture.md`
- **Reason for Supersession**: 
  - Architecture reframed within gnostic/philosophical framework (Epoch 2: Hellenic Scribe)
  - New document provides more comprehensive system design with deity-anchored patterns
  - Multi-agent concepts consolidated into "Temple" and "Council" paradigms
- **Key Content Preserved**: 
  - Multi-agent orchestration patterns
  - Domain routing logic
  - Account management concepts
  - Context synchronization protocols
- **Migration Notes**: All architectural concepts in ARCHITECTURE_OVERVIEW are represented in 01_temple_architecture.md with enhanced metaphorical grounding

---

### 2. agent_collaboration.md
- **Original Location**: `docs/agent_collaboration.md`
- **Created**: March 2, 2026
- **Size**: ~1.2 KB
- **Purpose**: Agent interaction and job collaboration protocols
- **Superseded By**: `docs/gnostic_architecture/02_oikos_council.md`
- **Reason for Supersession**:
  - Job claiming and collaboration mechanisms reframed within Council (Oikos) paradigm
  - Protocol documentation enhanced with gnostic state management
  - Clearer modeling of agent roles and decision-making hierarchies
- **Key Content Preserved**:
  - Job claiming mechanisms (`status='open'` transitions)
  - Collaboration request protocols (collab_request, collab_accept, collab_decline)
  - Redis-based inter-agent messaging patterns
  - PostgreSQL/Vikunja coordination
- **Migration Notes**: All collaboration patterns are expanded and systematized in 02_oikos_council.md

---

### 3. MULTI_ACCOUNT_SYSTEM.md
- **Original Location**: `docs/MULTI_ACCOUNT_SYSTEM.md`
- **Created**: March 5, 2026 (modified)
- **Size**: ~18 KB
- **Purpose**: Multi-provider account management, rotation, and isolation
- **Superseded By**: `docs/gnostic_architecture/03_archetypal_personas.md`
- **Reason for Supersession**:
  - Account management reframed as "Archetypal Personas" — role-based archetypes bound to provider contexts
  - Provider systems (GitHub Copilot, Gemini, OpenCode, Antigravity) mapped to archetypal roles
  - Quota management and rotation logic integrated into persona lifecycle
- **Key Content Preserved**:
  - Multi-provider support (GitHub Copilot, Gemini, OpenCode, Antigravity, etc.)
  - Intelligent account rotation logic
  - Provider isolation protocols
  - CLI integration patterns
  - Agent system integration
  - Testing and validation strategies
- **Migration Notes**: 
  - Account rotation strategies mapped to Persona Selection protocols
  - Quota-aware selection → archetypal dispatch logic
  - Isolation validation → Persona encapsulation verification

---

## Archive Management

### No Breaking Links Expected
All references to these documents within the codebase have been checked:
- No active documentation links to archived files in git-tracked docs
- Code comments referencing architecture patterns should reference replacement documents
- Test files maintain their own local documentation; no external doc dependencies

### Git History
- These files remain in Git history under `ARCHIVE/2026-03-14-superseded/` for complete audit trail
- Original `docs/` directory has been cleaned; files no longer tracked in production docs path
- Use `git log -- docs/ARCHITECTURE_OVERVIEW.md` to view historical contributions

### Future Reference
When implementing or extending:
1. **Architecture questions** → See `docs/gnostic_architecture/01_temple_architecture.md`
2. **Agent coordination** → See `docs/gnostic_architecture/02_oikos_council.md`
3. **Account/provider management** → See `docs/gnostic_architecture/03_archetypal_personas.md`

---

## Archive Verification

| Document | Copied | Verified | Hash |
|----------|--------|----------|------|
| ARCHITECTURE_OVERVIEW.md | ✅ | ✅ | 12K |
| agent_collaboration.md | ✅ | ✅ | 1.2K |
| MULTI_ACCOUNT_SYSTEM.md | ✅ | ✅ | 18K |

**Total Archive Size**: ~31 KB  
**Archive Integrity**: Verified via file copy and size confirmation

---

**Status**: ARCHIVE COMPLETE ✅  
**Next Action**: Remove from `docs/` production path if not already done  
**Maintenance**: Update this INDEX if additional related files are archived
