---
priority: medium
context: documentation
activation: conditional
last_updated: 2026-02-17
version: 2.0
---

# Documentation Standards (MkDocs)

## Core Setup
- **mkdocs**: 1.6.1 (LTS validation)
- **mkdocs-material**: 10.0.2 (final feature release)
- **Base**: python:3.12-slim, non-root user (1001)
- **Mirror**: Tsinghua pip (pypi.tuna.tsinghua.edu.cn/simple)

## Theme Configuration
```yaml
theme:
  name: material
  features:
    - navigation.instant
    - navigation.tabs.sticky
    - navigation.sections
    - navigation.expand
    - search.suggest
    - search.highlight
    - content.code.copy
    - toc.integrate
```

## Required Plugins
| Plugin | Version | Purpose |
|--------|---------|---------|
| search | built-in | Prebuild index for <50ms |
| build_cache | latest | 80% faster incremental |
| gen-files | 0.6.1 | Automated API docs |
| literate-nav | 0.6.2 | SUMMARY.md navigation |
| glightbox | 0.5.2 | Image zoom |
| minify | 0.8.0 | 40-60% size reduction |

## Validation (mkdocs.yml)
```yaml
validation:
  nav:
    omitted_files: warn
    not_found: warn
  links:
    not_found: warn
    absolute_links: relative_to_docs
    anchors: warn
```

## Diátaxis Structure
5 domains × 4 quadrants:
- **Tutorials**: Learning-oriented
- **How-to**: Problem-oriented
- **Reference**: Information-oriented
- **Explanation**: Understanding-oriented

## Build Commands
```bash
# Development
mkdocs serve --dev-addr=0.0.0.0:8000 --livereload

# Production (strict)
mkdocs build --clean --strict

# Output to writable location
mkdocs build --site-dir /tmp/docs-site
```

## Performance Targets
- Clean build: <15s
- Warm build (cached): <5s
- Search: <50ms via prebuild_index

## Permissions Fix
```bash
# Fix ownership for rootless Podman
podman unshare chown -R 1001:1001 docs/

# Verify inside container
ls -la /workspace/docs/
```

## Deployment
```yaml
# podman-compose
services:
  mkdocs:
    image: xnai-mkdocs:latest
    ports:
      - "8000:8000"
    volumes:
      - ./docs:/workspace/docs:Z,U
    userns_mode: keep-id
    restart: unless-stopped
```

## Accessibility (WCAG 2.2 AA)
- Light/dark auto-switch (`prefers-color-scheme`)
- ARIA labels, keyboard nav
- Focus indicators, semantic HTML5
- Color contrast verification
- Lighthouse 95+ score

## Troubleshooting
| Issue | Resolution |
|-------|------------|
| Permission denied | `podman unshare chown -R 1001:1001 docs/` |
| Build warnings | Check strict mode output |
| Search slow | Enable `prebuild_index: true` |
| Links broken | Run `linkinator` validation |
