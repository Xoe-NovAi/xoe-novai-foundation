# 00-system: System & Navigation

This directory contains foundational system documentation, genealogy, strategy, and navigation guides for the entire documentation system.

## Contents

### Core System Documentation
- **GENEALOGY.md** - Complete lineage tracking of all 15 meta files consolidated into this structure
- **GENEALOGY-TRACKER.yaml** - Machine-readable genealogy metadata with timestamps
- **INDEX.md** - Quick navigation index organized by use case

### Strategic Configuration
- **DOCUMENTATION-SYSTEM-STRATEGY.md** - 9-part comprehensive strategy document covering:
  - Problem statement (documentation fragmentation)
  - Solution architecture (dual-build MkDocs)
  - Directory structure consolidation
  - MkDocs design patterns
  - PILLAR & RESEARCH document integration
  - Memory bank organization
  - Implementation checklist
  - Success criteria

- **HANDOFF-TO-CLAUDE-AI.md** - Research phase extraction template with:
  - P1/P2/P3 research framework
  - Session structure and success criteria
  - Git workflow and quality standards
  - Integration with PILLAR documents

- **DOCUMENTATION-CONSOLIDATION-COMPLETE.md** - Project completion and onboarding:
  - Statistics and metrics
  - Technical implementation details
  - Features enabled by consolidation
  - Architecture diagrams
  - How-to guide for maintenance

## Navigation Quick Links

**For Documentation Users:**
- New to the system? Start at [INDEX.md](INDEX.md) for navigation by role
- Want the full story? See [GENEALOGY.md](GENEALOGY.md) for complete file lineage
- Building/updating docs? Check [DOCUMENTATION-SYSTEM-STRATEGY.md](DOCUMENTATION-SYSTEM-STRATEGY.md)

**For Researchers:**
- Need research phase template? See [HANDOFF-TO-CLAUDE-AI.md](HANDOFF-TO-CLAUDE-AI.md)
- Phase 0 foundation already complete - See [01-strategic-planning/RESEARCH-P0-CRITICAL-PATH.md](../01-strategic-planning/RESEARCH-P0-CRITICAL-PATH.md)

**For Infrastructure/DevOps:**
- Check Makefile targets: `make docs-system` shows current status
- Commands: See [memory_bank/mkdocs-commands.md](../../memory_bank/mkdocs-commands.md)
- Deployment: MkDocs builds automatically on CI/CD

## Quick Start

### Explore the Documentation
```bash
# Start internal KB locally
make mkdocs-serve

# Open browser to http://localhost:8001
```

### Understanding the Structure
- This directory (00-system) contains navigation and strategy
- See [INDEX.md](INDEX.md) for role-based navigation
- PILLAR documents are in [01-strategic-planning/](../01-strategic-planning/)
- Research sessions are in [02-research-lab/](../02-research-lab/)

### Key Metrics
- **Total markdown files**: 349 across all sections
- **Organization**: 8-level hierarchy
- **Search capability**: Full-text search across all files
- **Build time**: ~25 seconds both builds combined
- **Update frequency**: Real-time on file changes (watching enabled)

## Architecture Overview

```
Documentation System (Dual-Build)
├── Public Build
│   ├── Source: docs/
│   ├── Config: mkdocs.yml
│   ├── Output: site/
│   └── Access: GitHub Pages + port 8000
│
└── Internal Build
    ├── Source: internal_docs/ (THIS DIRECTORY)
    ├── Config: mkdocs-internal.yml
    ├── Output: site-internal/
    └── Access: Team-only + port 8001
```

## Contributing to Documentation

### Adding New Pages
1. Create `.md` file in appropriate section
2. Add entry to `mkdocs-internal.yml` navigation
3. Use relative links: `[Link text](../01-strategic-planning/some-file.md)`
4. Test locally: `make mkdocs-serve`
5. Commit and push

### Updating This Section
- Modify `.md` files in this directory
- Changes auto-reload when serving: `make mkdocs-serve`
- Update navigation in `mkdocs-internal.yml` if adding new pages

## Related Sections

- **[01-strategic-planning/](../01-strategic-planning/)** - PILLAR documents and strategic roadmaps
- **[02-research-lab/](../02-research-lab/)** - Research sessions and templates
- **[03-infrastructure-ops/](../03-infrastructure-ops/)** - Deployment and operational documentation
- **[04-code-quality/](../04-code-quality/)** - Code audits, security findings, implementation guides

## Contact & Questions

- See **DOCUMENTATION-SYSTEM-STRATEGY.md** for comprehensive strategy
- See **memory_bank/mkdocs-commands.md** for all available commands
- See **activeContext.md** in memory_bank for current system status

---

**Status**: ✅ Production Ready  
**Last Updated**: 2026-02-12  
**Markdown Files in Section**: 6  
**Part of**: Internal Documentation System (349 total files)
