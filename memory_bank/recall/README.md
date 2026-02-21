# Recall Memory Tier

**Purpose**: Episodic memory - session logs, decisions, and conversation history.

## Structure

```
recall/
├── conversations/    # Session logs and conversation history
├── decisions/        # Architectural and strategic decisions
└── handovers/        # Agent handoff documents
```

## Usage

- **Not loaded by default** - searched when context is needed
- **Retention**: 90 days
- **Max Size**: 50MB total
- **Indexing**: Semantic search enabled

## File Naming Convention

| Type | Pattern | Example |
|------|---------|---------|
| Session | `YYYY-MM-DD_session-id.session.md` | `2026-02-20_ses_abc123.session.md` |
| Decision | `YYYY-MM-DD_topic.decision.md` | `2026-02-19_anyio-migration.decision.md` |
| Handover | `YYYY-MM-DD_from-to.handover.md` | `2026-02-20_glm5-opus.handover.md` |

## Search

Use semantic search via `localhost:8000/search` or the `search_recall` memory tool.

## Related

- `BLOCKS.yaml` - Configuration
- `archival/` - Long-term storage
- `activeContext/` - Active handovers (temporary)
