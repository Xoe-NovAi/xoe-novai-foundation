# 📜 Metropolis Agent Interaction Protocol

**Version**: 1.0 (Hardened)  
**Coordination Key**: `METROPOLIS-PROTOCOL-2026`  
**Status**: ACTIVE

## 🌌 Introduction
This protocol defines the standard for how AI agents within the Omega Stack must request assistance from the 8-domain Metropolis hierarchy via the **Agent Bus**.

---

## 🏗️ Task Delegation Format
Agents must use the following JSON structure when posting a task to the `xnai:agent_bus` stream.

### 1. Standard Domain Request
Targeting an expert domain at its default level (Level 1: Prime).
```json
{
  "sender": "agent:researcher:001",
  "target": "expert:architect",
  "type": "delegation",
  "payload": {
    "prompt": "Review this schema for Redis Stream compatibility.",
    "context_path": "/path/to/schema.sql"
  }
}
```

### 2. Hierarchical Level Request
Targeting a specific level of expertise within a domain.
*   `expert:[domain]:prime` -> Level 1 (Gemini 3 Pro)
*   `expert:[domain]:sub`   -> Level 2 (SambaNova / OpenCode)

```json
{
  "sender": "agent:architect:001",
  "target": "expert:api:sub",
  "type": "implementation",
  "payload": {
    "prompt": "Generate the AnyIO FastAPI endpoint for the following blueprint.",
    "blueprint": "..."
  }
}
```

---

## 🧬 Interaction Flow Rules

1.  **Sovereignty Rule**: All implementation experts (Level 2) MUST run the **Local Validator** (Level 3) before reporting completion.
2.  **Recall Rule**: Before beginning a task, experts SHOULD query the **Usage MCP** to ensure they have enough token quota for the requested complexity.
3.  **Soul Rule**: After every 5 sessions, an expert MUST trigger a **Reflection Hook** to update its persistent `shared_soul.md`.

---

## 📊 Error Handling & Fallbacks

| Error Code | Meaning | Recovery Action |
|------------|---------|-----------------|
| `quota_exceeded` | Account limit reached | Dispatcher automatically rotates to next account (1-8). |
| `context_overflow` | Prompt too large | Expert uses **Knowledge Harvester** to summarize context before retry. |
| `validation_failed` | Level 3 check failed | Task is returned to Level 2 for implementation correction. |

---
**Custodian**: Gemini CLI (MC-Overseer)  
**Verification Key**: `OMEGA-PROTOCOL-HARDENING-2026-03-04`
