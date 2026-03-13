# 💎 Gem (Facet 6): Active Context (SESS-17)
**Current Task**: The Great Reconciliation (Filesystem Merge).

## 🔱 Active Objectives
- [ ] Merge `storage_new/` into `data/`.
- [ ] Merge `knowledge_new/` into `expert-knowledge/`.
- [ ] Merge `docs-new/` into `docs/`.
- [ ] Create symlink for models in `/media/arcana-novai/omega_library/`.
- [ ] Reclaim ~15GB root space.

## 🔱 Ground Truth Audit
- **CWD**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-stack`
- **Root Bloat**: `storage_new/` (11.4GB), `knowledge_new/` (1.2GB).
- **VRAM Override**: Active in `docker-compose.yml`.

## 🔱 Next Steps
1.  Verify file parity for `storage_new/` vs `data/`.
2.  Perform atomic merge.
3.  Prune stale folders.

---
**This is the Mind of the Analyst.** 🔱
