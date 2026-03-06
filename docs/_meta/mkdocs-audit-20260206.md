# MkDocs Documentation Audit — February 6, 2026

## Executive Summary

Comprehensive audit of Xoe-NovAi Foundation documentation structure and MkDocs configuration for optimal performance and maintainability.

**Auditor**: Cline-Trinity (IDE-integrated engineer)
**Date**: 2026-02-06
**Scope**: Full docs/ structure, mkdocs.yml configuration, cross-references

---

## 1. Critical Issues Found

### 1.1 🚨 Expert Knowledge Path Mismatch
**Issue**: `expert-knowledge/` is at repository root, not in `docs/`
**Impact**: Files referenced in nav but not accessible to MkDocs build
**Files Affected**: All files in `expert-knowledge/`
**Solution**: Create symlinks or move/copy to `docs/expert-knowledge/`

### 1.2 🚨 Navigation Structure Incomplete
**Issue**: `_archive/` section in nav points to non-existent index
**Impact**: Broken navigation link
**Solution**: Remove from nav or create proper archive index

### 1.3 ⚠️ Missing Core Pages in Navigation
**Issue**: `docs/handover-to-grok-mc-arcana-20260206.md` not in nav
**Impact**: Orphaned page, not discoverable
**Solution**: Add to appropriate section (05-research/ or new section)

---

## 2. MkDocs Configuration Improvements

### 2.1 Missing Performance Plugins
```yaml
# Current: Missing build_cache and prebuild_index
# Required for <5s warm builds:
plugins:
  - search:
      prebuild_index: true  # Add this
  - build_cache:           # Add this entire block
      enabled: true
      cache_dir: .cache/mkdocs
```

### 2.2 Missing Validation Configuration
```yaml
# Add strict validation for production builds:
validation:
  nav:
    omitted_files: warn
    not_found: warn
    absolute_links: warn
  links:
    not_found: warn
    absolute_links: warn
    anchors: warn
```

### 2.3 Missing Extra Metadata
```yaml
extra:
  version:
    provider: mike  # For versioned documentation
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/Xoe-NovAi
```

---

## 3. File Organization Improvements

### 3.1 Diátaxis Structure Compliance
Current structure mostly follows Diátaxis but has inconsistencies:

| Section | Status | Issues |
|---------|--------|--------|
| 01-start | ✅ Good | Well organized |
| 02-tutorials | ⚠️ Needs cleanup | Too many "CR -" prefixed files |
| 03-how-to-guides | ✅ Good | Proper runbooks structure |
| 04-explanation | ⚠️ Needs consolidation | Too many root-level files |
| 05-research | ✅ Good | New Vikunja plan added |
| 06-development-log | ⚠️ Needs archival | Old entries should move to _archive/ |

### 3.2 Filename Standardization Needed
**Issue**: Many files use prefixes like "CR -", "DR -", "xnai-"
**Recommendation**: Standardize to kebab-case, remove prefixes in filenames (keep in titles)

### 3.3 Duplicate/Overlapping Content
**Found**:
- Multiple "xnai-*-v3.md" files in gemini-mastery/
- Several "CR -" files may duplicate content
- `04-explanation/stack-*.md` files overlap

---

## 4. Cross-Reference & Link Audit

### 4.1 Broken Internal Links (Suspected)
- Links to `expert-knowledge/` files will fail
- Relative paths in `02-tutorials/` may be inconsistent

### 4.2 Missing Index Pages
- `05-research/labs/` has no index.md
- `03-reference/releases/` needs index
- `expert-knowledge/` subdirectories need indexes

---

## 5. Performance Optimization Recommendations

### 5.1 Build Performance
**Current**: No caching configuration
**Target**: <5s warm build, <15s cold build

### 5.2 Image Optimization
- No glightbox plugin configured for images
- Consider adding image optimization pipeline

### 5.3 Search Optimization
- Missing prebuild_index (crucial for large sites)
- No search compression configured

---

## 6. Accessibility & Best Practices

### 6.1 WCAG 2.2 AA Compliance
- ✅ Theme supports light/dark mode
- ⚠️ Verify all images have alt text
- ⚠️ Check color contrast in custom CSS

### 6.2 SEO Optimization
- Missing meta description configuration
- No sitemap.xml generation configured
- Missing robots.txt

---

## 7. Recommended Action Plan

### Priority 1 (Critical)
1. Fix expert-knowledge path issue
2. Add handover document to navigation
3. Configure build_cache plugin

### Priority 2 (High)
4. Add validation configuration
5. Standardize filenames
6. Create missing index pages

### Priority 3 (Medium)
7. Archive old development logs
8. Consolidate overlapping content
9. Add SEO/meta configurations

---

## 8. MkDocs Build Verification

### Pre-Deployment Checklist
- [ ] `mkdocs build --clean --strict` passes
- [ ] All internal links resolve
- [ ] Search index generates
- [ ] No console errors
- [ ] Mobile responsive test

---

*Audit completed. Recommend proceeding with Priority 1 fixes immediately.*
