
---
priority: medium
context: documentation
activation: conditional
last_updated: 2026-01-27
version: 1.0
---

# MkDocs Best Practices

**Core Setup (2026 Standards)**:
- Lock to mkdocs==1.6.1 (granular validation LTS) and mkdocs-material==10.0.2 (final feature release; maintenance mode with bug fixes only—monitor Zensical successor for Rust-based modular future).
- Base: python:3.12-slim, non-root user mkdocs:1001, Tsinghua pip mirror for all installs (https://pypi.tuna.tsinghua.edu.cn/simple).
- Theme: Material with auto light/dark (prefers-color-scheme), WCAG 2.2 AA compliance (ARIA labels, keyboard nav, focus indicators, semantic HTML5, color contrast; verify Lighthouse 95+).
- Features: navigation.instant/progress/tracking/tabs/sticky/sections/expand/indexes/top/path; search.suggest/highlight/share; content.code.copy/annotate/tabs.link/tooltips; toc.integrate/follow.
- Plugins (exact versions from requirements-docs.txt):
  - search: {prebuild_index: true}  # Large sites (569+ files)
  - build_cache: {enabled: true, cache_dir: .cache/mkdocs}  # 80% faster incremental
  - gen-files (0.6.1): Automated API docs via scripts/generate_api_docs.py
  - literate-nav (0.6.2): From SUMMARY.md, implicit_index: true
  - section-index (0.3.10)
  - glightbox (0.5.2): Mobile touch, zoom, auto_caption
  - minify (0.8.0): HTML/JS/CSS (40-60% reduction)
  - git-revision-date-localized (1.5.0): timeago, creation_date, fallback_to_build_date
  - rss (1.2.0)
- Markdown: admonition, pymdownx.highlight/superfences/tabbed/tasklist/details, attr_list, meta (frontmatter), toc permalink.
- Validation (mkdocs.yml): nav omitted_files/not_found/absolute_links: warn; links not_found/absolute_links (relative_to_docs)/anchors/unrecognized_links: warn. Use --strict in CI.
- Build: `mkdocs build --clean --strict` (<15s clean, <5s warm via cache). Target /tmp/docs-site for container-writable output.
- Serve: `mkdocs serve --dev-addr=0.0.0.0:8000 --livereload` (dev); static + nginx/Caddy (prod, offline).
- Search: Prebuild_index for <50ms; hybrid BM25 + FAISS-CPU optional.
- Ryzen Optimizations: BuildKit cache mounts, concurrent workers where possible.

**Diátaxis Structure**:
- 5 domains × 4 quadrants + Research Hub/System Prompts (e.g., Tutorials/How-to/Reference/Explanation).
- Use index.md sections; frontmatter (python-frontmatter>=1.1.0) for domain/quadrant/confidence/tags/dependencies (preserve existing).
- Navigation: Nested tabs/sections; breadcrumb; auto-expand current.

**Migration & Maintenance**:
- Atomic: Timestamped backups, dry-runs, checksums, rollback. classify_content_robust.py with frontmatter-aware preservation.
- Classification: Keyword heuristics; manual for low-confidence; debug logging/single-file tests.
- Validation: Post-migration linkinator/Lighthouse; >95% frontmatter compliance.
- Permissions: Rootless Podman volumes ./docs:/workspace/docs:Z,U (after podman unshare chown). Containerize all installs.
- Deployment: podman-compose with custom bridge network; ports 8000:8000; restart unless-stopped.
- Maintenance: Monthly dep updates/link checks; quarterly benchmarks; annual WCAG audit.

**Troubleshooting**:
- Permissions: podman unshare chown -R 1001:1001 docs/; verify inside container.
- Builds: Check cache; review warnings (strict mode); fix encoding/links.
- Search: Ensure prebuild_index; test suggestions.
- Material: No new features post-10.0; prepare Zensical migration.

**Example mkdocs.yml snippet**:
```yaml
theme:
  features:
    - navigation.instant
    - navigation.tabs.sticky
    - search.suggest
plugins:
  - search: {prebuild_index: true}
  - build_cache: {enabled: true}
  - minify: {minify_html: true}
validation:
  links: {absolute_links: relative_to_docs, anchors: warn}
```
