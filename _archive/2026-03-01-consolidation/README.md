# Archive Index - March 2026 Consolidation

This archive contains consolidated historical files from the Xoe-NovAi Omega Stack project.

## Directory Structure

```
_archive/
└── 2026-03-01-consolidation/
    ├── by_source/          # Organized by original source location
    │   ├── memory_bank/
    │   │   ├── handovers/ # Session handovers (Feb 2026)
    │   │   └── research/  # Research job files
    │   ├── docs/          # Old docs (tutorials, explanation, diagrams)
    │   ├── session-states/ # Session state archives
    │   └── plans/         # Obsolete plans (AWQ removal)
    └── by_date/           # Chronological archives
        ├── 2026-02-11_deprecated/
        ├── 2026-02-14_consolidated/
        └── root-cleanup-2026-02-26/
```

## Origin Mapping

| Original Location | Archive Location |
|-------------------|------------------|
| `memory_bank/recall/handovers/*` | `by_source/memory_bank/handovers/` |
| `memory_bank/research/RJ-*` | `by_source/memory_bank/research/` |
| `session-state-archives/` | `by_source/session-states/` |
| `_archive/` (root) | `by_date/` |
| `docs/_archive/` | `by_source/docs/` (not yet merged) |

## Consolidation Date
2026-03-01

## Notes
- All files moved to preserve history while cleaning up active directories
- Duplicate files between `handovers/` and `handovers_consolidated/` resolved
- AWQ-related files moved to archive (AWQ removed from stack)

---
**Last Updated**: 2026-03-01
