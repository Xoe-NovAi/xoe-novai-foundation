---
title: "Omega-Stack Implementation Manual 05: Development Tool Integration"
section: "05"
scope: "7 dev tools, .gemini hub, MCP wiring, auth, per-tool validation"
status: "Actionable — Blocked by .gemini permissions"
priority: "P0 — All 7 Tools Blocked by EACCES"
last_updated: "2026-03-13"
---

# IMPL-05 — Development Tool Integration
## Omega-Stack Agent Implementation Manual

> **🤖 AGENT DIRECTIVE:** All 7 development tools are blocked by the `.gemini` permission issue. Complete IMPL-07 first, then use this manual to validate each tool's functionality and resolve any tool-specific configuration issues. The shared `.gemini` hub is the critical integration point.

---

## Table of Contents
1. [Tool Ecosystem Overview](#1-tool-ecosystem-overview)
2. [Shared .gemini Hub Structure](#2-shared-gemini-hub-structure)
3. [Per-Tool Recovery & Validation](#3-per-tool-recovery--validation)
4. [MCP Server Wiring per Tool](#4-mcp-server-wiring-per-tool)
5. [OAuth & Authentication Recovery](#5-oauth--authentication-recovery)
6. [Edge Cases](#6-edge-cases)
7. [Verification Checklist](#7-verification-checklist)

---

## 1. Tool Ecosystem Overview

| Tool | Primary Path | Access Mode | Failure Impact |
|------|------------|-------------|----------------|
| **Cline** | `~/.gemini/memory/` | RW (Full) | Agent logic, session memory lost |
| **Copilot CLI** | `~/.gemini/settings.json` | RO | Auth token load failure, login loop |
| **Gemini CLI** | `~/.gemini/` (admin) | RW (Admin) | Total stack lockout |
| **VS Code** | `~/.gemini/trustedFolders.json` | RO | Security warnings every launch |
| **OpenCode** | `~/.gemini/instances/` | RW (Full) | Facet orchestration fails |
| **Antigravity** | `~/.gemini/credentials/` | RW (Full) | Encrypted storage, RAG fails |
| **Crush** | `~/.gemini/memory/` | RO | Audit logging unavailable |

---

## 2. Shared .gemini Hub Structure

```
~/.gemini/  (symlink → omega-stack/.gemini/ or direct dir)
├── settings.json          # Global tool settings (shared)
├── oauth_creds.json       # OAuth tokens (0600 - owner only)
├── trustedFolders.json    # VS Code trusted paths
├── mcp_config.json        # MCP server routing
├── agents/                # Facet definitions (read by all tools)
├── policies/              # Access control per facet
├── skills/                # Custom skills (sentinel-skill: 0700)
├── memory/                # Cline + Crush read/write
├── credentials/           # Antigravity encrypted storage (0700)
├── instances/             # OpenCode facet state
├── chats/                 # Session history
└── keys/                  # Ed25519 agent keys
```

---

## 3. Per-Tool Recovery & Validation

### Cline

```bash
# After IMPL-07, test Cline memory access
ls -la ~/.gemini/memory/
cat ~/.gemini/memory/*.json 2>/dev/null | python3 -m json.tool | head -20
echo "If readable → Cline operational"

# Cline settings location (also check VS Code extension settings)
cat ~/.gemini/settings.json | python3 -m json.tool | grep -i cline
```

### Copilot CLI

```bash
# Test settings access
cat ~/.gemini/settings.json &>/dev/null && echo "✅ Copilot CLI: settings accessible"

# If in auth loop, clear and re-auth
# (Copilot CLI stores tokens in settings.json — fix permissions first)
github-copilot-cli --version 2>/dev/null || echo "Copilot CLI not in PATH"
```

### Gemini CLI (Primary AI Interface)

```bash
# Test full .gemini access
gemini --version 2>/dev/null
ls -la ~/.gemini/ && echo "✅ Gemini CLI: .gemini accessible"

# If Gemini CLI reports auth issues after permission fix:
# Re-run OAuth flow
gemini auth login 2>/dev/null || echo "Check Gemini CLI documentation for auth command"
```

### VS Code

```bash
# trustedFolders.json must be readable
cat ~/.gemini/trustedFolders.json 2>/dev/null | python3 -m json.tool
# If this fails, VS Code will show workspace trust warnings

# Fix specifically for VS Code:
chmod 644 ~/.gemini/trustedFolders.json
```

### OpenCode

```bash
# Test instances directory
ls -la ~/.gemini/instances/
[ -d ~/.gemini/instances ] && echo "✅ OpenCode: instances dir accessible"
```

### Antigravity

```bash
# credentials/ must be user-only
ls -la ~/.gemini/credentials/
# Expected: drwx------ (0700) — only arcana-novai has access
# Antigravity uses encrypted storage here — do NOT change to 0755
```

---

## 4. MCP Server Wiring per Tool

```bash
# View current MCP routing
cat ~/.gemini/mcp_config.json | python3 -m json.tool

# Expected: each tool section maps to correct MCP server ports
# Verify ports are listening:
for PORT in 8005 8006 8007 8008 8009 8010 8011 8012; do
  ss -tuln | grep -q ":$PORT " && echo "✅ MCP port $PORT active" || echo "❌ MCP port $PORT not listening"
done
```

---

## 5. OAuth & Authentication Recovery

```bash
#!/usr/bin/env bash
# Check OAuth token status (without exposing values)
echo "=== OAuth Token Status ==="
CREDS=~/.gemini/oauth_creds.json

if [ -r "$CREDS" ]; then
  # Check if tokens are expired (look for expiry field)
  EXPIRY=$(python3 -c "
import json, sys
with open('$CREDS') as f:
  data = json.load(f)
# Look for common expiry field names
for key in ['expires_at', 'expiry', 'exp', 'token_expiry']:
  if key in data:
    print(data[key])
    break
" 2>/dev/null)
  
  if [ -n "$EXPIRY" ]; then
    echo "Token expiry field found: $EXPIRY"
  else
    echo "No expiry field found — tokens may be long-lived"
  fi
  echo "✅ oauth_creds.json readable"
else
  echo "❌ oauth_creds.json NOT readable — run IMPL-07 first"
fi
```

---

## 6. Edge Cases

| Scenario | Resolution |
|----------|-----------|
| Tool re-creates settings.json as 100999 | Layer 4 timer repairs in ≤15 min; or run `acl_repair.sh` |
| Cline loses memory after container restart | Memory in `~/.gemini/memory/` persists if owned by 1000 |
| Copilot CLI in infinite auth loop | Fix permissions → `cat ~/.gemini/settings.json` must succeed |
| VS Code workspace trust popup on every open | Fix `trustedFolders.json` permissions: `chmod 644 ~/.gemini/trustedFolders.json` |
| Antigravity can't decrypt credentials | credentials/ mode must be 0700 — do NOT open to group |
| mcp_config.json invalid after tool update | Validate: `python3 -m json.tool ~/.gemini/mcp_config.json` |

---

## 7. Verification Checklist

```bash
#!/usr/bin/env bash
echo "=== IMPL-05 TOOL INTEGRATION VERIFICATION ==="

GEMINI=~/.gemini
test_tool() {
  local TOOL="$1" PATH="$2" MODE="$3"
  if [ "$MODE" = "r" ]; then
    [ -r "$PATH" ] && echo "✅ $TOOL: $PATH readable" || echo "❌ $TOOL: $PATH NOT readable"
  else
    touch "${PATH}/.write_test_$$" 2>/dev/null && rm "${PATH}/.write_test_$$" && \
      echo "✅ $TOOL: $PATH writable" || echo "❌ $TOOL: $PATH NOT writable"
  fi
}

test_tool "Cline"       "${GEMINI}/memory"           w
test_tool "Copilot CLI" "${GEMINI}/settings.json"    r
test_tool "Gemini CLI"  "${GEMINI}"                  w
test_tool "VS Code"     "${GEMINI}/trustedFolders.json" r
test_tool "OpenCode"    "${GEMINI}/instances"         w
test_tool "Antigravity" "${GEMINI}/credentials"       w
test_tool "Crush"       "${GEMINI}/memory"            r

# Credential security
CRED_MODE=$(stat -c '%a' "${GEMINI}/oauth_creds.json" 2>/dev/null)
[ "$CRED_MODE" = "600" ] && echo "✅ oauth_creds.json secured (600)" || echo "⚠️ oauth_creds.json mode: $CRED_MODE (should be 600)"

echo "=== END VERIFICATION ==="
```
