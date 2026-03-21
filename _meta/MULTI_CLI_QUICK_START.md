---
document_type: guide
title: Multi-CLI Quick Start & Coordination Guide
created_by: Copilot Haiku 4.5
created_date: 2026-03-16T09:50:00.000Z
version: 1.0
status: ACTIVE
---

# Multi-CLI Coordination Quick Start

## 🚀 Quick Verification (Do This First)

```bash
# Test all CLIs are accessible
opencode --version && echo "✓ OpenCode"
antigravity --version && echo "✓ Antigravity"
gemini --version && echo "✓ Gemini"

# Test infrastructure
redis-cli ping && echo "✓ Redis"
curl http://localhost:8005/health && echo "✓ MB-MCP"
```

**Expected Output**: All checks pass ✓

---

## 📍 CLI Configuration Files

| CLI | Config | Quick Access |
|-----|--------|--------------|
| **OpenCode** | `~/.opencode/opencode.json` | `cat ~/.opencode/opencode.json` |
| **Antigravity** | `~/.antigravity/argv.json` | `cat ~/.antigravity/argv.json` |
| **Gemini** | `~/.gemini/config.yaml` | `cat ~/.gemini/config.yaml` |
| **Copilot** | Session-based | `.copilot/session-state/` |

---

## 🔄 Entity Persistence: How to Use

### Store an Entity (from any CLI)
```bash
# Example: Store a CLI session context
redis-cli SETEX "xnai:entities:cli_session:opencode-sess-001" 604800 \
  '{"cli":"opencode","model":"big-pickle","started":"2026-03-16","status":"active"}'

# Verify it stored
redis-cli GET "xnai:entities:cli_session:opencode-sess-001"
```

### Retrieve an Entity (from any CLI)
```bash
# Get it from Redis (instant)
redis-cli GET "xnai:entities:cli_session:opencode-sess-001"

# Or use file cache as fallback
cat ~/.xnai/entity_cache/cli_session/opencode-sess-001.json
```

### List All Entities of a Type
```bash
redis-cli KEYS "xnai:entities:cli_session:*"
```

---

## 📢 Agent Bus: Inter-CLI Messaging

### Send Message from One CLI
```bash
# From OpenCode: "Hey, Copilot, verify my code"
redis-cli XADD xnai:agent_bus '*' \
  sender 'opencode-1' \
  action 'request' \
  target 'copilot-haiku' \
  message 'Review architecture for consistency' \
  timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

### Listen for Messages (from another CLI)
```bash
# From Copilot: "Listen for requests"
redis-cli XREAD COUNT 10 STREAMS xnai:agent_bus 0

# Or follow in real-time
redis-cli XREAD BLOCK 0 STREAMS xnai:agent_bus '$'
```

### Message Format (Standard)
```json
{
  "sender": "opencode-1",
  "target": "copilot-haiku",
  "action": "request|response|status|error",
  "message": "Human-readable content",
  "task_id": "TASK-20260316-123456",
  "timestamp": "2026-03-16T09:50:00Z"
}
```

---

## 🗳️ High-Level Deliberation: Making Group Decisions

### 1️⃣ Create a Proposal (from any CLI)
```python
# In Python (e.g., from Gemini CLI)
proposal = {
    "proposal_id": "PROP-2026-0316-001",
    "title": "Use Gemini for independent verification",
    "description": "Propose Gemini CLI as external reviewer for major decisions",
    "proposer": "copilot-haiku",
    "urgency": "high",
    "created_at": "2026-03-16T09:50:00Z"
}

# Store it
redis-cli SET "xnai:proposals:PROP-2026-0316-001" '{"proposal": proposal}' EX 604800
```

### 2️⃣ Request Deliberation (broadcast to all CLIs)
```bash
# Publish request to agent bus
redis-cli XADD xnai:agent_bus '*' \
  sender 'copilot-haiku' \
  action 'request_deliberation' \
  proposal_id 'PROP-2026-0316-001' \
  targets 'opencode-1,antigravity-1,gemini-1'
```

### 3️⃣ Each CLI Votes
```bash
# From OpenCode CLI
redis-cli HSET "xnai:proposals:PROP-2026-0316-001:votes" \
  "opencode-1" '{"vote":"approve","reasoning":"Aligns with architecture"}'

# From Antigravity CLI
redis-cli HSET "xnai:proposals:PROP-2026-0316-001:votes" \
  "antigravity-1" '{"vote":"approve","reasoning":"Improves security"}'

# From Gemini CLI
redis-cli HSET "xnai:proposals:PROP-2026-0316-001:votes" \
  "gemini-1" '{"vote":"approve","reasoning":"Ready to participate"}'
```

### 4️⃣ Tally Consensus
```bash
# Get all votes
redis-cli HGETALL "xnai:proposals:PROP-2026-0316-001:votes"

# Finalize (consensus = majority weighted vote)
redis-cli SET "xnai:proposals:PROP-2026-0316-001:status" "approved"
redis-cli XADD xnai:agent_bus '*' \
  sender 'copilot-haiku' \
  action 'proposal_finalized' \
  proposal_id 'PROP-2026-0316-001' \
  consensus 'approved'
```

---

## 📋 Active Session Tracking

### Current Session Context
```bash
# View current Copilot session
cat ~/.copilot/session-state/ad0d3d04-7e7b-4e69-a015-f3d35478223d/plan.md | head -50

# View current task
cat ~/.copilot/session-state/ad0d3d04-7e7b-4e69-a015-f3d35478223d/plan.md | grep -A 5 "Current Phase"
```

### Cross-CLI Status Check
```bash
# Check all active entities
redis-cli KEYS "xnai:entities:cli_session:*" | wc -l

# View OpenCode session status
redis-cli GET "xnai:entities:cli_session:opencode-current"

# View Antigravity status
redis-cli GET "xnai:entities:cli_session:antigravity-current"

# View Gemini status
redis-cli GET "xnai:entities:cli_session:gemini-current"
```

---

## 🔐 Security: Inter-CLI Authorization

### Before Accepting Messages, Verify Sender
```bash
# Valid senders (hardcoded list)
VALID_SENDERS=(
  "opencode-1"
  "opencode-2"
  "antigravity-1"
  "antigravity-2"
  "gemini-1"
  "copilot-haiku"
  "copilot-sonnet"
)

# Check if sender is in list
sender=$1
if [[ " ${VALID_SENDERS[@]} " =~ " ${sender} " ]]; then
  echo "✓ Sender authorized"
else
  echo "✗ Sender NOT authorized"
fi
```

### Rate Limiting Per CLI
```bash
# Track message count
redis-cli INCR "xnai:ratelimit:opencode-1:msgs"

# Set TTL for hourly reset
redis-cli EXPIRE "xnai:ratelimit:opencode-1:msgs" 3600

# Check if over limit (e.g., max 100 msgs/hour)
count=$(redis-cli GET "xnai:ratelimit:opencode-1:msgs")
if [ "$count" -gt 100 ]; then
  echo "✗ Rate limit exceeded"
else
  echo "✓ OK to send message"
fi
```

---

## 📚 Memory Bank Integration

### Archive Session to Memory Bank
```bash
# Copy current session context to memory bank
cp ~/.copilot/session-state/ad0d3d04-7e7b-4e69-a015-f3d35478223d/plan.md \
   memory_bank/sessions/copilot-sess-2026-03-16.md

# Archive proposal results
redis-cli GET "xnai:proposals:PROP-2026-0316-001:votes" > \
   memory_bank/decisions/prop-2026-0316-001-results.json
```

### Load Previous Session Context
```bash
# Find previous session
ls -lh memory_bank/sessions/ | tail -10

# Load it
PREV_CONTEXT=$(cat memory_bank/sessions/copilot-sess-2026-03-15.md)
redis-cli SET "xnai:entities:context:loaded" "$PREV_CONTEXT"
```

---

## 🆘 Troubleshooting

### Redis Connection Fails
```bash
# Check Redis is running
ps aux | grep redis-server

# Start Redis if needed
redis-server --daemonize yes

# Verify connection
redis-cli ping  # Should return PONG
```

### Entity Not Found
```bash
# Check file cache as fallback
ls ~/.xnai/entity_cache/cli_session/

# Or search memory_bank
grep -r "entity_id" memory_bank/entities/

# Restore from memory_bank
redis-cli SET "xnai:entities:cli_session:missing-id" \
  "$(cat memory_bank/entities/cli_session/missing-id.json)"
```

### Agent Bus Message Not Received
```bash
# Check stream exists
redis-cli XLEN xnai:agent_bus

# Check message arrived
redis-cli XREAD COUNT 10 STREAMS xnai:agent_bus 0

# Check for errors
redis-cli XREAD COUNT 10 STREAMS xnai:alerts 0
```

---

## 📞 Support Matrix

| Issue | Check | Fix |
|-------|-------|-----|
| CLI not starting | `CLI --version` | Reinstall CLI, check PATH |
| Redis down | `redis-cli ping` | `redis-server --daemonize yes` |
| Entity not persisting | `redis-cli GET key` | Check write permissions, TTL |
| Message not delivered | `redis-cli XLEN xnai:agent_bus` | Check sender/target format |
| Deliberation stuck | `redis-cli HGETALL proposal:votes` | Check all votes received |

---

## 📖 Full Documentation

- **Detailed Design**: `_meta/MULTI_CLI_RESTORATION_INFRASTRUCTURE.md`
- **Persistence Layer**: `app/XNAi_rag_app/persistence/`
- **Agent Bus Protocol**: `memory_bank/strategies/CLI-DISPATCH-PROTOCOLS.md`
- **Deliberation Engine**: `app/XNAi_rag_app/deliberation/`

**Last Updated**: 2026-03-16T09:50:00Z
