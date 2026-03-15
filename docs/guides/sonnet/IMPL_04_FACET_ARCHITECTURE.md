---
title: "Omega-Stack Implementation Manual 04: Facet Instance Architecture"
section: "04"
scope: "9 Gemini facets, Archon, .gemini isolation, instance lifecycle, permissions, subagent wiring"
status: "Actionable — Complete Rewrite with Archon Architecture"
owner: "arcana-novai (UID 1000)"
last_updated: "2026-03-13"
depends_on: "IMPL-07, ARCH-01, ARCH-02"
priority: "P1"
---

# IMPL-04 — Facet Instance Architecture
## Omega-Stack Agent Implementation Manual

> **🤖 AGENT DIRECTIVE:** Prerequisites in order: (1) IMPL-07 — permissions, (2) ARCH-01 — Archon identity design, (3) ARCH-02 — omega-facet CLI, (4) this manual — instance storage, lifecycle, backend wiring.

---

## Table of Contents
1. [Facet System Architecture](#1-facet-system-architecture)
2. [The Archon Designation](#2-the-archon-designation)
3. [Complete Facet Registry](#3-complete-facet-registry)
4. [Storage Architecture — Three Layers](#4-storage-architecture--three-layers)
5. [Per-Facet .gemini Isolation & Permissions](#5-per-facet-gemini-isolation--permissions)
6. [Instance Initialization — Full Procedure](#6-instance-initialization--full-procedure)
7. [Activation, Switching & Session Management](#7-activation-switching--session-management)
8. [Shared Backend Dependencies](#8-shared-backend-dependencies)
9. [Dormant Instance Management](#9-dormant-instance-management)
10. [Edge Cases & Failure Modes](#10-edge-cases--failure-modes)
11. [Verification Checklist](#11-verification-checklist)

---

## 1. Facet System Architecture

The Omega-Stack implements a 9-instance multi-agent system where each Gemini CLI instance (facet) has a distinct system prompt, isolated `.gemini/` state, specialized MCP tool set, and reports to the Archon (Gemini General, facet-4).

```
ARCHON (facet-4/General) — Polymath Oversoul, governs all facets
  └─ delegates via native subagents (.gemini/agents/*.md)
       ├── @researcher   → facet-1  [websearch, gnosis, memory-bank]
       ├── @engineer     → facet-2  [github, memory-bank, agentbus]
       ├── @infrastructure → facet-3 [agentbus, memory-bank, stats]
       ├── @creator      → facet-5  [memory-bank, websearch]
       ├── @datascientist → facet-6 [stats, rag, memory-bank]
       ├── @security     → facet-7  [gnosis, memory-bank]
       ├── @devops       → facet-8  [agentbus, stats, memory-bank]
       └── @general_legacy → facet-9 [memory-bank]
```

---

## 2. The Archon Designation

**Gemini General (facet-4) is the Archon** — the polymath Oversoul that orchestrates all 8 specialist facets.

| What makes the Archon | Implementation |
|----------------------|----------------|
| Polymath knowledge (all 8 domains) | `~/omega-stack/GEMINI.md` (master context) |
| Access to all 8 facets as subagents | `~/.gemini/agents/*.md` (8 definition files) |
| Delegation decision logic | GEMINI.md §Delegation Principles |
| Cross-facet memory | `~/.gemini/memory/archon_worldmodel.md` |
| Full MCP access (all 10 servers) | `~/.gemini/settings.json` mcpServers |

> **📋 See ARCH-01** for complete GEMINI.md content, all 8 subagent `.md` files, and settings.json configuration.

---

## 3. Complete Facet Registry

| ID | Facet | Specialization | MCP Servers | Instance Dir |
|----|-------|---------------|-------------|-------------|
| **4** | **Archon (General)** | **Polymath Oversoul** | **ALL 10** | `instance-4/` **← ACTIVE** |
| 1 | Researcher | Research & synthesis | websearch, gnosis, memory-bank | `instance-1/` |
| 2 | Engineer | Code & architecture | github, memory-bank, agentbus | `instance-2/` |
| 3 | Infrastructure | DevOps & platform | agentbus, memory-bank, stats | `instance-3/` |
| 5 | Creator | Technical writing | memory-bank, websearch | `instance-5/` |
| 6 | DataScientist | ML & analytics | stats, rag, memory-bank | `instance-6/` |
| 7 | Security | Security auditing | gnosis, memory-bank | `instance-7/` |
| 8 | DevOps | SRE & operations | agentbus, stats, memory-bank | `instance-8/` |
| 9 | General-Legacy | Fallback | memory-bank | `instance-9/` |

---

## 4. Storage Architecture — Three Layers

```
LAYER 1 — Frozen Templates (Read-Only Reference Copies, 454MB)
~/omega-stack/storage/instances/
├── general/gemini-cli/.gemini/    → Archon starting config
├── researcher/gemini-cli/.gemini/
├── engineer/gemini-cli/.gemini/
└── [other facets]

LAYER 2 — Active Working Copies (Live State)
~/omega-stack/instances-active/
├── instance-4/.gemini/  ← ACTIVE (5.2MB, has session history)
│   ├── agents/          ← All 8 subagent .md files (ARCH-01)
│   ├── skills/          ← Domain skill files
│   ├── memory/          ← World model + session logs
│   └── settings.json    ← enableAgents: true
├── instance-1/.gemini/  ← initialized but dormant
└── [instances 2,3,5-9] ← need initialization (§6)

LAYER 3 — Active Context Pointer
~/.gemini → symlink → instances-active/instance-4/.gemini/
             (Gemini CLI reads from here)
```

```bash
# Check current storage state
du -sh ~/Documents/Xoe-NovAi/omega-stack/storage/instances/*/
du -sh ~/Documents/Xoe-NovAi/omega-stack/instances-active/*/
readlink -f ~/.gemini
```

---

## 5. Per-Facet .gemini Isolation & Permissions

### 5.1 The Root Cause

All facet `.gemini` directories were owned by UID 100999 (Podman container) instead of UID 1000. Fix via IMPL-07 first.

### 5.2 Bulk Permission Fix (After IMPL-07)

```bash
#!/usr/bin/env bash
OMEGA=~/Documents/Xoe-NovAi/omega-stack

fix_gemini_dir() {
  local DIR="$1"
  [ -d "$DIR" ] || return 0
  sudo chown -R arcana-novai:arcana-novai "$DIR"
  setfacl -R -m "u:1000:rwx,u:100999:rwx,m::rwx" "$DIR" 2>/dev/null || true
  setfacl -d -m "u:1000:rwx,u:100999:rwx,m::rwx" "$DIR" 2>/dev/null || true
}

# Fix all template .gemini dirs
for FACET_DIR in "${OMEGA}/storage/instances"/*/; do
  fix_gemini_dir "${FACET_DIR}gemini-cli/.gemini"
done

# Fix all active instance .gemini dirs
for INST_DIR in "${OMEGA}/instances-active"/instance-*/; do
  fix_gemini_dir "${INST_DIR}.gemini"
done

# Fix home .gemini
fix_gemini_dir ~/.gemini

echo "✅ All facet .gemini directories fixed"
```

### 5.3 Security-Sensitive Subdirectories

These must remain owner-only (no ACL for UID 100999):

```bash
# After bulk fix, re-restrict sensitive paths
chmod 600 ~/.gemini/oauth_creds.json 2>/dev/null || true
setfacl -b ~/.gemini/oauth_creds.json 2>/dev/null || true  # Remove all ACLs
chmod 700 ~/.gemini/credentials/ 2>/dev/null || true
chmod 700 ~/.gemini/skills/sentinel-skill/ 2>/dev/null || true
chmod 700 ~/.gemini/keys/ 2>/dev/null || true
find ~/.gemini/keys/ -name "private.pem" -exec chmod 600 {} \; 2>/dev/null || true
```

---

## 6. Instance Initialization — Full Procedure

```bash
#!/usr/bin/env bash
set -euo pipefail

OMEGA=~/Documents/Xoe-NovAi/omega-stack
ACTIVE_DIR="${OMEGA}/instances-active"
TEMPLATES_DIR="${OMEGA}/storage/instances"

declare -A FACET_IDS=([archon]=4 [researcher]=1 [engineer]=2 [infrastructure]=3
                      [creator]=5 [datascientist]=6 [security]=7 [devops]=8 [general_legacy]=9)
declare -A FACET_TEMPLATES=([archon]=general [researcher]=researcher [engineer]=engineer
                             [infrastructure]=infrastructure [creator]=creator
                             [datascientist]=datascientist [security]=security
                             [devops]=devops [general_legacy]=general-legacy)
declare -A FACET_MCP=([archon]="all"
                      [researcher]="xnai-websearch,xnai-gnosis,memory-bank-mcp"
                      [engineer]="xnai-github,memory-bank-mcp,xnai-agentbus"
                      [infrastructure]="xnai-agentbus,memory-bank-mcp,xnai-stats-mcp"
                      [creator]="memory-bank-mcp,xnai-websearch"
                      [datascientist]="xnai-stats-mcp,xnai-rag,memory-bank-mcp"
                      [security]="xnai-gnosis,memory-bank-mcp"
                      [devops]="xnai-agentbus,xnai-stats-mcp,memory-bank-mcp"
                      [general_legacy]="memory-bank-mcp")

for FACET in "${!FACET_IDS[@]}"; do
  ID="${FACET_IDS[$FACET]}"
  INST="${ACTIVE_DIR}/instance-${ID}"
  GEMINI="${INST}/.gemini"
  TMPL="${TEMPLATES_DIR}/${FACET_TEMPLATES[$FACET]}/gemini-cli/.gemini"
  
  mkdir -p "${GEMINI}/memory" "${GEMINI}/chats" "${GEMINI}/agents" \
           "${GEMINI}/skills" "${GEMINI}/credentials" "${GEMINI}/instances"
  
  # Populate from frozen template if available
  [ -d "$TMPL" ] && rsync -a --ignore-existing "${TMPL}/" "${GEMINI}/" && \
    echo "  ✓ facet-${ID} ($FACET): from template" || \
    echo "  ✓ facet-${ID} ($FACET): fresh init"
  
  # Settings
  cat > "${GEMINI}/settings.json" << SETTINGS_EOF
{
  "theme": "Default",
  "selectedAuthType": "oauth-personal",
  "facet": "${FACET}",
  "facetId": ${ID},
  "experimental": {
    "enableAgents": $([ "$FACET" = "archon" ] && echo 'true' || echo 'false'),
    "enableSkills": true
  }
}
SETTINGS_EOF

  # Memory seed
  cat > "${GEMINI}/memory/facet_context.md" << MEM_EOF
# ${FACET^} Facet — Context
Facet ID: ${ID} | MCP Servers: ${FACET_MCP[$FACET]}
Initialized: $(date '+%Y-%m-%d')
Role: $([ "$FACET" = "archon" ] && echo "Archon — Polymath Oversoul governing all other facets" || echo "Specialist — called by Archon via subagent delegation")
MEM_EOF

  # Permissions
  sudo chown -R arcana-novai:arcana-novai "${INST}" 2>/dev/null || true
  setfacl -d -m "u:1000:rwx,u:100999:rwx,m::rwx" "${GEMINI}" 2>/dev/null || true
  chmod 700 "${GEMINI}/credentials" 2>/dev/null || true
done

# Copy Archon's agents/skills to its instance
cp ~/.gemini/agents/*.md "${ACTIVE_DIR}/instance-4/.gemini/agents/" 2>/dev/null || true
cp ~/.gemini/skills/*.md "${ACTIVE_DIR}/instance-4/.gemini/skills/" 2>/dev/null || true

# Set Archon as active
ln -sfn "${ACTIVE_DIR}/instance-4/.gemini" ~/.gemini
echo "✅ All facets initialized. Active: Archon (instance-4)"
```

---

## 7. Activation, Switching & Session Management

```bash
# Activate a specific facet (using omega-facet CLI)
omega-facet activate archon        # Return to Archon (default)
omega-facet activate researcher    # Switch to Researcher
omega-facet activate security      # Switch to Security for an audit

# Manual activation (without CLI)
FACET_DIR=~/Documents/Xoe-NovAi/omega-stack/instances-active/instance-7
ln -sfn "${FACET_DIR}/.gemini" ~/.gemini
sudo chown -R arcana-novai:arcana-novai ~/.gemini/ 2>/dev/null || true
setfacl -d -m u:1000:rwx,u:100999:rwx,m::rwx ~/.gemini/ 2>/dev/null || true

# Start Gemini CLI with specific working directory context
cd ~/Documents/Xoe-NovAi/omega-stack && gemini   # Loads project GEMINI.md (Archon context)

# Save session state before switching
cp -r ~/.gemini/chats/ \
  ~/Documents/Xoe-NovAi/omega-stack/instances-active/instance-4/session_$(date +%Y%m%d_%H%M%S)/

# Resume a previous session via checkpoint
# Within gemini: /checkpoint list
# gemini --checkpoint <checkpoint-name>
```

---

## 8. Shared Backend Dependencies

```bash
#!/usr/bin/env bash
echo "=== FACET BACKEND HEALTH ==="

for NAME_PORT_CRITICAL in \
  "memory-bank-mcp:8005:CRITICAL" \
  "redis:6379:CRITICAL" \
  "postgres:5432:CRITICAL" \
  "qdrant:6333:HIGH" \
  "xnai-websearch:8009:MEDIUM" \
  "xnai-github:8006:MEDIUM" \
  "xnai-agentbus:8011:MEDIUM" \
  "xnai-stats-mcp:8008:MEDIUM" \
  "xnai-gnosis:8010:MEDIUM" \
  "xnai-rag:8007:MEDIUM"; do
  
  NAME="${NAME_PORT_CRITICAL%%:*}"
  REMAINDER="${NAME_PORT_CRITICAL#*:}"
  PORT="${REMAINDER%%:*}"
  CRIT="${REMAINDER##*:}"
  
  if curl -sf "http://localhost:${PORT}/health" &>/dev/null 2>/dev/null || \
     nc -z localhost "$PORT" 2>/dev/null; then
    printf "  ✅ %-25s port %-6s [%s]\n" "$NAME" "$PORT" "$CRIT"
  else
    printf "  ❌ %-25s port %-6s [%s] — NOT AVAILABLE\n" "$NAME" "$PORT" "$CRIT"
  fi
done
```

---

## 9. Dormant Instance Management

```bash
# List all instance states
#!/usr/bin/env bash
OMEGA=~/Documents/Xoe-NovAi/omega-stack
ACTIVE_LINK=$(readlink -f ~/.gemini 2>/dev/null)

declare -A IDS=([archon]=4 [researcher]=1 [engineer]=2 [infrastructure]=3
                [creator]=5 [datascientist]=6 [security]=7 [devops]=8 [general_legacy]=9)

printf "%-18s  %-6s  %-10s  %s\n" "FACET" "ID" "STATE" "SIZE"
printf "%-18s  %-6s  %-10s  %s\n" "──────────────────" "──────" "──────────" "────"
for FACET in archon researcher engineer infrastructure creator datascientist security devops general_legacy; do
  ID="${IDS[$FACET]}"
  DIR="${OMEGA}/instances-active/instance-${ID}"
  GEMINI="${DIR}/.gemini"
  
  if [ ! -d "$DIR" ]; then STATE="🔴 UNINIT"
  elif [ "$(readlink -f ${GEMINI})" = "$ACTIVE_LINK" ] || \
       [ "${GEMINI}" = "$ACTIVE_LINK" ]; then STATE="🟢 ACTIVE"
  else STATE="⚫ DORMANT"
  fi
  
  SIZE=$([ -d "$DIR" ] && du -sh "$DIR" 2>/dev/null | cut -f1 || echo "—")
  printf "%-18s  %-6s  %-10s  %s\n" "$FACET" "$ID" "$STATE" "$SIZE"
done

# Cleanup old backup copies
# find instances-active/ -name "session_2026*" -mtime +30 -exec rm -rf {} +
# find instances-active/ -name "*.bak.*" -mtime +7 -exec rm -rf {} +
```

---

## 10. Edge Cases & Failure Modes

| Scenario | Symptom | Resolution |
|----------|---------|------------|
| ~/.gemini symlink broken | Gemini CLI: "configuration not found" | `omega-facet activate archon` |
| Subagent not found after creating .md file | `/agent researcher` returns error | `/agents reload` in session |
| Wrong facet context loaded | Response doesn't match expected domain | Check `readlink -f ~/.gemini`; re-activate correct facet |
| Two sessions conflict on same instance | Memory corruption, settings overwrite | Use separate tmux windows; only one active instance at a time |
| Instance disk grows unbounded | instances-active/ > 5GB | Archive old chats: `find instances-active -name "*.json" -mtime +30 -delete` |
| Template .gemini still 100999-owned | Cannot init new instances | Run §5.2 bulk fix; check sudo; re-run §6 initialization |
| Archon subagents disabled | `enableAgents: false` in settings.json | `omega-facet activate archon` (re-applies correct settings) |

---

## 11. Verification Checklist

```bash
#!/usr/bin/env bash
echo "=== IMPL-04 VERIFICATION ==="
OMEGA=~/Documents/Xoe-NovAi/omega-stack

ok() { echo "  ✅ $1"; }; fail() { echo "  ❌ $1"; }; warn() { echo "  ⚠️  $1"; }

# Archon setup (ARCH-01)
[ -f "${OMEGA}/GEMINI.md" ] && ok "Archon GEMINI.md" || fail "Archon GEMINI.md MISSING"
for FA in researcher engineer infrastructure creator datascientist security devops general_legacy; do
  [ -f ~/.gemini/agents/${FA}.md ] && ok "Subagent: $FA" || fail "Missing subagent: $FA"
done

# Instance directories
declare -A IDS=([archon]=4 [researcher]=1 [engineer]=2 [infrastructure]=3
                [creator]=5 [datascientist]=6 [security]=7 [devops]=8 [general_legacy]=9)
for FACET in "${!IDS[@]}"; do
  [ -d "${OMEGA}/instances-active/instance-${IDS[$FACET]}/.gemini" ] && \
    ok "instance-${IDS[$FACET]} ($FACET)" || warn "instance-${IDS[$FACET]} ($FACET) not initialized"
done

# Active symlink
[ -w ~/.gemini ] && ok ".gemini writable" || fail ".gemini NOT writable"
BAD=$(find "${OMEGA}/instances-active" -name ".gemini" -type d -not -user arcana-novai 2>/dev/null | wc -l)
[ "$BAD" -eq 0 ] && ok "All instances properly owned" || fail "$BAD instances with wrong ownership"

# Settings
python3 -c "
import json
with open('$HOME/.gemini/settings.json') as f: s = json.load(f)
print('  ✅ enableAgents: true' if s.get('experimental',{}).get('enableAgents') else '  ❌ enableAgents NOT enabled')
" 2>/dev/null

# Backends
curl -sf http://localhost:8005/health &>/dev/null && ok "memory-bank-mcp" || fail "memory-bank-mcp DOWN"

echo ""
echo "  Start Archon: cd ${OMEGA} && gemini"
echo "  Spawn facet:  omega-facet spawn researcher"
echo "=== END ==="
```
