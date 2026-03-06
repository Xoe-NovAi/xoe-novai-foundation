# MkDocs Commands Quick Reference

## 🎯 Most Used Commands

### Start Local Documentation Server
```bash
# For internal team documentation (PRIMARY - port 8001)
make mkdocs-serve

# For public GitHub pages documentation (port 8000)
make mkdocs-serve-public
```

**Then open browser:**
- Internal: `http://localhost:8001`
- Public: `http://localhost:8000`

### Build Documentation for Deployment
```bash
# Build both public and internal
make mkdocs-build

# Build just public docs
make docs-public

# Build just internal docs
make docs-internal
```

### Check Documentation System Status
```bash
make docs-system
```

Shows:
- Number of markdown files in each system
- Whether build artifacts exist
- Quick links to config files
- Available commands summary

## 📚 Full Documentation System

### Directory Structure
```
docs/                           # Public documentation (GitHub Pages)
├── mkdocs.yml                 # Public config
└── *.md                        # Public content

internal_docs/                  # Internal team documentation
├── mkdocs-internal.yml         # Internal config
├── 00-system/                  # System & navigation
├── 01-strategic-planning/      # PILLARS, roadmaps
├── 02-research-lab/            # Research sessions
├── 03-infrastructure-ops/      # Deployment, infrastructure
├── 04-code-quality/            # Audits, security
├── 05-client-projects/         # (Template for future)
├── 06-team-knowledge/          # (Template for future)
└── 07-archives/                # Historical records
```

### Build Outputs
```
site/                           # Public docs build (deployed to GitHub Pages)
site-internal/                  # Internal docs build (for team-only access)
```

## 🔧 Makefile Targets (All Available)

### MkDocs Building
| Command | Purpose |
|---------|---------|
| `make mkdocs-build` | Build both public and internal |
| `make docs-public` | Build public only |
| `make docs-internal` | Build internal only |
| `make docs-all` | Alias for mkdocs-build |
| `make mkdocs-clean` | Remove all build artifacts |

### MkDocs Serving (Development)
| Command | Purpose | Port |
|---------|---------|------|
| `make mkdocs-serve` | Serve internal docs | 8001 |
| `make mkdocs-serve-internal` | Serve internal docs | 8001 |
| `make mkdocs-serve-public` | Serve public docs | 8000 |

### System Information
| Command | Purpose |
|---------|---------|
| `make docs-system` | Show documentation system status |

## 📖 Where to Find Things

### Strategic Documents
- [PILLAR-1: Operational Stability](../internal_docs/01-strategic-planning/PILLAR-1-OPERATIONAL-STABILITY.md)
- [PILLAR-2: Scholar Differentiation](../internal_docs/01-strategic-planning/PILLAR-2-SCHOLAR-DIFFERENTIATION.md)
- [PILLAR-3: Modular Excellence](../internal_docs/01-strategic-planning/PILLAR-3-MODULAR-EXCELLENCE.md)

### Research Documents
- [RESEARCH-P0: Critical Path](../internal_docs/02-research-lab/RESEARCH-P0-CRITICAL-PATH.md)
- [RESEARCH-P1: (Extract template)](../internal_docs/02-research-lab/RESEARCH-P1-TEMPLATE.md)
- [RESEARCH-P2: (Extract template)](../internal_docs/02-research-lab/RESEARCH-P2-TEMPLATE.md)
- [RESEARCH-P3: (Extract template)](../internal_docs/02-research-lab/RESEARCH-P3-TEMPLATE.md)

### System Documentation
- [Documentation System Strategy](../internal_docs/00-system/DOCUMENTATION-SYSTEM-STRATEGY.md)
- [Genealogy Tracking](../internal_docs/00-system/GENEALOGY.md)
- [Handoff to Claude AI](../internal_docs/00-system/HANDOFF-TO-CLAUDE-AI.md)

### Code & Infrastructure
- [Internal Docs Index](../internal_docs/index.md) - Full navigation
- [Codebase Audit](../internal_docs/03-infrastructure-ops/) - Latest analysis
- [Security Audit](../internal_docs/04-code-quality/) - Security findings

## 🚀 CI/CD Integration

### Deployment Build
```bash
# Build both for deployment
make mkdocs-build

# Outputs:
# - site/           → Deploy to GitHub Pages (public)
# - site-internal/  → Deploy to internal server (private)
```

### GitHub Actions (Example)
```yaml
- name: Build documentation
  run: make mkdocs-build

- name: Deploy public docs
  run: # Deploy site/ to GitHub Pages

- name: Deploy internal docs
  run: # Deploy site-internal/ to internal server
```

## 🔍 Search & Navigation

Both documentation systems have:
- **Full-text search** - Search 349+ markdown files instantly
- **Navigation sidebar** - Organized by topic
- **Cross-references** - Links between PILLAR and RESEARCH docs
- **Mobile-friendly** - Works on all devices

### Finding Information Quickly
1. **Use search** (top right 🔍)
2. **Browse sidebar** (left navigation)
3. **Check index pages** for each section (e.g., `01-strategic-planning/INDEX.md`)
4. **Follow cross-references** between related docs

## 💡 Tips & Tricks

### Local Development
```bash
# Start internal docs and keep terminal alive
make mkdocs-serve

# In another terminal, edit docs
# Changes auto-reload in browser (watch for file changes)

# When done, press Ctrl+C to stop server
```

### Before Committing
```bash
# Always rebuild locally to catch errors
make mkdocs-build

# Check no errors were printed
# If errors, fix before committing
```

### Clean Build
```bash
# Sometimes needed if build artifacts are stale
make mkdocs-clean
make mkdocs-build
```

## 🔗 Related Documentation

- **MkDocs Official**: https://www.mkdocs.org/
- **Material Theme**: https://squidfunk.github.io/mkdocs-material/
- **Internal Docs**: Internal KB at `http://localhost:8001`
- **Makefile**: Full Makefile at workspace root with all targets

## 📝 Contributing to Documentation

### Adding New Pages
1. Create `.md` file in appropriate section
2. Add entry to `mkdocs.yml` or `mkdocs-internal.yml` navigation
3. Use relative links: `[Link text](../other-file.md)`
4. Test locally: `make mkdocs-serve`
5. Commit and push

### Updating PILLAR/RESEARCH Docs
- Edit files in `internal_docs/01-strategic-planning/` or `02-research-lab/`
- These are tracked in Git (not build artifacts)
- Build updates `mkdocs-internal.yml` nav if changed
- Always rebuild and test: `make mkdocs-build`

### Linking Between Systems
- From public docs: Don't link to internal docs
- From internal docs: Can reference PILLAR/RESEARCH docs
- Use absolute paths in `mkdocs.yml` nav entries

## ⚙️ Configuration Files

### Public Configuration (`mkdocs.yml`)
- Defines navigation for `docs/` folder
- Builds to `site/`
- Deployed to GitHub Pages

### Internal Configuration (`mkdocs-internal.yml`)
- Defines navigation for `internal_docs/` folder
- Builds to `site-internal/`
- For team-only access

Both use Material theme with:
- Dark/light mode toggle
- Search functionality
- Code highlighting
- Keyboard shortcuts

## 🆘 Troubleshooting

### "mkdocs command not found"
```bash
# Install package
pip install mkdocs mkdocs-material
```

### Build fails with errors
```bash
# Clean and rebuild
make mkdocs-clean
make mkdocs-build

# Check for broken links or syntax errors
# Fix errors in markdown files
```

### Port already in use (8001 or 8000)
```bash
# Kill existing process on port
lsof -i :8001  # Find process ID
kill -9 <PID>

# Then restart
make mkdocs-serve
```

### Can't find a file in search
```bash
# Rebuild with fresh search index
make mkdocs-clean
make mkdocs-build
```

## 📞 Support & Questions

- **Internal KB**: `http://localhost:8001` (when running `make mkdocs-serve`)
- **Strategy docs**: See `internal_docs/00-system/DOCUMENTATION-SYSTEM-STRATEGY.md`
- **Handoff guide**: See `internal_docs/00-system/HANDOFF-TO-CLAUDE-AI.md`
- **Genealogy**: See `internal_docs/00-system/GENEALOGY.md`

---

**Last Updated**: 2026-02-12
**Status**: ✅ Production Ready
**Dual-Build System**: Public (GitHub Pages) + Internal (Team KB)
