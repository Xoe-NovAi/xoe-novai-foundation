---
tool: cline
model: claude-sonnet-4-6
account: arcana-novai
git_branch: main
session_id: sprint5-2026-02-18
version: v1.0.0
created: 2026-02-18
tags: [cli, session-storage, copilot, gemini, opencode, cline, harvest, institutional-memory]
---

# CLI Session Storage — Deep Dive Research
**v1.0.0 | 2026-02-18 | Sprint 5**

## Executive Summary

All four primary AI CLI tools (GitHub Copilot CLI, Gemini CLI, OpenCode CLI, Cline) store
session data in different formats and locations. This document maps each storage system,
identifies the highest-value data, and defines the harvest strategy to capture institutional
memory into the XNAi RAG system.

---

## 1. GitHub Copilot CLI

### Storage Location
```
~/.copilot/session-state/<UUID>/
├── events.jsonl       # ★★★ PRIMARY — full conversation + action event stream
├── plan.md            # Generated plan document (markdown)
├── workspace.yaml     # Session metadata (id, cwd, summary, created_at)
├── checkpoints/
│   └── index.md       # Checkpoint index (often empty)
└── files/             # Generated/modified files during session
```

### Discovery
- **34 sessions** found on this system
- Sessions identified by UUID directory names
- Average session: 2-50MB events.jsonl

### events.jsonl Structure
```json
{"type": "user_message", "content": "...", "timestamp": "2026-01-15T14:22:00Z"}
{"type": "assistant_message", "content": "...", "model": "gpt-4o", "timestamp": "..."}
{"type": "tool_use", "tool": "create_file", "path": "...", "timestamp": "..."}
{"type": "tool_result", "output": "...", "timestamp": "..."}
{"type": "plan_created", "plan": "...", "timestamp": "..."}
```

### workspace.yaml Structure
```yaml
id: <UUID>
cwd: /home/arcana-novai/Documents/xnai-foundation
summary: "Working on RAG pipeline optimization"
created_at: "2026-01-15T14:20:00Z"
model: gpt-4o
```

### High-Value Data
- **Architectural decisions** embedded in assistant messages
- **Code snippets** created during sessions
- **Plan documents** with structured approach breakdowns
- **Tool use sequences** showing how problems were solved

### Harvest Priority: 🔴 CRITICAL
events.jsonl is the goldmine — captures full context of what Copilot did and decided.

---

## 2. Gemini CLI

### Storage Location
```
~/.gemini/
├── sessions/
│   └── <session-id>/
│       ├── conversation.json  # Full conversation history
│       └── metadata.json      # Session metadata
├── tmp/
│   └── gemini-debug-*.log     # Debug logs (when --debug enabled)
└── config.json                # Global config
```

### Session Format
Gemini CLI stores sessions as JSON arrays of turn objects:
```json
[
  {"role": "user", "parts": [{"text": "..."}]},
  {"role": "model", "parts": [{"text": "..."}]}
]
```

### Key Characteristics
- Sessions expire after 1 hour of inactivity by default
- `--resume` flag reloads previous session
- Context compaction happens at ~128K tokens (Gemini 2.0 Flash)
- Flash-Thinking uses different token accounting

### Harvest Priority: 🟡 MEDIUM
Shorter sessions, less architectural depth than Copilot. Still valuable for research outputs.

---

## 3. OpenCode CLI

### Storage Location
```
~/.opencode/
├── sessions/
│   └── <session-id>.json      # Session data
├── config.json                # Global config (mirrors .opencode/opencode.json)
└── logs/
    └── opencode-<date>.log
```

> **Note**: OpenCode was archived 2026-02-14 in favor of Antigravity CLI.
> Sessions from the OpenCode era are historical but contain valuable architectural decisions.

### Session Format
```json
{
  "id": "<session-id>",
  "created": "2026-01-10T10:00:00Z",
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "...", "model": "claude-sonnet-4-5"}
  ],
  "files": []
}
```

### Harvest Priority: 🟠 HIGH (historical archive)
Contains early architectural decisions for the XNAi stack before OpenCode archival.

---

## 4. Cline (VSCodium Extension)

### Storage Location
```
~/.config/VSCodium/User/globalStorage/saoudrizwan.claude-dev/
├── tasks/
│   └── <task-id>/
│       ├── api_conversation_history.json  # Full API message history
│       └── ui_messages.json               # UI-layer messages
├── settings/
│   └── cline_mcp_settings.json           # MCP server configs
└── cache/
    └── ...
```

### api_conversation_history.json Structure
```json
[
  {"role": "user", "content": [{"type": "text", "text": "..."}]},
  {"role": "assistant", "content": [{"type": "text", "text": "..."}]},
  {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "...", "content": "..."}]}
]
```

### Context Window Behavior
- **Nominal**: 200K tokens displayed in UI
- **Shadow window**: Evidence suggests ~400K actual capacity (user observed 250.8K tokens
  shown before compaction while progress bar was ~halfway, implying ~400K scale)
- **Compaction trigger**: Auto-compacts when approaching displayed limit
- Tasks persist across sessions — full history recoverable

### Harvest Priority: 🔴 CRITICAL
Cline tasks contain the richest institutional memory — every tool use, file edit, and
architectural decision is logged with full context.

---

## 5. Harvest Architecture

### Two-Strategy Approach

#### Strategy A: Reactive Harvest (harvest-cli-sessions.sh)
Runs periodically to collect existing session data:
```
~/.copilot/session-state/ → xoe-novai-sync/mc-imports/copilot/
~/.gemini/sessions/        → xoe-novai-sync/mc-imports/gemini/
~/.opencode/sessions/      → xoe-novai-sync/mc-imports/opencode/
~/.config/VSCodium/.../tasks/ → xoe-novai-sync/mc-imports/cline/
```

Then ingest into Qdrant `xnai_conversations` collection via `conversation_ingestion.py`.

#### Strategy B: Proactive Discipline (RULES.md updates)
All CLIs must save outputs to project directories:
- Research → `expert-knowledge/research/`
- Protocols → `expert-knowledge/protocols/`
- Plans → `memory_bank/`
- Code → appropriate `app/` or `scripts/` paths

### Qdrant Collection Schema
```python
# Collection: xnai_conversations
{
  "id": "uuid",
  "vector": [...],  # 768-dim fastembed embedding
  "payload": {
    "source": "copilot|gemini|opencode|cline",
    "session_id": "...",
    "timestamp": "ISO8601",
    "cwd": "/path/to/project",
    "role": "user|assistant",
    "content": "...",
    "tags": ["architectural-decision", "code", "research"],
    "model": "gpt-4o|gemini-2.0-flash|claude-opus-4-5"
  }
}
```

---

## 6. Priority Session List

Sessions to harvest immediately (by value):

| Priority | CLI | Data | Reason |
|----------|-----|------|--------|
| 1 | Cline | tasks/*/api_conversation_history.json | Richest context, all sprint work |
| 2 | Copilot | events.jsonl (34 sessions) | Architectural decisions, plans |
| 3 | OpenCode | sessions/*.json (pre-archive) | Historical stack decisions |
| 4 | Gemini | sessions/*.json | Research outputs |

---

## 7. Implementation Files

- **`scripts/harvest-cli-sessions.sh`** — Bash harvest script (see that file)
- **`app/XNAi_rag_app/conversation_ingestion.py`** — Python ingestion to Qdrant
- **`expert-knowledge/protocols/DOCUMENT-SIGNING-PROTOCOL.md`** — Frontmatter standard

---

## References

- Copilot CLI: `~/.copilot/session-state/` (34 sessions confirmed on system)
- Cline Extension: `~/.config/VSCodium/User/globalStorage/saoudrizwan.claude-dev/`
- Qdrant collection target: `xnai_conversations`
- Embedding model: `nomic-ai/nomic-embed-text-v1.5` (768-dim, fastembed)
