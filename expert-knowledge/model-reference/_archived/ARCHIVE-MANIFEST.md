---
title: Model Reference Archive Manifest
version: 1.0.0
last_updated: 2026-02-17
status: active
---

# Model Reference Archive Manifest

**Date**: 2026-02-17  
**Archive Location**: `expert-knowledge/model-reference/_archived/`  

---

## Archived Documents

### 1. opencode-models-breakdown-v1.0.0.md.archived

**Original Date**: 2026-02-13  
**Archive Date**: 2026-02-17  
**Reason**: Superseded by comprehensive new models documentation  

**Status**: Obsolete → Use these instead:
- `expert-knowledge/model-reference/opencode-free-models-v1.0.0.md` (comprehensive reference)
- `expert-knowledge/model-reference/cli-model-selection-strategy-v1.0.0.md` (unified strategy)

**Improvements in New Version**:
- ✅ Added detailed capability matrices
- ✅ Added recommended use cases per model
- ✅ Added XNAi integration examples
- ✅ Added cost analysis
- ✅ Added Ma'at alignment

**Retention Policy**: Keep as historical reference for 6 months, then delete (2026-08-17).

---

## New Model Reference Documents (2026-02-17)

| Document | Lines | Focus | Scope |
|----------|-------|-------|-------|
| `opencode-free-models-v1.0.0.md` | 467 | 5 OpenCode models | Comprehensive |
| `cline-cli-models-v1.0.0.md` | 509 | 9 Cline IDE models | Comprehensive |
| `copilot-cli-models-v1.0.0.md` | 639 | 12+ Copilot CLI models | Comprehensive |
| `cli-model-selection-strategy-v1.0.0.md` | 624 | Unified selection | Cross-CLI |

**Total New Content**: 2,239 lines of model reference documentation

---

## Archive Retention Policy

**Keep Archived Docs**:
- 6 months as historical reference
- For understanding evolution of model availability
- For comparing old vs new model recommendations

**Delete Archived Docs After**:
- 2026-08-17 (6 months post-archival)
- Or when newer major version released
- With explicit approval from team

---

## Migration Notes for Team

### If You Were Using Old opencode-models-breakdown-v1.0.0.md:

1. **For OpenCode models info**: Go to `opencode-free-models-v1.0.0.md`
2. **For general model selection**: Go to `cli-model-selection-strategy-v1.0.0.md`
3. **For Cline/Copilot models**: Go to respective CLI-specific docs

### Update All References:

**Old**:
```markdown
See `expert-knowledge/model-reference/opencode-models-breakdown-v1.0.0.md`
```

**New**:
```markdown
See `expert-knowledge/model-reference/opencode-free-models-v1.0.0.md`
```

---

## Archive Manifest Update Schedule

- **Weekly**: Check for newly outdated docs (Fridays)
- **Monthly**: Consolidate and reorganize archived docs (1st of month)
- **Quarterly**: Review retention policies (Q1/Q2/Q3/Q4)

---

**Archive Curator**: Copilot CLI  
**Last Checked**: 2026-02-17  
**Next Review**: 2026-02-24
