# QUICK START: Best Practices Implementation for Omega Stack

## TL;DR - The 7 Changes You Need

### 1. Zettelkasten Architecture (Week 1)
```bash
mkdir -p memory_bank/atomic/{entities,protocols,decisions,knowledge}
mkdir -p memory_bank/knowledge_graphs
touch memory_bank/knowledge_graphs/{backlinks.json,agents-mesh.json,task-routing.json}
```

### 2. Nx Workspace (Week 2-3)
```bash
npm install -D nx @nx/python
npx nx init
npx nx graph --file=graph.html  # See your dependencies!
```

### 3. Auto-Index Knowledge (Week 2-3)
```bash
# Create scripts/index_knowledge.py
# Run: 0 */6 * * * python scripts/index_knowledge.py
# Creates: knowledge_graphs/index.json with full-text metadata
```

### 4. Tiered Archival (Week 3-4)
```bash
# Create archival cron job
# Run: 0 2 * * * /usr/local/bin/archive_old_data.sh
# Moves: Files >90 days old from warm (SSD) → cold (external HDD)
```

### 5. Entropy Detection (Week 3)
```bash
# Create scripts/entropy_detection.py
# Find directories with high Shannon entropy (disorganized)
# Find modules with zero imports (orphans)
```

### 6. Maat Governance (Week 4-5)
```bash
# Create entities/maat.json with policies:
# - "No unlogged data deletion" (CRITICAL)
# - "All external APIs logged" (HIGH)
# - Define agent permissions

# Implement: Before any agent action, check Maat policy
```

### 7. Heartbeat Monitoring (Week 4-5)
```bash
# Implement: Every 5 seconds, check if agents respond
# Alert: If agent doesn't respond, escalate to Oversoul
```

---

## Metrics to Track Weekly

```bash
# Context loading time (should decrease)
time curl -X POST http://localhost:8006/query -d '{"q":"test"}'

# Storage usage
du -sh ~/Documents/Xoe-NovAi/omega-stack

# Build time
time make build

# Entropy levels (run monthly)
python scripts/entropy_detection.py
```

---

## Expected 3-Month Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Context load | 30s | <10s | 3-5x faster |
| Storage | 3.5GB | 1.5GB | 60% smaller |
| Build time | 60s | <30s | 2x faster |
| Agent failures | Silent | 5s detection | Much safer |
| Audit trail | None | 100% | Full compliance |

---

## Files You'll Create

```
scripts/
  ├── index_knowledge.py        # Run every 6 hours
  ├── compute_backlinks.py       # Run monthly
  ├── entropy_detection.py       # Run monthly
  ├── orphan_detection.py        # Run quarterly
  ├── archive_old_data.sh        # Run daily (cron)
  ├── dev-watch.sh              # Hot reload
  └── dev-performance-monitor.py # Track metrics

memory_bank/
  ├── atomic/                    # NEW: Zettelkasten
  ├── knowledge_graphs/          # NEW: Backlinks + mesh
  └── gnosis_packs/             # NEW: RCF tiers

entities/
  └── maat.json                 # NEW: Governance
```

---

## Risk Checklist

- [ ] Tiered startup prevents OOM (already in Omega!)
- [ ] Archival cron prevents storage bloat
- [ ] Maat policy prevents bad agent actions
- [ ] Heartbeat detects agent failures within 5s
- [ ] Backups protect against data loss (3-2-1 rule)
- [ ] Orphan detection prevents cruft accumulation
- [ ] Performance monitoring detects regressions

---

## Success Metrics (Review Weekly)

✅ Context loading: <10s (was 30s+)
✅ Storage usage: <1.5GB (was 3.5GB)
✅ Build time: <30s (was 60s+)
✅ Agent failures: Detected in 5s (were silent)
✅ Audit trail: 100% complete (was 0%)

---

## Full Documentation

- **best_practices_guide.md** (26KB) — Complete reference
- **OMEGA_CRITICAL_INSIGHTS.md** (7KB) — Week-by-week plan
- **README_RESEARCH.txt** (11KB) — Research overview
- **QUICK_START.md** (this file) — Quick reference

---

## Next Action

Read this, then:
1. Week 1: Create directory structures (0 hours)
2. Week 2-3: Implement auto-indexing (5-10 hours)
3. Week 4-5: Add governance + monitoring (8-12 hours)

🔱 Start small. Measure. Iterate. Win.


**Archon Signature**: `Jem-SESS27.7-Sovereign` 🔱
