# Memory Bank Design Improvements — GPT-4.1 Recommendation #4

**Confidence**: 75% (pending implementation validation)  
**Last Updated**: 2026-03-14

---

## Current State Analysis

### Memory Bank Structure
- **Location**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/memory_bank/`
- **Index file**: `memory_bank/index.json` (large but necessary)
- **Status**: Functional, but needs archival policy

### Assessment
✓ Index.json is large but necessary for recall  
✗ Manual reindexing is sufficient (no automation needed)  
✗ "Junk drawer" risk — no archival policy defined  
✗ No periodic review process  
✗ Decision records not in YAML format  

---

## Recommended Improvements

### 1. Archival Policy

**Rule**: Archive decision records older than 6 months

```bash
# Quarterly archival process (next: 2026-06-14)
find memory_bank/ -name "*.md" -mtime +180 -type f | \
  xargs -I {} mv {} memory_bank/archive/2026-Q2-archive/

# Preserve full audit trail
cp memory_bank/index.json memory_bank/archive/2026-Q2-archive/index-snapshot.json
```

### 2. Decision Record Format (YAML Front Matter)

**Before** (current markdown):
```markdown
# Decision: Use Redis for Caching

We decided to use Redis because...
```

**After** (YAML + markdown):
```yaml
---
title: Use Redis for Caching
date: 2026-03-14
category: infrastructure
status: active
confidence: 85%
depends_on: []
related: [memory-bank-structure, caching-strategy]
---

# Decision: Use Redis for Caching

We decided to use Redis because...
```

### 3. Periodic Review Process

**Monthly (automated via cron)**:
```bash
# Run monthly review (1st of each month at 02:00 UTC)
0 2 1 * * /home/arcana-novai/Documents/Xoe-NovAi/omega-stack/scripts/memory-bank-review.sh
```

**What the script does**:
1. Count records by category and age
2. Identify stale records (no update in 3+ months)
3. Flag records with low confidence (<60%)
4. Generate MEMORY_BANK_HEALTH_REPORT.md

### 4. Index Query Optimization

**Current**: Flat JSON array (slow for large datasets)  
**Improvement**: Add metadata + categories

```json
{
  "metadata": {
    "version": "2.0",
    "last_updated": "2026-03-14T04:30:00Z",
    "total_records": 245,
    "categories": {
      "infrastructure": 87,
      "security": 34,
      "decisions": 56,
      "incidents": 23,
      "deprecated": 45
    }
  },
  "records": [
    {
      "id": "dec-001",
      "title": "Use Redis for Caching",
      "category": "infrastructure",
      "date": "2026-03-14",
      "path": "memory_bank/decisions/caching-strategy.md",
      "status": "active",
      "confidence": 85
    }
  ],
  "archive": {
    "deprecated_count": 45,
    "last_archive": "2026-03-14",
    "location": "memory_bank/archive/"
  }
}
```

### 5. Cross-Reference Linking

**Update** all memory bank files with links:
```yaml
related: [other-record-id, another-record-id]
depends_on: [prerequisite-record-id]
blocks: [blocked-record-id]
```

This enables:
- Dependency graph visualization
- "What depends on this?" queries
- Circular dependency detection

---

## Implementation Checklist

### Phase 1: Structure & Documentation (Week 1)
- [ ] Create MEMORY_BANK_ARCHITECTURE.md (governance)
- [ ] Document YAML front matter schema
- [ ] Create archival script (scripts/memory-bank-archive.sh)
- [ ] Create review script (scripts/memory-bank-review.sh)

### Phase 2: Migration (Week 2-3)
- [ ] Audit all existing records (245 total)
- [ ] Add YAML headers to 80% of records
- [ ] Move records >6 months old to archive/
- [ ] Update index.json with new metadata

### Phase 3: Automation (Week 4)
- [ ] Set up cron job for monthly review
- [ ] Create dashboard for memory bank health
- [ ] Add pre-commit hook: validate YAML headers
- [ ] Document quarterly review process

### Phase 4: Optimization (Month 2+)
- [ ] Implement relationship queries
- [ ] Add visualization tool (dependency graph)
- [ ] Automate confidence scoring
- [ ] Create incident correlation (cross-reference similar issues)

---

## Risk Mitigation

### Risk: Data Loss During Migration
**Mitigation**: 
- Full backup before starting: `cp -r memory_bank memory_bank.backup.2026-03-14`
- Test on backup first
- Verify all records still accessible after migration

### Risk: Circular Dependencies
**Mitigation**:
- Pre-commit hook to detect cycles
- Quarterly audit of relationship graph
- Alert if new cycles detected

### Risk: Over-Archival
**Mitigation**:
- Conservative 6-month threshold (not 3)
- Always move to archive (never delete)
- Keep archive searchable and indexed

---

## Expected Benefits

✓ **Faster decisions**: YAML metadata enables quick queries  
✓ **Better recall**: Cross-references help find related decisions  
✓ **Audit trail**: Full history preserved forever  
✓ **Lower maintenance**: Automated review catches staleness  
✓ **Knowledge retention**: Organized archive prevents "junk drawer"  

---

## Validation Plan

After implementation, verify:
1. [ ] All 245 records migrated successfully
2. [ ] Index queries <1s response time
3. [ ] No data loss (backup audit)
4. [ ] YAML parsing 100% valid
5. [ ] Monthly review script runs successfully

**Confidence**: 75% → 90% (after validation)

---

**Next Steps**:
1. Review and approve archival policy
2. Create scripts (memory-bank-archive.sh, memory-bank-review.sh)
3. Schedule migration for next 2-week sprint
4. Run validation tests before deployment

**Timeline**: 4 weeks (full implementation + validation)  
**Owner**: Haiku (implementation) + User (approval gates)
