---
title: "Omega-Stack Implementation Manual 03: MCP Server Ecosystem"
section: "03"
scope: "10 MCP servers, ports 8005-8014, health, configuration, dependency wiring"
status: "Actionable"
priority: "P1 — 2 MCP Servers Unstable (xnai-rag, xnai-memory)"
last_updated: "2026-03-13"
---

# IMPL-03 — MCP Server Ecosystem
## Omega-Stack Agent Implementation Manual

> **🤖 AGENT DIRECTIVE:** The Omega-Stack runs 10 MCP (Model Context Protocol) servers providing context, tools, and data integration to 9 Gemini facets. Two servers are currently unstable (xnai-rag depends on unhealthy qdrant; xnai-memory has memory pressure issues). Fix IMPL-02 service recovery first.

---

## Table of Contents
1. [MCP Server Inventory](#1-mcp-server-inventory)
2. [Health Verification](#2-health-verification)
3. [Configuration Audit](#3-configuration-audit)
4. [Per-Server Recovery Runbooks](#4-per-server-recovery-runbooks)
5. [MCP Config Schema Validation](#5-mcp-config-schema-validation)
6. [Edge Cases & Failure Modes](#6-edge-cases--failure-modes)
7. [Verification Checklist](#7-verification-checklist)

---

## 1. MCP Server Inventory

| Server | Port | Status | Specialization | Dependencies |
|--------|------|--------|----------------|-------------|
| memory-bank-mcp | 8005 | ✅ Healthy | Context/RAG hub | redis, postgres |
| xnai-github | 8006 | 🟡 Functional | GitHub integration | external API |
| xnai-rag | 8007 | 🟠 Unstable | RAG retrieval | qdrant (unhealthy) |
| xnai-stats-mcp | 8008 | 🟡 Functional | Statistics/metrics | victoriametrics |
| xnai-websearch | 8009 | 🟡 Functional | Web search | external API |
| xnai-gnosis | 8010 | 🟡 Functional | Knowledge graph | postgres |
| xnai-agentbus | 8011 | 🟡 Functional | Agent messaging | redis |
| xnai-memory | 8012 | 🟠 Unstable | Memory retrieval | memory-bank-mcp |
| (unassigned) | 8013 | — | — | — |
| xnai-sambanova | 8014 | 🔵 Initializing | LLM integration | external API |

---

## 2. Health Verification

```bash
#!/usr/bin/env bash
# Full MCP health sweep
echo "=== MCP SERVER HEALTH SWEEP ==="
for PORT in 8005 8006 8007 8008 8009 8010 8011 8012 8014; do
  SVC=$(podman ps --format "{{.Names}}\t{{.Ports}}" 2>/dev/null | grep ":${PORT}->" | awk '{print $1}' | head -1)
  if curl -sf "http://localhost:${PORT}/health" &>/dev/null; then
    echo "✅ Port $PORT ($SVC): HEALTHY"
  elif curl -sf "http://localhost:${PORT}/" &>/dev/null; then
    echo "🟡 Port $PORT ($SVC): RESPONDING (no /health endpoint)"
  else
    echo "❌ Port $PORT ($SVC): NOT RESPONDING"
  fi
done
```

---

## 3. Configuration Audit

```bash
# Validate mcp_config.json
MCP_CONFIG=~/Documents/Xoe-NovAi/omega-stack/config/mcp_config.json
python3 -m json.tool "$MCP_CONFIG" > /dev/null && echo "✅ mcp_config.json is valid JSON" || echo "❌ JSON parse error"

# Check all referenced ports are listening
grep -oP '"port":\s*\K\d+' "$MCP_CONFIG" | while read PORT; do
  ss -tuln | grep -q ":$PORT " && echo "✅ Port $PORT listening" || echo "❌ Port $PORT NOT listening"
done
```

---

## 4. Per-Server Recovery Runbooks

### xnai-rag (Blocked by qdrant)

```bash
# Wait for qdrant to be healthy first
until curl -sf http://localhost:6333/health; do echo "Waiting for qdrant..."; sleep 5; done

# Restart xnai-rag
podman restart xnai-rag
sleep 10
curl -sf http://localhost:8007/health && echo "✅ xnai-rag healthy"
```

### xnai-memory (Memory pressure)

```bash
# Check current memory usage
podman stats --no-stream xnai-memory

# Add memory limit and restart
# In docker-compose.yml, ensure:
# deploy:
#   resources:
#     limits:
#       memory: 384M

podman restart xnai-memory
```

### xnai-sambanova (Initializing)

```bash
# SambaNova requires API credentials — verify they're set
grep -i 'sambanova\|SAMBA' ~/Documents/Xoe-NovAi/omega-stack/.env | head -5
# If empty, the service cannot initialize — add credentials first
```

---

## 5. MCP Config Schema Validation

```bash
#!/usr/bin/env bash
# Validate all MCP server definitions have required fields
python3 << 'PYEOF'
import json, sys

config_path = f"{__import__('os').path.expanduser('~')}/Documents/Xoe-NovAi/omega-stack/config/mcp_config.json"
with open(config_path) as f:
    config = json.load(f)

required_fields = ['name', 'port', 'description']
servers = config.get('servers', config.get('mcpServers', []))

if isinstance(servers, dict):
    servers = [{'name': k, **v} for k, v in servers.items()]

errors = 0
for svc in servers:
    for field in required_fields:
        if field not in svc:
            print(f"❌ {svc.get('name', 'unknown')}: missing '{field}'")
            errors += 1

if errors == 0:
    print(f"✅ All {len(servers)} MCP servers have required fields")
else:
    print(f"Found {errors} validation errors")
PYEOF
```

---

## 6. Edge Cases & Failure Modes

| Scenario | Symptom | Resolution |
|----------|---------|------------|
| xnai-rag hangs on qdrant reconnect | High CPU, no responses | `podman restart xnai-rag` with exponential backoff |
| memory-bank-mcp disk full | Write failures on context save | Storage cleanup (IMPL-01 §4) |
| xnai-agentbus queue overflow | Redis ENOMEM | Check redis memory: `podman exec redis redis-cli INFO memory` |
| xnai-websearch rate limited | 429 responses to queries | Implement request queuing or rotate API keys |
| Port 8013 gap | No service on expected port | Intentional gap — document and skip in health checks |

---

## 7. Verification Checklist

```bash
# All critical MCP servers responding
for PORT in 8005 8006 8009 8010 8011; do
  curl -sf "http://localhost:${PORT}/health" &>/dev/null && echo "✅ Port $PORT OK" || echo "❌ Port $PORT FAIL"
done

# mcp_config.json valid
python3 -m json.tool ~/Documents/Xoe-NovAi/omega-stack/config/mcp_config.json > /dev/null && echo "✅ Config valid"
```
