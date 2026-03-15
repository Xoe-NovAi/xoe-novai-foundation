---
title: "Omega-Stack Implementation Manual 06: Filesystem Architecture"
section: "06"
scope: "Directory structure, symlinks, volume mounts, permissions model, backup paths"
status: "Reference + Actionable"
priority: "P1 — Documentation + Cleanup Guidance"
last_updated: "2026-03-13"
---

# IMPL-06 — Filesystem Architecture
## Omega-Stack Agent Implementation Manual

> **🤖 AGENT DIRECTIVE:** This manual is both a reference for the Omega-Stack's filesystem layout and an actionable guide for verifying integrity, repairing symlinks, and executing directory-level cleanup to address the 93% disk crisis.

---

## Table of Contents
1. [Mount Points & Capacity](#1-mount-points--capacity)
2. [Critical Directory Tree](#2-critical-directory-tree)
3. [Symlink Integrity Check](#3-symlink-integrity-check)
4. [Volume Mounts Reference](#4-volume-mounts-reference)
5. [Permission Model](#5-permission-model)
6. [Directory-Level Cleanup Targets](#6-directory-level-cleanup-targets)
7. [Inode Exhaustion Check](#7-inode-exhaustion-check)
8. [Edge Cases](#8-edge-cases)

---

## 1. Mount Points & Capacity

```
Mount Point                              Size    Used   Free   Status
───────────────────────────────────────────────────────────────────────
/ (root, ext4, NVMe SSD)                 117GB   109GB   8GB   🔴 CRITICAL (93%)
/media/arcana-novai/omega_library        110GB   45GB    65GB  ✅ Healthy (40%)
/media/arcana-novai/omega_vault          16GB    12GB    4GB   ⚠️ Warning (75%)
───────────────────────────────────────────────────────────────────────
TOTAL                                    244GB   166GB   78GB
```

---

## 2. Critical Directory Tree

```
/home/arcana-novai/
├── .gemini/                    ← CRITICAL: symlink or direct dir
│   ├── settings.json           (should be 0644)
│   ├── oauth_creds.json        (MUST be 0600)
│   ├── trustedFolders.json     (should be 0644)
│   ├── mcp_config.json         (should be 0644)
│   ├── memory/                 (Cline/Crush: RW)
│   ├── credentials/            (Antigravity: 0700)
│   ├── instances/              (OpenCode: RW)
│   ├── agents/                 (facet definitions)
│   ├── policies/               (access control)
│   ├── skills/sentinel-skill/  (0700 — restricted)
│   ├── chats/                  (session history)
│   └── keys/                   (Ed25519 agent keys)
│
└── Documents/Xoe-NovAi/omega-stack/
    ├── .gemini/                ← ACTUAL .gemini (100999-owned — THE ISSUE)
    ├── docker-compose.yml      (885 lines, 25 services)
    ├── .env                    (plaintext secrets — see SUPP-02)
    ├── .git/                   (~84MB git history)
    ├── config/
    │   └── mcp_config.json     (42KB, 10 MCP servers)
    ├── storage/
    │   ├── instances/          (454MB frozen facet templates)
    │   ├── instances-active/   (5.2MB active instance)
    │   └── data/               (901MB service data)
    ├── scripts/
    │   ├── permissions/        (Layer 1-4 scripts)
    │   ├── backup/             (backup scripts)
    │   └── monitoring/         (health scripts)
    └── infra/
        └── docker/             (compose variants)
```

---

## 3. Symlink Integrity Check

```bash
#!/usr/bin/env bash
echo "=== SYMLINK INTEGRITY CHECK ==="

# Check .gemini symlink
GEMINI_TARGET=$(readlink -f ~/.gemini 2>/dev/null || echo "not a symlink")
echo ".gemini resolves to: $GEMINI_TARGET"
[ -d "$GEMINI_TARGET" ] && echo "✅ Target exists" || echo "❌ Target missing — broken symlink"

# Check owner of resolved target
if [ -d "$GEMINI_TARGET" ]; then
  OWNER=$(stat -c '%U' "$GEMINI_TARGET")
  [ "$OWNER" = "arcana-novai" ] && echo "✅ Owned by arcana-novai" || echo "❌ Owned by $OWNER"
fi

# Check all symlinks in project
echo ""
echo "All symlinks in omega-stack:"
find ~/Documents/Xoe-NovAi/omega-stack/ -maxdepth 3 -type l 2>/dev/null | while read LINK; do
  TARGET=$(readlink -f "$LINK" 2>/dev/null)
  if [ -e "$TARGET" ]; then
    echo "  ✅ $LINK → $TARGET"
  else
    echo "  ❌ BROKEN: $LINK → $TARGET"
  fi
done
```

---

## 4. Volume Mounts Reference

| Volume | Host Path | Container Path | Services Using |
|--------|-----------|----------------|----------------|
| `postgres_data` | Podman managed | `/var/lib/postgresql/data` | postgres |
| `redis_data` | Podman managed | `/data` | redis |
| `qdrant_data` | Podman managed | `/qdrant/storage` | qdrant |
| `memory_bank` | `./storage/data/` | `/app/memory` | memory-bank-mcp |
| `.gemini` | `./omega-stack/.gemini` | `/app/.gemini` | memory-bank, MCP servers |
| omega_library | `/media/arcana-novai/omega_library/` | `/library` | librarian, knowledge_miner |
| omega_vault | `/media/arcana-novai/omega_vault/` | `/vault` | backup services |

---

## 5. Permission Model

```
User Matrix:
  arcana-novai (UID 1000)  → Host user — should own all .gemini files
  container process (UID 100999) → Current owner of .gemini (THE PROBLEM)
  root (UID 0)             → System files only

Target Permission Model (after IMPL-07):
  ~/.gemini/                        drwxr-x---+ (ACL: u:1000:rwx, u:100999:rwx)
  ~/.gemini/settings.json           -rw-rw----+ (ACL: u:1000:rw, u:100999:rw)
  ~/.gemini/oauth_creds.json        -rw------- (0600 — owner only, no ACL)
  ~/.gemini/credentials/            drwx------ (0700 — owner only)
  ~/.gemini/skills/sentinel-skill/  drwx------ (0700 — restricted)
```

---

## 6. Directory-Level Cleanup Targets

```bash
#!/usr/bin/env bash
echo "=== CLEANUP TARGET ANALYSIS ==="

OMEGA=~/Documents/Xoe-NovAi/omega-stack/

# Git objects (compressible)
echo "Git repo size:"
du -sh "${OMEGA}/.git/" 2>/dev/null
echo "  → Run: cd $OMEGA && git gc --aggressive --prune=now"

# Node modules (can be reinstalled)
echo ""
echo "node_modules directories:"
find "$OMEGA" -name "node_modules" -type d 2>/dev/null | while read D; do
  du -sh "$D" 2>/dev/null
done
echo "  → Safe to delete and run: npm install"

# Log files >7 days old
echo ""
echo "Old log files:"
find "$OMEGA" -name "*.log" -mtime +7 2>/dev/null | xargs du -sh 2>/dev/null | sort -rh | head -10

# Build artifacts
echo ""
echo "Build cache/artifacts:"
find "$OMEGA" -name "__pycache__" -o -name "*.pyc" 2>/dev/null | xargs du -sh 2>/dev/null | head -5
find "$OMEGA" -name "dist" -o -name "build" -type d 2>/dev/null | xargs du -sh 2>/dev/null | head -5
```

---

## 7. Inode Exhaustion Check

```bash
# Disk can be "full" on inodes even with block space available
df -i /
# If IUse% > 90% → inode exhaustion (many small files)

# Find directories with most files (inode consumers)
for DIR in /home /var /tmp; do
  echo "$DIR: $(find $DIR -maxdepth 3 2>/dev/null | wc -l) inodes"
done | sort -t: -k2 -rn | head -10
```

---

## 8. Edge Cases

| Scenario | Resolution |
|----------|-----------|
| `.gemini` symlink broken | `ln -sfn ~/Documents/Xoe-NovAi/omega-stack/.gemini ~/.gemini` |
| Volume mount shows wrong ownership | Run `podman volume inspect <vol>` to find actual path; `sudo chown -R 1000:1000 <path>` |
| Inode exhaustion (not block exhaustion) | Find and delete directories with many small files: `find / -maxdepth 5 -type d -exec sh -c 'echo "$(ls {} | wc -l) {}"' \; | sort -rn | head -20` |
| Git .git/ growing unbounded | `git gc --aggressive` reduces pack size by 40-60% |
| node_modules taking 5+ GB | Delete and reinstall: `find . -name node_modules -exec rm -rf {} + && npm install` |
